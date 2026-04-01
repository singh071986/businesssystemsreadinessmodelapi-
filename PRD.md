# Product Requirements Document (PRD)
## Business Systems Readiness — ML Classification Engine

**Version:** 1.0  
**Date:** March 22, 2026  
**Owner:** Project Lead  
**Status:** Approved for Development

---

## 1. Overview

### 1.1 Purpose
Build a Machine Learning Classification Engine that takes a user's 12-question survey responses and predicts their **Business Systems Readiness Pathway** (Foundation, Growth, or Optimization) using logistic regression models. The engine produces deterministic, human-readable outputs with confidence scores and actionable summaries.

### 1.2 Background
Business owners complete a structured 12-question assessment covering all core system domains: offer clarity, online presence, lead capture, CRM, follow-up, delivery, payments, reactivation, reviews, AI usage, reporting, and retention. Based on response patterns, they are classified into one of three readiness pathways, each mapped to specific action plans.

### 1.3 Goals
- Accurately classify users into Foundation, Growth, or Optimization pathways.
- Provide human-readable reasoning for every classification.
- Generate a personalized summary (≤1,000 words) combining per-answer insights.
- Produce confidence scores from logistic regression probabilities.
- Deliver all outputs as structured JSON.

---

## 2. Scope

### 2.1 In Scope
- **Classification Engine**: Logistic regression multi-class classifier (Foundation / Growth / Optimization).
- **Feature Engineering**: 12 encoded question responses + 5 derived features (foundation count, growth count, optimization count, critical blocker count, total score).
- **Pathway Assignment**: Rule-aligned thresholds encoded in training data.
- **Summary Generation**: Template-based, drawing from per-answer explanation texts sourced from the Assessment Question Results document.
- **Output Schema**: Structured JSON output including `pathway`, `reasoning`, `confidence_score`, `summary`, `priority_actions`, `anti_priority_warnings`, `graduation_outlook`.
- **Input Validation**: Pydantic-based schema validation for 12-question responses (A–D).
- **Saved Model**: Serialised `.pkl` file (scikit-learn + joblib).
- **Test Cases**: Minimum 10 sample inputs covering all three pathways.

### 2.2 Out of Scope
- UI/UX development
- Deployment, hosting, or containerisation
- User authentication and session management
- Real-time API endpoints
- Model retraining pipelines

---

## 3. Assessment Question Framework

### 3.1 Questions and Answer Options

| # | Section | Question | A | B | C | D |
|---|---------|----------|---|---|---|---|
| Q1 | Clarity & Offer System | How clearly defined is your primary offer? | Still refining | Multiple offers, no focus | One clear offer + CTA | One offer, defined positioning + proof |
| Q2 | Presence System | What best describes your online presence? | No structured website | Basic website, limited conversion | Structured site, clear conversion path | Website + targeted landing pages |
| Q3 | Lead Capture System | How are leads captured? | Manual inquiries (email/DM) | Basic contact form / booking link | Form/booking with automated confirmations | Multi-step qualification (forms, AI, funnels) |
| Q4 | Customer Journey / CRM | How structured is your CRM and customer journey? | Inbox or spreadsheet | CRM exists but inconsistent use | Defined journey stages, consistent use | Lifecycle stages + segmentation + reporting |
| Q5 | Nurture & Follow-Up | What follow-up happens after inquiry? | Manual replies only | Templates but no automation | Automated confirmations + reminders | Multi-step nurture sequences |
| Q6 | Delivery System | How standardized is client onboarding and fulfillment? | Varies each time | Manual checklist, inconsistent | Structured onboarding workflow | Automated lifecycle transitions |
| Q7 | Payments & Offers | How are payments and offers handled? | Manual invoicing only | Online payments, limited automation | Integrated checkout + confirmation workflows | Subscriptions, order bumps, automated workflows |
| Q8 | Reactivation & Outreach | Do you actively monetize your existing database? | No reactivation efforts | Occasional manual outreach | Structured reactivation campaigns | Automated lifecycle-based reactivation + AI |
| Q9 | Reputation & Reviews | How do you generate and manage reviews? | No review system | Manual requests occasionally | Structured review request workflow | Automated Reviews AI + response workflows |
| Q10 | AI Engagement & Conversion | How are AI tools used in your engagement process? | No AI tools in use | AI tools installed but not integrated | AI tools integrated into workflows | AI voice/conversational agents at scale |
| Q11 | Reporting & Improvement | How do you track and improve performance? | Do not consistently track metrics | Check results occasionally | Review dashboards regularly, adjust workflows | Track lifecycle performance, attribute, optimise |
| Q12 | Lifetime Value & Retention | How do you increase revenue from existing clients? | No structured retention strategy | Occasional manual upsell offers | Planned follow-up offers or renewal reminders | Automated retention, renewal, expansion workflows |

### 3.2 Answer Encoding
```
A = 1 (Foundation-level)
B = 2 (Foundation/Growth transition)
C = 3 (Growth-level)
D = 4 (Optimization-level)
```

---

## 4. Pathway Definitions

### 4.1 Foundation Pathway
**Trigger:** 3 or more Foundation signals across all 12 questions.  
**Foundation signals are defined per question:**
- Q1–Q5: Answers A (1) or B (2)
- Q6–Q9, Q11, Q12: Answer A (1) only
- Q10: Not counted (neutral baseline)

**Priority focus:** Offer clarity, website presence, lead capture, CRM setup, follow-up automation.

### 4.2 Growth Pathway
**Trigger:** Foundation signal count < 3, and Optimization conditions not met.  
**Characteristics:** Mostly B–C responses, CRM in use but not fully automated, 0–3 D-level answers.  
**Priority focus:** Delivery standardisation, payment systems, reactivation, reviews.

