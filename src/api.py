"""
FastAPI interface for Business Systems Readiness classifier.

Run locally:
    uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
"""

import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.classifier import classify
from src.schema import AssessmentInput, ClassificationOutput


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


app = FastAPI(
    title="Business Systems Readiness API",
    version="1.2.0",
    description=(
        "API interface for pathway classification using the saved logistic "
        "regression model. Single-prediction only, with strict input "
        "validation, consistent error contract, and UI-ready JSON responses."
    ),
)

# UI integration support: configure allowed origins via environment variable.
# Example:
#   export CORS_ALLOW_ORIGINS="https://ui.example.com,http://localhost:3000"
origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
allow_origins = ["*"] if origins_raw == "*" else [o.strip() for o in origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Return validation errors in a consistent API contract format."""
    payload = ApiError(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        details=jsonable_encoder(exc.errors()),
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Normalize HTTPException into the agreed API error shape."""
    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        payload = ApiError(**exc.detail)
    else:
        payload = ApiError(
            code="HTTP_ERROR",
            message="Request failed.",
            details=exc.detail,
        )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health_check():
    return HealthResponse(
        status="ok",
        service="business-systems-readiness-api",
        version=app.version,
    )


@app.post(
    "/predict",
    response_model=ClassificationOutput,
    responses={
        422: {"model": ApiError, "description": "Validation error"},
        500: {"model": ApiError, "description": "Server/model error"},
    },
    tags=["Classification"],
)
def predict(payload: AssessmentInput):
    """
    Predict pathway for a single assessment payload.
    """
    try:
        result = classify(payload.responses, first_name=payload.first_name or "there")
        return ClassificationOutput(**result)
    except FileNotFoundError as exc:
        error = ApiError(
            code="MODEL_NOT_FOUND",
            message="Saved model file not found. Train model before inference.",
            details=str(exc),
        )
        raise HTTPException(status_code=500, detail=error.model_dump()) from exc
    except ValueError as exc:
        error = ApiError(
            code="VALIDATION_ERROR",
            message="Invalid assessment payload.",
            details=str(exc),
        )
        raise HTTPException(status_code=422, detail=error.model_dump()) from exc
    except Exception as exc:
        error = ApiError(
            code="INTERNAL_ERROR",
            message="Unexpected server error during prediction.",
            details=str(exc),
        )
        raise HTTPException(status_code=500, detail=error.model_dump()) from exc
