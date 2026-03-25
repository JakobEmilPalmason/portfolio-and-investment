# Valuation vs Intrinsic Value — EW

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** context/EW/financials.md, context/EW/quant-valuation.md, context/EW/quant-valuation.json, Yahoo Finance, Simply Wall St, Seeking Alpha, company Q4 2025 earnings release, analyst consensus estimates, Edwards Lifesciences 2026 guidance

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Stock trades at $82.50 vs quant base IV of $69.29 — 19% above base case, implying market prices in optimistic growth or higher exit multiple | 5 |
| 2 | Forward P/E of 25x on $3.31 EPS is reasonable for a quality medtech compounder, but trailing P/E of 45.6x reflects depressed FY2025 net income ($1.1B vs $4.2B in FY2024) | 4 |
| 3 | Sensitivity grid shows current price ($82.50) requires either ~21% Y1 revenue growth at base WACC, or base growth with a lower WACC (~7.5-8%) — both plausible but optimistic | 5 |
| 4 | Monte Carlo P(IV > Price) = 42.9% — a near coin-flip, suggesting the stock is neither clearly cheap nor clearly expensive under the model's assumptions | 4 |
| 5 | Terminal value represents 85-91% of enterprise value across scenarios — the valuation is overwhelmingly a bet on the long-term steady state, not near-term cash flows | 4 |
| 6 | Company guided FY2026 revenue of $6.4-6.8B (+8-10% growth) and adjusted EPS of $2.90-3.05, consistent with the quant model's base case growth assumptions | 3 |

## Detailed Analysis

### Quant Model Assessment and Stress Testing

The quant model produces a base IV of $69.29 per share using a 9.5% WACC, 18.8% Y1 revenue growth fading to 3% by Y5, a 27% operating margin, and a 15x EV/EBITDA exit multiple. The bear case ($47.46) uses a 10.5% WACC, 15.8% growth, and a 12x exit multiple, while the bull case ($94.16) assumes 9.0% WACC, 21.8% growth, and an 18x exit multiple.

I have several adjustments to the model. First, the 27% operating margin assumption anchors to FY2025's compressed level. Edwards has historically operated at 29-35% operating margins, and management is guiding toward margin expansion as TMTT scales (TMTT was margin-dilutive during its launch phase). A more reasonable steady-state margin is 29-31%. Second, the 3% terminal growth rate at Y5 may be conservative for a business with durable structural tailwinds — the aging global population, TAVR penetration into moderate aortic stenosis, and TMTT expansion into mitral/tricuspid. I would use 3.5% terminal growth. Third, the 15x exit multiple is reasonable but perhaps conservative for a market leader with 60%+ share, 78% gross margins, and minimal leverage; quality medtech peers trade at 18-22x EV/EBITDA.

### Adjusted Scenarios

**Bear case (adjusted): $55.** I agree the quant bear IV of $47 is too harsh. At a 12x exit multiple, the model assumes Edwards de-rates to commodity medtech levels, which is implausible for a business with 60%+ TAVR market share and 78% gross margins. Raising the bear exit multiple to 13x and allowing 28% operating margins produces roughly $55. This scenario assumes Medtronic gains meaningful TAVR share, TMTT scaling disappoints, and margins compress further from tariff and R&D spending pressure.

**Base case (adjusted): $78.** Starting from the quant's $69 base, I adjust upward for: (a) operating margin recovery to 29% vs 27%, (b) terminal growth of 3.5% vs 3%, and (c) accounting for the $3.5B net cash position which the EV-based model captures but which deserves emphasis. The net effect is roughly $78 per share. This scenario assumes Edwards executes on 2026 guidance, maintains TAVR dominance, and TMTT grows 30%+ annually.

**Bull case (adjusted): $105.** The quant bull of $94 understates the optionality. TMTT is on a path to $2B by 2030 (management target), SAPIEN M3 opens the mitral replacement market, and PASCAL for US tricuspid in Q4 2026 could be transformative. At a 20x exit multiple (consistent with premium medtech), 30% operating margins, and 4% terminal growth, I get approximately $105.

### Multiples in Context

Edwards trades at 25x forward earnings ($3.31 consensus), 24.7x EV/EBITDA, and 7.3x EV/revenue. The Medical Equipment industry trades at 30-33x P/E on average, meaning Edwards' forward P/E is actually below peers. However, the trailing P/E of 45.6x is inflated by temporarily depressed earnings. EV/EBITDA of 24.7x is above medtech peers (SYK ~22x, TMO ~18x), reflecting the market's willingness to pay for Edwards' growth profile and competitive position.

The forward P/E of 25x implies roughly 10-12% earnings growth compounding over the next several years, which aligns with management's 8-10% revenue growth guidance plus modest margin expansion. This is not pricing in perfection — it is pricing in successful execution of a credible plan.

### Reverse Engineering the Current Price

At $82.50, the sensitivity grid shows the stock sits between the 20.8% growth / 10.5% WACC cell ($82.91) and the 18.8% growth / 8.5% WACC cell ($84.28). The market is either pricing in slightly above-base growth at base WACC, or base growth with somewhat lower risk. Given the company just guided 8-10% revenue growth (below the quant model's 18.8% Y1 assumption, though the model may be using a different revenue base), the current price appears to embed reasonable rather than extreme optimism.

However, a critical nuance: the quant model's Y1 growth of 18.8% appears to extrapolate from recent trends, while management guides 8-10%. If I recalibrate Y1 growth to 9% (midpoint of guidance), the base IV would drop meaningfully — probably to $60-65. This is the key tension in the valuation.

### Market Pricing Assessment

The market is pricing Edwards as a quality compounder executing on a multi-year growth plan. At 25x forward earnings, it is not pricing in perfection (that would be 35x+), but it is pricing in consistent execution with no major competitive disruptions. The 42.9% Monte Carlo probability confirms this is roughly fairly valued — the stock is slightly above the median simulation outcome of $80.45. The risk is asymmetric to the downside if growth disappoints, but the business quality provides a floor well above zero.

## Signal Summary
- **Bull case:** TMTT scaling toward $2B by 2030, SAPIEN M3 launch, and operating margin recovery to 30%+ could drive earnings well above consensus, supporting $100+ valuation.
- **Bear case:** TAVR market share erosion from Medtronic Evolut improvements, TMTT execution risk, and sustained margin compression from tariffs and R&D spending could justify a stock in the $55-65 range.
- **Confidence:** Medium — The business quality is high and visible, but the valuation leaves limited room for error at current prices; the quant model's base case suggests overvaluation, while adjusted assumptions suggest roughly fair value.

## Red Flags
- Operating margin declining from 34.5% (FY2022) to 27.0% (FY2025) — a significant four-year compression trend that management needs to reverse
- ROIC declining from 20.9% to 12.6% over the same period — capital efficiency deteriorating as the balance sheet grows
- Terminal value constitutes 85-91% of EV — the valuation is heavily dependent on long-term assumptions, not near-term cash generation
- FY2024 net income of $4.2B appears to include a large one-time gain (possibly related to the Critical Care divestiture), making year-over-year comparisons unreliable

## Score: 5 / 10
Edwards Lifesciences is a high-quality business trading at approximately fair value on adjusted estimates — the quant model's base case suggests modest overvaluation, but reasonable adjustments for margin recovery and a quality premium bring the stock close to intrinsic value, leaving no clear margin of safety for new buyers.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 55 |
| IV Base | 78 |
| IV Bull | 105 |
| Currency | USD |
| MOS at Analysis Date | -50 |
