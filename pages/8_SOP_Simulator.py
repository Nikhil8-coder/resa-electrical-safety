import sys
from pathlib import Path

# Ensure root and backend package are in python path
_root_dir = Path(__file__).resolve().parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
_backend_dir = _root_dir / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, Role, S, Denied

st.set_page_config(
    page_title="10-Stage SOP Simulator — RESA",
    page_icon="▶️",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("▶️ 10-Stage Electrical Breakdown & Safety SOP Simulator")
st.markdown("Interactive demonstration of the complete life-cycle of a high-voltage electrical breakdown incident, from citizen dispatch to safe power restoration.")

STAGES = [
    {"num": 1, "title": "Citizen Hazard Report", "role": "👤 Citizen Anita Devi", "action": "Report 11kV severed conductor on village road."},
    {"num": 2, "title": "Substation Triage & Acknowledgment", "role": "⚡ Substation Operator Sunil Sharma", "action": "Acknowledge P1 Critical Hazard and assign Lineworker Rajesh Kumar."},
    {"num": 3, "title": "Lineworker Dispatch & ETA Reporting", "role": "🛠️ Lineworker Rajesh Kumar", "action": "Inspect site and declare ETA: 2 Hours with delay details and parts needed."},
    {"num": 4, "title": "Panchayat Escalation & Machinery", "role": "🏛️ Gram Panchayat Head", "action": "Dispatch emergency JCB & Tree Clearance crew to remove tangled branches."},
    {"num": 5, "title": "Feeder Isolation Request", "role": "🛠️ Lineworker Rajesh Kumar", "action": "Request Substation to trip feeder LN-204 and apply gang isolator switch."},
    {"num": 6, "title": "Substation Isolation & Permit-to-Work", "role": "⚡ Substation Operator Sunil Sharma", "action": "Rack out 11kV circuit breaker and issue electronic Permit-to-Work (PTW)."},
    {"num": 7, "title": "Field LOTO Verification", "role": "🛠️ Lineworker Rajesh Kumar", "action": "Verify Zero Voltage, apply portable earthing leads, affix padlock, and don PPE."},
    {"num": 8, "title": "Repair Execution (Work in Progress)", "role": "🛠️ Lineworker Rajesh Kumar", "action": "Splice ACSR conductor across 3 spans, replace pin insulators, clear site."},
    {"num": 9, "title": "Work Completed & LOTO Clearance", "role": "🛠️ Lineworker Rajesh Kumar", "action": "Remove earth leads, release padlock, declare all men and materials clear."},
    {"num": 10, "title": "Substation Restoration & Closure", "role": "⚡ Substation Operator Sunil Sharma", "action": "Close gang isolator, re-energize LN-204, notify citizen of power restoration."}
]

if "sim_stage" not in st.session_state:
    st.session_state.sim_stage = 1

curr = st.session_state.sim_stage

# Progress bar
st.progress(curr / 10.0, text=f"Stage {curr} of 10: {STAGES[curr - 1]['title']}")

stage_info = STAGES[curr - 1]

with st.container(border=True):
    st.markdown(f"### Stage {curr}: {stage_info['title']}")
    st.markdown(f"**Responsible Stakeholder:** {stage_info['role']}")
    st.markdown(f"**Operational Action:** {stage_info['action']}")

    st.divider()

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("⬅️ Previous Stage", disabled=(curr <= 1), use_container_width=True):
            st.session_state.sim_stage -= 1
            st.rerun()
    with c2:
        if curr < 10:
            if st.button("Next Stage ➔", type="primary", use_container_width=True):
                # Safely advance underlying service if simulator ticket exists
                try:
                    sim_cid = "SIM-DEMO"
                    if curr == 5:
                        st.session_state.svc.request_isolation(("worker1", Role.WORKER), sim_cid, "SOP Simulation Isolation")
                    elif curr == 6:
                        st.session_state.svc.review_isolation(("op1", Role.OPERATOR), sim_cid, approve=True, reason="SOP Simulation Approved")
                    elif curr == 7:
                        st.session_state.svc.field_verify(("worker1", Role.WORKER), sim_cid)
                    elif curr == 8:
                        st.session_state.svc.begin_repair(("worker1", Role.WORKER), sim_cid, checklist_done=True)
                    elif curr == 9:
                        st.session_state.svc.complete(("worker1", Role.WORKER), sim_cid)
                    elif curr == 10:
                        st.session_state.svc.restore(("op1", Role.OPERATOR), sim_cid, "Sim clearance", "Sim restore")
                except Exception:
                    pass
                st.session_state.sim_stage += 1
                st.rerun()
        else:
            if st.button("🔄 Restart Simulator", type="primary", use_container_width=True):
                st.session_state.sim_stage = 1
                st.rerun()

    with c3:
        st.caption("Central Electricity Authority (Safety & Electric Supply) Regulations Compliant Workflow")
