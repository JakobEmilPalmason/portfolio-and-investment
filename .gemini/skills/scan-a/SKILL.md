---
name: scan-a
description: Run Stage A pipeline — universe assembly (A1) then candidate filter (A2). Use to identify potential investment candidates from a broad universe of stocks.
---

# Stage A: Universe Assembly + Candidate Filter

Current week: !`grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2`

Run the full Stage A pipeline (A1 → A2) as described in CLAUDE.md.

## Step 1: Setup

```bash
CURRENT_WEEK=$(grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2)
mkdir -p "runs/$CURRENT_WEEK/scan"
```

## Step 2: Stage A1 — Universe Assembly

1. Read `prompts/scan-stage-a1.md` for the full execution template
2. Spawn one general-purpose Agent with WebSearch access
3. Agent reads seed files from `seeds/watchlist.json` and tracked tickers from `runs/*/reports/`
4. Agent uses up to 6 web searches for event/signal buckets
5. Agent writes output to `runs/$CURRENT_WEEK/scan/`:
   - `universe.json` — source of truth (150–400 tickers)
   - `universe-meta.json` — metadata + counts + concentration warnings

Wait for A1 to complete before proceeding.

## Step 3: Stage A2 — Candidate Filter

1. Read `prompts/scan-stage-a2.md` for the full execution template
2. Spawn one general-purpose Agent (minimal web search)
3. Agent reads `runs/$CURRENT_WEEK/scan/universe.json` as primary input
4. Agent writes output to `runs/$CURRENT_WEEK/scan/`:
   - `candidates.json` — ranked/filtered (80–150 tickers)
   - `candidates.csv` — pipe-delimited flat export
   - `candidates.md` — human-readable table
   - `scan-meta.json` — run metadata

## Step 4: Present Results

Show the user:
1. Universe size (A1) → candidate count (A2)
2. Top 20 candidates from `candidates.md`
3. Concentration warnings from `scan-meta.json`
4. Remind them to run `/scan-b` next for triage
