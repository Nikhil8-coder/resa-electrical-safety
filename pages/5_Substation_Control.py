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
    page_title="Substation Control Room — RESA",
    page_icon="⚡",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

# Ensure logged in as Operator
if st.session_state.get("authenticated_role") != Role.OPERATOR:
    st.session_state.current_user = "op1"
    st.session_state.authenticated_role = Role.OPERATOR

user_tuple = get_user_tuple("op1")
op_info = PERSONAS["op1"]

st.markdown(f"""
<div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <div>
        <h3 style="margin: 0; color: #1e40af; font-size: 17px; font-weight: 700;">⚡ Central Substation Control Room Desk</h3>
        <p style="margin: 2px 0 0 0; color: #1d4ed8; font-size: 13px;">Logged in as: <strong>{op_info['name']}</strong> ({op_info['title']}) • Substation: {op_info.get('substation', 'Central Grid')}</p>
    </div>
    <div>
        <span style="background: #dbeafe; color: #1e40af; font-weight: 600; font-size: 12px; padding: 4px 10px; border-radius: 6px;">SCADA Supervisory Authority: CEA Tier 1</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 1. Feeder Telemetry Cards
st.markdown("### ⚡ Regional Feeder Lines Status & Telemetry")
f_cols = st.columns(3)

feeder_specs = {
    "LN-204": {"name": "11kV Rural Feeder (Ward 4)", "voltage": 11.2, "load": "142 A", "status_override": None},
    "LN-205": {"name": "33kV Primary Transmission Line", "voltage": 33.1, "load": "480 A", "status_override": None},
    "LN-311": {"name": "11kV Agricultural Tubewell Feeder", "voltage": 10.9, "load": "88 A", "status_override": None}
}

for i, (line, spec) in enumerate(feeder_specs.items()):
    with f_cols[i]:
        state = st.session_state.grid.state.get(line, S.NORMAL)
        is_normal = (state == S.NORMAL)
        is_iso = ("ISOLATION" in state.value)
        is_wip = ("PROGRESS" in state.value)

        badge_bg = "#dcfce7" if is_normal else ("#fee2e2" if is_iso else "#fef3c7")
        badge_txt = "#166534" if is_normal else ("#991b1b" if is_iso else "#92400e")

        with st.container(border=True):
            st.markdown(f"#### ⚡ {line}")
            st.caption(spec["name"])
            st.markdown(f"<span style='background: {badge_bg}; color: {badge_txt}; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-size: 12px;'>STATE: {state.value}</span>", unsafe_allow_html=True)
            st.markdown(f"- **Operating Voltage:** `{spec['voltage']} kV`")
            st.markdown(f"- **Line Current Load:** `{spec['load']}`")
            if st.button(f"🔄 Reset {line} to Normal", key=f"rst_{line}"):
                st.session_state.grid.state[line] = S.NORMAL
                st.success(f"Feeder {line} manually reset to NORMAL.")
                st.rerun()

st.divider()

# 2. Substation Operator Actions
st.markdown("### 📋 Dispatch & Safety Isolation Clearance Desk")

complaints = list(st.session_state.svc.c.values())
pending_ack = [c for c in complaints if c.get("status") == "SUBMITTED"]
pending_iso = [c for c in complaints if st.session_state.svc.iso.get(c["id"], {}).get("status") == "REQUESTED"]
pending_restore = [c for c in complaints if st.session_state.grid.state.get(c.get("line"), S.NORMAL) == S.DONE]

t1, t2, t3 = st.tabs([
    f"📥 Pending Triage ({len(pending_ack)})",
    f"🔒 Isolation Requests ({len(pending_iso)})",
    f"⚡ Power Re-energization ({len(pending_restore)})"
])

with t1:
    if not pending_ack:
        st.info("No unacknowledged citizen complaints.")
    else:
        for c in pending_ack:
            cid = c["id"]
            with st.container(border=True):
                st.markdown(f"**Ticket `{cid}`: {c.get('category')}** - Priority: `{c.get('priority')}`")
                st.markdown(f"Location: {c.get('desc')}")
                b1, b2 = st.columns([1, 2])
                with b1:
                    if st.button(f"Acknowledge {cid}", key=f"ack_{cid}", type="primary"):
                        try:
                            st.session_state.svc.acknowledge(user_tuple, cid)
                            st.session_state.svc.assign(user_tuple, cid, "worker1", "LN-204")
                            st.success(f"Acknowledged and assigned to Lineworker Rajesh Kumar on LN-204.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

with t2:
    if not pending_iso:
        st.info("No pending line isolation requests from field crews.")
    else:
        for c in pending_iso:
            cid = c["id"]
            line = c.get("line") or "LN-204"
            r = st.session_state.svc.iso.get(cid, {})
            with st.container(border=True):
                st.markdown(f"#### ⚠️ Feeder Isolation Request: `{line}` for Ticket `{cid}`")
                st.markdown(f"**Lineworker:** Rajesh Kumar | **Reason:** {r.get('reason')}")
                iso_c1, iso_c2 = st.columns(2)
                with iso_c1:
                    iso_reason = st.text_input("SCADA Isolation Log Reason", value=f"Circuit Breaker Opened & Gang Isolator Racked Out for {cid}", key=f"why_{cid}")
                with iso_c2:
                    if st.button(f"⚡ Confirm Feeder Isolation & Issue Permit", key=f"appr_{cid}", type="primary"):
                        try:
                            st.session_state.svc.review_isolation(user_tuple, cid, approve=True, reason=iso_reason)
                            st.success(f"Feeder {line} isolated! Permit-to-work issued to field crew.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

with t3:
    if not pending_restore:
        st.info("No lines currently waiting for power restoration.")
    else:
        for c in pending_restore:
            cid = c["id"]
            line = c.get("line") or "LN-204"
            with st.container(border=True):
                st.markdown(f"#### ✅ Linework Completed on `{line}` (Ticket `{cid}`)")
                st.markdown(f"Lineworker Rajesh Kumar has released field earthing & LOTO locks.")
                res_c1, res_c2 = st.columns(2)
                with res_c1:
                    clr_reason = st.text_input("Clearance Audit Verification", value="All personnel clear; field earth leads removed", key=f"clr_{cid}")
                    rst_reason = st.text_input("Restoration Authorization Reason", value="Isolator closed, breaker re-energized, voltage normal", key=f"rst_{cid}")
                with res_c2:
                    if st.button(f"🔌 Re-energize Line & Restore Power", key=f"res_{cid}", type="primary"):
                        try:
                            st.session_state.svc.restore(user_tuple, cid, clr_reason, rst_reason)
                            st.success(f"Feeder {line} successfully re-energized! Power restored and ticket resolved.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
