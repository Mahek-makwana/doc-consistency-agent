# similarity_engine.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_documentation(code_text: str, doc_text: str):
    """
    Compute similarity between code and documentation using TF-IDF and cosine similarity.
    
    Args:
        code_text (str): Concatenated code text from all Python files.
        doc_text (str): Concatenated documentation text from all Markdown files.
    
    Returns:
        dict: {
            "cosine_similarity": float,  # overall similarity score (0-1)
            "code_vector_norm": float,    # L2 norm of code TF-IDF vector
            "doc_vector_norm": float      # L2 norm of doc TF-IDF vector
        }
    """
    from src.agent.stat_analysis import StatisticalAnalyzer
    
    analyzer = StatisticalAnalyzer()
    
    # We want to return the specific structure expected by the legacy code
    # The new analyzer simplifies this, but for backward compatibility we might want to expose the vectors if needed.
    # However, the previous implementation returned 'cosine_similarity', 'code_vector_norm', 'doc_vector_norm'.
    # Our new analyzer abstracts this.
    # Let's see if we can reconstruct it or if we just need the similarity.
    
    # Re-implementing using the analyzer's vectorizer to keep consistent logic
    combined_texts = [code_text, doc_text]
    try:
        tfidf_matrix = analyzer.vectorizer.fit_transform(combined_texts)
        code_vector = tfidf_matrix[0]
        doc_vector = tfidf_matrix[1]
        
        sim_score = cosine_similarity(code_vector, doc_vector)[0][0]
        
        return {
            "cosine_similarity": round(float(sim_score), 4),
            "code_vector_norm": round(float(np.linalg.norm(code_vector.toarray())), 4),
            "doc_vector_norm": round(float(np.linalg.norm(doc_vector.toarray())), 4)
        }
    except ValueError:
        return {
            "cosine_similarity": 0.0,
            "code_vector_norm": 0.0,
            "doc_vector_norm": 0.0
        }


if __name__ == "__main__":
    # --- Example test ---
    code_example = "def add(a, b): return a + b"
    doc_example = "This function adds two numbers and returns the result."
    print(check_documentation(code_example, doc_example))

