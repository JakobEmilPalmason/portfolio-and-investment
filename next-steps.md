# Next Steps

## What's Built

- **A1 (Universe Assembly)** → `scans/YYYY-MM-DD/universe.json` + `universe-meta.json`
- **A2 (Candidate Filter)** → `scans/YYYY-MM-DD/candidates.json` + csv + md + `scan-meta.json`
- **B1 (Fast Triage)** → `triage/YYYY-MM-DD/b1-results.json` + `b1-advance.json` + `b1-summary.md`
- **B2 (Focused Triage)** → `triage/YYYY-MM-DD/triage.json` + `triage.md` (≤8 deep_dives per batch)
- **C (Full Analysis)** → `reports/{TICKER}/01-09` + `FINAL-REPORT.md` + `FINAL-REPORT.json`
- **Queue** → `queue/queue.json` + `queue/queue.md` (living state file updated by triage and analyze)
- **run.sh** → dispatcher for all four commands: `scan`, `triage`, `analyze`, `monitor`

## What's Next (in order)

### 1. Monitor / diff engine
Compare `FINAL-REPORT.json` across runs. Surface score changes, new red flags, thesis drift, trigger fires. Designed as a cheap delta report, not a full re-analysis. See `prompts/monitor.md` for the spec. Implement after JSON outputs exist at meaningful scale.

### 2. Rebalance stub
Portfolio construction agent: takes all `approved` and `owned` queue entries, recommends target weights using a deterministic scoring framework. Deferred until there are enough `Own` verdicts to make it non-trivial.
