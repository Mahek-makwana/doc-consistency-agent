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
    analysis_logs = []

    # 1. Process Code Input
    if code_file and code_file.filename:
        c_bytes = await code_file.read()
        analysis_logs.append(f"Detected Code Source: {code_file.filename}")
        if code_file.filename.lower().endswith('.zip'):
            extracted_code = await extract_from_zip(c_bytes, code_ex)
            code_map.update(extracted_code)
            analysis_logs.append(f"Extracted {len(extracted_code)} code files from ZIP.")
            # Peek for docs in same zip
            extracted_docs = await extract_from_zip(c_bytes, doc_ex)
            doc_map.update(extracted_docs)
            if extracted_docs:
                analysis_logs.append(f"Found {len(extracted_docs)} documentation files inside Project ZIP.")
        else:
            code_map[code_file.filename] = c_bytes.decode("utf-8", errors="ignore")

    # 2. Process Doc Input
    if doc_file and doc_file.filename:
        d_bytes = await doc_file.read()
        analysis_logs.append(f"Detected Doc Source: {doc_file.filename}")
        if doc_file.filename.lower().endswith('.zip'):
            extracted = await extract_from_zip(d_bytes, doc_ex)
            doc_map.update(extracted)
            analysis_logs.append(f"Extracted {len(extracted)} external documentation files.")
        else:
            doc_map[doc_file.filename] = d_bytes.decode("utf-8", errors="ignore")

    if not code_map:
        return templates.TemplateResponse("index.html", {"request": request, "result": "no_input"})

    # 3. Structural Engine (Multi-Language) & Error Detection
    code_elements = {"functions": {}, "classes": {}} # name -> filename mapping
    parsing_errors = []

    for fname, content in code_map.items():
        if fname.endswith('.py'):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        code_elements["functions"][node.name] = fname
                    if isinstance(node, ast.ClassDef):
                        code_elements["classes"][node.name] = fname
            except Exception as e:
                parsing_errors.append(f"Syntax Error in {fname}: {str(e)}")
        else:
            # Generic Scanner
            classes = re.findall(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', content)
            for c in classes: code_elements["classes"][c] = fname
            
            funcs = re.findall(r'(?:public|private|static|\s)+[\w\<\>]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', content)
            for f in funcs: code_elements["functions"][f] = fname

    # 4. Doc Engine
    doc_elements = {"items": set()}
    for fname, content in doc_map.items():
        items = re.findall(r'(?:#+|\*\*|`)\s*([\w\.]+)', content)
        doc_elements["items"].update(items)

    # Calculate Gaps with File Origins
    missing_items = []
    total_found_in_code = list(code_elements["functions"].keys()) + list(code_elements["classes"].keys())
    
    for item in total_found_in_code:
        if item not in doc_elements["items"]:
            origin = code_elements["functions"].get(item) or code_elements["classes"].get(item)
            missing_items.append({"name": item, "file": origin})

    # 5. Semantic Analysis
    final_code_text = "\n".join(code_map.values())
    final_doc_text = "\n".join(doc_map.values())
    analysis = symmetric_analysis(final_code_text, final_doc_text)

    # 6. Build Detailed Result
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
        "detailed_missing": missing_items[:15], # Show more details
        "parsing_errors": parsing_errors,
        "analysis_logs": analysis_logs,
        "files_list": list(code_map.keys()) + list(doc_map.keys()),
        "export_raw": f"Score: {analysis['symmetric_score']}\nStatus: {analysis['match_label']}\n{analysis['analysis_summary']}"
    }

    return templates.TemplateResponse("index.html", {"request": request, "result": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
