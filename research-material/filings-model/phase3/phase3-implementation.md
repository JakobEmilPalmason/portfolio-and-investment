# Phase 3 Implementation: Evidence Database Schema & Storage Layer

Built 2026-03-19. Schema version 2 → 3.

---

## What Changed

| File | Lines | Action |
|------|-------|--------|
| `db/evidence_schema.sql` | 155 | New — 8 tables, 16 indexes |
| `src/evidence.py` | 738 | New — `EvidenceDB` class, 44 methods |
| `src/database.py` | 605 | Modified — 4 edits: version bump, JSON columns, init_db fix, migration block |
| `tests/test_evidence.py` | 721 | New — 39 test cases across 9 test classes |
| `research-material/filings-model/phase3-evidence-schema.md` | — | New — design rationale doc |

---

## Schema: `db/evidence_schema.sql`

No PRAGMAs. All `CREATE TABLE IF NOT EXISTS` for idempotent retry. Applied by the v2→v3 migration in `src/database.py:218-224`.

### source_documents

One row per SEC filing fetched. The natural key is `(ticker, doc_type, period_end)`.

```sql
CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    doc_type TEXT NOT NULL,          -- '10-K', '10-K/A', '10-Q', '10-Q/A'
    filing_date TEXT,
    period_end TEXT,
    accession_number TEXT,
    source_url TEXT,
    local_path TEXT NOT NULL,
    content_hash TEXT,               -- SHA-256
    section_count INTEGER DEFAULT 0,
    fetched_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, doc_type, period_end)
);
```

Amendment suffixes (`10-K/A`) are distinct doc_type values. This means a 10-K and its amendment coexist without collision. `content_hash` enables staleness detection on re-fetch.

### document_sections

Parsed sections within a filing. FK to source_documents. Natural key: `(source_document_id, section_key)`.

```sql
CREATE TABLE IF NOT EXISTS document_sections (
    id INTEGER PRIMARY KEY,
    source_document_id INTEGER NOT NULL REFERENCES source_documents(id),
    section_key TEXT NOT NULL,       -- 'mda', 'risk_factors', 'mda_part1'
    section_title TEXT,
    section_order INTEGER,
    content_text TEXT NOT NULL,
    content_hash TEXT,
    token_estimate INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(source_document_id, section_key)
);
```

Split sections use suffixed keys: `mda_part1`, `mda_part2`. The UNIQUE constraint accommodates this because each suffix is a distinct key.

### extracted_facts

Individual facts with full source citations. FK to source_documents (required) and document_sections (nullable — for document-level facts). Natural key: `(source_document_id, fact_key, fiscal_period)`.

```sql
CREATE TABLE IF NOT EXISTS extracted_facts (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    source_document_id INTEGER NOT NULL REFERENCES source_documents(id),
    document_section_id INTEGER REFERENCES document_sections(id),
    fact_type TEXT NOT NULL,          -- 'metric', 'narrative', 'guidance', 'risk_factor'
    fact_key TEXT NOT NULL,           -- 'revenue', 'roic', 'segment_revenue.cloud'
    fact_value TEXT,                  -- raw string: "$4.92 billion"
    fact_value_numeric REAL,          -- normalized: 4920000000.0
    fact_unit TEXT,                   -- 'USD', 'percent' (0.15), 'ratio', 'count', 'days'
    fiscal_period TEXT,
    confidence REAL NOT NULL,         -- no default: 1.0=XBRL, 0.85-0.95=regex, 0.7-0.9=LLM
    extraction_method TEXT,           -- 'xbrl', 'llm_structured', 'regex', 'computed'
    source_quote TEXT,
    source_char_offset_start INTEGER,
    source_char_offset_end INTEGER,
    computation_trace_json TEXT,      -- JSON: formula + inputs for derived metrics
    extraction_run_id TEXT,
    is_active INTEGER DEFAULT 1,     -- 0 = superseded by re-extraction
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(source_document_id, fact_key, fiscal_period)
);
```

`confidence` is NOT NULL with no default. Callers must explicitly set it. The value contract:

- `fact_value`: raw source string exactly as it appears in the filing
- `fact_value_numeric`: normalized to base units (dollars not millions, decimals not percentages)
- `fact_unit`: `USD` = actual dollars, `percent` = decimal (0.15 not 15), `ratio` = as-is

