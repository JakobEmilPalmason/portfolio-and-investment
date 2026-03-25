# Valuation vs Intrinsic Value — GILD

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant DCF model output (bear/base/bull), sensitivity grid (5x5), Monte Carlo (10,000 runs), Yahoo Finance (current multiples), GuruFocus (peer EV/EBITDA), StockAnalysis.com (peer forward PEs), Gilead FY2025 earnings release, analyst consensus targets (MarketBeat, Public.com), Simply Wall St DCF estimate, Fierce Pharma (Biktarvy patent timeline)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | ALL 25 sensitivity grid cells show IV above current price of $137.21, with the floor at $163.0 (WACC 8.2%, growth 3.1%) — a 19% upside even under worst-case assumptions | 5 |
| 2 | Monte Carlo P(IV > Price) = 99.9% across 10,000 simulations, with a mean IV of $215 and P5 of $168 — the probability of overpaying at $137 is statistically negligible | 5 |
| 3 | Forward P/E of 14.3x represents a meaningful discount to large-cap pharma peers: ABBV 15.7x, JNJ 18.1x, MRK 22.6x; only BMY (9.8x) is cheaper, reflecting its deeper patent cliff concerns | 4 |
| 4 | To reverse-engineer $137 as fair value, you need to assume ~2% perpetual revenue decline AND a 12x exit multiple AND WACC above 7.2% — essentially a scenario where the entire HIV franchise erodes with no pipeline offset | 4 |
| 5 | Biktarvy patent exclusivity extended to 2036 eliminates the near-term cliff risk that previously depressed the multiple, supporting a higher terminal value than the model's conservative 15x base case | 4 |
| 6 | Third-party DCF estimates range wildly from $90 (GuruFocus GF Value) to $288 (Simply Wall St), illustrating how sensitive pharma valuations are to terminal growth and discount rate assumptions | 3 |

## Detailed Analysis

**Quant Model as Anchor.** The deterministic DCF produces a base-case IV of $203.59 per share, with bear at $137.60 and bull at $278.92. The base case assumes 7.1% Y1 revenue growth fading to 3.0% by Y5, a 39.7% operating margin, 12% tax rate, and a 15x EV/EBITDA exit multiple at a 6.2% WACC. These assumptions are reasonable but deserve scrutiny. The 7.1% Y1 growth aligns with consensus — Gilead grew revenue 2.1% in FY2025 to $29.4B, but forward estimates embed acceleration from lenacapavir's PrEP approval, the bictegravir/lenacapavir daily oral combo launch, Trodelvy label expansion, and anito-cel in multiple myeloma. Four planned commercial launches in 2026 make 7% achievable, though not guaranteed. The fade to 3% by Y5 is conservative for a company with patent protection through 2036 on its core asset. I would adjust Y1 growth slightly lower to 6% given execution risk on four simultaneous launches, but keep the terminal trajectory intact.

**Exit Multiple Assessment.** The 15x EV/EBITDA base-case exit multiple is the most impactful assumption, comprising 79% of terminal EV. Current trailing EV/EBITDA is 12.8x, reflecting lingering market skepticism about Gilead's growth trajectory. Peers trade at: ABBV ~15.9x, MRK ~11.1x, JNJ ~14-15x, AMGN ~14-15x, BMY ~8-9x. A 15x exit implies Gilead re-rates to peer-average levels as the oncology franchise scales and Biktarvy's extended exclusivity becomes better appreciated. This is plausible but requires proof — the market needs to see lenacapavir treatment revenues materialize and oncology (Trodelvy, anito-cel) contribute meaningfully. My adjusted view: 14x exit is more prudent as a base case, which would bring base IV to approximately $190.

**Sensitivity Grid and Downside Protection.** The most striking feature of the valuation is that every single cell in the 5x5 sensitivity grid — spanning WACC from 4.2% to 8.2% and revenue growth from 3.1% to 11.1% — shows an IV above the current price. The absolute floor of the grid is $163 at the harshest corner (8.2% WACC, 3.1% growth). This means you need to assume conditions worse than any tested scenario to justify the current stock price. Even if I apply my more conservative 14x exit adjustment, the floor would drop to roughly $150 — still 9% above the current price.

