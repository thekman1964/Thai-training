import streamlit as st
import csv
import urllib.request
import io
import time
import json

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- PASTE YOUR GOOGLE APPS SCRIPT WEB APP URL HERE ---
WEBHOOK_URL = "YOUR_GOOGLE_APPS_SCRIPT_URL_HERE"

# Hide Streamlit Chrome UI
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .stApp {background-color: #FFFFFF !important;}
    .block-container {padding: 0.5rem !important;}
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATASET WITHOUT PANDAS ---
@st.cache_data(ttl=600)
def load_phrases():
    sheet_id = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
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

# --- COMPLETE SINGLE-COMPONENT UI ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ margin: 0; padding: 10px; background-color: #ffffff; text-align: center; }}
        
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
        .filter-btn-pill:hover {{ background-color: #E2E8F0; }}
        
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
        
        .nav-grid {{
            display: flex;
            gap: 6px;
            margin-bottom: 12px;
        }}
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

        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        .modal-content {{
            background-color: #ffffff;
            width: 90%;
            max-width: 360px;
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            max-height: 80vh;
            display: flex;
            flex-direction: column;
        }}
        .modal-header {{
            font-size: 16px;
            font-weight: bold;
            color: #1E293B;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .cat-list {{
            overflow-y: auto;
            flex-grow: 1;
            margin-bottom: 14px;
            padding-right: 4px;
        }}
        .cat-item {{
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #F1F5F9;
            font-size: 14px;
            color: #334155;
            cursor: pointer;
        }}
        .cat-item input {{
            margin-right: 10px;
            width: 18px;
            height: 18px;
            accent-color: #0066CC;
        }}
        .modal-actions {{
            display: flex;
            gap: 8px;
        }}
        .modal-actions button {{
            flex: 1;
            height: 38px;
            font-size: 13px;
        }}
    </style>
</head>
<body>

    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Flag_of_Thailand.svg" class="flag" alt="Thai Flag">
    <div class="title">Thai Listening and Reading</div>
    
    <button class="filter-btn-pill" onclick="openModal()">
        ⚙️ Filter: <span id="pillCatLabel">ALL</span>
    </button>
    
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
    <button id="saveBtn" class="btn btn-save" onclick="saveToSpreadsheet()">➕ SAVE TO SPREADSHEET</button>

    <div class="meta-info">
        <div><b>Available Records:</b> <span id="recordCount">{len(PHRASES_DB)}</span></div>
        <div><b>Spreadsheet Last Updated:</b> {LAST_UPDATED}</div>
    </div>

    <div id="filterModal" class="modal-overlay">
        <div class="modal-content">
            <div class="modal-header">
                <span>Select Categories</span>
                <span style="cursor:pointer; font-size: 18px;" onclick="closeModal()">✕</span>
            </div>
            <div class="cat-list" id="categoryContainer"></div>
            <div class="modal-actions">
                <button class="btn btn-dark" onclick="selectAllCategories(true)">All</button>
                <button class="btn btn-dark" onclick="selectAllCategories(false)">Clear</button>
                <button class="btn btn-blue" onclick="applyFilters()">Apply</button>
            </div>
        </div>
    </div>

    <script>
        const fullDb = {json_data};
        const allCategories = {json_cats};
        const webhookUrl = "{WEBHOOK_URL}";
        
        let activeDb = [...fullDb];
        let selectedCategories = new Set(allCategories);
        let currentIndex = 0;
        let isRevealed = false;

        function renderCategoryModal() {{
            const container = document.getElementById('categoryContainer');
            container.innerHTML = '';
            
            allCategories.forEach(cat => {{
                const item = document.createElement('label');
                item.className = 'cat-item';
                const isChecked = selectedCategories.has(cat) ? 'checked' : '';
                item.innerHTML = `<input type="checkbox" value="${{cat}}" ${{isChecked}} onchange="toggleCategory('${{cat}}')"> ${{cat}}`;
                container.appendChild(item);
            }});
        }}

        function toggleCategory(cat) {{
            if (selectedCategories.has(cat)) {{
                selectedCategories.delete(cat);
            }} else {{
                selectedCategories.add(cat);
            }}
        }}

        function selectAllCategories(status) {{
            if (status) {{
                selectedCategories = new Set(allCategories);
            }} else {{
                selectedCategories.clear();
            }}
            renderCategoryModal();
        }}

        function openModal() {{
            renderCategoryModal();
            document.getElementById('filterModal').style.display = 'flex';
        }}

        function closeModal() {{
            document.getElementById('filterModal').style.display = 'none';
        }}

        function applyFilters() {{
            if (selectedCategories.size === 0) {{
                alert("Please select at least one category.");
                return;
            }}
            
            activeDb = fullDb.filter(item => selectedCategories.has(item.category));
            
            if (selectedCategories.size === allCategories.length) {{
                document.getElementById('pillCatLabel').innerText = "ALL";
            }} else {{
                document.getElementById('pillCatLabel').innerText = `${{selectedCategories.size}} Selected`;
            }}
            
            document.getElementById('recordCount').innerText = `${{activeDb.length}} (Filtered)`;
            
            currentIndex = 0;
            isRevealed = false;
            closeModal();
            updateCard();
        }}

        function updateCard() {{
            if (activeDb.length === 0) {{
                document.getElementById('thaiDisplay').innerText = "No Records";
                document.getElementById('englishDisplay').innerText = "Select categories in filter";
                return;
            }}
            
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
            if (activeDb.length === 0) return;
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
            if (activeDb.length === 0) return;
            currentIndex = (currentIndex + 1) % activeDb.length;
            isRevealed = false;
            updateCard();
            playCurrentAudio();
        }}

        function prevPhrase() {{
            if (activeDb.length === 0) return;
            currentIndex = (currentIndex - 1 + activeDb.length) % activeDb.length;
            isRevealed = false;
            updateCard();
            playCurrentAudio();
        }}

        function randomPhrase() {{
            if (activeDb.length === 0) return;
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
            }} catch (e) {{
                console.error("Translation API error:", e);
            }}
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

        async function saveToSpreadsheet() {{
            const thaiText = document.getElementById('speechOutput').innerText;
            const englishText = document.getElementById('speechTrans').innerText;
            const saveBtn = document.getElementById('saveBtn');

            if (!thaiText || thaiText === "Spoken Thai text..." || englishText === "Translation unavailable" || englishText === "English translation...") {{
                alert("Please record and translate a valid phrase first.");
                return;
            }}

            if (!webhookUrl || webhookUrl === "YOUR_GOOGLE_APPS_SCRIPT_URL_HERE") {{
                alert("Please replace YOUR_GOOGLE_APPS_SCRIPT_URL_HERE in line 11 of thai_app.py with your Web App URL.");
                return;
            }}

            saveBtn.innerText = "SAVING...";
            saveBtn.disabled = true;

            try {{
                await fetch(webhookUrl, {{
                    method: 'POST',
                    mode: 'no-cors',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        thai: thaiText,
                        english: englishText,
                        category: "USER ADDED"
                    }})
                }});

                saveBtn.innerText = "✓ SAVED TO SPREADSHEET";
                saveBtn.style.backgroundColor = "#10B981";

                setTimeout(() => {{
                    saveBtn.innerText = "➕ SAVE TO SPREADSHEET";
                    saveBtn.style.backgroundColor = "#8B5CF6";
                    saveBtn.disabled = false;
                }}, 2500);

            }} catch (e) {{
                alert("Failed to save entry: " + e.message);
                saveBtn.innerText = "➕ SAVE TO SPREADSHEET";
                saveBtn.disabled = false;
            }}
        }}

        updateCard();
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=730, scrolling=True)
