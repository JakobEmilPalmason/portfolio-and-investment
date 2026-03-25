# Valuation vs Intrinsic Value — TMO

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** context/TMO/financials.md, context/TMO/quant-valuation.md, context/TMO/quant-valuation.json, Yahoo Finance, StockAnalysis.com, Seeking Alpha peer comparisons, MacroTrends historical multiples, analyst consensus (24 analysts), Thermo Fisher Q4 2025 earnings transcript, Simply Wall St peer data

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Owner earnings of ~$8.0B are remarkably stable ($7.9-8.2B over 4 years), providing a reliable valuation anchor despite revenue cyclicality | 5 |
| 2 | At $474, TMO trades at 17.6x forward earnings vs a 5-year average forward P/E of ~25x and life sciences peer average of ~30x — a meaningful compression | 5 |
| 3 | The sensitivity grid shows only 10 of 25 cells produce IV above $474; the base case cell ($455) sits below the current price | 4 |
| 4 | Monte Carlo P(IV > Price) of 42.8% signals the stock is roughly fairly valued on a probability-weighted basis — not clearly cheap | 4 |
| 5 | NIH/DOGE funding cuts and the 2026 guidance miss have driven a 26% drawdown from highs, creating a potential gap between sentiment and business fundamentals | 4 |
| 6 | Debt/EBITDA rose to 3.4x following the $9.4B Clario acquisition, compressing equity value in the DCF and widening the bear case discount | 3 |

## Detailed Analysis

**Owner Earnings and the Valuation Anchor.** The quant model's $8.0B owner earnings figure is well-supported by the data. TMO generated net income of $6.7B, added back $2.8B of D&A, and spent $1.5B on capex — yielding $8.0B. This figure has been strikingly stable at $7.9-8.2B over the past four fiscal years, even as revenues dipped from $44.9B (FY2022) through a trough of $42.9B (FY2023-24) and recovered to $44.6B (FY2025). The quant model classifies 100% of capex as maintenance, which I accept as conservative — TMO's capex is relatively modest at 3.4% of revenue, and the growth-through-acquisition model means organic growth capex is genuinely minimal. Looking forward, with management guiding for 4-6% reported revenue growth and operating leverage from PPI programs, owner earnings should reach $8.5-9.0B within 2-3 years under reasonable assumptions, or remain flat at $8.0B if NIH cuts bite harder than expected and Clario integration absorbs resources.

**Scenario Analysis — Anchored on the Quant DCF.** The quant model produces Bear $251, Base $424, Bull $623. I agree with the framework but adjust two of the three scenarios.

*Bear case (quant: $251, my estimate: $275):* The quant model assumes 5.4% Y1 growth fading to 3.0%, a 12x exit EV/EBITDA, and a 9.6% WACC. A 12x exit feels overly harsh for TMO, which has not sustained a sub-14x EV/EBITDA valuation in any multi-quarter period over the past decade. Even during the worst of the post-COVID normalization, TMO traded at roughly 14-15x EV/EBITDA. I would set the bear exit at 13x, which pushes the bear IV to approximately $275. The bear scenario requires sustained organic growth below 3%, persistent government funding cuts, and no recovery in China — possible but not probable.

*Base case (quant: $424, my estimate: $440):* The model assumes 8.4% Y1 growth, fading to 3.0% by year 5, an 18.2% operating margin, and a 15x exit multiple. The growth trajectory is reasonable given management's 4-6% reported growth guidance plus Clario accretion ($0.20-0.25 EPS). However, I believe the base case slightly underweights the biopharma reshoring tailwind — TMO's $2B U.S. manufacturing investment positions it to capture above-trend growth from 2027-2029 as drug manufacturing returns onshore. I nudge the base IV to $440, reflecting marginally higher growth in years 3-5.

*Bull case (quant: $623, my estimate: $620):* The model assumes 11.4% Y1 growth, an 18x exit, and an 8.1% WACC. This captures a scenario where biotech funding fully recovers, China stabilizes, Clario synergies exceed expectations, and rate cuts reduce the discount rate. I accept this estimate as reasonable. It requires several things going right simultaneously but none of them is individually implausible.

