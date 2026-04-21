# Valuation vs Intrinsic Value — DSV.CO

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-18
**Data Sources:**
- `context/DSV.CO/financials.md` (yfinance snapshot, 2026-04-18)
- `context/DSV.CO/quant-valuation.md` and `.json` (deterministic DCF, model-dated 2026-03-22)
- Web search: DSV 2025 Annual Report (4 Feb 2026), DSV investor slides FY2025, The Loadstar coverage of Schenker integration, Bernstein/Seeking Alpha analyst commentary, Moody's Nov 2025 credit opinion, Freightos/Xeneta 2026 freight outlook, historical DSV/Panalpina integration reporting.
- Note: 2025 reported figures reflect only ~8 months of Schenker consolidation (deal closed 30 April 2025), so FY2025 margins and multiples are distorted.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant model's bear/base/bull IV range is 1,332 / 2,516 / 3,897 DKK; current price 1,712.50 DKK sits between bear and base — roughly 29% above bear, 32% below base. | 5 |
| 2 | Monte Carlo P(IV > Price) was 100% against a 1,590.50 DKK reference price on 22 March; price has since risen ~7.7% to 1,712.50 but remains well below the P5 MC outcome of 2,362, so probability of undervaluation remains very high under the model's input distributions. | 4 |
| 3 | DSV's own 2026 guidance: EBIT before special items DKK 23.0–25.5B, including ≥DKK 4B incremental Schenker synergies on top of DKK 0.8B captured in 2025. Full DKK 9B run-rate synergies expected in 2027, integration done by end-2026 (pulled forward from 2028). | 5 |
| 4 | Quant model assumes 7.9% operating margin flat for 5 years (current depressed level). If synergies restore margins to ~11% (DSV standalone 2023 level), FY2027 EBIT lands near DSV's DKK 27–30B "exit run-rate" and base IV understates fair value by ~20–30%. | 5 |
| 5 | Analyst 19-broker median target is DKK 2,050 (~20% upside); Bernstein target DKK 1,700 (neutral). Implied: sell-side base case is close to my adjusted base IV of ~DKK 2,250. | 3 |
| 6 | Sensitivity grid: current price 1,712.50 DKK is below every single cell in the 5×5 grid (lowest cell is 2,394 at 16% growth + 12% WACC). Every plausible growth/WACC combination the quant tested implies the stock is cheap. | 4 |

## Detailed Analysis

**Owner earnings baseline.** DSV's owner earnings (net income + D&A − maintenance capex) have averaged DKK 15–16B over 2022–2025 on the pre-Schenker asset base. The quant model uses DKK 14.2B FY2025 OE as its anchor. This is a depressed figure: it reflects Schenker's partial-year contribution at low inherited margins, acquisition financing interest, and restructuring drag. A cleaner look: FY2022 delivered DKK 20.9B in OE at a DKK 235.7B revenue base at 10.7% operating margin — roughly the economic shape DSV is trying to recreate at a larger scale. Normalised OE post-integration, assuming ~11% margin on a DKK 290–320B revenue base (current FY2025 revenue DKK 247.3B reflects partial-year Schenker), should land DKK 24–28B. That figure — not FY2025 — is the right anchor for long-term IV.

**Bear case (I accept, with minor adjustment).** Quant bear IV of DKK 1,332 assumes 17% Y1 growth fading to 3%, 7.9% margin held flat, 11% WACC, 12x exit EV/EBITDA. This scenario roughly describes "synergies disappoint, margins stay at 8%, market derates logistics." It is pessimistic but not implausible — history of logistics roll-ups (Geodis, CEVA) shows many never closed the margin gap to DSV's historic levels. I adjust the bear case modestly *up* to DKK 1,450 to reflect that DSV has actually captured DKK 800M of synergies in year 1 (ahead of plan) and pulled the integration end-date forward two years — the execution risk is materially lower today than it was at deal close. The downside isn't "will they integrate?" anymore; it's "will the logistics cycle cooperate?"

**Base case (I adjust upward).** Quant base IV is DKK 2,516 on 20% Y1 growth fading to 3%, 7.9% margin held flat, 10% WACC, 15x exit EV/EBITDA. The growth schedule is broadly fine — 20% in Y1 captures the annualisation of Schenker's revenue from partial-year 2025 to full-year 2026. But the model's 7.9% margin assumption is the weakness. DSV's 2026 EBIT guidance midpoint DKK 24.25B on a DKK 300B+ revenue base implies ~8.0% margin at mid-integration, and DKK 9B of synergies arriving by 2027 on a ~DKK 24B base implies a run-rate closer to DKK 30B EBIT, or ~10% margin. I believe 9.5–10.5% is the right mid-cycle margin assumption, not 7.9%. At 10% margin with everything else held equal, base IV moves to roughly DKK 2,750–2,850. I'll call my adjusted base DKK 2,250 to stay conservative — blending the quant anchor with a discount for execution risk and cyclical timing — but the raw math of synergy guidance points higher.

