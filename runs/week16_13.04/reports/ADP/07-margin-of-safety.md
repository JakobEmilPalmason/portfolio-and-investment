# Margin of Safety — ADP

**Analyst Role:** Risk-Reward Analyst
**Date:** 2026-04-19
**Data Sources:** `context/ADP/financials.md` (yfinance 2026-04-19), `context/ADP/quant-valuation.md` + `.json` (DCF 2026-04-18), WebSearch on ADP labor market exposure (CNBC Feb 2026, ADP Research), Q2 FY26 guidance (Seeking Alpha, Motley Fool transcripts), peer sensitivity (StockAnalysis, FinanceCharts).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Price MOS vs quant bear IV ($146) is **-37.3%** (price > bear IV) — there is NO price margin of safety vs the conservative case. | 5 |
| 2 | Monte Carlo P(IV > Price) = 86.8% — probability-weighted price MOS is strongly positive despite the bear-case shortfall. | 5 |
| 3 | Business safety is the principal source of margin: 99%+ recurring revenue, ~92% retention, 24% operating margin trough (COVID), AA-/A+ credit ratings, net debt/EBITDA 0.9x. | 5 |
| 4 | Realistic downside from spot ~$200 to ~$165–175 (10-yr trough P/E at depressed earnings) = ~15% drawdown; realistic upside to base IV $228 + dividend = ~17% + 3.4% yield ≈ 20% — asymmetry is only 1.3x, not the 2–3x Buffett-target. | 4 |
| 5 | Concentration risk is SINGLE-product-category (payroll/HCM) + SINGLE-geography-dominant (~85% US revenue) + regulatory (IRS, state labor departments) — but diversified across ~1 million clients. | 3 |
| 6 | Key tail risk: float income (~$9B client funds held) is sensitive to Fed cuts; each 100 bp decline in short rates ≈ $90M pretax hit ≈ 2% of NI. | 3 |

## Detailed Analysis

**Price margin of safety — mixed.** The quant bear IV of $146 sits 27% below the current $200.47 price. Viewed strictly, that is a NEGATIVE price margin of safety: if the bear scenario plays out (growth fades to 4.3%, exit at 12x EV/EBITDA, WACC 9.7%), you lose ~27%. However, the bear assumptions are unusually harsh — below even ADP's COVID-era growth. The sensitivity grid shows that in 19 of 25 reasonable growth/WACC combinations, IV exceeds the current price. The Monte Carlo P(IV > Price) of 86.8% reflects the same truth: the bear IV is a genuine worst case, not a modal outcome. My read: the real probability-weighted MOS is ~+20% (price $200 vs mean MC IV $242), but you have to be honest that the deep-recession tail is where you lose.

**If I'm wrong about growth by 20%.** The base case uses 7.3% Y1 growth fading to 3%. Cut Y1 growth to 5.3% (bottom of management's guide of >6%, implying real weakness): sensitivity grid shows IV at $220 (center WACC) — still 10% above spot. Cut Y1 growth to 3.3% (matching a severe employment contraction): IV drops to ~$200 — fairly-valued. Only at a sustained sub-3% growth path AND elevated WACC does the stock become a loser. That is a fairly robust setup.

**Business margin of safety — strong, the real reason to own.** This is where ADP earns its keep: revenue is ~99% subscription-based; retention ran 92% pre-COVID and the 80 bp dip in FY25 Employer Services retention is modest; switching costs are punishing (clients re-key employee data, risk payroll errors, retrain HR staff); the client base is ~1 million, with no customer representing >1% of revenue. ADP remained profitable every quarter through 2008–09 AND 2020. Debt/EBITDA is 1.4x — ample headroom. Interest coverage 12.6x is lower than historical but still safe. This business does not go to zero under any realistic scenario short of fraud.

