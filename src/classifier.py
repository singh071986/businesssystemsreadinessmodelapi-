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
    PATHWAY_PRIORITY_SECTIONS,
    QUESTIONS,
    SECTION_FOCUS_DESCRIPTIONS,
    SECTION_NAMES,
    rule_based_classify,
)
from src.schema import AssessmentInput, ClassificationOutput
from src.train_model import build_features
from src.llm_summary import build_llm_summary

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


def _first_sentence(text: str) -> str:
    text = " ".join(text.split()).strip()
    for delimiter in (". ", "? ", "! "):
        if delimiter in text:
            return text.split(delimiter, 1)[0].strip() + text[text.find(delimiter): text.find(delimiter) + 1]
    return text


def _extract_reasoning_signals(reasoning: str) -> list[str]:
    lines = []
    for raw_line in reasoning.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        if line and line[-1] not in ".!?":
            line += "."
        lines.append(line)

    if lines:
        return lines

    parts = [part.strip() for part in reasoning.split(". ") if part.strip()]
    cleaned_parts = []
    for part in parts:
        if part and part[-1] not in ".!?":
            part += "."
        cleaned_parts.append(part)
    return cleaned_parts


def _build_summary_object(
    clean: dict, encoded: dict, pathway: str, reasoning: str, first_name: str = "there"
) -> dict:
    priority_qs = list(PATHWAY_PRIORITY_SECTIONS[pathway])

    # For Optimization, also include any D-answer sections not already in the priority list
    if pathway == "Optimization":
        d_extras = [q for q in QUESTIONS if encoded[q] == 4 and q not in priority_qs]
        all_relevant_qs = priority_qs + d_extras[:3]
    else:
        all_relevant_qs = priority_qs

    # Split into gaps (≤2) and strengths (≥3) within the pathway-relevant sections
    gap_qs = [q for q in all_relevant_qs if encoded[q] <= 2]
    strength_qs = [q for q in all_relevant_qs if encoded[q] >= 3]

    # --- Paragraph 1: friction/gaps grounded in the actual section blurbs ---
    if gap_qs:
        gap_names = ", ".join(SECTION_NAMES[q] for q in gap_qs[:3])
        gap_blurb_sentences = [
            _first_sentence(ANSWER_EXPLANATIONS[q][encoded[q]]) for q in gap_qs[:2]
        ]
        narrative_paragraph_1 = (
            f"The clearest friction right now sits in {gap_names}. "
            + " ".join(gap_blurb_sentences)
        )
    else:
        fallback_blurb = _first_sentence(
            ANSWER_EXPLANATIONS[all_relevant_qs[0]][encoded[all_relevant_qs[0]]]
        )
        narrative_paragraph_1 = (
            "Your priority systems are already performing well. "
            + fallback_blurb
            + " The opportunity now is tightening consistency across the remaining areas."
        )

    # --- Paragraph 2: shift toward what becomes possible ---
    if strength_qs:
        strength_names = " and ".join(SECTION_NAMES[q] for q in strength_qs[:2])
        strength_blurb = _first_sentence(ANSWER_EXPLANATIONS[strength_qs[0]][encoded[strength_qs[0]]])
        narrative_paragraph_2 = (
            f"Where your systems are already solid — particularly in {strength_names} — that foundation is working for you. "
            + strength_blurb
            + " As the remaining gaps close, the business becomes easier to run and more reliable to grow."
        )
    else:
        narrative_paragraph_2 = (
            "Once the systems in your priority areas are installed and running consistently, "
            "the business becomes more predictable, easier to manage, and ready to grow without "
            "depending entirely on your personal effort."
        )

    # --- Intro: 'Hi [name],' on its own line, pathway context + 1-2 reasoning signals ---
    reasoning_parts = _extract_reasoning_signals(reasoning)
    signal_parts = reasoning_parts[1:3] if len(reasoning_parts) > 1 else reasoning_parts[:2]
    signal_text = " ".join(signal_parts).strip()
    if signal_text and not signal_text.endswith("."):
        signal_text += "."

    pathway_context = {
        "Foundation": (
            "your results show you're in the business-building stage — working with real momentum "
            "and real gaps at the same time"
        ),
        "Growth": (
            "your foundation is largely in place, which means the work ahead is about making your "
            "systems more consistent and connected"
        ),
        "Optimization": (
            "your core systems are working well, which means the focus now shifts to deepening and "
            "automating what you've already built"
        ),
    }

    intro = (
        f"Hi {first_name},\n"
        f"Based on your answers, {pathway_context[pathway]}. "
        + (f"{signal_text} " if signal_text else "")
        + "Here's what your results show."
    )

    # --- Recommended focus areas: Section Name + one-line description ---
    focus_areas = [SECTION_FOCUS_DESCRIPTIONS[q] for q in priority_qs[:5]]

    # --- Support fields ---
    strongest_q = max(QUESTIONS, key=lambda q: (encoded[q], q))
    weakest_q = min(QUESTIONS, key=lambda q: (encoded[q], q))
    immediate_focus = SECTION_FOCUS_DESCRIPTIONS[priority_qs[0]].split(":")[0].strip()
    graduation_outlook = PATHWAY_GRADUATION_OUTLOOK[pathway]

    focus_lines = "\n".join(f"- {item}" for item in focus_areas)
    full_report_text = (
        f"{intro}\n\n"
        f"{narrative_paragraph_1}\n\n"
        f"{narrative_paragraph_2}\n\n"
        f"Your recommended focus areas:\n{focus_lines}\n\n"
        f"{graduation_outlook}"
    )

    return {
        "source": "deterministic_fallback",
        "intro": intro,
        "narrative_paragraph_1": narrative_paragraph_1,
        "narrative_paragraph_2": narrative_paragraph_2,
        "recommended_focus_areas": focus_areas,
        "strongest_area": SECTION_NAMES[strongest_q],
        "weakest_area": SECTION_NAMES[weakest_q],
        "immediate_focus": immediate_focus,
        "graduation_outlook": graduation_outlook,
        "full_report_text": full_report_text,
    }


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
        critical_blockers.append("offer clarity is still being defined")
    if encoded.get("q4", 0) <= 2:
        critical_blockers.append("CRM structure is still too light to give you a reliable picture of the pipeline")
    if encoded.get("q5", 0) <= 2:
        critical_blockers.append("follow-up still depends too heavily on manual effort")

    priority_qs = list(PATHWAY_PRIORITY_SECTIONS[pathway])
    weakest_qs = [q for q in priority_qs if encoded[q] <= 2]
    strongest_qs = [q for q in priority_qs if encoded[q] >= 3]

    opening_signal = {
        "Foundation": (
            "Several of your answers point to core systems that are still being built, which is why the business likely feels heavier to run than it should."
        ),
        "Growth": (
            "Your answers show that the fundamentals are in place, but several key systems are only partially running, which creates drag as volume increases."
        ),
        "Optimization": (
            "Your answers reflect a business with real operational maturity, so the next gains come from tightening performance rather than rebuilding basics."
        ),
    }[pathway]

    signals = [opening_signal]

    if strongest_qs and pathway in {"Growth", "Optimization"}:
        signals.append(_first_sentence(ANSWER_EXPLANATIONS[strongest_qs[0]][encoded[strongest_qs[0]]]))

    weakest_limit = 3 if pathway == "Foundation" else 2
    for q in weakest_qs[:weakest_limit]:
        signals.append(_first_sentence(ANSWER_EXPLANATIONS[q][encoded[q]]))

    if pathway == "Foundation":
        signals.append(
            f"Right now, {foundation_signals} of the 12 business domains are still showing foundation-stage patterns, so a few simple systems will create an outsized lift."
        )
    elif pathway == "Growth":
        if critical_blockers:
            blocker_text = "; ".join(critical_blockers)
            signals.append(
                f"Right now, full optimization is being held back because {blocker_text}, even though the underlying business has real momentum."
            )
        elif optimization_signals:
            signals.append(
                f"You already have {optimization_signals} area(s) performing at an optimization level, which is a strong sign that the next step is consistency rather than reinvention."
            )
    else:  # Optimization
        next_lever_qs = [q for q in priority_qs if encoded[q] < 4]
        if next_lever_qs:
            next_lever_names = " and ".join(SECTION_NAMES[q] for q in next_lever_qs[:2])
            signals.append(
                f"The clearest next-level opportunity now sits in {next_lever_names}, where stronger automation or tighter execution would unlock more leverage from what is already working."
            )
        else:
            signals.append(
                "Across the board, your systems are already strong, so the work now is about refinement, speed, and higher-leverage automation."
            )

    deduped_signals = []
    seen = set()
    for signal in signals:
        cleaned = " ".join(signal.split()).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped_signals.append(cleaned)

    return "\n".join(f"- {signal}" for signal in deduped_signals[:5])


# ---------------------------------------------------------------------------
# Main classification function
# ---------------------------------------------------------------------------

def classify(responses: Union[dict, str], first_name: str = "there") -> dict:
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
    deterministic_summary = _build_summary_object(
        clean,
        encoded,
        pathway,
        reasoning,
        first_name=first_name,
    )
    llm_summary = build_llm_summary(
        first_name=first_name,
        pathway=pathway,
        reasoning=reasoning,
        encoded=encoded,
        deterministic_summary=deterministic_summary,
    )
    summary = llm_summary or deterministic_summary
    priority_actions = PATHWAY_PRIORITY_ACTIONS[pathway]
    anti_priority_warnings = PATHWAY_ANTI_PRIORITY[pathway]

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
