# Phase 4 Implementation Manual — Post-Analysis Verification

## Context

Phases 1-3 are complete. Phase 1 fetches SEC filings and extracts XBRL financial data. Phase 2 extracts narrative facts from 10-K sections (MD&A, Risk Factors, Business) via two-pass LLM pipeline. Phase 3 stores everything in 8 SQLite tables. The analysis pipeline (umbrella agents 01-08 + assembler) produces `FINAL-REPORT.md` and `FINAL-REPORT.json` for each ticker.

**The gap:** Nothing currently verifies whether claims in the analysis reports are grounded in actual filing evidence. An agent can write "Revenue grew 15%" and there's no check against the SEC filing. Phase 4 closes this gap.

**What Phase 4 does:**
1. Decomposes completed analysis reports (sections 01-08) into atomic, verifiable assertions
2. Matches each assertion against extracted facts in the evidence DB
3. Runs a fresh-context LLM verification pass (anti-sycophancy)
4. Executes deterministic arithmetic for quantitative claims
5. Records the full audit trail and produces a verification score

**Depends on:** Phase 1 (XBRL facts in `context/{TICKER}/edgar-10k.md`), Phase 2 (LLM narrative facts in `extracted_facts` table), Phase 3 (all 8 evidence tables, EvidenceDB class). **Breaking changes:** None. Opt-in via `./run.sh verify TICKER`.

---

## Architecture

**Input:** Completed umbrella sections (01-08.md) in `runs/{CURRENT_WEEK}/reports/{TICKER}/`. Each section contains a Key Findings table, Detailed Analysis prose, Signal Summary, Red Flags, and Score.

**Three-pass verification pipeline:**

1. **Pass A (Decompose):** Parse report sections into atomic assertions. Purely mechanical — regex on Key Findings tables + LLM on prose paragraphs. One LLM call per section. Output: `assertions` table rows.

2. **Pass B (Verify):** For each assertion, find matching extracted facts and score the match. **Critical anti-sycophancy design:** this runs in a fresh LLM context with a different prompt than extraction. The verifier is explicitly instructed to flag contradictions. One LLM call per batch of 5 assertions.

3. **Pass C (Compute):** For assertions marked `requires_arithmetic=1`, the LLM identifies the formula and input operands. Python executes the formula in a sandboxed environment. The LLM never does arithmetic.

**LLM invocation:** `claude --print --output-format json` subprocess calls, matching the project's existing pattern. JSON Schema in prompt text + Pydantic v2 validation on the Python side.

**Cost estimate:** ~5-15 LLM calls per ticker (8 sections for Pass A + 5-10 batches for Pass B). At 20-30 tickers: **$20-40/cycle**.

---

## Files

### New files

| File | LOC | Purpose |
|------|-----|---------|
| `scripts/verify_claims.py` | ~300 | CLI entry point + orchestrator |
| `scripts/sec_edgar/claim_decomposer.py` | ~250 | Pass A: parse reports into assertions |
| `scripts/sec_edgar/fact_checker.py` | ~300 | Pass B: verify assertions against evidence |
| `scripts/sec_edgar/arithmetic_engine.py` | ~150 | Pass C: sandboxed formula execution |
| `src/evidence_models.py` | +80 | Add verification Pydantic models |
| `prompts/evidence/decompose-claims.md` | ~60 | Pass A prompt for prose decomposition |
| `prompts/evidence/verify-claims.md` | ~80 | Pass B prompt (anti-sycophancy) |
| `tests/test_claim_decomposer.py` | ~200 | Decomposition tests (mocked LLM) |
| `tests/test_fact_checker.py` | ~200 | Verification tests (mocked LLM) |
| `tests/test_arithmetic_engine.py` | ~150 | Sandbox safety tests |

### Modified files

| File | Change |
|------|--------|
| `src/evidence_models.py` | Add `DecomposedAssertion`, `AssertionBatch`, `VerificationResult`, `VerificationBatch` Pydantic models |
| `run.sh` | Add `cmd_verify()` function + dispatch entry |

### Unchanged files

