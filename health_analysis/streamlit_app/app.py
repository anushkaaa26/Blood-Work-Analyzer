import os
import sys
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Force standard protobuf implementation for stability on cloud reboots
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page Configuration with Medical Branding
st.set_page_config(
    page_title="Hana | Blood Work Analyzer", 
    page_icon="🩸",
    layout="wide"
)

# Custom Theme Variables for a Premium Dark/Modern Aesthetic
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }
    .subtitle {
        color: #A0AEC0;
        font-size: 1.1rem;
        margin-bottom: 2.5rem !important;
    }
    div[data-testid="stExpander"] {
        border-radius: 10px !important;
        background-color: #1A202C !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: Context & Compliance ---
with st.sidebar:
    st.markdown("### 🧬 About Hana")
    st.write("This AI-powered assistant extracts clinical markers from raw laboratory text and maps them directly to actionable lifestyle adjustments and traditional dietary wisdom.")
    
    st.markdown("---")
    st.caption("⚠️ **Clinical Disclaimer:** This tool is for educational and wellness tracking purposes only. It does not replace professional medical advice, diagnosis, or treatment plans.")

# --- MAIN HEADER ---
st.markdown('<h1 class="main-title">🩸 Hana</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Driven Biomarker Extraction & Personalized Indian Nutrition Mapping</p>', unsafe_allow_html=True)

llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("📋 Patient Report Entry")
    
    # UI Upgrade: One-click Sample Injector for easier testing/demonstrations
    with st.expander("💡 Need a sample report to test?"):
        sample_text = (
            "CBC REPORT\n"
            "Hemoglobin: 11.2 g/dL | Reference: 13.0 - 17.0 (LOW)\n"
            "Total WBC Count: 7,500 /uL | Reference: 4,000 - 11,000 (NORMAL)\n"
            "Vitamin D3: 18 ng/mL | Reference: 30.0 - 100.0 (HIGHLY DEFICIENT)\n"
            "Serum Cholesterol: 245 mg/dL | Reference: < 200 (HIGH)"
        )
        st.code(sample_text, language="text")
        if st.button("Inject Sample Data", use_container_width=True):
            st.session_state["blood_report_input"] = sample_text
            st.rerun()

    # Bind text area to session state so the injector button works cleanly
    if "blood_report_input" not in st.session_state:
        st.session_state["blood_report_input"] = ""

    blood_report = st.text_area(
        label="Paste your report below",
        height=350,
        value=st.session_state["blood_report_input"],
        placeholder="Paste your raw laboratory data text here (including reference metrics)...",
        label_visibility="collapsed"
    )
    
    analyze_clicked = st.button("🚀 Run Diagnostic Review", type="primary", use_container_width=True)

with right_col:
    st.subheader("📊 Analytical Insights")
    
    # UI Upgrade: Modern dynamic tabs instead of stacked boxes
    tab1, tab2 = st.tabs(["❤️ Health Summary", "🥗 Tailored Indian Diet Plan"])
    
    with tab1:
        health_container = st.container(border=True)
        health_placeholder = health_container.empty()
        health_placeholder.info("Awaiting report submission. The summary of physiological markers will populate here.")
        
    with tab2:
        diet_container = st.container(border=True)
        diet_placeholder = diet_container.empty()
        diet_placeholder.info("Awaiting report submission. Customized dietary guardrails will populate here.")

# --- CORE EXECUTION LOGIC (100% Unchanged) ---
if analyze_clicked:
    if not blood_report.strip():
        with left_col:
            st.error("⚠️ Please input laboratory parameters before initiating analysis.")
    else:
        with st.spinner("🔬 Deconstructing biomarkers and computing dietary correlations..."):

            # Stage 1: Extract and flag abnormal values (Logic Unchanged)
            extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL
based on the reference ranges provided in the report.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{blood_report}
"""
            extraction_response = llm.invoke(extraction_prompt)
            extracted_values = extraction_response.text

            # Stage 2: Health summary and Indian diet plan (Logic Unchanged)
            diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, provide two clearly separated sections:

SECTION 1 - HEALTH SUMMARY:
Write 4-5 lines explaining the patient's condition in simple, non-technical language.

SECTION 2 - INDIAN DIET PLAN:
List foods to eat more of and foods to avoid, using commonly available Indian foods
like dal, sabzi, roti, rice, etc. Keep it practical and concise.

Blood Work Analysis:
{extracted_values}
"""
            diet_response = llm.invoke(diet_prompt)
            full_response = diet_response.text

        # Parsing logic (Logic Unchanged)
        if "SECTION 2" in full_response:
            parts = full_response.split("SECTION 2")
            health_summary = parts[0].replace("SECTION 1 - HEALTH SUMMARY:", "").replace("SECTION 1", "").strip()
            diet_plan = ("SECTION 2" + parts[1]).replace("SECTION 2 - INDIAN DIET PLAN:", "").replace("SECTION 2", "").strip()
        else:
            health_summary = full_response
            diet_plan = ""

        # UI Upgrade Render: Beautiful native markdown directly inside our tab system
        health_placeholder.markdown(health_summary)
        diet_placeholder.markdown(diet_plan if diet_plan else full_response)
