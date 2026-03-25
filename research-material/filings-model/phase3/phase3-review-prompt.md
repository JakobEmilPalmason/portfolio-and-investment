# Phase 3 Review Prompt: Database Schema + Evidence Storage

You are reviewing the implementation of Phase 3 of the Evidence and Extraction Layer. Phase 3 adds persistent, queryable evidence storage to an existing SQLite-backed investment analysis system.

Read the masterplan at `research-material/filings-model/masterplan.md` (focus on Phase 3 in Section 5, the full schema in Section 7, integration points in Section 6, and risk analysis in Section 9). Then read the existing database layer at `src/database.py` and `db/schema.sql` to understand the patterns this must follow.

Your job is to catch every issue that could cause bugs, data corruption, migration failures, or integration problems — before any code is written.

---

## What Phase 3 Adds

- `db/evidence_schema.sql` — 8 new tables (source_documents, document_sections, extracted_facts, assertions, assertion_evidence, verification_runs, semantic_diffs, computation_cache)
- `src/evidence/evidence_db.py` (~300 LOC) — SQLite read/write layer
- Modifications to `src/database.py`: SCHEMA_VERSION 2→3, extend `_JSON_COLUMNS`, add v2→v3 migration

---

## Review Checklist

Work through every section below. For each item, state PASS, ISSUE, or QUESTION with a concrete explanation. Do not skip items. Do not handwave.

### A. Schema Correctness

1. **UNIQUE constraints — too tight?**
   - `source_documents(ticker, doc_type, period_end)` — what happens with amended filings (10-K/A)? Is `doc_type='10-K/A'` a separate value or does it collide with `'10-K'`? If a company amends its 10-K for the same period, can the system store both the original and the amendment?
   - `document_sections(source_document_id, section_key)` — can a single filing have multiple subsections under the same key (e.g., two separate "notes" segments)? If so, does this constraint silently drop one?
   - `computation_cache(ticker, computation_key)` — the key format is `'roic_FY2025'`. What if you need to recompute the same metric with corrected inputs? Does the UNIQUE constraint prevent storing historical computation attempts?

2. **UNIQUE constraints — too loose?**
   - `extracted_facts` has no UNIQUE constraint at all. Can the same fact (same ticker, same fact_key, same fiscal_period, same source_document_id) be inserted twice from different extraction runs? If yes, which one wins when queried? If no, what prevents duplicates?

3. **Foreign key cascading behavior**
   - No ON DELETE clause is specified on any REFERENCES. SQLite defaults to NO ACTION (which means RESTRICT when foreign_keys=ON). Walk through the filing supersession scenario: a new 10-K is filed for the same period. The old `source_documents` row needs to be invalidated. What happens to its `document_sections`, `extracted_facts`, and downstream `assertion_evidence` rows? Can the old document be deleted? If not, how is it marked stale? The plan mentions content_hash invalidation but no concrete mechanism.

4. **Missing or wrong indexes**
   - `extracted_facts` is indexed on ticker, fact_key, fiscal_period — but queries from Phase 4 (verification) will join through `source_document_id` and `document_section_id`. Are these FK columns indexed?
   - `assertion_evidence` is indexed on `assertion_id` but not `extracted_fact_id`. Reverse lookups ("which assertions use this fact?") will table-scan. Is that acceptable at scale?
   - `verification_runs` has no index on `ticker`. Finding all verification runs for a ticker requires a scan.
   - `source_documents` has no index on `accession_number`, the primary EDGAR lookup key.

5. **Column type decisions**
   - `fact_value` is TEXT and `fact_value_numeric` is REAL. What are the conversion rules? If fact_value says "4.92 billion" and fact_value_numeric says 4920000000, which is canonical? What about units — does `fact_unit='USD_millions'` mean the numeric value is already in millions, or raw? This ambiguity will cause arithmetic errors downstream.
   - `confidence REAL DEFAULT 1.0` — makes sense for XBRL, but LLM extractions should not default to 1.0. Should the default be NULL or a lower value, with 1.0 set explicitly only for mechanical extraction?

