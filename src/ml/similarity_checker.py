from typing import Dict, Any, List, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class SimilarityChecker:
    """
    Advanced semantic analysis engine using Scikit-Learn.
    Performs TF-IDF vectorization and Code-Doc consistency checks.
    """

    def __init__(self):
        # Allow token_pattern to capture typical code identifiers (words with underscores, etc)
        self.vectorizer = TfidfVectorizer(
            token_pattern=r"(?u)\b\w[\w]+\b",
            stop_words='english'
        )

    def preprocess(self, text: str) -> str:
        """
        Normalize text for comparison:
        - Lowercase
        - Split camelCase / snake_case
        - Remove structural punctuation
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Replace snake_case with spaces
        text = text.replace("_", " ")
        
        # Replace common code punctuation with spaces
        # (We keep words, but remove syntax chars)
        for char in "()[]{}:;.,=":
            text = text.replace(char, " ")
            
        return text

    def compute_similarity(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        """
        Computes cosine similarity between code and documentation.
        Returns detailed statistics including gap analysis.
        """
        if not code_text.strip() or not doc_text.strip():
            return {
                "score": 0.0,
                "common_terms": [],
                "missing_in_code": [],
                "missing_in_doc": [],
                "recommendation": "Missing input text."
            }

        # Preprocess
        clean_code = self.preprocess(code_text)
        clean_doc = self.preprocess(doc_text)

        try:
            # Fit and Transform
            tfidf_matrix = self.vectorizer.fit_transform([clean_code, clean_doc])
            
            # Compute Cosine Similarity
            # Matrix is 2xN. Row 0 is Code, Row 1 is Doc.
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            score = float(similarity_matrix[0][0])
            
            # --- GAP ANALYSIS ---
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get non-zero indices for code and doc
            code_indices = tfidf_matrix[0].nonzero()[1]
            doc_indices = tfidf_matrix[1].nonzero()[1]
            
            code_terms = set(feature_names[i] for i in code_indices)
            doc_terms = set(feature_names[i] for i in doc_indices)
            
            common_terms = code_terms.intersection(doc_terms)
            missing_in_code = doc_terms - code_terms
            missing_in_doc = code_terms - doc_terms
            
            # Generate Recommendation
            recommendation = self._generate_recommendation(score, len(common_terms), len(doc_terms))

            return {
                "score": round(score, 4),
                "common_terms": sorted(list(common_terms)),
                "missing_in_code": sorted(list(missing_in_code)),
                "missing_in_doc": sorted(list(missing_in_doc)),
                "recommendation": recommendation
            }

        except ValueError as e:
            # Usually happens if vocabulary is empty after stop words removal
            return {
                "score": 0.0,
                "error": str(e),
                "recommendation": "Unable to compute similarity (empty vocabulary)."
            }

    def _generate_recommendation(self, score: float, common_count: int, doc_count: int) -> str:
        if score > 0.8:
            return "Excellent consistency. detailed documentation matches code well."
        elif score > 0.5:
            return "Moderate consistency. Some key terms are shared, but description could be more precise."
        elif score > 0.2:
            return "Low consistency. Documentation is vague or describes different concepts than the code."
        else:
            if doc_count == 0:
                return "No documentation content found."
            return "Critical mismatch. Code and documentation share almost no vocabulary."
