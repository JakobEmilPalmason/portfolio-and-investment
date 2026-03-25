# Valuation vs Intrinsic Value — ROP

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-23
**Data Sources:** Yahoo Finance (yfinance auto-fetch), quant-valuation model (DCF/MC/sensitivity), Seeking Alpha, Investing.com earnings transcripts, TIKR, RBC Capital research notes, Roper Technologies IR filings

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Price of $354 sits below the quant bear-case IV of $411, implying 14% MOS even on pessimistic assumptions | 5 |
| 2 | Forward P/E of 15.2x is roughly half the 5-year average P/E of ~32x; EV/EBITDA of 14.6x vs 10-year median of ~22x | 5 |
| 3 | Monte Carlo simulation yields P(IV > Price) = 100% across 10,000 runs, with P5 at $596 — 69% above current price | 4 |
| 4 | Reverse-engineering the current price implies permanent organic growth of ~2-3% and a terminal multiple of 10-11x EBITDA — well below this business's track record | 5 |
| 5 | 2026 guidance of only 5-6% organic growth and softness in Deltek/Neptune/DAT justify some multiple compression but not a 40% drawdown | 4 |
| 6 | Sensitivity grid shows IV ranges from $583 to $1,012 across all growth/WACC combinations — current price is below every single cell | 4 |

## Detailed Analysis

**Quant model stress test.** The DCF model uses a base-case WACC of 8.2%, Y1 revenue growth of 17.6% fading to 3% terminal, and a 15x exit EBITDA multiple. These assumptions are reasonable but arguably conservative for a business generating 69% gross margins and 31% FCF margins with minimal capex (1.3% of revenue). The bear case at 9.2% WACC, 14.6% Y1 growth, and 12x exit still yields $411 per share — 16% above the current price. I stress-tested by layering in a scenario where organic growth stalls at 4% for two years (reflecting Deltek/Neptune headwinds) before recovering: even in this scenario, the 5-year DCF with a 12x exit yields approximately $380-390 per share, still above the current price. The model's assumptions hold up under reasonable stress.

**Scenario analysis.** Bear case ($411): organic growth decelerates to 5% and stays there, no further margin expansion, 12x exit multiple reflects permanent re-rating as a "slow-growth software conglomerate." This scenario requires believing Roper's acquisition engine permanently breaks down and AI disrupts its vertical software moat — possible but unlikely given their embedded mission-critical products. Base case ($635): 8% total revenue growth (5-6% organic + 2-3% M&A), stable 40% EBITDA margins, 15x exit. This is essentially what management guided for 2026 extending forward. Bull case ($888): successful AI monetization across portfolio, return to 8%+ organic growth, continued high-quality M&A deployment from $6B+ capacity, 18x exit reflecting premium compounder status. The wide bull-to-bear spread ($411-$888) reflects genuine uncertainty about the growth trajectory, but the critical point is that even the bear case is above the current price.

**Multiples in context.** ROP's current EV/EBITDA of 14.6x is at its lowest level since 2019 and sits at the bottom decile of its 10-year range (median ~22x). The forward P/E of 15.2x compares to a 5-year average of ~32x. This is a business with 69% gross margins, 31% FCF margins, 95%+ recurring revenue, and a 15-year track record of double-digit compounding. Peers like Constellation Software (CSU.TO), Danaher (DHR), and Fortive (FTV) trade at 20-30x forward earnings. Even adjusting for Roper's near-term growth headwinds, the multiple compression seems disproportionate. The discount relative to its own history and peers creates a substantial valuation gap.

**Reverse-engineering the price.** At $354 per share (market cap ~$38B, EV ~$46B), the market is pricing ROP at roughly 14.6x trailing EBITDA of $3.1B. For this price to represent fair value on a 5-year DCF basis, you would need to assume: (a) organic growth permanently stuck at 2-3%, (b) no accretive M&A despite $6B capacity, (c) terminal multiple compression to 10-11x EBITDA, and (d) WACC above 10%. This combination requires a structural impairment thesis — that Roper's vertical software businesses are facing secular decline. The 5-6% organic growth guide for 2026, while disappointing, is a cyclical trough driven by three specific segments (Deltek GovCon, Neptune meters, DAT freight), not a structural break. Management explicitly noted they are not baking in recovery in these areas and will raise guidance as visibility improves.

**Monte Carlo assessment.** The 10,000-simulation Monte Carlo returns P(IV > Price) = 100%, with the 5th percentile at $596 — 69% above the current price. The mean IV of $775 implies 119% upside. Even accounting for model uncertainty and potential overstatement of base-case margins, the probability distribution is overwhelmingly skewed to the upside. The standard deviation of $116 around the mean of $775 suggests reasonable model stability.

**Key risk to valuation thesis.** The single biggest risk is that AI genuinely disrupts Roper's vertical software moat, enabling horizontal platforms to replicate niche functionality. If this materializes and organic growth turns negative, the bear case drops toward $300-350. However, Roper's software products are deeply embedded in customer workflows (court management, healthcare compliance, freight logistics), creating switching costs that are functional rather than contractual. Management's formation of an AI accelerator team suggests they view AI as an opportunity to expand margins rather than a threat.

## Signal Summary
- **Bull case:** At 15x forward earnings with $2.4B FCF, the market is pricing in permanent growth impairment that contradicts Roper's 15-year compounding track record and $6B M&A firepower.
- **Bear case:** AI disruption of vertical software, sustained organic growth deceleration below 4%, and failure of acquisition pipeline could validate the lower multiple.
- **Confidence:** High — The valuation case is quantitatively compelling, with the price sitting below even the most conservative DCF scenario across all sensitivity grid cells.

## Red Flags
- 2026 organic growth guidance of 5-6% is the lowest in recent history, signaling near-term headwinds
- Debt/EBITDA at 3.0x is elevated relative to the 2023 trough of 2.4x, reflecting recent acquisition spending
- Terminal value represents 73-82% of total DCF value, making the exit multiple assumption critical
- Interest coverage has declined from 11.6x (FY2023) to 7.0x (FY2025) as debt has grown
- Current ratio of 0.5x and negative working capital indicate reliance on continuous cash generation

## Score: 9 / 10
The stock trades below the quant bear-case IV, below every cell in the sensitivity grid, and at half its historical multiple — a rare alignment of quantitative signals pointing to deep undervaluation for a high-quality compounder.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 411 |
| IV Base | 635 |
| IV Bull | 888 |
| Currency | USD |
| MOS at Analysis Date | 14 |
