# Masterplan: Evidence and Extraction Layer

## 1. Context & Purpose

The portfolio-and-investment platform runs an 8-umbrella Buffett-style analysis pipeline on equities, producing `FINAL-REPORT.md/.json` with verdicts, scores, and intrinsic value estimates. Today, analysis agents rely on aggregate yfinance data (`context/{TICKER}/financials.md`) plus ad-hoc web search. There is:

- **No structured extraction from SEC filings** — agents see yfinance summaries, not primary-source evidence
- **No programmatic verification** that report claims match source data
- **No audit trail** from assertion → evidence → source document
- **No separation** of language reasoning from arithmetic
- **No cross-period change detection** beyond manual inspection

This masterplan adds an Evidence and Extraction Layer that fills those gaps while preserving the existing pipeline unchanged.

### What this document is

A synthesized implementation guide drawn from three independent AI-generated plans (Agent 1, Agent 2, Agent 3) and their shared research foundation (`research-material/`). Each plan was evaluated against: (a) the actual codebase, (b) cited academic sources, (c) engineering proportionality for a solo/small-fund operation.

---

## 2. Plan Comparison & Verdict

### 2.1 The Three Plans

| Dimension | Agent 1 | Agent 2 | Agent 3 |
|-----------|---------|---------|---------|
| **File** | `implementation-plans/agent1.md` (8.9KB) | `implementation-plans/agent2.md` (10.7KB) | `implementation-plans/agent3.md` (27KB) |
| **Architecture** | Separate microservice (`services/evidence/`) | Separate repo (`investment-extractor/`) | Peer to `fetch-financials.py` within existing repo |
| **Database** | PostgreSQL 16 + pgvector + MinIO | PostgreSQL + Qdrant + Redis | SQLite (extends existing `db/portfolio.db` pattern) |
| **Orchestration** | Temporal workflows + FastAPI | LangGraph or LlamaIndex | Shell + Python scripts (matches `run.sh` pattern) |
| **EDGAR client** | EdgarTools + Docling | sec-edgar-downloader + unstructured.io | EdgarTools (free, structured section access) |
| **LLM integration** | Provider-agnostic | OpenAI (sample code uses `instructor` + OpenAI client) | Claude (matches existing pipeline) |
| **New dependencies** | ~15+ (Postgres, pgvector, MinIO, Temporal, FastAPI, SQLAlchemy, Alembic, Docling, Table Transformer, httpx, tenacity, orjson, structlog) | ~10+ (Postgres, Qdrant, Redis, LangGraph/LlamaIndex, unstructured.io, instructor, ragas) | 2 hard (edgartools, pydantic v2) |
| **Integration detail** | None — proposes external boundary | None — proposes separate repo | Exact line numbers in `run.sh`, `src/database.py`, `db/schema.sql` |
| **Cost model** | None | None | $30-60/cycle for LLM tier; 500 tickers = ~10min EDGAR fetch |
| **Phased rollout** | 6 phases but no backward-compatibility analysis | 5 phases + sample code | 8 phases, each independently useful, none breaking |
| **Schema** | Conceptual (interfaces described, no DDL) | Conceptual (Pydantic models described, no DDL) | Full SQLite DDL provided (7 tables, ~120 LOC) |
| **LOC estimates** | None | None | Per-file estimates totaling ~3,250 LOC |

### 2.2 Verdict: Agent 3 as skeleton, enriched by Agent 1's rigor

**Agent 3 is the best plan** for three reasons:

1. **Integration.** It's the only plan that actually fits the existing system. The platform uses SQLite (`db/portfolio.db`), shell dispatch (`run.sh` line 831), and context-file feeding (`run.sh` lines 426-438). Agent 3 slots into this pattern. Agent 1 and 2 propose entirely new infrastructure stacks that would require months of setup before producing any research value.

2. **Proportionality.** A solo/small-fund running a Claude Code pipeline does not need PostgreSQL, MinIO, Temporal, FastAPI, Qdrant, or Redis. SQLite handles the projected scale trivially (125K rows for 500 tickers × 5 filings). The existing database has 10 tables and runs fine at `SCHEMA_VERSION = 2`.

3. **Actionability.** Agent 3 provides exact file paths, line numbers, LOC estimates, CLI commands, a full database schema, and a cost model. You could start Phase 1 today.

**However, Agent 1 contributes critical ideas that Agent 3 underweights:**

- **SEC source policy**: The legal distinction between filed (HTML/TXT = official) and furnished (XBRL = reconciliation layer) is important for audit integrity. Agent 1 is the only plan that gets this right with citations.
- **Table structure preservation**: Agent 1's approach to maintaining coordinates, merged headers, row/column paths, and cell provenance is more rigorous than Agent 3's pipe-delimited markdown tables.
- **Docling**: Worth evaluating as a conversion fallback for complex filings where EdgarTools' `.markdown()` loses table structure.

**Agent 2 contributes useful framing:**

