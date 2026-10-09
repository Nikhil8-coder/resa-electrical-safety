"""FastAPI layer over the RESA safety core and workflow services.
Supports demo authentication, RBAC, full complaint lifecycle, grid management, and modern Web Portal.
"""
import os, hashlib, hmac, secrets
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .workflows.safety import Grid, Denied, Role, S
from .services.resa import Resa

app = FastAPI(title="RESA (Reliable Electrical System Addresser)", version="2.0.0")

# Enable CORS for browser access and public tunnels
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

grid = Grid(["LN-204", "LN-205", "LN-311"])

def _h(p):
    return hashlib.pbkdf2_hmac("sha256", p.encode(), b"demo-salt", 100_000).hex()

DEMO_PW = os.getenv("DEMO_PW", "change-me")
USERS = {
    "worker1": (_h(DEMO_PW), Role.WORKER),
    "op1": (_h(DEMO_PW), Role.OPERATOR),
    "cit1": (_h(DEMO_PW), Role.CITIZEN),
    "pan1": (_h(DEMO_PW), Role.PANCHAYAT),
    "admin": (_h(DEMO_PW), Role.ADMIN),
}
TOKENS: dict = {}

class Login(BaseModel):
    username: str
    password: str

class Move(BaseModel):
    target: str
    ticket: str
    reason: str = ""
    confirm: bool = False
    field_checklist: bool = False

class NewComplaint(BaseModel):
    category: str
    description: str
    lat: float
    lon: float
    photos: list[str] = []

class Act(BaseModel):
    worker: str = ""
    line: str = ""
    reason: str = ""
    approve: bool = True
    checklist: bool = False
    clearance_reason: str = ""

def user(authorization: str = Header(None)):
    token = (authorization or "").removeprefix("Bearer ").strip()
    u = TOKENS.get(token)
    if not u:
        raise HTTPException(401, "unauthenticated")
    return u

def _run(fn, *a):
    try:
        return fn(*a)
    except Denied as e:
        raise HTTPException(403, str(e))

# Service layer initialized with SQLite persistence
svc = Resa(["LN-204", "LN-205", "LN-311"], load_db=True)
svc.grid = grid  # share one grid with lines API

# Pre-seed initial demo complaint if empty for immediate live display
if len(svc.c) == 0:
    try:
        c1 = svc.create(("cit1", Role.CITIZEN), "Broken Electrical Line", "High-voltage line snapped near Substation Feeder 4. Sparks observed on ground.", 17.3850, 78.4867, ["line_snap.jpg"])
        svc.acknowledge(("op1", Role.OPERATOR), c1)
        svc.assign(("op1", Role.OPERATOR), c1, "worker1", "LN-204")
        
        c2 = svc.create(("cit1", Role.CITIZEN), "Sparking Wire", "Transformer secondary bus wire sparking intermittently during peak load.", 17.3912, 78.4921, ["spark.png"])
        svc.acknowledge(("op1", Role.OPERATOR), c2)

        c3 = svc.create(("cit1", Role.CITIZEN), "Power Outage", "Ward 4 feeder tripped after lightning storm.", 17.3780, 78.4750)
    except Exception:
        pass

@app.post("/api/auth/login")
def login(b: Login):
    rec = USERS.get(b.username)
    if not rec or not hmac.compare_digest(rec[0], _h(b.password)):
        raise HTTPException(401, "invalid credentials")
    t = secrets.token_urlsafe(24)
    TOKENS[t] = (b.username, rec[1])
    return {
        "token": t,
        "username": b.username,
        "role": rec[1].value if hasattr(rec[1], "value") else str(rec[1])
    }

@app.get("/api/auth/me")
def get_me(u=Depends(user)):
    return {
        "username": u[0],
        "role": u[1].value if hasattr(u[1], "value") else str(u[1])
    }

