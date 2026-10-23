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
from shared_state import init_shared_state, render_gov_header, render_sidebar, PERSONAS, FLOW

st.set_page_config(
    page_title="Track Electrical Grievance — RESA",
    page_icon="🔍",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("🔍 Public Grievance Tracking Desk")
st.markdown("Track the live progress of electrical breakdown complaints across all 7 Indian standard operating stages.")

# Search Input
all_cids = list(st.session_state.svc.c.keys())
default_cid = st.session_state.get("tracked_ticket_id")
if not default_cid or default_cid not in all_cids:
    default_cid = all_cids[0] if all_cids else ""

col_search, _ = st.columns([1.5, 1])
with col_search:
    search_cid = st.selectbox("Select or Enter Official Ticket ID *", options=all_cids, index=all_cids.index(default_cid) if default_cid in all_cids else 0)

if not search_cid:
    st.info("No complaints found in the system registry.")
    st.stop()

comp = st.session_state.svc.c.get(search_cid)
if not comp:
    st.error(f"Grievance Ticket ID `{search_cid}` not found.")
    st.stop()

status = comp.get("status", "SUBMITTED")
priority = comp.get("priority", "P3")
worker_id = comp.get("worker")
worker_info = PERSONAS.get(worker_id) if worker_id else None
eta = comp.get("eta")
eta_reason = comp.get("eta_reason")
resources = comp.get("resources_needed")
govt_support = comp.get("govt_support", [])

with st.container(border=True):
    h1, h2 = st.columns([2, 1])
    with h1:
        st.subheader(f"🎫 Grievance #{search_cid}: {comp.get('category')}")
        st.markdown(f"**Reported Incident:** {comp.get('desc')}")
        st.markdown(f"**GPS Location:** `{comp.get('lat', 17.3850):.4f} N, {comp.get('lon', 78.4867):.4f} E`")
    with h2:
        status_color = "#16a34a" if status in ("RESOLVED", "CLOSED") else ("#d97706" if status == "WORK_IN_PROGRESS" else "#2563eb")
        st.markdown(f"<div style='text-align: right;'><span style='background: {status_color}; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 13px;'>STATUS: {status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: right; margin-top: 8px;'><span style='color: {'#dc2626' if priority == 'P1' else '#475569'}; font-weight: 700;'>PRIORITY: {priority}</span></div>", unsafe_allow_html=True)

    st.markdown("#### ⚡ 7-Stage Indian Electrical Safety SOP Lifecycle")
    curr_idx = FLOW.index(status) if status in FLOW else 0
    step_cols = st.columns(len(FLOW))
    for i, step in enumerate(FLOW):
        with step_cols[i]:
            is_active = (i <= curr_idx)
            icon = "✅" if i < curr_idx else ("▶️" if i == curr_idx else "⚪")
            step_label = step.replace("_", " ").title()
            st.markdown(f"<div style='font-size: 11px; text-align: center; color: {'#16a34a' if is_active else '#94a3b8'}; font-weight: {'700' if is_active else '400'};'>{icon}<br>{step_label}</div>", unsafe_allow_html=True)

    st.divider()

    st1, st2 = st.columns(2)
    with st1:
        st.markdown("##### 🛠️ Field Lineworker & Arrival Time")
        if worker_info:
            st.markdown(f"**Lineworker:** {worker_info['icon']} **{worker_info['name']}** (Badge: `{worker_info.get('badge', 'LW-01')}`)")
            if eta:
                st.info(f"⏱️ **Estimated Duration:** **{eta}**\n\n**Reason:** {eta_reason or 'Work under execution'}\n\n**Equipment Needed:** {resources or 'Standard Lineworker Toolkit'}")
            else:
                st.caption("Lineworker assigned; inspecting site.")
        else:
            st.caption("Awaiting lineworker dispatch from Substation Control.")

    with st2:
        st.markdown("##### 🏛️ Gram Panchayat Government Support")
        if govt_support:
            for gs in govt_support:
                st.success(f"🚜 **Support Sanctioned:** **{gs['type']}**\n\n*Notes:* {gs.get('notes', 'Deployed by Gram Panchayat')}")
        else:
            st.caption("No additional local administration machinery needed.")

    # Timeline Log
    if comp.get("timeline"):
        st.divider()
        st.markdown("##### 📜 Official Audit Timeline")
        for entry in comp["timeline"]:
            ts_str = entry.get("timestamp") or "Just now"
            st.markdown(f"- `{ts_str}`: **{entry.get('stage')}** — {entry.get('note', '')}")
