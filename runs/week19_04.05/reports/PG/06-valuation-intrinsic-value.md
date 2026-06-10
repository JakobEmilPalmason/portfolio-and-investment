# Valuation vs Intrinsic Value — PG

**Analyst Role:** Valuation Analyst
**Date:** 2026-05-06
**Data Sources:** `context/PG/financials.md` (yfinance, 2026-05-06), `context/PG/quant-valuation.md` and `quant-valuation.json` (deterministic DCF), web search results from May 2026 covering FY2026 Q1–Q3 guidance, China/SK-II commentary, GLP-1 impact studies, peer multiples (KO, CL, KMB), 10-year UST yield, and PG's 10-year P/E history (Macrotrends, fullratio, Yahoo Finance, Motley Fool, Investor.com transcripts).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At $146.68 the stock trades **$7.80 above the quant base IV of $138.88**, implying ~zero base-case margin of safety and a -68% MOS to the bear case. | 5 |
| 2 | Monte Carlo P(IV > Price) = **30.0%** — the model says there is roughly a 70% probability the stock is overvalued under randomized assumptions. | 5 |
| 3 | The quant bear case assumes -2.0% revenue growth, which is **inconsistent with management's stated FY2026 guidance** of 0–4% organic growth and Q3 FY2026 actual of +3% organic; the bear case is overly punitive. | 4 |
| 4 | Trailing P/E of 21.4x is **~20% below PG's 10-year average P/E of ~26.4x**, the cheapest the stock has been on a multiple basis since 2013–2014. | 4 |
| 5 | EV/EBITDA of 14.5x is below PG's 10-year median of ~18.0x and roughly in line with CL (15.1x), cheaper than KO (22.1x), and slightly more expensive than KMB (12.5x). | 3 |
| 6 | Sensitivity grid shows the **current price ($146.68) sits between the 1% growth / 5.2% WACC cell ($141.56) and the 3% growth / 6.2% WACC cell ($149.23)** — i.e. the market is pricing roughly 2% real organic growth at the modeled WACC. | 4 |

## Detailed Analysis

**Owner earnings baseline.** The quant model reports adjusted owner earnings of $16.0B (FY2025) using net income + D&A − maintenance capex. Maintenance capex is estimated at ~$2.85B (75% of total $3.77B), with $0.93B of growth capex. On 2,329M shares, that's roughly **$6.86 per share of owner earnings today**. FCF margin has averaged ~17% over four years and FCF conversion has averaged 96%. The earnings stream is real, and capital intensity is low for the volume produced.

**Stress-testing the quant scenarios.** The base case ($138.88) assumes 1% Y1 revenue growth fading to 3%, 24.3% operating margin held flat, 21% tax, 6.2% WACC, and a 15x exit EV/EBITDA. I think the **growth assumption is too low**. Management's stated long-term algorithm is 3–5% organic growth, FY2026 guidance is 0–4% organic, and Q3 FY2026 just delivered +3%. PG has compounded organic growth at roughly 4% over the last five years. A 1% Y1 fading to 3% is plausible only if you believe FX, tariffs, and a soft consumer continue to bite — which is the current near-term reality but not the through-cycle norm. Adjusting the base to **2.5% Y1 fading to 3%** with the same WACC and exit multiple lifts the IV roughly to the **$149–$155 range** (interpolating from the sensitivity grid: 3% growth at 6.2% WACC = $149.23). My adjusted base is **~$150**.

The bear case ($87.16) bakes in -2% revenue growth and a 12x exit multiple. Negative organic growth has not occurred at PG since the early 2010s portfolio rationalization, and even then only briefly. A more honest bear — sticky GLP-1 effect on grooming/health/snack-adjacent products, persistent China headwinds, FX of -2%, and operating-margin compression to 22% — would still get you flat to +1% volume growth, suggesting a more realistic bear IV near **$110–$120** (consistent with the -1% growth row of the sensitivity grid: $111–$134 across the WACC range). I'll keep the conservative anchor at **$110** to reflect the genuine downside case but not the model's mechanical extrapolation.

The bull case ($198.84) requires 4% organic growth, 5.8% WACC, and an 18x exit EV/EBITDA. 4% growth is the high end of management's algorithm and matches strong execution years, but an 18x EV/EBITDA exit is in the historical 90th percentile and assumes rates stay benign. I think a more sober bull is **$175–$185**, capturing strong China beauty recovery (SK-II +18%), modest tariff relief, and 3.5% organic growth at a 16x exit.

**Multiples in context.** Trailing P/E 21.4x and forward 20.7x are roughly 20% below PG's 10-year average (~26x) and median (~25x). EV/EBITDA 14.5x is roughly 17% below PG's own 10-year median of ~18x. Versus peers: PG is meaningfully cheaper than KO (24.8x P/E, 22.1x EV/EBITDA), trades at a small discount to CL (26.2x P/E), and trades at a small premium to KMB (20.6x P/E, 12.5x EV/EBITDA). The relative valuation is reasonable — PG is best-in-class on ROIC (19%) and dividend track record (70 consecutive raises), so a small premium to KMB and a discount to KO is defensible.

**What the price implies.** Reverse-engineering: at $146.68, holding WACC at 6.2% and exit multiple at 15x, the market is pricing ~2% real organic growth — almost exactly in line with the cautious end of management's guidance. The market is **not pricing in perfection**, but it is also not pricing in disaster. The Monte Carlo distribution centers at $135.95 with a P75 of $150.21, so today's price sits in the upper-middle of the simulated outcomes. P(IV > Price) of 30% is the quant model's honest read: most randomized assumption combinations produce an IV below today's price.

**Synthesis.** Adjusting for what I believe are realistic growth assumptions, my IV range is **bear $110 / base $150 / bull $180**. Today's $146.68 sits just below my adjusted base but ~33% above my conservative bear. There is no margin of safety on the bear case and only a sliver on the base.

## Signal Summary

- **Bull case:** China beauty recovery sustains (SK-II +18% Q3), tariffs ease, organic growth runs 3–4% on FX tailwind, EPS grows mid-single-digits, multiple re-rates toward 23x → stock to ~$175–$180 over 24–36 months.
- **Bear case:** GLP-1 erodes snack/grooming-adjacent volumes, China stays weak ex-SK-II, dollar strength returns, tariffs persist, organic growth flatlines, multiple compresses to 17x → stock to ~$110–$120.
- **Confidence:** Medium — earnings stream is highly predictable but the spread between adjusted IV and price is small enough that the verdict swings on a 100bps growth assumption.

## Red Flags

- Current price exceeds the quant base IV by ~$8 — no MOS on the conservative case, and only modest MOS even after my upward adjustments.
- Monte Carlo P(IV > Price) of 30% is a quant model warning that price has run ahead of normalized fundamentals.
- Forward P/E (20.7x) is below historical average but the historical average reflects a long period of zero rates; with the 10-year UST at 4.37% the appropriate "fair" multiple may be lower than the 2014–2021 norm.
- Sensitivity grid shows IV range of roughly $100–$180 — a wide band for a Buffett-style "boring compounder," suggesting the WACC and growth assumptions matter more than the model implies.

## Score: 6 / 10

PG is fairly to mildly overvalued today: trading slightly above my adjusted base IV, with thin margin of safety on conservative assumptions and a 70% Monte Carlo probability of being overvalued — solid business, wrong price for a starter position.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 110 |
| IV Base | 150 |
| IV Bull | 180 |
| Currency | USD |
| MOS at Analysis Date | -33.3 |
