# Agent Architecture Reference

Quick-reference for any agent working in this codebase. For full specifications, see `CLAUDE.md` at repo root.
For the docs index, see `docs/README.md`.
For the visual architecture diagram, see `docs/architecture/pipeline-architecture-diagram.md`.

---

## System Overview

Buffett-style investment analysis pipeline powered by AI agents. Stocks flow through progressive filtering (scan → triage → full analysis), producing structured reports with verdicts (Own/Watch/Pass). Reports feed into portfolio operations: allocation, pre-buy checks, paper trading, and performance tracking.

---

## Directory Map

```
.
├── runs/{week}/              # Weekly pipeline output (one complete cycle per week)
│   ├── scan/                 #   A1 + A2 output (universe.json, candidates.json)
│   ├── triage/               #   B1 + B2 output (b1-results.json, triage.json)
│   └── reports/{TICKER}/     #   Stage C output (01-09.md, FINAL-REPORT.md/.json)
│
├── context/{TICKER}/         # Input context per ticker
│   ├── financials.md         #   Auto-fetched from yfinance (24h cache)
│   ├── quant-valuation.md    #   Auto-generated DCF, sensitivity, Monte Carlo (human-readable)
│   ├── quant-valuation.json  #   Auto-generated structured valuation (machine-readable)
│   └── *.md                  #   User-provided: 10-K notes, transcripts, research
│
├── queue/                    # Central state
│   └── queue.json            #   One entry per ticker, all pipeline states
│
├── prompts/                  # Agent instruction files
│   ├── _shared-format.md     #   Output schema all analysis agents must follow
│   ├── scan-stage-a1.md      #   Universe assembly instructions
│   ├── scan-stage-a2.md      #   Candidate filter instructions
│   ├── triage-stage-b1.md    #   Fast triage instructions
│   ├── triage-stage-b2.md    #   Focused triage instructions
│   ├── 01-08*.md             #   8 umbrella analysis prompts
│   ├── 09-compact-checklist.md
│   ├── assembler.md          #   Final report assembly + JSON output
│   ├── allocator.md          #   AI portfolio construction
│   ├── monitor.md            #   Cross-run diff spec (stub)
│   └── evidence/             #   Evidence extraction prompts
│
├── scripts/                  # CLI tools (entry points)
│   ├── paper_trade.py        #   Portfolio ledger: buy/sell/short/cover/holdings
│   ├── fetch-financials.py   #   yfinance → context/{TICKER}/financials.md
│   ├── fetch-edgar.py        #   SEC EDGAR → evidence tables + optional context .md
│   ├── portfolio-sim.py      #   Snapshot allocator (hypothetical, read-only)
│   ├── prebuy-check.py       #   C1/C2/C3 gate before trades
│   ├── allocation-input.py   #   Build data blob for AI allocator
│   ├── validate.sh           #   JSON schema validation for pipeline outputs
│   ├── semantic-diff.py      #   Cross-period FINAL-REPORT comparison
│   ├── verify_claims.py      #   Fact-check extracted claims
│   ├── backfill-iv.py        #   Recompute IV via quant models
│   └── batch-revalue.py      #   Batch IV revaluation
│
├── src/                      # Python modules (imported, not run directly)
│   ├── database.py           #   SQLite wrapper, schema, migrations, CRUD
│   ├── models.py             #   Lot, Position, Portfolio dataclasses (Decimal)
│   ├── portfolio_engine.py   #   PortfolioEngine: trades, policy, FIFO, summary
│   ├── trade_proposer.py     #   Generate trade proposals from queue + reports
│   ├── trade_executor.py     #   Execute approved proposals
│   ├── price_fetcher.py      #   yfinance + Tiingo with SQLite cache (4h TTL)
│   ├── snapshot.py           #   Daily portfolio snapshots + SPY benchmark
│   ├── reporter.py           #   QuantStats performance reporting
│   ├── evidence.py           #   EvidenceDB: 8 evidence tables
│   ├── evidence_models.py    #   Evidence dataclasses
│   └── quant/                #   Deterministic valuation models
│       ├── dcf.py            #     3-scenario DCF engine
│       ├── wacc.py           #     CAPM-based WACC
│       ├── owner_earnings.py #     Owner earnings from GAAP
│       ├── montecarlo.py     #     10K simulation IV distribution
│       ├── sensitivity.py    #     WACC/growth parameter grids
│       ├── parser.py         #     Parse financials.md → model inputs
│       ├── models.py         #     DCFInputs, DCFOutputs, SensitivityTable
│       ├── formatters.py     #     Table + heatmap rendering, JSON/MD file writers
│       └── cli.py            #     CLI: --write (md), --json-out (json), --quiet, --sensitivity, --monte-carlo
│
├── db/                       # Database
│   ├── portfolio.db          #   Source of truth (SQLite)
│   └── evidence_schema.sql   #   Evidence table definitions
│
├── seeds/                    # Manual inputs
│   └── watchlist.json        #   Curated seed list for A1
│
├── portfolio/                # Portfolio-level state
│   ├── portfolio-state.md    #   Human-readable render of current holdings
│   ├── allocation-input.json #   Data blob for allocator (generated)
│   ├── config.json           #   Optional: capital_base, prebuy thresholds
│   └── archive/              #   Historical allocation runs
│
├── dashboard/                # Streamlit UI (read-only)
│   └── app.py                #   5 pages: Workspace, Research, Performance, PreBuy, Simulator
│
├── docs/                     # Architecture docs
│   ├── AGENTS.md             #   This file
│   └── pipeline-architecture.md  # Mermaid diagram of full system
│
├── run.sh                    # Central dispatcher for all commands
├── CLAUDE.md                 # Full pipeline specification
├── INVESTMENT-POLICY.md      # Position sizing and portfolio rules
└── README.md                 # User-facing overview
```

