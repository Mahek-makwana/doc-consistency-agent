
import sys, os
# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline.pipeline_logic import run_consistency_check

def test_local_pipeline():
    print("Testing pipeline logic locally...")
    code = "def foo(): pass"
    doc = "function foo does nothing"
    
    result = run_consistency_check(code, doc)
    print("Pipeline Result:", result)
    
    assert "symmetric_score" in result
    print("Local pipeline logic verification PASSED.")

if __name__ == "__main__":
    test_local_pipeline()
