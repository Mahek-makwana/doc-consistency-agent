from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class StatisticalAnalyzer:
    """
    Core engine for statistical text alignment using Scikit-Learn.
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

    def preprocess(self, text: str) -> str:
        """
        Simple preprocessing to normalize text for comparison.
        """
        # Lowercase
        text = text.lower()
        # Replace underscores with spaces (common in variable names vs descriptions)
        text = text.replace("_", " ")
        # Remove common code structural characters causing noise
        for char in ["(", ")", ":", ",", ".", "=", "{", "}", "[", "]", ";", '"', "'"]:
            text = text.replace(char, " ")
        return text

    def compute_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Computes cosine similarity and performs gap analysis.
        Returns a dictionary with score and details.
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Preprocess both inputs
            t1 = self.preprocess(text1)
            t2 = self.preprocess(text2)
            
            vectors = self.vectorizer.fit_transform([t1, t2])
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
                
            # --- GAP ANALYSIS ---
            feature_names = self.vectorizer.get_feature_names_out()
            dense = vectors.todense()
            denselist = dense.tolist()
            
            # Identify which words are in T1 (code) and T2 (doc)
            code_words = set()
            doc_words = set()
            
            for col_idx, val in enumerate(denselist[0]):
                if val > 0: code_words.add(feature_names[col_idx])
                    
            for col_idx, val in enumerate(denselist[1]):
                if val > 0: doc_words.add(feature_names[col_idx])
            
            common = code_words.intersection(doc_words)
            missing_in_code = doc_words - code_words
            missing_in_doc = code_words - doc_words
            
            suggestions = []
            if len(common) == 0:
                suggestions.append("CRITICAL: No common vocabulary found. Rename variables to match domain terms.")
            
            if len(missing_in_code) > 0:
                top_missing = list(missing_in_code)[:5]
                suggestions.append(f"The code does not mention these terms found in the documentation: {', '.join(top_missing)}.")
                
            if len(missing_in_doc) > 0:
                top_missing = list(missing_in_doc)[:5]
                suggestions.append(f"The following code elements appear to be undocumented: {', '.join(top_missing)}.")

            return {
                "score": float(similarity),
                "common_words": list(common),
                "missing_in_code": list(missing_in_code),
                "missing_in_doc": list(missing_in_doc),
                "suggestions": suggestions
            }
            
        except ValueError:
            return {
                "score": 0.0,
                "common_words": [],
                "missing_in_code": [],
                "missing_in_doc": [],
                "suggestions": ["Input text too short or empty."]
            }

    def symmetric_analysis(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        """
        Performs symmetric analysis and gap detection.
        """
        # We now get a dict back from compute_similarity (which actually does the full analysis now)
        # We call it once because we analyze the PAIR.
        
        analysis = self.compute_similarity(code_text, doc_text)
        sim_score = analysis["score"]
        
        match_label = "Poor match"
        if sim_score > 0.60:
            match_label = "Excellent match"
        elif sim_score > 0.35:
            match_label = "Moderate match"

        return {
            "forward_match": sim_score,
            "backward_match": sim_score, 
            "symmetric_score": sim_score,
            "match_label": match_label,
            "details": analysis # Include the detailed gap analysis
        }

# Helper for backward compatibility or simple usage
def symmetric_analysis(code_text: str, doc_text: str):
    analyzer = StatisticalAnalyzer()
    return analyzer.symmetric_analysis(code_text, doc_text)

def compute_similarity(text1: str, text2: str):
    analyzer = StatisticalAnalyzer()
    return analyzer.compute_similarity(text1, text2)

