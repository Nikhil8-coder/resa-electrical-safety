import sys
from pathlib import Path

_root_dir = Path(__file__).resolve().parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
_backend_dir = _root_dir / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, PERSONAS

st.set_page_config(
    page_title="Citizen Services — RESA Portal",
    page_icon="📢",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("📢 Citizen Public Grievance & Hazard Portal")
st.caption("Official consumer interface for reporting electrical hazards, snapped wires, and feeder outages.")

user_tuple = get_user_tuple("cit1")

# Quick Action Banner
st.markdown("""
<div style="background: rgba(30, 41, 59, 0.6); padding: 16px 20px; border-radius: 10px; border-left: 4px solid #38bdf8; margin-bottom: 20px;">
    <strong>Welcome, Citizen (Anita Devi).</strong> You can report life-threatening electrical hazards directly to substation engineers, or track the progress of previously filed breakdown tickets in real time.
</div>
""", unsafe_allow_html=True)

col_act1, col_act2 = st.columns(2)
with col_act1:
    if st.button("🚨 Report New Electrical Hazard / Breakdown", type="primary", use_container_width=True):
        st.switch_page("pages/2_🚨_Report_Hazard.py")
with col_act2:
    if st.button("🔍 Track Existing Ticket Status", use_container_width=True):
        st.switch_page("pages/3_🔍_Track_Complaint.py")

st.divider()

# List of My Filed Complaints
st.subheader("📋 My Registered Electrical Complaints")
complaints = st.session_state.svc.get_complaints(user_tuple)

if not complaints:
    st.info("You have not registered any electrical complaints yet. Click above to report a breakdown.")
else:
    for c in reversed(complaints):
        status_color = "green" if c.get("status") == "RESOLVED" else ("orange" if "PROGRESS" in c.get("status") else "blue")
        priority_badge = "🔴 P1 Critical Hazard" if c.get("priority") == "P1" else "🔵 Standard"
        
        with st.expander(f"**Ticket ID:** `{c['id']}` — **{c['category']}** (:{status_color}[{c['status']}])", expanded=(c.get("status") != "RESOLVED")):
            c_desc_col, c_meta_col = st.columns([1.5, 1])
            with c_desc_col:
                st.markdown(f"**Reported Issue:**\n{c['desc']}")
                st.caption(f"📍 GPS Coordinates: Latitude `{c['lat']:.4f}`, Longitude `{c['lon']:.4f}`")
                if c.get("photos"):
                    st.caption(f"📷 Attached Photo Evidence: `{', '.join(c['photos'])}`")
            with c_meta_col:
                st.markdown(f"**Priority:** {priority_badge}")
                st.markdown(f"**Assigned Feeder:** `{c.get('line') or 'Pending Triage'}`")
                st.markdown(f"**Dispatched Worker:** `{c.get('worker') or 'Pending Dispatch'}`")
                st.caption(f"🕒 Registered: {c.get('created')}")

            # Quick button to open dedicated track page for this ticket
            if st.button(f"🔍 Open Full Timeline for {c['id']}", key=f"track_btn_{c['id']}"):
                st.session_state.tracked_ticket_id = c['id']
                st.switch_page("pages/3_🔍_Track_Complaint.py")
