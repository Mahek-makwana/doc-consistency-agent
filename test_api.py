# test_api.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# -----------------------------
# 1) Test /similarity endpoint
# -----------------------------
similarity_payload = {
    "code": "def add(a, b): return a + b",
    "documentation": "This function adds two numbers and returns the result."
}

try:
    response = requests.post(f"{BASE_URL}/similarity", json=similarity_payload)
    print("=== /similarity RESULT ===")
    print(json.dumps(response.json(), indent=4))
except Exception as e:
    print("Error calling /similarity:", e)

# -----------------------------
# 2) Test /scan endpoint
# -----------------------------
try:
    response = requests.post(f"{BASE_URL}/scan")
    print("\n=== /scan RESULT ===")
    # Print only summary to avoid huge output
    scan_result = response.json()
    print("File counts:", scan_result.get("file_counts"))
    print("Stats:", scan_result.get("stats"))
    print("Scan output preview:", scan_result.get("scan_output")[:500], "...")  # first 500 chars
except Exception as e:
    print("Error calling /scan:", e)

