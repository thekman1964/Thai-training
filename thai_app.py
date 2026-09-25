import streamlit as st
import csv
import urllib.request
import io
import time
import json
import urllib.parse

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.5rem !important;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_phrases():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    last_updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    
    try:
        req = urllib.request.urlopen(url)
        csv_text = req.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_text))
        
        cleaned = []
        for row in reader:
            thai = str(row.get("Thai", "")).strip()
            english = str(row.get("English", "")).strip()
            category = str(row.get("Category", "GENERAL")).strip().upper()
            
            if thai and english:
                cleaned.append({
                    "thai": thai,
                    "english": english,
                    "category": category if category else "GENERAL"
                })
        if cleaned:
            return cleaned, last_updated
    except Exception:
        pass

    return [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
        {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"}
    ], last_updated

PHRASES_DB, LAST_UPDATED = load_phrases()
UNIQUE_CATEGORIES = sorted(list(set(p['category'] for p in PHRASES_DB)))
json_data = json.dumps(PHRASES_DB)
json_cats = json.dumps(UNIQUE_CATEGORIES)

# Session state to hold recorded/translated text for saving
if "recorded_thai" not in st.session_state:
    st.session_state.recorded_thai = ""
if "recorded_eng" not in st.session_state:
    st.session_state.recorded_eng = ""

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ margin: 0; padding: 10px; background-color: #ffffff; color: #000000; text-align: center; }}
        
        .flag {{ width: 55px; height: 36px; border-radius: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .title {{ font-size: 18px; margin: 6px 0 4px 0; color: #000; font-weight: bold; }}
        
        .filter-btn-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background-color: #F1F5F9;
            border: 1px solid #CBD5E1;
            border-radius: 16px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
            color: #334155;
            cursor: pointer;
            margin-bottom: 4px;
        }}
        
        .thai-text {{ font-size: 32px; font-weight: bold; color: #000; margin: 8px 0; min-height: 48px; }}
        .sub-text {{ font-size: 14px; color: #777; margin-bottom: 15px; min-height: 24px; }}
        .eng-text {{ font-size: 20px; font-weight: bold; color: #0066CC; margin-bottom: 15px; min-height: 24px; }}
        
        .btn {{
            width: 100%;
            height: 46px;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 800;
            color: #ffffff !important;
            cursor: pointer;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }}
        
        .btn-blue {{ background-color: #0066CC; }}
        .btn-orange {{ background-color: #FF6600; }}
        .btn-dark {{ background-color: #1A202C; }}
        .btn-green {{ background-color: #28A745; }}
        
        .nav-grid {{ display: flex; gap: 6px; margin-bottom: 12px; }}
        .nav-grid .btn {{ flex: 1; margin-bottom: 0; }}
        
        hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0; }}

        .spoken-title {{ color: #FF6600; font-size: 28px; font-weight: bold; margin-bottom: 4px; min-height: 38px; }}
        .spoken-trans {{ color: #0066CC; font-size: 18px; font-weight: bold; margin-bottom: 10px; min-height: 26px; }}
        
        .btn-outline {{
            background-color: #FFFFFF !important;
            color: #FF6600 !important;
            border: 2px solid #FF6600 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        
        .meta-info {{ font-size: 12px; color: #555; margin-top: 12px; line-height: 1.4; }}
    </style>
</head>
<body>

    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Flag_of_Thailand.svg" class="flag" alt="Thai Flag">
    <div class="title">Thai Listening and Reading</div>
    
    <div id="thaiDisplay" class="thai-text"></div>
    <div id="englishDisplay" class="sub-text">Click "REVEAL" to view English translation</div>

    <button class="btn btn-blue" onclick="toggleReveal()">REVEAL</button>
    <button class="btn btn-orange" onclick="playCurrentAudio()">PHRASE</button>

    <div class="nav-grid">
        <button class="btn btn-dark" onclick="prevPhrase()">BACK</button>
        <button class="btn btn-green" onclick="randomPhrase()">RANDOM</button>
        <button class="btn btn-dark" onclick="nextPhrase()">NEXT</button>
    </div>

    <hr>

    <div id="speechOutput" class="spoken-title">Spoken Thai text...</div>
    <div id="speechTrans" class="spoken-trans">English translation...</div>

    <button id="sttBtn" class="btn btn-orange" onclick="startRecognition()">TRANSLATE</button>
    <button class="btn btn-outline" onclick="speakRecognizedText()">HEAR SPOKEN THAI TEXT</button>

    <script>
        const fullDb = {json_data};
        let activeDb = [...fullDb];
        let currentIndex = 0;
        let isRevealed = false;

        function updateCard() {{
            if (activeDb.length === 0) return;
            const item = activeDb[currentIndex];
            document.getElementById('thaiDisplay').innerText = item.thai;
            if (isRevealed) {{
                document.getElementById('englishDisplay').innerText = item.english;
                document.getElementById('englishDisplay').className = "eng-text";
            }} else {{
                document.getElementById('englishDisplay').innerText = 'Click "REVEAL" to view English translation';
                document.getElementById('englishDisplay').className = "sub-text";
            }}
        }}

        function toggleReveal() {{
            isRevealed = !isRevealed;
            updateCard();
        }}

        function playCurrentAudio() {{
            if (activeDb.length === 0) return;
            const utterance = new SpeechSynthesisUtterance(activeDb[currentIndex].thai);
            utterance.lang = 'th-TH';
            window.speechSynthesis.speak(utterance);
        }}

        function nextPhrase() {{
            currentIndex = (currentIndex + 1) % activeDb.length;
            isRevealed = false;
            updateCard();
            playCurrentAudio();
        }}

        function prevPhrase() {{
            currentIndex = (currentIndex - 1 + activeDb.length) % activeDb.length;
            isRevealed = false;
            updateCard();
            playCurrentAudio();
        }}

        function randomPhrase() {{
            currentIndex = Math.floor(Math.random() * activeDb.length);
            isRevealed = false;
            updateCard();
            playCurrentAudio();
        }}

        async function translateThaiText(text) {{
            const match = fullDb.find(item => item.thai.trim() === text.trim());
            if (match) return match.english;

            try {{
                const url = `https://api.mymemory.translated.net/get?q=${{encodeURIComponent(text)}}&langpair=th|en`;
                const res = await fetch(url);
                const data = await res.json();
                if (data.responseData && data.responseData.translatedText) {{
                    return data.responseData.translatedText;
                }}
            }} catch (e) {{}}
            return "Translation unavailable";
        }}

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        
        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.lang = 'th-TH';
            
            recognition.onresult = async (event) => {{
                const text = event.results[0][0].transcript;
                document.getElementById('speechOutput').innerText = text;
                document.getElementById('speechTrans').innerText = "Translating...";
                
                const translation = await translateThaiText(text);
                document.getElementById('speechTrans').innerText = translation;
                
                // Securely send data back to Streamlit native context
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {{thai: text, english: translation}}}}, '*');
                
                resetSttBtn();
            }};

            recognition.onerror = () => resetSttBtn();
            recognition.onend = () => resetSttBtn();
        }}

        function startRecognition() {{
            if (recognition) {{
                try {{
                    recognition.start();
                    const btn = document.getElementById('sttBtn');
                    btn.innerText = "LISTENING...";
                    btn.style.backgroundColor = "#CC0000";
                }} catch(e) {{ recognition.stop(); }}
            }} else {{
                alert("Speech recognition is not supported on this browser.");
            }}
        }}

        function resetSttBtn() {{
            const btn = document.getElementById('sttBtn');
            btn.innerText = "TRANSLATE";
            btn.style.backgroundColor = "#FF6600";
        }}

        function speakRecognizedText() {{
            const txt = document.getElementById('speechOutput').innerText;
            if (txt && txt !== "Spoken Thai text...") {{
                const utterance = new SpeechSynthesisUtterance(txt);
                utterance.lang = 'th-TH';
                window.speechSynthesis.speak(utterance);
            }}
        }}

        updateCard();
    </script>
</body>
</html>
"""

# Render mobile UI component
component_result = st.components.v1.html(html_code, height=550, scrolling=True)

# Native Python Save Section (Completely bypasses Apps Script / Webhooks)
st.markdown("---")
st.subheader("💾 Save Translated Phrase to Google Sheet")

# Pull values either from user typing or automatic speech capture
default_thai = component_result.get("thai", "") if isinstance(component_result, dict) else ""
default_eng = component_result.get("english", "") if isinstance(component_result, dict) else ""

input_thai = st.text_input("Thai Text", value=default_thai, placeholder="Speak or type Thai text...")
input_eng = st.text_input("English Translation", value=default_eng, placeholder="Translation...")

if st.button("CONFIRM AND SAVE TO SHEET", type="primary", use_container_width=True):
    if not input_thai:
        st.error("Please provide valid Thai text.")
    else:
        try:
            # Direct server-side append using gspread if credentials exist, 
            # or a clean fallback notification
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            # If service account file is present
            creds_dict = st.secrets.get("gcp_service_account", None)
            
            if creds_dict:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
                sheet.append_row([input_thai, input_eng, "USER ADDED"])
                st.success("✓ Successfully saved directly to Google Sheet!")
            else:
                st.info("To enable direct database writes without Apps Script, add your GCP service account JSON dictionary to Streamlit Secrets under `gcp_service_account`.")
        except Exception as e:
            st.error(f"Save error: {e}")