| File | Why unchanged |
|------|---------------|
| `src/evidence.py` | All assertion/evidence/verification methods already exist (Phase 3) |
| `src/database.py` | Schema v3 already applied with all 8 tables |
| `db/evidence_schema.sql` | All tables already exist |
| `scripts/sec_edgar/llm_extract.py` | Phase 2 extraction unchanged |
| `prompts/assembler.md` | Not modified in Phase 4 (evidence_summary field is Phase 5 work) |

---

## File-by-File Specification

### 1. `src/evidence_models.py` — new models (append to existing file)

Add these models after the existing `ExtractionBatch` class:

```python
# ---------------------------------------------------------------------------
# Phase 4 models — claim decomposition and verification
# ---------------------------------------------------------------------------

class DecomposedAssertion(BaseModel):
    """A single verifiable assertion extracted from a report section."""
    assertion_text: str = Field(..., min_length=10,
        description="The atomic claim, independently understandable")
    assertion_type: str = Field(...,
        description="quantitative | qualitative | comparative | causal",
        pattern=r"^(quantitative|qualitative|comparative|causal)$")
    category: str = Field(...,
        description="finding | strength | risk | red_flag | trigger",
        pattern=r"^(finding|strength|risk|red_flag|trigger)$")
    requires_arithmetic: bool = Field(False,
        description="True if claim requires formula verification (derived metrics)")
    source_location: str = Field(...,
        description="Where in the section: 'key_findings:3' or 'detailed_analysis:para2'")


class AssertionBatch(BaseModel):
    """All assertions from a report section (Pass A output)."""
    umbrella_number: int
    section_title: str
    assertions: list[DecomposedAssertion]
    total_assertions: int


class VerificationResult(BaseModel):
    """Verification of one assertion against evidence (Pass B output)."""
    assertion_index: int = Field(..., description="Index into the batch being verified")
    relationship: str = Field(...,
        description="supports | contradicts | partial | unverifiable",
        pattern=r"^(supports|contradicts|partial|unverifiable)$")
    match_score: float = Field(..., ge=0.0, le=1.0,
        description="Confidence that the evidence supports/contradicts the assertion")
    matched_fact_key: Optional[str] = Field(None,
        description="fact_key of the best matching extracted_fact, or null")
    reasoning: str = Field(..., min_length=10,
        description="Brief explanation of why this relationship was assigned")
    numeric_expected: Optional[float] = Field(None,
        description="The number the assertion claims (if quantitative)")
    numeric_actual: Optional[float] = Field(None,
        description="The number the evidence shows (if quantitative)")


class VerificationBatch(BaseModel):
    """Verification results for a batch of assertions (Pass B output)."""
    results: list[VerificationResult]
    skipped_assertions: list[int] = Field(default_factory=list,
        description="Indices of assertions that could not be verified at all")
```

**Schema registry addition:**
```python
VERIFICATION_SCHEMAS: dict[str, type[BaseModel]] = {
    "decompose": AssertionBatch,
    "verify": VerificationBatch,
}

def get_verification_schema(schema_key: str) -> dict:
    model = VERIFICATION_SCHEMAS.get(schema_key, VerificationBatch)
    return model.model_json_schema()
```

---

### 2. `scripts/sec_edgar/claim_decomposer.py`

Parse umbrella sections 01-08 into atomic assertions. Two extraction paths: mechanical (Key Findings table) and LLM (Detailed Analysis prose).

```python
"""
Claim decomposer — extract verifiable assertions from analysis report sections.

Two extraction paths:
1. Mechanical: regex-parse the Key Findings table (always present, structured)
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
PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "decompose-claims.md"

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
```

**Key functions:**

`decompose_section(section_text: str, umbrella_number: int, ticker: str) -> list[dict]`
- Calls `_parse_key_findings(section_text, umbrella_number)` for mechanical extraction
- Calls `_decompose_prose(section_text, umbrella_number, ticker)` for LLM extraction
- Deduplicates (same assertion from both paths → keep the more specific one)
- Returns list of dicts ready for `EvidenceDB.batch_insert_assertions()`