- **Named extraction passes** (Locator → Extractor → Calculator → Auditor) — clear mental model for the multi-pass pipeline.
- **Failure point table** — well-structured risk analysis format.
- **Evaluation with ragas** — useful for later-phase pipeline assessment.

### 2.3 What this masterplan does differently from any single agent

- Uses Agent 3's architecture, file structure, and phased rollout as the skeleton
- Adopts Agent 1's SEC source policy and table-handling rigor
- Incorporates Agent 1's document provenance model (every fact traces to filing URL + section + character offset)
- Adds Agent 2's named-pass mental model to Agent 3's multi-pass extraction
- Includes critical assessment and fact-checking of all cited research
- Maps every change to exact lines in the existing codebase

---

## 3. Research Foundation

All three plans draw on a shared research base (`research-material/agent1.md`, `agent2.md`, `agent3.md`, `agent-consensus-summary.md`). Below are the key findings, verified for accuracy.

### 3.1 Benchmarks That Matter

| Benchmark | Key Finding | Cited By | Verification Status |
|-----------|-------------|----------|-------------------|
| **FinanceBench** (Patronus AI, 2023) | Naive RAG on SEC filings: **19% accuracy**. Oracle context: **85%**. 66-point gap = retrieval quality is the #1 bottleneck. | Agent 3 | Numbers appear in research-material/agent3.md. Consistent with long-context findings below. |
| **FinQA** (EMNLP 2021) | GPT-4 zero-shot: **68.8%**. With CoT: ~84%. Agent 1 cites **65.05 execution accuracy** vs **91.16 expert**. Microsoft 2024 eval: GPT-4/EEDP at **76.05**. | All three | Agent 1 and 3 cite different numbers for GPT-4 on FinQA (65.05 vs 68.8). These likely reflect different evaluation conditions (zero-shot vs execution accuracy vs different GPT-4 versions). Both are plausible. The gap to expert (91.16) is the important takeaway: LLMs are still materially below human experts on financial numerical reasoning. |
| **TAT-QA** (ACL 2021) | Hybrid table+text QA. Agent 1 cites **58.0 F1** vs **90.8 human**. | Agent 1 | Large gap confirms pure-text models struggle with tabular reasoning. |
| **DocFinQA** | Retrieval-assisted GPT-4: **47.5**. Retrieval-free: **23.0**. | Agent 1 | 2x improvement with retrieval on long documents confirms section-based retrieval is mandatory. |
| **"Lost in the Middle"** (Liu et al.) | **20+ percentage point** accuracy drop for content in document middle. U-shaped performance curve. | All three | Agent 2 cites "2023", Agent 3 cites "TACL 2024". **TACL 2024 is the correct publication venue.** Agent 2's date is wrong. The finding itself is well-established and directly relevant: 10-K Risk Factors (page 20), MD&A (page 40), financials (page 60) are exactly the vulnerable positions. |

### 3.2 Key Technical Solutions

| Problem | Best Approach | Evidence |
|---------|---------------|----------|
| **Table structure collapse** | XBRL for tagged financials + structured markdown for narrative tables | XBRL eliminates ambiguity for tagged line items. Agent 2 cites 5-30% accuracy on complex balance sheets when tables flatten to prose. Agent 1 recommends preserving coordinates, merged headers, row/column paths. |
| **Section chunking** | Structure-aware (respect headers/SEC item boundaries) | Agent 3 cites Snowflake benchmark: **87.7% context recall** vs 75-82% for fixed/recursive/semantic chunking. Agent 1 proposes heading-aware chunking by SEC item boundaries. Both correct — structure-aware chunking demonstrably outperforms naive approaches. |
| **Claim verification** | Agent 3: `difflib.SequenceMatcher` (ratio < 0.85 → reject). Agent 3 also cites **MiniCheck** (770M params, GPT-4-level fact-checking at 400x lower cost, EMNLP 2024). | MiniCheck is promising for later phases but adds complexity. Start with `difflib` (stdlib, zero dependencies), graduate to MiniCheck if verification accuracy is insufficient. |
| **Arithmetic accuracy** | **Program of Thoughts (PoT)**: LLM writes formula, Python executes. | Agent 3 cites +12% over CoT (ICML 2023). Agent 1 uses Python `Decimal` for computation. Both correct: the critical principle is LLM identifies what to calculate, deterministic code executes. |
| **EDGAR data access** | **EdgarTools** >=2.0 (Python, free, no API key) | Agent 1 and 3 both recommend. Provides `.mda` accessor, `.markdown()` output, XBRL support, CIK lookup. Agent 3's choice as primary client is correct for this project. |

### 3.3 SEC Source Policy (from Agent 1, critically important)

Agent 1 makes a legally significant point that Agent 2 and 3 underweight:

> "SEC HTML/TXT is the legal narrative source of truth; SEC XBRL/companyfacts is the numeric reconciliation layer, not the narrative truth layer, because the SEC states only plain text/HTML are official filings and XBRL is furnished, not filed."

