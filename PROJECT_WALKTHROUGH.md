# 📘 CraftAI - DocSync Agent: Project Walkthrough

This document serves as a comprehensive guide for the **CraftAI - DocSync Agent**, designed for stakeholders and technical reviews. It explains the "Why", "How", and "What" of the project, including demo scenarios for live presentations.

---

## 🚀 1. Executive Summary
The **CraftAI - DocSync Agent** is an intelligent consistency-checking system that ensures software documentation stays in sync with actual source code. It uses **Statistical Text Alignment** and **Operational Intent Detection** to provide a symmetric score of how well a document reflects the code logic.

---

## 2. Valid Document Types & ZIP Support

To ensure the highest accuracy, the **CraftAI - DocSync Agent** focuses on text-based semantic alignment.

### ✅ Valid Document Types
The agent works best with the following file formats:
*   **Code**: `.py` (Python), `.js`/`.ts` (JavaScript/TypeScript), `.java`, `.cpp`, `.c`.
*   **Documentation**: `.md` (Markdown), `.txt` (Plain Text), `.rst` (reStructuredText).
*   **Note**: Binary formats like `.pdf` or `.docx` are not supported directly to avoid noise from formatting characters.

### 📦 ZIP File Support (Batch Analysis)
You can now upload **ZIP files** to analyze entire project folders at once:
*   **The Code ZIP**: The agent will find and concatenate all `.py`, `.js`, etc., files inside the zip.
*   **The Documentation ZIP**: The agent will extract all `.md` and `.txt` files to form a unified documentation base for comparison.

---

## 3. Development & Technology Stack

The agent was built using a modern AI engineering stack, focusing on **Statistical NLP** (Natural Language Processing) and **Symmetric Analysis**.

### 💻 Core Tech Stack
*   **Language**: `Python 3.11` (Chosen for its robust ecosystem for AI and data science).
*   **Machine Learning**: `Scikit-Learn` (Used specifically for **TF-IDF Vectorization** and **Cosine Similarity** algorithms).
*   **Numerical Processing**: `NumPy` (Handles the matrix operations and vector normalization).
*   **Web Framework**: `FastAPI` (Selected for its high performance and speed in serving AI models).
*   **Frontend**: `HTML5 / TailwindCSS` (Implemented a custom, premium dashboard with **Glassmorphism** aesthetics).
*   **Server/Hosting**: `Uvicorn` (ASGI server) deployed via **Docker** on **Render.com**.

### 🔌 API & External Integrations
1.  **CraftAI Pipeline**: 
    *   Used the `craft-ai-sdk` to package the analysis logic into an industrial-grade pipeline.
    *   **Integration**: Defined in `src/pipeline/deploy_pipeline.py`.
2.  **Dev Environment Tools**:
    *   **VS Code**: Primary development environment.
    *   **Git / GitHub**: Version control and CI/CD hosting.
    *   **GitHub Actions**: Automation for the DocSync consistency check workflow.

### 🔑 Configuration (Tokens & Environment)
To run this agent in a production/team environment, we use the following configuration structure:
*   **`CRAFT_AI_ACCESS_TOKEN`**: Used for deploying and triggering the pipeline on the CraftAI cloud.
*   **`CRAFT_AI_ENVIRONMENT_URL`**: The endpoint for the company's dedicated CraftAI environment.
*   **`OPENAI_API_KEY`** (Optional): Tied to the `LLM Integration` layer for generating suggested documentation fixes.
*   **`PORT`**: Dynamically assigned for cloud accessibility.

---

## 4. How the Agent Works (The "Brain")

The core engine is built using **Python** and **Scikit-Learn**. Here is the 3-step pipeline:

### A. Preprocessing & Normalization
- **Logic**: It strips away code syntax (punctuation, brackets) and converts `camelCase` or `snake_case` into readable words.
- **Why?**: To ensure that a variable named `calculate_euclidean_distance` matches the phrase "calculate euclidean distance" in documentation.

### B. Statistical Vectorization (TF-IDF)
- **Tool**: `TfidfVectorizer` (Term Frequency-Inverse Document Frequency).
- **Technique**: We use **Symmetric Log-Scaling**. We map the code and the document into a high-dimensional mathematical space.
- **Scoring**: We compute the **Cosine Similarity** between the code vector and the doc vector. A score of `1.0` is a perfect match; `0.0` is completely unrelated.

