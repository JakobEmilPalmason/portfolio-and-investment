"""
Semantic diffing — cross-period comparison of extracted evidence.

Two modes:
1. Numeric: deterministic delta/% change on matched fact_keys (no LLM).
2. Narrative: LLM compares matched section texts for material changes.

Phase 6 of the evidence extraction masterplan.
"""

import json
import logging
from pathlib import Path

from .llm_extract import _claude_extract, _parse_json_response, ExtractionError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

import sys
sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError
from src.evidence_models import NarrativeDiffResult, get_narrative_diff_schema

logger = logging.getLogger(__name__)

DIFF_PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "semantic-diff.md"
MAX_RETRIES = 1
DEFAULT_TIMEOUT = 180  # narrative diff can be longer than single-pass extraction


# ---------------------------------------------------------------------------
# Numeric diffing (deterministic)
# ---------------------------------------------------------------------------

def _section_prefix(fact_key: str) -> str:
    """Extract section prefix from a dot-notation fact_key.

    market_risk.fx.eur -> market_risk
    mda.revenue_growth -> mda
    """
    if fact_key.startswith("market_risk"):
        return "market_risk"
    return fact_key.split(".")[0] if "." in fact_key else fact_key


def _significance_from_pct(pct_change: float) -> int:
    """Map absolute percentage change to 1-5 significance scale.

    0-25%: 1, 25-50%: 2, 50-75%: 3, 75-100%: 4, 100%+: 5
    """
    return min(5, 1 + int(abs(pct_change) / 0.25))


def diff_numeric_facts(
    facts_a: list[dict],
    facts_b: list[dict],
    period_a: str,
    period_b: str,
    ticker: str,
) -> list[dict]:
    """Compute deterministic numeric diffs between two sets of extracted facts.

    Args:
        facts_a: Active facts from period A (from EvidenceDB.get_facts_for_ticker).
        facts_b: Active facts from period B.
        period_a: Fiscal period label (e.g., "FY2024").
        period_b: Fiscal period label (e.g., "FY2025").
        ticker: Stock ticker.

    Returns:
        List of dicts ready for EvidenceDB.insert_semantic_diff().
    """
    # Build lookup: fact_key -> fact (numeric only)
    map_a = {
        f["fact_key"]: f
        for f in facts_a
        if f.get("fact_value_numeric") is not None
    }
    map_b = {
        f["fact_key"]: f
        for f in facts_b
        if f.get("fact_value_numeric") is not None
    }

    all_keys = set(map_a.keys()) | set(map_b.keys())
    diffs: list[dict] = []

    for key in sorted(all_keys):
        in_a = key in map_a
        in_b = key in map_b

        if in_a and in_b:
            val_a = map_a[key]["fact_value_numeric"]
            val_b = map_b[key]["fact_value_numeric"]
            unit = map_a[key].get("fact_unit", "")

            if val_a == val_b:
                continue  # no change

            delta = val_b - val_a
            pct_change = delta / val_a if val_a != 0 else (float("inf") if delta > 0 else float("-inf"))

            # Skip infinite pct_change for significance calc
            if abs(pct_change) == float("inf"):
                significance = 5
            else:
                significance = _significance_from_pct(pct_change)

            # Format human-readable values
            human_a = map_a[key].get("fact_value", str(val_a))
            human_b = map_b[key].get("fact_value", str(val_b))

            diffs.append({
                "ticker": ticker,
                "section_key": _section_prefix(key),
                "period_a": period_a,
                "period_b": period_b,
                "diff_type": "numeric_shift",
                "summary": f"{key}: {human_a} -> {human_b} ({pct_change:+.1%})",
                "detail_json": json.dumps({
                    "fact_key": key,
                    "value_a": val_a,
                    "value_b": val_b,
                    "unit": unit,
                    "delta_absolute": round(delta, 4),
                    "delta_percent": round(pct_change, 4),
                }),
                "significance": significance,
            })

        elif in_b and not in_a:
            val_b = map_b[key]["fact_value_numeric"]
            human_b = map_b[key].get("fact_value", str(val_b))
            diffs.append({
                "ticker": ticker,
                "section_key": _section_prefix(key),
                "period_a": period_a,
                "period_b": period_b,
                "diff_type": "added",
                "summary": f"{key}: new in {period_b} ({human_b})",
                "detail_json": json.dumps({
                    "fact_key": key,
                    "value_b": val_b,
                    "unit": map_b[key].get("fact_unit", ""),
                }),
                "significance": 2,
            })

        else:  # in_a and not in_b
            val_a = map_a[key]["fact_value_numeric"]
            human_a = map_a[key].get("fact_value", str(val_a))
            diffs.append({
                "ticker": ticker,
                "section_key": _section_prefix(key),
                "period_a": period_a,
                "period_b": period_b,
                "diff_type": "removed",
                "summary": f"{key}: removed in {period_b} (was {human_a})",
                "detail_json": json.dumps({
                    "fact_key": key,
                    "value_a": val_a,
                    "unit": map_a[key].get("fact_unit", ""),
                }),
                "significance": 2,
            })

    return diffs


