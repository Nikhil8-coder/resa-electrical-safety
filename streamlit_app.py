import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, PERSONAS, CATEGORIES, HAZARD, FLOW, Denied, Role, S

st.set_page_config(
    page_title="RESA — National Electrical Safety & Grievance Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_shared_state()
render_gov_header()
render_sidebar()

# Check if a specific role is currently authenticated/active
role = st.session_state.get("authenticated_role")

# ==============================================================================
# SCREEN 1: NATIONAL ROLE IDENTITY & LOGIN GATE (If not yet selected)
# ==============================================================================
if not role:
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.12); padding: 26px; border-radius: 14px; margin-bottom: 24px; text-align: center;">
        <span style="background: #f59e0b; color: #0f172a; font-weight: 800; font-size: 11px; padding: 4px 12px; border-radius: 999px; text-transform: uppercase; letter-spacing: 1px;">Official Government Utility Services</span>
        <h2 style="color: #ffffff; font-size: 26px; font-weight: 800; margin: 10px 0 6px 0;">National Electrical Safety & Coordination Portal</h2>
        <p style="color: #94a3b8; font-size: 14px; max-width: 720px; margin: 0 auto;">
            Welcome. Before entering the system, please select your identity to access your dedicated, uncluttered department interface:
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏛️ Select Your Role to Login:")

    c_cit, c_wrk, c_pan = st.columns(3)

    # 1. Citizen Login Card
    with c_cit:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 22px; border-radius: 12px; height: 260px; display: flex; flex-col; justify-content: space-between;">
            <div>
                <div style="font-size: 32px; margin-bottom: 8px;">👤 <strong>Citizen / Consumer</strong></div>
                <p style="color: #38bdf8; font-weight: 600; font-size: 13px; margin-bottom: 8px;">Public Grievance & Hazard Reporting</p>
                <p style="color: #cbd5e1; font-size: 13px; line-height: 1.4;">
                    • File new breakdown reports (snapped lines, transformer sparks, outages)<br>
                    • Track live ticket status & repair progress<br>
                    • View worker's estimated time to restore power (ETA)
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("👤 Login as Citizen (Anita Devi)", key="gate_login_cit", type="primary", use_container_width=True):
            st.session_state.authenticated_role = "citizen"
            st.session_state.current_user = "cit1"
            st.rerun()

    # 2. Lineworker Login Card
    with c_wrk:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 22px; border-radius: 12px; height: 260px; display: flex; flex-col; justify-content: space-between;">
            <div>
                <div style="font-size: 32px; margin-bottom: 8px;">🛠️ <strong>Field Lineworker</strong></div>
                <p style="color: #10b981; font-weight: 600; font-size: 13px; margin-bottom: 8px;">Emergency Repair Crew & LOTO Terminal</p>
                <p style="color: #cbd5e1; font-size: 13px; line-height: 1.4;">
                    • View dispatched problem areas & GPS coordinates<br>
                    • Request line isolation & 4-step LOTO checklist<br>
                    • Publish repair duration estimates (hours/days needed)<br>
                    • Escalate to Gram Panchayat for government/crane support
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("🛠️ Login as Lineworker (Rajesh Kumar)", key="gate_login_wrk", type="primary", use_container_width=True):
            st.session_state.authenticated_role = "worker"
            st.session_state.current_user = "worker1"
            st.rerun()

    # 3. Gram Panchayat Login Card
    with c_pan:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 22px; border-radius: 12px; height: 260px; display: flex; flex-col; justify-content: space-between;">
            <div>
                <div style="font-size: 32px; margin-bottom: 8px;">🏛️ <strong>Gram Panchayat</strong></div>
                <p style="color: #fbbf24; font-weight: 600; font-size: 13px; margin-bottom: 8px;">Village Public Safety & Governance</p>
                <p style="color: #cbd5e1; font-size: 13px; line-height: 1.4;">
                    • Inspect citizen issues & assigned worker statuses<br>
                    • Monitor worker time estimates & delay causes<br>
                    • Review worker escalations & authorize Government Support (tree clearing, police barricades, emergency JCB)
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("🏛️ Login as Gram Panchayat (Ward 4)", key="gate_login_pan", type="primary", use_container_width=True):
            st.session_state.authenticated_role = "panchayat"
            st.session_state.current_user = "pan1"
            st.rerun()

    st.divider()

    # Control Room & Statutory Tools Expandable
    with st.expander("⚡ Substation Control Room & Statutory Safety Tools", expanded=False):
        c_op, c_sim = st.columns(2)
        with c_op:
            st.markdown("**Central Substation Control Terminal (Sunil Sharma - op1)**")
            st.caption("Manage feeder circuit breakers, triage incoming tickets, issue line isolation permits, and restore power.")
            if st.button("⚡ Login as Substation Operator", key="gate_login_op", use_container_width=True):
                st.session_state.authenticated_role = "operator"
                st.session_state.current_user = "op1"
                st.rerun()
        with c_sim:
            st.markdown("**Automated 10-Stage SOP Simulator & Audit Registry**")
            st.caption("Inspect immutable trigger-enforced safety logs or execute the automated 10-stage SOP simulation.")
            if st.button("▶ Open Automated SOP Simulator", key="gate_login_sim", use_container_width=True):
                st.switch_page("pages/8_▶_Automated_SOP_Simulator.py")

    st.stop()