---

## Pipeline Stages

| Stage | Trigger | Agent(s) | Input | Output | Output Dir |
|-------|---------|----------|-------|--------|------------|
| **A1** Universe Assembly | `run A1`, `run scan` | 1 general | seeds + tracked + curated + web | `universe.json`, `universe-meta.json` | `runs/{week}/scan/` |
| **A2** Candidate Filter | `run A2`, `run scan` | 1 general | `universe.json` | `candidates.json`, `.csv`, `.md`, `scan-meta.json` | `runs/{week}/scan/` |
| **B1** Fast Triage | `run B1`, `run triage` | 1 general | `candidates.json` | `b1-results.json`, `b1-advance.json`, `b1-summary.md` | `runs/{week}/triage/` |
| **B2** Focused Triage | `run B2`, `run triage` | 1 general | `b1-advance.json` + existing reports | `triage.json`, `triage.md`, `deep-dive.csv` | `runs/{week}/triage/` |
| **Fetch** | `fetch TICKER`, auto before analyze | 1 script | yfinance API | `context/{TICKER}/financials.md` | `context/` |
| **Quant** | auto before analyze (after fetch) | `src/quant` CLI | `context/{TICKER}/financials.md` | `quant-valuation.md` + `.json` | `context/{TICKER}/` |
| **C** Full Analysis | `analyze TICKER` | 3 parallel + 2 sequential | context/ + prompts/ | 01-09.md + FINAL-REPORT.md/.json | `runs/{week}/reports/{TICKER}/` |
| **Allocate** | `allocate` | 1 general | queue + reports + prices + portfolio | `allocation-proposal.json/.md` | `portfolio/allocations/{run-id}/` |

### Stage C Detail

```
                    ┌─────────────────────┐
                    │   Fetch Financials   │  (auto, before analysis)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Fetch SEC EDGAR   │  (auto, non-blocking)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Quant Valuation   │  (auto, non-blocking)
                    │   DCF + WACC +      │  writes quant-valuation.md
                    │   Monte Carlo +     │  + quant-valuation.json
                    │   Sensitivity +     │  to context/{TICKER}/
                    │   Owner Earnings    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
     ┌────────────────┐ ┌───────────────┐ ┌─────────────────┐
     │ Business Agent │ │Finance Agent  │ │Valuation Agent  │
     │ 01 Competence  │ │04 Economics   │ │06 Valuation+IV  │
     │ 02 Moat        │ │05 Balance Sht │ │07 Margin Safety │
     │ 03 Management  │ │               │ │08 Temperament   │
     └───────┬────────┘ └──────┬────────┘ └────────┬────────┘
              │                │                     │
              └────────────────┼─────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │  09 Checklist Agent  │  (reads 01-08)
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Assembler Agent   │  (reads 01-09 + quant JSON)
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            FINAL-REPORT.md       FINAL-REPORT.json
            (full narrative)      (verdict+scores+IV
                                   +iv_source
                                   +mc_prob
                                   +sensitivity_range)
                                          │
                                          ▼
                                    queue.json
                                    (state update)
```

Each analysis agent reads:
- Its prompt file(s) from `prompts/`
- `prompts/_shared-format.md` (output schema)
- All files in `context/{TICKER}/` (including `quant-valuation.md` and `quant-valuation.json` — deterministic DCF output)
- Uses WebSearch for current data

The Valuation Agent (umbrella 06) uses the quant model as its **starting anchor** — stress-testing and adjusting the deterministic IV rather than computing from scratch. The Assembler **prefers quant-model IV** over AI-extracted IV when populating FINAL-REPORT.json.

---

