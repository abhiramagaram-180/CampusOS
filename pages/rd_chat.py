"""
R&D Lab Zone Chat — AI assistant for the campus R&D department.
Ask about projects, publications, lab equipment, research, etc.
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="R&D Genie", page_icon="🔬", layout="centered")

st.markdown(
 """
 <style>
 #MainMenu, header, footer, [data-testid="stSidebar"] { display: none !important; }
 .stApp { background: #080b10; }
 .stMain { background: #080b10; }
 </style>
 """,
 unsafe_allow_html=True,
)

st.page_link("app.py", label="← Back to Campus", icon="🏫")

st.markdown(
 """
 <div style="text-align: center; padding: 30px 0 20px;">
 <div style="font-size: 48px;">🔬</div>
 <h1 style="color: #9b5bf5; font-size: 28px; margin: 8px 0;">R&D Genie</h1>
 <p style="color: #666; font-size: 14px;">Projects, publications, lab equipment & research opportunities</p>
 </div>
 """,
 unsafe_allow_html=True,
)

if "rd_messages" not in st.session_state:
 st.session_state.rd_messages = [
 {
 "role": "assistant",
 "content": "🔬 Welcome to the R&D Genie! I can tell you about ongoing projects, published papers, lab equipment availability, research opportunities, and funding. What are you curious about?",
 "time": datetime.now().strftime("%I:%M %p"),
 }
 ]

if "rd_typing" not in st.session_state:
 st.session_state.rd_typing = False

chat_container = st.container()

with chat_container:
 for msg in st.session_state.rd_messages:
 is_user = msg["role"] == "user"

 if is_user:
 st.markdown(
 f"""
 <div style="display: flex; justify-content: flex-end; margin: 8px 0;">
 <div style="background: #9b5bf5; color: #fff; padding: 10px 16px; border-radius: 16px 16px 4px 16px; max-width: 75%; font-size: 14px;">
 {msg['content']}
 <div style="font-size: 10px; opacity: 0.7; text-align: right; margin-top: 4px;">{msg.get('time', '')}</div>
 </div>
 </div>
 """,
 unsafe_allow_html=True,
 )
 else:
 st.markdown(
 f"""
 <div style="display: flex; justify-content: flex-start; margin: 8px 0;">
 <div style="background: #1f172a; color: #ddd; padding: 10px 16px; border-radius: 16px 16px 16px 4px; max-width: 75%; font-size: 14px; border: 1px solid #3a2550;">
 <div style="font-size: 11px; color: #9b5bf5; font-weight: bold; margin-bottom: 4px;">🔬 R&D Genie</div>
 {msg['content']}
 <div style="font-size: 10px; color: #666; text-align: right; margin-top: 4px;">{msg.get('time', '')}</div>
 </div>
 </div>
 """,
 unsafe_allow_html=True,
 )

 if st.session_state.rd_typing:
 st.markdown(
 """
 <div style="display: flex; justify-content: flex-start; margin: 8px 0;">
 <div style="background: #1f172a; padding: 12px 18px; border-radius: 16px 16px 16px 4px; border: 1px solid #3a2550;">
 <div style="display: flex; gap: 4px;">
 <div style="width: 6px; height: 6px; background: #9b5bf5; border-radius: 50%; animation: bounce 1.4s infinite;"></div>
 <div style="width: 6px; height: 6px; background: #9b5bf5; border-radius: 50%; animation: bounce 1.4s infinite 0.2s;"></div>
 <div style="width: 6px; height: 6px; background: #9b5bf5; border-radius: 50%; animation: bounce 1.4s infinite 0.4s;"></div>
 </div>
 </div>
 </div>
 <style>
 @keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-4px); } }
 </style>
 """,
 unsafe_allow_html=True,
 )

st.markdown(
 """
 <style>
 .stChatMessage { display: none !important; }
 div[data-testid="stChatInput"] { display: none !important; }
 </style>
 """,
 unsafe_allow_html=True,
)

col1, col2 = st.columns([5, 1])

with col1:
 user_input = st.text_input(
 "Ask the R&D Genie...",
 key="rd_input",
 label_visibility="collapsed",
 placeholder="e.g., 'What projects are currently active?'",
 )

with col2:
 send_clicked = st.button("➤", key="rd_send", type="primary")

st.markdown("<div style='display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0;'>", unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4)

with r1:
 if st.button("🔬 Active projects", key="rq1"):
 user_input = "What projects are currently active?"

with r2:
 if st.button("📑 Publications", key="rq2"):
 user_input = "Show me recent publications"

with r3:
 if st.button("🔧 Lab equipment", key="rq3"):
 user_input = "What lab equipment can I use?"

with r4:
 if st.button("💼 Research jobs", key="rq4"):
 user_input = "Are there research assistant positions?"

st.markdown("</div>", unsafe_allow_html=True)

if (send_clicked or user_input) and user_input.strip():
 question = user_input.strip()

 st.session_state.rd_messages.append(
 {
 "role": "user",
 "content": question,
 "time": datetime.now().strftime("%I:%M %p"),
 }
 )

 st.session_state.rd_typing = True
 st.rerun()

elif st.session_state.rd_typing:
 st.session_state.rd_typing = False

 last_msg = st.session_state.rd_messages[-1]
 question = last_msg["content"].lower()

 responses = {
 "project": "🔬 <strong>Active Projects (3):</strong><br><br>1. <strong>AI-Powered Campus Navigation</strong> — Real-time pathfinding using computer vision and sensor fusion. 4 team members.<br>2. <strong>Smart Campus IoT</strong> — Sensor network for energy optimization and air quality monitoring. 6 team members.<br>3. <strong>Blockchain Academic Certificates</strong> — Verifiable credential system on Ethereum. 3 team members.<br><br>Want to join any of these?",
 "publish": "📑 <strong>Recent Publications (5 this semester):</strong><br>• 'Campus Navigation with Deep RL' — IEEE Conf. on AI<br>• 'IoT Energy Optimization' — ACM Computing Surveys<br>• 'Verifiable Credentials on Blockchain' — Springer Blockchain Journal<br>• 'Student Analytics Dashboard' — IEEE Access<br>• 'Smart Room Booking System' — ACM UbiComp<br><br>I can send you the PDF links.",
 "equip": "🔧 <strong>Lab Equipment Available:</strong><br><br>• Oscilloscopes (×8) — Book in 2-hr slots<br>• 3D Printers (×3) — Overnight prints available<br>• VR Headsets (×6) — For AI/VR projects<br>• Drone testing platform — Needs safety clearance<br>• Soldering stations (×4) — First come first served<br><br>Want me to book something?",
 "job": "💼 <strong>Open Research Positions:</strong><br><br>1. <strong>RA — AI Navigation Project</strong> (2 openings, CS/ECE)<br>2. <strong>RA — IoT Lab</strong> (1 opening, ECE)<br>3. <strong>Summer Intern — Blockchain</strong> (1 opening, CSE)<br><br>Stipend: ₹15K–25K/month. Apply through the R&D portal.",
 "default": f"🔬 Interesting! I can help with projects, publications, equipment booking, and research positions. You asked: \"{last_msg['content']}\" — Let me look into that!",
 }

 response = responses["default"]
 for key, val in responses.items():
 if key != "default" and key in question:
 response = val
 break

 st.session_state.rd_messages.append(
 {
 "role": "assistant",
 "content": response,
 "time": datetime.now().strftime("%I:%M %p"),
 }
 )

 st.rerun()
