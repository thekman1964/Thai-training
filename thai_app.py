import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import random

# Force page configuration
st.set_page_config(layout="centered")

# --- Custom Styling: Clean Light Theme ---
st.markdown("""
    <style>
    /* Clean background */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Ensure readable text color on buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
    }

    /* Orange output text for interpreted speech */
    .thai-speech-output {
        color: #FF6600;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 15px;
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
if 'translated' not in st.session_state:
    st.session_state.translated = False

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

# --- APP LAYOUT ---

st.title("Thai Listening and Reading")

# Main Phrase Display Area
st.markdown(f"<h1 style='text-align: center; font-size: 40px; color: #000000; margin-bottom: 5px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# English Translation / Hint
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; font-size: 20px; color: #000000;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #555555; font-size: 16px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# Reveal & Play Phrase Buttons
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

st.markdown("---")

# Microphone Input Section
st.markdown("<h4 style='text-align: center;'>Microphone Input</h4>", unsafe_allow_html=True)
spoken_audio = mic_recorder(
    start_prompt="🎙 Start Speaking",
    stop_prompt="⏹ Stop Recording",
    key='recorder',
    use_container_width=True
)

# Interpreted Speech Output
text_to_show = "Heard Thai Text Goes Here..."
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']

st.markdown(f"<div class='thai-speech-output'>{text_to_show}</div>", unsafe_allow_html=True)

# Translate Button
if st.button("TRANSLATE", key="btn_translate", type="primary", use_container_width=True):
    st.session_state.translated = True

st.markdown("---")

# Navigation Buttons
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("⬅ Previous", key="btn_prev", use_container_width=True):
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
