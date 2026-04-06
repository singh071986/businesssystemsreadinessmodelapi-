# Summary Object — Product Requirements Document

**Document scope:** Defines the intended behaviour of every field in `SummaryObject`, maps each field to the requirements in the narrative assembly prompt, and identifies where the current deterministic fallback implementation is compliant, partially compliant, or non-compliant.

**Two modes of operation**
- **Deterministic fallback** (current): `source = "deterministic_fallback"`. All fields are assembled in `_build_summary_object()` in `src/classifier.py` using static lookup tables from `src/data_utils.py`.
- **LLM-generated** (implemented, opt-in): `source = "llm_generated"` when `SUMMARY_SOURCE=llm` and `ANTHROPIC_API_KEY` is configured. The same fields are populated by Claude using the narrative assembly prompt in `data/narrative_assembly_prompt_draft3.docx`. No API or UI changes are required when switching.

---

## Summary Object Field Reference

### `source`

**What it stores:** A string flag indicating how this summary was produced.

| Value | Meaning |
|---|---|
| `"deterministic_fallback"` | Built from static lookup tables. Correct structure, functional narrative. |
| `"llm_generated"` | Built by Claude using the narrative prompt and strict JSON output mapping. |

**Prompt requirement:** Not explicitly named in the prompt, but essential for the UI to know whether it is displaying a machine-assembled or LLM-written report, and for QA tracing.

---

### `intro`

**Prompt requirement — Part 1 (Personalized Intro):**
> Write a warm, direct opening paragraph. Begin with a salutation that addresses the user by first name followed by a comma on its own line (e.g. 'Hi Sarah,' or 'Sarah,') before the opening sentence. Acknowledge the stage their business is in without judgment. Name their assigned pathway naturally — not as a label, but as a description of where they are right now. Reference 1-2 of the ML reasoning signals to make it feel specific to them. The tone should feel like a knowledgeable friend who has just reviewed their answers and genuinely sees their business clearly.
> **Target length:** 1 short paragraph, 3–5 sentences.

**What the code does:**
- Generates `"Hi {first_name},\n"` — salutation on its own line. ✅
- Writes a pathway-context sentence in natural language (e.g. "your foundation is largely in place, which means the work ahead is about making your systems more consistent and connected"). ✅
- Appends 1-2 ML reasoning signals and closes with "Here's what your results show."

**Current output example (Growth, Sarah):**
```
Hi Sarah,
Based on your answers, your foundation is largely in place, which means the work
ahead is about making your systems more consistent and connected.
2 Foundation signal(s) detected (threshold for Foundation is 3). 0 Optimization-level
response(s) detected (threshold for Optimization is 4 with no blockers).
Here's what your results show.
```

**Compliance assessment:**

| Requirement | Status | Notes |
|---|---|---|
| Salutation on its own line | ✅ Met | `"Hi Sarah,\n"` |
| Pathway described naturally, not as a label | ✅ Met | Three pathway-specific context strings written in plain language |
| Reference 1-2 ML reasoning signals | ⚠️ Partial | Signals are included but as raw ML diagnostic text ("2 Foundation signal(s) detected (threshold for Foundation is 3)") — not converted to human-readable narrative. A reader receiving this as a finished report would see machine output, not a friend's observation. |
| 3–5 sentences | ⚠️ Partial | Technically 3 sentences but the middle sentence(s) are ML jargon, not narrative sentences. |
| Tone: warm, knowledgeable friend | ❌ Not met | The ML signal text breaks this. "2 Foundation signal(s) detected (threshold for Foundation is 3)" reads as a debug log, not empathetic professional language. |

**Gap to fix when LLM is wired in:** The LLM prompt handles this correctly — it receives the reasoning bullets and is instructed to weave 1-2 into natural language. The deterministic fallback should either (a) suppress the raw signal text entirely, or (b) convert it to a humanised sentence (e.g. "Several of your answers point to core systems that are still in progress — particularly around follow-up and offer clarity.").

---

### `narrative_paragraph_1`

**Prompt requirement — Part 2, Paragraph 1:**
> The first paragraph should describe where friction currently exists or where the business is strong — grounded in their actual answers. Prioritize the sections most relevant to their pathway.

**Pathway section priority rules:**
- Foundation → Q1, Q2, Q3, Q4, Q5, Q6
- Growth → Q3, Q4, Q5, Q6, Q7, Q8
- Optimization → Q8, Q9, Q10, Q11, Q12 + any section where they answered D

