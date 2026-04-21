# Valuation vs Intrinsic Value — UNH

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-18
**Data Sources:** `context/UNH/financials.md` (yfinance, auto-fetched 2026-04-18), `context/UNH/quant-valuation.md` and `.json` (deterministic DCF, base IV $556, bear $454, bull $1,028); WebSearch for analyst consensus (marketbeat/public.com: $361 median PT, ~$363 mean from 49 analysts), BofA PT raise to $337 after 4/2026 MA rate finalization (24/7 Wall St); peer multiples (stockanalysis.com, gurufocus, financecharts); historical multiple range (macrotrends, gurufocus: 10-yr P/E median 22, EV/EBITDA median 14); 2026 guidance and MCR outlook (benzinga, stocktwits, phemex); MA demographics (HealthScape, Chartis, McKinsey); CEO transition and DOJ probe context (WSJ via becker's, techtarget, UNH press release 5/13/2025).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | FY2025 operating margin collapsed to 4.2% vs FY22-24 avg of 8.5%, driving the quant model's depressed base case; this is the central valuation question — cyclical or structural? | 5 |
| 2 | Quant model base IV of $556 uses FY2025 margin (4.2%) as baseline but also assumes 15.2% Y1 revenue growth — management is actually guiding revenue to shrink toward $439B in 2026 as they exit unprofitable MA counties | 5 |
| 3 | Management's own 2026 guide: ~88.8% MCR, ~3.6% net margin, adjusted EPS floor of $17.75 — a clear multi-year recovery path, not a permanent impairment | 4 |
| 4 | UNH trades at 24.5x trailing and 16.1x forward P/E; EV/EBITDA 16.5x is slightly above 10-yr median of 14.2, suggesting market is pricing in some normalization but not full return to prior profitability | 4 |
| 5 | Street consensus PT of ~$361 (26 analysts) and BofA $337 post-MA rate finalization cluster tightly — the market sees fair value ~10-15% above today's $325 | 3 |
| 6 | Quant Monte Carlo P(IV > Price) = 100% is misleading because the MC varies growth/WACC but NOT margin — the single largest uncertainty is held constant at the depressed 4.2% | 5 |

## Detailed Analysis

### Starting from the quant model, then adjusting

The deterministic DCF anchors at base IV $556, bear $454, bull $1,028, with a Monte Carlo P(IV > Price) of 100% and a sensitivity grid where every cell (growth 11-19%, WACC 4.3-8.3%) lands above the current $325 price. Taken at face value, UNH is deeply undervalued. But the model has a structural flaw for a business in a margin reset: it uses **trailing FY2025 operating margin of 4.2% as the forward assumption**, while simultaneously projecting Year-1 revenue growth of 15.2%. Reality is the mirror image — management has explicitly guided revenue to *shrink* to ~$439B in 2026 (from $447.6B in FY25) while *expanding* margin via repricing and exiting money-losing Medicare Advantage markets.

The two errors offset in opposite directions, so I'm rebuilding the base case from scratch rather than just trusting the anchor.

### Normalized earnings power — the real debate

This is a margin question, not a growth question. Historical facts:
- FY22-24 operating margin averaged 8.5% (range 8.1-8.8%)
- FY25 operating margin 4.2% (one-off Change Healthcare cyber impact + MA utilization spike + front-loaded repricing pain)
- FY26 guide implies net margin ~3.6%, roughly 5.0-5.5% operating margin
- Management targets recovery to adjusted EPS ~$17.75 "and above" — that's ~6-7% net margin on a shrinking revenue base

Three durable headwinds prevent a full return to 8.5%: (1) CMS V28 risk adjustment model compresses MA coding revenue, (2) DOJ probe may force changes to MA billing practices, (3) MA benefit generosity will be lower going forward, which limits premium growth. Three durable tailwinds support margins above trough: (1) Optum Health/Rx scale (40%+ of earnings, higher margin), (2) MA demographic tailwind (51% penetration heading to 54% by 2030, baby boomer age-in continues), (3) scale advantages in cost negotiation.

My normalized operating margin estimate: **6.5-7.0%** by 2028-29. Not the 8.5% peak, not the 4.2% trough, but structurally 150-200 bps below history.

### My bear/base/bull IV

On normalized 2028-29 earnings:

- **Bear ($300):** Normalized op margin 5.5% (regulatory compression worse than expected, Optum growth decelerates), revenue flat at $445B → operating income $24.5B → net income ~$15B → EPS ~$17 → 17-18x multiple (stressed) → $290-310. Quant bear of $454 is too generous; it assumes a clean 15x exit multiple on growing EBITDA. If the DOJ probe lands a structural remedy, 15x is wrong.

- **Base ($380):** Normalized op margin 6.75%, revenue $450B growing 4% p.a. long term → operating income $30B → net income $21B → EPS ~$24 → 16x forward P/E (in line with forward guide of 16.1x today, slight discount to 10-yr P/E median of 22x reflecting regulatory overhang) → $385. This is well below quant base of $556 because I disagree with the margin/growth combination the model uses.

- **Bull ($520):** Operating margin recovers to 7.5%, MA rate increases stay favorable (2027 came in at +2.48% net, above expectations), DOJ probe resolves without material cost, Optum continues compounding → normalized EPS ~$28, 18-19x multiple → $510-530. This is well below quant bull of $1,028 — the quant bull assumes 18% revenue growth Y1 which is simply not plausible given management is actively shrinking revenue.

### Sensitivity grid — which cells are plausible?

The quant grid (growth 11-19% × WACC 4.3-8.3%) doesn't reflect the actual constraint set. Management is guiding 0 to -2% Y1 revenue growth. If I extend the grid mentally down to 0-5% growth (off the chart), and apply my normalized margin (not 4.2%), the plausible cell cluster lands near $350-450 — roughly in line with the Street consensus at $361. The current $325 price sits just below the plausible center of that range, implying a modest but not deep margin.

### Implied expectations vs reality

At $325 and a 16.1x forward P/E on Street's $20 forward EPS, the market is already pricing in: (1) 2026 is the trough, (2) MCR normalizes to ~86% by 2027-28, (3) no catastrophic DOJ outcome. That's a reasonable base case, not a pessimistic one. The market is not pricing in "disaster" — it's pricing in "slow, messy recovery." For UNH to be a multibagger from here, you need the quant bull case (full 8.5% margin return + 15% revenue growth) which I don't believe.

### Multiples in context

UNH trailing P/E 24.5x looks optically rich but reflects depressed trailing earnings. Forward 16.1x is below 10-yr P/E median of 22 and matches peer Elevance (~16x), richer than Humana (~12x), CVS (~10x), Centene (~9x). The premium to other payers is warranted because of Optum diversification (Optum is ~55% of profit and grows at mid-teens ROIC), but the gap has rightfully narrowed during this reset. EV/EBITDA 16.5x is above 10-yr median of 14.2, reflecting depressed EBITDA.

## Signal Summary

- **Bull case:** MCR normalizes by 2027 to ~86%, Optum compounds at 10%+, DOJ probe resolves with modest fines, stock re-rates to 18-19x $28 normalized EPS = ~$520.
- **Bear case:** Regulatory overhang persists, structural MA margin compression sticks, DOJ remedies force business model changes, stock derates to ~$290-310 on stressed earnings and multiple.
- **Confidence:** Medium — the direction of recovery is clear but magnitude and timing have a $200+ per-share range. Quant model's 100% P(IV > Price) is unreliable because it doesn't vary the margin assumption.

## Red Flags

- Quant model anchors on depressed FY25 margin without stress-testing — its 100% P(IV > Price) is a false signal of certainty.
- Management credibility dented: 2024 guidance missed materially, guidance withdrawn mid-2025, new/old CEO Hemsley just back. Next few quarters of guidance need to actually hit.
- DOJ probe expanded into Optum Rx physician compensation (Feb 2026 WSJ) — the scope is widening, not narrowing.
- Revenue will likely shrink in 2026 — first time in UNH's history as a public company. Any business model that requires "shrinking to profitability" deserves skepticism about structural demand.

## Score: 7 / 10

Modestly undervalued on normalized earnings power. My base IV of $380 vs price of $325 = ~14% margin. Not a deep-value bargain, but a quality compounder trading at a reasonable price during a credible if uncertain recovery. Score would be 8 if Street consensus and quant model were closer and I had higher confidence in the normalized margin path.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 300 |
| IV Base | 380 |
| IV Bull | 520 |
| Currency | USD |
| MOS at Analysis Date | -8.2 |
