import streamlit as st
from gtts import gTTS
import io
import base64
from streamlit_mic_recorder import mic_recorder
import random

st.set_page_config(layout="centered")

# --- Custom CSS Styling & Forced Horizontal Layout ---
st.markdown("""
    <style>
    /* Force Light Theme */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Shift whole page content upward */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* Target all Streamlit buttons for clean single-line text */
    div.stButton > button, div[data-testid="stCustomComponent"] button {
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 8px 0px !important;
        white-space: nowrap !important;
    }

    /* Orange Primary Buttons & Custom Mic Button Styling */
    div.stButton > button[kind="primary"], div[data-testid="stCustomComponent"] button {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        border: none !important;
        width: 100% !important;
    }

    /* Navy Secondary Buttons */
    div.stButton > button[kind="secondary"] {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* FORCE HORIZONTAL ROW ON MOBILE: Prevent st.columns from stacking vertically */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0px !important;
        min-width: 0 !important;
    }

    /* Reduce Vertical Gaps Between Blocks */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -10px !important;
        padding-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to center single controls
def centered_button(label, key, type="secondary"):
    _, col, _ = st.columns([1, 4, 1])
    with col:
        return st.button(label, key=key, type=type, use_container_width=True)

# Dataset
PHRASES_DB = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
    {"thai": "ขอโทษครับ", "english": "Excuse me."}
]

# --- Initialize Session State ---
if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False
if "interpreted_thai" not in st.session_state:
    st.session_state.interpreted_thai = ""

current_phrase = PHRASES_DB[st.session_state.phrase_index]
total = len(PHRASES_DB)

# 1. Main Title & Main Thai Phrase Display
st.markdown("<h3 style='text-align: center; color: #000000; margin-top: 0px;'>Thai Listening and Reading</h3>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; font-size: 40px; color: #000000; margin: 4px 0;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 2. English Hint Text under Main Phrase (Blue Text)
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #0066CC; font-size: 20px; font-weight: bold; margin-bottom: 4px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #777777; font-size: 15px; margin-bottom: 4px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 3. Reveal Button
if centered_button("👁 Reveal", "btn_reveal", type="secondary"):
    st.session_state.reveal = not st.session_state.reveal

# 4. Play Phrase Button
if centered_button("▶ Play Phrase", "btn_play", type="primary"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64_audio = base64.b64encode(fp.getvalue()).decode()
    md_audio = f'<audio autoplay src="data:audio/mp3;base64,{b64_audio}"></audio>'
    st.markdown(md_audio, unsafe_allow_html=True)

# 5. Navigation Buttons (Horizontal Layout)
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("⬅ Prev", key="btn_prev", type="secondary", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total
        st.session_state.reveal = False
        st.session_state.interpreted_thai = ""
        st.rerun()

with nav_col2:
    if st.button("🔀 Rand", key="btn_rand", type="secondary", use_container_width=True):
        st.session_state.phrase_index = random.randint(0, total - 1)
        st.session_state.reveal = False
        st.session_state.interpreted_thai = ""
        st.rerun()

with nav_col3:
    if st.button("➡ Next", key="btn_next", type="secondary", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total
        st.session_state.reveal = False
        st.session_state.interpreted_thai = ""
        st.rerun()

st.divider()

# 6. Interpreted Thai Output Display Field
if st.session_state.interpreted_thai:
    st.markdown(f"<h2 style='text-align: center; color: #FF6600; font-size: 32px; font-weight: bold;'>{st.session_state.interpreted_thai}</h2>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #888888; font-size: 15px;'>Spoken Thai text will display here...</p>", unsafe_allow_html=True)

# 7. Integrated Translate / Microphone Button
_, translate_col, _ = st.columns([1, 4, 1])
with translate_col:
    spoken_audio = mic_recorder(
        start_prompt="🎙 TRANSLATE",
        stop_prompt="⏹ Stop Recording",
        key='translate_recorder',
        use_container_width=True
    )

# Capture transcribed text into the output field without error states
if spoken_audio and 'text' in spoken_audio and spoken_audio['text'].strip():
    st.session_state.interpreted_thai = spoken_audio['text']
