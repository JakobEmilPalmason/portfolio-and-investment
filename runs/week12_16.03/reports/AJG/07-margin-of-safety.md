# Margin of Safety — AJG

**Analyst Role:** Risk & Safety Analyst
**Date:** 2026-03-22
**Data Sources:** Quant model output (context/AJG/quant-valuation.md — bear/base/bull IV, sensitivity grid, Monte Carlo P5/P50), context/AJG/financials.md (Yahoo Finance via yfinance), web search (AJG Q4 2025 earnings, AssuredPartners integration update, 2026 organic growth guidance, AI disruption risk context)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Price is 7.3% ABOVE quant bear IV of $200 — there is no margin of safety against the realistic downside case; the 38% drawdown from $351 IS the correction the market has already taken | 5 |
| 2 | Monte Carlo P5 of $304 is 41% above current price — the quant model's worst 5th percentile outcome still implies major undervaluation, supporting the bull case more than it warns of the bear | 4 |
| 3 | Sensitivity grid floor of $307 (worst plausible cell) is 43% above $214.82 — within the model's assumption universe, the stock looks safe; the question is what the model doesn't capture | 4 |
| 4 | Business-level margin of safety is exceptionally high: 80%+ recurring revenues, no underwriting risk, asset-light, 130+ country diversification, no single client >1% of revenue | 5 |
| 5 | AssuredPartners integration risk is the single largest unquantified risk — $575M in integration costs over 3 years, leadership transition, culture merge of 10,900+ employees | 4 |
| 6 | Net debt of $11.6B at 3.7x gross debt/EBITDA is the weakest balance sheet in AJG's history — adds financial risk at exactly the wrong time (largest acquisition, softening premium cycle) | 4 |
| 7 | The 52-week low of $195 (hit February 2026) is only $15 below current price — the technical floor has been tested; a retest is plausible | 3 |

## Detailed Analysis

**Price vs. Bear IV: The Key Safety Calculation**

The quant model's bear IV of $200 uses 17% Y1 revenue growth (still above organic-only), a 12x exit EV/EBITDA, and an 8.3% WACC. At the current price of $214.82, the stock sits 7.3% above this bear IV — technically a negative margin of safety against the quant's conservative case. This is the central tension in the AJG investment thesis: the stock appears to offer excellent upside (51% to base IV of $325) but no cushion against the downside scenario. The traditional Buffett margin of safety framework would call for a 25-40% discount to conservative IV before initiating a position, which would require a price of $120-$150 against the bear IV of $200 — a level the stock is unlikely to reach without a catastrophic business deterioration. The more relevant framing for AJG is: (1) the 38% decline from $351 to $214 is itself a margin of safety via price compression, and (2) the business model provides structural protection against deep permanent impairment.

**The 38% Drawdown as the Correction: Is the Work Already Done?**

The stock fell from $351.23 (June 2025) to $195 (February 2026) — a 44% peak-to-trough decline — before recovering to $214.82. The decline absorbed three simultaneous fears: AI disruption to the brokerage model, AssuredPartners integration risk from the $13.4B deal, and leverage concerns at 3.7x debt/EBITDA. The question is whether this repricing adequately compensates for the risks. Against the quant base IV of $325, the current price represents a 34% discount — consistent with a "reasonable MOS" entry on a quality compounder. Against the quant bear IV of $200, there is no cushion. For an investor who believes the base case is substantially more likely than the bear case — which the Monte Carlo supports (P5 of $304 implies only a 5% chance of IV below $304) — the current price offers a reasonable risk-adjusted entry.

**Multiple Downside Scenarios: Stress-Testing the Quant Bear**

The quant bear case ($200) is the model's floor, but scenarios that push below it are conceivable:

Scenario A — Integration Breakdown: AssuredPartners culture clash results in producer attrition of 10-15%. Organic growth from the combined entity stalls at 2-3%. Integration costs run $800M over 3 years (vs. $575M guided). EBITDA comes in at $3.0B rather than $3.6B. At 12x EBITDA and $11.6B net debt, equity value per share falls to approximately $165. This is a material impairment scenario but requires both execution failure and multiple compression simultaneously. Probability: 10-15%.

Scenario B — Insurance Premium Softening + Recession: A hard landing in 2026-2027 causes businesses to reduce coverage, driving organic growth negative. Premium rates fall 10-15% across property. AJG revenue growth flatlines at 0-2%. EBITDA compresses to $3.1-3.2B. At 14x EBITDA (peer-floor multiple) with stable debt, equity value is approximately $175-185. Probability: 15-20%.

