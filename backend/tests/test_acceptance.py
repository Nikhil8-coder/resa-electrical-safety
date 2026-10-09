import pytest
from app.services.resa import Resa
from app.workflows.safety import Denied
CIT, WRK, OP, PAN = ("cit1","CITIZEN"), ("w1","LINE_WORKER"), ("op1","SUBSTATION_OPERATOR"), ("pan1","PANCHAYAT_ADMIN")
def test_mvp_scenario_end_to_end():
    r = Resa(["LN-204"])
    cid = r.create(CIT, "Transformer Failure", "Humming, smoke", 17.38, 78.48, ["a.jpg"]); assert cid.startswith("RESA-2026-")
    r.acknowledge(OP, cid); r.assign(OP, cid, "w1", "LN-204")
    r.start(WRK, cid); r.request_isolation(WRK, cid, "Replace fuse")
    r.review_isolation(OP, cid, True, "Isolated per SOP, permit issued")
    r.field_verify(WRK, cid); r.begin_repair(WRK, cid, True); r.complete(WRK, cid)
    r.restore(OP, cid, "Clearance checked", "Restore per SOP")
    assert r.view(CIT, cid)["status"] == "RESOLVED" and r.grid.state["LN-204"].value == "NORMAL"
    assert any(n["event"] == "RESOLVED" and n["to"] == "cit1" for n in r.notes.sent)
    assert r.dashboard(PAN)["resolved"] == 1 and len(r.grid.audit()) == 9
def test_idor_and_rbac():
    r = Resa(["LN-204"]); cid = r.create(CIT, "Power Outage", "x", 1, 1)
    with pytest.raises(Denied): r.view(("cit2","CITIZEN"), cid)
    with pytest.raises(Denied): r.acknowledge(CIT, cid)
    with pytest.raises(Denied): r.dashboard(CIT)
def test_worker_cannot_skip_isolation_or_reach_unassigned():
    r = Resa(["LN-204"]); cid = r.create(CIT, "Fallen Pole", "x", 1, 1); r.acknowledge(OP, cid); r.assign(OP, cid, "w1", "LN-204")
    with pytest.raises(Denied): r.start(("w2","LINE_WORKER"), cid)
    r.start(WRK, cid)
    with pytest.raises(Denied): r.begin_repair(WRK, cid, True)
def test_invalid_input():
    r = Resa(["LN-204"])
    with pytest.raises(Denied): r.create(CIT, "Bogus", "x", 1, 1)
    with pytest.raises(Denied): r.create(CIT, "Other", "x", 999, 1)
    with pytest.raises(Denied): r.create(CIT, "Other", "x", 1, 1, ["shell.exe"])