@app.get("/api/users")
def get_users(u=Depends(user)):
    return [
        {"username": "worker1", "name": "Worker 1 (Field Team A)", "role": Role.WORKER.value},
        {"username": "op1", "name": "Operator 1 (Central Substation)", "role": Role.OPERATOR.value},
        {"username": "cit1", "name": "Anita Devi (Citizen)", "role": Role.CITIZEN.value},
        {"username": "pan1", "name": "Panchayat Admin (Ward 4)", "role": Role.PANCHAYAT.value},
        {"username": "admin", "name": "System Administrator", "role": Role.ADMIN.value},
    ]

@app.get("/api/grid/lines")
def lines(u=Depends(user)):
    return {k: v.value for k, v in grid.state.items()}

@app.post("/api/grid/lines/{line}/transition")
def move(line: str, b: Move, u=Depends(user)):
    try:
        return {"state": grid.transition(u[0], u[1], line, b.target, b.ticket, b.reason, b.confirm, b.field_checklist).value}
    except Denied as e:
        raise HTTPException(403, str(e))

@app.get("/api/audit-logs")
def audit(u=Depends(user)):
    if u[1] not in (Role.OPERATOR, Role.ADMIN):
        raise HTTPException(403, "forbidden")
    raw_logs = grid.audit()
    return [
        {
            "id": r[0],
            "ts": r[1],
            "user": r[2],
            "role": r[3],
            "action": r[4],
            "line": r[5],
            "ticket": r[6],
            "prev": r[7],
            "new": r[8],
            "reason": r[9],
            "result": r[10]
        }
        for r in raw_logs
    ]

@app.post("/api/complaints")
def new_c(b: NewComplaint, u=Depends(user)):
    cid = _run(svc.create, u, b.category, b.description, b.lat, b.lon, b.photos)
    return {"id": cid}

@app.get("/api/complaints")
def list_complaints(u=Depends(user)):
    return svc.get_complaints(u)

@app.get("/api/complaints/{cid}")
def get_c(cid: str, u=Depends(user)):
    return _run(svc.view, u, cid)

@app.post("/api/complaints/{cid}/{action}")
def act(cid: str, action: str, b: Act, u=Depends(user)):
    m = {
        "acknowledge": lambda: svc.acknowledge(u, cid),
        "assign": lambda: svc.assign(u, cid, b.worker, b.line),
        "start": lambda: svc.start(u, cid),
        "isolation-request": lambda: svc.request_isolation(u, cid, b.reason),
        "isolation-review": lambda: svc.review_isolation(u, cid, b.approve, b.reason),
        "field-verify": lambda: svc.field_verify(u, cid),
        "begin-repair": lambda: svc.begin_repair(u, cid, b.checklist),
        "complete": lambda: svc.complete(u, cid),
        "restore": lambda: svc.restore(u, cid, b.clearance_reason, b.reason),
        "close": lambda: svc.close(u, cid),
        "escalate": lambda: svc.escalate(u, cid),
    }
    if action not in m:
        raise HTTPException(404, "unknown action")
    _run(m[action])
    return {"ok": True, "complaint_id": cid, "action": action}

@app.get("/api/work-orders")
def work_orders(u=Depends(user)):
    return svc.get_work_orders(u)

@app.get("/api/isolation-requests")
def isolation_requests(u=Depends(user)):
    return svc.get_isolation_requests(u)

@app.get("/api/dashboard")
def dash(u=Depends(user)):
    return _run(svc.dashboard, u)

@app.get("/api/notifications")
def notes(u=Depends(user)):
    return [
        n for n in svc.notes.sent
        if n["to"] == u[0] or (u[1] in (Role.OPERATOR, Role.ADMIN) and n["to"] == "SUBSTATION")
    ]

# Serve Web Portal
TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"

@app.get("/app", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def get_app():
    if TEMPLATE_PATH.exists():
        return HTMLResponse(content=TEMPLATE_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>RESA Web Portal loading...</h2>")