Scenario C — AI Structural Disintermediation: An AI platform begins winning complex commercial accounts in 2027-2028, compressing commission rates by 10-15% in personal and small commercial lines (30% of AJG revenue). EV/EBITDA multiple de-rates permanently to 12-13x. This scenario requires 5-7 years to play out fully, during which time AJG would generate $15-20B in cumulative FCF. Even in this scenario, the stock at $214 is likely fairly valued. Probability of severe impact within 5 years: 10%.

Scenario D — Quant Model Base Case Materializes: 20% Y1 growth (achieved via AssuredPartners), synergies flow through, leverage normalizes to 3.0x by 2027. Stock re-rates toward $300-325 within 3-5 years. Probability: 50-55%.

**Sensitivity Grid: Where Are the Danger Zones?**

The quant sensitivity grid (growth 16-24% / WACC 5.3-9.3%) shows a floor of $307 — safely above $214.82. The grid's danger zones for this investment are not within the grid itself but below it: outcomes where Y1 revenue growth falls below 16% would require both organic growth stalling AND the AssuredPartners inorganic contribution disappointing. Since AssuredPartners added ~$2.5-3B in revenue to a $11.6B base, the consolidated growth rate in FY2025-FY2026 is structurally above 16% unless there is significant client attrition from the acquisition. The WACC dimension is less threatening: even at 9.3% (bear WACC), IVs range from $307 to $433. A scenario that pushes WACC above 9.3% would require either beta re-rating (unlikely given AJG's defensive characteristics) or a significant rise in the risk-free rate.

**Qualitative Risks the Quant Model Does Not Capture**

The quant model is deterministic on its assumptions but does not model: (1) Goodwill impairment risk — AJG carries $23.6B in goodwill and intangibles on $70.7B in assets; a material impairment would not affect cash flow but would signal thesis deterioration and trigger a revaluation. (2) Regulatory risk — increased transparency requirements on broker compensation (contingent commissions, volume overrides) could structurally compress margins by 50-100bps; this has precedent from the 2004-2005 Spitzer investigations. (3) Key person risk — J. Patrick Gallagher Jr. has been instrumental in the M&A culture; leadership transition risk exists though the organization is deep. (4) Integration execution — the quant model treats revenue as growing cleanly through the consolidation; producer attrition, systems integration failures, or client defections during the transition would impair the base revenue assumption. (5) Interest rate sensitivity — each 50bps rise in blended borrowing costs adds approximately $65-70M to annual interest expense, reducing owner earnings directly.

**The Floor: What Is Truly the Downside?**

AJG going to zero is essentially inconceivable. The business is an intermediary — it bears no insurance claims risk, has no mark-to-market balance sheet, and generates $1.8-2.4B in annual FCF. Even a bankruptcy scenario would result in a controlled reorganization with substantial equity residual. The realistic worst-case floor for permanent capital loss from $214.82 is: severe integration failure + recession + multiple compression to 10-11x EV/EBITDA = approximately $130-150. This is a 35-40% downside from current price, which is painful but not catastrophic for a patient investor. The more relevant downside for a 5-year investor is the quant bear at $200 (7% below current) — not permanent impairment but a zero-return or slightly negative return scenario if held for 1-2 years and the bad scenario materializes.

## Signal Summary

- **Bull case:** The 38% drawdown from peak has created a 34% discount to the quant base IV with a 100% Monte Carlo probability of undervaluation — a rare setup for a proven compounder with recurring revenues and visible synergy catalysts.
- **Bear case:** The bear IV of $200 is only 7% below current price, leverage is at record highs, and AssuredPartners integration risk is the largest unquantified variable in AJG's 40-year history.
- **Confidence:** Medium — business-level margin of safety is excellent; price-level margin of safety is thin vs. the quant bear; the favorable risk-reward ratio (upside ~51% to base vs. downside ~7% to bear) compensates for the thin cushion.

## Red Flags

- Price is 7.3% above quant bear IV — no traditional price MOS; position sizing must reflect this
- Net debt/EBITDA of 3.2x (gross 3.7x) is historically unprecedented for AJG; stays elevated through 2027 per management guidance
- Interest coverage of 3.9x EBIT/interest is the thinnest in AJG's history; leaves limited buffer if EBITDA deteriorates
- 52-week low of $195 was touched in February 2026 — only $20 below current price; a retest is plausible on any negative news
- AssuredPartners integration budget of $575M over 3 years — historically, actual integration costs in large broker deals exceed initial estimates
- FCF step-down from $2.4B (FY2024) to $1.8B (FY2025) reflects integration spending; if FCF does not recover to $2.5B+ by FY2026, the thesis is strained

## Score: 6 / 10

AJG has strong business-level margin of safety (recurring revenues, no balance sheet risk, asset-light model) but very thin price-level margin of safety against the quant bear IV of $200, with net debt at record highs and a major integration underway — the 38% drawdown provides a reasonable but not comfortable cushion, warranting a modest rather than aggressive position.