6. **Section splitting vs UNIQUE constraint**
   - The plan says sections are capped at 8,000 tokens and "split at next heading if exceeded." But `UNIQUE(source_document_id, section_key)` means a split section can't have two rows with the same key. How are split sections represented? Does the key get a suffix (e.g., `'mda_part1'`, `'mda_part2'`)? If so, does the schema_registry still map `'mda'` correctly?

7. **Temporal data model**
   - There is no `is_current` or `superseded_by` column on `source_documents` or `extracted_facts`. When a filing is re-extracted (new content hash), are old rows deleted, updated, or kept alongside new ones? If kept, how does a consumer know which set of facts is current? The plan says "invalidate all linked extracted_facts + re-extract" but the schema has no invalidation flag.

### B. Migration Safety

8. **Sequential migration path**
   - The existing `migrate()` handles v1→v2. The plan adds v2→v3. What if a fresh install occurs? `init_db()` runs `schema.sql` (which creates v1 tables), then `migrate()` runs v1→v2→v3. But the evidence tables are in `evidence_schema.sql`, not `schema.sql`. Does `init_db()` also need to run `evidence_schema.sql`? Or does `migrate()` handle it? What's the source of truth for a fresh install?

9. **Migration atomicity**
   - If `evidence_schema.sql` creates 8 tables and the 5th CREATE fails (e.g., syntax error), are the first 4 committed? SQLite's `executescript()` does not wrap in a transaction by default. The migration needs explicit BEGIN/COMMIT or error handling that rolls back partial schema changes.

10. **_JSON_COLUMNS extension**
    - The existing `_JSON_COLUMNS` is a `frozenset` (immutable). The plan says "extend" it with 4 new entries: `computation_trace`, `detail_json`, `run_metadata_json`, `inputs_json`. A frozenset cannot be mutated in-place. How is this extended — new frozenset? Union? Does the evidence_db.py module need its own JSON column set?

11. **Schema version table**
    - After migration, `schema_version` should have a row for version 3 with `applied_at`. Verify the migration code inserts this row. Check: can the system detect if migration was interrupted (v2 tables exist but v3 row missing)?

### C. Pattern Conformance with Existing Database Layer

12. **Separate class or extension?**
    - The plan says evidence_db.py "follows src/database.py pattern." But is it a NEW class (`EvidenceDatabase`) or does it ADD methods to the existing `Database` class? If separate: two connections to the same SQLite file means WAL mode must be configured on both, and busy_timeout must handle contention. If extending: the Database class grows significantly and violates single-responsibility.

13. **Decimal handling**
    - The existing layer uses `Decimal` for all monetary values with `_dec()` and `_float()` converters. Evidence facts include REAL values (revenue, margins, ratios) that aren't money. Should evidence_db.py use Decimal for `fact_value_numeric`? If not, is there a risk of precision mismatch when computed values (from arithmetic_engine) feed back into reports that use Decimal?

14. **Row-to-dict conversion**
    - The existing `_row_to_dict()` auto-deserializes columns in `_JSON_COLUMNS`. If evidence_db.py uses its own connection, it needs its own `_row_to_dict()` or the existing one needs to know about evidence JSON columns. Verify this is addressed.

15. **Error handling**
    - Existing layer raises `DuplicateEntryError` for UNIQUE violations. Evidence layer will hit UNIQUE violations when re-extracting. Is that expected behavior (catch + update)? Or is it a bug (should upsert)? The choice affects whether methods are INSERT or INSERT OR REPLACE.

16. **Logging**
    - Existing layer logs all operations via module-level logger. Verify the plan calls for the same in evidence_db.py. Extraction runs can produce hundreds of inserts per ticker — will logging volume be a problem?

### D. Data Integrity & Provenance

17. **Provenance chain completeness**
    - The selling point is: every number traces to `extracted_facts.id → document_sections.id → source_documents.id → filing URL`. Walk through a concrete example: "ROIC = 15.98%". Trace it from computation_cache through extracted_facts inputs through document_sections to source_documents. Does every link exist? Are there any gaps where the chain breaks (e.g., computed values referencing other computed values)?

18. **extraction_run_id in extracted_facts**
    - This column exists but has no FK to verification_runs (which has `run_id`). Are these the same concept? If not, where is the extraction run tracked? If it's just a string tag, how are all facts from a single run grouped or invalidated?

