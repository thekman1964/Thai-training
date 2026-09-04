import streamlit as st
from gtts import gTTS
import io
from googletrans import Translator
from streamlit_mic_recorder import mic_recorder
import random

translator = Translator()

# Force page configuration
st.set_page_config(layout="centered")

# --- Custom Styling for Forced Mobile Sizing ---
st.markdown("""
    <style>
    /* Force mobile container width limit */
    .element-container, .stButton {
        max-width: 50% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    div.stButton > button {
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 10px 0px !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sample Phrase Database
PHRASES = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."}
]

if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

current = PHRASES[st.session_state.phrase_index]

# Header
st.markdown("<h2 style='text-align: center;'>Thai Listening and Reading</h2>", unsafe_allow_html=True)

# Main Thai Phrase Display
st.markdown(f"<h1 style='text-align: center; font-size: 42px;'>{current['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center;'>{current['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: gray;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 1. Reveal Button
if st.button("👁 Reveal", key="btn_reveal"):
    st.session_state.reveal = not st.session_state.reveal

# 2. Play Phrase Button
if st.button("▶ Play Phrase", key="btn_play"):
    tts = gTTS(text=current["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3')

# 3. Speech Audio Recorder (Start & Stop)
st.markdown("<p style='text-align: center; font-weight: bold;'>Voice Input:</p>", unsafe_allow_html=True)
audio_record = mic_recorder(
    start_prompt="🎙 Start Speaking",
    stop_prompt="⏹ Stop Speaking",
    key='recorder'
)

# 4. Navigation Buttons
if st.button("⬅ Previous", key="btn_prev"):
    st.session_state.phrase_index = (st.session_state.phrase_index - 1) % len(PHRASES)
    st.session_state.reveal = False
    st.rerun()

if st.button("➡ Next", key="btn_next"):
    st.session_state.phrase_index = (st.session_state.phrase_index + 1) % len(PHRASES)
    st.session_state.reveal = False
    st.rerun()

if st.button("🔀 Random", key="btn_rand"):
    st.session_state.phrase_index = random.randint(0, len(PHRASES) - 1)
    st.session_state.reveal = False
    st.rerun()

st.divider()

# --- Orange Output Display & Translation ---
display_text = current["thai"] if not st.session_state.translated_text else st.session_state.translated_text
st.markdown(f"<h1 style='text-align: center; color: #FF6600; font-size: 40px;'>{display_text}</h1>", unsafe_allow_html=True)

# 5. Translate Button
if st.button("TRANSLATE", key="btn_trans", type="primary"):
    try:
        res = translator.translate(current["thai"], src='th', dest='en')
        st.session_state.translated_text = res.text
        st.rerun()
    except Exception:
        st.session_state.translated_text = "Cannot Understand"
        st.rerun()
