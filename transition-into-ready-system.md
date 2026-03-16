# From AI research workbench to paper-trading-ready portfolio system

**This repo has a strong AI-driven research pipeline but zero portfolio infrastructure.** The gap between "generates stock verdicts" and "tracks paper-trading P&L" is roughly 1,500–2,500 lines of Python, one SQLite database, and four new modules. The existing A1→C pipeline and INVESTMENT-POLICY.md are solid foundations — but `portfolio-sim.py` is a stateless toy that outputs to stdout, the Saxo API is broken, there's no transaction ledger, no snapshots, no benchmark tracking, and the sizing rules in the investment policy exist only as prose. This report maps the exact path from current state to a functioning paper-trading system, drawing on patterns from the best open-source investing repos.

---

## 1. How serious AI-assisted investing repos are structured

The open-source AI investing landscape has matured dramatically since 2023. The most relevant repos for a Buffett-style Claude Code workbench cluster into four tiers: complete agent systems, data platforms, portfolio analytics libraries, and optimization tools.

**virattt/ai-hedge-fund** (~43k stars) is the closest structural analog to this repo. It uses 18 LLM-powered agents modeling legendary investors — Buffett, Munger, Graham, Damodaran, Burry — plus specialized agents for technicals, sentiment, fundamentals, and risk management. Its pipeline mirrors this repo's: analyst agents gather data concurrently, philosophy agents evaluate, a risk manager sets position limits, and a portfolio manager makes final decisions. Built on LangGraph with OpenAI/Anthropic support. The key architectural lesson: it keeps LLM reasoning strictly separated from deterministic portfolio execution.

**OpenBB** (~63k stars) has evolved from a retail-investor terminal into an open data platform with MCP server support for AI agent integration. It provides a unified Python API across 100+ data providers — switch from Yahoo to FMP to Polygon by changing one parameter. This is the single most relevant data layer for any AI investing workbench.

**FinGPT** (~18k stars) focuses on fine-tuning LLMs for financial sentiment analysis using LoRA. Useful as a building block for sentiment signals but not a complete system. **TauricResearch/TradingAgents** introduces a bull/bear debate mechanism where agents argue opposing sides before decisions — a pattern worth borrowing for thesis stress-testing.

The maturity progression across these repos follows a consistent pattern: **(1)** data access → **(2)** screening/filtering → **(3)** single-stock deep analysis → **(4)** portfolio construction → **(5)** backtesting → **(6)** performance reporting → **(7)** paper trading → **(8)** automation. This repo is solidly at stage 3 with elements of stage 4. **The critical gap is stages 6–7: no persistent portfolio state and no performance measurement.** Most repos that attempt to skip from analysis directly to live trading fail because they never validated their decision quality through paper trading.

Common architectural patterns across the best repos: Pandas DataFrames as the universal data interchange format; strict separation of data sourcing from analysis from execution; LLMs for research augmentation with deterministic code for all portfolio rules; and SQLite or flat files (never Postgres) for single-user systems.

---

## 2. Best tools and repos to adopt, borrow from, or avoid

### Candidate tools and repos comparison table

