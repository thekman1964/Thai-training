import streamlit as st
from gtts import gTTS
import io
import base64
import time
import requests
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- Page Setup ---
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] { visibility: hidden; display: none; }
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    .block-container { padding: 0.2rem 0.5rem 0rem 0.5rem !important; }
    hr { margin: 10px 0px !important; }
    </style>
""", unsafe_allow_html=True)

# Helper function to play audio
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
        if(audio) {{ audio.currentTime = 0; audio.play(); }}
    </script>
    """
    components.html(audio_html, height=0)

# Fetch phrases from Google Sheet
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

# Read query params for state management
query_params = st.query_params
current_idx = int(query_params.get("idx", 0)) % total
is_revealed = query_params.get("rev", "0") == "1"
should_play = query_params.get("play", "0") == "1"

current_phrase = PHRASES_DB[current_idx]

# Play audio if requested via query param
if should_play:
    play_thai_audio(current_phrase["thai"])

# Pre-render English display string to avoid complex quote nesting inside the f-string
if is_revealed:
    english_display = f'<div class="english-text">{current_phrase["english"]}</div>'
else:
    english_display = '<div class="hint-text">Click "REVEAL" to view English translation</div>'

prev_idx = (current_idx - 1) % total
next_idx = (current_idx + 1) % total
rev_toggle = 0 if is_revealed else 1

top_app_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #FFFFFF;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            text-align: center;
        }}
        .flag {{
            width: 55px;
            height: 36px;
            margin-top: 2px;
            margin-bottom: 2px;
            border-radius: 3px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.2);
        }}
        h4 {{
            margin: 0;
            color: #000000;
            font-weight: 600;
        }}
        h2 {{
            font-size: 32px;
            color: #000000;
            margin: 6px 0;
        }}
        .english-text {{
            color: #0066CC;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 12px;
        }}
        .hint-text {{
            color: #777777;
            font-size: 13px;
            margin-bottom: 12px;
        }}
        .btn-stack {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            width: 100%;
        }}
        .row-center {{
            display: flex;
            justify-content: center;
            width: 100%;
        }}
        .row-three {{
            display: flex;
            justify-content: center;
            gap: 6px;
            width: 100%;
        }}
        .btn {{
            height: 42px;
            font-weight: 900;
            font-size: 13px;
            border-radius: 6px;
            border: 3px solid #000000;
            box-sizing: border-box;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
        }}
        .btn-rev {{ width: 50%; background-color: #0066CC; color: #FFFFFF; }}
        .btn-phr {{ width: 50%; background-color: #FF6600; color: #FFFFFF; }}
        .btn-nav {{ flex: 1; background-color: #1A202C; color: #FFFFFF; }}
        .btn-rnd {{ flex: 1; background-color: #28A745; color: #FFFFFF; }}
    </style>
</head>
<body>
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Flag_of_Thailand.svg" class="flag" alt="Flag">
    <h4>Thai Listening and Reading</h4>
    <h2>{current_phrase['thai']}</h2>

    {english_display}

    <div class="btn-stack">
        <div class="row-center">
            <button class="btn btn-rev" id="btn-rev">REVEAL</button>
        </div>
        <div class="row-center">
            <button class="btn btn-phr" id="btn-phr">PHRASE</button>
        </div>
        <div class="row-three">
            <button class="btn btn-nav" id="btn-back">BACK</button>
            <button class="btn btn-rnd" id="btn-rand">RANDOM</button>
            <button class="btn btn-nav" id="btn-next">NEXT</button>
        </div>
    </div>

    <script>
        function nav(params) {{
            window.parent.location.search = "?" + params;
        }}
        document.getElementById('btn-rev').onclick = function() {{ nav("idx={current_idx}&rev={rev_toggle}&play=0"); }};
        document.getElementById('btn-phr').onclick = function() {{ nav("idx={current_idx}&rev={1 if is_revealed else 0}&play=1"); }};
        document.getElementById('btn-back').onclick = function() {{ nav("idx={prev_idx}&rev=0&play=1"); }};
        document.getElementById('btn-rand').onclick = function() {{ nav("idx=" + Math.floor(Math.random() * {total}) + "&rev=0&play=1"); }};
        document.getElementById('btn-next').onclick = function() {{ nav("idx={next_idx}&rev=0&play=1"); }};
    </script>
</body>
</html>
"""

components.html(top_app_html, height=280)

st.divider()

# Speech Recognition Section
st_speech_html = f"""
<div style="text-align: center; font-family: sans-serif;">
    <div id="output" style="color: #FF6600; font-size: 32px; font-weight: bold; min-height: 40px; margin-bottom: 2px;">
        Spoken Thai text...
    </div>
    
    <div id="translation" style="color: #0066CC; font-size: 20px; font-weight: bold; min-height: 28px; margin-bottom: 8px;">
        English translation...
    </div>
    
    <button id="stt-btn" style="
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        border: 3px solid #000000 !important;
        border-radius: 6px !important;
        height: 42px !important;
        line-height: 36px !important;
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
        border: 3px solid #FF6600 !important;
        font-size: 13px !important;
        font-weight: 900 !important;
        border-radius: 6px !important;
        height: 42px !important;
        line-height: 36px !important;
        padding: 0px !important;
        width: 100% !important;
        cursor: pointer !important;
        box-sizing: border-box !important;
    ">HEAR SPOKEN THAI TEXT</button>

    <div style="margin-top: 12px; font-size: 12px; color: #555555; line-height: 1.4;">
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
