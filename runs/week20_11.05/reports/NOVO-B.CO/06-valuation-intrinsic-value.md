# Valuation vs Intrinsic Value — NOVO-B.CO

**Analyst Role:** Valuation Analyst
**Date:** 2026-05-11
**Data Sources:** Quant DCF model (context/NOVO-B.CO/quant-valuation.json, generated 2026-05-11), Yahoo Finance via fetch-financials.py (2026-05-11), Novo Nordisk Q1 2026 earnings release (May 6, 2026 — CNBC, Reuters, GlobeNewswire), KFF/Bloomberg coverage of IRA negotiated price ($274) and Trump MFN deal ($245–350), CMS Medicare price negotiation announcement, FDA April 30, 2026 proposal to exclude semaglutide from 503B compounding bulks list, Eli Lilly Q1 2026 earnings / retatrutide pipeline coverage (Allsci, Biospace), Q4 2025 Lilly investor presentation, prior week15_06.04 NOVO-B.CO analyst report for continuity.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant model returns Bear/Base/Bull IV of DKK 496 / 737 / 1,015 with WACC 6.1% and beta 0.35; current price 300 DKK gives a stated MOS of +39.5% vs. bear and Monte Carlo P(IV > Price) = 100% — but these inputs need to be stress-tested before being accepted | 5 |
| 2 | Q1 2026 results (May 6) reset the narrative: oral Wegovy hit ~2x consensus on pill revenue (DKK 2.26B, 1.3M scripts), Wegovy holds 65% of US new prescriptions, and FY2026 guidance was tightened upward to -4% to -12% (from -5% to -13%) — stock rose 5–7% on the print | 5 |
| 3 | Competitive structure has hardened against Novo: Lilly's tirzepatide (Mounjaro + Zepbound) is now the world's best-selling drug at $24.8B in 9M 2025; retatrutide (triple agonist, ~28.7% weight loss) is on track for 2026 regulatory submission; tirzepatide patents extend into the late 2030s | 5 |
| 4 | US pricing is structurally lower: IRA negotiated $274/month for semaglutide (-71% vs $959 list) effective 2027, with Trump MFN deal layering $245–350/month for GLP-1s starting 2026 — modeling 38–39% terminal operating margin (vs FY2025 41.3%) is now the prudent base case | 4 |
| 5 | Reported FCF collapsed to DKK 29B (FY2025) vs DKK 70B (FY2023) — but DKK 68B of the DKK 90B capex is growth capex (oral GLP-1 + next-gen manufacturing); my judgment-adjusted IV uses owner earnings, not reported FCF, but applies a 30% weight to a "decline scenario" the quant model doesn't price in | 4 |

## Detailed Analysis

**Quant model anchor and why it can't be accepted on its own.** The deterministic DCF in `src/quant` produces a bear/base/bull IV of DKK 496 / 737 / 1,015 with a 100% Monte Carlo probability that intrinsic value exceeds the current 300 DKK. The P5 of the simulation is DKK 594 — still nearly double the current price. Every cell of the 5×5 sensitivity grid (growth 1.5–9.5%, WACC 4.1–8.1%) sits above DKK 576. On paper, this is a screaming buy. But the engine has two structural quirks here. First, it uses a CAPM-derived WACC of 6.1% with a beta of 0.35 — Novo's low beta is a function of the stock historically tracking like a defensive staple, not a signal that its forward cash flows are actually low-risk. Forward risk in this name is dominated by competitive share loss and US pricing — neither of which moves with the equity market. Second, the quant model fades revenue growth from 5.5% to 3.0% over 5 years and holds the operating margin flat at 41.3%. Both assumptions are defensible as a base case but neither reflects the genuine asymmetric risk of a 0–2% growth, 30–35% margin world. I therefore use the quant output as my anchor but adjust both the WACC and the scenario weights.

**My adjusted scenarios (DKK).** I rebuild the three cases with explicit, plainer assumptions, then weight a fourth "decline" case at 30% to capture the GLP-1 commoditization tail:

