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
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, PERSONAS, Denied, Role, S

st.set_page_config(
    page_title="Lineworker Terminal — RESA",
    page_icon="🛠️",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

# Ensure logged in as Lineworker
if st.session_state.get("authenticated_role") != Role.WORKER:
    st.session_state.current_user = "worker1"
    st.session_state.authenticated_role = Role.WORKER

user_tuple = get_user_tuple("worker1")
worker_info = PERSONAS["worker1"]

st.markdown(f"""
<div style="background: #fffbeb; border: 1px solid #fef3c7; border-left: 5px solid #f59e0b; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <div>
        <h3 style="margin: 0; color: #92400e; font-size: 17px; font-weight: 700;">🛠️ Field Lineworker Terminal</h3>
        <p style="margin: 2px 0 0 0; color: #b45309; font-size: 13px;">Logged in as: <strong>{worker_info['name']}</strong> ({worker_info['title']}) • Badge: <code>{worker_info.get('badge', 'LW-882')}</code></p>
    </div>
    <div>
        <span style="background: #fde68a; color: #92400e; font-weight: 600; font-size: 12px; padding: 4px 10px; border-radius: 6px;">Safety Certified: IS-5216 & CEA Grid SOP</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Find active complaints assigned to worker
assigned_complaints = [c for c in st.session_state.svc.c.values() if c.get("worker") == "worker1"]

# If none assigned, fallback to any active complaint
if not assigned_complaints:
    active_pool = [c for c in st.session_state.svc.c.values() if c.get("status") not in ("RESOLVED", "CLOSED")]
    if active_pool:
        target_c = active_pool[0]
        # auto-assign for demo
        try:
            st.session_state.svc.assign(("op1", Role.OPERATOR), target_c["id"], "worker1", "LN-204")
            assigned_complaints = [target_c]
        except Exception:
            assigned_complaints = active_pool
    else:
        assigned_complaints = list(st.session_state.svc.c.values())

if not assigned_complaints:
    st.info("No active breakdown work orders currently assigned.")
    st.stop()

# Select active work ticket
ticket_options = [c["id"] for c in assigned_complaints]
selected_cid = st.selectbox("Select Active Work Order / Breakdown Ticket:", options=ticket_options)
comp = st.session_state.svc.c.get(selected_cid)

if not comp:
    st.error("Selected ticket not found.")
    st.stop()

line = comp.get("line") or "LN-204"
feeder_state = st.session_state.grid.state.get(line, S.NORMAL)

# 1. Area Where Problem is Located
st.markdown("### 📍 Area Where Problem is Located (Hazard Dispatch)")
area_col1, area_col2, area_col3 = st.columns([1.2, 1, 1])

with area_col1:
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px;">
        <span style="color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 700;">Feeder Line & Area</span>
        <h4 style="margin: 4px 0 6px 0; color: #0f172a;">⚡ Feeder: {line}</h4>
        <p style="margin: 0; font-size: 13px; color: #334155;">
            <strong>Category:</strong> {comp.get('category')}<br>
            <strong>Reported Area:</strong> {comp.get('desc')}
        </p>
    </div>
    """, unsafe_allow_html=True)

with area_col2:
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px;">
        <span style="color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 700;">GPS Coordinates</span>
        <h4 style="margin: 4px 0 6px 0; color: #0f172a;">🌐 {comp.get('lat', 17.3850):.4f} N, {comp.get('lon', 78.4867):.4f} E</h4>
        <p style="margin: 0; font-size: 13px; color: #334155;">
            <strong>Citizen Contact:</strong> Anita Devi (+91 98765 43210)<br>
            <strong>Priority:</strong> <span style="color: #dc2626; font-weight: 700;">{comp.get('priority', 'P1')} - HIGH HAZARD</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with area_col3:
    state_color = "#16a34a" if feeder_state == S.NORMAL else ("#dc2626" if feeder_state == S.ISO_OK else "#d97706")
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px;">
        <span style="color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 700;">Feeder Safety State</span>
        <h4 style="margin: 4px 0 6px 0; color: {state_color};">⚡ {feeder_state.value}</h4>
        <p style="margin: 0; font-size: 13px; color: #334155;">
            <strong>Ticket Status:</strong> <code>{comp.get('status')}</code><br>
            <strong>Safety LOTO:</strong> {'VERIFIED & SAFE' if feeder_state in (S.WIP, S.DONE) else 'NOT READY'}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 2. Repair Duration & Delay Estimator (Requested Feature)
st.markdown("### ⏱️ Repair Duration & Delay Estimator")
st.caption("Submit expected repair hours or days, delay causes, and needed resources. Citizens and the Gram Panchayat see this in real-time.")

with st.form(f"eta_form_{selected_cid}", clear_on_submit=False):
    ec1, ec2 = st.columns([1, 2])
    with ec1:
        eta_num = st.number_input("Estimated Time Needed", min_value=1, max_value=72, value=2)
        eta_unit = st.selectbox("Unit", ["Hours", "Days"])
        full_eta_str = f"{eta_num} {eta_unit}"

    with ec2:
        reason_str = st.text_input(
            "Reason for Duration / Delay Scope *",
            value=comp.get("eta_reason") or "Severe 11kV conductor severance across road; needs 3 spans restringing and tree branch clearance",
            placeholder="Explain why this much time is needed (e.g., Heavy rain, damaged transformer coil, road blockage)..."
        )
        resources_str = st.text_input(
            "Equipment / Materials Required *",
            value=comp.get("resources_needed") or "50m ACSR conductor, 2 pin insulators, tree trimming crew",
            placeholder="List required parts (e.g., Replacement 25kVA transformer, JCB, hydraulic crimper)..."
        )

    submit_eta = st.form_submit_button("💾 Submit Duration & Delay Estimate", type="primary", use_container_width=True)
    if submit_eta:
        try:
            st.session_state.svc.update_estimate(user_tuple, selected_cid, full_eta_str, reason_str, resources_str)
            st.success(f"✅ Estimate updated: **{full_eta_str}** reported to Citizen and Gram Panchayat.")
            st.rerun()
        except Exception as e:
            st.error(f"Error updating estimate: {str(e)}")

st.divider()

# 3. Escalate to Gram Panchayat for Government Support
st.markdown("### 🏛️ Request Local Government Assistance from Gram Panchayat")
st.caption("If repair is delayed by trees, traffic, or heavy machinery needs, immediately notify the Gram Panchayat Head.")

with st.form(f"escalate_form_{selected_cid}", clear_on_submit=False):
    esc_col1, esc_col2 = st.columns([1, 1.5])
    with esc_col1:
        support_type = st.selectbox("Select Government Support Needed *", [
            "🌳 Tree / Branch Clearance Squad (Forest/PWD)",
            "🚧 Police Road Barricading & Traffic Diversion",
            "🚜 Emergency JCB / Heavy Excavator Crane",
            "💡 Emergency Mobile Diesel Generator"
        ])
    with esc_col2:
        esc_notes = st.text_input("Site Notes for Panchayat Head *", value="Branches entangled with 11kV lines near school road. Need JCB and tree cutting team before power restringing.")

    submit_esc = st.form_submit_button("📢 Raise Request to Gram Panchayat", use_container_width=True)
    if submit_esc:
        try:
            st.session_state.svc.escalate(user_tuple, selected_cid, f"{support_type} - {esc_notes}")
            st.success(f"✅ Escalation registered! Gram Panchayat dashboard has been alerted for **{support_type}**.")
            st.rerun()
        except Exception as e:
            st.error(f"Error escalating: {str(e)}")

st.divider()

# 4. Safety LOTO Verification & Work Status Execution
st.markdown("### 🔒 Safety Protocol & Work Status Execution")
st.caption("Strict Indian Electricity Rules & Central Electricity Authority SOP adherence.")

act1, act2 = st.columns(2)

with act1:
    st.markdown("#### Step 1: Substation Line Isolation")
    if feeder_state == S.NORMAL:
        st.warning("⚠️ Line is currently **NORMAL (Energized)**. You must request feeder isolation before any field work!")
        if st.button(f"⚡ Request Feeder Isolation for {line}", type="primary", use_container_width=True):
            try:
                st.session_state.svc.request_isolation(user_tuple, selected_cid, f"Field maintenance for {comp.get('category')}")
                st.success(f"Isolation requested on {line}. Substation Operator notified.")
                st.rerun()
            except Denied as e:
                st.error(str(e))
    elif feeder_state in (S.MAINT_REQ, S.ISO_REQ):
        st.info("⏳ Feeder isolation request pending operator confirmation in Substation Control Room.")
    else:
        st.success(f"✅ Feeder {line} is officially **ISOLATED & PERMITTED** by Substation.")

with act2:
    st.markdown("#### Step 2: 4-Point LOTO Verification & Work Progress")
    
    chk_v = st.checkbox("1. Zero Voltage confirmed using calibrated detector (< 50V residual)", key="chk_v")
    chk_e = st.checkbox("2. Portable safety earthing leads securely clamped to all phases", key="chk_e")
    chk_l = st.checkbox("3. Physical padlock & danger tag applied on gang-operated switch", key="chk_l")
    chk_p = st.checkbox("4. Arc-flash suit, helmet, and tested 11kV rubber gloves donned", key="chk_p")

    loto_complete = (chk_v and chk_e and chk_l and chk_p)

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if feeder_state == S.ISO_OK:
            if st.button("▶ Mark Work In Progress", type="primary", disabled=not loto_complete, use_container_width=True):
                try:
                    st.session_state.svc.field_verify(user_tuple, selected_cid)
                    st.session_state.svc.begin_repair(user_tuple, selected_cid, checklist_done=True)
                    st.success("Safety verified! Status marked as WORK IN PROGRESS.")
                    st.rerun()
                except Denied as e:
                    st.error(str(e))
            if not loto_complete:
                st.caption("⚠️ Check all 4 safety items above to enable Work In Progress.")
        elif feeder_state == S.WIP:
            st.info("🔧 Work is currently **IN PROGRESS** on site.")

    with col_btn2:
        if feeder_state == S.WIP or comp.get("status") == "WORK_IN_PROGRESS":
            if st.button("✅ Mark Work Completed & Release LOTO", type="primary", use_container_width=True):
                try:
                    st.session_state.svc.complete(user_tuple, selected_cid)
                    st.success("Work marked as COMPLETED! Clearance issued to Substation for power restoration.")
                    st.rerun()
                except Denied as e:
                    st.error(str(e))
        elif feeder_state == S.DONE:
            st.success("✅ Work marked COMPLETED. Awaiting Substation Operator re-energization.")
