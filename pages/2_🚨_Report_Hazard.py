import sys
from pathlib import Path

_root_dir = Path(__file__).resolve().parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
_backend_dir = _root_dir / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple, CATEGORIES, HAZARD, Denied

st.set_page_config(
    page_title="Report Electrical Breakdown — RESA",
    page_icon="🚨",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("🚨 Report Electrical Hazard or Breakdown")
st.markdown("Official emergency reporting desk. High-priority hazards (snapped conductors, pole damage, fire sparks) immediately alert central substation dispatchers.")

user_tuple = get_user_tuple("cit1")

col_form, col_guidelines = st.columns([1.4, 1])

with col_form:
    st.subheader("📝 Grievance & Hazard Details Form")
    with st.form("hazard_report_form", clear_on_submit=False):
        category = st.selectbox(
            "Select Electrical Incident Category *",
            options=sorted(list(CATEGORIES)),
            index=sorted(list(CATEGORIES)).index("Broken Electrical Line") if "Broken Electrical Line" in CATEGORIES else 0,
            help="Select the option that most accurately represents the physical hazard."
        )

        is_p1 = category in HAZARD
        if is_p1:
            st.warning("⚠️ **CRITICAL HAZARD DETECTED:** This report will be tagged with **P1 Maximum Priority** and dispatched urgently to emergency repair crews.")
        else:
            st.info("ℹ️ Standard Distribution Maintenance Ticket (Priority P3).")

        description = st.text_area(
            "Detailed Description of Incident / Hazard *",
            placeholder="Please detail exact location landmarks, extent of damage, presence of water/fire, and immediate public safety risk...",
            height=120
        )

        st.markdown("**📍 Location & GPS Coordinates**")
        gps_col1, gps_col2 = st.columns(2)
        
        default_lat = st.session_state.get("auto_lat", 17.3850)
        default_lon = st.session_state.get("auto_lon", 78.4867)

        lat = gps_col1.number_input("Latitude", value=float(default_lat), format="%.4f")
        lon = gps_col2.number_input("Longitude", value=float(default_lon), format="%.4f")

        photo_file = st.file_uploader(
            "Attach Photographic Evidence (Optional, .jpg, .png)",
            type=["jpg", "jpeg", "png"],
            help="High-resolution photos assist linemen in selecting appropriate replacement fuses, insulators, and conductors."
        )

        st.caption("Statutory Warning: Submitting false or mischievous hazard reports is punishable under Section 146 of the Electricity Act.")

        submitted = st.form_submit_button("🚀 Submit Official Hazard Report", type="primary", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("Submission Error: Please enter a descriptive statement of the hazard.")
            else:
                try:
                    photos = [photo_file.name] if photo_file else ["site_photo.jpg"]
                    cid = st.session_state.svc.create(user_tuple, category, description, lat, lon, photos)
                    
                    st.success(f"🎉 **Report Registered Successfully!** Your Official Ticket ID is **`{cid}`**")
                    st.session_state.last_submitted_cid = cid
                    st.session_state.tracked_ticket_id = cid

                    # Printable confirmation receipt
                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 18px; border-radius: 10px; margin-top: 14px;">
                        <h4 style="margin: 0 0 6px 0; color: #10b981;">✅ Official Ticket Confirmation</h4>
                        <p style="margin: 0; font-size: 13px; color: #f1f5f9;">
                            <strong>Ticket ID:</strong> {cid}<br>
                            <strong>Category:</strong> {category}<br>
                            <strong>Priority:</strong> {'P1 (Emergency Hazard)' if is_p1 else 'P3 (Standard Outage)'}<br>
                            <strong>Status:</strong> SUBMITTED (Dispatched to Substation Operator Queue)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                except Denied as e:
                    st.error(f"Validation Error: {str(e)}")

    if "last_submitted_cid" in st.session_state:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button(f"🔍 Track Ticket {st.session_state.last_submitted_cid} on Tracking Page ➔", type="secondary"):
            st.switch_page("pages/3_🔍_Track_Complaint.py")

with col_guidelines:
    st.subheader("📋 Public Safety SOP Guidelines")
    st.markdown("""
    * **Stay at least 10 meters (33 feet) away** from any broken conductor touching the ground.
    * **Never touch fallen wires**, fencing, or trees in contact with electrical cables.
    * In case of transformer explosion or fire, **do not pour water**; notify the fire department immediately.
    * Keep children and cattle away from water-logged areas with downed power cables.
    * **Emergency Central Control Room Hotline:** `1912` (Toll-Free, 24x7)
    """)

    st.divider()

    st.markdown("#### ⚡ Feeder Lines in Active Territory")
    st.markdown("- **Feeder LN-204**: 11 kV Primary Rural Feeder")
    st.markdown("- **Feeder LN-205**: 33 kV Substation Trunk Transmission")
    st.markdown("- **Feeder LN-311**: Agricultural Irrigation Feeder Line")

    if st.button("← Back to Citizen Services", use_container_width=True):
        st.switch_page("pages/1_📢_Citizen_Services.py")
