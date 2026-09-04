import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import random

# Force page configuration to force mobile sizing behavior
st.set_page_config(layout="centered")

# --- Custom Styling for Forced Mobile Sizing and Spacing ---
# This styles ALL buttons to be narrow, large font, tight spacing, and sets specific colors.
st.markdown("""
    <style>
    /* 1. Target all elements/buttons and constrain width/margin */
    div.stButton > button {
        width: 50% !important; /* Force all buttons to be half width */
        margin-left: auto !important; /* Center the buttons */
        margin-right: auto !important;
        font-size: 22px !important; /* Large text font */
        font-weight: bold !important;
        border-radius: 8px !important;
        display: block !important;
    }

    /* 2. Style Default text (paragraphs, dividers, etc.) to black */
    p, hr, div[data-testid="stMarkdownContainer"] p {
        color: black !important;
    }

    /* 3. TIGHTEN VERTICAL SPACING BETWEEN BLOCKS */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -15px !important; /* Drastically reduces spacing drastically */
        padding-bottom: 0 !important;
    }

    /* 4. Primary / Translate / Play Button Styling (Orange) */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important; /* Specific Orange */
        color: white !important;
        border: none !important;
    }

    /* 5. Start/Stop Microphone Buttons (Green/Red styling) */
    #recorder-start-button {
        background-color: #28a745 !important; /* Specific Green */
        color: white !important;
        border: none !important;
    }
    #recorder-stop-button {
        background-color: #dc3545 !important; /* Specific Red */
        color: white !important;
        border: none !important;
    }

    /* 6. Orange Output Text for Interpreted Speech */
    .thai-speech-output {
        color: #FF6600 !important; /* Orange */
        font-size: 44px !important; /* Same size as main phrase */
        font-weight: bold !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        font-family: inherit;
    }

    /* Visibility fix for audio player against white */
    audio {
        filter: invert(1) grayscale(1);
    }
    </style>
""", unsafe_allow_html=True)

# Placeholder database structure for testing navigation
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

# --- Define Navigation Functions ---
def next_phrase():
    st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total_phrases
    st.session_state.reveal = False
    st.session_state.tts_audio = None # Reset audio on nav

def prev_phrase():
    st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total_phrases
    st.session_state.reveal = False
    st.session_state.tts_audio = None # Reset audio on nav

def random_phrase():
    st.session_state.phrase_index = random.randint(0, total_phrases - 1)
    st.session_state.reveal = False
    st.session_state.tts_audio = None # Reset audio on nav

# --- APP LAYOUT ---

# 1. Title
st.title("Thai Listening and Reading")

# 2. Main Phrase Display area (large black font)
st.markdown(f"<h1 style='text-align: center; font-size: 48px; color: black; margin-bottom: 2px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 3. English Hint text (Gray)
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: black;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: gray; font-size: 16px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# Spacing Helper
st.write("")

# 4. Reveal Button (Navy/Default styling, 50% width)
if st.button("👁 Reveal", key="btn_reveal", use_container_width=True):
    st.session_state.reveal = not st.session_state.reveal

# 5. Play Phrase Button (Orange styling, 50% width)
# Type="primary" triggers the custom orange CSS rule
if st.button("▶ Play Phrase", key="btn_play", type="primary", use_container_width=True):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.session_state.tts_audio = fp.getvalue()

# Display audio player below the button if generated
if st.session_state.tts_audio:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.audio(st.session_state.tts_audio, format='audio/mp3')

# 6. Microphone Recording Section (Centered)
# Provides explicit "Start Recording" and "Stop Recording" options
st.markdown("<p style='text-align: center; font-weight: bold; margin-bottom: 2px;'>Microphone Input:</p>", unsafe_allow_html=True)
spoken_audio = mic_recorder(
    start_prompt="🎙 Start Speaking",
    stop_prompt="⏹ Stop Recording",
    key='recorder',
    use_container_width=True
)

# Spacing Helper
st.write("")

# 7. Navigation Buttons (Navy/Default styling, 50% width)
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

# --- Orange Output Text for Interpreted Speech ---
# Defaults to prompt text if nothing is heard
text_to_show = "Heard Thai Text Goes Here..."
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']
else:
    text_to_show = "Cannot Understand / Please speak Thai..."

st.markdown(f"<div class='thai-speech-output'>{text_to_show}</div>", unsafe_allow_html=True)

# 8. Orange TRANSLATE Button (50% width)
# type="primary" triggers the orange CSS styling rule
if st.button("TRANSLATE", key="btn_translate", type="primary", use_container_width=True):
    st.session_state.translated = True

# Logic for translate button if needed (Placeholder)
if st.session_state.get('translated') and spoken_audio:
    st.info("Translation function triggered. Hook up Google Translate API logic here.")
