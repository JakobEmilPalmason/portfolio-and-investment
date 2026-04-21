# Valuation vs Intrinsic Value — RACE

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-29
**Data Sources:** Quant DCF model (src/quant), Ferrari FY2025 earnings release (Feb 2026), Yahoo Finance, Alpha Spread DCF, GuruFocus GF Value, Morningstar, analyst consensus via MarketBeat, Seeking Alpha, Ferrari investor relations

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant base-case IV of $283 sits 11% below current price of $317; Monte Carlo gives only 20% probability of undervaluation | 5 |
| 2 | At 30.7x trailing P/E, Ferrari trades at a steep luxury premium but has derated 39% from its 2025 peak — now below its 5-year median multiple | 4 |
| 3 | Reverse-engineering $317 requires ~11% revenue CAGR and sustained 39%+ EBITDA margins for 5+ years — achievable but leaves zero margin for error | 5 |
| 4 | Third-party DCF estimates range widely from $150 to $510, reflecting genuine uncertainty about what discount rate and terminal growth rate apply to a scarcity-luxury franchise | 4 |
| 5 | P/FCF of 67x is the most stretched metric — FCF conversion lagged in 2025 due to elevated capex around the EV launch cycle | 3 |
| 6 | Analyst consensus target of $443 implies 40% upside, but sell-side has historically anchored to Ferrari's premium and been slow to cut targets during corrections | 3 |

## Detailed Analysis

**Quant model as anchor.** The deterministic DCF produces a base-case per-share IV of $283, with bear $174 and bull $365. At $317, the stock sits above both the base and bear cases, falling within the bull corridor. The sensitivity grid shows $317 is only justified in the upper-left quadrant — combinations of 10.9%+ growth with sub-7.2% WACC, or 12.9% growth at any WACC below 8.2%. The Monte Carlo distribution (mean $284, median $281, P(IV > Price) = 20.2%) confirms the stock is more likely overvalued than not under the model's assumptions. This is a quantitative starting point, not a final answer — the model may underweight Ferrari's pricing power and brand durability.

**Stress-testing the quant assumptions.** The quant model assumes 8.9% Y1 revenue growth fading to 3.0% by Y5. Ferrari's 2026 guidance of ~€7.5B implies ~5% top-line growth, but the company has consistently beaten guidance (FY2025 revenues came in at €7.15B vs initial guidance of ~€6.9B). More importantly, the model's exit multiples (12-15-18x EV/EBITDA) may be too conservative for a business that has never traded below 15x even in its worst selloffs. If the base-case exit multiple were 18x instead of 15x, the base IV would lift to roughly $330-340, closer to the current price. The WACC of 7.2% seems reasonable given the low beta (0.55), though one could argue Ferrari's equity risk premium should be lower than market given its defensive cash flow profile.

**Where judgment differs from the quant model.** I would nudge the base-case exit multiple from 15x to 17x EV/EBITDA, reflecting Ferrari's demonstrated ability to sustain luxury-tier multiples through cycles. This adjustment lifts the base IV to approximately $310-320, making the stock roughly fairly valued rather than moderately overvalued. However, I would not adjust growth assumptions upward — the 5% guided growth for 2026 is conservative, but the model's 8.9% Y1 already gives credit for upside. The bear case at $174 remains a useful stress test but assumes a severe de-rating that has never occurred in Ferrari's public history.

**Multiples in context.** Trailing P/E of 30.7x compares to Hermes at ~54x, LVMH at ~20x, Porsche at ~15x, and the S&P 500 at ~22x. Ferrari sits between its luxury peers and the broader market, which is defensible given its hybrid identity (luxury brand economics with automotive revenue). The forward P/E of 25.7x reflects expected earnings growth, which makes the valuation less extreme. EV/EBITDA of 24x is rich but has compressed from 35x+ at the 2025 peak. The P/FCF of 67x is the outlier metric — driven by a capex-heavy year (EV development, Maranello factory expansion) that depresses current free cash flow relative to earnings power. Normalized P/FCF is closer to 35-40x.

**Reverse-engineering the current price.** For $317 to represent fair value at a 7.2% WACC, you need to believe: (1) revenue growth of ~10-11% CAGR for the next 5 years (vs guided 5% for 2026 and historical 12% CAGR), (2) EBITDA margins holding at 39%+ (management is guiding exactly this), (3) a terminal exit multiple of 17-18x EV/EBITDA (at the high end of historical range but not unprecedented), and (4) continued share count reduction via buybacks. Items 2-4 are plausible. Item 1 is the stretch — it requires consistent volume growth, mix enrichment, and successful EV model launches to sustain double-digit top-line growth. This is not impossible, but it is the optimistic scenario, not the base case.

**Probability-weighted assessment.** The Monte Carlo P(IV > Price) of 20.2% tells us that under the model's distributional assumptions, Ferrari is overvalued in ~4 out of 5 scenarios. Even with my exit-multiple adjustment, this would only rise to perhaps 30-35%. This is not a screaming buy, but after a 39% drawdown from the peak, it is no longer the extreme overvaluation it was at $519. The stock is in a gray zone — expensive on conventional metrics, but with a business quality that has historically justified paying up.

## Signal Summary

- **Bull case:** Ferrari's 39% drawdown has compressed multiples to the low end of its historical range, and a scarcity-model luxury franchise with 24% ROIC, order books through 2027, and pricing power deserves a premium that the quant DCF underweights.
- **Bear case:** Even after the selloff, the stock trades above the quant base-case IV, P/FCF is 67x, and US tariffs plus EV execution risk could compress multiples further — the margin for error at $317 remains thin.
- **Confidence:** Medium — The wide spread between third-party valuations ($150-$510) and the model's own bear-to-bull range ($174-$365) reflects genuine uncertainty about what discount rate to apply to a franchise with no true comparable.

## Red Flags

- P/FCF of 67x is extreme even for a luxury compounder; capex normalization is assumed but not guaranteed
- US tariff exposure (30%+ of revenue) with no production flexibility — 10% price increases test even ultra-wealthy buyer tolerance
- 2026 revenue guidance of only 5% growth does not support the 10%+ growth rate needed to justify current price
- Monte Carlo shows 80% probability of overvaluation under model assumptions
- EV launch (Ferrari Luce) in 2026 is a brand-defining moment with binary outcome risk

## Score: 4 / 10

After a 39% drawdown, Ferrari is no longer egregiously overvalued, but the quant model, sensitivity analysis, and Monte Carlo all indicate the stock trades above fair value in most scenarios — it remains priced for near-perfect execution with limited margin for error.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 174 |
| IV Base | 283 |
| IV Bull | 365 |
| Currency | USD |
| MOS at Analysis Date | -82.2 |