| Name | Category | Why relevant | Verdict | Maintenance | Complexity | Where it fits |
|------|----------|-------------|---------|-------------|------------|---------------|
| **QuantStats** | Portfolio analytics | HTML tear sheets, 40+ metrics, benchmark comparison | **Adopt** | Active (same author as yfinance) | Low | Feed daily returns → generate weekly/monthly reports |
| **OpenBB** | Data aggregation | Unified API across 100+ providers, MCP server for Claude | **Adopt** | Very active (company-backed, v4.5+) | Medium | Replace raw yfinance calls; single data layer |
| **edgartools** | SEC fundamentals | Free SEC EDGAR data, XBRL parsing, no API key needed | **Adopt** | Active, growing rapidly | Low | Supplement yfinance with authoritative fundamental data |
| **Tiingo** | Price data | Best free tier (500 req/day), validated EOD data | **Adopt** | Stable API | Low | Primary price source or yfinance backup |
| **fredapi** | Macro data | 800k+ time series from the Fed, free | **Adopt** | Stable | Low | Macro context for investment thesis |
| **PyPortfolioOpt** | Position sizing | Black-Litterman, discrete allocation, scikit-learn-like API | **Adopt (Phase 3)** | Maintained, good docs | Low | Optimize weights across concentrated picks |
| **Streamlit** | Dashboard | 39k stars, lowest friction, huge financial dashboard community | **Adopt (Phase 3)** | Very active (Snowflake) | Low | Portfolio dashboard, research browser |
| **sqlite-utils** | DB utilities | Simon Willison's high-level SQLite API + CLI | **Adopt** | Active | Very low | Simplify all SQLite operations |
| **Datasette** | DB browser | Instant web UI for any SQLite database | **Borrow** | Active | Low | Ad-hoc exploration of research DB |
| **ai-hedge-fund** | Architecture ref | Multi-agent investor philosophy pattern | **Borrow ideas** | Active (43k stars) | N/A | Study agent separation patterns |
| **bt + ffn** | Backtesting | Lightweight, composable "algo stack" for rebalancing | **Borrow (Phase 3)** | Maintained | Low-Med | Test rebalancing strategies historically |
| **Langfuse** | LLM tracing | Open-source LLM observability, free cloud tier | **Borrow (Phase 3)** | Very active (23k stars) | Medium | Debug LLM research quality over time |
| **Riskfolio-Lib** | Advanced optimization | 24 risk measures, cardinality constraints | **Postpone** | Active | High | Only if you need institutional-grade optimization |
| **Backtrader** | Backtesting | Event-driven, unmaintained | **Avoid** | Dormant (single maintainer) | High | Overkill for Buffett-style rebalancing |
| **Zipline-reloaded** | Backtesting | Quantopian legacy, heavy installation | **Avoid** | Community-maintained | High | Factor investing focus, not value investing |
| **VectorBT** | Backtesting | Fast but OSS edition stalling, Commons Clause license | **Avoid** | OSS slowing, PRO is commercial | Medium | Speed irrelevant for 8-15 stock portfolio |
| **pyfolio** | Analytics | Unmaintained since Quantopian died (2020) | **Avoid** | Dead | N/A | QuantStats is strictly better |
| **Prefect/Dagster/Airflow** | Scheduling | Workflow orchestration | **Avoid** | Active | High | Massive overkill for weekly solo scripts |
| **MLflow/W&B** | Experiment tracking | ML experiment platforms | **Avoid** | Active | High | Wrong abstraction for investment research |
| **PostgreSQL** | Database | Relational database server | **Avoid** | N/A | High | Zero benefit at solo-investor scale |

### Paper trading: build custom, don't adopt a framework

**No widely-adopted Python library exists for local paper trading without a broker API.** Backtrader has a broker simulator buried inside its framework, but extracting it means adopting the entire Cerebro engine — heavy for a concentrated portfolio that trades weekly. QSTrader has clean Position/Portfolio classes but is geared toward algorithmic backtesting. The pragmatic answer for a Buffett-style system is **~300–400 lines of custom Python** with dataclasses for Position, Portfolio, Transaction, and PortfolioSnapshot, persisted to SQLite. The low trading frequency (perhaps 2–5 trades per month) doesn't justify framework overhead.

### Financial data: the recommended stack costs $0/month

The current yfinance dependency is fragile. Yahoo has aggressively tightened rate limiting since late 2024 — users report `429` errors even on first requests from cloud environments. yfinance is an unofficial scraper, not an API; any Yahoo layout change breaks it. **Cache every price fetch in SQLite and never depend on a single yfinance call succeeding.** The recommended data stack: **Tiingo** (500 free requests/day, validated data) as primary price source, **edgartools** (free, direct from SEC) for authoritative fundamentals, **FRED via fredapi** for macro context, and **OpenBB** as the aggregation layer that lets you swap providers with one parameter change. Total cost: zero.

### Portfolio analytics: QuantStats is the clear winner

**QuantStats generates professional-grade HTML tear sheets in four lines of code**: `import quantstats as qs; qs.reports.html(returns, "SPY", output="report.html")`. It calculates Sharpe, Sortino, max drawdown, CAGR, alpha, beta, rolling statistics, monthly return heatmaps, and Monte Carlo simulations. It benchmarks against any index. It's actively maintained by the same developer who created yfinance. For a concentrated Buffett-style portfolio, this is the only analytics library you need. Skip pyfolio (dead), empyrical (superseded), and Riskfolio-Lib (overkill for reporting).

### Infrastructure: boring and reliable

**Database**: SQLite, unambiguously. A solo investor analyzing ~75 tickers/week generates perhaps 50–100 MB/year — trivially small. SQLite's JSON functions let you store and query semi-structured LLM outputs. FTS5 enables full-text search across all research text. WAL mode allows a dashboard to read while scripts write. The entire database is one file you can back up with `cp`. DuckDB is a nice complement for ad-hoc analytics but not required.

