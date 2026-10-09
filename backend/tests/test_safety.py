import sqlite3, pytest
from app.workflows.safety import Grid, Denied
T = "RESA-2026-000245"
def g(): return Grid(["LN-204"])
def run(g, steps):
    for who, role, tgt, kw in steps: g.transition(who, role, "LN-204", tgt, T, **kw)
OK = dict(reason="per SOP", confirm=True)
FULL = [("w","LINE_WORKER","MAINTENANCE_REQUESTED",{}), ("w","LINE_WORKER","ISOLATION_REQUESTED",{}),
 ("o","SUBSTATION_OPERATOR","ISOLATION_CONFIRMED",OK), ("w","LINE_WORKER","FIELD_SAFETY_VERIFICATION",{}),
 ("w","LINE_WORKER","WORK_IN_PROGRESS",dict(field_checklist=True)), ("w","LINE_WORKER","WORK_COMPLETED",{}),
 ("o","SUBSTATION_OPERATOR","CLEARANCE_CONFIRMED",OK), ("o","SUBSTATION_OPERATOR","RESTORATION_AUTHORIZED",OK),
 ("o","SUBSTATION_OPERATOR","NORMAL",OK)]
def test_full_cycle_and_audit():
    x = g(); run(x, FULL); assert x.state["LN-204"].value == "NORMAL" and len(x.audit()) == 9
def test_wip_cannot_jump_to_normal():
    x = g(); run(x, FULL[:5])
    with pytest.raises(Denied): x.transition("o","SUBSTATION_OPERATOR","LN-204","NORMAL",T,reason="r",confirm=True)
def test_worker_cannot_confirm_isolation():
    x = g(); run(x, FULL[:2])
    with pytest.raises(Denied): x.transition("w","LINE_WORKER","LN-204","ISOLATION_CONFIRMED",T,reason="r",confirm=True)
def test_operator_needs_confirm_and_reason():
    x = g(); run(x, FULL[:2])
    with pytest.raises(Denied): x.transition("o","SUBSTATION_OPERATOR","LN-204","ISOLATION_CONFIRMED",T)
def test_field_checklist_required():
    x = g(); run(x, FULL[:4])
    with pytest.raises(Denied): x.transition("w","LINE_WORKER","LN-204","WORK_IN_PROGRESS",T)
def test_citizen_denied_and_denial_audited():
    x = g()
    with pytest.raises(Denied): x.transition("c","CITIZEN","LN-204","MAINTENANCE_REQUESTED",T)
    assert x.audit()[0][-1].startswith("DENIED")
def test_audit_immutable():
    x = g(); run(x, FULL[:1])
    with pytest.raises(sqlite3.DatabaseError): x.db.execute("DELETE FROM audit")