**What the code does:**
1. Identifies the pathway's priority sections from `PATHWAY_PRIORITY_SECTIONS`.
2. For Optimization, also appends any question answered D that is not already in the priority list (up to 3 extra).
3. Splits those sections into gaps (answer ≤ 2) and strengths (answer ≥ 3).
4. If gaps exist: names the gap sections and pulls `_first_sentence()` from `ANSWER_EXPLANATIONS` for the top 2 gap sections.
5. If no gaps: uses a fallback sentence acknowledging all priority systems are performing.

**Current output example (Growth, Sarah):**
```
The clearest friction right now sits in Nurture & Follow-Up System, Reactivation &
Outreach System. Having templates is a smart move — it saves time and keeps your
communication consistent. You're already doing something most business owners don't
— you occasionally reach back out to people who've gone quiet or haven't heard from
you in a while.
```

**Compliance assessment:**

| Requirement | Status | Notes |
|---|---|---|
| Grounded in actual answers | ✅ Met | Section names and blurb sentences are answer-specific |
| Pathway-relevant sections prioritized | ✅ Met | Uses `PATHWAY_PRIORITY_SECTIONS` lookup |
| Do not copy blurbs verbatim | ⚠️ Partial | `_first_sentence()` extracts the first sentence of the blurb, which is close to verbatim. The prompt says to "weave the key insights together so they read as one flowing narrative, not a list of separate observations." The current assembly — name the gaps, attach two isolated blurb sentences — reads as a list, not a weave. |
| One flowing paragraph | ⚠️ Partial | Three sentences structured as: title sentence + blurb 1 + blurb 2. The gap between blurb 1 and blurb 2 is abrupt (both begin "Having..." / "You're already..."). |

**Gap to fix when LLM is wired in:** The LLM is explicitly given all 12 blurbs as source material and instructed to weave rather than copy. The deterministic fallback could improve by adding a connective sentence rather than dropping two isolated blurb sentences next to each other.

---

### `narrative_paragraph_2`

**Prompt requirement — Part 2, Paragraph 2:**
> The second paragraph should begin to shift toward what becomes possible when the right systems are in place.

**What the code does:**
1. Identifies strength sections (answer ≥ 3) within the pathway's priority questions.
2. If strengths exist: names them, pulls `_first_sentence()` from the strength blurb, and closes with a forward-looking sentence.
3. If no strengths: uses a generic forward-looking fallback.

**Current output example (Growth, Sarah):**
```
Where your systems are already solid — particularly in Lead Capture System and
Customer Journey / CRM System — that foundation is working for you. Your lead
capture system is doing more than just collecting information — it's responding.
As the remaining gaps close, the business becomes easier to run and more reliable
to grow.
```

**Current output example (Foundation, all-A, Sarah):**
```
Once the systems in your priority areas are installed and running consistently,
the business becomes more predictable, easier to manage, and ready to grow without
depending entirely on your personal effort.
```

**Compliance assessment:**

| Requirement | Status | Notes |
|---|---|---|
| Shifts toward what becomes possible | ⚠️ Partial | The shift exists ("As the remaining gaps close...") but it is a single closing sentence rather than a full paragraph that develops this direction. |
| Connected to Paragraph 1 | ⚠️ Partial | The two paragraphs are thematically related but not explicitly connected by transitional language. |
| Grounded in actual answers | ✅ Met | Uses pathway-filtered strength sections; blurb sentence is answer-specific. |
| Foundation all-gap edge case | ⚠️ Partial | When there are no strengths (all-A Foundation), the fallback paragraph is generic and not grounded in specific answers. |

---

### `recommended_focus_areas`

**Prompt requirement — Part 2, Bulleted List:**
> After the two paragraphs, include a bulleted list of 3–5 recommended business systems to focus on, drawn from the pathway's priority build list. Label this list clearly as: 'Your recommended focus areas:'. Each bullet should be a single line — the system name followed by a plain-language description of what it means for their business. Keep each bullet under 20 words.

**What the code does:**
- Returns the first 5 entries from `SECTION_FOCUS_DESCRIPTIONS` for the pathway's priority sections.
- Each entry is pre-written as: `"System Name: one-line plain-language description."`

