from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import zipfile
import io
import ast
import re
from src.agent.stat_analysis import symmetric_analysis

app = FastAPI(title="CraftAI - DocSync Professional")
templates = Jinja2Templates(directory="templates")

# --- UTILS ---
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

# --- CORE ENDPOINT ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    code_file: UploadFile = File(None),
    doc_file: UploadFile = File(None)
):
    code_ex = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb']
    doc_ex = ['.md', '.txt', '.rst', '.html']

    code_map = {}
    doc_map = {}

    # 1. Process Code Input
    if code_file and code_file.filename:
        c_bytes = await code_file.read()
        if code_file.filename.lower().endswith('.zip'):
            code_map = await extract_from_zip(c_bytes, code_ex)
            # Peek for docs in same zip
            doc_map.update(await extract_from_zip(c_bytes, doc_ex))
        else:
            code_map[code_file.filename] = c_bytes.decode("utf-8", errors="ignore")

    # 2. Process Doc Input
    if doc_file and doc_file.filename:
        d_bytes = await doc_file.read()
        if doc_file.filename.lower().endswith('.zip'):
            doc_map.update(await extract_from_zip(d_bytes, doc_ex))
        else:
            doc_map[doc_file.filename] = d_bytes.decode("utf-8", errors="ignore")

    if not code_map:
        return templates.TemplateResponse("index.html", {"request": request, "result": "no_input"})

    # 3. Structural Engine (Multi-Language)
    code_elements = {"functions": set(), "classes": set()}
    for fname, content in code_map.items():
        if fname.endswith('.py'):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)): code_elements["functions" if isinstance(node, ast.FunctionDef) else "classes"].add(node.name)
            except: pass
        else:
            # Generic Scanner
            classes = re.findall(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', content)
            code_elements["classes"].update(classes)
            funcs = re.findall(r'(?:public|private|static|\s)+[\w\<\>]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', content)
            code_elements["functions"].update(funcs)

    # 4. Doc Engine
    doc_elements = {"items": set()}
    for content in doc_map.values():
        items = re.findall(r'(?:#+|\*\*|`)\s*([\w\.]+)', content)
        doc_elements["items"].update(items)

    missing_items = (code_elements["functions"] | code_elements["classes"]) - doc_elements["items"]

    # 5. Semantic Analysis
    final_code_text = "\n".join(code_map.values())
    final_doc_text = "\n".join(doc_map.values())
    analysis = symmetric_analysis(final_code_text, final_doc_text)

    # 6. Build Result for "Figma" Frontend
    result = {
        "score": int(analysis['symmetric_score'] * 100),
        "label": analysis['match_label'],
        "icon": analysis['match_icon'],
        "summary": analysis['analysis_summary'],
        "stats": {
            "files": len(code_map) + len(doc_map),
            "logic_gaps": analysis['issue_summary']['categories']['logic_gaps'],
            "missing_in_docs": len(missing_items)
        },
        "visual": analysis['visual_data']['values'],
        "missing_list": sorted(list(missing_items))[:10],
        "export_raw": f"Score: {analysis['symmetric_score']}\nStatus: {analysis['match_label']}\n{analysis['analysis_summary']}"
    }

    return templates.TemplateResponse("index.html", {"request": request, "result": result})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
