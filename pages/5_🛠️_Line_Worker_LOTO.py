import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, Denied

st.set_page_config(
    page_title="Line Worker LOTO Safety — RESA",
    page_icon="🛠️",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("🛠️ Field Lineworker Safety Terminal & LOTO Desk")
st.caption("Authorized Maintenance Technician: Rajesh Kumar (worker1) • Emergency Breakdown Rapid Response Crew")

user_tuple = get_user_tuple("worker1")

st.markdown("""
<div style="background: rgba(245, 158, 11, 0.15); border-left: 4px solid #f59e0b; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
    ⚠️ <strong>STATUTORY SAFETY DIRECTIVE:</strong> Never physically touch any conductor until (1) Substation digital isolation permit is confirmed, (2) Calibrated detector verifies zero energy, and (3) Portable ground earthing sets are clamped.
</div>
""", unsafe_allow_html=True)

col_orders, col_loto = st.columns([1.1, 1.4])

# Left Column: Dispatched Job Orders
with col_orders:
    st.subheader("📋 Dispatched Job Orders Queue")
    orders = st.session_state.svc.get_work_orders(user_tuple)

    if not orders:
        st.info("No active work orders currently assigned to lineworker worker1.")
        selected_cid = None
    else:
        order_options = [o["complaint_id"] for o in orders]
        selected_cid = st.selectbox(
            "Select Active Incident Job Ticket:",
            options=order_options,
            format_func=lambda cid: f"{cid} ({st.session_state.svc.c.get(cid, {}).get('category')})"
        )

        if selected_cid:
            c = st.session_state.svc.c.get(selected_cid, {})
            with st.container(border=True):
                st.markdown(f"### Job: `{c['id']}`")
                st.markdown(f"**Feeder Line:** `{c.get('line')}` | **Priority:** **{c.get('priority')}**")
                st.markdown(f"**Hazard Category:** {c.get('category')}")
                st.markdown(f"**Location Coordinates:** Lat `{c.get('lat'):.4f}`, Lon `{c.get('lon'):.4f}`")
                st.write(f"**Consumer Statement:** *{c.get('desc')}*")
                st.info(f"**Current Ticket Status:** `{c.get('status')}`")

# Right Column: Mandatory LOTO Execution Desk
with col_loto:
    st.subheader("🛡️ Mandatory 4-Step Safety SOP Checklist (LOTO)")
    
    if not selected_cid:
        st.caption("Please select an assigned job ticket from the left queue to begin SOP procedures.")
    else:
        c = st.session_state.svc.c.get(selected_cid, {})
        status = c.get("status")

        # Step 1: Start job on site
        st.markdown("#### Step 1: Arrive On-Site")
        if status == "WORKER_DISPATCHED":
            if st.button("📍 Mark Arrived On-Site & Request Maintenance", type="primary", use_container_width=True):
                try:
                    st.session_state.svc.start(user_tuple, selected_cid)
                    st.success("Assessment started on-site!")
                    st.rerun()
                except Denied as e:
                    st.error(str(e))
        elif status in ("WORK_IN_PROGRESS", "WORK_COMPLETED", "RESOLVED"):
            st.success("✓ Arrived on-site and safety assessment verified.")

        st.divider()

        # Step 2: Request Digital Line Isolation
        st.markdown("#### Step 2: Substation Line Isolation Permit")
        iso_info = st.session_state.svc.iso.get(selected_cid)
        
        if not iso_info:
            iso_reason = st.text_input("State technical justification for line de-energization:", value="Replace damaged high-voltage conductor span", key=f"iso_in_{selected_cid}")
            if st.button("⚠️ Submit Line Isolation Request to Substation", key=f"btn_iso_req_{selected_cid}", type="primary"):
                try:
                    st.session_state.svc.request_isolation(user_tuple, selected_cid, iso_reason)
                    st.success("Line isolation permit requested from Substation Operator!")
                    st.rerun()
                except Denied as e:
                    st.error(str(e))
        else:
            if iso_info.get("status") == "REQUESTED":
                st.warning("⏳ Isolation permit submitted. Awaiting Substation Operator authorization and breaker tagging.")
            elif iso_info.get("status") == "ISOLATED":
                st.success("✅ **LINE ISOLATION PERMIT GRANTED:** Feeder line opened and locked out at substation.")
            elif iso_info.get("status") == "REJECTED":
                st.error("❌ Isolation permit was rejected by Substation Operator. Contact control room.")

        st.divider()

        # Step 3: Mandatory 4-Point LOTO Verification
        st.markdown("#### Step 3: Mandatory OSHA / IEEE Field Safety Verification")
        st.caption("All 4 safety steps must be physically performed on-site before commencing wire contact.")

        chk_dead = st.checkbox("1. High-Voltage Detector Test (Live-Dead-Live method confirms 0.0 Volts)", key=f"c1_{selected_cid}")
        chk_earth = st.checkbox("2. Portable Ground Earthing Clamps fastened on conductors upstream & downstream", key=f"c2_{selected_cid}")
        chk_lock = st.checkbox("3. Lock-Out / Tag-Out (LOTO) Physical Padlocks & Danger Tag secured", key=f"c3_{selected_cid}")
        chk_ppe = st.checkbox("4. Personal Protective Equipment (Class 4 1000V gloves, arc shield, harness) inspected", key=f"c4_{selected_cid}")

        all_loto_checked = chk_dead and chk_earth and chk_lock and chk_ppe

        act_c1, act_c2 = st.columns(2)

        with act_c1:
            if st.button("🔧 Begin Physical Repair Work (WIP)", key=f"btn_wip_{selected_cid}", type="primary", use_container_width=True):
                if not all_loto_checked:
                    st.error("🚨 **OSHA/IEEE VIOLATION DETECTED:** You cannot begin repair until all 4 LOTO safety checklist items are confirmed!")
                else:
                    try:
                        # Field verify then begin repair
                        st.session_state.svc.field_verify(user_tuple, selected_cid)
                        st.session_state.svc.begin_repair(user_tuple, selected_cid, True)
                        st.success("Field verify and LOTO confirmed! Repair is in progress.")
                        st.rerun()
                    except Denied as e:
                        st.error(f"Safety Violation: {str(e)}")

        with act_c2:
            if st.button("✅ Complete Repair & Clear Line", key=f"btn_comp_{selected_cid}", use_container_width=True):
                try:
                    st.session_state.svc.complete(user_tuple, selected_cid)
                    st.success("Repair complete! Ground clamps removed and field clearance submitted to substation.")
                    st.rerun()
                except Denied as e:
                    st.error(f"Action Denied: {str(e)}")
