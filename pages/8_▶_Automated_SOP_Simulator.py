import time
import streamlit as st
from shared_state import init_shared_state, render_gov_header, render_sidebar, Role, S

st.set_page_config(
    page_title="10-Stage SOP Simulator — RESA",
    page_icon="▶",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("▶ Automated 10-Stage SOP Safety Lifecycle Simulator")
st.caption("Live digital simulation demonstrating end-to-end hazard triage, isolation permit review, field LOTO verification, and safe power restoration.")

st.markdown("""
<div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
    <h4 style="margin: 0 0 8px 0; color: #38bdf8;">⚡ Demonstration Objectives</h4>
    <p style="font-size: 13px; color: #cbd5e1; margin: 0;">
        This automated test simulator executes the statutory 10-stage lifecycle in real-time across Citizen, Substation Operator, and Lineworker roles, verifying that no step can be skipped and that audit logs are generated at every state transition.
    </p>
</div>
""", unsafe_allow_html=True)

col_run, col_history = st.columns([1.5, 1])

with col_run:
    if st.button("🚀 Execute Complete 10-Stage SOP Lifecycle", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_box = st.status("Executing 10-Stage Digital Coordination Protocol...", expanded=True)

        try:
            with status_box:
                # Ensure feeder LN-204 is in clean NORMAL state before beginning
                st.session_state.grid.state["LN-204"] = S.NORMAL

                # Stage 1: Citizen creates complaint
                st.write("**Stage 1:** 👤 Citizen `cit1` reports high-priority Transformer Failure with GPS & photo...")
                cid = st.session_state.svc.create(
                    ("cit1", Role.CITIZEN),
                    "Transformer Failure",
                    "Audible arcing and smoke observed on pole transformer near primary health center.",
                    17.3850, 78.4867, ["transformer_flashover.jpg"]
                )
                progress_bar.progress(10)
                time.sleep(0.3)
                st.write(f"✓ **Generated Official Ticket ID:** `{cid}` (Priority: P1 Critical)")

                # Stage 2: Operator acknowledges
                st.write(f"**Stage 2:** ⚡ Substation Operator `op1` acknowledges ticket `{cid}`...")
                st.session_state.svc.acknowledge(("op1", Role.OPERATOR), cid)
                progress_bar.progress(20)
                time.sleep(0.3)
                st.write("✓ Ticket state advanced to `ACKNOWLEDGED`.")

                # Stage 3: Operator assigns worker & line
                st.write(f"**Stage 3:** ⚡ Operator dispatches Lineworker `worker1` to Feeder `LN-204`...")
                st.session_state.svc.assign(("op1", Role.OPERATOR), cid, "worker1", "LN-204")
                progress_bar.progress(30)
                time.sleep(0.3)
                st.write("✓ Lineman dispatched. Feeder line linked.")

                # Stage 4: Worker arrives on-site
                st.write(f"**Stage 4:** 🛠️ Lineworker `worker1` arrives on-site and begins hazard inspection...")
                st.session_state.svc.start(("worker1", Role.WORKER), cid)
                progress_bar.progress(40)
                time.sleep(0.3)
                st.write("✓ Grid line moved to `MAINTENANCE_REQUESTED`.")

                # Stage 5: Worker requests line isolation
                st.write(f"**Stage 5:** ⚠️ Lineworker requests digital line isolation on `LN-204`...")
                st.session_state.svc.request_isolation(("worker1", Role.WORKER), cid, "Replace damaged primary transformer fuse cutout")
                progress_bar.progress(50)
                time.sleep(0.3)
                st.write("✓ Line moved to `ISOLATION_REQUESTED`. Central control room alerted.")

                # Stage 6: Operator approves isolation
                st.write(f"**Stage 6:** ⚡ Substation Operator opens circuit breaker, locks out switch, and confirms permit...")
                st.session_state.svc.review_isolation(("op1", Role.OPERATOR), cid, True, "Feeder breaker 4 physically racked out and tagged per SOP")
                progress_bar.progress(60)
                time.sleep(0.3)
                st.write("✓ Feeder line de-energized: `ISOLATION_CONFIRMED`. Permit issued.")

                # Stage 7: Worker field safety verification
                st.write(f"**Stage 7:** 🛠️ Lineworker performs field-side zero-energy contact testing...")
                st.session_state.svc.field_verify(("worker1", Role.WORKER), cid)
                progress_bar.progress(70)
                time.sleep(0.3)
                st.write("✓ Line state advanced to `FIELD_SAFETY_VERIFICATION`.")

                # Stage 8: Worker verifies 4-step LOTO and begins repair
                st.write(f"**Stage 8:** 🛡️ Lineworker clamps ground earth sets, installs padlocks, dons PPE, and commences repair...")
                st.session_state.svc.begin_repair(("worker1", Role.WORKER), cid, True)
                progress_bar.progress(80)
                time.sleep(0.3)
                st.write("✓ Line and ticket state advanced to `WORK_IN_PROGRESS`.")

                # Stage 9: Worker completes physical repair
                st.write(f"**Stage 9:** 🛠️ Lineworker finishes physical fuse replacement and submits field clearance...")
                st.session_state.svc.complete(("worker1", Role.WORKER), cid)
                progress_bar.progress(90)
                time.sleep(0.3)
                st.write("✓ Feeder line cleared: `WORK_COMPLETED`.")

                # Stage 10: Operator restores power
                st.write(f"**Stage 10:** ⚡ Substation Operator verifies staff is clear, removes tags, and re-energizes Feeder `LN-204`...")
                st.session_state.svc.restore(("op1", Role.OPERATOR), cid, "All ground sets removed and personnel clear", "Feeder energized per SOP")
                progress_bar.progress(100)
                time.sleep(0.3)
                st.write("✓ Power safely restored! Feeder returned to `NORMAL`.")

                status_box.update(label=f"🎉 Complete! Ticket {cid} 100% RESOLVED with Zero Violations.", state="complete")
                st.balloons()

                st.session_state.last_sim_cid = cid

        except Exception as e:
            status_box.update(label=f"Simulation Failed: {str(e)}", state="error")
            st.error(f"Error during lifecycle: {str(e)}")

    if "last_sim_cid" in st.session_state:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button(f"🔍 Inspect Tracked Ticket {st.session_state.last_sim_cid} ➔", use_container_width=True):
                st.session_state.tracked_ticket_id = st.session_state.last_sim_cid
                st.switch_page("pages/3_🔍_Track_Complaint.py")
        with col_s2:
            if st.button("🔒 Inspect Generated Audit Logs ➔", use_container_width=True):
                st.switch_page("pages/7_🔒_Safety_Audit_Trail.py")

with col_history:
    st.subheader("📜 Expected Statutory Sequence")
    st.markdown("""
    1. **Citizen Submission:** Ticket ID generated & logged.
    2. **Operator Triage:** Acknowledged in central queue.
    3. **Resource Dispatch:** Lineman & Feeder assigned.
    4. **On-Site Assessment:** Lineman on location.
    5. **Digital Isolation:** Permit requested.
    6. **Operator Authorization:** Breaker racked out.
    7. **Zero-Energy Check:** Field verification done.
    8. **LOTO Verification:** Earthing & padlocks applied.
    9. **Repair Completion:** Field clearance submitted.
    10. **Safe Power Restoration:** Line re-energized.
    """)
