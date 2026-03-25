# Phase 4 Spec Review: Post-Analysis Verification

**Reviewer:** Claude Opus 4.6
**Date:** 2026-03-21
**Status:** Pre-implementation spec review (no code exists yet)

## Context

Phases 1-3 of the filings model are implemented: EDGAR fetch + XBRL extraction, LLM narrative extraction, and SQLite evidence DB. Phase 4 adds post-analysis verification — decomposing report claims into assertions, matching them against SEC filing evidence, and scoring their grounding. A detailed implementation spec exists (`phase4-implementation.md`, 718 lines) and a review prompt (`phase4-implementation-review-prompt.md`), but no code has been written. This review examines the spec itself before building.

**Files reviewed:**
- `research-material/filings-model/phase4/phase4-implementation.md` (718 lines — full spec)
- `research-material/filings-model/phase4/phase4-implementation-review-prompt.md` (268 lines — review checklist)
- `db/evidence_schema.sql` (155 lines — 8 tables)
- `src/evidence.py` (813 lines — EvidenceDB, 45 methods)
- `src/evidence_models.py` (157 lines — Phase 2 Pydantic models)
- `scripts/sec_edgar/llm_extract.py` (369 lines — Phase 2 LLM pattern)
- `runs/week12_16.03/reports/SYK/04-business-economics.md` (reference report format)
- `src/database.py` (605 lines — Database class, migrate())
- `run.sh` (dispatch table pattern)

---

## Part 1: Plan vs Infrastructure (Spec Readiness)

### 1.1 Pydantic Models

| Item | Verdict | Finding |
|------|---------|---------|
| `DecomposedAssertion` | **SPEC GAP** | Defines `source_location` field ("key_findings:3", "detailed_analysis:para2"), but the `assertions` table has no `source_location` column. `_assertion_to_db_dict()` silently drops it. LLM tokens wasted extracting a field that's thrown away. |
| `AssertionBatch` | **SPEC READY** | Clean. `total_assertions` redundant with `len(assertions)` but harmless for LLM validation. |
| `VerificationResult` | **SPEC READY** | Fields map to `assertion_evidence` table. `matched_fact_key` bridges LLM output to DB lookup. |
| `VerificationBatch` | **SPEC READY** | `skipped_assertions` provides explicit failure tracking. |
| Schema registry (`get_verification_schema`) | **SPEC READY** | Follows existing `get_extraction_schema()` pattern in `evidence_models.py:142-151`. |

### 1.2 Claim Decomposer

| Item | Verdict | Finding |
|------|---------|---------|
| Key Findings regex `\| \d+ \| (.*?) \| (\d) \|` | **SPEC GAP** | Doesn't mention skipping header row (`\| # \| Finding \|`) or separator (`\|---\|`). Will produce parse errors or garbage assertions if not handled. Easy fix but must be explicit. |
| Red Flags extraction | **SPEC READY** | Confirmed against SYK/04: plain `- ` bullets under `## Red Flags`. |
| LLM prose decomposition | **SPEC READY** | Matches `_claude_extract()` pattern from `llm_extract.py:62-68`. |
| Type inference heuristics | **SPEC READY** | number -> quantitative, "vs" -> comparative, "driven by" -> causal, else -> qualitative. Reasonable for mechanical path. |
| `requires_arithmetic` flagging | **SPEC READY** | Clear rule: only derived metrics (ROIC, margins, ratios), NOT raw numbers. |
| Deduplication | **SPEC GAP** | "Keep the more specific one" has no concrete algorithm. How is specificity measured? |
| Output -> `batch_insert_assertions()` | **SPEC READY** | `_assertion_to_db_dict()` produces exactly the 7 keys the INSERT expects (verified against `evidence.py:428-430`). |

### 1.3 Fact Checker

| Item | Verdict | Finding |
|------|---------|---------|
| Numeric cross-check before LLM | **SPEC READY** | Clear tolerance thresholds. Saves ~30% of LLM calls. |
| Candidate fact retrieval | **SPEC READY** | Cap at 20 facts per assertion. Sort by confidence descending. |
| Anti-sycophancy subprocess isolation | **SPEC READY** | Fresh `claude --print` call, zero shared history. |
| Batch size of 5 | **SPEC READY** | Reasonable token budget. |
| `unverifiable` handling | **SPEC CONFLICT** | `_mark_all_unverifiable()` referenced in orchestrator (spec line 408) but never defined. `assertion_evidence.extracted_fact_id` is `NOT NULL` — can't create evidence links with no fact. See Required Change #2. |

### 1.4 Arithmetic Engine

