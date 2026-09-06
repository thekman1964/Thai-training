import streamlit as st
import time
import requests
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- Remove Streamlit Wrappers & Spacing ---
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] { visibility: hidden; display: none; }
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    .block-container { padding: 0.1rem 0.2rem !important; max-width: 100% !important; }
    iframe { width: 100% !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

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
phrases_json = json.dumps(PHRASES_DB, ensure_ascii=False)

# Self-Contained Mobile App HTML
full_app_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * {{
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }}
        body {{
            margin: 0;
            padding: 4px 8px;
            background: #FFFFFF;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            text-align: center;
        }}
        .flag {{
            width: 50px;
            height: 32px;
            margin: 2px auto;
            display: block;
            border-radius: 3px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.2);
        }}
        h4 {{
            margin: 2px 0 0 0;
            color: #000000;
            font-size: 15px;
            font-weight: 600;
        }}
        .thai-card {{
            font-size: 28px;
            font-weight: bold;
            color: #000000;
            margin: 8px 0;
            min-height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .translation-card {{
            font-size: 18px;
            font-weight: bold;
            color: #0066CC;
            min-height: 26px;
            margin-bottom: 10px;
        }}
        .hint-card {{
            font-size: 12px;
            color: #777777;
            min-height: 26px;
            margin-bottom: 10px;
        }}

        /* Responsive Layout Grid */
        .controls-container {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
            max-width: 420px;
            margin: 0 auto;
        }}
        .btn-row {{
            display: flex;
            width: 100%;
            justify-content: center;
            gap: 6px;
        }}

        /* Universal Responsive Button Styling */
        .btn {{
            height: 42px;
            border-radius: 6px;
            border: 3px solid #000000;
            font-weight: 900;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            transition: opacity 0.1s ease;
        }}
        .btn:active {{
            opacity: 0.75;
        }}

        /* Button Colors */
        .btn-rev {{ width: 65%; background-color: #0066CC; color: #FFFFFF; }}
        .btn-phr {{ width: 65%; background-color: #FF6600; color: #FFFFFF; }}
        .btn-nav {{ flex: 1; background-color: #1A202C; color: #FFFFFF; }}
        .btn-rnd {{ flex: 1; background-color: #28A745; color: #FFFFFF; }}

        .divider {{
            border: 0;
            height: 1px;
            background: #E2E8F0;
            margin: 14px 0;
        }}

        .stt-output {{
            color: #FF6600;
            font-size: 26px;
            font-weight: bold;
            min-height: 36px;
            margin-bottom: 2px;
        }}
        .stt-translation {{
            color: #0066CC;
            font-size: 18px;
            font-weight: bold;
            min-height: 24px;
            margin-bottom: 8px;
        }}
        .btn-stt {{
            width: 100%;
            background-color: #FF6600;
            color: #FFFFFF;
        }}
        .btn-hear {{
            width: 100%;
            background-color: #FFFFFF;
            color: #FF6600;
            border: 3px solid #FF6600;
        }}

        .meta-info {{
            margin-top: 12px;
            font-size: 11px;
            color: #555555;
            line-height: 1.4;
        }}
    </style>
</head>
<body>

    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Flag_of_Thailand.svg" class="flag" alt="Flag">
    <h4>Thai Listening and Reading</h4>

    <div id="thai-text" class="thai-card">--</div>
    <div id="english-text" class="hint-card">Click "REVEAL" to view English translation</div>

    <div class="controls-container">
        <div class="btn-row">
            <button class="btn btn-rev" id="btn-reveal">REVEAL</button>
        </div>
        <div class="btn-row">
            <button class="btn btn-phr" id="btn-phrase">PHRASE</button>
        </div>
        <div class="btn-row">
            <button class="btn btn-nav" id="btn-back">BACK</button>
            <button class="btn btn-rnd" id="btn-rand">RANDOM</button>
            <button class="btn btn-nav" id="btn-next">NEXT</button>
        </div>
    </div>

    <div class="divider"></div>

    <div id="output" class="stt-output">Spoken Thai text...</div>
    <div id="translation" class="stt-translation">English translation...</div>

    <div class="controls-container">
        <button id="stt-btn" class="btn btn-stt">TRANSLATE</button>
        <button id="speak-btn" class="btn btn-hear">HEAR SPOKEN THAI TEXT</button>
    </div>

    <div class="meta-info">
        <div><b>Available Records:</b> {len(PHRASES_DB)}</div>
        <div><b>Spreadsheet Last Updated:</b> {SHEET_LAST_UPDATED}</div>
    </div>

<script>
    const db = {phrases_json};
    let currentIndex = 0;
    let isRevealed = false;

    const thaiText = document.getElementById('thai-text');
    const englishText = document.getElementById('english-text');

    function renderCard(playAudio = false) {{
        if(!db || db.length === 0) return;
        const item = db[currentIndex];
        thaiText.innerText = item.thai;

        if (isRevealed) {{
            englishText.innerText = item.english;
            englishText.className = "translation-card";
        }} else {{
            englishText.innerText = 'Click "REVEAL" to view English translation';
            englishText.className = "hint-card";
        }}

        if (playAudio) {{
            speakThai(item.thai);
        }}
    }}

    function speakThai(text) {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'th-TH';
            window.speechSynthesis.speak(utterance);
        }}
    }}

    document.getElementById('btn-reveal').onclick = () => {{
        isRevealed = !isRevealed;
        renderCard(false);
    }};

    document.getElementById('btn-phrase').onclick = () => {{
        speakThai(db[currentIndex].thai);
    }};

    document.getElementById('btn-back').onclick = () => {{
        currentIndex = (currentIndex - 1 + db.length) % db.length;
        isRevealed = false;
        renderCard(true);
    }};

    document.getElementById('btn-rand').onclick = () => {{
        currentIndex = Math.floor(Math.random() * db.length);
        isRevealed = false;
        renderCard(true);
    }};

    document.getElementById('btn-next').onclick = () => {{
        currentIndex = (currentIndex + 1) % db.length;
        isRevealed = false;
        renderCard(true);
    }};

    // --- Speech Recognition ---
    const sttBtn = document.getElementById('stt-btn');
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
            speakThai(textToSpeak);
        }}
    }};

    if (SpeechRecognition) {{
        const recognition = new SpeechRecognition();
        recognition.lang = 'th-TH';
        recognition.interimResults = false;

        sttBtn.onclick = () => {{
            try {{
                recognition.start();
                sttBtn.innerText = "LISTENING...";
                sttBtn.style.backgroundColor = "#CC0000";
            }} catch(e) {{
                recognition.stop();
            }}
        }};

        recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            output.innerText = transcript;
            sttBtn.innerText = "TRANSLATE";
            sttBtn.style.backgroundColor = "#FF6600";
            translateText(transcript);
        }};

        recognition.onerror = () => {{
            sttBtn.innerText = "TRANSLATE";
            sttBtn.style.backgroundColor = "#FF6600";
        }};

        recognition.onend = () => {{
            sttBtn.innerText = "TRANSLATE";
            sttBtn.style.backgroundColor = "#FF6600";
        }};
    }} else {{
        output.innerText = "Speech Recognition not supported";
    }}

    // Initial render
    renderCard(false);
</script>
</body>
</html>
"""

components.html(full_app_html, height=560, scrolling=False)