`_parse_key_findings(section_text: str, umbrella_number: int) -> list[dict]`
- Regex for markdown table rows: `| \d+ | (.*?) | (\d) |`
- Each finding → one assertion with `category="finding"`, `assertion_type` inferred (contains a number → "quantitative", contains "vs"/"compared" → "comparative", contains "driven by"/"due to" → "causal", else → "qualitative")
- `requires_arithmetic=True` if finding mentions derived metrics (ROIC, FCF conversion, margins, ratios)

`_parse_red_flags(section_text: str, umbrella_number: int) -> list[dict]`
- Regex for `## Red Flags` section, extract bullet points
- Each → assertion with `category="red_flag"`

`_decompose_prose(section_text: str, umbrella_number: int, ticker: str) -> list[dict]`
- Uses `claude --print --output-format json` with `prompts/evidence/decompose-claims.md`
- Extracts Detailed Analysis paragraphs only (skip Key Findings, Signal Summary, Score)
- Returns `AssertionBatch.assertions` validated through Pydantic
- Max 15 assertions per section (prioritize quantitative > comparative > causal > qualitative)

`decompose_report(report_dir: Path, ticker: str) -> list[dict]`
- Reads sections 01-08 from `report_dir`
- Calls `decompose_section()` for each
- Returns all assertions with `report_path` set to `str(report_dir / "FINAL-REPORT.md")`

**Assertion-to-DB dict conversion:**
```python
def _assertion_to_db_dict(assertion, umbrella_number: int, ticker: str, report_path: str) -> dict:
    return {
        "ticker": ticker,
        "report_path": report_path,
        "umbrella_number": umbrella_number,
        "assertion_text": assertion.assertion_text,
        "assertion_type": assertion.assertion_type,
        "category": assertion.category,
        "requires_arithmetic": 1 if assertion.requires_arithmetic else 0,
    }
```

---

### 3. `scripts/sec_edgar/fact_checker.py`

Verify assertions against extracted facts. Anti-sycophancy: runs in fresh context with a different prompt than extraction.

```python
"""
Fact checker — verify report assertions against extracted evidence.

Anti-sycophancy design: verification runs in fresh LLM context with a
prompt that explicitly encourages flagging contradictions.

Phase 4 of the evidence extraction masterplan.
"""
```

**Key functions:**

`verify_assertions(assertions: list[dict], ticker: str, quiet: bool = False) -> list[dict]`
- Main entry point. For each batch of 5 assertions:
  1. Retrieve candidate facts from DB (`get_facts_for_ticker` with matching `fact_type`/`fact_key` patterns)
  2. Build verification prompt with assertion text + candidate facts (fact_key, fact_value, source_quote)
  3. Call `claude --print --output-format json` with `prompts/evidence/verify-claims.md`
  4. Validate response via `VerificationBatch.model_validate()`
  5. For each result, find the matching `extracted_fact_id` from `matched_fact_key`
  6. Return list of dicts ready for `EvidenceDB.insert_assertion_evidence()`

`_build_candidate_facts(assertion: dict, all_facts: list[dict]) -> list[dict]`
- For quantitative assertions: filter facts where `fact_value_numeric is not None`
- For specific metrics (revenue, ROIC, margins): match by `fact_key` prefix
- Include both XBRL (`extraction_method='xbrl'`) and LLM facts
- Cap at 20 candidate facts per assertion to keep prompt within token budget
- Sort by confidence descending (prefer XBRL confidence=1.0 over LLM confidence=0.85)

`_evidence_to_db_dict(result: VerificationResult, assertion_id: int, fact_id: int | None, method: str) -> dict`
- Converts Pydantic model to dict for `insert_assertion_evidence()`
- Sets `verification_method` based on how the match was made:
  - `"llm_semantic"` — LLM determined the relationship
  - `"numeric_exact"` — assertion and fact numeric values match within 2%
  - `"numeric_mismatch"` — assertion and fact disagree by >5%
  - `"no_evidence"` — no candidate facts found

**Numeric cross-check (mechanical, no LLM):**

