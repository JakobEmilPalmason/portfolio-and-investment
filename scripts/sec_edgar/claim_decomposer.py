"""
Claim decomposer — extract verifiable assertions from analysis report sections.

Two extraction paths:
1. Mechanical: regex-parse the Key Findings table and Red Flags bullets (free, high confidence)
2. LLM: decompose Detailed Analysis prose into atomic claims

Phase 4 of the evidence extraction masterplan.
"""

import json
import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

import sys
sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from src.evidence_models import AssertionBatch, get_verification_schema

PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "decompose-claims.md"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 1
MAX_ASSERTIONS_PER_SECTION = 15

UMBRELLA_FILES = {
    1: "01-circle-of-competence.md",
    2: "02-durable-competitive-advantage.md",
    3: "03-management-capital-allocation.md",
    4: "04-business-economics.md",
    5: "05-balance-sheet-safety.md",
    6: "06-valuation-intrinsic-value.md",
    7: "07-margin-of-safety.md",
    8: "08-temperament-time-horizon.md",
}

UMBRELLA_TITLES = {
    1: "Circle of Competence",
    2: "Durable Competitive Advantage",
    3: "Management & Capital Allocation",
    4: "Business Economics",
    5: "Balance Sheet Safety",
    6: "Valuation & Intrinsic Value",
    7: "Margin of Safety",
    8: "Temperament & Time Horizon",
}

