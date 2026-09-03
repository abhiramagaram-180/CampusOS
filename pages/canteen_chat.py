"""
Canteen Zone Chat — AI assistant for the campus canteen.
Ask about menu, timings, nutrition, dietary options, etc.
"""

from datetime import datetime

import streamlit as st

st.set_page_config(page_title="Canteen Genie", page_icon="🍽️", layout="centered")

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
        <div style="font-size: 48px;">🍽️</div>
        <h1 style="color: #e8945b; font-size: 28px; margin: 8px 0;">Canteen Genie</h1>
        <p style="color: #666; font-size: 14px;">Menu, timings, nutrition info & dietary options</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "canteen_messages" not in st.session_state:
    st.session_state.canteen_messages = [
        {
            "role": "assistant",
            "content": "🍽️ Welcome to the Canteen Genie! I can tell you today's menu, check if there are vegan/gluten-free options, share nutritional info, or tell you about off-peak hours. What's on your mind?",
            "time": datetime.now().strftime("%I:%M %p"),
        }
    ]

if "canteen_typing" not in st.session_state:
    st.session_state.canteen_typing = False

chat_container = st.container()

with chat_container:
    for msg in st.session_state.canteen_messages:
        is_user = msg["role"] == "user"

        if is_user:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; margin: 8px 0;">
                    <div style="background: #e8945b; color: #1a0f05; padding: 10px 16px; border-radius: 16px 16px 4px 16px; max-width: 75%; font-size: 14px;">
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
                    <div style="background: #2a1f17; color: #ddd; padding: 10px 16px; border-radius: 16px 16px 16px 4px; max-width: 75%; font-size: 14px; border: 1px solid #4a3525;">
                        <div style="font-size: 11px; color: #e8945b; font-weight: bold; margin-bottom: 4px;">🍽️ Canteen Genie</div>
                        {msg['content']}
                        <div style="font-size: 10px; color: #666; text-align: right; margin-top: 4px;">{msg.get('time', '')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if st.session_state.canteen_typing:
        st.markdown(
            """
            <div style="display: flex; justify-content: flex-start; margin: 8px 0;">
                <div style="background: #2a1f17; padding: 12px 18px; border-radius: 16px 16px 16px 4px; border: 1px solid #4a3525;">
                    <div style="display: flex; gap: 4px;">
                        <div style="width: 6px; height: 6px; background: #e8945b; border-radius: 50%; animation: bounce 1.4s infinite;"></div>
                        <div style="width: 6px; height: 6px; background: #e8945b; border-radius: 50%; animation: bounce 1.4s infinite 0.2s;"></div>
                        <div style="width: 6px; height: 6px; background: #e8945b; border-radius: 50%; animation: bounce 1.4s infinite 0.4s;"></div>
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

# clear_on_submit empties the field after each send, so a rerun can't
# re-fire the same message (that was the infinite-append bug).
with st.form("canteen_chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Ask the Canteen Genie...",
            key="canteen_input",
            label_visibility="collapsed",
            placeholder="e.g., 'Is there anything vegan today?'",
        )
    with col2:
        send_clicked = st.form_submit_button("➤", type="primary")

st.markdown("<div style='display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0;'>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

quick = None
with c1:
    if st.button("📋 Today's menu", key="cq1"):
        quick = "What's on the menu today?"

with c2:
    if st.button("⏰ Timings", key="cq2"):
        quick = "What are the canteen timings?"

with c3:
    if st.button("🥗 Veg options", key="cq3"):
        quick = "Are there vegan options?"

with c4:
    if st.button("📊 Nutrition info", key="cq4"):
        quick = "Can I see nutritional information?"

st.markdown("</div>", unsafe_allow_html=True)

pending = quick or (user_input.strip() if send_clicked and user_input.strip() else None)

if pending:
    st.session_state.canteen_messages.append(
        {
            "role": "user",
            "content": pending,
            "time": datetime.now().strftime("%I:%M %p"),
        }
    )

    st.session_state.canteen_typing = True
    st.rerun()

elif st.session_state.canteen_typing:
    st.session_state.canteen_typing = False

    last_msg = st.session_state.canteen_messages[-1]
    question = last_msg["content"].lower()

    responses = {
        "menu": "📋 <strong>Today's Menu:</strong><br>🥞 <strong>Breakfast</strong> (7:30-10 AM): Idli, Dosa, Poha, Upma<br>🍛 <strong>Lunch</strong> (12-2 PM): Rice, Roti, Dal, Veg Curry, Chicken<br>🥤 <strong>Snacks</strong> (4-6 PM): Samosa, Puffs, Fresh Juice<br>🍚 <strong>Dinner</strong> (7-9 PM): Full meals, biryani, pasta",
        "time": "⏰ <strong>Canteen Timings:</strong><br>• Breakfast: 7:30 AM – 10:00 AM<br>• Lunch: 12:00 PM – 2:00 PM<br>• Snacks: 4:00 PM – 6:00 PM<br>• Dinner: 7:00 PM – 9:00 PM<br><br>The canteen is closed between 2-4 PM and after 9 PM.",
        "veg": "🥗 Yes! We have several options for you:<br>• Dedicated veg counters (counters 3 & 4)<br>• Vegan options: Item #7 (vegan bowl) and #12 (fruit salad)<br>• Jain options available on request<br>• All ingredients are clearly labeled",
        "nutrition": "📊 <strong>Today's Nutrition Highlights:</strong><br>• Veg Thali: ~450 kcal, 18g protein<br>• Chicken Biryani: ~550 kcal, 32g protein<br>• Vegan Bowl: ~380 kcal, 15g protein<br>• Fresh Juice: ~90 kcal<br><br>Want a specific dish analyzed?",
        "default": f"🍽️ Great question! I can help with menus, timings, nutrition info, and dietary options. You asked: \"{last_msg['content']}\" — Let me check that for you.",
    }

    response = responses["default"]
    for key, val in responses.items():
        if key != "default" and key in question:
            response = val
            break

    st.session_state.canteen_messages.append(
        {
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%I:%M %p"),
        }
    )

    st.rerun()
