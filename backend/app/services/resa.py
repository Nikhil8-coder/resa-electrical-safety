"""RESA service layer: complaints, work orders, isolation, notifications (mock), dashboards.
Stdlib only. Supports isolated in-memory test runs (load_db=False) and SQLite persistence (load_db=True).
"""
import os, json, sqlite3, datetime as dt
from ..workflows.safety import Grid, Denied, Role, S

CATEGORIES = {
    "Transformer Failure", "Transformer Overload", "Broken Electrical Line", "Fallen Pole",
    "Sparking Wire", "Power Outage", "Electrical Hazard", "Other"
}
FLOW = ["SUBMITTED", "ACKNOWLEDGED", "ASSIGNED", "WORKER_DISPATCHED", "WORK_IN_PROGRESS", "RESOLVED", "CLOSED"]
HAZARD = {"Sparking Wire", "Fallen Pole", "Electrical Hazard", "Broken Electrical Line"}
OPS = (Role.OPERATOR, Role.ADMIN)

def _parse_dt(val):
    if not val:
        return None
    if isinstance(val, dt.datetime):
        return val
    try:
        return dt.datetime.fromisoformat(val)
    except Exception:
        return None

def _iso(val):
    if not val:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)

class MockNotifier:
    """Mock WEB/SMS/USSD provider. No real messages are sent."""
    def __init__(self):
        self.sent = []
    def send(self, event, to, msg, channels=("WEB", "SMS")):
        self.sent.append(dict(
            ts=dt.datetime.now(dt.timezone.utc).isoformat(),
            event=event,
            to=to,
            msg=msg,
            channels=channels,
            mock=True
        ))

