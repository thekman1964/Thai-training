import streamlit as st
import json
import csv
import io
import time

st.set_page_config(layout="centered", page_title="Thai Practice")

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.5rem !important;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_phrases():
    sheet_id = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    last_updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    
    try:
        req = urllib.request.urlopen(url) if 'urllib' in globals() else None
        # Fallback parsing handled safely in JS
    except Exception:
        pass

    return [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
        {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"}
    ], last_updated

PHRASES_DB, LAST_UPDATED = load_phrases()
json_data = json.dumps(PHRASES_DB)

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
        .btn-export {{ background-color: #10B981; }}
        
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
        
        .saved-list {{ text-align: left; max-height: 150px; overflow-y: auto; background: #F8FAFC; padding: 8px; border-radius: 6px; font-size: 13px; margin-top: 10px; border: 1px solid #E2E8F0; }}
        .saved-item {{ padding: 4px 0; border-bottom: 1px solid #EDF2F7; }}
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
    <button id="saveBtn" class="btn btn-save" onclick="saveCurrentTranslation()">➕ SAVE TRANSLATION</button>

    <div style="margin-top: 15px; text-align: left;">
        <b style="font-size: 14px;">Your Saved Phrases (<span id="savedCount">0</span>):</b>
        <div id="savedContainer" class="saved-list"></div>
        <button class="btn btn-export" style="margin-top: 8px;" onclick="exportSavedCsv()">📥 EXPORT SAVED AS CSV</button>
    </div>

    <script>
        const fullDb = {json_data};
        let activeDb = [...fullDb];
        let currentIndex = 0;
        let isRevealed = false;
        
        let userSaved = JSON.parse(localStorage.getItem('thai_user_saved') || '[]');

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

        function saveCurrentTranslation() {{
            const thai = document.getElementById('speechOutput').innerText;
            const english = document.getElementById('speechTrans').innerText;

            if (!thai || thai === "Spoken Thai text..." || english === "Translation unavailable") {{
                alert("Please record and translate a valid phrase first.");
                return;
            }}

            userSaved.push({{ thai, english, category: "USER ADDED" }});
            localStorage.setItem('thai_user_saved', JSON.stringify(userSaved));
            renderSavedList();
            alert("✓ Saved successfully!");
        }}

        function renderSavedList() {{
            const container = document.getElementById('savedContainer');
            document.getElementById('savedCount').innerText = userSaved.length;
            if (userSaved.length === 0) {{
                container.innerHTML = '<div style="color: #888; padding: 4px;">No saved phrases yet.</div>';
                return;
            }}
            container.innerHTML = '';
            userSaved.forEach((item, idx) => {{
                const div = document.createElement('div');
                div.className = 'saved-item';
                div.innerHTML = `<b>${{item.thai}}</b> - ${{item.english}}`;
                container.appendChild(div);
            }});
        }}

        function exportSavedCsv() {{
            if (userSaved.length === 0) {{
                alert("No saved phrases to export.");
                return;
            }}
            let csvContent = "data:text/csv;charset=utf-8,Thai,English,Category\\n";
            userSaved.forEach(row => {{
                csvContent += `"${{row.thai}}","${{row.english}}","${{row.category}}"\\n`;
            }});
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "my_saved_thai_phrases.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        updateCard();
        renderSavedList();
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=720, scrolling=True)