**Bull case (I accept but fade).** Quant bull IV of DKK 3,897 needs 23% Y1 growth, 9.5% WACC, 18x exit. The 18x EV/EBITDA exit is aggressive — DSV has historically traded 12–16x through cycles, and peer Kuehne+Nagel currently trades ~8.5x. 18x would price DSV at a premium to pre-Schenker levels, which is hard to defend if the industry is entering a more competitive phase. I cap bull at DKK 3,200, which assumes full DKK 9B synergies captured plus ~2% organic volume growth and a 15–16x exit multiple.

**Multiples reality-check.** Trailing P/E 48.3x is noise (reflects Schenker one-offs). Forward P/E 19.6x is the cleaner read — reasonable for a compounder but not cheap. EV/EBITDA 22.8x looks expensive vs K+N at ~8.5x, but K+N is pure-play forwarding with no post-merger accretion story, while DSV's EBITDA is mid-integration. On 2027 consensus EBIT of DKK 27–30B and assuming EBITDA ~DKK 33–36B, forward EV/EBITDA drops to 13–15x — which is where it should be. P/FCF 16.1x is arguably the most useful multiple: DSV converts well, and 16x on DKK 19B of FCF is priced for moderate growth, not exuberance.

**What's priced in at 1,712.50 DKK?** Reverse-engineering: at DKK 405B market cap and DKK 492B EV, getting to "fair" requires roughly DKK 25–27B of run-rate EBIT within 18–24 months — which is almost exactly management's 2026 guidance. In other words, today's price assumes synergies land on plan but doesn't credit any upside from volume recovery or multiple re-rating. That's not pricing perfection; it's pricing the guided case with zero margin of error.

**Sensitivity and Monte Carlo.** The 5×5 grid (rev growth 16–24% vs WACC 8–12%) produces a minimum IV of DKK 2,394 in the harshest cell. Current price DKK 1,712.50 sits below every cell, meaning any plausible growth-WACC pair in this range implies undervaluation. MC P(IV > Price) of 100% confirms this but is suspiciously tight — the input distributions don't model margin compression, which is the real variable. My broader bear/base/bull span (DKK 1,450–3,200) with margin as the swing factor gives a more honest probability: I'd put P(IV > Price) at ~70–75%, not 100%.

**Bottom line.** Adjusted IV range: DKK 1,450 (bear) / DKK 2,250 (base) / DKK 3,200 (bull). Current price DKK 1,712.50 is 18% above my bear and 24% below my base. The stock is not screaming cheap, but it is priced at roughly management's guided case with clear optionality if synergies overshoot — which, per the 2025 run-rate being ahead of original plan, is the more likely outcome than a stumble.

## Signal Summary

- **Bull case:** Synergies fully landed by 2027, operating margin restored to 10–11%, multiple re-rates to 14–16x EV/EBITDA as market sees clean post-integration DSV; stock compounds to DKK 3,000+ by 2028 (~75% upside).
- **Bear case:** Synergy execution stalls, logistics cycle deteriorates, operating margin stuck at 7–8%, market derates to K+N-like 9x EV/EBITDA; stock drifts to DKK 1,400–1,500 (~15% downside).
- **Confidence:** Medium — quant anchor is directionally useful but relies on the wrong margin input; my adjusted range leans on management guidance, which DSV has a 4-for-4 M&A track record of delivering but still carries execution risk.

## Red Flags

- Quant model holds operating margin flat at the trough level (7.9%), understating the mechanical impact of DKK 9B synergies. IV base of DKK 2,516 should be viewed as a floor for a well-executing case, not the central estimate.
- Terminal value is 80% of base-case enterprise value — a lot of the quant IV is a function of the 3% terminal growth assumption and 15x exit multiple. Small changes there swing IV meaningfully.
- Monte Carlo P(IV > Price) = 100% is too clean. Input distributions don't stress margin recovery failure, which is the real risk. Treat MC as illustrative, not literal.
- Interest expense nearly doubled FY24→FY25 (DKK 2.0B → 3.7B) from acquisition debt — rising rates or a covenant re-test would compress equity value directly.
- Valuation depends on synergy capture; if integration slips meaningfully (precedent: Geodis, XPO restructurings), IV migrates toward bear case fast.

## Score: 7 / 10

Reasonably valued to modestly undervalued with asymmetric upside if synergies land. Not screaming cheap, not priced for perfection. The stock is roughly at "guidance-delivered" fair value, with free optionality if the 2027 synergy run-rate is reached on schedule. A 7 reflects a real but not extraordinary discount to probability-weighted IV, backed by a management team with a four-deal integration track record.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 1450 |
| IV Base | 2250 |
| IV Bull | 3200 |
| Currency | DKK |
| MOS at Analysis Date | -18.1 |
