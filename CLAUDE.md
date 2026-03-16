# Investment Analysis Workbench

This project is a Buffett-style investment analysis system powered by Claude Code agents. Each "umbrella" of analysis is handled by a specialized agent role, all following the same output format.

## Current Pipeline Run

| | |
|---|---|
| **Current week** | `week12_16.03` |
| **Active scan** | `runs/week12_16.03/scan/` |
| **Active triage** | `runs/week12_16.03/triage/` |
| **Active reports** | `runs/week12_16.03/reports/` |

**Update `CURRENT_WEEK` in `run.sh` (line ~27) and the table above when a new week begins.**

All pipeline output lives under `runs/`. Each week folder contains `scan/`, `triage/`, and `reports/` — one complete cycle in one place. Global state (`context/`, `queue/`, `seeds/`) lives at repo root.

---

## How It Works

When a user asks to analyze a stock (e.g., "analyze AAPL" or "run analysis on MSFT"), follow this workflow:

### Step 1: Setup
1. Create directory `runs/{CURRENT_WEEK}/reports/{TICKER}/` if it doesn't exist.
2. Read `prompts/_shared-format.md` — this is the output schema all agents must follow.
3. Financial data is auto-fetched before analysis (see "Financial Data Fetch" section below). Check if `context/{TICKER}/` exists. If it does, read all files in it — this includes auto-fetched financials and any user-provided research (10-K notes, earnings transcripts, etc.). Pass this context to every agent.

### Step 2: Run Analysis Agents (3 parallel batches)
Spawn 3 Agent subagents in parallel. Each agent gets:
- The shared format from `prompts/_shared-format.md`
- Its specific umbrella prompt(s) from `prompts/`
- The ticker symbol and today's date
- Any user-provided context files
- Instruction to use web search for current financial data

**Business Analyst Agent** (umbrellas 1-3):
- Read prompts: `01-circle-of-competence.md`, `02-durable-competitive-advantage.md`, `03-management-capital-allocation.md`
- Write output to: `runs/{CURRENT_WEEK}/reports/{TICKER}/01-circle-of-competence.md`, `…/02-durable-competitive-advantage.md`, `…/03-management-capital-allocation.md`

**Financial Analyst Agent** (umbrellas 4-5):
- Read prompts: `04-business-economics.md`, `05-balance-sheet-safety.md`
- Write output to: `runs/{CURRENT_WEEK}/reports/{TICKER}/04-business-economics.md`, `…/05-balance-sheet-safety.md`

**Valuation Analyst Agent** (umbrellas 6-8):
- Read prompts: `06-valuation-intrinsic-value.md`, `07-margin-of-safety.md`, `08-temperament-time-horizon.md`
- Write output to: `runs/{CURRENT_WEEK}/reports/{TICKER}/06-valuation-intrinsic-value.md`, `…/07-margin-of-safety.md`, `…/08-temperament-time-horizon.md`

Each agent should:
- Use **WebSearch** to find current financial data, recent news, and analyst estimates
- Follow the shared format EXACTLY for each section
- Write each section to its own file in `runs/{CURRENT_WEEK}/reports/{TICKER}/`
- Be honest about data sources and confidence levels

### Step 3: Compact Checklist
After all 3 agents complete, spawn one more agent:

**Checklist Agent** (umbrella 9):
- Read prompt: `09-compact-checklist.md`
- Read all completed sections from `runs/{CURRENT_WEEK}/reports/{TICKER}/` (01-08)
- Write output to: `runs/{CURRENT_WEEK}/reports/{TICKER}/09-compact-checklist.md`

### Step 4: Final Report Assembly
Spawn one final agent:

**Synthesis Agent**:
- Read prompt: `assembler.md`
- Read ALL section files from `runs/{CURRENT_WEEK}/reports/{TICKER}/` (01-09)
- Write output to: `runs/{CURRENT_WEEK}/reports/{TICKER}/FINAL-REPORT.md` AND `runs/{CURRENT_WEEK}/reports/{TICKER}/FINAL-REPORT.json`
- After writing both files, update `queue/queue.json`: set `current_state = monitor_only`, `last_analysis_date = today`, `current_verdict` from FINAL-REPORT.json, `thesis_status = intact`, `next_required_action = monitor`

### Step 5: Present Results
After the final report is written, show the user:
1. The **verdict** (Own / Watch / Pass)
2. The **score dashboard** (table of all 8 scores)
3. The **compact checklist** (8 forced sentences)
4. Let them know the full report is at `runs/{CURRENT_WEEK}/reports/{TICKER}/FINAL-REPORT.md`

