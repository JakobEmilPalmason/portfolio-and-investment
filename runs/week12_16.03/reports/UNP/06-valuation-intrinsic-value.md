# Valuation vs Intrinsic Value — UNP

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Deterministic DCF model (src/quant), yfinance financials, Union Pacific Q4 2025 earnings call, Yahoo Finance, StockAnalysis, analyst consensus estimates, peer filings (CSX, NSC)

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Base IV of $230 sits ~2% below the current price of $235 — the stock is approximately fairly valued on a probability-weighted basis | 5 |
| 2 | Monte Carlo P(IV > Price) of 41.1% means the market is pricing in slightly better-than-base-case execution, not euphoria but not a bargain | 4 |
| 3 | The sensitivity grid shows current price requires ~2% revenue growth and ~8.5% WACC — exactly the base case, leaving no margin for error | 4 |
| 4 | P/FCF of 35.6x is elevated relative to history and peers, driven by heavy capex cycle (~$3.8B/year); owner earnings yield of ~4.2% is more reasonable | 3 |
| 5 | The pending Norfolk Southern merger introduces binary optionality not captured in the DCF — bull case could be significantly higher if approved, but regulatory risk is real | 4 |
| 6 | Management guided mid-single-digit EPS growth for 2026 off $11.98 base, consistent with quant model base assumptions but not exciting | 3 |

## Detailed Analysis

**Owner Earnings Anchor.** The quant model estimates owner earnings of $7.1B, separating $2.5B maintenance capex (65% of total) from $1.3B growth capex. This passes the sanity check — railroads require substantial ongoing maintenance (track, rolling stock, signals) but Union Pacific's precision-scheduled railroading (PSR) has improved asset utilization. Net income of $7.1B plus D&A minus maintenance capex yields roughly $5.8B in distributable owner earnings, or about $9.75 per share. At $235, the stock trades at ~24x owner earnings — not cheap, but defensible for a regulated monopoly with 40%+ operating margins.

**Scenario Analysis — Starting From the Quant Model.** The bear case IV of $142 assumes -1% revenue growth and a 12x exit multiple. I find this too harsh for a duopoly with pricing power: even in the 2020 freight recession, Union Pacific's revenue declined only ~10% peak-to-trough and recovered within two years. I would adjust the bear IV upward to approximately $160 by using a 13x exit multiple, which better reflects the floor for a business with this quality of earnings. The base case IV of $230 assumes 2% revenue growth fading to 3% by Y5 with a 15x exit multiple. This aligns well with management's mid-single-digit EPS growth guidance and 3-4% volume/price growth. I accept the base IV as reasonable. The bull case IV of $333 assumes 5% revenue growth and an 18x exit. I would trim this to approximately $310, because sustained 5% top-line growth requires a strong freight cycle that the current macro backdrop ("softer" per management) does not support. However, if the Norfolk Southern merger closes, the combined entity's synergies ($1.5-2B estimated) could push fair value well above $333 — this is upside optionality the model does not capture.

**Multiples in Context.** At 19.6x trailing P/E, Union Pacific trades below CSX (24.3x) and roughly in line with its own 5-year average (~20-21x). The EV/EBITDA of 13.7x is similarly near the middle of its historical 12-16x range. The forward P/E of 17.4x on $13.51 consensus EPS implies moderate but not aggressive growth expectations. The P/FCF of 35.6x looks alarming in isolation, but this reflects the capex-heavy nature of railroads — owner earnings yield of ~4.2% is the more relevant metric and is adequate for a business of this quality, though not a screaming buy.

**Reverse-Engineering the Current Price.** Looking at the sensitivity grid, $235 sits almost exactly at the 2.0% growth / 8.5% WACC cell ($227). To justify the current price, the market needs Union Pacific to grow revenue at ~2-3% annually, maintain 40%+ operating margins, and deserve a 15x exit EV/EBITDA multiple. These are not aggressive assumptions — they represent a continuation of current trends. But they are also not conservative. There is essentially zero margin for error baked into the price. If WACC ticks up to 9.5% (say, rates stay higher for longer), the same growth assumptions produce IV of $215 — about 8% downside.

**Implied Expectations vs Reality.** The market is not pricing in perfection, nor is it pricing in pessimism. This is a "fairly valued quality compounder" setup. The 41.1% Monte Carlo probability of being undervalued confirms this: it is roughly a coin flip. The distribution is fairly tight (std dev $38.62 on a mean of $228), reflecting the predictability of railroad economics. The risk is not that the business implodes — it is that you pay a fair price and earn only the earnings yield (~5%) plus modest growth, resulting in mid-to-high single-digit total returns. That is acceptable but not Buffett-grade.

**Merger Wildcard.** The proposed Norfolk Southern acquisition, if approved (expected closing early 2027), could be transformational. A transcontinental railroad with $1.5-2B in synergies would likely re-rate the combined entity. But STB scrutiny is intense, the application was initially rejected for incompleteness, and regulatory risk is non-trivial. I would not pay up for merger optionality, but it provides asymmetric upside that is not in the model.

## Signal Summary
- **Bull case:** If the Norfolk Southern merger closes and freight volumes recover, UNP could be worth $310+ within 2-3 years, making today's price look cheap in hindsight.
- **Bear case:** A freight recession combined with higher-for-longer rates and merger failure could push the stock to $160-180, a 25-30% drawdown from here.
- **Confidence:** Medium — the business is highly predictable, but the merger overhang and macro uncertainty widen the outcome distribution beyond what the DCF captures.

## Red Flags
- P/FCF of 35.6x is optically expensive and could attract selling pressure if growth disappoints
- 78-85% of enterprise value sits in the terminal value — highly sensitive to exit multiple assumptions
- $32.8B in total debt (2.6x net debt/EBITDA) is manageable but limits financial flexibility during a downturn
- The Norfolk Southern merger creates a binary outcome that could dominate the stock's trajectory regardless of standalone fundamentals
- Rail inflation running at ~4% squeezes margins if pricing power does not keep pace

## Score: 5 / 10
Union Pacific is approximately fairly valued at $235 — the quant model's base IV of $230 and Monte Carlo mean of $228 both sit slightly below the current price, and the sensitivity grid confirms the market is pricing in base-case execution with no margin for error. This is a quality business at a fair price, not a bargain.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 160 |
| IV Base | 230 |
| IV Bull | 310 |
| Currency | USD |
| MOS at Analysis Date | -46.8 |
