# Investment Analysis Workbench — Full Repo Snapshot
> Auto-generated for AI review. Contains all config, prompts, and shell scripts.

---

# TABLE OF CONTENTS

1. CLAUDE.md — Master orchestration instructions
2. README.md — Project overview
3. prompts/_shared-format.md — Output schema (all agents)
4. prompts/scan-stage-a1.md — Stage A1: Universe Assembly
5. prompts/scan-stage-a2.md — Stage A2: Candidate Filter
6. prompts/triage-stage-b1.md — Stage B1: Fast Triage
7. prompts/triage-stage-b2.md — Stage B2: Focused Triage
8. prompts/assembler.md — Final Report Assembler
9. prompts/monitor.md — Monitor (stub/spec)
10. prompts/01-circle-of-competence.md
11. prompts/02-durable-competitive-advantage.md
12. prompts/03-management-capital-allocation.md
13. prompts/04-business-economics.md
14. prompts/05-balance-sheet-safety.md
15. prompts/06-valuation-intrinsic-value.md
16. prompts/07-margin-of-safety.md
17. prompts/08-temperament-time-horizon.md
18. prompts/09-compact-checklist.md
19. seeds/watchlist.json — Seed watchlist
20. run.sh — Main command dispatcher
21. run-analysis.sh — Analyze-only script (deprecated, still used internally)
22. validate.sh — Pipeline output validator

---

# 1. CLAUDE.md

```markdown
# Investment Analysis Workbench

This project is a Buffett-style investment analysis system powered by Claude Code agents. Each "umbrella" of analysis is handled by a specialized agent role, all following the same output format.

## How It Works

When a user asks to analyze a stock (e.g., "analyze AAPL" or "run analysis on MSFT"), follow this workflow:

### Step 1: Setup
1. Create directory `reports/{TICKER}/` if it doesn't exist.
2. Read `prompts/_shared-format.md` — this is the output schema all agents must follow.
3. Check if `context/{TICKER}/` exists. If it does, read all files in it — this is user-provided research (10-K notes, earnings transcripts, financials). Pass this context to every agent.

### Step 2: Run Analysis Agents (3 parallel batches)
Spawn 3 Agent subagents in parallel. Each agent gets:
- The shared format from `prompts/_shared-format.md`
- Its specific umbrella prompt(s) from `prompts/`
- The ticker symbol and today's date
- Any user-provided context files
- Instruction to use web search for current financial data

**Business Analyst Agent** (umbrellas 1-3):
- Read prompts: `01-circle-of-competence.md`, `02-durable-competitive-advantage.md`, `03-management-capital-allocation.md`
- Write output to: `reports/{TICKER}/01-circle-of-competence.md`, `reports/{TICKER}/02-durable-competitive-advantage.md`, `reports/{TICKER}/03-management-capital-allocation.md`

**Financial Analyst Agent** (umbrellas 4-5):
- Read prompts: `04-business-economics.md`, `05-balance-sheet-safety.md`
- Write output to: `reports/{TICKER}/04-business-economics.md`, `reports/{TICKER}/05-balance-sheet-safety.md`

**Valuation Analyst Agent** (umbrellas 6-8):
- Read prompts: `06-valuation-intrinsic-value.md`, `07-margin-of-safety.md`, `08-temperament-time-horizon.md`
- Write output to: `reports/{TICKER}/06-valuation-intrinsic-value.md`, `reports/{TICKER}/07-margin-of-safety.md`, `reports/{TICKER}/08-temperament-time-horizon.md`

Each agent should:
- Use **WebSearch** to find current financial data, recent news, and analyst estimates
- Follow the shared format EXACTLY for each section
- Write each section to its own file in `reports/{TICKER}/`
- Be honest about data sources and confidence levels

### Step 3: Compact Checklist
After all 3 agents complete, spawn one more agent:

**Checklist Agent** (umbrella 9):
- Read prompt: `09-compact-checklist.md`
- Read all completed sections from `reports/{TICKER}/` (01-08)
- Write output to: `reports/{TICKER}/09-compact-checklist.md`

### Step 4: Final Report Assembly
Spawn one final agent:

**Synthesis Agent**:
- Read prompt: `assembler.md`
- Read ALL section files from `reports/{TICKER}/` (01-09)
- Write output to: `reports/{TICKER}/FINAL-REPORT.md` AND `reports/{TICKER}/FINAL-REPORT.json`
- After writing both files, update `queue/queue.json`: set `current_state = monitor_only`, `last_analysis_date = today`, `current_verdict` from FINAL-REPORT.json, `thesis_status = intact`, `next_required_action = monitor`

### Step 5: Present Results
After the final report is written, show the user:
1. The **verdict** (Own / Watch / Pass)
2. The **score dashboard** (table of all 8 scores)
3. The **compact checklist** (8 forced sentences)
4. Let them know the full report is at `reports/{TICKER}/FINAL-REPORT.md`

## Pipeline Overview

```
Stage A1 (Universe Assembly)  →  scans/YYYY-MM-DD/   (universe.json + universe-meta.json)
Stage A2 (Candidate Filter)   →  scans/YYYY-MM-DD/   (candidates.json + csv + md + scan-meta.json)
Stage B1 (Fast Triage)        →  triage/YYYY-MM-DD/b1-*
Stage B2 (Focused Triage)     →  triage/YYYY-MM-DD/triage.*
Stage C  (Full Analysis)      →  reports/{TICKER}/
Queue                         →  queue/queue.json
```

---

## Stage A1: Universe Assembly

**Trigger phrases:** "run A1", "run universe assembly", "rebuild universe"
**Also triggered by:** "run scan", "run Stage A", "refresh universe", "rebuild candidate list", "update candidates" — followed by A2

Stage A1 builds a broad raw stock universe. Its job is assembly and deduplication only — no scoring, no thesis construction, no prioritization.

### Purpose
Merge candidates from multiple sources into a single raw universe JSON. Tag each entry with source/category metadata. Produce 150–400 unique names for A2 to filter.

### Inputs
1. **Tracked** — `reports/` directories → `source_bucket: tracked`
2. **Seed** — `seeds/watchlist.json` → `source_bucket: seed`
3. **Built-in curated lists** (embedded in prompt, agent prior knowledge) → sector bucket names
4. **Web searches** — up to 6 queries for event/signal buckets

### Source buckets
| bucket | how to populate |
|--------|----------------|
| `tracked` | existing `reports/` directories |
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
| `scans/YYYY-MM-DD/universe.json` | source of truth — raw array, minimal schema |
| `scans/YYYY-MM-DD/universe-meta.json` | run metadata + counts by bucket/sector/geography + concentration_warnings |

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
1. Most recent `scans/YYYY-MM-DD/universe.json` — primary input
2. Agent's own knowledge of these businesses (no web search unless critical gap)

### Output files
| file | purpose |
|------|---------|
| `scans/YYYY-MM-DD/candidates.json` | source of truth — ranked/filtered candidates |
| `scans/YYYY-MM-DD/candidates.csv` | flat CSV, pipe-delimited source_bucket |
| `scans/YYYY-MM-DD/candidates.md` | human-readable table + summary stats |
| `scans/YYYY-MM-DD/scan-meta.json` | run metadata + ranking rules v2 snapshot |

### How to run
Read `prompts/scan-stage-a2.md` — full execution template. Spawn one general-purpose agent with the scan date.

### Constraints
- No additional web searches (A1 already ran them) unless one critical fact is missing
- No valuation math. No multi-sentence descriptions.
- JSON is source of truth. Markdown is a render only.
- A2 feeds Stage B1 triage — do not skip to full analysis from here.

### Archive convention
Old scan outputs live in `scans/archive/YYYY-MM-DD/`. The active/latest run is always at `scans/YYYY-MM-DD/`.

---

## Stage B1: Fast Triage

**Trigger phrases:** "run B1", "run fast triage"
**Also triggered by:** "run triage", "run Stage B" — as the first step, followed by B2

Stage B1 is a mechanical filter pass over the A2 candidate list. Harsh, fast, no web search. Every name gets one verdict.

### Purpose
Eliminate obvious no's. Reduce the A2 candidate list to a smaller advance set for B2. B1 hold names auto-become `inbox` (queue state) — they never enter B2.

### Inputs
1. Most recent `scans/YYYY-MM-DD/candidates.json` — primary input
2. Agent's prior knowledge only — no web search

### How to run
Read `prompts/triage-stage-b1.md` — full execution template. Spawn one general-purpose agent with the scan date.

### B1 verdict values
- `advance` — quality business, moat demonstrable, worth a real second look in B2
- `hold` — passes quality bar but no reason to act now; auto-becomes `inbox`
- `reject` — eliminated: pre-profit/speculative, extreme leverage, commodity, Pass verdict with no change, or outside circle of competence

### Output files
| file | purpose |
|------|---------|
| `triage/YYYY-MM-DD/b1-results.json` | all records (advance + hold + reject) |
| `triage/YYYY-MM-DD/b1-advance.json` | survivors only — input for B2 |
| `triage/YYYY-MM-DD/b1-summary.md` | compact one-line table + counts |

### Constraints
- No web search
- No scores, no valuation math, no essays
- One `b1_reason` per name (≤ 12 words)
- JSON is source of truth

---

## Stage B2: Focused Triage

**Trigger phrases:** "run B2", "run focused triage"
**Also triggered by:** "run triage", "run Stage B" — as the second step after B1
**Date argument:** "triage latest" or "triage YYYY-MM-DD" — not "triage TICKER"

Stage B2 applies thoughtful triage to the B1 advance set. Still not deep research, but a genuine opinion on each name.

### Purpose
Assign a real `next_action` to each B1 survivor. Produce a clean deep-dive shortlist (≤8 names) and monitor/refresh set.

### Inputs
1. `triage/YYYY-MM-DD/b1-advance.json` — primary input
2. `scans/YYYY-MM-DD/scan-meta.json` — supporting context
3. `reports/{TICKER}/FINAL-REPORT.md` for each already-analyzed ticker

### How to run
Read `prompts/triage-stage-b2.md` — full execution template. Spawn one general-purpose agent with the triage date.

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
| `triage/YYYY-MM-DD/triage.json` | source of truth — one record per B2 candidate |
| `triage/YYYY-MM-DD/triage.md` | human-readable report + shortlists |
| `triage/YYYY-MM-DD/deep-dive.csv` | deep dive shortlist export (optional) |

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

## Adding Context
Users can place supporting documents in `context/{TICKER}/` before running analysis:
- 10-K excerpts or notes
- Earnings call transcripts
- Custom financial spreadsheet exports
- Industry research
- Competitor analysis

The more context provided, the better the analysis. Without context, agents rely on web search and training knowledge.

## Philosophy
This is a Buffett-style analysis framework. Key principles:
- Business reality over market noise
- Not losing money over maximizing gains
- Understanding over complexity
- Patience over activity
- Honesty over conviction

If you don't have high confidence you understand the business, the right move is to do nothing.
```