```python
def _numeric_cross_check(assertion_text: str, fact_value_numeric: float) -> tuple[str, float]:
    """Extract number from assertion text, compare to fact value.
    Returns (relationship, match_score)."""
    # Extract numbers from assertion: regex for $X.XB, X.X%, X.Xx patterns
    # Compare within tolerance:
    #   - Within 2%: ("supports", 0.95)
    #   - Within 5%: ("supports", 0.85)
    #   - Within 10%: ("partial", 0.70)
    #   - Beyond 10%: ("contradicts", 0.30)
```

This runs BEFORE the LLM verification call. If the numeric cross-check produces a definitive result (exact match or clear contradiction), skip the LLM call for that assertion to save cost.

---

### 4. `scripts/sec_edgar/arithmetic_engine.py`

Sandboxed Python arithmetic execution. LLM identifies formula and operands, Python executes.

```python
"""
Arithmetic engine — deterministic formula execution in sandboxed environment.

Rule: LLM writes the formula string + identifies input facts.
      Python executes with ast.parse() whitelist + restricted builtins.
      LLM never does arithmetic.

Phase 4 of the evidence extraction masterplan.
"""

import ast
import logging
import math
import signal

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 5

# AST node whitelist — only arithmetic operations allowed
ALLOWED_NODES = {
    ast.Module, ast.Expr, ast.Expression,
    ast.BinOp, ast.UnaryOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd,
    ast.Constant,  # numbers, strings (for dict keys)
    ast.Name, ast.Load,
    ast.Call,  # only whitelisted functions
}

ALLOWED_FUNCTIONS = {"abs", "min", "max", "round"}

SAFE_BUILTINS = {
    "abs": abs, "min": min, "max": max, "round": round,
    "True": True, "False": False, "None": None,
}
```

**Key functions:**

`validate_formula(formula: str) -> bool`
- Parse with `ast.parse(formula, mode='eval')`
- Walk AST: every node must be in `ALLOWED_NODES`
- For `ast.Call` nodes: function name must be in `ALLOWED_FUNCTIONS`
- Return True if safe, False if any disallowed node found

`execute_formula(formula: str, inputs: dict[str, float]) -> float`
- Validate formula first
- Build namespace: `SAFE_BUILTINS` + `inputs` dict + `math` module (pi, e, sqrt, log)
- Execute with timeout: `signal.alarm(TIMEOUT_SECONDS)`
- Return result as float
- Raise `ArithmeticSandboxError` on validation failure, timeout, or execution error

`verify_arithmetic_assertion(assertion_text: str, candidate_facts: list[dict], ticker: str) -> dict`
- Uses LLM to identify formula and map operands to fact IDs
- Calls `execute_formula()` with fact values as inputs
- Compares result to claimed value in assertion
- Returns computation_cache dict: `{ticker, computation_key, formula, inputs_json, result_value, result_unit, computed_at}`

**Sandbox safety layers:**
1. AST node whitelist (no imports, no attribute access, no assignments)
2. Restricted `__builtins__` (no `exec`, `eval`, `open`, `__import__`)
3. 5-second timeout via `signal.SIGALRM`
4. Float result only — no side effects

---

### 5. `scripts/verify_claims.py`

CLI entry point. Orchestrates the full verification pipeline.

```python
"""
CLI entry point for Phase 4 post-analysis verification.

Usage:
    python3 scripts/verify_claims.py TICKER
    python3 scripts/verify_claims.py TICKER --report-dir runs/week12_16.03/reports/SYK
    python3 scripts/verify_claims.py TICKER --quiet
"""
```

**Main flow:**

