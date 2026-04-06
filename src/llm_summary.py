import json
import os
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Optional

from src.data_utils import ANSWER_EXPLANATIONS, ANSWER_LABELS, QUESTIONS, SECTION_NAMES


ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_TIMEOUT_SECONDS = 25
DEFAULT_MAX_TOKENS = 1000

DEFAULT_SYSTEM_PROMPT = (
    "You are an expert business strategist and narrative writer. "
    "Write a three-part report in plain, human language based only on the source material. "
    "Avoid jargon and avoid copying source sentences verbatim."
)


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def llm_summary_enabled() -> bool:
    source = os.getenv("SUMMARY_SOURCE", "deterministic").strip().lower()
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    return source == "llm" and bool(api_key)


@lru_cache(maxsize=1)
def _load_system_prompt() -> str:
    configured = os.getenv("NARRATIVE_PROMPT_DOCX_PATH", "").strip()
    if configured:
        prompt_path = Path(configured)
    else:
        prompt_path = Path(__file__).resolve().parent.parent / "data" / "narrative_assembly_prompt_draft3.docx"

    if not prompt_path.exists():
        return DEFAULT_SYSTEM_PROMPT

    try:
        with zipfile.ZipFile(prompt_path) as zf:
            xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(xml_bytes)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for para in root.findall(".//w:p", ns):
            parts = [node.text for node in para.findall(".//w:t", ns) if node.text]
            if parts:
                paragraphs.append("".join(parts))
        prompt_text = "\n".join(paragraphs).strip()
        return prompt_text or DEFAULT_SYSTEM_PROMPT
    except Exception:
        return DEFAULT_SYSTEM_PROMPT


def _extract_json_object(text: str) -> Optional[dict]:
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    snippet = cleaned[start : end + 1]
    try:
        data = json.loads(snippet)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _build_user_prompt(
    first_name: str,
    pathway: str,
    reasoning: str,
    encoded: dict,
    pathway_focus_areas: list[str],
) -> str:
    lines = [
        "Create a personalized three-part business summary.",
        "Return JSON only with this exact schema:",
        "{",
        '  "intro": "string",',
        '  "narrative_paragraph_1": "string",',
        '  "narrative_paragraph_2": "string",',
        '  "recommended_focus_areas": ["string", "string", "string"],',
        '  "graduation_outlook": "string"',
        "}",
        "",
        "Hard constraints:",
        "1) intro must be 2-3 sentences and begin with 'Hi <first_name>,' on its own line.",
        "2) paragraph_1 must be 2-3 sentences describing current friction/strength grounded in source answers.",
        "3) paragraph_2 must be 2-3 sentences shifting toward what becomes possible as systems improve.",
        "4) recommended_focus_areas must contain exactly 3 single-line bullets (each under 12 words).",
        "5) graduation_outlook must be 1-2 sentences, pathway-specific and personalized.",
        "6) Write in plain English, warm but direct, no model diagnostics or threshold jargon.",
        "7) Be concise. Total output must not exceed 600 tokens.",
        "",
        f"first_name: {first_name}",
        f"pathway: {pathway}",
        f"reasoning_signals: {reasoning}",
        "",
        "Suggested pathway focus areas:",
    ]

    for idx, area in enumerate(pathway_focus_areas, start=1):
        lines.append(f"{idx}. {area}")

    lines.append("")
    lines.append("Answer-grounded source material (use this only):")
    for q in QUESTIONS:
        v = encoded[q]
        lines.append(
            f"- {q} | {SECTION_NAMES[q]} | {ANSWER_LABELS[q][v]} | {ANSWER_EXPLANATIONS[q][v]}"
        )

    return "\n".join(lines)


def _call_anthropic(system_prompt: str, user_prompt: str) -> Optional[str]:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))
    timeout_seconds = int(os.getenv("ANTHROPIC_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }

    req = urllib.request.Request(
        ANTHROPIC_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        content = data.get("content", [])
        text_chunks = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
        return "\n".join(chunk for chunk in text_chunks if chunk).strip() or None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def build_llm_summary(
    first_name: str,
    pathway: str,
    reasoning: str,
    encoded: dict,
    deterministic_summary: dict,
) -> Optional[dict]:
    if not llm_summary_enabled():
        return None

    system_prompt = _load_system_prompt()
    user_prompt = _build_user_prompt(
        first_name=first_name,
        pathway=pathway,
        reasoning=reasoning,
        encoded=encoded,
        pathway_focus_areas=deterministic_summary.get("recommended_focus_areas", []),
    )

    llm_text = _call_anthropic(system_prompt=system_prompt, user_prompt=user_prompt)
    parsed = _extract_json_object(llm_text or "")
    if not parsed:
        return None

    intro = str(parsed.get("intro", "")).strip()
    p1 = str(parsed.get("narrative_paragraph_1", "")).strip()
    p2 = str(parsed.get("narrative_paragraph_2", "")).strip()
    outlook = str(parsed.get("graduation_outlook", "")).strip()
    focus = parsed.get("recommended_focus_areas", [])

    if not all([intro, p1, p2, outlook]) or not isinstance(focus, list):
        return None

    cleaned_focus = [str(item).strip() for item in focus if str(item).strip()]
    if len(cleaned_focus) < 3:
        cleaned_focus = deterministic_summary.get("recommended_focus_areas", [])[:5]
    cleaned_focus = cleaned_focus[:5]

    focus_lines = "\n".join(f"- {item}" for item in cleaned_focus)
    full_report_text = (
        f"{intro}\n\n"
        f"{p1}\n\n"
        f"{p2}\n\n"
        f"Your recommended focus areas:\n{focus_lines}\n\n"
        f"{outlook}"
    )

    return {
        "source": "llm_generated",
        "intro": intro,
        "narrative_paragraph_1": p1,
        "narrative_paragraph_2": p2,
        "recommended_focus_areas": cleaned_focus,
        "strongest_area": deterministic_summary["strongest_area"],
        "weakest_area": deterministic_summary["weakest_area"],
        "immediate_focus": deterministic_summary["immediate_focus"],
        "graduation_outlook": outlook,
        "full_report_text": full_report_text,
    }