**Multiples in Context.** TMO's current trailing P/E of 26.7x sits well below its 5-year average of ~31x. The forward P/E of 17.6x is the cheapest the stock has been on forward earnings in several years — approaching trough multiples last seen in late 2022 and March 2020. EV/EBITDA at 18.6x sits below the 5-year median of ~21.4x. Against peers, TMO trades at a meaningful discount: Danaher commands 45-47x trailing P/E and ~25x EV/EBITDA; Agilent trades at ~31x trailing P/E; the life sciences peer average is ~30x P/E. TMO's 24.8x P/E vs the peer average of 29.7x represents a ~17% discount. The P/FCF of 40.1x looks elevated, but FY2025 FCF of $6.3B is depressed relative to prior years ($7.3B in FY2024) due to higher working capital needs from the Clario integration. Normalized P/FCF using a ~$7B run rate is closer to 25x, which is reasonable for a business of this quality and durability.

**What Must Be True for $474 to Be Justified.** The sensitivity grid provides a precise answer. At the base WACC of 8.6%, you need roughly 10.4% revenue growth to justify $474 — the grid cell at 10.4% / 8.6% produces $475.47, almost exactly the current price. At lower WACCs: 7.6% WACC with 8.4% growth produces $478.90 (essentially fair). In other words, the market is pricing TMO for either (a) above-guidance growth at the current cost of capital, or (b) in-line growth with a modest decline in rates. This is neither heroic nor pessimistic — it is pricing for competent execution with no margin for error.

**Implied Expectations vs Reality.** The Monte Carlo P(IV > Price) of 42.8% says the probability-weighted outcome slightly favors the stock being overvalued at $474. The Monte Carlo mean of $459 sits 3% below current price, and the median of $454 is 4% below. The market is not pricing in perfection (that would be $600+), but it is pricing in smooth execution of the guided playbook. The critical question: are the NIH/DOGE headwinds a transient 1-2 year overhang (making TMO modestly undervalued as the market over-extrapolates near-term pain) or a structural impairment to the academic/government end market (~15-20% of revenue)? CEO Casper expects caution to "probably abate" in H2 2026 — if he is right, the stock is cheap. If the cuts persist or deepen, the base case IV needs to come down another 5-10%.

## Signal Summary
- **Bull case:** TMO trades at multi-year low multiples (17.6x forward P/E, below 5-year averages and well below peers), and if NIH/tariff headwinds prove transient, reversion to even moderate historical multiples drives 30-40% upside.
- **Bear case:** Elevated debt from the Clario acquisition, persistent government funding cuts, and China weakness could keep earnings growth below 5% and compress multiples further, leaving limited upside from current levels.
- **Confidence:** Medium — the business quality is high-conviction, but the near-term earnings trajectory has genuine uncertainty from exogenous factors (government policy, tariffs, China macro).

## Red Flags
- Debt/EBITDA jumped to 3.4x from 2.7x following the Clario deal — highest in at least 4 years
- ROIC of 8.6% barely exceeds the WACC of 8.6%, meaning economic value creation above cost of capital is razor-thin at current invested capital levels
- FCF declined 14% YoY ($7.3B to $6.3B) while net income grew, suggesting cash conversion may be under pressure from acquisition integration costs
- 2026 guidance missed consensus expectations, driven explicitly by NIH and DOGE-related research funding cuts — visibility on this headwind is low
- Terminal value represents 74-84% of enterprise value across scenarios, making the DCF highly sensitive to exit multiple and long-term growth assumptions
- Forward EPS of $26.89 is non-GAAP adjusted; GAAP EPS is significantly lower due to ~$3B annual amortization of acquired intangibles

## Score: 6 / 10
TMO is roughly fairly valued at $474, trading near the center of a plausible intrinsic value distribution ($275-$620). The forward P/E compression to 17.6x is genuinely attractive relative to history and peers, but the quant model's base IV ($424), my adjusted base ($440), and the Monte Carlo mean ($459) all sit at or below the current price. Modest upside requires at least mid-single-digit growth execution and no further multiple compression — a reasonable but not generous setup that does not yet offer a Buffett-style discount.

## Intrinsic Value Summary
| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 275 |
| IV Base | 440 |
| IV Bull | 620 |
| Currency | USD |
| MOS at Analysis Date | -72.4 |
