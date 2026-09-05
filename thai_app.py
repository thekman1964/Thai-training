import streamlit as st
from gtts import gTTS
import io
import base64
import random
import time
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- Custom Mobile CSS Styling ---
st.markdown("""
    <style>
    /* Hide top Streamlit header bar, main menu, and footer (Red Box area) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stHeader"] {display: none;}

    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* Target all Streamlit buttons for clean single-line text and vertical spacing */
    div.stButton > button {
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 8px 0px !important;
        white-space: nowrap !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
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

    /* FORCE HORIZONTAL ROW ON MOBILE: Prevent st.columns from stacking vertically */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        margin-top: 8px !important;
        margin-bottom: 8px !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0px !important;
        min-width: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

def centered_button(label, key, type="secondary"):
    _, col, _ = st.columns([1, 4, 1])
    with col:
        return st.button(label, key=key, type=type, use_container_width=True)

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

# 0. Waving Thailand Flag Header Image
st.markdown(
    """
    <div style="text-align: center; margin-top: 10px; margin-bottom: 10px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Flag_of_Thailand.svg" 
             alt="Thailand Flag" 
             style="width: 80px; height: 53px; display: inline-block; border-radius: 4px; box-shadow: 0px 2px 5px rgba(0,0,0,0.2);">
    </div>
    """,
    unsafe_allow_html=True
)

# 1. Main Title & Display
st.markdown("<h3 style='text-align: center; color: #000000; margin-top: 0px;'>Thai Listening and Reading</h3>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; font-size: 40px; color: #000000; margin: 8px 0;'>{current_phrase['thai']}</h1>", unsafe_allow_html=True)

# 2. English Hint
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #0066CC; font-size: 20px; font-weight: bold; margin-bottom: 12px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #777777; font-size: 15px; margin-bottom: 12px;'>Click \"Reveal\" to view English translation</p>", unsafe_allow_html=True)

# 3. Reveal Button
if centered_button("👁 Reveal", "btn_reveal", type="secondary"):
    st.session_state.reveal = not st.session_state.reveal

# 4. Play Phrase Button (Fixed for repeated clicks using unique timestamp injection)
if centered_button("▶ Play Phrase", "btn_play", type="primary"):
    tts = gTTS(text=current_phrase["thai"], lang='th')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64_audio = base64.b64encode(fp.getvalue()).decode()
    
    # Generate unique timestamp key to force immediate playback on every press
    audio_key = int(time.time() * 1000)
    audio_html = f"""
    <audio id="audio_{audio_key}" autoplay>
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

# 5. Navigation Buttons
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("⬅ Prev", key="btn_prev", type="secondary", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total
        st.session_state.reveal = False
        st.rerun()

with nav_col2:
    if st.button("🔀 Rand", key="btn_rand", type="secondary", use_container_width=True):
        st.session_state.phrase_index = random.randint(0, total - 1)
        st.session_state.reveal = False
        st.rerun()

with nav_col3:
    if st.button("➡ Next", key="btn_next", type="secondary", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total
        st.session_state.reveal = False
        st.rerun()

st.divider()

# 6. Browser Native Speech-to-Text Component (Orange Display + Button)
st_speech_html = """
<div style="text-align: center; font-family: sans-serif;">
    <div id="output" style="color: #FF6600; font-size: 30px; font-weight: bold; min-height: 45px; margin-bottom: 12px;">
        Spoken Thai text will display here...
    </div>
    <button id="stt-btn" style="
        background-color: #FF6600;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 0px;
        width: 70%;
        max-width: 280px;
        cursor: pointer;
    ">🎙 TRANSLATE</button>
</div>

<script>
    const btn = document.getElementById('stt-btn');
    const output = document.getElementById('output');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
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
