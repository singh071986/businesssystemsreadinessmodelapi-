# Production Deployment README
## Business Systems Readiness API (FastAPI + Saved Model)

This document is a production-focused guide for deploying the classifier API.
It covers architecture, required files, setup, run commands, and production test steps.

---

## 1. Production Scope

This service exposes ML inference APIs over HTTP using FastAPI and a pre-trained
saved model artifact.

Core responsibilities in production:
- Accept assessment request payloads
- Validate input (strict schema)
- Load and use saved model for inference
- Return JSON response with pathway and reasoning
- Return a compact 12-paragraph summary under 1,000 characters total
- Return standardized JSON error responses

Out of scope for this service:
- Frontend/UI hosting
- Authentication gateway (can be added in reverse proxy/API gateway)
- Database persistence (not required for inference-only mode)

---

## 2. Required Project Files

Minimum files needed in production deployment package:

- `src/api.py` (FastAPI interface)
- `src/classifier.py` (inference logic)
- `src/schema.py` (request/response validation)
- `src/data_utils.py` (question mappings and pathway logic)
- `src/train_model.py` (feature builder and model schema compatibility)
- `models/pathway_classifier.pkl` (saved model artifact)
- `requirements.txt` (dependencies)

Recommended to include for verification:
- `tests/test_api.py`
- `tests/test_validation.py`
- `tests/prod_smoke_test.py`

---

## 3. Production Directory Structure

```text
Ripponmar22/
├── PRODUCTION_README.md
├── requirements.txt
├── models/
│   └── pathway_classifier.pkl
├── src/
│   ├── api.py
│   ├── classifier.py
│   ├── schema.py
│   ├── data_utils.py
│   └── train_model.py
└── tests/
    ├── test_api.py
    ├── test_validation.py
    └── prod_smoke_test.py
```

---

## 4. Environment Requirements

- OS: Linux/macOS (recommended Linux for production)
- Python: 3.9+
- Pip: latest recommended
- CPU: any modern CPU (inference is lightweight)
- RAM: 1 GB minimum (2 GB+ recommended)

---

## 5. Install and Setup

### Step 1: Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Confirm model artifact exists

```bash
ls -lh models/pathway_classifier.pkl
```

If model file is missing, generate it:

```bash
python src/train_model.py
```

---

## 6. Run API in Production Mode

### Option A: Direct uvicorn (simple)

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Option B: Multi-worker uvicorn (recommended for production)

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 2
```

### Optional environment variable for CORS

Allow specific UI origins:

```bash
export CORS_ALLOW_ORIGINS="https://your-ui-domain.com,http://localhost:3000"
```

---

## 7. API Endpoints (Production Contract)

- `GET /health`
- `POST /predict`

Interactive docs (if enabled):
- `/docs`
- `/redoc`

Detailed API contract document:
- `docs/api_interface.md`

---

## 8. Input Validation Guarantees

The service enforces these rules before inference:

1. All questions `q1` to `q12` are mandatory
2. No extra keys allowed (only `q1` through `q12`)
3. Each answer must be string and one of `A`, `B`, `C`, `D`
4. Invalid input returns HTTP 422 JSON error

Standardized error response shape:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "details": []
}
```

---

## 9. Production Test Steps (Must Run)

Run these checks before go-live and in CI/CD:

### 9.1 Validation rules test

```bash
python tests/test_validation.py
```

Expected:
- `Results: 5/5 passed, 0 failed`

### 9.2 Classifier logic regression test

```bash
python tests/test_classifier.py
```

Expected:
- `Results: 12/12 passed, 0 failed`

### 9.3 Saved-model production smoke test

```bash
python tests/prod_smoke_test.py
```

Expected:
- `Results: 4/4 passed, 0 failed`

### 9.4 API endpoint smoke test

```bash
python tests/test_api.py
```

Expected:
- API checks pass for health, predict, and validation failure handling

### 9.5 Summary contract verification

The deployed API must return:
- exactly 12 summary paragraphs
- combined summary length under 1,000 characters

Quick verification command:

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C",
      "q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"
    }
  }' | python3 -c 'import sys,json; d=json.load(sys.stdin); s=d["summary"]; print("chars=", len(s)); print("paragraphs=", len([p for p in s.split("\n\n") if p.strip()]))'
```

---

## 10. Manual Runtime Verification

After starting API server, run:

### Health check

```bash
curl -s http://localhost:8000/health
```

Expected: status `ok`

### Single prediction

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C",
      "q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"
    }
  }'
```

Expected:
- JSON with `pathway`, `confidence_score`, `summary`, etc.

### Validation failure check

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "q1":"A","q2":"A","q3":"A"
    }
  }'
```

Expected:
- HTTP 422 with standardized error JSON

---

## 11. Deployment Checklist

Before release:

- [ ] `models/pathway_classifier.pkl` exists and is compatible
- [ ] `python tests/test_validation.py` passes
- [ ] `python tests/test_classifier.py` passes
- [ ] `python tests/prod_smoke_test.py` passes
- [ ] `python tests/test_api.py` passes
- [ ] CORS origin configured for production UI
- [ ] API starts successfully with production command
- [ ] `/health` returns status `ok`

---

## 12. Troubleshooting

### Issue: Model file missing

Symptom:
- API returns HTTP 500 with `MODEL_NOT_FOUND`

Fix:
```bash
python src/train_model.py
```

### Issue: Validation error on request

Symptom:
- API returns HTTP 422

Fix:
- Ensure payload has exactly `q1..q12`
- Ensure each value is one of `A/B/C/D`

### Issue: CORS blocked from UI

Fix:
```bash
export CORS_ALLOW_ORIGINS="https://your-ui-domain.com"
```
Restart API server.

---

## 13. Recommended Production Command Summary

```bash
source .venv/bin/activate
pip install -r requirements.txt
python tests/test_validation.py
python tests/test_classifier.py
python tests/prod_smoke_test.py
python tests/test_api.py
export CORS_ALLOW_ORIGINS="https://your-ui-domain.com"
uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 2
```

---

## 14. Versioning

Service/API contract version:
- `1.2.0`

Recent contract change in `1.2.0`:
- single prediction only
- summary compacted to 12 paragraphs under 1,000 characters total

If request/response fields change, bump API version and update:
- `src/api.py`
- `docs/api_interface.md`
- `PRODUCTION_README.md`

---

Production guide completed for FastAPI inference deployment.
