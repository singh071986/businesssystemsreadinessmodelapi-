"""
test_validation.py
==================
Validation-focused tests for request schema rules.

Rules enforced:
- Exactly q1..q12 must be present (all mandatory).
- No extra keys are allowed.
- Each answer must be string and one of A/B/C/D.
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import classify


def _base_payload(answer: str = "A") -> dict:
    return {f"q{i}": answer for i in range(1, 13)}


def test_valid_payload_passes():
    payload = _base_payload("A")
    result = classify(payload)
    assert result["pathway"] in {"Foundation", "Growth", "Optimization"}


def test_missing_question_fails():
    payload = _base_payload("A")
    payload.pop("q12")

    try:
        classify(payload)
        assert False, "Expected missing question validation to fail."
    except Exception as exc:
        msg = str(exc)
        assert "Missing required question(s)" in msg
        assert "q12" in msg


def test_extra_question_fails():
    payload = _base_payload("A")
    payload["q13"] = "A"

    try:
        classify(payload)
        assert False, "Expected extra key validation to fail."
    except Exception as exc:
        msg = str(exc)
        assert "Unexpected question key(s)" in msg
        assert "q13" in msg


def test_invalid_answer_letter_fails():
    payload = _base_payload("A")
    payload["q5"] = "E"

    try:
        classify(payload)
        assert False, "Expected invalid answer validation to fail."
    except Exception as exc:
        msg = str(exc)
        assert "Invalid answer(s)" in msg
        assert "q5" in msg


def test_non_string_answer_fails():
    payload = _base_payload("A")
    payload["q5"] = 3

    try:
        classify(payload)
        assert False, "Expected non-string answer validation to fail."
    except Exception as exc:
        msg = str(exc)
        # Pydantic error message for non-string input
        assert "valid string" in msg or "must be a string" in msg


if __name__ == "__main__":
    # Lightweight direct runner without pytest dependency
    tests = [
        test_valid_payload_passes,
        test_missing_question_fails,
        test_extra_question_fails,
        test_invalid_answer_letter_fails,
        test_non_string_answer_fails,
    ]

    passed = 0
    failed = 0

    print("=" * 65)
    print("Validation Test Suite")
    print("=" * 65)

    for test_fn in tests:
        name = test_fn.__name__
        try:
            test_fn()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            failed += 1

    print("=" * 65)
    print(f"Results: {passed}/{len(tests)} passed, {failed} failed")
    print("=" * 65)

    sys.exit(0 if failed == 0 else 1)
