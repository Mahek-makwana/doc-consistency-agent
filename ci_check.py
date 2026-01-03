
import sys
import os

# Ensure project root is in sys.path
# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agent.stat_analysis import symmetric_analysis
from src.utils.file_detector import list_python_files, list_markdown_files
from src.utils.file_loader import FileLoader

def main():
    print("Starting CI Documentation Consistency Check...")
    
    CODE_PATH = os.path.join(PROJECT_ROOT, "src")
    DOC_PATH = os.path.join(PROJECT_ROOT, "docs")
    
    # 1. Load Texts
    print(f"Loading files from {CODE_PATH} and {DOC_PATH}...")
    py_files = list_python_files(CODE_PATH)
    md_files = list_markdown_files(DOC_PATH)
    
    if not py_files:
        print("No Python files found.")
        sys.exit(0) # Or 1?
        
    code_text = ""
    for p in py_files:
        try:
            code_text += FileLoader.load(str(p)) + "\n"
        except Exception:
            pass
            
    doc_text = ""
    for p in md_files:
        try:
            doc_text += FileLoader.load(str(p)) + "\n"
        except Exception:
            pass
            
    # 2. Analyze
    if not doc_text.strip():
        print("WARNING: No documentation text found!")
        # We might want to fail here
        sys.exit(1)

    result = symmetric_analysis(code_text, doc_text)
    
    print("\n" + "="*60)
    print("        CRAFTAI - DOCSYNC AGENT REPORT")
    print("="*60)
    print(f"Forward Match (Code->Doc): {result['forward_match']:.4f}")
    print(f"Backward Match (Doc->Code): {result['backward_match']:.4f}")
    print(f"Symmetric Score:           {result['symmetric_score']:.4f}")
    print(f"Status:                    {result['match_icon']} {result['match_label']}")
    print("-" * 60)
    
    if result['details']['suggestions']:
        print("\n💡 ACTIONABLE SUGGESTIONS:")
        for sugg in result['details']['suggestions']:
            print(f"  • {sugg}")
    
    print("-" * 60)
    print(f"Common Keywords: {', '.join(result['details']['common_words'][:10])}...")
    print("=" * 60 + "\n")
    
    # 3. Decision
    THRESHOLD = 0.15
    if result["symmetric_score"] < THRESHOLD:
        print(f"❌ FAILED: Consistency score {result['symmetric_score']:.4f} is below threshold {THRESHOLD}")
        sys.exit(1)
    else:
        print("✅ PASSED: Documentation consistency is acceptable.")
        sys.exit(0)

if __name__ == "__main__":
    main()