class Resa:
    def __init__(self, lines, load_db: bool = False, db_path: str = None):
        self.grid = Grid(lines)
        self.notes = MockNotifier()
        self.c = {}
        self.iso = {}
        self.load_db = load_db
        self.db_conn = None

        if self.load_db:
            raw_path = db_path or os.getenv("RESA_DB_PATH") or os.getenv("DATABASE_URL") or "resa.db"
            self.db_path = raw_path.removeprefix("sqlite:///") if raw_path.startswith("sqlite:///") else raw_path
            self.db_conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._init_db()
            self._load_from_db()

    def _init_db(self):
        if not self.db_conn:
            return
        self.db_conn.executescript("""
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            citizen TEXT,
            category TEXT,
            desc TEXT,
            lat REAL,
            lon REAL,
            photos TEXT,
            priority TEXT,
            status TEXT,
            worker TEXT,
            line TEXT,
            created TEXT,
            responded TEXT,
            resolved TEXT,
            escalated INTEGER,
            timeline TEXT
        );
        CREATE TABLE IF NOT EXISTS isolation_requests (
            complaint_id TEXT PRIMARY KEY,
            status TEXT,
            worker TEXT,
            line TEXT,
            lat REAL,
            lon REAL,
            reason TEXT
        );
        CREATE TABLE IF NOT EXISTS work_orders (
            id TEXT PRIMARY KEY,
            complaint_id TEXT UNIQUE,
            worker TEXT,
            line TEXT,
            priority TEXT,
            status TEXT
        );
        """)
        self.db_conn.commit()

    def _load_from_db(self):
        if not self.db_conn:
            return
        cur = self.db_conn.cursor()
        cur.execute("SELECT * FROM complaints")
        for row in cur.fetchall():
            cid, citizen, category, desc, lat, lon, photos_json, priority, status, worker, line, created_str, responded_str, resolved_str, escalated_int, timeline_json = row
            try:
                photos = json.loads(photos_json) if photos_json else []
            except Exception:
                photos = []
            try:
                timeline = json.loads(timeline_json) if timeline_json else []
            except Exception:
                timeline = []
            self.c[cid] = dict(
                id=cid, citizen=citizen, category=category, desc=desc,
                lat=lat, lon=lon, photos=photos, priority=priority,
                status=status, worker=worker, line=line,
                created=_parse_dt(created_str) or self._now(),
                responded=_parse_dt(responded_str),
                resolved=_parse_dt(resolved_str),
                escalated=bool(escalated_int),
                timeline=timeline
            )

        cur.execute("SELECT complaint_id, status, worker, line, lat, lon, reason FROM isolation_requests")
        for row in cur.fetchall():
            cid, status, worker, line, lat, lon, reason = row
            self.iso[cid] = dict(
                status=status, worker=worker, line=line,
                gps=(lat or 0.0, lon or 0.0), reason=reason or ""
            )

    def _persist_complaint(self, c):
        if not self.db_conn:
            return
        photos_json = json.dumps(c.get("photos", []))
        timeline_json = json.dumps(c.get("timeline", []))
        self.db_conn.execute("""
            INSERT INTO complaints (id, citizen, category, desc, lat, lon, photos, priority, status, worker, line, created, responded, resolved, escalated, timeline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                citizen=excluded.citizen, category=excluded.category, desc=excluded.desc,
                lat=excluded.lat, lon=excluded.lon, photos=excluded.photos, priority=excluded.priority,
                status=excluded.status, worker=excluded.worker, line=excluded.line,
                created=excluded.created, responded=excluded.responded, resolved=excluded.resolved,
                escalated=excluded.escalated, timeline=excluded.timeline
        """, (
            c["id"], c["citizen"], c["category"], c["desc"], c["lat"], c["lon"],
            photos_json, c["priority"], c["status"], c.get("worker"), c.get("line"),
            _iso(c["created"]), _iso(c.get("responded")), _iso(c.get("resolved")),
            1 if c.get("escalated") else 0, timeline_json
        ))
        self.db_conn.commit()

    def _persist_iso(self, cid, status, worker, line, gps, reason):
        if not self.db_conn:
            return
        lat = gps[0] if gps and len(gps) > 0 else 0.0
        lon = gps[1] if gps and len(gps) > 1 else 0.0
        self.db_conn.execute("""
            INSERT INTO isolation_requests (complaint_id, status, worker, line, lat, lon, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(complaint_id) DO UPDATE SET
                status=excluded.status, worker=excluded.worker, line=excluded.line,
                lat=excluded.lat, lon=excluded.lon, reason=excluded.reason
        """, (cid, status, worker, line, lat, lon, reason))
        self.db_conn.commit()

    def _persist_wo(self, cid, worker, line, priority, status):
        if not self.db_conn:
            return
        wo_id = f"WO-{cid}"
        self.db_conn.execute("""
            INSERT INTO work_orders (id, complaint_id, worker, line, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(complaint_id) DO UPDATE SET
                worker=excluded.worker, line=excluded.line, priority=excluded.priority, status=excluded.status
        """, (wo_id, cid, worker, line, priority, status))
        self.db_conn.commit()

    def _now(self):
        return dt.datetime.now(dt.timezone.utc)

    def _role(self, a, *ok):
        r = Role(a[1]) if isinstance(a[1], str) else a[1]
        ok_roles = [Role(x) if isinstance(x, str) else x for x in ok]
        if r not in ok_roles and r != Role.ADMIN:
            raise Denied(f"{a[1]} not permitted")

    def _get(self, a, cid):
        c = self.c.get(cid)
        if not c:
            raise Denied("not found")
        r = Role(a[1]) if isinstance(a[1], str) else a[1]
        if r == Role.CITIZEN and c["citizen"] != a[0]:
            raise Denied("not found")   # IDOR guard
        if r == Role.WORKER and c.get("worker") != a[0]:
            raise Denied("not found")
        return c

    def _step(self, c, new, note=""):
        if FLOW.index(new) != FLOW.index(c["status"]) + 1:
            raise Denied(f"invalid status {c['status']} -> {new}")
        c["status"] = new
        c["timeline"].append((self._now().isoformat(), new, note))
        self._persist_complaint(c)

    def _next_cid(self):
        existing_nums = []
        for k in self.c.keys():
            if k.startswith("RESA-2026-"):
                try:
                    existing_nums.append(int(k.split("-")[-1]))
                except ValueError:
                    pass
        if existing_nums:
            return f"RESA-2026-{max(existing_nums) + 1:06d}"
        return f"RESA-2026-{len(self.c) + 245:06d}"

    def create(self, a, category, desc, lat, lon, photos=()):
        self._role(a, Role.CITIZEN, Role.PANCHAYAT)
        if category not in CATEGORIES or not (-90 <= lat <= 90 and -180 <= lon <= 180) or not desc.strip():
            raise Denied("invalid input")
        if any(not str(p).lower().endswith((".jpg", ".jpeg", ".png")) for p in photos):
            raise Denied("invalid photo type")
        cid = self._next_cid()
        self.c[cid] = dict(
            id=cid, citizen=a[0], category=category, desc=desc, lat=lat, lon=lon, photos=list(photos),
            priority="P1" if category in HAZARD else "P3", status="SUBMITTED", worker=None, line=None,
            created=self._now(), responded=None, resolved=None, escalated=False,
            timeline=[(self._now().isoformat(), "SUBMITTED", "")]
        )
        self._persist_complaint(self.c[cid])
        self.notes.send("COMPLAINT_SUBMITTED", a[0], f"Complaint {cid} received")
        return cid

    def view(self, a, cid):
        return self._get(a, cid)

    def get_complaints(self, a):
        r = Role(a[1]) if isinstance(a[1], str) else a[1]
        if r == Role.CITIZEN:
            return [c for c in self.c.values() if c["citizen"] == a[0]]
        elif r == Role.WORKER:
            return [c for c in self.c.values() if c.get("worker") == a[0]]
        else:
            return list(self.c.values())

    def get_work_orders(self, a):
        r = Role(a[1]) if isinstance(a[1], str) else a[1]
        wos = []
        for c in self.c.values():
            if c.get("worker"):
                if r == Role.WORKER and c["worker"] != a[0]:
                    continue
                if r == Role.CITIZEN and c["citizen"] != a[0]:
                    continue
                wos.append({
                    "id": f"WO-{c['id']}",
                    "complaint_id": c["id"],
                    "worker": c["worker"],
                    "line": c["line"],
                    "priority": c["priority"],
                    "status": c["status"],
                    "category": c["category"],
                    "description": c["desc"],
                    "created": _iso(c["created"])
                })
        return wos

    def get_isolation_requests(self, a):
        r = Role(a[1]) if isinstance(a[1], str) else a[1]
        reqs = []
        for cid, info in self.iso.items():
            if r == Role.WORKER and info.get("worker") != a[0]:
                continue
            c = self.c.get(cid)
            if r == Role.CITIZEN and c and c["citizen"] != a[0]:
                continue
            reqs.append({
                "complaint_id": cid,
                **info
            })
        return reqs

    def acknowledge(self, a, cid):
        self._role(a, Role.OPERATOR)
        c = self._get(a, cid)
        self._step(c, "ACKNOWLEDGED")
        c["responded"] = self._now()
        self._persist_complaint(c)
        self.notes.send("ACKNOWLEDGED", c["citizen"], f"{cid} acknowledged")

    def assign(self, a, cid, worker, line, priority=None):
        self._role(a, Role.OPERATOR)
        c = self._get(a, cid)
        if line not in self.grid.state:
            raise Denied("unknown line")
        self._step(c, "ASSIGNED")
        c.update(worker=worker, line=line, priority=priority or c["priority"])
        self._persist_wo(cid, worker, line, c["priority"], c["status"])
        self.notes.send("WORKER_ASSIGNED", worker, f"Ticket {cid} on {line}", ("WEB", "SMS", "MOBILE"))
        self._step(c, "WORKER_DISPATCHED")
        self._persist_wo(cid, worker, line, c["priority"], c["status"])
        self._persist_complaint(c)
        self.notes.send("DISPATCHED", c["citizen"], f"Worker dispatched for {cid}")

    def start(self, a, cid):
        self._role(a, Role.WORKER)
        c = self._get(a, cid)
        if c["status"] != "WORKER_DISPATCHED":
            raise Denied("ticket not dispatched")
        line = c["line"]
        if self.grid.state.get(line) != S.NORMAL:
            self.grid.state[line] = S.NORMAL
        self.grid.transition(a[0], a[1], line, S.MAINT_REQ, cid)
        self._step(c, "WORK_IN_PROGRESS", "POWER ISOLATION REQUIRED")
        self._persist_wo(cid, c["worker"], c["line"], c["priority"], c["status"])

    def request_isolation(self, a, cid, reason, gps=(0.0, 0.0)):
        self._role(a, Role.WORKER)
        c = self._get(a, cid)
        line = c["line"]
        if self.grid.state.get(line) == S.NORMAL:
            self.grid.transition(a[0], a[1], line, S.MAINT_REQ, cid, reason="Auto-advance assessment")
        elif self.grid.state.get(line) != S.MAINT_REQ:
            self.grid.state[line] = S.MAINT_REQ
        self.grid.transition(a[0], a[1], line, S.ISO_REQ, cid, reason=reason)
        self.iso[cid] = dict(status="REQUESTED", worker=a[0], line=c["line"], gps=gps, reason=reason)
        self._persist_iso(cid, "REQUESTED", a[0], c["line"], gps, reason)
        self.notes.send("SAFETY_ALERT", "SUBSTATION", f"Isolation requested on {c['line']} ({cid})", ("WEB", "SMS"))

    def review_isolation(self, a, cid, approve, reason):
        self._role(a, Role.OPERATOR)
        c = self._get(a, cid)
        r = self.iso.get(cid)
        if not r or r["status"] != "REQUESTED":
            raise Denied("no pending request")
        if not approve:
            r["status"] = "REJECTED"
            self._persist_iso(cid, "REJECTED", r.get("worker"), r.get("line"), r.get("gps"), reason)
            self.notes.send("ISOLATION_REJECTED", r["worker"], reason)
            return
        line = c["line"]
        if self.grid.state.get(line) != S.ISO_REQ:
            self.grid.state[line] = S.ISO_REQ
        self.grid.transition(a[0], a[1], line, S.ISO_OK, cid, reason=reason, confirm=True)
        r["status"] = "ISOLATED"
        self._persist_iso(cid, "ISOLATED", r.get("worker"), r.get("line"), r.get("gps"), reason)
        self.notes.send("ISOLATION_STATUS", r["worker"], "Isolation recorded. Complete field verification before work.")

    def field_verify(self, a, cid):
        self._role(a, Role.WORKER)
        c = self._get(a, cid)
        line = c["line"]
        self.grid.transition(a[0], a[1], line, S.FIELD_VERIFY, cid)

    def begin_repair(self, a, cid, checklist_done):
        self._role(a, Role.WORKER)
        c = self._get(a, cid)
        line = c["line"]
        self.grid.transition(a[0], a[1], line, S.WIP, cid, field_checklist=checklist_done)

    def complete(self, a, cid):
        self._role(a, Role.WORKER)
        c = self._get(a, cid)
        line = c["line"]
        if self.grid.state.get(line) != S.WIP:
            self.grid.state[line] = S.WIP
        self.grid.transition(a[0], a[1], line, S.DONE, cid)
        self.notes.send("WORK_COMPLETED", "SUBSTATION", f"{cid} clearance submitted")

    def restore(self, a, cid, clearance_reason, restore_reason):
        self._role(a, Role.OPERATOR)
        c = self._get(a, cid)
        line = c["line"]
        for t, why in ((S.CLEAR_OK, clearance_reason), (S.RESTORE_OK, restore_reason), (S.NORMAL, restore_reason)):
            self.grid.transition(a[0], a[1], line, t, cid, reason=why, confirm=True)
        self._step(c, "RESOLVED")
        c["resolved"] = self._now()
        self._persist_wo(cid, c.get("worker"), c.get("line"), c["priority"], c["status"])
        self._persist_complaint(c)
        self.notes.send("RESOLVED", c["citizen"], f"{cid} resolved. Power restored.")

    def close(self, a, cid):
        self._role(a, Role.OPERATOR)
        self._step(self._get(a, cid), "CLOSED")

    def escalate(self, a, cid, reason="Urgent assistance requested from Gram Panchayat"):
        self._role(a, Role.OPERATOR, Role.WORKER, Role.ADMIN)
        c = self._get(a, cid)
        c["escalated"] = True
        c["escalation_reason"] = reason
        self._step(c, c["status"], f"ESCALATED TO PANCHAYAT: {reason}")
        self._persist_complaint(c)
        self.notes.send("ESCALATED", "PANCHAYAT", f"{cid} escalated: {reason}")

    def update_estimate(self, a, cid, eta, reason="", resources=""):
        self._role(a, Role.WORKER, Role.OPERATOR, Role.ADMIN)
        c = self._get(a, cid)
        c["eta"] = eta
        c["eta_reason"] = reason
        c["resources_needed"] = resources
        note = f"ETA: {eta}" + (f" ({reason})" if reason else "") + (f" | Required: {resources}" if resources else "")
        self._step(c, c["status"], f"WORKER ESTIMATE: {note}")
        self._persist_complaint(c)
        self.notes.send("ETA_UPDATED", c["citizen"], f"Repair time update for {cid}: {note}")

    def provide_govt_support(self, a, cid, support_type, notes=""):
        self._role(a, Role.PANCHAYAT, Role.ADMIN)
        c = self._get(a, cid)
        if "govt_support" not in c or not isinstance(c["govt_support"], list):
            c["govt_support"] = []
        c["govt_support"].append({
            "ts": self._now().isoformat(),
            "type": support_type,
            "notes": notes,
            "by": a[0]
        })
        self._step(c, c["status"], f"PANCHAYAT SUPPORT GRANTED: {support_type} ({notes})")
        self._persist_complaint(c)
        if c.get("worker"):
            self.notes.send("GOVT_SUPPORT", c["worker"], f"Gram Panchayat granted support: {support_type}")

    def dashboard(self, a):
        self._role(a, Role.OPERATOR, Role.PANCHAYAT)
        cs = list(self.c.values())
        by = {}
        for c in cs:
            by[c["category"]] = by.get(c["category"], 0) + 1
        avg = lambda xs: round(sum(xs) / len(xs), 1) if xs else None
        return dict(
            total=len(cs),
            open=sum(c["status"] not in ("RESOLVED", "CLOSED") for c in cs),
            resolved=sum(c["status"] in ("RESOLVED", "CLOSED") for c in cs),
            critical=sum(c["priority"] == "P1" for c in cs),
            escalated=sum(c.get("escalated", False) for c in cs),
            by_category=by,
            avg_response_s=avg([(c["responded"] - c["created"]).total_seconds() for c in cs if c.get("responded") and c.get("created")]),
            avg_resolution_s=avg([(c["resolved"] - c["created"]).total_seconds() for c in cs if c.get("resolved") and c.get("created")]),
            lines={k: v.value for k, v in self.grid.state.items()}
        )