## Pipeline Overview

```
Stage A1 (Universe Assembly)  →  runs/{week}/scan/    (universe.json + universe-meta.json)
Stage A2 (Candidate Filter)   →  runs/{week}/scan/    (candidates.json + csv + md + scan-meta.json)
Stage B1 (Fast Triage)        →  runs/{week}/triage/  (b1-results.json, b1-advance.json, b1-summary.md)
Stage B2 (Focused Triage)     →  runs/{week}/triage/  (triage.json, triage.md, deep-dive.csv)
Fetch (Financial Data)        →  context/{TICKER}/financials.md
Stage C  (Full Analysis)      →  runs/{week}/reports/{TICKER}/
Queue                         →  queue/queue.json
Portfolio Simulator           →  stdout (snapshot allocation from queue + FINAL-REPORT.json)
```

---

## Stage A1: Universe Assembly

**Trigger phrases:** "run A1", "run universe assembly", "rebuild universe"
**Also triggered by:** "run scan", "run Stage A", "refresh universe", "rebuild candidate list", "update candidates" — followed by A2

Stage A1 builds a broad raw stock universe. Its job is assembly and deduplication only — no scoring, no thesis construction, no prioritization.

### Purpose
Merge candidates from multiple sources into a single raw universe JSON. Tag each entry with source/category metadata. Produce 150–400 unique names for A2 to filter.

### Inputs
1. **Tracked** — `runs/*/reports/` directories → `source_bucket: tracked`
2. **Seed** — `seeds/watchlist.json` → `source_bucket: seed`
3. **Built-in curated lists** (embedded in prompt, agent prior knowledge) → sector bucket names
4. **Web searches** — up to 6 queries for event/signal buckets

### Source buckets
| bucket | how to populate |
|--------|----------------|
| `tracked` | existing `runs/*/reports/` directories |
| `seed` | `seeds/watchlist.json` |
| `large_cap_us_quality` | built-in list: ~30 US quality compounders |
| `large_cap_europe_quality` | built-in list: ~20 European quality names |
| `semis_and_infra` | built-in list: ~15 semiconductor + tech infra names |
| `healthcare_quality` | built-in list: ~15 pharma/medtech/diagnostics names |
| `industrial_compounders` | built-in list: ~15 quality industrial names |
| `financial_quality` | built-in list: ~15 financial quality names |
| `consumer_quality` | built-in list: ~15 quality consumer names |
| `post_earnings` | web search: notable earnings movers last 30 days |
| `52wk_low` | web search: quality large-caps near 52-week low |
| `52wk_high` | web search: quality large-caps near 52-week high |
| `fcf_roic` | web search: high FCF yield or ROIC names |
| `sector_leader` | web search: dominant names by sector not already in universe |

### Output files
| file | purpose |
|------|---------|
| `runs/{week}/scan/universe.json` | source of truth — raw array, minimal schema |
| `runs/{week}/scan/universe-meta.json` | run metadata + counts by bucket/sector/geography + concentration_warnings |

### How to run
Read `prompts/scan-stage-a1.md` — full execution template. Spawn one general-purpose agent.

### Constraints
- No thesis_tag, no priority, no triage_rec — that is A2's job
- No analysis prose. No valuation math.
- Dedup: one entry per ticker; merge source_bucket arrays
- If tracked + seed exceed 20% of total, that's a signal the curated sector lists are under-represented — ensure all sector buckets were populated
- Skip micro-caps, SPACs, pre-revenue, pure commodity plays
- JSON is source of truth

---

## Stage A2: Candidate Filter

**Trigger phrases:** "run A2", "filter candidates"
**Also triggered by:** "run scan", "run Stage A" — as the second step after A1

Stage A2 takes the raw A1 universe and applies lightweight filtering, prioritization, and tagging to produce a ranked candidate list for Stage B.

### Purpose
Reduce the A1 universe (150–400 names) to a manageable candidate set (80–150 names) with enough signal for Stage B to triage. No deep research, no valuation narratives.

### Inputs
1. Most recent `runs/{week}/scan/universe.json` — primary input
2. Agent's own knowledge of these businesses (no web search unless critical gap)

### Output files
| file | purpose |
|------|---------|
| `runs/{week}/scan/candidates.json` | source of truth — ranked/filtered candidates |
| `runs/{week}/scan/candidates.csv` | flat CSV, pipe-delimited source_bucket |
| `runs/{week}/scan/candidates.md` | human-readable table + summary stats |
| `runs/{week}/scan/scan-meta.json` | run metadata + ranking rules v2 snapshot |

