import streamlit as st
import os
from google import genai

# 1. Page Configuration
st.set_page_config(page_title="AI Doctor Co-Pilot", layout="wide")

# 2. Secure Key Retrieval
# This looks at Streamlit Cloud secrets first, then environment variables
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("CRITICAL ERROR: No API Key detected. Please ensure 'GEMINI_API_KEY' is set in Streamlit Cloud Secrets.")
    st.stop()

# 3. Fail-safe Client Initialization
try:
    # Explicitly set vertexai=False to bypass the ValueError you are seeing
    client = genai.Client(api_key=api_key, vertexai=False)
except Exception as e:
    st.error(f"Failed to initialize AI Client: {e}")
    st.stop()

st.success("AI Client initialized successfully!")

# ... rest of your code ...