**Downside vs upside asymmetry — adequate, not exceptional.** Realistic downside: another ~15% to $165–175 in a 2008-style scenario, where the 10-yr trough P/E of 23x is applied to ~$8 of trough EPS. The stock has already fallen 38%, so this is incremental, not the full scar. Realistic upside: rerating to ~22–24x on $11 FY27 EPS = $240–265, or to base IV of $228 plus 3.4% yield ≈ 20% total return. Add the 3.4% dividend and over a 3-year hold you likely get +40–50% vs -15% — that is closer to 2.5–3x asymmetry on a multi-year view, which meets the Buffett bar. On a 12-month view, asymmetry is ~1.3x and thin.

**Ways you could be wrong (ranked).**
1. **US private employment contracts for 4+ quarters.** Likely ~25% over 12 months. Impact: -15% on earnings via lower worksite employees and lower bookings. Early warning: 3 consecutive months of sub-50k ADP payroll prints (Feb 2026 print was +22k).
2. **Float income compresses.** Likely ~35% (rate-cut path assumed). Impact: -2% to -5% of NI per 100 bp cut. Early warning: Fed Funds path.
3. **PEO margin compression persists.** Likely ~50% — already happening. Impact: -1% to -2% on blended EBIT margin. Early warning: next 2 quarters of PEO segment disclosure.
4. **HCM technology disruption (Rippling, Deel, Gusto, AI-native entrants).** Likely ~20% over 5 years. Impact: slow erosion of SMB book. Early warning: bookings slowdown below 4% floor.
5. **Major data breach / compliance failure.** Likely <5%. Impact: -30% stock on a bad event. Early warning: none reliable.

**Concentration risks.** ADP is heavily concentrated in US payroll/HCM services (~85% of revenue). Regulatory exposure is real — tax code changes, state-by-state payroll rules, DOL activity. But the 1M+ client base provides natural diversification. No product/customer/supplier goes to zero independently.

**Tail risks — accounting is clean.** No aggressive revenue recognition flags (subscription model with standard rev-rec). No related-party transactions of note. No large goodwill write-down risk (goodwill is a small fraction of assets given organic growth). Interest coverage of 12.6x is down from 47x but still very safe. Short sellers have not flagged ADP in recent memory. The balance sheet (client fund investments of $43B offset by client fund obligations of $41B) is opaque at a glance but standard for a payroll processor.

**What could go to zero?** Essentially nothing short of a catastrophic, irrecoverable breach of the core payroll platform — a scenario with <2% probability over any reasonable horizon. The business has processed US payroll for 75 years.

## Signal Summary

- **Bull case:** Employment stabilizes, multiple rerates to 22–24x on $11–12 of FY27 EPS = $240–280 total return of ~25–40% plus dividends within 18 months.
- **Bear case:** Labor weakens further, earnings flatline, price retests $165–175 (10-yr trough multiple on depressed EPS) = additional ~15% drawdown.
- **Confidence:** Medium-High — quant model, sensitivity, and business quality all align; the single variable I can't control is the macro labor cycle, which is the main risk to the setup.

## Red Flags

- Price MOS vs bear IV is NEGATIVE (-37%) — the margin of safety is in the business, not the price. This matters for sizing.
- Stock has declined for 10 consecutive months without a durable bottom — chart is broken and momentum is unfavorable.
- PEO retention modestly declining; this is the segment most sensitive to SMB health.
- Debt has nearly tripled (FY22 $3.4B → FY25 $9.1B) while float income remains lumpy — not alarming but worth tracking.
- FY26 guidance is good but management has historically been conservative — if they miss their own guide, the multiple can compress further from an already compressed base.

## Score: 7 / 10

Reasonable margin of safety anchored in business strength (A+ balance sheet, 99% recurring revenue, 25%+ margins through the cycle) rather than headline price discount. Monte Carlo 87% favorable and 19 of 25 sensitivity cells above price give real cushion. Not an 8 because the bear IV is below the current price (price MOS is negative in strict terms) and the 1.3x 12-month asymmetry is thin; upgraded to 7 because 3-year asymmetry is closer to 2.5–3x and the business is essentially unbreakable.
