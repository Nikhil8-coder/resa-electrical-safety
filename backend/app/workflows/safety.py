"""RESA safety state machine + RBAC + immutable audit log.
Digital coordination only: it never switches equipment and never implies a line is
physically safe. Field isolation, testing, earthing and LOTO remain human SOP duties."""
import sqlite3, datetime as dt
from enum import Enum

class Role(str, Enum):
    CITIZEN="CITIZEN"; WORKER="LINE_WORKER"; OPERATOR="SUBSTATION_OPERATOR"
    PANCHAYAT="PANCHAYAT_ADMIN"; ADMIN="SYSTEM_ADMIN"

class S(str, Enum):
    NORMAL="NORMAL"; MAINT_REQ="MAINTENANCE_REQUESTED"; ISO_REQ="ISOLATION_REQUESTED"
    ISO_OK="ISOLATION_CONFIRMED"; FIELD_VERIFY="FIELD_SAFETY_VERIFICATION"
    WIP="WORK_IN_PROGRESS"; DONE="WORK_COMPLETED"; CLEAR_OK="CLEARANCE_CONFIRMED"
    RESTORE_OK="RESTORATION_AUTHORIZED"

# Strictly linear: no state can be skipped, none can jump to NORMAL except restoration.
NEXT = {S.NORMAL:S.MAINT_REQ, S.MAINT_REQ:S.ISO_REQ, S.ISO_REQ:S.ISO_OK, S.ISO_OK:S.FIELD_VERIFY,
        S.FIELD_VERIFY:S.WIP, S.WIP:S.DONE, S.DONE:S.CLEAR_OK, S.CLEAR_OK:S.RESTORE_OK, S.RESTORE_OK:S.NORMAL}
W, O, A = Role.WORKER, Role.OPERATOR, Role.ADMIN
# Who may move INTO each state. Operator-only: isolation, clearance, restoration, return to normal.
ACTORS = {S.MAINT_REQ:{W,A}, S.ISO_REQ:{W,A}, S.ISO_OK:{O,A}, S.FIELD_VERIFY:{W,A}, S.WIP:{W,A},
          S.DONE:{W,A}, S.CLEAR_OK:{O,A}, S.RESTORE_OK:{O,A}, S.NORMAL:{O,A}}
OPERATOR_STEPS = {S.ISO_OK, S.CLEAR_OK, S.RESTORE_OK, S.NORMAL}

class Denied(Exception): pass

class Grid:
    def __init__(self, lines):
        self.state = {l: S.NORMAL for l in lines}
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.executescript("""
        CREATE TABLE audit(id INTEGER PRIMARY KEY, ts TEXT, user TEXT, role TEXT, action TEXT,
          line TEXT, ticket TEXT, prev TEXT, new TEXT, reason TEXT, result TEXT);
        CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'audit is immutable'); END;
        CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'audit is immutable'); END;""")

    def _log(self, user, role, line, ticket, prev, new, reason, result):
        self.db.execute("INSERT INTO audit VALUES(NULL,?,?,?,?,?,?,?,?,?,?)",
            (dt.datetime.now(dt.timezone.utc).isoformat(), user, role, "LINE_TRANSITION", line, ticket,
             prev, new, reason, result)); self.db.commit()

    def transition(self, user, role, line, target, ticket, reason="", confirm=False, field_checklist=False):
        role = Role(role); target = S(target); prev = self.state.get(line)
        def deny(msg):
            self._log(user, role.value, line, ticket, getattr(prev,"value",None), target.value, reason, "DENIED: "+msg)
            raise Denied(msg)
        if prev is None: deny("unknown line")
        if not ticket: deny("related ticket required")
        if role not in ACTORS[target]: deny(f"{role.value} may not set {target.value}")
        if NEXT[prev] != target: deny(f"invalid transition {prev.value} -> {target.value}")
        if target in OPERATOR_STEPS and not (confirm and reason.strip()):
            deny("explicit confirmation and reason required")
        if target == S.WIP and not field_checklist:
            deny("worker must confirm field-side safety verification (SOP: test, earth, LOTO)")
        self.state[line] = target
        self._log(user, role.value, line, ticket, prev.value, target.value, reason, "SUCCESS")
        return target

    def audit(self): return self.db.execute("SELECT * FROM audit ORDER BY id").fetchall()