`is_active` enables soft-delete on re-extraction. Old facts get `is_active = 0` instead of being deleted. This preserves assertion_evidence links for audit.

The UNIQUE constraint on `(source_document_id, fact_key, fiscal_period)` prevents silent duplicate facts from the same filing. If the same metric appears in different sections (e.g., revenue in both income_stmt and mda), the extractor must use disambiguated keys: `revenue.income_stmt` vs `revenue.mda`.

### assertions

Claims extracted from analysis reports (FINAL-REPORT.md) that we want to verify against filing evidence. No FK to extracted_facts — linked via assertion_evidence.

```sql
CREATE TABLE IF NOT EXISTS assertions (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    report_path TEXT NOT NULL,
    umbrella_number INTEGER,          -- 1-8
    assertion_text TEXT NOT NULL,
    assertion_type TEXT NOT NULL,     -- 'quantitative', 'qualitative', 'comparative', 'causal'
    category TEXT,
    requires_arithmetic INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### assertion_evidence

Join table linking assertions to supporting/contradicting facts. Only FK in the codebase with `ON DELETE CASCADE` — deleting an assertion auto-deletes its evidence links.

```sql
CREATE TABLE IF NOT EXISTS assertion_evidence (
    id INTEGER PRIMARY KEY,
    assertion_id INTEGER NOT NULL REFERENCES assertions(id) ON DELETE CASCADE,
    extracted_fact_id INTEGER NOT NULL REFERENCES extracted_facts(id),
    relationship TEXT NOT NULL,       -- 'supports', 'contradicts', 'partial', 'unverifiable'
    match_score REAL,
    verification_method TEXT,
    verification_detail_json TEXT,
    verified_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(assertion_id, extracted_fact_id)
);
```

### verification_runs

Audit log of verification passes. One row per `./run.sh verify TICKER` invocation.

```sql
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
```

### semantic_diffs

Cross-period changes detected between filings. No UNIQUE constraint — same section/periods can have multiple diff entries of different types.

```sql
CREATE TABLE IF NOT EXISTS semantic_diffs (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    section_key TEXT NOT NULL,
    period_a TEXT NOT NULL,
    period_b TEXT NOT NULL,
    diff_type TEXT NOT NULL,          -- 'added', 'removed', 'changed', 'numeric_shift'
    summary TEXT NOT NULL,
    detail_json TEXT,
    significance INTEGER DEFAULT 3,  -- 1-5
    created_at TEXT DEFAULT (datetime('now'))
);
```

### computation_cache

Deterministic arithmetic results. Performance optimization — can always be rebuilt from facts.

```sql
CREATE TABLE IF NOT EXISTS computation_cache (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    computation_key TEXT NOT NULL,    -- 'roic_FY2025'
    formula TEXT NOT NULL,
    inputs_json TEXT NOT NULL,        -- JSON: {param: value, source_fact_ids: [...]}
    result_value REAL,
    result_unit TEXT,
    computed_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, computation_key)
);
```

`inputs_json` contains soft references to fact IDs. If facts are deactivated (re-extraction), cache entries point at nothing. Caller must call `invalidate_computations(ticker)` after re-extraction.

### Indexes (16)

```sql
idx_source_documents_ticker          ON source_documents(ticker)
idx_source_documents_accession       ON source_documents(accession_number)
idx_document_sections_document       ON document_sections(source_document_id)
idx_extracted_facts_ticker           ON extracted_facts(ticker)
idx_extracted_facts_document         ON extracted_facts(source_document_id)
idx_extracted_facts_key              ON extracted_facts(fact_key)
idx_extracted_facts_period           ON extracted_facts(fiscal_period)
idx_extracted_facts_extraction_run   ON extracted_facts(extraction_run_id)
idx_extracted_facts_active           ON extracted_facts(is_active)
idx_assertions_ticker                ON assertions(ticker)
idx_assertions_umbrella              ON assertions(umbrella_number)
idx_assertion_evidence_assertion     ON assertion_evidence(assertion_id)
idx_assertion_evidence_fact          ON assertion_evidence(extracted_fact_id)
idx_verification_runs_ticker         ON verification_runs(ticker)
idx_semantic_diffs_ticker            ON semantic_diffs(ticker)
idx_computation_cache_ticker         ON computation_cache(ticker)
```

Indexes on `extraction_run_id`, `source_document_id` (on facts), and `accession_number` were added because `delete_facts_for_extraction_run`, FK joins, and EDGAR lookups all scan these columns.

---

## Migration: `src/database.py` Changes

Four edits.

### Edit 1: Version bump (line 19)

```python
SCHEMA_VERSION = 3  # was 2
```

### Edit 2: JSON columns (lines 24-37)

Added 5 new column names to `_JSON_COLUMNS` frozenset:

```python
_JSON_COLUMNS = frozenset({
    "rule_checks_json",
    "verdicts_json",
    "top_holdings_json",
    "positions_json",
    "sector_exposure_json",
    "concentration_json",
    "skipped_json",
    "computation_trace_json",     # NEW — extracted_facts
    "verification_detail_json",   # NEW — assertion_evidence
    "run_metadata_json",          # NEW — verification_runs
    "detail_json",                # NEW — semantic_diffs
    "inputs_json",                # NEW — computation_cache
})
```

These names must be in the set because `_row_to_dict` auto-deserializes them on read (`json.loads`) and `_decimal_fields_from_dict` auto-serializes them on write (`json.dumps`). Without this, passing a dict for `computation_trace_json` would try to bind a Python dict to SQLite (fails), and reads would return raw JSON strings.

### Edit 3: init_db fix (lines 122-143)

`init_db()` previously inserted `SCHEMA_VERSION` (which would now be 3) into the `schema_version` table. This meant `migrate()` would see version 3 and no-op, but `schema.sql` only contains v1+v2 tables. Evidence tables would never be created on fresh installs.

Fixed: `init_db()` now inserts version `1`. The `migrate()` method walks through all migration steps.

```python
def init_db(self) -> None:
    """Run schema.sql and insert initial schema_version.

    Inserts version 1 so that migrate() walks through all migration
    steps (v1→v2→v3 etc.) to create tables not in schema.sql.
    """
    schema_sql = SCHEMA_PATH.read_text()
    if self.db_path != ":memory:":
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    self.conn.executescript(schema_sql)
    existing = self.conn.execute(
        "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if existing is None:
        self.conn.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (1,),  # was SCHEMA_VERSION
        )
        self.conn.commit()
    logger.info("Database initialized at %s", self.db_path)
