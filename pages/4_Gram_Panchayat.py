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
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, PERSONAS, Denied, Role

st.set_page_config(
    page_title="Gram Panchayat Executive Portal — RESA",
    page_icon="🏛️",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

# Ensure logged in as Panchayat
if st.session_state.get("authenticated_role") != Role.PANCHAYAT:
    st.session_state.current_user = "pan1"
    st.session_state.authenticated_role = Role.PANCHAYAT

user_tuple = get_user_tuple("pan1")
pan_info = PERSONAS["pan1"]

st.markdown(f"""
<div style="background: #fdf2f8; border: 1px solid #fbcfe8; border-left: 5px solid #db2777; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <div>
        <h3 style="margin: 0; color: #9d174d; font-size: 17px; font-weight: 700;">🏛️ Gram Panchayat Executive Dashboard</h3>
        <p style="margin: 2px 0 0 0; color: #be185d; font-size: 13px;">Logged in as: <strong>{pan_info['name']}</strong> ({pan_info['title']}) • Office: {pan_info.get('office', 'Panchayat Bhavan')}</p>
    </div>
    <div>
        <span style="background: #fce7f3; color: #9d174d; font-weight: 600; font-size: 12px; padding: 4px 10px; border-radius: 6px;">Constituency: Ward 4 Rural Block</span>
    </div>
</div>
""", unsafe_allow_html=True)

complaints = list(st.session_state.svc.c.values())
open_complaints = [c for c in complaints if c.get("status") not in ("RESOLVED", "CLOSED")]
escalated_complaints = [c for c in complaints if c.get("escalated")]

# Top Metric Cards
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Village Issues", len(complaints))
m2.metric("Active Breakdowns", len(open_complaints))
m3.metric("Urgent Escalations", len(escalated_complaints), delta="Needs Action" if escalated_complaints else "Normal")
m4.metric("Active Lineworkers", "2 Crews Deployed")

st.divider()

# 1. Village Citizens & Their Reported Issues
st.markdown("### 👥 Village Citizens & Reported Issues Directory")
st.caption("All electrical hazard reports submitted by residents within this Gram Panchayat jurisdiction.")

if not complaints:
    st.info("No complaints registered in this Panchayat territory.")
else:
    for c in reversed(complaints):
        cid = c["id"]
        status = c.get("status", "SUBMITTED")
        priority = c.get("priority", "P3")
        citizen_key = c.get("citizen", "cit1")
        citizen_data = PERSONAS.get(citizen_key, PERSONAS["cit1"])
        worker_key = c.get("worker")
        worker_data = PERSONAS.get(worker_key) if worker_key else None
        eta = c.get("eta")
        eta_reason = c.get("eta_reason")
        resources = c.get("resources_needed")
        govt_support = c.get("govt_support", [])
        is_esc = c.get("escalated", False)

        with st.container(border=True):
            r1, r2, r3 = st.columns([1.5, 1.5, 1.2])

            with r1:
                st.markdown(f"#### 🎫 Ticket `{cid}`: {c.get('category')}")
                st.markdown(f"**Citizen:** 👤 {citizen_data['name']} ({citizen_data.get('phone', 'N/A')})")
                st.markdown(f"**Location:** 📍 {c.get('desc')}")
                if is_esc:
                    st.error(f"🚨 **WORKER ESCALATION:** {c.get('escalation_reason', 'Urgent Panchayat support requested')}")

            with r2:
                st.markdown("##### 👷 Assigned Lineworker & Work Status")
                if worker_data:
                    st.markdown(f"**Lineworker:** {worker_data['icon']} **{worker_data['name']}** (Badge: `{worker_data.get('badge', 'LW-01')}`)")
                    st.markdown(f"**Feeder Line:** ⚡ `{c.get('line', 'LN-204')}`")
                    if eta:
                        st.info(f"⏱️ **Worker ETA:** **{eta}**\n\n*Delay Cause:* {eta_reason or 'None reported'}\n\n*Needed:* {resources or 'Standard tools'}")
                    else:
                        st.caption("Repair duration assessment pending from lineworker...")
                else:
                    st.warning("⚠️ Unassigned: Awaiting dispatch by Substation Control.")

            with r3:
                st.markdown("##### 📊 Status & Support")
                status_color = "#16a34a" if status in ("RESOLVED", "CLOSED") else ("#d97706" if status == "WORK_IN_PROGRESS" else "#2563eb")
                st.markdown(f"<span style='background: {status_color}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 11px;'>STATUS: {status}</span>", unsafe_allow_html=True)
                st.markdown(f"**Priority:** `{'🔴 P1 CRITICAL' if priority == 'P1' else '🔵 P3 STANDARD'}`")

                if govt_support:
                    st.markdown("**Local Govt Machinery:**")
                    for gs in govt_support:
                        st.markdown(f"- ✅ **{gs['type']}** *(Deployed)*")
                else:
                    st.caption("No government support deployed yet.")

st.divider()

# 2. Local Government Support Action Desk (Requested Feature)
st.markdown("### 🚜 Gram Panchayat Emergency Government Support Action Desk")
st.markdown("The Gram Panchayat executive can sanction and dispatch local public administration machinery to expedite power restoration:")

with st.form("panchayat_support_form", clear_on_submit=False):
    target_cid = st.selectbox(
        "Select Breakdown Grievance Ticket to Support *",
        options=[c["id"] for c in open_complaints] if open_complaints else [c["id"] for c in complaints]
    )

    sc1, sc2 = st.columns([1, 1.5])
    with sc1:
        support_choice = st.selectbox("Select Government Administration Action *", [
            "🌳 Forest / Tree Trimming Squad (Clear Fallen Branches)",
            "🚧 Police Traffic Barricades & Road Diversion",
            "🚜 Emergency JCB / Heavy Crane (Erect Damaged Pole)",
            "💡 Mobile Diesel Generator (Emergency Clinic / Water Supply)",
            "📢 Loudspeaker Public Warning & Village Announcement"
        ])
    with sc2:
        support_notes = st.text_input(
            "Administrative Sanction Notes *",
            value="Dispatched from Ward 4 Panchayat emergency development fund.",
            placeholder="e.g. Sanctioned JCB from Block Development Office for 4 hours..."
        )

    submit_support = st.form_submit_button("🚜 Dispatch Government Support & Notify Crew", type="primary", use_container_width=True)
    if submit_support:
        try:
            st.session_state.svc.provide_govt_support(user_tuple, target_cid, support_choice, support_notes)
            st.success(f"✅ Government support **{support_choice}** successfully approved for ticket `{target_cid}`! Lineworker and Citizen notified.")
            st.rerun()
        except Exception as e:
            st.error(f"Error recording government support: {str(e)}")
