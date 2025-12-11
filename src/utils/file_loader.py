# src/utils/file_loader.py

import os
import json
import yaml

class FileLoader:
    """
    Generic loader for .txt, .md, .json, .yml, .yaml files.
    """

    SUPPORTED_TEXT = {".txt", ".md", ".py"}
    SUPPORTED_JSON = {".json"}
    SUPPORTED_YAML = {".yaml", ".yml"}

    @staticmethod
    def load(path: str):
        """
        Automatically detect file type and return content.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        ext = os.path.splitext(path)[1].lower()

        # ---------------------------
        # TEXT FILES
        # ---------------------------
        if ext in FileLoader.SUPPORTED_TEXT:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        # ---------------------------
        # JSON
        # ---------------------------
        if ext in FileLoader.SUPPORTED_JSON:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        # ---------------------------
        # YAML
        # ---------------------------
        if ext in FileLoader.SUPPORTED_YAML:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def load_folder(folder_path: str):
        """
        Load all supported files inside a folder.
        Returns dictionary {filename: content}
        """

        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Not a folder: {folder_path}")

        results = {}
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()

                if (
                    ext in FileLoader.SUPPORTED_TEXT
                    or ext in FileLoader.SUPPORTED_JSON
                    or ext in FileLoader.SUPPORTED_YAML
                ):
                    try:
                        results[filename] = FileLoader.load(file_path)
                    except Exception as e:
                        results[filename] = f"Failed to load: {e}"

        return results