**Dashboard**: Streamlit. Lowest friction, largest community of investment dashboard examples, Plotly charts built-in. A working portfolio dashboard takes ~100 lines of pure Python.

**Scheduling**: cron + shell script wrapper for local execution. If the repo is on GitHub, **GitHub Actions** with a cron schedule provides free cloud execution, monitoring, and failure notifications. Do not install Prefect, Dagster, or Airflow — weekly frequency doesn't justify orchestration infrastructure.

**Experiment tracking**: A SQLite `analyses` table with a JSON column for LLM outputs. Add Langfuse (free cloud tier) only if you need detailed prompt/completion tracing for debugging LLM quality.

---

## 3. Gap analysis against paper-trading-ready standard

### What exists vs. what's missing

| Capability | Status | Assessment |
|-----------|--------|------------|
| AI-assisted stock idea generation | ✅ Exists | A1→A2 pipeline works |
| Thesis creation | ✅ Exists | FINAL-REPORT.md per ticker |
| Candidate ranking | ✅ Exists | Queue states + B1/B2 triage |
| Explicit trade proposals | ⚠️ Partial | portfolio-decision.json exists but is not connected to execution |
| Deterministic portfolio/risk rules | ⚠️ Prose only | INVESTMENT-POLICY.md defines rules but **nothing enforces them in code** |
| Paper portfolio tracking | ❌ Missing | portfolio-sim.py is stateless, outputs to stdout |
| Transaction ledger | ❌ Missing | No record of buys, sells, or position history |
| Performance reporting | ❌ Missing | No returns, no benchmark comparison, no tear sheets |
| Repeatable workflow | ❌ Missing | No scheduler, no CLI entry point, no state machine |
| Monitoring/alerts | ❌ Missing | monitor.md is a stub |
| Tests | ❌ Missing | No test suite |

### The five exact blockers preventing paper-trading readiness

**Blocker 1: No persistent portfolio state.** `portfolio-sim.py` recalculates everything from scratch each run. It has no memory of previous weeks, no cost basis, no cash balance. A paper trading system must know what it "owns" between runs.

**Blocker 2: No transaction ledger.** Without an append-only record of trades, you cannot calculate realized P&L, reconstruct historical state, or audit why a position was opened. This is the foundational data structure of any paper trading system.

**Blocker 3: No daily/weekly snapshots.** Performance measurement requires a time series of portfolio values. Without snapshots, you cannot calculate returns, drawdowns, or benchmark-relative performance.

**Blocker 4: No bridge from verdicts to trades.** The pipeline produces FINAL-REPORT.json with verdicts ("Own" / "Pass") and portfolio-decision.json with weights. But nothing translates these into actual trade proposals, applies sizing rules, checks sector caps, or confirms execution. The LLM output floats in a void.

**Blocker 5: Sizing rules are not enforced in code.** INVESTMENT-POLICY.md says "initial 3%, max 7%, min 1%, sector cap 35%." But `portfolio-sim.py` applies equal-weight allocation, ignoring these rules entirely. The policy is aspirational, not operational.

### Minimum viable paper portfolio: what must exist

Before you can call this "paper trading," you need exactly five things:

1. A **SQLite database** with tables for positions, transactions, and portfolio snapshots
2. A **Portfolio engine** that tracks cash, positions, and enforces sizing rules from INVESTMENT-POLICY.md
3. A **trade proposal generator** that reads pipeline verdicts and produces actionable proposals
4. A **trade executor** that records approved trades to the ledger and updates positions
5. A **snapshot mechanism** that records daily portfolio value and benchmark value for performance tracking

Everything else — dashboards, QuantStats reports, scheduling, advanced analytics — is Phase 2+.

---

## 4. Target architecture design

### How the existing pipeline connects to the new portfolio ledger

```
EXISTING PIPELINE (unchanged)
A1 (universe) → A2 (filter) → B1 (fast triage) → B2 (focused triage) → C (full analysis)
                                                                              ↓
                                                           FINAL-REPORT.json + portfolio-decision.json
                                                                              ↓
NEW PORTFOLIO LAYER ─────────────────────────────────────────────────────────────
                                                                              ↓
                                                    TradeProposalGenerator (deterministic Python)
                                                       • Reads current portfolio from SQLite
                                                       • For "Own" verdicts → propose BUY at 3%
                                                       • For "Pass" on held stocks → propose SELL
                                                       • Enforces sizing rules, sector caps, cash check
                                                                              ↓
                                                           trade_proposals table (status=PENDING)
                                                                              ↓
                                                    Human review via CLI: approve / reject / modify
                                                                              ↓
                                                           TradeExecutor
                                                       • Records transaction (append-only)
                                                       • Updates position (cost basis, shares)
                                                       • Updates cash balance
                                                                              ↓
                                                    Daily: SnapshotEngine
                                                       • Fetches current prices (cached via yfinance/Tiingo)
                                                       • Records portfolio value + benchmark value
                                                       • Feeds QuantStats for reporting
```

