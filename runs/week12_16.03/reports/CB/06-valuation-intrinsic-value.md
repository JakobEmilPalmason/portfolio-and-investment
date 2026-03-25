# Valuation vs Intrinsic Value — CB

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Yahoo Finance (yfinance auto-fetch), quant DCF model (src/quant), Chubb Q4 2025 earnings release (Feb 3 2026), StockAnalysis.com historical multiples, Macrotrends CB P/E history, Seeking Alpha peer comparison, Simply Wall St valuation data

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Monte Carlo simulation assigns 89.1% probability that IV exceeds current price of $322.58 | 5 |
| 2 | Base case DCF IV of $393 implies 21.9% upside; 42 of 25 sensitivity grid cells sit above current price | 5 |
| 3 | Current trailing P/E of 12.6x is only modestly above the 5-year average of 12.1x despite materially improved earnings quality (record combined ratio 85.7% full-year, 81.2% Q4) | 4 |
| 4 | Forward P/E of 11.1x on consensus $29.17 EPS implies the market embeds near-zero premium for Chubb's superior underwriting discipline vs peers | 4 |
| 5 | Owner earnings of $10.6B in FY2025 growing from $5.5B in FY2022 — a 24% CAGR — yet the stock prices in low-single-digit earnings growth | 4 |
| 6 | The quant model's bear case ($220) requires WACC of 7.8% and only 5.1% revenue growth, both conservative for a 0.49-beta global insurer in a hard-market environment | 3 |

## Detailed Analysis

**Quant Model Stress Test.** The base case assumes 8.1% Year 1 revenue growth fading to 3.0% by Year 5, a 15% operating margin, and a 6.8% WACC. These inputs are defensible but arguably conservative. Chubb grew net premiums written 6.6% in FY2025 on top of 8-9% in prior years, all while achieving record underwriting profitability. The P&C insurance market remains in a favorable pricing cycle with rate increases broadly sustaining, particularly in commercial casualty and excess lines. Revenue growth of 8% in Year 1 is achievable without heroic assumptions; the fade to 3% by Year 5 builds in meaningful deceleration. The 15% operating margin is a reasonable proxy for Chubb's net margin trajectory (17.2% in FY2025), though it understates the true operating efficiency given insurance accounting conventions. The exit multiple of 15x EV/EBITDA is appropriate for an elite franchise, sitting between the bear case (12x, distressed-cycle trough) and bull case (18x, peak cycle premium). I see no material delta to flag — the base case anchors well.

**WACC Assessment.** The CAPM-derived WACC of 6.8% uses a beta of 0.49, risk-free rate of 4.5%, and 5.5% market risk premium, producing a cost of equity of 7.2%. Chubb's actual beta may be even lower — some sources cite 0.25 over recent periods — which would reduce the cost of equity to approximately 5.9% and WACC to around 5.6%. At 5.8% WACC and 8.1% growth, the sensitivity grid shows IV of $441, a 37% premium to today's price. The debt cost of 4.4% pre-tax is sensible for a AA-rated insurer. The 88/12 equity/debt capital structure is conservative; Chubb's $17.2B total debt against $73.8B equity gives a D/E of 23.4%. Overall, the WACC may be slightly overstated, which means the base IV of $393 is, if anything, a conservative anchor.

**Sensitivity Grid Analysis.** The 5x5 grid spans $317 to $553 in IV. At the current price of $322.58, only the most pessimistic corner (4.1% growth, 8.8% WACC = $317) produces an IV below the current price. All other 24 cells produce IV above $322.58, with the center of mass around $400-$460. The most plausible cells — 6-8% growth with 5.8-6.8% WACC — cluster in the $383-$441 range, suggesting 19-37% upside. This asymmetry is the strongest quantitative signal: you need both below-trend growth and an elevated discount rate simultaneously to justify today's price.

**Monte Carlo Probability.** The 10,000-run Monte Carlo produces a mean IV of $423, median of $417, with P(IV > Price) = 89.1%. The P5 percentile of $295 represents only 8.5% downside from $322.58, while the P95 of $570 represents 77% upside. The standard deviation of $84 implies a coefficient of variation of ~20%, which is moderate for a DCF model. The probability distribution is clearly skewed to the upside.

**Owner Earnings Trajectory.** FY2025 owner earnings of $10.6B (net income $10.3B + D&A $301M, zero capex for insurance) represent $27.17 per share. At a conservative 6% growth rate, owner earnings reach ~$14.2B by FY2030, or $36+ per share. Applying a 12x multiple to that yields $432; at 15x, it yields $540. The current $322.58 price implies the market expects only minimal owner earnings growth — well below Chubb's demonstrated trajectory.

**Peer and Historical Multiples.** Chubb's trailing P/E of 12.6x compares to Travelers at ~17.8x and the multi-line insurance industry average of ~12.0x. Chubb's P/B of 1.7x exceeds the industry average but is justified by its 15% ROE — well above the cost of equity. Historically, Chubb has traded at a 5-year average P/E of 12.1x, so today's multiple is roughly in line with history. However, the quality of earnings has improved meaningfully: the combined ratio has moved from 90%+ in FY2022 to a record 85.7% in FY2025. A business with improving underwriting margins deserves multiple expansion, not stasis.

**Reverse Engineering $322.58.** At the current price, the implied earnings yield is 7.9% (trailing) and 9.0% (forward). For $322.58 to represent fair value, you would need to believe: (a) net premiums growth decelerates to ~4% and stays there, (b) the combined ratio reverts upward by 2-3 points, and (c) the WACC should be 7.5%+. While not impossible — catastrophe losses could spike — this scenario assigns no credit to Chubb's pricing discipline, global diversification, or the structural hard-market tailwind. It is a bear-leaning assumption set.

## Signal Summary
- **Bull case:** Chubb's record underwriting profitability and 89% Monte Carlo probability of being undervalued suggest the market is mispricing a durable franchise at a cyclically low multiple.
- **Bear case:** A major catastrophe year (California wildfires, hurricanes) could spike the combined ratio, compress earnings 20-30%, and validate the current discount.
- **Confidence:** High — The convergence of DCF, Monte Carlo, sensitivity grid, and peer multiples all point to undervaluation in the $70-$100/share range versus base IV.

## Red Flags
- Terminal value constitutes 77-86% of enterprise value across scenarios — typical for insurance but creates sensitivity to exit multiple assumptions
- Bear case IV of $220 is 32% below current price, meaning a sustained hard reversion in underwriting could create meaningful downside
- FY2025 FCF of $12.8B dropped from $16.2B in FY2024 — timing-driven (reserve builds, investment portfolio rebalancing) but worth monitoring

## Score: 8 / 10
Chubb trades at a meaningful discount to base intrinsic value ($393 vs $322.58, ~22% upside) with 89% Monte Carlo probability of being undervalued, but the bear case IV of $220 and catastrophe tail risk prevent a top-decile score.

## Intrinsic Value Summary
| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 220 |
| IV Base | 393 |
| IV Bull | 594 |
| Currency | USD |
| MOS at Analysis Date | 18 |