# ==============================================================================
# TOP BAR FOR AUTHENTICATED SESSIONS: USER IDENTITY & ROLE LOGOUT
# ==============================================================================
u_key = st.session_state.get("current_user", "cit1")
u_data = PERSONAS.get(u_key, PERSONAS["cit1"])

top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.5); padding: 10px 16px; border-radius: 8px; border-left: 4px solid #38bdf8; display: inline-block;">
        Logged in as: <strong>{u_data['icon']} {u_data['name']}</strong> &nbsp;|&nbsp; Portal: <strong>`{u_data['title']}`</strong>
    </div>
    """, unsafe_allow_html=True)
with top_col2:
    if st.button("🚪 Switch Role / Logout", key="btn_logout_top", use_container_width=True):
        st.session_state.authenticated_role = None
        st.session_state.current_user = None
        st.rerun()

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# SCREEN 2: DEDICATED CITIZEN PORTAL (Problem Reporting & Live Status Tracking)
# ==============================================================================
if role == "citizen":
    user_tuple = get_user_tuple("cit1")
    
    tab_report, tab_track, tab_history = st.tabs([
        "🚨 Report Electrical Problem / Hazard",
        "🔍 Track Problem Status & Live Timeline",
        "📋 My Registered Complaints"
    ])

    # Citizen Tab 1: Report Problem Form
    with tab_report:
        st.subheader("🚨 Report Electrical Hazard or Power Breakdown")
        st.caption("Official consumer emergency desk. Snapped live conductors and sparking transformers immediately alert central substation dispatchers.")

        with st.form("citizen_hazard_form", clear_on_submit=False):
            category = st.selectbox(
                "Select Electrical Incident Category *",
                options=sorted(list(CATEGORIES)),
                index=sorted(list(CATEGORIES)).index("Broken Electrical Line") if "Broken Electrical Line" in CATEGORIES else 0
            )

            is_p1 = category in HAZARD
            if is_p1:
                st.warning("⚠️ **CRITICAL HAZARD DETECTED:** This report will be tagged with **P1 Maximum Priority** and dispatched urgently to emergency repair crews.")
            else:
                st.info("ℹ️ Standard Distribution Maintenance Ticket (Priority P3).")

            description = st.text_area(
                "Detailed Description of Problem / Hazard *",
                placeholder="Describe exact landmarks (near school, hospital, pole number), visible sparks, fallen trees, or immediate public danger...",
                height=110
            )

            st.markdown("**📍 Location & GPS Coordinates**")
            g1, g2 = st.columns(2)
            lat = g1.number_input("Latitude", value=17.3850, format="%.4f")
            lon = g2.number_input("Longitude", value=78.4867, format="%.4f")

            photo_file = st.file_uploader("Attach Photo Evidence (Optional)", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("🚀 Submit Official Problem Report", type="primary", use_container_width=True)

            if submitted:
                if not description.strip():
                    st.error("Please enter a description of the electrical issue.")
                else:
                    try:
                        photos = [photo_file.name] if photo_file else ["site_photo.jpg"]
                        cid = st.session_state.svc.create(user_tuple, category, description, lat, lon, photos)
                        st.session_state.tracked_ticket_id = cid
                        st.success(f"🎉 **Problem Reported Successfully!** Your Official Ticket Reference ID is **`{cid}`**")
                        st.info("Switch to the 'Track Problem Status' tab to view real-time repair progress.")
                    except Denied as e:
                        st.error(f"Validation Error: {str(e)}")

    # Citizen Tab 2: Track Problem Status & Worker ETA
    with tab_track:
        st.subheader("🔍 Track Your Electrical Complaint Status")
        all_tickets = list(st.session_state.svc.c.keys())
        default_search = st.session_state.get("tracked_ticket_id", all_tickets[-1] if all_tickets else "")

        search_cid = st.text_input("Enter Your Ticket Reference ID:", value=default_search, placeholder="e.g. RESA-2026-000245").strip()

        if search_cid and search_cid in st.session_state.svc.c:
            c = st.session_state.svc.c[search_cid]
            status = c.get("status", "SUBMITTED")
            cur_idx = FLOW.index(status) if status in FLOW else 0

            # 7-Stage Stepper
            st.markdown("#### 📊 7-Stage Digital Restoration Lifecycle")
            step_cols = st.columns(len(FLOW))
            for idx, step_name in enumerate(FLOW):
                with step_cols[idx]:
                    if idx < cur_idx:
                        st.markdown(f"<div style='background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; border-radius: 8px; padding: 8px 4px; text-align: center;'><span style='color: #10b981;'>✓</span><br><strong style='color: #10b981; font-size: 10px;'>{step_name}</strong></div>", unsafe_allow_html=True)
                    elif idx == cur_idx:
                        st.markdown(f"<div style='background: rgba(59, 130, 246, 0.3); border: 2px solid #3b82f6; border-radius: 8px; padding: 8px 4px; text-align: center;'><span style='color: #3b82f6;'>⚡</span><br><strong style='color: #ffffff; font-size: 10px;'>{step_name}</strong></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='background: rgba(30, 41, 59, 0.4); border: 1px solid #334155; border-radius: 8px; padding: 8px 4px; text-align: center;'><span style='color: #64748b;'>•</span><br><span style='color: #64748b; font-size: 10px;'>{step_name}</span></div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # WORKER ESTIMATED TIME (ETA) HIGHLIGHT
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

            # GOVERNMENT / PANCHAYAT SUPPORT HIGHLIGHT
            if c.get("govt_support"):
                st.markdown("""<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 14px; border-radius: 10px; margin-bottom: 16px;">
                    <h5 style="margin: 0 0 4px 0; color: #10b981;">🏛️ Gram Panchayat Government Support Provided</h5>
                """, unsafe_allow_html=True)
                for sup in c["govt_support"]:
                    st.markdown(f"- **{sup['type']}**: {sup['notes']} *(Approved by {sup['by']})*")
                st.markdown("</div>", unsafe_allow_html=True)

            # Details
            c_info1, c_info2 = st.columns(2)
            with c_info1:
                st.markdown(f"**Ticket ID:** `{c['id']}`")
                st.markdown(f"**Category:** {c['category']} ({c['priority']})")
                st.markdown(f"**Location:** Lat `{c['lat']:.4f}`, Lon `{c['lon']:.4f}`")
                st.write(f"**Reported Problem:** {c['desc']}")
            with c_info2:
                st.markdown(f"**Current Status:** `{c['status']}`")
                st.markdown(f"**Assigned Feeder:** `{c.get('line') or 'Pending Triage'}`")
                st.markdown(f"**Assigned Lineman:** `{c.get('worker') or 'Pending Dispatch'}`")
                st.caption(f"Registered at: {c.get('created')}")

            # Chronological Timeline
            st.markdown("#### 📜 Official Timeline Updates")
            for entry in c.get("timeline", []):
                st.markdown(f"- 🕒 `{entry[0]}` — **{entry[1]}** {('— *' + entry[2] + '*') if len(entry) > 2 and entry[2] else ''}")
        else:
            st.info("Enter a valid Ticket ID above to track its live progress.")

    # Citizen Tab 3: My History
    with tab_history:
        st.subheader("📋 My Registered Electrical Complaints")
        my_cs = [c for c in st.session_state.svc.c.values() if c.get("citizen") == "cit1"]
        if not my_cs:
            st.info("No registered complaints found for your account.")
        else:
            for item in reversed(my_cs):
                with st.expander(f"Ticket `{item['id']}` — {item['category']} ({item['status']})"):
                    st.write(f"**Description:** {item['desc']}")
                    st.caption(f"Feeder: `{item.get('line') or 'Unassigned'}` | Lineman: `{item.get('worker') or 'Unassigned'}`")
                    if st.button(f"Track {item['id']}", key=f"hist_tr_{item['id']}"):
                        st.session_state.tracked_ticket_id = item['id']
                        st.rerun()


# ==============================================================================
# SCREEN 3: DEDICATED FIELD LINEWORKER TERMINAL
# ==============================================================================
elif role == "worker":
    user_tuple = get_user_tuple("worker1")
    st.subheader("🛠️ Field Lineworker Safety Terminal & Area Dispatch")
    st.caption("Authorized Maintenance Technician: Rajesh Kumar (worker1) • Emergency Breakdown Rapid Response Crew")

    orders = st.session_state.svc.get_work_orders(user_tuple)

    if not orders:
        st.info("No active breakdown work orders currently assigned to lineworker worker1.")
    else:
        order_options = [o["complaint_id"] for o in orders]
        selected_cid = st.selectbox(
            "Select Active Work Order / Incident Ticket:",
            options=order_options,
            format_func=lambda cid: f"{cid} — {st.session_state.svc.c.get(cid, {}).get('category')}"
        )

        c = st.session_state.svc.c.get(selected_cid, {})
        status = c.get("status")

        col_area, col_ops = st.columns([1.1, 1.4])

        # Left Column: Area of Problem & Escalations
        with col_area:
            st.markdown("### 📍 Problem Location & Area Details")
            with st.container(border=True):
                st.markdown(f"#### Incident: `{c['id']}`")
                st.markdown(f"**Feeder Line:** `{c.get('line')}` | Priority: **{c.get('priority')}**")
                st.markdown(f"**Hazard Category:** {c.get('category')}")
                st.markdown(f"**📍 Exact Area Coordinates:**\nLat `{c.get('lat'):.4f}`, Lon `{c.get('lon'):.4f}`")
                st.markdown(f"**Citizen Statement:**\n*{c.get('desc')}*")
                if c.get("photos"):
                    st.caption(f"📷 Attached Photo: `{', '.join(c['photos'])}`")
                st.info(f"**Current Status:** `{status}`")

            st.divider()

            # Worker Feature 1: Estimate Hours/Days & Materials Needed
            st.markdown("### ⏱️ Report Repair Duration & ETA")
            st.caption("Tell the citizen and Gram Panchayat how long this repair will take and what materials are needed:")

            with st.form(f"worker_eta_form_{selected_cid}"):
                eta_time = st.selectbox(
                    "Estimated Repair Time Needed *",
                    options=["1 Hour", "2 Hours", "3 Hours", "5 Hours", "8 Hours", "1 Day", "2 Days", "3 Days"]
                )
                eta_cause = st.text_input(
                    "Reason for Delay / Technical Problem *",
                    value=c.get("eta_reason", "Conductor snapped across poles; requires tensioning")
                )
                eta_res = st.text_input(
                    "Materials / Equipment Required *",
                    value=c.get("resources_needed", "11kV Pin Insulator, 50m ACSR wire, bucket ladder")
                )
                btn_eta = st.form_submit_button("📢 Publish Time Estimate to Citizen & Panchayat", type="primary")

                if btn_eta:
                    st.session_state.svc.update_estimate(user_tuple, selected_cid, eta_time, eta_cause, eta_res)
                    st.success(f"Estimated repair duration ({eta_time}) updated successfully!")
                    st.rerun()

            st.divider()

            # Worker Feature 2: Escalate to Gram Panchayat for Government Support
            st.markdown("### 🏛️ Request Gram Panchayat Support")
            st.caption("If you need government assistance on-site (tree cutting, police barricade, crowd control, heavy machinery):")

            with st.form(f"worker_panchayat_esc_{selected_cid}"):
                esc_type = st.selectbox(
                    "Select Government Support Needed *",
                    options=[
                        "Tree Trimming / Fallen Branch Clearance",
                        "Police Barricades & Traffic / Crowd Control",
                        "Heavy Machinery Support (JCB / Crane)",
                        "Hospital / Health Clinic Emergency Generator",
                        "Administrative Right-of-Way Access"
                    ]
                )
                esc_msg = st.text_input(
                    "Urgent Message to Gram Panchayat Head *",
                    value="Heavy fallen tree branch resting on 11kV conductor span. Need Panchayat tree-cutting team and road barricade."
                )
                btn_esc = st.form_submit_button("📢 Escalate to Gram Panchayat for Assistance", type="primary")

                if btn_esc:
                    st.session_state.svc.escalate(user_tuple, selected_cid, f"{esc_type}: {esc_msg}")
                    st.success("Escalation dispatched to Gram Panchayat! Panchayat Head will be notified.")
                    st.rerun()

        # Right Column: Safety Operations & LOTO Execution Desk
        with col_ops:
            st.markdown("### 🛡️ Mandatory Safety Protocol & Work Operations")

            # Step 1: Arrive on-site
            st.markdown("#### Step 1: Arrive On-Site")
            if status == "WORKER_DISPATCHED":
                if st.button("📍 Mark Arrived On-Site & Inspect Hazard", type="primary", use_container_width=True):
                    try:
                        st.session_state.svc.start(user_tuple, selected_cid)
                        st.success("On-site inspection started!")
                        st.rerun()
                    except Denied as e:
                        st.error(str(e))
            elif status in ("WORK_IN_PROGRESS", "WORK_COMPLETED", "RESOLVED"):
                st.success("✓ Arrived on-site and hazard inspection registered.")

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
                    st.warning("⏳ Isolation permit submitted. Awaiting Substation Operator authorization.")
                    if st.button("⚡ Substation Operator: 1-Click Authorize Permit & Open Breaker", key=f"quick_auth_{selected_cid}", type="primary"):
                        try:
                            st.session_state.svc.review_isolation(get_user_tuple("op1"), selected_cid, True, "Approved remotely per SOP")
                            st.success("Permit authorized! Feeder de-energized.")
                            st.rerun()
                        except Denied as e:
                            st.error(str(e))
                elif iso_info.get("status") == "ISOLATED":
                    st.success("✅ **LINE ISOLATION PERMIT GRANTED:** Feeder line de-energized and locked out at substation.")

            st.divider()

            # Step 3: Mandatory 4-Point LOTO Verification
            st.markdown("#### Step 3: Mandatory OSHA / IEEE Field Safety Verification")
            st.caption("Zero-energy test, earthing, padlocks, and PPE must be confirmed before physical conductor contact.")

            col_chk_all, _ = st.columns([1.5, 1])
            with col_chk_all:
                if st.button("⚡ Auto-Check All 4 LOTO Safety Steps", key=f"chk_all_{selected_cid}"):
                    st.session_state[f"c1_{selected_cid}"] = True
                    st.session_state[f"c2_{selected_cid}"] = True
                    st.session_state[f"c3_{selected_cid}"] = True
                    st.session_state[f"c4_{selected_cid}"] = True
                    st.rerun()

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
                            line_name = c.get('line')
                            cur_state = st.session_state.grid.state.get(line_name)
                            if cur_state == S.ISO_OK:
                                st.session_state.svc.field_verify(user_tuple, selected_cid)
                            if st.session_state.grid.state.get(line_name) == S.FIELD_VERIFY:
                                st.session_state.svc.begin_repair(user_tuple, selected_cid, True)
                            st.success("Field verify and LOTO confirmed! Repair is now in progress.")
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

            if status in ("WORK_IN_PROGRESS", "WORK_COMPLETED"):
                st.divider()
                st.info("Power restoration handover: Once repair is done, Substation Operator can safely re-energize the feeder.")
                if st.button("⚡ Restore Feeder Power Now (Substation Handover)", key=f"quick_restore_{selected_cid}", type="primary", use_container_width=True):
                    try:
                        line_name = c.get('line')
                        if st.session_state.grid.state.get(line_name) != S.DONE:
                            st.session_state.grid.state[line_name] = S.DONE
                        st.session_state.svc.restore(get_user_tuple("op1"), selected_cid, "Field clearance checked", "Feeder re-energized per SOP")
                        st.success("Power safely restored! Feeder returned to NORMAL.")
                        st.rerun()
                    except Denied as e:
                        st.error(str(e))


# ==============================================================================
# SCREEN 4: DEDICATED GRAM PANCHAYAT DASHBOARD
# ==============================================================================
elif role == "panchayat":
    user_tuple = get_user_tuple("pan1")
    st.subheader("🏛️ Gram Panchayat Public Safety & Government Support Dashboard")
    st.caption("Elected Public Representative: Gram Panchayat Head (Ward 4) • Rural Electricity Board Governance Portal")

    # 1. Five Major KPI Metrics
    dash_data = st.session_state.svc.dashboard(("pan1", Role.PANCHAYAT))
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Village Incidents", dash_data.get("total", 0))
    k2.metric("Active Breakdowns", dash_data.get("open", 0), delta=f"-{dash_data.get('resolved', 0)} resolved", delta_color="inverse")
    k3.metric("Power Restored", dash_data.get("resolved", 0), "✓ Safe Resolution")
    k4.metric("P1 Critical Hazards", dash_data.get("critical", 0), "Emergency priority")
    k5.metric("Panchayat Escalations", dash_data.get("escalated", 0), "Action Required")

    st.divider()

    # 2. Worker Escalations & Requests for Government Support
    st.markdown("### 🚨 Urgent Worker Escalations Requiring Government Support")
    st.caption("Lineworkers in the field who have requested Gram Panchayat assistance (tree removal, police barricades, heavy cranes):")

    escalated_cs = [c for c in st.session_state.svc.c.values() if c.get("escalated")]

    if not escalated_cs:
        st.success("✅ No urgent worker escalations currently pending. All field maintenance is proceeding normally.")
    else:
        for ec in escalated_cs:
            with st.container(border=True):
                st.markdown(f"#### ⚠️ Ticket `{ec['id']}` — {ec['category']} (Feeder: `{ec.get('line')}`)")
                st.markdown(f"**Assigned Worker:** `{ec.get('worker')}` | **Current Work Status:** `{ec.get('status')}`")
                st.error(f"**Worker Escalation Reason:** {ec.get('escalation_reason') or 'Assistance requested'}")
                if ec.get("eta"):
                    st.warning(f"⏱️ **Worker Estimated Repair Duration:** {ec.get('eta')} — *{ec.get('eta_reason')}*")

                st.markdown("**🏛️ Government Support Action Center:**")
                act_col1, act_col2, act_col3 = st.columns(3)

                with act_col1:
                    if st.button("🌳 Dispatch Tree Clearance Crew", key=f"pan_tree_{ec['id']}", use_container_width=True):
                        st.session_state.svc.provide_govt_support(user_tuple, ec['id'], "Tree Clearance", "Panchayat emergency tree-trimming team dispatched to site")
                        st.success("Tree cutting crew mobilized!")
                        st.rerun()

                with act_col2:
                    if st.button("🚧 Mobilize Police & Barricades", key=f"pan_pol_{ec['id']}", use_container_width=True):
                        st.session_state.svc.provide_govt_support(user_tuple, ec['id'], "Police Barricades", "Local police and traffic barricades stationed for public safety")
                        st.success("Police barricades authorized!")
                        st.rerun()

                with act_col3:
                    if st.button("🚜 Authorize JCB / Heavy Crane", key=f"pan_jcb_{ec['id']}", use_container_width=True):
                        st.session_state.svc.provide_govt_support(user_tuple, ec['id'], "Heavy Machinery", "Gram Panchayat emergency JCB / Crane funded and dispatched")
                        st.success("Heavy machinery dispatched!")
                        st.rerun()

    st.divider()

    # 3. Comprehensive Citizen Complaints & Worker Status Registry
    st.markdown("### 📋 Village Citizen Complaints, Assigned Workers & Work Status")
    all_complaints = list(st.session_state.svc.c.values())

    if not all_complaints:
        st.info("No recorded citizen complaints in the registry.")
    else:
        for c in reversed(all_complaints):
            with st.container(border=True):
                head1, head2, head3 = st.columns([1.5, 1.2, 1])
                with head1:
                    st.markdown(f"**Ticket:** `{c['id']}` • **{c['category']}**")
                    st.caption(f"Reported by: **{c.get('citizen')}** | 📍 Lat: `{c.get('lat'):.4f}`, Lon: `{c.get('lon'):.4f}`")
                    st.write(f"*{c.get('desc')}*")
                with head2:
                    st.markdown(f"**Assigned Worker:** `{c.get('worker') or 'Pending Dispatch'}`")
                    st.markdown(f"**Feeder Line:** `{c.get('line') or 'Unassigned'}`")
                    if c.get("eta"):
                        st.markdown(f"⏱️ **Worker ETA:** `{c.get('eta')}` ({c.get('eta_reason', '')})")
                with head3:
                    status_badge = "🟢 RESOLVED" if c.get("status") == "RESOLVED" else ("🔵 " + c.get("status"))
                    st.markdown(f"Status: **{status_badge}**")
                    if c.get("govt_support"):
                        st.caption("✓ Govt Support Granted")


# ==============================================================================
# SCREEN 5: CENTRAL SUBSTATION OPERATOR ROOM
# ==============================================================================
elif role == "operator":
    user_tuple = get_user_tuple("op1")
    st.subheader("⚡ Central Substation Operator Control Room")
    st.caption("Authorized Terminal: Sunil Sharma (op1) • Regional 33/11kV Substation Control Desk")

    # High Voltage Feeder Status Cards
    st.markdown("#### 📡 Regional Feeder Telemetry")
    feeder_cols = st.columns(len(st.session_state.grid.state))
    for idx, (line, state) in enumerate(st.session_state.grid.state.items()):
        with feeder_cols[idx]:
            if state.value == "NORMAL":
                st.success(f"**{line}**\n🟢 `NORMAL`\n11.0 kV | 78% Load")
            else:
                st.warning(f"**{line}**\n🟠 `{state.value}`")
                if st.button(f"🔄 Reset {line}", key=f"rst_op_{line}"):
                    st.session_state.grid.state[line] = S.NORMAL
                    st.rerun()

    st.divider()

    col_triage, col_permits = st.columns([1.3, 1])

    with col_triage:
        st.subheader("📥 Incident Triage & Work Order Dispatch")
        for c in reversed(list(st.session_state.svc.c.values())):
            with st.container(border=True):
                st.markdown(f"**Ticket:** `{c['id']}` • **{c['category']}** (Status: `{c['status']}`)")
                st.write(f"*{c['desc']}*")

                if c["status"] == "SUBMITTED":
                    if st.button("✓ Acknowledge Ticket", key=f"ack_{c['id']}", type="primary"):
                        st.session_state.svc.acknowledge(user_tuple, c["id"])
                        st.rerun()
                elif c["status"] == "ACKNOWLEDGED":
                    d1, d2 = st.columns(2)
                    w_pick = d1.selectbox("Worker", ["worker1"], key=f"w_{c['id']}")
                    l_pick = d2.selectbox("Feeder", ["LN-204", "LN-205", "LN-311"], key=f"l_{c['id']}")
                    if st.button("🚀 Dispatch Lineman", key=f"disp_{c['id']}", type="primary"):
                        st.session_state.svc.assign(user_tuple, c["id"], w_pick, l_pick)
                        st.rerun()
                elif c["status"] in ("WORK_IN_PROGRESS", "WORK_COMPLETED"):
                    if st.button("⚡ Restore Power & Close Incident", key=f"rst_pow_{c['id']}", type="primary"):
                        line_name = c.get('line')
                        if st.session_state.grid.state.get(line_name) != S.DONE:
                            st.session_state.grid.state[line_name] = S.DONE
                        st.session_state.svc.restore(user_tuple, c["id"], "Staff clear", "Power re-energized per SOP")
                        st.rerun()

    with col_permits:
        st.subheader("🔐 Line Isolation Permits Desk")
        reqs = st.session_state.svc.get_isolation_requests(user_tuple)
        if not reqs:
            st.info("No active isolation permit requests in queue.")
        else:
            for req in reversed(reqs):
                with st.container(border=True):
                    st.markdown(f"**Permit for Feeder:** `{req.get('line')}` (Ticket: `{req['complaint_id']}`)")
                    st.caption(f"Lineman: `{req.get('worker')}` | Reason: *{req.get('reason')}*")
                    if req.get("status") == "REQUESTED":
                        if st.button("✓ Authorize Isolation Permit", key=f"rev_{req['complaint_id']}", type="primary"):
                            st.session_state.svc.review_isolation(user_tuple, req['complaint_id'], True, "Breaker opened and tagged per SOP")
                            st.rerun()
                    else:
                        st.success(f"Status: {req.get('status')}")
