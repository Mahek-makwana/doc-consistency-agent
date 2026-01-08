from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
import re
import zipfile
import io
import json
import uvicorn
import os
from typing import Dict, Any, List

app = FastAPI()

# --- FIGMA UI TEMPLATE (SELF-CONTAINED SPA) ---
def get_html():
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CraftAI DocSync Agent</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/lucide@latest"></script>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Outfit', sans-serif; background-color: #050505; color: white; margin: 0; overflow: hidden; }}
            .glass-card {{ background: #0f1115; border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 30px; transition: 0.3s; }}
            .glass-card:hover {{ transform: translateY(-5px); border-color: rgba(99,102,241,0.5); }}
            .nav-btn {{ display: flex; align-items: center; gap: 15px; padding: 16px 20px; border-radius: 14px; color: #888; transition: 0.3s; cursor: pointer; }}
            .nav-btn.active {{ background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); color: #6366f1; }}
            .nav-btn:hover:not(.active) {{ background: rgba(255,255,255,0.03); color: white; }}
            .main-header {{ font-size: 3.5rem; font-weight: 900; letter-spacing: -2px; line-height: 1; }}
            .header-accent {{ color: #a855f7; }}
            .upload-area {{ border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px; transition: 0.2s; cursor: pointer; min-height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
            .upload-area:hover {{ border-color: #6366f1; background: rgba(99,102,241,0.02); }}
            .btn-initiate {{ background: linear-gradient(135deg, #6366f1, #a855f7); box-shadow: 0 4px 15px rgba(99,102,241,0.3); transition: 0.3s; }}
            .btn-initiate:hover {{ transform: scale(1.01); box-shadow: 0 6px 20px rgba(99,102,241,0.5); }}
            .progress-bar {{ height: 8px; border-radius: 4px; background: rgba(255, 255, 255, 0.05); overflow: hidden; }}
            .progress-fill {{ height: 100%; border-radius: 4px; transition: 1s ease-in-out; }}
            .view-section {{ display: none; height: calc(100vh - 40px); overflow-y: auto; padding-bottom: 80px; }}
            .view-section.active {{ display: block; }}
            .preview-box {{ background: #000; border-radius: 16px; padding: 20px; font-family: monospace; font-size: 11px; color: #aaa; overflow-x: auto; max-height: 250px; border: 1px solid #222; }}
            ::-webkit-scrollbar {{ width: 6px; }}
            ::-webkit-scrollbar-thumb {{ background: #222; border-radius: 10px; }}
            
            @media print {{
                body * {{ visibility: hidden; }}
                #print-area, #print-area * {{ visibility: visible; }}
                #print-area {{ position: absolute; left: 0; top: 0; width: 100% !important; background: white !important; color: black !important; }}
            }}
        </style>
    </head>
    <body class="flex min-h-screen">
        <aside class="w-72 border-r border-white/10 p-8 flex flex-col gap-8 hidden md:flex">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center font-black text-2xl">✨</div>
                <div>
                    <div class="text-sm font-black uppercase tracking-wider">CraftAI</div>
                    <div class="text-[10px] font-black uppercase text-indigo-500 tracking-[0.2em] -mt-1">DocSync Agent</div>
                </div>
            </div>
            <nav class="flex flex-col gap-2 mt-4">
                <div onclick="showView('dashboard')" class="nav-btn nav-link active" data-view="dashboard"><i data-lucide="home"></i> Dashboard</div>
                <div onclick="showView('reports')" class="nav-btn nav-link" data-view="reports"><i data-lucide="file-text"></i> Reports</div>
                <div onclick="showView('history')" class="nav-btn nav-link" data-view="history"><i data-lucide="clock"></i> History</div>
            </nav>
            <div class="mt-auto pt-8 border-t border-white/5 text-[10px] font-black uppercase text-neutral-600">Enterprise Access v2.1</div>
        </aside>

        <main class="flex-1 p-12 max-w-7xl mx-auto w-full relative">
            
            <section id="dashboard" class="view-section active">
                <h1 class="main-header mb-12">CraftAI DocSync <span class="header-accent">Agent</span></h1>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div>
                        <label class="block text-2xl font-black text-purple-400 uppercase mb-4">Project Scenario</label>
                        <div class="upload-area p-8" onclick="document.getElementById('code_file').click()">
                            <i data-lucide="upload-cloud" class="w-12 h-12 text-indigo-500 mb-4"></i>
                            <div class="font-bold text-neutral-400 mb-1">Drag and drop code or zip</div>
                            <input type="file" id="code_file" class="hidden" onchange="fileSelected(this, 'code-status')">
                            <div id="code-status" class="text-xs text-indigo-400 font-bold mt-2">No file selected</div>
                        </div>
                    </div>
                    <div>
                        <label class="block text-2xl font-black text-purple-400 uppercase mb-4">Documentation</label>
                        <div class="upload-area p-8" onclick="document.getElementById('doc_file').click()">
                            <i data-lucide="file-search" class="w-12 h-12 text-indigo-500 mb-4"></i>
                            <div class="font-bold text-neutral-400 mb-1">Upload README or MD</div>
                            <input type="file" id="doc_file" class="hidden" onchange="fileSelected(this, 'doc-status')">
                            <div id="doc-status" class="text-xs text-indigo-400 font-bold mt-2">No file selected</div>
                        </div>
                    </div>
                </div>

                <button onclick="runAudit()" id="audit-btn" class="btn-initiate w-full py-5 rounded-2xl font-black text-lg uppercase tracking-widest flex items-center justify-center gap-3 mb-16">
                    ✨ Initiate Consistency Audit
                </button>

                <div id="results-area" class="grid grid-cols-1 md:grid-cols-4 gap-8 opacity-0 transition-opacity duration-500 mb-12">
                    <!-- Cards injected here -->
                </div>

                <!-- NEW: FILE VISIBILITY SECTION -->
                <div id="visibility-area" class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 hidden">
                    <div class="glass-card">
                        <h4 class="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] mb-4">Analyzed Source Code</h4>
                        <div id="code-preview" class="preview-box whitespace-pre"></div>
                    </div>
                    <div class="glass-card">
                        <h4 class="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] mb-4">Analyzed Documentation</h4>
                        <div id="doc-preview" class="preview-box whitespace-pre"></div>
                    </div>
                </div>
            </section>

            <section id="reports" class="view-section">
                <h1 class="main-header mb-12">Detailed <span class="header-accent">Reports</span></h1>
                <div id="latest-report-container" class="space-y-8">
                    <div class="glass-card text-center py-20 text-neutral-600 italic">No analysis performed yet. Go to Dashboard to start.</div>
                </div>
            </section>

            <section id="history" class="view-section">
                <h1 class="main-header mb-12">Audit <span class="header-accent">History</span></h1>
                <div class="glass-card overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-white/5 text-[10px] font-black uppercase text-neutral-500">
                            <tr>
                                <th class="p-4">Timestamp</th>
                                <th class="p-4">File Name</th>
                                <th class="p-4">Score</th>
                                <th class="p-4">Status</th>
                                <th class="p-4">Action</th>
                            </tr>
                        </thead>
                        <tbody id="history-body" class="text-sm">
                            <!-- History rows here -->
                        </tbody>
                    </table>
                </div>
            </section>
        </main>

        <div id="print-area" class="hidden p-20 bg-white text-black"></div>

        <script>
            lucide.createIcons();
            let history = JSON.parse(localStorage.getItem('docSyncHistory') || '[]');
            updateHistoryTable();

            function showView(viewId) {{
                document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
                document.getElementById(viewId).classList.add('active');
                
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                document.querySelector(`[data-view="${{viewId}}"]`).classList.add('active');
                
                if (viewId === 'reports') renderReportsView();
                if (viewId === 'history') updateHistoryTable();
            }}

            function fileSelected(input, targetId) {{
                if (input.files[0]) {{
                    document.getElementById(targetId).textContent = "Selected: " + input.files[0].name;
                }}
            }}

            async function runAudit() {{
                const codeFile = document.getElementById('code_file').files[0];
                const docFile = document.getElementById('doc_file').files[0];
                if (!codeFile) return alert("Please upload a code file.");
                
                const btn = document.getElementById('audit-btn');
                btn.innerHTML = '<span class="animate-spin text-2xl">⏳</span> ANALYZING...';
                btn.disabled = true;

                const formData = new FormData();
                formData.append('code_file', codeFile);
                if (docFile) formData.append('doc_file', docFile);

                try {{
                    const resp = await fetch('/analyze', {{ method: 'POST', body: formData }});
                    const data = await resp.json();
                    
                    data.timestamp = new Date().toLocaleString();
                    data.fileName = codeFile.name;
                    history.unshift(data);
                    localStorage.setItem('docSyncHistory', JSON.stringify(history.slice(0, 20)));
                    
                    renderResults(data);
                    btn.innerHTML = '✨ Initiate Consistency Audit';
                    btn.disabled = false;
                }} catch (e) {{
                    alert("Error during analysis. Check server logs.");
                    btn.innerHTML = '✨ Initiate Consistency Audit';
                    btn.disabled = false;
                }}
            }}

            function renderResults(data) {{
                const area = document.getElementById('results-area');
                area.style.opacity = '0';
                
                // Show File Visibility
                const visArea = document.getElementById('visibility-area');
                visArea.classList.remove('hidden');
                document.getElementById('code-preview').textContent = data.code_snippet;
                document.getElementById('doc-preview').textContent = data.doc_snippet || "No documentation provided.";

                setTimeout(() => {{
                    area.innerHTML = `
                        <div class="glass-card">
                            <div class="flex items-center gap-4 mb-8">
                                <div class="w-10 h-10 bg-indigo-500/10 text-indigo-500 rounded-xl flex items-center justify-center"><i data-lucide="search"></i></div>
                                <div class="text-[10px] font-black uppercase text-white/50 leading-tight">Analysis<br>Summary</div>
                            </div>
                            <div class="flex justify-between mb-2 text-xs font-bold text-neutral-500 uppercase">Score <span class="text-xl font-black text-white">${{data.score}}%</span></div>
                            <div class="progress-bar"><div class="progress-fill bg-indigo-500" style="width:${{data.score}}%"></div></div>
                            <p class="text-[10px] mt-4 font-bold text-neutral-600 uppercase tracking-widest">${{data.label}}</p>
                        </div>

                        <div class="glass-card">
                            <div class="flex items-center gap-4 mb-8">
                                <div class="w-10 h-10 bg-purple-500/10 text-purple-500 rounded-xl flex items-center justify-center"><i data-lucide="trending-up"></i></div>
                                <div class="text-[10px] font-black uppercase text-white/50 leading-tight">Statistic<br>Report</div>
                            </div>
                            <div class="flex justify-between mb-4"><span class="text-[10px] font-bold text-neutral-500 uppercase">Total Gaps</span><span class="text-xl font-black">${{data.stats.issues}}</span></div>
                            <div class="flex justify-between"><span class="text-[10px] font-bold text-neutral-500 uppercase">Synced Units</span><span class="text-xl font-black text-emerald-500">${{data.stats.synced}}</span></div>
                        </div>

                        <div class="glass-card">
                            <div class="flex items-center gap-4 mb-8">
                                <div class="w-10 h-10 bg-pink-500/10 text-pink-500 rounded-xl flex items-center justify-center"><i data-lucide="alert-circle"></i></div>
                                <div class="text-[10px] font-black uppercase text-white/50 leading-tight">Issue<br>Summary</div>
                            </div>
                            <div class="text-[11px] text-neutral-400 space-y-2">
                                ${{data.detailed_issues.map(i => `• ${{i}}`).join('<br>')}}
                            </div>
                        </div>

                        <div class="glass-card flex flex-col items-center">
                            <div id="chart-main" style="width:120px;height:120px;"></div>
                            <p class="text-[10px] font-black mt-4 uppercase text-neutral-500">Semantic Alignment Matrix</p>
                            <div class="flex gap-4 mt-2 text-[8px] font-black">
                                <span><span class="text-indigo-500 mr-1">●</span> SYNCED</span>
                                <span><span class="text-pink-500 mr-1">●</span> GAP</span>
                            </div>
                        </div>
                    `;
                    lucide.createIcons();
                    renderChart('chart-main', data.visual);
                    area.style.opacity = '1';
                }}, 300);
            }}

            function renderChart(divId, values) {{
                Plotly.newPlot(divId, [{{
                    values: values,
                    labels: ['Synced', 'Gaps'],
                    type: 'pie',
                    hole: .8,
                    marker: {{ colors: ['#6366f1', '#f472b6'] }},
                    showlegend: false,
                    textinfo: 'none'
                }}], {{ margin: {{t:0,b:0,l:0,r:0}}, paper_bgcolor: 'rgba(0,0,0,0)', width:120, height:120 }}, {{displayModeBar: false}});
            }}

            function updateHistoryTable() {{
                const tbody = document.getElementById('history-body');
                tbody.innerHTML = history.length ? history.map((item, idx) => `
                    <tr class="border-t border-white/5 hover:bg-white/5 transition-colors">
                        <td class="p-4 text-neutral-500">${{item.timestamp}}</td>
                        <td class="p-4 font-bold">${{item.fileName}}</td>
                        <td class="p-4 font-black ${{item.score > 70 ? 'text-emerald-500' : 'text-pink-500'}}">${{item.score}}%</td>
                        <td class="p-4"><span class="px-2 py-1 bg-neutral-800 rounded text-[9px] font-bold uppercase">${{item.label}}</span></td>
                        <td class="p-4"><button onclick="viewOldReport(${{idx}})" class="text-indigo-400 hover:text-white transition-colors text-xs font-black uppercase">View</button></td>
                    </tr>
                `).join('') : '<tr><td colspan="5" class="p-8 text-center text-neutral-600">No history found.</td></tr>';
            }}

            function renderReportsView() {{
                const container = document.getElementById('latest-report-container');
                if (!history.length) return;
                
                const latest = history[0];
                container.innerHTML = `
                    <div class="glass-card" id="active-report">
                        <div class="flex justify-between items-start mb-12">
                            <div>
                                <h3 class="text-2xl font-black mb-1">${{latest.fileName}}</h3>
                                <p class="text-xs text-neutral-500 uppercase font-bold tracking-widest">${{latest.timestamp}}</p>
                            </div>
                            <button onclick="downloadReport()" class="flex items-center gap-2 bg-indigo-500/10 text-indigo-400 px-6 py-3 rounded-xl border border-indigo-400/20 hover:bg-indigo-500 hover:text-white transition-all font-black text-xs uppercase">
                                <i data-lucide="download" class="w-4 h-4"></i> Download PDF
                            </button>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                            <div class="space-y-8">
                                <div>
                                    <h4 class="text-xs font-black text-neutral-500 uppercase tracking-[0.2em] mb-4">Alignment Breakdown</h4>
                                    <p class="text-lg font-medium leading-relaxed">${{latest.detail}}</p>
                                </div>
                                <div class="space-y-4">
                                    <h4 class="text-xs font-black text-neutral-500 uppercase tracking-[0.2em]">Operational Insights</h4>
                                    <ul class="space-y-2 text-sm text-neutral-400">
                                        ${{latest.detailed_issues.length ? latest.detailed_issues.map(i => `<li class="flex gap-3"><span class="text-pink-500">▶</span> ${{i}}</li>`).join('') : '<li class="text-emerald-500 font-bold">✓ Documentation matches code logic patterns perfectly.</li>'}}
                                    </ul>
                                </div>
                            </div>
                            <div class="bg-black/20 p-8 rounded-3xl border border-white/5 flex flex-col items-center justify-center">
                                <div id="report-chart" style="width:200px;height:200px;"></div>
                                <div class="mt-8 grid grid-cols-2 gap-8 text-center">
                                    <div><p class="text-[10px] font-bold text-neutral-500 uppercase">Coverage</p><p class="text-2xl font-black text-white">${{latest.score}}%</p></div>
                                    <div><p class="text-[10px] font-bold text-neutral-500 uppercase">Gaps</p><p class="text-2xl font-black text-pink-500">${{latest.stats.issues}}</p></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                lucide.createIcons();
                setTimeout(() => {{
                    Plotly.newPlot('report-chart', [{{
                        values: latest.visual,
                        type: 'pie',
                        hole: .8,
                        marker: {{ colors: ['#6366f1', '#f472b6'] }},
                        showlegend: false,
                        textinfo: 'none'
                    }}], {{ margin: {{t:0,b:0,l:0,r:0}}, paper_bgcolor: 'rgba(0,0,0,0)', width:200, height:200 }}, {{displayModeBar: false}});
                }}, 100);
            }}

            function viewOldReport(idx) {{
                const item = history[idx];
                history = [item, ...history.filter((_, i) => i !== idx)];
                localStorage.setItem('docSyncHistory', JSON.stringify(history));
                showView('reports');
            }}

            function downloadReport() {{
                const latest = history[0];
                const printContent = `
                    <div style="font-family: sans-serif; padding: 40px; color: black;">
                        <h1 style="font-size: 32px; font-weight: 800; border-bottom: 4px solid #6366f1; padding-bottom: 20px;">CONSISTENCY AUDIT REPORT</h1>
                        <p style="text-transform: uppercase; font-weight: bold; color: #666;">Project: ${{latest.fileName}}</p>
                        <p style="text-transform: uppercase; font-weight: bold; color: #666; margin-bottom: 40px;">Timestamp: ${{latest.timestamp}}</p>
                        
                        <div style="background: #f0f4ff; padding: 30px; border-radius: 20px; border: 1px solid #cce0ff; margin-bottom: 40px;">
                            <h2 style="margin: 0; font-size: 40px;">SCORE: ${{latest.score}}%</h2>
                            <p style="font-weight: 800; color: #6366f1; margin-top: 5px;">STATUS: ${{latest.label}}</p>
                        </div>

                        <h3 style="text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 10px;">Executive Summary</h3>
                        <p style="line-height: 1.6; font-size: 16px;">${{latest.detail}}</p>

                        <h3 style="text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-top: 40px;">Detailed Observations</h3>
                        <ul style="line-height: 2;">
                            ${{latest.detailed_issues.map(i => `<li style="margin-bottom: 10px;">❌ ${{i}}</li>`).join('')}}
                        </ul>

                        <div style="margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999; text-align: center;">
                            CraftAI DocSync Agent v2.1 - Corporate Audit Output
                        </div>
                    </div>
                `;
                const area = document.getElementById('print-area');
                area.innerHTML = printContent;
                area.classList.remove('hidden');
                window.print();
                area.classList.add('hidden');
            }}
        </script>
    </body>
    </html>
    """
    return html

# --- CORE ENGINE ---
class Engine:
    def audit(self, c, d):
        found = set(re.findall(r"(?:def|function|class)\s+([A-Za-z_]\w*)", c))
        found.update(re.findall(r"(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:\(.*\)|function)", c))
        found = {f for f in found if len(f) > 2}
        comments = " ".join(re.findall(r"(?:#|//|/\*|'''|\"\"\")(.*?)(?:\*/|'''|\"\"\"|\n|$)", c, re.DOTALL))
        pool = (d + " " + comments).lower()
        
        c_prev = c[:800] + "..." if len(c) > 800 else c
        d_prev = d[:800] + "..." if len(d) > 800 else d

        if not found:
            return {
                "score": 0, "label": "No Logic Found", "stats": {"issues": 0, "synced": 0}, 
                "detail": "Empty project input.", "visual": [0, 1], "detailed_issues": ["Critical: Analysis empty."],
                "code_snippet": c_prev, "doc_snippet": d_prev
            }
        synced = {l for l in found if l.lower() in pool}
        missing = found - synced
        score = int((len(synced)/len(found))*100)
        issue_list = [f"Documentation missing for '{m}'" for m in list(missing)[:10]]
        return {
            "score": score,
            "label": "Accurate Alignment" if score > 75 else "Partial Mismatch",
            "stats": {"issues": len(missing), "synced": len(synced)},
            "detail": f"Identified {len(found)} logic units. {len(missing)} are undocumented.",
            "visual": [len(synced), len(missing)],
            "detailed_issues": issue_list,
            "code_snippet": c_prev, "doc_snippet": d_prev
        }

engine = Engine()

# --- APP ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def home(): return get_html()

@app.post("/analyze")
async def analyze(code_file: UploadFile = File(None), doc_file: UploadFile = File(None)):
    c_text, d_text = "", ""
    
    # Supported code file extensions (including ML/Data Science)
    CODE_EXTENSIONS = (
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', 
        '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.m', '.r', '.pl',
        '.ipynb',  # Jupyter Notebooks
        '.sql',    # SQL queries
        '.sh',     # Shell scripts
        '.bat'     # Batch scripts
    )
    
    # Supported documentation extensions
    DOC_EXTENSIONS = ('.md', '.txt', '.rst', '.markdown', '.text')
    
    if code_file:
        try:
            buf = await code_file.read()
            
            # Special handling for Jupyter Notebooks
            if code_file.filename.endswith('.ipynb'):
                try:
                    notebook = json.loads(buf.decode('utf-8'))
                    for cell in notebook.get('cells', []):
                        if cell.get('cell_type') == 'code':
                            c_text += ''.join(cell.get('source', [])) + "\n\n"
                        elif cell.get('cell_type') == 'markdown':
                            d_text += ''.join(cell.get('source', [])) + "\n\n"
                except:
                    c_text = buf.decode(errors='ignore')
            
            # Handle ZIP files
            elif code_file.filename.endswith('.zip'):
                try:
                    with zipfile.ZipFile(io.BytesIO(buf)) as z:
                        for n in z.namelist():
                            if n.endswith(CODE_EXTENSIONS) and not n.startswith('__MACOSX'):
                                try:
                                    file_content = z.read(n)
                                    
                                    # Special handling for .ipynb inside ZIP
                                    if n.endswith('.ipynb'):
                                        try:
                                            notebook = json.loads(file_content.decode('utf-8'))
                                            for cell in notebook.get('cells', []):
                                                if cell.get('cell_type') == 'code':
                                                    c_text += ''.join(cell.get('source', [])) + "\n\n"
                                                elif cell.get('cell_type') == 'markdown':
                                                    d_text += ''.join(cell.get('source', [])) + "\n\n"
                                        except:
                                            c_text += file_content.decode(errors='ignore') + "\n"
                                    else:
                                        c_text += file_content.decode(errors='ignore') + "\n"
                                except:
                                    continue
                except zipfile.BadZipFile:
                    c_text = buf.decode(errors='ignore')
            
            # Handle regular text files
            else:
                c_text = buf.decode(errors='ignore')
                
        except Exception as e:
            c_text = f"# Error reading file: {str(e)}"
    
    if doc_file:
        try:
            buf = await doc_file.read()
            if doc_file.filename.endswith('.zip'):
                try:
                    with zipfile.ZipFile(io.BytesIO(buf)) as z:
                        for n in z.namelist():
                            if n.endswith(DOC_EXTENSIONS) and not n.startswith('__MACOSX'):
                                try:
                                    d_text += z.read(n).decode(errors='ignore') + "\n"
                                except:
                                    continue
                except zipfile.BadZipFile:
                    d_text = buf.decode(errors='ignore')
            else:
                d_text = buf.decode(errors='ignore')
        except Exception as e:
            d_text = f"Error reading documentation: {str(e)}"
    
    return engine.audit(c_text, d_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