**Current output example (Growth, Sarah):**
```
- Lead Capture System: an automated process so every inquiry receives an immediate response.
- Customer Journey / CRM System: a single place to track every lead and client consistently.
- Nurture & Follow-Up System: automated sequences so every lead stays warm without manual effort.
- Delivery System: a repeatable onboarding workflow so every client starts the same way.
- Payments & Offers System: checkout connected to workflows so payment triggers the next step.
```

**Compliance assessment:**

| Requirement | Status | Notes |
|---|---|---|
| 3–5 items | ✅ Met | Always 5 (top 5 of the 6 pathway-priority sections) |
| Labeled "Your recommended focus areas:" | ✅ Met | Label is in `full_report_text` assembly |
| System name + plain-language description | ✅ Met | Format matches exactly |
| Each bullet under 20 words | ✅ Met | All entries verified under 20 words |
| Drawn from pathway's priority build list | ✅ Met | Filtered to pathway using `PATHWAY_PRIORITY_SECTIONS` |

**This is the most fully compliant section of the deterministic fallback.**

---

### `graduation_outlook`

**Prompt requirement — Part 3 (Graduation Outlook Statement):**
> Write a forward-looking closing statement that tells the user what becomes possible when they complete this stage. Be specific to their pathway. Keep it encouraging, grounded, and free of hype. 1 short paragraph, 2–4 sentences. Do not copy these benchmarks verbatim. Use them as a guide for tone and content, then write the closing in your own words, personalized to what this specific user's answers revealed.

**What the code does:**
- Returns `PATHWAY_GRADUATION_OUTLOOK[pathway]` directly — a static string per pathway.

**Current output examples:**

*Foundation:*
```
Once you have one clear offer, a structured website, a basic CRM, and automated
follow-up in place, you'll be ready to move into the Growth pathway — where your
focus shifts from building the basics to running them reliably and adding delivery
and payment systems that scale with your client volume.
```

*Growth:*
```
Once you have standardised delivery, integrated payments, a structured reactivation
strategy, and consistent metrics review in place, you'll be ready to move into the
Optimization pathway — where your focus shifts to AI-assisted engagement, lifecycle
automation, and continuous performance improvement.
```

**Compliance assessment:**

| Requirement | Status | Notes |
|---|---|---|
| Forward-looking | ✅ Met | All three pathway strings are forward-looking |
| Pathway-specific | ✅ Met | One string per pathway, each references that pathway's graduation conditions |
| 2–4 sentences | ✅ Met | One compound sentence — borderline; is complete but tight |
| Encouraging, grounded, free of hype | ✅ Met | Tone is measured and specific |
| Do not copy benchmark verbatim | ❌ Not met | The static strings are nearly identical to the benchmark text in the prompt document. The prompt requires these to be rewritten to reflect what this specific user's answers revealed, not a generic pathway description. |
| Personalized to specific answers | ❌ Not met | All Growth users receive the identical text regardless of which systems are their actual weakest points. |

**Gap to fix when LLM is wired in:** The LLM is instructed to use the graduation benchmark as a guide and write in its own words. The deterministic fallback cannot personalise this without more conditional logic. For now, the static text is accurate and meets the intent — but it is not personalised.

---

### `full_report_text`

**What it stores:** All three narrative parts assembled in order, exactly as the prompt specifies, with blank lines between sections.

**Structure:**
```
{intro}                          ← Part 1
\n\n
{narrative_paragraph_1}          ← Part 2, paragraph 1
\n\n
{narrative_paragraph_2}          ← Part 2, paragraph 2
\n\n
Your recommended focus areas:    ← Part 2, bulleted list label
- {focus_area_1}
- {focus_area_2}
...
\n\n
{graduation_outlook}             ← Part 3
```

**Purpose:** This is the render-ready field. The UI can display `full_report_text` as-is without assembling the parts itself. When the LLM replaces the fallback, it populates the same field.

**Compliance with prompt's three-part output requirement:**

| Part | Required | Present | Status |
|---|---|---|---|
| Part 1 — Personalized Intro | "Hi [name]," + opening | `intro` | ✅ |
| Part 2 — Cohesive Narrative + Bullets | 2 paragraphs + labeled list | `narrative_paragraph_1`, `narrative_paragraph_2`, `recommended_focus_areas` | ✅ |
| Part 3 — Graduation Outlook | Forward-looking closing | `graduation_outlook` | ✅ |
| "Exactly three parts, in this order" | Required | Assembled in this order | ✅ |

---

