import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, FLOW

st.set_page_config(
    page_title="Track Breakdown Ticket — RESA",
    page_icon="🔍",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("🔍 Official Breakdown Ticket Status Tracker")
st.caption("Public verification desk. Track real-time repair progress, lineworker dispatch, and power restoration clearances.")

user_tuple = get_user_tuple("cit1")

all_tickets = list(st.session_state.svc.c.keys())
default_search = st.session_state.get("tracked_ticket_id", all_tickets[-1] if all_tickets else "")

col_search, col_spacer = st.columns([2, 1])
with col_search:
    search_cid = st.text_input(
        "Enter Official Ticket Reference ID:",
        value=default_search,
        placeholder="e.g. RESA-2026-000245",
        help="Paste or enter the 16-character RESA ticket ID generated upon submission."
    ).strip()

if not search_cid:
    st.info("Please enter a Ticket ID above to inspect current restoration progress.")
    if all_tickets:
        st.markdown("**Recent Registered Tickets in System:**")
        quick_cols = st.columns(min(len(all_tickets), 4))
        for i, q_cid in enumerate(reversed(all_tickets[-4:])):
            with quick_cols[i]:
                if st.button(f"🔍 Inspect {q_cid}", key=f"quick_{q_cid}", use_container_width=True):
                    st.session_state.tracked_ticket_id = q_cid
                    st.rerun()
else:
    c = st.session_state.svc.c.get(search_cid)
    if not c:
        st.error(f"❌ Ticket Reference **`{search_cid}`** not found in utility registry. Please verify your reference number.")
    else:
        st.divider()

        # Visual 7-Stage Stepper
        st.subheader("📊 7-Stage Digital Restoration Lifecycle")
        
        current_status = c.get("status", "SUBMITTED")
        current_idx = FLOW.index(current_status) if current_status in FLOW else 0

        step_cols = st.columns(len(FLOW))
        for idx, step_name in enumerate(FLOW):
            with step_cols[idx]:
                if idx < current_idx:
                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; border-radius: 8px; padding: 10px 4px; text-align: center;">
                        <span style="color: #10b981; font-size: 16px;">✓</span><br>
                        <strong style="color: #10b981; font-size: 10px; display: block; margin-top: 4px;">{step_name}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                elif idx == current_idx:
                    st.markdown(f"""
                    <div style="background: rgba(59, 130, 246, 0.3); border: 2px solid #3b82f6; border-radius: 8px; padding: 10px 4px; text-align: center; box-shadow: 0 0 10px rgba(59,130,246,0.3);">
                        <span style="color: #3b82f6; font-size: 16px;">⚡</span><br>
                        <strong style="color: #ffffff; font-size: 10px; display: block; margin-top: 4px;">{step_name}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid #334155; border-radius: 8px; padding: 10px 4px; text-align: center;">
                        <span style="color: #64748b; font-size: 16px;">•</span><br>
                        <span style="color: #64748b; font-size: 10px; display: block; margin-top: 4px;">{step_name}</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Worker Estimated Time (ETA) Highlight
        if c.get("eta"):
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.2); border: 2px solid #f59e0b; padding: 16px; border-radius: 10px; margin-bottom: 16px;">
                <h4 style="margin: 0 0 6px 0; color: #fbbf24;">⏱️ Field Lineworker Repair Time Estimate</h4>
                <p style="margin: 0; font-size: 14px; color: #ffffff;">
                    <strong>Estimated Time to Restore Power:</strong> <span style="font-size: 16px; font-weight: 800; color: #fef08a;">{c['eta']}</span><br>
                    <strong>Delay / Root Cause Reason:</strong> {c.get('eta_reason') or 'Standard repair'}<br>
                    {f"<strong>Materials / Equipment Required:</strong> {c.get('resources_needed')}" if c.get('resources_needed') else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Government / Panchayat Support Highlight
        if c.get("govt_support"):
            st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 14px; border-radius: 10px; margin-bottom: 16px;">
                <h5 style="margin: 0 0 4px 0; color: #10b981;">🏛️ Gram Panchayat Government Support Provided</h5>
            """, unsafe_allow_html=True)
            for sup in c["govt_support"]:
                st.markdown(f"- **{sup['type']}**: {sup['notes']} *(Approved by {sup['by']})*")
            st.markdown("</div>", unsafe_allow_html=True)

        # Ticket Information Card
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px;">
                <h4 style="margin: 0 0 10px 0; color: #f8fafc;">📋 Incident Details</h4>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Ticket ID:</strong> <code>{c['id']}</code></p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Hazard Category:</strong> {c['category']}</p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Priority Level:</strong> {'🔴 P1 Maximum Hazard' if c.get('priority') == 'P1' else '🔵 P3 Standard'}</p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Location Coordinates:</strong> Lat {c['lat']:.4f}, Lon {c['lon']:.4f}</p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 0;"><strong>Consumer Description:</strong> {c['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_info2:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px;">
                <h4 style="margin: 0 0 10px 0; color: #f8fafc;">🛠️ Dispatch & Restoration Status</h4>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Feeder Grid Line:</strong> <code>{c.get('line') or 'Pending Assignment'}</code></p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Assigned Lineman:</strong> <code>{c.get('worker') or 'Pending Dispatch'}</code></p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Current Status:</strong> <strong style="color: {'#10b981' if current_status == 'RESOLVED' else '#3b82f6'};">{current_status}</strong></p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 6px;"><strong>Date Registered:</strong> {c.get('created')}</p>
                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 0;"><strong>Power Restored:</strong> {c.get('resolved') or 'Restoration In Progress'}</p>
            </div>
            """, unsafe_allow_html=True)

        # Chronological Audit History
        st.subheader("📜 Official Chronological Timeline Log")
        timeline = c.get("timeline", [])
        if not timeline:
            st.caption("No timeline transitions recorded yet.")
        else:
            for entry in timeline:
                ts, status_label, note = entry[0], entry[1], (entry[2] if len(entry) > 2 else "")
                st.markdown(f"- 🕒 `{ts}` — **{status_label}** {'— *' + note + '*' if note else ''}")

st.divider()
c_back1, c_back2 = st.columns(2)
with c_back1:
    if st.button("← Back to Citizen Services", use_container_width=True):
        st.switch_page("pages/1_📢_Citizen_Services.py")
with c_back2:
    if st.button("🚨 Report Another Hazard", type="primary", use_container_width=True):
        st.switch_page("pages/2_🚨_Report_Hazard.py")
