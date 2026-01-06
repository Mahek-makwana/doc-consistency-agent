
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from src.agent.stat_analysis import symmetric_analysis
import ast
import re

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

    # 1. Read files into memory once
    c_file_data = await code_file.read() if code_file and code_file.filename else None
    d_file_data = await doc_file.read() if doc_file and doc_file.filename else None

    code_map = {} # {filename: content}
    doc_map = {}

    # 2. Extract Data
    if code_text:
        code_map["manual_input.py"] = code_text
    if doc_text:
        doc_map["manual_input.md"] = doc_text

    if c_file_data:
        if code_file.filename.lower().endswith('.zip'):
            extracted = await extract_from_zip(c_file_data, code_ex)
            code_map.update(extracted)
            if not d_file_data and not doc_text:
                doc_map.update(await extract_from_zip(c_file_data, doc_ex))
        else:
            code_map[code_file.filename] = c_file_data.decode("utf-8", errors="ignore")

    if d_file_data:
        if doc_file.filename.lower().endswith('.zip'):
            extracted = await extract_from_zip(d_file_data, doc_ex)
            doc_map.update(extracted)
            if not c_file_data and not code_text:
                code_map.update(await extract_from_zip(d_file_data, code_ex))
        else:
            doc_map[doc_file.filename] = d_file_data.decode("utf-8", errors="ignore")

    # 3. Aggregate for Statistical Analysis
    final_code_text = "\n".join(code_map.values())
    final_doc_text = "\n".join(doc_map.values())

    # 4. Structural Analysis (Reference Match Logic)
    from src.utils.python_parser import parse_python_file
    from src.utils.doc_parser import extract_documented_items
    import tempfile
    
    code_elements = {"functions": set(), "classes": set(), "methods": set()}
    doc_elements = {"functions": set(), "classes": set()}

    for fname, content in code_map.items():
        if fname.endswith('.py'):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        code_elements["functions"].add(node.name)
                    if isinstance(node, ast.ClassDef):
                        code_elements["classes"].add(node.name)
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                code_elements["methods"].add(f"{node.name}.{item.name}")
            except: pass

    for fname, content in doc_map.items():
        if fname.endswith('.md') or fname.endswith('.txt'):
            # Naive detection for names in headers
            headers = re.findall(r'##\s+([\w\.]+)', content)
            doc_elements["functions"].update(headers)
            doc_elements["classes"].update(headers)

    missing_struct = {
        "functions": sorted(list(code_elements["functions"] - doc_elements["functions"]))[:10],
        "classes": sorted(list(code_elements["classes"] - doc_elements["classes"]))[:10],
        "methods": sorted(list(code_elements["methods"] - doc_elements["functions"]))[:10]
    }

    # Run Analysis
    result = None
    if final_code_text.strip() or final_doc_text.strip():
        result = symmetric_analysis(final_code_text, final_doc_text)
        result["structural"] = {
            "files_analyzed": len(code_map) + len(doc_map),
            "missing_functions_count": len(code_elements["functions"] - doc_elements["functions"]),
            "missing_classes_count": len(code_elements["classes"] - doc_elements["classes"]),
            "missing_methods_count": len(code_elements["methods"] - doc_elements["functions"]),
            "missing_items": missing_struct
        }
        # Override score if structural gaps are huge
        struct_issues = result["structural"]["missing_functions_count"] + result["structural"]["missing_classes_count"]
        if struct_issues > 5:
            result["symmetric_score"] *= 0.8 # Documentation tax for missing elements
            result["match_label"] = "Needs Work (Structural Gaps)"
    else:
        result = {
            "forward_match": 0, "backward_match": 0, "symmetric_score": 0,
            "match_label": "No Input", "match_icon": "❓",
            "details": {"suggestions": ["Provide code/docs."], "common_words": [], "missing_in_code": [], "missing_in_doc": []}
        }
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "code": "[ZIP Content Extracted]" if c_file_data and code_file.filename.lower().endswith('.zip') else final_code_text[:500],
        "doc": "[ZIP Content Extracted]" if d_file_data and doc_file.filename.lower().endswith('.zip') else final_doc_text[:500]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
