import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import random

# Force page configuration to centered layout
st.set_page_config(layout="centered")

# --- Custom Styling: Compact Single-Screen Layout ---
st.markdown("""
    <style>
    /* Clean white background and remove top/bottom padding */
    .stApp {
        background-color: #FFFFFF;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 500px !important;
    }
    
    /* Compact button styling */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 0.35rem 0.5rem !important;
    }

    /* Reduce vertical padding across blocks */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -8px !important;
        padding-bottom: 0 !important;
    }

    /* Custom box for translated Thai speech text */
    .thai-speech-box {
        background-color: #FFF5EC;
        border: 2px solid #FF6600;
        border-radius: 8px;
        color: #FF6600;
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Sample database structure
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
if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None

current_phrase = PHRASES_DB[st.session_state.phrase_index]
total_phrases = len(PHRASES_DB)

# --- Navigation Functions ---
def next_phrase():
    st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total_phrases
    st.session_state.reveal = False
    st.session_state.tts_audio = None

def prev_phrase():
    st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total_phrases
    st.session_state.reveal = False
    st.session_state.tts_audio = None

def random_phrase():
    st.session_state.phrase_index = random.randint(0, total_phrases - 1)
    st.session_state.reveal = False
    st.session_state.tts_audio = None

# --- COMPACT APP LAYOUT ---

# 1. Main Phrase Display (Moved right to top)
st.markdown(f"<h1 style='text-align: center; font-size: 38px; color: #000000; margin-top: 0px; margin-bottom: 2px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 2. English Translation / Hint
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #000000; margin-bottom: 8px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #666666; font-size: 14px; margin-bottom: 8px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 3. Reveal & Play Buttons Side-by-Side
col1, col2 = st.columns(2)
with col1:
    if st.button("👁 Reveal", key="btn_reveal", use_container_width=True):
        st.session_state.reveal = not st.session_state.reveal

with col2:
    if st.button("▶ Play Phrase", key="btn_play", type="primary", use_container_width=True):
        tts = gTTS(text=current_phrase["thai"], lang='th')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.session_state.tts_audio = fp.getvalue()

if st.session_state.tts_audio:
    st.audio(st.session_state.tts_audio, format='audio/mp3')

# 4. Spoken Input Output Field (Positioned directly above recording button)
spoken_audio = mic_recorder(
    start_prompt="🎙 Speak On",
    stop_prompt="⏹ Speak Off",
    key='recorder',
    use_container_width=True
)

text_to_show = "Heard Thai Text Goes Here..."
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']

st.markdown(f"<div class='thai-speech-box'>{text_to_show}</div>", unsafe_allow_html=True)

# 5. Bottom Navigation Bar
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("⬅ Prev", key="btn_prev", use_container_width=True):
        prev_phrase()
        st.rerun()

with nav2:
    if st.button("🔀 Random", key="btn_rand", use_container_width=True):
        random_phrase()
        st.rerun()

with nav3:
    if st.button("➡ Next", key="btn_next", use_container_width=True):
        next_phrase()
        st.rerun()