**This is correct.** SEC EDGAR documentation distinguishes between "filed" documents (the official legal record — HTML/TXT) and "furnished" data (XBRL, which companies submit but which the SEC does not treat as the legally binding version). For audit integrity, our system should:

- Use **SEC HTML/TXT** as the canonical narrative source (MD&A, Risk Factors, Notes)
- Use **XBRL** as a high-confidence numeric cross-check, not the narrative truth
- When XBRL and HTML disagree, **flag for review** rather than auto-resolving

### 3.4 Claims We Should Be Skeptical Of

| Claim | Source | Concern |
|-------|--------|---------|
| "SpreadsheetLLM indicates token efficiency improved by 96%" | Agent 2 | Plausible for their specific compression technique but unlikely to generalize to all financial table extraction. Treat as aspirational, not guaranteed. |
| "JPMorgan DocLLM outperforms GPT-4 on 14/16 tasks (+33 F1 on forms)" | Agent 3 (arxiv 2401.00908) | DocLLM is specialized for form-like documents. Financial filings are more heterogeneous than forms. The +33 F1 likely doesn't transfer directly to 10-K extraction. |
| "Balyasny $29B AUM, 20-person AI team, ~180 investment teams" | Agent 3 | These numbers come from the research material (`research-material/agent3.md`), not from direct verification. AUM and team size change frequently. The implementation patterns (federated deployment, micro-agents for filing changes) are more useful than the specific numbers. |
| Agent 2's "5-30% accuracy on complex balance sheets" for table collapse | Agent 2 | No specific benchmark cited. The range is very wide (5-30%) suggesting this is an estimate, not a measured result. The directional claim (table flattening hurts accuracy badly) is well-established; the specific numbers should not be treated as precise. |

---

## 4. Architecture Decisions

### 4.1 Core Principle: Peer to fetch-financials, not a new service

The evidence layer slots in as a **peer to `scripts/fetch-financials.py`** — another data-gathering script that writes context files. This avoids creating a new pipeline stage and leverages the existing pattern where `run.sh` lines 426-438 read ALL files in `context/{TICKER}/` and pass them to analysis agents.

```
cmd_analyze():
  1. python3 scripts/fetch-financials.py TICKER          # existing (yfinance)
  2. python3 scripts/fetch-evidence.py TICKER             # NEW (SEC EDGAR)
  3. Build CONTEXT from all files in context/{TICKER}/    # existing, unchanged
  4. Run umbrella agents                                   # existing, unchanged
```

**Why not a microservice (Agent 1) or separate repo (Agent 2)?**

- The current system runs as Claude Code agents + shell scripts + SQLite. Adding PostgreSQL, MinIO, Temporal, FastAPI, or Qdrant would create a second operational surface with different deployment, backup, monitoring, and debugging patterns.
- The projected scale (500 tickers, ~125K evidence rows, ~25-100GB raw filing cache) is well within SQLite's capabilities.
- If scale demands a migration later, the SQLite schema can be mechanically translated to PostgreSQL. Build for today's scale, migrate if needed.

### 4.2 Two-Tier Extraction (from Agent 3)

| Tier | Method | Token Cost | Coverage |
|------|--------|-----------|----------|
| **Tier 1: Mechanical** | XBRL fact parsing + regex on structured tables | Zero | ~60% of evidence (segment revenue, margins, debt schedules, per-share data) |
| **Tier 2: LLM** | Section-based structured extraction with Pydantic schemas | ~40-80K tokens/ticker | ~40% (risk factors, guidance, management commentary, qualitative assertions) |

Tier 2 only runs for tickers advancing to Stage C analysis (~20-30/cycle), not all 500. This keeps LLM costs at **$30-60/cycle**.

### 4.3 Source Hierarchy (synthesized from Agent 1 + Agent 3)

| Priority | Source | Role | Trust Level |
|----------|--------|------|-------------|
| 1 | SEC HTML/TXT filing (via EdgarTools) | Canonical narrative source | Authoritative (filed) |
| 2 | SEC XBRL (via EdgarTools) | Numeric cross-check | High (furnished, not filed) |
| 3 | `financials.md` (via yfinance) | Aggregate financial data | Medium (third-party aggregation) |
| 4 | Web search | Gap-filling for non-EDGAR tickers | Low (requires citation) |

When XBRL numeric values and HTML narrative values disagree by >5%, **flag for review** — do not auto-resolve.

### 4.4 Multi-Pass Extraction (synthesis of all three plans)

Using Agent 2's named-pass model mapped to Agent 3's implementation:

