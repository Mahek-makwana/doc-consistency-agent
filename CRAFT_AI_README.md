# CraftAI Pipeline Integration Guide

This guide explains how to deploy your **Statistical Text Alignment Engine** as a reusable pipeline on the CraftAI platform.

## Files Created

*   **`src/pipeline/pipeline_logic.py`**: The core function `run_consistency_check` that will be executed by the pipeline. It wraps your existing symmetric analysis logic.
*   **`src/pipeline/deploy_pipeline.py`**: A Python script to automate the deployment of the pipeline using `craft-ai-sdk`.
*   **`requirements.txt`**: Updated to include `craft-ai-sdk`.

## 🚀 How to Deploy

### 1. Prerequisites
You need a CraftAI account, an Environment URL, and an Access Token.

### 2. Set Credentials
Set these environment variables in your terminal or a `.env` file (if you create one):

```bash
# Windows PowerShell
$env:CRAFT_AI_ENVIRONMENT_URL = "https://your-environment-url"
$env:CRAFT_AI_ACCESS_TOKEN = "your-access-token"
```

### 3. Install Usage Dependencies
Ensure you have the SDK installed (I added it to requirements, but you might need to install it in your environment):
```bash
pip install craft-ai-sdk
```

### 4. Run Deployment
Execute the deployment script:
```bash
python src/pipeline/deploy_pipeline.py
```

## 🔍 How it Works
1.  The script reads your code and requirements.
2.  It sends `src/pipeline/pipeline_logic.py` (and usage of `src/agent`) to CraftAI.
3.  CraftAI creates a Docker container with `scikit-learn` installed.
4.  Your pipeline `doc-consistency-check` becomes available to be triggered via API.

## ✅ Verification
We defined `src/pipeline/test_pipeline_local.py` which proves the logic works locally before deployment.