```

### Edit 4: Migration block (lines 145-225)

Two changes inside `migrate()`:

1. After `self.init_db()`, re-read version and fall through to migration checks (previously returned immediately).

2. Added v2→v3 block after the existing v1→v2 block:

```python
if current < 3:
    evidence_path = REPO_ROOT / "db" / "evidence_schema.sql"
    self.conn.executescript(evidence_path.read_text())
    self.conn.execute(
        "INSERT INTO schema_version (version) VALUES (?)", (3,)
    )
    self.conn.commit()
```

Fresh install path: `schema.sql` (v1+v2 tables) → version 1 → migrate v1→v2 (IF NOT EXISTS, no-op) → v2→v3 (evidence tables) → version 3.

Existing v2 DB path: migrate sees version 2 → skips v1→v2 → runs v2→v3 (evidence tables) → version 3.

`executescript()` issues an implicit COMMIT before running. If DDL fails mid-way, partial tables exist. `CREATE TABLE IF NOT EXISTS` makes retry idempotent.

---

## Python Layer: `src/evidence.py`

`EvidenceDB` takes a `Database` instance, reuses its `.conn` property. Does not own the connection. Follows the same patterns as `database.py`:

- `_decimal_fields_from_dict(input)` before every write (Decimal→float, dict→JSON string)
- `_row_to_dict(row)` on every read (JSON string→dict)
- `self.conn.commit()` after every write
- `DuplicateEntryError` on `sqlite3.IntegrityError` with `from e`
- `logger.debug` for individual inserts, `logger.info` for bulk operations and deletes

### source_documents — 6 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_source_document` | `(doc: dict) -> int` | lastrowid | Raises `DuplicateEntryError` on `UNIQUE(ticker, doc_type, period_end)` |
| `upsert_source_document` | `(doc: dict) -> int` | lastrowid | `ON CONFLICT DO UPDATE` — updates filing_date, accession_number, source_url, local_path, content_hash, section_count, fetched_at |
| `get_source_document` | `(doc_id: int) -> Optional[dict]` | dict or None | By primary key |
| `get_source_documents_for_ticker` | `(ticker, doc_type=None) -> list[dict]` | list | ORDER BY filing_date DESC. Optional doc_type filter |
| `get_source_document_by_key` | `(ticker, doc_type, period_end) -> Optional[dict]` | dict or None | Lookup by natural key |
| `update_source_document` | `(doc_id, **fields) -> None` | None | Dynamic SET for mutable fields: content_hash, section_count, local_path, source_url, fetched_at |

