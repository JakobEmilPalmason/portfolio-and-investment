# Phase 4 Implementation Review — Post-Analysis Verification

You are reviewing the Phase 4 implementation of a Buffett-style investment analysis system. Phase 4 adds post-analysis verification: decomposing report claims into assertions, matching them against SEC filing evidence, and scoring their grounding. This is the anti-sycophancy layer — it catches claims in analysis reports that aren't supported by primary source evidence.

## Your Inputs

Read these files in order before starting your review:

### 1. Design context (read first)
- `research-material/filings-model/masterplan.md` — Section 5 (Phase 4), Section 9 (anti-sycophancy), Section 6 (arithmetic engine)
- `research-material/filings-model/phase4/phase4-implementation.md` — The implementation manual this code was built from

### 2. Existing infrastructure (understand before reviewing new code)
- `db/evidence_schema.sql` — All 8 tables (focus on: `assertions`, `assertion_evidence`, `verification_runs`, `computation_cache`)
- `src/evidence.py` — EvidenceDB class. Focus on: assertion methods (insert, batch, get, delete), evidence link methods, verification run methods, `get_evidence_summary_for_ticker()`
- `src/evidence_models.py` — Existing Pydantic models (Phase 2) + new Phase 4 models (DecomposedAssertion, AssertionBatch, VerificationResult, VerificationBatch)

### 3. Phase 4 new code (the code you are reviewing)
- `scripts/sec_edgar/claim_decomposer.py` — Pass A: report → atomic assertions
- `scripts/sec_edgar/fact_checker.py` — Pass B: assertions × evidence → verification links
- `scripts/sec_edgar/arithmetic_engine.py` — Pass C: sandboxed formula execution
- `scripts/verify_claims.py` — CLI entry point + orchestrator
- `prompts/evidence/decompose-claims.md` — Pass A prompt
- `prompts/evidence/verify-claims.md` — Pass B prompt (anti-sycophancy)

### 4. Tests
- `tests/test_claim_decomposer.py`
- `tests/test_fact_checker.py`
- `tests/test_arithmetic_engine.py`

### 5. Integration points
- `run.sh` — Should have new `cmd_verify()` function and dispatch entry
- `scripts/sec_edgar/__init__.py` — Should export new functions
- A sample report to understand assertion sources: `runs/week12_16.03/reports/SYK/04-business-economics.md`

### 6. Existing patterns to match
- `scripts/sec_edgar/llm_extract.py` — Phase 2 LLM invocation pattern (`_claude_extract`, retry logic, JSON parsing)
- `scripts/sec_edgar/sections.py` — Phase 2 section parsing patterns
- `scripts/sec_edgar/__main__.py` — Phase 2 orchestration pattern (Database context manager, EvidenceDB usage)

---

## Part 1: Plan vs Implementation

For each item below, state **DONE**, **PARTIAL**, **MISSING**, or **DEVIATED** with a brief finding.

### 1.1 Pydantic models
- [ ] `DecomposedAssertion` model with all fields (assertion_text, assertion_type, category, requires_arithmetic, source_location)
- [ ] `AssertionBatch` model with umbrella_number, section_title, assertions list, total_assertions
- [ ] `VerificationResult` model with relationship, match_score, matched_fact_key, reasoning, numeric_expected, numeric_actual
- [ ] `VerificationBatch` model with results list and skipped_assertions
- [ ] Schema registry functions (`get_verification_schema`)
- [ ] All enum patterns match existing Phase 2 patterns (field names, validation rules)

### 1.2 Claim decomposer
- [ ] Key Findings table regex extraction (mechanical, no LLM)
- [ ] Red Flags bullet point extraction (mechanical)
- [ ] LLM prose decomposition via `claude --print --output-format json`
- [ ] Assertion type inference (quantitative/qualitative/comparative/causal)
- [ ] `requires_arithmetic` flagging — only derived metrics (ROIC, margins, ratios), NOT raw numbers
- [ ] Deduplication across mechanical + LLM paths
- [ ] `decompose_report()` reads all 8 section files
- [ ] Output dicts match `EvidenceDB.batch_insert_assertions()` expected schema