---

# 2. README.md

```markdown
# Investment Analysis Workbench

A Buffett-style investment analysis system powered by Claude Code agents. Each "umbrella" of analysis is handled by a specialized agent role, producing structured markdown and JSON reports.

## Philosophy

This framework is built around a simple idea: **buy a wonderful business at a sensible price, with high confidence you understand it.** If you don't have that confidence, the right move is to do nothing.

The analysis is organized into 8 umbrellas, each answering a core question:

| # | Umbrella | Core Question |
|---|----------|---------------|
| 1 | Circle of Competence | Can you explain how this business makes money in plain language? |
| 2 | Durable Competitive Advantage | Why will this company still be strong in 10 years? |
| 3 | Management & Capital Allocation | Do they act like owners? |
| 4 | Business Economics | High, stable returns on capital -- not just growth? |
| 5 | Balance Sheet Safety | Can it survive a bad 2-3 years without raising money? |
| 6 | Valuation vs Intrinsic Value | What is it worth based on owner earnings? |
| 7 | Margin of Safety | Is there a gap between price and conservative value? |
| 8 | Temperament & Time Horizon | If it drops 30% but the business is intact, do you panic? |

Plus a **compact checklist** -- 8 forced sentences every investor should be able to recite about any position they own.

## Commands

### Option 1: Inside Claude Code (Primary)

Open this project in Claude Code and say natural phrases:

```
run scan
triage latest
analyze AAPL
```

### Option 2: Shell Script (Batch/CI)

```bash
./run.sh scan
./run.sh triage latest
./run.sh triage 2026-03-11
./run.sh analyze AAPL
./run.sh monitor AAPL   # stub — not yet implemented
```

## Pipeline

```
scan    →  scans/YYYY-MM-DD/universe.json   (A1)
        →  scans/YYYY-MM-DD/candidates.json  (A2)

