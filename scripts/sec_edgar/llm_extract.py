"""
Multi-pass LLM narrative extraction.

Pass 1 (Identifier): Scan a section, list every factual claim.
Pass 2 (Extractor): For each claim batch, extract structured facts with source quotes.
Character offsets computed post-hoc by substring match.

Uses claude --print --output-format json for structured output.

Phase 2 of the evidence extraction masterplan.
"""

import difflib
import json
import logging
import subprocess
from pathlib import Path

# Resolve repo root so imports work regardless of working directory
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

import sys
sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from src.evidence_models import (
    ClaimList,
    ExtractionBatch,
    ExtractedFactModel,
    get_claim_list_schema,
    get_extraction_schema,
)

logger = logging.getLogger(__name__)

PASS1_PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "identify-claims.md"
PASS2_PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "extract-structured.md"

CLAIM_BATCH_SIZE = 5  # claims per Pass 2 invocation
MAX_CLAIMS_PER_SECTION = 30  # Must match prompts/evidence/identify-claims.md line 32
DEFAULT_TIMEOUT = 120  # seconds per claude call
QUOTE_MATCH_THRESHOLD = 0.85  # difflib ratio for fuzzy quote matching
MAX_RETRIES = 1  # retry once on validation failure


class ExtractionError(Exception):
    """Raised when an LLM extraction call fails."""
    pass


# ---------------------------------------------------------------------------
# LLM invocation
# ---------------------------------------------------------------------------