# Derived metric keywords that flag requires_arithmetic=True
DERIVED_METRIC_PATTERNS = re.compile(
    r"\b(ROIC|ROE|ROA|FCF conversion|FCF-to-net|margin|gross margin|"
    r"operating margin|net margin|EBITDA margin|growth rate|CAGR|"
    r"debt[/-](?:to[/-])?(?:equity|EBITDA|capital)|"
    r"interest coverage|current ratio|payout ratio|"
    r"conversion ratio|yield)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Mechanical extraction — Key Findings table
# ---------------------------------------------------------------------------

def _parse_key_findings(section_text: str, umbrella_number: int) -> list[dict]:
    """Extract assertions from the Key Findings markdown table."""
    assertions = []
    # Match rows like: | 1 | Finding text here | 5 |
    for match in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(\d)\s*\|$", section_text, re.MULTILINE):
        row_num = int(match.group(1))
        finding = match.group(2).strip()
        significance = int(match.group(3))

        if not finding or len(finding) < 10:
            continue

        assertions.append({
            "assertion_text": finding,
            "assertion_type": _infer_type(finding),
            "category": "finding",
            "requires_arithmetic": bool(DERIVED_METRIC_PATTERNS.search(finding)),
            "source_location": f"key_findings:{row_num}",
        })

    return assertions


# ---------------------------------------------------------------------------
# Mechanical extraction — Red Flags
# ---------------------------------------------------------------------------

def _parse_red_flags(section_text: str, umbrella_number: int) -> list[dict]:
    """Extract assertions from Red Flags bullet points."""
    assertions = []

    # Find the Red Flags section
    red_flags_match = re.search(r"^## Red Flags\s*\n(.*?)(?=^## |\Z)", section_text, re.MULTILINE | re.DOTALL)
    if not red_flags_match:
        return []

    red_flags_text = red_flags_match.group(1)
    for i, match in enumerate(re.finditer(r"^- (.+)$", red_flags_text, re.MULTILINE), start=1):
        text = match.group(1).strip()
        if len(text) < 10:
            continue

        assertions.append({
            "assertion_text": text,
            "assertion_type": _infer_type(text),
            "category": "red_flag",
            "requires_arithmetic": bool(DERIVED_METRIC_PATTERNS.search(text)),
            "source_location": f"red_flags:{i}",
        })

    return assertions


# ---------------------------------------------------------------------------
# Type inference
# ---------------------------------------------------------------------------

def _infer_type(text: str) -> str:
    """Infer assertion_type from text content."""
    # Contains a specific number → quantitative
    if re.search(r"\$[\d,.]+[BMKbmk]?|\d+(\.\d+)?%|\d{2,}[,.]\d", text):
        return "quantitative"
    # Comparative language
    if re.search(r"\b(vs\.?|compared|versus|higher than|lower than|outpaced|exceeded|below|above)\b", text, re.IGNORECASE):
        return "comparative"
    # Causal language
    if re.search(r"\b(driven by|due to|resulting from|caused by|reflects|attributed to)\b", text, re.IGNORECASE):
        return "causal"
    return "qualitative"


# ---------------------------------------------------------------------------
# LLM prose decomposition
# ---------------------------------------------------------------------------

def _claude_extract(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Call claude --print --output-format json. Returns raw stdout."""
    try:
        result = subprocess.run(
            ["claude", "--print", "--output-format", "json",
             "--allowedTools", "", "--", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude timed out after {timeout}s")
    except FileNotFoundError:
        raise RuntimeError("claude CLI not found")

    if result.returncode != 0:
        raise RuntimeError(f"claude exit code {result.returncode}: {result.stderr[:300]}")
    return result.stdout


def _parse_json_response(raw: str) -> dict:
    """Parse JSON, handling {"result": ...} wrappers."""
    data = json.loads(raw)
    if isinstance(data, dict) and "result" in data:
        inner = data["result"]
        if isinstance(inner, str):
            inner = json.loads(inner)
        if isinstance(inner, dict):
            return inner
    return data


def _extract_detailed_analysis(section_text: str) -> str:
    """Extract just the Detailed Analysis section for LLM decomposition."""
    # From "## Detailed Analysis" to next "## " header
    match = re.search(r"^## Detailed Analysis\s*\n(.*?)(?=^## |\Z)", section_text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _decompose_prose(
    section_text: str, umbrella_number: int, ticker: str,
) -> list[dict]:
    """LLM decomposition of prose paragraphs into atomic assertions."""
    prose = _extract_detailed_analysis(section_text)
    if not prose or len(prose) < 50:
        return []

    if not PROMPT_PATH.exists():
        logger.warning("Decompose prompt not found at %s", PROMPT_PATH)
        return []

    template = PROMPT_PATH.read_text(encoding="utf-8")
    schema_json = json.dumps(get_verification_schema("decompose"), indent=2)
    title = UMBRELLA_TITLES.get(umbrella_number, f"Umbrella {umbrella_number}")

    prompt = (
        template
        .replace("{UMBRELLA_NUMBER}", str(umbrella_number))
        .replace("{SECTION_TITLE}", title)
        .replace("{TICKER}", ticker)
        .replace("{JSON_SCHEMA}", schema_json)
    )
    prompt = prompt + "\n\n" + prose

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = _parse_json_response(raw)
            batch = AssertionBatch.model_validate(data)
            return [
                {
                    "assertion_text": a.assertion_text,
                    "assertion_type": a.assertion_type,
                    "category": a.category,
                    "requires_arithmetic": a.requires_arithmetic,
                    "source_location": a.source_location,
                }
                for a in batch.assertions[:MAX_ASSERTIONS_PER_SECTION]
            ]
        except (RuntimeError, json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Prose decompose attempt %d: %s", attempt + 1, exc)
            if attempt < MAX_RETRIES:
                continue
            return []

    return []


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _deduplicate(mechanical: list[dict], llm: list[dict]) -> list[dict]:
    """Deduplicate assertions from mechanical and LLM paths.

    Rule: prefer assertion with numeric value; if tied, prefer longer text.
    Mechanical and LLM assertions from different source_locations always kept.
    """
    if not llm:
        return mechanical
    if not mechanical:
        return llm

    # Build set of normalized mechanical texts for fuzzy matching
    mech_texts = {a["assertion_text"].lower().strip() for a in mechanical}

    combined = list(mechanical)
    for llm_a in llm:
        llm_text_lower = llm_a["assertion_text"].lower().strip()
        # Skip if very similar to an existing mechanical assertion
        is_dup = False
        for mt in mech_texts:
            # Simple overlap check: if >70% of words overlap, consider duplicate
            llm_words = set(llm_text_lower.split())
            mech_words = set(mt.split())
            if llm_words and mech_words:
                overlap = len(llm_words & mech_words) / min(len(llm_words), len(mech_words))
                if overlap > 0.7:
                    is_dup = True
                    break
        if not is_dup:
            combined.append(llm_a)

    return combined


# ---------------------------------------------------------------------------
# Section decomposition
# ---------------------------------------------------------------------------

def decompose_section(
    section_text: str, umbrella_number: int, ticker: str,
) -> list[dict]:
    """Decompose a single report section into verifiable assertions.

    Returns list of assertion dicts (not yet DB-ready — missing ticker/report_path).
    """
    mechanical = _parse_key_findings(section_text, umbrella_number)
    mechanical.extend(_parse_red_flags(section_text, umbrella_number))
    llm_assertions = _decompose_prose(section_text, umbrella_number, ticker)
    return _deduplicate(mechanical, llm_assertions)


# ---------------------------------------------------------------------------
# Report-level decomposition
# ---------------------------------------------------------------------------

def _assertion_to_db_dict(
    assertion: dict, umbrella_number: int, ticker: str, report_path: str,
) -> dict:
    """Convert assertion to dict for EvidenceDB.batch_insert_assertions()."""
    return {
        "ticker": ticker,
        "report_path": report_path,
        "umbrella_number": umbrella_number,
        "assertion_text": assertion["assertion_text"],
        "assertion_type": assertion["assertion_type"],
        "category": assertion.get("category", "finding"),
        "requires_arithmetic": 1 if assertion.get("requires_arithmetic") else 0,
    }


def decompose_report(report_dir: Path, ticker: str) -> list[dict]:
    """Decompose all 8 umbrella sections into DB-ready assertion dicts.

    Skips missing section files with a warning.
    Returns list of dicts ready for batch_insert_assertions().
    """
    report_path = str(report_dir / "FINAL-REPORT.md")
    all_assertions = []

    for umbrella_num, filename in UMBRELLA_FILES.items():
        section_file = report_dir / filename
        if not section_file.exists():
            logger.warning("Section file missing, skipping: %s", section_file)
            continue

        section_text = section_file.read_text(encoding="utf-8")
        assertions = decompose_section(section_text, umbrella_num, ticker)

        for a in assertions:
            all_assertions.append(
                _assertion_to_db_dict(a, umbrella_num, ticker, report_path)
            )

    logger.info("Decomposed %d assertions from %s", len(all_assertions), report_dir)
    return all_assertions
