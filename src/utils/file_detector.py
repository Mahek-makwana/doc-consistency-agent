from pathlib import Path

EXCLUDED_DIRS = {".venv", "venv", "site-packages", "__pycache__"}

def list_all_files(base_path: str):
    """
    Returns ALL project files, excluding venv and system folders.
    """
    base = Path(base_path)
    files = []

    for f in base.rglob("*"):
        if not f.is_file():
            continue

        # Skip excluded dirs
        if any(ex in f.parts for ex in EXCLUDED_DIRS):
            continue

        files.append(f)

    return files


def list_python_files(base_path: str):
    """
    Returns only .py files (excluding venv).
    """
    return [f for f in list_all_files(base_path) if f.suffix == ".py"]


def list_markdown_files(base_path: str):
    """
    Returns only .md documentation files (excluding venv).
    """
    return [f for f in list_all_files(base_path) if f.suffix == ".md"]

