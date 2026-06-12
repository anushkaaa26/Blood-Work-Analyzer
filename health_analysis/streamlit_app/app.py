import os
import sys
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Force standard protobuf implementation for stability on cloud reboots
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page Configuration - Clean & Professional
st.set_page_config(
    page_title="Blood Work Analyzer", 
    page_icon="🩸",
    layout="wide"
)

# Custom Enterprise-grade UI Styling
st.markdown("""
<style>
    /* Global font sizing and cleaner text spacing */
    .reportview-container .main .block-container {
        padding-top: 2rem !important;
    }
    .header-title {
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        color: #FFFFFF;
        margin-bottom: 0.2rem !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-subtitle {
        color: #718096;
        font-size: 1rem;
        margin-bottom: 2rem !important;
    }
    /* Polish text area container */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #3F444E !important;
        background-color: #1A1D24 !important;
        color: #E2E8F0 !important;
    }
    /* Polish tab headers */
    button[data-baseweb="tab"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: Clinical Guardrails & Context ---
with st.sidebar:
    st.markdown("### 📋 System Instructions")
    st.info(
        "1. Paste the raw text copy of a pathology lab report into the entry panel.\n"
        "2. Ensure numerical results and baseline reference intervals are visible.\n"
        "3. Click 'Run Analysis' to initialize data parsing."
    )
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** This automated engine provides biomarker mapping and nutritional insights for educational purposes only. Results must be verified by a qualified healthcare professional.")

# --- CLEAN HEADER ---
st.markdown('<div class="header-title">🩸 Blood Work Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Clinical Biomarker Parsing & Tailored Indian Nutritional Frameworks</div>', unsafe_allow_html=True)

llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it")

# Two-column dynamic split
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown("### 📥 Input Report Data")
    
    # Minimalist Sample Data Option
    with st.expander("📝 Load Sample Laboratory Data (For Testing)"):
        sample_text = (
            "COMPLETE BLOOD COUNT & METABOLIC PANEL\n"
            "Hemoglobin: 11.2 g/dL | Reference: 13.0 - 17.0 (LOW)\n"
            "Total WBC Count: 7,500 /uL | Reference: 4,000 - 11,000 (NORMAL)\n"
            "Vitamin D3: 18 ng/mL | Reference: 30.0 - 100.0 (DEFICIENT)\n"
            "Serum Cholesterol: 245 mg/dL | Reference: < 200 (HIGH)"
        )
        st.text(sample_text)
        if st.button("Populate Input Field", use_container_width=True):
            st.session_state["blood_report_input"] = sample_text
            st.rerun()

    # Session state handling for input continuity
    if "blood_report_input" not in st.session_state:
        st.session_state["blood_report_input"] = ""

    blood_report = st.text_area(
        label="Paste your report data",
        height=380,
        value=st.session_state["blood_report_input"],
        placeholder="Paste plain text lab data here...",
        label_visibility="collapsed"
    )
    
    analyze_clicked = st.button("⚙️ Run Analysis", type="primary", use_container_width=True)

with right_col:
    st.markdown("### 📊 Generated Assessment")
    
    # Clean, distraction-free UI tabs
    tab1, tab2 = st.tabs(["Clinical Summary", "Dietary Strategy"])
    
    with tab1:
        health_container = st.container(border=True)
        health_placeholder = health_container.empty()
        health_placeholder.caption("Awaiting data input. Physiological summaries will populate here.")
        
    with tab2:
        diet_container = st.container(border=True)
        diet_placeholder = diet_container.empty()
        diet_placeholder.caption("Awaiting data input. Practical Indian food guidelines will populate here.")

# --- ENGINE EXECUTION LOGIC (100% Unchanged) ---
if analyze_clicked:
    if not blood_report.strip():
        with left_col:
            st.error("Please insert laboratory text data before analyzing.")
    else:
        with st.spinner("Processing biomarkers and matching nutritional indices..."):

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

        # UI Rendering directly into the clean tabs
        health_placeholder.markdown(health_summary)
        diet_placeholder.markdown(diet_plan if diet_plan else full_response)
