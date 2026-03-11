# Monitor — Change Detection

**NOT YET IMPLEMENTED. Requires structured JSON outputs to exist at scale.**

---

## Intent

The monitor agent compares the current `FINAL-REPORT.json` for a ticker against a previous run and surfaces what changed. It is a delta report, not a full re-analysis.

## Planned Inputs

1. `reports/{TICKER}/FINAL-REPORT.json` — current structured output
2. `reports/{TICKER}/FINAL-REPORT.json.prev` — previous run's snapshot (archived by the system before overwrite)
3. Recent news / price data (web search, 2–3 queries max)

## Planned Outputs

`monitor/{TICKER}/YYYY-MM-DD.md` containing:
- Score changes (delta per umbrella, direction)
- New red flags not present in prior run
- Removed red flags (risk resolved or reclassified)
- Valuation move: price vs. intrinsic value estimate change
- Thesis status: strengthened / weakened / unchanged
- Trigger check: did any buy or sell trigger fire?
- Recommended action: none / re-triage / full refresh / immediate review

## Design Notes

- Only runs when FINAL-REPORT.json exists for the ticker
- Cheap by design: 2–3 web searches, no umbrella writeups, output is one page
- Escalates to `refresh` (full 8-umbrella re-run) only if thesis has materially changed or a sell trigger has fired
- Useful for `owned` and `watchlist` states in the queue

## Status

Deferred. Implement after FINAL-REPORT.json output exists across a meaningful sample of tickers.

Command: `./run.sh monitor TICKER` — currently prints a stub message.
