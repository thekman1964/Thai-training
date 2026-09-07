@st.cache_data(ttl=600)
def load_phrases_with_meta():
    sheet_id = "1_vMSPtMo3-JD2qARp4zwrcvNrhEuSKHQVEOT1IMwgFw"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    last_updated = "Unknown"
    
    # Try fetching live Google Sheet
    try:
        head_res = requests.head(url)
        if "Last-Modified" in head_res.headers:
            last_updated = head_res.headers["Last-Modified"]
        else:
            last_updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
        
        df = pd.read_csv(url)
        if "Thai" in df.columns and "English" in df.columns:
            phrases = df[['Thai', 'English']].dropna().to_dict('records')
            cleaned = [{"thai": str(p['Thai']).strip(), "english": str(p['English']).strip()} for p in phrases if str(p['Thai']).strip()]
            if cleaned:
                return cleaned, last_updated
    except Exception:
        pass

    # Local fallback to attached CSV file if Google Sheets fetch fails
    try:
        df_local = pd.read_csv("Thai_Phrases_for_app.csv")
        phrases = df_local[['Thai', 'English']].dropna().to_dict('records')
        cleaned = [{"thai": str(p['Thai']).strip(), "english": str(p['English']).strip()} for p in phrases if str(p['Thai']).strip()]
        return cleaned, "Loaded from local file"
    except Exception:
        return [
            {"thai": "เลี้ยวขวาครับ", "english": "Turn right please."},
            {"thai": "ตรงไปแล้วเลี้ยวซ้าย", "english": "Go straight then turn left."},
            {"thai": "ขอโทษครับ", "english": "Excuse me."}
        ], last_updated