| Pass | Name | Input | Output | Token Cost |
|------|------|-------|--------|-----------|
| **Pass 0** | Mechanical | XBRL facts + structured tables | `extracted_facts` with `extraction_method='xbrl'`, `confidence=1.0` | Zero |
| **Pass 1** | Identifier | One filing section | List of factual claims in that section (natural language) | Low (~2K tokens/section) |
| **Pass 2** | Extractor | Each identified claim + source section | Structured `ExtractedFact` with verbatim `source_quote` | Medium (~500 tokens/claim) |
| **Pass 3** | Verifier | Extracted fact + source section (fresh context, different prompt) | `VerificationResult` with match score | Medium (~500 tokens/fact) |
| **Arithmetic** | Calculator | Formula description + input facts | Deterministic Python result with full provenance | Zero (Python only) |

Pass 1 (Identify) keeps each LLM call simple — scan for claims, don't extract structured data yet. This avoids the "lost in the middle" problem by separating detection from extraction.

### 4.5 Deterministic Arithmetic (Program of Thoughts)

LLM decides **what** to calculate. Python **executes**. Every input number traces to a source fact.

```python
# LLM output (Pass 2):
formula = "(operating_income * (1 - tax_rate)) / ((ic_curr + ic_prev) / 2)"
inputs = {"operating_income": 4920000000, "tax_rate": 0.19, ...}  # each maps to extracted_facts.id

# Python sandbox executes:
result = 0.1598  # ROIC — deterministic, auditable
```

Sandbox defense (from Agent 3): `ast.parse()` whitelist (only arithmetic ops + `abs/min/max/round/math.*`), restricted `__builtins__`, 5-second timeout.

### 4.6 Non-US Ticker Handling

The codebase tracks non-US tickers (MC.PA, WKL.AS, HLMA.L — all confirmed with `context/` directories and FINAL-REPORT.json files). SEC EDGAR only covers US filers. For non-US tickers:

- **Skip EDGAR extraction** with a warning (no 10-K/10-Q available)
- **Continue using yfinance + web search** (current behavior, unchanged)
- Context files: only `financials.md` (no `evidence-10K-*.md`)
- Analysis quality is unchanged from current pipeline for these tickers

---

## 5. Implementation Roadmap

### Phase 1: EDGAR Client + XBRL Extraction (Tier 1)

**Goal:** Fetch SEC filings and extract deterministic numeric facts with zero LLM cost.

**Depends on:** Nothing. **Breaking changes:** None.

**Steps:**

1. **EDGAR Client** — `src/evidence/edgar_client.py` (~300 LOC)
   - EdgarTools wrapper: CIK lookup, filing download, rate limiting (5 req/s, SEC allows 10)
   - Cache raw filings to `cache/edgar/{TICKER}/{accession}/`
   - Filings are immutable after publication → permanent cache, no TTL
   - Freshness check on filing index only (24h, matching `fetch-financials.py` pattern at line 29)
   - Non-US tickers → skip with warning

2. **Section Parser** — `src/evidence/section_parser.py` (~250 LOC)
   - Parse 10-K markdown into sections by header hierarchy
   - Section keys: `mda`, `risk_factors`, `income_stmt`, `balance_sheet`, `cash_flow`, `segment_data`, `notes`
   - Each chunk: `section_key`, `section_order`, `char_count`, `token_estimate`
   - Hard cap: 8,000 tokens per section (split at next heading if exceeded)
   - Preserve table structure (pipe-delimited markdown tables, not flattened prose)

3. **XBRL Numeric Extractor** — `src/evidence/xbrl_extractor.py` (~200 LOC)
   - Extract tagged financial facts via EdgarTools XBRL
   - Canonical tag mapping for variant tags (Revenue → `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` / `us-gaap:Revenues` / custom extensions)
   - Output: `extracted_facts` rows with `extraction_method='xbrl'`, `confidence=1.0`
   - Fallback for non-XBRL tickers: regex on `financials.md` structured tables

**CLI:** `./run.sh extract TICKER`

**Verification:** `python3 scripts/fetch-evidence.py INTU` → verify `context/INTU/evidence-10K-*.md` created with segment revenue data matching known values.

### Phase 2: LLM Extraction (Tier 2)

**Goal:** Extract narrative evidence (risk factors, guidance, management commentary) that XBRL can't capture.

**Depends on:** Phase 1. **Breaking changes:** None.

**Steps:**

4. **Evidence Models** — `src/evidence_models.py` (~150 LOC)
   - Pydantic v2 models: `ExtractedFact`, `Assertion`, `VerificationResult`, `SemanticDiff`
   - Section-specific schemas: `IncomeStatementFacts`, `SegmentRevenueFacts`, `RiskFactorFindings`, `GuidanceFacts`
   - These define the structured output schemas for Claude AND validate rows before DB insertion

5. **Schema Registry** — `src/evidence/schema_registry.py` (~100 LOC)
   - Map `section_key` → Pydantic model for extraction
   - Ensures each section type gets a constrained extraction prompt (reduces hallucination)

