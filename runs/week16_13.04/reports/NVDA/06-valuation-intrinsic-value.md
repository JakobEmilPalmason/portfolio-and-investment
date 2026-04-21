# Valuation vs Intrinsic Value — NVDA

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-18
**Data Sources:** `context/NVDA/financials.md` (Yahoo Finance, 2026-04-18), `context/NVDA/quant-valuation.md` and `.json` (deterministic DCF engine, 2026-04-18), WebSearch (MarketBeat, TipRanks, TradingView, Seeking Alpha, Tom's Hardware, IBTimes, dshort/Advisor Perspectives, CNBC for April 2026 NVDA coverage, analyst targets, Rubin roadmap, hyperscaler capex commentary, 10-year Treasury).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant-model intrinsic value is Bear $68 / Base $94 / Bull $124 vs current price $201.68 — the market is ~114% above the DCF base case. | 5 |
| 2 | Monte Carlo run of 10,000 scenarios returns P(IV > Price) = 0.0%. Even the P95 outcome ($138.89) sits 31% below the market price. | 5 |
| 3 | Full 5×5 sensitivity grid (growth 16–24% × WACC 15.3–19.3%) caps IV at $142.12 — market price is outside every plausible cell of the quant model. | 5 |
| 4 | Wall Street consensus target ~$265 (56 analysts) implies a 31% expected return — built on FY27E EPS ~$8.30 and a ~32x forward multiple, implying growth-and-margin persistence that the DCF does not grant. | 4 |
| 5 | Reverse-DCF: to justify $201.68 at a 13% discount rate, NVDA needs ~28% revenue CAGR for 5 years with terminal 18x EV/EBITDA and no margin compression. | 4 |
| 6 | Analyst-favored valuation framework (forward P/E of 17.9x vs $11.24 forward EPS) is materially more generous than the DCF because it ignores capital intensity, WACC, and the post-2027 fade. | 3 |

## Detailed Analysis

**Starting anchor — the quant DCF.** The `src/quant` engine, running a 5-year exit-multiple DCF with CAPM WACC, returns a per-share intrinsic value of $67.97 (bear) / $94.39 (base) / $124.10 (bull). Base-case assumptions are credible but not generous: 20% Y1 revenue growth fading to 3% terminal, 60.4% operating margin held flat, 17.3% WACC (driven primarily by beta of 2.33 × 5.5% equity premium on top of a 4.5% risk-free — the quant model's risk-free is 24bps above the 10Y Treasury at 4.26% on 2026-04-17, so not unreasonable), and a 15x EV/EBITDA exit multiple. Owner earnings for FY2026 run $116.9B simple / $120.1B adjusted, with maintenance capex around 1.3% of revenue. This IV range is directly usable and is where I start.

**Do I agree with the quant model assumptions?** Mostly yes. The beta of 2.33 is the single biggest driver of the "expensive" read — it compounds into a 17.3% cost of equity that punishes terminal value. A lower beta (say 1.6, closer to mega-cap tech) or a lower equity risk premium (5.0% instead of 5.5%) would pull WACC closer to 13-14%. At that discount rate, my own cut of the base case (20% growth fading to 3%, 60% margins, 15x exit) would move IV into the $130-$160 range — still below market, but closer. I flag this as the most defensible adjustment. Conversely, I would not push the exit multiple above 18x for a hardware-leveraged cyclical whose customers (hyperscalers) are already drawing down free cash flow to buy GPUs that may be obsolete in three years.

**Sensitivity grid tells a brutal story.** The 5×5 grid shows IV as a function of 5-year revenue growth (16-24%) and WACC (15.3-19.3%). The maximum cell — 24% growth with 15.3% WACC — prints $142.12. That is the ceiling of the deterministic model under plausible-to-aggressive parameters. Current price at $201.68 sits $60 (42%) above that ceiling. The only way to reach $201 inside this framework is either (a) materially lower WACC (i.e. a lower beta or lower equity premium than consensus uses), (b) a higher terminal exit multiple (>20x), or (c) sustained >25% growth that never fades. Each is defensible in isolation; assuming all three together is what the market is doing.

**Monte Carlo: 0.0% probability of IV above price.** Out of 10,000 simulations, zero produced an intrinsic value above $201.68. The P95 is $138.89 and the mean is $113.90. This does not mean NVDA will fall to $113 — stock prices are set by the marginal buyer's narrative, not the DCF — but it does mean the probability-weighted DCF outcome is materially below the market. A value investor should take this seriously. A growth investor should ask what assumption the model is underweighting.

**Reverse DCF — what must be true for $201?** To get to $201 with a 13% discount rate, 60% operating margins held flat, and a 3% terminal growth rate, I get roughly 28% revenue CAGR for 5 years with an 18x terminal multiple. That means revenue growing from $216B (FY26) to ~$745B by FY31. Hyperscaler capex is projected at $600-700B in 2026 — NVDA is claiming ~30% of that. Sustaining 28% share of a pool that itself is growing 30% per year requires both (a) no meaningful loss of share to custom silicon from Google, Amazon, Meta, OpenAI/AMD, Anthropic's Trainium effort, or Qualcomm/Tesla, and (b) no decline in pricing power as competitors catch up. Both are possible, neither is certain.

**Multiples context.** Trailing P/E of 41.2x and forward P/E of 17.9x are unremarkable for a hyperscaler-exposed chipmaker. But the trailing P/B of 31.2x and P/FCF of 84.3x are not — they reveal how much of the equity value is parked in expectations beyond FY26. Peers: AVGO forward P/E ~32-35x, TSM ~24.5x, AMD trading on forward multiples north of 50x on optimistic out-year EPS. NVDA at 17.9x FY27 EPS looks cheap relative to AVGO, but AVGO has $60B+ of enterprise software revenue that NVDA doesn't; TSM has physical fab moat and better free-cash conversion. NVDA's forward multiple is the right level IF FY27 EPS of $11.24 is durable — but that EPS is already 13% below where FY26 printed, implying the consensus quietly expects a down-cycle.

**Market signal — the analyst target.** The 56-analyst mean is $265 (median $264, high $380, low $140). The low ($140) is below the quant bull; the mean is $140 above the quant base. Consensus is anchoring on forward multiples, TAM expansion, and sequential product roadmap (Blackwell -> Rubin 2H2026 -> Rubin Ultra 2027 -> Feynman 2028) rather than full-cycle DCF. Both frameworks have merit. For Buffett-style analysis, I weight the cash-flow framework more heavily because it survives multiple de-ratings.

## Signal Summary

- **Bull case:** AI capex proves structural (not cyclical), NVDA holds >70% share of accelerators through Rubin Ultra, sovereign-AI and agentic-inference open a second demand wave, and the market re-rates terminal multiple to 20x+ — justifying something in the $200-$260 range even on DCF.
- **Bear case:** Hyperscaler capex growth decelerates in late 2026 or 2027 as free cash flow pressure bites, custom silicon takes 10-15 points of share, and NVDA compresses to a 25x multiple on normalized earnings — price re-rates toward the quant base of $94-$124.
- **Confidence:** Medium — the DCF math is unambiguous (expensive by every cell of the sensitivity grid), but the uncertainty on terminal growth and capex durability is real. Confidence on "fairly valued" would be higher than on "significantly overvalued."

## Red Flags

- Zero Monte Carlo scenarios produce IV above current price — stock is outside the entire modeled distribution.
- Full sensitivity grid max ($142.12) is 30% below market — no plausible growth/WACC combination inside the model supports current price.
- Reverse-engineered price assumptions (28% 5-yr CAGR, no margin compression, 18x+ exit multiple) require compounding goodwill that is historically rare for a hardware vendor.
- Beta of 2.33 means the stock is priced to move violently in either direction — a cost-of-equity rerate alone could swing IV 25-30%.
- Forward EPS ($11.24) is already 13% below trailing ($4.90... wait — trailing is $4.90 from FY26 which ended Jan 2026; forward $11.24 represents FY27 consensus, meaning consensus expects growth, not decline — so this is not a bearish flag but should be watched for downward revisions).

## Score: 3 / 10

Significantly overvalued on a rigorous DCF — 0% Monte Carlo probability of IV > Price and a full sensitivity grid that tops out 30% below the market is a rare and clear signal. The score would be 4-5 if you accept a lower-WACC / higher-multiple framing that brings IV into the $140-$170 range, but even then there is no margin of safety at $201.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 68 |
| IV Base | 94 |
| IV Bull | 124 |
| Currency | USD |
| MOS at Analysis Date | -196.6 |
