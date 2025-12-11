from pathlib import Path
import re

def extract_documented_items(md_file: str):
    """
    Extract documented functions/classes and their descriptions from markdown files.
    Returns a dict with 'functions' and 'classes', where each is a dict of name -> description.
    """
    path = Path(md_file)
    
    documented = {
        "functions": {},
        "classes": {},
    }
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return documented

    # Split by headers to group content with titles
    # This is a naive heuristic assuming structure like:
    # ## function_name
    # Description text...
    
    lines = content.split('\n')
    current_item = None
    current_type = None
    buffer = []
    
    def save_current():
        if current_item and buffer:
            desc = "\n".join(buffer).strip()
            if current_type == "function":
                documented["functions"][current_item] = desc
            elif current_type == "class":
                documented["classes"][current_item] = desc

    for line in lines:
        clean = line.strip()
        
        # Detect headers
        if line.startswith("## "):
            save_current() # Save previous
            
            # Reset
            buffer = []
            header_text = line.replace("##", "").strip()
            
            # Heuristics to determine if function or class
            # 1. explicit prefixes
            if header_text.startswith("function:"):
                current_item = header_text.replace("function:", "").strip()
                current_type = "function"
            elif header_text.startswith("class:"):
                current_item = header_text.replace("class:", "").strip()
                current_type = "class"
            elif "def " in header_text:
                current_item = header_text.replace("def ", "").split("(")[0]
                current_type = "function"
            elif header_text[0].isupper():
                current_item = header_text
                current_type = "class"
            else:
                current_item = header_text
                current_type = "function"
                
        elif current_item:
            # Collect description lines
            if not line.startswith("#"):
                buffer.append(line)
    
    save_current() # Save last item
    
    return documented
