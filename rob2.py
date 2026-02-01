import streamlit as st
import ollama
import json
import pandas as pd
import io
from PyPDF2 import PdfReader

# --- Page Configuration ---
st.set_page_config(page_title="RoB-2 automated ratings", page_icon="💊", layout="wide")

# --- Function to Fetch Local Models ---
def get_local_models():
    try:
        client = ollama.Client() 
        models_info = client.list()
        model_names = []
        if 'models' in models_info:
            # Compatibility check for different Ollama versions
            model_names = [m.get('name') or m.get('model') for m in models_info['models']]
        
        if model_names:
            return sorted(model_names)
        return []
    except Exception as e:
        return []

# --- UI Header ---
st.title("🔬 RoB-2 Expert Batch Extractor")
st.markdown("Automated Risk of Bias assessment using local LLMs (Ollama).")

# --- Instructions ---
with st.expander("📖 How to use this tool", expanded=True):
    st.markdown("""
    ### Prerequisites
    1. **Install Ollama:** [ollama.com](https://ollama.com).
    2. **Get Models:** Run `ollama pull llama3.1:8b` (or higher) in your terminal.
    3. **Service:** Keep the Ollama application active in the background.

    ### Steps
    1. **Select Model:** Choose your installed model in the sidebar.
    2. **Upload PDFs:** Drag and drop clinical trial PDFs.
    3. **Process:** Each study is analyzed individually. The system will retry up to 3 times if data is missing.
    """)

# --- Sidebar Settings ---
with st.sidebar:
    st.header("Configuration")
    
    # Unique key added to prevent DuplicateElementId error
    if st.button("🔄 Refresh Models", key="refresh_sidebar"):
        st.rerun()
    
    actual_models = get_local_models()
    academic_recommendations = ["llama3.1:70b", "command-r", "qwen2.5:7b", "llama3.1:8b", "gemma:2b"]
    
    if actual_models:
        options = actual_models + ["Other (Type name...)"]
        st.success(f"Connected! {len(actual_models)} models found.")
    else:
        options = academic_recommendations + ["Other (Type name...)"]
        st.warning("⚠️ No local models detected. Is Ollama running?")

    selected_option = st.selectbox("Select Local Model", options=options)
    
    if selected_option == "Other (Type name...)":
        model_name = st.text_input("Enter model name exactly:", value="")
    else:
        model_name = selected_option

    output_format = st.selectbox("Export Format", [".csv", ".xlsx"])
    st.divider()
    st.caption("Privacy: 100% Local processing.")

# --- File Upload ---
uploaded_files = st.file_uploader("Upload Study PDFs", type="pdf", accept_multiple_files=True)

# --- Expert Prompt ---
EXPERT_SYSTEM_PROMPT = """
You are a professional reviewer. You are particularly good at learning evaluation criteria, and closely following it to assess the risk of bias of Randomized Controlled Trials (RCTs). 

IMPORTANT: 
- You must output ONLY a JSON object.
- Make all judgments based on facts. If information is missing, select "Probably no".

JSON Structure:
{
  "D1": {"judgment": "Definitely yes/Probably yes/Probably no/Definitely no", "support": "Reason"},
  "D2": {"judgment": "...", "support": "..."},
  "D3": {"judgment": "...", "support": "..."},
  "D4": {"judgment": "...", "support": "..."},
  "D5": {"judgment": "...", "support": "..."},
  "Overall": {"judgment": "...", "support": "..."}
}
"""

def get_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content: text += content + " "
    return " ".join(text.split())

def safe_map_judgment(res_json, domain):
    data = res_json.get(domain, {})
    if not isinstance(data, dict): return "N/A"
    j = data.get('judgment', 'N/A').lower()
    if "yes" in j or "low" in j: return "Low"
    if "no" in j or "high" in j: return "High"
    if "some" in j: return "Some concerns"
    return "N/A"

# --- Processing Logic ---
if uploaded_files and st.button("Start Batch Processing", key="start_main"):
    all_results = []
    total_files = len(uploaded_files)
    
    progress_text = st.empty()
    retry_status = st.empty()
    progress_bar = st.progress(0)
    
    for index, file in enumerate(uploaded_files):
        current_num = index + 1
        raw_text = get_pdf_text(file)
        study_context = raw_text[:15000] 
        
        success = False
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts and not success:
            attempts += 1
            status_msg = f"Analyzing {file.name} (Attempt {attempts}/{max_attempts})"
            progress_text.text(f"Study {current_num}/{total_files}: {status_msg}")
            
            try:
                response = ollama.generate(
                    model=model_name,
                    prompt=f"{EXPERT_SYSTEM_PROMPT}\n\nArticle Content:\n{study_context}",
                    format="json"
                )
                
                res_json = json.loads(response['response'])
                
                temp_res = {
                    "Study": file.name.replace(".pdf", ""),
                    "D1": safe_map_judgment(res_json, 'D1'),
                    "D2": safe_map_judgment(res_json, 'D2'),
                    "D3": safe_map_judgment(res_json, 'D3'),
                    "D4": safe_map_judgment(res_json, 'D4'),
                    "D5": safe_map_judgment(res_json, 'D5'),
                    "Overall": safe_map_judgment(res_json, 'Overall'),
                    "Full_JSON": res_json
                }
                
                # Check for N/As in domains
                has_na = any(temp_res[k] == "N/A" for k in ["D1", "D2", "D3", "D4", "D5", "Overall"])
                
                if not has_na:
                    all_results.append(temp_res)
                    success = True
                    retry_status.empty()
                else:
                    if attempts < max_attempts:
                        retry_status.warning(f"⚠️ Incomplete data for {file.name}. Retrying...")
                    else:
                        all_results.append(temp_res)
                        retry_status.error(f"❌ Could not retrieve full data for {file.name} after {max_attempts} attempts.")
            
            except Exception as e:
                if attempts >= max_attempts:
                    st.error(f"Error in {file.name}: {e}")
                    break
        
        progress_bar.progress(current_num / total_files)
    
    progress_text.text("Batch processing complete.")
    retry_status.empty()

    if all_results:
        df = pd.DataFrame(all_results)
        view_cols = ["Study", "D1", "D2", "D3", "D4", "D5", "Overall"]
        st.subheader("Results Preview")
        st.dataframe(df[view_cols])

        # --- Downloads ---
        c1, c2 = st.columns(2)
        with c1:
            if output_format == ".csv":
                csv_data = df[view_cols].to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv_data, "rob2_results.csv", "text/csv")
            else:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                    df[view_cols].to_excel(writer, index=False)
                st.download_button("📥 Download Excel", buf.getvalue(), "rob2_results.xlsx")
        
        with c2:
            full_csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📑 Download Full Report (Audit)", full_csv, "rob2_full_audit.csv")

        with st.expander("View Detailed AI Justifications"):
            for res in all_results:
                st.write(f"### {res['Study']}")
                st.json(res['Full_JSON'])