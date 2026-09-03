import streamlit as st
import streamlit.components.v1 as components
import random
import csv
import urllib.request
import base64
import time
from io import BytesIO
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Thai Listening and Reading",
    page_icon="🇹🇭",
    layout="centered"
)

# --- GOOGLE SHEET CONFIGURATION ---
SPREADSHEET_ID = '1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw'
CSV_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv'

@st.cache_data(ttl=30)
def load_phrases_from_google_sheet():
    phrases = []
    error_message = None
    try:
        req = urllib.request.Request(
            CSV_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            lines = [line.decode('utf-8') for line in response.readlines()]
            reader = csv.DictReader(lines)
            
            for row in reader:
                thai = row.get('Thai', '').strip()
                eng = row.get('English', '').strip()
                if thai and eng:
                    phrases.append({"Thai": thai, "English": eng})
    except Exception as e:
        error_message = str(e)
    
    return phrases, error_message

phrases_data, fetch_error = load_phrases_from_google_sheet()

# --- COMPACT STYLING & PERFECT ALIGNMENT CSS ---
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 700px !important; 
    }
    
    .stApp { background-color: #f8fafc; }
    
    .main-title { 
        font-size: 24px !important; 
        font-weight: 800; 
        color: #0f172a; 
        text-align: center; 
        margin-top: 0px; 
        margin-bottom: 4px; 
    }
    
    .card-container { 
        background: white; 
        border-radius: 12px; 
        padding: 12px 15px 8px 15px; 
        box-shadow: 0 4px 15px -3px rgba(0,0,0,0.08); 
        text-align: center; 
        border: 1px solid #e2e8f0; 
        margin-bottom: 4px; 
    }
    
    .thai-heading { 
        font-size: 32px !important; 
        font-weight: 800; 
        color: #0f172a; 
        margin-bottom: 2px; 
        line-height: 1.2;
    }
    
    .english-sub { 
        font-size: 19px !important; 
        font-weight: 600; 
        color: #2563eb; 
        min-height: 24px; 
        margin-bottom: 4px;
    }
    
    .hidden-text { 
        font-size: 15px !important; 
        color: #94a3b8; 
        font-style: italic; 
        min-height: 24px; 
        margin-bottom: 4px;
    }
    
    /* ENFORCED ORANGE BORDER ON PLAY PHRASE BUTTON */
    .st-key-play_phrase_btn button {
        border: 2px solid #f97316 !important;
        color: #ea580c !important;
        font-weight: 600 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
        height: 42px !important;
        margin-top: 0px !important;
    }
    .st-key-play_phrase_btn button:hover {
        background-color: #fff7ed !important;
        border-color: #ea580c !important;
        color: #c2410c !important;
    }

    /* ALIGNMENT FIX FOR BOTH COLUMNS */
    div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
    }
    
    div[data-testid="column"] > div {
        width: 100% !important;
    }

    /* Eliminate vertical gaps and offset from custom components */
    div[data-testid="column"] iframe {
        height: 42px !important;
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    div[data-testid="column"] p {
        margin-bottom: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- AUDIO GENERATION ---
@st.cache_data
def get_gtts_audio(text):
    try:
        tts = gTTS(text=text, lang='th')
        tts_fp = BytesIO()
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)
        return tts_fp.read()
    except Exception as e:
        return None

def trigger_audio_playback(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    ts = int(time.time() * 1000)
    audio_html = f"""
        <audio id="audio_{ts}" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var sound = document.getElementById("audio_{ts}");
            if (sound) {{
                sound.currentTime = 0;
                sound.play().catch(function(e) {{ console.log(e); }});
            }}
        </script>
    """
    components.html(audio_html, height=0, width=0)

# --- STATE MANAGEMENT ---
if "index" not in st.session_state:
    st.session_state.index = 0
if "reveal" not in st.session_state:
    st.session_state.reveal = False
if "should_autoplay" not in st.session_state:
    st.session_state.should_autoplay = False

st.markdown('<div class="main-title">Thai Listening and Reading</div>', unsafe_allow_html=True)

if fetch_error:
    st.error(f"⚠️ Could not load Google Sheet: {fetch_error}")

total = len(phrases_data)

if total > 0:
    if st.session_state.index >= total:
        st.session_state.index = 0

    card = phrases_data[st.session_state.index]

    # --- CARD DISPLAY ---
    st.markdown(f"""
    <div class="card-container">
        <div class="thai-heading">{card['Thai']}</div>
        <div class="{ 'english-sub' if st.session_state.reveal else 'hidden-text' }">
            {card['English'] if st.session_state.reveal else 'Click "Reveal" to view English translation'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- REVEAL BUTTON ---
    _, reveal_col, _ = st.columns([1, 2, 1])
    with reveal_col:
        if st.button("👁️ Reveal", use_container_width=True):
            st.session_state.reveal = not st.session_state.reveal
            st.session_state.should_autoplay = True
            st.rerun()

    # --- AUDIO & MIC SECTION (ALIGNMENT FIX) ---
    col_audio, col_mic = st.columns(2)

    trigger_play = False

    with col_audio:
        st.markdown("**Thai Audio Output:**")
        if st.button("▶️ Play Phrase", key="play_phrase_btn", use_container_width=True):
            trigger_play = True

    with col_mic:
        st.markdown("**Practice Pronunciation:**")
        spoken_text = speech_to_text(
            language='th',
            start_prompt="🎙️ Start Speaking",
            stop_prompt="⏹️ Stop",
            key=f"speech_rec_{st.session_state.index}"
        )

    # Trigger audio playback
    audio_bytes = get_gtts_audio(card['Thai'])
    if audio_bytes and (st.session_state.should_autoplay or trigger_play):
        trigger_audio_playback(audio_bytes)
        st.session_state.should_autoplay = False

    # Feedback area for speech recognition
    if 'spoken_text' in locals() and spoken_text:
        target_clean = card['Thai'].replace(" ", "").replace("ครับ", "").replace("ค่ะ", "")
        spoken_clean = spoken_text.replace(" ", "").replace("ครับ", "").replace("ค่ะ", "")
        if spoken_clean in target_clean or target_clean in spoken_clean:
            st.success(f"✅ Great job! Heard: **{spoken_text}**")
        else:
            st.error(f"❌ Try again. Heard: **{spoken_text}**")

    # --- NAVIGATION BUTTONS ---
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.index = (st.session_state.index - 1) % total
            st.session_state.reveal = False
            st.session_state.should_autoplay = True
            st.rerun()
    with b2:
        if st.button("➡️ Next", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % total
            st.session_state.reveal = False
            st.session_state.should_autoplay = True
            st.rerun()
    with b3:
        if st.button("🔀 Random", use_container_width=True):
            st.session_state.index = random.randint(0, total - 1)
            st.session_state.reveal = False
            st.session_state.should_autoplay = True
            st.rerun()

    st.caption(f"Card {st.session_state.index + 1} of {total}")