### Database schema (SQLite)

Six tables, all in a single `portfolio.db` file:

**positions** — mutable, one open row per ticker:
`id INTEGER PRIMARY KEY, ticker TEXT NOT NULL, sector TEXT, status TEXT DEFAULT 'OPEN', side TEXT DEFAULT 'LONG', shares REAL NOT NULL, avg_cost_basis REAL NOT NULL, total_cost REAL, current_price REAL, market_value REAL, unrealized_pnl REAL, realized_pnl REAL DEFAULT 0, weight_pct REAL, first_entry TEXT, last_update TEXT, entry_report_ref TEXT, thesis TEXT, UNIQUE(ticker, status)`

**transactions** — append-only audit log:
`id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, ticker TEXT NOT NULL, action TEXT NOT NULL, shares REAL, price REAL, total_value REAL, fees REAL DEFAULT 0, reason TEXT, report_ref TEXT, run_id TEXT, pre_trade_cash REAL, post_trade_cash REAL, position_id INTEGER REFERENCES positions(id)`

**portfolio_snapshots** — one row per trading day:
`id INTEGER PRIMARY KEY, date TEXT NOT NULL UNIQUE, total_value REAL, cash REAL, positions_value REAL, num_positions INTEGER, daily_return REAL, cumulative_return REAL, benchmark_value REAL, benchmark_return REAL, excess_return REAL, top_holdings TEXT`

**benchmark_prices** — daily close for SPY:
`date TEXT, ticker TEXT DEFAULT 'SPY', close_price REAL, daily_return REAL, UNIQUE(date, ticker)`

**trade_proposals** — human-in-the-loop staging:
`id INTEGER PRIMARY KEY, created_at TEXT, run_id TEXT, ticker TEXT, proposed_action TEXT, proposed_shares REAL, proposed_price REAL, rationale TEXT, sizing_method TEXT, rule_checks TEXT, status TEXT DEFAULT 'PENDING', reviewed_at TEXT, executed_at TEXT, transaction_id INTEGER, rejection_reason TEXT`

**research_runs** — links pipeline to trades:
`run_id TEXT PRIMARY KEY, run_date TEXT, week_folder TEXT, pipeline_stage TEXT, tickers_input TEXT, tickers_output TEXT, verdicts TEXT, status TEXT DEFAULT 'COMPLETE'`

### Core Python classes and interfaces

Four dataclasses form the core domain model. **Position** tracks a single holding with FIFO lot tracking for accurate realized P&L on partial sells. The `add_shares` method updates weighted average cost basis; `remove_shares` uses FIFO to calculate realized gains. **Portfolio** holds all positions plus cash, calculates total value and weights, and crucially enforces the sizing rules from INVESTMENT-POLICY.md via a `check_sizing_rules` method that validates initial size ≤3%, max weight ≤7%, min weight ≥1%, sector cap ≤35%, and cash sufficiency — returning a dict of pass/fail checks. **TradeProposalGenerator** reads FINAL-REPORT.json verdicts, compares against current holdings, and produces proposals for new buys, full exits, and rebalancing trims. **PortfolioSnapshot** is a frozen point-in-time record of total value, cash, positions value, and benchmark value.

Use `Decimal` for all financial math in Python — `float` produces cumulative rounding errors. Store as `REAL` in SQLite but convert immediately on read.

### Where LLMs should vs. should not be used

LLMs should handle: universe scanning rationale, qualitative analysis of filings/earnings, thesis generation, competitive moat assessment, and management quality evaluation. **LLMs must never handle**: position sizing calculations, sector cap enforcement, P&L computation, trade execution, or cash balance management. The boundary is clear — LLMs produce verdicts ("Own" / "Pass" with confidence and thesis), deterministic code enforces all portfolio rules. This separation is the architectural pattern every serious AI investing repo follows, and it's critical for auditability.

### Performance calculation approach

