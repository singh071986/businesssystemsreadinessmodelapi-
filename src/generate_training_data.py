"""
generate_training_data.py
=========================
Generates a synthetic labelled training dataset for the pathway classifier
by applying the rule-based classification logic to systematically constructed
answer combinations.

Run:
    python src/generate_training_data.py

Output:
    data/training_data.json    — list of {"responses": {...}, "label": "..."} objects
"""

import json
import random
import sys
from pathlib import Path

# Allow imports from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_utils import QUESTIONS, rule_based_classify

RANDOM_SEED = 42
SAMPLES_PER_CLASS = 450  # ~1350 total samples


def _random_responses(weights: dict = None) -> dict:
    """Return a random {q1..q12: int 1-4} dict, optionally biased."""
    w = weights or {}
    return {
        q: random.choices(
            [1, 2, 3, 4],
            weights=w.get(q, [1, 1, 1, 1]),
            k=1,
        )[0]
        for q in QUESTIONS
    }


def _generate_foundation_sample() -> dict:
    """
    Generate one Foundation sample.
    Strategy: bias toward A/B answers, especially on critical questions
    (Q1, Q2, Q3, Q4, Q5) which have the widest Foundation ranges.
    """
    # Weights: heavily favour A and B across the board
    weights = {q: [4, 3, 2, 1] for q in QUESTIONS}
    while True:
        r = _random_responses(weights)
        if rule_based_classify(r) == "Foundation":
            return r


def _generate_growth_sample() -> dict:
    """
    Generate one Growth sample.
    Strategy: bias toward C/D on most questions; keep Foundation signals < 3
    and Optimisation conditions unmet.
    """
    weights = {q: [1, 2, 4, 2] for q in QUESTIONS}
    # Ensure critical blocker questions lean toward C/D
    for q in ["q1", "q4", "q5"]:
        weights[q] = [1, 1, 4, 2]
    # Cap Optimisation-level signals by discouraging D on CRM/reporting
    weights["q4"] = [1, 2, 5, 1]
    weights["q11"] = [1, 2, 5, 1]

    while True:
        r = _random_responses(weights)
        if rule_based_classify(r) == "Growth":
            return r


def _generate_optimization_sample() -> dict:
    """
    Generate one Optimization sample.
    Requirements:
        - Q1 >= 2 (not A)
        - Q4 >= 3, Q5 >= 3 (no critical blockers)
        - Q11 >= 3 (strong reporting)
        - At least 4 D answers
    Strategy: force D on 4+ random questions, force C/D on Q4, Q5, Q11.
    """
    weights = {q: [0, 1, 3, 5] for q in QUESTIONS}
    # Ensure no A on critical blockersweights["q1"] = [0, 2, 4, 4]
    weights["q1"] = [0, 2, 4, 4]
    weights["q4"] = [0, 0, 3, 7]
    weights["q5"] = [0, 0, 3, 7]
    weights["q11"] = [0, 0, 3, 7]

    while True:
        r = _random_responses(weights)
        if rule_based_classify(r) == "Optimization":
            return r


def generate_dataset(n_per_class: int = SAMPLES_PER_CLASS) -> list:
    """
    Generate a balanced dataset with n_per_class samples per pathway.

    Returns:
        List of dicts: [{"responses": {q1..q12: int}, "label": str}, ...]
    """
    random.seed(RANDOM_SEED)
    dataset = []

    generators = {
        "Foundation": _generate_foundation_sample,
        "Growth": _generate_growth_sample,
        "Optimization": _generate_optimization_sample,
    }

    for label, gen_fn in generators.items():
        for _ in range(n_per_class):
            responses = gen_fn()
            dataset.append({"responses": responses, "label": label})

    # Shuffle to avoid ordering artefacts
    random.shuffle(dataset)
    return dataset


def main():
    output_path = Path(__file__).resolve().parent.parent / "data" / "training_data.json"
    output_path.parent.mkdir(exist_ok=True)

    print("Generating training data...")
    dataset = generate_dataset()

    label_counts = {}
    for item in dataset:
        label_counts[item["label"]] = label_counts.get(item["label"], 0) + 1

    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"Saved {len(dataset)} samples to {output_path}")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count} samples")


if __name__ == "__main__":
    main()