### document_sections — 4 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_document_section` | `(section: dict) -> int` | lastrowid | Raises `DuplicateEntryError` on `UNIQUE(source_document_id, section_key)` |
| `upsert_document_section` | `(section: dict) -> int` | lastrowid | `ON CONFLICT DO UPDATE` — updates title, order, content, hash, token_estimate |
| `get_document_sections` | `(source_document_id: int) -> list[dict]` | list | ORDER BY section_order ASC |
| `get_document_section_by_key` | `(source_document_id, section_key) -> Optional[dict]` | dict or None | Lookup by composite key |

### extracted_facts — 10 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_extracted_fact` | `(fact: dict) -> int` | lastrowid | Raises `DuplicateEntryError` on `UNIQUE(source_document_id, fact_key, fiscal_period)` |
| `batch_insert_facts` | `(facts: list[dict]) -> int` | count | `executemany()` + single commit. Logs at INFO |
| `get_extracted_fact` | `(fact_id: int) -> Optional[dict]` | dict or None | By primary key |
| `get_facts_for_ticker` | `(ticker, fact_type=None, fact_key=None, fiscal_period=None, include_inactive=False, limit=500) -> list[dict]` | list | Multi-filter. Defaults to `is_active=1`. ORDER BY fiscal_period DESC, created_at DESC |
| `get_facts_for_document` | `(source_document_id, include_inactive=False) -> list[dict]` | list | All facts for a filing. ORDER BY fact_key |
| `get_facts_for_section` | `(document_section_id: int) -> list[dict]` | list | Active facts only. ORDER BY fact_key |
| `get_facts_by_extraction_run` | `(extraction_run_id: str) -> list[dict]` | list | All facts from a run (includes inactive). ORDER BY id |
| `get_fact_with_provenance` | `(fact_id: int) -> Optional[dict]` | dict or None | JOIN to source_documents + document_sections. Returns doc_type, filing_date, section_key, section_title alongside fact fields |
| `deactivate_facts_for_document` | `(source_document_id: int) -> int` | count | Sets `is_active = 0` on all active facts for a document. Used before re-extraction |
| `delete_facts_for_extraction_run` | `(extraction_run_id: str) -> int` | count | Hard delete. Used for cleanup |

### assertions — 6 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_assertion` | `(assertion: dict) -> int` | lastrowid | |
| `batch_insert_assertions` | `(assertions: list[dict]) -> int` | count | `executemany()` + single commit |
| `get_assertion` | `(assertion_id: int) -> Optional[dict]` | dict or None | |
| `get_assertions_for_ticker` | `(ticker, umbrella_number=None) -> list[dict]` | list | ORDER BY umbrella_number ASC, id ASC |
| `get_unverified_assertions` | `(ticker=None) -> list[dict]` | list | LEFT JOIN to assertion_evidence, WHERE ae.id IS NULL. Assertions with zero evidence links |
| `delete_assertions_for_report` | `(report_path: str) -> int` | count | ON DELETE CASCADE auto-removes assertion_evidence rows |

### assertion_evidence — 5 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_assertion_evidence` | `(link: dict) -> int` | lastrowid | Raises `DuplicateEntryError` on `UNIQUE(assertion_id, extracted_fact_id)` |
| `get_evidence_for_assertion` | `(assertion_id: int) -> list[dict]` | list | JOIN to extracted_facts — returns fact_key, fact_value, fact_value_numeric, fact_unit, fiscal_period, source_quote, confidence alongside link fields. ORDER BY match_score DESC |
| `get_evidence_for_fact` | `(extracted_fact_id: int) -> list[dict]` | list | Reverse lookup — JOIN to assertions. Returns ticker, assertion_text, assertion_type, umbrella_number |
| `get_evidence_summary_for_ticker` | `(ticker: str) -> dict` | dict | Aggregate counts: total_assertions, verified_count, supported_count, contradicted_count, partial_count, unverifiable_count. Single query with LEFT JOIN + CASE WHEN |
| `update_assertion_evidence` | `(assertion_id, extracted_fact_id, **fields) -> None` | None | Dynamic SET for: relationship, match_score, verification_method, verification_detail_json, verified_at. Handles JSON serialization for verification_detail_json |

