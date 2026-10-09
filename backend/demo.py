"""Cross-platform demo: run while `uvicorn app.main:app` is running. Usage: python demo.py"""
import json, os, urllib.request
B, PW = "http://127.0.0.1:8000", os.getenv("DEMO_PW", "change-me")
def call(path, body=None, tok=None):
    h = {"Content-Type": "application/json"}
    if tok: h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(B + path, json.dumps(body).encode() if body is not None else None, h)
    return json.load(urllib.request.urlopen(req))
tok = lambda u: call("/api/auth/login", {"username": u, "password": PW})["token"]
CIT, OP, WK = tok("cit1"), tok("op1"), tok("worker1")
cid = call("/api/complaints", dict(category="Transformer Failure", description="Smoke", lat=17.38, lon=78.48, photos=["a.jpg"]), CIT)["id"]
print("Complaint", cid)
for t, a, b in [(OP,"acknowledge",{}), (OP,"assign",{"worker":"worker1","line":"LN-204"}), (WK,"start",{}),
    (WK,"isolation-request",{"reason":"Replace fuse"}), (OP,"isolation-review",{"approve":True,"reason":"Isolated per SOP, permit issued"}),
    (WK,"field-verify",{}), (WK,"begin-repair",{"checklist":True}), (WK,"complete",{}),
    (OP,"restore",{"clearance_reason":"Clearance checked","reason":"Restore per SOP"})]:
    print(a, call(f"/api/complaints/{cid}/{a}", b, t))
print("Status:", call(f"/api/complaints/{cid}", None, CIT)["status"])
print("Audit rows:", len(call("/api/audit-logs", None, OP)))
