# main.py (FastAPI API)

import sys
import os
import io
import contextlib
from fastapi import FastAPI

# ---------------------------------------------------
# Ensure project root is in sys.path
# ---------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------
# Import scanner and similarity engine
# ---------------------------------------------------
from scanner_main import main_scan  # your full project scanner
from similarity_engine import check_documentation
from src.agent.stat_analysis import symmetric_analysis
from src.utils.file_loader import FileLoader
from src.utils.file_detector import list_python_files, list_markdown_files

# ---------------------------------------------------
# FastAPI app
# ---------------------------------------------------
app = FastAPI(title="Doc Consistency Agent API")


@app.get("/")
def home():
    return {"message": "Doc Consistency Agent API is running"}


@app.post("/scan")
def run_scan():
    """
    Runs the full project scan and returns:
      - Console output of main_scan()
      - Project-level statistical analysis
      - File counts
    """
    CODE_PATH = "./src"
    DOC_PATH = "./docs"

    py_files = list_python_files(CODE_PATH)
    md_files = list_markdown_files(DOC_PATH)

    # Load code and docs text
    code_text_parts = []
    for p in py_files:
        try:
            txt = FileLoader.load(str(p))
            code_text_parts.append(f"#FILE: {os.path.basename(str(p))}\n{txt}\n")
        except Exception as e:
            code_text_parts.append(f"#FILE_LOAD_ERROR: {str(p)} - {e}\n")

    doc_text_parts = []
    for p in md_files:
        try:
            txt = FileLoader.load(str(p))
            doc_text_parts.append(f"#DOC: {os.path.basename(str(p))}\n{txt}\n")
        except Exception as e:
            doc_text_parts.append(f"#DOC_LOAD_ERROR: {str(p)} - {e}\n")

    code_text = "\n".join(code_text_parts)
    doc_text = "\n".join(doc_text_parts)

    # Project-level statistical analysis
    stat_result = symmetric_analysis(code_text, doc_text)

    # Capture main_scan() output
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            main_scan()
        except Exception as e:
            print("ERROR during scan:", str(e))
    scanner_output = buffer.getvalue()

    return {
        "scan_output": scanner_output,
        "stats": stat_result,
        "file_counts": {
            "python_files": len(py_files),
            "markdown_files": len(md_files)
        }
    }


@app.post("/similarity")
def run_similarity(code: str, documentation: str):
    """
    Accepts raw code and documentation strings,
    returns a similarity score/report from similarity_engine.py
    """
    try:
        result = check_documentation(code, documentation)
        return {"similarity_result": result}
    except Exception as e:
        return {"error": str(e)}

