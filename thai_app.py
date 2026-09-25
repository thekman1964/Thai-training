# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Strict mobile layout and forced side-by-side columns styling
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.6rem !important; max-width: 500px;}
    /* Force horizontal alignment for button columns on mobile */
    div[data-testid="column"] {
        width: 33.33% !important;
        flex: 33.33% !important;
        min-width: 33.33% !important;
    }
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 42px; font-size: 14px;}
    h1, p, div, span, button {font-family: 'Tahoma', Arial, sans-serif !important;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=10)
def load_phrases():
    try:
        df = pd.read_csv(CSV_URL, encoding='utf-8')
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        phrases = []
        for _, row in df.iterrows():
            thai = str(row.get("thai", "")).strip()
            english = str(row.get("english", "")).strip()
            category = str(row.get("category", "general")).strip().upper()
            
            # Filter out invalid, NaN, or corrupted symbol rows
            if thai and thai.lower() != "nan" and thai != "-ฐ" and english and english.lower() != "nan":
                phrases.append({
                    "thai": thai,
                    "english": english,
                    "category": category if category else "GENERAL"
                })
        if phrases:
            return phrases, f"Loaded {len(phrases)} valid phrases."
    except Exception as e:
        return None, f"Error: {e}"
    
    return None, "No valid phrases found."

PHRASES_DB, status_msg = load_phrases()

if not PHRASES_DB:
    st.warning(f"⚠️ {status_msg}")
    PHRASES_DB = [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
        {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"}
    ]

if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

st.markdown("<div style='text-align: center; margin-bottom: -10px;'><h3>🇹🇭 Thai Listening & Reading</h3></div>", unsafe_allow_html=True)

current_card = PHRASES_DB[st.session_state.index % len(PHRASES_DB)]

st.markdown("---")
st.markdown(f"<h1 style='text-align: center; font-size: 32px; margin-bottom: 0px;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.revealed:
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #0066CC; font-weight: bold; margin-top: 5px;'>{current_card['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; font-size: 12px; color: #777; margin-top: 5px;'>Click 'Reveal' to view English translation</p>", unsafe_allow_html=True)

if st.button("REVEAL", type="primary"):
    st.session_state.revealed = not st.session_state.revealed
    st.rerun()

# Three columns tightly packed side-by-side
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