def _claude_extract(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Call claude --print --output-format json. Returns raw stdout string.

    Raises ExtractionError on timeout or non-zero exit code.
    """
    try:
        result = subprocess.run(
            [
                "claude", "--print",
                "--output-format", "json",
                "--allowedTools", "",
                "--", prompt,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ExtractionError(f"claude timed out after {timeout}s")
    except FileNotFoundError:
        raise ExtractionError("claude CLI not found — is Claude Code installed?")

    if result.returncode != 0:
        raise ExtractionError(
            f"claude exit code {result.returncode}: {result.stderr[:300]}"
        )

    return result.stdout


def _parse_json_response(raw: str) -> dict:
    """Parse JSON from claude output, handling possible wrapper formats."""
    data = json.loads(raw)

    # --output-format json may wrap in {"result": ...}
    if isinstance(data, dict) and "result" in data:
        inner = data["result"]
        if isinstance(inner, str):
            inner = json.loads(inner)
        if isinstance(inner, dict):
            return inner

    return data


# ---------------------------------------------------------------------------
# Pass 1: Identify claims
# ---------------------------------------------------------------------------

def _run_pass1(
    section_text: str,
    section_key: str,
    ticker: str,
    fiscal_period: str,
) -> ClaimList | None:
    """Pass 1: Identify factual claims in a section.

    Returns a ClaimList on success, None on failure.
    """
    template = PASS1_PROMPT_PATH.read_text(encoding="utf-8")
    schema_json = json.dumps(get_claim_list_schema(), indent=2)

    prompt = (
        template
        .replace("{SECTION_KEY}", section_key)
        .replace("{TICKER}", ticker)
        .replace("{FISCAL_PERIOD}", fiscal_period)
        .replace("{JSON_SCHEMA}", schema_json)
    )
    prompt = prompt + "\n\n---\n\nSECTION TEXT:\n\n" + section_text

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = _parse_json_response(raw)
            return ClaimList.model_validate(data)
        except ExtractionError as e:
            logger.warning("Pass 1 attempt %d: extraction error: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            return None
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("Pass 1 attempt %d: parse/validate error: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            return None

    return None


# ---------------------------------------------------------------------------
# Pass 2: Extract structured facts
# ---------------------------------------------------------------------------

def _run_pass2(
    claims: list,
    section_text: str,
    section_key: str,
    ticker: str,
    fiscal_period: str,
) -> ExtractionBatch | None:
    """Pass 2: Extract structured facts from a batch of claims.

    Returns an ExtractionBatch on success, None on failure.
    """
    template = PASS2_PROMPT_PATH.read_text(encoding="utf-8")
    schema_json = json.dumps(get_extraction_schema(section_key), indent=2)

    claims_text = "\n".join(
        f"- [{c.claim_type}] {c.claim_text}" for c in claims
    )

    prompt = (
        template
        .replace("{SECTION_KEY}", section_key)
        .replace("{TICKER}", ticker)
        .replace("{FISCAL_PERIOD}", fiscal_period)
        .replace("{JSON_SCHEMA}", schema_json)
        .replace("{CLAIMS}", claims_text)
    )
    prompt = prompt + "\n\n---\n\nSECTION TEXT:\n\n" + section_text

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = _parse_json_response(raw)
            return ExtractionBatch.model_validate(data)
        except ExtractionError as e:
            logger.warning("Pass 2 attempt %d: extraction error: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            return None
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("Pass 2 attempt %d: parse/validate error: %s", attempt + 1, e)
            if attempt < MAX_RETRIES:
                continue
            return None

    return None


# ---------------------------------------------------------------------------
# Character offset computation
# ---------------------------------------------------------------------------

def _compute_char_offsets(
    source_quote: str, section_text: str,
) -> tuple[int | None, int | None]:
    """Find the source_quote's position in the section text.

    Tries exact substring match first. Falls back to fuzzy sliding-window
    match (difflib). Returns (start, end) or (None, None).
    """
    if not source_quote or not section_text:
        return None, None

    # Exact match
    idx = section_text.find(source_quote)
    if idx >= 0:
        return idx, idx + len(source_quote)

    # Fuzzy match: slide a window of similar length across the text
    quote_len = len(source_quote)
    if quote_len > len(section_text):
        return None, None

    best_ratio = 0.0
    best_start = None

    # Sample positions for efficiency (step = quarter of quote length)
    step = max(1, quote_len // 4)
    for start in range(0, len(section_text) - quote_len + 1, step):
        candidate = section_text[start : start + quote_len]
        ratio = difflib.SequenceMatcher(None, source_quote, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_start = start

    if best_ratio >= QUOTE_MATCH_THRESHOLD and best_start is not None:
        return best_start, best_start + quote_len

    return None, None


# ---------------------------------------------------------------------------
# Confidence assignment
# ---------------------------------------------------------------------------

def _assign_confidence(fact: ExtractedFactModel, has_exact_offset: bool) -> float:
    """Assign confidence based on extraction method and quote match quality.

    LLM-extracted quantitative facts: 0.85 base
    LLM-extracted narrative facts: 0.80 base
    Exact quote match: +0.05 bonus
    Capped at 0.95 (below XBRL confidence of 1.0).
    """
    base = 0.85 if fact.fact_value_numeric is not None else 0.80
    if has_exact_offset:
        base += 0.05
    return min(base, 0.95)


# ---------------------------------------------------------------------------
# Fact-to-DB conversion
# ---------------------------------------------------------------------------

def _fact_to_db_dict(
    fact: ExtractedFactModel,
    ticker: str,
    source_document_id: int,
    document_section_id: int | None,
    fiscal_period: str,
    extraction_run_id: str,
    section_text: str,
) -> dict:
    """Convert Pydantic model to dict for EvidenceDB.batch_insert_facts()."""
    start, end = _compute_char_offsets(fact.source_quote, section_text)
    has_exact = (
        start is not None
        and end is not None
        and section_text[start:end] == fact.source_quote
    )

    return {
        "ticker": ticker,
        "source_document_id": source_document_id,
        "document_section_id": document_section_id,
        "fact_type": fact.fact_type.value,
        "fact_key": fact.fact_key,
        "fact_value": fact.fact_value,
        "fact_value_numeric": fact.fact_value_numeric,
        "fact_unit": fact.fact_unit.value,
        "fiscal_period": fact.fiscal_period or fiscal_period,
        "confidence": _assign_confidence(fact, has_exact),
        "extraction_method": "llm_structured",
        "source_quote": fact.source_quote,
        "source_char_offset_start": start,
        "source_char_offset_end": end,
        "computation_trace_json": None,
        "extraction_run_id": extraction_run_id,
        "is_active": 1,
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def extract_section_facts(
    section_text: str,
    section_key: str,
    ticker: str,
    fiscal_period: str,
    extraction_run_id: str,
    source_document_id: int,
    document_section_id: int | None,
    quiet: bool = False,
) -> list[dict]:
    """Extract structured facts from a filing section via two-pass LLM pipeline.

    Returns list of dicts ready for EvidenceDB.batch_insert_facts().
    Partial success is valid — failed batches are skipped, successful ones kept.
    """
    # Pass 1: Identify claims
    claims = _run_pass1(section_text, section_key, ticker, fiscal_period)
    if not claims or not claims.claims:
        if not quiet:
            logger.info("  %s/%s: no claims identified", ticker, section_key)
        return []

    if not quiet:
        logger.info(
            "  %s/%s: %d claims identified",
            ticker, section_key, len(claims.claims),
        )

    # Pass 2: Extract facts in batches
    all_facts: list[dict] = []
    for i in range(0, len(claims.claims), CLAIM_BATCH_SIZE):
        batch = claims.claims[i : i + CLAIM_BATCH_SIZE]
        batch_num = i // CLAIM_BATCH_SIZE + 1
        try:
            extraction = _run_pass2(
                batch, section_text, section_key, ticker, fiscal_period,
            )
            if extraction and extraction.facts:
                for fact in extraction.facts:
                    db_fact = _fact_to_db_dict(
                        fact, ticker, source_document_id,
                        document_section_id, fiscal_period,
                        extraction_run_id, section_text,
                    )
                    all_facts.append(db_fact)
                if not quiet and extraction.skipped_claims:
                    logger.info(
                        "  %s/%s batch %d: %d skipped claims",
                        ticker, section_key, batch_num,
                        len(extraction.skipped_claims),
                    )
        except ExtractionError as e:
            logger.warning(
                "  %s/%s batch %d: %s",
                ticker, section_key, batch_num, e,
            )
            continue

    if not quiet:
        logger.info(
            "  %s/%s: %d facts extracted total",
            ticker, section_key, len(all_facts),
        )

    return all_facts
