import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text
import random

# --- SET CONFIGURATION TO FORCE LIGHT THEME BASE ---
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

# Placeholder phrases database (until you add your JSON/Sheets sync)
PHRASES_DB = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
    {"thai": "ขอโทษครับ", "english": "Excuse me / I'm sorry."}
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

# --- INJECT CUSTOM CSS TO MATCH USER SKETCH ---
# This forces white background, sets navy buttons, orange highlights, 
# reduces vertical spacing, and defines font sizes.
st.markdown("""
    <style>
    /* Force Light Mode Aesthetics on the App Container */
    .stApp {
        background-color: white !important;
        color: black !important;
    }

    /* Target headers and standard text to be black */
    h1, h2, h3, p, div[data-testid="stMarkdownContainer"] p {
        color: black !important;
    }

    /* Redefine 'Primary' buttons (used for orange accents) */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important; /* Specific Orange */
        color: white !important;
        border: 2px solid #FF6600 !important;
        font-size: 22px !important; /* Large text */
        font-weight: bold !important;
    }

    /* Redefine 'Secondary' buttons (the standard navy ones) */
    div.stButton > button[kind="secondary"] {
        background-color: #1A202C !important; /* specific Navy */
        color: white !important;
        border: 1px solid #1A202C !important;
        font-size: 22px !important; /* Large text */
        font-weight: bold !important;
    }

    /* TIGHTEN VERTICAL SPACING BETWEEN BLOCKS */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -15px !important; /* Reduces gap drastically */
        padding-bottom: 0 !important;
    }

    /* Define Orange Output Text for Interpreted Speech */
    .thai-speech-output {
        color: #FF6600 !important; /* Orange */
        font-size: 38px !important; /* Matching main phrase size */
        font-weight: bold !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        font-family: inherit;
    }
    
    /* Ensure audio player is black/visible */
    audio {
        filter: invert(1) grayscale(1);
    }
    </style>
""", unsafe_allow_html=True) # --- TYPO FIXED HERE (True, not e) ---

# --- App Layout ---

# 1. Title
st.markdown("<h1 style='text-align: center;'>Thai Listening and Reading</h1>", unsafe_allow_html=True)

# 2. Main Phrase Display area (White card effect)
st.markdown(f"<h1 style='text-align: center; font-size: 48px; color: black; margin-bottom: 5px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: black;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: gray;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# Spacing Helper
st.write("")

# Helper function to generate centered half-width buttons
def centered_button(label, key, type="secondary"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(label, key=key, use_container_width=True, type=type)

# 3. Reveal Button (Navy)
if centered_button("👁 Reveal", "btn_reveal"):
    st.session_state.reveal = not st.session_state.reveal

# 4. Play Phrase Button (Orange styling)
# Type="primary" triggers the custom orange CSS rule
if centered_button("▶ Play Phrase", "btn_play", type="primary"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.session_state.tts_audio = fp.getvalue()

# Display audio player if generated
if st.session_state.tts_audio:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.audio(st.session_state.tts_audio, format='audio/mp3')

# 5. Microphone Recording (Centered)
# The library styles this itself, but centering helps
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    spoken_text = speech_to_text(
        language='th', 
        start_prompt="🎙 Start Speaking", 
        stop_prompt="⏹ Stop", 
        key='speech',
        use_container_width=True
    )

# 6. Navigation Buttons (Navy)
if centered_button("⬅ Previous", "btn_prev"):
    prev_phrase()
    st.rerun()

if centered_button("➡ Next", "btn_next"):
    next_phrase()
    st.rerun()

if centered_button("🔀 Random", "btn_rand"):
    random_phrase()
    st.rerun()

# 7. Divider and Lower Section
st.divider()

# --- Interpreted Speech Display (Orange Text) ---
# Default/Error text can be provided if needed
text_to_show = spoken_text if spoken_text else "Cannot Understand / Say something..."
st.markdown(f"<div class='thai-speech-output'>{text_to_show}</div>", unsafe_allow_html=True)

# 8. Orange TRANSLATE Button
if centered_button("TRANSLATE", "btn_translate", type="primary"):
    st.session_state.translated = True

if st.session_state.get('translated') and spoken_text:
    st.info("Translation module triggered. Hook up API here.")
