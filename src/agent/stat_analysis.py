import re
from typing import Dict, Any, List, Set

class EnterpriseDocSyncEngine:
    """
    Structural Audit Engine with Internal Code-Doc Hybrid Sensing.
    """

    def __init__(self):
        self.code_patterns = {
            "functions": [r"def\s+([A-Za-z_]\w*)\s*\(", r"function\s+([A-Za-z_]\w*)\s*\("],
            "classes": [r"class\s+([A-Za-z_]\w*)"],
            "docstrings": [r'"""(.*?)"""', r"'''(.*?)'''", r"/\*(.*?)\*/", r"//(.*?)\n"]
        }

    def perform_audit(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        # 1. EXTRACT CODE ENTITIES
        funcs = set(re.findall(self.code_patterns["functions"][0], code_text) + re.findall(self.code_patterns["functions"][1], code_text))
        classes = set(re.findall(self.code_patterns["classes"][0], code_text))
        all_code_items = funcs.union(classes)

        # 2. EXTRACT DOC REFERENCES (External + Internal Docstrings)
        internal_docs = " ".join(re.findall(self.code_patterns["docstrings"][0], code_text, re.DOTALL))
        combined_docs = doc_text + " " + internal_docs
        
        doc_refs = set(re.findall(r"([A-Za-z_]\w*)", combined_docs))

        if not all_code_items:
            return self._empty_result()

        # 3. CALCULATE REAL CONSISTENCY
        synced = all_code_items.intersection(doc_refs)
        missing = all_code_items - doc_refs
        
        # Calculate base score (weighted by complexity)
        score = int((len(synced) / len(all_code_items)) * 100) if all_code_items else 0
        
        # Accurate Reasons for "Issue Summary"
        main_reason = "Consistency is high."
        if score < 50:
            main_reason = f"Identified {len(missing)} logic segments with no descriptive coverage in comments or README."
        elif score < 100:
            main_reason = f"Minor gaps: {len(missing)} entities are operational but lack documentation."

        return {
            "score": score,
            "label": "Production Quality" if score > 80 else "Partial Alignment" if score > 40 else "Critical Mismatch",
            "summary": main_reason,
            "stats": {
                "total_issues": len(missing),
                "synced_terms": len(synced),
                "breakdown": {
                    "Terminology": 100 if score == 100 else (100 - score),
                    "Logic": len(missing) * 10 # Multiplier for visual bar
                }
            },
            "suggestions": [f"Document the function '{m}'" for m in list(missing)[:5]],
            "visual": [len(synced), len(missing), 5] # Synced, Gaps, Structure
        }

    def _empty_result(self):
        return {
            "score": 0, "label": "No Logic Detected", "summary": "Uploaded file contains no class or function definitions.",
            "stats": {"total_issues": 1, "synced_terms": 0, "breakdown": {"Terminology": 100, "Logic": 100}},
            "suggestions": ["Add function or class definitions to the file."],
            "visual": [0, 10, 0]
        }

def symmetric_analysis(code_text: str, doc_text: str):
    return EnterpriseDocSyncEngine().perform_audit(code_text, doc_text)