6. **Multi-Pass LLM Extractor** — `src/evidence/llm_extractor.py` (~400 LOC)
   - **Pass 1 (Identifier):** Scans section, lists every factual assertion (natural language). Prompt: `prompts/evidence/identify-claims.md`
   - **Pass 2 (Extractor):** For each claim, extract structured data with verbatim `source_quote`. Uses section-specific Pydantic schema from registry. Quantitative claims set `requires_arithmetic=True`. Prompt: `prompts/evidence/extract-structured.md`
   - Character offsets computed post-hoc by exact substring match

**CLI:** `./run.sh extract TICKER --tier2` (or automatic when Tier 1 completes)

**Verification:** Compare XBRL-extracted revenue against LLM-extracted revenue for 5 tickers → must agree within 5%.

### Phase 3: Database Schema + Evidence Storage

**Goal:** Persistent, queryable evidence storage with full provenance chain.

**Depends on:** Phase 2. **Breaking changes:** None (additive tables only).

**Steps:**

7. **Evidence Database Layer** — `src/evidence/evidence_db.py` (~300 LOC)
   - SQLite read/write following `src/database.py` pattern (same conventions, WAL mode, foreign keys)
   - Methods: `insert_extracted_fact()`, `get_facts_for_ticker()`, `insert_assertion()`, `link_assertion_to_fact()`, `get_unverified_assertions()`, `get_verification_summary()`
   - Migration: bump `SCHEMA_VERSION` from 2 → 3 in `src/database.py` (line 19), apply `db/evidence_schema.sql`
   - Extend `_JSON_COLUMNS` (lines 24-32) with: `computation_trace`, `detail_json`, `run_metadata_json`, `inputs_json`

**Full schema:** See Section 7 below.

### Phase 4: Post-Analysis Verification

**Goal:** After analysis agents write reports, decompose their claims and verify against evidence.

**Depends on:** Phase 3. **Breaking changes:** None.

**Steps:**

8. **Fact Checker** — `src/evidence/fact_checker.py` (~200 LOC)
   - Independently verify each extracted fact against source section
   - Different prompt from extraction (avoids self-confirmation bias — critical per sycophancy research)
   - Numeric verification: source_quote exists + value matches within tolerance + unit consistent
   - Narrative verification: source_quote supports assertion directionally
   - Cross-validate XBRL vs LLM values (must agree within 5%)
   - Prompt: `prompts/evidence/verify-claims.md`

9. **Claim Decomposer** — `src/evidence/claim_decomposer.py` (~150 LOC)
   - Read existing umbrella report sections (01-08) and decompose into atomic assertions
   - Parse Key Findings table first (structured), then scan Detailed Analysis paragraphs
   - Each assertion categorized as: `quantitative`, `qualitative`, `comparative`, `causal`
   - Links to supporting `extracted_facts` via `assertion_evidence` join table

10. **Arithmetic Engine** — `src/evidence/arithmetic_engine.py` (~200 LOC)
    - Three-layer sandbox: `ast.parse()` whitelist → restricted `__builtins__` → 5s timeout
    - Records formula string, inputs (with source fact IDs), and result in `computation_cache`
    - Full provenance: every number → `extracted_facts.id` → `document_sections.id` → `source_documents.id`

**CLI:** `./run.sh verify TICKER`

**Verification:** `./run.sh verify INTU` → verify assertions link to evidence with >80% verification score.

### Phase 5: Prompt Updates + FINAL-REPORT.json Enhancement

**Goal:** Teach analysis agents to use SEC evidence and record evidence quality in structured output.

**Depends on:** Phase 2 (evidence files must exist). **Breaking changes:** None (new field is optional).

**Steps:**

11. **Prompt updates:** Add ~10 lines to each umbrella prompt (01-08) teaching agents to prefer SEC evidence files when available, cite source document, and distinguish XBRL-verified from LLM-extracted data.

12. **Assembler update:** Add optional `evidence_summary` field to `FINAL-REPORT.json` schema in `prompts/assembler.md`. Structure:
    ```json
    "evidence_summary": {
      "total_assertions": 42,
      "verified_count": 38,
      "supported_count": 35,
      "contradicted_count": 1,
      "unverifiable_count": 6,
      "overall_score": 0.83,
      "data_sources": ["10-K FY2025 (XBRL+HTML)", "financials.md (yfinance)"]
    }
    ```

### Phase 6: Semantic Diffing

**Goal:** Detect changes between filing periods — the "what changed?" question that all three research agents ranked as a top-3 use case.

**Depends on:** Phase 3. **Breaking changes:** None.

**Steps:**

13. **Semantic Differ** — `src/evidence/semantic_differ.py` (~150 LOC) + `scripts/semantic-diff.py` (~200 LOC)
    - Match sections by `section_key` across filing periods
    - Numeric diffs: deterministic delta + % change for each `fact_key` present in both periods
    - Narrative diffs: LLM compares both section texts, identifies tone shifts, new risks, guidance changes
    - Output: `context/{TICKER}/evidence-changes.md` + `semantic_diffs` DB rows
    - Prompt: `prompts/evidence/semantic-diff.md`

