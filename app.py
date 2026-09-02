"""
CampusOS — Main Application
Embeds the 3D HiggsField game and manages zone navigation.
"""

import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="CampusOS",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# HIDE STREAMLIT CHROME
# ============================================================

st.markdown(
    """
    <style>
    #MainMenu, header, footer, [data-testid="stSidebar"] {
        display: none !important;
    }

    .stApp {
        background: #080b10;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    .zone-status {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 15px;
    }

    .zone-chip {
        padding: 8px 18px;
        border-radius: 20px;
        border: 1px solid #222;
        background: #0d1117;
        color: #888;
        font-size: 13px;
    }

    .zone-chip.active {
        border-color: #35e38a;
        color: #35e38a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# NAVIGATION
# ============================================================

with st.container():
    col_pla, col_lib, col_can, col_rd = st.columns(4)

    with col_pla:
        st.page_link(
            "pages/placement_chat.py",
            label="Placement Cell",
            icon="💼",
        )

    with col_lib:
        st.page_link(
            "pages/library_chat.py",
            label="Library Chat",
            icon="📚",
        )

    with col_can:
        st.page_link(
            "pages/canteen_chat.py",
            label="Canteen Chat",
            icon="🍽️",
        )

    with col_rd:
        st.page_link(
            "pages/rd_chat.py",
            label="R&D Chat",
            icon="🔬",
        )

# ============================================================
# 3D GAME
# ============================================================

# Your game/server.js serves the Three.js application.
# Keep that server running in the other terminal.

GAME_URL = "http://localhost:3000"

components.iframe(
    GAME_URL,
    height=780,
    scrolling=False,
)

# ============================================================
# ZONE STATUS PANEL
# ============================================================

st.markdown(
    """
    <div class="zone-status">
        <span class="zone-chip">💼 Placement</span>
        <span class="zone-chip">📚 Library</span>
        <span class="zone-chip">🍽️ Canteen</span>
        <span class="zone-chip">🔬 R&D Lab</span>
    </div>
    """,
    unsafe_allow_html=True,
)