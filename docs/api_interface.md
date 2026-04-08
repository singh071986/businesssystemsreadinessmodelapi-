# API Interface Agreement (UI Integration)

## Purpose

This document defines the publish-ready API contract between the ML service and UI application.
The API serves pathway predictions from the saved model at models/pathway_classifier.pkl.

Contract version:
- `v1.2.0`

Compatibility:
- Single-prediction interface only.
- Explicit error contract and CORS support included.

Production URL:
- https://business-api.thewebsitemembership.com

Local development URL:
- http://localhost:8000

Interactive docs (production):
- Swagger UI: https://business-api.thewebsitemembership.com/docs
- ReDoc: https://business-api.thewebsitemembership.com/redoc

Interactive docs (local):
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Base URLs

Production:
- https://business-api.thewebsitemembership.com

Production endpoints:
- Health: https://business-api.thewebsitemembership.com/health
- Predict: https://business-api.thewebsitemembership.com/predict

Local:
- http://localhost:8000

Interactive API docs (local):
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

Request fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `first_name` | string | No | Client first name used to personalise the summary. Defaults to "there" if omitted. |
| `responses` | object | Yes | Object containing q1–q12 answers |
| `responses.q1`–`responses.q12` | string | Yes | Each must be one of `A`, `B`, `C`, `D` |

Request body (with first_name):
```json
{
  "first_name": "Sarah",
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

Request body (without first_name — also valid):
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
- `first_name` is optional — omit or pass `null`; summary will use "there" as salutation
- `responses` is mandatory
- q1 to q12 are all mandatory
- only q1 to q12 are allowed (no extra keys)
- each answer must be a string and one of A, B, C, D
- keys are normalised to lowercase; values are normalised to uppercase

HTTP response codes:

| Code | When | Error `code` field |
|---|---|---|
| `200` | Prediction succeeded | — |
| `422` | Any request validation failure — missing field, wrong answer letter, extra key, invalid JSON body, wrong types | `VALIDATION_ERROR` |
| `500` | Model file not found on server | `MODEL_NOT_FOUND` |
| `500` | Unexpected internal server error | `INTERNAL_ERROR` |
| `404` | Route does not exist (e.g. `/unknown`) | FastAPI default (not custom contract) |
| `405` | Wrong HTTP method (e.g. `GET /predict`) | FastAPI default (not custom contract) |

> Note: `400 Bad Request` is **never returned** by this API. All bad request scenarios (malformed body, missing fields, invalid values) return `422`.

Success response fields:
- input_responses
- input_text
- pathway
- reasoning
- confidence_score
- class_probabilities
- summary (structured object for deterministic fallback and future LLM output)
- priority_actions
- anti_priority_warnings
- graduation_outlook

Summary object fields:
- source
- intro
- narrative_paragraph_1
- narrative_paragraph_2
- recommended_focus_areas
- strongest_area
- weakest_area
- immediate_focus
- graduation_outlook
- full_report_text

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

3) Test quickly with curl (production):
```bash
curl -s https://business-api.thewebsitemembership.com/health
```

```bash
curl -s -X POST https://business-api.thewebsitemembership.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sarah",
    "responses": {
      "q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C",
      "q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"
    }
  }'
```

Or locally:
```bash
curl -s http://localhost:8000/health
```

---

## UI Integration Notes

- Use `/predict` for form submit of a single assessment.
- UI should branch on HTTP status:
  - `200`: render prediction result
  - `422`: show input validation feedback to user
  - `500`: show retry/support message
- UI should read `code`, `message`, and optionally `details` from error payload.
- Use `summary.intro`, `summary.narrative_paragraph_1`, and `summary.narrative_paragraph_2` for structured UI placement.
- Use `summary.full_report_text` for one-shot report rendering/export.

If model is missing in deployment, run:
```bash
python src/train_model.py
```

Postman verification after redeploy:
- `GET https://business-api.thewebsitemembership.com/health` should return version `1.2.0`
- `POST /predict` should return `summary` object with:
  - `intro`, `narrative_paragraph_1`, and `narrative_paragraph_2`
  - `recommended_focus_areas` list populated
  - `full_report_text` populated
