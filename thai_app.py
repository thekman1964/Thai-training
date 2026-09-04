import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import random

# Force page configuration
st.set_page_config(layout="centered")

# --- Custom Styling: White Background, Dark Text & Tight Spacing ---
st.markdown("""
    <style>
    /* 1. Force Pure White App Background */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }

    /* 2. Style Default Text to Dark/Black */
    h1, h2, h3, p, div, label, span, [data-testid="stMarkdownContainer"] p {
        color: #111111 !important;
    }

    /* 3. Button Styling: Half-Width, Centered, Large Font */
    div.stButton > button {
        width: 50% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        display: block !important;
        background-color: #1A202C !important; /* Navy Blue */
        color: #FFFFFF !important;
        border: none !important;
    }
    
    /* Hover state for buttons */
    div.stButton > button:hover {
        background-color: #2D3748 !important;
        color: #FFFFFF !important;
    }

    /* 4. Primary Buttons (Play & Translate) Styled Orange */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #E05A00 !important;
    }

    /* 5. Reduce Vertical Padding/Spacing Between Elements */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -10px !important;
        padding-bottom: 0 !important;
    }

    /* 6. Orange Output Text for Interpreted Speech */
    .thai-speech-output {
        color: #FF6600 !important;
        font-size: 36px !important;
        font-weight: bold !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    
    /* Audio Player Styling */
    audio {
        width: 100%;
        margin-top: 10px;
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
st.markdown(f"<h1 style='text-align: center; font-size: 44px; color: #111111; margin-bottom: 5px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# English Translation / Hint
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; font-size: 20px; color: #111111;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #666666; font-size: 16px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

st.write("")

# Reveal Button
if st.button("👁 Reveal", key="btn_reveal", use_container_width=True):
    st.session_state.reveal = not st.session_state.reveal

# Play Phrase Button (Primary / Orange)
if st.button("▶ Play Phrase", key="btn_play", type="primary", use_container_width=True):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.session_state.tts_audio = fp.getvalue()

if st.session_state.tts_audio:
    st.audio(st.session_state.tts_audio, format='audio/mp3')

# Microphone Input Section
st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 15px;'>Microphone Input:</p>", unsafe_allow_html=True)
spoken_audio = mic_recorder(
    start_prompt="🎙 Start Speaking",
    stop_prompt="⏹ Stop Recording",
    key='recorder',
    use_container_width=True
)

st.write("")

# Navigation Buttons
if st.button("⬅ Previous", key="btn_prev", use_container_width=True):
    prev_phrase()
    st.rerun()

if st.button("➡ Next", key="btn_next", use_container_width=True):
    next_phrase()
    st.rerun()

if st.button("🔀 Random", key="btn_rand", use_container_width=True):
    random_phrase()
    st.rerun()

st.divider()

# Interpreted Speech Output
text_to_show = "Heard Thai Text Goes Here..."
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']

st.markdown(f"<div class='thai-speech-output'>{text_to_show}</div>", unsafe_allow_html=True)

# Translate Button (Primary / Orange)
if st.button("TRANSLATE", key="btn_translate", type="primary", use_container_width=True):
    st.session_state.translated = True
