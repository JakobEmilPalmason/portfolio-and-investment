# Valuation vs Intrinsic Value — CPRT

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** context/CPRT/financials.md, context/CPRT/quant-valuation.md, context/CPRT/quant-valuation.json, Yahoo Finance, Seeking Alpha, StockAnalysis.com, Motley Fool, Simply Wall St, Copart 10-Q (Jan 2026)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At $32.87, CPRT trades at ~21x trailing earnings vs its 5-year average of ~35x — a 40% multiple compression suggesting the market is pricing in meaningful deterioration | 5 |
| 2 | Quant model base IV of $34.33 is only 4.4% above current price, but uses conservative 8% Y1 growth and fades to 3% — Copart's 10% revenue CAGR (FY2022-2025) suggests this understates likely growth | 4 |
| 3 | Monte Carlo P(IV > Price) of 76.9% indicates a probability-weighted favorable outcome, with the median simulation at $35.82 (9% above current price) | 4 |
| 4 | Adjusted owner earnings of $1.6B imply a 19.5x OE multiple at current market cap — reasonable for a capital-light duopoly compounder with 16%+ ROIC | 4 |
| 5 | Recent Q2 FY2026 revenue miss ($1.12B vs $1.16B prior year) and margin compression (op margin 34.7% vs 36.6%) introduces near-term earnings uncertainty | 3 |
| 6 | DOJ money laundering investigation creates unquantifiable tail risk that justifies some valuation discount | 3 |

## Detailed Analysis

**Starting from the quant model.** The DCF produces bear/base/bull per-share IVs of $25.19/$34.33/$44.83. I broadly agree with the base case methodology but see room to adjust several assumptions. The base case uses 8% Y1 revenue growth fading to 3% over 5 years, a 10.6% WACC, and a 15x EV/EBITDA exit multiple. The WACC is reasonable — Copart's beta of 1.11 and near-zero leverage make the cost of equity effectively the WACC at 10.6%. However, the exit multiple deserves scrutiny. Copart's 10-year median EV/EBITDA has been ~22x, and even after the current de-rating the stock trades at 13.7x. A 15x exit multiple for a business with this quality profile — duopoly position, 45% gross margins, minimal capital requirements — feels conservative for a base case, though not unreasonable given near-term headwinds.

**Stress-testing growth assumptions.** The bear case at 5% Y1 growth may be too generous given Q2 FY2026 actually showed a 3.6% revenue decline year-over-year. If the current softness persists for 2-3 quarters, the bear case should use 2-3% Y1 growth, which would push bear IV closer to $22-23. Conversely, the bull case at 11% Y1 growth is plausible but not stretched — Copart has international expansion runway (Germany, Finland, Spain) and growing non-insurance volume (dealer and wholesale segments). I would push the bull case to 12-13% with an 18-20x exit multiple, yielding a bull IV closer to $48-50, given the long-term structural tailwinds of increasing vehicle complexity (higher repair costs = more total losses) and global expansion.

**Multiples in context.** At 20.7x trailing P/E and 13.7x EV/EBITDA, Copart trades at its cheapest multiple in at least 5 years. The 5-year average P/E is ~35x. Peers are limited — the closest comparable is IAA (now part of Ritchie Bros), which was acquired at roughly 20-25x earnings. The current multiple implies the market expects low-single-digit earnings growth, which contradicts Copart's track record of double-digit earnings compounding. The P/FCF of 30.7x looks elevated, but this is distorted by $351M of growth capex (62% of total). On maintenance capex alone, owner earnings are $1.6B, putting the P/OE at roughly 20x — much more reasonable.

**What must be true for today's price to be justified?** Looking at the sensitivity grid, the current price of $32.87 sits near the 6% growth / 10.6% WACC cell ($33.73) and the 8% growth / 11.6% WACC cell ($34.65). This means the market is pricing in either (a) growth slowing to 6% at the current risk level, or (b) base-case growth with an elevated risk premium. Neither assumption is unreasonable given the Q2 miss and DOJ overhang, but both represent a more pessimistic view than Copart's long-term track record supports. I adjust my own estimates: bear $23 (reflecting a scenario where the Q2 weakness extends and DOJ creates real fines), base $36 (8% growth, 10.6% WACC, 16x exit — slightly higher exit than quant model given business quality), and bull $50 (12% growth driven by international expansion, 10% WACC as risk premium normalizes, 18x exit).

**Implied expectations vs reality.** The Monte Carlo distribution is informative — 76.9% probability that IV exceeds the current price, with P5 at $29.49 setting a reasonable floor. I think the input distributions may be slightly narrow on the upside given international optionality, but the central tendency is credible. The market appears to be pricing in a scenario between P10 ($30.78) and P25 ($33.10) of the Monte Carlo distribution — i.e., a below-median outcome. For a business that has compounded revenue at 10% and earnings at 12%+ over the past 4 years with virtually no debt, this feels like the market is pricing in near-term disappointment as permanent.

## Signal Summary

- **Bull case:** Multiple re-rating toward historical average (~30x P/E) as revenue growth resumes and DOJ risk is resolved, yielding 50-60% upside to ~$48-50.
- **Bear case:** Revenue declines persist, DOJ investigation leads to material fines, and the multiple stays compressed — downside to $22-23 (30% below current).
- **Confidence:** Medium — The business quality is high and the valuation is unambiguously cheap relative to history, but the Q2 miss and DOJ investigation create genuine near-term uncertainty that could keep the stock depressed.

## Red Flags

- Q2 FY2026 revenue declined 3.6% YoY — first material decline in years, suggesting possible cyclical headwinds in salvage volumes
- Operating margin compressed from 36.6% to 34.7%, breaking a multi-year trend of stability
- DOJ money laundering investigation with unquantifiable financial exposure
- ROIC trending down from 24.2% (FY2022) to 16.6% (FY2025) — partly driven by growing cash pile sitting on balance sheet, but warrants monitoring
- Growth capex running at $350M+/year with unclear near-term returns

## Score: 7 / 10

Copart is modestly undervalued at $32.87 — trading at a significant discount to its 5-year average multiples with a 77% Monte Carlo probability of being undervalued, but the thin margin versus the quant model's bear case ($25.19) and near-term operational headwinds prevent a higher score.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 23 |
| IV Base | 36 |
| IV Bull | 50 |
| Currency | USD |
| MOS at Analysis Date | -43 |