- **Adjusted Bear (IV ≈ DKK 460):** Use a 7.5% WACC (corresponds to ~0.55 beta — more honest for a name with active US pricing reset and a credible #2 position). Revenue growth fades from 3% to 1% over 5 years. Operating margin compresses to 36% by year 5. Exit multiple 11x EV/EBITDA. This is roughly equivalent to the quant grid cell at 1.5% growth × 7.1% WACC (DKK 603) but with an additional 250–300bp of terminal margin compression, which knocks ~25% off. Result: ~DKK 460.
- **Adjusted Base (IV ≈ DKK 690):** Use a 6.8% WACC (mid-cycle, slightly above the quant model). Revenue growth fades from 5% to 2.5% over 5 years (slower than the quant's 5.5→3%, reflecting tougher Lilly comp). Operating margin fades from 41% to 38%. Exit multiple 14x EV/EBITDA. This lands ~6% below the quant base (DKK 737) and inside the quant grid at 3.5% growth / 7.1% WACC (DKK 664).
- **Adjusted Bull (IV ≈ DKK 950):** I use slightly less than the quant bull because the bull's 8.5% Y1 growth feels stretched against Q1 2026's -4% to -12% guidance even after the upward revision. Use 6% WACC, 7% Y1 growth fading to 3.5%, operating margin holding 40%, exit 17x. ~DKK 950.
- **Adjusted Decline (IV ≈ DKK 240):** This case is the one the quant model does not price. Revenue declines 2% per year for 3 years then stabilizes; operating margin compresses to 30% by year 5 (cheap oral generics, sustained MFN pricing, Lilly takes another 10 points of share); WACC 8%; exit 9x EV/EBITDA. ~DKK 240. This is roughly the current price — and it tells you exactly what the market is pricing.

**Probability-weighted IV.** Applying 25% bear / 35% base / 10% bull / 30% decline:
(0.25 × 460) + (0.35 × 690) + (0.10 × 950) + (0.30 × 240) ≈ DKK 524.
That is my single-number central estimate. The quant model's base case of DKK 737 is 41% higher, which gives you a sense of how much "decline scenario" weight bridges the gap.

**Multiples in context.** At 300 DKK, Novo trades at 10.9x trailing P/E and 8.1x EV/EBITDA. Trailing P/E of ~11x for a business with 36% ROIC, 81% gross margin, and 41% operating margin is, by any historical standard for high-quality pharma, in the low decile. The market has clearly applied a structurally-impaired multiple. The natural counter-question — what would justify it? — points to either (a) ~0% terminal growth plus a 25–30% margin or (b) a permanent re-rating to a small-pharma multiple. Both are plausible, neither is locked in. The Q1 2026 print on May 6 was the first piece of hard data pushing back against (a): pill scripts at 2x estimate and Wegovy holding 65% of US new prescriptions suggest Novo is not losing the volume war the way the price implies, even while it is losing the dollar war on price.

**Reverse-engineering 300 DKK.** Using the sensitivity grid, no cell reaches 300 — the lowest cell at 1.5% growth × 8.1% WACC is DKK 577. To get the DCF down to 300 within the model framework, you need either: (a) flat-to-negative revenue growth for 5+ years combined with margin compression to ~30%, or (b) a WACC above 11%, or (c) an exit multiple below 7x EV/EBITDA. My adjusted decline scenario (DKK 240) reaches that territory by stacking all three of those moves modestly. So the current price is consistent with — but only with — the world where competition AND pricing AND multiple compression all play out simultaneously and stick. That can happen. But it is not the central expectation. The base case probability is materially higher than the decline case probability, which is why even with a 30% weight on decline, the expected IV is well above the spot price.

**Implied expectations vs likely reality.** The Monte Carlo gives 100% probability that IV > price, which sounds too clean — but the distribution is built from the same growth/margin/WACC range used in the model, none of which dip into outright decline. The honest read is: across the universe of "modest growth / modest margin compression" futures, the stock is cheap. The risk that matters is the decline universe — outright share loss to Lilly, oral generics, sustained MFN — which is outside the quant grid. The Q1 2026 reaction (stock +5–7%) suggests the market is no longer in pure-capitulation mode, and the FDA's April 30 proposal to close 503B compounding is a real positive that's worth ~1–2% of revenue uplift over time. Net: the price is pricing in pessimism, my judgment IV (~DKK 525) still gives a 75% upside, and the asymmetry remains favorable — just less overwhelming than the quant model in isolation suggests.

## Signal Summary

- **Bull case:** Q1 2026 confirmed oral Wegovy is expanding the market rather than cannibalizing, capex investments are tracking on schedule, US pricing reset is largely already in the numbers, and CagriSema approval (late 2026) revalidates pipeline depth — stock re-rates toward DKK 600–700 over 2–3 years.
- **Bear case:** Retatrutide files in 2026 with best-in-class data, Lilly consolidates the premium tier, US pricing keeps compressing under MFN, and Novo earns DKK 80–90B net income at a sub-12x multiple — stock stays in the DKK 240–320 range for years.
- **Confidence:** Medium-High — The quant model is directionally correct that the stock is cheap, but the gap between the quant central estimate (737 DKK) and my probability-weighted estimate (525 DKK) is real and reflects honest disagreement on the decline-scenario weight.

## Red Flags

- The quant model's beta of 0.35 / WACC of 6.1% understates competitive-pricing risk; using a more honest 7% WACC alone reduces IV by ~10–12%.
- FY2025 reported FCF of DKK 29B (vs DKK 70B in FY2023) is a real number that screening tools will see — investor narrative depends on capex normalization actually happening in 2027–2029 as guided.
- Operating margin compression risk from MFN pricing (US is ~55–60% of revenue) is not fully reflected in the quant base case's flat 41.3% margin.
- 30% probability weight on a decline scenario (DKK 240 IV) is a judgment call — if reality is even worse (e.g. semaglutide oral generics by 2030), even my adjusted IV is too high.

## Score: 8 / 10

After stress-testing the quant model with a 30% weight on a competitive-decline scenario and using a more honest 7% WACC, my probability-weighted IV is DKK 525 — giving a ~75% upside to the conservative case (DKK 460) and ~130% to the base (DKK 690); the asymmetry is still strongly favorable, the Q1 2026 print added fundamental support, but the score is 8 rather than 9 because the quant model's headline 100% MC probability oversells the certainty.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 460 |
| IV Base | 690 |
| IV Bull | 950 |
| Currency | DKK |
| MOS at Analysis Date | 35 |
