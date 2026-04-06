# API Interface Agreement (testapi.businessystem.com)

## Purpose

This document defines the published API contract for the Business Systems Readiness service deployed for testing at `testapi.businessystem.com`.

The service is a FastAPI application that serves pathway predictions using the saved model file at `models/pathway_classifier.pkl`.

Contract version:
- `v1.2.0`

Compatibility:
- Single-request prediction interface only
- Strict validation for `q1` through `q12`
- Consistent JSON error contract for application-level failures
- CORS support via environment variable

## Base URLs

Primary deployed test URL:
- `https://testapi.businessystem.com`

Primary deployed endpoints:
- Health: `https://testapi.businessystem.com/health`
- Predict: `https://testapi.businessystem.com/predict`
- Swagger UI: `https://testapi.businessystem.com/docs`
- ReDoc: `https://testapi.businessystem.com/redoc`

Local development URL:
- `http://localhost:8000`

Local development endpoints:
- Health: `http://localhost:8000/health`
- Predict: `http://localhost:8000/predict`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security and CORS

Authentication:
- No authentication is currently enforced by the application
- Add authentication upstream with a gateway, proxy, or WAF if needed

CORS:
- Controlled by environment variable `CORS_ALLOW_ORIGINS`
- Default behavior allows all origins when the variable is `*`
- Example restricted configuration:

```bash
export CORS_ALLOW_ORIGINS="https://ui.example.com,http://localhost:3000"
```

## Content Type

Requests:
- `Content-Type: application/json`

Responses:
- Success responses return JSON
- Application-level errors return JSON
- DNS, TLS, or proxy failures may return non-JSON output before the request reaches FastAPI

## Endpoint Contracts

### 1) GET /health

Purpose:
- Verifies that the FastAPI application is running and routable

Success response (`200`):

```json
{
  "status": "ok",
  "service": "business-systems-readiness-api",
  "version": "1.2.0"
}
```

Response fields:
- `status`: service health marker
- `service`: service identifier string
- `version`: FastAPI app version

### 2) POST /predict

Purpose:
- Predicts the pathway for one assessment submission

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

Validation rules enforced by the application:
- `responses` must be a JSON object
- `q1` through `q12` are all required
- No keys other than `q1` through `q12` are allowed
- Every answer must be a string
- Each answer must be one of `A`, `B`, `C`, or `D`
- Keys are normalized to lowercase and values are normalized to uppercase

Success response (`200`):
- Returns the full classification output object

Success response fields:
- `input_responses`
- `input_text`
- `pathway`
- `reasoning`
- `confidence_score`
- `class_probabilities`
- `summary`
- `priority_actions`
- `anti_priority_warnings`
- `graduation_outlook`

Example success response:

```json
{
  "input_responses": {
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
  },
  "input_text": "I have one clear primary offer and CTA. | Basic website with limited conversion structure. | ...",
  "pathway": "Growth",
  "reasoning": "Predicted Growth: 1 foundation signal detected, 0 optimization signals. No critical Foundation blockers present.",
  "confidence_score": 0.7823,
  "class_probabilities": {
    "Foundation": 0.1245,
    "Growth": 0.7823,
    "Optimization": 0.0932
  },
  "summary": {
    "source": "deterministic_fallback",
    "intro": "{{client_name}}, your results place you in the Growth stage right now. Predicted Growth from response pattern similarity.",
    "narrative_paragraph_1": "The clearest pressure points right now sit in Presence System, Nurture & Follow-Up System, and Reactivation & Outreach System. Those areas still rely on manual effort or inconsistent execution, which makes the business feel heavier to run than it should.",
    "narrative_paragraph_2": "Your current strength is most visible in Clarity & Offer System, Lead Capture System, and Customer Journey / CRM System. As the weaker systems catch up, those stronger areas become easier to scale without adding the same level of personal effort.",
    "recommended_focus_areas": [
      "Standardise your client onboarding and fulfillment into a documented workflow.",
      "Connect your payment system to automated confirmation and onboarding sequences.",
      "Launch a structured reactivation campaign to your existing database.",
      "Implement a consistent review request process at the close of every client engagement.",
      "Set up a regular metrics review cadence — weekly or monthly — using a simple dashboard."
    ],
    "strongest_area": "Customer Journey / CRM System",
    "weakest_area": "AI Engagement & Conversion System",
    "immediate_focus": "Standardise your client onboarding and fulfillment into a documented workflow.",
    "graduation_outlook": "Once you have standardised delivery, integrated payments, a structured reactivation strategy, and consistent metrics review in place, you'll be ready to move into the Optimization pathway — where your focus shifts to AI-assisted engagement, lifecycle automation, and continuous performance improvement.",
    "full_report_text": "{{client_name}}, your results place you in the Growth stage right now. Predicted Growth from response pattern similarity.\n\nThe clearest pressure points right now sit in Presence System, Nurture & Follow-Up System, and Reactivation & Outreach System. Those areas still rely on manual effort or inconsistent execution, which makes the business feel heavier to run than it should.\n\nYour current strength is most visible in Clarity & Offer System, Lead Capture System, and Customer Journey / CRM System. As the weaker systems catch up, those stronger areas become easier to scale without adding the same level of personal effort.\n\nYour recommended focus areas:\n- Standardise your client onboarding and fulfillment into a documented workflow.\n- Connect your payment system to automated confirmation and onboarding sequences.\n- Launch a structured reactivation campaign to your existing database.\n- Implement a consistent review request process at the close of every client engagement.\n- Set up a regular metrics review cadence — weekly or monthly — using a simple dashboard.\n\nOnce you have standardised delivery, integrated payments, a structured reactivation strategy, and consistent metrics review in place, you'll be ready to move into the Optimization pathway — where your focus shifts to AI-assisted engagement, lifecycle automation, and continuous performance improvement."
  },
  "priority_actions": [
    "Standardise your client onboarding and fulfillment into a documented workflow.",
    "Connect your payment system to automated confirmation sequences."
  ],
  "anti_priority_warnings": [
    "Don't invest heavily in AI tools until your CRM is consistently used."
  ],
  "graduation_outlook": "Once you have standardised delivery, integrated payments, and consistent metrics review, you'll be ready to move into the Optimization pathway."
}
```