### How to run
Read `prompts/scan-stage-a2.md` — full execution template. Spawn one general-purpose agent with the scan week.

### Constraints
- No additional web searches (A1 already ran them) unless one critical fact is missing
- No valuation math. No multi-sentence descriptions.
- JSON is source of truth. Markdown is a render only.
- A2 feeds Stage B1 triage — do not skip to full analysis from here.

---

## Stage B1: Fast Triage

**Trigger phrases:** "run B1", "run fast triage"
**Also triggered by:** "run triage", "run Stage B" — as the first step, followed by B2

Stage B1 is a mechanical filter pass over the A2 candidate list. Harsh, fast, no web search. Every name gets one verdict.

### Purpose
Eliminate obvious no's. Reduce the A2 candidate list to a smaller advance set for B2. B1 hold names auto-become `inbox` (queue state) — they never enter B2.

### Inputs
1. Most recent `runs/{week}/scan/candidates.json` — primary input
2. Agent's prior knowledge only — no web search

### How to run
Read `prompts/triage-stage-b1.md` — full execution template. Spawn one general-purpose agent with the scan week.

### B1 verdict values
- `advance` — quality business, moat demonstrable, worth a real second look in B2
- `hold` — passes quality bar but no reason to act now; auto-becomes `inbox`
- `reject` — eliminated: pre-profit/speculative, extreme leverage, commodity, Pass verdict with no change, or outside circle of competence

### Output files
| file | purpose |
|------|---------|
| `runs/{week}/triage/b1-results.json` | all records (advance + hold + reject) |
| `runs/{week}/triage/b1-advance.json` | survivors only — input for B2 |
| `runs/{week}/triage/b1-summary.md` | compact one-line table + counts |

### Constraints
- No web search
- No scores, no valuation math, no essays
- One `b1_reason` per name (≤ 12 words)
- JSON is source of truth

---

## Stage B2: Focused Triage

**Trigger phrases:** "run B2", "run focused triage"
**Also triggered by:** "run triage", "run Stage B" — as the second step after B1
**Date argument:** "triage latest" or "triage week11_09.03" — not "triage TICKER"

Stage B2 applies thoughtful triage to the B1 advance set. Still not deep research, but a genuine opinion on each name.

### Purpose
Assign a real `next_action` to each B1 survivor. Produce a clean deep-dive shortlist (≤8 names) and monitor/refresh set.

### Inputs
1. `runs/{week}/triage/b1-advance.json` — primary input
2. `runs/{week}/scan/scan-meta.json` — supporting context
3. `runs/*/reports/{TICKER}/FINAL-REPORT.md` for each already-analyzed ticker

### How to run
Read `prompts/triage-stage-b2.md` — full execution template. Spawn one general-purpose agent with the triage week.

### next_action values
- `deep_dive` — new name, high quality, understandable, reasonable valuation setup; run full 8-umbrella pipeline
- `refresh` — already analyzed; thesis evolved materially, price moved >20%, or report >6 months old
- `monitor` — quality business; wrong price or no catalyst; or already analyzed with intact thesis
- `discard` — speculative, extreme leverage, commodity, or Pass verdict with no change

### Research budget
Hard cap: **8 deep_dives per batch.** Additional high-conviction names become `monitor` with reason prefixed "Above-budget:". See `prompts/triage-stage-b2.md` for full rules.

### Queue update (after B2 completes)
After writing triage output files, update `queue/queue.json`:
- B2 `deep_dive` → `current_state = deep_research`
- B2 `monitor` → `current_state = watchlist`
- B2 `discard` → `current_state = rejected`
- B1 `hold` → `current_state = inbox` (if not already present)
- B1 `reject` → `current_state = rejected` (if not already present)
- New tickers not in queue get added; existing entries get state and dates updated
- Set `last_triage_date` for all touched entries

### Output files
| file | purpose |
|------|---------|
| `runs/{week}/triage/triage.json` | source of truth — one record per B2 candidate |
| `runs/{week}/triage/triage.md` | human-readable report + shortlists |
| `runs/{week}/triage/deep-dive.csv` | deep dive shortlist export (optional) |