# ---------------------------------------------------------------------------
# Narrative diffing (LLM)
# ---------------------------------------------------------------------------

def _call_narrative_diff(
    text_a: str,
    text_b: str,
    section_key: str,
    ticker: str,
    period_a: str,
    period_b: str,
) -> NarrativeDiffResult | None:
    """Call Claude to compare two section texts. Returns parsed result or None."""
    template = DIFF_PROMPT_PATH.read_text(encoding="utf-8")
    schema_json = json.dumps(get_narrative_diff_schema(), indent=2)

    prompt = (
        template
        .replace("{SECTION_KEY}", section_key)
        .replace("{TICKER}", ticker)
        .replace("{PERIOD_A}", period_a)
        .replace("{PERIOD_B}", period_b)
        .replace("{JSON_SCHEMA}", schema_json)
        .replace("{TEXT_A}", text_a)
        .replace("{TEXT_B}", text_b)
    )

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt, timeout=DEFAULT_TIMEOUT)
            data = _parse_json_response(raw)
            return NarrativeDiffResult.model_validate(data)
        except ExtractionError as e:
            logger.warning("Narrative diff attempt %d: extraction error: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            return None
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("Narrative diff attempt %d: parse/validate error: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            return None

    return None


def diff_narrative_sections(
    sections_a: list[dict],
    sections_b: list[dict],
    period_a: str,
    period_b: str,
    ticker: str,
    quiet: bool = False,
) -> list[dict]:
    """Compare matched filing sections via LLM narrative analysis.

    Args:
        sections_a: Document sections from period A (from EvidenceDB.get_document_sections).
        sections_b: Document sections from period B.
        period_a: Fiscal period label.
        period_b: Fiscal period label.
        ticker: Stock ticker.
        quiet: Suppress progress output.

    Returns:
        List of dicts ready for EvidenceDB.insert_semantic_diff().
    """
    map_a = {s["section_key"]: s for s in sections_a}
    map_b = {s["section_key"]: s for s in sections_b}

    all_keys = sorted(set(map_a.keys()) | set(map_b.keys()))
    diffs: list[dict] = []

    for key in all_keys:
        in_a = key in map_a
        in_b = key in map_b

        if in_a and in_b:
            text_a = map_a[key].get("content_text", "")
            text_b = map_b[key].get("content_text", "")

            if not text_a.strip() or not text_b.strip():
                continue

            if not quiet:
                logger.info("  Diffing section %s ...", key)

            result = _call_narrative_diff(
                text_a, text_b, key, ticker, period_a, period_b,
            )
            if result and result.changes:
                for change in result.changes:
                    diffs.append({
                        "ticker": ticker,
                        "section_key": key,
                        "period_a": period_a,
                        "period_b": period_b,
                        "diff_type": change.change_type,
                        "summary": change.description,
                        "detail_json": json.dumps({
                            "quote_period_a": change.quote_a,
                            "quote_period_b": change.quote_b,
                            "category": change.category,
                        }),
                        "significance": change.significance,
                    })
                if not quiet:
                    logger.info("    %s: %d changes found", key, len(result.changes))
            elif not quiet:
                logger.info("    %s: no material changes", key)

        elif in_b and not in_a:
            diffs.append({
                "ticker": ticker,
                "section_key": key,
                "period_a": period_a,
                "period_b": period_b,
                "diff_type": "added",
                "summary": f"New section '{key}' in {period_b}",
                "detail_json": json.dumps({"category": "other"}),
                "significance": 3,
            })

        else:  # in_a and not in_b
            diffs.append({
                "ticker": ticker,
                "section_key": key,
                "period_a": period_a,
                "period_b": period_b,
                "diff_type": "removed",
                "summary": f"Section '{key}' removed in {period_b}",
                "detail_json": json.dumps({"category": "other"}),
                "significance": 3,
            })

    return diffs
