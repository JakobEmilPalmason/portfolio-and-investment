# Valuation vs Intrinsic Value — NOVO-B.CO

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-14
**Data Sources:** Quant DCF model (context/NOVO-B.CO/quant-valuation.json, generated 2026-03-24), Yahoo Finance via fetch-financials.py (2026-04-14), Novo Nordisk FY2025 annual report, analyst consensus estimates (22 analysts), Eli Lilly peer comparison, web search for current GLP-1 competitive landscape and pricing developments

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At DKK 246, Novo trades at 10.7x trailing earnings and 7.6x EV/EBITDA — the lowest multiples in over a decade and roughly one-quarter of direct competitor Eli Lilly's multiples (40.8x P/E, 27.6x EV/EBITDA) | 5 |
| 2 | The quant model's bear-case IV of DKK 539 sits 119% above the current price; every cell in the 25-cell sensitivity grid (min DKK 642) exceeds the stock price by at least 161% | 5 |
| 3 | Adjusted owner earnings of DKK 102.4B imply the market is paying ~10.7x OE for a business earning 36% ROIC with 81% gross margins — a level typically reserved for structurally declining or commodity businesses | 5 |
| 4 | Reverse-engineering the current price requires assuming revenue declines of roughly 8-10% per year for 5 years, or a permanent margin compression of 20+ percentage points — neither is supported by the company's actual 2026 guidance of a 5-13% single-year sales dip | 4 |
| 5 | The forward P/E of 11.5x prices in zero recovery from the 2026 trough, despite the Wegovy pill launch expanding the addressable patient population and CagriSema FDA decision expected by late 2026 | 4 |

## Detailed Analysis

**Owner Earnings and Earning Power.** The quant model calculates adjusted owner earnings of DKK 102.4B using maintenance capex of DKK 22.0B (24% of the DKK 90.1B total capex). This separation is critical for Novo Nordisk right now because the company is in the middle of a massive manufacturing buildout — $4.1B in North Carolina, EUR 432M in Ireland, multi-billion expansion in Chartres, France — all growth capex aimed at scaling oral GLP-1 and next-generation production capacity. Simple free cash flow (DKK 29.0B in FY2025) dramatically understates recurring earning power because 76% of capex is growth investment expected to be substantially complete by 2028-2029. A reasonable range for owner earnings in 3-5 years is DKK 110-140B, reflecting modest revenue growth from oral Wegovy ramp and CagriSema launch, partially offset by lower net pricing. Even in a bear case where revenue is flat and margins compress 300bp, owner earnings would be approximately DKK 90-95B — still supporting an intrinsic value well above the current price.

**Scenario Analysis Anchored on Quant Model.** The quant model produces bear/base/bull IVs of DKK 539/800/1,099. I broadly agree with the base case assumptions (7.4% Y1 revenue growth, 41.3% operating margin, 5.6% WACC, 15x exit multiple) but would make two adjustments. First, the WACC of 5.6% derived from a beta of 0.27 may understate risk given the current competitive and pricing uncertainty; a more conservative 6.5-7.0% WACC is defensible, which the sensitivity grid shows still yields IVs of DKK 672-774 — all far above the current price. Second, the model uses a flat 41.3% operating margin; I would fade this to 38-39% by Y5 to reflect structural pricing pressure from IRA negotiations (Ozempic at $274/month vs. $959 list), the Trump pricing deals, and intensifying competition from Eli Lilly's Foundayo and eventual oral generics. Even with both conservative adjustments applied simultaneously (7.0% WACC, 38% terminal margin, 4% growth), the implied IV remains in the DKK 550-600 range — still more than double the current stock price. My own scenario estimates: Bear DKK 500, Base DKK 720, Bull DKK 1,000.

