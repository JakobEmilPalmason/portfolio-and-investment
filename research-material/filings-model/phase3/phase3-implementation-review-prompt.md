# Phase 3 Implementation Review — Reviewer Prompt

You are reviewing the implementation of Phase 3 (Database Schema + Evidence Storage) of the Evidence and Extraction Layer. Your job is to verify what was built, catch shortcuts, find bugs, and confirm the code is production-ready before any downstream phase builds on top of it.

## Context

This project is a Buffett-style investment analysis pipeline. The existing database (`db/portfolio.db`, schema v2) has 10 tables for paper trading. Phase 3 adds 8 evidence tables for storing facts extracted from SEC filings with full provenance (every fact traces to a source quote in a filing).

**Phase 3 is storage only** — no EDGAR fetching, no LLM calls, no extraction logic. Just the schema and the Python read/write layer.

## Your Inputs

Read these files in order:

1. **The plan:** `research-material/filings-model/masterplan.md` — Section 5 (Phase 3), Section 7 (full schema), Section 6 (integration points), Section 9 (risk analysis)
2. **The plan TLDR:** `research-material/filings-model/masterplan-tldr.md` — Phase 3 section
3. **The known issues list:** `research-material/filings-model/phase3-review-prompt.md` — 30-item checklist with pre-identified risks
4. **The existing database layer:** `src/database.py` — this is the pattern bible. Every convention in the new code must match.
5. **The existing schema:** `db/schema.sql` — DDL conventions, column naming, index naming
6. **The new schema:** `db/evidence_schema.sql` — the 8 new tables
7. **The new Python layer:** `src/evidence.py` — the EvidenceDB class
8. **The tests:** `tests/test_evidence.py`
9. **Any modifications to:** `src/database.py` (the 3 surgical edits: version bump, JSON columns, migration)

---

## Part 1: Plan vs Implementation Checklist

For each item below, verify whether the implementation matches the plan. State **DONE**, **PARTIAL**, **MISSING**, or **DEVIATED** with an explanation.

### 1.1 Schema Completeness

| Table | Planned | Check |
|-------|---------|-------|
| `source_documents` | 11 columns + UNIQUE(ticker, doc_type, period_end) | Verify all columns present with correct types and constraints |
| `document_sections` | 9 columns + UNIQUE(source_document_id, section_key) | Verify FK to source_documents, NOT NULL on content_text |
| `extracted_facts` | 19 columns, no UNIQUE | Verify all columns including source_char_offset_start/end, computation_trace_json |
| `assertions` | 9 columns | Verify assertion_type and requires_arithmetic columns |
| `assertion_evidence` | 9 columns + UNIQUE(assertion_id, extracted_fact_id) | Verify both FKs, relationship TEXT NOT NULL |
| `verification_runs` | 12 columns + UNIQUE run_id | Verify run_metadata_json column |
| `semantic_diffs` | 10 columns | Verify significance INTEGER DEFAULT 3 |
| `computation_cache` | 10 columns + UNIQUE(ticker, computation_key) | Verify inputs_json and formula NOT NULL |

For each table, check:
- Every column from the plan exists with the correct type
- No extra columns were added without justification
- No columns were silently dropped
- DEFAULT values match the plan
- NOT NULL constraints match the plan
- UNIQUE constraints match the plan
- FK REFERENCES are correct (table and column)

### 1.2 Index Completeness

The plan specifies 13 indexes. Verify each exists:

| Index | On |
|-------|----|
| `idx_source_documents_ticker` | source_documents(ticker) |
| `idx_document_sections_document` | document_sections(source_document_id) |
| `idx_extracted_facts_ticker` | extracted_facts(ticker) |
| `idx_extracted_facts_key` | extracted_facts(fact_key) |
| `idx_extracted_facts_period` | extracted_facts(fiscal_period) |
| `idx_assertions_ticker` | assertions(ticker) |
| `idx_assertions_umbrella` | assertions(umbrella_number) |
| `idx_assertion_evidence_assertion` | assertion_evidence(assertion_id) |
| `idx_assertion_evidence_fact` | assertion_evidence(extracted_fact_id) |
| `idx_verification_runs_ticker` | verification_runs(ticker) |
| `idx_semantic_diffs_ticker` | semantic_diffs(ticker) |
| `idx_computation_cache_ticker` | computation_cache(ticker) |

Also check: were any additional indexes added? Were any of the planned ones dropped?

### 1.3 database.py Modifications

Three surgical edits were planned:

| Edit | What | Where |
|------|------|-------|
| A | `SCHEMA_VERSION = 2` → `SCHEMA_VERSION = 3` | Line 19 |
| B | Add 5 JSON columns to `_JSON_COLUMNS` frozenset | Lines 24-32 |
| C | Add `if current < 3:` migration block after the `if current < 2:` block | After line 207 |

