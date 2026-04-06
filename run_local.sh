#!/usr/bin/env bash
# run_local.sh
# ------------
# Starts the FastAPI app locally with LLM and all env vars loaded from .env.local.
# Mirrors production cPanel config so local == prod behaviour.
#
# Usage:
#   chmod +x run_local.sh   (one time)
#   ./run_local.sh

set -e

ENV_FILE=".env.local"

if [[ ! -f "$ENV_FILE" ]]; then
  echo ""
  echo "ERROR: $ENV_FILE not found."
  echo ""
  echo "Run these steps first:"
  echo "  cp .env.local.example .env.local"
  echo "  # Edit .env.local and add your ANTHROPIC_API_KEY"
  echo ""
  exit 1
fi

# Load .env.local into shell environment
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo ""
echo "=== Local run (production-equivalent) ==="
echo "  SUMMARY_SOURCE     : ${SUMMARY_SOURCE}"
echo "  ANTHROPIC_MODEL    : ${ANTHROPIC_MODEL}"
echo "  ANTHROPIC_API_KEY  : ${ANTHROPIC_API_KEY:0:12}... (truncated)"
echo "  CORS_ALLOW_ORIGINS : ${CORS_ALLOW_ORIGINS}"
echo ""
echo "  API docs  : http://localhost:8000/docs"
echo "  Health    : http://localhost:8000/health"
echo "  Predict   : http://localhost:8000/predict"
echo ""

.venv311/bin/uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
