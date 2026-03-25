# Margin of Safety — UNP

**Analyst Role:** Risk-Reward Analyst
**Date:** 2026-03-22
**Data Sources:** Deterministic DCF model (src/quant), Monte Carlo simulation, sensitivity grid, Union Pacific Q4 2025 earnings call, Yahoo Finance, analyst estimates, regulatory filings (STB)

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | No price margin of safety — current price of $235 exceeds the conservative (bear) IV of $160 by 47%, meaning the stock must execute at or above base-case assumptions to justify its price | 5 |
| 2 | Strong business margin of safety — duopoly position, 40% operating margins, essential infrastructure, regulated pricing power provide a durable floor under earnings | 5 |
| 3 | Monte Carlo P(IV > Price) of 41.1% means the probability-weighted outcome is slightly unfavorable — less than coin-flip odds of being undervalued | 4 |
| 4 | Sensitivity grid shows only 8 of 25 cells produce IV above the current price ($235), and all require either above-base growth or below-base WACC | 4 |
| 5 | Bear-to-bull IV spread of $150 ($160-$310) provides a defined range, but the downside from current price to bear IV (-32%) exceeds the upside to bull IV (+32%) — symmetric, not asymmetric | 3 |

## Detailed Analysis

**Price Margin of Safety: Absent.** The adjusted conservative (bear) IV of $160 sits 32% below the current price of $235. MOS = ($160 - $235) / $160 = -46.8%. There is no price margin of safety by any honest measure. The Monte Carlo simulation reinforces this: at P(IV > Price) of 41.1%, the probability-weighted outcome slightly favors the stock being overvalued versus undervalued. Looking at the sensitivity grid, the current price of $235 requires at minimum 2% revenue growth at 8.5% WACC ($227 cell, still slightly below) — this is the exact base case. To get comfortable with $235, you need either above-average growth (4%+) or a below-average discount rate (7.5% or lower). Only 8 of 25 grid cells produce IV above $235. This is not the profile of a stock with a margin of safety.

**Business Margin of Safety: Substantial.** Where UNP lacks price safety, it compensates with business durability. Union Pacific operates one of only two western U.S. Class I railroads (with BNSF, owned by Berkshire Hathaway). This is a natural duopoly protected by impossible-to-replicate physical infrastructure — 32,000+ route miles, $85B+ replacement cost. Switching costs are enormous: shippers build facilities along specific rail lines. Operating margins of 40.2% are best-in-class among North American railroads (CSX runs at ~30% operating margin, or 70% operating ratio). The business generates $5.5B+ in free cash flow annually and has raised dividends for 15+ consecutive years. Even in the 2020 freight collapse, Union Pacific remained profitable and recovered quickly. This is not a business that goes to zero.

**Downside vs Upside Asymmetry.** From $235, the realistic downside to bear IV ($160) is -32%. The realistic upside to bull IV ($310) is +32%. This is symmetric — not the 2-3x upside-to-downside ratio that Buffett-style investing demands. The Monte Carlo P5 ($169) and P95 ($296) further confirm the range is balanced around fair value. In a severe recession scenario (2008-style), railroad stocks declined 40-50% — that would put UNP at $140-150, which actually converges with the bear IV. The recovery took approximately 2-3 years. For a long-term holder, the business would survive and recover, but the opportunity cost of holding through that drawdown is real.

**Zero Scenarios.** Union Pacific going to zero is essentially impossible absent nationalization or a complete restructuring of the American freight system. The physical assets alone are worth $50-60B in replacement terms. Debt of $32.8B is manageable at 2.6x net debt/EBITDA, with no near-term maturity walls. Even a catastrophic freight downturn would not impair the business permanently — railroads have survived two World Wars, the Great Depression, and deregulation. The worst realistic scenario is a prolonged period of stagnant earnings plus multiple compression, which could mean a $130-150 stock price but not capital impairment.

**Key Risks — How You Could Be Wrong.**
1. **Freight recession deepens** (Likelihood: Medium, Severity: Medium). S&P Global is forecasting deterioration in industrial production and housing starts. If volumes decline 5-10% over 2026-2027, EPS could fall to $10-11, pushing the stock to $180-200. Early warning: quarterly carload volumes, intermodal container counts, ISM manufacturing index.
2. **Norfolk Southern merger fails** (Likelihood: Medium, Severity: Low-Medium). The STB has already rejected the initial application and is requesting additional documentation. If the merger collapses, UNP loses the bull-case optionality and could see a 5-10% de-rating as merger premium unwinds. Early warning: STB procedural rulings, state AG opposition filings.
3. **Higher-for-longer interest rates** (Likelihood: Medium, Severity: Medium). With $32.8B in total debt, each 100bp increase in refinancing costs adds ~$300M in annual interest expense. The WACC sensitivity is stark: moving from 8.5% to 9.5% WACC reduces base IV from $227 to $215. Early warning: 10-year Treasury yield, Fed dot plot.
4. **Regulatory tightening on rail pricing** (Likelihood: Low, Severity: High). The STB has periodically considered stricter rate regulation. A forced reduction in pricing power would directly compress margins. This is a tail risk but would fundamentally alter the investment thesis.
5. **Intermodal competition from autonomous trucking** (Likelihood: Low-Medium over 5-10 years, Severity: Medium). If autonomous trucking achieves scale, it erodes railroads' cost advantage on medium-haul freight. This is a 5-10 year risk, not immediate, but it chips away at the long-term moat narrative.

**Concentration Risks.** Union Pacific's revenue is concentrated in North America (primarily U.S. and Mexico cross-border), with meaningful exposure to coal (~15% of revenue, secularly declining), agricultural products (weather-dependent), and intermodal (macro-sensitive). Mexico cross-border freight (~10% of revenue) creates tariff and trade policy exposure. Geographic concentration in the western U.S. means natural disasters, wildfires, or infrastructure disruption along key corridors could temporarily impair operations.

**Tail Risks.** The Norfolk Southern merger is the dominant tail risk — both upside and downside. Beyond that: a major derailment or environmental disaster (a la East Palestine for NSC in 2023) could trigger regulatory backlash and reputational damage. Accounting is straightforward for railroads — depreciation schedules are the main judgment area, and there are no red flags in UNP's financials.

## Signal Summary
- **Bull case:** The business is a fortress — 40% margins, duopoly position, essential infrastructure — and if the merger closes, the combined entity re-rates significantly higher.
- **Bear case:** At $235, you are paying full price for base-case execution with no margin for error; a freight recession or rate spike could deliver a 20-30% drawdown with no buffer.
- **Confidence:** Medium — high confidence in the business quality, but low confidence that the current price offers adequate compensation for the risks.

## Red Flags
- MOS of -46.8% means price exceeds conservative IV by a wide margin
- Only 41.1% probability of being undervalued per Monte Carlo — less than a coin flip
- Only 8 of 25 sensitivity grid cells produce IV above the current price
- Downside-to-upside ratio is symmetric (1:1), not the asymmetric profile value investors seek
- $32.8B debt load amplifies earnings sensitivity to rate changes
- Coal revenue (~15%) is secularly declining, creating a structural headwind

## Score: 4 / 10
Union Pacific is a high-quality business with no price margin of safety — the current price of $235 exceeds the conservative IV of $160 by 47%, Monte Carlo gives only 41% odds of undervaluation, and the sensitivity grid requires above-base-case assumptions to justify the price. The business moat is real, but you are paying for it in full.
