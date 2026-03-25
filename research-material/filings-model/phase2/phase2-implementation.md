# Phase 2 Implementation Manual — LLM Narrative Extraction (Tier 2)

## Context

Phase 1 (EDGAR Client + XBRL Extraction) and Phase 3 (Database Schema + Storage) are both complete. Phase 2 fills the gap between them: extracting narrative evidence from 10-K sections (MD&A, Risk Factors, Business description) that XBRL cannot capture. This is the layer that turns SEC prose into structured, citable facts stored in the Phase 3 database and rendered as context files for the analysis agents.

**Depends on:** Phase 1 (EDGAR client in `scripts/sec_edgar/`), Phase 3 (EvidenceDB in `src/evidence.py`).
**Breaking changes:** None. Opt-in via `--tier2` flag.

---

## Architecture

**Foundation:** `filing.obj()` from edgartools returns a `TenK`/`TwentyF`/`FortyF` object with named section accessors:
- `.business` → Item 1 text
- `.risk_factors` → Item 1A text
- `.management_discussion` → Item 7 text (MD&A)
- `['Item 7A']` → Item 7A text (Market Risk, via `__getitem__`)

Phase 1 used `company.get_financials()` (a different API path — financial statements only). Phase 2 uses `company.get_filings(form=...).latest().obj()` to access the full filing's narrative sections.

**Two-pass extraction:**
1. **Pass 1 (Identify):** LLM scans a section, lists every factual claim in natural language. Keeps each call simple — detection only, no structured extraction yet. Avoids "lost in the middle" by separating detection from extraction.
2. **Pass 2 (Extract):** For each batch of claims, LLM extracts structured facts with verbatim `source_quote`. Uses Pydantic-generated JSON Schema for reliable output. Character offsets computed post-hoc by exact substring match.

**LLM invocation:** `claude --print --output-format json` subprocess calls. Matches the project's existing pattern (`run.sh` uses `claude --print` for all agent invocations). Include the target JSON structure in the prompt text. Validate output with Pydantic v2 on the Python side. Retry once on validation failure.

**Cost:** ~8-25 LLM calls per ticker (3-5 sections × Pass 1 + 5-20 claims batched in groups of 5 × Pass 2). At 20-30 tickers per cycle: **$30-60/cycle** (per masterplan estimate).

---

## Files

### New files

| File | LOC | Purpose |
|------|-----|---------|
| `src/evidence_models.py` | ~200 | Pydantic v2 models + JSON Schema generation |
| `scripts/sec_edgar/sections.py` | ~200 | Section parsing from edgartools TenK/TwentyF objects |
| `scripts/sec_edgar/llm_extract.py` | ~350 | Multi-pass LLM extraction orchestrator |
| `scripts/sec_edgar/render_evidence.py` | ~150 | Render narrative evidence to markdown |
| `prompts/evidence/identify-claims.md` | ~80 | Pass 1 prompt template |
| `prompts/evidence/extract-structured.md` | ~100 | Pass 2 prompt template |
| `tests/test_evidence_models.py` | ~150 | Model validation tests |
| `tests/test_sections.py` | ~120 | Section parsing tests |
| `tests/test_llm_extract.py` | ~200 | Extraction pipeline tests (mocked LLM) |

### Modified files

| File | Change |
|------|--------|
| `scripts/sec_edgar/client.py` | Add `fetch_filing_object()` function (~40 LOC) |
| `scripts/sec_edgar/__init__.py` | Add exports for new functions |
| `scripts/sec_edgar/__main__.py` | Add `--tier2` flag and orchestration (~60 LOC) |

### Unchanged files

| File | Why unchanged |
|------|---------------|
| `src/evidence.py` | All 44 EvidenceDB methods already exist — Phase 2 is a consumer |
| `src/database.py` | Schema v3 already applied |
| `db/evidence_schema.sql` | All 8 tables already exist |
| `scripts/sec_edgar/xbrl.py` | Phase 1 XBRL extraction unchanged |
| `scripts/sec_edgar/render.py` | Phase 1 markdown renderer unchanged |
| `run.sh` | `cmd_extract()` already passes all args through to `scripts/fetch-edgar.py` |

---

## File-by-File Specification

### 1. `src/evidence_models.py`

Pydantic v2 models that serve as the shared contract between extraction (scripts) and storage (src). These generate JSON Schemas for the LLM prompts and validate data before DB insertion.

```python
"""
Pydantic v2 models for the evidence extraction pipeline.

Used by:
- LLM extraction (scripts/sec_edgar/llm_extract.py) — JSON Schema in prompts, output validation
- DB storage (src/evidence.py) — validate before batch_insert_facts()

Not used by Phase 1 XBRL extraction (which writes dicts directly).
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FactType(str, Enum):
    metric = "metric"
    narrative = "narrative"
    guidance = "guidance"
    risk_factor = "risk_factor"


class FactUnit(str, Enum):
    usd = "USD"
    percent = "percent"
    ratio = "ratio"
    count = "count"
    days = "days"
    text = "text"  # purely narrative facts with no numeric value
```