## Queue State Machine

```
                    ┌─────────┐
         A2 ──────▶│  triage  │ (transient)
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌─────────┐ ┌──────────┐
B1 hold ▶│ inbox  │ │rejected │ │deep_     │◀ B2 deep_dive
         └───┬────┘ └─────────┘ │research  │
             │                   └────┬─────┘
        B2 triage                     │
             │               Stage C completes
             ▼                        │
        ┌──────────┐          ┌───────▼───────┐
        │watchlist │          │ monitor_only  │
        └──────────┘          └───────────────┘
                                      │
                               (manual only)
                                      │
                              ┌───────▼───────┐
                              │   approved    │
                              └───────┬───────┘
                                      │
                               (manual only)
                                      │
                              ┌───────▼───────┐
                              │    owned      │
                              └───────────────┘
```

**Who writes queue.json:**
| Writer | Updates |
|--------|---------|
| B1 agent | `hold` → inbox, `reject` → rejected |
| B2 agent | `deep_dive` → deep_research, `monitor` → watchlist, `discard` → rejected |
| Assembler | deep_research → monitor_only, sets verdict + date + thesis |
| Manual | monitor_only → approved → owned |

**Who reads queue.json:**
- B2 (existing reports for refresh), Allocator, Pre-Buy, Portfolio Sim, Policy Engine, Dashboard (3 pages)

---

## Key Files

| File | Role |
|------|------|
| `run.sh` | Central dispatcher — all pipeline commands route through here |
| `CLAUDE.md` | Full pipeline specification (canonical reference) |
| `queue/queue.json` | Central state — every ticker the pipeline has touched |
| `prompts/_shared-format.md` | Output schema for all 8 umbrella analysis sections |
| `prompts/assembler.md` | Defines FINAL-REPORT.md + FINAL-REPORT.json structure |
| `runs/{week}/reports/{TICKER}/FINAL-REPORT.json` | Key artifact: verdict, scores, IV, triggers |
| `context/{TICKER}/financials.md` | Auto-fetched financial data (yfinance) |
| `db/portfolio.db` | SQLite: positions, lots, transactions, snapshots, prebuy_checks |
| `src/portfolio_engine.py` | Trade execution, policy enforcement, FIFO lot tracking |
| `src/database.py` | SQLite schema, migrations, all CRUD operations |
| `src/price_fetcher.py` | Price fetching with cache (yfinance primary, Tiingo fallback) |
| `seeds/watchlist.json` | Curated seed list for A1 universe assembly |
| `portfolio/config.json` | Optional: capital_base, prebuy thresholds |
| `INVESTMENT-POLICY.md` | Position sizing rules, sector limits, sell triggers |

---

## CLI Commands

All commands via `./run.sh <command>`:

| Command | What it does |
|---------|-------------|
| `scan` | Run A1 + A2 (universe assembly + candidate filter) |
| `triage [week]` | Run B1 + B2 (fast triage + focused triage) |
| `fetch TICKER [...]` | Fetch financials from yfinance → context/{TICKER}/financials.md |
| `fetch --all-reports` | Fetch financials for all tickers with existing reports |
| `analyze TICKER` | Auto-fetch + run full 8-umbrella analysis + assemble |
| `allocate [CAPITAL]` | AI portfolio construction from queue + reports |
| `portfolio [CAPITAL]` | Snapshot portfolio simulator (read-only, hypothetical) |
| `buy TICKER --price P --amount A --iv IV` | Paper trade: open long position |
| `sell TICKER --price P --shares N` | Paper trade: close/trim long |
| `short TICKER --price P --shares N --iv IV` | Paper trade: open short position |
| `cover TICKER --price P --shares N` | Paper trade: close/trim short |
| `holdings` | Print current portfolio state |
| `ledger init --capital N` | Initialize empty portfolio ledger |
| `ledger refresh [TICKER...]` | Update prices via yfinance |
| `ledger history` | Print transaction log |
| `prebuy TICKER` | Run C1/C2/C3 pre-buy gate check |
| `prebuy --own` | Dashboard: C1/C2 for all Own-verdict tickers |
| `snapshot` | Capture daily portfolio snapshot for performance tracking |
| `dashboard` | Launch Streamlit dashboard |
| `validate <type>` | JSON schema validation for pipeline outputs |
| `monitor TICKER` | Cross-run diff report (stub — not yet implemented) |

---

## Data Flow Summary

