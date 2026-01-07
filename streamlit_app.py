import streamlit as st
import re
import zipfile
import io
import pandas as pd
from typing import Dict, Any, List, Set
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CraftAI DocSync | Enterprise",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background-color: #050505;
        color: #ffffff;
    }
    
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: -2px;
        margin-bottom: 2rem;
        background: linear-gradient(to right, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .metric-value {
        font-size: 3.5rem;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 900;
        text-transform: uppercase;
        color: #6366f1;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- CORE ENGINE ---
class EnterpriseDocSyncEngine:
    def __init__(self):
        self.patterns = {
            "logic": [
                r"def\s+([A-Za-z_]\w*)",
                r"function\s+([A-Za-z_]\w*)",
                r"(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:\(.*\)|function)",
                r"class\s+([A-Za-z_]\w*)",
                r"(['\"]?[\w-]+['\"]?)\s*:",
            ]
        }

    def perform_audit(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        found_logic = set()
        for p in self.patterns["logic"]:
            found_logic.update(re.findall(p, code_text))
        found_logic = {l.strip("'\"") for l in found_logic if len(l) > 2}
        
        comments = " ".join(re.findall(r"(?:#|//|/\*|'''|\"\"\")(.*?)(?:\*/|'''|\"\"\"|\n|$)", code_text, re.DOTALL))
        doc_pool = (doc_text + " " + comments).lower()
        
        if not found_logic:
            return self._empty_result()

        synced = {l for l in found_logic if l.lower() in doc_pool}
        missing = found_logic - synced
        score = int((len(synced) / len(found_logic)) * 100)

        if score == 0:
            issue_detail = f"CRITICAL GAP: The agent detected {len(found_logic)} logic entities, but NONE are described. High risk."
        elif score < 100:
            issue_detail = f"DOCUMENTATION DEBT: {len(missing)} specific entities are missing coverage. Missing: {', '.join(list(missing)[:3])}"
        else:
            issue_detail = "PERFECT ALIGNMENT: Every code entity is explained in the documentation context."

        return {
            "score": score,
            "label": "Accurate Alignment" if score > 70 else "Partial Mismatch" if score > 30 else "Critical Mismatch",
            "summary": f"Audit of {len(found_logic)} elements complete.",
            "detailed_issue": issue_detail,
            "stats": {
                "total_issues": len(missing),
                "synced_terms": len(synced),
            },
            "missing_list": list(missing),
            "visual": [len(synced), len(missing)]
        }

    def _empty_result(self):
        return {"score": 0, "label": "No Logic Detected", "summary": "Empty scan.", "detailed_issue": "REASON: No structural entities found.", "stats": {"total_issues": 0, "synced_terms": 0}, "missing_list": [], "visual": [0, 1]}

engine = EnterpriseDocSyncEngine()

# --- HELPERS ---
def extract_files(uploaded_file, extensions):
    content = ""
    if uploaded_file.name.endswith('.zip'):
        with zipfile.ZipFile(uploaded_file) as z:
            for name in z.namelist():
                if any(name.lower().endswith(ext) for ext in extensions):
                    with z.open(name) as f:
                        content += f.read().decode("utf-8", errors="ignore") + "\n"
    else:
        content = uploaded_file.read().decode("utf-8", errors="ignore")
    return content

# --- INITIALIZE STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#6366f1;'>CraftAI</h1>", unsafe_allow_html=True)
    page = st.radio("Navigation", ["Dashboard", "Audit History", "Settings"])
    st.divider()
    st.info("Enterprise DocSync v2.0")

# --- MAIN VIEW ---
if page == "Dashboard":
    st.markdown("<h1 class='main-header'>DocSync Dashboard</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        code_file = st.file_uploader("1. Project Code (ZIP, PY, JS, etc.)", type=['zip', 'py', 'js', 'ts', 'java', 'cpp', 'cs'])
    with col2:
        doc_file = st.file_uploader("2. Documentation (MD, TXT, RST)", type=['md', 'txt', 'rst', 'zip'])
    
    if st.button("🚀 INITIATE CONSISTENCY AUDIT", use_container_width=True):
        if code_file:
            with st.spinner("Analyzing structural alignment..."):
                code_text = extract_files(code_file, ['.py', '.js', '.ts', '.java', '.cpp', '.cs'])
                doc_text = extract_files(doc_file, ['.md', '.txt', '.rst']) if doc_file else ""
                
                result = engine.perform_audit(code_text, doc_text)
                
                # Save to history
                st.session_state.history.insert(0, {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "project": code_file.name,
                    "score": result['score'],
                    "status": result['label']
                })
                
                # Results Display
                st.divider()
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown(f"""
                        <div class="glass-card">
                            <p class="metric-label">Consistency Score</p>
                            <p class="metric-value">{result['score']}%</p>
                            <p style="color:#6366f1; font-weight:900;">{result['label']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with r2:
                    st.markdown(f"""
                        <div class="glass-card">
                            <p class="metric-label">Structural Stats</p>
                            <p style="font-size:1.5rem; font-weight:900; margin-top:10px;">Synced: <span style="color:#10b981;">{result['stats']['synced_terms']}</span></p>
                            <p style="font-size:1.5rem; font-weight:900;">Issues: <span style="color:#ef4444;">{result['stats']['total_issues']}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with r3:
                    st.markdown(f"""
                        <div class="glass-card">
                            <p class="metric-label">Issue Summary</p>
                            <p style="font-size:0.9rem; color:#9ca3af; margin-top:10px;">{result['detailed_issue']}</p>
                        </div>
                    """, unsafe_allow_html=True)

                if result['missing_list']:
                    st.subheader("⚠️ Documentation Gaps")
                    for item in result['missing_list'][:5]:
                        st.error(f"Missing documentation for entity: `{item}`")
        else:
            st.warning("Please upload a code file to begin.")

elif page == "Audit History":
    st.markdown("<h1 class='main-header'>Audit History</h1>", unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No audit history found.")

elif page == "Settings":
    st.markdown("<h1 class='main-header'>System Settings</h1>", unsafe_allow_html=True)
    st.write("Enterprise configuration options.")
    st.checkbox("Enable AI Auto-Fix", value=True)
    st.checkbox("Deep Context Scanning", value=True)
