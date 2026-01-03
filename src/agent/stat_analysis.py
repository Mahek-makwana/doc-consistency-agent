from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class StatisticalAnalyzer:
    """
    Core engine for statistical text alignment using Scikit-Learn.
    Features:
    - TF-IDF with log-scaling for keyword overlap.
    - Symmetric analysis (Code <-> Doc).
    - Operational alignment check (Intent detection).
    """

    def __init__(self):
        # We use use_idf=False because in a 2-document comparison, IDF penalizes 
        # words that appear in both (which is exactly what we WANT to match).
        # We want to measure vocabulary overlap magnitude.
        self.vectorizer = TfidfVectorizer(
            token_pattern=r"(?u)\b\w\w+\b",
            use_idf=False,
            norm='l2',
            sublinear_tf=True # Log scaling for TF (1+log(tf)) to reduce impact of repeated keywords
        )
        
        # Mapping of code-patterns to documentation-intent words
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
        Normalizes text by removing punctuation and code-specific noise.
        """
        # Lowercase
        text = text.lower()
        # Replace underscores with spaces (common in variable names vs descriptions)
        text = text.replace("_", " ")
        # Remove common code structural characters causing noise
        text = re.sub(r'[()\[\]{}:,.=;\'"]', " ", text)
        return text

    def _check_operational_alignment(self, code: str, doc: str) -> List[str]:
        """
        Specialized check for intent: if code does X, does doc say X?
        """
        gaps = []
        code_lower = code.lower()
        doc_lower = doc.lower()

        for trigger, synonyms in self.operational_map.items():
            if trigger in code_lower:
                # Code has the trigger, check if doc has ANY of the synonyms or the trigger itself
                found = any(s in doc_lower for s in synonyms) or (trigger in doc_lower)
                if not found:
                    gaps.append(f"Operational Gap: Code uses '{trigger}' but documentation doesn't mention related operations ({', '.join(synonyms[:2])}).")
        
        return gaps

    def compute_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Computes cosine similarity and performs symmetric gap analysis.
        """
        if not text1.strip() or not text2.strip():
            return {
                "score": 0.0,
                "common_words": [],
                "missing_in_code": [],
                "missing_in_doc": [],
                "suggestions": ["One or both input texts are empty."]
            }
        
        try:
            # Preprocess both inputs
            t1 = self.preprocess(text1)
            t2 = self.preprocess(text2)
            
            # Combine for vocabs
            vectors = self.vectorizer.fit_transform([t1, t2])
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
                
            # --- GAP ANALYSIS ---
            feature_names = self.vectorizer.get_feature_names_out()
            dense = vectors.toarray()
            
            # Identify which words are in T1 (code) and T2 (doc)
            code_words = {feature_names[i] for i, val in enumerate(dense[0]) if val > 0}
            doc_words = {feature_names[i] for i, val in enumerate(dense[1]) if val > 0}
            
            common = code_words.intersection(doc_words)
            missing_in_code = doc_words - code_words
            missing_in_doc = code_words - doc_words
            
            suggestions = self._check_operational_alignment(text1, text2)
            
            # General keyword suggestions
            if len(common) < 3 and similarity < 0.3:
                suggestions.append("Critical: Documentation lacks technical keywords from the code. Use code identifiers in docstrings.")
            
            if len(missing_in_doc) > 10:
                suggestions.append(f"Documentation might be incomplete. {len(missing_in_doc)} code terms are missing.")

            return {
                "score": float(similarity),
                "common_words": sorted(list(common)),
                "missing_in_code": sorted(list(missing_in_code)),
                "missing_in_doc": sorted(list(missing_in_doc)),
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "common_words": [],
                "missing_in_code": [],
                "missing_in_doc": [],
                "suggestions": [f"Error during analysis: {str(e)}"]
            }

    def symmetric_analysis(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        """
        Performs symmetric analysis and quality labeling.
        """
        # We now get a dict back from compute_similarity (which actually does the full analysis now)
        # We call it once because we analyze the PAIR.
        
        analysis = self.compute_similarity(code_text, doc_text)
        sim_score = analysis["score"]
        
        # Symmetric validation: Score represents bidirectional overlap since we don't use IDF
        # However, to be strictly symmetric, we ensure the score is consistent.
        
        if sim_score > 0.75:
            match_label = "Production Quality"
            icon = "💎"
        elif sim_score > 0.50:
            match_label = "High Alignment"
            icon = "✅"
        elif sim_score > 0.25:
            match_label = "Partial Alignment"
            icon = "⚠️"
        else:
            match_label = "Poor Alignment"
            icon = "❌"

        return {
            "forward_match": sim_score, # Code -> Doc
            "backward_match": sim_score, # Doc -> Code (identical in Cosine)
            "symmetric_score": sim_score,
            "match_label": match_label,
            "match_icon": icon,
            "details": analysis
        }

# Helper for backward compatibility or simple usage
def symmetric_analysis(code_text: str, doc_text: str):
    analyzer = StatisticalAnalyzer()
    return analyzer.symmetric_analysis(code_text, doc_text)

def compute_similarity(text1: str, text2: str):
    analyzer = StatisticalAnalyzer()
    return analyzer.compute_similarity(text1, text2)