Use **TWRR** (time-weighted rate of return) as the primary metric for benchmark comparison — it measures strategy quality independent of cash flow timing. Calculate sub-period returns between each cash flow event, then geometrically link them. For understanding actual dollar-weighted experience, also compute **MWRR** via XIRR (scipy.optimize.brentq to find the IRR of cash flows). Feed the daily return series from portfolio_snapshots directly into QuantStats for professional tear sheets including Sharpe, Sortino, max drawdown, rolling statistics, and monthly heatmaps.

### End-to-end weekly workflow

**Monday**: Update prices, take daily snapshot, review weekend news. **Tuesday**: Run A1 (universe assembly) and A2 (candidate filter). **Wednesday**: Run B1 (fast triage) and B2 (focused triage). **Thursday**: Run C (full analysis), review FINAL-REPORTs — this is the primary human checkpoint. **Friday AM**: Run trade proposal generator against new verdicts. **Friday PM**: Review and approve proposals via CLI (`python paper_trade.py review-proposals`). Execute approved trades. **Saturday**: Generate weekly performance report via QuantStats. The daily snapshot should run every trading day via cron regardless of pipeline activity.

---

## 5. Phased implementation roadmap

### Phase 1: Minimum viable paper portfolio (weeks 1–3)

The goal is: after Phase 1, you can say "I paper-traded this week" and have a ledger to prove it.

**Deliverables**: SQLite database with all six tables. Portfolio engine with Position/Portfolio classes enforcing sizing rules. Trade proposal generator that reads FINAL-REPORT.json verdicts. CLI for reviewing/approving/executing proposals. Daily snapshot mechanism. Basic stdout reporting of portfolio state.

**Files to create**: `src/models.py` (Position, Portfolio, Transaction, Snapshot dataclasses), `src/database.py` (SQLite CRUD with schema migration), `src/portfolio_engine.py` (Portfolio class with sizing enforcement), `src/trade_proposer.py` (verdict → proposal logic), `src/trade_executor.py` (proposal → transaction + position update), `src/snapshot.py` (daily price fetch + snapshot recording), `scripts/paper_trade.py` (CLI entry point using argparse or click), `db/portfolio.db` (auto-created on first run), `db/schema.sql` (reference DDL).

**Dependencies to add**: `click` (CLI framework, pip install click). No other new deps — sqlite3 is built-in, dataclasses are built-in. Use existing yfinance for prices with retry logic.

**Acceptance criteria**: Can initialize a $100k paper portfolio. Can ingest FINAL-REPORT.json verdicts and generate trade proposals. Can approve/reject proposals via CLI. Approved trades are recorded in transactions table. Positions table reflects current holdings with cost basis. Daily snapshots capture portfolio and benchmark value. Can reconstruct full trade history from transactions table.

**What can be postponed**: Dashboard, QuantStats reports, alternative data providers, scheduling, tests (yes, tests come in Phase 2 — the schema and logic need to stabilize first).

### Phase 2: Robust research pipeline and reporting (weeks 4–6)

**Deliverables**: QuantStats integration for HTML tear sheets. Benchmark comparison (SPY). Data provider hardening (caching, retry, fallback). Research run tracking in SQLite. Basic test suite for portfolio math. Shell script wrapper for weekly workflow.

**Files to create/modify**: `src/reporter.py` (QuantStats integration + custom summary), `src/price_fetcher.py` (multi-provider with cache + retry), `src/research_tracker.py` (log pipeline runs to research_runs table), `scripts/weekly_run.sh` (orchestrate full week pipeline), `tests/test_portfolio.py` (test sizing rules, P&L calc, FIFO), `tests/test_trade_proposer.py`.

**Dependencies to add**: `quantstats` (pip install quantstats), `tiingo` (pip install tiingo) as backup price source, `edgartools` (pip install edgartools) for SEC fundamentals, `fredapi` (pip install fredapi) for macro data.

**Acceptance criteria**: Weekly HTML performance report generated automatically. Portfolio returns compared against SPY with alpha, Sharpe, and drawdown metrics. Price fetching survives yfinance outages via fallback. All pipeline runs logged with ticker-level verdicts. Core portfolio math has >90% test coverage.

### Phase 3: Monitoring, analytics, and evaluation (weeks 7–10)

**Deliverables**: Streamlit dashboard for portfolio overview and research browsing. Position monitoring with alert thresholds. Historical research quality analysis (did "Own" verdicts outperform?). PyPortfolioOpt integration for weight optimization. Scheduling via cron or GitHub Actions.

