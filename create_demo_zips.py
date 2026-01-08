import zipfile
import os

def create_zip(zip_name, files_dict):
    with zipfile.ZipFile(zip_name, 'w') as z:
        for filename, content in files_dict.items():
            z.writestr(filename, content)
    print(f"✅ Created: {zip_name}")

# --- CODE ZIP CONTENT ---
code_files = {
    "auth_service.py": "def login(user, pwd):\n    # Authenticate via database\n    return verify_credentials(user, pwd)",
    "data_utils.py": "def calculate_statistics(data):\n    # Compute mean and standard deviation\n    import numpy as np\n    return np.mean(data), np.std(data)",
    "api_handler.py": "def fetch_weather(city):\n    import requests\n    return requests.get(f'https://api.weather.com/{city}').json()"
}

# --- DOCS ZIP CONTENT ---
doc_files = {
    "readme.md": "# Project Overview\nThis project handles user login and data statistics calculations.",
    "api_guide.md": "## Weather API\nThe fetch weather function retrieves global weather data using the official API.",
}

if __name__ == "__main__":
    create_zip("code_demo.zip", code_files)
    create_zip("docs_demo.zip", doc_files)
    print("\n🚀 DONE! You now have 'code_demo.zip' and 'docs_demo.zip' in your folder.")
    print("You can now upload these to your CraftAI website to show off the ZIP feature!")