**Pass 1 models:**

```python
class IdentifiedClaim(BaseModel):
    """A single factual claim found in a section (Pass 1 output)."""
    claim_text: str = Field(..., description="The factual claim in one sentence")
    claim_type: str = Field(..., description="quantitative | qualitative | comparative | causal")
    is_quantitative: bool = Field(..., description="True if the claim contains a specific number")
    approximate_location: str = Field(..., description="First 10 words of the sentence containing the claim")


class ClaimList(BaseModel):
    """All claims from a section (Pass 1 output)."""
    section_key: str
    claims: list[IdentifiedClaim]
    total_claims: int
```

**Pass 2 models:**

```python
class ExtractedFactModel(BaseModel):
    """Structured extraction from a single claim (Pass 2 output)."""
    fact_type: FactType
    fact_key: str = Field(..., description="Dot-notation key: 'revenue.cloud', 'risk.regulatory'")
    fact_value: str = Field(..., description="Human-readable value as stated in filing")
    fact_value_numeric: Optional[float] = Field(None, description="Normalized to base units")
    fact_unit: FactUnit
    fiscal_period: Optional[str] = Field(None, description="FY2025, Q3FY2025, etc.")
    source_quote: str = Field(..., min_length=10, description="VERBATIM substring from filing text")
    confidence_note: Optional[str] = Field(None, description="Caveats about extraction confidence")


class ExtractionBatch(BaseModel):
    """Extracted facts from a batch of claims (Pass 2 output)."""
    section_key: str
    facts: list[ExtractedFactModel]
    skipped_claims: list[str] = Field(default_factory=list)
```

**Schema registry** (dict at module level — no separate file needed):

```python
# Section → extraction model mapping
# All sections currently use ExtractionBatch; section-specific models
# can be added later (e.g., RiskFactorBatch with severity field)
SECTION_SCHEMAS: dict[str, type[BaseModel]] = {
    "mda": ExtractionBatch,
    "risk_factors": ExtractionBatch,
    "business": ExtractionBatch,
    "market_risk": ExtractionBatch,
}


def get_extraction_schema(section_key: str) -> dict:
    """Return JSON Schema dict for a section's extraction model."""
    model = SECTION_SCHEMAS.get(section_key, ExtractionBatch)
    return model.model_json_schema()
```

**Design note:** The masterplan specifies separate `src/evidence/schema_registry.py` (~100 LOC), but a dict + one function in the models file accomplishes the same thing in ~10 lines. Section-specific models (e.g., `RiskFactorBatch` with a severity field) can be added later by extending this dict.

---

### 2. `scripts/sec_edgar/sections.py`

Parse 10-K/20-F/40-F narrative sections via edgartools, split long sections, compute token estimates, return dicts ready for `EvidenceDB.upsert_document_section()`.

```python
"""
Section parser — extract narrative sections from SEC filings via edgartools.

Uses filing.obj() to get TenK/TwentyF/FortyF objects with named section accessors.
Splits sections exceeding TOKEN_CAP at paragraph boundaries.
"""

import hashlib
import logging
import sys

logger = logging.getLogger(__name__)

TOKEN_CAP = 8000       # max tokens per section chunk
CHARS_PER_TOKEN = 4    # conservative estimate (no tiktoken dependency)
```

**Section map** (form type → section_key → accessor):

```python
def _get_section_text(filing_obj, accessor):
    """Safely call an accessor, return text or None."""
    try:
        if callable(accessor):
            result = accessor(filing_obj)
        else:
            result = filing_obj[accessor]
        # edgartools returns str, Section object, or None
        if result is None:
            return None
        return str(result) if not isinstance(result, str) else result
    except Exception as e:
        logger.warning("Section accessor failed: %s", e)
        return None


SECTION_MAP = {
    "10-K": [
        ("business",     "Business",                lambda obj: obj.business),
        ("risk_factors", "Risk Factors",            lambda obj: obj.risk_factors),
        ("mda",          "Management Discussion",   lambda obj: obj.management_discussion),
        ("market_risk",  "Market Risk",             lambda obj: obj["Item 7A"]),
    ],
    "20-F": [
        ("business",     "Business",                lambda obj: obj.business),
        ("risk_factors", "Risk Factors",            lambda obj: obj.risk_factors),
        ("mda",          "Operating Review",        lambda obj: obj.management_discussion),
    ],
    "40-F": [
        ("business",     "Business",                lambda obj: obj.business),
        ("risk_factors", "Risk Factors",            lambda obj: obj.risk_factors),
        ("mda",          "MD&A",                    lambda obj: getattr(obj, "mda_text", None)),
    ],
}
```

Handle amendment form types (10-K/A, 20-F/A, 40-F/A) by stripping the `/A` suffix for the section map lookup.

**Key functions:**

`extract_sections(filing_obj, form_type: str) -> list[dict]`
- Looks up the section map for the form type (strip `/A` suffix)
- For each section accessor, calls `_get_section_text()`
- If text exceeds TOKEN_CAP, calls `_split_section()`
- Returns list of dicts: `{section_key, section_title, section_order, content_text, content_hash, token_estimate}`
- Warnings list for sections that returned None

