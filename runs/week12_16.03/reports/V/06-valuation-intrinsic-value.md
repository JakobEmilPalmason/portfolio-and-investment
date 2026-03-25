# Valuation vs Intrinsic Value — V

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant DCF model (src/quant), Yahoo Finance via yfinance, Wall Street analyst consensus (35 analysts), Macrotrends historical P/E data, Visa Q1 FY2026 earnings call, web search for peer multiples and regulatory context

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At $301.62, Visa trades 7% below the quant base IV of $324 and near the P10 Monte Carlo percentile, suggesting the market is pricing in meaningful headwinds | 5 |
| 2 | Trailing P/E of 28.3x is 16% below the 5-year average of ~34.7x and below the 10-year average of ~33.6x, the cheapest the stock has been outside the 2022 trough | 5 |
| 3 | Monte Carlo P(IV > Price) of 88.6% implies strong probability-weighted upside, even acknowledging the model's mechanical assumptions | 4 |
| 4 | Forward P/E of 20.7x on $14.54 consensus EPS implies the market is discounting regulatory risk (CCCA, DOJ suit) that may not fully materialize for years | 4 |
| 5 | Terminal value comprises 74-83% of enterprise value across scenarios, making the exit multiple assumption the single most impactful lever | 3 |
| 6 | Reverse-engineering the current price implies ~9-10% revenue growth and a ~12x exit multiple — essentially the bear case baked in as the base | 5 |

## Detailed Analysis

### Owner Earnings Anchor

The quant model estimates owner earnings at $20.1B (FY2025 adjusted), with maintenance capex of just $1.2B (80% of total capex). This is a business that converts virtually all its operating income to distributable cash. I find the owner earnings figure reasonable — Visa's asset-light model requires minimal reinvestment to maintain its network. The growth capex allocation of $300M is conservative; Visa's actual technology and innovation spend likely runs higher when including personnel costs capitalized through the income statement, but this does not materially change the picture. Owner earnings have compounded at ~10% annually over four years ($14.9B in FY2022 to $20.1B in FY2025), and I see no reason this trajectory breaks in the medium term.

### Stress-Testing the Quant Model Assumptions

**Bear case (IV: $229).** The quant model assumes 10% revenue growth fading to 3% and a 12x exit multiple at a 9.6% WACC. I view this as genuinely conservative but not punitive enough to capture a worst-case regulatory outcome. If the CCCA passes and interchange fees compress by 10 basis points (as the proposed settlement implies), net revenue growth could dip to 7-8% for several years. However, Visa would likely offset this through volume growth, value-added services (growing 28% YoY), and pricing power in cross-border transactions. A 12x exit multiple would be the lowest sustained valuation Visa has seen since its early public years. I adjust the bear IV slightly downward to $220 to account for a scenario where regulatory headwinds compress both revenue growth and the multiple simultaneously.

**Base case (IV: $324).** The model assumes 13% revenue growth fading to 3% with a 15x exit multiple at 8.6% WACC. Management guided for low-double-digit net revenue growth in FY2026, and the Zacks consensus pegs revenue at $44.4B (+11.1%). The 13% assumption is slightly above consensus and reflects an optimistic take on cross-border and value-added services momentum. I would shade this to 11-12% growth, which brings the base IV closer to $335-350 when I also consider that a 15x exit multiple is reasonable for a business with 80%+ gross margins and 36% ROIC. The WACC of 8.6% is appropriate given Visa's low beta and minimal debt. I set my adjusted base IV at $340.

**Bull case (IV: $432).** The model assumes 16% growth and an 18x exit multiple at 8.1% WACC. This requires Visa to accelerate meaningfully above current trajectory — possible if value-added services and new flows (B2B payments, Visa Direct) inflect faster than expected. An 18x exit multiple is at the upper end of historical range but not unprecedented for this business quality. I keep the bull IV at $430.

### Multiples in Context

Visa's trailing P/E of 28.3x compares to its 5-year average of ~34.7x and 10-year average of ~33.6x. The September 2022 trough was 25.3x — so we are only 12% above the worst valuation of the last decade. Mastercard currently trades at ~30-31x earnings, a 7-10% premium to Visa, versus a historical average premium of ~17%. This convergence suggests either Visa is relatively cheap or Mastercard has de-rated.

EV/EBITDA of 20.0x is similarly compressed versus Visa's historical average of ~25x. P/FCF of 26.4x, given $21.6B in free cash flow, implies an FCF yield of 3.8% — attractive for a business compounding cash flows at 10%+.

The forward P/E of 20.7x on $14.54 consensus EPS is particularly telling. If Visa grows EPS at 12% for three years (conservative), FY2028 EPS would approach $20. At a 25x forward multiple (below historical average), that implies a share price above $500. The current price is discounting significant multiple compression or earnings disappointment.

### Reverse-Engineering the Current Price

At $301.62, the sensitivity grid places the current price in the neighborhood of the 9% growth / 8.6% WACC cell ($308) or the 11% growth / 9.6% WACC cell ($321). In other words, the market is pricing Visa as if either: (a) revenue growth slows to below management guidance permanently, or (b) the risk-adjusted discount rate should be materially higher than CAPM suggests — likely reflecting regulatory/litigation risk as a quasi-permanent overhang.

Looking at the sensitivity grid, 22 of 25 cells produce an IV above the current price of $301.62. Only the three cells combining 9% growth with WACC of 9.6% or higher fall below. The market is essentially pricing in the worst corner of the assumption space.

### Monte Carlo and Probability-Weighted Assessment

The Monte Carlo simulation's P(IV > Price) of 88.6% at $307.14 is even more favorable at today's $301.62. The P5 is $291, meaning there is only a 5% probability the stock is worth less than $291 — just 3.5% below the current price. The mean IV of $364 implies 21% upside. The distribution is right-skewed, with the P75 at $396 and P95 at $447.

I consider the Monte Carlo input distributions reasonable. Revenue growth distributions centered on 13% with moderate dispersion capture the range of plausible outcomes. The main risk the model underweights is a regime change in interchange economics from regulation — a fat-tailed event that would shift the entire distribution leftward. Even so, the probability-weighted case is strongly favorable.

## Signal Summary
- **Bull case:** Visa is trading at a decade-low multiple while the business compounds owner earnings at 10%+, with value-added services and new payment flows providing upside optionality to $430+.
- **Bear case:** CCCA passage plus DOJ debit antitrust resolution could structurally compress interchange economics, pushing fair value toward $220.
- **Confidence:** High — Visa's financial transparency, predictable cash flows, and 15+ years of public market history make valuation anchoring reliable; the key uncertainty is binary regulatory risk, not business fundamentals.

## Red Flags
- Terminal value is 74-83% of enterprise value across all scenarios, meaning the exit multiple assumption drives the majority of the valuation — small changes in terminal assumptions swing IV by $30-50 per share
- The CCCA and DOJ debit suit represent genuine structural threats that the DCF model cannot adequately capture through standard growth/WACC sensitivity
- Client incentives grew faster than revenue in recent quarters, potentially signaling competitive pressure on net yields

## Score: 7 / 10
Visa is modestly undervalued at $301.62, trading 7% below a conservatively adjusted base IV of $340, with 88.6% Monte Carlo probability of undervaluation and multiples near decade lows — but the bear case IV of $220 offers no price margin of safety, and binary regulatory risk prevents a higher conviction score.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 220 |
| IV Base | 340 |
| IV Bull | 430 |
| Currency | USD |
| MOS at Analysis Date | -37.1 |
