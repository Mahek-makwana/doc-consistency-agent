import ast
from pathlib import Path

def parse_python_file(file_path: str):
    """
    Parse a Python file and extract functions, classes, and docstrings.
    """
    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)

    funcs = []
    classes = []

    for node in ast.walk(tree):
        # Functions
        if isinstance(node, ast.FunctionDef):
            funcs.append({
                "name": node.name,
                "docstring": ast.get_docstring(node)
            })

        # Classes
        if isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "docstring": ast.get_docstring(node)
            })

    return {
        "file": str(path),
        "functions": funcs,
        "classes": classes
    }
