import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text
import random

# --- INITIAL APP CONFIGURATION ---
# This forces light base, centers the layout, and collapses sidebars.
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS FOR USER SKETCH DESIGN ---
# This forces white background, navy buttons, orange accents, 
# massive font sizes, and DRASTICALLY tighter vertical gaps.
st.markdown("""
    <style>
    /* 1. Force White Background on App & Content Containers */
    .stApp, div[data-testid="stSidebar"], div.block-container {
        background-color: white !important;
        color: black !important;
    }

    /* 2. Style Default text (paragraphs, dividers, etc.) to black */
    p, hr, div[data-testid="stMarkdownContainer"] p {
        color: black !important;
    }

    /* 3. Increase header sizes for the main title */
    h1 {
        font-size: 42px !important;
        text-align: center;
        margin-bottom: 5px !important;
    }

    /* 4. DRASTICALLY REDUCE SPACE BETWEEN BUTTONS */
    /* Streamlit uses flex gaps; we force it to -10px */
    div[data-testid="stVerticalBlock"] {
        gap: -10px !important;
    }
    
    /* Also target the inner margin of standard blocks */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -10px !important;
        padding-bottom: 0 !important;
    }

    /* 5. General Button Styling (Navy base, massive font) */
    div.stButton > button {
        font-size: 24px !important; /* Massive font */
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }

    /* Specific Primary Button (Orange Translate / Play) */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important; /* Specific Orange */
        color: white !important;
    }

    /* Specific Secondary Button (Navy Navigation/Reveal) */
    div.stButton > button[kind="secondary"] {
        background-color: #1A202C !important; /* Specific Navy */
        color: white !important;
    }
    
    /* 6. Orange Output Text for Interpreted Speech */
    .thai-speech-output {
        color: #FF6600 !important; /* Orange */
        font-size: 48px !important; /* Same size as main phrase */
        font-weight: bold !important;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 5px;
        font-family: inherit;
    }
    
    /* Visibility fix for audio player against white */
    audio {
        filter: invert(1) grayscale(1);
    }
    </style>
""", unsafe_allow_html=True)

# Placeholder database for testing navigation
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
if 'translated' not in st.session_state:
    st.session_state.translated = False

current_phrase = PHRASES_DB[st.session_state.phrase_index]
total_phrases = len(PHRASES_DB)

# Helper function to generate centered half-width buttons
# Columns([1, 2, 1]) ensures the button takes 50% width centered on screen.
def centered_button(label, key, type="secondary"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(label, key=key, use_container_width=True, type=type)

# --- APP LAYOUT (DESIGNED LIKE SKETCH) ---

# 1. Main Title
st.title("Thai Listening and Reading")

# 2. Main Phrase Display area (White background implied)
st.markdown(f"<h1 style='text-align: center; font-size: 48px; color: black; margin-bottom: 2px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 3. English Hint text (Gray)
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: black;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: gray; font-size: 16px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 4. Reveal Button (Navy, Half Width)
if centered_button("👁 Reveal", "btn_reveal", type="secondary"):
    st.session_state.reveal = not st.session_state.reveal

# 5. Play Phrase Button (Orange styling, Half Width)
# Type="primary" triggers the custom orange CSS rule
if centered_button("▶ Play Phrase", "btn_play", type="primary"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3')

# 6. Microphone Recording (Centered, Library styles itself but centering helps)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    spoken_text = speech_to_text(language='th', start_prompt="🎙 Start Speaking", stop_prompt="⏹ Stop", key='speech', use_container_width=True)

# 7. Navigation Buttons (Navy, Half Width)
if centered_button("⬅ Previous", "btn_prev", type="secondary"):
    st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total_phrases
    st.session_state.reveal = False
    st.rerun()

if centered_button("➡ Next", "btn_next", type="secondary"):
    st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total_phrases
    st.session_state.reveal = False
    st.rerun()

if centered_button("🔀 Random", "btn_rand", type="secondary"):
    st.session_state.phrase_index = random.randint(0, total_phrases - 1)
    st.session_state.reveal = False
    st.rerun()

st.divider()

# --- Interpreted Speech Display (Orange Text, Large Font) ---
# Defaults to prompt text if nothing is heard
text_to_show = spoken_text if spoken_text else "Cannot Understand..."
st.markdown(f"<div class='thai-speech-output'>{text_to_show}</div>", unsafe_allow_html=True)

# 8. Orange TRANSLATE Button (Half Width)
if centered_button("TRANSLATE", "btn_translate", type="primary"):
    st.session_state.translated = True

if st.session_state.get('translated') and spoken_text:
    st.info("Translation module triggered. Hook up API here.")
