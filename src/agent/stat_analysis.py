from typing import Dict, Any, List
import re
import math
from collections import Counter

class StatisticalAnalyzer:
    """
    Enterprise-Grade Consistency Engine.
    Provides accurate, dynamic counts for the Figma Dashboard.
    """

    def __init__(self):
        self.stop_words = set(['the', 'a', 'is', 'are', 'to', 'in', 'of', 'and', 'with', 'for', 'it', 'this', 'that'])
        
        # Categories for the "Issue Summary" bars
        self.category_keywords = {
            "Terminology": ["name", "term", "variable", "identifier", "call", "parameter"],
            "Style": ["format", "structure", "clean", "indent", "comment", "docstring"],
            "Logic": ["algorithm", "flow", "step", "calculation", "process", "sequence"]
        }

    def preprocess(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s_]', ' ', text)
        return [t for t in text.split() if t not in self.stop_words and len(t) > 1]

    def _cosine_similarity(self, vec1: Counter, vec2: Counter) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([val**2 for val in vec1.values()])
        sum2 = sum([val**2 for val in vec2.values()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        return float(numerator) / denominator if denominator else 0.0

    def symmetric_analysis(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        tokens_code = self.preprocess(code_text)
        tokens_doc = self.preprocess(doc_text)
        
        vec_code = Counter(tokens_code)
        vec_doc = Counter(tokens_doc)
        
        sim_score = self._cosine_similarity(vec_code, vec_doc)
        
        # Calculate Real Gaps
        code_words = set(vec_code.keys())
        doc_words = set(vec_doc.keys())
        
        missing_in_docs = code_words - doc_words
        zombie_docs = doc_words - code_words
        
        # Categorize Missing Items Dynamically
        breakdown = {"Terminology": 0, "Style": 0, "Logic": 0}
        for word in missing_in_docs:
            if any(k in word for k in self.category_keywords["Terminology"]): breakdown["Terminology"] += 1
            elif any(k in word for k in self.category_keywords["Style"]): breakdown["Style"] += 1
            else: breakdown["Logic"] += 1

        # Final Formatting
        if sim_score > 0.8: status = ("Excellent Alignment", "💎", "High")
        elif sim_score > 0.5: status = ("Moderate Alignment", "✅", "Medium")
        else: status = ("Critical Mismatch", "❌", "Low")

        return {
            "score": int(sim_score * 100),
            "label": status[0],
            "icon": status[1],
            "health": status[2],
            "summary": f"Audit complete. Verified {len(code_words)} logic elements against {len(doc_words)} documentation items.",
            "stats": {
                "total_issues": len(missing_in_docs) + len(zombie_docs),
                "logic_gaps": breakdown["Logic"],
                "synced_terms": len(code_words & doc_words),
                "breakdown": breakdown
            },
            "suggestions": [f"Align '{w}' in documentation" for w in list(missing_in_docs)[:5]],
            "visual": [len(code_words & doc_words), len(missing_in_docs), len(zombie_docs)]
        }

def symmetric_analysis(code_text: str, doc_text: str):
    return StatisticalAnalyzer().symmetric_analysis(code_text, doc_text)
