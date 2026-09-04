import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text
import random

st.set_page_config(layout="centered")

# --- Database ---
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

# --- Header ---
st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 0px;'>Thai Listening and Reading</h2>", unsafe_allow_html=True)

# --- Main Phrase Box ---
st.markdown(f"<h1 style='text-align: center; font-size: 48px; color: #000000; margin-top: 10px; margin-bottom: 0px;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #333333; font-size: 20px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #888888; font-size: 16px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# Helper function: Creates half-width centered layout via native columns
def half_width_col():
    _, col, _ = st.columns([1, 2, 1])
    return col

# 1. Reveal Button
with half_width_col():
    if st.button("👁 Reveal", use_container_width=True):
        st.session_state.reveal = not st.session_state.reveal

# 2. Play Phrase Button
with half_width_col():
    if st.button("▶ Play Phrase", type="primary", use_container_width=True):
        tts = gTTS(text=current_phrase["thai"], lang='th')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')

# 3. Mic Recording
with half_width_col():
    spoken_text = speech_to_text(
        language='th', 
        start_prompt="🎙 Start Speaking", 
        stop_prompt="⏹ Stop", 
        key='speech', 
        use_container_width=True
    )

# 4. Navigation Buttons (Previous, Next, Random)
with half_width_col():
    if st.button("⬅ Previous", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total
        st.session_state.reveal = False
        st.rerun()

with half_width_col():
    if st.button("➡ Next", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total
        st.session_state.reveal = False
        st.rerun()

with half_width_col():
    if st.button("🔀 Random", use_container_width=True):
        st.session_state.phrase_index = random.randint(0, total - 1)
        st.session_state.reveal = False
        st.rerun()

st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)

# --- Bottom Section: Heard Thai Text in Orange ---
text_to_show = spoken_text if spoken_text else "Cannot Understand"
st.markdown(f"<h1 style='text-align: center; font-size: 44px; color: #FF6600; margin-top: 5px; margin-bottom: 10px;'>{text_to_show}</h1>", unsafe_allow_html=True)

# 5. Orange Translate Button
with half_width_col():
    st.button("TRANSLATE", type="primary", use_container_width=True)
