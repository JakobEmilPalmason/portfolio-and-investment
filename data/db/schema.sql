PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL,
    applied_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Positions: one open row per ticker
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    company TEXT,
    sector TEXT,
    side TEXT DEFAULT 'LONG',
    status TEXT DEFAULT 'OPEN',
    shares REAL NOT NULL DEFAULT 0,
    avg_cost_basis REAL NOT NULL DEFAULT 0,
    total_cost REAL NOT NULL DEFAULT 0,
    realized_pnl REAL DEFAULT 0,
    first_entry_date TEXT,
    last_update TEXT,
    entry_report_ref TEXT,
    thesis_summary TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, status)
);

-- FIFO lot tracking
CREATE TABLE IF NOT EXISTS lots (
    id INTEGER PRIMARY KEY,
    position_id INTEGER NOT NULL REFERENCES positions(id),
    ticker TEXT NOT NULL,
    shares REAL NOT NULL,
    cost_per_share REAL NOT NULL,
    purchase_date TEXT NOT NULL,
    transaction_id INTEGER REFERENCES transactions(id),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Append-only transaction ledger
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    run_id TEXT,
    ticker TEXT NOT NULL,
    action TEXT NOT NULL,
    shares REAL NOT NULL,
    price REAL NOT NULL,
    gross_value REAL NOT NULL,
    fees REAL DEFAULT 0,
    net_value REAL NOT NULL,
    realized_pnl REAL DEFAULT 0,
    reason TEXT,
    report_ref TEXT,
    pre_trade_cash REAL,
    post_trade_cash REAL,
    position_id INTEGER REFERENCES positions(id),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Daily portfolio snapshots
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id INTEGER PRIMARY KEY,
    snapshot_date TEXT NOT NULL UNIQUE,
    total_value REAL NOT NULL,
    cash REAL NOT NULL,
    positions_value REAL NOT NULL,
    num_positions INTEGER DEFAULT 0,
    daily_return REAL,
    cumulative_return REAL,
    benchmark_ticker TEXT DEFAULT 'SPY',
    benchmark_value REAL,
    benchmark_daily_return REAL,
    excess_return REAL,
    top_holdings_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Trade proposals (human-in-the-loop staging)
CREATE TABLE IF NOT EXISTS trade_proposals (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    run_id TEXT,
    ticker TEXT NOT NULL,
    proposed_action TEXT NOT NULL,
    proposed_shares REAL,
    proposed_price REAL,
    proposed_value REAL,
    target_weight_pct REAL,
    rationale TEXT,
    sizing_method TEXT,
    rule_checks_json TEXT,
    all_rules_passed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'PENDING',
    reviewed_at TEXT,
    review_note TEXT,
    executed_at TEXT,
    transaction_id INTEGER REFERENCES transactions(id)
);

-- Research run tracking
CREATE TABLE IF NOT EXISTS research_runs (
    run_id TEXT PRIMARY KEY,
    run_date TEXT NOT NULL,
    week_folder TEXT,
    pipeline_stage TEXT,
    input_count INTEGER,
    output_count INTEGER,
    verdicts_json TEXT,
    status TEXT DEFAULT 'COMPLETE',
    created_at TEXT DEFAULT (datetime('now'))
);

-- Price cache
CREATE TABLE IF NOT EXISTS price_cache (
    ticker TEXT NOT NULL,
    price_date TEXT NOT NULL,
    close_price REAL NOT NULL,
    source TEXT,
    fetched_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (ticker, price_date)
);

-- Pre-buy check history
CREATE TABLE IF NOT EXISTS prebuy_checks (
    id INTEGER PRIMARY KEY,
    run_at TEXT NOT NULL,
    ticker TEXT NOT NULL,
    company TEXT,
    mode TEXT NOT NULL,
    analysis_date TEXT,
    age_days INTEGER,
    report_path TEXT,
    verdict TEXT,
    average_score REAL,
    min_umbrella_score REAL,
    min_umbrella_name TEXT,
    mos_score REAL,
    c1_pass INTEGER,
    c1_detail TEXT,
    iv_conservative REAL,
    iv_currency TEXT,
    current_price REAL,
    price_date TEXT,
    mos_pct REAL,
    threshold_price REAL,
    threshold_pct REAL,
    c2_pass INTEGER,
    c2_detail TEXT,
    c3_pass INTEGER,
    thesis_text TEXT,
    result TEXT NOT NULL,
    capital_base REAL,
    position_size REAL,
    shares_at_threshold REAL,
    stale_flag INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Portfolio sim run history
CREATE TABLE IF NOT EXISTS sim_runs (
    id INTEGER PRIMARY KEY,
    run_at TEXT NOT NULL,
    capital REAL NOT NULL,
    min_verdict TEXT NOT NULL,
    top_n INTEGER NOT NULL,
    allowed_states TEXT,
    total_positions INTEGER,
    positions_json TEXT,
    sector_exposure_json TEXT,
    concentration_json TEXT,
    skipped_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_positions_ticker ON positions(ticker);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_lots_position ON lots(position_id);
CREATE INDEX IF NOT EXISTS idx_lots_ticker ON lots(ticker);
CREATE INDEX IF NOT EXISTS idx_transactions_ticker ON transactions(ticker);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON portfolio_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON trade_proposals(status);
CREATE INDEX IF NOT EXISTS idx_prebuy_ticker ON prebuy_checks(ticker);
CREATE INDEX IF NOT EXISTS idx_prebuy_run_at ON prebuy_checks(run_at);
CREATE INDEX IF NOT EXISTS idx_sim_runs_run_at ON sim_runs(run_at);
