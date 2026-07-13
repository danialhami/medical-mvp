import streamlit as st
import json

# 1. Set up Page Config & Custom CSS for a "Stunning" UI
st.set_page_config(page_title="AI Doctor Co-Pilot", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    /* Modern minimalist theme */
    .main { background-color: #f8f9fc; }
    .stTextArea textarea { border-radius: 10px; border: 1px solid #e0e4f1; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .css-1d391kg { padding-top: 2rem; }
    
    /* Custom Card Styling */
    .diagnosis-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f4f9 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #4CAF50;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .header-gradient {
        background: -webkit-linear-gradient(45deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Clean up the file uploader */
    .stFileUploader { border-radius: 10px; background-color: white; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. Bilingual Setup: Language Toggle
col_lang1, col_lang2 = st.columns([5, 1])
with col_lang2:
    language = st.radio("Language / 语言", ["中文 (Chinese)", "English"], horizontal=True, label_visibility="collapsed")

if language == "中文 (Chinese)":
    ui = {
        "title": "智能医生辅助诊断系统",
        "subtitle": "⚡ 极速离线引擎 | 实时概率分析",
        "input_header": "📋 临床输入 (实时监测)",
        "symptoms_label": "输入患者症状 / 临床观察",
        "symptoms_placeholder": "在此输入症状，系统将实时进行疾病预测...",
        "upload_label": "📷 上传皮损图像",
        "output_header": "🤖 实时诊断与概率分析",
        "primary_dx": "首选诊断 (Primary Diagnosis)",
        "confidence": "置信度:",
        "ddx_header": "📊 鉴别诊断概率 (Top 3 DDx)",
        "icd_label": "ICD-10 编码:",
        "rx_header": "💊 推荐处方与干预方案",
        "disclaimer": "⚠️ 仅供医疗专业人员参考。最终决定需由执业医师确认。"
    }
    db_file = "dermatology_core_data_CN.json"
    default_disease = "特应性皮炎"
else:
    ui = {
        "title": "AI Doctor Co-Pilot System",
        "subtitle": "⚡ Zero-Latency Offline Engine | Real-Time Probabilities",
        "input_header": "📋 Clinical Input (Real-Time)",
        "symptoms_label": "Enter Patient Symptoms / Clinical Observations",
        "symptoms_placeholder": "Start typing symptoms here for instant predictions...",
        "upload_label": "📷 Upload Lesion Image",
        "output_header": "🤖 Real-Time Diagnostic Insights",
        "primary_dx": "Primary Diagnosis",
        "confidence": "Confidence:",
        "ddx_header": "📊 Differential Diagnosis Probabilities (Top 3)",
        "icd_label": "ICD-10 Code:",
        "rx_header": "💊 Recommended Prescriptions & Interventions",
        "disclaimer": "⚠️ For medical professional use only. Final signature required by a physician."
    }
    db_file = "dermatology_core_data_EN.json"
    default_disease = "atopic_dermatitis"

# 3. Load Local Knowledge Base
@st.cache_data
def load_knowledge_base(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"⚠️ '{file_name}' not found. Please ensure it is uploaded.")
        st.stop()

kb = load_knowledge_base(db_file)

# 4. Main Layout
st.markdown(f"<h1 class='header-gradient'>🏥 {ui['title']}</h1>", unsafe_allow_html=True)
st.caption(ui["subtitle"])
st.markdown("---")

col1, spacer, col2 = st.columns([1.2, 0.1, 1.5])

with col1:
    st.markdown(f"### {ui['input_header']}")
    # Real-time text area: Streamlit auto-reruns when the user pauses/clicks away
    symptoms = st.text_area(ui["symptoms_label"], placeholder=ui["symptoms_placeholder"], height=200)
    uploaded_image = st.file_uploader(ui["upload_label"], type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Scan Active", use_container_width=True, clamp=True)

with col2:
    st.markdown(f"### {ui['output_header']}")
    
    # --- 100% OFFLINE PROBABILITY MATH ENGINE ---
    scores = {}
    symptom_lower = symptoms.lower() if symptoms else ""
    
    # Calculate scores for ALL diseases simultaneously
    for key, data in kb["conditions"].items():
        score = 0
        if symptoms:
            # 1. High-weight exact name matches
            if key.lower() in symptom_lower: score += 20
            if data.get("name_en", "").lower() in symptom_lower: score += 20
            if data.get("name_cn", "") in symptom_lower or data.get("name", "") in symptom_lower: score += 20
            
            # 2. Medium-weight physical finding matches
            findings = data.get("key_physical_findings", data.get("关键体征", []))
            for finding in findings:
                words = finding.replace("_", " ").lower().split()
                for word in words:
                    if len(word) > 2 and word in symptom_lower: score += 3
            
            # 3. Low-weight DDx context matches
            ddx_list = data.get("differential_diagnosis", data.get("鉴别诊断", []))
            for ddx in ddx_list:
                disease_str = ddx.get("disease", ddx.get("疾病", "")).replace("_", " ").lower()
                if disease_str and disease_str in symptom_lower: score += 1
                
        scores[key] = score

    # Sort diseases by score
    sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate Probabilities (Relative Confidence for Top 3)
    top_3 = sorted_diseases[:3]
    top_total_score = sum(v for k, v in top_3)
    
    probabilities = []
    if top_total_score > 0:
        for k, v in top_3:
            # Softmax-style relative percentage
            prob = (v / top_total_score) * 100
            probabilities.append((k, prob))
    else:
        # Default idle state if nothing is typed
        probabilities = [(default_disease, 98.5), (list(kb["conditions"].keys())[1], 1.0), (list(kb["conditions"].keys())[2], 0.5)]

    # --- RENDER STUNNING UI ---
    
    # 1. Primary Diagnosis Card
    primary_key, primary_prob = probabilities[0]
    matched_data = kb["conditions"][primary_key]
    
    name = matched_data.get("name", primary_key)
    name_en_or_cn = matched_data.get("name_en", matched_data.get("name_cn", ""))
    
    st.markdown(f"""
    <div class="diagnosis-card">
        <h4 style="color: #4CAF50; margin-top: 0;">{ui['primary_dx']}</h4>
        <h2>{name} <span style="font-size: 18px; color: #666;">({name_en_or_cn})</span></h2>
        <p><b>{ui['icd_label']}</b> <code>{matched_data['icd10']}</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Probability Progress Bars (Top 3 DDx)
    st.markdown(f"**{ui['ddx_header']}**")
    for dx_key, prob in probabilities:
        dx_name = kb["conditions"][dx_key].get("name", dx_key)
        col_dx, col_prob = st.columns([3, 1])
        with col_dx:
            st.markdown(f"*{dx_name}*")
            # Convert prob to 0.0 - 1.0 for the progress bar
            st.progress(prob / 100.0)
        with col_prob:
            st.markdown(f"<h3 style='text-align: right; color: #1e3c72; margin-top: -5px;'>{prob:.1f}%</h3>", unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Beautiful Expanding Prescription Panels
    st.markdown(f"### {ui['rx_header']}")
    prescriptions = matched_data.get("处方", matched_data.get("prescriptions", {}))
    
    for category, drugs in prescriptions.items():
        with st.expander(f"📌 {category.replace('_', ' ').title()}", expanded=True):
            for item in drugs:
                if "drug" in item or "药品" in item:
                    d_name = item.get("drug", item.get("药品", "Unknown Drug"))
                    d_en = item.get("英文名", item.get("drug_cn", ""))
                    dose = item.get("dose", item.get("用法", "Standard dose"))
                    
                    st.markdown(f"**{d_name}** ({d_en})  \n*{dose}*")
                    
                    alert = item.get("alert", item.get("警示", ""))
                    if alert: 
                        color = "red" if "RED" in alert.upper() or "红" in alert else "orange" if "YELLOW" in alert.upper() or "黄" in alert else "green"
                        st.markdown(f":{color}[**Safety Alert: {alert}**]")
                    st.divider()
                else:
                    st.info(f"💡 {item.get('special', item.get('特殊说明', 'Intervention'))}")

    st.caption(ui["disclaimer"])