### 4.3 Optimization Pathway
**Trigger:** All of the following:
- No critical Foundation blockers (Q1 ≠ A, Q4 answers ≥ C, Q5 answers ≥ C)
- At least 4 Optimization-level (D) responses
- Strong CRM maturity: Q4 ≥ C
- Strong reporting: Q11 ≥ C

**Priority focus:** AI engagement, lifecycle automation, attribution, advanced retention.

### 4.4 Critical Foundation Blockers
These signals automatically prevent Optimization classification:
- **Q1 = A** — Offer is undefined (systems cannot stabilise without clarity)
- **Q4 ≤ B** — No structured CRM (customer journey tracking absent)
- **Q5 ≤ B** — No follow-up automation (manual or template-only)

---

## 5. ML Model Specification

### 5.1 Algorithm
**Logistic Regression (Multi-Class: One-vs-Rest)**
- Library: `scikit-learn.linear_model.LogisticRegression`
- Multi-class strategy: `multi_class='ovr'`
- Solver: `lbfgs`
- Max iterations: 1000
- Regularisation: L2 (default), C=1.0

### 5.2 Features

| Feature | Type | Description |
|---------|------|-------------|
| `q1` – `q12` | int (1–4) | Encoded answer for each question |
| `foundation_count` | int (0–11) | Count of answers in Foundation signal range |
| `growth_count` | int (0–12) | Count of answers at Growth level (value = 3) |
| `optimization_count` | int (0–12) | Count of answers at Optimisation level (value = 4) |
| `critical_blocker_count` | int (0–3) | Count of Q1=A, Q4≤B, Q5≤B |
| `total_score` | int (12–48) | Sum of all encoded answers |

**Total features: 17**

### 5.3 Training Data
- Synthetic data generated using rule-based classification logic.
- ~450 samples per class (1,350 total) covering diverse answer combinations.
- Class-balanced generation ensures no class imbalance.
- Train/test split: 80/20; evaluation metric: overall accuracy.

### 5.4 Model Serialisation
Model and label encoder saved to `models/pathway_classifier.pkl` using `joblib`.

---

## 6. Input / Output Schema

### 6.1 Input Schema
```json
{
  "responses": {
    "q1": "C",
    "q2": "B",
    "q3": "C",
    "q4": "C",
    "q5": "B",
    "q6": "C",
    "q7": "C",
    "q8": "B",
    "q9": "C",
    "q10": "A",
    "q11": "C",
    "q12": "B"
  }
}
```
- Each key `q1`–`q12` is required.
- Each value must be one of `"A"`, `"B"`, `"C"`, `"D"` (case-insensitive).

### 6.2 Output Schema
```json
{
  "input_responses": {
    "q1": "C", "q2": "B", ...
  },
  "input_text": "I have one clear primary offer and CTA. | Basic website with limited conversion structure. | ...",
  "pathway": "Growth",
  "reasoning": "Predicted Growth: 1 foundation signal, 0 optimization signals. No critical Foundation blockers present.",
  "confidence_score": 0.7823,
  "class_probabilities": {
    "Foundation": 0.1245,
    "Growth": 0.7823,
    "Optimization": 0.0932
  },
  "summary": "...",
  "priority_actions": [
    "Automate your follow-up sequences beyond template use.",
    "Standardise your client onboarding workflow."
  ],
  "anti_priority_warnings": [
    "Don't invest heavily in AI tools until CRM is consistently used.",
    "Don't launch paid ads without a stable lead capture system."
  ],
  "graduation_outlook": "Once you have standardised delivery, automated follow-up, and structured payments, you will be ready to move toward Optimization-level systems."
}
```

---

## 7. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Prediction latency | < 100ms per inference |
| Model accuracy | ≥ 95% on test set |
| Python version | 3.9+ |
| Dependencies | scikit-learn, numpy, pydantic, joblib |
| Code style | PEP 8 compliant |
| Output format | JSON (UTF-8) |
| Model file size | < 5 MB |

---

## 8. Deliverables

| Deliverable | File/Location | Status |
|-------------|---------------|--------|
| PRD Document | `PRD.md` | ✅ Complete |
| Input/Output Schema | `src/schema.py` | ✅ Complete |
| Question & Answer Data | `src/data_utils.py` | ✅ Complete |
| Training Data Generator | `src/generate_training_data.py` | ✅ Complete |
| Model Training Script | `src/train_model.py` | ✅ Complete |
| Classification Engine | `src/classifier.py` | ✅ Complete |
| Saved Model | `models/pathway_classifier.pkl` | Generated at runtime |
| Sample JSON (10+ cases) | `data/user_request_examples.json` | ✅ Complete |
| Test Suite | `tests/test_classifier.py` | ✅ Complete |
| Feature Documentation | `docs/feature_documentation.md` | ✅ Complete |
| README / Installation Guide | `README.md` | ✅ Complete |

---

## 9. Acceptance Criteria

1. Running `python src/train_model.py` generates a saved model at `models/pathway_classifier.pkl` with ≥ 95% accuracy.
2. Running `python tests/test_classifier.py` runs ≥ 10 test cases and prints pass/fail results.
3. Each classification output is valid JSON matching the output schema.
4. Foundation, Growth, and Optimization pathways are all demonstrated in test cases.
5. The `summary` field is ≤ 1,000 words and references each of the 12 question answers.
6. Confidence scores are in range [0.0, 1.0] and class probabilities sum to 1.0.

---

*Document prepared for the Business Systems Readiness Assessment Platform — ML Classification Engine (Project 1).*