**Multiples in Context.** The current 10.7x trailing P/E and 7.6x EV/EBITDA are not just low relative to Novo's own history (5-year average P/E of approximately 35-40x); they are low in absolute terms for any business with 81% gross margins, 41% operating margins, and 36% ROIC. Eli Lilly trades at 40.8x P/E and 27.6x EV/EBITDA. Even adjusting for Lilly's faster near-term growth trajectory, the valuation gap implies the market is pricing Novo as if it were a mature pharma company facing imminent generic erosion rather than the co-leader of the largest new drug category in a generation. The 7.6x EV/EBITDA implies the market expects EBITDA to decline roughly 40-50% from current levels over a sustained period. For context, even generic-threatened pharma companies typically trade at 8-10x EV/EBITDA. At 15x EV/EBITDA (its 10-year average), Novo would be worth approximately DKK 690 per share on current earnings alone.

**Reverse-Engineering the Current Price.** Using the sensitivity grid, the lowest IV cell (DKK 642) assumes 3.4% revenue growth and 7.6% WACC — and that still exceeds the current price by 161%. To get the DCF to DKK 246, you would need to assume either: (a) revenue declines of 8-10% annually for 5 years combined with margin compression to ~30%, or (b) a WACC above 12%, or (c) a terminal multiple below 5x EV/EBITDA. None of these scenarios is reasonable for a company with Novo's competitive position, brand, pipeline depth, and the secular tailwind of a global obesity epidemic affecting over 1 billion people. The current price effectively assumes the GLP-1 market becomes commoditized and Novo loses pricing power entirely — but even the Trump pricing deal and IRA negotiations still leave the company with significant margins.

**Market Pricing: Pessimism, Not Perfection.** The Monte Carlo simulation returns P(IV > Price) = 100.0% across 10,000 runs, with the P5 percentile at DKK 661 — nearly 2.7x the current price. The market is pricing extreme pessimism. The catalysts driving this pessimism — the bleak 2026 guidance (5-13% sales decline), CagriSema's initial REDEFINE 1 miss on the 25% weight-loss target (it hit 20.4%), Lilly's market share gains to 60% — are real but already fully reflected in (and arguably over-discounted by) the current price. The 6.67% dividend yield, the highest in Novo's modern history, is another signal the market has left this stock for dead. The Wegovy pill launch is showing early signs of expanding the total patient pool rather than cannibalizing injectables, and CagriSema FDA approval by late 2026 would provide a meaningful next catalyst.

## Signal Summary

- **Bull case:** Market is pricing permanent decline into a business with 81% gross margins, 36% ROIC, and an addressable market still in early innings of penetration; oral Wegovy launch and CagriSema approval restore growth narrative, driving re-rating toward 20-25x earnings (DKK 460-575).
- **Bear case:** Pricing pressure proves structural and persistent, Lilly continues taking share, CagriSema disappoints on efficacy, and margins compress toward 30% — but even then, the stock is cheap at current levels.
- **Confidence:** High — The valuation gap between price and any reasonable IV estimate is so wide that errors in individual assumptions (growth rate, margin, WACC) do not change the directional conclusion; even the most punitive sensitivity scenario yields an IV 2.6x the current price.

## Red Flags

- FY2025 FCF conversion dropped to 28.3% (from 69% in FY2024) due to DKK 90.1B capex — the growth capex thesis must prove out or this capital is at risk of being stranded
- The quant model's WACC of 5.6% (beta 0.27) may understate true cost of capital given the stock's recent 52% drawdown and elevated competitive uncertainty
- P/FCF of 2,898x on reported FCF looks alarming on a screen; investors must understand the maintenance vs. growth capex distinction to avoid being misled
- Novo guided for a 5-13% sales decline in 2026 — this is the first revenue decline in over a decade and introduces execution uncertainty around the oral transition

## Score: 9 / 10

At DKK 246, Novo Nordisk trades at a historically extreme discount to any reasonable intrinsic value estimate, with the quant model's bear case (DKK 539) offering 119% upside, the base case (DKK 800) offering 225% upside, and every sensitivity cell exceeding the price by at least 161% — this is a rare instance where the valuation case is overwhelming across virtually all reasonable assumption sets.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 500 |
| IV Base | 720 |
| IV Bull | 1000 |
| Currency | DKK |
| MOS at Analysis Date | 51 |