triage  →  triage/YYYY-MM-DD/b1-advance.json (B1)
        →  triage/YYYY-MM-DD/triage.json      (B2, ≤8 deep_dives)

analyze →  reports/TICKER/FINAL-REPORT.md
        →  reports/TICKER/FINAL-REPORT.json

queue   →  queue/queue.json  (updated by triage + analyze automatically)
```

## Verdicts

- **Own** — Average score >= 7, no individual score below 4, margin of safety >= 6.
- **Watch** — Average score 5-7 or one critical weakness.
- **Pass** — Average score < 5, multiple weak scores, or thin margin of safety.
```

---

# 3. prompts/_shared-format.md

```markdown
# Standardized Output Format

Every analysis section MUST follow this exact structure. No deviations.

Write in plain language, as if explaining to a smart friend who isn't a finance professional. Avoid jargon unless necessary — and if you use it, explain it. Channel the clarity and directness of a Buffett shareholder letter.

---

## Required Output Structure

```
# {Umbrella Name} — {TICKER}

**Analyst Role:** {Your role name}
**Date:** {YYYY-MM-DD}
**Data Sources:** {List exactly what you used: web search results, user-provided files, training knowledge. Be honest about staleness.}

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | {One clear sentence} | {1=minor, 5=critical} |
| 2 | ... | ... |
| 3 | ... | ... |

Minimum 3 findings, maximum 6. Each finding should be a concrete, verifiable statement — not an opinion.

## Detailed Analysis

