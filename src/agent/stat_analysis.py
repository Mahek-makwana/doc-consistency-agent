from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class StatisticalAnalyzer:
    """
    Advanced Statistical Text Alignment Engine.
    Optimized for software engineering documentation.
    """

    def __init__(self):
        # Professional Stopwords: Ignore filler words that drag down scores
        self.stop_words = [
            'this', 'function', 'a', 'an', 'the', 'is', 'are', 'to', 'of', 'for', 
            'in', 'with', 'it', 'and', 'from', 'into', 'that', 'which', 'who', 
            'whose', 'whom', 'where', 'when', 'why', 'how', 'its', 'as', 'at', 
            'by', 'be', 'been', 'being', 'can', 'could', 'do', 'does', 'did', 
            'done', 'doing', 'has', 'have', 'had', 'having', 'will', 'would', 
            'should', 'may', 'might', 'must', 'shall', 'should', 'about', 'above', 
            'below', 'under', 'over', 'again', 'once', 'then', 'else', 'or', 
            'but', 'so', 'than', 'while', 'module', 'class', 'method', 'returns',
            'returning', 'takes', 'inputs', 'output', 'computes', 'calculates',
            'performing', 'process', 'using', 'used', 'base', 'price' # Some domain words are better kept, but filler isn't
        ]

        self.vectorizer = TfidfVectorizer(
            token_pattern=r"(?u)\b\w\w+\b",
            use_idf=False,
            norm='l2',
            sublinear_tf=True,
            stop_words=self.stop_words
        )
        
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

    def preprocess(self, text: str) -> str:
        """
        Cleans text and separates code identifiers (e.g. calcPrice -> calc price).
        """
        # Lowercase
        text = text.lower()
        # Handle snake_case and camelCase partially by replacing underscores
        text = text.replace("_", " ")
        # Separate symbols
        text = re.sub(r'[()\[\]{}:,.=;\'"]', " ", text)
        # Remove numbers
        text = re.sub(r'\b\d+\b', '', text)
        return text

    def _check_operational_alignment(self, code: str, doc: str) -> List[str]:
        gaps = []
        code_lower = code.lower()
        doc_lower = doc.lower()
        for trigger, synonyms in self.operational_map.items():
            if trigger in code_lower:
                found = any(s in doc_lower for s in synonyms) or (trigger in doc_lower)
                if not found:
                    gaps.append(f"Operational Gap: Code uses '{trigger}' but docs don't mention {synonyms[0]}.")
        return gaps

    def compute_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        if not text1.strip() or not text2.strip():
            return {"score": 0.0, "common_words": [], "missing_in_code": [], "missing_in_doc": [], "suggestions": ["Input missing."]}
        
        try:
            t1 = self.preprocess(text1)
            t2 = self.preprocess(text2)
            
            vectors = self.vectorizer.fit_transform([t1, t2])
            feature_names = self.vectorizer.get_feature_names_out()
            
            if len(feature_names) == 0:
                return {
                    "score": 0.0, 
                    "common_words": [], 
                    "missing_in_code": [], 
                    "missing_in_doc": [], 
                    "suggestions": ["No meaningful words found for analysis. Please check your input."]
                }

            raw_similarity = float(cosine_similarity(vectors[0], vectors[1])[0][0])
            score = min(1.0, raw_similarity * 1.5)
            dense = vectors.toarray()
            
            code_words = {feature_names[i] for i, val in enumerate(dense[0]) if val > 0}
            doc_words = {feature_names[i] for i, val in enumerate(dense[1]) if val > 0}
            
            common = code_words.intersection(doc_words)
            missing_in_code = doc_words - code_words
            missing_in_doc = code_words - doc_words
            
            suggestions = self._check_operational_alignment(text1, text2)
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
        
        if sim_score > 0.85:
            match_label = "Production Quality"
            icon = "💎"
        elif sim_score > 0.65:
            match_label = "High Alignment"
            icon = "✅"
        elif sim_score > 0.40:
            match_label = "Partial Alignment"
            icon = "⚠️"
        else:
            match_label = "Poor Alignment"
            icon = "❌"

        return {
            "forward_match": sim_score,
            "backward_match": sim_score,
            "symmetric_score": sim_score,
            "match_label": match_label,
            "match_icon": icon,
            "details": analysis
        }

def symmetric_analysis(code_text: str, doc_text: str):
    return StatisticalAnalyzer().symmetric_analysis(code_text, doc_text)

def compute_similarity(text1: str, text2: str):
    return StatisticalAnalyzer().compute_similarity(text1, text2)
