import streamlit as st
import pandas as pd
import random
import base64

st.set_page_config(layout="centered", page_title="Thai Practice")

SHEET_ID = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.markdown("""
    <style>
    #MainMenu, header, footer, div[data-testid="stHeader"] {display: none !important;}
    .block-container {padding: 0.8rem !important; max-width: 500px;}
    .stButton button {width: 100%; border-radius: 6px; font-weight: bold; height: 48px; margin-bottom: 4px;}
    </style>
""", unsafe_allow_html=True)

def b64_decode(b64_str):
    return base64.b64decode(b64_str.encode('utf-8')).decode('utf-8')

@st.cache_data(ttl=60)
def load_phrases():
    try:
        df = pd.read_csv(CSV_URL)
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
            return phrases, None
    except Exception as e:
        return None, str(e)
    
    return None, "No valid rows found in sheet."

PHRASES_DB, err = load_phrases()

if err:
    # Base64 encoded fallback strings are 100% immune to Windows text editor corruption
    PHRASES_DB = [
        {
            "thai": b64_decode("4Lit4Lix4LiZ4Li44LmI4Lih4Liq4Liy4Lij4Liw"), 
            "english": "Turn right please.", 
            "category": "NAVIGATION"
        },
        {
            "thai": b64_decode("4Lin4Li04LiX4Lii4Li04Liq4LiV4Lij4Liq4Liy4Lij4Liw"), 
            "english": "Go straight then turn left.", 
            "category": "NAVIGATION"
        },
        {
            "thai": b64_decode("4Lit4Liy4LiE4Liy4Lij4Liw"), 
            "english": "Excuse me.", 
            "category": "GENERAL"
        }
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
