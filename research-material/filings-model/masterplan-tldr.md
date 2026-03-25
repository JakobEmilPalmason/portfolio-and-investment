# Evidence Layer — TLDR

## What we're building

A system that pulls real SEC filings (10-K, 10-Q) and extracts verified facts from them, so our analysis agents work from primary sources instead of yfinance summaries and web search guesses.

It plugs into the existing pipeline with zero breaking changes — just another script that writes files to `context/{TICKER}/`, which `run.sh` already reads automatically.

## Why it matters

- Agents currently have no access to actual SEC filings
- No way to verify if a report claim matches the source data
- No way to detect what changed between filing periods
- LLMs do math badly — we need to separate "what to calculate" from "do the calculation"

## What it produces

For each US ticker:
- `context/{TICKER}/evidence-10K-YYYY.md` — structured facts extracted from the 10-K
- `context/{TICKER}/evidence-changes.md` — what changed vs last period
- Database records linking every fact to its exact source quote in the filing

Non-US tickers (MC.PA, WKL.AS, HLMA.L) skip this — no SEC filings. They continue with yfinance + web search as before.

## How it works

```
./run.sh analyze TICKER
  1. fetch-financials.py   (existing — yfinance data)
  2. fetch-evidence.py     (NEW — SEC EDGAR data)
  3. Read all context/      (existing — unchanged)
  4. Run umbrella agents    (existing — unchanged)
```

### Two tiers of extraction

**Tier 1 — Mechanical (free, no LLM):** Parse XBRL tagged data for hard numbers — revenue, margins, debt, per-share data. ~60% of what we need. Confidence = 1.0.

**Tier 2 — LLM (costs tokens):** Extract risk factors, guidance, management commentary. Uses multi-pass approach:
1. **Identify** — scan a section, list all factual claims
2. **Extract** — for each claim, pull structured data + exact source quote
3. **Verify** — fresh context, different prompt, check the extraction is correct

When Tier 1 and Tier 2 disagree on a number by >5%, flag it rather than picking a winner.

### Math rule

LLM writes the formula. Python executes it. Every input traces to a source fact. No LLM arithmetic.

## New dependencies

Just 2: `edgartools` (free SEC access) and `pydantic` v2 (schema validation). Everything else is stdlib.

## Build order

Each phase works on its own. Nothing breaks if you stop after any phase.

### Phase 1 — EDGAR fetch + XBRL extraction
Build the EDGAR client, section parser, and XBRL extractor. Output: `./run.sh extract TICKER` writes evidence markdown files to `context/`.

**New files:**
- `scripts/fetch-evidence.py` — CLI entry point
- `src/evidence/edgar_client.py` — EDGAR wrapper with rate limiting + cache
- `src/evidence/section_parser.py` — split filing into sections by headers
- `src/evidence/xbrl_extractor.py` — mechanical numeric extraction

**Test:** `./run.sh extract INTU` → check that `context/INTU/evidence-10K-*.md` has correct segment revenue numbers.

### Phase 2 — LLM extraction
Add the multi-pass LLM extractor for narrative content (risk factors, guidance, tone).

**New files:**
- `src/evidence_models.py` — Pydantic schemas for extracted facts
- `src/evidence/schema_registry.py` — maps section type → extraction schema
- `src/evidence/llm_extractor.py` — Identify → Extract → Verify pipeline
- `prompts/evidence/identify-claims.md`
- `prompts/evidence/extract-structured.md`

**Test:** XBRL revenue and LLM-extracted revenue agree within 5% for 5 tickers.

### Phase 3 — Database storage
Add 7 new tables to SQLite for persistent evidence with full provenance chain. Bump `SCHEMA_VERSION` from 2 → 3.

**New files:**
- `db/evidence_schema.sql` — table DDL
- `src/evidence/evidence_db.py` — SQLite layer (follows existing `src/database.py` patterns)

**Modify:**
- `src/database.py` line 19: version 2 → 3
- `src/database.py` lines 24-32: add new JSON columns

### Phase 4 — Post-analysis verification
After reports are written, decompose their claims and check them against extracted evidence.

**New files:**
- `src/evidence/fact_checker.py` — verification with fresh context
- `src/evidence/claim_decomposer.py` — report → atomic assertions
- `src/evidence/arithmetic_engine.py` — sandboxed Python math
- `scripts/verify-claims.py` — CLI
- `prompts/evidence/verify-claims.md`

**Test:** `./run.sh verify INTU` → >80% of assertions link to supporting evidence.

### Phase 5 — Prompt updates
Teach analysis agents to prefer SEC evidence when available. Add `evidence_summary` field to `FINAL-REPORT.json`.

**Modify:**
- `prompts/01-08` (each): add ~10 lines about using evidence files
- `prompts/assembler.md`: add optional evidence_summary to JSON schema

### Phase 6 — Semantic diffing
Detect what changed between filing periods. Numeric diffs are deterministic. Narrative diffs use LLM.

**New files:**
- `src/evidence/semantic_differ.py`
- `scripts/semantic-diff.py`
- `prompts/evidence/semantic-diff.md`

**Test:** `./run.sh diff V --period-a FY2024 --period-b FY2025` → finds numeric and narrative changes.

### Phase 7 — Dashboard
Add evidence tab to Streamlit dashboard: verification scores, unsupported claims, filing freshness.

### Phase 8 — Eval harness
Automated tests for extraction accuracy, citation validity, and arithmetic correctness. Follows existing `eval.yaml` pattern.

## run.sh integration

| Change | Where |
|--------|-------|
| Add `extract`, `verify`, `diff` commands | Dispatch table (line 831) |
| Add evidence fetch to analyze flow | After financials fetch (line 424) |
| Add `cmd_extract()`, `cmd_verify()`, `cmd_diff()` | New functions |

The key insight: `run.sh` lines 426-438 already read ALL files from `context/{TICKER}/`. Evidence files land there automatically — no context-reading changes needed.

## Key guardrails

| Risk | Defense |
|------|---------|
| LLM fabricates a quote | Fuzzy match against source text — reject if <85% match |
| LLM does math wrong | LLM writes formula, Python sandbox executes it |
| Verifier agrees with extractor (sycophancy) | Verify in fresh context with different prompt |
| Full 10-K overwhelms context | Section-based chunking, 8K token cap, never stuff full filing |
| Stale cache hides changes | SHA-256 content hash — re-extract when filing changes |
| XBRL tags vary across companies | Canonical tag mapping + LLM fallback for unknowns |

## Cost

- EDGAR access: free, rate limited to 5 req/s
- Tier 1 (XBRL): free
- Tier 2 (LLM): ~40-80K tokens/ticker → **$30-60 per analysis cycle** (20-30 tickers)
- Storage: trivial for SQLite (125K rows at full scale)
- New packages: 2

## Total scope

~3,250 lines of new code across 15 Python files, 4 prompt templates, and 1 SQL schema file.
