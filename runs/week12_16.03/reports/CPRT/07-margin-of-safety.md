# Margin of Safety — CPRT

**Analyst Role:** Risk-Reward Analyst
**Date:** 2026-03-22
**Data Sources:** context/CPRT/financials.md, context/CPRT/quant-valuation.md, context/CPRT/quant-valuation.json, Yahoo Finance, Copart 10-Q (Jan 2026), DOJ disclosure filings, Seeking Alpha, Simply Wall St

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | No price margin of safety vs conservative bear IV — current price of $32.87 is 43% above the analyst-adjusted bear case of $23 and 30% above the quant bear of $25.19 | 5 |
| 2 | Exceptional business margin of safety — duopoly position, $4.8B net cash, 0.1x debt/EBITDA, 8.4x current ratio, and 45% gross margins provide a fortress balance sheet | 5 |
| 3 | Monte Carlo shows 76.9% P(IV > Price), but the 5th percentile at $29.49 implies only 10% downside in a tail scenario — limited permanent capital loss risk | 4 |
| 4 | Sensitivity grid shows 15 of 25 cells produce IV above current price ($32.87), meaning most plausible assumption combinations favor the investor | 4 |
| 5 | DOJ investigation is an unquantifiable binary risk that cannot be modeled — potential fines could range from immaterial to multi-billion | 4 |
| 6 | Bear-to-bull spread of $23 to $50 (2.2x range) provides meaningful asymmetry: ~30% downside vs ~52% upside from current price | 3 |

## Detailed Analysis

**Price margin of safety is absent against the conservative case.** The quant model bear IV of $25.19 sits 23% below the current price, meaning there is no price MOS on a conservative basis. My own adjusted bear case of $23 is even lower, reflecting the possibility that the Q2 revenue decline becomes a multi-quarter trend. At $32.87, the stock needs at least base-case execution to justify the current price. However, the sensitivity grid provides nuance: in 15 of 25 cells (60%), the implied IV exceeds the current price. The current price sits in the lower-middle quadrant of the grid, which means the market is pricing in roughly a 6% growth / 10.6% WACC scenario. If Copart reverts to anything resembling its historical growth rate, the stock is cheap. If growth has structurally slowed, it is roughly fairly valued.

**Business margin of safety is among the strongest I have analyzed.** Copart operates in a structural duopoly with IAA (Ritchie Bros). The business model — acting as an intermediary between insurance companies and vehicle buyers — generates recurring, mission-critical revenue. Insurance companies cannot efficiently process totaled vehicles without Copart or IAA's yard network, technology platform, and buyer base. Switching costs are high because Copart's 200+ yard locations represent decades of land acquisition that cannot be replicated. The balance sheet is pristine: $4.8B in cash against $104M in total debt. Even in a severe downturn, Copart could operate for years without external financing. This business resilience means that even if I am wrong on growth, the probability of permanent capital loss is near zero.

**Downside vs upside asymmetry.** From $32.87: bear case ($23) implies 30% downside; base case ($36) implies 10% upside; bull case ($50) implies 52% upside. The bear-to-bull ratio is 1.7:1 in favor of upside. This is decent but not the 2-3x asymmetry ideal for a high-conviction position. The Monte Carlo distribution reinforces this — the mean is $36.09 (10% above current) with standard deviation of $4.22. The distribution is moderately right-skewed, which is favorable. Critically, the P5 of $29.49 suggests that even in a bad scenario, the stock is only ~10% lower. The downside floor is supported by the massive cash position — $4.8B cash alone is roughly $5.00/share, providing a tangible asset base.

**Zero scenarios.** Permanent capital loss is extremely unlikely. Copart owns hundreds of salvage yards (real assets), has virtually no debt, and generates over $1B in free cash flow annually. The only plausible near-zero scenario would involve massive fraud or a DOJ outcome that fundamentally disrupts operations — both are very low probability. The DOJ investigation relates to potential money laundering through the auction platform (likely foreign buyers using the platform to move illicit funds). Comparable DOJ money laundering settlements in other industries have typically been in the hundreds of millions, not existential. For Copart, even a $500M fine would represent roughly 3 months of operating cash flow.

**Key risks, specifically.** First, the DOJ investigation could result in operational restrictions (e.g., limiting international buyer participation) that structurally reduce auction competitiveness — more concerning than the fine itself. Second, insurance company consolidation could shift bargaining power away from Copart on fee rates, compressing margins. The Q2 operating margin decline from 36.6% to 34.7% may be an early signal. Third, a sustained decline in driving miles or total loss frequency (e.g., from autonomous driving advances) would shrink the addressable market, though this is a 10+ year risk. Fourth, international expansion execution risk — Copart has invested heavily in land and infrastructure in Europe, and returns are not yet proven at scale. Fifth, the declining ROIC trend (24.2% to 16.6% over three years) could signal diminishing returns on the incremental capital being deployed.

## Signal Summary

- **Bull case:** DOJ resolves with a manageable fine, revenue growth resumes at 8-10%, and the multiple re-rates from 21x to 28-30x P/E — stock reaches $48-50 within 18-24 months.
- **Bear case:** Revenue declines persist, DOJ restricts international buyer access, margins compress further, and the stock settles at $22-25 on a structurally lower earnings base.
- **Confidence:** Medium — The business quality provides a high floor, but the absence of price MOS against the conservative case and unresolved DOJ risk limit conviction.

## Red Flags

- No price margin of safety vs conservative IV — stock needs base-case execution to work
- DOJ money laundering investigation with unknown scope and potential operational remedies
- First meaningful revenue decline in Q2 FY2026 (-3.6% YoY) after years of consistent growth
- Operating margin compression to 34.7% from 36.6%, breaking historical stability
- ROIC declining for three consecutive years despite revenue growth
- Heavy growth capex ($350M+/year) with uncertain near-term payoff

## Score: 6 / 10

The business margin of safety is exceptional — fortress balance sheet, duopoly position, and near-zero probability of permanent capital loss. However, the price margin of safety is thin to nonexistent against conservative scenarios. The stock needs at least base-case execution to generate positive returns, and the DOJ overhang adds unquantifiable risk. This is a quality business at a fair-to-modestly-cheap price, not a fat pitch.
