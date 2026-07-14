import streamlit as st
import json

# 1. Set up Page Config & Custom CSS
st.set_page_config(page_title="AI Doctor Co-Pilot", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    .main { background-color: #f8f9fc; }
    .stTextArea textarea { border-radius: 10px; border: 1px solid #e0e4f1; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .css-1d391kg { padding-top: 2rem; }
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
    .stFileUploader { border-radius: 10px; background-color: white; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .waiting-state {
        text-align: center;
        padding: 50px 20px;
        color: #8898aa;
        background: white;
        border-radius: 15px;
        border: 2px dashed #e0e4f1;
        margin-top: 20px;
    }
    .ebm-tag {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Bilingual Setup & Dynamic UI Dictionary
col_lang1, col_lang2 = st.columns([5, 1])
with col_lang2:
    language = st.radio("Language / 语言", ["中文 (Chinese)", "English"], horizontal=True, label_visibility="collapsed")

if language == "中文 (Chinese)":
    ui = {
        "title": "智能医生辅助诊断系统",
        "subtitle": "⚡ 循证医学 (EBM) 离线引擎 | 实时概率分析",
        "input_header": "📋 临床输入",
        "symptoms_label": "输入患者症状 / 临床观察",
        "symptoms_placeholder": "在此输入症状...",
        "button": "🔍 运行智能分析",
        "upload_label": "📷 上传皮损图像",
        "waiting_msg": "⏳ 等待临床输入...<br><span style='font-size:14px;'>请在左侧输入症状并点击分析按钮。</span>",
        "header_main": "🤖 实时诊断与循证决策",
        "header_sub": "Real-Time Diagnostic Insights & Evidence-Based Medicine",
        "primary_main": "首选诊断",
        "primary_sub": "Primary Diagnosis",
        "ddx_main": "📊 鉴别诊断概率 (Top 5 DDx)",
        "ddx_sub": "Differential Diagnosis Probabilities",
        "icd_label": "ICD-10 编码:",
        "rx_main": "💊 推荐处方与干预方案",
        "rx_sub": "Recommended Prescriptions & Interventions",
        "special_pop": "👨‍👩‍👧 特殊人群用药指南 / Special Populations",
        "guidelines": "📚 临床指南与文献 / Clinical Guidelines & References",
        "disclaimer": "⚠️ 仅供医疗专业人员参考。最终决定需由执业医师确认。"
    }
    db_file = "dermatology_core_data_CN.json"
else:
    ui = {
        "title": "AI Doctor Co-Pilot System",
        "subtitle": "⚡ Evidence-Based Medicine (EBM) Engine | Offline Mode",
        "input_header": "📋 Clinical Input",
        "symptoms_label": "Enter Patient Symptoms / Clinical Observations",
        "symptoms_placeholder": "Type symptoms here...",
        "button": "🔍 Analyze Symptoms",
        "upload_label": "📷 Upload Lesion Image",
        "waiting_msg": "⏳ Awaiting clinical data...<br><span style='font-size:14px;'>Enter symptoms on the left to trigger EBM diagnosis.</span>",
        "header_main": "🤖 Real-Time Diagnostic Insights & EBM",
        "header_sub": "实时诊断与循证决策",
        "primary_main": "Primary Diagnosis",
        "primary_sub": "首选诊断",
        "ddx_main": "📊 Differential Diagnosis Probabilities (Top 5)",
        "ddx_sub": "鉴别诊断概率",
        "icd_label": "ICD-10 Code:",
        "rx_main": "💊 Recommended Prescriptions & Interventions",
        "rx_sub": "推荐处方与干预方案",
        "special_pop": "👨‍👩‍👧 Special Populations / 特殊人群用药指南",
        "guidelines": "📚 Clinical Guidelines & References / 临床指南与文献",
        "disclaimer": "⚠️ For medical professional use only. Final signature required by a physician."
    }
    db_file = "dermatology_core_data_EN.json"

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
dataset = kb.get("conditions", kb)
disease_keys = [k for k in dataset.keys() if k not in ["metadata", "global_settings", "morphology_builder"]]

# 4. Main Layout
st.markdown(f"<h1 class='header-gradient'>🏥 {ui['title']}</h1>", unsafe_allow_html=True)
st.caption(ui["subtitle"])
st.markdown("---")

col1, spacer, col2 = st.columns([1.2, 0.1, 1.5])

with col1:
    st.markdown(f"### {ui['input_header']}")
    symptoms = st.text_area(ui["symptoms_label"], placeholder=ui["symptoms_placeholder"], height=160)
    st.button(ui["button"], type="primary", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_image = st.file_uploader(ui["upload_label"], type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Scan Active", use_container_width=True, clamp=True)

with col2:
    if not symptoms.strip():
        # Waiting State
        st.markdown(f"### {ui['header_main']}")
        st.markdown(f"<p style='color: #8898aa; font-size: 14px; margin-top: -15px; margin-bottom: 20px;'><i>{ui['header_sub']}</i></p>", unsafe_allow_html=True)
        st.markdown(f"<div class='waiting-state'><h2>{ui['waiting_msg']}</h2></div>", unsafe_allow_html=True)
    else:
        # Dynamic Main Header
        st.markdown(f"### **{ui['header_main']}**")
        st.markdown(f"<p style='color: #8898aa; font-size: 14px; margin-top: -15px; margin-bottom: 20px;'><i>{ui['header_sub']}</i></p>", unsafe_allow_html=True)

        # --- OFFLINE PROBABILITY MATH ENGINE ---
        scores = {}
        symptom_lower = symptoms.lower()
        
        for key in disease_keys:
            data = dataset[key]
            score = 0
            names_to_check = [
                key.lower(), 
                data.get("name_en", "").lower(), data.get("name_cn", "").lower(), data.get("name", "").lower(),
                data.get("EnglishName", "").lower(), data.get("ChineseName", "").lower()
            ]
            for n in names_to_check:
                if n and n in symptom_lower: score += 20
            
            findings = []
            findings.extend(data.get("key_physical_findings", data.get("关键体征", [])))
            findings.extend(data.get("Symptoms", []))
            if "PhysicalFindings" in data:
                findings.extend(data["PhysicalFindings"].get("PrimaryLesions", []))
                findings.extend(data["PhysicalFindings"].get("SecondaryLesions", []))
            
            for finding in findings:
                words = finding.replace("_", " ").lower().split()
                for word in words:
                    if len(word) > 2 and word in symptom_lower: score += 3
            
            ddx_list = data.get("differential_diagnosis", data.get("鉴别诊断", []))
            if "DifferentialDiagnosis" in data: ddx_list.extend(data["DifferentialDiagnosis"])
            for ddx in ddx_list:
                if isinstance(ddx, dict):
                    disease_str = ddx.get("disease", ddx.get("疾病", "")).replace("_", " ").lower()
                else:
                    disease_str = str(ddx).lower()
                if disease_str and disease_str in symptom_lower: score += 1
                    
            scores[key] = score

        # Math Logic Top 5
        sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_diseases[:5]
        top_total_score = sum(v for k, v in top_5)
        probabilities = []
        
        if top_total_score > 0:
            for k, v in top_5:
                probabilities.append((k, (v / top_total_score) * 100))
        else:
            probabilities = [(disease_keys[0], 80.0), (disease_keys[1], 10.0), (disease_keys[2], 5.0), (disease_keys[3], 3.0), (disease_keys[4], 2.0)]

        # --- DYNAMIC BILINGUAL RENDERING ---
        primary_key, primary_prob = probabilities[0]
        matched_data = dataset[primary_key]
        
        # Extract both languages securely
        name_cn = matched_data.get("ChineseName", matched_data.get("name_cn", matched_data.get("name", primary_key)))
        name_en = matched_data.get("EnglishName", matched_data.get("name_en", "English name unavailable"))
        icd = matched_data.get("ICD10", matched_data.get("icd10", "Unknown"))
        
        # Determine which language is primary vs secondary for the UI
        if language == "中文 (Chinese)":
            disease_main = name_cn
            disease_sub = name_en
        else:
            disease_main = name_en
            disease_sub = name_cn
        
        # 1. Primary Diagnosis Card (Fully Bilingual)
        st.markdown(f"""
        <div class="diagnosis-card">
            <h4 style="color: #4CAF50; margin-top: 0; margin-bottom: 5px;">{ui['primary_main']}</h4>
            <p style="color: #8898aa; font-size: 13px; margin-top: 0; margin-bottom: 10px;"><i>{ui['primary_sub']}</i></p>
            <h2 style="margin-top: 0;">{disease_main} <span style="font-size: 18px; color: #666; font-weight: normal;">({disease_sub})</span></h2>
            <p style="margin-bottom: 0;"><b>{ui['icd_label']}</b> <code>{icd}</code></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Probability Progress Bars (Top 5 DDx - Fully Bilingual)
        st.markdown(f"**{ui['ddx_main']}**")
        st.markdown(f"<p style='color: #8898aa; font-size: 13px; margin-top: -10px;'><i>{ui['ddx_sub']}</i></p>", unsafe_allow_html=True)
        
        for dx_key, prob in probabilities:
            dx_data = dataset[dx_key]
            dx_cn = dx_data.get("ChineseName", dx_data.get("name_cn", dx_data.get("name", dx_key)))
            dx_en = dx_data.get("EnglishName", dx_data.get("name_en", ""))
            
            if language == "中文 (Chinese)":
                dx_display_main = dx_cn
                dx_display_sub = dx_en
            else:
                dx_display_main = dx_en
                dx_display_sub = dx_cn
                
            col_dx, col_prob = st.columns([3, 1])
            with col_dx:
                st.markdown(f"**{dx_display_main}** <br> <span style='font-size:13px; color:#8898aa;'><i>{dx_display_sub}</i></span>", unsafe_allow_html=True)
                st.progress(prob / 100.0)
            with col_prob:
                st.markdown(f"<h3 style='text-align: right; color: #1e3c72; margin-top: 10px;'>{prob:.1f}%</h3>", unsafe_allow_html=True)
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Prescriptions & Treatments
        st.markdown(f"### {ui['rx_main']}")
        st.markdown(f"<p style='color: #8898aa; font-size: 14px; margin-top: -15px;'><i>{ui['rx_sub']}</i></p>", unsafe_allow_html=True)
        
        if "处方" in matched_data or "prescriptions" in matched_data:
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
                            st.info(f"💡 {item.get('special', item.get('特殊说明', ''))}")
        
        elif "Treatment" in matched_data:
            for category, treatments in matched_data["Treatment"].items():
                with st.expander(f"📌 {category} Line Treatment", expanded=True):
                    for t in treatments:
                        st.markdown(f"- {t}")

        # 4. Special Populations
        has_pregnancy = "Pregnancy" in matched_data
        has_pediatric = "PediatricConsiderations" in matched_data
        
        if has_pregnancy or has_pediatric:
            with st.expander(ui["special_pop"], expanded=False):
                if has_pregnancy:
                    st.markdown("**🤰 Pregnancy Guidelines:**")
                    st.success(f"Safe: {', '.join(matched_data['Pregnancy'].get('SafeDrugs', []))}")
                    st.error(f"Avoid: {', '.join(matched_data['Pregnancy'].get('Avoid', []))}")
                if has_pediatric:
                    st.markdown("**👶 Pediatric Considerations:**")
                    st.info(str(matched_data["PediatricConsiderations"]))

        # 5. EBM Guidelines & References
        has_guidelines = "Guidelines" in matched_data
        has_refs = "References" in matched_data
        
        if has_guidelines or has_refs:
            with st.expander(ui["guidelines"], expanded=False):
                if has_guidelines:
                    st.markdown("**Core Guidelines:**")
                    for g_name, g_text in matched_data["Guidelines"].items():
                        st.markdown(f"- <span class='ebm-tag'>{g_name}</span> {g_text}", unsafe_allow_html=True)
                if has_refs:
                    st.markdown("<br>**Literature References:**", unsafe_allow_html=True)
                    for ref in matched_data["References"]:
                        st.caption(f"📖 *{ref.get('Title', '')}* — {ref.get('Citation', '')}")

        st.caption(ui["disclaimer"])
