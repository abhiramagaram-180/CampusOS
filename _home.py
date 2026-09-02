"""
_home.py — CampusOS campus view.
Embeds the 3D game and shows the zone nav row. Registered as the default
page of st.navigation in app.py (the actual entrypoint); st.set_page_config
is called once there, not here — Streamlit only allows one call per run.
"""

import streamlit as st
import streamlit.components.v1 as components
import os

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
# NAVIGATION
# ============================================================

# Create hidden navigation links that the game can trigger
with st.container():
 col_pla, col_lib, col_can, col_rd = st.columns(4)

 with col_pla:
  st.page_link("pages/placement_chat.py", label="Placement Cell", icon="💼")

 with col_lib:
  st.page_link("pages/library_chat.py", label="Library Chat", icon="📚")

 with col_can:
  st.page_link("pages/canteen_chat.py", label="Canteen Chat", icon="🍽️")

 with col_rd:
  st.page_link("pages/rd_chat.py", label="R&D Chat", icon="🔬")

# ============================================================
# 3D GAME
# ============================================================

game_path = os.path.join(
 os.path.dirname(__file__), "game", "public", "index.html"
)

if os.path.exists(game_path):
 with open(game_path, "r", encoding="utf-8") as f:
  game_html = f.read()

 # Inline src/main.js so the game works inside Streamlit's components.html
 # sandbox, whose relative-URL resolution can't reliably find external
 # files served from disk (there's no static file server behind it).
 main_js_path = os.path.join(os.path.dirname(game_path), "src", "main.js")
 if os.path.exists(main_js_path):
  with open(main_js_path, "r", encoding="utf-8") as f:
   main_js = f.read()
  game_html = game_html.replace(
   '<script type="module" src="src/main.js"></script>',
   f'<script type="module">\n{main_js}\n</script>',
  )

 # Inject message bridge for Streamlit communication
 message_bridge = """
 <script>
 // Bridge between game and Streamlit parent
 window.addEventListener('message', (event) => {
 if (event.data && event.data.type === 'campusos-genie-query') {
 // Forward to Streamlit via a hidden form
 const zonePages = {
 'placement': 'pages/placement_chat.py',
 'library': 'pages/library_chat.py',
 'canteen': 'pages/canteen_chat.py',
 'rd': 'pages/rd_chat.py',
 };
 const targetPage = zonePages[event.data.zone];
 if (targetPage) {
 // Find and click the matching page_link
 const links = window.parent.document.querySelectorAll('a[href*="' + event.data.zone + '"]');
 if (links.length > 0) {
 links[0].click();
 }
 }
 }
 });
 </script>
 """

 # Insert the bridge before </body>
 game_html = game_html.replace("</body>", message_bridge + "</body>")

 components.html(game_html, height=780, scrolling=False)

else:
 st.error("Game files not found. Run `cd game && npm install && npm start` first.")
 st.code(f"Expected: {game_path}")

# ============================================================
# ZONE STATUS PANEL
# ============================================================

st.markdown(
 """
 <style>
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
 <div class="zone-status">
 <span class="zone-chip">💼 Placement</span>
 <span class="zone-chip">📚 Library</span>
 <span class="zone-chip">🍽️ Canteen</span>
 <span class="zone-chip">🔬 R&D Lab</span>
 </div>
 """,
 unsafe_allow_html=True,
)