For each edit:
- Was it done exactly as planned?
- Were any other lines in database.py changed? If so, why? Was it necessary?
- Edit B: verify the exact column names added match the column names in evidence_schema.sql (they must be identical strings)
- Edit C: verify the migration reads evidence_schema.sql from the correct path, inserts version 3 into schema_version, and commits

### 1.4 EvidenceDB Class

The plan specifies ~40 methods. Verify:

**Source documents (5 methods):**
- [ ] `insert_source_document` — inserts, raises DuplicateEntryError on conflict
- [ ] `get_source_document` — by id
- [ ] `get_source_documents_for_ticker` — by ticker
- [ ] `get_source_document_by_key` — by (ticker, doc_type, period_end)
- [ ] `update_source_document` — updates existing row

**Document sections (4 methods):**
- [ ] `insert_document_section` — inserts, raises DuplicateEntryError on conflict
- [ ] `get_document_sections` — by source_document_id, ordered by section_order
- [ ] `get_document_section_by_key` — by (source_document_id, section_key)
- [ ] `upsert_document_section` — INSERT OR REPLACE

**Extracted facts (7 methods):**
- [ ] `insert_extracted_fact` — inserts single fact
- [ ] `get_extracted_fact` — by id
- [ ] `get_facts_for_ticker` — multi-filter (by ticker, optional fact_type, fact_key, fiscal_period, extraction_method)
- [ ] `get_facts_for_document` — by source_document_id
- [ ] `get_facts_for_section` — by document_section_id
- [ ] `get_facts_by_extraction_run` — by extraction_run_id
- [ ] `delete_facts_for_extraction_run` — deletes by extraction_run_id

**Assertions (5 methods):**
- [ ] `insert_assertion` — inserts
- [ ] `get_assertion` — by id
- [ ] `get_assertions_for_ticker` — by ticker
- [ ] `get_unverified_assertions` — LEFT JOIN to assertion_evidence, returns assertions with no evidence links
- [ ] `delete_assertions_for_report` — deletes by report_path, cascades to assertion_evidence manually

**Assertion evidence (5 methods):**
- [ ] `insert_assertion_evidence` — inserts, raises DuplicateEntryError on conflict
- [ ] `get_evidence_for_assertion` — JOIN to extracted_facts, enriched rows
- [ ] `get_evidence_for_fact` — reverse lookup: which assertions use this fact
- [ ] `get_evidence_summary_for_ticker` — aggregate counts (supported, contradicted, etc.)
- [ ] `update_assertion_evidence` — updates match_score, relationship, etc.

**Verification runs (4 methods):**
- [ ] `insert_verification_run` — inserts, raises DuplicateEntryError on duplicate run_id
- [ ] `get_verification_run` — by run_id
- [ ] `get_verification_runs_for_ticker` — by ticker
- [ ] `get_latest_verification_run` — by ticker, most recent run_date

**Semantic diffs (5 methods):**
- [ ] `insert_semantic_diff` — inserts
- [ ] `get_diffs_for_ticker` — multi-filter (optional section_key, diff_type)
- [ ] `get_diffs_between_periods` — by ticker, period_a, period_b
- [ ] `get_high_significance_diffs` — significance >= threshold
- [ ] `delete_diffs_between_periods` — deletes by ticker, period_a, period_b

**Computation cache (4 methods):**
- [ ] `upsert_computation` — INSERT OR REPLACE
- [ ] `get_computation` — by ticker, computation_key
- [ ] `get_computations_for_ticker` — by ticker
- [ ] `invalidate_computations` — deletes by ticker (or ticker + key prefix)

**Cross-table (2 methods):**
- [ ] `get_ticker_evidence_summary` — counts across all tables for a ticker
- [ ] `get_fact_with_provenance` — JOIN extracted_facts → document_sections → source_documents

For every missing method: flag it. For every extra method: ask why.

### 1.5 Tests

The plan specifies 16 tests. Verify each:

| # | Test | What it covers |
|---|------|---------------|
| 1 | Schema version is 3 after migration | Migration correctness |
| 2 | Insert + get source_document round-trip | All fields survive |
| 3 | Duplicate source_document raises DuplicateEntryError | UNIQUE enforcement |
| 4 | Insert + get document_sections ordered by section_order | Ordering correctness |
| 5 | Upsert document_section updates content | Upsert behavior |
| 6 | Insert + get extracted_facts | Basic CRUD |
| 7 | JSON column round-trip (computation_trace_json dict→dict) | Auto-serialization |
| 8 | Insert + get assertions ordered by umbrella_number | Ordering |
| 9 | Unverified assertions query (LEFT JOIN correctness) | Complex query |
| 10 | Insert + get assertion_evidence (JOIN enrichment) | Join correctness |
| 11 | Duplicate assertion_evidence raises DuplicateEntryError | UNIQUE enforcement |
| 12 | Insert + get verification_run (run_metadata_json round-trip) | JSON + CRUD |
| 13 | Semantic diffs with significance filtering | Filter correctness |
| 14 | Upsert computation_cache updates result | Upsert behavior |
| 15 | Foreign key enforcement (invalid source_document_id fails) | FK integrity |
| 16 | ticker_evidence_summary end-to-end counts | Cross-table query |

