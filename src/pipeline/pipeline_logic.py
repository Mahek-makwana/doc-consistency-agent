
from src.agent.stat_analysis import symmetric_analysis

def run_consistency_check(code_text: str, doc_text: str):
    """
    CraftAI Pipeline Function.
    
    Args:
        code_text (str): The source code to analyze.
        doc_text (str): The documentation to check against.
        
    Returns:
        dict: The symmetric analysis result.
    """
    # This function wraps our existing logic for the pipeline
    result = symmetric_analysis(code_text, doc_text)
    return result
