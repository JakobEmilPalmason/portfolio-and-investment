# Valuation vs Intrinsic Value — MSFT

**Analyst Role:** Valuation Analyst
**Date:** 2026-05-11
**Data Sources:**
- `context/MSFT/financials.md` (Yahoo Finance, 2026-05-11)
- `context/MSFT/quant-valuation.md` (deterministic DCF, 2026-05-11)
- Web search: Q3 FY26 results & Azure growth (CNBC, Microsoft IR, Futurum, 2026-04-29/30)
- Web search: Capex revision to $190B CY26 (The Register, Global Data Center Hub, 2026-04-30)
- Web search: AI ROIC debate (InvestorPlace, Bank of America via Fortune, 2026)
- Web search: 10Y Treasury at 4.38% on 2026-05-08 (Federal Reserve H.15)

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant DCF gives Bear $261 / Base $377 / Bull $509 per share; current $409.58 sits between Base and Bull. | 5 |
| 2 | CY2026 capex guide jumped to ~$190B (+61% YoY) vs $64.6B in FY25; $25B of the increase is component-price inflation, not extra capacity. | 5 |
| 3 | Azure grew 40% in CC in Q3 FY26; total revenue +18% to $82.9B; AI run-rate now $37B (+123%). The quant 12.5% Y1 revenue growth is *too low* on the front end. | 4 |
| 4 | Monte Carlo P(IV > Price) = 58% — only modestly favorable; the median MC outcome ($421) is essentially at today's price. | 4 |
| 5 | At $409.58, P/FCF = 82x (TTM). Forward P/E 21.2x is moderate, but FCF is being compressed by the capex tsunami — the market is valuing earnings, not cash. | 4 |
| 6 | Quant model treats only ~50% of capex as maintenance. With $190B going out the door, "growth capex" is now ~$130-150B/year — that has to compound at high ROIC for years for it to be value-creating. | 5 |

## Detailed Analysis

**Starting from the quant anchor.** The deterministic DCF lands at Base $377, Bear $261, Bull $509, using WACC 10.4% (CAPM: Rf 4.5%, beta 1.09, MRP 5.5%, Re 10.5%, after-tax Rd 3.3%, mostly-equity weighting), revenue growth fading from 12.5% → 3.0% over five years, operating margin 45.6%, and a 15x exit EV/EBITDA. The model treats maintenance capex as the D&A proxy (~12% of revenue) and discounts the rest as growth. Net debt is trivial at $12.9B. I think the structure is right, but two assumptions need to be flexed *both* up and down for MSFT today.

**Where I'd flex the growth assumption *up* — at least in the early years.** Q3 FY26 just printed revenue +18% (15% CC) and Azure +40% CC, with the AI run-rate hitting $37B (+123% YoY) and 20M paid Copilot seats. The quant's 12.5% Y1 is a back-mirror number; the live tape is closer to 15–17% near-term. I'd nudge Year 1 growth to 14–15% in my base case. That pushes my Base IV up by roughly $25–35/share, into the $400–410 range — almost exactly where the stock trades. Reading sensitivity grid row 14.5%, column 10.4%: IV is $459. That's my "growth-tilted" base.

**Where I'd flex it *down* — the capex problem.** CY2026 capex is now $190B vs FY25 $64.6B. Even stripping the $25B of component-price inflation, capacity capex is up ~$100B in one year. The quant model implicitly assumes that maintenance % of capex stays ~50%; in reality the "growth capex" line is exploding faster than revenue. That means owner earnings (NI + D&A − maintenance capex) won't track NI for years. FCF margin has already fallen from 32.9% (FY22) to 25.4% (FY25). If 2026 capex lands at $190B and D&A doesn't catch up immediately, FCF could compress further before it rebounds. The bear case ROIC scenario (~8% on incremental AI capex per InvestorPlace and BoA) is survivable but value-destroying at the margin. The bull case (~50% mature ROIC) is plausible but doesn't show up in financials until ~2029–2030. The market is being asked to underwrite faith.