### 1.3 Fact checker
- [ ] Mechanical numeric cross-check BEFORE LLM call (save cost on obvious matches)
- [ ] Candidate fact retrieval with proper filtering (type, key prefix, confidence sort)
- [ ] LLM verification via `claude --print` in fresh subprocess (anti-sycophancy)
- [ ] Assertion batching (5 per LLM call)
- [ ] Relationship assignment with correct thresholds (supports/partial/contradicts/unverifiable)
- [ ] Evidence-to-DB dict conversion for `insert_assertion_evidence()`
- [ ] Handles missing evidence gracefully (no facts for ticker → all unverifiable)

### 1.4 Arithmetic engine
- [ ] AST node whitelist — only arithmetic ops + whitelisted functions
- [ ] `validate_formula()` rejects: imports, exec, eval, open, attribute access, assignments
- [ ] `execute_formula()` with restricted `__builtins__`
- [ ] 5-second timeout via `signal.SIGALRM`
- [ ] Returns float result only
- [ ] `verify_arithmetic_assertion()` orchestrates LLM formula identification + sandbox execution
- [ ] Results stored in `computation_cache` table

### 1.5 CLI orchestrator
- [ ] `scripts/verify_claims.py` with argparse (ticker, --report-dir, --quiet)
- [ ] Locates latest report directory automatically
- [ ] Idempotent: `delete_assertions_for_report()` before re-inserting
- [ ] Uses `Database()` context manager (NOT `db._conn.close()`)
- [ ] Stores verification_run with correct summary counts
- [ ] Prints human-readable summary to stdout
- [ ] `run.sh` has `cmd_verify()` function and dispatch entry

### 1.6 Prompts
- [ ] `decompose-claims.md` has template placeholders ({UMBRELLA_NUMBER}, {SECTION_TITLE}, {TICKER}, {JSON_SCHEMA})
- [ ] `verify-claims.md` has explicit anti-sycophancy language ("YOUR JOB IS TO FIND ERRORS")
- [ ] `verify-claims.md` has {ASSERTIONS}, {EVIDENCE}, {TICKER}, {JSON_SCHEMA} placeholders
- [ ] Both prompts instruct JSON-only output (no markdown fences)

### 1.7 Tests
- [ ] Decomposer: regex extraction, LLM mock, type inference, arithmetic flagging, empty handling
- [ ] Fact checker: numeric tolerance levels, candidate filtering, LLM mock, partial failure
- [ ] Arithmetic: AST whitelist, injection rejection, timeout, division by zero, allowed functions
- [ ] All tests use `unittest.mock.patch` for subprocess (no live LLM calls)

---

## Part 2: Code Quality Deep Dives

### 2.1 Anti-sycophancy integrity
This is the most critical architectural property. Verify:

- [ ] Pass B (fact_checker) launches `claude --print` as a subprocess, NOT as a continued conversation
- [ ] The verify-claims prompt does NOT reference extraction results, does NOT say "the analysis found..."
- [ ] The verifier receives raw evidence (fact_key, fact_value, source_quote) not the extraction's interpretation
- [ ] Contradictions are stored as `relationship='contradicts'` with low match_score — not suppressed or rationalized
- [ ] If the verifier flags a contradiction, the orchestrator records it faithfully (no filtering)

### 2.2 Arithmetic sandbox safety
Walk every code path that could execute arbitrary strings:

- [ ] `ast.parse()` is called BEFORE any `eval`/`exec`
- [ ] The AST walker rejects every node type not in the whitelist — check the whitelist is complete (no `ast.Attribute`, no `ast.Import`, no `ast.Assign`, no `ast.Subscript` unless justified)
- [ ] `__builtins__` is explicitly restricted (not just `{}` — verify no leakage through `math` module or input dict)
- [ ] `signal.SIGALRM` timeout is set (note: does not work on Windows — document or handle)
- [ ] Input dict values are all `float` — no user-controlled strings can enter the namespace
- [ ] The sandbox cannot be escaped via: `().__class__.__bases__[0].__subclasses__()`, `type.__subclasses__()`, or similar

