# System Architecture – DocSync Agent

The DocSync Agent follows a modular, layered architecture designed for
scalability, reusability, and CI integration.

## High-Level Components

1. **Input Layer**
   - Source code files (.py, .js, etc.)
   - Documentation files (.md, .txt)
   - ZIP-based batch uploads

2. **Processing Layer**
   - Text normalization & token cleanup
   - Function & documentation extraction
   - Statistical vectorization

3. **Analysis Engine**
   - TF-IDF vector comparison
   - Cosine similarity scoring
   - Operational intent detection

4. **API Layer**
   - FastAPI endpoints
   - JSON-based responses

5. **Automation Layer**
   - GitHub Actions CI
   - CraftAI pipeline deployment

## Design Principles

- Separation of concerns
- Deterministic scoring (no black-box AI)
- Explainable results
- CI-first mindset