### verification_runs — 4 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_verification_run` | `(run: dict) -> int` | lastrowid | Raises `DuplicateEntryError` on `UNIQUE(run_id)` |
| `get_verification_run` | `(run_id: str) -> Optional[dict]` | dict or None | By run_id (text key) |
| `get_verification_runs_for_ticker` | `(ticker, limit=20) -> list[dict]` | list | ORDER BY run_date DESC |
| `get_latest_verification_run` | `(ticker: str) -> Optional[dict]` | dict or None | Most recent by run_date |

### semantic_diffs — 5 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `insert_semantic_diff` | `(diff: dict) -> int` | lastrowid | |
| `get_diffs_for_ticker` | `(ticker, section_key=None, min_significance=None) -> list[dict]` | list | Multi-filter. ORDER BY significance DESC, period_b DESC |
| `get_diffs_between_periods` | `(ticker, period_a, period_b) -> list[dict]` | list | All diffs for a specific period pair |
| `get_high_significance_diffs` | `(min_significance=4, limit=50) -> list[dict]` | list | Cross-ticker. ORDER BY significance DESC, created_at DESC |
| `delete_diffs_between_periods` | `(ticker, period_a, period_b) -> int` | count | For re-running diff analysis |

### computation_cache — 4 methods

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `upsert_computation` | `(comp: dict) -> int` | lastrowid | `ON CONFLICT(ticker, computation_key) DO UPDATE` — updates formula, inputs_json, result_value, result_unit, computed_at |
| `get_computation` | `(ticker, computation_key) -> Optional[dict]` | dict or None | By natural key |
| `get_computations_for_ticker` | `(ticker: str) -> list[dict]` | list | ORDER BY computation_key |
| `invalidate_computations` | `(ticker, computation_key_prefix=None) -> int` | count | DELETE. If prefix given, uses LIKE for partial match (e.g., `roic_` deletes roic_FY2024 and roic_FY2025) |

### Cross-table — 1 method

| Method | Signature | Returns | Notes |
|--------|-----------|---------|-------|
| `get_ticker_evidence_summary` | `(ticker: str) -> dict` | dict | Returns: ticker, source_document_count, total_facts (active only), total_assertions, verified_assertions, verification_coverage (ratio 0-1), latest_verification_score, high_significance_diffs (significance >= 4) |

---

## Tests: `tests/test_evidence.py`

39 tests, 9 test classes, runs in 0.046s. All use in-memory databases.

```
TestSchemaVersion (3 tests)
  test_fresh_install_is_v3          — init_db + migrate → version 3
  test_all_evidence_tables_exist    — all 8 tables in sqlite_master
  test_v2_to_v3_migration           — simulates existing v2 DB → migrate → v3

TestSourceDocuments (6 tests)
  test_insert_and_get               — round-trip all fields
  test_duplicate_raises             — same (ticker, doc_type, period_end) → DuplicateEntryError
  test_upsert_updates_existing      — ON CONFLICT updates content_hash + section_count
  test_get_by_key                   — natural key lookup
  test_get_for_ticker_with_filter   — doc_type filter
  test_amendment_distinct_from_original — 10-K and 10-K/A coexist

TestDocumentSections (3 tests)
  test_insert_and_get_ordered       — ORDER BY section_order
  test_upsert_updates_content       — ON CONFLICT updates content_text
  test_get_by_key                   — composite key lookup

TestExtractedFacts (9 tests)
  test_insert_and_get               — round-trip including numeric values
  test_duplicate_raises             — same (doc, key, period) → DuplicateEntryError
  test_json_roundtrip               — computation_trace_json dict→dict
  test_batch_insert                 — 10 facts via executemany
  test_deactivate_facts             — is_active toggle, default query excludes inactive
  test_confidence_required          — omitting confidence → error
  test_foreign_key_enforcement      — invalid source_document_id → IntegrityError
  test_get_fact_with_provenance     — JOIN returns doc_type + section_key
  test_multi_filter_query           — fact_type filter

TestAssertions (3 tests)
  test_insert_and_get_ordered       — ORDER BY umbrella_number
  test_batch_insert                 — 5 assertions via executemany
  test_filter_by_umbrella           — umbrella_number filter

TestAssertionEvidence (6 tests)
  test_insert_and_get_evidence      — JOIN enrichment with fact fields
  test_duplicate_raises             — same (assertion_id, fact_id) → DuplicateEntryError
  test_unverified_assertions        — LEFT JOIN: 1 unverified → 0 after linking
  test_cascade_delete               — delete assertion → evidence links auto-removed
  test_evidence_summary             — aggregate counts
  test_json_roundtrip_in_evidence   — verification_detail_json dict→dict

TestVerificationRuns (2 tests)
  test_insert_and_get               — run_metadata_json dict→dict
  test_latest_run                   — ORDER BY run_date DESC LIMIT 1

TestSemanticDiffs (3 tests)
  test_insert_and_filter_by_significance — min_significance + section_key filters
  test_diffs_between_periods        — period pair lookup
  test_json_roundtrip               — detail_json dict→dict

TestComputationCache (3 tests)
  test_upsert_and_get               — inputs_json dict→dict
  test_upsert_updates               — ON CONFLICT updates result_value
  test_invalidate                   — prefix-based deletion (roic_*)

TestTickerEvidenceSummary (1 test)
  test_end_to_end_summary           — full pipeline: doc → facts → assertions → evidence → verification run → diff → summary
```

