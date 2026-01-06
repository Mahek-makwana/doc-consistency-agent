# CraftAI Pipeline Design

The DocSync Agent is packaged as a reusable CraftAI pipeline.

## Pipeline Stages

1. **Ingestion**
   - Accepts raw text or ZIP inputs

2. **Preprocessing**
   - Syntax stripping
   - Case normalization

3. **Statistical Alignment**
   - TF-IDF vectorization
   - Symmetric similarity scoring

4. **Operational Checks**
   - Detects IO, math, API usage
   - Flags semantic drift

5. **Output**
   - Structured JSON report
   - CI-friendly exit codes

## Reusability

The pipeline can be deployed:
- As a web service
- Inside CI workflows
- As an internal API
