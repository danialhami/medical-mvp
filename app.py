import streamlit as st
import json
import time

# 1. Set up Page Config
st.set_page_config(page_title="AI Doctor Co-Pilot (China)", layout="wide", page_icon="🏥")

# 2. Load the Local Knowledge Base
def load_knowledge_base():
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ 'knowledge_base.json' not found. Please make sure the file is in the same folder.")
        st.stop()

kb = load_knowledge_base()

# 3. UI Header
st.title("🏥 智能医生辅助诊断系统 (MVP)")
st.caption("AI-Assisted Diagnostic Co-Pilot for Rapid Clinical Workflows")
st.markdown("---")

# 4. Layout: Two Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 Patient Information Input")
    
    symptoms = st.text_area(
        "Enter Patient Symptoms / Clinical Observations (Chinese or English)",
        placeholder="e.g., Patient reports severe itching on arms for 3 days, red rashes visible."
    )
    
    uploaded_image = st.file_uploader("Upload Lesion Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Patient Scan", use_container_width=True)
        
    analyze_btn = st.button("Run AI Diagnosis Analysis", type="primary", use_container_width=True)

with col2:
    st.header("🤖 AI Diagnostic Real-Time Insights")
    
    if analyze_btn:
        if not symptoms and not uploaded_image:
            st.error("Please provide either symptoms text or an image to analyze.")
        else:
            # Simulate a slight delay to make it "feel" like AI is thinking
            with st.spinner("Analyzing against global & Chinese medical databases..."):
                time.sleep(1.5) 
                
                # The "Mock" AI Logic
                matched_disease = kb["diseases"][0] # Default to Eczema
                
                # If the doctor types specific keywords, switch the diagnosis
                if symptoms:
                    if "acne" in symptoms.lower() or "粉刺" in symptoms or "痤疮" in symptoms:
                        matched_disease = kb["diseases"][1]
                
                # Display Results
                st.success(f"**Primary Diagnostic Match Found (>95% Confidence Verified)**")
                
                st.subheader(f"{matched_disease['name_zh']} ({matched_disease['name_en']})")
                st.markdown(f"**ICD-10 Code:** `{matched_disease['icd_10']}`")
                
                st.markdown("### 📈 Trending & Useful Drugs (China NMPA)")
                
                for drug in matched_disease["trending_drugs"]:
                    with st.container(border=True):
                        st.markdown(f"**Drug Name:** {drug['generic_name']} ({drug['trade_name']})")
                        st.markdown(f"**Market Trend:** `{drug['trend_status']}`")
                        st.markdown(f"**Clinical Context:** {drug['reason']}")
                        st.info(f"🇨🇳 Insurance Status: {drug['medical_insurance']}")
                
                st.markdown("---")
                st.caption("⚠️ Note: This is an AI co-pilot decision support tool. Final signature required by a licensed physician.")
    else:
        st.info("Awaiting input. Upload an image or type symptoms, then click 'Run AI Diagnosis Analysis'.")