```python
def verify_ticker(ticker: str, report_dir: Path = None, quiet: bool = False) -> dict:
    """Run full verification pipeline for a ticker. Returns verification summary."""

    # 1. Locate report
    if report_dir is None:
        report_dir = _find_latest_report(ticker)

    # 2. Decompose: extract assertions from sections 01-08
    assertions = decompose_report(report_dir, ticker)
    if not assertions:
        return {"error": "No assertions extracted"}

    # 3. Store assertions in DB
    with Database() as db:
        db.migrate()
        ev = EvidenceDB(db)

        # Clear previous assertions for this report (idempotent re-runs)
        report_path = str(report_dir / "FINAL-REPORT.md")
        ev.delete_assertions_for_report(report_path)

        ev.batch_insert_assertions(assertions)
        stored = ev.get_assertions_for_ticker(ticker)

        # 4. Get all extracted facts for this ticker
        all_facts = ev.get_facts_for_ticker(ticker, limit=1000)

        if not all_facts:
            # No evidence extracted — mark all as unverifiable
            _mark_all_unverifiable(ev, stored)
        else:
            # 5. Verify assertions against evidence
            evidence_links = verify_assertions(stored, ticker, quiet=quiet)
            for link in evidence_links:
                ev.insert_assertion_evidence(link)

            # 6. Arithmetic verification for flagged assertions
            arithmetic_assertions = [a for a in stored if a.get("requires_arithmetic")]
            for a in arithmetic_assertions:
                result = verify_arithmetic_assertion(a["assertion_text"], all_facts, ticker)
                if result:
                    ev.upsert_computation(result)

        # 7. Compute and store verification run
        run_id = f"verify-{ticker}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        summary = ev.get_evidence_summary_for_ticker(ticker)

        ev.insert_verification_run({
            "run_id": run_id,
            "ticker": ticker,
            "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_assertions": summary["total_assertions"],
            "verified_count": summary["verified_assertions"],
            "supported_count": summary["supported_count"],
            "contradicted_count": summary["contradicted_count"],
            "unverifiable_count": summary.get("unverifiable_count", 0),
            "overall_score": summary["verification_coverage"],
            "run_metadata_json": json.dumps({
                "report_dir": str(report_dir),
                "fact_count": len(all_facts),
                "phase": 4,
            }),
        })

        # 8. Print summary
        if not quiet:
            _print_summary(ticker, summary, stored)

        return summary
```

**CLI:**
```python
parser.add_argument("ticker", help="Ticker symbol")
parser.add_argument("--report-dir", help="Override report directory")
parser.add_argument("--quiet", action="store_true")
```

**run.sh integration:**
```bash
cmd_verify() {
    local ticker="${1:-}"
    if [ -z "$ticker" ]; then
        echo "ERROR: TICKER required. Usage: $0 verify TICKER"
        exit 1
    fi
    shift
    python3 "$SCRIPT_DIR/scripts/verify_claims.py" "$ticker" "$@"
}

# In dispatch table:
verify)    cmd_verify "$@" ;;
```

**Summary output format (stdout):**
```
Verification: SYK (2026-03-20)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Assertions:    42
Verified:      38 (90.5%)
  Supported:   35
  Partial:      2
  Contradicted: 1
Unverifiable:   4

Contradictions:
  [U4] "ROIC of 12.2%" — evidence shows 10.0% (match_score: 0.25)

Overall score: 0.83
```

---

### 6. `prompts/evidence/decompose-claims.md`

```markdown
# Evidence Verification — Pass A: Decompose Report Claims

You are extracting verifiable assertions from an investment analysis
report section. Each assertion must be atomic, independently testable,
and traceable to the report text.

**Umbrella Section:** {UMBRELLA_NUMBER} — {SECTION_TITLE}
**Ticker:** {TICKER}

## What to extract

For each paragraph in the Detailed Analysis section below, identify every
factual claim that could be verified against a company's SEC filing.

- Quantitative claims: specific numbers, percentages, dollar amounts, ratios
- Comparative claims: "higher than", "grew from X to Y", "outpaced"
- Causal claims: "driven by", "due to", "resulting from"
- Qualitative claims: business model facts, competitive position statements

## What NOT to extract

- Opinions or subjective judgments ("strong", "impressive", "concerning")
- Forward-looking speculation without specific numbers
- Restatements of the same fact in different words
- Generic industry statements not specific to the company
- Score justifications (the "Score: X/10" line)

## Rules

1. Maximum 15 assertions per section.
2. Set requires_arithmetic=true ONLY for derived metrics: ROIC, FCF conversion
   ratios, margin calculations, growth rates computed from two data points.
   Raw numbers from the filing (revenue, net income) do NOT require arithmetic.
3. category must be one of: finding, strength, risk, red_flag, trigger
4. source_location format: "key_findings:N" for table rows,
   "detailed_analysis:paraN" for prose paragraphs,
   "red_flags:N" for red flag bullets, "signal_summary:bull|bear" for signals

## Output

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```

