# Phase 3 Implementation Review (Revised): Evidence Database Schema + Storage Layer

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
| `assertions` | **DONE — but see issue #7** | 9 columns + `created_at`. Matches plan exactly. No UNIQUE constraint — see Shortcuts section. |
| `assertion_evidence` | **DEVIATED (improved)** | 9 columns + `created_at`. Added `ON DELETE CASCADE` on `assertion_id` FK (masterplan had no CASCADE). Renamed `verification_detail` → `verification_detail_json`. Both improvements. |
| `verification_runs` | **DONE** | 12 columns + `created_at` + `UNIQUE(run_id)`. Matches plan. |
| `semantic_diffs` | **DONE** | 10 columns + `created_at`. `significance INTEGER DEFAULT 3`. Matches plan. |
| `computation_cache` | **DONE** | 10 columns + `created_at` + `UNIQUE(ticker, computation_key)`. Matches plan. |

No columns were silently dropped. No unjustified extra columns except `is_active` (justified by soft-delete lifecycle).

### 1.2 Index Completeness

All 13 planned indexes exist. **4 extra indexes added:**

| Extra Index | Table | Justified? |
|-------------|-------|------------|
| `idx_source_documents_accession` | `source_documents(accession_number)` | Yes — EDGAR lookups by accession |
| `idx_extracted_facts_document` | `extracted_facts(source_document_id)` | Yes — FK join performance |
| `idx_extracted_facts_extraction_run` | `extracted_facts(extraction_run_id)` | Yes — `delete_facts_for_extraction_run` scans this |
| `idx_extracted_facts_active` | `extracted_facts(is_active)` | **No** — boolean column with only two values (0/1) has near-zero selectivity. The query optimizer will rarely use a single-column index on this. Should be a composite index like `(ticker, is_active)` or `(source_document_id, is_active)` to actually help queries that filter on both. See issue #9. |

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

**45 methods total** (plan header says ~44).

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

**Suggested addition:** `get_facts_for_ticker` would benefit from an `extraction_method` filter parameter. Future phases will need to distinguish XBRL-sourced from LLM-extracted facts. Not a spec deviation — the plan doesn't specify filter parameters — but a practical gap that Phase 4+ will encounter.

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

All 16 required tests present. Implementation adds 23 more (39 total).

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
| All reads use `_row_to_dict()` | **FAIL** — `get_evidence_summary_for_ticker` (line 498) uses `dict(row)` which bypasses `_row_to_dict` and skips JSON deserialization. `get_ticker_evidence_summary` (lines 702-720) uses `.fetchone()["c"]` directly, also bypassing `_row_to_dict`. See issue #3. |
| All writes use `_decimal_fields_from_dict()` | **PASS** — every INSERT/UPSERT |
| All writes call `self.conn.commit()` | **PASS** — every write method |
| IntegrityError → `DuplicateEntryError` with table + ticker | **ISSUE** — `insert_semantic_diff` (line 592) catches IntegrityError and raises DuplicateEntryError, but `semantic_diffs` has NO UNIQUE constraint. The only IntegrityError possible is a NOT NULL violation, not a duplicate. Semantically misleading. See issue #8. |
| Return types: int/dict/list[dict] | **PASS** |
| Parameterized queries (? placeholders) | **PASS** — no SQL injection surface |
| Type hints on all methods | **PASS** |
| Docstrings on public methods | **PASS** |

### 2.3 Import Hygiene

| Check | Verdict |
|-------|---------|
| Exactly `Database, DuplicateEntryError, _row_to_dict, _decimal_fields_from_dict` | **ISSUE** — `import json` appears inline at line 516 inside `update_assertion_evidence` instead of at module level. Hidden dependency. |
| No new external dependencies | **PASS** |
| No circular imports | **PASS** |

---

## Part 3: Known Risk Resolution

### 3.1 Fresh Install Bug — **FIXED**

