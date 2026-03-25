"""
Fact checker — verify report assertions against extracted evidence.

Anti-sycophancy design: verification runs in fresh LLM context with a
prompt that explicitly encourages flagging contradictions.

Phase 4 of the evidence extraction masterplan.
"""

import json
import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

import sys
sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from src.evidence_models import VerificationBatch, get_verification_schema

PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "verify-claims.md"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 1
BATCH_SIZE = 5
MAX_CANDIDATE_FACTS = 20


# ---------------------------------------------------------------------------
# Numeric extraction from assertion text
# ---------------------------------------------------------------------------

# Patterns for extracting numbers from assertions
_NUM_PATTERNS = [
    # $4.3B, $18.4B, $761M
    (re.compile(r"\$\s*([\d,.]+)\s*[Bb](?:illion)?"), 1e9),
    (re.compile(r"\$\s*([\d,.]+)\s*[Mm](?:illion)?"), 1e6),
    (re.compile(r"\$\s*([\d,.]+)\s*[Kk]"), 1e3),
    (re.compile(r"\$\s*([\d,.]+)\s*[Tt](?:rillion)?"), 1e12),
    # Plain dollar amounts (assume millions if > 100, else raw)
    (re.compile(r"\$\s*([\d,.]+)"), 1.0),
    # Percentages: 11%, ~11%, 63-64% (take first number)
    (re.compile(r"~?\s*([\d,.]+)\s*%"), 0.01),
]


def _extract_number(text: str) -> float | None:
    """Extract the first recognizable number from assertion text."""
    for pattern, multiplier in _NUM_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                num_str = match.group(1).replace(",", "")
                return float(num_str) * multiplier
            except ValueError:
                continue
    return None


# ---------------------------------------------------------------------------
# Numeric cross-check (mechanical, no LLM)
# ---------------------------------------------------------------------------

def _numeric_cross_check(
    assertion_text: str, fact_value_numeric: float,
) -> tuple[str, float] | None:
    """Compare number in assertion to fact value.

    Returns (relationship, match_score) or None if no number in assertion.
    """
    assertion_num = _extract_number(assertion_text)
    if assertion_num is None or fact_value_numeric is None:
        return None

    if assertion_num == 0 and fact_value_numeric == 0:
        return ("supports", 0.95)

    if assertion_num == 0 or fact_value_numeric == 0:
        return ("contradicts", 0.30)

    pct_diff = abs(assertion_num - fact_value_numeric) / abs(fact_value_numeric)

    if pct_diff <= 0.02:
        return ("supports", 0.95)
    elif pct_diff <= 0.05:
        return ("supports", 0.85)
    elif pct_diff <= 0.10:
        return ("partial", 0.70)
    else:
        return ("contradicts", 0.30)


# ---------------------------------------------------------------------------
# Candidate fact retrieval
# ---------------------------------------------------------------------------

def _build_candidate_facts(
    assertion: dict, all_facts: list[dict],
) -> list[dict]:
    """Select relevant facts for an assertion. Cap at MAX_CANDIDATE_FACTS."""
    assertion_text = assertion.get("assertion_text", "").lower()

    # Simple keyword matching for fact relevance
    keywords = set()
    for word in re.findall(r"[a-z]+", assertion_text):
        if len(word) > 3:
            keywords.add(word)

    scored_facts = []
    for fact in all_facts:
        score = 0.0
        fact_key = fact.get("fact_key", "").lower()
        fact_value = fact.get("fact_value", "").lower()

        # Keyword overlap with fact_key
        for kw in keywords:
            if kw in fact_key:
                score += 2.0
            if kw in fact_value:
                score += 1.0

        # Quantitative assertion + numeric fact: bonus
        if assertion.get("assertion_type") == "quantitative" and fact.get("fact_value_numeric") is not None:
            score += 1.0

        # Higher confidence facts preferred
        score += fact.get("confidence", 0.5) * 0.5

        if score > 0:
            scored_facts.append((score, fact))

    # Sort by relevance score descending, then by confidence
    scored_facts.sort(key=lambda x: (-x[0], -x[1].get("confidence", 0)))
    return [f for _, f in scored_facts[:MAX_CANDIDATE_FACTS]]


# ---------------------------------------------------------------------------
# LLM verification
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


