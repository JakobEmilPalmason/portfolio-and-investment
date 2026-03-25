# Valuation vs Intrinsic Value — MA

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Yahoo Finance (yfinance auto-fetch), quant-valuation model (src/quant DCF), Seeking Alpha, MarketBeat, StockAnalysis, MacroTrends, company Q4 2025 earnings call, analyst consensus estimates

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Current price ($496) sits almost exactly at quant base-case IV ($495), suggesting fair value at base assumptions | 5 |
| 2 | Trailing P/E of 30x is 20% below the 5-year average of ~38x, indicating meaningful multiple compression | 4 |
| 3 | Monte Carlo simulation shows 85.6% probability IV exceeds current price, with median IV of $578 | 4 |
| 4 | Company guiding 12-13% revenue growth for FY2026 vs quant model's 16.2% Y1 assumption — model may be slightly aggressive | 4 |
| 5 | Owner earnings of $15B (FY2025) growing at 18-19% annually, with minimal maintenance capex ($1.1B, 92% of total) — asset-light compounding | 5 |
| 6 | Value-added services approaching 40% of revenue and growing ~20% annually provide an underappreciated growth vector | 3 |

## Detailed Analysis

**Starting from the Quant Model.** The DCF engine produces a bear/base/bull range of $347/$495/$662 per share, using an 8.9% WACC (CAPM-derived from 0.84 beta), 16.2% Y1 revenue growth fading to 3% by Y5, and a 15x base exit EV/EBITDA multiple. The base case of $495 is essentially at the current price of $496, which at face value suggests Mastercard is fairly valued. However, several assumptions in the quant model deserve scrutiny.

**Stress-Testing Growth Assumptions.** The quant model uses 16.2% revenue growth in Y1, which reflects FY2025's reported growth rate. However, Mastercard's own FY2026 guidance calls for 12-13% net revenue growth on a currency-neutral basis. Analyst consensus sits around 12.6% for FY2026. This means the quant model's Y1 growth assumption is likely 3-4 percentage points too high. Looking at the sensitivity grid, at 12.2% growth and 8.9% WACC, the IV drops to $491 — essentially today's price. That said, the growth fade to 3% by Y5 is arguably too conservative for a business with secular tailwinds in digital payments (global card penetration still well below 50% of consumer spending in many markets) and a rapidly scaling value-added services segment growing at 20%+. A more realistic fade schedule might sustain 8-10% growth through Y5 rather than collapsing to 3%. This partly offsets the lower near-term growth. My adjusted base case uses 13% Y1 growth fading to 6% by Y5, producing an IV around $520.

**Evaluating the Exit Multiple.** The 15x EV/EBITDA base exit multiple is reasonable but potentially conservative for a business of this quality. Mastercard currently trades at 22x EV/EBITDA, and its 5-year average trailing P/E is ~38x (implying higher EBITDA multiples historically). Visa trades at 20x EV/EBITDA. For a capital-light duopoly with 60%+ operating margins, 60%+ ROIC, and durable competitive advantages, a 15x terminal multiple arguably undervalues the franchise. However, in a normalizing rate environment, some multiple compression is warranted. I would use 16-17x as a more appropriate base exit, which lifts the base IV to roughly $540-560.

**Multiples in Context.** The trailing P/E of 30x is 20% below the 5-year average of ~38x and represents the lowest valuation Mastercard has traded at since late 2022. The forward P/E of 22x (using $22.65 consensus EPS) is more telling — it prices in ~14% earnings growth, which is below what analysts project (13.6% EPS growth in FY2026, accelerating to 15.7% in FY2027). Compared to Visa (forward P/E ~23x, EV/EBITDA ~20x), Mastercard trades at a slight premium, which is consistent with its faster revenue growth rate. Relative to the S&P 500 at ~20x forward earnings, Mastercard's premium is modest given its superior growth, margins, and return on capital profile.

**What Must Be True for Current Price.** At $496, the market is pricing in roughly 12% revenue growth fading to 3-4% over five years with no multiple expansion — essentially a deceleration scenario where Mastercard grows at GDP+ rates. The sensitivity grid confirms this: the current price sits in the lower-left quadrant of the grid (lower growth, higher WACC), meaning the market is pricing in a pessimistic combination. For the price to be justified as a good long-term entry, you need to believe that growth will not sustainably exceed low double digits and that the terminal multiple will compress below historical averages. Given secular digitization tailwinds, the value-added services ramp, and the duopoly's pricing power, this appears conservative.

**Monte Carlo and Probability-Weighted Outcomes.** The Monte Carlo simulation shows 85.6% probability that IV exceeds the current price, with a mean IV of $582 and standard deviation of $77. The P5 (worst 5% of outcomes) is $460 — about 7% below today's price — while the P95 is $716. This distribution is right-skewed, consistent with a high-quality compounder where the base case delivers solid returns and upside scenarios deliver substantially more. Even at P25 ($527), you would earn roughly 6% upside from the current price. The probability-weighted expected return is attractive.

## Signal Summary
- **Bull case:** Value-added services sustain 15-20% growth, digital payment penetration accelerates in emerging markets, multiple re-rates toward historical average (~35x P/E). IV $620-680. Requires continued execution, no major regulatory disruption.
- **Bear case:** Regulatory actions (Credit Card Competition Act, EU interchange caps) compress net revenue growth to high single digits, fintech competition erodes share, multiple compresses further to 25x P/E. IV $350-400. Requires multiple simultaneous headwinds materializing.
- **Confidence:** Medium-high. The business quality is clear, the valuation is the most reasonable it has been in years, and the probability distribution favors upside. The main uncertainty is near-term growth trajectory given macro and regulatory headwinds.

## Red Flags
- Quant model Y1 growth assumption (16.2%) exceeds company guidance (12-13%) — the model is somewhat optimistic near-term
- Rebates and incentives growing 16% annually could pressure net revenue growth more than headline numbers suggest
- Operating expense growth accelerating (14% in FY2025) needs monitoring
- Terminal value accounts for 80% of base case — highly sensitive to exit multiple assumption

## Score: 7 / 10
Mastercard is trading near its quant base-case IV but at the lowest P/E multiple in years, with a probability-weighted distribution strongly favoring upside; the market is pricing in a pessimistic growth deceleration that appears inconsistent with the business's secular tailwinds, making this a reasonably valued to modestly undervalued opportunity for patient investors.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 370 |
| IV Base | 540 |
| IV Bull | 660 |
| Currency | USD |
| MOS at Analysis Date | -34 |