**Files to create**: `dashboard/app.py` (Streamlit dashboard), `dashboard/pages/portfolio.py`, `dashboard/pages/research.py`, `dashboard/pages/performance.py`, `src/monitor.py` (threshold alerts — price drops, weight drift, sector breach), `src/optimizer.py` (PyPortfolioOpt wrapper), `.github/workflows/weekly_research.yml` (GitHub Actions schedule).

**Dependencies to add**: `streamlit` (pip install streamlit), `plotly` (pip install plotly), `pyportfolioopt` (pip install pyportfolioopt), `openbb` (pip install openbb) for unified data access.

**Acceptance criteria**: Dashboard shows current positions, P&L, allocation chart, recent trades. Can browse past research reports by ticker and week. Alert triggers when position exceeds 7% weight or sector exceeds 35%. Weekly research pipeline runs on schedule without manual intervention. Can answer: "Which LLM verdicts were most profitable?"

### Phase 4: Optional broker integration (weeks 11+)

Even though the user chose local-only, the architecture should not preclude eventual broker integration. What would be needed: an **ExecutionAdapter** interface with `submit_order()`, `get_positions()`, `get_account_balance()` methods. The paper trading executor is one implementation; an Alpaca adapter or Interactive Brokers adapter would be another. **Alpaca** (alpaca-py, pip install alpaca-py) is the most popular choice for individual investors — free paper trading API, commission-free, REST + WebSocket. **Interactive Brokers** (ib_insync, pip install ib_insync) offers broader market access but requires TWS Gateway running locally. The key insight: if Phase 1–3 are built correctly with the ExecutionAdapter pattern, adding broker integration is a ~200-line adapter, not a rewrite.

---

## 6. Proposed directory tree and first 10 implementation tasks

### Target state directory tree

```
repo-root/
├── db/
│   ├── portfolio.db              # SQLite database (auto-created, .gitignored)
│   └── schema.sql                # Reference DDL for all tables
├── src/
│   ├── __init__.py
│   ├── models.py                 # Position, Portfolio, Transaction, Snapshot dataclasses
│   ├── database.py               # SQLite connection, CRUD ops, migrations
│   ├── portfolio_engine.py       # Portfolio class: sizing rules, sector caps, trade execution
│   ├── trade_proposer.py         # Verdict → trade proposal generation
│   ├── trade_executor.py         # Proposal → transaction recording + position update
│   ├── snapshot.py               # Daily snapshot capture: prices, portfolio value, benchmark
│   ├── price_fetcher.py          # Multi-source price fetching with cache/retry/fallback
│   ├── reporter.py               # QuantStats integration, weekly/monthly HTML reports
│   ├── research_tracker.py       # Log pipeline runs to research_runs table
│   ├── monitor.py                # Threshold alerts: weight drift, sector breach, drawdown
│   └── optimizer.py              # PyPortfolioOpt wrapper for position sizing (Phase 3)
├── scripts/
│   ├── paper_trade.py            # CLI entry point: init, propose, review, execute, snapshot, report
│   ├── portfolio-sim.py          # EXISTING — keep as legacy reference, eventually deprecate
│   ├── fetch-financials.py       # EXISTING — refactor to use price_fetcher.py
│   └── weekly_run.sh             # Shell wrapper for full weekly workflow
├── dashboard/                    # Phase 3
│   ├── app.py                    # Streamlit entry point
│   └── pages/
│       ├── portfolio.py          # Current holdings, P&L, allocation
│       ├── performance.py        # Returns, benchmark comparison, tear sheet
│       └── research.py           # Browse past analyses by ticker/week
├── tests/
│   ├── test_models.py            # Position math, cost basis, FIFO
│   ├── test_portfolio_engine.py  # Sizing rules, sector caps
│   ├── test_trade_proposer.py    # Verdict → proposal logic
│   └── test_snapshot.py          # Snapshot capture and return calculation
├── runs/                         # EXISTING — unchanged
│   └── {week}/
├── queue/                        # EXISTING — unchanged
│   └── queue.json
├── portfolios/                   # EXISTING — unchanged
│   └── {date}/
├── INVESTMENT-POLICY.md          # EXISTING — unchanged (now enforced by portfolio_engine.py)
└── requirements.txt              # Updated with new deps
```

### First 10 implementation tasks in priority order

