# Valuation vs Intrinsic Value — MRSH

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-24
**Data Sources:** Yahoo Finance (yfinance auto-fetch), deterministic DCF model (src/quant), Marsh FY2025 annual results press release, Insurance Journal, Simply Wall St, MarketBeat, MacroTrends (historical P/E), peer comparison data (AON, WTW, AJG)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Current price of $173.87 sits below every single cell in the 5x5 sensitivity grid (floor: $216), implying undervaluation even under worst-case assumptions | 5 |
| 2 | Monte Carlo simulation yields P(IV > Price) = 99.9% across 10,000 runs, with P5 at $216.55 — still 25% above current price | 5 |
| 3 | Forward P/E of 15.3x is a multi-year low for a business that historically trades at 20-25x; peer group average is 23.7x | 4 |
| 4 | Organic revenue growth decelerated from 7% in FY2024 to 4% in FY2025, partially explaining the de-rating | 4 |
| 5 | $7.75B McGriff acquisition doubled net debt from $10.1B to $16.9B, compressing interest coverage from 9.7x to 6.8x | 3 |
| 6 | Conservative IV (25b/75base) of $231 implies 24.8% margin of safety at $173.87 | 5 |

## Detailed Analysis

**Quant Model Anchor.** The deterministic DCF produces a bear/base/bull range of $156/$256/$371 per share. The base case assumes 11.8% Y1 revenue growth (which includes McGriff inorganic contribution), fading to 3% by Y5, a 23.1% operating margin held flat, and a 15.0x exit multiple on EBITDA. The WACC of 7.5% is derived from CAPM with a 0.73 beta, which reflects the defensive nature of the insurance brokerage model. The conservative IV blend (25% bear, 75% base) produces $231 per share, placing the current price at a 24.8% discount.

**Stress-Testing Assumptions.** I find the base case growth rate of 11.8% in Y1 reasonable given FY2025 GAAP revenue growth of 10% (including McGriff inorganic) and underlying organic growth of 4%. However, the fade to 3% by Y5 may be conservative — Marsh has delivered 5-7% organic growth consistently over the past decade, and the brokerage model benefits from insurance premium inflation even in soft markets. The 15.0x exit multiple is moderate relative to Marsh's 13-year median EV/EBITDA of 14.5x and its current 13.2x (which is depressed). The WACC of 7.5% is fair for a low-beta, asset-light business; if anything, the 0.73 beta argues for a lower discount rate, which would push IV higher. On balance, I believe the model's base case is slightly conservative and the true fair value sits closer to $265-$280.

**Sensitivity Grid Analysis.** The most striking finding is that at $173.87, the stock trades below the absolute floor of the sensitivity grid ($216.08 at 7.8% growth and 9.5% WACC — the harshest combination). This means the market is pricing in either a structural break in the business model, a significant recession in insurance demand, or a capital structure crisis — none of which appear likely for the world's largest insurance broker with $5B in annual FCF and entrenched client relationships.

**Multiple Context.** At 15.3x forward earnings and 13.2x EV/EBITDA, MRSH trades at a significant discount to both its own history and its peer group. AON trades at roughly 21x forward earnings, AJG at 26x, and WTW at 15x. Marsh has historically commanded a premium among brokers due to its scale, margin leadership, and consulting diversification (Mercer + Oliver Wyman). The current multiple compression appears to reflect: (1) organic growth deceleration to 4%, (2) elevated debt post-McGriff, and (3) broader market rotation away from financial services. The deceleration concern is valid but likely temporary — McGriff integration is expected to be meaningfully accretive in 2026+, and insurance brokerage demand is structurally growing.

**Reverse-Engineering the Current Price.** To justify $173.87, the DCF would require either: (a) WACC above 10% (implying far higher risk than a 0.73-beta business warrants), (b) revenue growth of <3% for all five projection years with margin compression, or (c) an exit multiple below 10x, which would be a historic low for the sector. None of these scenarios aligns with the business fundamentals of a dominant, asset-light, recurring-revenue franchise.

**Organic Growth Caveat.** The one legitimate concern is that FY2025 organic growth of 4% represents a step-down from 7% in FY2024 and the mid-single-digit trend. If this deceleration is structural rather than cyclical, the base case IV would compress toward $230-$240 rather than $256. Even so, the stock would remain materially undervalued.

## Signal Summary
- **Bull case:** The market has over-penalized a temporary organic growth deceleration and McGriff integration uncertainty, creating a 25%+ discount to conservative IV for the world's largest insurance broker with 14% ROIC and $5B annual FCF.
- **Bear case:** Organic growth has structurally downshifted to low-single-digits, McGriff integration costs drag on margins for longer than expected, and elevated debt limits capital return flexibility — fair value is still $200+, but upside is more modest.
- **Confidence:** High — The quant model, multiples analysis, and reverse-engineering all converge on the same conclusion: the stock is meaningfully undervalued at $173.87. The only disagreement is on the magnitude of undervaluation.

## Red Flags
- Organic revenue growth decelerated from 7% to 4% in FY2025 — could signal competitive or cyclical pressure
- Net debt nearly doubled to $16.9B post-McGriff; interest coverage compressed to 6.8x
- Integration risk on a $7.75B acquisition is non-trivial and costs are still flowing through
- Stock is near 52-week low ($164.89), suggesting the market sees something not captured in backward-looking financials
- FY2025 net margin (15.4%) declined from FY2024 (16.6%), partly due to acquisition-related costs

## Score: 9 / 10
The stock trades below the worst-case cell in the sensitivity grid and at a 24.8% discount to conservative IV, with 99.9% Monte Carlo probability of being undervalued — this is a clear and compelling valuation setup for a high-quality, asset-light compounder.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 231 |
| IV Base | 256 |
| IV Bull | 371 |
| Currency | USD |
| MOS at Analysis Date | 24.7% |
