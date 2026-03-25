# Phase 3 Implementation Review: Evidence Database Schema + Storage Layer

## Context

Phase 3 adds 8 evidence tables and a Python CRUD layer (`EvidenceDB`) to the existing SQLite-backed investment analysis system. The goal: every fact extracted from SEC filings traces to its exact source quote. This review cross-references the actual implementation against the masterplan spec, the 30-item pre-review checklist, and the 5-part implementation review prompt.

**Files reviewed:**
- `db/evidence_schema.sql` (155 lines — 8 tables, 16 indexes)
- `src/evidence.py` (738 lines — EvidenceDB class, 45 methods)
- `src/database.py` (605 lines — 4 surgical edits)
- `tests/test_evidence.py` (721 lines — 39 tests, 9 classes)

---

## Part 1: Plan vs Implementation

### 1.1 Schema Completeness

| Table | Verdict | Details |
|-------|---------|---------|
| `source_documents` | **DONE** | 11 columns + `created_at` + `UNIQUE(ticker, doc_type, period_end)`. All columns present with correct types. |
| `document_sections` | **DONE** | 9 columns + `created_at` + `UNIQUE(source_document_id, section_key)`. FK to source_documents, NOT NULL on content_text. |
| `extracted_facts` | **DEVIATED (improved)** | 20 columns (added `is_active INTEGER DEFAULT 1`). Changed `confidence REAL DEFAULT 1.0` to `confidence REAL NOT NULL` (no default — forces explicit setting). Added `UNIQUE(source_document_id, fact_key, fiscal_period)` (masterplan said no UNIQUE). Renamed `computation_trace` → `computation_trace_json` (follows `_json` suffix convention). All deviations are improvements. |
| `assertions` | **DONE** | 9 columns + `created_at`. Matches plan exactly. |
| `assertion_evidence` | **DEVIATED (improved)** | 9 columns + `created_at`. Added `ON DELETE CASCADE` on `assertion_id` FK (masterplan had no CASCADE). Renamed `verification_detail` → `verification_detail_json`. Both improvements. |
| `verification_runs` | **DONE** | 12 columns + `created_at` + `UNIQUE(run_id)`. Matches plan. |
| `semantic_diffs` | **DONE** | 10 columns + `created_at`. `significance INTEGER DEFAULT 3`. Matches plan. |
| `computation_cache` | **DONE** | 10 columns + `created_at` + `UNIQUE(ticker, computation_key)`. Matches plan. |

No columns were silently dropped. No unjustified extra columns except `is_active` (justified by soft-delete lifecycle).

### 1.2 Index Completeness

All 13 planned indexes exist. **4 extra indexes added** (all justified):

| Extra Index | Table | Justification |
|-------------|-------|---------------|
| `idx_source_documents_accession` | `source_documents(accession_number)` | EDGAR lookups by accession |
| `idx_extracted_facts_document` | `extracted_facts(source_document_id)` | FK join performance |
| `idx_extracted_facts_extraction_run` | `extracted_facts(extraction_run_id)` | `delete_facts_for_extraction_run` scans this |
| `idx_extracted_facts_active` | `extracted_facts(is_active)` | All queries filter on `is_active = 1` |

Index names follow `idx_{full_table_name}_{column}` — slightly different from masterplan shorthand (`idx_facts_ticker` vs `idx_extracted_facts_ticker`) but more correct.

### 1.3 database.py Modifications

| Edit | Verdict | Details |
|------|---------|---------|
| A: `SCHEMA_VERSION = 3` | **DONE** | Line 19. |
| B: 5 JSON columns added to `_JSON_COLUMNS` | **DONE** | Lines 24-37. Names verified character-for-character against `evidence_schema.sql`: `computation_trace_json`, `verification_detail_json`, `run_metadata_json`, `detail_json`, `inputs_json`. All match. Note: masterplan listed 4 entries but missed `verification_detail_json` — implementation correctly identified all 5. |
| C: Migration block `if current < 3:` | **DONE** | Lines 218-224. Reads `evidence_schema.sql`, executes it, inserts version 3, commits. |
| D (unplanned): `init_db()` fix | **DONE** | Lines 122-143. Now inserts version 1 instead of `SCHEMA_VERSION`. Critical fix for fresh installs. Also: `migrate()` re-reads version after `init_db()` and falls through to migration steps. |

