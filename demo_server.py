from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import zipfile
import io
import ast
import re
from src.agent.stat_analysis import symmetric_analysis

app = FastAPI(title="CraftAI DocSync Enterprise")
templates = Jinja2Templates(directory="templates")

# --- ROBUST UTILS ---
async def extract_all_files(file_bytes, target_extensions):
    """Deep scans ZIPs or reads single files with robust error handling"""
    file_map = {}
    try:
        # Check if it's a ZIP by header
        if file_bytes[:4] == b'PK\x03\x04':
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                for info in z.infolist():
                    if info.is_dir(): continue
                    name = info.filename
                    # Deep scan for target extensions
                    if any(name.lower().endswith(ext.lower()) for ext in target_extensions):
                        with z.open(name) as f:
                            file_map[name] = f.read().decode("utf-8", errors="ignore")
        else:
            # Handle as single text file if not a ZIP
            # Note: We need a filename, but we only have bytes here.
            # In the main analyze function, we handle single file naming.
            pass 
    except Exception as e:
        print(f"Extraction error: {e}")
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
    code_ex = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs']
    doc_ex = ['.md', '.txt', '.rst', '.markdown']

    code_map = {}
    doc_map = {}
    logs = []

    # 1. PROCESS CODE / PROJECT SOURCE
    if code_file and code_file.filename:
        c_bytes = await code_file.read()
        if code_file.filename.lower().endswith('.zip'):
            code_map = await extract_all_files(c_bytes, code_ex)
            # PEER AT DOCS AUTOMATICALLY INSIDE THE CODE ZIP
            doc_map.update(await extract_all_files(c_bytes, doc_ex))
            logs.append(f"Auto-extracted {len(code_map)} logic files and {len(doc_map)} internal docs.")
        else:
            # Single file upload
            code_map[code_file.filename] = c_bytes.decode("utf-8", errors="ignore")
            logs.append(f"Detected single logic file: {code_file.filename}")

    # 2. PROCESS EXTERNAL DOCS (Optional)
    if doc_file and doc_file.filename:
        d_bytes = await doc_file.read()
        if doc_file.filename.lower().endswith('.zip'):
            extracted_docs = await extract_all_files(d_bytes, doc_ex)
            doc_map.update(extracted_docs)
            logs.append(f"Added {len(extracted_docs)} external documentation files.")
        else:
            doc_map[doc_file.filename] = d_bytes.decode("utf-8", errors="ignore")
            logs.append(f"Added manual doc: {doc_file.filename}")

    if not code_map:
        return templates.TemplateResponse("index.html", {"request": request, "result": "no_input"})

    # 3. SEMANTIC ANALYSIS
    final_code = "\n".join(code_map.values())
    final_doc = "\n".join(doc_map.values())
    
    # Run analysis
    analysis = symmetric_analysis(final_code, final_doc)
    
    # 4. PREPARE RESULTS
    result = {
        "score": int(analysis['symmetric_score'] * 100),
        "label": analysis['match_label'],
        "icon": analysis['match_icon'],
        "summary": analysis['analysis_summary'],
        "stats": {
            "files": len(code_map) + len(doc_map),
            "common_terms": len(set(re.findall(r'\w+', final_code.lower())) & set(re.findall(r'\w+', final_doc.lower()))),
            "logic_gaps": analysis['issue_summary']['categories']['logic_gaps']
        },
        "visual": analysis['visual_data']['values'],
        "suggestions": analysis['details']['suggestions'][:3],
        "file_list": list(code_map.keys())[:10],
        "logs": logs,
        "export_raw": f"CraftAI DocSync Report\nScore: {analysis['symmetric_score']}\nSummary: {analysis['analysis_summary']}"
    }

    return templates.TemplateResponse("index.html", {"request": request, "result": result})

if __name__ == "__main__":
    # Ensure it works on cloud ports (Vercel/Railway) or local 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
