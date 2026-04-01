# API Interface Agreement (UI Integration)

## Purpose

This document defines the publish-ready API contract between the ML service and UI application.
The API serves pathway predictions from the saved model at models/pathway_classifier.pkl.

Contract version:
- `v1.2.0`

Compatibility:
- Single-prediction interface only.
- Explicit error contract and CORS support included.

Base URL (local):
- http://localhost:8000

Interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Base URLs

Local:
- http://localhost:8000

Interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Security and CORS

Current auth:
- No authentication (to be added by gateway in production).

CORS:
- Configured via environment variable `CORS_ALLOW_ORIGINS`.
- Example:
  - `CORS_ALLOW_ORIGINS=https://ui.example.com,http://localhost:3000`

---

## Endpoint Contracts

### 1) GET /health

Purpose:
- Service health check.

Success response (`200`):
```json
{
  "status": "ok",
  "service": "business-systems-readiness-api",
  "version": "1.2.0"
}
```

---

### 2) POST /predict

Purpose:
- Predict pathway for one assessment request.

Request body:
```json
{
  "responses": {
    "q1": "C",
    "q2": "B",
    "q3": "C",
    "q4": "C",
    "q5": "B",
    "q6": "C",
    "q7": "C",
    "q8": "B",
    "q9": "C",
    "q10": "A",
    "q11": "C",
    "q12": "B"
  }
}
```

Validation rules (enforced server-side):
- q1 to q12 are mandatory
- only q1 to q12 are allowed (no extra keys)
- each answer must be string and one of A, B, C, D

Success response (`200`):
- Full `ClassificationOutput` JSON payload.

Error responses:
- `422` validation failure
- `500` model missing / internal processing failure

Success response fields:
- input_responses
- input_text
- pathway
- reasoning
- confidence_score
- class_probabilities
- summary (12 paragraphs total, one per answer, combined total under 1,000 characters)
- priority_actions
- anti_priority_warnings
- graduation_outlook

---

## Error Contract (Interface Agreement)

All errors are returned using this top-level JSON shape:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "details": [
    {
      "loc": ["body", "responses"],
      "msg": "Value error, Missing required question(s): ['q12']",
      "type": "value_error"
    }
  ]
}
```

Standard codes:
- `VALIDATION_ERROR`
- `MODEL_NOT_FOUND`
- `INTERNAL_ERROR`
- `HTTP_ERROR`

---

## Run the API

1) Install dependencies:
```bash
pip install -r requirements.txt
```

2) Start server:
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

3) Test quickly with curl:
```bash
curl -s http://localhost:8000/health
```

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

---

## UI Integration Notes

- Use `/predict` for form submit of a single assessment.
- UI should branch on HTTP status:
  - `200`: render prediction result
  - `422`: show input validation feedback to user
  - `500`: show retry/support message
- UI should read `code`, `message`, and optionally `details` from error payload.

If model is missing in deployment, run:
```bash
python src/train_model.py
```

Postman verification after redeploy:
- `GET http://localhost:8000/health` should return version `1.2.0`
- `POST /predict` should return `summary` with:
  - 12 paragraphs
  - total length under 1,000 characters
