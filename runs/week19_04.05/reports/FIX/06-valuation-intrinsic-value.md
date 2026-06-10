# Valuation vs Intrinsic Value — FIX

**Analyst Role:** Valuation Analyst
**Date:** 2026-05-06
**Data Sources:** `context/FIX/financials.md` (yfinance, 2026-05-06), `context/FIX/quant-valuation.md` and `quant-valuation.json` (deterministic DCF, 2026-05-06), web search (TipRanks, TIKR, 24/7 Wall St, stockanalysis.com, gurufocus, simplywall.st, CreditSights, Futurum Group, Tom's Hardware on hyperscaler capex).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant DCF intrinsic value range is bear $497 / base $805 / bull $1,156 vs. market price $1,991.50 — every scenario is below the price by 42% to 75%. | 5 |
| 2 | Trailing P/E 57.9x, EV/EBITDA 41.4x, P/FCF 64.2x are 2-3x typical specialty-contractor multiples (EME ~18x EV/EBITDA, WSO ~20x). | 5 |
| 3 | Monte Carlo (10,000 sims, distribution centered around $964) shows P(IV > Price) = 0.0%; even the 95th-percentile draw ($1,277) is 36% below today. | 5 |
| 4 | The full 5x5 sensitivity grid (rev growth 16-24%, WACC 11.8-15.8%) tops out at $1,227 — no realistic combination of growth and discount rate produces fair value at $1,991. | 5 |
| 5 | FY2025 operating margin (14.4%) and ROIC (47.5%) are at all-time peaks; the model already capitalizes peak earnings, so there is little hidden conservatism to recover. | 4 |
| 6 | Sell-side mean target ($1,991) equals the share price, with high target $2,050 — analysts have no remaining upside to model and are anchored to the cycle. | 4 |

## Detailed Analysis

**Owner earnings baseline.** FY2025 owner earnings were ~$1.02B (NI $1.0B + D&A $142M − maintenance capex $142M). The quant model uses this directly, separating $13M of growth capex. On 35.2M shares, that's roughly $29/share of owner earnings today, against a price of $1,991 — implying a 1.5% owner-earnings yield. For a cyclical, project-based contractor, that is the kind of yield investors normally demand from a long-duration utility, not from a beta-1.71 specialty engineer.

**Quant model anchor and where I would and would not adjust.** The quant model's bear/base/bull at $497/$805/$1,156 already builds in a generous setup for the base case: 20% revenue growth in Year 1, fading over five years to 3% terminal, 14.4% operating margin held constant (peak), 13.8% CAPM WACC (beta 1.71), 15x exit EV/EBITDA, and a ~$0.5B net cash position. The model is mechanical, not pessimistic. The only place I would push back is the **growth schedule**: hyperscaler capex is now expected at ~$725B in 2026 (Tom's Hardware, Futurum) and likely higher in 2027, which could justify holding 18-22% revenue growth for two extra years before fading. If I extend the high-growth window from 5 to 7 years and lift the exit multiple to 18x (matching WSO's ~20x and EME's 18x), the base IV moves to roughly $1,100-$1,300 — still 35-45% below price.

**What must be true for $1,991 to be justified?** Reverse-engineering against the model: holding 13.8% WACC and a 15x exit multiple, you need revenue to roughly double by Year 5 (≥18-20% CAGR sustained, no fade) AND operating margin to expand from 14.4% to ~18% AND a 20-22x exit EV/EBITDA. That is three optimistic levers stacked simultaneously. The sensitivity grid confirms it: the highest cell (24% growth, 11.8% WACC) only reaches $1,227. To clear $1,991 you need a combination of inputs that lies entirely outside the plausible 5x5 grid the model generates from FIX's own history. That is the textbook signature of a stock priced for perfection.

**Multiples in context.** FIX trades at 41.4x EV/EBITDA and 57.9x trailing P/E. EMCOR (EME), the closest mechanical-contractor comp, trades around 18x EV/EBITDA. Watsco (WSO), a higher-multiple HVAC distributor, trades around 20x. FIX is at roughly 2x its closest peers despite serving the same end-market mix. Even versus its own 5-year history (10-15x EV/EBITDA pre-AI cycle), the current multiple represents a 3-4x re-rating that the business would have to validate with sustained earnings growth, not a one-off backlog spike.

**Implied expectations vs likely reality.** The market is implicitly pricing in ~7-10 more years of high-teens growth at peak margins. Hyperscaler capex is real — $725B in 2026 is a credible number — but capex-to-revenue ratios for the hyperscalers (47% MSFT, 54% META, 86% ORCL) are at levels analysts repeatedly call "untenable." When (not if) the digestion phase arrives, FIX's 45%-of-revenue data center exposure becomes a concentration risk, not a growth engine. Monte Carlo P(IV > Price) at 0.0% across 10,000 simulations is the model's way of saying every reasonable distribution of inputs still leaves the stock above intrinsic value.

**Stress-test with optimistic assumptions.** Generous case: 20% growth held for 7 years (not 5), margin expansion to 16%, exit at 18x EV/EBITDA, WACC 12.5%. That produces an IV of roughly $1,300-$1,500. Heroic case (24% growth held for 7 years, 18% margins, 20x exit, 11.5% WACC): roughly $1,700-$1,800. Even the heroic case still sits below the current price. There is no honest way to draw an IV that meets $1,991 without assuming the cycle never ends.

## Signal Summary

- **Bull case:** Hyperscaler AI capex extends to 2030, FIX captures more share at higher margins, IV grows into the price over 4-5 years and the stock compounds at the rate of earnings growth.
- **Bear case:** Data center capex digestion in 2027 cuts FIX's backlog conversion, margins revert toward 9-10%, and the stock re-rates from 41x to 15x EV/EBITDA — a 60%+ drawdown.
- **Confidence:** High — the quant model, the sensitivity grid, the Monte Carlo, and the peer-multiple comparison all point to the same conclusion regardless of which lens you use.

## Red Flags

- Sell-side mean price target ($1,991) equals current price — analysts have no model upside, only momentum.
- 45% of revenue from data centers concentrated in a handful of hyperscaler customers; backlog is reflexive with hyperscaler capex guidance.
- 99% of 52-week range, +362% over 12 months — pricing pattern matches blow-off-top behavior, not a fundamentals-led re-rating.
- Peak everything: peak margin (14.4%), peak ROIC (47.5%), peak FCF margin, peak multiple, peak backlog. Mean reversion in any one of these compresses IV materially.

## Score: 2 / 10

Significantly overvalued. Every honest scenario — quant model, sensitivity grid, Monte Carlo, peer multiples, and reverse-engineered price — produces an IV at least 35% below today. Business quality is real, but the price has run far past it.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 497 |
| IV Base | 805 |
| IV Bull | 1156 |
| Currency | USD |
| MOS at Analysis Date | -300.9 |
