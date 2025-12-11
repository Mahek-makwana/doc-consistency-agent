import sys, os
# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from src.agent.stat_analysis import StatisticalAnalyzer, symmetric_analysis

class TestStatisticalAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = StatisticalAnalyzer()

    def test_exact_match(self):
        text = "This is a sample function."
        score = self.analyzer.compute_similarity(text, text)
        self.assertAlmostEqual(score, 1.0, places=4)

    def test_complete_mismatch(self):
        # Using completely different words to ensure low similarity
        # "apple banana" vs "space rocket" should have no overlap in simple bag-of-words
        t1 = "apple banana fruit"
        t2 = "space rocket galaxy"
        score = self.analyzer.compute_similarity(t1, t2)
        # It's possible to get 0.0
        self.assertEqual(score, 0.0)

    def test_partial_match(self):
        t1 = "calculate euclidean distance"
        t2 = "compute euclidean distance"
        score = self.analyzer.compute_similarity(t1, t2)
        self.assertTrue(0.0 < score < 1.0)
        self.assertGreater(score, 0.5)

    def test_symmetric_analysis(self):
        code = "def compute_sum(a, b): return a + b"
        doc = "This function is used to compute_sum of two numbers."
        result = self.analyzer.symmetric_analysis(code, doc)
        
        self.assertIn("forward_match", result)
        self.assertIn("backward_match", result)
        self.assertIn("symmetric_score", result)
        self.assertIn("match_label", result)
        self.assertGreater(result["symmetric_score"], 0.0)

    def test_empty_input(self):
        score = self.analyzer.compute_similarity("", "something")
        self.assertEqual(score, 0.0)

    def test_legacy_wrapper(self):
        # Ensure the standalone function still works
        result = symmetric_analysis("test", "test")
        self.assertAlmostEqual(result["symmetric_score"], 1.0)

if __name__ == '__main__':
    unittest.main()
