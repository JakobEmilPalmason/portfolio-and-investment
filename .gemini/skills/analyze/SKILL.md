---
name: analyze
description: Run full Buffett-style 8-umbrella analysis on a stock ticker. Use when performing deep research on a specific company identified during the triage phase.
---

# Stage C: Full Analysis

Current week: !`grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2`

Run full analysis on a ticker as described in CLAUDE.md.

**Arguments:** `$ARGUMENTS`
- First word: TICKER (required, e.g., AAPL)
- Second word: mode (optional) — `full` (default), `assemble` (re-assembly from existing sections), or `1`–`9` (single umbrella)

Parse the ticker from the first word. Uppercase it. If no mode given, default to `full`.

## Step 1: Setup

```bash
CURRENT_WEEK=$(grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2)
mkdir -p "runs/$CURRENT_WEEK/reports/$TICKER"
```

## Step 2: Fetch Financials

Run: `python3 scripts/fetch-financials.py --quiet $TICKER`

If it fails, proceed anyway — agents will use web search.

## Step 3: Gather Context

1. Read `prompts/_shared-format.md` — output schema for all agents
2. Read all files in `data/context/$TICKER/` if the directory exists (financials.md + any user-provided docs)

## Step 4: Run Analysis (mode-dependent)

### Full mode (default)

**Batch 1 — 3 agents in parallel:**

- **Business Analyst Agent**: Read prompts `01-circle-of-competence.md`, `02-durable-competitive-advantage.md`, `03-management-capital-allocation.md`. Write sections 01–03 to `runs/$CURRENT_WEEK/reports/$TICKER/`.

- **Financial Analyst Agent**: Read prompts `04-business-economics.md`, `05-balance-sheet-safety.md`. Write sections 04–05.

- **Valuation Analyst Agent**: Read prompts `06-valuation-intrinsic-value.md`, `07-margin-of-safety.md`, `08-temperament-time-horizon.md`. Write sections 06–08.

Each agent gets: shared format, its prompts, ticker, today's date, context files. Each agent uses WebSearch for current data.

**Batch 2 — after all 3 complete:**

- **Checklist Agent**: Read `09-compact-checklist.md`. Read completed sections 01–08. Write section 09.

**Batch 3 — after checklist:**

- **Synthesis Agent**: Read `assembler.md`. Read all sections 01–09. Write `FINAL-REPORT.md` and `FINAL-REPORT.json`. Update `data/queue/queue.json`.

### Assemble mode

Skip Batch 1. Run Batch 2 (checklist from existing 01–08) then Batch 3 (assembler).

### Single umbrella mode (1–9)

Run only the specified umbrella agent. Write only that section file. Do not run assembler.

## Step 5: Present Results

Show the user:
1. The **verdict** (Own / Watch / Pass)
2. The **score dashboard** (table of all 8 scores)
3. The **compact checklist** (8 forced sentences)
4. Path to full report: `runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.md`