**My adjusted scenarios.** I keep the quant skeleton but adjust:

| | Quant | My adjusted | Reasoning |
|--|------|-------------|-----------|
| Bear IV | $261 | **$280** | Quant bear has 9.5% Y1 growth; I'd hold Y1 at 11% (Azure has demonstrable demand) but assume worse on margin compression as capex flows through D&A. WACC 11.4%. Exit 11x. |
| Base IV | $377 | **$420** | Y1 growth 14.5% (live AI/Azure tape), fade to 3% by Y5, WACC 10.4%, exit 15x. This matches sensitivity grid cell (14.5%, 10.4%) = $459 — I shave $40 for FCF compression risk during capex peak. |
| Bull IV | $509 | **$540** | Y1 15.5%, sustained margin expansion as Copilot monetizes, exit 18x. AI productivity dividends arrive on schedule. |

**What must be true for $409.58 today?** Reading the sensitivity grid, the current price corresponds to roughly 10.5% growth at 9.4% WACC, or 12.5% growth at ~11.0% WACC. Both are plausible. The grid says ~60% of the 25 cells produce IV above current price. That's consistent with the Monte Carlo P(IV > Price) = 58%. Translation: the market is not pricing perfection (that would be the Bull at $509), nor disaster (Bear $261). It's pricing a slightly cautious base case — which is fair given the capex shock.

**Multiples in context.** Trailing P/E 24.4x and Forward P/E 21.2x are *below* MSFT's 10-year average forward P/E (~28x). EV/EBITDA 17x is in line with history. P/FCF at 82x looks awful, but that's the capex-suppressed denominator — once normalized, P/FCF is probably 35–40x. None of these multiples scream "expensive" for a 45% operating-margin, 30% ROIC compounder growing high-teens. They also don't scream "bargain." This is a fair-to-modestly-rich valuation for a uniquely high-quality business.

**Implied expectations vs reality.** At $409.58, the market is pricing roughly 12% revenue growth for five years with stable margins, fading to 3% terminal. The actual run-rate is 18%. The market disconnect is the capex worry: investors are correctly noting that if the $190B doesn't earn its cost of capital, the IV is dragged down by negative incremental ROIC. That's the real swing factor — not Azure's headline growth.

## Signal Summary

- **Bull case:** Azure + Copilot monetization compounds at 25%+ through 2028, capex peaks in CY26-27 then plateaus, FCF margin recovers to 30%+, stock re-rates to bull IV ($540) — that's +32% from here, plus dividends.
- **Bear case:** AI capex is structurally over-built across the industry, MSFT's incremental ROIC compresses to high-single-digits, FCF stays in the 25% margin range for years, multiple de-rates to 18x forward earnings, stock drifts to ~$280 (-32%).
- **Confidence:** Medium — the business quality is exceptional and well understood, but the capex cycle introduces real uncertainty about owner-earnings trajectory for 3-5 years. Quant model is a reasonable anchor; my adjustments are modest, not heroic.

## Red Flags

- $190B CY26 capex is more than the entire FY25 free cash flow — this is the largest single-company infrastructure investment in corporate history and the payback math is unproven at this scale.
- FCF margin has fallen from 32.9% (FY22) to 25.4% (FY25) and is likely to fall further before recovering.
- $110B AI investment commitments and a coincident large employee buyout suggest management itself sees margin pressure ahead.
- Bank of America notes hyperscaler capex now consumes 94% of operating cash flow after dividends/buybacks — MSFT is approaching the limits of self-financing.
- Stock-based compensation $12B (FY25) — a real cost, not adjusted out of FCF here.
- 27% position in 52-week range — the market has been derating the name even as fundamentals improve, suggesting institutional skepticism is real.

## Score: 6 / 10

Fairly valued. Current price sits squarely between my adjusted Base ($420) and Bear ($280), with MC giving 58% probability of undervaluation. Not a bargain, not a trap. The capex unknown is the single most important variable.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 280 |
| IV Base | 420 |
| IV Bull | 540 |
| Currency | USD |
| MOS at Analysis Date | -46.3 |