### `strongest_area` and `weakest_area`

**What they store:** The section name with the highest and lowest encoded answer value across all 12 questions.

**Prompt requirement:** Not directly named in the prompt. These are support fields used by the UI and optionally by the LLM as input context when personalizing the report.

**Note on current logic:** `strongest_area` and `weakest_area` are computed across all 12 questions, not just the pathway-relevant sections. This means for a Growth user, `strongest_area` could be Q12 (Retention), which is not a Growth priority. The LLM prompt also does not use these directly — they are metadata for the UI dashboard, not part of the narrative.

---

### `immediate_focus`

**What it stores:** The section name of the first item in the pathway's priority list — the single most important area to address right now.

**Purpose:** Intended for prominent display in the UI (e.g. a "Start here" callout). Not part of the narrative text.

---

## Word Count Constraint

**Prompt requirement:** Parts 1 and 2 combined must be no more than 500 words.

**Current checks:** Not enforced in code. Based on sample output, the Growth sample runs approximately 220–270 words for Parts 1 and 2, well within budget. The Foundation all-A sample is shorter (~180 words) due to the P2 fallback. No enforcement is needed unless LLM output is uncontrolled.

---

## Tone and Voice Compliance Summary

| Tone Principle | Deterministic Fallback | LLM (planned) |
|---|---|---|
| Warm but never gushing | ✅ Neutral, not effusive | Should be — instructions explicit |
| Direct and plain, no jargon | ❌ ML signal text in intro breaks this | ✅ LLM is told to avoid jargon |
| Honest without being harsh | ✅ Gaps named clearly and matter-of-factly | Should be — instructions explicit |
| Tone shifts with pathway | ✅ Three distinct `pathway_context` strings | ✅ Prompt provides calibration examples |
| Sentences clear and varied | ⚠️ Assembled formulaically; some repetition | Should improve with LLM |
| No consecutive sentences starting the same way | ⚠️ "Having..." / "You're already..." in same paragraph | Should improve with LLM |
| No passive voice | ✅ Mostly active | Should be enforced by prompt |

---

## Summary: What Is Working vs. What Is a Gap

**Working well in deterministic fallback:**
- Three-part structure matches prompt order exactly.
- `first_name` is threaded through correctly; salutation is on its own line.
- Pathway section prioritization (Foundation Q1-6, Growth Q3-8, Optimization Q8-12+D) is correctly implemented.
- Focus area bullets match the required format: system name + plain-language description, under 20 words.
- All blurbs are answer-specific — the text varies with what the user actually selected.
- `full_report_text` is render-ready for the UI without client-side assembly.

**Gaps in deterministic fallback (resolved when LLM is wired in):**
1. **ML signal text in intro** — Raw diagnostic strings ("2 Foundation signal(s) detected...") appear verbatim inside the intro. This is the most visible quality problem. The intro should reference what those signals mean in plain English, not what the ML model computed.
2. **Paragraphs assembled, not woven** — Both narrative paragraphs are built by dropping isolated blurb sentences next to each other. The prompt requires weaving insights into a continuous narrative.
3. **Paragraph 2 is strength acknowledgment, not a forward shift** — The prompt's intent for P2 is to begin moving the reader toward possibility. The current P2 names strengths but does not develop the "what becomes possible" direction substantively.
4. **Graduation outlook not personalized** — Static text per pathway. The prompt explicitly says not to copy the benchmark verbatim and to personalise it to what the specific user's answers revealed.
5. **3–5 sentence target for intro** — Currently 3 sentences, but two of them are ML output. Effectively 1 human-written sentence plus noise.

---

## Implemented LLM Integration Path

The classifier now supports Claude generation in a safe opt-in mode:
1. Build deterministic summary first as a guaranteed fallback.
2. If `SUMMARY_SOURCE=llm` and `ANTHROPIC_API_KEY` is present, assemble all 12 answer blurbs as source material.
3. Load system prompt from `data/narrative_assembly_prompt_draft3.docx` (or `NARRATIVE_PROMPT_DOCX_PATH` when provided).
4. Call Anthropic Messages API and request strict JSON for intro, two narrative paragraphs, focus areas, and graduation outlook.
5. Validate and map the LLM output to the existing `SummaryObject`, then set `source = "llm_generated"`.
6. If LLM output is invalid or request fails, automatically return deterministic summary with no API contract change.

No changes to the API contract, schema, or UI are required.
