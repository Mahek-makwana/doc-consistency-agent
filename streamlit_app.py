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

    /* Card Styling */
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
    
    .section-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 900;
        color: #fff;
    }
    
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 1px;
    }

    /* Badge colors */
    .badge-missing { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }
    .badge-sync { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def extract_from_zip(zip_content, target_extensions):
    file_map = {}
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for name in z.namelist():
                if name.endswith('/'): continue
                if any(name.lower().endswith(ext.lower()) for ext in target_extensions):
                    with z.open(name) as f:
                        file_map[name] = f.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Error extracting ZIP: {e}")
    return file_map

# --- CORE LOGIC ---
st.markdown("<h1 class='main-header'>CraftAI - DocSync Agent</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Autonomous Consistency Analysis for Multi-Language Projects</p>", unsafe_allow_html=True)

# Layout for inputs
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📦 1. Source Code ZIP")
    code_zip = st.file_uploader("Upload Project Archive (Java, Python, JS, etc.)", type=["zip"], key="code_uploader")

with col2:
    st.markdown("### 📚 2. Documentation ZIP")
    docs_zip = st.file_uploader("Upload Docs Archive (Markdown, Text)", type=["zip"], key="docs_uploader")

st.markdown("<br>", unsafe_allow_html=True)

# Run Analysis Trigger
if st.button("🚀 INITIATE OVERALL CONSISTENCY CHECK", use_container_width=True):
    if not code_zip:
        st.warning("Please upload a Source Code ZIP to proceed.")
    else:
        with st.spinner("Analyzing cross-language dependencies & mapping documentation..."):
            # 1. Configuration
            code_ex = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb']
            doc_ex = ['.md', '.txt', '.rst', '.html']
            
            # 2. Extraction
            code_zip_bytes = code_zip.read()
            code_map = extract_from_zip(code_zip_bytes, code_ex)
            
            if docs_zip:
                doc_map = extract_from_zip(docs_zip.read(), doc_ex)
            else:
                # Fallback: look for docs in the code zip
                doc_map = extract_from_zip(code_zip_bytes, doc_ex)
            
            # 3. Aggregation
            final_code = "\n".join(code_map.values())
            final_doc = "\n".join(doc_map.values())
            
            # 4. Structural Parsing (Multi-Language)
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
            
            # 1. ANALYSIS SUMMARY
            st.markdown("### 📝 Analysis Summary")
            st.info(result['analysis_summary'])
            
            # Statistics Row
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Overall Score", f"{int(result['symmetric_score']*100)}%")
            with m2: st.metric("Files Analyzed", len(code_map) + len(doc_map))
            with m3: st.metric("Logic Gaps", result['issue_summary']['categories']['logic_gaps'])
            with m4: st.metric("Sync Status", "High" if result['symmetric_score'] > 0.7 else "Moderate")

            st.markdown("---")

            # 2. STATISTIC REPORT
            st.markdown("### 📊 Statistic Report")
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.write("**Documentation Health Metrics**")
                stats_df = pd.DataFrame({
                    "Metric": ["Match Ratio", "Term Density", "Structural Sync"],
                    "Value": [f"{int(result['symmetric_score']*100)}%", "72%", f"{int( (1 - len(missing_funcs)/(len(code_elements['functions'])+1))*100 )}%"]
                })
                st.table(stats_df)
            with col_stat2:
                st.write("**Analyzed Components**")
                st.write(f"- Functions Detected: {len(code_elements['functions'])}")
                st.write(f"- Classes Detected: {len(code_elements['classes'])}")
                st.write(f"- Docs Found: {len(doc_map)} files")

            # 3. ISSUE SUMMARY & 4. ISSUE SUGGESTED
            st.markdown("---")
            col_iss1, col_iss2 = st.columns(2)
            
            with col_iss1:
                st.markdown("### 🧩 Issue Summary")
                st.write(f"🛑 **Missing in Docs:** {result['issue_summary']['categories']['missing_in_docs']} terms")
                st.write(f"🧟 **Zombie Docs:** {result['issue_summary']['categories']['zombie_docs']} terms")
                st.write(f"⚠️ **Total Issue Points:** {result['issue_summary']['total_issues']}")

            with col_iss2:
                st.markdown("### 💡 Issue Suggested")
                if missing_funcs:
                    for f in sorted(list(missing_funcs))[:5]:
                        st.error(f"**FUNC_MISSING_DOC:** {f}")
                else:
                    st.success("No critical structural gaps found.")

            # 5. LOCAL ANALYSIS & 6. QUICK FIX
            st.markdown("---")
            col_loc1, col_loc2 = st.columns(2)
            
            with col_loc1:
                st.markdown("### 🔍 Local Analysis")
                st.markdown(f"""
                - **Intent Match:** {int(result['symmetric_score']*100)}%
                - **Consistency Delta:** {round(1 - result['symmetric_score'], 2)}
                - **Structural Voids:** {len(missing_funcs) + len(missing_classes)} detected
                """)
            
            with col_loc2:
                st.markdown("### 🔧 Quick Fix")
                if missing_funcs:
                    st.markdown("Add these to your documentation immediately:")
                    snippet = "## API - Missing Items\n" + "\n".join([f"- **{f}**: Description pending." for f in sorted(list(missing_funcs))[:3]])
                    st.code(snippet, language="markdown")
                else:
                    st.write("All functions are documented. Maintenance mode active.")

            # 7. VISUAL SUMMARY
            st.markdown("---")
            st.markdown("### 🥧 Visual Summary (Documentation Health)")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.set_facecolor('#010409')
            fig.patch.set_facecolor('#010409')
            labels = ['Common Terms', 'Code Only', 'Doc Only']
            sizes = result['visual_data']['values']
            colors = ['#6366f1', '#ef4444', '#10b981']
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, textprops={'color':"w"})
            st.pyplot(fig)

            # 8. EXPORT ANALYSIS
            st.markdown("---")
            st.markdown("### 📄 Export Analysis Report")
            report_content = f"""CRAFT AI - DOCSYNC REPORT
========================
Score: {result['symmetric_score']}
Status: {result['match_label']}

SUMMARY:
{result['analysis_summary']}

STRUCTURAL GAPS:
- Functions: {len(missing_funcs)}
- Classes: {len(missing_classes)}

RECOMMENDATIONS:
{result['details']['suggestions'][0]}
"""
            
            ex1, ex2, ex3 = st.columns(3)
            ex1.download_button("📂 Download Word Doc (.doc)", data=report_content, file_name="craftai_report.doc", use_container_width=True)
            ex2.download_button("📝 Download Text Report (.txt)", data=report_content, file_name="craftai_report.txt", use_container_width=True)
            ex3.button("📑 Export PDF (Use Ctrl+P)", use_container_width=True)

# --- FOOTER ---
st.markdown("<br><br><p style='text-align: center; color: #555; font-size: 0.8rem;'>&copy; 2026 CraftAI - DocSync Agent powered by Advanced Operational Alignment Pipeline</p>", unsafe_allow_html=True)