`init_db()` now inserts version 1 (line 140), not `SCHEMA_VERSION`. `migrate()` re-reads version after `init_db()` (line 153) and falls through all migration steps. Fresh install path: `schema.sql` → version 1 → v1→v2 (IF NOT EXISTS, no-op on tables already in schema.sql) → v2→v3 (evidence tables) → version 3. Test `test_fresh_install_is_v3` validates this.

### 3.2 executescript() Atomicity — **PARTIALLY FIXED**

`CREATE TABLE IF NOT EXISTS` makes retry idempotent. Version 3 insert happens AFTER all tables are created (line 222-223). If DDL fails mid-way, partial tables exist but version stays at 2 — re-running `migrate()` will re-attempt. This is the best SQLite can do without wrapping `executescript()`.

### 3.3 No UNIQUE on extracted_facts — **FIXED**

`UNIQUE(source_document_id, fact_key, fiscal_period)` added at line 64 of `evidence_schema.sql`. Combined with the `is_active` flag and `deactivate_facts_for_document()`, the re-extraction flow is: deactivate old → insert new. Test `test_duplicate_raises` validates constraint enforcement.

### 3.4 Manual Cascade Deletion — **PARTIALLY FIXED**

`ON DELETE CASCADE` on `assertion_evidence.assertion_id` (line 83) means `delete_assertions_for_report()` cleanly cascades. Test `test_cascade_delete` validates this.

**However:** The review of FK behavior is incomplete. See issues #1 (C1), #10, and #11 for the full picture of FK deletion gaps across the schema.

### 3.5 JSON Column Name Mismatch — **ALL MATCH**

| `_JSON_COLUMNS` entry | `evidence_schema.sql` column | Match? |
|----------------------|----------------------------|--------|
| `computation_trace_json` | `computation_trace_json TEXT` (extracted_facts) | **YES** |
| `verification_detail_json` | `verification_detail_json TEXT` (assertion_evidence) | **YES** |
| `run_metadata_json` | `run_metadata_json TEXT` (verification_runs) | **YES** |
| `detail_json` | `detail_json TEXT` (semantic_diffs) | **YES** |
| `inputs_json` | `inputs_json TEXT NOT NULL` (computation_cache) | **YES** |

### 3.6 Amended Filing Handling — **FIXED**

`10-K/A` is a distinct `doc_type` value. Test `test_amendment_distinct_from_original` validates this.

---

## Part 4: All Issues Found

Issues are numbered sequentially. Severity: CRITICAL, HIGH, MEDIUM, LOW.

---

### #1. `delete_facts_for_extraction_run` crashes on FK violation [CRITICAL]

**File:** `src/evidence.py:333-341`
**Schema:** `db/evidence_schema.sql:84` — `extracted_fact_id INTEGER NOT NULL REFERENCES extracted_facts(id)` (no ON DELETE clause = RESTRICT)

The method does a bare `DELETE FROM extracted_facts WHERE extraction_run_id = ?` with no pre-delete check for `assertion_evidence` rows referencing those facts. If any fact has been linked to an assertion, SQLite raises IntegrityError. The method has no handler for this.

**When it breaks:** First time someone re-runs extraction on a document whose facts have already been verified.

**Fix options (with trade-offs):**
- **(A) Refuse hard-delete when evidence links exist.** Query `assertion_evidence` first; if any rows reference targeted facts, raise a clear error directing callers to use `deactivate_facts_for_document` instead. Preserves verification history. Most conservative.
- **(B) Delete evidence links first, then facts.** Pre-delete query + manual cascade with a logged warning. Destroys verification history silently — downstream consumers lose evidence links.
- **(C) Add `ON DELETE CASCADE` to `assertion_evidence.extracted_fact_id`** in the schema, matching the assertion side. Clean but makes it easy to accidentally destroy evidence data. Requires schema migration (v3→v4 or schema alter).

**Recommendation:** Option A. Hard-delete of verified facts should be an explicit, deliberate action — not something that happens silently inside a pipeline re-run. The soft-delete path (`deactivate_facts_for_document`) already exists for the common re-extraction case.

---

### #2. `get_evidence_for_assertion` returns stale/deactivated facts [HIGH]

