import streamlit as st
import csv
import urllib.request
import urllib.parse
import io
import time

st.set_page_config(layout="centered", page_title="Thai Practice")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzInN-jnJSFBs7XkodFxP1Y_BR5QnjNFmFU2L080hmhLe3LiGBJobu6oPJ2mwBQOD0s0Q/exec"

# Hide Streamlit Chrome UI
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .stApp {background-color: #FFFFFF !important;}
    .block-container {padding: 0.5rem !important;}
    </style>
""", unsafe_allow_html=True)

# Load phrases dataset
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

# Native Streamlit Form for reliable saving directly from Python backend
with st.form("native_save_form", clear_on_submit=False):
    st.markdown("### ➕ Manual / Quick Sheet Sync")
    st_thai = st.text_input("Thai Phrase")
    st_eng = st.text_input("English Translation")
    submitted = st.form_submit_button("SAVE DIRECTLY TO SPREADSHEET")
    
    if submitted:
        if st_thai and st_eng:
            try:
                params = urllib.parse.urlencode({
                    "thai": st_thai,
                    "english": st_eng,
                    "category": "USER ADDED"
                })
                req = urllib.request.Request(f"{WEBHOOK_URL}?{params}", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    st.success(f"✓ Successfully written to Sheet: {st_thai} — {st_eng}")
            except Exception as e:
                st.error(f"Save failed: {e}")
        else:
            st.warning("Please fill in both fields.")
