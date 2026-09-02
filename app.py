"""
CampusOS — Main Application
Embeds the 3D campus game and manages zone navigation.
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="CampusOS",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        #MainMenu,
        header,
        footer,
        [data-testid="stSidebar"] {
            display: none !important;
        }

        .stApp {
            background: #080b10;
        }

        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        iframe {
            border: none !important;
        }

        .zone-status {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 12px;
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

# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Game
# ---------------------------------------------------------

GAME_URL = "http://localhost:3000"

# JavaScript bridge:
# The game sends a message when the player enters a zone
# and wants to open the corresponding Streamlit page.
bridge_html = """
<script>
window.addEventListener("message", function(event) {

    if (!event.data) {
        return;
    }

    if (event.data.type !== "campusos-genie-query") {
        return;
    }

    const zone = event.data.zone;

    const zonePages = {
        placement: "placement_chat.py",
        library: "library_chat.py",
        canteen: "canteen_chat.py",
        rd: "rd_chat.py"
    };

    const targetPage = zonePages[zone];

    if (!targetPage) {
        return;
    }

    /*
     * Streamlit's page links are in the parent document.
     * Find the correct link and click it.
     */
    const links = window.parent.document.querySelectorAll("a");

    for (const link of links) {

        const href = link.getAttribute("href");

        if (href && href.includes(targetPage)) {
            link.click();
            break;
        }
    }

});
</script>
"""

# Load bridge separately so it runs in the game iframe's parent context.
components.html(
    bridge_html,
    height=0,
    scrolling=False,
)

# Main game iframe
try:
    components.iframe(
        GAME_URL,
        height=780,
        scrolling=False,
    )

except Exception as e:
    st.error("Unable to load the CampusOS game.")
    st.code(str(e))

# ---------------------------------------------------------
# Zone status
# ---------------------------------------------------------

st.markdown(
    """
    <div class="zone-status">
        <span class="zone-chip active">💼 Placement</span>
        <span class="zone-chip">📚 Library</span>
        <span class="zone-chip">🍽️ Canteen</span>
        <span class="zone-chip">🔬 R&D</span>
    </div>
    """,
    unsafe_allow_html=True,
)