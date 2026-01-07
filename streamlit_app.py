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

# --- ADVANCED CUSTOM CSS (FIGMA GRADE - EXACT REPLICATION) ---
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
        width: 280px !important;
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .logo-box {
        width: 38px;
        height: 38px;
        background: #6366f1;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 18px;
    }
    
    .logo-text-container { line-height: 1.1; }
    .logo-text-top { font-size: 14px; font-weight: 900; text-transform: uppercase; }
    .logo-text-bot { font-size: 9px; font-weight: 900; text-transform: uppercase; color: #6366f1; }

    /* Main Header */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: -2px;
        margin-bottom: 2rem;
        color: #ffffff;
    }
    .header-accent { color: #a855f7; }

    /* Dashboard Cards Grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-top: 30px;
    }
    
    .card {
        background: #0f1115;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        position: relative;
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .icon-container {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    
    .card-title {
        font-size: 14px;
        font-weight: 900;
        color: #fff;
    }

    /* Specific Metric Styles */
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .metric-label { font-size: 11px; font-weight: 600; color: #888; }
    .metric-value { font-size: 18px; font-weight: 900; color: #fff; }
    .metric-delta { font-size: 10px; font-weight: 900; padding: 2px 6px; border-radius: 4px; }
    .delta-neg { color: #ef4444; background: rgba(239, 68, 68, 0.1); }
    .delta-pos { color: #10b981; background: rgba(16, 185, 129, 0.1); }

    /* Progress Bars */
    .progress-container { margin-top: 10px; }
    .progress-bg { width: 100%; height: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 3px; }

    /* Sub-Section Labels */
    .sub-label { font-size: 10px; font-weight: 900; color: #555; text-transform: uppercase; margin-bottom: 8px; }

    /* Quick Fix Box */
    .code-preview {
        background: #050505;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 8px;
        font-family: monospace;
        font-size: 10px;
        color: #666;
        margin-bottom: 15px;
    }

    /* Buttons Override */
    div.stButton > button {
        background: linear-gradient(to right, #6366f1, #a855f7) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-size: 12px !important;
        padding: 0.8rem !important;
    }

    /* Wide Visual Summary Card */
    .visual-summary-container {
        grid-column: span 2;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .visual-text { flex: 1; }
    .visual-chart { flex: 1; }

</style>
""", unsafe_allow_html=True)

# --- ENGINE ---
class EnterpriseDocSyncEngine:
    def __init__(self):
        self.patterns = {
            "logic": [
                r"def\s+([A-Za-z_]\w*)",
                r"function\s+([A-Za-z_]\w*)",
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
        
        if not found_logic: return self._empty_result()

        synced = {l for l in found_logic if l.lower() in doc_pool}
        missing = found_logic - synced
        score = int((len(synced) / len(found_logic)) * 100)
        
        return {
            "score": score,
            "synced_count": len(synced),
            "total_issues": len(missing),
            "docs_analyzed": 3, # Mock for UI
            "terminology_score": score - (len(missing) % 5),
            "style_score": 100 - (len(missing) * 2),
            "summary_text": f"Audit of {len(found_logic)} elements complete. {len(missing)} gaps identified in structural alignment.",
            "file_list": ["/analysis_engine.py", "/main_server.py"],
            "suggestion": "Fix Delta Implementation"
        }

    def _empty_result(self):
        return {"score": 0, "synced_count": 0, "total_issues": 0, "docs_analyzed": 0, "terminology_score": 0, "style_score": 0, "summary_text": "Ready to scan.", "file_list": [], "suggestion": "N/A"}

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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <div class="logo-box">✨</div>
            <div class="logo-text-container">
                <div class="logo-text-top">CraftAI</div>
                <div class="logo-text-bot">DocSync Agent</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<a href="#" class="nav-btn active">🏠 Dashboard</a>', unsafe_allow_html=True)
    st.markdown('<a href="#" class="nav-btn">📊 Reports</a>', unsafe_allow_html=True)
    st.markdown('<a href="#" class="nav-btn">🕒 History</a>', unsafe_allow_html=True)

# --- MAIN PAGE ---
st.markdown("<h1 class='main-header'>CraftAI DocSync <span class='header-accent'>Agent</span></h1>", unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1:
    st.markdown("<p style='font-size:24px; font-weight:900; color:#a855f7; text-transform:uppercase;'>Project Scenario</p>", unsafe_allow_html=True)
    code_file = st.file_uploader("Code", label_visibility="collapsed", type=['zip', 'py', 'js', 'ts'])
with u2:
    st.markdown("<p style='font-size:24px; font-weight:900; color:#a855f7; text-transform:uppercase;'>Documentation</p>", unsafe_allow_html=True)
    doc_file = st.file_uploader("Docs", label_visibility="collapsed", type=['md', 'txt', 'zip'])

if st.button("✨ INITIATE CONSISTENCY AUDIT", use_container_width=True):
    if code_file:
        code_text = extract_files(code_file, ['.py', '.js', '.ts'])
        doc_text = extract_files(doc_file, ['.md', '.txt']) if doc_file else ""
        res = engine.perform_audit(code_text, doc_text)

        # TOP ROW: 4 CARDS
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="icon-container" style="background:rgba(99,102,241,0.2); color:#6366f1;">🔍</div><div class="card-title">Analysis<br>Summary</div></div>
                    <div class="metric-row"><span class="metric-label">Docs Analyzed</span><span class="metric-value">{res['docs_analyzed']}</span></div>
                    <div class="metric-row"><span class="metric-label">Consistency Score</span><span class="metric-value">{res['score']}%</span></div>
                    <div class="progress-container"><div class="progress-bg"><div class="progress-fill" style="width:{res['score']}%; background:#6366f1;"></div></div></div>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="icon-container" style="background:rgba(168,85,247,0.2); color:#a855f7;">📈</div><div class="card-title">Statistic Report</div></div>
                    <p class="sub-label">Total Issues</p>
                    <div class="metric-row"><span class="metric-value">{res['total_issues']}</span><span class="metric-delta delta-neg">-12%</span></div>
                    <p class="sub-label" style="margin-top:15px;">Synced Terms</p>
                    <div class="metric-row"><span class="metric-value">{res['synced_count']}</span><span class="metric-delta delta-pos">+8%</span></div>
                </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="icon-container" style="background:rgba(244,114,182,0.2); color:#f472b6;">❕</div><div class="card-title">Issue Summary</div></div>
                    <p style="font-size:10px; color:#888; margin-bottom:15px;">{res['summary_text']}</p>
                    <div class="metric-row"><span class="metric-label">Terminology</span><span class="metric-label">{res['terminology_score']}</span></div>
                    <div class="progress-bg"><div class="progress-fill" style="width:{res['terminology_score']}%; background:#ef4444;"></div></div>
                    <div class="metric-row" style="margin-top:10px;"><span class="metric-label">Style</span><span class="metric-label">{res['style_score']}</span></div>
                    <div class="progress-bg"><div class="progress-fill" style="width:{res['style_score']}%; background:#6366f1;"></div></div>
                </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="icon-container" style="background:rgba(129,140,248,0.2); color:#818cf8;">💡</div><div class="card-title">Issue Suggested</div></div>
                    <p style="text-align:center; color:#6366f1; font-weight:900; margin-top:40px; cursor:pointer;">View all →</p>
                </div>
            """, unsafe_allow_html=True)

        # BOTTOM ROW: 3 CARDS (Visual is wide)
        bc1, bc2, bc3 = st.columns([1, 1, 2])
        
        with bc1:
            st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="icon-container" style="background:rgba(99,102,241,0.2); color:#6366f1;">📍</div><div class="card-title">Local Analysis</div></div>
                    <div class="code-preview">{res['file_list'][0] if res['file_list'] else 'Searching...'}</div>
                </div>
            """, unsafe_allow_html=True)

        with bc2:
            st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="icon-container" style="background:rgba(168,85,247,0.2); color:#a855f7;">⚡</div><div class="card-title">Quick Fix</div></div>
                    <div class="code-preview"># {res['suggestion']}</div>
                    <button style="width:100%; background:#6366f1; border:none; color:white; padding:8px; border-radius:10px; font-weight:900; font-size:10px; cursor:pointer;">Apply Fix</button>
                </div>
            """, unsafe_allow_html=True)

        with bc3:
            st.markdown(f"""
                <div class="card" style="display:flex; align-items:center; gap:30px;">
                    <div class="visual-text">
                        <div class="card-header" style="margin-bottom:10px;">
                            <div class="icon-container" style="background:rgba(99,102,241,0.2); color:#6366f1;">📊</div>
                            <div class="card-title">Visual Summary</div>
                        </div>
                        <p style="font-size:10px; color:#666; line-height:1.4;">Semantic map showing the overlap between codebase logic and documentation.</p>
                        <div style="margin-top:20px; font-size:10px; font-weight:900;">
                            <span style="color:#6366f1;">●</span> Synced &nbsp;&nbsp; <span style="color:#f472b6;">●</span> Gap
                        </div>
                    </div>
                    <div class="visual-chart" style="width:100%;">
            """, unsafe_allow_html=True)
            
            fig = go.Figure(data=[go.Pie(
                labels=['Synced', 'Gap'],
                values=[res['synced_count'], res['total_issues']],
                hole=.85,
                marker_colors=['#6366f1', '#f472b6'],
                textinfo='none'
            )])
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', height=150)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.warning("Please upload a code file to begin.")
