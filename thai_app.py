import streamlit as st
import time
import random
import gspread

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.8rem !important; max-width: 500px;}
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 48px; margin-bottom: 4px;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_phrases():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        client = gspread.service_account_from_dict(creds_dict)
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        
        records = sheet.get_all_records()
        cleaned = []
        for row in records:
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
            return cleaned, None
    except Exception as e:
        return None, str(e)

    return None, "No records found in spreadsheet."

PHRASES_DB, error_msg = load_phrases()

if error_msg:
    st.error(f"⚠️ Google Sheets Error: {error_msg}")
    PHRASES_DB = [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
        {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"}
    ]

if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

st.markdown("<div style='text-align: center;'><h3>🇹🇭 Thai Listening & Reading</h3></div>", unsafe_allow_html=True)

current_card = PHRASES_DB[st.session_state.index % len(PHRASES_DB)]

st.markdown("---")
st.markdown(f"<h1 style='text-align: center; font-size: 38px; margin-bottom: 4px;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.revealed:
    st.markdown(f"<p style='text-align: center; font-size: 22px; color: #0066CC; font-weight: bold;'>{current_card['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; font-size: 13px; color: #777;'>Click 'Reveal' to view English translation</p>", unsafe_allow_html=True)

if st.button("REVEAL", type="primary"):
    st.session_state.revealed = not st.session_state.revealed
    st.rerun()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("BACK"):
        st.session_state.index = (st.session_state.index - 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()
with col2:
    if st.button("RANDOM"):
        st.session_state.index = random.randint(0, len(PHRASES_DB) - 1)
        st.session_state.revealed = False
        st.rerun()
with col3:
    if st.button("NEXT"):
        st.session_state.index = (st.session_state.index + 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()

st.markdown("---")
st.markdown("### ➕ Add New Phrase to Google Sheet")

with st.form("add_form", clear_on_submit=True):
    new_thai = st.text_input("Thai Text")
    new_english = st.text_input("English Translation")
    new_category = st.selectbox("Category", ["NAVIGATION", "GENERAL", "USER ADDED", "FOOD", "EMERGENCY"])
    
    submitted = st.form_submit_button("Save to Spreadsheet")
    if submitted:
        if new_thai.strip() and new_english.strip():
            try:
                creds_dict = dict(st.secrets["gcp_service_account"])
                if "private_key" in creds_dict:
                    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                
                client = gspread.service_account_from_dict(creds_dict)
                sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
                
                sheet.append_row([new_thai.strip(), new_english.strip(), new_category.strip()])
                st.success(f"Successfully appended: {new_thai} -> {new_english}")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed to write to sheet: {e}")
        else:
            st.warning("Please fill in both Thai and English fields.")
