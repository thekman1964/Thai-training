import streamlit as st
from gtts import gTTS
import io
import base64
from streamlit_mic_recorder import mic_recorder
import random

st.set_page_config(layout="centered")

# --- Custom CSS for Styling & Typography ---
st.markdown("""
    <style>
    /* Force Light Theme */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Target all Streamlit buttons to force single-line text and proper height */
    div.stButton > button {
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px 0px !important;
        white-space: nowrap !important;
    }

    /* Orange Primary Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* Navy Secondary Buttons */
    div.stButton > button[kind="secondary"] {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* Reduce Vertical Gaps Between Elements */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -6px !important;
        padding-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to reliably center and widen every button using native columns
def centered_button(label, key, type="secondary"):
    _, col, _ = st.columns([1, 4, 1])
    with col:
        return st.button(label, key=key, type=type, use_container_width=True)

# Sample Dataset
PHRASES_DB = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
    {"thai": "ขอโทษครับ", "english": "Excuse me."}
]

if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False

current_phrase = PHRASES_DB[st.session_state.phrase_index]
total = len(PHRASES_DB)

# 1. Main Title & Thai Display
st.markdown("<h2 style='text-align: center; color: #000000;'>Thai Listening and Reading</h2>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; font-size: 42px; color: #000000; margin: 10px 0;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #333333; font-size: 20px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #777777; font-size: 16px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 2. Reveal Button
if centered_button("👁 Reveal", "btn_reveal", type="secondary"):
    st.session_state.reveal = not st.session_state.reveal

# 3. Play Phrase Button (Autoplays background audio without showing player bar)
if centered_button("▶ Play Phrase", "btn_play", type="primary"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64_audio = base64.b64encode(fp.getvalue()).decode()
    md_audio = f'<audio autoplay src="data:audio/mp3;base64,{b64_audio}"></audio>'
    st.markdown(md_audio, unsafe_allow_html=True)

# 4. Microphone Input Button
_, mic_col, _ = st.columns([1, 4, 1])
with mic_col:
    spoken_audio = mic_recorder(
        start_prompt="🎙 Speak On",
        stop_prompt="⏹ Stop",
        key='recorder',
        use_container_width=True
    )

# 5. Navigation Buttons (Centered and stack evenly)
if centered_button("⬅ Previous", "btn_prev", type="secondary"):
    st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total
    st.session_state.reveal = False
    st.rerun()

if centered_button("➡ Next", "btn_next", type="secondary"):
    st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total
    st.session_state.reveal = False
    st.rerun()

if centered_button("🔀 Random", "btn_rand", type="secondary"):
    st.session_state.phrase_index = random.randint(0, total - 1)
    st.session_state.reveal = False
    st.rerun()

st.divider()

# 6. Bottom English Translation Output Box
text_to_show = current_phrase["english"]
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']

st.markdown(f"<h2 style='text-align: center; color: #FF6600; font-size: 28px;'>{text_to_show}</h2>", unsafe_allow_html=True)

# 7. Translate Button
centered_button("TRANSLATE", "btn_translate", type="primary")
