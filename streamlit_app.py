import streamlit as st
import re
import zipfile
import io
from typing import Dict, Any, List, Set
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CraftAI DocSync Dashboard",
    page_icon="✨",
    layout="wide",
)

# --- REFINED CSS (Matching Uploaded Design) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Dashboard Title */
    .dashboard-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #6366f1; /* Purple/Indigo */
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .section-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #666;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }

    /* Override Streamlit default buttons */
    div.stButton > button {
        background-color: #1e2129 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        padding: 0.8rem !important;
        font-weight: 700 !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Cards Styling */
    .result-card {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 20px;
        padding: 2rem;
        min-height: 200px;
    }
    
    .card-label {
        font-size: 0.8rem;
        font-weight: 900;
        color: #6366f1;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 2rem;
    }
    
    .score-value {
        font-size: 1.5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }
    
    .status-text {
        font-size: 1rem;
        font-weight: 600;
        color: #6366f1;
    }
    
    .stats-row {
        font-size: 1.8rem;
        font-weight: 900;
        margin: 1rem 0;
    }
    
    .stats-green { color: #10b981; }
    .stats-red { color: #ef4444; }
    
    .summary-text {
        font-size: 0.9rem;
        color: #888;
        line-height: 1.6;
    }

    /* file uploader custom styling */
    [data-testid="stFileUploader"] {
        background-color: #111318;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 10px;
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
            "stats": {"total": len(missing), "synced": len(synced)},
            "missing": list(missing),
            "detail": issue_detail
        }

    def _empty_result(self):
        return {"score": 0, "label": "No Logic", "stats": {"total": 0, "synced": 0}, "missing": [], "detail": "No code found."}

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

# --- UI LAYOUT ---
st.markdown("<h1 class='dashboard-title'>DocSync Dashboard</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("<p class='section-label'>Project Code (ZIP, PY, JS, etc.)</p>", unsafe_allow_html=True)
    code_file = st.file_uploader("Code Upload", label_visibility="collapsed", type=['zip', 'py', 'js', 'ts', 'java', 'cpp', 'cs'])

with col2:
    st.markdown("<p class='section-label'>Documentation (MD, TXT, RST)</p>", unsafe_allow_html=True)
    doc_file = st.file_uploader("Doc Upload", label_visibility="collapsed", type=['md', 'txt', 'rst', 'zip'])

st.write("") # Spacer

if st.button("🚀 INITIATE CONSISTENCY AUDIT"):
    if code_file:
        code_text = extract_files(code_file, ['.py', '.js', '.ts', '.java', '.cpp', '.cs'])
        doc_text = extract_files(doc_file, ['.md', '.txt', '.rst']) if doc_file else ""
        
        result = engine.perform_audit(code_text, doc_text)
        
        st.divider()
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
                <div class="result-card">
                    <p class="card-label">CONSISTENCY SCORE</p>
                    <p class="score-value">{result['score']}%</p>
                    <p class="status-text">{result['label']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
                <div class="result-card">
                    <p class="card-label">STRUCTURAL STATS</p>
                    <p class="stats-row text-white">Synced: <span class="stats-green">{result['stats']['synced']}</span></p>
                    <p class="stats-row text-white">Issues: <span class="stats-red">{result['stats']['total']}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
                <div class="result-card">
                    <p class="card-label">ISSUE SUMMARY</p>
                    <p class="summary-text">{result['detail']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Please provide a code file.")
