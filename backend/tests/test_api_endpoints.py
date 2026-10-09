from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_and_auth_profile():
    # 1. Valid login for worker1
    r = client.post("/api/auth/login", json={"username": "worker1", "password": "change-me"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "token" in data
    assert data["username"] == "worker1"
    assert data["role"] == "LINE_WORKER"
    worker_tok = data["token"]

    # 2. Check /api/auth/me profile
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {worker_tok}"})
    assert r.status_code == 200
    me = r.json()
    assert me["username"] == "worker1"
    assert me["role"] == "LINE_WORKER"

    # 3. Valid login for admin
    r = client.post("/api/auth/login", json={"username": "admin", "password": "change-me"})
    assert r.status_code == 200
    admin_data = r.json()
    assert admin_data["role"] == "SYSTEM_ADMIN"
    admin_tok = admin_data["token"]

    # 4. Check available users
    r = client.get("/api/users", headers={"Authorization": f"Bearer {admin_tok}"})
    assert r.status_code == 200
    users = r.json()
    assert any(u["username"] == "worker1" for u in users)

    # 5. Invalid credentials rejection
    r = client.post("/api/auth/login", json={"username": "worker1", "password": "wrong-password"})
    assert r.status_code == 401

    # 6. Unauthenticated me endpoint
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert r.status_code == 401

def test_grid_lines_and_complaint_flow():
    # Logins
    cit_tok = client.post("/api/auth/login", json={"username": "cit1", "password": "change-me"}).json()["token"]
    op_tok = client.post("/api/auth/login", json={"username": "op1", "password": "change-me"}).json()["token"]
    wrk_tok = client.post("/api/auth/login", json={"username": "worker1", "password": "change-me"}).json()["token"]

    # Check grid lines
    r = client.get("/api/grid/lines", headers={"Authorization": f"Bearer {cit_tok}"})
    assert r.status_code == 200
    assert "LN-204" in r.json()

    # Create complaint
    r = client.post("/api/complaints", json={
        "category": "Broken Electrical Line",
        "description": "Snapped line on highway pole 12",
        "lat": 17.385,
        "lon": 78.486,
        "photos": ["evidence.jpg"]
    }, headers={"Authorization": f"Bearer {cit_tok}"})
    assert r.status_code == 200, r.text
    cid = r.json()["id"]
    assert cid.startswith("RESA-2026-")

    # Citizen views complaint
    r = client.get(f"/api/complaints/{cid}", headers={"Authorization": f"Bearer {cit_tok}"})
    assert r.status_code == 200
    assert r.json()["status"] == "SUBMITTED"

    # Operator acknowledges
    r = client.post(f"/api/complaints/{cid}/acknowledge", json={}, headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200

    # Operator assigns to worker1 on LN-204
    r = client.post(f"/api/complaints/{cid}/assign", json={"worker": "worker1", "line": "LN-204"}, headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200

    # Worker checks work orders
    r = client.get("/api/work-orders", headers={"Authorization": f"Bearer {wrk_tok}"})
    assert r.status_code == 200
    wos = r.json()
    assert any(wo["complaint_id"] == cid for wo in wos)

    # Worker starts
    r = client.post(f"/api/complaints/{cid}/start", json={}, headers={"Authorization": f"Bearer {wrk_tok}"})
    assert r.status_code == 200

    # Worker requests isolation
    r = client.post(f"/api/complaints/{cid}/isolation-request", json={"reason": "Safety fuse replacement"}, headers={"Authorization": f"Bearer {wrk_tok}"})
    assert r.status_code == 200

    # Isolation requests listed
    r = client.get("/api/isolation-requests", headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200
    assert any(req["complaint_id"] == cid for req in r.json())

    # Operator reviews and approves isolation
    r = client.post(f"/api/complaints/{cid}/isolation-review", json={"approve": True, "reason": "Breaker locked and tagged per SOP"}, headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200

    # Worker field-verifies
    r = client.post(f"/api/complaints/{cid}/field-verify", json={}, headers={"Authorization": f"Bearer {wrk_tok}"})
    assert r.status_code == 200

    # Worker begins repair with checklist
    r = client.post(f"/api/complaints/{cid}/begin-repair", json={"checklist": True}, headers={"Authorization": f"Bearer {wrk_tok}"})
    assert r.status_code == 200

    # Worker completes
    r = client.post(f"/api/complaints/{cid}/complete", json={}, headers={"Authorization": f"Bearer {wrk_tok}"})
    assert r.status_code == 200

    # Operator restores power
    r = client.post(f"/api/complaints/{cid}/restore", json={"clearance_reason": "Field clearance checked", "reason": "Restoration per SOP"}, headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200

    # Final verification
    r = client.get(f"/api/complaints/{cid}", headers={"Authorization": f"Bearer {cit_tok}"})
    assert r.status_code == 200
    assert r.json()["status"] == "RESOLVED"

    # Operator checks audit log
    r = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200
    assert len(r.json()) >= 9

    # Check dashboard
    r = client.get("/api/dashboard", headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 200
    assert r.json()["resolved"] >= 1
