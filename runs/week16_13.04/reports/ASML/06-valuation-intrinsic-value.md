# Valuation vs Intrinsic Value — ASML

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-18
**Data Sources:** `context/ASML/financials.md`, `context/ASML/financials.json`, `context/ASML/quant-valuation.md`, `context/ASML/quant-valuation.json` (deterministic DCF from `src/quant`, dated 2026-04-18). Web search: ASML Q1 2026 earnings press release, ASML 2030 guidance reaffirmation (44–60B EUR / 56–60% GM), analyst consensus trackers (MarketBeat, Public.com, Simply Wall St, Alpha Spread, GuruFocus, Stock Unlock), peer multiples for AMAT/LRCX/KLAC/TEL (drrobertcastellano on Substack, Investing.com, Tickeron). Snapshot price: $1,459.80. Reporting currency is EUR, trading currency USD — all IV figures below are stated in USD to match the trading quote.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant DCF produces bear/base/bull IV of $464 / $665 / $893 at 12.0% WACC with 18.8% Y1 revenue growth fading to 3% by Y5 — all three scenarios sit 39–68% *below* the $1,459.80 trading price. | 5 |
| 2 | Monte Carlo (10,000 runs) gives P(IV > Price) = 0.0%; P95 IV is only $972.83, still 33% below the current quote. | 5 |
| 3 | The entire sensitivity grid (22.8% growth × 10% WACC at the optimistic corner, reaching IV $997) cannot reach today's price — the market requires assumptions *outside* the grid to justify current value. | 5 |
| 4 | Analyst consensus price targets ($1,482–$1,645 mean, $1,744 median, high $1,994) imply 1–20% upside; independent DCF models (GuruFocus $1,119, StockUnlock $1,617) are split — closer to quant on the bear side. | 4 |
| 5 | Forward P/E of 30.5x, EV/EBITDA 43.8x, P/FCF 69.5x — richer than LRCX (~36x fwd), AMAT (~26x), Tokyo Electron (~28x), and above long-term ASML history of ~25–30x fwd. | 4 |
| 6 | ASML's own 2030 guidance of €44–60B revenue (vs €32.7B FY25) and 56–60% gross margin is already inside the quant bull case on growth (≈6–13% CAGR to 2030) but not on margin — guided GM exceeds current 52.8% meaningfully. | 3 |

## Detailed Analysis

**Owner earnings baseline.** The quant model pegs FY2025 adjusted owner earnings at $9.6B using D&A proxy for maintenance capex, with maintenance capex at 63% of total ($1.0B of $1.6B). FCF in FY2025 was $11.0B (33.8% FCF margin, 115% FCF/NI conversion). Five-year owner-earnings trajectory compounds at ~20% ($4.9B in 2022 to $9.6B in 2025). If the 2030 guide-mid (~€52B revenue, 58% GM, assume 36% op margin, 18% tax) lands, owner earnings scale to roughly $14–17B by 2030. Discounted back at 12% and capitalized at a 15x exit multiple, that is consistent with the quant base case — not materially higher.

**Scenario analysis (anchored on quant, with adjustments).**

- **Bear ($464 quant → my $500):** Quant bear uses 15.8% Y1 growth fading to 3%, 12x exit, 13% WACC. I adjust upward slightly to reflect (a) the €38.8B backlog and EUV capacity fully booked through 2027 — near-term revenue is very visible, (b) ASML's 100% EUV monopoly, which deserves a structurally lower equity-risk premium than the quant's 12%+ WACC treats it to. Bear case still assumes a cyclical downturn (2028–29 digestion) and further China DUV restrictions; I model ~$500/share.
- **Base ($665 quant → my $750):** Quant base uses 18.8% Y1 growth, 3% terminal, 15x exit, 12% WACC. I raise this because (a) the Y5 fade to 3% is likely too aggressive given ASML's 5-year visibility through backlog and the guide implies ≥8% CAGR through 2030, (b) a 15x EV/EBITDA exit for a 100%-monopoly asset with 38% EBITDA margins and 39% ROIC is arguably too low — peer median is 30–40x. Bumping exit multiple to 18x and extending above-trend growth by one year yields ~$750.
- **Bull ($893 quant → my $1,000):** Quant bull uses 21.8% Y1, 18x exit, 11.5% WACC. I lift to ~$1,000 to reflect: High-NA ramp success, sustained 58%+ gross margin per 2030 guide, and terminal multiple for a quasi-monopoly node-shrink arms dealer. Even then I cannot reach the $1,459 quote without stacking (a) 22%+ growth sustained longer, (b) WACC below 10%, and (c) 25x exit multiple — three aggressive assumptions simultaneously.

