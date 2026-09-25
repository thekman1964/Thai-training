import streamlit as st
import time
import random
import requests

st.set_page_config(layout="centered", page_title="Thai Practice")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbznTCxcQ2BYhYp59_gtqgb82DX8Qo4NKBLLhN3ftIxwQEvzs25kVFpv1hjq5jgmWLgHhQ/exec"

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
        response = requests.get(WEB_APP_URL, timeout=10)
        if response.status_code == 200:
            # Check if Google returned an HTML login page instead of JSON
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return None, f"Apps Script returned HTML instead of JSON. Did you set 'Who has access' to 'Anyone' and create a NEW deployment?"
            
            records = response.json()
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
        else:
            return None, f"HTTP Error Status: {response.status_code}"
    except Exception as e:
        return None, str(e)

    return None, "Unknown loading error."

PHRASES_DB, err = load_phrases()

if err:
    st.warning(f"⚠️ Notice: {err}. Using safe fallback cards.")
    # Unicode-escaped so Windows editors cannot corrupt the Thai characters
    PHRASES_DB = [
        {"thai": "\u0e4e\u0e40\u0e25\u0e35\u0e40\u0e22\u0e49\u0e27\u0e02\u0e27\u0e32\u0e04\u0e23\u0e31\u0e1a", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "\u0e15\u0e23\u0e07\u0e40\u0e1b\u0e35\u0e22\u0e19", "english": "Go straight.", "category": "NAVIGATION"},
        {"thai": "\u0e02\u0e2d\u0e42\u0e17\u0e37\u0e04\u0e23\u0e31\u0e1a", "english": "Excuse me.", "category": "GENERAL"}
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
                payload = {
                    "thai": new_thai.strip(),
                    "english": new_english.strip(),
                    "category": new_category.strip()
                }
                res = requests.post(WEB_APP_URL, json=payload, timeout=10)
                if res.status_code == 200:
                    st.success(f"Successfully appended: {new_thai} -> {new_english}")
                    st.cache_data.clear()
                else:
                    st.error("Failed to write to sheet via Web App.")
            except Exception as e:
                st.error(f"Network error: {e}")
        else:
            st.warning("Please fill in both Thai and English fields.")
