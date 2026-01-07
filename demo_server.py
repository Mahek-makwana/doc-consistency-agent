from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import zipfile
import io
import ast
import re
from src.agent.stat_analysis import symmetric_analysis

app = FastAPI(title="CraftAI - DocSync Agent")
templates = Jinja2Templates(directory="templates")

# --- CORE UTILS ---
async def extract_from_zip(zip_content, target_extensions):
    file_map = {}
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for name in z.namelist():
                if name.endswith('/'): continue
                if any(name.lower().endswith(ext.lower()) for ext in target_extensions):
                    with z.open(name) as f:
                        file_map[name] = f.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Zip extraction error: {e}")
    return file_map

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    code_file: UploadFile = File(None),
    doc_file: UploadFile = File(None)
):
    code_ex = ['.py', '.js', '.java', '.cpp', '.cs', '.go']
    doc_ex = ['.md', '.txt', '.rst']

    code_map = {}
    doc_map = {}
    
    # 1. Extraction Logic (Multi-Doc Support)
    if code_file and code_file.filename:
        c_bytes = await code_file.read()
        if code_file.filename.lower().endswith('.zip'):
            code_map = await extract_from_zip(c_bytes, code_ex)
            # Find docs inside code if not separate
            if not doc_file or not doc_file.filename:
                doc_map.update(await extract_from_zip(c_bytes, doc_ex))
        else:
            code_map[code_file.filename] = c_bytes.decode("utf-8", errors="ignore")

    if doc_file and doc_file.filename:
        d_bytes = await doc_file.read()
        if doc_file.filename.lower().endswith('.zip'):
            doc_map.update(await extract_from_zip(d_bytes, doc_ex))
        else:
            doc_map[doc_file.filename] = d_bytes.decode("utf-8", errors="ignore")

    if not code_map:
        return templates.TemplateResponse("index.html", {"request": request, "result": "no_input"})

    # 2. Consistency Analysis (Terminology & Logic)
    final_code = "\n".join(code_map.values())
    final_doc = "\n".join(doc_map.values())
    
    # Extract terms for Terminology Check
    code_terms = set(re.findall(r'\b[a-z_][a-z0-9_]{3,}\b', final_code.lower()))
    doc_terms = set(re.findall(r'\b[a-z_][a-z0-9_]{3,}\b', final_doc.lower()))
    
    # Semantic Check
    analysis = symmetric_analysis(final_code, final_doc)
    
    # 3. Create Comprehensive Result
    result = {
        "score": int(analysis['symmetric_score'] * 100),
        "label": analysis['match_label'],
        "icon": analysis['match_icon'],
        "summary": analysis['analysis_summary'],
        "stats": {
            "files": len(code_map) + len(doc_map),
            "common_terms": len(code_terms & doc_terms),
            "logic_gaps": analysis['issue_summary']['categories']['logic_gaps']
        },
        "visual": analysis['visual_data']['values'],
        "suggestions": analysis['details']['suggestions'][:3],
        "file_list": list(code_map.keys())[:5],
        "export_raw": f"Score: {analysis['symmetric_score']}\n{analysis['analysis_summary']}"
    }

    return templates.TemplateResponse("index.html", {"request": request, "result": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
