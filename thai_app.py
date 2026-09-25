# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
# Corrected Google Visualization API CSV export endpoint (prevents 400 Bad Request)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.8rem !important; max-width: 500px;}
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 48px; margin-bottom: 4px;}
    h1, p, div, span, button {font-family: Tahoma, Arial, sans-serif !important;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_phrases():
    try:
        df = pd.read_csv(CSV_URL, encoding='utf-8')
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        phrases = []
        for _, row in df.iterrows():
            thai = str(row.get("thai", "")).strip()
            english = str(row.get("english", "")).strip()
            category = str(row.get("category", "general")).strip().upper()
            
            if thai and thai != "nan" and english and english != "nan":
                phrases.append({
                    "thai": thai,
                    "english": english,
                    "category": category if category else "GENERAL"
                })
        if phrases:
            return phrases
    except Exception:
        pass
    
    # Unicode-escaped fallback list (immune to Windows text editor encoding corruption)
    return [
        {"thai": "\u0e4e\u0e40\u0e25\u0e35\u0e40\u0e22\u0e49\u0e27\u0e02\u0e27\u0e32\u0e04\u0e23\u0e31\u0e1a", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "\u0e15\u0e23\u0e07\u0e40\u0e1b\u0e35\u0e22\u0e19", "english": "Go straight.", "category": "NAVIGATION"},
        {"thai": "\u0e02\u0e2d\u0e42\u0e17\u0e37\u0e04\u0e23\u0e31\u0e1a", "english": "Excuse me.", "category": "GENERAL"}
    ]

PHRASES_DB = load_phrases()

if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

st.markdown("<div style='text-align: center;'><h3>🇹🇭 Thai Listening & Reading</h3></div>", unsafe_allow_html=True)

current_card = PHRASES_DB[st.session_state.index % len(PHRASES_DB)]

st.markdown("---")
st.markdown(f"<h1 style='text-align: center; font-size: 36px; margin-bottom: 4px;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.revealed:
    st.markdown(f"<p style='text-align: center; font-size: 20px; color: #0066CC; font-weight: bold;'>{current_card['english']}</p>", unsafe_allow_html=True)
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
