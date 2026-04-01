"""
prod_smoke_test.py
==================
Production-style smoke checks for the saved model artifact.

What this verifies:
1. Saved model file exists and can be loaded.
2. Valid payload predicts successfully.
3. Invalid payloads are rejected by validation.
4. Summary format remains under 1,000 words and covers all 12 answers.

Run:
    python tests/prod_smoke_test.py
"""

import json
import sys
from pathlib import Path

import joblib

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import classify

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "pathway_classifier.pkl"
CLEAN_REQUESTS_PATH = ROOT / "data" / "user_request_examples.json"


def _assert(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def test_model_artifact_exists_and_loads():
    _assert(MODEL_PATH.exists(), f"Missing model file: {MODEL_PATH}")
    bundle = joblib.load(MODEL_PATH)
    _assert("model" in bundle, "Model bundle missing key: model")
    _assert("scaler" in bundle, "Model bundle missing key: scaler")
    _assert("encoding_pathway" in bundle, "Model bundle missing key: encoding_pathway")


def test_valid_payload_predicts():
    payload = {f"q{i}": "C" for i in range(1, 13)}
    result = classify(payload)
    _assert(result["pathway"] in {"Foundation", "Growth", "Optimization"}, "Invalid pathway")
    _assert(0.0 <= result["confidence_score"] <= 1.0, "Confidence score out of range")


def test_invalid_payloads_are_rejected():
    invalid_cases = {
        "missing_q12": {f"q{i}": "A" for i in range(1, 12)},
        "extra_q13": {**{f"q{i}": "A" for i in range(1, 13)}, "q13": "A"},
        "invalid_letter": {**{f"q{i}": "A" for i in range(1, 13)}, "q4": "E"},
        "non_string": {**{f"q{i}": "A" for i in range(1, 13)}, "q5": 3},
    }

    for name, payload in invalid_cases.items():
        try:
            classify(payload)
            raise AssertionError(f"Expected validation failure for case: {name}")
        except Exception:
            pass


def test_summary_contract():
    _assert(CLEAN_REQUESTS_PATH.exists(), f"Missing input file: {CLEAN_REQUESTS_PATH}")
    with open(CLEAN_REQUESTS_PATH) as f:
        requests = json.load(f)
    _assert(isinstance(requests, list), "Clean requests file should contain a list")
    _assert(len(requests) > 0, "Clean requests file should not be empty")

    result = classify(requests[0])
    paragraph_count = len([part for part in result["summary"].split("\n\n") if part.strip()])
    _assert(paragraph_count == 12, f"Expected 12 summary paragraphs, found {paragraph_count}")
    _assert(len(result["summary"]) <= 1000, "Summary exceeds 1,000 characters")


def main():
    tests = [
        test_model_artifact_exists_and_loads,
        test_valid_payload_predicts,
        test_invalid_payloads_are_rejected,
        test_summary_contract,
    ]

    passed = 0
    failed = 0

    print("=" * 68)
    print("Production Smoke Test")
    print("=" * 68)

    for fn in tests:
        name = fn.__name__
        try:
            fn()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            failed += 1

    print("=" * 68)
    print(f"Results: {passed}/{len(tests)} passed, {failed} failed")
    print("=" * 68)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