---

REPORT SECTION TEXT:
```

---

### 7. `prompts/evidence/verify-claims.md`

**Critical: anti-sycophancy design.** This prompt runs in fresh context and explicitly encourages contradiction detection.

```markdown
# Evidence Verification — Pass B: Verify Claims Against Evidence

You are an independent fact-checker verifying investment report claims
against SEC filing evidence. You have NO access to the original analysis
and NO obligation to agree with it.

**YOUR JOB IS TO FIND ERRORS.** If the evidence contradicts a claim,
say so clearly. Do not rationalize discrepancies. Do not assume the
report is correct. The portfolio depends on honest verification.

**Ticker:** {TICKER}

## Assertions to verify

{ASSERTIONS}

## Available evidence (extracted from SEC filings)

{EVIDENCE}

## Verification rules

### Relationship assignment
- **supports**: Evidence directly confirms the assertion. Numbers match
  within 2% tolerance. Narrative facts align with the claim.
- **partial**: Evidence partially confirms but with caveats. Numbers
  within 5-10% tolerance. Narrative support is tangential.
- **contradicts**: Evidence directly refutes the assertion. Numbers
  differ by >10%. Narrative evidence says the opposite.
- **unverifiable**: No relevant evidence found. Do NOT force a match.

### Numeric matching
- Extract the number from the assertion and from the evidence fact_value_numeric
- Compare: within 2% = supports (0.95), within 5% = supports (0.85),
  within 10% = partial (0.70), beyond 10% = contradicts (0.30)
- WATCH FOR: unit mismatches (millions vs billions), different fiscal periods,
  different line items (revenue vs net revenue vs segment revenue)

### Narrative matching
- The evidence source_quote must be relevant to the assertion topic
- Score based on specificity: direct quote support (0.90), same topic (0.75),
  tangential (0.55), no relevance (0.20)

### Anti-sycophancy checks
- If a claim says "grew 15%" but evidence shows 11%, that is a CONTRADICTION
- If a claim cites a specific dollar amount that doesn't appear in evidence, mark UNVERIFIABLE
- If a claim makes a causal attribution ("driven by X") with no evidence for the causal link, mark PARTIAL at best
- Prefer honest "unverifiable" over fabricated "supports"

## Output

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```

---

ASSERTION DETAILS AND EVIDENCE:
```

---

## Key Design Decisions

### Fresh-context verification (anti-sycophancy)
Pass B runs as a separate `claude --print` subprocess call with zero shared conversation history from extraction. The prompt explicitly says "YOUR JOB IS TO FIND ERRORS" and "Do not assume the report is correct." This prevents the verification LLM from deferring to the extraction LLM's conclusions.

### Mechanical numeric cross-check before LLM
Quantitative assertions get a pure-Python numeric comparison first. If assertion says "$4.3B" and the evidence `fact_value_numeric` is `4300000000.0`, that's a deterministic match — no LLM needed. This saves ~30% of LLM calls and produces higher-confidence scores.

### Two-path decomposition (mechanical + LLM)
Key Findings tables are structured markdown — regex extraction is reliable and free. LLM is only used for the Detailed Analysis prose where claims are embedded in natural language. This keeps cost low and mechanical extraction at confidence=1.0.

### Arithmetic engine isolation
The LLM identifies WHAT to compute and WITH WHICH inputs. Python computes the result. This means arithmetic errors are Python bugs (reproducible, debuggable), not LLM hallucinations (non-deterministic).

### Idempotent re-runs
`delete_assertions_for_report(report_path)` clears previous assertions before re-inserting. This means `./run.sh verify TICKER` can be run repeatedly without accumulating duplicate assertions. The cascade delete on `assertion_evidence` cleans up evidence links too.

