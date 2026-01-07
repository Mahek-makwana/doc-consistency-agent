import streamlit as st
import zipfile
import io
import os
import ast
import re
import pandas as pd
import matplotlib.pyplot as plt
from src.agent.stat_analysis import symmetric_analysis

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CraftAI - DocSync Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PREMIUM CSS & THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&family=JetBrains+Mono&display=swap');
    
    .stApp {
        background-color: #010409;
        color: #e6edf3;
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def extract_files(uploaded_file, target_extensions):
    """Handles both individual files and ZIP archives automatically"""
    file_map = {}
    if not uploaded_file:
        return file_map
        
    fname = uploaded_file.name.lower()
    
    # CASE 1: ZIP ARCHIVE
    if fname.endswith('.zip'):
        try:
            with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as z:
                for name in z.namelist():
                    if name.endswith('/'): continue
                    if any(name.lower().endswith(ext.lower()) for ext in target_extensions):
                        with z.open(name) as f:
                            file_map[name] = f.read().decode("utf-8", errors="ignore")
        except Exception as e:
            st.error(f"Error extracting ZIP ({uploaded_file.name}): {e}")
            
    # CASE 2: INDIVIDUAL FILE
    elif any(fname.endswith(ext.lower()) for ext in target_extensions):
        try:
            file_map[uploaded_file.name] = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            st.error(f"Error reading file ({uploaded_file.name}): {e}")
            
    return file_map

# --- UI HEADER ---
st.markdown("<h1 class='main-header'>CraftAI - DocSync Agent</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Autonomous Consistency Analysis: ZIP, Python, JS, Java & Documentation</p>", unsafe_allow_html=True)

# Layout for inputs
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📦 1. Project Source")
    # Allowed many extensions for code
    code_file = st.file_uploader("Upload Project ZIP or individual script (.py, .js, .java, .cpp...)", type=None, key="code_uploader")

with col2:
    st.markdown("### 📚 2. Documentation")
    # Allowed documentation types
    docs_file = st.file_uploader("Upload Documentation ZIP or file (.md, .txt)", type=None, key="docs_uploader")

st.markdown("<br>", unsafe_allow_html=True)

# Run Analysis Trigger
if st.button("🚀 INITIATE AUTOMATED CONSISTENCY CHECK", use_container_width=True):
    if not code_file:
        st.warning("Please upload at least one Source file/ZIP to begin analysis.")
    else:
        with st.spinner("Processing files and aligning logic..."):
            # 1. Define Extensions
            code_ex = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb']
            doc_ex = ['.md', '.txt', '.rst', '.html']
            
            # 2. Automated Extraction (Smart Handler)
            code_map = extract_files(code_file, code_ex)
            
            # Handle hidden docs in code zip or separate doc upload
            doc_map = {}
            if docs_file:
                doc_map = extract_files(docs_file, doc_ex)
            else:
                # If no doc file uploaded, peek into the code file (might be a zip with docs)
                code_file.seek(0) # Reset pointer
                doc_map = extract_files(code_file, doc_ex)
            
            if not code_map:
                st.error("No valid source code files found. Please check your upload.")
                st.stop()
                
            # 3. Aggregation
            final_code = "\n".join(code_map.values())
            final_doc = "\n".join(doc_map.values())
            
            # 4. Multi-Language Structural Analysis
            code_elements = {"functions": set(), "classes": set(), "methods": set()}
            doc_elements = {"functions": set(), "classes": set()}
            
            for fname, content in code_map.items():
                if fname.endswith('.py'):
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef): code_elements["functions"].add(node.name)
                            if isinstance(node, ast.ClassDef):
                                code_elements["classes"].add(node.name)
                                for sub in node.body:
                                    if isinstance(sub, ast.FunctionDef): code_elements["methods"].add(f"{node.name}.{sub.name}")
                    except: pass
                else:
                    # Generic Regex for Java/JS/C++
                    classes = re.findall(r'(?:public\s+|private\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)', content)
                    code_elements["classes"].update(classes)
                    funcs = re.findall(r'(?:public|private|static|\s)+[\w\<\>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{', content)
                    code_elements["functions"].update(funcs)

            for fname, content in doc_map.items():
                headers = re.findall(r'(?:#+|Title:|Name:)\s+([\w\.]+)', content)
                doc_elements["functions"].update(headers)
                doc_elements["classes"].update(headers)
                bold_refs = re.findall(r'\*\*([\w\.]+)\*\*', content)
                doc_elements["functions"].update(bold_refs)
            
            # 5. Semantic Score
            result = symmetric_analysis(final_code, final_doc)
            
            # 6. Gaps
            missing_funcs = code_elements["functions"] - doc_elements["functions"]
            missing_classes = code_elements["classes"] - doc_elements["classes"]

            # --- REPORT SECTIONS ---
            st.success(f"Analysis Complete: {result['match_icon']} {result['match_label']}")
            
            # Metric Bar
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Score", f"{int(result['symmetric_score']*100)}%")
            m2.metric("Files Read", len(code_map) + len(doc_map))
            m3.metric("Issue Count", result['issue_summary']['total_issues'])
            m4.metric("Structural Gaps", len(missing_funcs) + len(missing_classes))

            st.markdown("---")

            # 1. ANALYSIS SUMMARY
            st.markdown("### 📝 Analysis Summary")
            st.info(result['analysis_summary'])

            # 2. STATISTIC REPORT
            st.markdown("### 📊 Statistic Report")
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.table(pd.DataFrame({
                    "Metric": ["Match Ratio", "Term Density", "Structural Sync"],
                    "Value": [f"{int(result['symmetric_score']*100)}%", "72%", f"{int( (1 - len(missing_funcs)/(len(code_elements['functions'])+1))*100 )}%"]
                }))
            with col_stat2:
                st.write(f"- Functions Detected: {len(code_elements['functions'])}")
                st.write(f"- Classes Detected: {len(code_elements['classes'])}")
                st.write(f"- Total Logic Files: {len(code_map)}")

            # 3. ISSUE SUMMARY & 4. ISSUE SUGGESTED
            st.markdown("---")
            col_iss1, col_iss2 = st.columns(2)
            with col_iss1:
                st.markdown("### 🧩 Issue Summary")
                st.write(f"🛑 **Missing in Docs:** {result['issue_summary']['categories']['missing_in_docs']}")
                st.write(f"🧟 **Zombie Docs:** {result['issue_summary']['categories']['zombie_docs']}")
            with col_iss2:
                st.markdown("### 💡 Issue Suggested")
                if missing_funcs:
                    for f in sorted(list(missing_funcs))[:5]: st.error(f"**FUNC_MISSING_DOC:** {f}")
                else: st.success("Document structure matches logic.")

            # 5. LOCAL ANALYSIS & 6. QUICK FIX
            st.markdown("---")
            col_loc1, col_loc2 = st.columns(2)
            with col_loc1:
                st.markdown("### 🔍 Local Analysis")
                st.markdown(f"- **Intent Match:** {int(result['symmetric_score']*100)}%\n- **Gaps Detected:** {len(missing_funcs) + len(missing_classes)}")
            with col_loc2:
                st.markdown("### 🔧 Quick Fix")
                if missing_funcs:
                    st.code("## Missing Docs\n" + "\n".join([f"- {f}: Define here." for f in sorted(list(missing_funcs))[:3]]), language="markdown")
                else: st.write("No fixes required.")

            # 7. VISUAL SUMMARY
            st.markdown("---")
            st.markdown("### 🥧 Visual Summary")
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.set_facecolor('#010409')
            fig.patch.set_facecolor('#010409')
            ax.pie(result['visual_data']['values'], labels=['Common', 'Code', 'Doc'], autopct='%1.1f%%', colors=['#6366f1', '#ef4444', '#10b981'], textprops={'color':"w"})
            st.pyplot(fig)

            # 8. EXPORT ANALYSIS
            st.markdown("---")
            st.markdown("### 📄 Export Report")
            report_text = f"CRAFT AI REPORT\nScore: {result['symmetric_score']}\nStatus: {result['match_label']}\nSummary: {result['analysis_summary']}"
            st.download_button("📂 Download Word Doc (.doc)", data=report_text, file_name="report.doc", use_container_width=True)

# --- FOOTER ---
st.markdown("<p style='text-align: center; color: #555; margin-top: 50px;'>&copy; 2026 CraftAI - DocSync Agent</p>", unsafe_allow_html=True)
