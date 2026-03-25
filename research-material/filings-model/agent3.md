# Evidence and Extraction Layer — Implementation Blueprint

## Context

The portfolio-and-investment platform runs 8-umbrella Buffett-style analyses on stocks, producing FINAL-REPORT.md/.json with verdicts, scores, and IV estimates. Today, analysis agents rely on yfinance aggregate data (`context/{TICKER}/financials.md`) plus ad-hoc web search. There is **no structured extraction from SEC filings**, no programmatic verification that report claims match source data, no audit trail from assertion → evidence → source document, and no separation of language reasoning from arithmetic. This blueprint adds an Evidence and Extraction Layer that fills those gaps without breaking the existing pipeline.

---

## Section 1: Research & Prior Art

### 1.1 Academic Benchmarks

| Benchmark | Key Finding |
|-----------|-------------|
| **FinanceBench** (Patronus AI, 2023) | Naive RAG on SEC filings: **19% accuracy**. Oracle context: **85%**. The 66-point gap means retrieval quality is the #1 bottleneck — not model capability. |
| **FinQA** (EMNLP 2021) | GPT-4 zero-shot: 68.8%. With CoT: ~84%. Multi-agent reflection adds +5-15% (ACM ICAIF 2024). |
| **TAT-QA** (ACL 2021) | Hybrid table+text QA. Pure-text models struggle with tabular reasoning. |
| **"Lost in the Middle"** (Liu et al., TACL 2024) | 20+ percentage point accuracy drop for content in the middle of long contexts. 10-K Risk Factors (page 20), MD&A (page 40), financials (page 60) are exactly the vulnerable positions. |

### 1.2 Industry Approaches

- **JPMorgan DocLLM** (arxiv 2401.00908): Layout-aware transformer using OCR bounding boxes. Outperforms GPT-4 on 14/16 structured extraction tasks (+33 F1 on forms). Key insight: positional layout matters for table extraction.
- **Balyasny** ($29B AUM): 20-person AI team, federated deployment across ~180 investment teams. Internal eval pipeline measuring 12+ dimensions. Central Bank Speech Analyst cut macro analysis from 2 days → 30 minutes.
- **Point72**: Building scale infrastructure (70+ engineering roles). $1B AI-focused fund. Less public on methodology.

### 1.3 Key Technical Solutions

| Problem | Best Approach | Evidence |
|---------|---------------|----------|
| Table structure preservation | **XBRL for financials** + Markdown conversion for narrative | XBRL = zero ambiguity for tagged line items; EdgarTools `.markdown()` preserves table structure |
| Section chunking | **Structure-aware** (respect headers) | 87.7% context recall vs 75-82% for fixed/recursive/semantic (Snowflake benchmark) |
| Claim verification | **MiniCheck** (770M params) | GPT-4-level fact-checking at 400x lower cost (EMNLP 2024) |
| Arithmetic accuracy | **Program of Thoughts** (PoT) | +12% over CoT by delegating computation to Python (ICML 2023) |
| Data sourcing | **EdgarTools** (Python, free) | `.mda`, `.markdown()`, XBRL access, no API key needed |

### 1.4 Data Source Comparison

| Source | MD&A Quality | Cost | Best For |
|--------|-------------|------|----------|
| EdgarTools (EDGAR) | Good (`.mda` accessor) | Free | Item-level section access + XBRL |
| sec-api | Very good (item extraction) | Paid | High-volume commercial use |
| Calcbench | Financials only | Paid | Standardized financial data |
| Capital IQ/FactSet | Excellent | $50K-200K+/yr | Institutional-grade |
| Raw EDGAR HTML | Requires parsing | Free | Fallback |

**Decision:** EdgarTools for this project — free, structured section access, Markdown output, XBRL support.

---

## Section 2: Implementation Logic

### 2.1 Architecture: Peer to fetch-financials, Not a New Stage

The evidence layer slots in as a **peer to `fetch-financials.py`** — another data-gathering script that writes context files. This avoids creating a new pipeline stage and leverages the existing pattern where `run.sh` lines 428-438 read all files in `context/{TICKER}/` and pass them to analysis agents.

