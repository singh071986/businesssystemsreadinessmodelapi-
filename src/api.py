"""
FastAPI interface for Business Systems Readiness classifier.

Run locally:
    uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
"""

import os
import time
import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.classifier import MODEL_PATH, classify
from src.logging_utils import get_app_logger, get_runtime_context, log_event
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

app_logger = get_app_logger("business_api.api")


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _expose_error_details() -> bool:
    # Keep internal exception strings hidden by default in production responses.
    return _is_truthy(os.getenv("API_EXPOSE_ERROR_DETAILS", "false"))


# UI integration support: configure allowed origins via environment variable.
# Example:
#   export CORS_ALLOW_ORIGINS="https://ui.example.com,http://localhost:3000"
origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
allow_origins = ["*"] if origins_raw == "*" else [o.strip() for o in origins_raw.split(",") if o.strip()]
allow_credentials = False if allow_origins == ["*"] else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def log_startup() -> None:
    log_event(
        app_logger,
        "app_startup",
        version=app.version,
        cors_allow_origins=allow_origins,
        model_exists=MODEL_PATH.exists(),
        model_path=str(MODEL_PATH),
        **get_runtime_context(),
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    started_at = time.perf_counter()

    log_event(
        app_logger,
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query=request.url.query or None,
        host=request.headers.get("host"),
        forwarded_for=request.headers.get("x-forwarded-for"),
        client_host=request.client.host if request.client else None,
        content_type=request.headers.get("content-type"),
        content_length=request.headers.get("content-length"),
    )

    try:
        response = await call_next(request)
    except Exception as exc:
        log_event(
            app_logger,
            "request_failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            elapsed_ms=round((time.perf_counter() - started_at) * 1000, 2),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise

    response.headers["X-Request-ID"] = request_id
    log_event(
        app_logger,
        "request_finished",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        elapsed_ms=round((time.perf_counter() - started_at) * 1000, 2),
        response_content_length=response.headers.get("content-length"),
    )
    return response


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Return validation errors in a consistent API contract format."""
    log_event(
        app_logger,
        "request_validation_error",
        request_id=getattr(request.state, "request_id", None),
        path=request.url.path,
        method=request.method,
        details=jsonable_encoder(exc.errors()),
    )
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
    log_event(
        app_logger,
        "http_exception",
        request_id=getattr(request.state, "request_id", None),
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        code=payload.code,
        details=payload.details,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health_check():
    log_event(app_logger, "health_check")
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
def predict(payload: AssessmentInput, request: Request):
    """
    Predict pathway for a single assessment payload.
    """
    request_id = getattr(request.state, "request_id", None)
    log_event(
        app_logger,
        "predict_started",
        request_id=request_id,
        first_name_provided=payload.first_name is not None,
        response_keys=sorted(payload.responses.keys()),
    )
    try:
        result = classify(
            payload.responses,
            first_name=payload.first_name or "there",
            request_id=request_id,
        )
        log_event(
            app_logger,
            "predict_finished",
            request_id=request_id,
            pathway=result["pathway"],
            confidence_score=result["confidence_score"],
        )
        return ClassificationOutput(**result)
    except FileNotFoundError as exc:
        log_event(
            app_logger,
            "predict_model_not_found",
            request_id=request_id,
            error=str(exc),
        )
        error = ApiError(
            code="MODEL_NOT_FOUND",
            message="Saved model file not found. Train model before inference.",
            details=str(exc) if _expose_error_details() else None,
        )
        raise HTTPException(status_code=500, detail=error.model_dump()) from exc
    except ValueError as exc:
        log_event(
            app_logger,
            "predict_value_error",
            request_id=request_id,
            error=str(exc),
        )
        error = ApiError(
            code="VALIDATION_ERROR",
            message="Invalid assessment payload.",
            details=str(exc),
        )
        raise HTTPException(status_code=422, detail=error.model_dump()) from exc
    except Exception as exc:
        app_logger.exception("predict_unhandled_exception request_id=%s", request_id)
        error = ApiError(
            code="INTERNAL_ERROR",
            message="Unexpected server error during prediction.",
            details=str(exc) if _expose_error_details() else None,
        )
        raise HTTPException(status_code=500, detail=error.model_dump()) from exc
