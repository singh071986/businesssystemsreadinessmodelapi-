"""
classifier.py
=============
Main classification engine for the Business Systems Readiness Assessment.

Usage (programmatic):
    from src.classifier import classify
    result = classify({"q1": "C", "q2": "B", ..., "q12": "B"})

Usage (CLI):
    python src/classifier.py '{"q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C","q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"}'
    python src/classifier.py --file data/user_request_examples.json
"""

import json
import sys
from pathlib import Path
from typing import Union

import joblib
import numpy as np

# Allow imports from root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_utils import (
    ANSWER_ENCODING,
    ANSWER_EXPLANATIONS,
    ANSWER_LABELS,
    FOUNDATION_SIGNALS,
    PATHWAY_ANTI_PRIORITY,
    PATHWAY_GRADUATION_OUTLOOK,
    PATHWAY_PRIORITY_ACTIONS,
    QUESTIONS,
    SECTION_NAMES,
    SECTION_QUESTIONS,
    rule_based_classify,
)
from src.schema import AssessmentInput, ClassificationOutput
from src.train_model import build_features

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "pathway_classifier.pkl"

_model_bundle = None  # cached after first load

SHORT_SECTION_NAMES = {
    "q1": "Q1 Offer",
    "q2": "Q2 Presence",
    "q3": "Q3 Leads",
    "q4": "Q4 CRM",
    "q5": "Q5 Follow-up",
    "q6": "Q6 Delivery",
    "q7": "Q7 Payments",
    "q8": "Q8 Reactivation",
    "q9": "Q9 Reviews",
    "q10": "Q10 AI",
    "q11": "Q11 Reporting",
    "q12": "Q12 Retention",
}

SUMMARY_TAIL = {
    1: "Build basics.",
    2: "Standardise next.",
    3: "Strong base.",
    4: "Ready to scale.",
}


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Run `python src/train_model.py` first to train and save the model."
            )
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def _build_summary(encoded: dict) -> str:
    """
    Build a personalised summary with exactly 12 concise paragraphs, one for
    each answer, while keeping the combined summary under 1,000 characters.
    """
    TOTAL_CHAR_LIMIT = 980
    separators_len = (len(QUESTIONS) - 1) * 2
    per_paragraph_limit = max(45, (TOTAL_CHAR_LIMIT - separators_len) // len(QUESTIONS))

    def _trim_chars(text: str, limit: int) -> str:
        text = " ".join(text.split()).strip()
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)].rstrip(" ,.;:") + "..."

    paragraphs = []
    for q in QUESTIONS:
        val = encoded[q]
        paragraph = (
            f"{SHORT_SECTION_NAMES[q]}: {ANSWER_LABELS[q][val]} {SUMMARY_TAIL[val]}"
        )
        paragraphs.append(_trim_chars(paragraph, per_paragraph_limit))

    summary = "\n\n".join(paragraphs)
    if len(summary) <= TOTAL_CHAR_LIMIT:
        return summary

    # Safety fallback: use tighter labels while preserving all 12 paragraphs.
    paragraphs = []
    fallback_limit = max(35, per_paragraph_limit - 10)
    for q in QUESTIONS:
        val = encoded[q]
        compact = f"{SHORT_SECTION_NAMES[q]}: {SUMMARY_TAIL[val]}"
        paragraphs.append(_trim_chars(compact, fallback_limit))

    summary = "\n\n".join(paragraphs)
    return summary[:TOTAL_CHAR_LIMIT]


# ---------------------------------------------------------------------------
# Reasoning builder
# ---------------------------------------------------------------------------

def _build_reasoning(encoded: dict, pathway: str) -> str:
    foundation_signals = sum(
        1 for q, signals in FOUNDATION_SIGNALS.items()
        if encoded.get(q, 0) in signals
    )
    optimization_signals = sum(1 for v in encoded.values() if v == 4)

    critical_blockers = []
    if encoded.get("q1", 0) == 1:
        critical_blockers.append("undefined primary offer (Q1=A)")
    if encoded.get("q4", 0) <= 2:
        critical_blockers.append("no structured CRM (Q4=A/B)")
    if encoded.get("q5", 0) <= 2:
        critical_blockers.append("no follow-up automation (Q5=A/B)")

    parts = [f"Predicted {pathway} from response pattern similarity."]

    if pathway == "Foundation":
        parts.append(
            f"{foundation_signals} Foundation-level signal(s) detected across the 12 domains."
        )
        if critical_blockers:
            parts.append(
                "Critical Foundation blockers present: " + "; ".join(critical_blockers) + "."
            )
    elif pathway == "Optimization":
        parts.append(
            f"{optimization_signals} Optimization-level (D) responses detected. "
            "No critical Foundation blockers. Strong CRM and reporting maturity confirmed."
        )
    else:  # Growth
        parts.append(
            f"{foundation_signals} Foundation signal(s) detected (threshold for Foundation is 3). "
            f"{optimization_signals} Optimization-level response(s) detected "
            "(threshold for Optimization is 4 with no blockers)."
        )
        if critical_blockers:
            parts.append(
                "Optimization blocked by: " + "; ".join(critical_blockers) + "."
            )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Main classification function