### C. Operational Alignment (Intent Detection)
- **Feature**: This is our "Secret Sauce". The agent looks for **operational triggers**.
- **Example**: If it sees the word `sqrt` or `**2` in the code, it checks if the documentation contains words like "root", "square", or "math". If not, it flags an **Operational Gap**, even if the vocabulary is otherwise similar.

### D. Premium Reporting Dashboard (New)
- **Statistic Report**: Provides a granular breakdown of score categories, logic gaps, and "zombie" (unused) documentation.
- **Visual Summary**: Interactive **Chart.js** doughnuts that visualize the vocabulary overlap between code and docs.
- **Quick Fix Suggestions**: Algorithmic generation of missing documentation snippets to bridge vocabulary gaps instantly.
- **Export Analysis**: Professional export tools allowing users to download reports as **.TXT** or generate **PDF reports** via the browser print engine.

---

## 5. Website & Deployment Details

- **Public URL**: `https://your-app-name.onrender.com` (Check your Render Dashboard for the specific link).
- **Hosting**: Deployed via **Render.com** (Free Tier).
- **Infrastructure**: The app is **Dockerized**. This ensures it runs exactly the same way in the cloud as it does on your local machine.
- **Availability**: 24/7 access. Note: On the free tier, the site may "sleep" after 15 minutes of inactivity; simply refresh the page to wake it up in 30 seconds.

---

## 6. How to Run the Demo (Step-by-Step)

Follow these steps to show the agent running live on your local machine during the meeting:

### Step 1: Open Terminal & Activate Environment
Open your terminal (PowerShell) in the project folder and activate the virtual environment to ensure all libraries are loaded:
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Start the DocSync Server
Run the following command to launch the web dashboard:
```powershell
python demo_server.py
```

### Step 3: Open the Dashboard
Open your web browser and go to:
**[http://localhost:8000](http://localhost:8000)**

### Step 4: Run Scenario Tests
Copy the examples from **Section 6** below and paste them into the "Source Code" and "Documentation" boxes. Click **"Run Consistency Check"** to show the results.

---

## 7. Live Test Scenarios (Examples for Demo)

Use these examples during your meeting to show the agent's intelligence.

### ✅ Scenario A: "Production Quality" (Good Alignment)
**Source Code:**
```python
def calc_final_price(base, tax_rate, discount):
    # Apply discount first
    price = base * (1 - discount)
    # Then add tax
    total = price * (1 + tax_rate)
    return round(total, 2)
```

**Documentation:**
```markdown
### Price Calculator
This function calculates the final price of an item. 
It applies a percentage discount to the base cost and then computes the total including the tax rate.
The result is rounded to two decimal places.
```
- **Outcome**: **90%+ Similarity**. The keywords "calculate", "tax", "discount", "price", and "total" align perfectly.

---

### ⚠️ Scenario B: "Partial Alignment" (Moderate Match)
**Source Code:**
```python
def save_user_profile(user_id, data):
    import json
    path = f"storage/{user_id}.json"
    with open(path, 'w') as f:
        json.dump(data, f)
```

**Documentation:**
```markdown
### User Manager
This module manages user security and IDs. 
It ensures that profile data is kept updated within the system.
```
- **Outcome**: **30-40% Similarity**. While it mentions "user" and "data", it fails to mention that the code is specifically **saving** or **writing to JSON**.
- **Agent Advice**: It will suggest adding terms like "save", "path", or "json" to the docs.

---

### ❌ Scenario C: "Poor Alignment" (The "Drift" Warning)
**Source Code:**
```python
def fetch_api_status():
    import requests
    r = requests.get("https://api.status.com/v1/health")
    return r.json()
```

**Documentation:**
```markdown
### API Key Generator
This function creates a new security token for the user. 
It provides an encrypted string to be used for authentication.
```
- **Outcome**: **0-10% Similarity**. This is a classic case of **Documentation Drift** (the code was changed to a health check, but the docs still describe a key generator).
- **Agent Advice**: It will raise a **Critical Alert** and flag the operational mismatch between "fetch" (code) and "generator" (docs).

---

## 8. Integration for the Company
The project is ready for professional scaling:
1.  **GitHub Actions**: Every code commit automatically runs `ci_check.py` to block "bad" updates.
2.  **CraftAI Pipeline**: The analysis logic is exposed as a reusable API component that can be called by other internal tools.

---
**Presented by**: CraftAI - DocSync Agent
**Version**: 1.0.0 (Premium Statistical Engine)