```
cmd_analyze():
  1. python3 scripts/fetch-financials.py TICKER          # existing (yfinance)
  2. python3 scripts/fetch-evidence.py TICKER             # NEW (SEC EDGAR)
  3. Build CONTEXT from all files in context/{TICKER}/    # existing, unchanged
  4. Run umbrella agents                                   # existing, unchanged
```

### 2.2 Two-Tier Extraction

| Tier | Method | Token Cost | Coverage |
|------|--------|-----------|----------|
| **Tier 1: Mechanical** | XBRL fact parsing + regex on structured tables | Zero | ~60% of evidence (segment revenue, margins, debt schedules) |
| **Tier 2: LLM** | Section-based structured extraction with Pydantic schemas | ~40-80K tokens/ticker | ~40% (risk factors, guidance, management commentary) |

Tier 2 only runs for tickers advancing to Stage C analysis (~20-30/cycle), not all 500.

### 2.3 Deterministic Arithmetic (Program of Thoughts)

LLM decides **what** to calculate. Python **executes**. Every input number traces to a source fact.

```python
# LLM output:
formula = "(operating_income * (1 - tax_rate)) / ((ic_curr + ic_prev) / 2)"
inputs = {"operating_income": 4920000000, "tax_rate": 0.19, ...}

# Python sandbox executes:
result = 0.1598  # ROIC
# All inputs trace back to extracted_facts with source citations
```

Sandbox defense: `ast.parse()` whitelist (only arithmetic ops + `abs/min/max/round/math.*`), restricted `__builtins__`, 5-second timeout.

### 2.4 Zero-Trust Verification Loop

```
Generate claim → Decompose into atomic assertions → Verify each against source text
  → Cross-check XBRL vs LLM extraction (must agree within 5%)
  → Flag ungrounded claims → Separate arithmetic audit → Human review for flagged items
```

Source quote verification: fuzzy match `source_quote` against section text via `difflib.SequenceMatcher`. Ratio < 0.85 → reject and retry. Second failure → store with `confidence=0.5`, flag for review.

### 2.5 Semantic Diffing

Compare current filing against prior period. Numeric diffs are deterministic (delta + % change). Narrative diffs (MD&A tone, new/changed risk factors, guidance language shifts) use LLM with both section texts. Output: `context/{TICKER}/evidence-changes.md`.

---

## Section 3: 15-Step Implementation Roadmap

### Phase 1: Normalization (Steps 1-3)

**Step 1: EDGAR Client** — `src/evidence/edgar_client.py` (~300 LOC)
- EdgarTools wrapper: CIK lookup, filing download, rate limiting (5 req/s)
- Cache raw filings to `cache/edgar/{TICKER}/{accession}/`
- Filings are immutable after publication → permanent cache, no TTL
- Freshness check on filing index only (24h, matching `fetch-financials.py` pattern)
- Handle non-US tickers gracefully (MC.PA, WKL.AS, HLMA.L → skip with warning)

**Step 2: Section Parser** — `src/evidence/section_parser.py` (~250 LOC)
- Parse 10-K markdown into sections by header hierarchy (`## `, `### `)
- Parse existing `financials.md` into table sections
- Each chunk: `section_key` (slug), `section_order`, `char_count`, `token_estimate`
- Hard cap: 8,000 tokens per section (split at next heading if exceeded)
- Preserve table structure (pipe-delimited tables, not flattened)

**Step 3: XBRL Numeric Extractor** — `src/evidence/xbrl_extractor.py` (~200 LOC)
- Extract tagged financial facts via EdgarTools XBRL
- Canonical tag mapping for variant tags (Revenue → `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` / `us-gaap:Revenues` / custom extensions)
- Output: `extracted_facts` rows with `extraction_method='xbrl'`, `confidence=1.0`
- Fallback for non-XBRL tickers: regex on `financials.md` structured tables

### Phase 2: Schema Definition (Steps 4-5)

