"""
CampusOS — Placement Cell Page
Dual-mode: Chat with Genie OR submit a new placement record.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MOCK_MODE, ZONE_SPACE_IDS, WAREHOUSE_ID
from genie_client import ask_genie

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CampusOS — Placement Cell",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    #MainMenu, header, footer, [data-testid="stSidebar"] { display: none !important; }
    .stApp { background: #080b10; }

    .placement-header {
        text-align: center;
        padding: 25px 0 15px;
    }
    .placement-header h1 {
        color: #35e38a;
        font-size: 2em;
        margin: 0;
    }
    .placement-header p {
        color: #888;
        font-size: 14px;
        margin: 5px 0 0;
    }

    .mode-toggle {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }

    .form-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 12px;
        padding: 24px;
        max-width: 700px;
        margin: 0 auto;
    }

    .success-box {
        background: #0d2818;
        border: 1px solid #35e38a;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        color: #35e38a;
        font-size: 16px;
        margin-top: 16px;
    }

    .sql-panel {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 10px;
    }
    .sql-panel summary {
        color: #888;
        cursor: pointer;
        font-size: 13px;
    }
    .sql-panel code {
        color: #35e38a;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="placement-header">
        <h1>💼 Placement Cell</h1>
        <p>Track placements, ask analytics questions, or submit your offer details</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE INIT
# ============================================================

if "placement_messages" not in st.session_state:
    st.session_state.placement_messages = []
if "placement_conv_id" not in st.session_state:
    st.session_state.placement_conv_id = None

# ============================================================
# MODE TOGGLE
# ============================================================

mode = st.radio(
    "Mode",
    ["💬 Chat with Genie", "📝 Submit Placement"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<hr style='border-color: #1e2a3a; margin: 10px 0 20px;'>", unsafe_allow_html=True)

# ============================================================
# TAB 1: CHAT WITH GENIE
# ============================================================

if mode == "💬 Chat with Genie":
    space_id = ZONE_SPACE_IDS.get("placement", "")

    if not space_id and not MOCK_MODE:
        st.warning("⚠️ Genie Space ID not configured. Set `CAMPUSOS_PLACEMENT_SPACE_ID` in config.")

    # Suggested questions
    st.markdown("**Try asking:**")
    suggestions = [
        "What percentage of CSE students from 2025 batch got placed?",
        "Which company offered the highest package in 2024?",
        "How many students from each branch got Tier 1 offers?",
        "What is the placement rate by batch year?",
    ]

    cols = st.columns(len(suggestions))
    for i, q in enumerate(suggestions):
        if cols[i].button(q, key=f"suggest_{i}", use_container_width=True):
            st.session_state.placement_messages.append({"role": "user", "content": q})
            with st.spinner("Thinking..."):
                answer = ask_genie("placement", q, st.session_state.placement_conv_id)
            st.session_state.placement_messages.append({"role": "assistant", "answer": answer})
            if answer.conversation_id:
                st.session_state.placement_conv_id = answer.conversation_id
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history — user turns are plain strings, assistant turns are GenieAnswer objects,
    # so branch on the explicit role instead of assuming every entry has .text
    for m in st.session_state.placement_messages:
        with st.chat_message(m["role"]):
            if m["role"] == "user":
                st.markdown(m["content"])
            else:
                a = m["answer"]
                if a.error:
                    st.error(a.error)
                else:
                    st.markdown(a.text)
                    if a.df is not None:
                        st.dataframe(a.df, use_container_width=True)
                    try:
                        if a.df is not None and len(a.df.columns) >= 2:
                            num_cols = a.df.select_dtypes(include="number").columns
                            if len(num_cols) >= 1:
                                st.bar_chart(a.df.set_index(a.df.columns[0])[num_cols[0]])
                    except Exception:
                        pass
                    if a.sql:
                        with st.expander("🔍 Show the SQL Genie ran"):
                            st.code(a.sql, language="sql")

    # Chat input
    if prompt := st.chat_input("Ask about placements..."):
        st.session_state.placement_messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            answer = ask_genie("placement", prompt, st.session_state.placement_conv_id)
        st.session_state.placement_messages.append({"role": "assistant", "answer": answer})
        if answer.conversation_id:
            st.session_state.placement_conv_id = answer.conversation_id
        st.rerun()

# ============================================================
# TAB 2: SUBMIT PLACEMENT
# ============================================================

elif mode == "📝 Submit Placement":
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Add Your Placement Details")
    st.markdown("Fill in your placement information. It will be added to the placement database.")

    with st.form("placement_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Student Details**")
            student_id = st.text_input("Student ID *", placeholder="e.g. 1FB21CS001")
            student_name = st.text_input("Full Name *", placeholder="e.g. Rahul Sharma")
            branch = st.selectbox(
                "Branch *",
                ["CSE", "ISE", "ECE", "AIML", "EEE", "ME", "CV", "Other"],
            )
            batch_year = st.number_input("Batch Year *", min_value=2020, max_value=2030, value=2025)
            cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)

        with col2:
            st.markdown("**Placement Details**")
            company_name = st.text_input("Company Name *", placeholder="e.g. Microsoft")
            package_ctc = st.number_input("Package (CTC in LPA) *", min_value=0.0, value=12.0, step=0.5)
            role_type = st.selectbox(
                "Role Type *",
                ["Full-time", "Internship", "Intern + PPO", "Part-time"],
            )
            offer_status = st.selectbox(
                "Offer Status *",
                ["Accepted", "Pending", "Declined"],
            )
            tier = st.selectbox("Company Tier", [1, 2, 3], index=0,
                                format_func=lambda x: {1: "Tier 1 (Dream)", 2: "Tier 2 (Core)", 3: "Tier 3 (Mass)"}[x])

        submitted = st.form_submit_button("✅ Submit Placement Record", use_container_width=True, type="primary")

        if submitted:
            if not all([student_id, student_name, company_name]):
                st.error("⚠️ Please fill in all required fields (marked with *)")
            else:

                # Build INSERT SQL
                insert_sql = f"""INSERT INTO workspace.default.students
    (student_id, name, branch, batch_year, cgpa, company_name, package_ctc_lpa, role_type, offer_status, tier)
VALUES
    ('{student_id}', '{student_name}', '{branch}', {batch_year}, {cgpa}, '{company_name}', {package_ctc}, '{role_type}', '{offer_status}', {tier})"""

                if MOCK_MODE:
                    st.markdown(
                        f"""
                        <div class="success-box">
                            ✅ <strong>Mock Mode — Record would be inserted:</strong><br>
                            {student_name} ({student_id}) from {branch} {batch_year} batch<br>
                            Placed at <strong>{company_name}</strong> — ₹{package_ctc} LPA ({role_type})
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.code(insert_sql, language="sql")
                    st.info("💡 Flip `MOCK_MODE = False` in `config.py` to write to real Databricks.")
                else:
                    try:
                        from genie_client import execute_sql
                        result = execute_sql(insert_sql, WAREHOUSE_ID)
                        st.markdown(
                            f"""
                            <div class="success-box">
                                ✅ <strong>Record inserted successfully!</strong><br>
                                {student_name} — {company_name} — ₹{package_ctc} LPA
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to insert: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
