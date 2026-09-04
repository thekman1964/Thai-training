import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import random

st.set_page_config(layout="centered")

# --- Mobile Compact Styling ---
st.markdown("""
    <style>
    /* Force white background and zero out top margins */
    .stApp { background-color: #FFFFFF !important; }
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 0.5rem !important; 
        max-width: 420px !important; 
    }
    
    /* Compact half-width buttons with explicit light text */
    div.stButton > button {
        width: 60% !important;
        margin: 0 auto !important;
        display: block !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        font-size: 15px !important;
        padding: 4px 8px !important;
        background-color: #2D3748 !important;
        color: #FFFFFF !important;
    }

    /* Primary Orange Buttons (Play & Translate) */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
    }

    /* Orange Output Display Field at Bottom */
    .thai-speech-box {
        border: 2px solid #FF6600;
        background-color: #FFF5EC;
        border-radius: 6px;
        color: #FF6600;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        padding: 6px;
        margin: 6px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sample Phrase Database
PHRASES_DB = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
    {"thai": "ขอโทษครับ", "english": "Excuse me."}
]

# Session State
if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False
if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

current_phrase = PHRASES_DB[st.session_state.phrase_index]
total_phrases = len(PHRASES_DB)

# 1. Main Phrase Display
st.markdown(f"<h1 style='text-align: center; font-size: 34px; color: #000000; margin-top: 0; margin-bottom: 2px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 2. English Translation (Blue & Bold when revealed)
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #0055FF; font-weight: bold; font-size: 18px; margin-bottom: 6px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #666666; font-size: 13px; margin-bottom: 6px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 3. Action Buttons
if st.button("👁 Reveal", key="btn_reveal"):
    st.session_state.reveal = not st.session_state.reveal

if st.button("▶ Play Phrase", key="btn_play", type="primary"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.session_state.tts_audio = fp.getvalue()

if st.session_state.tts_audio:
    st.audio(st.session_state.tts_audio, format='audio/mp3')

# 4. Microphone Input Toggle
spoken_audio = mic_recorder(
    start_prompt="🎙 Speak On",
    stop_prompt="⏹ Speak Off",
    key='recorder',
    use_container_width=True
)

# 5. Navigation Controls
if st.button("⬅ Previous", key="btn_prev"):
    st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total_phrases
    st.session_state.reveal = False
    st.session_state.tts_audio = None
    st.rerun()

if st.button("➡ Next", key="btn_next"):
    st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total_phrases
    st.session_state.reveal = False
    st.session_state.tts_audio = None
    st.rerun()

if st.button("🔀 Random", key="btn_rand"):
    st.session_state.phrase_index = random.randint(0, total_phrases - 1)
    st.session_state.reveal = False
    st.session_state.tts_audio = None
    st.rerun()

# 6. Bottom Output Box & Orange Translate Button
text_to_show = st.session_state.translated_text if st.session_state.translated_text else "Heard Thai Text / Translation"
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']

st.markdown(f"<div class='thai-speech-box'>{text_to_show}</div>", unsafe_allow_html=True)

if st.button("TRANSLATE", key="btn_translate", type="primary"):
    st.session_state.translated_text = current_phrase['english']
    st.rerun()
