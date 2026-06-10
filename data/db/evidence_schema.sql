-- Evidence extraction layer — schema v3
-- Applied by the v2→v3 migration in src/database.py
--
-- Value contract:
--   fact_value:         raw source string as it appears ("$4.92 billion", "15.3%")
--   fact_value_numeric: normalized base-unit number (4920000000.0, 0.153)
--   fact_unit:          'USD' (actual dollars), 'percent' (decimal 0.15), 'ratio', 'count', 'days'
--   confidence:         1.0=XBRL/computed, 0.85-0.95=regex, 0.7-0.9=llm_structured
--   section_key:        split sections use suffixed keys ('mda_part1', 'mda_part2')
--   doc_type:           includes amendment suffix ('10-K', '10-K/A', '10-Q', '10-Q/A')

-- Source documents: one row per filing fetched
CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    filing_date TEXT,
    period_end TEXT,
    accession_number TEXT,
    source_url TEXT,
    local_path TEXT NOT NULL,
    content_hash TEXT,
    section_count INTEGER DEFAULT 0,
    fetched_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, doc_type, period_end)
);

-- Parsed sections within a filing
CREATE TABLE IF NOT EXISTS document_sections (
    id INTEGER PRIMARY KEY,
    source_document_id INTEGER NOT NULL REFERENCES source_documents(id),
    section_key TEXT NOT NULL,
    section_title TEXT,
    section_order INTEGER,
    content_text TEXT NOT NULL,
    content_hash TEXT,
    token_estimate INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(source_document_id, section_key)
);

-- Extracted facts with source citations
CREATE TABLE IF NOT EXISTS extracted_facts (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    source_document_id INTEGER NOT NULL REFERENCES source_documents(id),
    document_section_id INTEGER REFERENCES document_sections(id),
    fact_type TEXT NOT NULL,
    fact_key TEXT NOT NULL,
    fact_value TEXT,
    fact_value_numeric REAL,
    fact_unit TEXT,
    fiscal_period TEXT,
    confidence REAL NOT NULL,
    extraction_method TEXT,
    source_quote TEXT,
    source_char_offset_start INTEGER,
    source_char_offset_end INTEGER,
    computation_trace_json TEXT,
    extraction_run_id TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(source_document_id, fact_key, fiscal_period)
);

-- Assertions from analysis reports to verify
CREATE TABLE IF NOT EXISTS assertions (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    report_path TEXT NOT NULL,
    umbrella_number INTEGER,
    assertion_text TEXT NOT NULL,
    assertion_type TEXT NOT NULL,
    category TEXT,
    requires_arithmetic INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Links assertions to supporting/contradicting evidence
CREATE TABLE IF NOT EXISTS assertion_evidence (
    id INTEGER PRIMARY KEY,
    assertion_id INTEGER NOT NULL REFERENCES assertions(id) ON DELETE CASCADE,
    extracted_fact_id INTEGER NOT NULL REFERENCES extracted_facts(id),
    relationship TEXT NOT NULL,
    match_score REAL,
    verification_method TEXT,
    verification_detail_json TEXT,
    verified_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
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
    diff_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    detail_json TEXT,
    significance INTEGER DEFAULT 3,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Computation cache for deterministic arithmetic
CREATE TABLE IF NOT EXISTS computation_cache (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    computation_key TEXT NOT NULL,
    formula TEXT NOT NULL,
    inputs_json TEXT NOT NULL,
    result_value REAL,
    result_unit TEXT,
    computed_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, computation_key)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_source_documents_ticker ON source_documents(ticker);
CREATE INDEX IF NOT EXISTS idx_source_documents_accession ON source_documents(accession_number);
CREATE INDEX IF NOT EXISTS idx_document_sections_document ON document_sections(source_document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_ticker ON extracted_facts(ticker);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_document ON extracted_facts(source_document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_key ON extracted_facts(fact_key);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_period ON extracted_facts(fiscal_period);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_extraction_run ON extracted_facts(extraction_run_id);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_ticker_active ON extracted_facts(ticker, is_active);
CREATE INDEX IF NOT EXISTS idx_assertions_ticker ON assertions(ticker);
CREATE INDEX IF NOT EXISTS idx_assertions_umbrella ON assertions(umbrella_number);
CREATE INDEX IF NOT EXISTS idx_assertion_evidence_assertion ON assertion_evidence(assertion_id);
CREATE INDEX IF NOT EXISTS idx_assertion_evidence_fact ON assertion_evidence(extracted_fact_id);
CREATE INDEX IF NOT EXISTS idx_verification_runs_ticker ON verification_runs(ticker);
CREATE INDEX IF NOT EXISTS idx_semantic_diffs_ticker ON semantic_diffs(ticker);
CREATE INDEX IF NOT EXISTS idx_computation_cache_ticker ON computation_cache(ticker);