`_split_section(text: str, section_key: str, token_cap: int) -> list[tuple[str, str, str]]`
- Splits at double-newline (`\n\n`) boundaries
- Returns list of `(section_key_with_suffix, title_with_part, text_chunk)`
- Suffixed keys: `mda_part1`, `mda_part2`, etc.
- If a single paragraph exceeds the cap, split at sentence boundaries (`. `)

`_estimate_tokens(text: str) -> int` — `len(text) // CHARS_PER_TOKEN`

`_content_hash(text: str) -> str` — `hashlib.sha256(text.encode()).hexdigest()[:16]`

**Error handling:** Each section accessor is individually try/excepted via `_get_section_text()`. If edgartools can't parse Item 7 but can parse Item 1A, we extract what we can. Never fatal.

---

### 3. `scripts/sec_edgar/client.py` — extension

Add one new function. Do not modify `fetch_10k()`.

```python
def fetch_filing_object(ticker: str, force: bool = False, quiet: bool = False):
    """
    Fetch the latest 10-K/20-F/40-F filing object for narrative section parsing.

    Returns (filing_obj, filing_metadata) or (None, None) on failure.
    The filing_obj is a TenK/TwentyF/FortyF with section accessors.
    filing_metadata is the same dict format as fetch_10k().
    """
    _set_identity()

    try:
        company = Company(ticker)
    except CompanyNotFoundError:
        if not quiet:
            print(f"  {ticker} — Company not found on EDGAR. Skipping.", file=sys.stderr)
        return None, None
    except Exception as e:
        if not quiet:
            print(f"  {ticker} — EDGAR lookup failed: {e}", file=sys.stderr)
        return None, None

    filing_metadata = {
        "company_name": company.name,
        "cik": str(company.cik),
        "ticker": ticker,
        "form_type": None,
        "filing_date": None,
        "period_of_report": None,
        "accession_no": None,
    }

    try:
        filings = company.get_filings(form=FORM_TYPES)
        if not filings or len(filings) == 0:
            if not quiet:
                print(f"  {ticker} — No filings found.", file=sys.stderr)
            return None, None

        latest = filings.latest()
        filing_metadata["form_type"] = latest.form
        filing_metadata["filing_date"] = str(latest.filing_date)
        filing_metadata["period_of_report"] = str(latest.period_of_report)
        filing_metadata["accession_no"] = latest.accession_no

        filing_obj = latest.obj()
        return filing_obj, filing_metadata

    except Exception as e:
        if not quiet:
            print(f"  {ticker} — Failed to get filing object: {e}", file=sys.stderr)
        return None, None
```

**Design note:** This duplicates the Company resolution from `fetch_10k()`. An alternative is refactoring both to share the resolution, but that risks breaking the working Phase 1 code. Keep them independent — they're ~20 lines of shared logic.

---

### 4. `scripts/sec_edgar/llm_extract.py`

Multi-pass LLM extraction orchestrator. The core of Phase 2.

```python
"""
Multi-pass LLM narrative extraction.

Pass 1 (Identifier): Scan a section, list every factual claim.
Pass 2 (Extractor): For each claim batch, extract structured facts with source quotes.
Character offsets computed post-hoc by substring match.

Uses claude --print --output-format json for structured output.
"""

import difflib
import json
import logging
import subprocess
from pathlib import Path

from src.evidence_models import (
    ClaimList, ExtractionBatch, ExtractedFactModel,
    get_extraction_schema,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PASS1_PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "identify-claims.md"
PASS2_PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "extract-structured.md"

CLAIM_BATCH_SIZE = 5    # claims per Pass 2 invocation
MAX_CLAIMS_PER_SECTION = 30
DEFAULT_TIMEOUT = 120   # seconds per claude call
QUOTE_MATCH_THRESHOLD = 0.85  # difflib ratio for fuzzy quote matching
MAX_RETRIES = 1  # retry once on validation failure
```

**Main entry point:**

```python
def extract_section_facts(
    section_text: str,
    section_key: str,
    ticker: str,
    fiscal_period: str,
    extraction_run_id: str,
    source_document_id: int,
    document_section_id: int,
    quiet: bool = False,
) -> list[dict]:
    """
    Extract structured facts from a filing section via two-pass LLM pipeline.

    Returns list of dicts ready for EvidenceDB.batch_insert_facts().
    """
    # Pass 1: Identify claims
    claims = _run_pass1(section_text, section_key, ticker, fiscal_period)
    if not claims or not claims.claims:
        if not quiet:
            logger.info("  %s/%s: no claims identified", ticker, section_key)
        return []

    if not quiet:
        logger.info("  %s/%s: %d claims identified", ticker, section_key, len(claims.claims))

    # Pass 2: Extract facts in batches
    all_facts = []
    for i in range(0, len(claims.claims), CLAIM_BATCH_SIZE):
        batch = claims.claims[i:i + CLAIM_BATCH_SIZE]
        try:
            extraction = _run_pass2(batch, section_text, section_key, ticker, fiscal_period)
            if extraction and extraction.facts:
                for fact in extraction.facts:
                    db_fact = _fact_to_db_dict(
                        fact, ticker, source_document_id, document_section_id,
                        fiscal_period, extraction_run_id, section_text,
                    )
                    all_facts.append(db_fact)
        except ExtractionError as e:
            logger.warning("  %s/%s batch %d: %s", ticker, section_key, i // CLAIM_BATCH_SIZE, e)
            continue

    if not quiet:
        logger.info("  %s/%s: %d facts extracted", ticker, section_key, len(all_facts))

    return all_facts
```