**File:** `src/evidence.py:459-469`

The JOIN at line 464 (`JOIN extracted_facts f ON ae.extracted_fact_id = f.id`) does NOT filter `f.is_active = 1`. After re-extraction deactivates old facts, evidence queries still return stale fact data (old values, old source quotes).

This is either a bug or an intentional audit design. Either way it must be explicitly addressed:
- **If stale evidence should be excluded:** Add `AND f.is_active = 1` to the WHERE clause (with an `include_inactive` parameter for audit views).
- **If stale evidence is intentional (audit trail):** Document this choice clearly in the method docstring AND in the schema design doc. Add the `is_active` field to the returned dict so consumers can distinguish.

**Same issue affects:** `get_evidence_for_fact` (line 471-481) — also joins without `is_active` filter.

---

### #3. `get_evidence_summary_for_ticker` has a semantic unit mismatch [HIGH]

**File:** `src/evidence.py:483-502`

The query mixes two incompatible counting units:
- `total_assertions` uses `COUNT(DISTINCT a.id)` — counts **assertions** (correct)
- `verified_count` uses `COUNT(DISTINCT CASE WHEN ae.id IS NOT NULL THEN a.id END)` — counts **assertions** (correct)
- `supported_count` uses `SUM(CASE WHEN ae.relationship = 'supports' THEN 1 ELSE 0 END)` — counts **evidence links** (wrong unit)

One assertion with 3 supporting facts: `total_assertions = 1`, `supported_count = 3`. Downstream consumers comparing these will get nonsensical ratios (300% supported?).

**Fix:** Use `COUNT(DISTINCT CASE WHEN ae.relationship = 'supports' THEN a.id END)` for all relationship counts, matching the unit of `total_assertions`.

---

### #4. Two methods bypass `_row_to_dict` [MEDIUM]

