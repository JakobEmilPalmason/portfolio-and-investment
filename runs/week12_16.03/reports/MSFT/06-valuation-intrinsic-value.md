# Valuation vs Intrinsic Value — MSFT

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** context/MSFT/quant-valuation.json, context/MSFT/quant-valuation.md, context/MSFT/financials.md, Yahoo Finance, Seeking Alpha, Motley Fool, TipRanks, web search for peer multiples and recent developments

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At $382, MSFT trades right at the quant base IV ($381) and 45% above bear IV ($264), leaving no price margin of safety against conservative assumptions | 5 |
| 2 | Owner earnings of $101.8B are inflated by using D&A as maintenance capex proxy; true maintenance capex is likely higher given the $64.6B total capex run rate, which compresses adjusted IV | 5 |
| 3 | MSFT is now the cheapest Magnificent Seven stock on forward P/E (20.3x) and trades below its 5-year average P/E of ~30x, reflecting genuine pessimism around capex ROI | 4 |
| 4 | Monte Carlo gives 70.3% probability IV exceeds price, but input distributions may understate capex risk and OpenAI partnership uncertainty, making this probability optimistic | 4 |
| 5 | Sensitivity grid shows current price ($382) is justified at approximately 10.8% growth / 10.4% WACC ($394), meaning the market is pricing in below-base-case growth | 3 |
| 6 | The 53% maintenance capex ratio the model uses is likely too low for a company spending $100B/year on AI infrastructure; even small shifts here move IV materially | 4 |

## Detailed Analysis

**Owner Earnings Assessment.** The quant model estimates adjusted owner earnings at $101.8B by treating D&A ($34.2B) as the maintenance capex proxy and classifying the remaining $30.4B of capex as growth investment. This is mechanically correct but deserves scrutiny. D&A has surged from $13.9B in FY2023 to $34.2B in FY2025, reflecting the massive GPU and datacenter buildout. The real question is whether today's $64.6B capex includes a growing maintenance tail — servers and cooling infrastructure that must be replaced every 3-5 years. If true maintenance capex is closer to 60-65% of total (rather than 53%), owner earnings drop to roughly $90-95B, reducing base IV by approximately $30-40 per share. I adjust my base owner earnings estimate to $95B, acknowledging that growth capex is genuinely creating new capacity but that the maintenance burden is rising faster than the D&A proxy suggests.

**Scenario Analysis.** For the bear case, the quant model assumes 9.8% Y1 growth fading to 3%, an 11.4% WACC, and a 12x exit multiple, producing $264 per share. I broadly agree with this as a reasonable floor, but I would note one additional risk: if Azure growth decelerates further (it already disappointed in Q2 FY2026) and the OpenAI partnership fractures — with Amazon now competing for OpenAI's cloud workloads — the exit multiple could compress below 12x. My adjusted bear IV is $250, reflecting a 10-11x exit multiple in a scenario where AI capex proves partially stranded. For the base case, the quant model's $381 is remarkably close to today's price. I accept the 12.8% Y1 growth and fade schedule as reasonable given Azure's 31% growth and Office/Dynamics durability, but I lower my base IV to $365 to account for higher maintenance capex and the risk that operating margins compress 1-2 points as AI infrastructure costs run ahead of AI revenue monetization. For the bull case, I agree the quant model's $513 is achievable if Azure AI revenue continues its 45% growth trajectory, Copilot monetization accelerates across the enterprise, and margins hold. I keep this at $510.

**Multiples in Context.** MSFT at 20.3x forward P/E is genuinely cheap relative to its own history (5-year average ~30x) and vs Magnificent Seven peers. The trailing P/E of 23.9x and EV/EBITDA of 16.4x are below the software industry average of 26x P/E. However, the P/FCF of 52.9x is alarming — FCF margin has compressed from 33% (FY2022) to 25% (FY2025) as capex consumes more operating cash flow. The P/FCF multiple is the honest signal: investors are paying 53x the cash the business actually generates after all capital spending. This creates a tension — MSFT looks cheap on earnings multiples because D&A masks the true cash cost of the business, but expensive on FCF multiples because capex is real cash out the door.

**What Must Be True.** The sensitivity grid shows the current price of $382 sits near the intersection of ~10.8% growth / 10.4% WACC ($394). This means the market is pricing in growth modestly below the quant base case — roughly 10-11% revenue growth sustained, with margins holding. This is not unreasonable given Azure's recent deceleration and capex concerns, but it is not pessimistic either. For the price to be a genuine bargain, you need to believe growth re-accelerates above 12% as AI infrastructure spending converts into AI revenue — a plausible but unproven thesis. The 53 Wall Street analysts with a mean target of $595 are pricing in a much more optimistic scenario, implying the market has room to re-rate if capex fears prove overblown.

**Monte Carlo Reliability.** The 70.3% P(IV > Price) is supportive but not decisive. The Monte Carlo's P5 of $341 and P95 of $534 produce a reasonable spread, but the input distributions likely underweight the fat-tail risk of AI capex impairment and OpenAI partnership breakdown. I would adjust the effective probability to approximately 60-65% after accounting for these model-exogenous risks.

## Signal Summary
- **Bull case:** If Azure AI monetization inflects and Copilot adoption accelerates, MSFT re-rates to 25-28x earnings, implying $470-530 — a 25-40% upside from here.
- **Bear case:** If AI capex proves partially stranded and OpenAI exclusivity is lost, FCF remains depressed and the stock trades to $250-280, a 25-35% downside.
- **Confidence:** Medium — The business quality is not in doubt, but the valuation gap between "fairly valued" and "cheap" is narrow, and the capex cycle introduces genuine uncertainty about future cash generation.

## Red Flags
- P/FCF of 52.9x signals that earnings multiples overstate cheapness; real cash generation is under pressure
- D&A surge from $13.9B to $34.2B in two years may understate true maintenance burden as AI infrastructure ages
- FCF margin compressed from 33% to 25% in three years with no clear inflection point
- OpenAI partnership under strain — Microsoft threatening to sue over Amazon deal creates strategic uncertainty
- 45% of Azure cloud backlog tied to a single unprofitable customer (OpenAI)

## Score: 6 / 10
MSFT is approximately fairly valued at $382 relative to a stress-tested base IV of $365, with meaningful upside in the bull case but no clear margin of safety against conservative assumptions; the compressed P/E is offset by an elevated P/FCF and rising capex uncertainty.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 250 |
| IV Base | 365 |
| IV Bull | 510 |
| Currency | USD |
| MOS at Analysis Date | -52.7 |