**LLM invocation:**

```python
class ExtractionError(Exception):
    pass


def _claude_extract(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Call claude --print --output-format json. Returns raw JSON string."""
    try:
        result = subprocess.run(
            ["claude", "--print", "--output-format", "json",
             "--allowedTools", "",  # no tools for extraction
             "--", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ExtractionError(f"claude timed out after {timeout}s")

    if result.returncode != 0:
        raise ExtractionError(f"claude exit code {result.returncode}: {result.stderr[:300]}")

    return result.stdout
```

**Pass 1 implementation:**

```python
def _run_pass1(section_text: str, section_key: str, ticker: str, fiscal_period: str) -> ClaimList | None:
    """Pass 1: Identify factual claims in a section."""
    template = PASS1_PROMPT_PATH.read_text()
    schema_json = json.dumps(ClaimList.model_json_schema(), indent=2)

    prompt = template.replace("{SECTION_KEY}", section_key)
    prompt = prompt.replace("{TICKER}", ticker)
    prompt = prompt.replace("{FISCAL_PERIOD}", fiscal_period)
    prompt = prompt.replace("{JSON_SCHEMA}", schema_json)
    prompt = prompt + "\n\n---\n\nSECTION TEXT:\n\n" + section_text

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = json.loads(raw)
            # Handle possible wrapper: {"result": ...} from --output-format json
            if "result" in data and isinstance(data["result"], (dict, str)):
                inner = data["result"]
                if isinstance(inner, str):
                    inner = json.loads(inner)
                data = inner
            return ClaimList.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            if attempt < MAX_RETRIES:
                logger.warning("Pass 1 attempt %d failed: %s — retrying", attempt + 1, e)
                continue
            logger.warning("Pass 1 failed after retries: %s", e)
            return None
```

**Pass 2 implementation:**

```python
def _run_pass2(
    claims: list, section_text: str, section_key: str,
    ticker: str, fiscal_period: str,
) -> ExtractionBatch | None:
    """Pass 2: Extract structured facts from a batch of claims."""
    template = PASS2_PROMPT_PATH.read_text()
    schema_json = json.dumps(ExtractionBatch.model_json_schema(), indent=2)

    claims_text = "\n".join(
        f"- [{c.claim_type}] {c.claim_text}" for c in claims
    )

    prompt = template.replace("{SECTION_KEY}", section_key)
    prompt = prompt.replace("{TICKER}", ticker)
    prompt = prompt.replace("{FISCAL_PERIOD}", fiscal_period)
    prompt = prompt.replace("{JSON_SCHEMA}", schema_json)
    prompt = prompt.replace("{CLAIMS}", claims_text)
    prompt = prompt + "\n\n---\n\nSECTION TEXT:\n\n" + section_text

    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = json.loads(raw)
            if "result" in data and isinstance(data["result"], (dict, str)):
                inner = data["result"]
                if isinstance(inner, str):
                    inner = json.loads(inner)
                data = inner
            return ExtractionBatch.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            if attempt < MAX_RETRIES:
                logger.warning("Pass 2 attempt %d failed: %s — retrying", attempt + 1, e)
                continue
            logger.warning("Pass 2 failed after retries: %s", e)
            return None
```

**Character offset computation:**

```python
def _compute_char_offsets(source_quote: str, section_text: str) -> tuple[int | None, int | None]:
    """Find the source_quote's position in the section text.

    Tries exact substring match first. Falls back to fuzzy match (difflib).
    Returns (start, end) or (None, None).
    """
    # Exact match
    idx = section_text.find(source_quote)
    if idx >= 0:
        return idx, idx + len(source_quote)

    # Fuzzy match: slide a window of similar length
    quote_len = len(source_quote)
    best_ratio = 0.0
    best_start = None

    # Sample positions (every 100 chars) for efficiency
    step = max(1, quote_len // 4)
    for start in range(0, len(section_text) - quote_len + 1, step):
        candidate = section_text[start:start + quote_len]
        ratio = difflib.SequenceMatcher(None, source_quote, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_start = start

    if best_ratio >= QUOTE_MATCH_THRESHOLD and best_start is not None:
        return best_start, best_start + quote_len

    return None, None
```

**Confidence assignment:**

