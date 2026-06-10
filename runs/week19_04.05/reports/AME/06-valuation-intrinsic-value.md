# Valuation vs Intrinsic Value — AME

**Analyst Role:** Valuation Analyst
**Date:** 2026-05-06
**Data Sources:** Quant model output (`context/AME/quant-valuation.md`, `quant-valuation.json` — DCF with CAPM WACC, sensitivity grid, 10K-run Monte Carlo, dated 2026-05-06); auto-fetched financials (`context/AME/financials.md` — yfinance, dated 2026-05-06); web searches for analyst price targets (MarketBeat, TipRanks, StockAnalysis), Q1 2026 earnings (Globe and Mail, Motley Fool, Benzinga, Seeking Alpha transcripts), and peer multiples (BeyondSPX, valueinvesting.io, Stern NYU Damodaran tables).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant model bear/base/bull IV is $109 / $165 / $229; current price $238.83 sits above the bull case. | 5 |
| 2 | Monte Carlo P(IV > Price) is 1.3% — the simulation effectively never beats today's price across 10,000 runs. | 5 |
| 3 | Sensitivity grid (5×5 of growth × WACC) tops out at $230 in the most optimistic cell — current price is above every realistic cell. | 4 |
| 4 | AME trades at 36.1x trailing P/E, 27.1x forward P/E, 23.0x EV/EBITDA, and 39.5x P/FCF — the high end of "operational excellence" peers (FTV 12.5x EV/EBITDA, ITW 18.2x, ROP 18.7x). | 5 |
| 5 | Q1 2026 was a record (sales +11%, EPS +13%, organic orders +22%, backlog $3.87B); raised FY26 EPS guide to $7.94–$8.14 — the price already reflects this. | 4 |
| 6 | Sell-side average target is $244–$257; even the high-water target of $280 is only ~17% above today's price, with no analyst target meaningfully ahead of the bull DCF. | 3 |

## Detailed Analysis

**Starting from the quant model.** The deterministic DCF anchors at a base IV of $164.87 with WACC 9.9% (CAPM-derived: Rf 4.5%, beta 1.03, ERP 5.5%, cost of equity 10.2%; net debt is small so debt weight is only 4.1%), Y1 revenue growth of 9.1% fading to 3.0% terminal, an exit multiple of 15x EV/EBITDA, and an operating margin of 25.8%. Bear ($109) compresses growth to 6.1% Y1 and the exit multiple to 12x; bull ($229) stretches growth to 12.1% Y1 and the exit multiple to 18x. Current price of $238.83 prints **above the bull case**, which is rare and demands scrutiny.

**Stress-testing the assumptions.** The base case is, if anything, generous. Operating margin is held flat at the FY25 record level of 25.8%, even though FY22 was 24.4%. The growth fade goes from 9.1% to 3.0% over five years — that's a steady-state growth assumption embedded for a $7.4B revenue industrial that compounds revenue at ~7% over the long cycle (FY22 $6.2B → FY25 $7.4B is ~6.1% CAGR). The 15x exit multiple is roughly today's median for the AMETEK peer group (ROP, FTV, ITW range 12.5x–18.7x), so I would not adjust it materially. The 9.9% WACC is reasonable; a 50bp move either way reprices the base IV by ~$15. Net: I am comfortable with the **base IV at ~$165** and would only adjust the bull case to acknowledge Q1 2026's stronger order book.

**My adjusted scenarios.**
- **Bear ($110, in line with quant):** Growth stalls at 5–6% as defense and aerospace book-to-bill normalizes off the current peak; margin compresses 100–150bp on mix and acquisition integration; multiple compresses to 12x EV/EBITDA. The implied EV/EBITDA at this IV is only 11.1x — fair for a slowing industrial.
- **Base ($165, in line with quant):** AME does what it has historically done — high-single-digit organic growth, margins flat to up, mid-teens EBITDA multiple. This is the centroid of the sensitivity grid (9.1% growth × 9.9% WACC = $177.68; with the mechanically slightly lower base it lands at $165).
- **Bull ($240, slightly above quant's $229):** I would adjust the bull modestly higher to reflect the record Q1 2026 backlog ($3.87B) and the raised FY26 guide ($7.94–$8.14 EPS). If AME holds 12% organic growth two more years and the multiple holds at 18x, you can defend low-$240s. But the implied EV/EBITDA is already 20.5x in the quant bull — there is little room left to move up.

**Multiples in context.** AME's 23.0x EV/EBITDA is at the high end of the operational-excellence cohort. ROP trades at ~19x EV/EBITDA (mostly software now, justifying a richer multiple); FTV at 12.5x; ITW at 18.2x. AME does not have ROP's software mix, and its ROIC of ~12.8% is average for the group, not exceptional. The 36.1x trailing P/E and 39.5x P/FCF are uncomfortable for an industrial growing high single digits — these are software-style multiples on a hardware compounder. Forward P/E of 27.1x is more digestible but still demands the high-single-digit growth to continue uninterrupted.

**Reverse-engineering today's price.** To justify $238.83 in the quant framework, you need approximately **13% revenue growth fading to 3% AND a 18x exit multiple AND WACC at 9.4%** — i.e., the bull case in full. Equivalently, in the sensitivity grid the only cells anywhere near today's price are the bottom-right corner (13.1% growth at low WACC = $211–$230). The market is pricing close to the bull DCF outcome as the **expected** outcome, leaving no room for error.

**Implied expectations vs likely reality.** Monte Carlo P(IV > Price) of **1.3%** is, plainly, a flashing red light. Out of 10,000 simulated parameter combinations the model concludes the stock is undervalued in 130 of them — and the median IV is $176.53, ~26% below the current price. Even the P95 outcome ($223.08) is below today's price. The market is paying for AME's quality and order momentum, not for a margin of safety. Sell-side targets ($244–$257 mean) are clustered just above the current price, suggesting consensus is similarly anchored on Q1 momentum rather than long-term IV.

## Signal Summary

- **Bull case:** Defense/aerospace cycle persists, AME compounds at low double digits for three more years, the multiple stays at 23x EV/EBITDA, and the stock drifts to $260–$280 over 12–18 months in line with sell-side targets — a low-teens return from here.
- **Bear case:** Industrial cycle softens, organic growth reverts to 4–5%, the multiple compresses toward FTV/ITW (15–18x EV/EBITDA), and the stock retraces to $170–$190 — a 20–30% drawdown.
- **Confidence:** **High** — quant model, sensitivity grid, Monte Carlo, peer multiples, and analyst targets all point in the same direction: the stock is trading at or above intrinsic value with no margin of safety.

## Red Flags

- Current price is above **every cell** in the 5×5 sensitivity grid except where you stack the most optimistic growth and the lowest WACC.
- P(IV > Price) of 1.3% is among the lowest readings across the pipeline's coverage — only justifiable if the model inputs are systematically too conservative, which the FY25 baseline financials do not support.
- 23x EV/EBITDA on a 12.8% ROIC industrial is a software-grade multiple on a hardware-grade business.
- Q1 2026's record backlog and order growth are partly defense/aero cyclicality — extrapolating those into the terminal year is exactly the kind of "peak earnings as normal" pitfall the prompt warns against.

## Score: 3 / 10

Quality business, but the price has run well past any defensible IV — base case suggests ~30% downside to fair value and the upside is fully priced in. Modestly to significantly overvalued.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 110 |
| IV Base | 165 |
| IV Bull | 240 |
| Currency | USD |
| MOS at Analysis Date | -117.1 |
