import streamlit as st
from gtts import gTTS
import io
import base64
import random
import time
import requests
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- CSS OVERRIDES FOR NATIVE BUTTON COLORS ---
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

    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Force horizontal blocks to auto-distribute evenly */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
        gap: 6px !important;
    }

    [data-testid="stColumn"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }

    /* Universal Base Styling for Native Buttons */
    div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 40px !important;
        min-height: 40px !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        border-radius: 6px !important;
        padding: 0px !important;
        line-height: 32px !important;
        white-space: nowrap !important;
        margin: 2px 0px !important;
        box-sizing: border-box !important;
        cursor: pointer !important;
    }

    /* Target specific buttons via key-based structural position */

    /* Row 1: REVEAL - Blue */
    [data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stButton"] > button {
        background-color: #0066CC !important;
        color: #FFFFFF !important;
        border: 4px solid #0066CC !important;
    }

    /* Row 2: PHRASE - Orange */
    [data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stButton"] > button {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        border: 4px solid #FF6600 !important;
    }

    /* Row 3 Column 1: BACK - Dark Gray */
    [data-testid="stHorizontalBlock"]:nth-of-type(3) [data-testid="stColumn"]:nth-of-type(1) div[data-testid="stButton"] > button {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: 4px solid #000000 !important;
    }

    /* Row 3 Column 2: RANDOM - Bright Green */
    [data-testid="stHorizontalBlock"]:nth-of-type(3) [data-testid="stColumn"]:nth-of-type(2) div[data-testid="stButton"] > button {
        background-color: #28A745 !important;
        color: #FFFFFF !important;
        border: 4px solid #28A745 !important;
    }

    /* Row 3 Column 3: NEXT - Dark Gray */
    [data-testid="stHorizontalBlock"]:nth-of-type(3) [data-testid="stColumn"]:nth-of-type(3) div[data-testid="stButton"] > button {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: 4px solid #000000 !important;
    }

    /* Force button label text color to White */
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span {
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }

    hr {
        margin: 6px 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Audio Player Helper
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

# Fetch phrases from Google Sheet along with last updated timestamp
@st.cache_data(ttl=600)
def load_phrases_with_meta():
    sheet_id = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    last_updated = "Unknown"
    
    try:
        head_res = requests.head(url)
        if "Last-Modified" in head_res.headers:
            last_updated = head_res.headers["Last-Modified"]
        else:
            last_updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    except Exception:
        last_updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())

    try:
        df = pd.read_csv(url)
        if "Thai" in df.columns and "English" in df.columns:
            phrases = df[['Thai', 'English']].dropna().to_dict('records')
            cleaned = [{"thai": str(p['Thai']).strip(), "english": str(p['English']).strip()} for p in phrases if str(p['Thai']).strip()]
            return cleaned, last_updated
    except Exception:
        pass

    fallback = [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
        {"thai": "ขอโทษครับ", "english": "Excuse me."}
    ]
    return fallback, last_updated

PHRASES_DB, SHEET_LAST_UPDATED = load_phrases_with_meta()
total = len(PHRASES_DB)

# Initialize Session State
if "phrase_index" not in st.session_state:
    st.session_state.phrase_index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False
if "auto_play" not in st.session_state:
    st.session_state.auto_play = False

current_phrase = PHRASES_DB[st.session_state.phrase_index]

# Header Flag Image
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

# Title & Main Thai Phrase Display
st.markdown("<h4 style='text-align: center; color: #000000; margin: 0px;'>Thai Listening and Reading</h4>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; font-size: 32px; color: #000000; margin: 2px 0;'>{current_phrase['thai']}</h2>", unsafe_allow_html=True)

# English Translation Display
if st.session_state.reveal:
    st.markdown(f"<p style='text-align: center; color: #0066CC; font-size: 20px; font-weight: bold; margin-bottom: 4px;'>{current_phrase['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; color: #777777; font-size: 13px; margin-bottom: 4px;'>Click \"REVEAL\" to view English translation</p>", unsafe_allow_html=True)

# Trigger auto audio play if needed
if st.session_state.auto_play:
    play_thai_audio(current_phrase["thai"])
    st.session_state.auto_play = False

# --- NATIVE STREAMLIT BUTTONS ---

# Row 1: REVEAL
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("REVEAL", key="btn_reveal", use_container_width=True):
        st.session_state.reveal = not st.session_state.reveal
        st.rerun()

