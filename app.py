import streamlit as st
import os
from google import genai

# This line finds the key from the Streamlit Cloud Secrets dashboard
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

# Initialize the AI client securely
client = genai.Client(api_key=GEMINI_API_KEY)
