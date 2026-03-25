# Valuation vs. Intrinsic Value — AJG

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant model output (context/AJG/quant-valuation.md — deterministic DCF, sensitivity grid, Monte Carlo 10,000 runs), context/AJG/financials.md (Yahoo Finance via yfinance), web search (AJG Q4 2025 earnings release, AssuredPartners integration update, peer EV/EBITDA for MMC/AON/WTW, 2026 organic growth guidance)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant base IV of $325 implies 51% upside from $214.82; Monte Carlo P(IV > Price) = 100% across 10,000 simulations | 5 |
| 2 | Trailing P/E of 37.4x is structurally misleading — $1.1B non-cash acquisition D&A distorts GAAP; forward P/E of 14.5x on $14.82 EPS reflects true earning power | 5 |
| 3 | Bear IV of $200 is only 7.3% below current price — unusually thin gap that makes the bear case the binding constraint for position sizing | 5 |
| 4 | Quant model's 20% Y1 revenue growth is achievable in FY2025 (AssuredPartners contributed ~$2.5-3B incremental), but FY2026 organic guidance of 5.5% means inorganic boost fades | 4 |
| 5 | AJG trades at 19.4x EV/EBITDA vs MMC at ~14-16x and AON at ~17x — a premium that has historically been justified by faster growth but has compressed significantly since peak | 3 |
| 6 | Sensitivity grid floor at $307 (worst plausible cell: 16% growth / 9.3% WACC) sits 43% above current price — undervaluation is robust across assumption ranges | 4 |
| 7 | Owner earnings of $2.5B (FY2025) represent a 4.5% yield on $55.2B market cap — thin for a compounder but supported by 8-10% organic growth visibility | 3 |

## Detailed Analysis

**Owner Earnings as the True Earnings Anchor**

The quant model anchors intrinsic value on FY2025 owner earnings of $2.5B: net income $1.5B plus D&A of $1.1B minus maintenance capex of $145M. This is the most economically honest earnings representation for AJG. The D&A add-back is justified: $1.1B of amortization is almost entirely purchase-price amortization from 776 acquisitions over four decades, not economic depreciation of operating assets. An insurance broker requires minimal reinvestment — capex has run at just 1% of revenue — and the business generates substantially more cash than GAAP earnings suggest. FCF conversion averaged 155% of net income over FY2023-FY2025, confirming this consistently. On a per-share basis, FY2025 owner earnings of $2.5B across 257M shares equals approximately $9.73/share. If AJG delivers the $160M in synergies targeted by end of 2026 and organic growth holds at 5.5%, owner earnings should reach approximately $3.0-3.2B by FY2027 ($11.70-12.50/share). The quant model uses FY2025 owner earnings as its starting base revenue-normalized cash flow, producing a WACC of 7.3% (CAPM-derived, beta 0.67, risk-free rate 4.5%) — a defensible rate for a low-beta, recurring-revenue services business.

**Scenario Analysis Anchored on the Quant Model**

The quant bear case ($200/share) uses 17% Y1 revenue growth (still above pure organic), a 12x exit EV/EBITDA, and an 8.3% WACC. This is a genuine stress scenario: it assumes the market re-rates AJG to below peer multiples, inorganic growth decelerates, and the cost of capital rises. At $214.82, the stock is 7.3% above this bear IV — meaning the price already embeds near-full-stress conditions. A rational bear case investor would need to believe organic growth stalls to 3-4%, AssuredPartners integration underperforms, and the multiple compresses to 12x EV/EBITDA (below all current peers). That combination is low-probability but not impossible. The quant base case ($325/share) requires 20% Y1 revenue growth, 15x exit EV/EBITDA, and 7.3% WACC. The 20% figure is aggressive for organic-only AJG (~8-10%) but fully achievable for the consolidated entity in FY2025-FY2026 post-AssuredPartners close in August 2025, which added approximately $2.5-3B in annualized revenue. AssuredPartners drove AJG to approximately $14B in annual revenue — consistent with the 20% step-up modeled. The growth fade assumption (to 3% by Y5) is conservative and captures the reversion toward organic-only growth as the M&A benefit amortizes. The 15x exit EV/EBITDA is actually below AJG's current 19.4x and below its 5-year historical range (19.8x-25.7x), making it a conservative exit assumption. The quant bull case ($466/share) uses 23% Y1 growth, 18x exit multiple, and 6.8% WACC — achievable if synergies materialize faster than expected ($260-280M vs $160M target) and the market re-rates closer to historical norms.

**Multiples in Context: What 14.5x Forward P/E and 19.4x EV/EBITDA Tell Us**

