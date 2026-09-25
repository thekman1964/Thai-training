# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Bulletproof mobile CSS: Forces side-by-side columns and correct Thai diacritic rendering on iOS/Android
st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.5rem !important; max-width: 500px;}
    
    /* Force all columns to stay side-by-side on mobile */
    [data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 0px !important;
        padding: 0 2px !important;
    }
    
    .stButton button {
        width: 100% !important; 
        border-radius: 6px; 
        font-weight: bold; 
        height: 40px; 
        font-size: 12px;
        padding: 0px !important;
    }
    
    /* Universal font stack including Apple/Android system fonts for correct Thai rendering */
    h1, p, div, span, button {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Tahoma, Arial, sans-serif !important;
    }
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
            
            if thai and thai.lower() != "nan" and english and english.lower() != "nan":
                phrases.append({
                    "thai": thai,
                    "english": english,
                    "category": category if category else "GENERAL"
                })
        if phrases:
            return phrases
    except Exception:
        pass
    
    return [
        {"thai": "เลี้ยวขวาครับ", "english": "Turn right please.", "category": "NAVIGATION"},
        {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left.", "category": "NAVIGATION"},
        {"thai": "ขอโทษครับ", "english": "Excuse me.", "category": "GENERAL"}
    ]

PHRASES_DB = load_phrases()

if "index" not in st.session_state:
    st.session_state.index = 0
if "revealed" not in st.session_state:
    st.session_state.revealed = False

st.markdown("<div style='text-align: center;'><h3>🇹🇭 Thai Practice</h3></div>", unsafe_allow_html=True)

current_card = PHRASES_DB[st.session_state.index % len(PHRASES_DB)]

st.markdown("---")
st.markdown(f"<h1 style='text-align: center; font-size: 32px; margin-bottom: 0px;'>{current_card['thai']}</h1>", unsafe_allow_html=True)

if st.session_state.revealed:
    st.markdown(f"<p style='text-align: center; font-size: 18px; color: #0066CC; font-weight: bold; margin-top: 5px;'>{current_card['english']}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; font-size: 12px; color: #777; margin-top: 5px;'>Click 'Reveal' for translation</p>", unsafe_allow_html=True)

# 4 side-by-side columns for all controls to guarantee a clean mobile layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("REVEAL", type="primary"):
        st.session_state.revealed = not st.session_state.revealed
        st.rerun()
with col2:
    if st.button("BACK"):
        st.session_state.index = (st.session_state.index - 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()
with col3:
    if st.button("RANDOM"):
        st.session_state.index = random.randint(0, len(PHRASES_DB) - 1)
        st.session_state.revealed = False
        st.rerun()
with col4:
    if st.button("NEXT"):
        st.session_state.index = (st.session_state.index + 1) % len(PHRASES_DB)
        st.session_state.revealed = False
        st.rerun()
