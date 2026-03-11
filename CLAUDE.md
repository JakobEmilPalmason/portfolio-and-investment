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
