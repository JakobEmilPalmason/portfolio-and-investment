# Valuation & Intrinsic Value --- MTD

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-29
**Data Sources:** Yahoo Finance (yfinance auto-fetch), quant DCF model (src/quant), Mettler-Toledo Q4 2025 earnings release, sell-side consensus (BofA, Morgan Stanley, Jefferies), TIKR.com valuation models, Seeking Alpha, company 2026 guidance

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Current price of $1,232 sits 66% above the quant base-case IV of $742 and 16% above even the bull IV of $1,058 | 5 |
| 2 | Every cell in the 5x5 sensitivity grid (growth 0.9%-8.9%, WACC 9.6%-13.6%) produces an IV below the current price; the highest grid value is $1,010 | 5 |
| 3 | To justify $1,232, the market must be pricing in sustained ~8-9% revenue growth AND a terminal multiple of 20x+ EV/EBITDA --- well above the quant model's 15x exit | 4 |
| 4 | Management's own 2026 guidance implies only ~4% local-currency revenue growth and $46.05-$46.70 adjusted EPS, which on a 26-27x forward P/E gets you to roughly $1,200-$1,260 | 4 |
| 5 | Sell-side consensus target of ~$1,505 (mean) implies the Street awards MTD a ~30-35x forward P/E on 2027 EPS of $51, reflecting a durable quality premium that the DCF model does not capture | 4 |
| 6 | Owner earnings of $888M on an enterprise value of $27.2B produce a 3.3% owner-earnings yield --- thin for a business growing mid-single digits | 3 |

## Detailed Analysis

**Starting from the quant model.** The DCF produces a base-case IV of $742 per share using a CAPM-derived WACC of 11.6%, 4.9% Year-1 revenue growth fading to 3.0% by Year 5, and a 15x EV/EBITDA exit multiple. The bear case ($468) and bull case ($1,058) bracket a wide range, but the current price of $1,232 exceeds all three scenarios. The Monte Carlo simulation (10,000 runs, mean $762, P95 $972) assigns a 0.0% probability that intrinsic value exceeds the current price. This is an unambiguous signal from the model: on standard DCF assumptions, MTD is significantly overvalued.

**Stress-testing the assumptions.** The quant model's WACC of 11.6% is defensible given MTD's 1.44 beta, but the market may be implicitly using a lower discount rate for a business with this quality profile (46% ROIC, 59% gross margins, near-100% FCF conversion). If we compress WACC to 9.0% --- aggressive but not absurd for a high-quality compounder in a lower-rate environment --- and raise the exit multiple to 20x EV/EBITDA (closer to MTD's trailing 22.5x), the DCF would produce a base-case IV in the $1,100-$1,200 range. That is, you need both a materially lower discount rate AND a higher exit multiple to approach the current price. The 15x exit multiple in the quant model is conservative for MTD's quality tier; peers like Danaher and Roper have historically traded at 18-22x. This is the single largest source of model-vs-market gap.

**Reverse-engineering $1,232.** At the current enterprise value of $27.2B and FY2025 EBITDA of ~$1.2B, MTD trades at 22.5x EV/EBITDA. For this to be rational on a 5-year DCF basis, the market must assume: (a) revenue growth of 6-8% annually (well above management's 4% 2026 guide), (b) continued margin expansion toward 30%+ operating margins, (c) a terminal multiple of 18-20x EV/EBITDA, and (d) a WACC around 9%. Management's medium-term target of "6% or better sales growth plus 100+ bps margin expansion" supports part of this but not all. The implied growth rate embedded in the stock is roughly double what the company is guiding for the near term.

**Multiples context.** MTD's trailing P/E of 29.3x and forward P/E of 24.1x sit at a premium to the broader life-sciences peer group average of ~27x trailing and ~22x forward. Historically, MTD has commanded a premium due to its capital-light model, consistent buybacks (reducing share count by ~3% annually), and high ROIC. The 5-year average forward P/E has been approximately 30-35x; at 24x forward earnings, the stock is actually below its own historical range, which partly reflects the recent 19% pullback from the November 2025 high of $1,525. This is an important nuance: while the DCF says "expensive," the relative multiple says "moderately discounted vs. own history."

**What must be true.** For $1,232 to represent fair value over a 5-year horizon, MTD needs to deliver roughly $65-70 in EPS by 2030 (implying ~10% EPS CAGR from 2025) and trade at 18-20x earnings at exit. This is achievable through the combination of mid-single-digit organic revenue growth, 50-100 bps annual margin expansion, and continued aggressive buybacks. It is not a layup, but it is not fantasy either for a business of this quality. The question is whether an investor is being adequately compensated for the risk of paying this price.

**Verdict on valuation.** The DCF model is correct that on standard assumptions, MTD is expensive. However, the model somewhat understates the business's quality premium by using a conservative exit multiple. Adjusting for a more realistic terminal value narrows the gap but does not close it. At $1,232, the stock is priced for flawless execution and favorable macro conditions. There is virtually no margin for error in the valuation, and the owner-earnings yield of 3.3% offers thin compensation for the capital deployed.

## Signal Summary
- **Bull case:** Quality premium is justified; MTD's ROIC moat, pricing power, and buyback machine can compound EPS at 10%+ through the cycle, supporting a 25-30x forward P/E.
- **Bear case:** Paying 66% above base-case IV for a mid-single-digit grower with China headwinds and tariff drag offers essentially zero margin of safety; any earnings miss will compress the multiple sharply.
- **Confidence:** High --- the quantitative evidence is overwhelming that the stock is above fair value on most reasonable assumptions; the debate is only about degree.

## Red Flags
- Price exceeds every single cell in the quant sensitivity grid (25 out of 25 scenarios)
- Monte Carlo P(IV > Price) = 0.0% --- zero of 10,000 simulations justify the current price under standard assumptions
- Owner-earnings yield of 3.3% is below the risk-free rate (~4.5%), meaning an investor earns less than Treasuries on a yield basis
- Negative stockholders' equity ($-24M) means the entire equity valuation rests on future cash flows, with no asset backstop
- 2026 guidance implies only 4% local-currency growth --- below the ~6-8% the market appears to be pricing in

## Score: 3 / 10
MTD is a world-class business trading at a price that offers no margin of safety under any standard DCF framework; even aggressive assumption adjustments barely approach the current price, and the owner-earnings yield is below the risk-free rate.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 468 |
| IV Base | 742 |
| IV Bull | 1058 |
| Currency | USD |
| MOS at Analysis Date | -163 |
