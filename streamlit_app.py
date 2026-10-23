import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, PERSONAS

st.set_page_config(
    page_title="RESA — National Electrical Safety & Grievance Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_shared_state()
render_gov_header()
render_sidebar()

# Official Banner
st.markdown("""
<div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); padding: 24px; border-radius: 12px; margin-bottom: 24px;">
    <h2 style="color: #f8fafc; font-weight: 800; margin-bottom: 6px;">National Electrical Breakdown & Safety Management System</h2>
    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 0;">
        Welcome to the official <strong>RESA Portal</strong>. This portal provides segregated, specialized digital services for citizens to report electrical hazards, substation officers to manage line isolations, lineworkers to enforce mandatory Lock-Out / Tag-Out (LOTO) safety, and panchayat representatives to monitor public safety SLAs.
    </p>
</div>
""", unsafe_allow_html=True)

# Persona Switcher for convenient testing
st.markdown("#### 🔑 Quick Persona Switcher & Session Access")
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
with col_p1:
    if st.button("👤 Citizen (cit1)", use_container_width=True, type="primary" if st.session_state.current_user == "cit1" else "secondary"):
        st.session_state.current_user = "cit1"
        st.rerun()
with col_p2:
    if st.button("⚡ Operator (op1)", use_container_width=True, type="primary" if st.session_state.current_user == "op1" else "secondary"):
        st.session_state.current_user = "op1"
        st.rerun()
with col_p3:
    if st.button("🛠️ Worker (worker1)", use_container_width=True, type="primary" if st.session_state.current_user == "worker1" else "secondary"):
        st.session_state.current_user = "worker1"
        st.rerun()
with col_p4:
    if st.button("🏛️ Panchayat (pan1)", use_container_width=True, type="primary" if st.session_state.current_user == "pan1" else "secondary"):
        st.session_state.current_user = "pan1"
        st.rerun()
with col_p5:
    if st.button("🛡️ Admin (admin)", use_container_width=True, type="primary" if st.session_state.current_user == "admin" else "secondary"):
        st.session_state.current_user = "admin"
        st.rerun()

st.divider()

# Portal Directory Cards (Dedicated Pages)
st.markdown("### 🏛️ Dedicated Departmental Portals")
st.caption("Select your department below to access your dedicated, uncluttered portal:")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px; height: 100%;">
        <div style="font-size: 28px; margin-bottom: 8px;">📢 <strong>Citizen Services Portal</strong></div>
        <p style="color: #cbd5e1; font-size: 13px;">
            Public portal for consumers and rural citizens. File high-priority electrical hazard reports with automatic GPS tagging and photo uploads.
        </p>
    </div>
    """, unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🚨 Report Hazard Page", key="btn_rep_haz", use_container_width=True, type="primary"):
            st.switch_page("pages/2_🚨_Report_Hazard.py")
    with c_btn2:
        if st.button("🔍 Track Ticket Page", key="btn_tr_comp", use_container_width=True):
            st.switch_page("pages/3_🔍_Track_Complaint.py")

with row1_col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px; height: 100%;">
        <div style="font-size: 28px; margin-bottom: 8px;">⚡ <strong>Substation Control Room</strong></div>
        <p style="color: #cbd5e1; font-size: 13px;">
            Authorized terminal for substation control engineers. Real-time feeder line monitoring, incident triage, work order dispatching, and digital line isolation permits.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Open Substation Desk", key="btn_open_op", use_container_width=True, type="primary"):
        st.session_state.current_user = "op1"
        st.switch_page("pages/4_⚡_Substation_Control.py")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px; height: 100%;">
        <div style="font-size: 28px; margin-bottom: 8px;">🛠️ <strong>Field Lineworker Terminal (LOTO)</strong></div>
        <p style="color: #cbd5e1; font-size: 13px;">
            Field technician terminal. Review dispatched job orders, request digital line isolations, and complete mandatory 4-step OSHA/IEEE Lock-Out / Tag-Out verifications.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🛠️ Open Lineworker Terminal", key="btn_open_wrk", use_container_width=True, type="primary"):
        st.session_state.current_user = "worker1"
        st.switch_page("pages/5_🛠️_Line_Worker_LOTO.py")

with row2_col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px; height: 100%;">
        <div style="font-size: 28px; margin-bottom: 8px;">🏛️ <strong>Panchayat & Executive KPI Desk</strong></div>
        <p style="color: #cbd5e1; font-size: 13px;">
            Executive dashboard for Gram Panchayat leaders and distribution utility directors. Real-time resolution metrics, incident category distributions, and SLA timers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏛️ Open Panchayat Dashboard", key="btn_open_pan", use_container_width=True, type="primary"):
        st.session_state.current_user = "pan1"
        st.switch_page("pages/6_🏛️_Panchayat_Executive.py")

st.divider()

# Public Audit Registry & Simulation Row
st.markdown("### 🔒 Public Statutory Registry & Simulator")
c_aud, c_sim = st.columns(2)
with c_aud:
    st.info("📜 **Statutory Safety Audit Registry**: Cryptographically trigger-enforced logs of all feeder line state changes and LOTO verifications.")
    if st.button("🔒 View Immutable Audit Trail", use_container_width=True):
        st.switch_page("pages/7_🔒_Safety_Audit_Trail.py")

with c_sim:
    st.success("▶ **10-Stage SOP Lifecycle Simulator**: Live interactive demonstration showing end-to-end hazard reporting, triage, isolation, and safe restoration.")
    if st.button("▶ Open Automated SOP Simulator", use_container_width=True):
        st.switch_page("pages/8_▶_Automated_SOP_Simulator.py")
