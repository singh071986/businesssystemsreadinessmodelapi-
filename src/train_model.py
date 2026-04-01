"""
train_model.py
==============
Trains a Logistic Regression multi-class classifier on the synthetic
assessment dataset and saves the model artifact to models/.

Run:
    python src/train_model.py

Outputs:
    models/pathway_classifier.pkl   — joblib-serialised model bundle
    data/training_data.json         — generated if it doesn't already exist
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Allow imports from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_utils import QUESTIONS, PATHWAY_ENCODING, ENCODING_PATHWAY, FOUNDATION_SIGNALS
from src.generate_training_data import generate_dataset

RANDOM_SEED = 42
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "pathway_classifier.pkl"
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "training_data.json"


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

def build_features(responses: dict) -> list:
    """
    Convert a {q1..q12: int(1-4)} dict into a feature vector.

    Features (17 total):
        q1..q12     — raw encoded answer (int 1-4)
        foundation_count      — questions in Foundation signal range
        growth_count          — answers == 3 (Growth level)
        optimization_count    — answers == 4 (Optimisation level)
        critical_blocker_count — count of Q1=1, Q4<=2, Q5<=2
        total_score           — sum of all encoded answers (12-48)
    """
    q_vals = [responses[q] for q in QUESTIONS]

    foundation_count = sum(
        1 for q, signals in FOUNDATION_SIGNALS.items()
        if responses.get(q, 0) in signals
    )
    growth_count = sum(1 for v in q_vals if v == 3)
    optimization_count = sum(1 for v in q_vals if v == 4)

    critical_blocker_count = (
        int(responses.get("q1", 1) == 1)
        + int(responses.get("q4", 1) <= 2)
        + int(responses.get("q5", 1) <= 2)
    )

    total_score = sum(q_vals)

    return q_vals + [
        foundation_count,
        growth_count,
        optimization_count,
        critical_blocker_count,
        total_score,
    ]


def load_or_generate_data() -> list:
    if DATA_PATH.exists():
        print(f"Loading existing training data from {DATA_PATH}")
        with open(DATA_PATH) as f:
            return json.load(f)
    print("Generating training data...")
    dataset = generate_dataset()
    DATA_PATH.parent.mkdir(exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Saved {len(dataset)} samples to {DATA_PATH}")
    return dataset


def prepare_arrays(dataset: list):
    """Build X (feature matrix) and y (label array) from dataset."""
    X, y = [], []
    for item in dataset:
        X.append(build_features(item["responses"]))
        y.append(PATHWAY_ENCODING[item["label"]])
    return np.array(X, dtype=float), np.array(y, dtype=int)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(dataset: list):
    X, y = prepare_arrays(dataset)

    # Train / test split (stratified to preserve class balance)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )

    # Feature scaling (improves LR convergence)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Logistic Regression (multi-class One-vs-Rest via OneVsRestClassifier)
    from sklearn.multiclass import OneVsRestClassifier
    base_lr = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        C=1.0,
        random_state=RANDOM_SEED,
    )
    model = OneVsRestClassifier(base_lr)
    model.fit(X_train_scaled, y_train)

    # Evaluation on hold-out test set
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)

    print(f"\nTest set accuracy: {acc:.4f} ({acc * 100:.2f}%)")
    print("\nClassification Report:")
    target_names = [ENCODING_PATHWAY[i] for i in sorted(ENCODING_PATHWAY)]
    print(classification_report(y_test, y_pred, target_names=target_names))

    # 5-fold cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    X_all_scaled = scaler.transform(X)
    cv_scores = cross_val_score(model, X_all_scaled, y, cv=cv, scoring="accuracy")
    print(f"5-fold CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    return model, scaler, acc


def save_model(model, scaler):
    MODEL_PATH.parent.mkdir(exist_ok=True)
    bundle = {
        "model": model,
        "scaler": scaler,
        "feature_names": (
            [f"q{i}" for i in range(1, 13)]
            + ["foundation_count", "growth_count", "optimization_count",
               "critical_blocker_count", "total_score"]
        ),
        "pathway_encoding": PATHWAY_ENCODING,
        "encoding_pathway": ENCODING_PATHWAY,
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"\nModel bundle saved to {MODEL_PATH}")


def main():
    print("=" * 60)
    print("Business Systems Readiness — Model Training")
    print("=" * 60)

    dataset = load_or_generate_data()
    print(f"\nLoaded {len(dataset)} training samples.")

    model, scaler, acc = train(dataset)

    if acc < 0.90:
        print(
            f"\nWARNING: Test accuracy {acc:.2%} is below the 90% threshold. "
            "Review training data generation or model hyperparameters."
        )

    save_model(model, scaler)
    print("\nTraining complete.")


if __name__ == "__main__":
    main()
