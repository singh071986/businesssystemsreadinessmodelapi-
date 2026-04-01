"""
schema.py
=========
Pydantic v2 input/output schemas for the Business Systems Readiness
Classification Engine.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Input Schema
# ---------------------------------------------------------------------------

VALID_ANSWERS = {"A", "B", "C", "D"}
REQUIRED_QUESTIONS = {f"q{i}" for i in range(1, 13)}


class AssessmentInput(BaseModel):
    """
    Input payload: 12 question responses (Q1–Q12), each answered A, B, C, or D.
    """

    responses: Dict[str, str]

    @field_validator("responses")
    @classmethod
    def validate_responses(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not isinstance(v, dict):
            raise ValueError("`responses` must be a JSON object (dictionary).")

        # Normalise keys to lowercase and validate each value is a string.
        normalised = {}
        for k, val in v.items():
            if not isinstance(k, str):
                raise ValueError("All response keys must be strings like 'q1', 'q2', ..., 'q12'.")
            if not isinstance(val, str):
                raise ValueError(
                    f"Answer for '{k}' must be a string value in A/B/C/D. Received: {type(val).__name__}."
                )
            normalised[k.lower()] = val.upper().strip()

        missing = REQUIRED_QUESTIONS - set(normalised.keys())
        if missing:
            raise ValueError(
                f"Missing required question(s): {sorted(missing)}. "
                "All 12 questions (q1–q12) must be answered."
            )

        extra = set(normalised.keys()) - REQUIRED_QUESTIONS
        if extra:
            raise ValueError(
                f"Unexpected question key(s): {sorted(extra)}. "
                "Only q1 through q12 are allowed."
            )

        invalid = {
            k: val
            for k, val in normalised.items()
            if val not in VALID_ANSWERS
        }
        if invalid:
            raise ValueError(
                f"Invalid answer(s) {invalid}. "
                "Each answer must be one of A, B, C, or D."
            )

        return normalised

    model_config = {"json_schema_extra": {
        "example": {
            "responses": {
                "q1": "C", "q2": "B", "q3": "C", "q4": "C",
                "q5": "B", "q6": "C", "q7": "C", "q8": "B",
                "q9": "C", "q10": "A", "q11": "C", "q12": "B",
            }
        }
    }}


# ---------------------------------------------------------------------------
# Output Schema
# ---------------------------------------------------------------------------

class ClassificationOutput(BaseModel):
    """
    Full classification result returned by the engine.
    """

    input_responses: Dict[str, str]
    """The original normalised responses as submitted."""

    input_text: str
    """Pipe-delimited string of all selected answer labels."""

    pathway: str
    """Predicted pathway: 'Foundation', 'Growth', or 'Optimization'."""

    reasoning: str
    """Human-readable explanation of the classification decision."""

    confidence_score: float
    """Probability of the predicted class (0.0 – 1.0)."""

    class_probabilities: Dict[str, float]
    """Probabilities for all three classes summing to 1.0."""

    summary: str
    """
    Personalised narrative (≤1,000 words) synthesised from every answer's
    detailed explanation.
    """

    priority_actions: List[str]
    """3–5 highest-leverage next steps for this pathway."""

    anti_priority_warnings: List[str]
    """2–3 actions to explicitly avoid at this stage."""

    graduation_outlook: str
    """What becomes possible once the pathway conditions are met."""

    model_config = {"json_schema_extra": {
        "example": {
            "input_responses": {
                "q1": "C", "q2": "B", "q3": "C", "q4": "C",
                "q5": "B", "q6": "C", "q7": "C", "q8": "B",
                "q9": "C", "q10": "A", "q11": "C", "q12": "B",
            },
            "input_text": (
                "I have one clear primary offer and CTA. | "
                "Basic website with limited conversion structure. | ..."
            ),
            "pathway": "Growth",
            "reasoning": (
                "Predicted Growth: 1 foundation signal detected, 0 optimization signals. "
                "No critical Foundation blockers present."
            ),
            "confidence_score": 0.7823,
            "class_probabilities": {
                "Foundation": 0.1245,
                "Growth": 0.7823,
                "Optimization": 0.0932,
            },
            "summary": "...",
            "priority_actions": [
                "Standardise your client onboarding and fulfillment into a documented workflow.",
                "Connect your payment system to automated confirmation sequences.",
            ],
            "anti_priority_warnings": [
                "Don't invest heavily in AI tools until your CRM is consistently used.",
            ],
            "graduation_outlook": (
                "Once you have standardised delivery, integrated payments, and consistent "
                "metrics review, you'll be ready to move into the Optimization pathway."
            ),
        }
    }}