For each: does the test exist? Does it actually test what it claims? Are assertions specific (exact values) or vague (`assertIsNotNone`)?

---

## Part 2: Convention Conformance

The new code must match `src/database.py` conventions exactly. Check each:

### 2.1 SQL Conventions (compare evidence_schema.sql against db/schema.sql)

- [ ] Every table has `id INTEGER PRIMARY KEY` as first column
- [ ] Every table has `created_at TEXT DEFAULT (datetime('now'))` as last column
- [ ] Column types use only: TEXT, INTEGER, REAL (no BOOLEAN, no BLOB, no VARCHAR)
- [ ] Booleans are INTEGER (0/1) not TEXT
- [ ] All NOT NULL constraints match what makes semantic sense (required fields)
- [ ] JSON columns are suffixed `_json` (e.g., `computation_trace_json`, not `computation_trace`)
- [ ] REFERENCES use inline syntax: `column INTEGER REFERENCES table(id)`, not separate FK constraints
- [ ] UNIQUE constraints use table-level syntax: `UNIQUE(col1, col2)`
- [ ] Index names follow pattern: `idx_{table}_{column}` (e.g., `idx_extracted_facts_ticker`)
- [ ] No PRAGMAs in the schema file (those belong in connection setup)
- [ ] `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` — idempotent DDL

### 2.2 Python Conventions (compare src/evidence.py against src/database.py)

- [ ] Module-level `logger = logging.getLogger(__name__)`
- [ ] EvidenceDB takes `Database` instance, accesses `db.conn` — does NOT create its own connection
- [ ] All reads use `_row_to_dict()` on every row returned
- [ ] All writes use `_decimal_fields_from_dict()` before INSERT/UPDATE
- [ ] All writes call `self.db.conn.commit()` after execution
- [ ] IntegrityError catches raise `DuplicateEntryError(table, ticker, message)` with table name and ticker
- [ ] Methods return `int` (row id) for inserts, `dict` for single reads, `list[dict]` for multi reads
- [ ] SQL uses parameterized queries (`?` placeholders), never f-strings or string concatenation
- [ ] No raw SQL string building for WHERE clauses — if dynamic filters are needed, build a list of conditions and params safely
- [ ] Type hints on all method signatures
- [ ] Docstrings on public methods (even brief ones)

### 2.3 Import Hygiene

- [ ] `from src.database import Database, DuplicateEntryError, _row_to_dict, _decimal_fields_from_dict` — exactly these imports, nothing more
- [ ] No new external dependencies (no pydantic, no dataclasses beyond stdlib)
- [ ] No circular imports

---

## Part 3: Known Risk Items

The pre-review identified specific risks. For each, verify whether the implementation addressed it or ignored it.

### 3.1 Fresh Install Bug (CRITICAL)

`database.py:init_db()` inserts `SCHEMA_VERSION` directly on fresh databases. If `SCHEMA_VERSION = 3` but `init_db()` only runs `schema.sql` (v1 tables), then the DB is at "version 3" with no v2 or v3 tables. `migrate()` sees `current >= SCHEMA_VERSION` and skips everything.

**Check:** Does the implementation fix this? Possible fixes:
- `init_db()` inserts version 1 instead of `SCHEMA_VERSION`
- `init_db()` also runs evidence_schema.sql
- `init_db()` calls `migrate()` after initial schema creation
- None of the above (bug still present)

If unfixed: this breaks every `:memory:` test and every fresh clone. **This is a showstopper.**

### 3.2 executescript() Atomicity

`executescript()` issues an implicit COMMIT before running, then executes each statement individually (no wrapping transaction). If the evidence schema has a syntax error in table 5 of 8, tables 1-4 exist but version stays at 2.

**Check:** Is the migration recovery-safe? On re-run after partial failure, does `IF NOT EXISTS` make it idempotent? Does the version insert happen only after all tables are created?

### 3.3 No UNIQUE on extracted_facts

Without a UNIQUE constraint, duplicate facts accumulate silently if the delete-before-insert pattern isn't followed.

**Check:** Did the implementation add a UNIQUE constraint? If not, is there defensive logic (e.g., a check before insert, or documented contract that callers must delete first)?

### 3.4 Manual Cascade Deletion

No `ON DELETE CASCADE` means code must manually delete child rows before parent rows.

