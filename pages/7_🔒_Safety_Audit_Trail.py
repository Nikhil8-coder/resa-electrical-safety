import sys
from pathlib import Path

_root_dir = Path(__file__).resolve().parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
_backend_dir = _root_dir / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import streamlit as st
import pandas as pd
from shared_state import init_shared_state, render_gov_header, render_sidebar, get_user_tuple

st.set_page_config(
    page_title="Safety Audit Registry — RESA",
    page_icon="🔒",
    layout="wide"
)

init_shared_state()
render_gov_header()
render_sidebar()

st.title("🔒 Statutory Electrical Safety Audit Registry")
st.caption("Cryptographic & Database Trigger-Enforced Public Inspection Log • Central Electricity Authority Compliance")

st.markdown("""
<div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
    <strong>SQLITE ENGINE TRIGGER ENFORCEMENT ACTIVE:</strong> Every line transition and SOP clearance is recorded into the statutory <code>audit</code> table. Modifying or deleting records throws an un-bypassable database engine <code>ABORT ('audit is immutable')</code> exception.
</div>
""", unsafe_allow_html=True)

try:
    raw_audit = st.session_state.grid.audit()
    
    if not raw_audit:
        st.info("No audit transition records registered yet.")
    else:
        # Convert to DataFrame
        columns = ["ID", "Timestamp (UTC)", "User", "Role", "Action", "Feeder Line", "Ticket ID", "Previous State", "New State", "Reason / Clearance", "Result"]
        df = pd.DataFrame(raw_audit, columns=columns)

        # Filters
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1.5])
        
        all_lines = ["All Feeders"] + sorted(list(df["Feeder Line"].unique()))
        selected_line = f_col1.selectbox("Filter by Feeder Line:", all_lines)

        all_results = ["All Results", "SUCCESS", "DENIED"]
        selected_res = f_col2.selectbox("Filter by Execution Result:", all_results)

        search_query = f_col3.text_input("Search by Ticket or User:", placeholder="e.g. RESA-2026 or worker1")

        filtered_df = df.copy()

        if selected_line != "All Feeders":
            filtered_df = filtered_df[filtered_df["Feeder Line"] == selected_line]

        if selected_res != "All Results":
            filtered_df = filtered_df[filtered_df["Result"].str.contains(selected_res, case=False, na=False)]

        if search_query:
            filtered_df = filtered_df[
                filtered_df["Ticket ID"].str.contains(search_query, case=False, na=False) |
                filtered_df["User"].str.contains(search_query, case=False, na=False) |
                filtered_df["Reason / Clearance"].str.contains(search_query, case=False, na=False)
            ]

        st.subheader(f"📜 Audit Records ({len(filtered_df)} entries found)")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        # Export CSV Button
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Statutory Audit Log (CSV)",
            data=csv_data,
            file_name="RESA_Statutory_Safety_Audit_Log.csv",
            mime="text/csv",
            type="primary"
        )

except Exception as e:
    st.error(f"Error accessing statutory audit database: {str(e)}")
