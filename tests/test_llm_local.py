"""
tests/test_llm_local.py
-----------------------
Standalone test that calls build_llm_summary() directly.
Bypasses the ML classifier entirely — no model files needed.
Auto-loads .env.local so no manual `export` needed.

Usage:
    .venv311/bin/python tests/test_llm_local.py
"""

import json
import os
import sys

# ── Load .env.local automatically ─────────────────────────────────────────────
def _load_dotenv_local(path: str = ".env.local") -> None:
    """Minimal dotenv loader — no third-party libraries required."""
    if not os.path.exists(path):
        print(f"[WARN] {path} not found — using existing shell environment")
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    print(f"[INFO] Loaded env vars from {path}")


_load_dotenv_local()

# ── Import after env vars are set ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.llm_summary import build_llm_summary, llm_summary_enabled

# ── Sample Growth pathway input ───────────────────────────────────────────────
SAMPLE_FIRST_NAME = "Sarah"
SAMPLE_PATHWAY = "Growth"
SAMPLE_REASONING = (
    "High scores in adaptability, learning orientation, and appetite for "
    "challenge. Responses indicate someone energised by new environments "
    "and keen to stretch beyond current capability."
)
SAMPLE_ENCODED = {
    "q1": "C", "q2": "B", "q3": "C", "q4": "C",
    "q5": "B", "q6": "C", "q7": "C", "q8": "B",
    "q9": "C", "q10": "A", "q11": "C", "q12": "B",
}
SAMPLE_DETERMINISTIC = {
    "headline": "You're wired for Growth",
    "source": "deterministic_fallback",
    "tagline": "You thrive when things are changing.",
    "description": "You are energised by novelty and challenge.",
    "action": "Seek out roles that push your boundaries.",
    "coaching_note": "Watch for over-commitment when excited.",
}

# ── Run test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print("=== LLM Summary Local Test ===")
    print(f"  llm_summary_enabled() → {llm_summary_enabled()}")
    print()

    if not llm_summary_enabled():
        print("[WARN] LLM is disabled.")
        print("       Check that .env.local contains both:")
        print("         SUMMARY_SOURCE=llm")
        print("         ANTHROPIC_API_KEY=<your real key>")
        sys.exit(0)

    print("[INFO] Calling build_llm_summary() ...")
    result = build_llm_summary(
        first_name=SAMPLE_FIRST_NAME,
        pathway=SAMPLE_PATHWAY,
        reasoning=SAMPLE_REASONING,
        encoded=SAMPLE_ENCODED,
        deterministic_summary=SAMPLE_DETERMINISTIC,
    )

    if result is None:
        print("[FAIL] build_llm_summary() returned None")
        print("       Check the ANTHROPIC_API_KEY, or run with SUMMARY_SOURCE=deterministic to test fallback.")
        sys.exit(1)

    print()
    print("[PASS] LLM summary returned successfully")
    print()
    print(json.dumps(result, indent=2))
    print()

    source = result.get("source", "")
    if source == "llm_generated":
        print("[PASS] source == 'llm_generated' ✓")
    else:
        print(f"[WARN] source == '{source}' — expected 'llm_generated'")
