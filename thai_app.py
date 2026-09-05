import streamlit as st
from gtts import gTTS
import io
import base64
import random
import time
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- Mobile Compact CSS Styling (Single-Screen Fit) ---
st.markdown("""
    <style>
    /* Hide top Streamlit header bar, main menu, and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stHeader"] {display: none;}

    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Drastically compact padding to prevent scrolling */
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Target all Streamlit buttons for compact sizing */
    div.stButton > button {
        font-size: 14px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        padding: 5px 0px !important;
        white-space: nowrap !important;
        margin-top: 2px !important;
        margin-bottom: 2px !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* FORCE HORIZONTAL ROW ON MOBILE */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0px !important;
        min-width: 0 !important;
    }

    hr {
        margin: 6px 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to play audio dynamically
def play_thai_audio(text):
    tts = gTTS(text=text, lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64_audio = base64.b64encode(fp.getvalue()).decode()
    
    audio_key = int(time.time() * 1000)
    audio_html = f"""
    <audio id="audio_{audio_key}" autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    <script>
        var audio = document.getElementById('audio_{audio_key}');
        if(audio) {{
            audio.currentTime = 0;
            audio.play();
        }}
    </script>
    """
    components.html(audio_html, height=0)

# Fetch phrases from Google Sheet with static fallback
@st.cache_data(ttl=600)
def load_phrases():
    sheet_id = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url)
        if "Thai" in df.columns and "English" in df.columns:
            phrases = df[['Thai', 'English']].dropna().to_dict('records')
            return [{"thai": str(p['Thai']).strip(), "english": str(p['English']).strip()} for p in phrases if str(p['Thai']).strip()]
    except Exception:
        pass
    return [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
        {"thai": "ขอโทษครับ", "english": "Excuse me."}
    ]

PHRASES_DB = load_phrases()
total = len(PHRASES_DB)

# Initialize Session State
if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False
if "auto_play" not in st.session_state:
    st.session_state.auto_play = False

current_phrase = PHRASES_DB[st.session_state.phrase_index]

# 0. Waving Thailand Flag Header Image
st.markdown(
    """
    <div style="text-align: center; margin-top: 2px; margin-bottom: 2px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Flag_of_Thailand.svg" 
             alt="Thailand Flag" 
             style="width: 55px; height: 36px; display: inline-block; border-radius: 3px; box-shadow: 0px 2px 4px rgba(0,0,0,0.2);">
    </div>
    """,
    unsafe_allow_html=True
)

# 1. Main Title & Phrase Display
st.markdown("<h4 style='text-align: center; color: #000000; margin: 0px;'>Thai Listening and Reading</h4>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; font-size: 32px; color: #000000; margin: 2px 0;'>{current_phrase['thai']}</h2>", unsafe_allow_html=True)

# 2. English Hint Display
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #0066CC; font-size: 16px; font-weight: bold; margin-bottom: 4px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #777777; font-size: 13px; margin-bottom: 4px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 3. Reveal Button
_, col_rev, _ = st.columns([1, 4, 1])
with col_rev:
    if st.button("👁 Reveal", key="btn_reveal", type="secondary", use_container_width=True):
        st.session_state.reveal = not st.session_state.reveal

# 4. Play Phrase Button
_, col_play, _ = st.columns([1, 4, 1])
with col_play:
    if st.button("▶ Play Phrase", key="btn_play", type="primary", use_container_width=True):
        play_thai_audio(current_phrase["thai"])

# Trigger speech audio immediately if requested by Navigation
if st.session_state.auto_play:
    play_thai_audio(current_phrase["thai"])
    st.session_state.auto_play = False

# 5. Navigation Buttons (Each speaks phrase on press)
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("⬅ Prev", key="btn_prev", type="secondary", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total
        st.session_state.reveal = False
        st.session_state.auto_play = True
        st.rerun()

with nav_col2:
    if st.button("🔀 Rand", key="btn_rand", type="secondary", use_container_width=True):
        st.session_state.phrase_index = random.randint(0, total - 1)
        st.session_state.reveal = False
        st.session_state.auto_play = True
        st.rerun()

with nav_col3:
    if st.button("➡ Next", key="btn_next", type="secondary", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total
        st.session_state.reveal = False
        st.session_state.auto_play = True
        st.rerun()

st.divider()

# 6. Integrated Speech-to-Text with Real-time English Translation Output Field
st_speech_html = """
<div style="text-align: center; font-family: sans-serif;">
    <!-- Spoken Thai Output -->
    <div id="output" style="color: #FF6600; font-size: 24px; font-weight: bold; min-height: 32px; margin-bottom: 2px;">
        Spoken Thai text...
    </div>
    
    <!-- English Translation Output (Field located above TRANSLATE button) -->
    <div id="translation" style="color: #0066CC; font-size: 18px; font-weight: bold; min-height: 26px; margin-bottom: 6px;">
        English translation...
    </div>
    
    <button id="stt-btn" style="
        background-color: #FF6600;
        color: white;
        font-size: 15px;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 8px 0px;
        width: 70%;
        max-width: 260px;
        cursor: pointer;
    ">🎙 TRANSLATE</button>
</div>

<script>
    const btn = document.getElementById('stt-btn');
    const output = document.getElementById('output');
    const translation = document.getElementById('translation');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    async function translateText(text) {
        try {
            translation.innerText = "Translating...";
            const res = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=th|en`);
            const data = await res.json();
            if(data && data.responseData && data.responseData.translatedText) {
                translation.innerText = data.responseData.translatedText;
            } else {
                translation.innerText = "Translation unavailable";
            }
        } catch(e) {
            translation.innerText = "Translation error";
        }
    }

    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'th-TH';
        recognition.interimResults = false;

        btn.onclick = () => {
            try {
                recognition.start();
                btn.innerText = "⏹ Listening...";
                btn.style.backgroundColor = "#CC0000";
            } catch(e) {
                recognition.stop();
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            output.innerText = transcript;
            btn.innerText = "🎙 TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
            
            // Translate recognized Thai into English instantly
            translateText(transcript);
        };

        recognition.onerror = () => {
            btn.innerText = "🎙 TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
        };

        recognition.onend = () => {
            btn.innerText = "🎙 TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
        };
    } else {
        output.innerText = "Speech Recognition not supported in browser";
    }
</script>
"""

components.html(st_speech_html, height=140)
