import sys
from pathlib import Path

# Ensure root and backend directories in python path for Streamlit Cloud
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
_backend = _root / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, PERSONAS, Role

st.set_page_config(
    page_title="RESA — National Electrical Safety & Grievance Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
    <h1 style="color: #0b1e36; margin-bottom: 6px; font-weight: 800;">National Electrical Safety & Breakdown Coordination Portal</h1>
    <p style="color: #475569; font-size: 16px; max-width: 800px; margin: 0 auto;">
        Government of India official digital gateway for reporting power breakdown hazards, coordinating field lineworker repairs, and dispatching Gram Panchayat emergency administrative support.
    </p>
</div>
""", unsafe_allow_html=True)

# Active session reminder if already logged in
current_user = st.session_state.get("current_user")
if current_user and current_user in PERSONAS:
    p = PERSONAS[current_user]
    st.info(f"🔑 **Active Identity:** You are currently logged in as **{p['icon']} {p['name']}** (`{p['title']}`).")

st.markdown("### 🏛️ Select Your Identity & Login Portal")
st.markdown("Before entering the system, please identify who you are. Each stakeholder has a dedicated, uncluttered portal designed for their specific official responsibilities:")

col1, col2 = st.columns(2)

with col1:
    # 1. Citizen Login Card
    with st.container(border=True):
        st.markdown("### 👤 Citizen / Consumer Portal")
        st.caption("Public Access • Energy Consumers & Rural Residents")
        st.markdown("""
        * **Report Electrical Hazards:** Snapped wires, sparking transformers, leaning poles.
        * **Live Complaint Tracker:** Follow your grievance through the 7-stage Indian SOP.
        * **Lineworker Arrival Time (ETA):** See real-time repair progress and delay explanations.
        * **Gram Panchayat Support Updates:** View local government machinery deployed.
        """)
        st.markdown(f"**Demo Profile:** `Anita Devi (Citizen - Ward 4)`")
        if st.button("👤 Login as Citizen ➔", type="primary", use_container_width=True, key="login_citizen_btn"):
            st.session_state.current_user = "cit1"
            st.session_state.authenticated_role = Role.CITIZEN
            st.switch_page("pages/1_Citizen_Portal.py")

    # 3. Gram Panchayat Login Card
    with st.container(border=True):
        st.markdown("### 🏛️ Gram Panchayat Executive Portal")
        st.caption("Local Self-Government • Public Representatives")
        st.markdown("""
        * **Village Citizens Directory:** View all electrical issues raised in your Panchayat area.
        * **Lineworker Monitoring:** Track assigned field repair teams and live work status.
        * **Repair Delays & Requirements:** See lineworker ETA, delay reasons, and needed equipment.
        * **1-Click Government Support:** Dispatch Tree Clearance squads, Police barricades, or JCBs.
        """)
        st.markdown(f"**Demo Profile:** `Panchayat Head (Ward 4 - Gram Panchayat)`")
        if st.button("🏛️ Login as Gram Panchayat ➔", type="primary", use_container_width=True, key="login_panchayat_btn"):
            st.session_state.current_user = "pan1"
            st.session_state.authenticated_role = Role.PANCHAYAT
            st.switch_page("pages/4_Gram_Panchayat.py")

with col2:
    # 2. Lineworker Login Card
    with st.container(border=True):
        st.markdown("### 🛠️ Field Lineworker Terminal")
        st.caption("Authorized Field Crew • Distribution Maintenance")
        st.markdown("""
        * **Breakdown Area Location:** GPS coordinates, feeder line, and pole landmarks.
        * **Time & Delay Estimator:** Submit needed hours/days, delay causes, and material needs.
        * **Panchayat Escalation:** Request emergency local administration machinery (JCB/Trees).
        * **LOTO Safety Verification:** 4-Point safety checklist before working on de-energized lines.
        """)
        st.markdown(f"**Demo Profile:** `Rajesh Kumar (Field Lineworker - Team A)`")
        if st.button("🛠️ Login as Lineworker ➔", type="primary", use_container_width=True, key="login_worker_btn"):
            st.session_state.current_user = "worker1"
            st.session_state.authenticated_role = Role.WORKER
            st.switch_page("pages/3_Lineworker_Terminal.py")

    # 4. Substation Control Room Card
    with st.container(border=True):
        st.markdown("### ⚡ Substation Control Room Desk")
        st.caption("Grid Engineers • 33kV / 11kV Operations")
        st.markdown("""
        * **Feeder Telemetry:** Monitor real-time electrical load on LN-204, LN-205, and LN-311.
        * **Permit-to-Work (PTW):** Authorize feeder isolation requests submitted by field crews.
        * **Safety Clearance:** Verify digital Lock-Out/Tag-Out release before restoring power.
        * **Restoration Dispatch:** Safe re-energization conforming to Central Electricity Authority SOPs.
        """)
        st.markdown(f"**Demo Profile:** `Sunil Sharma (Substation Control Officer)`")
        if st.button("⚡ Login as Substation Operator ➔", type="primary", use_container_width=True, key="login_operator_btn"):
            st.session_state.current_user = "op1"
            st.session_state.authenticated_role = Role.OPERATOR
            st.switch_page("pages/5_Substation_Control.py")

st.divider()

st.markdown("### 🔗 Quick Direct Access Links")
qc1, qc2, qc3, qc4 = st.columns(4)
with qc1:
    if st.button("🚨 Direct Hazard Report", use_container_width=True):
        st.switch_page("pages/2_Report_Hazard.py")
with qc2:
    if st.button("🔍 Public Grievance Tracker", use_container_width=True):
        st.switch_page("pages/6_Track_Complaint.py")
with qc3:
    if st.button("🔒 Statutory Safety Audit Log", use_container_width=True):
        st.switch_page("pages/7_Safety_Audit_Trail.py")
with qc4:
    if st.button("▶ 10-Stage SOP Simulator", use_container_width=True):
        st.switch_page("pages/8_SOP_Simulator.py")