```python
def _assign_confidence(fact: ExtractedFactModel, has_exact_offset: bool) -> float:
    """Assign confidence based on extraction method and quote match quality.

    LLM-extracted quantitative facts: 0.85 base
    LLM-extracted narrative facts: 0.80 base
    Exact quote match: +0.05 bonus
    """
    base = 0.85 if fact.fact_value_numeric is not None else 0.80
    if has_exact_offset:
        base += 0.05
    return min(base, 0.95)  # cap below XBRL confidence (1.0)
```

**Fact-to-DB conversion:**

```python
def _fact_to_db_dict(
    fact: ExtractedFactModel,
    ticker: str,
    source_document_id: int,
    document_section_id: int,
    fiscal_period: str,
    extraction_run_id: str,
    section_text: str,
) -> dict:
    """Convert Pydantic model to dict for EvidenceDB.batch_insert_facts()."""
    start, end = _compute_char_offsets(fact.source_quote, section_text)
    has_exact = start is not None and section_text[start:end] == fact.source_quote

    return {
        "ticker": ticker,
        "source_document_id": source_document_id,
        "document_section_id": document_section_id,
        "fact_type": fact.fact_type.value,
        "fact_key": f"{fact.fact_key}",  # already dot-notation from LLM
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
```

**fact_key naming convention** (critical — must not collide with XBRL keys):

XBRL extraction (Phase 1) uses keys like `revenue`, `net_income`, `total_assets`. LLM extraction must use disambiguated dot-notation keys to avoid UNIQUE constraint violations on `(source_document_id, fact_key, fiscal_period)`:

| Section | Example fact_keys |
|---------|------------------|
| mda | `mda.revenue_growth_yoy`, `mda.segment.cloud_revenue`, `mda.margin_driver.pricing` |
| risk_factors | `risk.regulatory.eu`, `risk.competitive.market_share`, `risk.macro.interest_rate` |
| business | `biz.model.subscription`, `biz.geography.countries`, `biz.employees.total` |
| market_risk | `market_risk.fx.eur_usd`, `market_risk.interest.sensitivity` |

The section prefix ensures no collision with XBRL fact_keys. Document this convention in the prompt.

---

### 5. `scripts/sec_edgar/render_evidence.py`

Render extracted narrative facts to `context/{TICKER}/evidence-10K-{YYYY}.md` for agent consumption. Follows the same pattern as `render.py`.

```python
"""
Markdown renderer for narrative evidence extracted from SEC filings.

Output: compact markdown for agent consumption, organized by section.
"""

from datetime import datetime, timezone


def render_evidence_markdown(ticker: str, facts: list[dict], filing_metadata: dict, warnings: list[str] = None) -> str:
    """Render extracted narrative facts as a markdown file."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    period = filing_metadata.get("period_of_report", "unknown")
    form = filing_metadata.get("form_type", "10-K")
    company = filing_metadata.get("company_name", ticker)

    sections = []

    # Header
    sections.append(f"# Narrative Evidence: {ticker} — {company} ({form} {_fiscal_year(period)})")
    sections.append(f"\n**Generated:** {now}")
    sections.append(f"**Source:** SEC EDGAR (LLM extraction from {form})")
    sections.append(f"**Extraction method:** Tier 2 — multi-pass structured extraction")
    sections.append(f"**Filing period:** {period}")
    sections.append(f"**Confidence range:** 0.80-0.90 (LLM-extracted)")

    # Group facts by section_key prefix (mda.*, risk.*, biz.*, market_risk.*)
    grouped = _group_by_section(facts)

    section_labels = {
        "mda": "MD&A Key Findings",
        "risk": "Risk Factors",
        "biz": "Business Description",
        "market_risk": "Market Risk Disclosures",
    }

    for key in ["mda", "risk", "biz", "market_risk"]:
        group = grouped.get(key, [])
        if not group:
            continue
        label = section_labels.get(key, key)
        sections.append(f"\n## {label} ({len(group)} facts extracted)\n")
        sections.append("| Fact Key | Value | Source Quote (excerpt) | Conf |")
        sections.append("|----------|-------|----------------------|------|")
        for f in group:
            quote = (f["source_quote"][:60] + "...") if len(f.get("source_quote", "")) > 60 else f.get("source_quote", "")
            conf = f"{f['confidence']:.2f}" if f.get("confidence") else "—"
            sections.append(f"| {f['fact_key']} | {f.get('fact_value', '—')} | {quote} | {conf} |")

    # Warnings
    if warnings:
        sections.append("\n## Data Gaps & Warnings\n")
        for w in warnings:
            sections.append(f"- {w}")
    elif not facts:
        sections.append("\n## Data Gaps & Warnings\n\n- No narrative facts could be extracted from this filing.")
    else:
        sections.append("\n## Data Gaps & Warnings\n\nNone — extraction completed successfully.")

    return "\n".join(sections) + "\n"
```

Output file path: `context/{TICKER}/evidence-10K-{YYYY}.md` (where YYYY is the fiscal year from period_of_report).

---

### 6. `scripts/sec_edgar/__init__.py` changes