**Monte Carlo Probability Distribution.** The 10,000-run Monte Carlo simulation produces a mean IV of $215.32 with a standard deviation of $30.58. The P5 (5th percentile) sits at $168.34, meaning there is only a 5% probability that IV falls below $168 — still 23% above today's price. The P(IV > Price) of 99.9% is one of the strongest signals I have seen in this framework. The distribution is tight enough (coefficient of variation ~14%) to provide high conviction that the stock is undervalued.

**Reverse Engineering Fair Value at $137.** For the current price to be "correct," you would need to believe: (1) Gilead's revenue stagnates or declines from here, with Veklury falling to negligible levels, Biktarvy growth plateauing, and none of the four 2026 launches contributing materially; (2) margins compress from 39.7% to mid-30s due to pricing pressure or mix shift toward lower-margin oncology; (3) the market never re-rates the stock above 12x EV/EBITDA despite a pharma peer group averaging 13-16x. This "everything goes wrong" scenario contradicts Biktarvy's 52% market share dominance, the extended 2036 exclusivity, and lenacapavir's first-in-class PrEP indication with twice-yearly dosing. The bear case is not impossible, but it requires compounding multiple negative assumptions simultaneously.

**Peer Multiple Comparison.** GILD's forward P/E of 14.3x sits below the large-cap pharma average. Detailed comparisons: ABBV trades at 15.7x forward (Humira biosimilar losses largely absorbed, Skyrizi/Rinvoq ramping), MRK at 22.6x (Keytruda franchise, but approaching its own patent cliff in 2028), JNJ at 18.1x (diversified, lower growth), AMGN at 13.7x (debt from Horizon acquisition weighing), and BMY at 9.8x (deep patent cliff on Opdivo/Revlimid). GILD's discount to the ex-BMY peer group average of ~17.5x forward P/E is unjustified given its superior patent runway (2036 vs. peers' nearer cliffs) and ROIC of 21.7%. Applying even a 16x forward P/E to the $9.61 forward EPS yields $154 — 12% above today. At 18x (JNJ parity), you get $173.

## Signal Summary

- **Bull case:** Lenacapavir PrEP becomes a multi-billion dollar franchise, oncology launches execute, and market re-rates GILD to peer-average multiples (16-18x forward P/E), driving the stock toward $180-$220.
- **Bear case:** Pipeline launches disappoint, Veklury revenue continues declining, and the market keeps the multiple compressed at 12-13x forward earnings, limiting upside to the low $140s.
- **Confidence:** High — The combination of a 99.9% Monte Carlo probability, ALL 25 sensitivity cells above current price, and a peer-discounted forward multiple provides unusually strong quantitative support that GILD is undervalued at $137.

## Red Flags

- Biktarvy concentration risk: ~47% of total revenue from one product, despite 2036 patent extension
- Veklury (remdesivir) in secular decline — revenue expected to drop from $1.4B to $0.6B by 2026, a direct headwind to top-line growth
- Four simultaneous commercial launches in 2026 create execution risk — if even two underperform, the growth thesis weakens
- Third-party valuation estimates range from $90 to $288 — extreme dispersion suggests the market has no consensus on Gilead's terminal value
- HIV pricing pressure from government programs (340B, IRA negotiations) could compress margins over time

## Score: 8 / 10

GILD trades at a significant discount to its quant-derived intrinsic value across every tested scenario, with peer multiples confirming undervaluation relative to large-cap pharma. The one-point deduction reflects execution risk on four simultaneous launches and the wide dispersion in third-party valuations, which signals genuine uncertainty about terminal growth.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 138 |
| IV Base | 190 |
| IV Bull | 265 |
| Currency | USD |
| MOS at Analysis Date | 0.6 |
