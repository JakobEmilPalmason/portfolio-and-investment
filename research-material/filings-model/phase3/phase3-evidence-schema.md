# Phase 3: Evidence Database Schema — Implementation Plan

**Status:** In progress
**Depends on:** None (storage-only layer)
**Produces:** 8 SQLite tables + Python CRUD layer for evidence storage

---

## Overview

Build the SQLite schema and Python read/write layer for the evidence extraction system. Every fact extracted from SEC filings traces back to its exact source quote in the filing. This phase is storage only — no EDGAR fetching, no LLM calls, no extraction logic.

Existing DB is at schema version 2 with 9 paper-trading tables. This adds 8 evidence tables and bumps to version 3.

## Files

| File | Action | Purpose |
|------|--------|---------|
| `db/evidence_schema.sql` | Create | DDL for 8 evidence tables + 16 indexes |
| `src/evidence.py` | Create | `EvidenceDB` class with ~44 CRUD methods |
| `src/database.py` | Modify | Bump version 2→3, add JSON cols, fix init_db, add migration |
| `tests/test_evidence.py` | Create | 21 smoke tests |

---

## Design Decisions (from Phase 3 Review)

### Critical Fix: Fresh Install Migration Path

`init_db()` previously inserted `SCHEMA_VERSION` directly, so `migrate()` no-oped on fresh installs. Since `schema.sql` only contains v1+v2 tables, evidence tables were never created.

**Fix:** `init_db()` inserts version 1. `migrate()` re-reads version after `init_db()` and falls through to all migration steps. Fresh install path: schema.sql (v1+v2 tables) → version 1 → migrate v1→v2 (no-op) → v2→v3 (evidence tables) → version 3.

### UNIQUE Constraint on extracted_facts

Added `UNIQUE(source_document_id, fact_key, fiscal_period)` to prevent silent duplicate facts. One value per fact_key per period per filing. If the same metric appears in different sections, the extractor uses a disambiguated key (e.g., `revenue.mda` vs `revenue.income_stmt`).

### Amended Filings

10-K amendments (10-K/A) treated as distinct `doc_type` values. `UNIQUE(ticker, doc_type, period_end)` naturally accommodates them. Both `insert_source_document` and `upsert_source_document` methods provided.

### ON DELETE CASCADE

Only on `assertion_evidence.assertion_id → assertions.id`. Deleting an assertion automatically cleans up its evidence links. All other FKs use manual control.

### Fact Staleness

`is_active INTEGER DEFAULT 1` on extracted_facts. Re-extraction marks old facts inactive rather than deleting. Preserves assertion_evidence links for audit. Query methods filter `is_active = 1` by default.

### Confidence Enforcement

`confidence REAL NOT NULL` with no DEFAULT. Forces callers to explicitly set confidence:
- XBRL: 1.0
- regex: 0.85-0.95
- llm_structured: 0.7-0.9
- computed: 1.0

### Batch Operations

`batch_insert_facts()` and `batch_insert_assertions()` use `executemany()` with single commit for performance. ~70 individual commits per ticker → 1.

---

## Value Contract

| Column | Content | Examples |
|--------|---------|----------|
| `fact_value` | Raw source string exactly as it appears | "$4.92 billion", "15.3%" |
| `fact_value_numeric` | Normalized base-unit number | 4920000000.0, 0.153 |
| `fact_unit` | Unit label | `USD` (actual dollars), `percent` (decimal 0.15), `ratio`, `count`, `days` |
| `confidence` | Extraction reliability | 1.0=XBRL, 0.85-0.95=regex, 0.7-0.9=LLM |
| `section_key` | Machine-readable slug, suffixed for splits | `mda`, `mda_part1`, `risk_factors` |
| `doc_type` | Filing type with amendment suffix | `10-K`, `10-K/A`, `10-Q`, `10-Q/A` |

---

## Tables (8)

### source_documents
One row per filing fetched. `UNIQUE(ticker, doc_type, period_end)`.

### document_sections
Parsed sections within a filing. FK → source_documents. `UNIQUE(source_document_id, section_key)`.

### extracted_facts
Individual facts with source citations. FK → source_documents (required), document_sections (optional). `UNIQUE(source_document_id, fact_key, fiscal_period)`. Has `is_active` flag for staleness. `confidence NOT NULL`.

### assertions
Claims from analysis reports to verify. Independent of facts — linked via assertion_evidence.

### assertion_evidence
Join table: assertions ↔ facts. `ON DELETE CASCADE` from assertions. `UNIQUE(assertion_id, extracted_fact_id)`.

### verification_runs
Audit log of verification passes. `run_id TEXT UNIQUE`.

### semantic_diffs
Cross-period changes between filings. Significance 1-5 scale.

### computation_cache
Deterministic arithmetic results. `UNIQUE(ticker, computation_key)`. inputs_json is a soft reference (documented limitation).

---

## Indexes (16)

```
source_documents:      ticker, accession_number
document_sections:     source_document_id
extracted_facts:       ticker, source_document_id, fact_key, fiscal_period, extraction_run_id, is_active
assertions:            ticker, umbrella_number
assertion_evidence:    assertion_id, extracted_fact_id
verification_runs:     ticker
semantic_diffs:        ticker
computation_cache:     ticker
```

---

## Python Layer: EvidenceDB (~44 methods)

Takes a `Database` instance, reuses its `.conn`. Follows existing patterns: `_decimal_fields_from_dict` before writes, `_row_to_dict` on reads, commit after every write, `DuplicateEntryError` on `IntegrityError`.

### source_documents (6)
`insert_source_document`, `upsert_source_document`, `get_source_document`, `get_source_documents_for_ticker`, `get_source_document_by_key`, `update_source_document`

### document_sections (4)
`insert_document_section`, `upsert_document_section`, `get_document_sections`, `get_document_section_by_key`

### extracted_facts (10)
`insert_extracted_fact`, `batch_insert_facts`, `get_extracted_fact`, `get_facts_for_ticker`, `get_facts_for_document`, `get_facts_for_section`, `get_facts_by_extraction_run`, `get_fact_with_provenance`, `deactivate_facts_for_document`, `delete_facts_for_extraction_run`

### assertions (6)
`insert_assertion`, `batch_insert_assertions`, `get_assertion`, `get_assertions_for_ticker`, `get_unverified_assertions`, `delete_assertions_for_report`

### assertion_evidence (5)
`insert_assertion_evidence`, `get_evidence_for_assertion`, `get_evidence_for_fact`, `get_evidence_summary_for_ticker`, `update_assertion_evidence`

### verification_runs (4)
`insert_verification_run`, `get_verification_run`, `get_verification_runs_for_ticker`, `get_latest_verification_run`

### semantic_diffs (5)
`insert_semantic_diff`, `get_diffs_for_ticker`, `get_diffs_between_periods`, `get_high_significance_diffs`, `delete_diffs_between_periods`

### computation_cache (4)
`upsert_computation`, `get_computation`, `get_computations_for_ticker`, `invalidate_computations`

### Cross-table (1)
`get_ticker_evidence_summary` — aggregate counts across all tables for a ticker

---

## Known Limitations

1. **computation_cache.inputs_json** is a soft reference to fact IDs. If facts are deactivated/deleted, cache entries point at nothing. Mitigation: `invalidate_computations(ticker)` after re-extraction.
2. **executescript() implicit commit** means partial DDL failure during migration is possible. Mitigated by `CREATE TABLE IF NOT EXISTS` making retry idempotent.
3. **No thread safety** — single connection, no locking. Acceptable for sequential pipeline execution.
