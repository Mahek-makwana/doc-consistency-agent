
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

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    code_file: UploadFile = File(None),
    doc_file: UploadFile = File(None),
    code_text: str = Form(None),
    doc_text: str = Form(None)
):
    # Process Code
    final_code = ""
    if code_file and code_file.filename:
        content = await code_file.read()
        final_code = content.decode("utf-8")
    elif code_text:
        final_code = code_text
        
    # Process Doc
    final_doc = ""
    if doc_file and doc_file.filename:
        content = await doc_file.read()
        final_doc = content.decode("utf-8")
    elif doc_text:
        final_doc = doc_text
    
    # Run Analysis
    result = None
    if final_code or final_doc:
        print(f"DEBUG ANALYSIS START")
        print(f"Code Length: {len(final_code)}")
        print(f"Doc Length: {len(final_doc)}")
        print(f"Code Snippet: {final_code[:50].replace(chr(10), ' ')}...")
        print(f"Doc Snippet: {final_doc[:50].replace(chr(10), ' ')}...")
        
        # Avoid crashing if empty
        result = symmetric_analysis(final_code or "", final_doc or "")
        print(f"Result: {result}")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "code": final_code,
        "doc": final_doc
    })

if __name__ == "__main__":
    # Get port from environment variable for cloud deployment
    port = int(os.environ.get("PORT", 8000))
    # Using 0.0.0.0 to allow external traffic in hosted environments
    uvicorn.run(app, host="0.0.0.0", port=port)
