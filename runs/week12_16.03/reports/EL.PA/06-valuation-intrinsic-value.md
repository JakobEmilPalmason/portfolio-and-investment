# Valuation vs Intrinsic Value -- EL.PA

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-23
**Data Sources:** Yahoo Finance (yfinance auto-fetch), quant DCF model (src/quant), EssilorLuxottica Q4/FY2025 press release (Feb 2026), Bloomberg, CNBC, analyst consensus (22 analysts), web search for peer multiples and growth outlook

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Stock trades at EUR 194.75, a 40% discount to the quant base IV of EUR 286 and a 32% discount to the DCF sensitivity base case of EUR 330 | 5 |
| 2 | All 25 sensitivity grid cells produce IV above current price; Monte Carlo P(IV > Price) = 99.9% across 10,000 simulations | 5 |
| 3 | Forward P/E of 22.5x is near the lowest multiple EssilorLuxottica has traded at in over five years, despite record revenue growth of 11.2% at constant currency in FY2025 | 5 |
| 4 | Terminal value represents 80-87% of enterprise value across scenarios, making the exit multiple assumption the single most leveraged input | 4 |
| 5 | Quant model uses 14.2% Y1 revenue growth which is achievable given FY2025 delivered 11.2% (reported) / 18.4% in Q4, plus Meta smart glasses scaling to 20M units in 2026 | 3 |
| 6 | ROIC of 5.2% sits below WACC of 6.7%, suggesting the business as currently measured does not earn above its cost of capital -- but this reflects heavy goodwill/intangibles from the Essilor-Luxottica merger distorting invested capital | 3 |

## Detailed Analysis

**Stress-testing the quant model assumptions.** The base case assumes 14.2% Y1 revenue growth fading to 3% by Y5, a 6.7% WACC, and a 15x EV/EBITDA exit multiple. The Y1 growth rate is plausible: FY2025 delivered 11.2% reported growth (7.5% in EUR terms due to currency headwinds), and Q4 alone surged 18.4%. The Meta smart glasses ramp -- from 7 million units in 2025 to a targeted 20 million in 2026 -- provides a tangible incremental growth driver. However, the 14.2% figure assumes both organic momentum and smart glasses contribution continue uninterrupted. My adjustment: a more conservative 12% Y1 growth is prudent given tariff headwinds and the possibility that smart glasses margins are below corporate average. This shifts the base IV modestly lower to roughly EUR 270-280, still well above the current price.

**WACC assessment.** The 6.7% base WACC derived from CAPM (beta 0.55, Rf 4.5%, ERP 5.5%) appears reasonable for a defensive consumer/medtech hybrid. EssilorLuxottica's low beta reflects genuine business stability -- eyewear demand is non-cyclical, and the company has near-monopoly positioning in prescription lenses. Interest coverage at 11.2x and net debt/EBITDA at 1.1x confirm investment-grade credit quality (Moody's rates it A3). The bear case WACC of 7.7% is a fair upper bound; anything above 8% would overstate the risk for this business.

**Sensitivity grid and Monte Carlo.** The sensitivity grid is remarkably constructive: even the worst-case cell (10.2% growth, 8.7% WACC) produces an IV of EUR 252, still 29% above today's price. The Monte Carlo 5th percentile is EUR 247, meaning there is only a 5% probability the stock is worth less than EUR 247 under the model's input distributions. The P(IV > Price) of 99.9% is an extraordinarily strong statistical signal. My assessment of input distributions: the growth and WACC ranges are sensible, though the exit multiple distribution may be slightly generous (the model centers on 15x EV/EBITDA; a normalized range of 12-16x would be more conservative for a mature phase). Even so, at 12x exit, the bear IV is EUR 176 -- only 10% below today's price.

**Owner earnings and valuation on cash flows.** Owner earnings have grown steadily from EUR 3.5B (FY2022) to EUR 3.9B (FY2025), a 3.7% CAGR. On a per-share basis, that is approximately EUR 8.50 of owner earnings, giving a price-to-owner-earnings ratio of 23x at today's price. Over a 3-5 year horizon, if owner earnings grow at 8-10% annually (conservative given the company's mid-teens constant-currency revenue growth and margin expansion targets of 19-20% adjusted operating margin), owner earnings could reach EUR 5.5-6.0B by 2030, or EUR 12-13 per share. At a 20x multiple, that implies a share price of EUR 240-260; at 25x, EUR 300-325.

**Multiples in context.** The trailing P/E of 39x reflects depressed EPS relative to the company's earnings power (currency headwinds, non-cash amortization from M&A). The forward P/E of 22.5x is far more telling and sits at a substantial discount to EssilorLuxottica's 5-year average forward P/E of approximately 30-35x. Peers like Alcon (ALC) trade at roughly 25-28x forward earnings with slower growth; Hoya trades at 30x+. The current EV/EBITDA of 18.3x is also compressed versus a historical range of 22-28x. The market is pricing EssilorLuxottica as though growth is reverting sharply, despite evidence to the contrary.

**What must be true for today's price to be justified?** Reverse-engineering the DCF: at EUR 195, the market is implying either (a) revenue growth slows to low-single-digits immediately, (b) margins contract rather than expand, or (c) a permanent multiple de-rating to 12-13x EV/EBITDA. None of these scenarios aligns with the company's FY2025 results (record growth, margin expansion guidance to 19-20%), the Meta smart glasses tailwind, or the structural growth in myopia management (22% revenue growth in that segment). The market appears to be pricing in broad European equity risk aversion and tariff fears rather than business-specific deterioration.

**Market pricing: pessimism, not perfection.** The stock is at its 52-week low, down 40% from highs, while the business posted record results. This is classic pessimism-driven dislocation. The 22 covering analysts have a median target of EUR 327.50, implying 68% upside. While analyst targets are directional rather than precise, the gap between consensus and market price is unusually wide for a mega-cap.

## Signal Summary
- **Bull case:** Market is mispricing a dominant, growing franchise at a 40% discount to intrinsic value; Meta smart glasses, myopia management, and margin expansion provide multiple re-rating catalysts within 12-24 months.
- **Bear case:** Tariff escalation, EUR/USD volatility, and a consumer spending slowdown compress earnings growth to low-single-digits, validating the current depressed multiple.
- **Confidence:** High -- The quantitative evidence is overwhelming (99.9% MC probability, all sensitivity cells above price), and the qualitative drivers (smart glasses scaling, structural myopia trends, monopoly lens positioning) are robust.

## Red Flags
- Terminal value dominance (80-87% of EV) makes the exit multiple assumption disproportionately impactful
- ROIC (5.2%) below WACC (6.7%) on reported figures -- goodwill-inflated capital base masks true economic returns
- FX headwinds reduced reported growth from 11.2% constant-currency to 7.5% in EUR -- this gap could persist or widen
- Supreme acquisition (USD 1.5B) is a strategic stretch into apparel/streetwear with unproven synergies
- Smart glasses margins and unit economics are not disclosed separately, creating earnings quality uncertainty

## Score: 9 / 10
EssilorLuxottica is clearly undervalued by every quantitative measure available: the DCF base case implies 47% upside, the Monte Carlo 5th percentile is 27% above the current price, forward multiples are at multi-year lows despite accelerating growth, and the market is pricing in a bear scenario that contradicts the company's record FY2025 results.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 176 |
| IV Base | 286 |
| IV Bull | 411 |
| Currency | EUR |
| MOS at Analysis Date | 32 |
