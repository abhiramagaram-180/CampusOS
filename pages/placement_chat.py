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
import placement_store

# Question intents we can answer locally from submitted records, so a freshly
# entered placement (e.g. a record-high CTC) shows up in the chat answers.
_HIGHEST_HINTS = ("highest", "top ", "max", "maximum", "biggest", "largest", "best package")
_PACKAGE_WORDS = ("package", "ctc", "salary", "pay", "compensation", "offer")


def _apply_local_knowledge(question: str, answer):
    """Fold submitted placement records into an analytics answer (demo).

    Only touches the answer when the question is clearly about the highest
    package; otherwise it just notes that submitted records exist.
    """
    submitted = placement_store.get_submitted()
    if not submitted:
        return answer

    q = (question or "").lower()
    if any(h in q for h in _HIGHEST_HINTS) and any(w in q for w in _PACKAGE_WORDS):
        top = placement_store.highest_package()
        if top:
            company, lpa = top
            # One row per offer, ranked. The `placement` column is a unique
            # label ("1. Foo", "2. Foo", ...) so the bar chart shows every
            # offer instead of summing two rows that share a company name.
            lb = placement_store.leaderboard_df().head(placement_store.MAX_LEADERBOARD_ROWS)
            answer.error = None
            answer.text = (
                f"The highest package on record is ₹{lpa:g} LPA at {company}, "
                f"counting {len(submitted)} record(s) submitted through the form."
            )
            answer.df = lb[["placement", "package_ctc_lpa"]].reset_index(drop=True)
            answer.sql = (
                "SELECT company_name, package_ctc_lpa\n"
                "FROM workspace.default.students\n"
                "ORDER BY package_ctc_lpa DESC\n"
                f"LIMIT {placement_store.MAX_LEADERBOARD_ROWS}"
            )
        return answer

    answer.text = (answer.text or "") + (
        f"\n\n_({len(submitted)} recently submitted placement record(s) also on file.)_"
    )
    return answer

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
                answer = _apply_local_knowledge(q, ask_genie("placement", q, st.session_state.placement_conv_id))
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
            answer = _apply_local_knowledge(prompt, ask_genie("placement", prompt, st.session_state.placement_conv_id))
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
                record = {
                    "student_id": student_id,
                    "name": student_name,
                    "branch": branch,
                    "batch_year": int(batch_year),
                    "cgpa": float(cgpa),
                    "company_name": company_name,
                    "package_ctc_lpa": float(package_ctc),
                    "role_type": role_type,
                    "offer_status": offer_status,
                    "tier": int(tier),
                }
                placement_store.add_placement(record)

                insert_sql = f"""INSERT INTO workspace.default.students
    (student_id, name, branch, batch_year, cgpa, company_name, package_ctc_lpa, role_type, offer_status, tier)
VALUES
    ('{student_id}', '{student_name}', '{branch}', {int(batch_year)}, {cgpa}, '{company_name}', {package_ctc}, '{role_type}', '{offer_status}', {int(tier)})"""

                st.markdown(
                    f"""
                    <div class="success-box">
                        ✅ <strong>Placement record saved.</strong><br>
                        {student_name} ({student_id}) — {branch} {int(batch_year)} batch<br>
                        {company_name} — ₹{package_ctc:g} LPA ({role_type}, {offer_status})
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                top = placement_store.highest_package()
                if top and top[0] == company_name and abs(top[1] - float(package_ctc)) < 1e-9:
                    st.success(f"🏆 ₹{float(package_ctc):g} LPA is now the highest package on record — ask the Genie about it.")

                st.code(insert_sql, language="sql")

                if MOCK_MODE:
                    st.info("Mock mode: saved to the local demo store. Switch to 💬 Chat with Genie and ask about the highest package.")
                else:
                    try:
                        from genie_client import execute_sql  # optional live-mode helper
                        execute_sql(insert_sql, WAREHOUSE_ID)
                        st.caption("Also written to Databricks.")
                    except Exception as e:
                        st.warning(f"Saved to the local store. Databricks write skipped: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Everything on record so far — nothing you submit ever drops off this list.
    board = placement_store.leaderboard_df()
    submitted_n = int((board["source"] == "submitted").sum())
    st.markdown(f"#### 📊 Placements on record  ·  {submitted_n} submitted")
    st.dataframe(
        board[["rank", "company_name", "package_ctc_lpa", "source"]],
        use_container_width=True,
        hide_index=True,
    )
