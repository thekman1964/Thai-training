import streamlit as st
import csv
import urllib.request
import urllib.parse
import io
import time
import json
from streamlit_mic_recorder import speech_to_text

st.set_page_config(layout="centered", page_title="Thai Practice")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzInN-jnJSFBs7XkodFxP1Y_BR5QnjNFmFU2L080hmhLe3LiGBJobu6oPJ2mwBQOD0s0Q/exec"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .stApp {background-color: #FFFFFF !important;}
    .block-container {padding: 1rem !important; max-width: 500px;}
    div.stButton > button {width: 100%; height: 48px; font-weight: bold; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

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

def translate_thai(text):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=th|en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data.get("responseData", {}).get("translatedText", "Translation unavailable")
    except Exception:
        return "Translation error"

st.title("🇹🇭 Thai Language Sync")

st.subheader("🎤 Speak Thai")
text_spoken = speech_to_text(language='th-TH', start_prompt="TAP TO RECORD THAI", stop_prompt="STOP RECORDING", key='speech_input')

if text_spoken:
    st.session_state["recorded_thai"] = text_spoken
    st.session_state["translated_eng"] = translate_thai(text_spoken)

recorded_thai = st.text_input("Spoken Thai Text", value=st.session_state.get("recorded_thai", ""))
translated_eng = st.text_input("English Translation", value=st.session_state.get("translated_eng", ""))

if st.button("➕ SAVE DIRECTLY TO SPREADSHEET", type="primary"):
    if recorded_thai and translated_eng:
        with st.spinner("Writing to Google Sheet..."):
            try:
                params = urllib.parse.urlencode({
                    "thai": recorded_thai,
                    "english": translated_eng,
                    "category": "USER ADDED"
                })
                full_url = f"{WEBHOOK_URL}?{params}"
                req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    res_text = response.read().decode('utf-8')
                    if "SUCCESS" in res_text:
                        st.success(f"✓ Appended to Sheet: {recorded_thai} — {translated_eng}")
                    else:
                        st.error(f"Sheet returned error: {res_text}")
            except Exception as e:
                st.error(f"Server save failed: {e}")
    else:
        st.warning("Please capture audio or enter text in both fields.")