**Step 4: Evidence Models** — `src/evidence_models.py` (~150 LOC)
- Pydantic v2 models: `ExtractedFact`, `Assertion`, `VerificationResult`, `SemanticDiff`
- Section-specific schemas: `IncomeStatementFacts`, `SegmentRevenueFacts`, `RiskFactorFindings`, `GuidanceFacts`
- These are passed to Claude as structured output schemas AND validate rows before DB insertion

**Step 5: Schema Registry** — `src/evidence/schema_registry.py` (~100 LOC)
- Map `section_key` → Pydantic model for extraction
- Ensures each section type gets a constrained extraction prompt (reduces hallucination)

### Phase 3: Multi-Pass Agentic Extraction (Steps 6-8)

**Step 6: Pass 1 — Identify Claims** — `src/evidence/llm_extractor.py`
- LLM scans a section and lists every factual assertion (natural language, no structured extraction yet)
- Avoids "lost in the middle" by keeping this task simple (scan, don't extract)
- Prompt template: `prompts/evidence/identify-claims.md`

**Step 7: Pass 2 — Extract Structured Data** — `src/evidence/llm_extractor.py`
- For each identified claim, extract structured data with verbatim `source_quote`
- Uses section-specific Pydantic schema from registry
- Quantitative claims set `requires_arithmetic=True` with formula description (no LLM math)
- Character offsets computed post-hoc by exact substring match
- Prompt template: `prompts/evidence/extract-structured.md`

**Step 8: Pass 3 — Verify** — `src/evidence/fact_checker.py` (~200 LOC)
- Independently verify each extracted fact against source section
- Different prompt from extraction (avoids self-confirmation bias)
- Numeric verification: source_quote exists + value matches within tolerance + unit consistent
- Narrative verification: source_quote supports assertion directionally
- Cross-validate XBRL vs LLM values (must agree within 5%)
- Prompt template: `prompts/evidence/verify-claims.md`

### Phase 4: Semantic Diffing (Steps 9-10)

**Step 9: Period Alignment** — `src/evidence/semantic_differ.py` (~150 LOC)
- Match sections by `section_key` across filing periods
- Flag sections added/removed between periods

**Step 10: Diff Generation** — `src/evidence/semantic_differ.py` + `scripts/semantic-diff.py`
- Numeric diffs: deterministic delta + % change for each `fact_key` present in both periods
- Narrative diffs: LLM compares both section texts, identifies tone shifts, new risks, guidance changes
- Output: `context/{TICKER}/evidence-changes.md` + `semantic_diffs` DB rows
- CLI: `./run.sh diff INTU --period-a FY2024 --period-b FY2025`
- Prompt template: `prompts/evidence/semantic-diff.md`

### Phase 5: Defensive Guards (Steps 11-12)

**Step 11: Arithmetic Engine** — `src/evidence/arithmetic_engine.py` (~200 LOC)
- Three-layer sandbox: `ast.parse()` whitelist → restricted `__builtins__` → 5s timeout
- Records formula string, inputs (with source fact IDs), and result in `computation_cache`
- Full provenance: every number → `extracted_facts.id` → `document_sections.id` → `source_documents.id`

**Step 12: Claim Decomposer** — `src/evidence/claim_decomposer.py` (~150 LOC)
- Read existing umbrella report sections (01-08) and decompose into atomic assertions
- Parse Key Findings table first (structured), then scan Detailed Analysis paragraphs
- Each assertion categorized and stored in `assertions` table
- Links to supporting `extracted_facts` via `assertion_evidence` join table

### Phase 6: Integration, Caching, Evaluation (Steps 13-15)

**Step 13: Evidence Database Layer** — `src/evidence/evidence_db.py` (~300 LOC)
- SQLite read/write following `src/database.py` pattern (same conventions, WAL mode, foreign keys)
- Methods: `insert_extracted_fact()`, `get_facts_for_ticker()`, `insert_assertion()`, `link_assertion_to_fact()`, `get_unverified_assertions()`, `get_verification_summary()`
- Migration: bump `SCHEMA_VERSION` from 2 → 3 in `src/database.py`, apply `db/evidence_schema.sql`
- Extend `_JSON_COLUMNS` with: `computation_trace`, `detail_json`, `run_metadata_json`, `inputs_json`

**Step 14: Pipeline Integration**
- `run.sh`: Add `extract`, `verify`, `diff` commands to dispatch table (line 831)
- `run.sh` `cmd_analyze()`: Add evidence fetch after financials fetch (line 424)
- Prompt updates: Add ~10 lines to each umbrella prompt teaching agents to use SEC evidence
- `prompts/assembler.md`: Add optional `evidence_summary` field to FINAL-REPORT.json schema
- Post-analysis: Run verification after assembler writes FINAL-REPORT.json

**Step 15: Evaluation Harness** — `evals/evidence/`
- Extraction accuracy: known 10-K section → ground-truth facts → measure precision/recall
- Citation validity: verify `source_quote` is verbatim substring of source section
- Arithmetic correctness: known inputs + expected outputs → verify engine
- Decomposition completeness: known report section → verify all quantitative claims captured
- Follows existing `eval.yaml` pattern

---

## Section 4: Critical Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `run.sh` | Add `cmd_extract`, `cmd_verify`, `cmd_diff` functions + dispatch entries; add evidence fetch to `cmd_analyze` after line 424 | ~60 LOC added |
| `src/database.py` | Bump SCHEMA_VERSION to 3; extend `_JSON_COLUMNS`; add evidence migration to `migrate()` | ~20 LOC added |
| `db/schema.sql` | Add evidence tables (or new `db/evidence_schema.sql` sourced by migration) | ~120 LOC |
| `prompts/assembler.md` | Add optional `evidence_summary` field to FINAL-REPORT.json schema | ~15 LOC |
| `prompts/01-08` | Add ~10-line section teaching agents to use SEC evidence files | ~10 LOC each |

**New files created:**

```
scripts/
  fetch-evidence.py              # CLI entry point (~800 LOC)
  verify-claims.py               # Verification CLI (~200 LOC)
  semantic-diff.py               # Cross-period diff CLI (~200 LOC)

src/evidence/
  __init__.py
  edgar_client.py                # EDGAR fetcher + cache (~300 LOC)
  section_parser.py              # Section-based chunking (~250 LOC)
  xbrl_extractor.py              # XBRL fact extraction (~200 LOC)
  schema_registry.py             # Section → Pydantic schema map (~100 LOC)
  llm_extractor.py               # Multi-pass extraction (~400 LOC)
  arithmetic_engine.py           # Sandboxed Python arithmetic (~200 LOC)
  fact_checker.py                # Verification loop (~200 LOC)
  claim_decomposer.py            # Report → atomic assertions (~150 LOC)
  semantic_differ.py             # Period-over-period diffs (~150 LOC)
  evidence_db.py                 # SQLite layer (~300 LOC)
  constants.py                   # Enums, XBRL tag maps (~100 LOC)

src/evidence_models.py           # Pydantic models (~150 LOC)

db/evidence_schema.sql           # DDL for evidence tables (~120 LOC)

prompts/evidence/
  identify-claims.md             # Pass 1 prompt
  extract-structured.md          # Pass 2 prompt
  verify-claims.md               # Pass 3 prompt
  semantic-diff.md               # Diff prompt

context/{TICKER}/
  evidence-10K-YYYY.md           # Extracted 10-K evidence (auto-generated)
  evidence-10Q-YYYY-QN.md        # Extracted 10-Q evidence (auto-generated)
  evidence-changes.md            # Period diff summary (auto-generated)

cache/edgar/
  ticker-cik.json                # CIK mapping (fetched once)
  {TICKER}/{accession}/          # Raw filing cache (permanent)

evals/evidence/
  eval.yaml                      # Eval config
  fixtures/                      # Ground-truth test cases
```

---

## Section 5: SQLite Schema (New Tables)

```sql
-- Source documents: one row per filing fetched
CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    doc_type TEXT NOT NULL,            -- '10-K', '10-Q', 'financials.md'
    filing_date TEXT,
    period_end TEXT,
    accession_number TEXT,
    source_url TEXT,
    local_path TEXT NOT NULL,
    content_hash TEXT,                 -- SHA-256 for staleness detection
    section_count INTEGER DEFAULT 0,
    fetched_at TEXT NOT NULL,
    UNIQUE(ticker, doc_type, period_end)
);

-- Parsed sections within documents
CREATE TABLE IF NOT EXISTS document_sections (
    id INTEGER PRIMARY KEY,
    source_document_id INTEGER NOT NULL REFERENCES source_documents(id),
    section_key TEXT NOT NULL,          -- 'mda', 'risk_factors', 'income_stmt'
    section_title TEXT,
    section_order INTEGER,
    content_text TEXT NOT NULL,
    content_hash TEXT,
    token_estimate INTEGER,
    UNIQUE(source_document_id, section_key)
);

-- Extracted facts with source citations
CREATE TABLE IF NOT EXISTS extracted_facts (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    source_document_id INTEGER NOT NULL REFERENCES source_documents(id),
    document_section_id INTEGER REFERENCES document_sections(id),
    fact_type TEXT NOT NULL,            -- 'metric', 'narrative', 'guidance', 'risk_factor'
    fact_key TEXT NOT NULL,             -- 'segment_revenue.cloud', 'roic'
    fact_value TEXT,
    fact_value_numeric REAL,
    fact_unit TEXT,                     -- 'USD_millions', 'percent', 'ratio'
    fiscal_period TEXT,
    confidence REAL DEFAULT 1.0,
    extraction_method TEXT,            -- 'xbrl', 'llm_structured', 'regex', 'computed'
    source_quote TEXT,
    source_char_offset_start INTEGER,
    source_char_offset_end INTEGER,
    computation_trace TEXT,            -- JSON: formula + inputs for computed values
    extraction_run_id TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Assertions from analysis reports
CREATE TABLE IF NOT EXISTS assertions (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    report_path TEXT NOT NULL,
    umbrella_number INTEGER,
    assertion_text TEXT NOT NULL,
    assertion_type TEXT NOT NULL,       -- 'quantitative', 'qualitative', 'comparative', 'causal'
    category TEXT,
    requires_arithmetic INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Links assertions to supporting/contradicting evidence
CREATE TABLE IF NOT EXISTS assertion_evidence (
    id INTEGER PRIMARY KEY,
    assertion_id INTEGER NOT NULL REFERENCES assertions(id),
    extracted_fact_id INTEGER NOT NULL REFERENCES extracted_facts(id),
    relationship TEXT NOT NULL,         -- 'supports', 'contradicts', 'partial', 'unverifiable'
    match_score REAL,
    verification_method TEXT,
    verification_detail TEXT,           -- JSON
    verified_at TEXT,
    UNIQUE(assertion_id, extracted_fact_id)
);

-- Verification run audit log
CREATE TABLE IF NOT EXISTS verification_runs (
    id INTEGER PRIMARY KEY,
    run_id TEXT NOT NULL UNIQUE,
    ticker TEXT NOT NULL,
    run_date TEXT NOT NULL,
    total_assertions INTEGER,
    verified_count INTEGER,
    supported_count INTEGER,
    contradicted_count INTEGER,
    unverifiable_count INTEGER,
    overall_score REAL,
    run_metadata_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Cross-period semantic diffs
CREATE TABLE IF NOT EXISTS semantic_diffs (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    section_key TEXT NOT NULL,
    period_a TEXT NOT NULL,
    period_b TEXT NOT NULL,
    diff_type TEXT NOT NULL,            -- 'added', 'removed', 'changed', 'numeric_shift'
    summary TEXT NOT NULL,
    detail_json TEXT,
    significance INTEGER DEFAULT 3,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Computation cache for deterministic arithmetic
CREATE TABLE IF NOT EXISTS computation_cache (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    computation_key TEXT NOT NULL,      -- 'roic_FY2025'
    formula TEXT NOT NULL,
    inputs_json TEXT NOT NULL,          -- JSON: {param: value, ...} with fact IDs
    result_value REAL,
    result_unit TEXT,
    computed_at TEXT NOT NULL,
    UNIQUE(ticker, computation_key)
);
```

---

## Section 6: Library Stack

| Package | Purpose | Hard Req? |
|---------|---------|-----------|
| `edgartools` >=2.0 | SEC EDGAR access (CIK, filings, XBRL, `.mda`, `.markdown()`) | Yes |
| `pydantic` >=2.0 | Structured output schemas, validation, `model_json_schema()` | Yes |
| `tiktoken` >=0.5 | Accurate token counting for context budgeting | No (fallback: chars/4) |
| `lxml` >=4.9 | XBRL/XML parsing fallback | No (edgartools handles most cases) |
| `xxhash` >=3.0 | Fast content hashing for staleness checks | No (fallback: hashlib.sha256) |
| `difflib` (stdlib) | Text similarity for source quote matching | Built-in |
| `ast` (stdlib) | Formula validation whitelist for arithmetic sandbox | Built-in |

Only 2 hard dependencies added. Everything else already in use (yfinance, pandas, sqlite3) or optional.

---

## Section 7: "Flop" Analysis — 5 Critical Failure Points

### F1: XBRL Tag Inconsistency Across Filers
**Risk:** Revenue tagged as `us-gaap:Revenues` by one company, `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` by another, or a custom extension tag.
**Guardrail:** Canonical tag mapping in `constants.py` covering known variants. Unknown tags → fall back to LLM extraction (`extraction_method='llm_structured'`). Nightly reconciliation flags tickers where XBRL and LLM disagree by >2%.

### F2: Source Quote Fabrication
**Risk:** LLM returns a paraphrased quote that isn't a verbatim substring of the source, breaking the citation chain.
**Guardrail:** Post-extraction fuzzy match via `difflib.SequenceMatcher`. Ratio < 0.85 → reject + retry with explicit "copy exact text" instruction. Second failure → `confidence=0.5` + flag. Char offsets only populated on exact match.

### F3: Arithmetic Sandbox Injection
**Risk:** Malformed formula description causes sandboxed `eval()` to execute harmful code.
**Guardrail:** Three layers: (1) `ast.parse()` + node whitelist (`BinOp`, `UnaryOp`, `Num`, `Name`, whitelisted `Call`), (2) restricted `__builtins__` namespace, (3) 5-second timeout. All formulas + inputs logged.

### F4: Context Window Overflow / "Lost in the Middle"
**Risk:** Full 10-K (80K+ tokens) overwhelms context. Middle sections get degraded attention.
**Guardrail:** Section-based chunking with 8K token cap. Multi-pass extraction (Identify → Extract per-claim) keeps each LLM call under 12K tokens. Never stuff a full filing into one call.

### F5: Stale Evidence Masking Changes
**Risk:** Cached extraction from an old filing used to verify a new report, missing material changes.
**Guardrail:** `content_hash` column on `source_documents`. New fetch with different hash → invalidate all linked `extracted_facts` + re-extract. Section-level granularity via `document_sections.content_hash` — only re-extract changed sections.

---

## Section 8: Sample Execution — Extracting Segment Revenue for INTU

```
INPUT: ticker="INTU", target="segment_revenue", period="FY2025"

STEP 1: Fetch filing
  scripts/fetch-evidence.py INTU
  → edgartools: Company("INTU").get_filings(form="10-K").latest()
  → filing.markdown() → context/INTU/10-K_2025.md
  → filing.xbrl → context/INTU/xbrl/10-K_2025.json
  → INSERT source_documents (ticker='INTU', doc_type='10-K', period_end='2025-07-31')

STEP 2: Parse into sections
  section_parser.parse_filing_sections("context/INTU/10-K_2025.md")
  → segment_data section: "Revenue by segment...\n| Segment | FY2025 | FY2024 |..."
  → INSERT document_sections (section_key='segment_data', token_estimate=1850)

STEP 3: XBRL extraction (Tier 1, deterministic)
  xbrl_extractor.extract_xbrl_facts("INTU", "context/INTU/xbrl/10-K_2025.json")
  → tag: us-gaap:Revenue..., segment=GlobalBusinessSolutions, value=11842000000
  → INSERT extracted_facts (fact_key='segment_revenue.global_business_solutions',
       fact_value_numeric=11842000000, extraction_method='xbrl', confidence=1.0)

STEP 4: LLM extraction (Tier 2, cross-validation)
  Pass 1 (identify): "GBS segment revenue was $11.8B", "Consumer was $4.4B", ...
  Pass 2 (extract): ExtractedFact(fact_value_numeric=11842000000,
    source_quote='Global Business Solutions Group generated revenues of $11,842 million')
  → Verify: difflib match ratio = 1.0 (exact match at offset 2847)
  → INSERT extracted_facts (extraction_method='llm_structured', confidence=0.95)

STEP 5: Cross-validate
  XBRL: 11842000000 vs LLM: 11842000000 → delta 0.0% → MATCH

STEP 6: Write evidence context file
  → context/INTU/evidence-10K-2025.md (markdown with [XBRL] and [LLM] tags)

STEP 7: Analysis agent consumes it
  run.sh cmd_analyze reads ALL files in context/INTU/ → passes to umbrella agents
  → Agent writes "Global Business Solutions revenue of $11.8B" in section 04
  → Source: evidence-10K-2025.md [XBRL-verified]

STEP 8: Post-analysis verification
  Decompose section 04 → assertion: "GBS revenue was $11.8B in FY2025"
  → Link to extracted_facts.id via assertion_evidence (relationship='supports', score=0.97)
  → Full audit trail: assertion → fact → section → document → SEC filing
```

---

## Section 9: Scale & Cost Model

| Dimension | Number | Strategy |
|-----------|--------|----------|
| EDGAR rate limits | 10 req/s (SEC), 5 req/s (our ceiling) | Token bucket; 500 tickers = ~10 min |
| Disk cache | ~50-200MB per ticker raw filing | 500 tickers = 25-100GB; prune >5yr filings |
| LLM token cost (Tier 2) | ~40-80K tokens/ticker/filing | Only Stage C tickers (~20-30/cycle) = ~$30-60/cycle |
| DB size | ~50 evidence items/ticker/filing | 500 tickers × 5 filings = 125K rows (trivial for SQLite) |
| Filing freshness | Quarterly (10-Q) or annual (10-K) | Only re-extract when new filing appears |
| Non-US tickers | No EDGAR coverage | Fall back to yfinance + web search (unchanged) |

---

## Section 10: Implementation Order (Phased Rollout)

Each phase is independently useful and backward-compatible.

| Phase | Deliverable | Depends On | Breaking Changes |
|-------|-------------|------------|------------------|
| **1** | EDGAR client + XBRL extraction + `./run.sh extract TICKER` | None | None |
| **2** | LLM extraction (Tier 2) + evidence markdown files in `context/` | Phase 1 | None |
| **3** | DB schema v3 + evidence_db layer | Phase 2 | None (additive tables) |
| **4** | Post-analysis verification + `./run.sh verify TICKER` | Phase 3 | None |
| **5** | Prompt updates (teach agents to cite evidence) + `evidence_summary` in FINAL-REPORT.json | Phase 2 | None (new field is optional) |
| **6** | Semantic diffing + `./run.sh diff TICKER` | Phase 3 | None |
| **7** | Dashboard evidence section | Phase 3 | None |
| **8** | Evaluation harness | Phase 4 | None |

---

## Verification Plan

1. **Phase 1 smoke test:** `python3 scripts/fetch-evidence.py INTU` → verify `context/INTU/evidence-10K-*.md` created with segment revenue data matching known values
2. **Cross-validation test:** Compare XBRL-extracted revenue against `financials.md` yfinance revenue for 5 tickers → must agree within 5%
3. **Pipeline integration test:** `./run.sh analyze INTU` → verify evidence files are consumed by agents (check section 04 references SEC filing data)
4. **Verification test:** `./run.sh verify INTU` → verify assertions link to evidence with >80% verification score
5. **Diff test:** `./run.sh diff V --period-a FY2024 --period-b FY2025` → verify numeric deltas and narrative changes detected
6. **Backward compat test:** Run `./run.sh analyze` for a ticker WITHOUT evidence files → must produce identical output to current pipeline
7. **Scale test:** `./run.sh extract --all-queue deep_research` → verify rate limiting, caching, and no EDGAR 429 errors