**Files:**
- `src/evidence.py:498` — `get_evidence_summary_for_ticker` uses `dict(row)` instead of `_row_to_dict(row)`. This skips JSON deserialization. Currently no JSON columns in the result, but the pattern violation means future changes adding JSON fields would silently break.
- `src/evidence.py:702-726` — `get_ticker_evidence_summary` uses `.fetchone()["c"]` directly on 5 queries. Not a `_row_to_dict` issue (it's extracting scalar counts), but it means these results never flow through the standard conversion pipeline.

**Fix for line 498:** Change `dict(row)` to `_row_to_dict(row)`.

---

### #5. `assertions` table has no UNIQUE constraint — duplicates accumulate silently [MEDIUM]

**Schema:** `db/evidence_schema.sql:68-78`

The `assertions` table has NO UNIQUE constraint. Running assertion extraction twice on the same report creates duplicate rows. `batch_insert_assertions` will happily insert them because no IntegrityError fires.

`delete_assertions_for_report(report_path)` exists as a cleanup path, but nothing prevents duplicates from accumulating if the caller forgets to delete first. There's no `upsert_assertion` method or idempotency guard.

**Fix options:**
- Add `UNIQUE(report_path, assertion_text)` or `UNIQUE(ticker, report_path, umbrella_number, assertion_text)`.
- Or: document that callers MUST call `delete_assertions_for_report` before re-inserting, and add a defensive check in `batch_insert_assertions`.

---

### #6. `insert_semantic_diff` catches IntegrityError for a table with no UNIQUE [MEDIUM]

**File:** `src/evidence.py:577-593`

The try/except at line 592 catches `sqlite3.IntegrityError` and raises `DuplicateEntryError("semantic_diffs", ...)`. But `semantic_diffs` has **no UNIQUE constraint**. The only IntegrityError possible here is a NOT NULL violation (e.g., missing `ticker`, `section_key`, `period_a`, `period_b`, `diff_type`, or `summary`). Labeling a NOT NULL failure as "DuplicateEntryError" is semantically misleading.

**Fix:** Either remove the try/except (let NOT NULL failures propagate naturally) or catch and raise a more appropriate error.

---

### #7. Batch insert methods don't rollback pending rows on failure [MEDIUM]

**File:** `src/evidence.py:221-246, 365-384`

When `executemany()` hits an IntegrityError mid-batch (e.g., duplicate at row 7 of 10), the except block re-raises as `DuplicateEntryError` without calling `self.conn.rollback()`. Python's `sqlite3` module opens an implicit transaction for DML, so rows 1-6 sit in a pending transaction. They are NOT committed yet, but they WILL be silently committed by the next `self.conn.commit()` call from any subsequent method. The caller receives an error, potentially retries or moves on, and the partial rows persist without anyone knowing.

**Fix:** Add `self.conn.rollback()` before `raise DuplicateEntryError(...)` in both batch methods.

---

### #8. Batch insert methods return `len(prepared)` instead of cursor rowcount [MEDIUM]

**File:** `src/evidence.py:242, 379`

`batch_insert_facts` returns `len(prepared)` (the count of input dicts). `batch_insert_assertions` does the same. Neither captures the cursor from `executemany()` to check `cursor.rowcount`, which is the actual number of rows affected. If `executemany` silently skips any row, the returned count is wrong.

**Fix:** Capture the cursor: `cur = self.conn.executemany(...)`, return `cur.rowcount`.

---

### #9. `idx_extracted_facts_active` on boolean column is nearly useless [LOW]

**Schema:** `db/evidence_schema.sql:146`

An index on a column with only two values (0 and 1) provides almost no selectivity. The query optimizer will rarely use it for single-column lookups. The index adds write overhead (every INSERT/UPDATE on is_active maintains it) for negligible read benefit.

**Fix:** Replace with a composite index that actually helps the queries: `(ticker, is_active)` or `(source_document_id, is_active)`.

---

### #10. No delete methods for source_documents or document_sections [LOW]

**File:** `src/evidence.py` — entire file

There is no `delete_source_document()` or `delete_document_sections()` method. Cleaning up a filing requires manual ordered deletion (assertion_evidence → facts → sections → document) due to FK constraints (all default to RESTRICT). No convenience method exists for this lifecycle operation.

The soft-delete path (`deactivate_facts_for_document`) handles re-extraction but not cleanup of abandoned or erroneously inserted filings.

**Fix:** Add a `delete_source_document(doc_id)` method that deletes in the correct FK order, or at minimum document the required deletion sequence.

---

### #11. FK deletion behavior not audited beyond assertion_evidence [LOW]

**Schema:** `db/evidence_schema.sql`

The schema has the following FK relationships, all defaulting to RESTRICT (except the one CASCADE):

| FK | Default Behavior | Impact |
|----|-----------------|--------|
| `document_sections.source_document_id → source_documents.id` | RESTRICT | Can't delete a source_document that has sections |
| `extracted_facts.source_document_id → source_documents.id` | RESTRICT | Can't delete a source_document that has facts |
| `extracted_facts.document_section_id → document_sections.id` | RESTRICT | Can't delete a section that has facts |
| `assertion_evidence.assertion_id → assertions.id` | CASCADE | Deleting assertion auto-deletes evidence links |
| `assertion_evidence.extracted_fact_id → extracted_facts.id` | RESTRICT | Can't delete a fact that has evidence links (issue #1) |

This means the only safe deletion path without hitting FK errors is: assertion_evidence → extracted_facts → document_sections → source_documents. Any deviation raises IntegrityError. This is correct referential integrity but creates a maintenance burden given that no convenience methods exist (issue #10).

---

### #12. `test_confidence_required` tests the wrong thing [LOW]

**File:** `tests/test_evidence.py:276-280`

The test deletes the `confidence` key from the dict and catches generic `Exception`. This tests Python's named parameter binding failure (`:confidence` KeyError from missing key), NOT the SQL `NOT NULL` constraint. A proper test would pass `confidence=None` and verify the database rejects the NULL value with an IntegrityError.

**Fix:** Change to `fact = self._sample_fact(fact_key="test_no_conf", confidence=None)` and assert `sqlite3.IntegrityError` (or a more specific exception).

---

### #13. `get_facts_for_ticker` default `limit=500` is a silent truncation risk [LOW]

**File:** `src/evidence.py:261`

A ticker with 5+ years of filings and 70+ facts per filing easily exceeds 500 rows. Callers have no indication that results were truncated — the method returns a list with exactly 500 items and no flag.

**Fix options:**
- Default to no limit (or a much higher limit like 5000).
- Return a tuple `(results, truncated: bool)`.
- Document the default prominently in the docstring.

---

### #14. Inline `import json` in `update_assertion_evidence` [LOW]

**File:** `src/evidence.py:516`

`json` is imported inside the method body. Every other JSON-handling path goes through `_decimal_fields_from_dict`. This method bypasses that pattern by doing manual `json.dumps()` on `verification_detail_json`.

**Fix:** Add `import json` at module level (line 11), or refactor to process the fields dict through `_decimal_fields_from_dict`.

---

### #15. `get_diffs_for_ticker` missing `diff_type` filter [LOW]

**File:** `src/evidence.py:595-614`

The method supports `section_key` and `min_significance` filters but not `diff_type`. Callers wanting only "added" or "changed" diffs must filter in Python. One-line addition to the conditions builder.

---

### #16. `update_source_document` has zero test coverage with dynamic SQL [LOW]

**File:** `src/evidence.py:114-130`

This method uses f-string column name interpolation (`f"UPDATE source_documents SET {', '.join(sets)} WHERE id = ?"`) — the same dynamic SQL pattern flagged elsewhere. Column names are whitelisted (safe), but the method has zero test coverage. Any bug in the SET construction or the allowed-column list would go undetected.

---

### #17. `get_evidence_summary_for_ticker` returns NULL for SUM columns on empty result [HIGH]

**File:** `src/evidence.py:483-502`

When a ticker has zero assertions, the aggregate query still returns a row (SQL aggregate queries always do), so the `dict(row)` fallback at line 498 is **unreachable**. The returned row has: `COUNT(DISTINCT a.id) = 0` (integer), but `SUM(CASE WHEN ae.relationship = 'supports' ...)` returns **NULL** (not 0). Callers expecting integers for `supported_count`, `contradicted_count`, `partial_count`, `unverifiable_count` get `None`.

**Fix:** Wrap all SUM expressions in `COALESCE(SUM(...), 0)`.

---

### #18. `get_facts_for_section` missing `include_inactive` parameter [MEDIUM]

**File:** `src/evidence.py:293-298`

This method always filters `is_active = 1` with no override:
```python
"SELECT * FROM extracted_facts WHERE document_section_id = ? AND is_active = 1 ORDER BY fact_key"
```

Both `get_facts_for_document` (line 285) and `get_facts_for_ticker` (line 254) have `include_inactive` parameters. This is an inconsistent API surface — one of three fact-query methods silently omits inactive facts with no way to override.

**Fix:** Add `include_inactive: bool = False` parameter matching the other two methods.

---

### #19. `update_assertion_evidence` silently no-ops on non-existent rows [MEDIUM]

**File:** `src/evidence.py:504-526`

The UPDATE executes against `(assertion_id, extracted_fact_id)` but doesn't check `cursor.rowcount`. If no matching row exists, the method returns `None` without any error or warning. The caller has no way to know the update didn't apply.

**Fix:** After execute, check `cur.rowcount == 0` and either raise an error or return a boolean indicating success.

---

### #20. Two confusingly similar method names [LOW]

**File:** `src/evidence.py:483, 700`

- `get_evidence_summary_for_ticker` (line 483) — returns assertion/evidence link counts from a LEFT JOIN
- `get_ticker_evidence_summary` (line 700) — returns cross-table aggregate (docs, facts, assertions, verification, diffs)

Near-identical names, completely different return shapes. Will cause caller confusion.

**Fix:** Rename one for clarity. E.g., `get_verification_summary_for_ticker` (line 483) and `get_ticker_evidence_summary` (line 700), making the distinction between verification-specific and cross-table clear.

---

### #21. `batch_insert_facts` doesn't capture the cursor from `executemany()` [MEDIUM]

**File:** `src/evidence.py:227-244`

The method calls `self.conn.executemany(...)` without capturing the cursor, then returns `len(prepared)` as the count. Should capture `cur = self.conn.executemany(...)` and use `cur.rowcount` for the actual affected row count. Same issue in `batch_insert_assertions` (line 371-380). (Related to but distinct from #8 — #8 flags the wrong return value, this flags the missing cursor capture.)

---

## Notes on f-string SQL Pattern

The review initially called out the f-string SQL pattern only for `update_source_document` (#16) and `get_facts_for_document` (original L1). In practice, this is a **pervasive pattern** across the codebase:

- `update_source_document` (line 128) — dynamic SET from whitelisted columns
- `update_assertion_evidence` (line 523) — dynamic SET from whitelisted columns
- `get_facts_for_ticker` (line 280) — dynamic WHERE from conditions builder
- `get_facts_for_document` (line 288) — inline active_clause toggle
- `get_diffs_for_ticker` (line 611) — dynamic WHERE from conditions builder

All are safe (column names and clause fragments are hardcoded, never from user input). This is a conscious pattern choice in the codebase, not a one-off deviation.

---

## Note on FK Enforcement Dependency

`PRAGMA foreign_keys=ON` is set per-connection in `Database.connect()` (`database.py:115`), not in the schema file. All FK enforcement tests depend on this. If anyone uses `evidence_schema.sql` directly against a raw `sqlite3` connection (e.g., `sqlite3 :memory: < db/evidence_schema.sql`), FKs won't be enforced. This is a dependency to be aware of, not a bug — SQLite defaults foreign keys to OFF.

---

## Note on Issue #3 Fix Semantics

The suggested fix for #3 (`COUNT(DISTINCT CASE WHEN ae.relationship = 'supports' THEN a.id END)`) correctly matches the unit of `total_assertions`. However: an assertion with **both** "supports" and "contradicts" evidence links will be counted in both `supported_count` and `contradicted_count`. This means `supported_count + contradicted_count + partial_count + unverifiable_count` could exceed `total_assertions`. This may be desirable (it surfaces conflicting evidence) but should be documented explicitly.

---

## Part 5: Functional Verification Plan

### 5.1 Schema Validity
```bash
sqlite3 :memory: < db/evidence_schema.sql && echo "PASS"
```

### 5.2 Migration Roundtrip
```python
from src.database import Database
db = Database(":memory:")
db.init_db()
db.migrate()
# Verify schema_version is 3
# Verify all 8 evidence tables exist
# Verify all 16 indexes exist
# Verify original 10 tables still present
```

### 5.3 Test Suite
```bash
python3 -m unittest tests.test_evidence -v
```
Expected: 39 passed.

### 5.4 Real Database Safety
```bash
cp db/portfolio.db db/portfolio.db.bak
python3 -c "from src.database import Database; db = Database(); db.migrate()"
# Verify existing data intact
# Verify 8 new tables exist
# Verify schema_version shows 3
```

### 5.5 FK Violation Reproduction (validates #1)
```python
# Insert document → insert fact → insert assertion → link via assertion_evidence
# Then: delete_facts_for_extraction_run(run_id) → currently unhandled IntegrityError
```

### 5.6 Stale Evidence Reproduction (validates #2)
```python
# Insert document → insert fact → insert assertion → link via assertion_evidence
# Deactivate the fact (is_active=0)
# Call get_evidence_for_assertion → verify stale fact data is still returned
```

### 5.7 Summary Unit Mismatch Reproduction (validates #3)
```python
# Insert 1 assertion → link it to 3 facts (all 'supports')
# Call get_evidence_summary_for_ticker
# Observe: total_assertions=1, supported_count=3 (not 1)
```

---

## Verdict

**NEEDS FIXES** — 1 critical, 3 high, 8 medium, 9 low.

The overall implementation quality is high: excellent SQL convention conformance, 39 well-written tests with realistic data, justified spec deviations (is_active flag, UNIQUE on facts, confidence NOT NULL, ON DELETE CASCADE on assertions). The FK safety gap (#1), stale evidence leak (#2), summary unit mismatch (#3), and NULL aggregates (#17) are the issues that will cause production bugs.

---

## Required Changes Before Merge (ordered by severity)

1. **[CRITICAL] Fix `delete_facts_for_extraction_run` FK safety** (`evidence.py:333-341`)
   - Refuse hard-delete when evidence links exist. Raise a clear error directing callers to `deactivate_facts_for_document`.
   - Add test: insert fact → link to assertion → call delete → verify error raised.

2. **[HIGH] Fix stale evidence in `get_evidence_for_assertion`** (`evidence.py:464`)
   - Add `AND f.is_active = 1` to the JOIN, or add `include_inactive` parameter defaulting to False.
   - Same fix for `get_evidence_for_fact` (line 474).
   - Add test: deactivate fact → query evidence → verify stale fact excluded (or is_active exposed).

3. **[HIGH] Fix unit mismatch in `get_evidence_summary_for_ticker`** (`evidence.py:489-492`)
   - Change `SUM(CASE WHEN ae.relationship = 'supports' ...)` to `COUNT(DISTINCT CASE WHEN ae.relationship = 'supports' THEN a.id END)` for all relationship columns.
   - Wrap in COALESCE for NULL safety (see #17).
   - Note: an assertion with both "supports" and "contradicts" evidence will be counted in both. Document this.
   - Add test: 1 assertion with 3 supporting facts → verify supported_count = 1 (not 3).

4. **[HIGH] Fix NULL aggregates in `get_evidence_summary_for_ticker`** (`evidence.py:489-492`)
   - Wrap all `SUM(CASE ...)` in `COALESCE(..., 0)` to prevent NULL returns for zero-assertion tickers.
   - Remove unreachable fallback dict at line 498 or convert to documented defensive code.
   - Add test: query summary for ticker with zero assertions → verify all counts are 0 (integer), not None.

5. **[MEDIUM] Fix `dict(row)` bypass in `get_evidence_summary_for_ticker`** (`evidence.py:498`)
   - Change `dict(row)` to `_row_to_dict(row)`.

6. **[MEDIUM] Add rollback in batch insert methods** (`evidence.py:245, 383`)
   - Add `self.conn.rollback()` before `raise DuplicateEntryError(...)` in both methods.

7. **[MEDIUM] Fix batch insert cursor capture and return value** (`evidence.py:227-244, 371-380`)
   - Capture cursor from `executemany()`: `cur = self.conn.executemany(...)`.
   - Return `cur.rowcount` instead of `len(prepared)`.

8. **[MEDIUM] Fix `insert_semantic_diff` error handling** (`evidence.py:592`)
   - Remove misleading DuplicateEntryError for a table with no UNIQUE constraint, or add a UNIQUE constraint if duplicates should be prevented.

9. **[MEDIUM] Guard against assertion duplicates** (`evidence.py`, `evidence_schema.sql`)
   - Either add UNIQUE constraint to assertions table, or add defensive check / documented contract that callers must delete before re-inserting.

10. **[MEDIUM] Add `include_inactive` to `get_facts_for_section`** (`evidence.py:293-298`)
    - Match the API surface of `get_facts_for_document` and `get_facts_for_ticker`.

11. **[MEDIUM] Fix silent no-op in `update_assertion_evidence`** (`evidence.py:504-526`)
    - Check `cursor.rowcount` after UPDATE. If 0, raise an error or return a boolean.

---

## Optional Improvements

- Replace `idx_extracted_facts_active` with composite index `(ticker, is_active)` for actual query benefit
- Add `delete_source_document()` convenience method with correct FK-ordered deletion
- Fix `test_confidence_required` to test SQL NOT NULL (pass `confidence=None`) instead of Python KeyError
- Increase or remove `get_facts_for_ticker` default limit=500
- Add `import json` at module level instead of inline at line 516
- Add `diff_type` filter to `get_diffs_for_ticker`
- Add test coverage for `update_source_document` (has dynamic SQL with zero tests)
- Add test for `get_evidence_for_fact` (reverse lookup)
- Document `is_active` soft-delete lifecycle in schema header
- Add test for migration idempotency
- Rename `get_evidence_summary_for_ticker` / `get_ticker_evidence_summary` to distinguish them clearly
- Add `extraction_method` filter to `get_facts_for_ticker` for Phase 4+ use

---

## Resolution of Pre-Review Checklist Items (30 items)

| # | Item | Resolution |
|---|------|-----------|
| 1 | UNIQUE too tight? | **PASS** — 10-K/A distinct doc_type; split sections use suffixed keys; computation_cache upsert overwrites |
| 2 | UNIQUE too loose on extracted_facts? | **FIXED** — UNIQUE(source_document_id, fact_key, fiscal_period) added |
| 3 | FK cascading behavior | **PARTIAL** — CASCADE on assertion side; fact-side FK RESTRICT causes crash (#1); no delete methods for documents/sections (#10, #11) |
| 4 | Missing indexes | **FIXED** — 4 extra indexes added (but is_active index has poor selectivity, #9) |
| 5 | Column type decisions | **IMPROVED** — confidence NOT NULL without default; value contract documented |
| 6 | Section splitting vs UNIQUE | **PASS** — suffixed keys documented |
| 7 | Temporal data model | **FIXED** — `is_active` flag (but evidence queries don't filter on it, #2) |
| 8 | Fresh install migration | **FIXED** — init_db inserts v1, migrate walks all steps |
| 9 | Migration atomicity | **PARTIALLY FIXED** — IF NOT EXISTS makes retry idempotent |
| 10 | _JSON_COLUMNS extension | **PASS** — new frozenset with all 12 entries |
| 11 | Schema version row | **PASS** — version 3 inserted after DDL, before commit |
| 12 | Separate class or extension? | **PASS** — separate EvidenceDB class, shares connection |
| 13 | Decimal handling | **PASS** — uses _decimal_fields_from_dict consistently |
| 14 | Row-to-dict conversion | **FAIL** — two methods bypass _row_to_dict (#4) |
| 15 | Error handling | **ISSUE** — misleading DuplicateEntryError on semantic_diffs (#6) |
| 16 | Logging | **PASS** — debug for individual ops, info for bulk/deletes |
| 17 | Provenance chain | **PASS** — `get_fact_with_provenance` JOINs facts → sections → documents |
| 18 | extraction_run_id | **PASS** — string tag, grouped/deletable by run |
| 19 | assertion_evidence relationship | **ISSUE** — unit mismatch in summary (#3) |
| 20 | Cross-period fact identity | **DEFERRED** — Phase 6 concern |
| 21 | Write volume / batching | **FIXED** — `batch_insert_facts/assertions` with executemany (but return value wrong, #8) |
| 22 | Query patterns indexed | **PARTIAL** — most common queries have coverage, but `get_evidence_for_fact` orders by `verified_at DESC` (no index), `get_assertions_for_ticker` with umbrella filter orders by `id` not `umbrella_number` (suboptimal index use), and `is_active` index has poor selectivity (#9) |
| 23 | Cache invalidation blast radius | **PASS** — deactivate soft-deletes, invalidate hard-deletes cache |
| 24 | Phase 4 dependency | **PASS** — assertions independent of facts |
| 25 | Phase 6 dependency | **PASS** — period format consistent |
| 26 | Phase 7 dependency | **PASS** — EvidenceDB takes Database instance |
| 27 | Non-US tickers | **PASS** — schema allows doc_type='financials.md' |
| 28 | Empty filings | **PASS** — content_text NOT NULL enforced |
| 29 | Re-running extraction | **ISSUE** — no uniqueness guard on assertions (#5) |
| 30 | Fresh clone, no DB | **FIXED** — init_db + migrate creates all tables at v3 |
