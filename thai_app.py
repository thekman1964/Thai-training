import streamlit as st
from gtts import gTTS
import io
import base64
import random
import time
import requests
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(layout="centered", page_title="Thai Practice")

# --- Mobile Compact & Precise Styling ---
st.markdown("""
    <style>
    /* Hide top Streamlit header bar, main menu, and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stHeader"] {display: none;}