```
seeds + tracked + curated + web
         │
         ▼
    universe.json (150-400)
         │
         ▼
    candidates.json (80-150)
         │
         ▼
    b1-advance.json (survivors)  ──▶  queue.json (hold/reject)
         │
         ▼
    triage.json ──────────────────▶  queue.json (watchlist/deep_research)
         │
    deep-dive.csv (max 8)
         │
         ▼
    context/{TICKER}/ ◀── fetch-financials.py + fetch-edgar.py
         │
         ▼
    quant-valuation.md + .json ◀── src/quant (DCF, WACC, MC, sensitivity)
         │
         ▼
    01-08.md → 09-checklist.md → FINAL-REPORT.md + .json ──▶ queue.json
                                        │
                    ┌───────────────────┬┴──────────────────┐
                    ▼                   ▼                    ▼
              AI Allocator        Pre-Buy Check        Policy Engine
              allocation-         C1/C2/C3 gates       7 hard + 5 soft
              proposal.json/md                         rules
                                                            │
                                                            ▼
                                                      paper_trade.py
                                                            │
                                                            ▼
                                                      db/portfolio.db
                                                      (positions, lots,
                                                       transactions)
                                                            │
                                                            ▼
                                                      snapshot.py → snapshots
                                                            │
                                                            ▼
                                                      Dashboard (5 pages)
```

**Feedback loops:**
- FINAL-REPORT.md → B2 (for refresh decisions on already-analyzed tickers)
- FINAL-REPORT.json → next scan cycle (tracked tickers feed A1)

---

## Conventions

| Convention | Rule |
|-----------|------|
| **Weekly folders** | All output in `runs/weekNN_DD.MM/`. Never write directly under `runs/`. Update `CURRENT_WEEK` in `run.sh` + `CLAUDE.md` at start of each week. |
| **Ticker format** | Always uppercase: `AAPL`, `MC.PA`, `NOVO-B.CO`, `BRK.B` |
| **Arithmetic** | All financial math uses `Decimal`, never `float` |
| **JSON is source of truth** | Markdown files are renders only. JSON files are canonical. |
| **Freshness** | `financials.md`: 24h cache. Prices: 4h SQLite cache. Snapshots: idempotent per trading day. |
| **Weekend prices** | Return Friday close on weekends |
| **Reports** | Must follow `prompts/_shared-format.md` schema exactly |
| **Queue updates** | Only B2 agent, Assembler agent, or manual user edits touch queue.json |
| **Portfolio dir** | Use `portfolio/` (not `portfolios/`) for all portfolio-level state |
| **Policy before trades** | Every buy/short runs through PolicyEngine before execution |

---

## Database Tables (db/portfolio.db)

**Core:**
| Table | Purpose |
|-------|---------|
| `positions` | One open row per ticker (side=LONG\|SHORT, status, shares, avg_cost) |
| `lots` | FIFO lot tracking (shares, cost_per_share, purchase_date) |
| `transactions` | Append-only ledger (INIT/BUY/SELL/SHORT/COVER with price, value, P&L) |

**Tracking:**
| Table | Purpose |
|-------|---------|
| `portfolio_snapshots` | Daily: total_value, cash, cumulative_return, SPY benchmark |
| `prebuy_checks` | C1/C2/C3 gate history per ticker |
| `trade_proposals` | PENDING/APPROVED/REJECTED/EXECUTED proposals |
| `sim_runs` | Snapshot allocation simulation results |
| `price_cache` | yfinance/Tiingo prices with 4h TTL |

**Evidence (separate schema):**
| Table | Purpose |
|-------|---------|
| `source_documents` | SEC filing metadata |
| `document_sections` | Parsed filing sections |
| `extracted_facts` | Structured facts from filings |
| `assertions` | Report claims to verify |
| `assertion_evidence` | Links assertions to supporting facts |
| `verification_runs` | Fact-check run results |
| `semantic_diffs` | Cross-period filing comparisons |
| `computation_cache` | Cached quant model results |

---

## Policy Engine Rules

Every trade runs through `src/portfolio_engine.py` before execution.

**Hard blocks (refuse):**
| Rule | Threshold |
|------|-----------|
| Single name weight | > 7% gross |
| Sector gross weight | > 35% gross |
| Gross exposure | > 130% |
| Net exposure | > 100% or < -30% |
| Verdict mismatch | Buying a Pass-verdict stock |
| Thesis break | Weakened/changed thesis status |

**Soft blocks (warn, --force to override):**
| Rule | Threshold |
|------|-----------|
| Single name warning | > 5% gross |
| Margin of safety | MOS < 0% (price > IV) |
| Stale analysis | Report > 6 months old |
| No report | Missing FINAL-REPORT.json |
| Minimum breadth | < 5 positions |

---

## Local Instructions

- For any dashboard change, ensure the Streamlit app is running (`./run.sh dashboard`) before closing the task.
- After UI changes, verify the Streamlit dashboard is responding successfully and report that verification in the final response.
- Do not treat a UI task as complete until the dashboard is active and the updated UI has been checked there.
