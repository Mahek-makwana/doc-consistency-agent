
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from src.agent.stat_analysis import symmetric_analysis

app = FastAPI(title="CraftAI - DocSync Agent")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

import zipfile
import io

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    code_file: UploadFile = File(None),
    doc_file: UploadFile = File(None),
    code_text: str = Form(None),
    doc_text: str = Form(None)
):
    code_ex = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb', '.pyi']
    doc_ex = ['.md', '.txt', '.rst', '.html', '.htm', '.markdown']

    async def extract_from_zip(zip_content, target_extensions):
        extracted = []
        files_found = []
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
                for name in z.namelist():
                    if name.endswith('/'): continue # Skip directories
                    if any(name.lower().endswith(ext.lower()) for ext in target_extensions):
                        files_found.append(name)
                        with z.open(name) as f:
                            extracted.append(f.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            print(f"Zip extraction error: {e}")
        return "\n".join(extracted), files_found

    # 1. Read files into memory once to avoid stream exhaustion
    c_file_data = await code_file.read() if code_file and code_file.filename else None
    d_file_data = await doc_file.read() if doc_file and doc_file.filename else None

    final_code = code_text or ""
    final_doc = doc_text or ""
    local_code_files = []
    local_doc_files = []

    # 2. Logic for extraction
    if c_file_data:
        if code_file.filename.lower().endswith('.zip'):
            final_code, local_code_files = await extract_from_zip(c_file_data, code_ex)
            # SMART ZIP: If only one zip uploaded, check it for docs too
            if not d_file_data and not doc_text:
                final_doc, local_doc_files = await extract_from_zip(c_file_data, doc_ex)
        else:
            final_code = c_file_data.decode("utf-8", errors="ignore")
            local_code_files = [code_file.filename]

    if d_file_data:
        if doc_file.filename.lower().endswith('.zip'):
            final_doc, local_doc_files = await extract_from_zip(d_file_data, doc_ex)
            # SMART ZIP reverse: If only one zip uploaded for doc, check it for code
            if not c_file_data and not code_text:
                final_code, local_code_files = await extract_from_zip(d_file_data, code_ex)
        else:
            final_doc = d_file_data.decode("utf-8", errors="ignore")
            local_doc_files = [doc_file.filename]

    # Run Analysis
    result = None
    if final_code.strip() or final_doc.strip():
        result = symmetric_analysis(final_code, final_doc)
        result["local_files"] = {
            "code": local_code_files,
            "docs": local_doc_files
        }
    else:
        result = {
            "forward_match": 0, "backward_match": 0, "symmetric_score": 0,
            "match_label": "No Input", "match_icon": "❓",
            "details": {
                "suggestions": ["Please provide source code or documentation (zip or paste)."],
                "common_words": [], "missing_in_code": [], "missing_in_doc": []
            }
        }
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "code": "[ZIP Content Extracted]" if c_file_data and code_file.filename.lower().endswith('.zip') else final_code,
        "doc": "[ZIP Content Extracted]" if d_file_data and doc_file.filename.lower().endswith('.zip') else final_doc
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