def _verify_batch_llm(
    assertions_batch: list[dict],
    candidate_facts_per_assertion: list[list[dict]],
    ticker: str,
) -> VerificationBatch | None:
    """Run LLM verification on a batch of assertions."""
    if not PROMPT_PATH.exists():
        logger.warning("Verify prompt not found at %s", PROMPT_PATH)
        return None

    template = PROMPT_PATH.read_text(encoding="utf-8")
    schema_json = json.dumps(get_verification_schema("verify"), indent=2)

    # Build assertions text
    assertions_text = ""
    for i, a in enumerate(assertions_batch):
        assertions_text += f"\n[{i}] {a['assertion_text']}"
        assertions_text += f"\n    Type: {a.get('assertion_type', 'unknown')}"
        assertions_text += f"\n    Category: {a.get('category', 'unknown')}\n"

    # Build evidence text
    evidence_text = ""
    for i, facts in enumerate(candidate_facts_per_assertion):
        evidence_text += f"\n--- Evidence for assertion [{i}] ---\n"
        if not facts:
            evidence_text += "  (no relevant evidence found)\n"
        else:
            for f in facts[:10]:  # Limit per-assertion to keep prompt manageable
                evidence_text += (
                    f"  fact_key: {f['fact_key']}\n"
                    f"  fact_value: {f['fact_value']}\n"
                    f"  fact_value_numeric: {f.get('fact_value_numeric', 'N/A')}\n"
                    f"  source_quote: {f.get('source_quote', 'N/A')[:200]}\n"
                    f"  confidence: {f.get('confidence', '?')}\n\n"
                )

    prompt = (
        template
        .replace("{TICKER}", ticker)
        .replace("{ASSERTIONS}", assertions_text)
        .replace("{EVIDENCE}", evidence_text)
        .replace("{JSON_SCHEMA}", schema_json)
    )

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = _parse_json_response(raw)
            return VerificationBatch.model_validate(data)
        except (RuntimeError, json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Verify batch attempt %d: %s", attempt + 1, exc)
            if attempt < MAX_RETRIES:
                continue
            return None

    return None


# ---------------------------------------------------------------------------
# Evidence link construction
# ---------------------------------------------------------------------------

def _find_fact_id_by_key(fact_key: str | None, all_facts: list[dict]) -> int | None:
    """Look up extracted_fact id by fact_key."""
    if not fact_key:
        return None
    for f in all_facts:
        if f.get("fact_key") == fact_key:
            return f.get("id")
    return None


def _evidence_to_db_dict(
    assertion_id: int,
    relationship: str,
    match_score: float,
    fact_id: int | None,
    verification_method: str,
    reasoning: str = "",
) -> dict | None:
    """Build dict for insert_assertion_evidence().

    Returns None if fact_id is None (unverifiable — no evidence row created).
    """
    if fact_id is None:
        # Per review: don't create evidence rows for unverifiable assertions.
        # The LEFT JOIN in get_evidence_summary_for_ticker() handles this.
        return None

    return {
        "assertion_id": assertion_id,
        "extracted_fact_id": fact_id,
        "relationship": relationship,
        "match_score": match_score,
        "verification_method": verification_method,
        "verification_detail_json": json.dumps({"reasoning": reasoning}),
        "verified_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def verify_assertions(
    stored_assertions: list[dict],
    all_facts: list[dict],
    ticker: str,
    quiet: bool = False,
) -> list[dict]:
    """Verify assertions against extracted facts.

    Returns list of evidence link dicts for insert_assertion_evidence().
    Assertions with no matching evidence get no evidence row (handled by DB query).
    """
    if not stored_assertions:
        return []
    if not all_facts:
        if not quiet:
            logger.info("No extracted facts for %s — all assertions unverifiable", ticker)
        return []

    evidence_links = []
    skipped_by_numeric = 0

    # Process in batches
    for batch_start in range(0, len(stored_assertions), BATCH_SIZE):
        batch = stored_assertions[batch_start : batch_start + BATCH_SIZE]

        # Build candidate facts for each assertion in batch
        candidates_per_assertion = [_build_candidate_facts(a, all_facts) for a in batch]

        # Try mechanical numeric cross-check first
        # Only trust numeric matches when numbers are CLOSE (supports/partial).
        # Mismatches go to LLM — the candidate fact may be irrelevant.
        batch_needs_llm = []
        batch_candidates_for_llm = []
        for i, (assertion, candidates) in enumerate(zip(batch, candidates_per_assertion)):
            if assertion.get("assertion_type") == "quantitative" and candidates:
                resolved = False
                for c in candidates:
                    check = _numeric_cross_check(assertion["assertion_text"], c.get("fact_value_numeric"))
                    if check:
                        rel, score = check
                        # Only trust mechanical match for supports/partial.
                        # "contradicts" from numeric check is unreliable because
                        # the candidate fact may be about something completely different.
                        if rel in ("supports", "partial"):
                            fact_id = c.get("id")
                            link = _evidence_to_db_dict(
                                assertion["id"], rel, score, fact_id,
                                "numeric_exact",
                                f"Numeric cross-check: assertion vs fact {c.get('fact_key')}",
                            )
                            if link:
                                evidence_links.append(link)
                                skipped_by_numeric += 1
                                resolved = True
                            break
                if not resolved:
                    batch_needs_llm.append(assertion)
                    batch_candidates_for_llm.append(candidates)
            else:
                batch_needs_llm.append(assertion)
                batch_candidates_for_llm.append(candidates)

        # LLM verification for remaining assertions
        if batch_needs_llm:
            result = _verify_batch_llm(batch_needs_llm, batch_candidates_for_llm, ticker)
            if result:
                for vr in result.results:
                    if 0 <= vr.assertion_index < len(batch_needs_llm):
                        assertion = batch_needs_llm[vr.assertion_index]
                        fact_id = _find_fact_id_by_key(vr.matched_fact_key, all_facts)
                        link = _evidence_to_db_dict(
                            assertion["id"],
                            vr.relationship,
                            vr.match_score,
                            fact_id,
                            "llm_semantic",
                            vr.reasoning,
                        )
                        if link:
                            evidence_links.append(link)

    if not quiet:
        logger.info(
            "Verification complete for %s: %d evidence links, %d resolved by numeric check",
            ticker, len(evidence_links), skipped_by_numeric,
        )

    return evidence_links
