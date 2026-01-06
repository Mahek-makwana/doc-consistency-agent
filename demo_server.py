
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
    async def get_text(file: UploadFile, manual_text: str, extensions: list):
        if file and file.filename and file.filename.strip():
            try:
                content = await file.read()
                if not content:
                    return manual_text or ""
                    
                if file.filename.lower().endswith('.zip'):
                    # Process ZIP
                    zip_text = []
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        for name in z.namelist():
                            # Case-insensitive extension check
                            if any(name.lower().endswith(ext.lower()) for ext in extensions):
                                with z.open(name) as f:
                                    zip_text.append(f.read().decode("utf-8", errors="ignore"))
                    return "\n".join(zip_text)
                return content.decode("utf-8", errors="ignore")
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                return manual_text or ""
        return manual_text or ""

    # Process Code
    code_ex = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb', '.pyi']
    final_code = await get_text(code_file, code_text, code_ex)
    
    # Process Doc
    doc_ex = ['.md', '.txt', '.rst', '.html', '.htm', '.markdown']
    final_doc = await get_text(doc_file, doc_text, doc_ex)
    
    # Run Analysis
    result = None
    if final_code.strip() or final_doc.strip():
        result = symmetric_analysis(final_code, final_doc)
    else:
        # Provide a dummy result with an error message
        result = {
            "forward_match": 0,
            "backward_match": 0,
            "symmetric_score": 0,
            "match_label": "No Input",
            "match_icon": "❓",
            "details": {
                "suggestions": ["Please provide either source code or documentation (paste text or upload files)."],
                "common_words": [],
                "missing_in_code": [],
                "missing_in_doc": []
            }
        }
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "code": final_code if not code_file or not code_file.filename.strip().lower().endswith('.zip') else f"[ZIP: {len(final_code)} chars extracted]",
        "doc": final_doc if not doc_file or not doc_file.filename.strip().lower().endswith('.zip') else f"[ZIP: {len(final_doc)} chars extracted]"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
