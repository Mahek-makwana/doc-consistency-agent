from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import zipfile
import io
import re
from src.agent.stat_analysis import symmetric_analysis
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple Server-Side Persistence for Demo
history_log = []

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
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "history": history_log})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, code_file: UploadFile = File(None), doc_file: UploadFile = File(None)):
    code_ex = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go']
    doc_ex = ['.md', '.txt', '.rst']

    code_map = {}
    doc_map = {}
    
    filename = code_file.filename if code_file else "Unknown Project"

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
        return templates.TemplateResponse("index.html", {"request": request, "result": "no_input", "history": history_log})

    # Perform Structural Analysis
    analysis = symmetric_analysis("\n".join(code_map.values()), "\n".join(doc_map.values()))
    
    # Store in History for the "History" button to work
    report_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": filename,
        "score": analysis["score"],
        "status": analysis["label"],
        "files_count": len(code_map)
    }
    history_log.insert(0, report_entry) # Most recent first

    # Clean up history to keep it fast
    if len(history_log) > 10:
        history_log.pop()

    analysis["file_list"] = list(code_map.keys())
    
    return templates.TemplateResponse("index.html", {"request": request, "result": analysis, "history": history_log})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