{3-6 paragraphs. Address every sub-question from your umbrella prompt. Use specific numbers, examples, and evidence. If you don't have data, say so explicitly — never fabricate.}

## Signal Summary

- **Bull case:** {One sentence — the best realistic outcome}
- **Bear case:** {One sentence — the worst realistic outcome}
- **Confidence:** {Low / Medium / High} — {One sentence explaining why}

## Red Flags

- {Bullet list of concerns, or "None identified"}
- {Each flag should be specific and actionable}

## Score: {X} / 10

{One sentence justification. Be honest — most companies should score 5-7. A 9-10 is exceptional. A 1-3 means serious problems.}
```

---

## Scoring Rubric (universal)

| Score | Meaning |
|-------|---------|
| 9-10 | Exceptional. Clear, durable advantage. Would be comfortable concentrating here. |
| 7-8 | Strong. Minor concerns but fundamentally sound. |
| 5-6 | Average. Some positives, some negatives. Needs more conviction to act. |
| 3-4 | Below average. Significant concerns. Would need a very cheap price. |
| 1-2 | Poor. Fundamental problems. Stay away. |

## Important Rules

1. **Never fabricate data.** If you searched and couldn't find a number, say "not found" rather than guessing.
2. **Cite your sources.** When using web search results, reference them.
3. **Be honest about uncertainty.** Low confidence is fine — dishonest confidence is not.
4. **Write for decision-making.** Every sentence should help the reader decide whether to own this business.
5. **Avoid hedge-fund jargon.** No "alpha generation" or "risk-adjusted returns." Plain English.
```

---

# 4. prompts/scan-stage-a1.md

```markdown
# Stage A1: Universe Assembly — Execution Template

This prompt drives Stage A1. Stage A1 is **assembly only** — build a broad raw stock universe from multiple sources, deduplicate, tag metadata. No scoring, no thesis construction, no prioritization. That is Stage A2's job.

---

## Do Not Use the Stage C Framework

The umbrella prompts (01–09) and `assembler.md` define how deep-dive analysis is conducted in Stage C. **Do not apply their criteria, scoring logic, or evaluation structure here.** A1 does not evaluate businesses — it assembles a list. Your only job is inclusion, deduplication, and metadata tagging using the rules in this prompt.

---

## Step 1: Read tracked names

List all directories under `reports/` to get currently tracked tickers. Each becomes a candidate with `source_bucket: ["tracked"]` and `already_analyzed: true`.

---

## Step 2: Read seed list

Read `seeds/watchlist.json`. Each seed entry becomes a candidate with `source_bucket: ["seed"]`. If a seed ticker is also tracked, merge: `source_bucket: ["tracked", "seed"]`.

---

## Step 3: Add built-in curated sector lists

These are your prior knowledge — do NOT web search for these. Add every name below as a candidate with the corresponding source_bucket. If a ticker is already in the universe from Step 1–2, merge its source_bucket (do not create a duplicate entry).

### `large_cap_us_quality` (~30 names)
COST, ADP, CTAS, CPRT, ROL, BR, PAYX, SSNC, MKTX, NFLX, VRSK, CSGP, FDS, ICE, CME, CBOE, NDAQ, MSCI, NKE, SBUX, MCD, YUM, HSY, CHD, EL, TPX, MCK, IQV, ISRG, EW

### `large_cap_europe_quality` (~20 names)
MC.PA (LVMH), RMS.PA (Hermès), SAP.DE (SAP), WKL.AS (Wolters Kluwer), OR.PA (L'Oréal), CFR.SW (Richemont), ADYEN.AS (Adyen), CRH (CRH plc), DSY.PA (Dassault Systèmes), EL.PA (EssilorLuxottica), KER.PA (Kering), STMN.SW (Straumann), LONN.SW (Lonza), NOVO-B.CO (Novo Nordisk), ASML.AS (ASML), DSV.CO (DSV), MAERSK-B.CO (Maersk), ORSTED.CO (Ørsted), RKT.L (Reckitt), ICG.L (InterContinental Hotels)

### `semis_and_infra` (~15 names)
NVDA, TSM, AMAT, LRCX, KLAC, MRVL, AVGO, ARM, QCOM, ADI, TXN, MPWR, ON, ACLS, ONTO

### `healthcare_quality` (~15 names)
LLY, NVO, AZN, ABBV, UNH, IQVIA, BSX, EW, STE, VEEV, DOCS, MCK, IDXX, WST, MTD

### `industrial_compounders` (~15 names)
ITW, EMR, PH, AME, WCN, RSG, GWW, MSC, CSX, NSC, UNP, XPO, EXPD, ODFL, TDG

### `financial_quality` (~15 names)
JPM, CB, AJG, AFL, MKL, RLI, MSCI, NDAQ, ICE, CME, FDS, MKTX, BX, KKR, GS

### `consumer_quality` (~15 names)
COST, NKE, SBUX, MCD, YUM, HSY, CHD, PG, KO, PEP, EL, SHW, POOL, TPX, DXCM

---

## Step 4: Web searches (up to 6 queries)

1. `"notable US earnings beats misses large cap [current month year]"` → `post_earnings`
2. `"quality large cap stocks near 52-week low [current month year]"` → `52wk_low`
3. `"quality large cap stocks near 52-week high momentum [current month year]"` → `52wk_high`
4. `"highest free cash flow yield large cap stocks [current year]"` → `fcf_roic`
5. `"dominant sector leader stocks by market cap [current year]"` → `sector_leader`
6. (optional) `"quality European large cap stocks [current year]"` → `large_cap_europe_quality`

---

## Step 5: Deduplication

One entry per ticker. Merge source_bucket arrays. Anti-domination check: if tracked + seed > 20% of total, ensure all sector buckets were populated.

---

## A1 Candidate Schema

```json
{
  "ticker": "COST",
  "company": "Costco Wholesale Corp.",
  "sector": "Consumer",
  "industry": "Warehouse Clubs",
  "source_bucket": ["large_cap_us_quality", "consumer_quality"],
  "mkt_cap_tier": "mega",
  "geography": "US",
  "already_analyzed": false,
  "as_of_date": "YYYY-MM-DD"
}
```

DO NOT include: thesis_tag, style_tag, short_reason, possible_disqualifier, priority, triage_rec, confidence

---

## Output Files

- `scans/YYYY-MM-DD/universe.json` — Valid JSON array, target 150–400 unique tickers
- `scans/YYYY-MM-DD/universe-meta.json` — run metadata + counts + concentration_warnings

universe-meta.json schema:
```json
{
  "run_date": "YYYY-MM-DD",
  "total_candidates": 0,
  "buckets_used": [],
  "counts_by_bucket": {},
  "counts_by_sector": {},
  "counts_by_geography": { "US": 0, "Europe": 0, "Asia": 0, "Other": 0 },
  "mkt_cap_distribution": { "mega": 0, "large": 0, "mid": 0 },
  "already_analyzed_count": 0,
  "tracked_plus_seed_pct": 0.0,
  "web_queries_run": [],
  "concentration_warnings": [],
  "stage": "A1"
}
```

concentration_warnings fire when: tracked_plus_seed_pct > 20%, any single bucket > 25%, any single sector > 35%.
```

---

# 5. prompts/scan-stage-a2.md

```markdown
# Stage A2: Candidate Filter — Execution Template

Takes the raw A1 universe and applies lightweight filtering, prioritization, and tagging. No additional web search unless one critical fact is missing.

---

## Step 1: Filter out disqualified names

Drop (mark priority=low, triage_rec=no, do NOT remove): pure commodities, highly regulated utilities, deep cyclicals with no durable advantage, extreme leverage/distress, speculative pre-profit small caps.

---

## Step 2: Add judgment fields

### `thesis_tag`
One of: `dominant_ecosystem` / `monopoly_power` / `secular_growth` / `quality_compounder` / `turnaround` / `mean_reversion` / `post_earnings_dislocation` / `52wk_recovery` / `high_fcf_yield` / `sector_leader`

### `style_tag`
One of: `compounder` / `value` / `cyclical` / `recovery` / `speculative` / `income`

### `short_reason` — one tight phrase (<12 words), why interesting NOW
### `possible_disqualifier` — one tight phrase (<12 words), main risk to skip
### `confidence` — `high` / `medium` / `low` (signal quality, not stock quality)

---

## Step 3: Ranking rules (v2)

**priority=high** if: (post_earnings|52wk_low|52wk_high|fcf_roic in source_bucket AND mkt_cap_tier in {mega,large}) OR (already_analyzed=true AND thesis_tag in {dominant_ecosystem,quality_compounder,secular_growth})

**priority=medium** if: any curated sector bucket OR seed|sector_leader (and no high trigger)

**priority=low** otherwise

**triage_rec=yes** if: (already_analyzed=false AND priority=high AND confidence in {high,medium}) OR (already_analyzed=true AND post_earnings|52wk_low|52wk_high in source_bucket)

**triage_rec=maybe** if: priority=high but no fresh event catalyst

**triage_rec=no** if: priority=low OR confidence=low OR filtered out

Sort: high→medium→low, within same: yes→maybe→no

---

## Full Candidate Schema

```json
{
  "ticker": "COST",
  "company": "Costco Wholesale Corp.",
  "sector": "Consumer",
  "industry": "Warehouse Clubs",
  "source_bucket": ["large_cap_us_quality", "consumer_quality"],
  "thesis_tag": "quality_compounder",
  "style_tag": "compounder",
  "short_reason": "Membership model creates captive repeat spend",
  "possible_disqualifier": "Premium valuation; limited international upside near-term",
  "mkt_cap_tier": "mega",
  "geography": "US",
  "already_analyzed": false,
  "priority": "medium",
  "triage_rec": "maybe",
  "confidence": "high",
  "as_of_date": "YYYY-MM-DD"
}
```

---

## Output Files

- `scans/YYYY-MM-DD/candidates.json` — sorted JSON array, target 80–150 tickers
- `scans/YYYY-MM-DD/candidates.csv` — same data, pipe-delimited source_bucket
- `scans/YYYY-MM-DD/candidates.md` — human-readable table + summary stats
- `scans/YYYY-MM-DD/scan-meta.json` — run metadata + ranking rules snapshot

Every entry must have non-empty short_reason and possible_disqualifier.
```

---

# 6. prompts/triage-stage-b1.md

```markdown
# Stage B1: Fast Triage — Execution Template

Mechanical filter pass. Eliminate obvious no's. One question per name: Is this worth a second look?

No web search. Use candidates.json + prior knowledge only.

---

## B1 Verdict Values

- `advance` — quality business, moat demonstrable, worth a real second look in B2
- `hold` — passes basic quality bar but: already monitored with no change, expensive, thin signal; park it (auto-becomes `inbox`, never enters B2)
- `reject` — pre-profit/speculative, extreme leverage, commodity, capital destroyer, prior Pass with no change, or outside circle of competence

---

## Decision Guidance

**Reject fast if:** no durable advantage, pre-profit, debt consuming FCF, commodity, prior Pass unchanged, don't understand the business.

**Hold if:** fine business but no reason to act, thin signal, mid-tier quality only interesting at different price.

**Advance if:** quality business, demonstrable moat you can name, not obviously broken, something material may have changed.

Soft cap: 15–25% of candidates as advance. Hard cap: 50 names maximum.

---

## B1 Record Schema

```json
{
  "ticker": "MSFT",
  "company": "Microsoft Corp.",
  "b1_verdict": "advance",
  "b1_reason": "dominant moat, FCF machine, not yet analyzed"
}
```

b1_reason: ≤ 12 words. Every candidate must appear. Hold names do not appear in b1-advance.json.

---

## Output Files

- `triage/YYYY-MM-DD/b1-results.json` — all records
- `triage/YYYY-MM-DD/b1-advance.json` — advance survivors only (may be empty array [])
- `triage/YYYY-MM-DD/b1-summary.md` — compact table + counts
```

---

# 7. prompts/triage-stage-b2.md

```markdown
# Stage B2: Focused Triage — Execution Template

Thoughtful triage on B1 advance list. Assign a real next_action to each survivor. Not deep research, but genuine opinion.

WebSearch: 3–5 names max, only for borderline cases.

---

## next_action Values

- `deep_dive` — new name, quality_score ≥ 7, understandable, reasonable valuation setup; run full 8-umbrella pipeline
- `refresh` — already analyzed; thesis evolved materially, price moved >20%, or report stale (>6 months)
- `monitor` — high quality but wrong price or no catalyst; OR already analyzed with intact thesis
- `discard` — speculative, extreme leverage, commodity, prior Pass unchanged

Hard cap: **8 deep_dives maximum per batch.** Demote extras to monitor with "Above-budget:" prefix.

---

## Triage Record Schema

```json
{
  "ticker": "MSFT",
  "company": "Microsoft Corp.",
  "business_type": "Enterprise software / cloud platform",
  "sector": "Technology",
  "thesis_tag": "dominant_ecosystem",
  "quality_score": 9,
  "valuation_score": 6,
  "balance_sheet_score": 10,
  "red_flag": "OpenAI cost drag; antitrust exposure in EU and US",
  "disqualifier": null,
  "why_interesting": "Azure + Copilot monetization at scale; Office365 installed base irreplaceable",
  "confidence": "high",
  "next_action": "deep_dive",
  "reason_for_action": "Best-in-class quality; not yet analyzed; broad selloff offers entry setup"
}
```

Scores 0–10, directional not precise:
- quality_score — business durability, moat, capital allocation, predictability
- valuation_score — rough sense of price reasonableness
- balance_sheet_score — leverage, resilience under stress

---

## Queue Update (after B2 completes)

- deep_dive → current_state = deep_research
- monitor → current_state = watchlist
- discard → current_state = rejected
- B1 hold → current_state = inbox
- B1 reject → current_state = rejected

Set last_triage_date for all touched entries.

---

## Output Files

- `triage/YYYY-MM-DD/triage.json` — source of truth
- `triage/YYYY-MM-DD/triage.md` — human-readable (per-ticker blocks, shortlists, research budget recommendation)
- `triage/YYYY-MM-DD/deep-dive.csv` — optional shortlist export
```

---

# 8. prompts/assembler.md

```markdown
# Final Report Assembler

## Your Role
Chief Investment Analyst. Read all 9 section files from `reports/{TICKER}/` and produce a cohesive final report.

---

## Output: FINAL-REPORT.md

```markdown
# Investment Analysis: {TICKER} — {Company Name}

**Date:** {YYYY-MM-DD}
**Verdict:** {Own / Watch / Pass}

> {2-3 sentence executive summary}

---

## Score Dashboard

| # | Umbrella | Score | One-Line Summary |
|---|----------|-------|------------------|
| 1 | Circle of Competence | X/10 | ... |
| 2 | Durable Competitive Advantage | X/10 | ... |
| 3 | Management & Capital Allocation | X/10 | ... |
| 4 | Business Economics | X/10 | ... |
| 5 | Balance Sheet Safety | X/10 | ... |
| 6 | Valuation vs Intrinsic Value | X/10 | ... |
| 7 | Margin of Safety | X/10 | ... |
| 8 | Temperament & Time Horizon | X/10 | ... |
| | **Average** | **X/10** | |

## Compact Checklist
{Copy 8 sentences from section 09 exactly.}

## Key Risks
{Top 3-5 risks, prioritized by likelihood and impact.}

## What Would Make This a Buy / Sell
- **Buy triggers**: {2-3 specific conditions}
- **Sell triggers**: {2-3 specific conditions}

---

## Full Analysis
{Sections 01-08 in full, separated by horizontal rules.}
```

## Verdict Logic
- **Own**: Average >= 7 AND no score below 4 AND margin of safety >= 6
- **Watch**: Average 5-7 OR one critical weakness
- **Pass**: Average < 5 OR multiple scores below 4 OR margin of safety < 4

The verdict is a framework, not a formula. End with: "If you don't have high confidence you understand this business, the right move is to do nothing."

---

## Second Output: FINAL-REPORT.json

```json
{
  "ticker": "",
  "company": "",
  "analysis_date": "YYYY-MM-DD",
  "verdict": "Own|Watch|Pass",
  "average_score": 0.0,
  "umbrella_scores": {
    "circle_of_competence": 0,
    "competitive_advantage": 0,
    "management": 0,
    "business_economics": 0,
    "balance_sheet": 0,
    "valuation": 0,
    "margin_of_safety": 0,
    "temperament": 0
  },
  "key_strengths": [],
  "key_risks": [],
  "red_flags": [],
  "buy_triggers": [],
  "sell_triggers": [],
  "valuation_summary": "",
  "source_summary": "",
  "confidence": "high|medium|low",
  "change_notes": ""
}
```

---

## Third Step: Update queue/queue.json

After writing both files, update the queue entry for this ticker:
- current_state → "monitor_only" (unless already "approved" or "owned" — preserve those)
- last_analysis_date → today
- current_verdict → from FINAL-REPORT.json
- thesis_status → "intact"
- next_required_action → "monitor"

Do NOT modify: owner_notes, tags, priority, source_batch, last_triage_date.
If queue.json doesn't exist, create it as a valid JSON array with just this entry.
```

---

# 9. prompts/monitor.md

```markdown
# Monitor — Change Detection

**NOT YET IMPLEMENTED.**

## Intent
Compare current FINAL-REPORT.json against a previous run. Cheap delta report, not full re-analysis.

## Planned Inputs
1. `reports/{TICKER}/FINAL-REPORT.json` — current
2. `reports/{TICKER}/FINAL-REPORT.json.prev` — previous snapshot
3. Recent news / price data (2–3 web searches)

## Planned Outputs
`monitor/{TICKER}/YYYY-MM-DD.md` with: score changes, new/removed red flags, valuation move, thesis status, trigger check, recommended action.

## Status
Deferred. Command: `./run.sh monitor TICKER` — currently prints stub message.
```

---

# 10. prompts/01-circle-of-competence.md

```markdown
# Umbrella 1: Circle of Competence

## Your Role
Business Clarity Analyst. Determine whether this business is understandable.

## What to Evaluate
1. What does this company sell, and to whom?
2. How does it actually make money? (revenue model)
3. What are the key drivers? (2-4 variables that matter most)
4. How predictable is the revenue? (recurring vs one-off)
5. Who are the customers and how concentrated are they?
6. Can you explain the business to someone in 2 minutes?

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Crystal clear. Could explain to a teenager. |
| 7-8 | Understandable with some study. |
| 5-6 | Moderately complex. Multiple revenue streams. |
| 3-4 | Complex, hard to pin down key drivers. |
| 1-2 | Opaque. Outside the circle. |

## Output
Follow the shared format exactly.
```

---

# 11. prompts/02-durable-competitive-advantage.md

```markdown
# Umbrella 2: Durable Competitive Advantage

## Your Role
Moat Analyst. Determine whether the company has a durable competitive advantage.

## What to Evaluate
1. What type of moat exists (if any)? — Switching costs / Network effects / Cost advantage / Brand/trust / Regulatory moat / Scale economics shared
2. How durable is the moat? (10-year horizon, disruption risk)
3. Evidence in the numbers: sustained margins, pricing power, stable/growing market share
4. Where is the moat weakest?
5. Do advantages reset every product cycle?

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Wide, durable moat. Would take a decade+ to replicate. |
| 7-8 | Clear moat in at least one dimension. |
| 5-6 | Narrow or temporary. Could erode in 3-5 years. |
| 3-4 | Weak. Competes on execution/price. Easy to replicate. |
| 1-2 | No moat. Commodity. Race to the bottom. |

## Output
Follow the shared format exactly.
```

---

# 12. prompts/03-management-capital-allocation.md

```markdown
# Umbrella 3: Management & Capital Allocation

## Your Role
Stewardship Analyst. Evaluate whether management acts like owners.

## What to Evaluate
1. Insider ownership (actual shares, not just options)
2. Capital allocation track record: buybacks timing, dividends, M&A quality, reinvestment ROIC, share count trend
3. Compensation design: per-share metrics vs revenue/EBITDA, SBC as % of revenue
4. Candor and consistency: do they explain mistakes? Is guidance honest?
5. Governance: dual-class shares, related-party transactions, board independence
6. Simple tell: read last 2-3 shareholder letters — do they talk like owners or politicians?

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Owner-operators, outstanding allocation, skin in the game, candid. |
| 7-8 | Good stewards, mostly rational, minor concerns. |
| 5-6 | Average, mixed record, compensation not perfectly aligned. |
| 3-4 | Empire-building, poor M&A, excessive SBC, governance issues. |
| 1-2 | Red flags: self-dealing, value-destroying allocation, chronic overpromising. |

## Output
Follow the shared format exactly.
```

---

# 13. prompts/04-business-economics.md

```markdown
# Umbrella 4: Business Economics

## Your Role
Business Economics Analyst. Evaluate the quality and sustainability of returns on capital.

## What to Evaluate
1. Returns on capital: ROIC and ROE over 5-10 years — high AND stable?
2. Margin structure: gross, operating, net margins — trend direction
3. Cash generation: FCF, FCF conversion (>80% healthy, <50% warning), owner earnings
4. Capital intensity: maintenance capex vs growth capex — asset-light preferred
5. Revenue quality: recurring vs one-time, volume vs price-driven, retention/churn
6. Operating leverage: do profits grow faster than revenue?

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | ROIC 20%+, strong FCF, asset-light, growing margins. |
| 7-8 | ROIC 15%+, solid FCF, manageable capex. |
| 5-6 | ROIC 10-15%, okay but lumpy FCF, moderate capex. |
| 3-4 | Below-average returns, high capex, inconsistent cash. |
| 1-2 | Capital-destroying, negative/very low ROIC, burns cash. |

## Output
Follow the shared format exactly. Include specific numbers wherever possible.
```

---

# 14. prompts/05-balance-sheet-safety.md

```markdown
# Umbrella 5: Balance Sheet Safety

## Your Role
Balance Sheet Safety Analyst. Can this company survive a bad 2-3 years without raising money?

## What to Evaluate
1. Debt levels and structure: total debt/EBITDA (below 2x comfortable, above 4x concerning), net debt, maturity schedule, fixed vs floating
2. Interest coverage: EBIT/interest expense (above 5x comfortable, below 3x warning, below 1.5x distress)
3. Liquidity: cash + credit facilities, current ratio, 12-24 month zero-revenue survival test
4. Refinancing risk: does survival depend on capital markets being open?
5. Off-balance-sheet obligations: leases, pensions, guarantees
6. Stress test: if revenue drops 30% for two years, does it survive without equity issuance?

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Net cash or minimal debt. Fortress balance sheet. |
| 7-8 | Conservative leverage, well-laddered maturities, strong coverage. |
| 5-6 | Moderate leverage, manageable but not conservative. |
| 3-4 | Elevated leverage, tight coverage, refinancing risk. |
| 1-2 | Overleveraged, near-term maturities at risk, survival risk. |

## Output
Follow the shared format exactly. Include specific debt figures and ratios.
```

---

# 15. prompts/06-valuation-intrinsic-value.md

```markdown
# Umbrella 6: Valuation vs Intrinsic Value

## Your Role
Valuation Analyst. Estimate what this business is actually worth based on owner earnings.

## What to Evaluate
1. Owner earnings: net income + D&A - maintenance capex = owner earnings. What today? Range in 3-5 years?
2. Simple scenario analysis (bear/base/bull): estimate owner earnings Year 5, apply multiple, discount back
3. Multiples in context: P/E, EV/EBITDA, P/FCF vs own history, peers, market — what does the multiple imply?
4. What must be true for today's price to be justified? Reverse-engineer the assumptions.
5. Implied expectations vs likely reality: pricing in perfection or disaster?

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Clearly undervalued, 30%+ upside on conservative estimates. |
| 7-8 | Reasonably to modestly undervalued, upside with patience. |
| 5-6 | Fairly valued, no clear edge. |
| 3-4 | Modestly overvalued, needs optimistic assumptions. |
| 1-2 | Significantly overvalued, pricing in perfection. |

## Output
Follow the shared format exactly. Include bear/base/bull scenarios with explicit assumptions.
```

---

# 16. prompts/07-margin-of-safety.md

```markdown
# Umbrella 7: Margin of Safety

## Your Role
Risk-Reward Analyst. Is there an adequate gap between current price and conservative intrinsic value?

## What to Evaluate
1. Price margin of safety: how much cheaper than bear-case valuation? Still make money if wrong by 20%?
2. Business margin of safety: is the business so strong it can absorb errors? (A fragile business at cheap price = value trap)
3. Downside vs upside asymmetry: quantify realistic downside and upside. Target 2-3x ratio.
4. What could go to zero? Scenarios however unlikely.
5. Ways you could be wrong (3-5 key risks): specific, concrete, with likelihood/severity/early warning sign
6. Concentration risks: one product, customer, geography, regulation
7. Tail risks: litigation, regulatory change, fraud, geopolitical, accounting red flags

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Large price discount + strong business. Asymmetric upside. |
| 7-8 | Reasonable margin, some cushion, manageable risks. |
| 5-6 | Thin margin, need most assumptions right. |
| 3-4 | Little to no margin, priced for perfection or fragile. |
| 1-2 | Negative margin — overpriced AND risky. |

## Output
Follow the shared format exactly. Be explicit about risk/reward ratio.
```

---

# 17. prompts/08-temperament-time-horizon.md

```markdown
# Umbrella 8: Temperament & Time Horizon

## Your Role
Portfolio Fit & Discipline Analyst. Does this investment fit a patient, owner-oriented approach?

## What to Evaluate
1. Holding period suitability: 5-10+ years? Or thesis dependent on near-term events?
2. Volatility tolerance: would you buy more at -30% if business is intact? Historical max drawdown?
3. Catalysts (if any): what could change the market's mind? When? Within company control?
4. Position sizing logic: how wrong can you be? Core vs starter? Appropriate portfolio %?
5. Correlation and portfolio overlap: accidentally making the same bet multiple times?
6. Process discipline: entry plan, sell rules, review cadence

## Scoring Rubric
| Score | Criteria |
|-------|----------|
| 9-10 | Perfect fit. High conviction, long runway, manageable volatility. |
| 7-8 | Good fit. Can hold through volatility. Clear plan. |
| 5-6 | Okay fit. Some holding period or volatility concerns. |
| 3-4 | Poor fit. Dependent on short-term catalysts. |
| 1-2 | Wrong approach. This is a trade, not an investment. |

## Output
Follow the shared format exactly.
```

---

# 18. prompts/09-compact-checklist.md

```markdown
# Umbrella 9: Compact Checklist

## Your Role
Final Synthesis Analyst. Produce exactly 8 forced sentences — one per core question. Do NOT use the standard format.

## Output Format

```
# Compact Checklist — {TICKER}

**Date:** {YYYY-MM-DD}

1. **Business**: {What do they sell and why do customers keep buying? — ONE sentence}
2. **Moat**: {What stops competitors from taking the profits? — ONE sentence}
3. **Economics**: {Evidence of strong returns on capital and real cash generation? — ONE sentence}
4. **Management**: {Do they allocate capital well? — ONE sentence}
5. **Debt risk**: {Could they survive a recession/industry downturn? — ONE sentence}
6. **Price**: {What must be true for today's price to make sense? — ONE sentence}
7. **Margin of safety**: {What protects you if you're wrong? — ONE sentence}
8. **Thesis breaker**: {What specific fact would make you sell? — ONE sentence}
```

## Rules
- Each answer is exactly ONE sentence.
- Be specific, not generic.
- If you can't write a clear, confident sentence: "I don't have enough conviction on this point."
- No hedging language.
```

---

# 19. seeds/watchlist.json

```json
{
  "_note": "Manually curated seed list. Edit freely between scan runs. These are source_bucket=seed in Stage A scans.",
  "seeds": [
    { "ticker": "MSFT",   "company": "Microsoft Corp.",           "sector": "Technology",    "industry": "Enterprise Software / Cloud" },
    { "ticker": "GOOG",   "company": "Alphabet Inc.",             "sector": "Technology",    "industry": "Internet / Search / Cloud" },
    { "ticker": "META",   "company": "Meta Platforms Inc.",       "sector": "Technology",    "industry": "Social Media / Digital Ads" },
    { "ticker": "V",      "company": "Visa Inc.",                 "sector": "Financials",    "industry": "Payment Networks" },
    { "ticker": "MA",     "company": "Mastercard Inc.",           "sector": "Financials",    "industry": "Payment Networks" },
    { "ticker": "BRK-B",  "company": "Berkshire Hathaway B",      "sector": "Financials",    "industry": "Diversified Conglomerate" },
    { "ticker": "CSU.TO", "company": "Constellation Software",    "sector": "Technology",    "industry": "Vertical Market Software" },
    { "ticker": "DHR",    "company": "Danaher Corp.",             "sector": "Industrials",   "industry": "Life Sciences Tools" },
    { "ticker": "MCO",    "company": "Moody's Corp.",             "sector": "Financials",    "industry": "Credit Ratings / Analytics" },
    { "ticker": "SPGI",   "company": "S&P Global Inc.",           "sector": "Financials",    "industry": "Credit Ratings / Data" },
    { "ticker": "FICO",   "company": "Fair Isaac Corp.",          "sector": "Technology",    "industry": "Analytics / Credit Scoring" },
    { "ticker": "ROP",    "company": "Roper Technologies",        "sector": "Industrials",   "industry": "Diversified Industrial Software" },
    { "ticker": "IDXX",   "company": "IDEXX Laboratories",        "sector": "Healthcare",    "industry": "Veterinary Diagnostics" },
    { "ticker": "TDG",    "company": "TransDigm Group",           "sector": "Industrials",   "industry": "Aerospace Components" },
    { "ticker": "ODFL",   "company": "Old Dominion Freight Line", "sector": "Industrials",   "industry": "LTL Trucking" },
    { "ticker": "SHW",    "company": "Sherwin-Williams Co.",      "sector": "Consumer",      "industry": "Specialty Coatings" },
    { "ticker": "FAST",   "company": "Fastenal Co.",              "sector": "Industrials",   "industry": "Industrial Distribution" },
    { "ticker": "POOL",   "company": "Pool Corp.",                "sector": "Consumer",      "industry": "Pool Supplies Distribution" },
    { "ticker": "MTD",    "company": "Mettler-Toledo Intl.",      "sector": "Industrials",   "industry": "Precision Instruments" },
    { "ticker": "WST",    "company": "West Pharmaceutical Services", "sector": "Healthcare", "industry": "Drug Delivery Components" }
  ]
}
```

---

# 20. run.sh — Main Command Dispatcher

```bash
#!/usr/bin/env bash
# Usage:
#   ./run.sh scan                    # Universe assembly (A1) then candidate filter (A2)
#   ./run.sh triage [latest|DATE]    # Fast triage (B1) then focused triage (B2), ≤8 deep_dives
#   ./run.sh analyze TICKER          # Full 8-umbrella analysis + final report
#   ./run.sh monitor TICKER          # Change detection (stub — not yet implemented)
#   ./run.sh validate <type> <file>  # Validate a pipeline output file

set -euo pipefail

# Key variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
SCANS_DIR="$SCRIPT_DIR/scans"
TRIAGE_DIR="$SCRIPT_DIR/triage"
TODAY=$(date +%Y-%m-%d)

# cmd_scan: runs A1 (claude --print with scan-stage-a1.md prompt), validates universe.json,
#           then runs A2 (claude --print with scan-stage-a2.md prompt), validates candidates.json
#           Writes pipeline-state.json checkpoints after each stage.

# cmd_triage: resolves scan date, runs B1 (claude --print, no WebSearch), validates b1-results.json
#             and b1-advance.json and b1-coverage, enriches b1-advance with candidates context via jq,
#             then runs B2 (claude --print with WebSearch), validates triage.json.
#             Skips B2 if B1 produced 0 advances.

# cmd_analyze: delegates to run-analysis.sh TICKER

# cmd_monitor: prints stub message

# cmd_validate: delegates to validate.sh

# All claude invocations use: claude --print --allowedTools "..." "prompt"
# A1/A2/B2 use: WebSearch,WebFetch,Read,Write,Glob,Grep
# B1 uses: Read,Write,Glob,Grep (no web search)
```

---

# 21. run-analysis.sh — Analyze-Only Script

```bash
#!/usr/bin/env bash
# DEPRECATED: Use ./run.sh instead. Still used internally by run.sh analyze.
# Usage:
#   ./run-analysis.sh TICKER           # Full analysis (all umbrellas + assembly)
#   ./run-analysis.sh TICKER 3         # Single umbrella
#   ./run-analysis.sh TICKER assemble  # Re-assemble from existing sections

# For each umbrella 1-8: runs claude --print with the umbrella prompt + shared format + context
# For umbrella 9 (checklist): includes all 8 section files as input
# For assembler: includes all 9 section files, produces FINAL-REPORT.md and FINAL-REPORT.json
# Pass/fail checks: every output must be non-empty; FINAL-REPORT.json must be valid JSON with verdict field
# Context: if context/{TICKER}/ exists, all files are appended to every agent prompt
```

---

# 22. validate.sh — Pipeline Output Validator

```bash
#!/usr/bin/env bash
# Usage: ./validate.sh <type> <file> [file2]
# Types: universe  candidates  b1-results  b1-advance  triage  final-report  b1-coverage
# Exit 0 = valid. Exit 1 = invalid.

# universe: JSON array, 10-600 entries, required fields: ticker company sector source_bucket mkt_cap_tier geography already_analyzed as_of_date
#           enums: mkt_cap_tier (mega/large/mid), geography (US/Europe/Asia/Other), sector (10 values)

# candidates: JSON array, 5-400 entries (warns if <50), required fields include thesis_tag style_tag short_reason etc.
#             enums: priority (high/medium/low), triage_rec (yes/maybe/no), confidence (high/medium/low), etc.
#             short_reason must be non-empty

# b1-results: JSON array, 1-600 entries, fields: ticker company b1_verdict b1_reason
#             enum: b1_verdict (advance/hold/reject), advance count soft cap 50

# b1-advance: JSON array, 0-50 entries, all must have b1_verdict=advance

# triage: JSON array, 0-50 entries, fields: ticker company business_type sector thesis_tag quality_score
#         valuation_score balance_sheet_score red_flag why_interesting confidence next_action reason_for_action
#         hard cap: ≤8 deep_dives, scores must be 0-10

# final-report: JSON object with required top-level fields including umbrella_scores (all 8 keys),
#               verdict must be Own/Watch/Pass, average_score 0-10

# b1-coverage: cross-check b1-results.json against candidates.json — no missing, no extra, no duplicate tickers
```

---

# DIRECTORY STRUCTURE

```
/
├── CLAUDE.md                    ← master orchestration instructions (this AI's CLAUDE.md)
├── README.md                    ← project overview
├── run.sh                       ← main dispatcher (scan / triage / analyze / monitor / validate)
├── run-analysis.sh              ← analyze-only, called by run.sh analyze
├── validate.sh                  ← schema validator for all pipeline outputs
├── prompts/
│   ├── _shared-format.md        ← output schema used by all 8 umbrella agents
│   ├── 01-circle-of-competence.md
│   ├── 02-durable-competitive-advantage.md
│   ├── 03-management-capital-allocation.md
│   ├── 04-business-economics.md
│   ├── 05-balance-sheet-safety.md
│   ├── 06-valuation-intrinsic-value.md
│   ├── 07-margin-of-safety.md
│   ├── 08-temperament-time-horizon.md
│   ├── 09-compact-checklist.md
│   ├── assembler.md             ← final report synthesis + FINAL-REPORT.json schema
│   ├── scan-stage-a1.md         ← Stage A1 execution template
│   ├── scan-stage-a2.md         ← Stage A2 execution template
│   ├── triage-stage-b1.md       ← Stage B1 execution template
│   ├── triage-stage-b2.md       ← Stage B2 execution template
│   └── monitor.md               ← monitor spec (not yet implemented)
├── seeds/
│   └── watchlist.json           ← manually curated seed tickers (20 names)
├── context/
│   └── {TICKER}/                ← user-provided research files (optional, per ticker)
├── scans/
│   └── YYYY-MM-DD/              ← Stage A outputs (universe.json, candidates.json, etc.)
├── triage/
│   └── YYYY-MM-DD/              ← Stage B outputs (b1-*.json, triage.json, etc.)
├── reports/
│   └── {TICKER}/                ← Stage C outputs (01-09 sections + FINAL-REPORT.md/.json)
└── queue/
    └── queue.json               ← living state file, updated by triage (B2) and analyze (assembler)
```
