from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
import re
import zipfile
import io
import json
import uvicorn
import os
from typing import Dict, Any

app = FastAPI()

# --- FIGMA UI TEMPLATE (SELF-CONTAINED) ---
def get_html(result=None):
    res_json = json.dumps(result) if result else "null"
    
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
            body {{ font-family: 'Outfit', sans-serif; background-color: #050505; color: white; margin: 0; }}
            .glass-card {{ background: #0f1115; border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 30px; transition: 0.3s; }}
            .glass-card:hover {{ transform: translateY(-5px); border-color: rgba(99,102,241,0.5); }}
            .nav-btn {{ display: flex; align-items: center; gap: 15px; padding: 16px 20px; border-radius: 14px; color: #888; transition: 0.3s; cursor: pointer; }}
            .nav-btn.active {{ background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); color: #6366f1; }}
            .nav-btn:hover:not(.active) {{ background: rgba(255,255,255,0.03); color: white; }}
            .main-header {{ font-size: 3.5rem; font-weight: 900; letter-spacing: -2px; line-height: 1; }}
            .header-accent {{ color: #a855f7; }}
            .upload-area {{ border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px; transition: 0.3s; cursor: pointer; }}
            .upload-area:hover {{ border-color: #6366f1; background: rgba(99,102,241,0.02); }}
            .btn-initiate {{ background: linear-gradient(135deg, #6366f1, #a855f7); box-shadow: 0 4px 15px rgba(99,102,241,0.3); transition: 0.3s; }}
            .btn-initiate:hover {{ transform: scale(1.02); box-shadow: 0 6px 20px rgba(99,102,241,0.5); }}
            .progress-bar {{ height: 8px; border-radius: 4px; background: rgba(255, 255, 255, 0.05); overflow: hidden; }}
            .progress-fill {{ height: 100%; border-radius: 4px; transition: 1s ease-in-out; }}
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
                <div class="nav-btn active"><i data-lucide="home"></i> Dashboard</div>
                <div class="nav-btn"><i data-lucide="file-text"></i> Reports</div>
                <div class="nav-btn"><i data-lucide="clock"></i> History</div>
            </nav>
        </aside>

        <main class="flex-1 p-12 max-w-7xl mx-auto w-full">
            <h1 class="main-header mb-12">CraftAI DocSync <span class="header-accent">Agent</span></h1>
            
            <form action="/analyze" method="post" enctype="multipart/form-data" class="space-y-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <label class="block text-2xl font-black text-purple-400 uppercase mb-4">Project Scenario</label>
                        <div class="upload-area p-8 text-center relative" onclick="document.getElementById('code_file').click()">
                            <i data-lucide="upload-cloud" class="w-12 h-12 text-indigo-500 mx-auto mb-4"></i>
                            <div class="font-bold text-neutral-400 mb-1">Drag and drop code or zip</div>
                            <input type="file" id="code_file" name="code_file" class="hidden" onchange="this.nextElementSibling.textContent = this.files[0].name">
                            <div class="mt-2 text-xs text-indigo-500 font-bold"></div>
                        </div>
                    </div>
                    <div>
                        <label class="block text-2xl font-black text-purple-400 uppercase mb-4">Documentation</label>
                        <div class="upload-area p-8 text-center relative" onclick="document.getElementById('doc_file').click()">
                            <i data-lucide="file-search" class="w-12 h-12 text-indigo-500 mx-auto mb-4"></i>
                            <div class="font-bold text-neutral-400 mb-1">Upload README or MD</div>
                            <input type="file" id="doc_file" name="doc_file" class="hidden" onchange="this.nextElementSibling.textContent = this.files[0].name">
                            <div class="mt-2 text-xs text-indigo-500 font-bold"></div>
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn-initiate w-full py-5 rounded-2xl font-black text-lg uppercase tracking-widest flex items-center justify-center gap-3">
                    ✨ Initiate Consistency Audit
                </button>
            </form>

            <div id="results-display" class="mt-16 grid grid-cols-1 md:grid-cols-4 gap-8 {'hidden' if not result else ''}">
                {"<!-- Cards will be injected if result exists -->"}
            </div>
        </main>
        <script>
            lucide.createIcons();
            const result = {res_json};
            if (result) {{
                const display = document.getElementById('results-display');
                display.classList.remove('hidden');
                display.innerHTML = `
                    <div class="glass-card">
                        <div class="flex items-center gap-4 mb-8">
                            <div class="w-10 h-10 bg-indigo-500/10 text-indigo-500 rounded-xl flex items-center justify-center"><i data-lucide="search"></i></div>
                            <div class="text-[10px] font-black uppercase text-white/50 leading-tight">Analysis Summary</div>
                        </div>
                        <div class="flex justify-between mb-2"><span class="text-[10px] font-bold text-neutral-500">Score</span><span class="text-xl font-black">${{result.score}}%</span></div>
                        <div class="progress-bar"><div class="progress-fill bg-indigo-500" style="width:${{result.score}}%"></div></div>
                    </div>
                    <div class="glass-card">
                         <div class="flex items-center gap-4 mb-8"><div class="w-10 h-10 bg-purple-500/10 text-purple-500 rounded-xl flex items-center justify-center"><i data-lucide="trending-up"></i></div><div class="text-[10px] font-black uppercase text-white/50 leading-tight">Statistic Report</div></div>
                         <div class="flex justify-between mb-2"><span class="text-[10px] font-bold text-neutral-500">Total Gaps</span><span class="text-xl font-black">${{result.stats.issues}}</span></div>
                         <div class="flex justify-between"><span class="text-[10px] font-bold text-neutral-500">Synced Units</span><span class="text-xl font-black text-emerald-500">${{result.stats.synced}}</span></div>
                    </div>
                    <div class="glass-card">
                         <div class="flex items-center gap-4 mb-8"><div class="w-10 h-10 bg-pink-500/10 text-pink-500 rounded-xl flex items-center justify-center"><i data-lucide="alert-circle"></i></div><div class="text-[10px] font-black uppercase text-white/50 leading-tight">Issue Summary</div></div>
                         <p class="text-[10px] text-neutral-400 leading-relaxed">${{result.detail}}</p>
                    </div>
                    <div class="glass-card flex flex-col justify-center items-center">
                         <div id="chart" style="width:100px;height:100px;"></div>
                         <p class="text-[8px] font-black mt-2 uppercase tracking-widest text-white/20">Semantic Alignment</p>
                    </div>
                `;
                lucide.createIcons();
                Plotly.newPlot('chart', [{{
                    values: result.visual,
                    type: 'pie',
                    hole: .8,
                    marker: {{ colors: ['#6366f1', '#f472b6'] }},
                    showlegend: false,
                    textinfo: 'none'
                }}], {{ margin: {{t:0,b:0,l:0,r:0}}, paper_bgcolor: 'rgba(0,0,0,0)', width:100, height:100 }}, {{displayModeBar: false}});
            }}
        </script>
    </body>
    </html>
    """
    return html

# --- CORE ENGINE ---
class EnterpriseDocSyncEngine:
    def audit(self, c_text: str, d_text: str) -> Dict[str, Any]:
        found = set(re.findall(r"def\s+([A-Za-z_]\w*)|function\s+([A-Za-z_]\w*)", c_text))
        found = {f[0] or f[1] for f in found if (f[0] or f[1])}
        comments = " ".join(re.findall(r"(?:#|//|/\*)(.*?)(?:\*/|\n|$)", c_text))
        pool = (d_text + " " + comments).lower()
        if not found: return {"score": 0, "stats": {"issues": 0, "synced": 0}, "detail": "No logic units detected in project.", "visual": [0, 1]}
        synced = {l for l in found if l.lower() in pool}
        score = int((len(synced)/len(found))*100)
        return {
            "score": score,
            "stats": {"issues": len(found)-len(synced), "synced": len(synced)},
            "detail": f"Aligning {len(found)} logic units with documentation context. {len(found)-len(synced)} gaps found.",
            "visual": [len(synced), len(found)-len(synced)]
        }

engine = EnterpriseDocSyncEngine()

# --- APP ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def home():
    return get_html()

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(code_file: UploadFile = File(None), doc_file: UploadFile = File(None)):
    c_text, d_text = "", ""
    if code_file:
        buf = await code_file.read()
        if code_file.filename.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(buf)) as z:
                for n in z.namelist():
                    if n.endswith(('.py','.js','.ts','.java','.cs')): c_text += z.read(n).decode(errors='ignore')
        else: c_text = buf.decode(errors='ignore')
    if doc_file:
        buf = await doc_file.read()
        d_text = buf.decode(errors='ignore')
    
    res = engine.audit(c_text, d_text)
    return get_html(res)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