## summary Contract

`summary` is a structured narrative object rendered directly by the UI.

Current source:
- `deterministic_fallback`

Available source options:
- `deterministic_fallback`
- `llm_generated`

Fields:
- `source`: where the report content came from
- `intro`: opening paragraph for the report
- `narrative_paragraph_1`: first main narrative paragraph
- `narrative_paragraph_2`: second main narrative paragraph
- `recommended_focus_areas`: ordered list of focus areas for the current pathway
- `strongest_area`: strongest detected system area
- `weakest_area`: weakest detected system area
- `immediate_focus`: highest-priority next focus area
- `graduation_outlook`: pathway-based graduation statement
- `full_report_text`: fully assembled fallback report text

UI guidance:
- Use the full `summary` object when you want richer structured rendering
- `summary.full_report_text` is suitable for immediate display if the UI does not want to assemble sections itself

## Application Error Contract

All application-generated errors use this top-level JSON shape:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "details": []
}
```

Supported application error codes:
- `VALIDATION_ERROR`
- `MODEL_NOT_FOUND`
- `INTERNAL_ERROR`
- `HTTP_ERROR`

### 422 Validation Error

Returned when request body validation fails or when invalid payload values are passed into the classifier.

Example:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "details": [
    {
      "type": "value_error",
      "loc": ["body", "responses"],
      "msg": "Value error, Missing required question(s): ['q12']. All 12 questions (q1–q12) must be answered.",
      "input": {
        "q1": "C"
      }
    }
  ]
}
```

### 500 Model Not Found

Returned when the saved model file is missing on the server.

Example:

```json
{
  "code": "MODEL_NOT_FOUND",
  "message": "Saved model file not found. Train model before inference.",
  "details": "[Errno 2] No such file or directory: '.../models/pathway_classifier.pkl'"
}
```

### 500 Internal Error

Returned when an unexpected server-side exception occurs during prediction.

Example:

```json
{
  "code": "INTERNAL_ERROR",
  "message": "Unexpected server error during prediction.",
  "details": "..."
}
```

## Network, DNS, and HTTPS Failures

These failures happen before the request reaches FastAPI, so they are not returned in the JSON error contract.

Examples:
- DNS not published: `curl: (6) Could not resolve host`
- TLS certificate mismatch: `curl: (60) SSL: no alternative certificate subject name matches target hostname`
- Proxy or host routing failure: HTML `404` page from LiteSpeed or cPanel instead of JSON

Handling guidance for UI and external clients:
- Treat DNS failures as environment or deployment issues
- Treat TLS certificate errors as SSL provisioning or hostname mismatch issues
- Treat non-JSON HTML `404` or `5xx` responses as web server or routing failures, not API contract responses

## HTTP Status Handling

Client behavior should branch on these statuses:
- `200`: render result or health payload
- `422`: show validation feedback using `code`, `message`, and `details`
- `500`: show retry or support message using `code`, `message`, and `details`

Non-application cases to handle separately:
- DNS resolution failure
- TLS certificate validation failure
- Network timeout
- HTML error page returned by proxy or host routing layer

## cURL Examples

### Deployed health check

```bash
curl -i https://testapi.businessystem.com/health
```

### Deployed prediction request

```bash
curl -i -X POST https://testapi.businessystem.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C",
      "q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"
    }
  }'
```

### Local health check

```bash
curl -i http://localhost:8000/health
```

### Local prediction request

```bash
curl -i -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C",
      "q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"
    }
  }'
```

## UI Consumer Scope

This document is intended for UI integration only.

The UI application does not need:
- backend source code
- `requirements.txt`
- `python src/train_model.py`
- model training steps

The UI application only needs:
- the base URL
- endpoint URLs
- request payload shape
- success response shape
- application error contract
- handling guidance for DNS, TLS, and non-JSON failures

## Deployment Verification Checklist

The deployed service is considered healthy only when all of these are true:
- `https://testapi.businessystem.com/health` returns HTTP `200` JSON
- `https://testapi.businessystem.com/predict` returns HTTP `200` JSON
- `https://testapi.businessystem.com/docs` loads Swagger UI
- SSL certificate is valid for `testapi.businessystem.com`
- DNS resolves publicly for `testapi.businessystem.com`
- `models/pathway_classifier.pkl` exists on the server

## UI Integration Notes

- Submit one completed assessment per `/predict` request
- Always send JSON with `Content-Type: application/json`
- Parse JSON only when the response content type is JSON
- If the response is HTML or the request fails before HTTP response, treat it as deployment or network failure
- For `422`, show validation feedback to the user
- For `500`, show a retry or support message
- The UI team does not need the backend project files to consume the deployed API