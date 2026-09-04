import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder
import random

st.set_page_config(layout="centered")

# Sample Phrase Database
PHRASES_DB = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
    {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
    {"thai": "ขอโทษครับ", "english": "Excuse me."}
]

# --- Session State ---
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

# Helper for half-width centered layout
def center_btn():
    _, col, _ = st.columns([1, 2, 1])
    return col

# --- Layout Top Padding / Header ---
st.write("") # Pushes content slightly down from the very top

# 1. Main Phrase Display Area
st.markdown(f"<h1 style='text-align: center; font-size: 38px; margin-bottom: 0px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 2. English Revealed Text (Blue & Bold)
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #0055FF; font-weight: bold; font-size: 20px; margin-bottom: 10px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #666666; font-size: 14px; margin-bottom: 10px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 3. Reveal Button
with center_btn():
    if st.button("👁 Reveal", key="btn_reveal", use_container_width=True):
        st.session_state.reveal = not st.session_state.reveal

# 4. Play Phrase Button (Orange)
with center_btn():
    if st.button("▶ Play Phrase", key="btn_play", type="primary", use_container_width=True):
        tts = gTTS(text=current_phrase["thai"], lang='th')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.session_state.tts_audio = fp.getvalue()

if st.session_state.tts_audio:
    with center_btn():
        st.audio(st.session_state.tts_audio, format='audio/mp3')

# 5. Microphone Input
st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 10px; margin-bottom: 2px;'>Microphone Input</p>", unsafe_allow_html=True)
with center_btn():
    spoken_audio = mic_recorder(
        start_prompt="🎙 Speak On",
        stop_prompt="⏹ Speak Off",
        key='recorder',
        use_container_width=True
    )

# 6. Navigation Buttons
with center_btn():
    if st.button("⬅ Previous", key="btn_prev", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total_phrases
        st.session_state.reveal = False
        st.session_state.tts_audio = None
        st.rerun()

with center_btn():
    if st.button("➡ Next", key="btn_next", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total_phrases
        st.session_state.reveal = False
        st.session_state.tts_audio = None
        st.rerun()

with center_btn():
    if st.button("🔀 Random", key="btn_rand", use_container_width=True):
        st.session_state.phrase_index = random.randint(0, total_phrases - 1)
        st.session_state.reveal = False
        st.session_state.tts_audio = None
        st.rerun()

st.divider()

# 7. Translated Field & Orange TRANSLATE Button at Bottom
text_to_show = st.session_state.translated_text if st.session_state.translated_text else "Heard Thai Text / Translation"
if spoken_audio and 'text' in spoken_audio and spoken_audio['text']:
    text_to_show = spoken_audio['text']

st.markdown(f"<div style='border: 2px solid #FF6600; border-radius: 8px; color: #FF6600; font-size: 22px; font-weight: bold; text-align: center; padding: 10px; margin-bottom: 10px;'>{text_to_show}</div>", unsafe_allow_html=True)

with center_btn():
    if st.button("TRANSLATE", key="btn_translate", type="primary", use_container_width=True):
        st.session_state.translated_text = current_phrase['english']
        st.rerun()