No other lines in `database.py` were changed beyond these 4 edits.

### 1.4 EvidenceDB Class — Method Audit

**45 methods total** (plan said ~40, implementation doc said 44).

| Group | Planned | Actual | Verdict |
|-------|---------|--------|---------|
| source_documents | 5 | 6 | +1: `upsert_source_document` (justified — ON CONFLICT pattern) |
| document_sections | 4 | 4 | All present |
| extracted_facts | 7 | 10 | +3: `batch_insert_facts`, `deactivate_facts_for_document`, `get_fact_with_provenance` (moved from cross-table) |
| assertions | 5 | 6 | +1: `batch_insert_assertions` |
| assertion_evidence | 5 | 5 | All present |
| verification_runs | 4 | 4 | All present |
| semantic_diffs | 5 | 5 | All present |
| computation_cache | 4 | 4 | All present |
| cross-table | 2 | 1 | `get_ticker_evidence_summary` present. `get_fact_with_provenance` moved to facts group. |

**No planned methods are missing.** All extras are justified (batch inserts for performance, upsert for idempotent re-fetch, deactivate for soft-delete lifecycle).

**One spec deviation: `get_facts_for_ticker` missing `extraction_method` filter.** Plan says multi-filter should include `extraction_method`. Implementation has `fact_type`, `fact_key`, `fiscal_period`, `include_inactive` — but NOT `extraction_method`.

### 1.5 Tests

| # | Spec Test | Verdict | Implementation Test |
|---|-----------|---------|---------------------|
| 1 | Schema version is 3 after migration | **DONE** | `test_fresh_install_is_v3` |
| 2 | Insert + get source_document round-trip | **DONE** | `test_insert_and_get` |
| 3 | Duplicate source_document raises DuplicateEntryError | **DONE** | `test_duplicate_raises` |
| 4 | Insert + get document_sections ordered by section_order | **DONE** | `test_insert_and_get_ordered` |
| 5 | Upsert document_section updates content | **DONE** | `test_upsert_updates_content` |
| 6 | Insert + get extracted_facts | **DONE** | `test_insert_and_get` |
| 7 | JSON column round-trip | **DONE** | `test_json_roundtrip` |
| 8 | Insert + get assertions ordered by umbrella_number | **DONE** | `test_insert_and_get_ordered` |
| 9 | Unverified assertions LEFT JOIN | **DONE** | `test_unverified_assertions` (both states tested) |
| 10 | Insert + get assertion_evidence JOIN enrichment | **DONE** | `test_insert_and_get_evidence` |
| 11 | Duplicate assertion_evidence raises | **DONE** | `test_duplicate_raises` |
| 12 | Insert + get verification_run JSON round-trip | **DONE** | `test_insert_and_get` |
| 13 | Semantic diffs with significance filtering | **DONE** | `test_insert_and_filter_by_significance` |
| 14 | Upsert computation_cache updates result | **DONE** | `test_upsert_updates` |
| 15 | Foreign key enforcement | **DONE** | `test_foreign_key_enforcement` |
| 16 | ticker_evidence_summary end-to-end | **DONE** | `test_end_to_end_summary` |

All 16 required tests present. Implementation adds 23 more (39 total) covering: v2→v3 migration, table existence, upserts, batch inserts, amendments, deactivation, confidence enforcement, provenance JOIN, multi-filter queries, cascade delete, JSON round-trips across multiple tables.

---

## Part 2: Convention Conformance

### 2.1 SQL Conventions

