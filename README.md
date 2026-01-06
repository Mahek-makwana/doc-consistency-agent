# CraftAI – DocSync Agent

## Overview

CraftAI – DocSync Agent is an automated documentation consistency checker designed to ensure that project documentation accurately reflects the behavior of the underlying source code. The system analyzes code, documentation, and structural metadata to detect mismatches such as missing functionality descriptions, outdated docs, or misleading explanations.

This project was built as part of an academic–industry aligned initiative with a focus on **engineering rigor**, **CI automation**, and **reproducibility**.

---

## Problem Statement

In real-world software projects, documentation often becomes inconsistent with the codebase over time. This leads to:

* Incorrect onboarding material
* Misaligned API documentation
* Higher maintenance cost
* Reduced trust in technical artifacts

CraftAI – DocSync Agent addresses this by automatically validating documentation against code intent and structure.

---

## Key Features

* Automated documentation ↔ code consistency checks
* Operational intent detection (what the code actually does)
* TF-IDF + cosine similarity–based semantic comparison
* Modular and reusable analysis pipeline
* CI/CD integration via GitHub Actions
* Artifact-based reporting for traceability

---

## How It Works

1. **Code Parsing** – Extracts functions, classes, and logical operations from source files
2. **Documentation Parsing** – Reads markdown and structured documentation files
3. **Intent Matching** – Compares code intent with documented descriptions using statistical NLP
4. **Consistency Scoring** – Generates similarity scores and flags mismatches
5. **CI Reporting** – Runs automatically on push / pull request and stores results as artifacts

---

## Project Structure

```
.github/workflows   # CI pipelines
src/                # Core analysis logic
  ├── agent
  ├── ml
  ├── pipeline
  └── utils
docs/               # Human-written documentation
frontend/           # Demo UI
ci_check.py         # CI entry-point
main.py             # FastAPI app entry-point
```

---

## Live Demo

**Hosted Application**
[https://craftai-docsync-agent.onrender.com](https://craftai-docsync-agent.onrender.com)

**Local Run**

```bash
python demo_server.py
```

---

## CI/CD Integration

The project includes a GitHub Actions workflow that:

* Installs dependencies
* Runs documentation consistency checks
* Uploads scan results as CI artifacts

This ensures every change is automatically validated.

---

## Security & Engineering Practices

* No runtime secrets stored in repository
* Minimal third-party CI actions
* Deterministic dependency installation
* Artifact-based audit trail

---

## Intended Use

* Academic research projects
* Early-stage startups
* Internal tooling for documentation QA
* CI validation for engineering teams

---

## License

This project is released for educational and demonstration purposes.

