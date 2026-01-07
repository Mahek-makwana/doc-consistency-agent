from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import zipfile
import io
import re
from typing import Dict, Any, List, Set

app = FastAPI()

# FIX: Use absolute path for Vercel to find templates reliably
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class EnterpriseDocSyncEngine:
    def __init__(self):
        self.patterns = {
            "logic": [
                r"def\s+([A-Za-z_]\w*)",           # Python
                r"function\s+([A-Za-z_]\w*)",      # JS/TS
                r"(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:\(.*\)|function)", # JS Arrow
                r"class\s+([A-Za-z_]\w*)",         # Classes
                r"(['\"]?[\w-]+['\"]?)\s*:",       # JS Object Keys
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
            issue_detail = f"CRITICAL GAP: The agent detected {len(found_logic)} logic entities, but NONE are described. High maintenance risk."
        elif score < 100:
            issue_detail = f"DOCUMENTATION DEBT: {len(missing)} specific entities are missing coverage. Undocumented areas: {', '.join(list(missing)[:3])}"
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
                "breakdown": {"Terminology": 100 - score, "Logic": len(missing) * 5}
            },
            "suggestions": [f"Add docstring for '{m}'" for m in list(missing)[:5]],
            "visual": [len(synced), len(missing), 2]
        }

    def _empty_result(self):
        return {
            "score": 0, "label": "No Logic Detected", "summary": "Scanning yielded no structural entities.",
            "detailed_issue": "REASON: File contains no standard functions, classes, or keys.",
            "stats": {"total_issues": 1, "synced_terms": 0, "breakdown": {"Terminology": 0, "Logic": 100}},
            "suggestions": ["Define logic to begin audit."],
            "visual": [0, 10, 0]
        }

def symmetric_analysis(code_text: str, doc_text: str):
    return EnterpriseDocSyncEngine().perform_audit(code_text, doc_text)

async def extract_all(file_bytes, extensions):
    file_map = {}
    if file_bytes[:4] == b'PK\x03\x04':
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            for info in z.infolist():
                if not info.is_dir() and any(info.filename.lower().endswith(e) for e in extensions):
                    with z.open(info.filename) as f:
                        file_map[info.filename] = f.read().decode("utf-8", errors="ignore")
    return file_map

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, code_file: UploadFile = File(None), doc_file: UploadFile = File(None)):
    code_ex = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go']
    doc_ex = ['.md', '.txt', '.rst']

    code_map, doc_map = {}, {}
    c_name = code_file.filename if code_file else ""
    d_name = doc_file.filename if doc_file else ""

    if code_file and code_file.filename:
        c_bytes = await code_file.read()
        if code_file.filename.lower().endswith('.zip'):
            code_map = await extract_all(c_bytes, code_ex)
            doc_map.update(await extract_all(c_bytes, doc_ex))
        else:
            code_map[code_file.filename] = c_bytes.decode("utf-8", errors="ignore")

    if doc_file and doc_file.filename:
        d_bytes = await doc_file.read()
        if doc_file.filename.lower().endswith('.zip'):
            doc_map.update(await extract_all(d_bytes, doc_ex))
        else:
            doc_map[doc_file.filename] = d_bytes.decode("utf-8", errors="ignore")

    if not code_map:
        return templates.TemplateResponse("index.html", {"request": request, "result": "no_input"})

    analysis = symmetric_analysis("\n".join(code_map.values()), "\n".join(doc_map.values()))
    analysis.update({"code_filename": c_name, "doc_filename": d_name, "file_list": list(code_map.keys())})
    
    return templates.TemplateResponse("index.html", {"request": request, "result": analysis})