| Check | Verdict |
|-------|---------|
| `id INTEGER PRIMARY KEY` first column | **PASS** — all 8 tables |
| `created_at TEXT DEFAULT (datetime('now'))` last column | **PASS** — all 8 tables |
| Column types: TEXT, INTEGER, REAL only | **PASS** — no BOOLEAN, BLOB, VARCHAR |
| Booleans as INTEGER | **PASS** — `is_active INTEGER`, `requires_arithmetic INTEGER` |
| JSON columns suffixed `_json` | **PASS** — `computation_trace_json`, `verification_detail_json`, `run_metadata_json`, `detail_json`, `inputs_json` |
| REFERENCES inline syntax | **PASS** |
| UNIQUE table-level syntax | **PASS** |
| Index names `idx_{table}_{column}` | **PASS** |
| No PRAGMAs in schema file | **PASS** |
| `IF NOT EXISTS` on all DDL | **PASS** |

### 2.2 Python Conventions

| Check | Verdict |
|-------|---------|
| Module-level `logger = logging.getLogger(__name__)` | **PASS** — line 21 |
| Takes `Database` instance, accesses `db.conn` | **PASS** — line 32-37 |
| All reads use `_row_to_dict()` | **PASS** — every SELECT method |
| All writes use `_decimal_fields_from_dict()` | **PASS** — every INSERT/UPSERT |
| All writes call `self.conn.commit()` | **PASS** — every write method |
| IntegrityError → `DuplicateEntryError` with table + ticker | **PASS** — all insert methods |
| Return types: int/dict/list[dict] | **PASS** |
| Parameterized queries (? placeholders) | **PASS** — no SQL injection surface |
| Type hints on all methods | **PASS** |
| Docstrings on public methods | **PASS** |

### 2.3 Import Hygiene

| Check | Verdict |
|-------|---------|
| Exactly `Database, DuplicateEntryError, _row_to_dict, _decimal_fields_from_dict` | **PASS** — line 14-19 |
| No new external dependencies | **PASS** |
| No circular imports | **PASS** |

**One violation:** `import json` appears inline at line 516 inside `update_assertion_evidence` instead of at module level. See M3 below.

---

## Part 3: Known Risk Resolution

### 3.1 Fresh Install Bug — **FIXED**

`init_db()` now inserts version 1 (line 140), not `SCHEMA_VERSION`. `migrate()` re-reads version after `init_db()` (line 153) and falls through all migration steps. Fresh install path: `schema.sql` → version 1 → v1→v2 (IF NOT EXISTS, no-op on tables already in schema.sql) → v2→v3 (evidence tables) → version 3. Test `test_fresh_install_is_v3` validates this.

### 3.2 executescript() Atomicity — **PARTIALLY FIXED**

`CREATE TABLE IF NOT EXISTS` makes retry idempotent. Version 3 insert happens AFTER all tables are created (line 222-223). If DDL fails mid-way, partial tables exist but version stays at 2 — re-running `migrate()` will re-attempt (IF NOT EXISTS skips already-created tables, creates remaining ones). This is the best SQLite can do without explicit BEGIN/COMMIT wrapping `executescript()` (which issues an implicit COMMIT first).

### 3.3 No UNIQUE on extracted_facts — **FIXED**

`UNIQUE(source_document_id, fact_key, fiscal_period)` added at line 64 of `evidence_schema.sql`. Combined with the `is_active` flag and `deactivate_facts_for_document()` method, the re-extraction flow is: deactivate old → insert new (unique constraint prevents accidental duplicates). Test `test_duplicate_raises` validates constraint enforcement.

### 3.4 Manual Cascade Deletion — **PARTIALLY FIXED**

`ON DELETE CASCADE` on `assertion_evidence.assertion_id` (line 83) means `delete_assertions_for_report()` cleanly cascades. Test `test_cascade_delete` validates this.

**However: `delete_facts_for_extraction_run()` at line 333 does NOT handle the fact side.** There is no CASCADE on `assertion_evidence.extracted_fact_id`. A hard DELETE on facts that have evidence links will raise an unhandled IntegrityError. See Critical finding C1 below.

### 3.5 JSON Column Name Mismatch — **ALL MATCH**

Side-by-side verification:

