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

    # Functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            params = [a.arg for a in node.args.args]
            funcs.append({
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "params": params,
                "is_method": False
            })

        # Classes
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append({
                        "name": item.name,
                        "docstring": ast.get_docstring(item),
                        "params": [a.arg for a in item.args.args]
                    })
            classes.append({
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "methods": methods
            })

    return {
        "file": str(path),
        "functions": [f for f in funcs if not f["is_method"]],
        "classes": classes
    }