### Constraints
- No deep analysis. No umbrella writeups. No valuation narratives.
- JSON is the source of truth. Markdown is a render only.
- WebSearch: 3–5 names max, only where price or recent news flips the decision.
- Do not mirror Stage A priority — triage agent must re-rank independently.
- Hard cap: ≤8 deep_dives. Based on genuine conviction only.
- Stage B2 feeds Stage C (full analysis) — do not skip to deep dive without triage.

---

## Queue

The queue is a living state file that tracks every ticker the pipeline has touched.

### File: `queue/queue.json`

One entry per ticker. Schema:
```json
{
  "ticker": "",
  "company": "",
  "current_state": "inbox|triage|watchlist|deep_research|approved|owned|monitor_only|rejected",
  "priority": "high|medium|low",
  "source_batch": "YYYY-MM-DD",
  "last_analysis_date": null,
  "last_triage_date": "YYYY-MM-DD",
  "current_verdict": null,
  "thesis_status": "intact|weakened|changed|unknown",
  "next_required_action": "",
  "owner_notes": "",
  "tags": []
}
```

### State definitions
| state | meaning |
|-------|---------|
| `inbox` | B1 hold — quality but no immediate catalyst; not yet triaged in B2 |
| `triage` | currently being triaged (transient) |
| `watchlist` | B2 monitor — quality business, waiting on better price or catalyst |
| `deep_research` | B2 deep_dive — assigned for full 8-umbrella analysis this cycle |
| `approved` | Own verdict — approved for potential position; manual update required |
| `owned` | Currently held position; manual update required |
| `monitor_only` | Full analysis complete; thesis intact; no action needed |
| `rejected` | B1 reject or B2 discard — eliminated from pipeline |

### Queue maintenance
Two pipeline steps update the queue automatically:

**After triage (B2):** B2 agent updates queue per the "Queue update" rules in Stage B2 above.

**After analyze (assembler):** Assembler agent updates queue entry for the ticker: `current_state` (if `deep_research` → `monitor_only`), `last_analysis_date`, `current_verdict`, `thesis_status = intact`, `next_required_action = monitor`. Does not touch `owner_notes` or `tags`.

**Manual updates:** `approved` and `owned` states require manual update. Owner notes and tags are always manual.

### Human-readable view: `queue/queue.md`
Sections: Summary / Deep Research Pipeline / Watchlist / Monitor / Rejected.

---

## Structured Outputs

Every `analyze TICKER` run produces two files:

- `reports/{TICKER}/FINAL-REPORT.md` — full narrative report (as always)
- `reports/{TICKER}/FINAL-REPORT.json` — machine-readable structured summary

The JSON includes verdict, all 8 umbrella scores, key strengths/risks/flags, buy/sell triggers, valuation summary, source summary, and confidence. See `prompts/assembler.md` for the full schema.

JSON enables: queue updates, monitor/diff engine, cross-run comparisons, dashboard rendering.

---

## Portfolio Simulator

**Trigger phrases:** "simulate portfolio", "portfolio sim", "what would I hold", "run portfolio", "show me the portfolio"
**Script:** `scripts/portfolio-sim.py` — no network calls, reads queue + FINAL-REPORT.json locally

A snapshot allocator. Given $X capital, applies the pipeline's own ranking logic (verdict → score → confidence) and deploys equal weight into the top-ranked names. Not a backtest.

### What it shows
1. **Holdings table** — ranked positions with verdict, score, confidence, weight %, and dollar value
2. **Sector exposure** — names and $ per sector (derived from queue tags)
3. **Concentration stats** — top 1/3/5 weight, HHI, total red flags across positions

### How to run
```bash
./run.sh portfolio                                           # Own-verdict, $100K, top 20
./run.sh portfolio 250000                                    # Own-verdict, $250K
./run.sh portfolio 500000 --min-verdict watch --top 15      # Include Watch, cap at 15
./run.sh portfolio --output json                            # Machine-readable JSON
```

Or directly: `python3 scripts/portfolio-sim.py [OPTIONS]`

### Options
| flag | default | meaning |
|------|---------|---------|
| `--capital X` | 100000 | Starting capital in dollars |
| `--top N` | 20 | Max positions (0 = all eligible) |
| `--min-verdict` | own | Minimum verdict tier: `own` or `watch` |
| `--states` | monitor_only,approved,owned | Queue states to draw from |
| `--output` | table | Output format: `table` or `json` |

### Eligibility and ranking
- Eligible: `current_state` in allowed states + `current_verdict` meets min-verdict + `FINAL-REPORT.json` exists
- Ranked: verdict (Own=2 > Watch=1) → `average_score` desc → confidence (high > medium > low) desc
- Allocation: equal weight across all selected positions

