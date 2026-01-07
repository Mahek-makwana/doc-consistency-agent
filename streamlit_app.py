import streamlit as st
import re
import zipfile
import io
import plotly.graph_objects as go
from typing import Dict, Any, List, Set
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CraftAI DocSync Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ADVANCED CUSTOM CSS (FIGMA GRADE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #050505 !important;
        color: #ffffff;
    }
    
    .stApp {
        background-color: #050505;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        width: 300px !important;
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 20px 0;
        margin-bottom: 40px;
    }
    
    .logo-box {
        width: 40px;
        height: 40px;
        background: #6366f1;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 20px;
    }
    
    .logo-text-top {
        font-size: 14px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: -0.5px;
        line-height: 1;
    }
    
    .logo-text-bot {
        font-size: 8px;
        font-weight: 900;
        text-transform: uppercase;
        color: #6366f1;
    }

    /* Nav Buttons */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: 0.3s;
        color: #666;
        font-weight: 600;
        text-decoration: none;
    }
    
    .nav-btn.active {
        background: linear-gradient(to right, #6366f1, #a855f7);
        color: white;
    }
    
    .nav-btn:hover:not(.active) {
        background: rgba(255, 255, 255, 0.03);
        color: #fff;
    }

    /* Main Content */
    .main-header {
        font-size: 4.5rem;
        font-weight: 900;
        letter-spacing: -3px;
        margin-bottom: 3rem;
        color: #ffffff;
    }
    
    .header-accent {
        color: #a855f7;
    }

    /* File Upload Boxes */
    .upload-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .upload-box {
        border: 2px dashed rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background: rgba(255, 255, 255, 0.01);
        transition: 0.3s;
    }
    
    .upload-box:hover {
        border-color: #6366f1;
        background: rgba(99, 102, 241, 0.02);
    }

    /* Audit Button */
    div.stButton > button {
        background: linear-gradient(to right, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1.2rem !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }

    /* Metrics Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-top: 40px;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        min-height: 180px;
    }
    
    .card-label {
        font-size: 10px;
        font-weight: 900;
        text-transform: uppercase;
        color: #555;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }
    
    .score-big {
        font-size: 48px;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 5px;
    }
    
    .status-badge {
        font-size: 10px;
        font-weight: 900;
        text-transform: uppercase;
        color: #6366f1;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .stat-name {
        font-size: 12px;
        font-weight: 900;
        color: #fff;
    }
    
    .stat-val-green { font-size: 24px; font-weight: 900; color: #10b981; }
    .stat-val-red { font-size: 24px; font-weight: 900; color: #ef4444; }
    
    .issue-text {
        font-size: 11px;
        color: #888;
        line-height: 1.6;
    }
    
    /* Progress bar */
    .p-bar-bg { width: 100%; height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; margin-top: 15px; overflow: hidden; }
    .p-bar-fill { height: 100%; background: #ef4444; }
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
            issue_detail = f"CRITICAL GAP: The agent detected {len(found_logic)} logic entities, but NONE are described in comments or README."
        elif score < 100:
            issue_detail = f"DOCUMENTATION DEBT: {len(missing)} specific entities are missing from your guides. Missing: {', '.join(list(missing)[:2])}..."
        else:
            issue_detail = "PERFECT ALIGNMENT: Every code entity is explained in the documentation context."

        return {
            "score": score,
            "label": "Accurate Alignment" if score > 70 else "Partial Mismatch" if score > 30 else "Critical Mismatch",
            "stats": {"issues": len(missing), "synced": len(synced)},
            "detail": issue_detail,
            "visual": [len(synced), len(missing)]
        }

    def _empty_result(self):
        return {"score": 0, "label": "No Logic", "stats": {"issues": 0, "synced": 0}, "detail": "Upload files to begin.", "visual": [0, 1]}

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

# --- SIDEBAR (FIGMA MATCH) ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <div class="logo-box">✨</div>
            <div>
                <div class="logo-text-top">CraftAI</div>
                <div class="logo-text-bot">DocSync Agent</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if 'current_page' not in st.session_state: st.session_state.current_page = 'dashboard'
    
    if st.button("📊 Dashboard", key="btn_dash", use_container_width=True): st.session_state.current_page = 'dashboard'
    if st.button("📑 Reports", key="btn_rep", use_container_width=True): st.session_state.current_page = 'reports'
    if st.button("🕒 History", key="btn_hist", use_container_width=True): st.session_state.current_page = 'history'
    
    st.divider()
    st.caption("Enterprise v2.0 (Stable)")

# --- MAIN PAGE (FIGMA MATCH) ---
if st.session_state.current_page == 'dashboard':
    st.markdown("<h1 class='main-header'>CraftAI DocSync <span class='header-accent'>Agent</span></h1>", unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("<p style='font-size:24px; font-weight:900; color:#a855f7; text-transform:uppercase; margin-bottom:10px;'>Project Scenario</p>", unsafe_allow_html=True)
        code_file = st.file_uploader("Code", label_visibility="collapsed", type=['zip', 'py', 'js', 'ts', 'java', 'cs'])
    with col_u2:
        st.markdown("<p style='font-size:24px; font-weight:900; color:#a855f7; text-transform:uppercase; margin-bottom:10px;'>Documentation</p>", unsafe_allow_html=True)
        doc_file = st.file_uploader("Docs", label_visibility="collapsed", type=['md', 'txt', 'zip'])
    
    if st.button("✨ INITIATE CONSISTENCY AUDIT"):
        if code_file:
            code_text = extract_files(code_file, ['.py', '.js', '.ts', '.java', '.cs'])
            doc_text = extract_files(doc_file, ['.md', '.txt']) if doc_file else ""
            
            result = engine.perform_audit(code_text, doc_text)
            
            # FIGMA GRID
            st.markdown(f"""
                <div class="metrics-grid">
                    <div class="glass-card">
                        <p class="card-label">Analysis Summary</p>
                        <p class="score-big">{result['score']}%</p>
                        <p class="status-badge">{result['label']}</p>
                    </div>
                    <div class="glass-card">
                        <p class="card-label">Statistic Report</p>
                        <div class="stat-row"><span class="stat-name">Total Issues</span><span class="stat-val-red">{result['stats']['issues']}</span></div>
                        <div class="stat-row"><span class="stat-name">Synced</span><span class="stat-val-green">{result['stats']['synced']}</span></div>
                    </div>
                    <div class="glass-card">
                        <p class="card-label">Issue Summary</p>
                        <p class="issue-text">{result['detail']}</p>
                        <div class="p-bar-bg"><div class="p-bar-fill" style="width:{100-result['score']}%"></div></div>
                    </div>
                    <div id="chart-card" class="glass-card">
                        <p class="card-label">Visual Summary</p>
                        <div id="plotly-anchor"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # DONUT CHART (Matching Pink/Indigo)
            fig = go.Figure(data=[go.Pie(
                labels=['Synced', 'Gaps'],
                values=result['visual'],
                hole=.8,
                marker_colors=['#6366f1', '#f472b6'],
                textinfo='none'
            )])
            fig.update_layout(
                showlegend=True,
                legend=dict(orientation="h", x=0.5, y=-0.1, xanchor="center", font=dict(size=10, color="#888")),
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=120,
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Please upload a code file.")

elif st.session_state.current_page == 'reports':
    st.markdown("<h1 class='main-header'>Detailed <span class='header-accent'>Reports</span></h1>", unsafe_allow_html=True)
    st.info("Full audit exports will appear here.")

elif st.session_state.current_page == 'history':
    st.markdown("<h1 class='main-header'>Audit <span class='header-accent'>History</span></h1>", unsafe_allow_html=True)
    st.caption("Logs of previous project structural checks.")
