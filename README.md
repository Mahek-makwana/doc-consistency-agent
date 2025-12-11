# 🤖 Intelligent Documentation Consistency Agent

> **An AI-powered pipeline that ensures your code and documentation are always in perfect sync.**

Unlike traditional linters that only check for *existence*, this agent uses **Semantic Analysis** and **Machine Learning** to verify that your documentation actually *describes* what your code *does*.

---

## 🚀 Overview

In modern software development, code evolves fast, but documentation often lags behind. This "Documentation Drift" leads to confusion, bugs, and increased onboarding time.

The **Doc Consistency Agent** solves this by:
1.  **Analyzing** code and docs using TF-IDF and Cosine Similarity (Scikit-Learn).
2.  **Detecting** mismatches, drift, and missing coverage.
3.  **Reporting** detailed consistency scores and semantic gaps.
4.  **Automating** fixes by generating missing docs and suggesting updates via Generative AI.
5.  **Integrating** directly into your CI/CD pipeline with automated Git branching and Pull Requests.

---

## ✨ Key Features

### 🧠 1. Semantic Consistency Analysis (Idea 1)
*   Uses **Scikit-Learn** validation logic.
*   Calculates a **Symmetric Consistency Score** (Forward & Backward match).
*   Identifies specific **vocabulary gaps** (e.g., Code uses "discount", Doc uses "tax").
*   Ignores syntax noise to focus on *meaning*.

### ⚡ 2. Automated Pipeline & GitOps (Idea 3)
*   **Auto-Scan**: Runs on every commit or manually.
*   **Auto-Document**: Generates Markdown documentation for undocumented functions using OpenAI.
*   **Auto-PR**: Automatically creates a new branch, commits changes, and pushes to GitHub.

### 🌐 3. Interactive Web Interface
*   **Ad-hoc Analysis**: Upload any code file and documentation file to check consistency instantly.
*   **Visual Reports**: Color-coded verdicts (Excellent, Moderate, Poor).
*   **AI Suggestions**: Receive actionable advice on how to align your terminology.

---

## 🛠️ Technology Stack

*   **Core**: Python 3.9+
*   **AI/ML**: Scikit-Learn (TF-IDF, Cosine Similarity), OpenAI API.
*   **Web Framework**: FastAPI, Uvicorn.
*   **Frontend**: HTML5, TailwindCSS (Jinja2 Templates).
*   **Automation**: GitPython, CI/CD Pipeline logic.

---

## 🏁 Getting Started

### Prerequisites
*   Python 3.8+ installed.
*   Git configured.
*   (Optional) OpenAI API Key for AI suggestions.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Mahek-makwana/doc-consistency-agent.git
    cd doc-consistency-agent
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment (Optional):**
    ```bash
    export OPENAI_API_KEY="your-key-here"
    ```

### Usage

#### 🅰️ Run the Web Interface (Interactive Mode)
Start the server to use the beautiful web UI:
```bash
python src/agent/main.py
```
> Open your browser at [http://localhost:8000](http://localhost:8000)

#### 🅱️ Run the CI/CD Pipeline (Automation Mode)
Run the full analysis on your repository. This will generate reports and suggestions in the `output/` folder.
```bash
python src/agent/main.py --mode pipeline --ci
```

#### 🔄 Run with Git Automation
Enable GitOps to automatically branch and push fixes:
```bash
python src/agent/main.py --mode pipeline --ci --git-ops
```

---

## 📊 How It Works

1.  **Ingestion**: The agent parses Python (`.py`) files to extract functions/docstrings and Markdown (`.md`) documentation files.
2.  **Vectorization**: It converts text into high-dimensional vectors using **TF-IDF**.
3.  **Comparion**: It computes the **Cosine Similarity** between the Code Vector and Documentation Vector.
    *   *Score > 0.60*: ✅ **Excellent Match**
    *   *Score > 0.35*: ⚠️ **Moderate Match**
    *   *Score < 0.35*: ❌ **Poor Match** (Drift Detected)
4.  **Action**:
    *   If undocumented: GEN-AI creates the doc.
    *   If mismatched: GEN-AI suggests terminology fixes.
    *   Final changes are packaged into a Git Commit.

---

## 📸 Screenshots

*(Add screenshots of the Web UI and Terminal Output here)*

---

**Developed for the AI Clinic.**
*Automating the boring stuff so engineers can focus on building.*