### 2.3 Exception handling
- [ ] LLM calls catch `ExtractionError`, `json.JSONDecodeError`, `pydantic.ValidationError` — NOT bare `Exception` or `ValueError`
- [ ] Arithmetic engine catches `ArithmeticSandboxError` specifically
- [ ] `signal.alarm(0)` is called in a `finally` block (reset timer even on error)
- [ ] Partial batch failure: if one assertion's verification fails, others continue (not fail-all)

### 2.4 Data integrity
- [ ] `delete_assertions_for_report()` cascade-deletes `assertion_evidence` rows (FK has ON DELETE CASCADE)
- [ ] After deleting old assertions, new `batch_insert_assertions()` won't hit UNIQUE violations (assertions table has NO unique constraint — verify this)
- [ ] `insert_assertion_evidence()` can handle the same assertion being verified multiple times (evidence links have UNIQUE on `(assertion_id, extracted_fact_id)`)
- [ ] `verification_runs.run_id` is genuinely unique (includes timestamp — check for collision risk at sub-second granularity)
- [ ] If no extracted_facts exist for a ticker, ALL assertions should be marked unverifiable (not silently skip verification)

### 2.5 Convention compliance
- [ ] Follows Phase 2 LLM invocation pattern: `subprocess.run(["claude", "--print", "--output-format", "json", "--allowedTools", "", "--", prompt])`
- [ ] Uses `_parse_json_response()` pattern for handling `{"result": ...}` wrappers (or imports from llm_extract)
- [ ] Logging uses `logger = logging.getLogger(__name__)` (not print to stdout for non-user output)
- [ ] DB access via `with Database() as db:` context manager
- [ ] Imports from `src.evidence` use the `EvidenceDB` class, NOT raw SQL

---

## Part 3: Known Risks

For each risk, state **PASS**, **ISSUE**, or **NEEDS VERIFICATION** with a finding.

| # | Risk | What could break |
|---|------|-----------------|
| R1 | Key Findings table regex fails on non-standard formatting | Sections with merged cells, missing pipe characters, or extra columns produce 0 assertions from mechanical path |
| R2 | `requires_arithmetic` over-flags | If every number gets `requires_arithmetic=True`, Pass C runs on 30+ assertions per ticker instead of 5-10 |
| R3 | Candidate fact matching is too broad | If `_build_candidate_facts()` returns all 200 facts for every assertion, the verification prompt exceeds token budget |
| R4 | Candidate fact matching is too narrow | If fact_key prefix matching misses relevant facts (e.g., assertion says "revenue" but fact_key is "mda.revenue_growth_yoy"), match_score artificially drops |
| R5 | Numeric extraction from assertion text | Regex for "$4.3B" → 4300000000.0 can fail on edge formats ("$4.3 billion", "4,300M", "~$4B", "approximately $4.3B") |
| R6 | LLM verifier is sycophantic despite prompt | If the verify-claims prompt is too weak or the evidence presentation biases toward agreement, contradictions won't surface |
| R7 | `signal.SIGALRM` unavailable on macOS subprocess | If the arithmetic engine runs in a subprocess context where signals are suppressed, timeout doesn't fire |
| R8 | Assertion deduplication drops legitimate distinct claims | Two similar-but-different claims (e.g., "revenue $25.1B" and "revenue grew 11%") might be deduplicated when both should survive |
| R9 | `get_evidence_summary_for_ticker()` counts are wrong | Phase 3 review found unit mismatch (assertions vs evidence links) in this method — verify the Phase 3 fix was applied |
| R10 | Empty `extracted_facts` table for ticker | If Phase 2 hasn't run for this ticker, verification has nothing to match against — should produce a clear warning, not silent zero scores |
| R11 | Concurrent verification runs on same ticker | Two `./run.sh verify TICKER` runs at the same time could race on `delete_assertions_for_report` + `batch_insert_assertions` |
| R12 | Report section files missing | If section 04 doesn't exist but others do, decomposer should skip gracefully (not crash) |
| R13 | Stale verification results | After re-running analysis (new sections 01-08), old verification results in DB are misleading until `verify` is re-run |
| R14 | `match_score` semantics inconsistent | A `contradicts` relationship with `match_score=0.30` means "30% confidence in the contradiction" — but consumers might read it as "30% match quality" |
| R15 | Arithmetic engine formula from LLM is invalid Python | LLM writes `NOPAT / avg(IC)` instead of valid Python `nopat / ((ic_curr + ic_prev) / 2)` — needs clear prompt guidance |

