from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import zipfile
import io
import re
from typing import Dict, Any, List, Set
from datetime import datetime

app = FastAPI()

# --- VERCEL STABILITY CONFIG ---
# Use absolute path for templates to avoid 500 errors in serverless functions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

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

        return {
            "score": score,
            "label": "Accurate Alignment" if score > 70 else "Partial Mismatch" if score > 30 else "Critical Mismatch",
            "stats": {"issues": len(missing), "synced": len(synced)},
            "detail": f"Audit of {len(found_logic)} elements complete. {len(missing)} gaps found.",
            "visual": [len(synced), len(missing)],
            "terminology_score": score,
            "style_score": 100 - (len(missing) % 15),
            "docs_analyzed": 1,
            "suggestion": f"Add docstrings for {list(missing)[0]}" if missing else "Optimize imports"
        }

    def _empty_result(self):
        return {"score": 0, "label": "No Logic", "stats": {"issues": 0, "synced": 0}, "detail": "Upload files to begin.", "visual": [0, 1], "terminology_score": 0, "style_score": 0}

engine = EnterpriseDocSyncEngine()

# --- UTILS ---
async def extract_all(file_bytes, extensions):
    content = ""
    try:
        if file_bytes[:4] == b'PK\x03\x04':
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                for name in z.namelist():
                    if any(name.lower().endswith(ext) for ext in extensions):
                        with z.open(name) as f:
                            content += f.read().decode("utf-8", errors="ignore") + "\n"
    except:
        pass
    return content

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "active_view": "dashboard"})

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok", "timestamp": datetime.now().isoformat()})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, code_file: UploadFile = File(None), doc_file: UploadFile = File(None)):
    code_ex = ['.py', '.js', '.ts', '.java', '.cs']
    doc_ex = ['.md', '.txt']
    
    code_text = ""
    doc_text = ""
    c_name = code_file.filename if code_file else "None"
    
    if code_file and code_file.filename:
        c_bytes = await code_file.read()
        if code_file.filename.lower().endswith('.zip'):
            code_text = await extract_all(c_bytes, code_ex)
        else:
            code_text = c_bytes.decode("utf-8", errors="ignore")

    if doc_file and doc_file.filename:
        d_bytes = await doc_file.read()
        if doc_file.filename.lower().endswith('.zip'):
            doc_text = await extract_all(d_bytes, doc_ex)
        else:
            doc_text = d_bytes.decode("utf-8", errors="ignore")

    if not code_text:
        return templates.TemplateResponse("index.html", {"request": request, "result": {"error": "no_input"}, "active_view": "dashboard"})

    res = engine.perform_audit(code_text, doc_text)
    res.update({"filename": c_name})
    
    return templates.TemplateResponse("index.html", {"request": request, "result": res, "active_view": "dashboard"})
