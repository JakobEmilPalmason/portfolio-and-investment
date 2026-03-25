---
name: scan-b
description: Run Stage B pipeline — fast triage (B1) then focused triage (B2). Use to filter candidates down to a shortlist for deep-dive analysis.
---

# Stage B: Fast Triage + Focused Triage

Current week: !`grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2`

Run the full Stage B pipeline (B1 → B2) as described in CLAUDE.md.

**Argument:** `$ARGUMENTS` — optional week identifier (defaults to `latest`)

## Step 1: Resolve Scan Week

If `$ARGUMENTS` is empty or "latest", find the most recent `runs/*/scan/candidates.json` that exists. Otherwise use the provided week name.

```bash
CURRENT_WEEK=$(grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2)
mkdir -p "runs/$CURRENT_WEEK/triage"
```

Validate that `runs/{SCAN_WEEK}/scan/candidates.json` exists before proceeding.

## Step 2: Stage B1 — Fast Triage

1. Read `prompts/triage-stage-b1.md` for the full execution template
2. Spawn one general-purpose Agent (NO web search)
3. Agent reads `runs/{SCAN_WEEK}/scan/candidates.json` as primary input
4. Agent writes output to `runs/$CURRENT_WEEK/triage/`:
   - `b1-results.json` — all records (advance + hold + reject)
   - `b1-advance.json` — survivors only
   - `b1-summary.md` — compact table + counts

Wait for B1 to complete before proceeding.

## Step 3: Stage B2 — Focused Triage

1. Read `prompts/triage-stage-b2.md` for the full execution template
2. Spawn one general-purpose Agent (limited web search: 3–5 names max)
3. Agent reads:
   - `runs/$CURRENT_WEEK/triage/b1-advance.json` — primary input
   - `runs/{SCAN_WEEK}/scan/scan-meta.json` — supporting context
   - `runs/*/reports/{TICKER}/FINAL-REPORT.md` for already-analyzed tickers
4. Agent writes output to `runs/$CURRENT_WEEK/triage/`:
   - `triage.json` — source of truth
   - `triage.md` — human-readable report
   - `deep-dive.csv` — shortlist export
5. Hard cap: 8 `deep_dive` verdicts maximum

## Step 4: Update Queue

After B2 completes, update `queue/queue.json` per CLAUDE.md rules:
- B2 `deep_dive` → `current_state = deep_research`
- B2 `monitor` → `current_state = watchlist`
- B2 `discard` → `current_state = rejected`
- B1 `hold` → `current_state = inbox`
- B1 `reject` → `current_state = rejected`

## Step 5: Present Results

Show the user:
1. B1 counts: advance / hold / reject
2. B2 deep-dive shortlist (up to 8 names)
3. B2 monitor and discard counts
4. Remind them to run `/analyze TICKER` for each deep-dive name
