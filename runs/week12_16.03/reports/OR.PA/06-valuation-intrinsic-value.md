# Valuation vs Intrinsic Value — OR.PA

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant DCF model (bear/base/bull), Monte Carlo simulation (10,000 runs), sensitivity grid, Yahoo Finance, StockAnalysis, MacroTrends (historical PE), L'Oréal 2025 Annual Results, peer comparisons (Estée Lauder, LVMH, P&G, Unilever)

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Current price €347.70 sits 16% above base IV of €299 and at the P75 of Monte Carlo distribution (€340) — the stock is priced for a bull outcome | 5 |
| 2 | Quant model base case uses 15.0x exit multiple, but L'Oréal's 10-year average PE is ~35x — the exit multiple assumption is arguably conservative for this business | 4 |
| 3 | Only 20.6% Monte Carlo probability that IV exceeds current price — four out of five scenarios say the stock is overvalued today | 5 |
| 4 | To justify €347.70 at base WACC 8.9%, the sensitivity grid requires >7.4% revenue growth — well above L'Oréal's 2025 like-for-like growth of 4.0% | 5 |
| 5 | Forward P/E of ~27x is below the 10-year average of ~35x, but still trades at a 15-35% premium to staples peers (P&G 23x, Unilever 20x, LVMH 25x) | 3 |
| 6 | Analyst consensus target of €403 (+16%) suggests the market expects re-rating, but this requires acceleration to 6%+ organic growth | 3 |

## Detailed Analysis

**Quant Model as Anchor.** The deterministic DCF produces a bear/base/bull range of €193/€299/€421 per share. The base case assumes 5.4% revenue growth, an 8.9% WACC, and a 15.0x exit multiple, yielding an IV of €299 — roughly 14% below today's price. The Monte Carlo simulation, which randomizes growth rates and discount rates across 10,000 paths, places the median IV at €306 and the mean somewhat higher, but critically, only 20.6% of simulations produce an IV above the current price. The P5-P95 range of €237–€394 tells us that even in a reasonably optimistic scenario (P95), the stock barely clears current levels with meaningful margin.

**Stress-Testing the Exit Multiple.** The 15.0x exit multiple in the base case is the most debatable assumption. L'Oréal has traded at 25-40x earnings for most of the past decade, with a 10-year average PE of ~35x. This premium reflects genuine business quality: 74% gross margins, #1 global market share in beauty, a portfolio spanning mass to luxury, and consistent organic growth. A 15x exit multiple implies a severe de-rating to commodity-staples levels. A more reasonable terminal multiple for a business of this quality might be 20-25x, which would shift the base IV meaningfully higher — likely into the €380-€450 range. However, the quant model's conservatism on exit multiples serves as a useful floor anchor, and the high terminal value concentration (83% of EV) means the exit multiple assumption dominates the valuation.

**Sensitivity Grid Analysis.** The most plausible cells in the sensitivity grid cluster around WACC 8.4-9.4% and revenue growth 4.4-6.4%. At the base WACC of 8.9% and a more achievable 4.0% growth rate (matching 2025 like-for-like), the grid likely produces an IV in the €260-€280 range — 20-25% below current price. To justify €347.70 within the model, you need either (a) growth above 7.4% at base WACC, which exceeds even L'Oréal's medium-term guidance, or (b) a WACC below 7.9%, which requires an extremely low equity risk premium. Neither is the base case.

**Peer Valuation Context.** L'Oréal's trailing PE of ~32x sits well above P&G (23x), Unilever (20x), and LVMH (25x), though below the distressed Estée Lauder (64x, reflecting depressed earnings). On a forward PE basis (~27x), L'Oréal commands a 10-35% premium over diversified consumer staples peers. This premium is partly justified — L'Oréal is a pure-play beauty company with higher growth than P&G/Unilever and higher margins than most peers. However, the premium has compressed from peak levels of 40x+ seen in 2021, and the current valuation still assumes L'Oréal can sustain mid-to-high single-digit growth for the foreseeable future.

**Reverse-Engineering the Current Price.** For €347.70 to represent fair value in a DCF framework, one of the following must hold: (1) sustained organic growth of 7%+ for the next decade, which exceeds the global beauty market growth rate of 4-5% and implies continued share gains; (2) an exit multiple of 22-25x, reflecting an assumption that L'Oréal's premium valuation is permanent; or (3) a WACC below 8%, which requires either a lower equity risk premium or a higher debt mix. The most defensible path is a combination of (2) and moderate growth: L'Oréal at 5-6% growth with a 20-22x exit multiple could produce an IV of €340-€380. This is the implicit bet the market is making.

**Verdict on Valuation.** The quant model with its conservative exit multiple says the stock is overvalued. Adjusting for L'Oréal's quality premium on the exit multiple narrows the gap but does not create a clear margin of safety. At €347.70, the stock is fairly to slightly overvalued — not egregiously expensive for a franchise of this quality, but not offering the margin of safety a disciplined value investor demands. The price embeds optimistic assumptions about growth reacceleration and sustained multiple premiums.

## Signal Summary
- **Bull case:** If L'Oréal reaccelerates to 6-7% organic growth (Kering Beauté acquisition, China recovery, e-commerce momentum) and the market sustains a 25-30x earnings multiple, the stock could reach €420-€450 within 2-3 years.
- **Bear case:** If growth stalls at 3-4% (China drag, tariff headwinds, consumer trade-down), multiple compression to 22-25x would push the stock toward €280-€320, a 10-20% decline from here.
- **Confidence:** Medium — The quant model is well-calibrated but the exit multiple assumption is the swing factor; L'Oréal's franchise quality arguably justifies a higher terminal multiple than 15x, but the degree of that adjustment is subjective.

## Red Flags
- Price sits at P75 of Monte Carlo distribution — statistically expensive in four out of five scenarios
- Terminal value is 83% of EV — valuation is heavily dependent on long-run assumptions
- ROIC declining from 18.8% to 15.1% — if this trend continues, the premium multiple is harder to sustain
- Revenue growth decelerated to 4.0% like-for-like in 2025, yet stock is priced for 7%+ growth in the quant model
- Forward PE of 27x still commands a significant premium to staples peers despite slowing growth

## Score: 4 / 10
L'Oréal trades 16% above its base DCF intrinsic value with only a 20.6% probability of undervaluation in Monte Carlo simulation; even adjusting for a higher quality-premium exit multiple, the stock offers no meaningful margin of safety at current prices and is priced for a growth reacceleration that has not yet materialized.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | €193 |
| IV Base | €299 |
| IV Bull | €421 |
| Currency | EUR |
| MOS at Analysis Date | -16.3% |
