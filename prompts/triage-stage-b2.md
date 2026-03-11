# Stage B2: Focused Triage — Execution Template

Stage B2 is the thoughtful half of triage. You are working from the B1 advance list — the obvious no's are already gone. Your job is to assign a real `next_action` to each survivor with enough care to be actionable.

This is still not deep research. No umbrella writeups. No valuation models. But you should have a genuine opinion on each name.

---

## Do Not Use the Stage C Framework

The umbrella prompts (01–09) and `assembler.md` define how deep-dive analysis is conducted in Stage C. **Do not apply their criteria, scoring logic, or evaluation structure here.** B2 uses only the quality/valuation/balance-sheet scores and next_action rules defined in this prompt. No umbrella scoring, no DCF logic, no circle-of-competence or margin-of-safety assessments.

---

## Inputs

1. **B1 survivors** — read `triage/YYYY-MM-DD/b1-advance.json`. This file has been enriched with candidates context and includes: `already_analyzed` (boolean), `source_bucket`, `thesis_tag`, `style_tag`, `short_reason`, `possible_disqualifier`, `priority`, `triage_rec`, `confidence`. Use `already_analyzed` to drive the refresh / monitor / discard logic for previously analyzed names.
2. **Prior reports** — for each candidate where `already_analyzed=true`, read `reports/{TICKER}/FINAL-REPORT.md` before assigning refresh vs. monitor vs. discard
3. **Scan context** — read `scans/YYYY-MM-DD/scan-meta.json` for background on how the candidates were assembled

---

## WebSearch Rule

3–5 names maximum. Use only for borderline cases where current price or a recent development would materially flip your decision. Not a broad sweep. If you're reaching for web search to make a routine call, you already have enough information.

---

## next_action Values

- `deep_dive` — new name, quality_score ≥ 7, understandable business, reasonable valuation setup; run full 8-umbrella pipeline
- `refresh` — already analyzed; thesis has evolved materially, price has moved significantly (>20%), or report is stale (>6 months old)
- `monitor` — high quality but no compelling entry now; OR already analyzed with intact thesis and no material change
- `discard` — speculative/pre-profit without setup; extreme leverage; commodity; already analyzed with Pass verdict and nothing has changed

---

## Deep Dive Target

Assign `deep_dive` based on genuine conviction only. Do not pad to hit a range. Do not prune to appear conservative.

The only question: is this a quality business you'd want to own at something close to its current price, that you haven't freshly analyzed?

## Research Budget

Hard cap: **8 deep_dives maximum per batch.**

If you have identified more than 8 names with genuine deep_dive conviction:
- Assign the top 8 based on: quality_score, novelty (not yet analyzed), and setup quality
- Demote additional names to `monitor` with `reason_for_action` starting with: "Above-budget: [original rationale]. Prioritize in next cycle."
- Do not pad the deep_dive list to hit 8. If only 4 names truly deserve it, assign 4.

The budget exists because 8 deep dives is roughly what one research cycle can absorb. A 41-name "deep dive" list is a monitor list with overconfidence.

---

## Triage Record Schema

One record per candidate. All 13 fields required; `disqualifier` may be null.

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
  "why_interesting": "Azure + Copilot monetization at scale; Office365 installed base irreplaceable; unmatched FCF and balance sheet",
  "confidence": "high",
  "next_action": "deep_dive",
  "reason_for_action": "Best-in-class quality; not yet analyzed; broad selloff offers an entry setup not seen in 18 months"
}
```

---

## Scoring Guidance (0–10, directional not precise)

- `quality_score` — business durability, moat strength, capital allocation, earnings predictability
- `valuation_score` — rough sense of whether current price is reasonable (not a DCF; directional judgment only)
- `balance_sheet_score` — net cash vs. debt, leverage ratios, financial resilience under stress

---

## Triage Logic

**deep_dive:** quality_score ≥ 7 + understandable business + reasonable valuation setup + not freshly analyzed

**refresh:** already_analyzed=true AND at least one of: thesis-changing development since last report, price moved >20% since report, report is stale (>6 months old)

**monitor:** high quality but expensive or no near-term catalyst; OR already_analyzed with intact thesis and no price dislocation

**discard:** speculative/pre-profit without compelling setup; extreme leverage (FCF consumed by debt service is not owner earnings); commodity with no pricing power; already analyzed with Pass verdict and no material positive change

---

## Override Guidance

- `triage_rec=yes` from Stage A does not mean deep_dive — re-rank using your own judgment
- `triage_rec=no` from Stage A does not mean discard — quality businesses may still warrant monitor
- For already_analyzed names: read FINAL-REPORT.md verdict before deciding; a prior Pass is a strong prior for discard unless something material has changed
- When uncertain between deep_dive and monitor, choose monitor

---

## Output Requirements

- One record per name in the B1 advance list — every survivor must appear
- `red_flag`: one tight phrase, the single most important risk
- `reason_for_action`: one sentence justifying next_action
- No essays. No umbrella writeups. No valuation narratives.
- Do not mirror Stage A priority — re-rank independently
- JSON is source of truth

---

## Output Files

Replace `YYYY-MM-DD` with the scan date:

```
triage/YYYY-MM-DD/triage.json      source of truth — one record per B2 candidate
triage/YYYY-MM-DD/triage.md        human-readable report + shortlists
triage/YYYY-MM-DD/deep-dive.csv    deep dive shortlist export (optional)
```

---

## triage.md Structure

1. **Per-ticker compact blocks** — all B2 candidates, one block each
   Format: `TICKER | Business type | Q/V/BS scores | Red flag | next_action | reason_for_action`
2. **Deep dive shortlist** — all deep_dive names with 1-line rationale each
3. **Refresh list** — already-analyzed names worth re-running, with reason
4. **Monitor list** — tiered if useful (waiting on price / waiting on catalyst / already analyzed intact)
5. **Discard list** — with one-line reason per name
6. **B1 holds (not triaged)** — brief note on what was held by B1 and why they weren't advanced
7. **Research budget recommendation** — how many pipeline runs to authorize this cycle
8. **Schema improvement suggestions** — 2–4 fields that would make future triage more reliable
