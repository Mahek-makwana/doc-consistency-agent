import os
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class AISuggester:
    def __init__(self):
        self.client = None
        if OpenAI and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI()
        else:
            print("Warning: OpenAI API Key not found or library missing. customized suggestions will be disabled.")

    def suggest_docstring(self, function_name: str, code_content: str) -> str:
        """
        Generates a Python docstring for a given function code.
        """
        if not self.client:
            return f'"""\n    TODO: Add documentation for {function_name}\n    """'

        prompt = f"""
        You are an expert Python developer.
        Generate a Google-style docstring for the following function.
        Return ONLY the docstring, including the triple quotes.

        Function Code:
        {code_content}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating docstring: {e}")
            return f'"""\n    TODO: Add documentation for {function_name}\n    """'

    def suggest_markdown_doc(self, title: str, summary: str) -> str:
        """
        Generates a Markdown documentation file content.
        """
        if not self.client:
            return f"# {title}\n\nTODO: Add detailed documentation.\n\nContext: {summary}"

        prompt = f"""
        You are a technical writer.
        Create a comprehensive Markdown documentation page for: {title}
        
        Context/Summary:
        {summary}
        
        Include:
        - Overview
        - Usage Examples
        - Technical Details
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating markdown: {e}")
            return f"# {title}\n\nTODO: Add detailed documentation."

# Singleton instance for easy import
suggester = AISuggester()

def suggest_documentation(missing_items, code_summary):
    # Backward compatibility wrapper
    return suggester.suggest_markdown_doc("Suggested Documentation", f"Missing items: {missing_items}\nCode Summary: {code_summary}")
