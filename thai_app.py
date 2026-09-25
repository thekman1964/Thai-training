import streamlit as st
import csv
import io
import time
import json
import os

st.set_page_config(layout="centered", page_title="Thai Practice")

# Local storage file for saved user entries
LOCAL_DB_FILE = "my_saved_phrases.csv"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.5rem !important;}
    </style>
""", unsafe_allow_html=True)

def load_phrases():
    last_updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    cleaned = []
    
    # Load user saved phrases first if they exist
    if os.path.exists(LOCAL_DB_FILE):
        try:
            with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    thai = str(row.get("Thai", "")).strip()
                    english = str(row.get("English", "")).strip()
                    category = str(row.get("Category", "USER ADDED")).strip().upper()
                    if thai and english:
                        cleaned.append({"thai": thai, "english": english, "category": category})
        except Exception:
            pass

    # Default starter phrases
    defaults = [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
        {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"}
    ]
    
    for d in defaults:
        if not any(p["thai"] == d["thai"] for p in cleaned):
            cleaned.append(d)

    return cleaned, last_updated

PHRASES_DB, LAST_UPDATED = load_phrases()
UNIQUE_CATEGORIES = sorted(list(set(p['category'] for p in PHRASES_DB)))
json_data = json.dumps(PHRASES_DB)
json_cats = json.dumps(UNIQUE_CATEGORIES)

# Handle save action from Python backend
if "save_status" not in st.session_state:
    st.session_state.save_status = None

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
        .btn-save {{ background-color: #8B5CF6; }}
        
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
                
                // Pass back to Streamlit container context
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue', 
                    value: {{thai: text, english: translation}}
                }}, '*');
                
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

component_result = st.components.v1.html(html_code, height=520, scrolling=True)

# Native Python Save Section
st.markdown("---")
st.subheader("💾 Save Translated Phrase")

captured_thai = ""
captured_eng = ""
if isinstance(component_result, dict):
    captured_thai = component_result.get("thai", "")
    captured_eng = component_result.get("english", "")

with st.form("save_form"):
    thai_input = st.text_input("Thai Text", value=captured_thai, placeholder="Spoken Thai text appears here...")
    eng_input = st.text_input("English Translation", value=captured_eng, placeholder="English translation...")
    submitted = st.form_submit_button("➕ SAVE ENTRY", type="primary", use_container_width=True)

    if submitted:
        if not thai_input or thai_input == "Spoken Thai text...":
            st.error("Please provide valid Thai text to save.")
        else:
            try:
                file_exists = os.path.exists(LOCAL_DB_FILE)
                with open(LOCAL_DB_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Thai", "English", "Category"])
                    writer.writerow([thai_input, eng_input if eng_input else "Translated", "USER ADDED"])
                st.success(f"✓ Saved successfully: {thai_input} ({eng_input})")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Save error: {e}")

# Option to download your saved phrases anytime
if os.path.exists(LOCAL_DB_FILE):
    with open(LOCAL_DB_FILE, "rb") as f:
        st.download_button(
            label="📥 Download All Saved Phrases (CSV)",
            data=f,
            file_name="my_saved_thai_phrases.csv",
            mime="text/csv",
            use_container_width=True
        )
