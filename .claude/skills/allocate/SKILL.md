---
name: allocate
description: "Run AI portfolio allocator — conviction-weighted Buffett-style portfolio construction"
disable-model-invocation: true
argument-hint: "[CAPITAL] [--label NAME]"
---

# AI Portfolio Allocator

Current week: !`grep -m1 'CURRENT_WEEK=' run.sh | cut -d'"' -f2`

Run the AI portfolio allocator as described in CLAUDE.md.

**Arguments:** `$ARGUMENTS`
- Capital: first numeric argument (default: 100000)
- `--label NAME`: optional run label for identification

## Step 1: Parse Arguments

- Extract capital (first number found, default $100,000)
- Extract label if `--label` flag present
- Generate run ID: `{YYYYMMDDTHHMMSSZ}-{label-slug}` or just timestamp if no label

## Step 2: Build Allocation Input

```bash
python3 scripts/allocation-input.py > portfolio/allocations/{run-id}/allocation-input.json
```

Create the run directory first: `portfolio/allocations/{run-id}/`

If the script fails, build the input manually by reading `queue/queue.json` and all `FINAL-REPORT.json` files for eligible tickers.

## Step 3: Run Allocator Agent

1. Read `prompts/allocator.md` for the full execution template
2. Read `portfolio/allocations/{run-id}/allocation-input.json` as primary input
3. Spawn one general-purpose Agent
4. Agent applies Buffett-style allocation logic: filter → rank → construct → risk overlay
5. Agent writes to `portfolio/allocations/{run-id}/`:
   - `allocation-proposal.json` — machine-readable target portfolio
   - `allocation-proposal.md` — human-readable proposal with rationale per position

## Step 4: Write Run Metadata

Write `portfolio/allocations/{run-id}/run-metadata.json`:
```json
{
  "run_id": "{run-id}",
  "label": "{label or null}",
  "capital": {capital},
  "timestamp": "{ISO timestamp}",
  "output_dir": "portfolio/allocations/{run-id}"
}
```

## Step 5: Present Results

Show the user:
1. Number of positions and total capital deployed vs cash
2. Top positions with weights and rationales
3. Sector exposure summary
4. Path to full proposal: `portfolio/allocations/{run-id}/allocation-proposal.md`
