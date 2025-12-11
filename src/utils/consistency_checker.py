from typing import Dict, Any, List
from src.utils.python_parser import parse_python_file
from src.utils.doc_parser import extract_documented_items
from src.utils.file_detector import list_python_files, list_markdown_files
from src.ml.similarity_checker import SimilarityChecker

class ConsistencyChecker:
    def __init__(self, code_dir: str, doc_dir: str):
        self.code_dir = code_dir
        self.doc_dir = doc_dir
        self.similarity_engine = SimilarityChecker()

    def run_check(self) -> Dict[str, Any]:
        py_files = list_python_files(self.code_dir)
        md_files = list_markdown_files(self.doc_dir)

        # 1. Aggregate Code Items
        code_repo = {
            "functions": {}, # name -> docstring
            "classes": {}    # name -> docstring
        }
        
        for f in py_files:
            parsed = parse_python_file(f)
            for fn in parsed["functions"]:
                code_repo["functions"][fn["name"]] = fn["docstring"] or ""
            for cl in parsed["classes"]:
                code_repo["classes"][cl["name"]] = cl["docstring"] or ""

        # 2. Aggregate Documentation Items
        doc_repo = {
            "functions": {}, # name -> description
            "classes": {}
        }
        
        for doc in md_files:
            extracted = extract_documented_items(doc)
            doc_repo["functions"].update(extracted["functions"])
            doc_repo["classes"].update(extracted["classes"])

        # 3. Compare & Analyze
        results = {
            "matches": [],
            "missing_docs": [],
            "missing_code": [],
            "stats": {
                "total_functions": len(code_repo["functions"]),
                "total_documented": 0,
                "average_similarity": 0.0
            }
        }

        total_sim = 0.0
        match_count = 0

        # Check Functions
        all_code_funcs = set(code_repo["functions"].keys())
        all_doc_funcs = set(doc_repo["functions"].keys())

        common_funcs = all_code_funcs.intersection(all_doc_funcs)
        missing_docs = all_code_funcs - all_doc_funcs
        missing_code = all_doc_funcs - all_code_funcs

        # Analyze Matches
        for func in common_funcs:
            code_docstring = code_repo["functions"][func]
            doc_desc = doc_repo["functions"][func]
            
            analysis = self.similarity_engine.compute_similarity(code_docstring, doc_desc)
            
            results["matches"].append({
                "name": func,
                "type": "function",
                "similarity_score": analysis["score"],
                "recommendation": analysis["recommendation"],
                "issues": {
                    "missing_in_code": analysis["missing_in_code"],
                    "missing_in_doc": analysis["missing_in_doc"]
                }
            })
            
            total_sim += analysis["score"]
            match_count += 1

        # Populate Result Lists
        results["missing_docs"] = list(missing_docs)
        results["missing_code"] = list(missing_code)
        
        results["stats"]["total_documented"] = len(common_funcs)
        if match_count > 0:
            results["stats"]["average_similarity"] = round(total_sim / match_count, 4)

        return results