### Sector derivation
Sector is inferred from queue `tags` using a tag→sector mapping (first matching tag wins). See `scripts/portfolio-sim.py` for the full `TAG_SECTOR` dict. Falls back to `"Other"`.

---

## Portfolio Ledger

**Trigger phrases:** "buy TICKER", "sell TICKER", "short TICKER", "cover TICKER", "show holdings", "refresh prices", "ledger init", "ledger history"

Persistent portfolio tracking with transaction history and policy compliance. Independent from the portfolio simulator (which is hypothetical). The ledger records actual paper-trade decisions.

### Files
| file | purpose |
|------|---------|
| `db/portfolio.db` | Source of truth — SQLite database (positions, lots, transactions) |
| `portfolio/portfolio-state.md` | Human-readable render, regenerated on every mutation |
| `scripts/paper_trade.py` | Core script with all subcommands (SQLite-backed) |
| `scripts/portfolio-ledger.py` | Legacy JSON-backed script (retained as fallback during transition) |

### How to run
```bash
./run.sh ledger init --capital 100000              # Initialize empty ledger
./run.sh buy V --price 312.50 --amount 3000 --iv 380 --reason "Own verdict"
./run.sh sell V --price 340 --shares 5 --reason "Trim to target"
./run.sh short CAT --price 705 --shares 10 --iv 272
./run.sh cover CAT --price 600 --shares 10
./run.sh holdings                                  # Print portfolio state
./run.sh holdings --output json                    # Machine-readable output
./run.sh ledger refresh                            # Update prices via yfinance
./run.sh ledger refresh V ADBE                     # Specific tickers only
./run.sh ledger check buy V --price 312 --amount 5000  # Dry-run policy check
./run.sh ledger history                            # Transaction log
./run.sh ledger history --ticker V --last 10       # Filtered history
./run.sh ledger migrate --from portfolio/ledger.json           # Migrate JSON → SQLite
./run.sh ledger migrate --from portfolio/ledger.json --dry-run # Preview without writing
```

### Policy rules
Every buy/short trade runs through the policy engine before execution.

| rule | threshold | severity |
|------|-----------|----------|
| Single name weight | > 7% gross | hard (refuse) |
| Single name warning | > 5% gross | soft (warn, --force to override) |
| Sector gross weight | > 35% gross | hard |
| Gross exposure | > 130% | hard |
| Net exposure max | > 100% | hard |
| Net exposure min | < -30% | hard |
| Verdict mismatch | buying Pass-verdict (Own and Watch allowed) | hard |
| Thesis break | weakened/changed status | hard |
| Margin of safety | MOS < 0% (price > IV) | soft |
| Stale analysis | report > 6 months old | soft |
| No report | missing FINAL-REPORT.json | soft |
| Minimum breadth | < 5 positions | soft |

### Cash model
`cash = total_capital - sum(long cost_basis)`. Shorts track notional exposure but don't consume cash. Short P&L: `(entry_price - current_price) * shares`.

### Intrinsic value
The `--iv` flag on buy/short provides the user's intrinsic value estimate. Not parsed from reports (valuation_summary is prose). MOS = `(IV - price) / IV` for longs.

---

## Dashboard

**Trigger phrases:** "open dashboard", "run dashboard", "show streamlit dashboard"
**Entry point:** `dashboard/app.py`

Read-only Streamlit dashboard layered alongside the Flask research browser. The dashboard never writes to `db/portfolio.db`. Portfolio and performance views read SQLite through `Database` and `PortfolioEngine`; research view reads the latest `FINAL-REPORT.json` / `FINAL-REPORT.md` plus `queue/queue.json`.

### Pages
1. **Portfolio** — current holdings, allocation pie, sector exposure, policy flags, top-level stats
2. **Performance** — cumulative portfolio return vs SPY, QuantStats summary, monthly heatmap when enough snapshots exist
3. **Research** — ticker selector, verdict, score table, strengths/risks, queue state, inline full report

### How to run
```bash
./run.sh dashboard
```

### Data freshness
- Dashboard reads are cached with a 60-second TTL.
- If performance history is missing, take a daily snapshot with:
```bash
./run.sh snapshot
```

---

## Pre-Buy Checklist

**Trigger phrases:** "prebuy TICKER", "pre-buy check TICKER", "check before buying TICKER"
**Script:** `scripts/prebuy-check.py`

Three-condition gate before a paper-trade buy.