**Task 1: Create the SQLite schema and database module**
Why first: Everything depends on persistent storage. Without this, nothing else works.
Files: `db/schema.sql`, `src/database.py`
Structure: `schema.sql` contains CREATE TABLE statements for all six tables (positions, transactions, portfolio_snapshots, benchmark_prices, trade_proposals, research_runs) with indexes. `database.py` provides a `Database` class wrapping `sqlite3.connect()` with WAL mode enabled, context manager for transactions, and methods: `init_db()`, `execute()`, `fetch_one()`, `fetch_all()`, `insert_transaction()`, `update_position()`, `insert_snapshot()`, `get_open_positions()`, `get_portfolio_state()`. Include a `migrate()` method that checks schema version and applies migrations — this prevents painful manual ALTER TABLE work later.
Dependencies: None (sqlite3 is built-in).

**Task 2: Build the core domain models**
Why second: Position, Portfolio, Transaction, and Snapshot are the vocabulary every other module speaks.
Files: `src/models.py`
Structure: Four `@dataclass` classes. `Position` with FIFO lot tracking: `add_shares(qty, price)` updates weighted average cost basis; `remove_shares(qty, price)` uses FIFO for realized P&L. `Portfolio` holding positions dict + cash, with properties for `total_value`, `positions_value`, `get_weight(ticker)`, `get_sector_weight(sector)`. `Transaction` as a frozen record. `PortfolioSnapshot` as a frozen point-in-time record. All financial fields use `Decimal`. Include `to_dict()` and `from_row()` methods for SQLite serialization.
Dependencies: None.

**Task 3: Implement the portfolio engine with sizing rule enforcement**
Why third: This is the core logic that makes the system trustworthy. Without rule enforcement, the investment policy is fiction.
Files: `src/portfolio_engine.py`
Structure: `PortfolioEngine` class that wraps `Portfolio` + `Database`. Key methods: `check_sizing_rules(ticker, sector, proposed_amount) → dict` validates initial_size ≤3%, max_weight ≤7%, min_weight ≥1%, sector_cap ≤35%, cash_sufficient. `execute_buy(ticker, shares, price, sector, reason, report_ref)` checks rules then records transaction + updates position. `execute_sell(ticker, shares, price, reason)` calculates FIFO realized P&L, records transaction, updates position. `load_from_db()` reconstructs Portfolio state from current positions table. `initialize(cash_amount)` creates a fresh portfolio.
Dependencies: Task 1 (database), Task 2 (models).

**Task 4: Build the trade proposal generator**
Why fourth: This bridges the existing LLM pipeline to the portfolio — the most critical missing connection.
Files: `src/trade_proposer.py`
Structure: `TradeProposalGenerator` class. `generate_proposals(run_id, verdicts_path) → List[dict]`: reads `portfolio-decision.json` or `FINAL-REPORT.json` files, compares verdicts against current holdings, produces proposals. New "Own" verdicts not in portfolio → BUY proposal at 3% initial size. Current holdings with "Pass" verdict → SELL proposal. Positions exceeding 7% → TRIM proposal. Each proposal includes: ticker, action, shares, price, rationale, sizing_method, rule_checks (pass/fail dict from portfolio_engine), and auto_approve flag (True only if all rules pass). Proposals are written to the trade_proposals table with status=PENDING.
Dependencies: Task 1 (database), Task 3 (portfolio engine).

**Task 5: Build the CLI entry point**
Why fifth: Without a CLI, there's no way to use the system. This is the primary user interface.
Files: `scripts/paper_trade.py`
Structure: Use `click` library. Commands: `init --cash 100000` (create fresh portfolio), `ingest-reports --week 2026-W12` (read pipeline outputs), `generate-proposals --week 2026-W12` (run trade proposer), `review-proposals` (interactive: list pending proposals, approve/reject each), `execute-approved` (run approved proposals through portfolio engine), `snapshot` (capture daily portfolio + benchmark values), `status` (print current portfolio table: ticker, shares, cost, current, P&L, weight), `history --ticker AAPL` (show all transactions for a ticker). Start with `argparse` if you want zero dependencies; switch to `click` for polish.
Dependencies: `click` (pip install click). Task 3 (portfolio engine), Task 4 (trade proposer).

**Task 6: Implement the daily snapshot mechanism**
Why sixth: Snapshots create the time series required for all performance analysis. Start capturing data immediately even before reporting is built.
Files: `src/snapshot.py`
Structure: `SnapshotEngine` class. `capture_snapshot(portfolio, date)`: fetches current prices for all open positions via yfinance (with retry + exponential backoff), fetches SPY close for benchmark, calculates portfolio total value and daily return, writes one row to portfolio_snapshots table and one row to benchmark_prices table. `backfill_benchmark(start_date, end_date)`: downloads SPY history to fill benchmark_prices table. Price caching: store fetched prices in a `price_cache` table (date, ticker, close) to avoid refetching. Important: handle weekends/holidays by carrying forward the last known price.
Dependencies: Task 1 (database), yfinance (existing).

