import sys
from pathlib import Path
import streamlit as st

# Ensure backend package is in python path
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.workflows.safety import Grid, Role, S, Denied
from app.services.resa import Resa, CATEGORIES, HAZARD

PERSONAS = {
    "cit1": {"name": "Anita Devi (Citizen)", "role": Role.CITIZEN, "icon": "👤", "title": "Citizen / Consumer"},
    "op1": {"name": "Sunil Sharma (Central Substation)", "role": Role.OPERATOR, "icon": "⚡", "title": "Substation Control Officer"},
    "worker1": {"name": "Rajesh Kumar (Field Team A)", "role": Role.WORKER, "icon": "🛠️", "title": "Field Line Maintenance Technician"},
    "pan1": {"name": "Panchayat Head (Ward 4)", "role": Role.PANCHAYAT, "icon": "🏛️", "title": "Gram Panchayat Public Representative"},
    "admin": {"name": "System Administrator", "role": Role.ADMIN, "icon": "🛡️", "title": "Super Administrator"},
}

def init_shared_state():
    """Initializes shared singleton instances across all multi-page Streamlit views."""
    if "grid" not in st.session_state:
        st.session_state.grid = Grid(["LN-204", "LN-205", "LN-311"])

    if "svc" not in st.session_state:
        st.session_state.svc = Resa(["LN-204", "LN-205", "LN-311"], load_db=False)
        st.session_state.svc.grid = st.session_state.grid
        # Seed realistic initial breakdown data so portal starts with populated queues
        try:
            c1 = st.session_state.svc.create(
                ("cit1", Role.CITIZEN),
                "Broken Electrical Line",
                "High-voltage 11kV conductor snapped across village road near pole P-42. Sparking on ground.",
                17.3850, 78.4867, ["line_snap.jpg"]
            )
            st.session_state.svc.acknowledge(("op1", Role.OPERATOR), c1)
            st.session_state.svc.assign(("op1", Role.OPERATOR), c1, "worker1", "LN-204")

            c2 = st.session_state.svc.create(
                ("cit1", Role.CITIZEN),
                "Sparking Wire",
                "Transformer secondary jumper sparking intermittently under agricultural pump surge load.",
                17.3912, 78.4921, ["spark.png"]
            )
            st.session_state.svc.acknowledge(("op1", Role.OPERATOR), c2)

            c3 = st.session_state.svc.create(
                ("cit1", Role.CITIZEN),
                "Power Outage",
                "Ward 4 feeder tripped following sudden severe thunderstorm.",
                17.3780, 78.4750
            )
        except Exception:
            pass

    if "current_user" not in st.session_state:
        st.session_state.current_user = "cit1"

    if "logged_in_users" not in st.session_state:
        st.session_state.logged_in_users = {"cit1": True}

def get_user_tuple(username=None):
    user = username or st.session_state.get("current_user", "cit1")
    info = PERSONAS.get(user, PERSONAS["cit1"])
    return (user, info["role"])

def render_gov_header():
    """Renders official public utility header on top of every page."""
    st.markdown("""
        <div style="background: linear-gradient(90deg, #0b1e36 0%, #16365c 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 20px; border-left: 6px solid #ff9933; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 11px; letter-spacing: 1.5px; color: #ff9933; font-weight: 700; text-transform: uppercase;">Ministry of Power & Energy Distribution • Government Utility Services</span>
                <h3 style="margin: 2px 0 0 0; color: #ffffff; font-size: 18px; font-weight: 800;">⚡ RESA — National Electrical Safety & Breakdown Coordination Portal</h3>
            </div>
            <div style="text-align: right; margin-top: 6px;">
                <span style="background: #ef4444; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;">🚨 TOLL-FREE 24x7 HELPLINE: 1912</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders clean, government-style portal navigation in sidebar."""
    st.sidebar.markdown("### 🏛️ Official Portals Gate")
    st.sidebar.caption("Central Electrical System Coordination")
    
    # Quick active user profile display
    u = st.session_state.get("current_user", "cit1")
    u_info = PERSONAS[u]
    st.sidebar.info(f"**Current Session:**\n{u_info['icon']} **{u_info['name']}**\nRole: `{u_info['title']}`")

    st.sidebar.divider()
    st.sidebar.markdown("**📡 Regional Feeder Lines Status**")
    for line, state in st.session_state.grid.state.items():
        if state.value == "NORMAL":
            st.sidebar.markdown(f"🟢 **{line}**: `NORMAL` (Energized)")
        elif "ISOLATION" in state.value:
            st.sidebar.markdown(f"🟣 **{line}**: `{state.value}`")
        elif "PROGRESS" in state.value:
            st.sidebar.markdown(f"🔵 **{line}**: `{state.value}`")
        else:
            st.sidebar.markdown(f"🟠 **{line}**: `{state.value}`")

    st.sidebar.divider()
    st.sidebar.caption("Statutory Notice: Digital safety coordination platform. Does not replace physical voltage test-before-touch or earthing SOPs.")
