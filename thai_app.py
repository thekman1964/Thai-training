import streamlit as st
import csv
import urllib.request
import io
import time
import json
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# Hide Streamlit Chrome UI & Keep Layout Clean
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .stApp {background-color: #FFFFFF !important;}
    .block-container {padding: 0.2rem !important; max-width: 420px !important;}
    iframe {width: 100% !important; border: none !important;}
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

# Extract unique categories dynamically
UNIQUE_CATEGORIES = sorted(list(set(p['category'] for p in PHRASES_DB)))
json_data = json.dumps(PHRASES_DB)
json_cats = json.dumps(UNIQUE_CATEGORIES)

# --- COMPLETE SINGLE-SCREEN MOBILE UI (TOUCH-FRIENDLY PADDING) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ margin: 0; padding: 6px; background-color: #ffffff; text-align: center; }}
        
        .flag {{ width: 50px; height: 34px; border-radius: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .title {{ font-size: 17px; margin: 6px 0 4px 0; color: #000; font-weight: bold; }}
        
        .filter-btn-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background-color: #F1F5F9;
            border: 1px solid #CBD5E1;
            border-radius: 16px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
            color: #334155;
            cursor: pointer;
            margin-bottom: 6px;
        }}
        .filter-btn-pill:hover {{ background-color: #E2E8F0; }}
        
        .thai-text {{ font-size: 30px; font-weight: bold; color: #000; margin: 6px 0; min-height: 44px; }}
        .sub-text {{ font-size: 14px; color: #777; margin-bottom: 12px; min-height: 22px; }}
        .eng-text {{ font-size: 20px; font-weight: bold; color: #0066CC; margin-bottom: 12px; min-height: 22px; }}
        
        /* Larger, more touch-friendly buttons with generous spacing */
        .btn {{
            width: 100%;
            height: 48px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 800;
            color: #ffffff !important;
            cursor: pointer;
            margin-bottom: 12px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        }}
        
        .btn-blue {{ background-color: #0066CC; }}
        .btn-orange {{ background-color: #FF6600; }}
        .btn-dark {{ background-color: #1A202C; }}
        .btn-green {{ background-color: #28A745; }}
        .btn-purple {{ background-color: #8E44AD; }}
        .btn-purple:hover {{ background-color: #732D91; }}
        
        .nav-grid {{
            display: flex;
            gap: 10px;
            margin-bottom: 12px;
        }}
        .nav-grid .btn {{ flex: 1; margin-bottom: 0; height: 44px; font-size: 14px; }}
        
        hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 12px 0; }}

        .spoken-title {{ 
            color: #FF6600; font-size: 22px; font-weight: bold; margin-bottom: 4px; min-height: 36px; 
            border: 2px dashed #FF6600; border-radius: 8px; padding: 6px; outline: none; background: #FFF9F5; width: 100%; text-align: center;
        }}
        .spoken-trans {{ 
            color: #0066CC; font-size: 16px; font-weight: bold; margin-bottom: 10px; min-height: 28px; 
            border: 2px dashed #0066CC; border-radius: 8px; padding: 6px; outline: none; background: #F0F7FF; width: 100%; text-align: center;
        }}
        
        .btn-outline {{
            background-color: #FFFFFF !important;
            color: #FF6600 !important;
            border: 2px solid #FF6600 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            height: 46px;
        }}
        
        .meta-info {{ font-size: 12px; color: #555; margin-top: 8px; line-height: 1.4; }}

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
            max-width: 340px;
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            max-height: 75vh;
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

    <input type="text" id="speechOutput" class="spoken-title" value="Spoken Thai text...">
    <input type="text" id="speechTrans" class="spoken-trans" value="English translation...">

    <button id="sttBtn" class="btn btn-orange" onclick="startRecognition()">TRANSLATE</button>
    <button class="btn btn-outline" onclick="speakRecognizedText()">HEAR SPOKEN THAI TEXT</button>
    <button class="btn btn-purple" onclick="addSpokenToSheet()">ADD TO SHEET</button>

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
        const WEB_APP_URL = "https://script.google.com/macros/s/AKfycbztke4DWB6dRnKpk-lel6kKZt5uU9fhvDxWrEaUFF7Rc9chuPrBgj9YOcNj8uCg-1sa/exec";
        
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

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        
        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.lang = 'th-TH';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onresult = async (event) => {{
                const text = event.results[0][0].transcript.trim();
                document.getElementById('speechOutput').value = text;
                resetSttBtn();
                
                document.getElementById('speechTrans').value = "Translating...";
                
                const cleanedText = text.normalize('NFC');
                const match = fullDb.find(item => item.thai.trim().normalize('NFC') === cleanedText);
                
                if (match) {{
                    document.getElementById('speechTrans').value = match.english;
                }} else {{
                    try {{
                        const apiRes = await fetch(`https://api.mymemory.translated.net/get?q=${{encodeURIComponent(text)}}&langpair=th|en`);
                        const apiData = await apiRes.json();
                        if (apiData && apiData.responseData && apiData.responseData.translatedText) {{
                            document.getElementById('speechTrans').value = apiData.responseData.translatedText;
                        }} else {{
                            document.getElementById('speechTrans').value = "Translation unavailable";
                        }}
                    }} catch (err) {{
                        document.getElementById('speechTrans').value = "Translation unavailable";
                    }}
                }}
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
                }} catch(e) {{ 
                    try {{ recognition.stop(); }} catch(err) {{}}
                    resetSttBtn();
                }}
            }} else {{
                alert("Speech recognition is not supported in this browser.");
            }}
        }}

        function resetSttBtn() {{
            const btn = document.getElementById('sttBtn');
            if (btn) {{
                btn.innerText = "TRANSLATE";
                btn.style.backgroundColor = "#FF6600";
            }}
        }}

        function speakRecognizedText() {{
            const txt = document.getElementById('speechOutput').value;
            if (txt && txt !== "Spoken Thai text...") {{
                const utterance = new SpeechSynthesisUtterance(txt);
                utterance.lang = 'th-TH';
                window.speechSynthesis.speak(utterance);
            }}
        }}

        function addSpokenToSheet() {{
            const thaiText = document.getElementById('speechOutput').value.trim();
            let engText = document.getElementById('speechTrans').value.trim();
            
            if (!thaiText || thaiText === "Spoken Thai text...") {{
                alert("Please enter or speak a Thai phrase first.");
                return;
            }}

            if (!engText || engText === "Translating..." || engText === "Translation unavailable") {{
                let userEng = prompt("Enter English translation for: " + thaiText);
                if (userEng === null) return;
                engText = userEng.trim();
                document.getElementById('speechTrans').value = engText;
            }}

            const targetUrl = WEB_APP_URL + `?thai=${{encodeURIComponent(thaiText)}}&english=${{encodeURIComponent(engText)}}&category=SPOKEN`;
            const beacon = new Image();
            beacon.src = targetUrl;
            
            alert("Added to Google Sheet successfully!");
        }}

        updateCard();
    </script>
</body>
</html>
"""

components.html(html_code, height=690, scrolling=False)
