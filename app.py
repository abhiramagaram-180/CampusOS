"""
CampusOS — Main Application
Embeds the 3D HiggsField/Three.js game and manages zone navigation.
"""

import os

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
    #MainMenu, header, footer, [data-testid="stSidebar"] { display: none !important; }
    .stApp { background: #080b10; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# NAVIGATION — links the game triggers
# ============================================================

with st.container():
    col_lib, col_can, col_rd, col_pl = st.columns(4)

    with col_lib:
        st.page_link("pages/library_chat.py", label="Library", icon="📚")

    with col_can:
        st.page_link("pages/canteen_chat.py", label="Canteen", icon="🍽️")

    with col_rd:
        st.page_link("pages/rd_chat.py", label="R&D", icon="🔬")

    with col_pl:
        st.page_link("pages/placement_chat.py", label="Placement", icon="💼")

# ============================================================
# 3D GAME
# ============================================================

game_path = os.path.join(
    os.path.dirname(__file__), "game", "public", "index.html"
)

if os.path.exists(game_path):
    with open(game_path, "r", encoding="utf-8") as f:
        game_html = f.read()

    # Inject message bridge for Streamlit communication
    message_bridge = """
    <script>
    // Bridge between game and Streamlit parent
    window.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'campusos-genie-query') {
            const knownZones = ['library', 'canteen', 'rd', 'placement'];
            if (knownZones.includes(event.data.zone)) {
                try {
                    const links = window.parent.document.querySelectorAll('a[href*="' + event.data.zone + '"]');
                    if (links.length > 0) {
                        links[0].click();
                    }
                } catch (e) {
                    // cross-origin iframe on deployed Streamlit — navigation bridge unavailable
                }
            }
        }
    });
    </script>
    """

    game_html = game_html.replace("</body>", message_bridge + "</body>")

    components.html(game_html, height=780, scrolling=False)

else:
    st.error("Game files not found.")
    st.code(f"Expected: {game_path}")
    st.info("Run `cd game && npm install && node server.js` to serve the game independently, or run Streamlit from the repo root.")