# ---------------------------------------------------------------------------

def classify(responses: Union[dict, str]) -> dict:
    """
    Classify a 12-question business systems assessment.

    Args:
        responses: dict mapping 'q1'–'q12' to 'A'/'B'/'C'/'D' (case-insensitive),
                   or a JSON string of the same shape.

    Returns:
        dict matching the ClassificationOutput schema.

    Raises:
        ValueError: if input validation fails.
        FileNotFoundError: if the model hasn't been trained yet.
    """
    # Accept raw JSON string
    if isinstance(responses, str):
        try:
            responses = json.loads(responses)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON input: {exc}") from exc

    # If the dict has a "responses" wrapper, unwrap it
    if "responses" in responses and isinstance(responses["responses"], dict):
        responses = responses["responses"]

    # Validate via Pydantic
    validated = AssessmentInput(responses=responses)
    clean = validated.responses  # normalised: lowercase keys, uppercase values

    # Encode to integers
    encoded = {q: ANSWER_ENCODING[clean[q]] for q in QUESTIONS}

    # Build feature vector
    features = np.array(build_features(encoded), dtype=float).reshape(1, -1)

    # Load model and predict
    bundle = _load_model()
    model = bundle["model"]
    scaler = bundle["scaler"]
    encoding_pathway = bundle["encoding_pathway"]

    features_scaled = scaler.transform(features)
    pred_idx = int(model.predict(features_scaled)[0])
    proba = model.predict_proba(features_scaled)[0]  # [Foundation, Growth, Optimization]

    pathway = encoding_pathway[pred_idx]
    confidence_score = float(proba[pred_idx])

    class_probabilities = {
        encoding_pathway[i]: round(float(proba[i]), 6)
        for i in range(len(proba))
    }

    # Cross-check with deterministic rule classifier
    rule_pathway = rule_based_classify(encoded)
    if rule_pathway != pathway:
        # Trust the deterministic rule for clear-cut cases
        pathway = rule_pathway
        rule_idx = {"Foundation": 0, "Growth": 1, "Optimization": 2}[rule_pathway]
        confidence_score = float(proba[rule_idx])

    # Build input_text
    input_text = " | ".join(ANSWER_LABELS[q][encoded[q]] for q in QUESTIONS)

    # Build outputs
    reasoning = _build_reasoning(encoded, pathway)
    summary = _build_summary(encoded)
    priority_actions = PATHWAY_PRIORITY_ACTIONS[pathway]
    anti_priority_warnings = PATHWAY_ANTI_PRIORITY[pathway]
    graduation_outlook = PATHWAY_GRADUATION_OUTLOOK[pathway]

    output = ClassificationOutput(
        input_responses=clean,
        input_text=input_text,
        pathway=pathway,
        reasoning=reasoning,
        confidence_score=round(confidence_score, 8),
        class_probabilities=class_probabilities,
        summary=summary,
        priority_actions=priority_actions,
        anti_priority_warnings=anti_priority_warnings,
        graduation_outlook=graduation_outlook,
    )

    return output.model_dump()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Business Systems Readiness Classifier"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help='JSON string of responses, e.g. \'{"q1":"C","q2":"B",...}\'',
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Path to a JSON file containing a single request or list of requests.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True).",
    )
    args = parser.parse_args()

    if args.file:
        with open(args.file) as fh:
            data = json.load(fh)
        # Support list of requests or single request
        requests = data if isinstance(data, list) else [data]
    elif args.input:
        requests = [json.loads(args.input)]
    else:
        parser.print_help()
        sys.exit(1)

    results = []
    for req in requests:
        result = classify(req)
        results.append(result)

    indent = 2 if args.pretty else None
    if len(results) == 1:
        print(json.dumps(results[0], indent=indent))
    else:
        print(json.dumps(results, indent=indent))


if __name__ == "__main__":
    _cli()
