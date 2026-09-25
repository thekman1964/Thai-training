import streamlit as st
import csv
import io
import time
import urllib.request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 1rem !important;}
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 46px;}
    </style>
""", unsafe_allow_html=True)

# Load phrases from Google Sheet CSV export
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

# Session state initialization
if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

# App Header
col_flag, col_title = st.columns([1, 5])
with col_flag:
    st.markdown("🇹🇭")
with col_title:
    st.markdown("### Thai Listening and Reading")

current_card = PHRASES_DB[st.session_state.index]

# Flashcard Display
st.markdown("---")
st.markdown(f"<h1 style='text-align: center; font-size: 38px; margin-bottom: 5px;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.revealed:
    st.markdown(f"<p style='text-align: center; font-size: 22px; color: #0066CC; font-weight: bold;'>{current_card['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; font-size: 14px; color: #777;'>Click 'Reveal' to view English translation</p>", unsafe_allow_html=True)

# Flashcard Action Buttons
if st.button("REVEAL", type="primary"):
    st.session_state.revealed = not st.session_state.revealed
    st.rerun()

col_back, col_rand, col_next = st.columns(3)
with col_back:
    if st.button("BACK"):
        st.session_state.index = (st.session_state.index - 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()
with col_rand:
    import random
    if st.button("RANDOM"):
        st.session_state.index = random.randint(0, len(PHRASES_DB) - 1)
        st.session_state.revealed = False
        st.rerun()
with col_next:
    if st.button("NEXT"):
        st.session_state.index = (st.session_state.index + 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()

# Native Add Phrase Section (Guaranteed Server-Side Execution)
st.markdown("---")
st.markdown("### ➕ Add Custom Phrase to Google Sheet")

with st.form("add_phrase_form", clear_on_submit=True):
    new_thai = st.text_input("Thai Text")
    new_english = st.text_input("English Translation")
    new_category = st.selectbox("Category", ["GENERAL", "NAVIGATION", "FOOD", "EMERGENCY", "USER ADDED"])
    
    submitted = st.form_submit_button("Save to Spreadsheet")
    if submitted:
        if new_thai.strip() and new_english.strip():
            try:
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds_dict = dict(st.secrets["gcp_service_account"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
                
                sheet.append_row([new_thai.strip(), new_english.strip(), new_category.strip()])
                st.cache_data.clear() # Clear cache so new row is immediately available
                st.success(f"Successfully added: {new_thai} -> {new_english}")
            except Exception as e:
                st.error(f"Google Sheet write error: {e}")
        else:
            st.warning("Please provide both Thai text and English translation.")
