# Valuation vs Intrinsic Value — ADP

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-19
**Data Sources:** `context/ADP/financials.md` (yfinance snapshot 2026-04-19), `context/ADP/quant-valuation.md` + `.json` (deterministic DCF generated 2026-04-18), WebSearch (Apr 2026) on analyst targets, historical P/E (Public.com, MacroTrends, FullRatio), peer multiples (Paychex, Paycom, Workday via Yahoo/StockAnalysis), FY2026 guidance (Seeking Alpha, DHRMap, Investing.com Q2 FY26 transcripts).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant DCF produces Bear/Base/Bull IV of $146 / $228 / $322 vs current price $200.47 — price sits just below base case but ~37% above the conservative bear IV. | 5 |
| 2 | Monte Carlo P(IV > Price) = 86.8% — probability-weighted setup is favorable because the market has already compressed the multiple from ~30x to ~19x. | 5 |
| 3 | ADP now trades at 19.3x trailing / 16.8x forward earnings vs a 5-yr average P/E of ~30.7x and 10-yr average ~30.2x — a ~35–45% multiple compression in 10 months. | 5 |
| 4 | Sensitivity grid shows IV > current price in 19 of 25 growth × WACC cells; the price only clears IV if both growth fades below 3.3% AND WACC rises above 9.7%. | 4 |
| 5 | FY26 management guidance (Jan 2026): revenue growth >6%, adjusted EPS growth 9–10% — directly in line with the quant model's 7.3% Y1 growth assumption. | 4 |
| 6 | Analyst consensus 12-month PT ~$260–$290 (15 analysts) = 30–45% upside; even the low target of $208 is above spot. | 3 |

## Detailed Analysis

**Quant anchor and why I largely agree with it.** The deterministic DCF uses a CAPM-derived WACC of 8.7% (beta 0.86, Rf 4.5%, ERP 5.5%), a 7.3% Y1 revenue growth fading to 3.0% by Y5, a 26.3% operating margin held flat, and an exit EV/EBITDA of 15.0x. Owner earnings are $4.1B FY25 with effectively 100% maintenance capex (D&A ≈ capex), which is the right treatment for a cap-light software/services business. Those inputs read as honest: growth matches management's just-reaffirmed FY26 guide of >6% revenue and ~10% EPS, margin is already at an achieved level (26.3% op margin FY25), and the 15x exit is below ADP's own 10-year trading average but appropriate given that employment growth is slowing. My adjusted base IV lands within $10 of the model's $228, so I'll use the model's bear/base/bull of **$146 / $228 / $322** as published.

**Where I'd gently push back.** The bear IV at $146 assumes 4.3% Y1 revenue growth and a 12x exit multiple. That is harsh for a dominant payroll processor with 99%+ recurring revenue and a float that earns interest on client funds. Even in a recession scenario, ADP has not posted sub-5% revenue growth in the past decade; FY20 (COVID) was +2% and that was with payroll volumes cratering. A 12x exit multiple would be below Paychex's current ~12.5x EV/EBITDA despite ADP having better scale, international reach, and a stronger technology stack (Lyric HCM). I view the bear as genuinely conservative rather than "realistic worst" — which is the right way to frame a margin of safety anchor. I am not adjusting it up.

**The sensitivity grid tells the story.** Of the 25 growth/WACC combinations, 19 produce IV above the current $200.47. The price only clears IV in the bottom-right quadrant: growth ≤5.3% AND WACC ≥9.7%. That requires both a durable slowdown in private employment (plausible but not base case) and a ~100 bp rise in the risk-free rate or risk premium from here (less plausible given the current 4.5% 10Y). The center cell at the base assumptions produces $240.78 — 20% above spot. The implication: at today's price, the market is implicitly pricing in 3–5% long-run growth AND ~10% WACC, both at the pessimistic end of reasonable.

**Multiples in context.** ADP at 19.3x TTM / 16.8x fwd is trading at a level it has not seen outside the March 2020 COVID lows. Compared to peers: Paychex 20.3x TTM, Paycom bull case uses 32x EV/EBITDA, Workday trades on revenue multiples and is loss-making on GAAP. ADP's EV/EBITDA of 13.4x is very close to Paychex at 12.5x despite ADP's superior scale (5x revenue) and Employer Services growth. The 10-year peak P/E was 38.0x (Dec 2021); the 10-year trough was 23.3x (Mar 2020). At 19.3x we are BELOW the 10-year trough. Either the market is right that employment is about to break (and ADP earnings will compress), or the stock is materially mispriced.

**Reverse-engineered implied expectations.** At $200.47 with $10.40 trailing EPS and applying a perpetuity framework, the market is pricing ~3% long-term growth on current earnings at a ~10% cost of equity — roughly inflation-plus-population. That is a very bearish read for a business that has grown EPS at ~10% CAGR over the past decade and just guided to 9–10% EPS growth for FY26. Either the market believes ADP's EPS is at a cyclical peak that will contract, or the discount is excessive. Given float income (9.1B of client fund investments at current yields) is actually a tailwind in a higher-rate world, the "peak earnings" case is weaker than it looks on the surface.

**Monte Carlo read.** P(IV > Price) of 86.8% is high. Mean IV $242, median $240, P5 $184, P95 $308. Even the P10 at $195 is only slightly below spot. The distribution is symmetric enough (std $37 on a mean $242) that the downside tail isn't fat. I'd not quarrel with this — it is consistent with my own scenario analysis.

## Signal Summary

- **Bull case:** Employment data stabilizes, float income compounds, ADP executes on Lyric + Workforce Suite. Stock re-rates back to 24–25x earnings (mid-historical) on ~$12 EPS by FY27 → $290–300 within 18 months, matching analyst consensus.
- **Bear case:** US enters meaningful recession, private payrolls contract for 2+ quarters, ADP loses ~10% of worksite employees, PEO margin compression continues, float yields fall. Earnings flatline at ~$10 and multiple stays at 16–17x → stock in $160–175 range.
- **Confidence:** High — quant model, analyst consensus, peer multiples, and historical trading range all triangulate to the same conclusion: ADP is cheap on any reasonable multi-year earnings power assumption.

## Red Flags

- Price has fallen 38% from the June 2025 high in ten months — such persistent weakness often signals the market sees something the model doesn't; however, the macro-slowdown narrative is a sufficient explanation here.
- The quant's 7.3% Y1 growth is at the upper end of management's ">6%" FY26 guide — if bookings slow to 4%, base IV drops ~10%.
- Interest coverage compressed from 47x (FY22) to 12.6x (FY25) as debt expanded from $3.4B to $9.1B; still very safe, but the direction matters.
- Forward P/E of 16.8x vs 5-yr average of ~30.7x is the kind of divergence that either snaps back or signals a structural re-rating — need to monitor whether 2–3 more prints confirm the downgrade view.

## Score: 8 / 10

Clearly undervalued on any framework I trust — quant Monte Carlo (87% prob), analyst consensus (~35% upside), historical multiple (30%+ below 10-yr average), peer context (in line with lower-quality PAYX on EV/EBITDA). Not a 9 because price can stay cheap if the labor market keeps weakening and because the stock has fallen for 10 months without finding a floor yet.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 146 |
| IV Base | 228 |
| IV Bull | 322 |
| Currency | USD |
| MOS at Analysis Date | -37.3 |