### Run

```bash
python3 -m unittest tests.test_evidence -v
```

---

## Design Decisions

### Fresh install migration path

`init_db()` inserts version 1 (not `SCHEMA_VERSION`). `migrate()` re-reads version after `init_db()` and falls through to all migration steps. This means fresh installs walk v1→v2→v3 and get all tables. Previously, `init_db()` inserted the current `SCHEMA_VERSION` directly, which meant `migrate()` no-oped and evidence tables were never created.

### UNIQUE on extracted_facts

`UNIQUE(source_document_id, fact_key, fiscal_period)` prevents silent duplicate facts. If the same metric appears in different sections, the extractor uses disambiguated keys. The constraint catches accidental duplicates at the DB level — a bug in the caller that forgets to deactivate before re-inserting gets caught immediately instead of silently corrupting downstream queries.

### ON DELETE CASCADE

Only on `assertion_evidence.assertion_id → assertions.id`. Deleting an assertion auto-cleans its evidence links. No other FK in the codebase uses CASCADE. This was chosen because assertion_evidence is a pure join table with no independent meaning.

### is_active flag

`is_active INTEGER DEFAULT 1` on extracted_facts. Re-extraction marks old facts inactive (`is_active = 0`) via `deactivate_facts_for_document()`. Preserves assertion_evidence links for audit history. All query methods filter `is_active = 1` by default. `include_inactive=True` overrides.

### confidence NOT NULL

No DEFAULT. Every insert must explicitly set confidence. Prevents LLM-extracted facts from silently appearing as XBRL-level confidence.

### Batch inserts

`batch_insert_facts()` and `batch_insert_assertions()` use `executemany()` with a single commit. A typical ticker extraction produces ~50 facts + ~20 assertions. Without batching, that's ~70 individual commits. With batching, it's 2.

### computation_cache soft references

`inputs_json` contains fact IDs as JSON values, not FK-enforced references. If facts are deactivated, cache entries point at nothing. Accepted as a known limitation — the cache is a performance optimization that can always be rebuilt. `invalidate_computations(ticker)` should be called after re-extraction.

---

## Verified

1. `sqlite3 :memory: < db/evidence_schema.sql` — parses clean
2. Fresh install (`Database(":memory:")` → `init_db()` → `migrate()`) — version 3, all 8 tables present
3. v2→v3 migration — existing v2 DB migrates to v3 without touching existing tables or data
4. Real DB — `db/portfolio.db` migrates cleanly, existing positions/transactions untouched
5. 39/39 tests pass in 0.046s

---

## What This Does Not Include

- No EDGAR fetching — that's Phase 1 (`scripts/fetch-evidence.py`, not yet built)
- No LLM extraction — that's Phase 2
- No claim decomposer or fact checker — that's Phase 4 (`./run.sh verify TICKER`)
- No prompt updates or FINAL-REPORT.json changes — that's Phase 5
- No semantic diffing logic — that's Phase 6
- No dashboard evidence tab — that's Phase 7
- No `run.sh` dispatch changes — those come when the scripts that use this schema are built

This is the container. The scripts that fill it are separate work.
