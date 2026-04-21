# Valuation vs Intrinsic Value — ITW

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-19
**Data Sources:** `context/ITW/financials.md` and `financials.json` (yfinance snapshot 2026-04-19), `context/ITW/quant-valuation.md` and `quant-valuation.json` (deterministic DCF, CAPM WACC, Monte Carlo 10k runs), web search (Public.com, TipRanks, MarketBeat, WallStreetZen for targets; MacroTrends and Fullratio for historical P/E; Investing.com and Benzinga for Q4 2025 earnings and 2026 guidance; 24/7 Wall St. for dividend/buyback).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant DCF gives bear/base/bull per-share IV of $115 / $187 / $270, with current price $272.26 sitting at the extreme upper edge of the bull case. | 5 |
| 2 | Monte Carlo (10,000 runs) shows only 0.65% probability that IV exceeds current price — the market is pricing outcomes the deterministic model rarely reaches. | 5 |
| 3 | Trailing P/E of 26.0x and EV/EBITDA of 18.7x sit ~13% above the 10-year mean P/E of 23.8x and near the upper end of ITW's historical range (MacroTrends, Fullratio). | 4 |
| 4 | 2026 management guidance is GAAP EPS $11.00–$11.40 (7% midpoint growth) and organic growth of only 1–3% — consistent with the quant's 2.5% base revenue growth assumption. | 4 |
| 5 | Sensitivity grid: current price of $272 exceeds every cell in the 5×5 growth-×-WACC matrix; the richest cell (6.5% growth, 7.9% WACC) produces only $248. | 5 |
| 6 | Analyst consensus targets cluster $257–$280 (target mean $275.88), essentially flat to current price — the Street is not underwriting upside either. | 3 |

## Detailed Analysis

**Starting anchor — the quant model.** The deterministic DCF (CAPM WACC 9.9%, exit multiple 15x EV/EBITDA, 5-year fade from 2.5% to 3.0% revenue growth, 26.3% operating margin, 2.5% maintenance capex, $8.1B net debt, 288M shares) produces a base IV of $187 per share. The bull case — which already assumes 5.5% first-year revenue growth, 18x exit multiple, and 9.4% WACC — tops out at $270. The bear case falls to $115. At $272.26, the stock trades above all three. MOS vs bear IV is −136%. The quant-flagged "negative revenue growth in projection" warning reflects that TTM FY2025 revenue was essentially flat (+0.9% vs FY2024) and FY2024 itself was down 1.3% vs FY2023; the model's 2.5% base-year growth is therefore already more optimistic than trailing reality, not a pessimistic extrapolation. Management's own 2026 guide of 1–3% organic growth corroborates the quant's assumption — there is no obvious upward adjustment the deterministic model is missing.

**Stress-testing the assumptions.** The most plausible way to justify a higher IV is a higher exit multiple (quality premium) rather than higher growth. If I substitute an 18x exit multiple (bull case) onto the base-case growth/WACC (2.5% / 9.9%), I still land near $215 — roughly $57 below the current price. To reach $272 with the base-case growth schedule I would need roughly an 22x exit EV/EBITDA and a sub-9% WACC simultaneously. Neither is impossible for a best-in-class compounder, but both sit above ITW's own historical averages (18.7x current vs a long-run EV/EBITDA closer to 15–17x) and above its 10-year mean P/E of ~24x. In short: the current price is consistent with *perpetual-premium* assumptions, not with the quant's mechanical extrapolation of 1–3% organic growth.

**Scenario view.**
- **Bear ($115)** — I think the quant bear is slightly too harsh; it assumes −0.5% Y1 revenue and a 12x exit. A more realistic bear (flat revenue, margins to 25%, 13x exit) nudges IV closer to **$135–$150**. Either way, a 45–55% drawdown is the realistic floor if the US industrial cycle rolls over and multiples compress.
- **Base ($187)** — I agree with the quant here. 2.5% revenue growth, 26.5% operating margin, 15x exit matches management's 2026 guide and ITW's historical average multiple. My adjusted base is **$185–$200**.
- **Bull ($270)** — Quant bull already requires 5.5% growth, 18x exit, and a low WACC. That triple-stack only reaches today's price. I'd flag this as a ceiling, not a base for upside. My adjusted bull is **$260–$290**.

**Multiples in context.** Trailing P/E 26.0x vs a 10-year mean of 23.8x (Fullratio/MacroTrends) — ~13% premium to history. Forward P/E 22.4x on the $12.14 forward EPS, still at the high end of the 5-year mean of 24.2x when growth was higher. EV/EBITDA of 18.7x vs Emerson Electric's 19.1x (Investing.com/Jan 2026) and the quality-industrial median near 15–17x. ITW does deserve a premium to mid-tier peers (higher ROIC ~28%, higher FCF conversion), but the current multiple leaves essentially no room for either multiple expansion or for the 1–3% organic growth to disappoint.

**Reverse DCF — what's baked into the price.** To justify $272, the market is implying roughly: ~4% revenue CAGR through 2030 (vs 0% realized 2022–2025), a 27%+ operating margin sustained indefinitely, and a 17–18x exit EV/EBITDA held forever. That is a pricing of *continued excellence* with no cyclical hiccup. For a Dividend King with 63 consecutive increases and enterprise-initiative margin uplift, it isn't absurd — but it leaves no cushion.

**Monte Carlo and sensitivity.** The MC distribution (mean $187, P95 $242, std $31) puts the current price at roughly the 99th percentile of modeled outcomes. **P(IV > Price) = 0.65%.** In the 5×5 sensitivity grid, the highest cell ($248) still sits $24 below the current price — every single combination of reasonable growth (−1.5% to +6.5%) and WACC (7.9% to 11.9%) yields an IV below market. The signal is unambiguous: you cannot twist this DCF's dials within reasonable ranges and produce today's price.

## Signal Summary

- **Bull case:** Enterprise-initiative margin expansion delivers 28%+ operating margin, 2026 revenue accelerates to 4%, and the market sustains its premium multiple — price drifts to $300+ over 2–3 years (low single-digit annualized return, mostly dividend + buyback).
- **Bear case:** US industrial cycle weakens in late 2026, organic growth flips negative, multiple re-rates to historical mean (~23x P/E on $11 EPS) — stock trades to $210–$240, a 12–23% drawdown from current.
- **Confidence:** **Medium** — quality of the underlying business and data is high; the gap between price and conservative IV is the clearest signal in this analysis.

## Red Flags

- Every cell of the 5×5 sensitivity grid (25 combinations) produces IV below current price.
- Monte Carlo P(IV > Price) = 0.65% — effectively the model cannot get there.
- Current EV/EBITDA of 18.7x and P/E of 26.0x both sit above ITW's 10-year averages.
- TTM revenue growth of +0.9% combined with 2026 management guide of 1–3% organic — slow growth at a premium multiple is an unforgiving setup.
- Analyst target mean of $275.88 implies ~1% upside; the Street is not underwriting further expansion.

## Score: 3 / 10

High-quality business priced for continued perfection. The quant model, historical multiples, and reverse-DCF all agree: today's price already reflects the bull case, with Monte Carlo putting the probability of undervaluation at under 1%. A great company is not a great investment at this multiple.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 140 |
| IV Base | 190 |
| IV Bull | 275 |
| Currency | USD |
| MOS at Analysis Date | -94.5 |
