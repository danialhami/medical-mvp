import streamlit as st
import json
import os
from PIL import Image
from google import genai
from google.genai import types

# 1. Setup
st.set_page_config(page_title="AI Doctor Co-Pilot", layout="wide", page_icon="🏥")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

@st.cache_data
def load_knowledge_base():
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        return json.load(f)

kb = load_knowledge_base()

# THE FIX: Create a lightweight index so the AI doesn't get overwhelmed by drug data
diagnostic_index = [
    {
        "id": d["id"],
        "name": f"{d['name_en']} ({d['name_zh']})",
        "key_symptoms": d.get("key_physical_findings", [])
    } for d in kb["diseases"]
]

# 2. UI Layout
st.title("🏥 智能医生辅助诊断系统 (Chain-of-Thought MVP)")
st.markdown("---")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("📋 Patient Input")
    symptoms = st.text_area("Enter Patient Symptoms", height=150, placeholder="e.g., patient has a rapid growing dome shaped nodule on face")
    uploaded_image = st.file_uploader("Upload Lesion Image", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Patient Scan", use_container_width=True)
        
    analyze_btn = st.button("Run Comprehensive AI Analysis", type="primary", use_container_width=True)

with col2:
    st.header("🤖 Differential Diagnosis Results")
    
    if analyze_btn:
        if not GEMINI_API_KEY:
            st.error("API Key missing in secrets!")
        elif not symptoms and not uploaded_image:
            st.warning("Provide symptoms or an image.")
        else:
            with st.spinner("Analyzing symptoms step-by-step..."):
                try:
                    contents = []
                    
                    # THE FIX: We force the AI to think BEFORE it outputs an ID, and we only pass the lightweight index.
                    system_instruction = f"""
                    You are an expert AI medical assistant. Review the symptoms/image.
                    You must cross-reference the patient presentation ONLY with this lightweight index: {json.dumps(diagnostic_index, ensure_ascii=False)}
                    
                    Return a JSON object with this EXACT structure:
                    {{
                      "step_by_step_reasoning": "Analyze the symptoms first. Explain why they match a specific condition and rule out others.",
                      "differential_diagnoses": [
                        {{
                           "disease_name": "Name of the disease",
                           "confidence_percentage": "XX%",
                           "matched_id": "Must be the exact ID from the index (e.g., D018)"
                        }}
                      ]
                    }}
                    Provide up to 3 differential diagnoses. If symptoms don't match anything in the index, use ID 'UNMATCHED'.
                    """
                    contents.append(system_instruction)
                    
                    if symptoms: contents.append(f"Symptoms: {symptoms}")
                    if uploaded_image: contents.append(Image.open(uploaded_image))
                        
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.3 # Slightly higher to allow for creative differential generation, but strict enough for medicine
                        )
                    )
                    
                    ai_result = json.loads(response.text)
                    
                    # Display Overall Reasoning
                    st.info(f"**🩺 AI Clinical Reasoning:** {ai_result.get('step_by_step_reasoning')}")
                    st.markdown("### 📊 Differential Diagnoses")
                    
                    for idx, diagnosis in enumerate(ai_result.get("differential_diagnoses", [])):
                        conf = diagnosis.get("confidence_percentage")
                        name = diagnosis.get("disease_name")
                        db_id = diagnosis.get("matched_id")
                        
                        if idx == 0:
                            st.success(f"**1. {name}** — Confidence: `{conf}` (Primary)")
                        else:
                            st.warning(f"**{idx+1}. {name}** — Confidence: `{conf}`")
                        
                        # THE FIX: We pull the heavy drug data locally using Python, NOT the AI
                        matched_disease = next((d for d in kb["diseases"] if d["id"] == db_id), None)
                        
                        if matched_disease:
                            st.markdown(f"**ICD-10:** `{matched_disease.get('icd_10', 'N/A')}` | **Category:** `{matched_disease.get('category_zh', 'N/A')}`")
                            with st.expander(f"💊 View Trending Drugs & Clinical Pathways", expanded=(idx==0)):
                                for drug in matched_disease.get("trending_drugs", []):
                                    st.markdown(f"**{drug['generic_name']} ({drug['trade_name']})**")
                                    st.write(f"- **Dosage:** {drug['usage_and_dosage']}")
                                    st.write(f"- **Trend & Reason:** {drug['trend_status']} — {drug['reason']}")
                                    st.write(f"- **Insurance:** {drug['medical_insurance']}")
                                    st.error(f"⚠️ **Alert:** {drug['safety_alert']}")
                                    st.markdown("---")
                                    
                                if "patient_education" in matched_disease:
                                    st.markdown("**📋 Patient Education:**")
                                    for tip in matched_disease["patient_education"]:
                                        st.caption(f"- {tip}")
                        else:
                            if db_id == "UNMATCHED":
                                st.caption("*No regional drug data available in local database for this specific condition.*")
                        
                except Exception as e:
                    st.error(f"Failed to parse AI response: {e}")