# Row 2: PHRASE
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("PHRASE", key="btn_phrase", use_container_width=True):
        play_thai_audio(current_phrase["thai"])

# Row 3: BACK, RANDOM, NEXT
col_back, col_rand, col_next = st.columns([1, 1, 1])
with col_back:
    if st.button("BACK", key="btn_back", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index - 1) % total
        st.session_state.reveal = False
        st.session_state.auto_play = True
        st.rerun()

with col_rand:
    if st.button("RANDOM", key="btn_rand", use_container_width=True):
        st.session_state.phrase_index = random.randint(0, total - 1)
        st.session_state.reveal = False
        st.session_state.auto_play = True
        st.rerun()

with col_next:
    if st.button("NEXT", key="btn_next", use_container_width=True):
        st.session_state.phrase_index = (st.session_state.phrase_index + 1) % total
        st.session_state.reveal = False
        st.session_state.auto_play = True
        st.rerun()

st.divider()

# Speech Recognition & Translation Section
st_speech_html = f"""
<div style="text-align: center; font-family: sans-serif;">
    <div id="output" style="color: #FF6600; font-size: 32px; font-weight: bold; min-height: 40px; margin-bottom: 2px;">
        Spoken Thai text...
    </div>
    
    <div id="translation" style="color: #0066CC; font-size: 20px; font-weight: bold; min-height: 28px; margin-bottom: 6px;">
        English translation...
    </div>
    
    <button id="stt-btn" style="
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        border: 4px solid #FF6600 !important;
        border-radius: 6px !important;
        height: 40px !important;
        line-height: 32px !important;
        padding: 0px !important;
        width: 100% !important;
        cursor: pointer !important;
        margin-bottom: 12px !important;
        box-sizing: border-box !important;
    ">TRANSLATE</button>
    <br>

    <button id="speak-btn" style="
        background-color: #FFFFFF !important;
        color: #FF6600 !important;
        border: 4px solid #FF6600 !important;
        font-size: 13px !important;
        font-weight: 900 !important;
        border-radius: 6px !important;
        height: 40px !important;
        line-height: 32px !important;
        padding: 0px !important;
        width: 100% !important;
        cursor: pointer !important;
        box-sizing: border-box !important;
    ">HEAR SPOKEN THAI TEXT</button>

    <div style="margin-top: 10px; font-size: 12px; color: #555555; line-height: 1.4;">
        <div><b>Available Records:</b> {total}</div>
        <div><b>Spreadsheet Last Updated:</b> {SHEET_LAST_UPDATED}</div>
    </div>
</div>

<script>
    const btn = document.getElementById('stt-btn');
    const speakBtn = document.getElementById('speak-btn');
    const output = document.getElementById('output');
    const translation = document.getElementById('translation');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    async function translateText(text) {{
        try {{
            translation.innerText = "Translating...";
            const res = await fetch(`https://api.mymemory.translated.net/get?q=${{encodeURIComponent(text)}}&langpair=th|en`);
            const data = await res.json();
            if(data && data.responseData && data.responseData.translatedText) {{
                translation.innerText = data.responseData.translatedText;
            }} else {{
                translation.innerText = "Translation unavailable";
            }}
        }} catch(e) {{
            translation.innerText = "Translation error";
        }}
    }}

    speakBtn.onclick = () => {{
        const textToSpeak = output.innerText.trim();
        if (textToSpeak && textToSpeak !== "Spoken Thai text...") {{
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = 'th-TH';
            window.speechSynthesis.speak(utterance);
        }}
    }};

    if (SpeechRecognition) {{
        const recognition = new SpeechRecognition();
        recognition.lang = 'th-TH';
        recognition.interimResults = false;

        btn.onclick = () => {{
            try {{
                recognition.start();
                btn.innerText = "LISTENING...";
                btn.style.backgroundColor = "#CC0000";
            }} catch(e) {{
                recognition.stop();
            }}
        }};

        recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            output.innerText = transcript;
            btn.innerText = "TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
            
            translateText(transcript);
        }};

        recognition.onerror = () => {{
            btn.innerText = "TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
        }};

        recognition.onend = () => {{
            btn.innerText = "TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
        }};
    }} else {{
        output.innerText = "Speech Recognition not supported in browser";
    }}
</script>
"""

components.html(st_speech_html, height=260)
