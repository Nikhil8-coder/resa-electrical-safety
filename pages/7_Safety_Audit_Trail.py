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
import pandas as pd
from shared_state import init_shared_state, render_gov_header, render_sidebar

st.set_page_config(
    page_title="Statutory Safety Audit Log — RESA",
    page_icon="🔒",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("🔒 Statutory Safety & LOTO Audit Trail")
st.markdown("Immutable record of all electrical switching operations, isolation requests, and lock-out/tag-out verifications conforming to CEA regulations.")

rows = st.session_state.grid.audit()

if not rows:
    st.info("No safety transitions recorded in this session yet.")
else:
    cols = ["Audit ID", "Timestamp (UTC)", "Actor ID", "Role", "Action", "Feeder Line", "Ticket ID", "Prev State", "Target State", "Reason / Proof", "Result"]
    df = pd.DataFrame(rows, columns=cols)

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Switching Operations", len(df))
    m2.metric("Successful Transitions", len(df[df["Result"] == "SUCCESS"]))
    denied_count = len(df[df["Result"].str.startswith("DENIED")])
    m3.metric("Safety Violations Blocked", denied_count, delta="Zero Breaches" if denied_count == 0 else f"{denied_count} Prevented")

    st.markdown("#### 📜 Statutory Transition Ledger")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Cryptographic Integrity: Enforced via SQLite BEFORE UPDATE and BEFORE DELETE trigger locks.")