**CLI:** `./run.sh diff TICKER --period-a FY2024 --period-b FY2025`

**Verification:** `./run.sh diff V --period-a FY2024 --period-b FY2025` → verify numeric deltas and narrative changes detected.

### Phase 7: Dashboard Evidence Section

**Goal:** Surface evidence quality and verification scores in the Streamlit dashboard.

**Depends on:** Phase 3. **Breaking changes:** None.

**Steps:**

14. Add evidence tab to `dashboard/app.py`:
    - Verification score per ticker
    - Unsupported/contradicted claims highlighted
    - Filing freshness indicators
    - Cross-period diff summaries

### Phase 8: Evaluation Harness

**Goal:** Continuous measurement of extraction accuracy and verification quality.

**Depends on:** Phase 4. **Breaking changes:** None.

**Steps:**

15. **Evaluation suite** — `evals/evidence/`
    - Extraction accuracy: known 10-K section → ground-truth facts → measure precision/recall
    - Citation validity: verify `source_quote` is verbatim substring of source section
    - Arithmetic correctness: known inputs + expected outputs → verify engine
    - Decomposition completeness: known report section → verify all quantitative claims captured
    - Follows existing `eval.yaml` pattern (lines 1-236)

---

## 6. Pipeline Integration Points

### 6.1 run.sh Changes

| Location | Change | Detail |
|----------|--------|--------|
| Line 831 dispatch table | Add `extract`, `verify`, `diff` commands | 3 new case entries |
| Lines 420-424 (cmd_analyze) | Add evidence fetch after financials fetch | `python3 "$SCRIPT_DIR/scripts/fetch-evidence.py" --quiet "$TICKER"` between financials fetch and context building |
| New function | `cmd_extract()` | Dispatches to `scripts/fetch-evidence.py` |
| New function | `cmd_verify()` | Dispatches to `scripts/verify-claims.py` |
| New function | `cmd_diff()` | Dispatches to `scripts/semantic-diff.py` |

**Critical integration insight:** Because `run.sh` lines 426-438 already read ALL files from `context/{TICKER}/`, the evidence layer's output files (`evidence-10K-*.md`, `evidence-changes.md`) are automatically consumed by analysis agents with zero changes to the context-reading logic.

### 6.2 src/database.py Changes

| Location | Change |
|----------|--------|
| Line 19 | `SCHEMA_VERSION = 2` → `SCHEMA_VERSION = 3` |
| Lines 24-32 | Extend `_JSON_COLUMNS` with 4 new entries |
| `migrate()` method | Add v2→v3 migration that applies `db/evidence_schema.sql` |

### 6.3 Prompt Changes

| File | Change |
|------|--------|
| `prompts/01-08` (each) | Add ~10-line section: "If SEC evidence files are available in the provided context, prefer them over web search. Cite source document type (10-K, 10-Q) and verification status ([XBRL-verified] or [LLM-extracted])." |
| `prompts/assembler.md` | Add optional `evidence_summary` field to FINAL-REPORT.json schema |

### 6.4 Backward Compatibility

Every phase is independently useful and backward-compatible:

- **No evidence files?** Analysis proceeds exactly as today (yfinance + web search). The context-reading loop at lines 426-438 simply has fewer files to read.
- **No evidence DB?** Reports are written the same way. Verification is optional.
- **Non-US tickers?** Skip EDGAR extraction with warning. Existing behavior unchanged.

---

## 7. Database Schema (New Tables)