```python
"""
sec_edgar — SEC EDGAR filing data extraction via edgartools.

Phase 1: XBRL facts + multi-year financial statements.
Phase 2: Narrative section parsing via TenK/TwentyF .obj() parsed sections.
"""

from .client import fetch_10k, fetch_filing_object
from .xbrl import extract_financials
from .sections import extract_sections
from .llm_extract import extract_section_facts

__all__ = ["fetch_10k", "fetch_filing_object", "extract_financials",
           "extract_sections", "extract_section_facts"]
```

---

### 7. `scripts/sec_edgar/__main__.py` changes

Add `--tier2` flag to argparse. After existing Tier 1 processing, if `--tier2` is set, run the narrative extraction pipeline.

```python
parser.add_argument("--tier2", action="store_true",
                    help="Run LLM narrative extraction (Tier 2) after XBRL extraction")
```

In the main processing loop, after the existing `fetch_10k()` call:

```python
if args.tier2 and result != "skipped" and result is not None:
    try:
        from .sections import extract_sections
        from .llm_extract import extract_section_facts
        from .render_evidence import render_evidence_markdown
        from src.database import Database
        from src.evidence import EvidenceDB

        # 1. Get filing object for section parsing
        filing_obj, filing_meta = fetch_filing_object(ticker, force=args.force, quiet=args.quiet)
        if filing_obj is None:
            if not args.quiet:
                print(f"  {ticker} — Tier 2: could not get filing object", file=sys.stderr)
            # Continue — Tier 1 already succeeded
        else:
            # 2. Parse sections
            sections, section_warnings = extract_sections(filing_obj, filing_meta["form_type"])

            # 3. Store in DB
            db = Database()
            db.connect()
            db.migrate()
            ev = EvidenceDB(db)

            doc_id = ev.upsert_source_document({
                "ticker": ticker,
                "doc_type": filing_meta["form_type"],
                "filing_date": filing_meta.get("filing_date"),
                "period_end": filing_meta.get("period_of_report"),
                "accession_number": filing_meta.get("accession_no"),
                "source_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={filing_meta.get('cik')}",
                "local_path": str(CONTEXT_DIR / ticker / "edgar-10k.md"),
                "content_hash": None,  # TODO: hash from filing content
                "section_count": len(sections),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

            section_ids = {}
            for s in sections:
                s["source_document_id"] = doc_id
                sid = ev.upsert_document_section(s)
                section_ids[s["section_key"]] = sid

            # 4. LLM extraction per section
            run_id = f"tier2-{ticker}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
            fiscal_period = _fiscal_period_from_date(filing_meta.get("period_of_report", ""))

            ev.deactivate_facts_for_document(doc_id)

            all_facts = []
            for s in sections:
                sec_id = section_ids.get(s["section_key"])
                facts = extract_section_facts(
                    s["content_text"], s["section_key"],
                    ticker, fiscal_period, run_id,
                    doc_id, sec_id,
                    quiet=args.quiet,
                )
                all_facts.extend(facts)

            if all_facts:
                ev.batch_insert_facts(all_facts)

            # 5. Render markdown
            fiscal_year = fiscal_period[:6] if fiscal_period else "unknown"
            md = render_evidence_markdown(ticker, all_facts, filing_meta, section_warnings)
            out_file = CONTEXT_DIR / ticker / f"evidence-10K-{fiscal_year}.md"
            out_file.write_text(md, encoding="utf-8")

            if not args.quiet:
                print(f"  {ticker} — Tier 2: {len(all_facts)} facts from {len(sections)} sections -> {out_file.name}")

            db._conn.close()

    except Exception as e:
        if not args.quiet:
            print(f"  {ticker} — Tier 2 ERROR: {e}", file=sys.stderr)
        # Don't count as failure — Tier 1 already succeeded
```

---

### 8. `prompts/evidence/identify-claims.md`

```markdown
# Evidence Extraction — Pass 1: Identify Claims

You are scanning a section of an SEC filing. List every factual claim
in the section text below. Do NOT extract structured data — that happens
in a separate pass.

**Section:** {SECTION_KEY}
**Ticker:** {TICKER}
**Filing period:** {FISCAL_PERIOD}

## What counts as a factual claim

- A specific number or metric ("revenue grew 11% to $40 billion")
- A stated business fact ("operates in 200+ countries")
- A forward-looking statement ("expects revenue growth of 8-10%")
- A risk disclosure with specifics ("subject to regulatory action in the EU")
- A comparison to prior period ("compared to $35.9 billion in the prior year")
- A management assertion about business drivers ("growth was driven by...")

## What does NOT count

- Boilerplate legal disclaimers or safe-harbor language
- Table-of-contents references or cross-references to other items
- Definitions of terms without factual content
- Repeated statements of the same fact in different words
- Pure GAAP accounting policy descriptions without company-specific facts

## Rules

1. Maximum {MAX_CLAIMS} claims. If there are more, prioritize:
   quantitative > comparative > causal > qualitative, and
   specific > vague.
2. Each claim must be independently understandable.
3. Keep claims close to the source language — do not rephrase significantly.
4. For claim_type use exactly one of: "quantitative", "qualitative",
   "comparative", "causal".
5. approximate_location: copy the first ~10 words of the sentence that
   contains the claim. This is used to locate it in the source later.

## Output

Return ONLY valid JSON matching this schema:

{JSON_SCHEMA}

---

SECTION TEXT:
```