**Task 7: Build the trade executor**
Why seventh: Completes the trading loop — proposals → approval → execution → ledger.
Files: `src/trade_executor.py`
Structure: `TradeExecutor` class. `execute_proposal(proposal_id)`: reads proposal from trade_proposals table, validates it's still PENDING, calls `portfolio_engine.execute_buy()` or `execute_sell()`, updates proposal status to EXECUTED with transaction_id reference and executed_at timestamp. `reject_proposal(proposal_id, reason)`: updates status to REJECTED with rejection_reason. `expire_stale_proposals(max_age_days=7)`: marks old PENDING proposals as EXPIRED. All execution is wrapped in a SQLite transaction for atomicity — if any step fails, the entire trade rolls back.
Dependencies: Task 3 (portfolio engine), Task 5 (CLI calls this).

**Task 8: Add price fetcher with caching and fallback**
Why eighth: Reduces yfinance dependency risk and improves data reliability for all downstream systems.
Files: `src/price_fetcher.py`
Structure: `PriceFetcher` class with provider chain pattern. `get_price(ticker, date=None) → Decimal`: checks SQLite price_cache first, then tries providers in order: (1) yfinance with retry/backoff, (2) Tiingo if API key configured, (3) FMP if API key configured. `get_history(ticker, start, end) → pd.DataFrame`: same fallback chain. `cache_price(ticker, date, price)`: writes to price_cache table. Configuration via environment variables: `TIINGO_API_KEY`, `FMP_API_KEY`. Provider health tracking: if a provider fails 3 times in a row, skip it for 1 hour. Log all provider failures for debugging.
Dependencies: yfinance (existing), optionally `tiingo` (pip install tiingo).

**Task 9: Integrate QuantStats for performance reporting**
Why ninth: Once snapshots are being captured (Task 6), you can generate the first real performance report.
Files: `src/reporter.py`
Structure: `PerformanceReporter` class. `generate_weekly_report(week)`: queries portfolio_snapshots and benchmark_prices, constructs a pandas Series of daily returns, calls `quantstats.reports.html(returns, benchmark_returns, output=f"reports/{week}/performance.html")`. `generate_summary() → dict`: returns key metrics (CAGR, Sharpe, Sortino, max drawdown, alpha, beta, current value, total P&L) for CLI display. `position_report() → pd.DataFrame`: per-position analysis with entry date, cost basis, current value, unrealized P&L, weight, days held. Store generated reports in `reports/{week}/` directory.
Dependencies: `quantstats` (pip install quantstats), `pandas` (existing).

**Task 10: Add basic tests for portfolio math**
Why tenth: The portfolio engine and FIFO P&L calculations are the most error-prone code. Tests here prevent expensive bugs that compound over time.
Files: `tests/test_models.py`, `tests/test_portfolio_engine.py`
Structure: Use `pytest`. Test cases for `test_models.py`: Position.add_shares updates cost basis correctly; Position.remove_shares FIFO calculates correct realized P&L; partial sells leave correct remaining cost basis; stock split handling adjusts shares and cost basis. Test cases for `test_portfolio_engine.py`: initial buy at 3% is allowed; buy exceeding 7% weight is rejected; sector cap at 35% is enforced; sell calculates correct realized P&L and updates cash; portfolio total_value = cash + sum(position market values); weight calculation sums to 100%. Use `Decimal` throughout tests. Each test creates an in-memory SQLite database via `:memory:` connection.
Dependencies: `pytest` (pip install pytest).

---

## Conclusion: what to actually do this week

The architecture mistakes in this repo are common ones — the most critical is treating portfolio simulation as stateless stdout output rather than persistent state. The fix is not complex: **SQLite + four Python modules + a CLI gets you to paper-trading-ready in roughly two weekends of focused work.** The existing pipeline is genuinely good; it just stops one step too early.

Three non-obvious insights from this research. First, **no off-the-shelf paper trading library fits this use case** — the custom build is smaller than the adapter code you'd write to integrate any framework. Second, **the most valuable data you're not capturing is daily portfolio snapshots** — start recording them immediately, even before the rest of the system is built, because you can't retroactively create performance history. Third, **the LLM/deterministic boundary is the most important architectural decision**: LLMs generate verdicts, deterministic code enforces rules. Every repo that blurs this line produces unreliable results. The existing INVESTMENT-POLICY.md is the right instinct — the task now is to make it executable code rather than aspirational prose.