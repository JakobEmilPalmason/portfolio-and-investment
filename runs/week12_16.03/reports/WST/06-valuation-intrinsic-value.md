# Valuation vs Intrinsic Value — WST

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant DCF model (src/quant), context/WST/financials.md, Yahoo Finance, Alpha Spread, Simply Wall St, GuruFocus, MacroTrends (historical P/E), company Q4 2025 earnings release and 2026 guidance

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Monte Carlo gives only 1.4% probability that IV exceeds current price — the stock is priced well above virtually all modeled outcomes | 5 |
| 2 | Current P/E of 35x is below the 5-year average (~43x), suggesting the market has already de-rated WST from its pandemic-era premium | 4 |
| 3 | Reverse-engineering the current price requires sustained ~11% revenue growth at a 15x+ exit multiple — aggressive for a mid-single-digit organic grower | 5 |
| 4 | The quant model's base case IV of $168 sits 29% below the current price; even the bull case ($232) barely approaches today's price | 5 |
| 5 | 2026 guidance of 5-7% organic growth and $7.85-$8.20 adjusted EPS supports the quant model's base assumptions, not the bull case | 4 |
| 6 | Net cash position (~$470M) and 95% FCF conversion provide genuine quality, but quality alone does not justify any price | 3 |

## Detailed Analysis

### Owner Earnings

The quant model estimates FY2025 owner earnings at $379M (simple, deducting full capex) to $494M (adjusted, using 60% maintenance capex). I anchor to the adjusted figure of ~$494M, which aligns closely with reported net income given the capital-light nature of WST's core packaging and delivery systems business. On 72.1M diluted shares, that is roughly $6.85 per share in owner earnings. Looking ahead 3-5 years, assuming 6-7% annual growth in owner earnings (consistent with guided organic revenue growth plus modest margin leverage), owner earnings could reach $7.50-$9.00 per share by FY2028-2030. This is a credible range but not an explosive growth trajectory.

### Scenario Analysis (Anchored on Quant Model)

**Bear case — Quant: $112, My estimate: $130.** The quant bear case assumes 4.5% revenue growth and 11.8% WACC with a 12x exit multiple. I view the 12x exit as slightly punitive for a business with WST's competitive position and switching costs. Even in a downturn, WST's products are essential to drug delivery — vials, stoppers, and cartridge components are not discretionary. I nudge the bear IV upward to ~$130, reflecting a 13x exit multiple on depressed but still positive earnings. The risk that justifies a lower figure would be a structural shift away from injectable drugs or a major manufacturing quality failure.

**Base case — Quant: $168, My estimate: $175.** The quant base assumes 7.5% revenue growth and 10.8% WACC with a 15x exit multiple. This is broadly reasonable. Company guidance for FY2026 implies 5-7% organic growth, with GLP-1 tailwinds (currently ~7% of revenue and growing) providing upside optionality. I modestly increase to $175 to reflect the GLP-1 growth contribution and the SmartDose divestiture sharpening the portfolio. The 15x exit multiple is fair for a quality healthcare components business but not generous.

**Bull case — Quant: $232, My estimate: $260.** The quant bull assumes 10.5% growth and 10.3% WACC with an 18x exit multiple. I see upside if GLP-1 adoption accelerates materially (some forecasts project the GLP-1 market growing 20%+ annually through 2030) and WST captures a disproportionate share of packaging and delivery device demand. An 18x exit multiple is achievable if WST re-rates as a GLP-1 infrastructure play. I stretch to $260 to account for this optionality, but acknowledge this requires multiple things to go right simultaneously.

### Multiples in Context

WST trades at 35x trailing P/E, which is below its 5-year average of ~43x. This de-rating reflects the post-pandemic normalization of vaccine-related demand. However, the forward P/E of 26.8x (on $8.84 consensus EPS) still prices in meaningful growth. Peers in medical instruments and life sciences trade at 24-30x forward earnings on average, putting WST at the high end. EV/EBITDA of 20.5x is similarly premium to the peer group average (~18x). P/FCF of 62.4x is notably elevated — partly reflecting $286M in growth capex that depresses reported FCF. On an owner earnings basis (maintenance capex only), the effective P/OE is ~35x, which is more palatable but still premium.

### What Must Be True for Today's Price

At $237, the market is implicitly pricing in 9-11% annual earnings growth for the next 5+ years and an exit multiple of at least 15-16x. Looking at the sensitivity grid, the current price of $237 does not appear in any cell — the maximum grid value is $223 (at 11.5% growth and 8.8% WACC, the most optimistic combination). This means the market is pricing WST above even the rosiest scenario in the quant model's sensitivity analysis. For the price to be justified, you need to believe either (a) growth will exceed 11.5% annually, (b) the appropriate WACC is below 8.8%, or (c) the exit multiple should be well above 18x. None of these is impossible, but requiring all favorable assumptions simultaneously is a hallmark of priced-for-perfection.

### Implied Expectations vs Reality

The Monte Carlo simulation — 10,000 runs with randomized assumptions — produces a mean IV of $177 and only 1.4% probability of IV exceeding the current price. This is a stark signal: the stock is not just modestly expensive, it is statistically expensive across the vast majority of plausible outcomes. The market is pricing in near-perfection. The GLP-1 narrative provides a credible growth catalyst, but it is already partially reflected in the forward multiple. If GLP-1 growth disappoints or competitors capture share of the packaging and delivery ecosystem, the de-rating risk is significant.

## Signal Summary

- **Bull case:** GLP-1 mega-trend drives WST to sustained double-digit growth, and the market re-rates the stock as essential healthcare infrastructure, justifying a premium multiple.
- **Bear case:** Post-pandemic normalization continues, organic growth reverts to 4-5%, and the P/E compresses toward peer averages (~25x), implying 25-30% downside.
- **Confidence:** Medium — WST is a genuinely high-quality business, but the valuation leaves almost no room for error, and the quant model overwhelmingly suggests overvaluation.

## Red Flags

- Current price exceeds every cell in the sensitivity grid — no reasonable growth/WACC combination produces IV at today's price
- Monte Carlo P(IV > Price) of 1.4% is among the lowest I have seen for a quality compounder
- P/FCF of 62.4x suggests the market is ignoring near-term capital intensity
- GLP-1 exposure (7% of revenue) is real but small; the narrative may be running ahead of the revenue contribution
- SmartDose divestiture removes a growth option, even if it simplifies the business

## Score: 3 / 10

WST is a premium business trading at a price that requires aggressive assumptions across growth, margins, and multiples simultaneously — the quant model, sensitivity grid, and Monte Carlo all converge on the conclusion that the stock is meaningfully overvalued at $237.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 130 |
| IV Base | 175 |
| IV Bull | 260 |
| Currency | USD |
| MOS at Analysis Date | -82.3 |