### Conditions
| | Condition | Automatable |
|---|---|---|
| C1 | Quality gate: verdict=Own, avg≥7.0, no umbrella<4, MOS score≥6 | Yes |
| C2 | Price vs IV: current price ≤ iv_conservative × (1 − threshold%) | Yes (needs IV data) |
| C3 | 3-sentence conviction check | Manual (interactive only) |

### How to run
```bash
./run.sh prebuy GILD                 # Single ticker, interactive C3
./run.sh prebuy GILD --dry-run-buy   # GO + write portfolio/pending/GILD-YYYY-MM-DD.json
./run.sh prebuy --own                # Dashboard: C1/C2 for all Own-verdict tickers
./run.sh prebuy GILD --capital 250000
```

### portfolio/config.json (optional, user-created)
Override defaults by creating `portfolio/config.json`:
```json
{
  "capital_base": 250000,
  "prebuy_min_score": 7.0,
  "prebuy_min_mos_score": 6,
  "prebuy_mos_threshold_pct": 20
}
```
`portfolio/` is the home for all portfolio-level state: ledger, transaction log, config, and pending dry-run records. Prefer `portfolio/` over `portfolios/` for all new files.

### IV data requirement
C2 requires `iv_conservative` in `FINAL-REPORT.json`. Existing reports without it show `N/A` in the dashboard and `CANNOT VERIFY` in single-ticker mode. Backfill with: `./run.sh analyze TICKER assemble`

### --dry-run-buy
When all 3 conditions pass, writes a pending record to `portfolio/pending/TICKER-YYYY-MM-DD.json` with price, shares, cost basis, MOS, and confirmed thesis. Nothing is committed to the ledger until you explicitly do so.

---

## Monitor (Stub)

**Trigger phrases:** "monitor TICKER"
**Status:** Not yet implemented.

Planned: compare `FINAL-REPORT.json` across runs, surface score/verdict/flag/trigger changes as a cheap delta report. See `prompts/monitor.md` for the spec.

`./run.sh monitor TICKER` prints a stub message pointing to the spec.

---

## Single Umbrella Mode
If the user asks to run just one umbrella (e.g., "run umbrella 3 on AAPL" or "just analyze management for TSLA"), run only that specific agent and write only that section file.

## Re-Assembly Mode
If the user asks to reassemble a report (e.g., "reassemble AAPL report"), run only Steps 3-4 using existing section files. Also write FINAL-REPORT.json and update queue.

## Financial Data Fetch

**Trigger phrases:** "fetch TICKER", "fetch financials", "fetch --all-reports"

`scripts/fetch-financials.py` uses yfinance (Yahoo Finance) to pull verified financial data and write it to `context/{TICKER}/financials.md`. This runs automatically before every `analyze` command.

### What it provides
- Current price, market cap, 52-week range, valuation multiples
- 4-5 years of income statement, balance sheet, cash flow (annual)
- Derived metrics: ROIC, ROE, ROA, margins, FCF conversion, owner earnings
- Debt & safety ratios: debt/EBITDA, interest coverage, current ratio
- Analyst estimates and price history context
- Data gaps & warnings section for transparency

### How to run
```bash
./run.sh fetch AAPL                       # single ticker
./run.sh fetch ADBE MSFT V MA             # multiple tickers
./run.sh fetch --all-reports              # all tickers with existing reports
./run.sh fetch --all-queue deep_research  # all tickers in a queue state
```

Or directly: `python3 scripts/fetch-financials.py [OPTIONS] TICKER [TICKER ...]`

### Freshness
Skips tickers where `context/{TICKER}/financials.md` is less than 24 hours old. Override with `--force`.

### Integration with analyze
`./run.sh analyze TICKER` auto-fetches before running analysis. If the fetch fails (no internet, invalid ticker), analysis proceeds with web search only.

### Dependencies
- `yfinance` (listed in `requirements.txt`)
- No API keys required

---

## Adding Context
Users can place additional supporting documents in `context/{TICKER}/` alongside the auto-fetched `financials.md`:
- 10-K excerpts or notes
- Earnings call transcripts
- Custom financial spreadsheet exports
- Industry research
- Competitor analysis

The more context provided, the better the analysis. Without context, agents rely on the auto-fetched financials and web search.

## Philosophy
This is a Buffett-style analysis framework. Key principles:
- Business reality over market noise
- Not losing money over maximizing gains
- Understanding over complexity
- Patience over activity
- Honesty over conviction

If you don't have high confidence you understand the business, the right move is to do nothing.