| `_JSON_COLUMNS` entry | `evidence_schema.sql` column | Match? |
|----------------------|----------------------------|--------|
| `computation_trace_json` | `computation_trace_json TEXT` (extracted_facts) | **YES** |
| `verification_detail_json` | `verification_detail_json TEXT` (assertion_evidence) | **YES** |
| `run_metadata_json` | `run_metadata_json TEXT` (verification_runs) | **YES** |
| `detail_json` | `detail_json TEXT` (semantic_diffs) | **YES** |
| `inputs_json` | `inputs_json TEXT NOT NULL` (computation_cache) | **YES** |

### 3.6 Amended Filing Handling — **FIXED**

`10-K/A` is a distinct `doc_type` value. `UNIQUE(ticker, doc_type, period_end)` naturally accommodates both original and amendment for the same period. Test `test_amendment_distinct_from_original` validates this.

---

## Part 4: Shortcuts Found

### C1. `delete_facts_for_extraction_run` will crash on FK violation [CRITICAL]

**File:** `src/evidence.py:333-341`
**Schema:** `db/evidence_schema.sql:84` — `extracted_fact_id INTEGER NOT NULL REFERENCES extracted_facts(id)` (no ON DELETE clause = RESTRICT)

The method does a bare `DELETE FROM extracted_facts WHERE extraction_run_id = ?` with no pre-delete check for `assertion_evidence` rows referencing those facts. If any fact has been linked to an assertion, SQLite raises IntegrityError (FK violation). The method has no try/except for this — it propagates as an unhandled exception.

This is asymmetric with the assertion side (which has ON DELETE CASCADE). The soft-delete path (`deactivate_facts_for_document`) is safe (UPDATE only). The hard-delete path is not.

**When it will break:** First time someone re-runs extraction on a document whose facts have already been verified and linked to assertions.

**Fix:** Before the DELETE, query `assertion_evidence` for rows referencing the targeted facts. Either delete those links first (with a logged warning), or raise a clear error.

### M1. Missing `extraction_method` filter on `get_facts_for_ticker` [MEDIUM]

**File:** `src/evidence.py:254-283`

Plan spec says the method should support `extraction_method` as an optional filter. Implementation has `fact_type`, `fact_key`, `fiscal_period`, `include_inactive` — but not `extraction_method`. Phase 4+ will need to filter "only XBRL facts" or "only LLM facts". One-line addition to the conditions builder.

### M2. Batch insert methods have no rollback on partial failure [MEDIUM]

**File:** `src/evidence.py:221-246, 365-384`

