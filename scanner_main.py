import sys
from src.agent.stat_analysis import symmetric_analysis
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utils.file_detector import list_python_files, list_markdown_files
from src.utils.python_parser import parse_python_file
from src.utils.doc_parser import extract_documented_items
from src.utils.consistency_checker import check_consistency
from src.utils.file_loader import fileloader 
from similarity_engine import check_documentation


def main_scan():
    print("=== DOCUMENTATION CONSISTENCY SCAN STARTED ===\n")

    BASE_PATH = "./"      # scan only your project folder (not system)
    CODE_PATH = "./src"
    DOC_PATH = "./docs"

    # 1. Collect files
    py_files = list_python_files(CODE_PATH)
    md_files = list_markdown_files(DOC_PATH)

    print(f"Total Python files: {len(py_files)}")
    print(f"Total Markdown docs: {len(md_files)}\n")

    # 2. Parse Python files
    print("=== CODE SUMMARY ===\n")
    for f in py_files:
        parsed = parse_python_file(f)
        print(f"FILE: {f}")

        print("Functions:")
        for fn in parsed["functions"]:
            print(f" - {fn['name']}")

        print("Classes:")
        for cl in parsed["classes"]:
            print(f" - {cl['name']}")

        print()

    # 3. Parse docs
    print("=== DOC SUMMARY ===\n")
    for md in md_files:
        items = extract_documented_items(md)
        print(f"{md}: {items}")

    print()

    # 4. Check consistency
    print("=== CONSISTENCY REPORT ===\n")
    result = check_consistency("./")    # your function expects only base path

    print("CODE ITEMS:", result["code"])
    print("DOC ITEMS:", result["docs"])
    print("\nMISSING DOCUMENTATION:", result["missing_docs"])

    print("\n=== SCAN COMPLETE ===")


def main():
    main_scan()


if __name__ == "__main__":
    main()        