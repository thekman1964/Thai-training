import streamlit as st
import pandas as pd
import random

# Streamlit Page Config
st.set_page_config(
    page_title="Thai Listening and Reading",
    page_icon="🇹🇭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS Styling
st.markdown("""
    <style>
    /* Hide default Streamlit header & menu */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stHeader"] {display: none;}

    /* Main Container Styles */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Button Layout & Base Styles */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 48px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.2s ease;
    }

    /* Target REVEAL button */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #1E2230;
        color: #FFFFFF;
        border: none;
    }

    /* Target PHRASE button */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #FF6B00;
        color: #FFFFFF;
        border: none;
    }

    /* FIXED: Target RANDOM button specifically using text selector */
    div.stButton > button:has(p:contains("RANDOM")),
    div.stButton > button:has(div:contains("RANDOM")) {
        background-color: #28A745 !important;
        color: #000000 !important;
        border: none !important;
    }

    /* FORCE HORIZONTAL ROW ON MOBILE */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 8px !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 !important;
        min-width: 0 !important;
    }

    /* Typography Styles */
    .thai-text {
        font-size: 38px;
        font-weight: 700;
        text-align: center;
        margin: 20px 0 10px 0;
        color: #000000;
    }

    .sub-text {
        font-size: 14px;
        color: #6B7280;
        text-align: center;
        margin-bottom: 15px;
    }

    .translation-text {
        font-size: 24px;
        font-weight: 600;
        text-align: center;
        color: #0056B3;
        margin-top: 15px;
    }
    </style>
""", unsafe_allowed_code_value=True)

# App Title & Header
st.markdown("<h2 style='text-align: center;'>🇹🇭<br>Thai Listening and Reading</h2>", unsafe_allow_html=True)

# --- Sample Logic / Data Placeholder ---
if 'phrase_idx' not in st.session_state:
    st.session_state.phrase_idx = 0
if 'show_reveal' not in st.session_state:
    st.session_state.show_reveal = False

# Thai phrase display
st.markdown("<div class='thai-text'>เลี้ยวขวาครับ</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Click \"REVEAL\" to view English translation</div>", unsafe_allow_html=True)

# REVEAL Action
if st.button("REVEAL", key="btn_reveal"):
    st.session_state.show_reveal = not st.session_state.show_reveal

if st.session_state.show_reveal:
    st.markdown("<div class='translation-text'>Turn right please.</div>", unsafe_allow_html=True)

st.button("PHRASE", key="btn_phrase")

# Navigation Control Row
col1, col2, col3 = st.columns(3)
with col1:
    st.button("BACK", key="btn_back")
with col2:
    st.button("RANDOM", key="btn_random")
with col3:
    st.button("NEXT", key="btn_next")

# Footer Translator Section
st.markdown("<h3 style='text-align: center; color: #FF6B00; margin-top: 30px;'>Spoken Thai text...</h3>", unsafe_allow_html=True)
st.button("TRANSLATE", key="btn_translate")

st.caption("Available Records: 940 | Spreadsheet Last Updated: 2026-09-05 10:42 UTC")