19. **assertion_evidence relationship semantics**
    - `relationship` is TEXT with values 'supports', 'contradicts', 'partial', 'unverifiable'. What happens when two facts about the same assertion disagree — one supports, one contradicts? Is the overall assessment in verification_runs? How is conflict resolution represented in the schema?

20. **Cross-period fact identity**
    - Semantic diffing (Phase 6) compares facts across periods. But `fact_key` like `'segment_revenue.cloud'` may not be stable across periods (segment names change, get renamed, get split). How does the differ handle key mismatches? Is this a schema issue or a code issue?

### E. Scale & Performance

21. **Write volume per extraction**
    - The plan estimates ~50 evidence items per ticker per filing. For a full extraction of 500 tickers × 5 filings = 125K rows in extracted_facts alone, plus sections, assertions, etc. SQLite handles this fine for reads, but what about bulk inserts? Is there a plan for batched inserts (executemany) vs one-at-a-time? The existing layer inserts one row at a time with auto-commit.

22. **Query patterns**
    - What are the 5 most common queries against the evidence tables? List them and verify each has appropriate index coverage. Common patterns to check: "all facts for ticker X in period Y", "all unverified assertions for ticker X", "all facts from a specific extraction run", "all diffs for ticker X between periods A and B".

23. **Cache invalidation blast radius**
    - When a source_document's content_hash changes, the plan says invalidate all linked extracted_facts and re-extract. For a single 10-K, that could be 50+ facts, each linked to assertions, each linked to assertion_evidence. What's the deletion/invalidation cascade? Is it performant? Is it correct?

### F. Integration with Downstream Phases

24. **Phase 4 dependency**
    - Phase 4 (verification) reads from extracted_facts and writes to assertions + assertion_evidence. The schema must support Phase 4's access patterns. Check: can Phase 4's claim_decomposer write assertions without extracted_facts existing yet (e.g., for tickers without SEC filings)? The schema allows it (no NOT NULL on assertion_evidence), but is that the intended behavior?

25. **Phase 6 dependency**
    - Semantic diffing writes to semantic_diffs. The `period_a` and `period_b` columns are TEXT (e.g., 'FY2024', 'FY2025'). Are these the same format as `extracted_facts.fiscal_period`? If not, joining across these tables requires format conversion.

26. **Phase 7 dependency**
    - Dashboard reads evidence data. It currently uses the `Database` class. If evidence is in a separate `EvidenceDatabase`, the dashboard needs to instantiate both. Is this addressed?

### G. Edge Cases

27. **Non-US tickers**
    - The plan says skip EDGAR for non-US tickers. But can non-US tickers still have `assertions` and `assertion_evidence` rows (from Phase 4 verification against yfinance data)? The schema allows it — `source_documents.doc_type` can be `'financials.md'`. Is this flow tested?

28. **Empty filings**
    - What if EdgarTools returns a filing with an empty or malformed section? The schema has `content_text TEXT NOT NULL` on document_sections. Does the system skip empty sections or error?

29. **Re-running extraction**
    - If `./run.sh extract TICKER` is run twice on the same filing, what happens? INSERT fails (UNIQUE constraint)? INSERT OR REPLACE overwrites? The answer determines whether extraction is idempotent or additive.

30. **Database file doesn't exist**
    - Fresh clone: no `db/portfolio.db`. First command is `./run.sh extract TICKER`. Does the init_db + migrate flow create both the portfolio tables AND the evidence tables? Or does evidence extraction fail because the DB hasn't been initialized by a portfolio command first?

---

## Output Format

For each numbered item (1-30), provide:

```
### [N]. [Item title]
**Verdict:** PASS | ISSUE | QUESTION
**Finding:** [What you found in the plan/schema]
**Risk:** [What could go wrong if unaddressed — be specific: data loss, silent corruption, runtime crash, etc.]
**Recommendation:** [Concrete fix, if applicable]
```

After all items, provide:

```
## Summary
- Critical issues (must fix before implementation): [count]
- Design questions (need decision before implementation): [count]
- Minor issues (fix during implementation): [count]
- Passes: [count]

## Top 3 Risks
1. [Most dangerous issue and why]
2. [Second most dangerous]
3. [Third most dangerous]
```
