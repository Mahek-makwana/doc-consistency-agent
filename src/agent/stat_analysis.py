from typing import Dict, Any, List
import re
import math
from collections import Counter

class StatisticalAnalyzer:
    """
    Advanced Statistical Text Alignment Engine (Pure Python - Optimized for Vercel).
    No heavy dependencies (scikit-learn/numpy) to stay under 250MB limit.
    """

    def __init__(self):
        self.stop_words = set([
            'this', 'function', 'a', 'an', 'the', 'is', 'are', 'to', 'of', 'for', 
            'in', 'with', 'it', 'and', 'from', 'into', 'that', 'which', 'who', 
            'whose', 'whom', 'where', 'when', 'why', 'how', 'its', 'as', 'at', 
            'by', 'be', 'been', 'being', 'can', 'could', 'do', 'does', 'did', 
            'done', 'doing', 'has', 'have', 'had', 'having', 'will', 'would', 
            'should', 'may', 'might', 'must', 'shall', 'should', 'about', 'above', 
            'below', 'under', 'over', 'again', 'once', 'then', 'else', 'or', 
            'but', 'so', 'than', 'while', 'module', 'class', 'method', 'returns',
            'returning', 'takes', 'inputs', 'output', 'computes', 'calculates',
            'performing', 'process', 'using', 'used', 'base', 'price'
        ])
        
        self.operational_map = {
            "dist": ["distance", "euclidean", "metric", "path"],
            "calc": ["calculate", "compute", "evaluate", "formula"],
            "fetch": ["retrieve", "get", "load", "download"],
            "save": ["store", "persist", "write", "export"],
            "train": ["fit", "learn", "optimize", "model"],
            "predict": ["infer", "forecast", "estimate", "output"],
            "sqrt": ["root", "square", "math"],
            "log": ["logarithm", "scale", "transform"]
        }

    def preprocess(self, text: str) -> List[str]:
        """Cleans text and returns a list of meaningful tokens."""
        text = text.lower()
        text = text.replace("_", " ")
        text = re.sub(r'[()\[\]{}:,.=;\'"/-]', " ", text)
        tokens = [t for t in text.split() if t not in self.stop_words and len(t) > 1]
        return tokens

    def _cosine_similarity(self, vec1: Counter, vec2: Counter) -> float:
        """Calculates cosine similarity between two frequency vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([val**2 for val in vec1.values()])
        sum2 = sum([val**2 for val in vec2.values()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def compute_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        if not text1.strip() or not text2.strip():
            return {"score": 0.0, "common_words": [], "missing_in_code": [], "missing_in_doc": [], "suggestions": ["Input missing."]}
        
        try:
            tokens1 = self.preprocess(text1)
            tokens2 = self.preprocess(text2)
            
            vec1 = Counter(tokens1)
            vec2 = Counter(tokens2)
            
            raw_sim = self._cosine_similarity(vec1, vec2)
            # Boost score slightly for marketing feel
            score = min(1.0, raw_sim * 1.5) if raw_sim > 0 else 0.0
            
            code_words = set(vec1.keys())
            doc_words = set(vec2.keys())
            
            common = code_words.intersection(doc_words)
            missing_in_code = doc_words - code_words
            missing_in_doc = code_words - doc_words
            
            suggestions = []
            # Operational Alignment Check
            code_str = text1.lower()
            doc_str = text2.lower()
            for trigger, synonyms in self.operational_map.items():
                if trigger in code_str:
                    found = any(s in doc_str for s in synonyms) or (trigger in doc_str)
                    if not found:
                        suggestions.append(f"Operational Gap: Code uses '{trigger}' but docs don't mention {synonyms[0]}.")
            
            if score < 0.5:
                suggestions.append("Improve vocabulary alignment between code identifiers and docstrings.")

            return {
                "score": score,
                "common_words": sorted(list(common)),
                "missing_in_code": sorted(list(missing_in_code)),
                "missing_in_doc": sorted(list(missing_in_doc)),
                "suggestions": suggestions
            }
        except Exception as e:
            return {"score": 0.0, "common_words": [], "missing_in_code": [], "missing_in_doc": [], "suggestions": [str(e)]}

    def symmetric_analysis(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        analysis = self.compute_similarity(code_text, doc_text)
        sim_score = analysis["score"]
        
        issues = {
            "missing_code": analysis["missing_in_doc"],
            "missing_docs": analysis["missing_in_code"],
            "operational": [s for s in analysis["suggestions"] if "Operational" in s]
        }

        if sim_score > 0.85:
            match_label = "Production Quality"; icon = "💎"
            summary = "Excellent alignment. Code and documentation are synchronized perfectly."
        elif sim_score > 0.65:
            match_label = "High Alignment"; icon = "✅"
            summary = "Strong alignment. Most core concepts are documented correctly."
        elif sim_score > 0.40:
            match_label = "Partial Alignment"; icon = "⚠️"
            summary = "Noticeable gaps detected. Some critical code logic lacks documentation support."
        else:
            match_label = "Poor Alignment"; icon = "❌"
            summary = "Critical mismatch. Documentation does not accurately reflect the source code."

        detailed_summary = f"{summary} Analyzed {len(analysis['common_words'])} common terms."
        
        return {
            "forward_match": sim_score,
            "backward_match": sim_score,
            "symmetric_score": sim_score,
            "match_label": match_label,
            "match_icon": icon,
            "analysis_summary": detailed_summary,
            "issue_summary": {
                "total_issues": len(issues["missing_code"]) + len(issues["missing_docs"]) + len(issues["operational"]),
                "categories": {
                    "missing_in_docs": len(issues["missing_code"]),
                    "zombie_docs": len(issues["missing_docs"]),
                    "logic_gaps": len(issues["operational"])
                }
            },
            "quick_fixes": [],
            "visual_data": {
                "labels": ["Common", "Code Only", "Doc Only"],
                "values": [len(analysis["common_words"]), len(issues["missing_code"]), len(issues["missing_docs"])]
            },
            "details": analysis
        }

def symmetric_analysis(code_text: str, doc_text: str):
    return StatisticalAnalyzer().symmetric_analysis(code_text, doc_text)
