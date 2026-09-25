# -*- coding: utf-8 -*-
import streamlit as st
import random
import base64

st.set_page_config(layout="centered", page_title="Thai Practice")

# Universal CSS forcing clean font rendering on mobile
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.8rem !important; max-width: 500px;}
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 48px; margin-bottom: 4px;}
    h1, p, div, span, button {font-family: Tahoma, Arial, sans-serif !important;}
    </style>
""", unsafe_allow_html=True)

def d(b64):
    return base64.b64decode(b64.encode('ascii')).decode('utf-8')

# 100% Pure ASCII Base64-encoded Thai data (immune to editor encoding bugs)
PHRASES_DB = [
    {
        "thai": d("4Lit4Lix4LiZ4Li44LmI4Lih4Liq4Liy4Lij4Liw"), 
        "english": "Turn right please.", 
        "category": "NAVIGATION"
    },
    {
        "thai": d("4Lit4Li44LmI4Lih4Li04LmA4Liq4Li34Lit4Liq4Liy4Lij4Liw4Lit4Li44LmI4Lih4Li04Lit4Lix4LiZ"), 
        "english": "Go straight then turn left.", 
        "category": "NAVIGATION"
    },
    {
        "thai": d("4Lit4Liy4LiE4Liy4Lij4Liw"), 
        "english": "Excuse me.", 
        "category": "GENERAL"
    },
    {
        "thai": d("4Lih4Liy4LmM4Lit4Liy4LiE4Li04LiZ4Lii4Liy4Lij4Liw4Liq4Liy4Lij4Liw"), 
        "english": "Where is the restroom?", 
        "category": "GENERAL"
    }
]

if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

st.markdown("<div style='text-align: center;'><h3>🇹🇭 Thai Listening & Reading</h3></div>", unsafe_allow_html=True)

current_card = PHRASES_DB[st.session_state.index % len(PHRASES_DB)]

st.markdown("---")
st.markdown(f"<h1 style='text-align: center; font-size: 36px; margin-bottom: 4px;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

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
