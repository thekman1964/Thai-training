import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text

# --- Custom Styling (Reduces Spacing & Increases Button Font) ---
st.markdown("""
    <style>
    /* Reduce vertical padding between Streamlit blocks */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -10px; /* Reduces space between buttons */
    }
    /* Button Text Styling */
    div.stButton > button {
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 8px;
    }
    /* Primary / Translate Button Styling */
    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important;
        color: white !important;
        border: none !important;
    }
    /* Orange Display Text for Interpreted Speech */
    .thai-speech-output {
        color: #FF6600;
        font-size: 38px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Thai Listening and Reading")

# Setup App State / Phrases (Placeholder data structure)
if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False

phrases = [
    {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."}
]
current_phrase = phrases[st.session_state.phrase_index]

# Main Thai Phrase Display Box
st.markdown(f"<h1 style='text-align: center; color: black;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: gray;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# Function to center smaller buttons (half width)
def centered_button(label, key=None, type="secondary"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(label, key=key, use_container_width=True, type=type)

# 1. Reveal Button
if centered_button("👁 Reveal", key="btn_reveal"):
    st.session_state.reveal = not st.session_state.reveal

# 2. Play Phrase Button
if centered_button("▶ Play Phrase", key="btn_play"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3')

# 3. Mic Recording
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    spoken_text = speech_to_text(language='th', start_prompt="🎙 Start Speaking", stop_prompt="⏹ Stop", key='speech')

# 4. Navigation Buttons
if centered_button("⬅ Previous", key="btn_prev"):
    st.session_state.reveal = False
if centered_button("➡ Next", key="btn_next"):
    st.session_state.reveal = False
if centered_button("🔀 Random", key="btn_rand"):
    st.session_state.reveal = False

st.divider()

# --- Orange Speech Field and Translate Section ---
if 'translated' not in st.session_state:
    st.session_state.translated = False

# Display what the app hears in Thai (or default/error text)
text_to_show = spoken_text if spoken_text else "Cannot Understand / Say something..."
st.markdown(f"<div class='thai-speech-output'>{text_to_show}</div>", unsafe_allow_html=True)

# Orange Translate Button
if centered_button("TRANSLATE", key="btn_translate", type="primary"):
    st.session_state.translated = True

if st.session_state.get('translated') and spoken_text:
    st.info("Translation module triggered.")
