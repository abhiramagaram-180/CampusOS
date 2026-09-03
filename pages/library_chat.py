"""
CampusOS — Library Zone Chat Page
Chat with the Library Genie about books, study rooms, research papers, hours.
"""

import os
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MOCK_MODE, ZONE_SPACE_IDS
from genie_client import ask_genie

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CampusOS — Library",
    page_icon="📚",
    layout="centered",
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

    .zone-header {
        text-align: center;
        padding: 25px 0 15px;
    }
    .zone-header h1 { color: #5b9bd5; font-size: 2em; margin: 0; }
    .zone-header p { color: #888; font-size: 14px; margin: 5px 0 0; }

    .suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 16px;
    }
    .suggestions .stButton > button {
        background: #1a2332;
        border: 1px solid #2a3a4a;
        color: #5b9bd5;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
    }
    .suggestions .stButton > button:hover {
        background: #2a3a4a;
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
    <div class="zone-header">
        <div style="font-size: 48px;">📚</div>
        <h1>Library Genie</h1>
        <p>Ask about books, study rooms, research papers & library hours</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Back button
st.page_link("app.py", label="← Back to Campus", icon="🏫")

# ============================================================
# SESSION STATE
# ============================================================

if "library_messages" not in st.session_state:
    st.session_state.library_messages = []
if "library_conv_id" not in st.session_state:
    st.session_state.library_conv_id = None

space_id = ZONE_SPACE_IDS.get("library", "")
if not space_id and not MOCK_MODE:
    st.warning("Library Genie Space ID not configured. Set GENIE_SPACE_LIBRARY env var.")

# ============================================================
# SUGGESTIONS
# ============================================================

st.markdown("**Try asking:**")
suggestions = [
    "What are the library opening hours?",
    "Find me books on machine learning",
    "Is a study room available?",
    "Find research papers on IoT",
]

suggest_cols = st.columns(len(suggestions))
for i, q in enumerate(suggestions):
    with suggest_cols[i]:
        if st.button(q, key=f"lib_suggest_{i}", use_container_width=True):
            st.session_state.library_messages.append({"role": "user", "content": q})
            with st.spinner("Thinking..."):
                answer = ask_genie("library", q, st.session_state.library_conv_id)
            st.session_state.library_messages.append({"role": "assistant", "answer": answer})
            if answer.conversation_id:
                st.session_state.library_conv_id = answer.conversation_id
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# CHAT HISTORY
# ============================================================

# User turns are plain strings, assistant turns are GenieAnswer objects,
# so branch on the explicit role instead of assuming every entry has .text
for m in st.session_state.library_messages:
    with st.chat_message(m["role"]):
        if m["role"] == "user":
            st.markdown(m["content"])
        else:
            a = m["answer"]
            if a.error:
                st.error(a.error)
            else:
                st.markdown(a.text)
                if a.df is not None and not a.df.empty:
                    st.dataframe(a.df, use_container_width=True)
                if a.sql:
                    with st.expander("Show the SQL Genie ran"):
                        st.code(a.sql, language="sql")

# ============================================================
# CHAT INPUT
# ============================================================

if prompt := st.chat_input("Ask the Library Genie..."):
    st.session_state.library_messages.append({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        answer = ask_genie("library", prompt, st.session_state.library_conv_id)
    st.session_state.library_messages.append({"role": "assistant", "answer": answer})
    if answer.conversation_id:
        st.session_state.library_conv_id = answer.conversation_id
    st.rerun()
