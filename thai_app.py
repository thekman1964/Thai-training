import streamlit as st
import random

st.set_page_config(layout="centered", page_title="Thai Practice")

# Universal CSS forcing Thai-compatible font rendering on mobile browsers
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.8rem !important; max-width: 500px;}
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 48px; margin-bottom: 4px;}
    h1, p, div, span, button, input {font-family: Tahoma, Arial, sans-serif !important;}
    </style>
""", unsafe_allow_html=True)

# Direct, unbreakable dataset with native Thai text
PHRASES_DB = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
    {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"},
    {"thai": "ห้องน้ำอยู่ที่ไหนครับ", "english": "Where is the restroom?", "category": "GENERAL"},
    {"thai": "เผ็ดนิดหน่อยครับ", "english": "A little bit spicy, please.", "category": "FOOD"}
]

if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

st.markdown("<div style='text-align: center;'><h3>🇹🇭 Thai Listening & Reading</h3></div>", unsafe_allow_html=True)

current_card = PHRASES_DB[st.session_state.index % len(PHRASES_DB)]

st.markdown("---")
# Explicit Thai font styling applied directly to the flashcard header
st.markdown(f"<h1 style='text-align: center; font-size: 34px; margin-bottom: 4px; font-family: Tahoma, Arial, sans-serif;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.revealed:
    st.markdown(f"<p style='text-align: center; font-size: 20px; color: #0066CC; font-weight: bold;'>{current_card['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; font-size: 13px; color: #777;'>Click 'Reveal' to view English translation</p>", unsafe_allow_html=True)

if st.button("REVEAL", type="primary"):
    st.session_state.revealed = not st.session_state.revealed
    st.rerun()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("BACK"):
        st.session_state.index = (st.session_state.index - 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()
with col2:
    if st.button("RANDOM"):
        st.session_state.index = random.randint(0, len(PHRASES_DB) - 1)
        st.session_state.revealed = False
        st.rerun()
with col3:
    if st.button("NEXT"):
        st.session_state.index = (st.session_state.index + 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()
