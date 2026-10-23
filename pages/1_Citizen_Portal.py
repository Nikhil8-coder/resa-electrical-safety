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
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, PERSONAS, CATEGORIES, HAZARD, FLOW, Denied, Role

st.set_page_config(
    page_title="Citizen Portal — RESA",
    page_icon="👤",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

# Ensure logged in as Citizen
if st.session_state.get("authenticated_role") != Role.CITIZEN:
    st.session_state.current_user = "cit1"
    st.session_state.authenticated_role = Role.CITIZEN

user_tuple = get_user_tuple("cit1")
citizen_info = PERSONAS["cit1"]

# Top citizen banner
st.markdown(f"""
<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <div>
        <h3 style="margin: 0; color: #166534; font-size: 17px; font-weight: 700;">👤 Citizen / Consumer Portal</h3>
        <p style="margin: 2px 0 0 0; color: #15803d; font-size: 13px;">Logged in as: <strong>{citizen_info['name']}</strong> ({citizen_info['title']}) • Contact: {citizen_info['phone']}</p>
    </div>
    <div>
        <span style="background: #dcfce7; color: #166534; font-weight: 600; font-size: 12px; padding: 4px 10px; border-radius: 6px;">Ward 4 • Rural Electrification Zone</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab_report, tab_track = st.tabs(["🚨 Report Electrical Hazard / Outage", "📋 My Reported Complaints & Status"])

with tab_report:
    st.subheader("🚨 Report Electrical Hazard or Breakdown")
    st.markdown("Submit emergency reports for snapped cables, sparking wires, transformer failure, or pole damage. Emergency reports receive immediate substation attention.")

    with st.form("citizen_report_form", clear_on_submit=False):
        c1, c2 = st.columns([1.2, 1])

        with c1:
            category = st.selectbox(
                "Select Electrical Incident Category *",
                options=sorted(list(CATEGORIES)),
                index=sorted(list(CATEGORIES)).index("Broken Electrical Line") if "Broken Electrical Line" in CATEGORIES else 0,
                help="Select the exact hazard observed."
            )

            is_p1 = category in HAZARD
            if is_p1:
                st.warning("⚠️ **CRITICAL HAZARD DETECTED:** This report will be tagged with **P1 Maximum Priority** and dispatched urgently to emergency repair crews.")
            else:
                st.info("ℹ️ Standard Distribution Maintenance Ticket (Priority P3).")

            description = st.text_area(
                "Detailed Description of Incident / Hazard *",
                placeholder="Detail exact location landmarks, extent of damage, presence of water/fire, and immediate public risk...",
                height=120
            )

        with c2:
            st.markdown("**📍 Location & GPS Coordinates**")
            village_landmark = st.text_input("Village / Colony Landmark *", value="Near Pole P-42, Shiv Mandir Road, Ward 4")
            
            gc1, gc2 = st.columns(2)
            lat = gc1.number_input("Latitude", value=17.3850, format="%.4f")
            lon = gc2.number_input("Longitude", value=78.4867, format="%.4f")

            photo_file = st.file_uploader(
                "Attach Photographic Evidence (Optional, .jpg, .png)",
                type=["jpg", "jpeg", "png"]
            )

        submitted = st.form_submit_button("🚨 Submit Hazard Grievance", type="primary", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("Please enter a descriptive statement of the hazard.")
            else:
                try:
                    photos = [photo_file.name] if photo_file else ["site_photo.jpg"]
                    full_desc = f"{description} [Landmark: {village_landmark}]"
                    cid = st.session_state.svc.create(user_tuple, category, full_desc, lat, lon, photos)

                    st.success(f"✅ **Grievance Registered Successfully!** Your Official Ticket ID is **`{cid}`**")
                    st.session_state.last_submitted_cid = cid

                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10b981; padding: 14px; border-radius: 8px; margin-top: 12px;">
                        <h4 style="margin: 0 0 4px 0; color: #10b981;">🎫 Official Ticket Confirmation</h4>
                        <p style="margin: 0; font-size: 13px;">
                            <strong>Ticket ID:</strong> <code>{cid}</code> | <strong>Category:</strong> {category} | <strong>Priority:</strong> {'P1 (Emergency)' if is_p1 else 'P3 (Standard)'}<br>
                            <strong>Status:</strong> SUBMITTED (Dispatched to Substation & Lineworker Queue)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                except Denied as e:
                    st.error(f"Validation Error: {str(e)}")

with tab_track:
    st.subheader("📋 My Reported Grievances & Live Status")
    st.markdown("Track the status of your reported electrical breakdowns, worker arrival times, and Gram Panchayat support actions.")

    # Fetch citizen's complaints
    all_complaints = [c for c in st.session_state.svc.c.values() if c.get("citizen") == "cit1"]

    if not all_complaints:
        st.info("You have not reported any electrical breakdowns yet. Use the 'Report Electrical Hazard' tab above to submit an issue.")
    else:
        for comp in reversed(all_complaints):
            cid = comp["id"]
            status = comp.get("status", "SUBMITTED")
            priority = comp.get("priority", "P3")
            created = comp.get("created")
            worker_id = comp.get("worker")
            eta = comp.get("eta")
            eta_reason = comp.get("eta_reason")
            resources = comp.get("resources_needed")
            govt_support = comp.get("govt_support", [])

            with st.container(border=True):
                # Header row
                top1, top2 = st.columns([2, 1])
                with top1:
                    p_badge = "🔴 P1 - EMERGENCY" if priority == "P1" else "🔵 P3 - STANDARD"
                    st.markdown(f"#### 🎫 Ticket `{cid}`: {comp.get('category')}")
                    st.caption(f"**Reported:** {created.strftime('%d %b %Y, %I:%M %p') if created else 'Just now'} • **Priority:** `{p_badge}`")
                with top2:
                    st.markdown(f"<div style='text-align: right;'><span style='background: #0284c7; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px;'>STATUS: {status}</span></div>", unsafe_allow_html=True)

                st.markdown(f"**Issue Details:** {comp.get('desc')}")

                # 7-Stage Flow Progress Stepper
                curr_idx = FLOW.index(status) if status in FLOW else 0
                step_cols = st.columns(len(FLOW))
                for i, step in enumerate(FLOW):
                    with step_cols[i]:
                        is_active = (i <= curr_idx)
                        icon = "✅" if i < curr_idx else ("▶️" if i == curr_idx else "⚪")
                        step_label = step.replace("_", " ").title()
                        st.markdown(f"<div style='font-size: 11px; text-align: center; color: {'#16a34a' if is_active else '#94a3b8'}; font-weight: {'700' if is_active else '400'};'>{icon}<br>{step_label}</div>", unsafe_allow_html=True)

                st.divider()

                # Lineworker ETA & Delay Section
                w_col, p_col = st.columns(2)
                with w_col:
                    st.markdown("##### 🛠️ Field Lineworker Status & ETA")
                    if worker_id and worker_id in PERSONAS:
                        w_info = PERSONAS[worker_id]
                        st.markdown(f"**Assigned Lineworker:** {w_info['icon']} **{w_info['name']}** (Badge: `{w_info.get('badge', 'LW-01')}`) • Phone: `{w_info.get('phone', 'N/A')}`")
                        if eta:
                            st.info(f"⏱️ **Estimated Repair Duration:** **{eta}**\n\n**Reason:** {eta_reason or 'Work under execution'}\n\n**Materials / Equipment Needed:** {resources or 'Standard Lineworker Toolkit'}")
                        else:
                            st.caption("Lineworker assigned. Site inspection and repair duration assessment in progress...")
                    else:
                        st.caption("Awaiting lineworker dispatch from substation control room...")

                with p_col:
                    st.markdown("##### 🏛️ Gram Panchayat Government Support")
                    if govt_support:
                        for gs in govt_support:
                            st.success(f"🚜 **Support Provided:** **{gs['type']}**\n\n*Notes:* {gs.get('notes', 'Local administration team deployed')} *(Approved by {gs.get('by', 'Panchayat')})*")
                    else:
                        st.caption("No additional local administration machinery required at this stage.")

                # Action if resolved
                if status == "RESOLVED":
                    st.success("🎉 **Power restored and breakdown resolved!** Please confirm your satisfaction:")
                    if st.button("✅ Confirm Resolution & Close Grievance", key=f"close_{cid}"):
                        try:
                            st.session_state.svc.close(("op1", Role.OPERATOR), cid)
                            st.success("Thank you! Grievance marked as CLOSED.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
