"""
test_classifier.py
==================
Test suite for the Business Systems Readiness Classification Engine.

Runs automatically against the saved model from models/pathway_classifier.pkl.

Usage:
    python tests/test_classifier.py

Each test case prints:
    PASS / FAIL  |  Expected pathway  →  Predicted pathway  |  Confidence score
"""

import json
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import classify


# ---------------------------------------------------------------------------
# Test case definitions
# ---------------------------------------------------------------------------

TEST_CASES = [
    # ---- FOUNDATION ----
    {
        "name": "TC-01: All A answers (Deep Foundation)",
        "responses": {
            "q1": "A", "q2": "A", "q3": "A", "q4": "A",
            "q5": "A", "q6": "A", "q7": "A", "q8": "A",
            "q9": "A", "q10": "A", "q11": "A", "q12": "A",
        },
        "expected_pathway": "Foundation",
    },
    {
        "name": "TC-02: Critical blockers on Q1, Q4 — Foundation",
        "responses": {
            "q1": "A", "q2": "B", "q3": "B", "q4": "A",
            "q5": "C", "q6": "B", "q7": "B", "q8": "B",
            "q9": "B", "q10": "A", "q11": "B", "q12": "A",
        },
        "expected_pathway": "Foundation",
    },
    {
        "name": "TC-03: B-heavy with multiple A answers — Foundation",
        "responses": {
            "q1": "B", "q2": "A", "q3": "A", "q4": "B",
            "q5": "B", "q6": "A", "q7": "B", "q8": "B",
            "q9": "A", "q10": "B", "q11": "A", "q12": "B",
        },
        "expected_pathway": "Foundation",
    },
    {
        "name": "TC-04: Foundation with some C answers but 5 Foundation signals",
        "responses": {
            "q1": "A", "q2": "C", "q3": "B", "q4": "B",
            "q5": "A", "q6": "C", "q7": "B", "q8": "A",
            "q9": "C", "q10": "A", "q11": "B", "q12": "A",
        },
        "expected_pathway": "Foundation",
    },
    {
        "name": "TC-12: Borderline Foundation — Q1=A, Q3=A, Q6=A (3 signals)",
        "responses": {
            "q1": "A", "q2": "C", "q3": "A", "q4": "C",
            "q5": "C", "q6": "A", "q7": "C", "q8": "C",
            "q9": "C", "q10": "C", "q11": "C", "q12": "C",
        },
        "expected_pathway": "Foundation",
    },

    # ---- GROWTH ----
    {
        "name": "TC-05: All C answers (Solid Growth)",
        "responses": {
            "q1": "C", "q2": "C", "q3": "C", "q4": "C",
            "q5": "C", "q6": "C", "q7": "C", "q8": "C",
            "q9": "C", "q10": "C", "q11": "C", "q12": "C",
        },
        "expected_pathway": "Growth",
    },
    {
        "name": "TC-06: B/C mix — Growth, no blockers, insufficient Optimisation",
        "responses": {
            "q1": "C", "q2": "B", "q3": "C", "q4": "C",
            "q5": "B", "q6": "C", "q7": "C", "q8": "B",
            "q9": "C", "q10": "A", "q11": "C", "q12": "B",
        },
        "expected_pathway": "Growth",
    },
    {
        "name": "TC-07: Growth with 3 D answers (below Optimisation threshold)",
        "responses": {
            "q1": "C", "q2": "C", "q3": "D", "q4": "C",
            "q5": "C", "q6": "D", "q7": "C", "q8": "C",
            "q9": "D", "q10": "C", "q11": "C", "q12": "C",
        },
        "expected_pathway": "Growth",
    },
    {
        "name": "TC-11: 4 D answers but Q5=B blocks Optimisation",
        "responses": {
            "q1": "C", "q2": "C", "q3": "D", "q4": "D",
            "q5": "B", "q6": "D", "q7": "C", "q8": "D",
            "q9": "C", "q10": "C", "q11": "C", "q12": "C",
        },
        "expected_pathway": "Growth",
    },

    # ---- OPTIMIZATION ----
    {
        "name": "TC-08: All D answers (Deep Optimisation)",
        "responses": {
            "q1": "D", "q2": "D", "q3": "D", "q4": "D",
            "q5": "D", "q6": "D", "q7": "D", "q8": "D",
            "q9": "D", "q10": "D", "q11": "D", "q12": "D",
        },
        "expected_pathway": "Optimization",
    },
    {
        "name": "TC-09: Optimisation — 5 D answers, Q4=D, Q11=D, no blockers",
        "responses": {
            "q1": "C", "q2": "C", "q3": "D", "q4": "D",
            "q5": "C", "q6": "D", "q7": "D", "q8": "C",
            "q9": "D", "q10": "C", "q11": "D", "q12": "C",
        },
        "expected_pathway": "Optimization",
    },
    {
        "name": "TC-10: Minimal Optimisation — exactly 4 D answers, Q4=D, Q11=D",
        "responses": {
            "q1": "C", "q2": "C", "q3": "C", "q4": "D",
            "q5": "C", "q6": "C", "q7": "D", "q8": "D",
            "q9": "C", "q10": "C", "q11": "D", "q12": "C",
        },
        "expected_pathway": "Optimization",
    },
]


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests(verbose: bool = True) -> dict:
    passed = 0
    failed = 0
    results = []

    print("=" * 70)
    print("Business Systems Readiness — Classifier Test Suite")
    print("=" * 70)

    for tc in TEST_CASES:
        name = tc["name"]
        expected = tc["expected_pathway"]

        try:
            output = classify(tc["responses"])
            predicted = output["pathway"]
            confidence = output["confidence_score"]
            reasoning = output["reasoning"]

            ok = predicted == expected
            status = "PASS" if ok else "FAIL"

            if ok:
                passed += 1
            else:
                failed += 1

            print(
                f"  [{status}]  {name}\n"
                f"          Expected: {expected:<14} Predicted: {predicted:<14} "
                f"Confidence: {confidence:.4f}"
            )
            if not ok:
                print(f"          Reasoning: {reasoning}")
            if verbose:
                print(
                    f"          class_probabilities: "
                    f"Foundation={output['class_probabilities']['Foundation']:.3f}  "
                    f"Growth={output['class_probabilities']['Growth']:.3f}  "
                    f"Optimization={output['class_probabilities']['Optimization']:.3f}"
                )
            print()

            results.append({
                "name": name,
                "expected": expected,
                "predicted": predicted,
                "confidence": confidence,
                "passed": ok,
            })

        except Exception as exc:
            failed += 1
            print(f"  [ERROR]  {name}\n          Exception: {exc}\n")
            results.append({
                "name": name,
                "expected": expected,
                "predicted": None,
                "confidence": None,
                "passed": False,
                "error": str(exc),
            })

    print("=" * 70)
    print(f"Results: {passed}/{len(TEST_CASES)} passed, {failed} failed")
    print("=" * 70)

    return {
        "total": len(TEST_CASES),
        "passed": passed,
        "failed": failed,
        "cases": results,
    }


# ---------------------------------------------------------------------------
# Full output demo — print one complete JSON result
# ---------------------------------------------------------------------------

def demo_full_output():
    """Print a fully-expanded JSON output for a representative Growth case."""
    print("\n" + "=" * 70)
    print("DEMO — Full JSON output for TC-06 (Growth pathway)")
    print("=" * 70)
    sample = {
        "q1": "C", "q2": "B", "q3": "C", "q4": "C",
        "q5": "B", "q6": "C", "q7": "C", "q8": "B",
        "q9": "C", "q10": "A", "q11": "C", "q12": "B",
    }
    result = classify(sample)

    # Print everything except the full summary (too long for terminal)
    printable = {k: v for k, v in result.items() if k != "summary"}
    print(json.dumps(printable, indent=2))

    print(f"\n  [summary] ({len(result['summary'].split())} words — truncated below)")
    print("  " + result["summary"][:400] + " ...")


if __name__ == "__main__":
    summary = run_tests(verbose=True)
    demo_full_output()

    # Exit with non-zero code if any test failed (useful for CI)
    sys.exit(0 if summary["failed"] == 0 else 1)