When `executemany()` hits an IntegrityError mid-batch (e.g., duplicate at row 7 of 10), the except block re-raises as `DuplicateEntryError` without calling `self.conn.rollback()`. Rows 1-6 may already be committed (SQLite's implicit transaction behavior). The caller gets an error but can't know how many rows persisted.

**Fix:** Add `self.conn.rollback()` before `raise DuplicateEntryError(...)` in both batch methods.

### M3. Inline `import json` in `update_assertion_evidence` [MEDIUM]

**File:** `src/evidence.py:516`

`json` is imported inside the method body, not at module level. Every other JSON-handling path goes through `_decimal_fields_from_dict`. This method bypasses that pattern by doing manual `json.dumps()` on `verification_detail_json`. Two issues:
1. Hidden dependency — `json` not in module imports
2. Pattern divergence — if `_JSON_COLUMNS` handling changes, this code path won't be updated

**Fix:** Either add `import json` at module level (line 11), or refactor to process the fields dict through `_decimal_fields_from_dict` before building SET.

### M4. `get_diffs_for_ticker` missing `diff_type` filter [MEDIUM]

**File:** `src/evidence.py:595-614`

The spec mentions `diff_type` as a filter parameter. Implementation only supports `section_key` and `min_significance`. One-line addition to the conditions builder.

### M5. `get_ticker_evidence_summary` runs 6 separate queries [MEDIUM]

**File:** `src/evidence.py:700-737`

Executes 5 independent COUNT queries plus a method call (`get_latest_verification_run`). Could be consolidated into 2-3 queries with subqueries or CTEs. Not a correctness issue, but measurable at scale.

### L1. f-string SQL in `get_facts_for_document` [LOW]

**File:** `src/evidence.py:286-291`

Uses `f"...{active_clause}..."` interpolation for a hardcoded SQL fragment. Safe (the value is never user input), but inconsistent with `get_facts_for_ticker` which uses the conditions/params list builder pattern 20 lines earlier.

### No stub methods found. No placeholder `NotImplementedError` raises. All 45 methods execute real SQL.

### Test data is realistic — AAPL ticker, real SEC accession number format, realistic financial values ($394B revenue), real section keys (mda, risk_factors, income_stmt), real report paths.

---

## Part 5: Functional Verification Plan

These checks must be run during implementation to validate the review findings:

### 5.1 Schema Validity
```bash
sqlite3 :memory: < db/evidence_schema.sql && echo "PASS"
```
Expected: exit 0, no errors.

### 5.2 Migration Roundtrip
```python
from src.database import Database
db = Database(":memory:")
db.init_db()
db.migrate()
# Verify schema_version is 3
# Verify all 8 evidence tables exist in sqlite_master
# Verify all 16 indexes exist
# Verify original 10 tables still present
```

### 5.3 Full CRUD Roundtrip
Insert source_document → insert section → insert fact → insert assertion → link via assertion_evidence → read everything back → verify JSON columns are dicts (not strings), FKs enforced, all fields round-trip.

### 5.4 Test Suite
```bash
python3 -m pytest tests/test_evidence.py -v
```
Expected: 39 passed, 0 skipped, 0 xfailed.

### 5.5 Existing Tests
```bash
python3 -m pytest tests/ -v
```
Note: Other test files appear deleted in git status. If they still exist, verify they pass.

### 5.6 Real Database Safety
```bash
cp db/portfolio.db db/portfolio.db.bak
python3 -c "from src.database import Database; db = Database(); db.migrate()"
# Verify existing data intact (spot-check positions, transactions)
# Verify 8 new tables exist
# Verify schema_version shows 3
```

### 5.7 FK Violation Test (validates C1)
```python
# Insert document → insert fact → insert assertion → link via assertion_evidence
# Then: delete_facts_for_extraction_run(run_id) → SHOULD fail or handle gracefully
# Currently: unhandled IntegrityError
```

---

## Verdict

**NEEDS FIXES** — 1 critical bug, 4 medium issues. The overall implementation quality is high (excellent convention conformance, 39 well-written tests, justified spec deviations), but the FK safety gap on `delete_facts_for_extraction_run` is a production-time crash waiting to happen.

---

## Required Changes Before Merge (ordered by severity)

1. **[CRITICAL] Fix `delete_facts_for_extraction_run` FK safety** (`evidence.py:333-341`)
   - Before DELETE, query assertion_evidence for rows referencing the targeted facts
   - Delete those evidence links first (log a warning for each), then delete facts
   - Add test: insert fact → link to assertion → call delete → verify clean deletion or clear error

2. **[MEDIUM] Add rollback in batch insert methods** (`evidence.py:245-246, 383-384`)
   - Add `self.conn.rollback()` in except blocks before re-raising DuplicateEntryError
   - Add test: batch-insert with a known duplicate mid-batch → verify none persist (all rolled back)

3. **[MEDIUM] Add `extraction_method` filter to `get_facts_for_ticker`** (`evidence.py:254`)
   - Add `extraction_method: str = None` parameter
   - Add condition to filter builder: `if extraction_method: clauses.append("extraction_method = ?"); params.append(extraction_method)`
   - Add test: insert facts with different extraction_methods → filter → verify

4. **[MEDIUM] Fix inline `import json`** (`evidence.py:516`)
   - Add `import json` at module-level imports (after line 11)
   - Or refactor to pass fields through `_decimal_fields_from_dict` before SET construction
   - Add test for `update_assertion_evidence`: insert link → update with dict for verification_detail_json → verify round-trip

5. **[MEDIUM] Add `diff_type` filter to `get_diffs_for_ticker`** (`evidence.py:595`)
   - Add `diff_type: str = None` parameter
   - Add condition to filter builder

---

## Optional Improvements

- Consolidate `get_ticker_evidence_summary` into 2-3 queries using subqueries/CTEs
- Standardize `get_facts_for_document` to use the conditions/params pattern
- Add test for migration idempotency (run migrate() twice on v3 DB → no-op)
- Add test for `get_source_document` returning None (empty table)
- Add test for `update_source_document`
- Add test for `get_evidence_for_fact` (reverse lookup)
- Add test for `delete_diffs_between_periods`
- Document the `is_active` soft-delete lifecycle in the schema header comment

---

## Resolution of Pre-Review Checklist Items (30 items)

| # | Item | Resolution |
|---|------|-----------|
| 1 | UNIQUE too tight? | **PASS** — 10-K/A distinct doc_type; split sections use suffixed keys; computation_cache upsert overwrites |
| 2 | UNIQUE too loose on extracted_facts? | **FIXED** — UNIQUE(source_document_id, fact_key, fiscal_period) added |
| 3 | FK cascading behavior | **PARTIAL** — CASCADE on assertion side; fact side has C1 bug |
| 4 | Missing indexes | **FIXED** — 4 extra indexes added beyond plan (accession, document FK, extraction_run, is_active) |
| 5 | Column type decisions | **IMPROVED** — confidence NOT NULL without default; value contract documented in schema header |
| 6 | Section splitting vs UNIQUE | **PASS** — suffixed keys (mda_part1, mda_part2) documented in schema comment |
| 7 | Temporal data model | **FIXED** — `is_active` flag + `deactivate_facts_for_document` method |
| 8 | Fresh install migration | **FIXED** — init_db inserts v1, migrate walks all steps |
| 9 | Migration atomicity | **PARTIALLY FIXED** — IF NOT EXISTS makes retry idempotent |
| 10 | _JSON_COLUMNS extension | **PASS** — new frozenset with all 12 entries |
| 11 | Schema version row | **PASS** — version 3 inserted after DDL, before commit |
| 12 | Separate class or extension? | **PASS** — separate EvidenceDB class, takes Database instance, shares connection |
| 13 | Decimal handling | **PASS** — uses _decimal_fields_from_dict consistently; evidence layer uses REAL/float, not Decimal |
| 14 | Row-to-dict conversion | **PASS** — uses existing _row_to_dict via shared _JSON_COLUMNS |
| 15 | Error handling | **PASS** — DuplicateEntryError on IntegrityError, upserts for idempotent operations |
| 16 | Logging | **PASS** — debug for individual ops, info for bulk/deletes |
| 17 | Provenance chain | **PASS** — `get_fact_with_provenance` JOINs facts → sections → documents |
| 18 | extraction_run_id | **PASS** — string tag, grouped via `get_facts_by_extraction_run`, deletable via `delete_facts_for_extraction_run` |
| 19 | assertion_evidence relationship | **PASS** — multiple facts per assertion supported; summary aggregates across relationships |
| 20 | Cross-period fact identity | **DEFERRED** — schema issue acknowledged as Phase 6 concern |
| 21 | Write volume / batching | **FIXED** — `batch_insert_facts` and `batch_insert_assertions` with executemany |
| 22 | Query patterns indexed | **PASS** — all common queries have index coverage |
| 23 | Cache invalidation blast radius | **PASS** — `deactivate_facts_for_document` soft-deletes, `invalidate_computations` hard-deletes cache |
| 24 | Phase 4 dependency | **PASS** — assertions can be inserted independently of facts |
| 25 | Phase 6 dependency | **PASS** — period format (e.g., 'FY2024') is TEXT, same across tables |
| 26 | Phase 7 dependency | **PASS** — EvidenceDB takes Database instance, dashboard instantiates both |
| 27 | Non-US tickers | **PASS** — schema allows doc_type='financials.md' for non-EDGAR sources |
| 28 | Empty filings | **PASS** — content_text NOT NULL enforced at schema level |
| 29 | Re-running extraction | **PASS** — upsert methods for documents/sections; deactivate + re-insert for facts |
| 30 | Fresh clone, no DB | **FIXED** — init_db + migrate creates all tables at v3 |
