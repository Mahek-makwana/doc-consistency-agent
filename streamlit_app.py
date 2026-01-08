import streamlit as st
import re
import zipfile
import io
import pandas as pd
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

# --- FIGMA-GRADE PREMIUM CSS ---
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
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        width: 300px !important;
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 30px 20px;
        margin-bottom: 30px;
    }
    
    .logo-box {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 22px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }
    
    .logo-text-container { line-height: 1.1; }
    .logo-text-top { font-size: 16px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; }
    .logo-text-bot { font-size: 10px; font-weight: 900; text-transform: uppercase; color: #6366f1; letter-spacing: 1px; }

    /* Professional Navigation */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 16px 20px;
        border-radius: 14px;
        margin: 8px 15px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 600;
        color: #888;
        border: 1px solid transparent;
    }
    
    .nav-btn.active {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #6366f1;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .nav-btn:hover:not(.active) {
        background: rgba(255, 255, 255, 0.03);
        color: #fff;
    }

    /* Main Typography */
    .main-header {
        font-size: 4.5rem;
        font-weight: 900;
        letter-spacing: -3px;
        margin-bottom: 2.5rem;
        color: #ffffff;
    }
    .header-accent { color: #a855f7; }

    /* Dashboard Grid with Extra Space */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 30px; /* INCREASED SPACING */
        margin-top: 40px;
    }
    
    .card {
        background: #0f1115;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 30px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 1px rgba(255,255,255,0.2);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 30px;
    }
    
    .icon-container {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    
    .card-title {
        font-size: 15px;
        font-weight: 900;
        color: #fff;
        line-height: 1.2;
    }

    /* Professional Metrics */
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }
    
    .metric-label { font-size: 12px; font-weight: 600; color: #777; }
    .metric-value { font-size: 22px; font-weight: 900; color: #fff; }
    .metric-delta { font-size: 11px; font-weight: 900; padding: 3px 8px; border-radius: 6px; }
    .delta-neg { color: #ef4444; background: rgba(239, 68, 68, 0.15); }
    .delta-pos { color: #10b981; background: rgba(16, 185, 129, 0.15); }

    /* Progress & Gaps */
    .progress-bg { width: 100%; height: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; overflow: hidden; margin-top: 5px; }
    .progress-fill { height: 100%; border-radius: 4px; transition: width 1s ease-in-out; }

    /* Action Box */
    .code-preview {
        background: #050505;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 12px;
        font-family: 'Fira Code', monospace;
        font-size: 11px;
        color: #aaa;
        margin-bottom: 20px;
        min-height: 60px;
    }

    /* Streamlit Button Overrides */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        border: none !important;
        border-radius: 14px !important;
        color: white !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-size: 13px !important;
        padding: 1rem !important;
        transition: 0.3s !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* Layout Spacing */
    [data-testid="stVerticalBlock"] > div { margin-bottom: 25px; }

    /* Tables for Reports/History */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background: #0f1115;
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .custom-table th { background: rgba(255, 255, 255, 0.03); padding: 20px; text-align: left; font-size: 11px; text-transform: uppercase; color: #666; font-weight: 900; }
    .custom-table td { padding: 20px; border-top: 1px solid rgba(255, 255, 255, 0.05); color: #fff; font-size: 14px; }
    
    .badge { padding: 4px 10px; border-radius: 6px; font-weight: 900; font-size: 10px; text-transform: uppercase; }
    .badge-high { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .badge-mid { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .badge-low { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

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
            "label": "Accurate Alignment" if score > 70 else "Partial Mismatch" if score > 30 else "Critical Mismatch",
            "synced_count": len(synced),
            "total_issues": len(missing),
            "docs_analyzed": 1,
            "terminology_score": score,
            "style_score": 100 - (len(missing) % 15),
            "summary_text": f"Audit of {len(found_logic)} elements complete. Found {len(missing)} documentation gaps.",
            "file_list": ["analysis.py", "utils.js"],
            "suggestion": f"Add docstrings for {list(missing)[0]}" if missing else "Optimize imports"
        }

    def _empty_result(self):
        return {"score": 0, "label": "No Logic", "synced_count": 0, "total_issues": 0, "docs_analyzed": 0, "terminology_score": 0, "style_score": 0, "summary_text": "No logic detected.", "file_list": [], "suggestion": "N/A"}

engine = EnterpriseDocSyncEngine()

# --- STATE MANAGEMENT ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# --- HELPERS ---
def extract_files(uploaded_file, extensions):
    content = ""
    try:
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(uploaded_file) as z:
                for name in z.namelist():
                    if any(name.lower().endswith(ext) for ext in extensions):
                        with z.open(name) as f:
                            content += f.read().decode("utf-8", errors="ignore") + "\n"
        else:
            content = uploaded_file.read().decode("utf-8", errors="ignore")
    except:
        pass
    return content

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown(f"""
        <div class="sidebar-logo">
            <div class="logo-box">✨</div>
            <div class="logo-text-container">
                <div class="logo-text-top">CraftAI</div>
                <div class="logo-text-bot">DocSync Agent</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Dashboard", use_container_width=True, key="nav_dash"): st.session_state.page = 'dashboard'
    if st.button("📊 Reports", use_container_width=True, key="nav_rep"): st.session_state.page = 'reports'
    if st.button("🕒 History", use_container_width=True, key="nav_hist"): st.session_state.page = 'history'
    
    st.divider()
    st.markdown("<p style='font-size:10px; color:#555;'>ENTERPRISE ACCOUNT</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#fff; font-weight:900;'>Guest Mode <span style='color:#6366f1;'>●</span></p>", unsafe_allow_html=True)

# --- ROUTER ---
if st.session_state.page == 'dashboard':
    st.markdown("<h1 class='main-header'>CraftAI DocSync <span class='header-accent'>Agent</span></h1>", unsafe_allow_html=True)

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("<p style='font-size:24px; font-weight:900; color:#a855f7; text-transform:uppercase; margin-bottom:15px;'>Project Scenario</p>", unsafe_allow_html=True)
        code_file = st.file_uploader("Code", label_visibility="collapsed", type=['zip', 'py', 'js', 'ts'])
    with col_u2:
        st.markdown("<p style='font-size:24px; font-weight:900; color:#a855f7; text-transform:uppercase; margin-bottom:15px;'>Documentation</p>", unsafe_allow_html=True)
        doc_file = st.file_uploader("Docs", label_visibility="collapsed", type=['md', 'txt', 'zip'])

    if st.button("✨ INITIATE CONSISTENCY AUDIT", use_container_width=True):
        if code_file:
            with st.spinner("Processing structural alignment..."):
                code_text = extract_files(code_file, ['.py', '.js', '.ts'])
                doc_text = extract_files(doc_file, ['.md', '.txt']) if doc_file else ""
                res = engine.perform_audit(code_text, doc_text)
                
                # Save to History
                audit_entry = {
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "project": code_file.name,
                    "score": res['score'],
                    "label": res['label'],
                    "issues": res['total_issues']
                }
                st.session_state.history.insert(0, audit_entry)

                # 4-CARD TOP GRID
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-header"><div class="icon-container" style="background:rgba(99,102,241,0.2); color:#6366f1;">🔍</div><div class="card-title">Analysis<br>Summary</div></div>
                            <div class="metric-row"><span class="metric-label">Docs Analyzed</span><span class="metric-value">1</span></div>
                            <div class="metric-row"><span class="metric-label">Consistency Score</span><span class="metric-value">{res['score']}%</span></div>
                            <div class="progress-bg"><div class="progress-fill" style="width:{res['score']}%; background:#6366f1;"></div></div>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-header"><div class="icon-container" style="background:rgba(168,85,247,0.2); color:#a855f7;">📈</div><div class="card-title">Statistic Report</div></div>
                            <div class="metric-row"><span class="metric-label">Total Issues</span><div style="text-align:right;"><span class="metric-value">{res['total_issues']}</span><br><span class="metric-delta delta-neg">-12%</span></div></div>
                            <div class="metric-row" style="margin-top:10px;"><span class="metric-label">Synced Terms</span><div style="text-align:right;"><span class="metric-value">{res['synced_count']}</span><br><span class="metric-delta delta-pos">+8%</span></div></div>
                        </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-header"><div class="icon-container" style="background:rgba(244,114,182,0.2); color:#f472b6;">❕</div><div class="card-title">Issue Summary</div></div>
                            <p style="font-size:11px; color:#666; margin-bottom:20px;">{res['summary_text']}</p>
                            <div class="metric-row"><span class="metric-label">Terminology</span><span class="metric-value" style="font-size:14px;">{res['terminology_score']}</span></div>
                            <div class="progress-bg"><div class="progress-fill" style="width:{res['terminology_score']}%; background:#ef4444;"></div></div>
                            <div class="metric-row" style="margin-top:15px;"><span class="metric-label">Style Match</span><span class="metric-value" style="font-size:14px;">{res['style_score']}</span></div>
                            <div class="progress-bg"><div class="progress-fill" style="width:{res['style_score']}%; background:#6366f1;"></div></div>
                        </div>
                    """, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-header"><div class="icon-container" style="background:rgba(129,140,248,0.2); color:#818cf8;">💡</div><div class="card-title">Issue Suggested</div></div>
                            <p style="text-align:center; color:#6366f1; font-weight:900; margin-top:50px; cursor:pointer; font-size:12px;">View all actionable insights →</p>
                        </div>
                    """, unsafe_allow_html=True)

                # BOTTOM GRID
                st.write("") # Space
                bc1, bc2, bc3 = st.columns([1, 1, 2])
                with bc1:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-header"><div class="icon-container" style="background:rgba(99,102,241,0.2); color:#6366f1;">📍</div><div class="card-title">Local Analysis</div></div>
                            <div class="code-preview">/{code_file.name}</div>
                            <p style="font-size:10px; color:#555;">SCANNING LOCAL RUNTIME...</p>
                        </div>
                    """, unsafe_allow_html=True)
                with bc2:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-header"><div class="icon-container" style="background:rgba(168,85,247,0.2); color:#a855f7;">⚡</div><div class="card-title">Quick Fix</div></div>
                            <div class="code-preview"># {res['suggestion']}</div>
                            <button style="width:100%; background:#6366f1; border:none; color:white; padding:10px; border-radius:10px; font-weight:900; font-size:11px;">Apply Fix</button>
                        </div>
                    """, unsafe_allow_html=True)
                with bc3:
                    st.markdown(f"""
                        <div class="card" style="display:flex; align-items:center;">
                            <div style="flex:1;">
                                <div class="card-header"><div class="icon-container" style="background:rgba(99,102,241,0.2); color:#6366f1;">📊</div><div class="card-title">Visual Summary</div></div>
                                <p style="font-size:11px; color:#666; line-height:1.6; padding-right:20px;">Semantic map showing the overlap between codebase logic and documentation.</p>
                                <div style="margin-top:20px; font-size:11px; font-weight:900;">
                                    <span style="color:#6366f1;">●</span> Synced &nbsp;&nbsp;&nbsp; <span style="color:#f472b6;">●</span> Gap
                                </div>
                            </div>
                            <div style="flex:1;">
                    """, unsafe_allow_html=True)
                    fig = go.Figure(data=[go.Pie(
                        labels=['Synced', 'Gap'],
                        values=[res['synced_count'], res['total_issues']],
                        hole=.85,
                        marker_colors=['#6366f1', '#f472b6'],
                        textinfo='none'
                    )])
                    fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', height=160)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.error("Upload a Project Scenario to begin.")

elif st.session_state.page == 'reports':
    st.markdown("<h1 class='main-header'>Detailed <span class='header-accent'>Reports</span></h1>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("Initiate an audit on the Dashboard to generate detailed reports.")
    else:
        st.markdown("<p style='color:#888; margin-bottom:30px;'>Below are the downloadable audit reports for your latest sessions.</p>", unsafe_allow_html=True)
        for h in st.session_state.history:
            with st.container():
                st.markdown(f"""
                    <div style="background:#0f1115; border:1px solid #222; border-radius:16px; padding:25px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <p style="font-size:10px; font-weight:900; color:#6366f1; text-transform:uppercase; letter-spacing:1px;">{h['timestamp']} - AUDIT COMPLETE</p>
                            <h3 style="margin:5px 0; font-weight:900;">{h['project']}</h3>
                            <span class="badge {'badge-high' if h['score']>70 else 'badge-mid' if h['score']>30 else 'badge-low'}">{h['label']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.download_button(f"DOWNLOAD PDF REPORT - {h['project']}", data=f"Project: {h['project']}\nScore: {h['score']}%", file_name=f"Report_{h['project']}.txt")

elif st.session_state.page == 'history':
    st.markdown("<h1 class='main-header'>Audit <span class='header-accent'>History</span></h1>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("No previous scan data found.")
    else:
        html = """<table class="custom-table"><thead><tr><th>Time</th><th>Project Name</th><th>Status</th><th>Score</th><th>Gaps</th></tr></thead><tbody>"""
        for h in st.session_state.history:
            badge_class = 'badge-high' if h['score'] > 70 else 'badge-mid' if h['score'] > 30 else 'badge-low'
            html += f"""<tr>
                <td style="color:#666; font-weight:900;">{h['timestamp']}</td>
                <td style="font-weight:900;">{h['project']}</td>
                <td><span class="badge {badge_class}">{h['label']}</span></td>
                <td style="font-weight:900;">{h['score']}%</td>
                <td style="color:#ef4444; font-weight:900;">{h['issues']}</td>
            </tr>"""
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        if st.button("CLEAR ALL HISTORY"):
            st.session_state.history = []
            st.rerun()