(The section text is appended programmatically by `_run_pass1()`.)

---

### 9. `prompts/evidence/extract-structured.md`

```markdown
# Evidence Extraction — Pass 2: Extract Structured Facts

You are extracting structured data from specific claims identified in an
SEC filing section. For each claim below, produce a structured fact with
a VERBATIM source quote from the section text.

**Section:** {SECTION_KEY}
**Ticker:** {TICKER}
**Filing period:** {FISCAL_PERIOD}

## Claims to extract

{CLAIMS}

## Extraction rules

### fact_key
Use dot-notation with the section prefix:
- MD&A: `mda.revenue_growth`, `mda.segment.cloud`, `mda.margin_driver.pricing`
- Risk Factors: `risk.regulatory.eu`, `risk.competitive`, `risk.macro.rates`
- Business: `biz.model.subscription`, `biz.geography`, `biz.employees`
- Market Risk: `market_risk.fx.eur`, `market_risk.interest.sensitivity`

### fact_value
Human-readable as stated in the filing: "$40.0 billion", "approximately 15%",
"200+ countries and territories".

### fact_value_numeric
Normalized to base units:
- Dollar amounts → actual dollars: "$40.0 billion" → 40000000000.0
- Percentages → decimal: "15.3%" → 0.153, "grew 11%" → 0.11
- Ratios → as stated: "1.08x" → 1.08
- Counts → as stated: "200 countries" → 200
- Set null for purely qualitative facts.

### fact_unit
Exactly one of: "USD", "percent", "ratio", "count", "days", "text"

### source_quote — CRITICAL
This MUST be a VERBATIM substring of the section text below. Rules:
1. Copy the exact characters from the source. Do not rephrase, reorder,
   or combine text from different sentences.
2. A Python `section_text.find(source_quote)` operation will be run.
   If it returns -1, the fact is penalized.
3. Include enough context to verify the fact (usually 1-2 sentences).
4. Minimum 10 characters.
5. If you cannot find a verbatim quote, add the claim to skipped_claims
   instead of fabricating a quote.

### fact_type
One of: "metric" (a number), "narrative" (qualitative business fact),
"guidance" (forward-looking), "risk_factor" (risk disclosure)

## Output

Return ONLY valid JSON matching this schema:

{JSON_SCHEMA}

---

SECTION TEXT:
```

(Section text appended programmatically by `_run_pass2()`.)

---

## Usage

```bash
# Tier 1 only (existing behavior)
./run.sh extract V

# Tier 1 + Tier 2 (XBRL + narrative)
./run.sh extract V --tier2

# Multiple tickers with Tier 2
./run.sh extract V INTU SYK --tier2

# Force re-extraction
./run.sh extract V --tier2 --force

# Direct Python invocation
python3 scripts/fetch-edgar.py --tier2 V INTU
```

Analysis pipeline integration: `./run.sh analyze TICKER` continues to call `./run.sh extract TICKER` (Tier 1 only). Users opt into Tier 2 by running `./run.sh extract TICKER --tier2` before analysis. This keeps the default analysis path fast.

---

## Output

For each ticker, Tier 2 produces:

1. **`context/{TICKER}/evidence-10K-FY{YYYY}.md`** — Compact markdown with extracted narrative facts, organized by section. Automatically consumed by analysis agents via the existing context-reading loop in `run.sh` (lines 437-448).

2. **Database records:**
   - `source_documents`: one row for the filing
   - `document_sections`: one row per parsed section (3-8 sections)
   - `extracted_facts`: one row per fact (~15-40 per ticker), all with `extraction_method='llm_structured'`, `confidence` in 0.80-0.90 range, verbatim `source_quote`, and character offsets where matched

---

## Key Design Decisions

### LLM invocation via `claude --print`
Every agent call in this project uses `claude --print`. Adding the Anthropic SDK would introduce a second invocation pattern, require an API key env var, and add a dependency. Subprocess calls are slower (~3s each) but the call count is manageable (8-25 per ticker). JSON Schema included in prompt text + Pydantic validation on the Python side gives reliable structured output.

### Two-pass separation
Pass 1 (Identify) and Pass 2 (Extract) run as separate LLM calls. This avoids the "lost in the middle" problem — each call processes either detection OR extraction, not both. Per masterplan section 4.4 and the FinanceBench/DocFinQA research.

### Section splitting at 8K tokens
MD&A sections can be 20K+ tokens. Splitting at paragraph boundaries keeps each LLM call focused. Suffixed section_keys (`mda_part1`, `mda_part2`) accommodate the UNIQUE constraint on `(source_document_id, section_key)`.

### fact_key collision avoidance
LLM-extracted facts use section-prefixed dot-notation keys (`mda.revenue_growth`) while XBRL facts use flat keys (`revenue`). The UNIQUE constraint on `(source_document_id, fact_key, fiscal_period)` catches any accidental collision at the DB level.

