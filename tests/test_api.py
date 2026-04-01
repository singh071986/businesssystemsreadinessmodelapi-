"""
API smoke tests for FastAPI interface.

Run:
    python tests/test_api.py
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api import app


def run():
    client = TestClient(app)

    print("=" * 60)
    print("API Smoke Test")
    print("=" * 60)

    # Health
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    print("[PASS] GET /health")

    # Predict single
    payload = {
        "responses": {
            "q1": "C", "q2": "B", "q3": "C", "q4": "C",
            "q5": "B", "q6": "C", "q7": "C", "q8": "B",
            "q9": "C", "q10": "A", "q11": "C", "q12": "B",
        }
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["pathway"] in {"Foundation", "Growth", "Optimization"}
    assert "confidence_score" in body
    assert len(body["summary"]) <= 1000
    assert len([part for part in body["summary"].split("\n\n") if part.strip()]) == 12
    print("[PASS] POST /predict")

    # Invalid request (missing q12)
    bad_payload = {
        "responses": {
            "q1": "A", "q2": "A", "q3": "A", "q4": "A",
            "q5": "A", "q6": "A", "q7": "A", "q8": "A",
            "q9": "A", "q10": "A", "q11": "A",
        }
    }
    r = client.post("/predict", json=bad_payload)
    assert r.status_code == 422
    err = r.json()
    assert err["code"] in {"VALIDATION_ERROR", "HTTP_ERROR"}
    assert "message" in err
    print("[PASS] POST /predict validation failure")

    print("=" * 60)
    print("Results: 2 endpoint checks + 1 validation check passed")
    print("=" * 60)


if __name__ == "__main__":
    run()