**Check:** Does `delete_assertions_for_report` delete `assertion_evidence` rows first? Does `delete_facts_for_extraction_run` handle linked `assertion_evidence` rows? Walk through the deletion order for each delete method and verify FK integrity won't block it.

### 3.5 JSON Column Name Mismatch

The 5 new JSON column names added to `_JSON_COLUMNS` in database.py must exactly match the column names in evidence_schema.sql. A single typo means that column's values are stored as raw JSON strings and returned as raw strings (not deserialized).

**Check:** List the 5 names from `_JSON_COLUMNS` and the corresponding column names from the schema DDL side by side. Do they match character-for-character?

### 3.6 Amended Filing Handling

`UNIQUE(ticker, doc_type, period_end)` on source_documents — does the code handle 10-K vs 10-K/A? Is there a comment or method that addresses amended filings?

---

## Part 4: Shortcut Detection

Reviewers often miss corners that were cut. Explicitly check for these patterns:

### 4.1 Stub Methods

Are any methods empty or raise `NotImplementedError`? Check every method body — does it actually execute SQL and return results, or is it a placeholder?

### 4.2 Hardcoded Test Data

Do tests use realistic data (real-looking tickers, realistic column values) or minimal stubs (`ticker="X"`, `fact_value="test"`)? Minimal stubs can pass while hiding type/format bugs.

### 4.3 Untested Error Paths

- Does any test verify that FK violations raise errors? (Test #15)
- Does any test verify behavior when querying an empty table? (No rows → empty list, not crash)
- Does any test verify that `get_unverified_assertions` correctly excludes assertions that DO have evidence? (Requires inserting both verified and unverified assertions)
- Does any test verify the manual cascade in `delete_assertions_for_report`?

### 4.4 Missing Filter Parameters

The plan says `get_facts_for_ticker` supports multi-filter (optional fact_type, fact_key, fiscal_period, extraction_method). Check: does the implementation actually accept and use all these filters, or does it only filter by ticker?

### 4.5 Missing Ordering

- `get_document_sections` should order by `section_order`
- `get_assertions_for_ticker` should order by `umbrella_number`
- `get_verification_runs_for_ticker` should order by `run_date DESC`
- `get_diffs_for_ticker` should have some meaningful ordering

Check: are ORDER BY clauses present and correct?

### 4.6 Commit-per-Row vs Batch

Does every write method call `commit()` individually? If so, is there any batch method or at least a note about future batch support? 50 individual commits per ticker extraction is measurably slow.

### 4.7 SQL Injection Surface

Check every method that builds SQL dynamically (especially multi-filter methods). Are all values passed as `?` parameters? Is any string concatenation used to build WHERE clauses? Even internal-only code should use parameterized queries — future callers may pass untrusted data.

---

## Part 5: Functional Verification

Run these checks (don't just read the code — actually verify):

### 5.1 Schema Validity
```bash
sqlite3 :memory: < db/evidence_schema.sql
echo $?  # must be 0
```

### 5.2 Migration Roundtrip
```python
from src.database import Database
db = Database(":memory:")
db.init_db()
db.migrate()
# Verify: schema_version is 3
# Verify: all 8 evidence tables exist (query sqlite_master)
# Verify: all 13 indexes exist
# Verify: original 10 tables still exist and are intact
```

### 5.3 Full CRUD Roundtrip
Insert a source_document → insert a section → insert a fact → insert an assertion → link them via assertion_evidence → read everything back → verify all fields match, JSON columns are dicts not strings, FKs are enforced.

### 5.4 Test Suite
```bash
python3 -m pytest tests/test_evidence.py -v
```
All 16 tests must pass. Check for any skipped or xfailed tests.

### 5.5 Existing Tests Still Pass
```bash
python3 -m pytest tests/ -v
```
Phase 3 changes to `database.py` must not break existing tests.

### 5.6 Real Database Safety
```bash
cp db/portfolio.db db/portfolio.db.bak
python3 -c "from src.database import Database; db = Database(); db.migrate()"
# Verify: existing data intact (spot-check positions, transactions)
# Verify: 8 new tables exist
# Verify: schema_version shows 3
```

---

## Output Format

Structure your review as:

```
## Plan vs Implementation
[For each section in Part 1, state DONE/PARTIAL/MISSING/DEVIATED with specifics]

## Convention Violations
[List every deviation from existing patterns, with file:line references]

## Known Risk Resolution
[For each risk in Part 3, state FIXED/UNFIXED/PARTIALLY FIXED with details]

## Shortcuts Found
[List everything from Part 4 that was cut or half-done]

## Test Results
[Output from Part 5 checks]

## Verdict
[One of: READY / NEEDS FIXES / NEEDS REDESIGN]

## Required Changes Before Merge
[Numbered list of specific changes, ordered by severity]

## Optional Improvements
[Nice-to-haves that don't block merge]
```
