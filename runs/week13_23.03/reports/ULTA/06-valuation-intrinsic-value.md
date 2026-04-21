# Valuation vs Intrinsic Value — ULTA

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-25
**Data Sources:** Quant DCF model (src/quant), context/ULTA/financials.md, context/ULTA/quant-valuation.json, Yahoo Finance, CNBC (Q4 FY2025 earnings), Circana beauty market data, MacroTrends (historical multiples), analyst consensus estimates (24 analysts)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant base IV of $602 implies 15% upside from current $525; Monte Carlo P(IV > Price) = 79.6%, strongly favorable | 5 |
| 2 | Forward P/E of 16.7x is below ULTA's 5-year average P/E of ~23x and below the beauty peer group average of ~31x, suggesting meaningful multiple compression already priced in | 5 |
| 3 | FY2026 guidance of $28.05-$28.55 EPS implies the market is pricing roughly 18.4x forward earnings — conservative for a 50%+ ROIC business with 6-7% top-line growth | 4 |
| 4 | Operating margin declined from 16.2% to 14.0% over two years; if this stabilizes at 14% (as guided), the quant base case is reasonable — but further compression would push IV toward bear territory | 4 |
| 5 | Terminal value represents 82% of enterprise value in the base case, making the exit multiple assumption (15x EV/EBITDA) the single most sensitive input | 3 |
| 6 | Sensitivity grid shows current price of $525 is justified by roughly 1.6% growth at base WACC — well below the company's guided 6-7% revenue growth, implying pessimistic expectations are baked in | 4 |

## Detailed Analysis

**Owner Earnings and Trajectory.** The quant model estimates adjusted owner earnings of $1.2B for FY2025, separating maintenance capex ($267M, or 71% of total capex) from growth capex ($107M). This is a reasonable split for a retailer in store-expansion mode. Over the past four years, owner earnings have been remarkably stable at $1.1-1.2B, even as ULTA invested heavily in new store openings and digital infrastructure. With FY2026 guided capex of $400-450M and revenue growth of 6-7%, I expect owner earnings to remain in the $1.1-1.3B range near-term, growing to $1.4-1.6B by FY2028 if margins stabilize and the store base matures.

**Scenario Analysis — Anchored on Quant Model.** The quant model produces a bear/base/bull range of $354/$602/$890. Starting with the bear case ($354, implying 2.6% growth, 9.8% WACC, 12x exit): I find this overly punitive. Even in a genuine downturn, ULTA's dominant physical footprint (1,500+ stores), loyalty program (46.7M members), and brand portfolio should sustain at least 3-4% growth. I would adjust the bear IV upward to $400, using 3.5% growth and a 13x exit multiple. For the base case ($602, 5.6% growth, 8.8% WACC, 15x exit): this is well-calibrated. Company guidance implies 6-7% FY2026 revenue growth, and the beauty industry is forecast to grow 3-5% through 2027. A 15x exit multiple matches the 10-year median EV/EBITDA of 14.2x. I hold the base at $600. For the bull case ($890, 8.6% growth, 8.3% WACC, 18x exit): this requires sustained high-single-digit growth and premium re-rating, which is achievable if TikTok Shop and international expansion deliver. However, I find 18x exit aggressive for a mature specialty retailer and would trim to $825, using a 16.5x exit.

**Multiples in Context.** ULTA's current trailing P/E of 20.4x sits below both its 5-year average of 23.3x and the beauty peer group average of ~31x. The forward P/E of 16.7x (on consensus $31.49 FY2027 EPS) is even more compelling. EV/EBITDA at 13.4x is slightly below the 10-year median of 14.2x. P/FCF at 26.1x looks elevated, but FCF was depressed in FY2025 by elevated growth capex; normalizing capex closer to maintenance levels would bring P/FCF down to ~20x. In sum, multiples suggest the market is pricing ULTA like a slow-growth mature retailer, not a business earning 50% ROIC with a 46.7M-member loyalty ecosystem.

**Reverse-Engineering Today's Price.** At $525 and roughly $1.8B EBITDA, ULTA trades at 13.4x EV/EBITDA. Looking at the sensitivity grid, the current price sits near the 1.6% growth / 8.8% WACC cell ($520). This means the market is implying barely above GDP growth for a business that just guided 6-7% revenue growth and has grown revenue at an 8% CAGR over the last four years. Either the market believes margin compression will accelerate sharply, or it is simply offering a pessimistic valuation reset after the recent selloff.

**Implied Expectations vs Reality.** The Monte Carlo simulation gives 79.6% probability that IV exceeds the current price — a strongly favorable signal. The median MC outcome ($616) implies 17% upside. The market appears to be pricing in a combination of continued margin erosion and growth deceleration that goes beyond what management has guided. With the stock down 27% from its February high following a slight EPS miss ($8.01 vs $8.03) and guidance that was marginally below consensus, the selloff looks disproportionate to the fundamental deterioration. The prestige beauty market remains healthy (4% growth in 2025, forecast 3-4% through 2027), and ULTA's first-mover position on TikTok Shop provides an incremental growth channel.

**Key Risk to Valuation.** The primary threat is if operating margins, currently at 14%, continue their two-year decline. Every 100bp of margin compression reduces owner earnings by roughly $110M and shaves approximately $40-50 from per-share IV. The 23% spike in SG&A expenses flagged in Q4 FY2025 earnings needs monitoring closely. If margins deteriorate to 12% (as some bears fear), my adjusted bear IV drops to around $350.

## Signal Summary

- **Bull case:** At 16.7x forward earnings with 50%+ ROIC and a dominant loyalty ecosystem, ULTA is priced for failure in a beauty market that continues to grow — the base IV of $600 implies 15% upside with margin stabilization alone.
- **Bear case:** If operating margin compression continues below 12% and growth decelerates to low single digits, the stock is fairly valued to slightly expensive versus a realistic bear IV of $350-400.
- **Confidence:** Medium-High — The quant model, Monte Carlo probabilities, and multiple compression all point to undervaluation, but margin trajectory is the key swing factor and remains uncertain after the Q4 SG&A spike.

## Red Flags

- Operating margin has declined from 16.2% to 14.0% in two years, with a further Q4 contraction to 12.2% quarter-over-quarter
- SG&A expenses spiked 23% in Q4, raising questions about cost discipline vs investment phase
- Terminal value is 82% of the base case enterprise value — heavy dependence on long-term assumptions
- FCF conversion declined from 94% to 80% as capex rose, though this partly reflects growth investment
- FY2026 EPS guidance of $28.05-$28.55 was marginally below consensus of $28.58, suggesting management is not sandbagging

## Score: 7 / 10

ULTA is moderately undervalued relative to its quality characteristics: the quant model, multiple compression, and MC probability all favor the long side, but margin uncertainty after two years of decline prevents a higher conviction score.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 400 |
| IV Base | 600 |
| IV Bull | 825 |
| Currency | USD |
| MOS at Analysis Date | -31.2 |
