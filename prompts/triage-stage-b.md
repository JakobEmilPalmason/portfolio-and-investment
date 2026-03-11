# Stage B: Triage — Execution Template [DEPRECATED]

> **Deprecated.** Stage B has been split into B1 (Fast Triage) and B2 (Focused Triage).
> Use `triage-stage-b1.md` and `triage-stage-b2.md` instead.
> This file is kept for reference only and should not be used to run triage.

This prompt drives a Stage B triage pass. Stage B is lightweight filtering only — no deep analysis, no valuation narratives, no umbrella writeups. Output is compact triage records in JSON and markdown.

---

## Inputs

1. **Candidates** — read `scans/YYYY-MM-DD/candidates.json` directly (do not paste into prompt)
2. **Scan context** — read `scans/YYYY-MM-DD/scan-meta.json` for how the scan was run
3. **Prior reports** — for each candidate where `already_analyzed=true`, read `reports/{TICKER}/FINAL-REPORT.md` to understand the prior verdict and thesis state before deciding refresh vs. monitor vs. discard

---

## WebSearch Rule

3–5 names maximum. Use only for borderline cases or highest-conviction names where current price or recent news could materially flip the triage decision. Not a broad sweep across the list.

---

## Triage Record Schema

One record per candidate, all fields required (`disqualifier` may be null):

```json
{
  "ticker": "MSFT",
  "company": "Microsoft Corp.",
  "business_type": "Enterprise software / cloud platform",
  "sector": "Technology",
  "thesis_tag": "dominant_ecosystem",
  "quality_score": 9,
  "valuation_score": 6,
  "balance_sheet_score": 9,
  "red_flag": "OpenAI cost drag; antitrust exposure",
  "disqualifier": null,
  "why_interesting": "Azure + Copilot monetization at scale; durable moat, high FCF",
  "confidence": "high",
  "next_action": "deep_dive",
  "reason_for_action": "Best-in-class quality, not yet analyzed, reasonable setup"
}
```

---

## next_action Values

- `deep_dive` — new name, high quality, understandable business, reasonable valuation setup; run full 8-umbrella pipeline
- `refresh` — already analyzed; thesis has evolved materially, price has moved significantly, or report is stale
- `monitor` — high quality but no compelling entry now; or already analyzed with intact thesis and no material change
- `discard` — speculative, cyclical without a setup, extreme debt load, or analyzed with Pass verdict and nothing has changed

---

## Scoring Guidance (0–10, directional not precise)

- `quality_score` — business durability, moat strength, capital allocation, earnings predictability
- `valuation_score` — rough sense of whether current price is reasonable (not a DCF; directional judgment only)
- `balance_sheet_score` — net cash vs. debt, leverage ratios, financial resilience under stress

---

## Triage Logic

**deep_dive:** quality_score ≥ 7, understandable business model, reasonable valuation setup, not already freshly analyzed

**refresh:** already_analyzed=true AND at least one of: thesis-changing development since last report, price moved >20% since report, report is stale (>6 months old)

**monitor:** high quality but expensive or no near-term catalyst; OR already_analyzed with intact thesis and no price dislocation

**discard:** speculative/pre-profit without compelling setup; extreme leverage (fails Buffett balance sheet test); commodity business with no pricing power; already analyzed with Pass verdict and no material positive change

---

## Override Guidance

- Stage A uses FCF yield as a signal for some entries — apply Buffett balance sheet filter; FCF consumed by debt service is not owner earnings
- `triage_rec=no` from Stage A does not mean discard — high-quality businesses may still warrant monitor
- `triage_rec=yes` from Stage A does not mean deep_dive — re-rank using your own judgment
- For already_analyzed names: read FINAL-REPORT.md verdict before deciding; a prior Pass is strong prior for discard unless something material has changed
- Conservative on deep_dive: when uncertain between deep_dive and monitor, choose monitor

---

## Output Requirements

- All records must have all 13 fields; `disqualifier` may be null
- `red_flag`: one tight phrase, the single most important risk
- `reason_for_action`: one sentence justifying next_action
- `deep_dive` target: 4–8 names total (be conservative)
- No essays. No umbrella writeups. No valuation narratives.
- Do not mirror Stage A priority — re-rank independently

---

## Output Files

Replace `YYYY-MM-DD` with the scan date:

```
triage/YYYY-MM-DD/triage.json      source of truth — one record per candidate
triage/YYYY-MM-DD/triage.md        human-readable report + shortlists
triage/YYYY-MM-DD/deep-dive.csv    optional: ticker, company, sector, scores, reason_for_action
```

Create the directory if it does not exist.

---

## triage.md Structure

1. **Per-ticker compact blocks** — all candidates, one block each
   Format: `TICKER | Business type | Q/V/BS scores | Red flag | next_action | reason_for_action`
2. **Deep dive shortlist** — 4–8 names with 1-line rationale each
3. **Refresh list** — already-analyzed names worth re-running, with reason
4. **Monitor list** — tiered if useful (waiting on price / waiting on catalyst / already analyzed intact)
5. **Discard list** — with one-line reason per name
6. **Research budget recommendation** — how many pipeline runs to authorize this cycle
7. **Schema improvement suggestions** — 2–4 fields that would make future triage more reliable