### Confidence scale
LLM facts: 0.80-0.90. XBRL facts: 1.0. The gap is deliberate — when both exist for the same metric, XBRL is preferred. The +0.05 bonus for exact source_quote match rewards verifiable extractions.

### Opt-in via `--tier2`
Tier 2 adds 30-75 seconds per ticker (LLM calls). Making it opt-in avoids slowing down the default `./run.sh extract` and `./run.sh analyze` paths. Users run Tier 2 explicitly when they want narrative evidence.

### Deactivate-then-insert pattern
Before inserting new facts, `deactivate_facts_for_document(doc_id)` marks all existing facts as `is_active=0`. This preserves assertion_evidence links for audit while ensuring queries return only the latest extraction. Matches the Phase 3 design intent.

---

## Test Strategy

### Unit tests: `tests/test_evidence_models.py`
- Valid model construction for ClaimList, ExtractionBatch, ExtractedFactModel
- Rejection of invalid data (missing source_quote, empty claim_text, invalid enum)
- JSON Schema generation matches expected structure
- FactType and FactUnit enum membership
- Round-trip: model_validate(model.model_dump()) == model

### Unit tests: `tests/test_sections.py`
- `_split_section()`: text below/at/above TOKEN_CAP
- Split at paragraph boundaries (not mid-sentence)
- `_estimate_tokens()`: chars/4 accuracy
- `_content_hash()`: determinism
- Section_key suffixing: `mda` → `mda_part1`, `mda_part2`
- SECTION_MAP covers all three form types (10-K, 20-F, 40-F)
- Amendment handling: `10-K/A` → same sections as `10-K`
- Mock filing objects (no network calls)

### Integration tests: `tests/test_llm_extract.py`
- Mock `subprocess.run` with canned JSON responses
- Pass 1 prompt construction: section text included, schema included
- Pass 2 prompt construction: claims included, section text included
- `_compute_char_offsets()`: exact match, fuzzy match, miss
- `_assign_confidence()`: quantitative vs narrative, with/without exact offset
- `_fact_to_db_dict()`: produces valid dicts for EvidenceDB.batch_insert_facts()
- Claim batching: 15 claims → 3 batches of 5
- Error handling: timeout, invalid JSON, empty response, partial success

### Verification (manual, 5 tickers)

```bash
./run.sh extract V INTU ODFL SYK TXN --tier2
```

Then:
1. Check `context/{TICKER}/evidence-10K-*.md` exists with facts per section
2. Compare XBRL revenue vs LLM-extracted `mda.revenue.*` — must agree within 5%
3. Verify source_quotes are verbatim substrings (spot-check 10 facts)
4. Check DB: `SELECT COUNT(*) FROM extracted_facts WHERE extraction_method='llm_structured'`

---

## Build Order

Each step is independently testable. Do not proceed to step N+1 until step N passes its tests.

| Step | File(s) | Test | Depends on |
|------|---------|------|------------|
| 1 | `src/evidence_models.py` | `tests/test_evidence_models.py` | Nothing |
| 2 | `prompts/evidence/identify-claims.md`, `extract-structured.md` | Read review | Nothing |
| 3 | `scripts/sec_edgar/sections.py` | `tests/test_sections.py` | edgartools |
| 4 | `scripts/sec_edgar/client.py` (add `fetch_filing_object`) | Manual: `fetch_filing_object("V")` returns TenK | Step 3 |
| 5 | `scripts/sec_edgar/llm_extract.py` | `tests/test_llm_extract.py` (mocked) | Steps 1, 2 |
| 6 | `scripts/sec_edgar/render_evidence.py` | Manual: render sample facts | Step 5 |
| 7 | `scripts/sec_edgar/__main__.py`, `__init__.py` (wiring) | `./run.sh extract V --tier2` end-to-end | Steps 3-6 |
| 8 | 5-ticker verification | Revenue cross-check, quote validation | Step 7 |

---

## What This Does Not Include

- **Verification pass (Pass 3):** The masterplan's "different prompt, fresh context" verification is Phase 4, not Phase 2. Phase 2 extracts; Phase 4 verifies.
- **Arithmetic engine:** Sandboxed Python math for derived metrics is Phase 4.
- **Prompt updates to umbrella agents:** Teaching analysis agents to prefer SEC evidence is Phase 5.
- **Semantic diffing:** Cross-period change detection is Phase 6.
- **Dashboard evidence tab:** Phase 7.
- **Auto-Tier2 in analyze flow:** `cmd_analyze()` continues to use Tier 1 only. Users opt in.

---

## New Dependencies

None. `edgartools>=3.0` and `pydantic>=2.0` are already in `requirements.txt`. `difflib`, `hashlib`, `subprocess`, `json` are stdlib.

---

## Estimated Total

~1,050 LOC new code + ~180 lines of prompts + ~470 LOC tests = **~1,700 LOC** across 9 new files + 3 modified files.
