import re
from typing import Dict, Any, List, Set

class EnterpriseDocSyncEngine:
    def __init__(self):
        self.patterns = {
            "logic": [
                r"def\s+([A-Za-z_]\w*)",           # Python
                r"function\s+([A-Za-z_]\w*)",      # JS/TS
                r"(?:const|let|var)\s+([A-Za-z_]\w*)\s*=\s*(?:\(.*\)|function)", # JS Arrow
                r"class\s+([A-Za-z_]\w*)",         # Classes
                r"(['\"]?[\w-]+['\"]?)\s*:",       # JS Object Keys (for configs)
            ],
            "docs": [
                r"([A-Za-z_]\w*)",                 # Any valid word (names)
            ]
        }

    def perform_audit(self, code_text: str, doc_text: str) -> Dict[str, Any]:
        # 1. EXTRACT LOGIC SEGMENTS
        found_logic = set()
        for p in self.patterns["logic"]:
            found_logic.update(re.findall(p, code_text))
        
        # Filter out minor keywords
        found_logic = {l.strip("'\"") for l in found_logic if len(l) > 2}

        # 2. EXTRACT DOCUMENTATION CONTEXT
        # We search comments for ANY reference to the logic names
        comments = " ".join(re.findall(r"(?:#|//|/\*|'''|\"\"\")(.*?)(?:\*/|'''|\"\"\"|\n|$)", code_text, re.DOTALL))
        doc_pool = (doc_text + " " + comments).lower()
        
        if not found_logic:
            return self._empty_result()

        synced = {l for l in found_logic if l.lower() in doc_pool}
        missing = found_logic - synced
        
        score = int((len(synced) / len(found_logic)) * 100)

        # 3. GENERATE DETAILED ISSUE SUMMARY
        if score == 0:
            issue_detail = f"CRITICAL GAP: The agent detected {len(found_logic)} logic entities (functions/keys), but absolutely NONE of them are described in your comments or README. This creates 'Silent Code' which is high risk for maintenance."
        elif score < 100:
            issue_detail = f"DOCUMENTATION DEBT: {len(missing)} specific functions/classes are missing from your guides. These undocumented areas can lead to integration errors. Missing elements include: {', '.join(list(missing)[:3])}..."
        else:
            issue_detail = "PERFECT ALIGNMENT: Every code entity is clearly mirrored and explained in the documentation context."

        return {
            "score": score,
            "label": "Accurate Alignment" if score > 70 else "Partial Mismatch" if score > 30 else "Critical Mismatch",
            "summary": f"Audit of {len(found_logic)} elements complete.",
            "detailed_issue": issue_detail,
            "stats": {
                "total_issues": len(missing),
                "synced_terms": len(synced),
                "breakdown": {"Terminology": 100 - score, "Logic": len(missing) * 5}
            },
            "suggestions": [f"Add detailed docstring for '{m}'" for m in list(missing)[:5]],
            "visual": [len(synced), len(missing), 2]
        }

    def _empty_result(self):
        return {
            "score": 0, "label": "No Logic Detected", "summary": "File scanning yielded no structural entities.",
            "detailed_issue": "REASON: The file doesn't seem to contain standard functions, classes, or configuration keys. Please upload a valid source file.",
            "stats": {"total_issues": 1, "synced_terms": 0, "breakdown": {"Terminology": 0, "Logic": 100}},
            "suggestions": ["Define functions or classes to begin audit."],
            "visual": [0, 10, 0]
        }

def symmetric_analysis(code_text: str, doc_text: str):
    return EnterpriseDocSyncEngine().perform_audit(code_text, doc_text)