Added to `db/evidence_schema.sql`, applied by v2→v3 migration:

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
    significance INTEGER DEFAULT 3,    -- 1-5 scale
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_facts_ticker ON extracted_facts(ticker);
CREATE INDEX IF NOT EXISTS idx_facts_key ON extracted_facts(fact_key);
CREATE INDEX IF NOT EXISTS idx_facts_period ON extracted_facts(fiscal_period);
CREATE INDEX IF NOT EXISTS idx_assertions_ticker ON assertions(ticker);
CREATE INDEX IF NOT EXISTS idx_assertion_evidence_assertion ON assertion_evidence(assertion_id);
CREATE INDEX IF NOT EXISTS idx_diffs_ticker ON semantic_diffs(ticker);
CREATE INDEX IF NOT EXISTS idx_source_docs_ticker ON source_documents(ticker);
```

---

## 8. New Files & Directory Structure

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
  verify-claims.md               # Pass 3 prompt (separate context from extraction)
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

**Estimated total new code:** ~3,250 LOC across 15 files + 4 prompt templates + 1 SQL schema file.

---

## 9. Risk Analysis & Guardrails

### 9.1 Critical Failure Points

| # | Failure | Why It Happens | Guardrail |
|---|---------|----------------|-----------|
| **F1** | XBRL tag inconsistency | Revenue tagged as `us-gaap:Revenues` by one company, `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` by another, or a custom extension | Canonical tag mapping in `constants.py` covering known variants. Unknown tags → fall back to LLM extraction. Nightly reconciliation flags tickers where XBRL and LLM disagree by >2%. |
| **F2** | Source quote fabrication | LLM returns paraphrased quote that isn't verbatim substring of source | `difflib.SequenceMatcher` post-extraction. Ratio < 0.85 → reject + retry with explicit "copy exact text" instruction. Second failure → `confidence=0.5` + flag. Char offsets only populated on exact match. |
| **F3** | Arithmetic sandbox injection | Malformed formula causes sandboxed execution to run harmful code | Three layers: (1) `ast.parse()` + node whitelist (`BinOp`, `UnaryOp`, `Num`, `Name`, whitelisted `Call`), (2) restricted `__builtins__` namespace, (3) 5-second timeout. All formulas + inputs logged. |
| **F4** | "Lost in the middle" | Full 10-K (80K+ tokens) overwhelms context window. Middle sections get degraded attention. | Section-based chunking with 8K token cap. Multi-pass extraction (Identify → Extract per-claim) keeps each LLM call under 12K tokens. Never stuff a full filing into one call. |
| **F5** | Stale evidence masking changes | Cached extraction from old filing used to verify new report | `content_hash` on `source_documents`. New fetch with different hash → invalidate all linked `extracted_facts` + re-extract. Section-level granularity via `document_sections.content_hash` — only re-extract changed sections. |
| **F6** | Sycophancy in verification | Verifier agrees with extractor because same conversation context | Verification uses a **fresh context** with a **different prompt** than extraction. This is critical — per research-material/agent3.md, sycophancy (>90% agreement rate) is more dangerous than hallucination for investment analysis because it operates through biased selection of real data. |

### 9.2 Anti-Sycophancy Design (from research consensus)

The research material's strongest shared warning: sycophancy — not hallucination — is the most dangerous LLM failure mode for concentrated portfolio managers. The evidence layer addresses this by:

1. **Separate contexts for extraction vs verification** — Pass 3 (Verify) runs in a fresh context with a different prompt than Pass 2 (Extract). No shared conversation history.
2. **Explicit anti-sycophancy instructions** in all evidence prompts: "You are permitted and encouraged to flag contradictions. Prioritize factual accuracy over consistency with prior extractions."
3. **XBRL as independent numeric check** — mechanical extraction cannot be sycophantic. When XBRL and LLM disagree, the disagreement itself is a signal.

---

## 10. Cost Model

| Dimension | Number | Strategy |
|-----------|--------|----------|
| EDGAR rate limits | 10 req/s (SEC), 5 req/s (our ceiling) | Token bucket; 500 tickers = ~10 min |
| Disk cache | ~50-200MB per ticker raw filing | 500 tickers = 25-100GB; prune >5yr filings |
| LLM token cost (Tier 2) | ~40-80K tokens/ticker/filing | Only Stage C tickers (~20-30/cycle) = **$30-60/cycle** |
| DB size | ~50 evidence items/ticker/filing | 500 tickers × 5 filings = 125K rows (trivial for SQLite) |
| Filing freshness | Quarterly (10-Q) or annual (10-K) | Only re-extract when new filing appears |
| Non-US tickers | No EDGAR coverage | Fall back to yfinance + web search (unchanged) |

### New Dependencies

| Package | Purpose | Required? |
|---------|---------|-----------|
| `edgartools` >=2.0 | SEC EDGAR access (CIK, filings, XBRL, `.mda`, `.markdown()`) | **Yes** |
| `pydantic` >=2.0 | Structured output schemas, validation, `model_json_schema()` | **Yes** |
| `tiktoken` >=0.5 | Accurate token counting for context budgeting | No (fallback: chars/4) |
| `lxml` >=4.9 | XBRL/XML parsing fallback | No (edgartools handles most cases) |
| `difflib` (stdlib) | Text similarity for source quote matching | Built-in |
| `ast` (stdlib) | Formula validation whitelist for arithmetic sandbox | Built-in |

Only **2 hard dependencies** added to `requirements.txt`. Compare: Agent 1 proposes ~15 new packages, Agent 2 proposes ~10.

---

## 11. Verification Plan (End-to-End)

| Test | Command | Success Criteria |
|------|---------|------------------|
| Phase 1 smoke test | `python3 scripts/fetch-evidence.py INTU` | `context/INTU/evidence-10K-*.md` created with segment revenue matching known values |
| XBRL cross-validation | Compare XBRL revenue vs `financials.md` yfinance revenue for 5 US tickers | Must agree within 5% |
| Non-US graceful skip | `python3 scripts/fetch-evidence.py MC.PA` | Warning printed, no crash, no evidence files created |
| Pipeline integration | `./run.sh analyze INTU` | Evidence files consumed by agents (check section 04 references SEC filing data) |
| Verification | `./run.sh verify INTU` | Assertions link to evidence with >80% verification score |
| Diff detection | `./run.sh diff V --period-a FY2024 --period-b FY2025` | Numeric deltas and narrative changes detected |
| Backward compat | `./run.sh analyze` for ticker WITHOUT evidence files | Identical output to current pipeline |
| Scale | `./run.sh extract --all-queue deep_research` | Rate limiting works, caching works, no EDGAR 429 errors |
| Citation integrity | Run verification on 3 tickers, check all `source_quote` values | Every quote is verbatim substring of source section |
| Schema migration | Delete `db/portfolio.db`, run any command | DB recreated at v3 with all evidence tables |

---

## 12. Source Bibliography

### Academic Papers

| Citation | Venue | Key Finding Used |
|----------|-------|-----------------|
| Chen et al., "FinQA: A Dataset of Numerical Reasoning over Financial Data" | EMNLP 2021 | Baseline accuracy gaps between LLMs and human experts on financial numerical reasoning |
| Zhu et al., "TAT-QA: A Question Answering Benchmark on a Hybrid of Tabular and Textual Content" | ACL 2021 | Hybrid table+text QA difficulty; pure-text models underperform |
| Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" | TACL 2024 (NOT 2023 — Agent 2's date is incorrect) | U-shaped attention curve; 20+ point accuracy drop for middle content |
| Chen et al., "Program of Thoughts Prompting" | ICML 2023 | +12% over CoT by delegating computation to Python |
| Tang et al., "MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents" | EMNLP 2024 | 770M parameter model achieves GPT-4-level fact-checking at 400x lower cost |
| Microsoft Research, "Evaluating LLMs Mathematical Reasoning in Financial Document QA" | 2024 | GPT-4/EEDP at 76.05 on FinQA, 77.91 on ConvFinQA, 70.32 on MultiHiertt |
| Patronus AI, "FinanceBench" | 2023 | Naive RAG: 19% accuracy. Oracle context: 85%. Retrieval quality is #1 bottleneck |
| Wang et al., "DocFinQA" | ACL 2024 | Retrieval-assisted GPT-4: 47.5 vs retrieval-free: 23.0 on long financial docs |

### Industry & Tools

| Source | URL | Used For |
|--------|-----|----------|
| SEC EDGAR APIs | sec.gov/search-filings/edgar-application-programming-interfaces | Official filing access |
| SEC Filing Guidance | sec.gov/edgar/searchedgar/aboutedgar.htm | Filed vs furnished distinction |
| EdgarTools | dgunning.github.io/edgartools/ | Primary EDGAR client (free, Python) |
| Docling | docling-project.github.io/docling/ | Referenced by Agent 1 as conversion fallback (evaluate for complex filings) |

### Research Material (Local)

| File | Content |
|------|---------|
| `research-material/agent1.md` | Evidence-grounded document extraction framework; token discipline rules |
| `research-material/agent2.md` | Institutional AI operating system; workflow orchestration |
| `research-material/agent3.md` | Practitioner evidence: Balyasny, Man Group, Point72, D.E. Shaw implementations |
| `research-material/agent-consensus-summary.md` | Synthesized consensus across all three research agents |
| `research-material/tldr-consensus.md` | 3 must-build systems + key technical rules |

---

## 13. What This Plan Deliberately Excludes

| Excluded Item | Reason | Revisit When |
|---------------|--------|-------------|
| PostgreSQL / pgvector | SQLite handles projected scale (125K rows). Migration is mechanical if needed. | Evidence DB exceeds 10GB or concurrent writes become a bottleneck |
| MinIO / S3 object storage | Local file cache (`cache/edgar/`) is sufficient for a single-operator system | Multi-user access or cloud deployment |
| Temporal / workflow orchestration | Shell scripts + Python CLIs match the existing pattern. Temporal adds operational complexity. | Pipeline exceeds 10 stages or needs retry/resume across failures |
| FastAPI service layer | No external consumers of evidence data. SQLite + CLI is sufficient. | Dashboard needs real-time evidence queries or other tools need API access |
| Redis / semantic caching | Filing cache is on disk (permanent, immutable). LLM calls are per-extraction-run, not repeated queries. | High-volume repeated queries against same evidence |
| LangGraph / LlamaIndex | Multi-pass extraction is implemented as sequential Python function calls, not a graph framework | Extraction logic becomes complex enough to need visual debugging |
| Docling | EdgarTools `.markdown()` is the primary converter. Docling is worth evaluating for complex table-heavy filings. | Table extraction accuracy is insufficient with EdgarTools alone |
| MiniCheck | Start with `difflib.SequenceMatcher` (stdlib). MiniCheck adds a 770M parameter model. | Citation verification accuracy is below 90% with difflib |
| ragas evaluation | Start with custom eval following existing `eval.yaml` pattern | Need standardized RAG evaluation metrics across multiple retrieval strategies |
