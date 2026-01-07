from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
import os
import zipfile
import io
import re
from typing import Dict, Any, List, Set
from jinja2 import Template

app = FastAPI()

# Manual Template Loading for Vercel Stability
def render_dashboard(request: Request, result: Any = None):
    # Get absolute path to template
    base_path = os.path.dirname(__file__)
    template_path = os.path.join(base_path, "templates", "index.html")
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Use Jinja2 to render the string directly
        # This bypasses the directory-scanning issues on Vercel
        template = Template(html_content)
        return template.render(request=request, result=result)
    except Exception as e:
        return f"<html><body><h1>Vercel Deployment Error</h1><p>Could not load template at {template_path}. Error: {str(e)}</p></body></html>"

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
        
        if not found_logic:
            return self._empty_result()

        synced = {l for l in found_logic if l.lower() in doc_pool}
        missing = found_logic - synced
        score = int((len(synced) / len(found_logic)) * 100)
        
        return {
            "score": score,
            "label": "Accurate Alignment" if score > 70 else "Partial Mismatch" if score > 30 else "Critical Mismatch",
            "summary": f"Audit of {len(found_logic)} elements complete.",
            "detailed_issue": f"Identified {len(missing)} logic gaps and {len(synced)} synced segments.",
            "stats": {
                "total_issues": len(missing),
                "synced_terms": len(synced),
                "breakdown": {"Terminology": 100 - score, "Logic": len(missing) * 5}
            },
            "suggestions": [f"Add documentation for '{m}'" for m in list(missing)[:3]],
            "visual": [len(synced), len(missing), 2]
        }

    def _empty_result(self):
        return {"score": 0, "label": "No Logic", "summary": "Empty scan.", "detailed_issue": "None", "stats": {"total_issues": 1, "synced_terms": 0, "breakdown": {"Terminology": 0, "Logic": 100}}, "suggestions": [], "visual": [0, 10, 0]}

def symmetric_analysis(c, d):
    return EnterpriseDocSyncEngine().perform_audit(c, d)

async def extract_all(b, e):
    m = {}
    if b[:4] == b'PK\x03\x04':
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            for i in z.infolist():
                if not i.is_dir() and any(i.filename.lower().endswith(ext) for ext in e):
                    with z.open(i.filename) as f:
                        m[i.filename] = f.read().decode("utf-8", errors="ignore")
    return m

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    content = render_dashboard(request, result=None)
    return HTMLResponse(content=content)

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, code_file: UploadFile = File(None), doc_file: UploadFile = File(None)):
    code_ex = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go']
    doc_ex = ['.md', '.txt', '.rst']
    code_map, doc_map = {}, {}
    c_n = code_file.filename if code_file else ""
    d_n = doc_file.filename if doc_file else ""

    if code_file and code_file.filename:
        b = await code_file.read()
        if code_file.filename.lower().endswith('.zip'):
            code_map = await extract_all(b, code_ex)
            doc_map.update(await extract_all(b, doc_ex))
        else:
            code_map[code_file.filename] = b.decode("utf-8", errors="ignore")

    if doc_file and doc_file.filename:
        b = await doc_file.read()
        if doc_file.filename.lower().endswith('.zip'):
            doc_map.update(await extract_all(b, doc_ex))
        else:
            doc_map[doc_file.filename] = b.decode("utf-8", errors="ignore")

    if not code_map:
        content = render_dashboard(request, result={"error": "no_input"})
        return HTMLResponse(content=content)

    res = symmetric_analysis("\n".join(code_map.values()), "\n".join(doc_map.values()))
    res.update({"code_filename": c_n, "doc_filename": d_n, "file_list": list(code_map.keys())})
    
    content = render_dashboard(request, result=res)
    return HTMLResponse(content=content)