---

## Part 4: Shortcuts Detection

Check for:
- [ ] Stub methods that return hardcoded values
- [ ] TODO/FIXME/HACK comments in production code
- [ ] Untested error paths (what happens when the DB is empty? when the report has 0 assertions? when all LLM calls fail?)
- [ ] Hardcoded test data that doesn't cover edge cases
- [ ] Missing validation on LLM output (e.g., `relationship` not in allowed set, `match_score` outside 0-1)
- [ ] Copy-pasted code from Phase 2 without adapting (different models, different prompt paths)

---

## Part 5: Functional Verification

Run these commands and report results:

### 5.1 Unit tests
```bash
python3 -m unittest tests.test_evidence_models -v
python3 -m unittest discover -s tests -p "test_claim_decomposer.py" -v
python3 -m unittest discover -s tests -p "test_fact_checker.py" -v
python3 -m unittest discover -s tests -p "test_arithmetic_engine.py" -v
```

### 5.2 Arithmetic sandbox safety
```python
# These must ALL be rejected by validate_formula():
validate_formula("__import__('os').system('rm -rf /')")
validate_formula("eval('1+1')")
validate_formula("exec('print(1)')")
validate_formula("open('/etc/passwd').read()")
validate_formula("().__class__.__bases__[0].__subclasses__()")
validate_formula("type.__subclasses__(type)")

# These must ALL pass:
validate_formula("(operating_income * (1 - tax_rate)) / ((ic_curr + ic_prev) / 2)")
validate_formula("abs(revenue_current - revenue_prior) / revenue_prior")
validate_formula("max(gross_profit / revenue, 0)")
```

### 5.3 Integration smoke test (requires Phase 2 evidence for SYK)
```bash
./run.sh verify SYK
```

Check:
- Exit code 0
- Summary printed to stdout
- DB: `SELECT COUNT(*) FROM assertions WHERE ticker='SYK'` returns 30-50
- DB: `SELECT COUNT(*) FROM assertion_evidence ae JOIN assertions a ON ae.assertion_id = a.id WHERE a.ticker='SYK'` returns >0
- DB: `SELECT * FROM verification_runs WHERE ticker='SYK' ORDER BY created_at DESC LIMIT 1` — verify counts are plausible

### 5.4 Idempotency test
```bash
./run.sh verify SYK
./run.sh verify SYK  # re-run immediately
```

Second run should:
- Delete old assertions (via `delete_assertions_for_report`)
- Re-insert fresh assertions
- Create a NEW verification_run (not overwrite the old one)
- DB: `SELECT COUNT(*) FROM verification_runs WHERE ticker='SYK'` should now be 2
- DB: `SELECT COUNT(*) FROM assertions WHERE ticker='SYK'` should be same count as first run (not doubled)

---

## Output Format

Structure your review as:

```
## Plan vs Implementation
[DONE/PARTIAL/MISSING/DEVIATED for each 1.1-1.7 item]

## Code Quality Issues
[File:line reference, severity (CRITICAL/HIGH/MEDIUM/LOW), description, recommendation]

## Risk Resolution
[PASS/ISSUE/NEEDS VERIFICATION for each R1-R15]

## Shortcuts Found
[List with file:line references]

## Test Results
[Pass/fail for each 5.1-5.4 command]

## Verdict
READY | NEEDS FIXES | NEEDS REDESIGN

## Required Changes Before Merge
[Numbered list, ordered by severity: CRITICAL first, then HIGH, then MEDIUM]

## Optional Improvements
[Nice-to-haves that don't block merge]
```
