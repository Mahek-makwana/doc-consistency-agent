# src/agent/test_stat.py
import sys, os

# ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agent.stat_analysis import compute_similarity, symmetric_analysis

t1 = "this function computes euclidean distance between two vectors"
t2 = "compute the euclidean distance between vectors"

print("Test texts:")
print("  t1:", t1)
print("  t2:", t2)

sim = compute_similarity(t1, t2)
print("\ncompute_similarity result:", sim)

report = symmetric_analysis(t1, t2)
print("\nsymmetric_analysis result:")
print(report)
