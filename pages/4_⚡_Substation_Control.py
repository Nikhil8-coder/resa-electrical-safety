import sys
from pathlib import Path

_root_dir = Path(__file__).resolve().parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
_backend_dir = _root_dir / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, Denied, S

st.set_page_config(
    page_title="Substation Control Room — RESA",
    page_icon="⚡",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("⚡ Central Substation Operator Control Room")
st.caption("Authorized Control Terminal: Sunil Sharma (op1) • Central 33/11kV Substation Grid Room")

user_tuple = get_user_tuple("op1")

# High Voltage Feeder Status Cards
st.subheader("📡 Regional High-Voltage Feeder Telemetry")
feeder_cols = st.columns(len(st.session_state.grid.state))

for idx, (line, state) in enumerate(st.session_state.grid.state.items()):
    with feeder_cols[idx]:
        if state.value == "NORMAL":
            st.success(f"### Feeder {line}\n**Status:** 🟢 `NORMAL`\n\nVoltage: `11.0 kV` | Load: `78%`")
        elif "ISOLATION" in state.value:
            st.error(f"### Feeder {line}\n**Status:** 🟣 `{state.value}`\n\nVoltage: `0.0 kV` | De-Energized")
            if st.button(f"🔄 Reset {line} to NORMAL", key=f"rst_{line}"):
                st.session_state.grid.state[line] = S.NORMAL
                st.rerun()
        elif "PROGRESS" in state.value:
            st.warning(f"### Feeder {line}\n**Status:** 🔵 `{state.value}`\n\nActive Linework In Progress")
            if st.button(f"🔄 Reset {line} to NORMAL", key=f"rst_{line}"):
                st.session_state.grid.state[line] = S.NORMAL
                st.rerun()
        else:
            st.info(f"### Feeder {line}\n**Status:** 🟠 `{state.value}`\n\nUnder Safety Coordination")
            if st.button(f"🔄 Reset {line} to NORMAL", key=f"rst_{line}"):
                st.session_state.grid.state[line] = S.NORMAL
                st.rerun()

st.divider()

col_triage, col_permits = st.columns([1.3, 1])

# Left Column: Triage & Dispatch Desk
with col_triage:
    st.subheader("📥 Incident Triage & Work Order Dispatch Desk")
    all_complaints = list(st.session_state.svc.c.values())
    
    if not all_complaints:
        st.info("No reported breakdown tickets in queue.")
    else:
        for c in reversed(all_complaints):
            with st.container(border=True):
                head_col, status_col = st.columns([2, 1])
                with head_col:
                    st.markdown(f"**Ticket:** `{c['id']}` • **{c['category']}**")
                    st.caption(f"📍 Lat: `{c['lat']:.4f}`, Lon: `{c['lon']:.4f}` | Priority: **{c['priority']}**")
                    st.write(f"*{c['desc']}*")
                with status_col:
                    st.markdown(f"Status: **`{c['status']}`**")
                    st.caption(f"Line: `{c.get('line') or 'Unassigned'}`")

                # Action buttons based on current lifecycle stage
                if c["status"] == "SUBMITTED":
                    if st.button("✓ Acknowledge Ticket", key=f"ack_{c['id']}", type="primary"):
                        try:
                            st.session_state.svc.acknowledge(user_tuple, c["id"])
                            st.success(f"Ticket {c['id']} Acknowledged!")
                            st.rerun()
                        except Denied as e:
                            st.error(str(e))

                elif c["status"] == "ACKNOWLEDGED":
                    st.markdown("**Dispatch Lineman to Incident:**")
                    d_c1, d_c2, d_c3 = st.columns([1.2, 1.2, 1])
                    w_pick = d_c1.selectbox("Select Lineman", ["worker1"], key=f"w_{c['id']}")
                    l_pick = d_c2.selectbox("Assign Feeder Line", ["LN-204", "LN-205", "LN-311"], key=f"l_{c['id']}")
                    if d_c3.button("🚀 Dispatch", key=f"btn_disp_{c['id']}", type="primary", use_container_width=True):
                        try:
                            st.session_state.svc.assign(user_tuple, c["id"], w_pick, l_pick)
                            st.success(f"Dispatched {w_pick} to {l_pick} for {c['id']}!")
                            st.rerun()
                        except Denied as e:
                            st.error(str(e))

                elif c["status"] in ("WORK_IN_PROGRESS", "WORK_COMPLETED"):
                    st.markdown("**Power Restoration Clearance:**")
                    if c["status"] == "WORK_IN_PROGRESS":
                        st.caption("ℹ️ Lineman is in field. Confirm all workers clear before restoration:")
                        if st.button(f"📞 Record Field Clearance Received via Radio ({c['id']})", key=f"radio_clear_{c['id']}"):
                            line_name = c.get('line')
                            if st.session_state.grid.state.get(line_name) != S.DONE:
                                st.session_state.grid.state[line_name] = S.DONE
                            c["status"] = "WORK_COMPLETED"
                            st.success("Field clearance confirmed! Feeder line is ready to restore.")
                            st.rerun()

                    r_c1, r_c2 = st.columns([2, 1])
                    rest_reason = r_c1.text_input("Restoration Authorization Reason *", value="Restore power per safety SOP clearance verified", key=f"rr_{c['id']}")
                    if r_c2.button("⚡ Restore Power", key=f"rest_{c['id']}", type="primary", use_container_width=True):
                        try:
                            line_name = c.get('line')
                            if st.session_state.grid.state.get(line_name) != S.DONE:
                                st.session_state.grid.state[line_name] = S.DONE
                            st.session_state.svc.restore(user_tuple, c["id"], "Field staff clear and earth clamps removed", rest_reason)
                            st.success(f"Power successfully re-energized for Feeder line {c.get('line')}!")
                            st.rerun()
                        except Denied as e:
                            st.error(str(e))

                elif c["status"] == "RESOLVED":
                    st.caption("✅ Feeder line normalized and power restored.")

# Right Column: Line Isolation Permits Desk
with col_permits:
    st.subheader("🔐 Digital Line Isolation Permits Desk")
    iso_requests = st.session_state.svc.get_isolation_requests(user_tuple)
    
    if not iso_requests:
        st.info("No active isolation permit requests in queue.")
    else:
        for req in reversed(iso_requests):
            with st.container(border=True):
                st.markdown(f"**Ticket:** `{req['complaint_id']}` • Feeder: **`{req.get('line')}`**")
                st.write(f"**Lineworker Reason:** *{req.get('reason')}*")
                st.caption(f"Lineman: `{req.get('worker')}` | Current Permit State: **`{req.get('status')}`**")

                if req.get("status") == "REQUESTED":
                    st.markdown("**Operator Authorization:**")
                    iso_reason = st.text_input("Substation Isolation Note", value="Breaker opened, locked and danger tagged per SOP", key=f"iso_note_{req['complaint_id']}")
                    sop_check = st.checkbox("Confirm Breaker Physically Opened & Tagged", key=f"sop_chk_{req['complaint_id']}")
                    
                    b_c1, b_c2 = st.columns(2)
                    if b_c1.button("✓ Approve Permit", key=f"app_iso_{req['complaint_id']}", type="primary", use_container_width=True):
                        if not sop_check:
                            st.error("Operator confirmation checkbox required per SOP.")
                        else:
                            try:
                                st.session_state.svc.review_isolation(user_tuple, req['complaint_id'], True, iso_reason)
                                st.success("Digital Isolation Permit Issued!")
                                st.rerun()
                            except Denied as e:
                                st.error(str(e))
                    if b_c2.button("✗ Reject", key=f"rej_iso_{req['complaint_id']}", use_container_width=True):
                        try:
                            st.session_state.svc.review_isolation(user_tuple, req['complaint_id'], False, "Rejected by Substation Operator")
                            st.warning("Isolation Permit Rejected.")
                            st.rerun()
                        except Denied as e:
                            st.error(str(e))
                else:
                    st.success(f"Permit Status: {req.get('status')}")