**Multiples in context.** At 30.5x forward EPS ($47.86), ASML trades at roughly 2x the S&P 500 forward multiple (~17x) and ~1.2x the broad semi-equipment median. Versus its own history, the stock has re-rated meaningfully in the post-2023 AI-capex cycle. The 43.8x EV/EBITDA is arguably *the* richest among quality industrials globally. The P/FCF of 69.5x is extreme — FY2025 FCF of $11B on a $573B market cap is a 1.9% FCF yield before growth. For that yield to be acceptable, the market is implicitly pricing sustained 15–20% annual FCF growth for a decade.

**Reverse-engineering the current price.** To justify $1,459.80 using the quant framework, the model would need roughly: 22–24% revenue growth sustained 5+ years (above current 2030 guide midpoint), sustained 38%+ operating margin, WACC of ≤9%, and a 22–25x EV/EBITDA exit. That is plausible only if you believe: (1) the 2030 €60B high-end guide is the *base* not the ceiling, (2) the post-2030 runway extends at similar growth, and (3) ASML deserves near-bond-like discount rates due to monopoly permanence. Three optimistic priors stacked.

**Implied expectations vs likely reality.** The stock is pricing in perfection at the exact moment that (a) US Congress (MATCH Act, early April 2026) is proposing to cut ASML's remaining China DUV business, already compressing China mix from 36% (Q4-25) to 19% (Q1-26), (b) semiconductor capex is notoriously cyclical and the 2023–26 run has been extraordinary, (c) Monte Carlo sits at 0% probability of IV > Price. When the market prices a great business for perfection, drawdowns are painful — ASML fell ~50% peak-to-trough in the 2022 downcycle.

**Where I differ from quant.** The quant model's 12% WACC is likely 100–200bps too high for a monopoly of this quality; its 3% terminal growth after a 5-year fade may under-capture ASML's durable long runway. My adjusted IV range of $500/$750/$1,000 is ~8–12% above the quant's — but still nowhere near the current price.

## Signal Summary

- **Bull case:** 2030 guide overshoots toward €60B with GM at 60%+, High-NA ramp drives structural share gains in leading-edge, China risk de-escalates, and multiple re-rates further on AI secular demand — stock compounds at 8–12%/yr from here.
- **Bear case:** MATCH Act passes and DUV China revenue evaporates; 2028–29 memory/foundry capex digestion drops revenue 20–30% in one cycle; multiple compresses toward 20–25x fwd; stock corrects 40–50% toward $800–900 IV range.
- **Confidence:** Medium-High — quant model, my adjustments, and sell-side DCFs (GuruFocus at $1,119, my $750 base) all agree the stock is overvalued; only StockUnlock and analyst price targets disagree (and price targets are 12-month, not intrinsic-value estimates).

## Red Flags

- Price 2.2x my base IV and 2.1x quant bear IV — no reasonable assumption set bridges the gap without stacking 3+ optimistic variables simultaneously.
- Terminal value is 76–84% of EV in quant scenarios — valuation extremely sensitive to small changes in terminal growth or WACC.
- Forward P/FCF of 69.5x implies a 1.4% forward FCF yield — demanding decades of continued high growth to deliver equity returns.
- Analyst 12-month price targets ($1,645 mean) are *not* intrinsic value estimates; they track near-term sentiment and momentum, not cash-flow anchors.
- ASML 91% of 52-week range, +139.8% from $608.73 low — sentiment is at or near peak, exactly when margin of safety tends to be thinnest.

## Score: 2 / 10

Great business trading 2.2x my base IV and 2.1x quant bear IV with Monte Carlo P(IV > Price) = 0%; even raising the quant's conservative WACC and pushing terminal growth can't bridge the gap. Honest answer: significantly overvalued at current quote.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 500 |
| IV Base | 750 |
| IV Bull | 1000 |
| Currency | USD |
| MOS at Analysis Date | -192.0 |
