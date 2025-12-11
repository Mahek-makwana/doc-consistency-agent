import sys
import os
import argparse
import json
import uvicorn
from fastapi import FastAPI
from contextlib import redirect_stdout
import io

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.utils.consistency_checker import ConsistencyChecker
from src.agent.ai_suggester import suggest_documentation

# ---------------------------------------------------
# FastAPI App Construction
# ---------------------------------------------------
app = FastAPI(title="Doc Consistency Agent API")

@app.get("/")
def home():
    return {"message": "Doc Consistency Agent API is running"}

@app.post("/scan")
def run_scan_api():
    """
    API Endpoint to run the consistency check.
    """
    checker = ConsistencyChecker(code_dir="./src", doc_dir="./docs")
    results = checker.run_check()
    return results

# ---------------------------------------------------
# CLI / Pipeline Logic
# ---------------------------------------------------
def run_pipeline_mode(ci_mode=False):
    print("Starting Consistency Pipeline...")
    
    # 1. Initialize Checker
    # Adjust paths as needed based on where script is run
    code_dir = os.path.abspath("src")
    doc_dir = os.path.abspath("docs")
    
    if not os.path.exists(code_dir):
        print(f"Error: Code directory not found at {code_dir}")
        return
    
    checker = ConsistencyChecker(code_dir=code_dir, doc_dir=doc_dir)
    
    # 2. Run Analysis
    print("Running semantic analysis...")
    results = checker.run_check()
    
    # 3. Generate Report
    report_lines = []
    report_lines.append("# Documentation Consistency Report")
    report_lines.append(f"**Average Semantic Similarity:** {results['stats']['average_similarity']}")
    report_lines.append(f"**Documented Functions:** {results['stats']['total_documented']} / {results['stats']['total_functions']}")
    report_lines.append("\n## Detailed Matches")
    
    for match in results["matches"]:
        icon = "✅" if match["similarity_score"] > 0.7 else "⚠️" if match["similarity_score"] > 0.4 else "❌"
        report_lines.append(f"### {icon} {match['name']} (Score: {match['similarity_score']})")
        report_lines.append(f"- **Assessment**: {match['recommendation']}")
        
        miss_code = match['issues']['missing_in_code']
        miss_doc = match['issues']['missing_in_doc']
        
        if miss_code:
            report_lines.append(f"- **Missing in Code (present in doc)**: {', '.join(miss_code[:5])}")
        if miss_doc:
            report_lines.append(f"- **Missing in Doc (present in code)**: {', '.join(miss_doc[:5])}")
            
    report_lines.append("\n## Missing Code Implementation")
    for item in results["missing_code"]:
        report_lines.append(f"- {item}")
        
    report_lines.append("\n## Missing Documentation")
    suggestions = {}
    for item in results["missing_docs"]:
        report_lines.append(f"- {item} (Documentation needed)")
        # If CI mode, maybe generate suggestions here?
        # For now, just listing them.
        suggestions[item] = "TODO: Generate AI suggestion"

    # 4. Output Files
    output_dir = "output" if not ci_mode else "."
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, "report.md")
    json_path = os.path.join(output_dir, "suggestions.json")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2)
        
    print(f"Report generated at {report_path}")
    print(f"Suggestions generated at {json_path}")


def main():
    parser = argparse.ArgumentParser(description="Doc Consistency Agent")
    parser.add_argument("--mode", choices=["api", "pipeline"], default="api", help="Run mode")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode (output to root)")
    parser.add_argument("--git-ops", action="store_true", help="Enable automatic git branching and pushing")
    
    args, unknown = parser.parse_known_args()
    
    # Check if run by uvicorn (which passes no args usually, or handled by uvicorn)
    # If explicitly called with python main.py --mode pipeline
    # If explicitly called with python main.py --mode pipeline
    if args.mode == "pipeline" or args.ci:
        # Use the new Combined Idea 1+3 Pipeline
        from src.agent.pipeline import CraftAIPipeline
        pipeline = CraftAIPipeline(code_dir=os.path.abspath("src"), doc_dir=os.path.abspath("docs"))
        pipeline.run(perform_git_actions=args.git_ops)
    else:
        # Default to running API via uvicorn if main is executed directly for API
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