The forward P/E of 14.5x is the critical metric. It is based on analyst consensus of $14.82 EPS for FY2026, which reflects a full year of the combined AJG + AssuredPartners entity with synergies beginning to flow. At 14.5x forward earnings, AJG is priced below Marsh McLennan (approximately 17-22x forward P/E, ~14-16x EV/EBITDA) and below Aon (approximately 19-20x forward P/E, ~17x EV/EBITDA). This is unusual: AJG has historically commanded a growth premium over both peers. The EV/EBITDA of 19.4x looks richer, but EBITDA is temporarily suppressed by $639M in interest expense on the post-AssuredPartners debt load and $575M in integration costs being amortized over three years. Adjusting for normalized debt service (management targets 3.0x leverage by late 2027), the underlying EBITDA multiple is lower than the headline figure implies. Peer context: Willis Towers Watson trades at approximately 13x EV/EBITDA and is the cheapest of the big four brokers. AJG's premium to WTW has compressed to its narrowest point in years. If AJG were to trade at a 2x EV/EBITDA premium to WTW (historically conservative), it would imply approximately 15x EV/EBITDA — roughly consistent with a stock price of $230-250 even on depressed near-term EBITDA.

**Reverse-Engineering $214.82: What the Market is Pricing**

At $214.82 per share, $55.2B market cap, and $67.5B EV against FY2025 EBITDA of $3.6B, the headline ratio is 18.75x EV/EBITDA. Working backwards through the quant DCF: to justify $214.82 with a 7.3% WACC and 15x exit multiple, the implied growth rate is approximately 6-8% — barely above organic guidance and well below the inorganic-boosted recent pace. Alternatively, keeping 20% Y1 growth and solving for the implied WACC: the market-implied discount rate is approximately 13-14%, or roughly 6-7 percentage points above CAPM. That risk premium would be appropriate for a company facing structural disruption, significant leverage stress, or deteriorating competitive position — none of which currently apply to AJG with precision. The most rational interpretation is that the market is pricing three simultaneous fears (AI disruption to the brokerage model, AssuredPartners integration failure, prolonged high leverage) and treating them as correlated, which historically overshoots fair value in the short term.

**Sensitivity Grid: The Most Plausible Range**

The quant sensitivity grid covers revenue growth from 16% to 24% (rows) and WACC from 5.3% to 9.3% (columns), producing IVs ranging from $307 to $526. The most plausible cluster for a 5-year horizon sits at 16-20% growth / 7.3-8.3% WACC, yielding IVs of $323-$388. Even the most conservative single cell — 16% growth at 9.3% WACC — produces an IV of $307, which is 43% above the current price of $214.82. This means the stock would need to be priced as if growth collapses below the worst quant scenario and WACC exceeds the bear case by 1.0% simultaneously to justify anything near the current price. The grid confirms the undervaluation is not an artifact of generous single assumptions but holds across a wide range.

**Monte Carlo: Is 100% Probability Credible?**

The Monte Carlo runs 10,000 simulations with stochastic variation in growth rate and WACC, producing P(IV > Price) = 100%, P5 = $304, P50 = $400, mean = $405. The 100% result should be understood as "within the model's assumption universe, no simulated scenario produces IV below $214.82." The P5 of $304 is the worst 5% outcome — and it is still 41% above current price. This is directionally credible: the quant model's assumptions are not extreme, and the business's recurring-revenue, asset-light characteristics make deep cash flow deterioration unlikely in the absence of a structural event. However, the Monte Carlo does not model scenarios outside the growth/WACC grid — including a major M&A write-down, a sustained multi-year insurance recession, or a regulatory event. The honest interpretation is "high statistical confidence of undervaluation within normal business conditions," not certainty.

## Signal Summary

- **Bull case:** AssuredPartners synergies ($260-280M by 2028) and organic growth recovery to 7%+ re-rate AJG back toward historical 20x EV/EBITDA, driving the stock toward the quant base IV of $325 within 3-5 years.
- **Bear case:** Integration costs overrun, organic growth stalls at 4-5%, and multiple compression to peer parity (~14-15x EV/EBITDA) leaves intrinsic value near the quant bear of $200 — only 7% below current price.
- **Confidence:** Medium — quant model strongly signals undervaluation with 100% MC probability and a 43% gap to the sensitivity floor, but the bear IV being close to the current price constrains certainty.

## Red Flags

- Bear IV of $200 is 7.3% below current price — the margin of safety vs the realistic downside case is essentially zero
- ROIC declined from 9.2% (FY2022) to 5.9% (FY2025) as acquisition-inflated invested capital ($36.3B) swamped earnings — must recover as synergies flow through
- Net debt of $11.6B at 3.2x net debt/EBITDA constrains capital flexibility; management targets 3.0x by late 2027
- Trailing P/FCF of 51.4x — FCF dropped to $1.8B in FY2025 from $2.4B in FY2024, partly from integration spending; normalization is required for the thesis to work
- The quant model's 20% Y1 growth assumption is driven by the AssuredPartners inorganic step-up; if the deal was mispriced, this assumption becomes the key fault line in the valuation

## Score: 7 / 10

At $214.82, AJG is modestly to meaningfully undervalued against the quant base IV of $325 with a 100% Monte Carlo probability of undervaluation, but the bear IV of $200 is uncomfortably close to the current price and the quant model's revenue growth assumptions depend on M&A execution remaining intact — limiting the score below 8.
