import streamlit as st
import csv
import urllib.request
import urllib.parse
import io
import time
import json

st.set_page_config(layout="centered", page_title="Thai Practice")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzInN-jnJSFBs7XkodFxP1Y_BR5QnjNFmFU2L080hmhLe3LiGBJobu6oPJ2mwBQOD0s0Q/exec"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 1rem !important; max-width: 500px;}
    div.stButton > button {width: 100%; height: 48px; font-weight: bold; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

st.title("🇹🇭 Thai Language Practice")

def translate_thai(text):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=th|en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data.get("responseData", {}).get("translatedText", "")
    except Exception:
        return ""

# Audio Upload Option
audio_file = st.file_uploader("Record or Upload Audio", type=["wav", "mp3", "m4a", "ogg"])

with st.form("sheet_sync_form"):
    thai_input = st.text_input("Thai Text", value=st.session_state.get("thai_val", ""))
    
    # Auto-translate trigger
    if st.form_submit_button("1. Auto-Translate Thai"):
        if thai_input:
            translated = translate_thai(thai_input)
            st.session_state["thai_val"] = thai_input
            st.session_state["eng_val"] = translated
            st.rerun()

    english_input = st.text_input("English Translation", value=st.session_state.get("eng_val", ""))
    
    # Save button executed strictly server-side
    save_submitted = st.form_submit_button("2. ➕ SAVE TO SPREADSHEET")

    if save_submitted:
        if thai_input and english_input:
            try:
                params = urllib.parse.urlencode({
                    "thai": thai_input,
                    "english": english_input,
                    "category": "USER ADDED"
                })
                full_url = f"{WEBHOOK_URL}?{params}"
                req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req) as response:
                    res_text = response.read().decode('utf-8')
                    if "SUCCESS" in res_text:
                        st.success(f"✓ Saved: {thai_input} — {english_input}")
                    else:
                        st.error(f"Google Sheet response: {res_text}")
            except Exception as e:
                st.error(f"Server save error: {e}")
        else:
            st.warning("Please fill in both fields before saving.")