| Item | Verdict | Finding |
|------|---------|---------|
| AST whitelist | **SPEC CONFLICT** | `ast.Attribute` absent from `ALLOWED_NODES`, but `math` module added to namespace. `math.sqrt(x)` requires `ast.Attribute` -> rejected at validation. The math module is dead code. See Required Change #3. |
| `validate_formula()` | **SPEC READY** | Correctly rejects imports, exec, eval, open, assignments. |
| SIGALRM timeout | **SPEC READY** | Works on macOS (this project's target). Not portable to Windows but irrelevant here. |
| `verify_arithmetic_assertion()` | **SPEC GAP** | Calls LLM to identify formula + operands, but no prompt template specified. `decompose-claims.md` and `verify-claims.md` exist — no `identify-formula.md`. See Required Change #4. |

### 1.5 CLI Orchestrator

| Item | Verdict | Finding |
|------|---------|---------|
| Main flow | **SPEC CONFLICT** | Lines 424-435 access `summary["verified_assertions"]` and `summary["verification_coverage"]`. But `get_evidence_summary_for_ticker()` (`evidence.py:552-573`) returns `verified_count` and `total_assertions` — no `verification_coverage` key. These keys belong to the *different* method `get_ticker_evidence_summary()` (`evidence.py:775-812`). See Required Change #1. |
| Idempotent re-runs | **SPEC READY** | `delete_assertions_for_report()` + ON DELETE CASCADE on `assertion_evidence`. |
| `Database()` context manager | **SPEC READY** | Matches existing pattern. |
| `run.sh` integration | **SPEC READY** | Clean `cmd_verify()` + dispatch entry. |
| `_find_latest_report()` | **SPEC GAP** | Referenced but not specified. Needs to scan `runs/week*/reports/{TICKER}/`, sort by week. |

### 1.6 Prompts

| Item | Verdict | Finding |
|------|---------|---------|
| `decompose-claims.md` | **SPEC READY** | Template placeholders, clear rules, JSON-only output. |
| `verify-claims.md` | **SPEC READY** | Strong anti-sycophancy: "YOUR JOB IS TO FIND ERRORS." Raw evidence, no interpretation. |
| Pass C prompt | **MISSING** | No `identify-formula.md` for arithmetic assertion verification. |

### 1.7 Tests

| Item | Verdict | Finding |
|------|---------|---------|
| Test strategy | **SPEC READY** | Mocked LLM, tolerance levels, AST validation, empty handling. |
| Missing paths | **SPEC GAP** | No test for empty `extracted_facts` (no-evidence path). No test for stale assertions from prior `report_path`. |

---

## Part 2: Anti-Sycophancy Integrity

**Verdict: SPEC READY** — this is the strongest part of the design.

- Pass B uses `claude --print` subprocess (fresh context, zero shared history)
- Verify-claims prompt does NOT reference extraction results
- Verifier receives raw evidence (fact_key, fact_value, source_quote) — not the extraction's interpretation
- Contradictions stored faithfully as `relationship='contradicts'`
- No filtering or rationalization in orchestrator

---

## Part 3: Arithmetic Sandbox Safety

**Verdict: SPEC CONFLICT** — fixable, see Required Change #3.

- AST whitelist is sound in principle (no imports, no attribute access, no assignments)
- But the math module contradiction means `sqrt`/`log` can't actually be called
- `ast.Subscript` absent — correct, since inputs are flat namespace names
- `__builtins__` restriction is solid
- SIGALRM timeout works on macOS

---

## Part 4: Risk Resolution

| # | Risk | Verdict | Finding |
|---|------|---------|---------|
| R1 | Key Findings regex fails on non-standard formatting | **ISSUE (MEDIUM)** | Header/separator rows not explicitly skipped. |
| R2 | `requires_arithmetic` over-flags | **PASS** | Clear rule excludes raw numbers. |
| R3 | Candidate facts too broad | **PASS** | 20-fact cap per assertion. |
| R4 | Candidate facts too narrow | **NEEDS VERIFICATION** | `fact_key` prefix matching depends on Phase 2 naming convention. Not enumerated in spec. |
| R5 | Numeric extraction edge formats | **ISSUE (MEDIUM)** | Actual assertions use `~11%`, `63-64%` (ranges), `$4.3B (17.1% margin)` (parenthetical). Spec regex patterns don't cover these. |
| R6 | Sycophantic verifier | **PASS** | Strong prompt + subprocess isolation. |
| R7 | SIGALRM on macOS | **PASS** | POSIX works. macOS-only project. |
| R8 | Deduplication drops distinct claims | **ISSUE (MEDIUM)** | No algorithm specified. |
| R9 | Summary method key mismatch | **ISSUE (CRITICAL)** | Wrong method or wrong keys in orchestrator. |
| R10 | Empty extracted_facts | **ISSUE (HIGH)** | `_mark_all_unverifiable()` undefined. NOT NULL FK prevents naive approach. |
| R11 | Concurrent runs | **PASS** | SQLite WAL + single user. Low risk. |
| R12 | Missing section files | **PASS** | Decomposer iterates UMBRELLA_FILES; should skip missing. |
| R13 | Stale verification | **PASS** | By design — opt-in via `./run.sh verify`. |
| R14 | `match_score` semantics | **ISSUE (LOW)** | "contradicts" at 0.30 is confusing. Score means confidence in the relationship, not match quality. |
| R15 | LLM formula validity | **ISSUE (MEDIUM)** | No Pass C prompt specified. |

---

## Part 5: Cost Estimate

**Verdict: Underestimated ~2x.**

| Pass | Calls/ticker | Reasoning |
|------|-------------|-----------|
| A (Decompose) | 8 | One per umbrella section |
| B (Verify) | 6-9 | 40-64 assertions / 5 per batch, minus ~30% skipped by numeric cross-check |
| C (Arithmetic) | 5-10 | One per `requires_arithmetic` assertion |
| **Total** | **19-27** | Spec claims "5-15" |

At 20-30 tickers: **$40-80/cycle**, not "$20-40." Still reasonable but should set accurate expectations.

---

## Verdict: NEEDS FIXES

The core architecture is sound — anti-sycophancy design, three-pass pipeline, subprocess isolation, and arithmetic sandbox are well-thought-out. But 2 critical issues and 2 high issues must be resolved in the spec before building. None require redesign.

---

## Required Changes Before Building

### CRITICAL

**1. Fix orchestrator summary method mismatch**
Spec lines 424-435 call `get_evidence_summary_for_ticker()` but access keys (`verified_assertions`, `verification_coverage`) that belong to the different method `get_ticker_evidence_summary()`. Fix: either switch to `get_ticker_evidence_summary()`, or use the correct keys from `get_evidence_summary_for_ticker()` (`verified_count`, `total_assertions`) and compute coverage manually.

- `evidence.py:552` — `get_evidence_summary_for_ticker()` returns: `{total_assertions, verified_count, supported_count, contradicted_count, partial_count, unverifiable_count}`
- `evidence.py:775` — `get_ticker_evidence_summary()` returns: `{ticker, source_document_count, total_facts, total_assertions, verified_assertions, verification_coverage, latest_verification_score, high_significance_diffs}`

**2. Resolve `unverifiable` assertions + NOT NULL FK**
`assertion_evidence.extracted_fact_id` is `NOT NULL`. For assertions with no matching evidence, the correct approach: do NOT create `assertion_evidence` rows. The LEFT JOIN in `get_evidence_summary_for_ticker()` already handles this — assertions with no links are naturally uncounted in `verified_count`. Remove the `_mark_all_unverifiable()` reference from the orchestrator. When no facts exist for a ticker, simply skip Pass B/C and let all assertions remain unlinked.

### HIGH

**3. Fix arithmetic engine `math` module contradiction**
`ast.Attribute` is absent from `ALLOWED_NODES`, making `math.sqrt()` fail at AST validation. Don't add `ast.Attribute` (opens `__class__.__bases__` attacks). Instead inject math functions directly into `SAFE_BUILTINS`:
```python
SAFE_BUILTINS = {
    "abs": abs, "min": min, "max": max, "round": round,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "pi": math.pi, "e": math.e,
    "True": True, "False": False, "None": None,
}
```
Remove `math` from the execution namespace entirely.

**4. Add Pass C arithmetic prompt**
Create `prompts/evidence/identify-formula.md`. Must instruct LLM to output:
```json
{"formula": "nopat / ((ic_curr + ic_prev) / 2)", "inputs": {"nopat": "fact_key_here", ...}, "expected_result": 0.10, "result_unit": "ratio"}
```
Without this, `verify_arithmetic_assertion()` has no defined LLM interaction.

### MEDIUM

**5. Decide on `source_location` field**
Either add `source_location TEXT` column to `assertions` table (requires v3->v4 migration note) and include it in `_assertion_to_db_dict()`, or remove it from `DecomposedAssertion` and the decompose prompt. Currently extracted and thrown away.

**6. Define deduplication algorithm**
Replace "keep the more specific one" with: prefer the assertion containing a numeric value; if tied, prefer longer text; if both from mechanical path (different sections), keep both.

**7. Add Key Findings regex guard**
Explicitly state: skip rows where first column is not a digit (`| # |`, `|---|`). The regex `^\| (\d+) \|` naturally handles this but the spec should mention it.

**8. Update cost estimate**
19-27 LLM calls per ticker, $40-80 per 20-30 ticker cycle.

**9. Specify `_find_latest_report()` logic**
Scan `runs/week*/reports/{TICKER}/` directories, sort by week number descending, return first containing at least one section `.md` file.

**10. Filter assertions by `report_path` in orchestrator**
After inserting, call `get_assertions_for_ticker(ticker)` — but this returns ALL assertions for the ticker across all report paths. If a prior week's assertions weren't cleaned up, they'd be re-verified. Add `report_path` filter or ensure the delete-before-insert covers all paths.

---

## Optional Improvements

1. Add `signal.alarm(0)` in `finally` block to reset timer on both success and error paths
2. Document SIGALRM is POSIX-only in arithmetic_engine docstring
3. Clarify `match_score` semantics: "confidence in the assessed relationship," not "match quality"
4. Add `partial_count` to `verification_runs` table (currently lost — `get_evidence_summary_for_ticker()` returns it but the run dict doesn't store it)
5. Handle numeric edge formats in assertion text: `~11%`, `63-64%` ranges, `$4.3B (17.1% margin)` parenthetical values