### No FINAL-REPORT.json modification in Phase 4
The `evidence_summary` field addition to `FINAL-REPORT.json` is Phase 5 work (prompt updates to assembler). Phase 4 stores verification results in the DB only. This keeps Phase 4 purely additive with zero risk to the existing report pipeline.

---

## Test Strategy

### Unit tests: `tests/test_claim_decomposer.py`
- `_parse_key_findings()`: regex on sample section text, correct count and types
- `_parse_red_flags()`: extract bullet points from sample section
- `_decompose_prose()`: mocked `subprocess.run` with canned JSON
- `decompose_report()`: mocked file reads + decompose, correct assertion count
- Assertion type inference: numbers → quantitative, "vs" → comparative, "driven by" → causal
- `requires_arithmetic` flagging: ROIC, margin calculations flagged, raw revenue not flagged
- Empty section handling: returns empty list, no crash

### Unit tests: `tests/test_fact_checker.py`
- `_numeric_cross_check()`: exact match, 2%, 5%, 10%, >10% tolerance levels
- `_build_candidate_facts()`: filters by type, caps at 20, sorts by confidence
- `verify_assertions()`: mocked LLM, full pipeline with 5-assertion batch
- `_evidence_to_db_dict()`: produces valid dicts for `insert_assertion_evidence()`
- Error handling: LLM timeout, invalid JSON, partial batch failure
- Anti-sycophancy: verifier output with contradictions is accepted (not suppressed)

### Unit tests: `tests/test_arithmetic_engine.py`
- `validate_formula()`: allowed ops pass, disallowed ops (import, exec, open) fail
- `execute_formula()`: basic arithmetic, ROIC calculation, margin calculation
- Timeout: infinite loop formula times out after 5 seconds
- Injection: `__import__('os')` rejected at AST validation
- Division by zero: raises ArithmeticSandboxError, not crashes Python
- Allowed functions: abs, min, max, round work; eval, exec rejected

### Verification (manual, 3 tickers)
```bash
./run.sh verify SYK
./run.sh verify V
./run.sh verify INTU
```

Then:
1. Check `assertions` table: 30-50 per ticker, correct umbrella_numbers
2. Check `assertion_evidence` table: >70% of assertions have at least one link
3. Check `verification_runs` table: overall_score 0.7-1.0
4. Spot-check 5 "supports" results: assertion and evidence should genuinely align
5. Spot-check any "contradicts" results: verify the contradiction is real
6. Check `computation_cache`: at least 3-5 entries for derived metrics

---

## Build Order

Each step independently testable. Do not proceed to N+1 until N passes.

| Step | File(s) | Test | Depends on |
|------|---------|------|------------|
| 1 | `src/evidence_models.py` (add models) | `tests/test_evidence_models.py` (extend) | Nothing |
| 2 | `prompts/evidence/decompose-claims.md`, `verify-claims.md` | Read review | Nothing |
| 3 | `scripts/sec_edgar/claim_decomposer.py` | `tests/test_claim_decomposer.py` | Step 1 |
| 4 | `scripts/sec_edgar/arithmetic_engine.py` | `tests/test_arithmetic_engine.py` | Nothing |
| 5 | `scripts/sec_edgar/fact_checker.py` | `tests/test_fact_checker.py` | Steps 1, 4 |
| 6 | `scripts/verify_claims.py` + `run.sh` | `./run.sh verify SYK` end-to-end | Steps 3, 5 |
| 7 | 3-ticker verification | Spot-check, DB queries | Step 6 |

---

## What This Does Not Include

- **evidence_summary field in FINAL-REPORT.json:** Phase 5 (prompt updates to assembler)
- **Prompt updates to umbrella agents:** Phase 5 (teaching agents to cite evidence)
- **Semantic diffing across report runs:** Phase 6
- **Dashboard evidence tab:** Phase 7
- **Evaluation harness:** Phase 8

---

## New Dependencies

None. All imports are stdlib (`ast`, `signal`, `re`, `json`, `subprocess`, `logging`) or already in `requirements.txt` (`pydantic>=2.0`).

---

## Estimated Total

~1,050 LOC new code + ~140 lines of prompts + ~550 LOC tests = **~1,740 LOC** across 10 new files + 2 modified files.
