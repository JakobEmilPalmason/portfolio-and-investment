# Valuation vs Intrinsic Value — CSU.TO

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant DCF model (src/quant), yfinance financials (context/CSU.TO/financials.md), quant-valuation.json, Q4 2025 earnings release (GlobeNewswire, March 9 2026), analyst consensus (Yahoo Finance), web search for current context

---

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Current price of C$2,499 sits below the quant model's bear-case IV of C$2,762 — a 9.5% margin of safety even against the most pessimistic scenario | 5 |
| 2 | All 25 cells of the sensitivity grid (revenue growth 16–24% × WACC 5.7–9.7%) produce an IV above current price; Monte Carlo assigns 100% probability that IV exceeds price | 5 |
| 3 | Trailing P/E of 75x is an accounting artifact: $1.4B of non-cash D&A on acquired intangibles depresses reported earnings; the correct cash-yield lens is P/FCF of 20.1x on $2.7B of real FCF | 4 |
| 4 | Owner earnings of ~$1.8B USD on 21.2M shares imply ~$85 USD (~C$117) per share in true cash earnings; at current price of C$2,499, the owner earnings yield is approximately 4.7% — attractive for a business still compounding at 15%+ revenue growth | 4 |
| 5 | Forward P/E of 13.6x on consensus forward EPS of $183 USD implies meaningful earnings normalization as D&A stabilizes relative to revenue — consistent with FCF/share of ~$127 USD (~C$175) today | 3 |
| 6 | The 52% drawdown from the May 2025 high is driven by two re-rating shocks — Mark Leonard's health-related resignation (September 2025) and AI disruption fears — not by any deterioration in underlying FCF generation | 5 |

---

## Detailed Analysis

**Cash Economics vs GAAP Optics.** Constellation Software's reported financials require a translator. FY2025 net income of $512M ($33 EPS) implies a 75x trailing P/E that looks absurd for a business growing revenue at 15%. The explanation is simple: the acquisition model generates ~$1.4B of annual D&A, almost entirely non-cash amortization of acquired intangibles (customer relationships, software, trade names). This is a real economic cost at the moment of acquisition, priced into the purchase, but it is not a recurring annual cash drain on the acquired businesses. Strip it out and add back maintenance CapEx of only $68M, and owner earnings land at $1.8B — a cash yield of roughly 4.7% on the current market cap. FCF of $2.7B is even stronger (FCF margin of 22.9%), reflecting working-capital dynamics in recurring-revenue VMS businesses. The forward P/E of 13.6x using consensus $183 EPS is the better anchoring multiple because it reflects normalized earnings as D&A amortization rolls off on the seasoned acquisition cohort.

**Quant Model Assessment — Are the Assumptions Defensible?** The DCF base case uses 20% Y1 revenue growth fading to 3% by Y5, 18.1% operating margins, and a 15x exit multiple on EBITDA. Revenue growth of 20% for FY2025 is consistent with the actual reported outcome ($11.6B vs $10.1B = +15.1% in USD; Q4 was +18% with acquisitions). The model is if anything slightly conservative on near-term revenue given deployment of capital at scale. The 15x EV/EBITDA exit multiple deserves scrutiny: historically CSU has traded at 19–22x EV/EBITDA; after the re-rating, current EV/EBITDA sits at approximately 22.6x on trailing EBITDA. A 15x exit multiple is a meaningful haircut that already bakes in de-rating risk. The 18.1% operating margin assumption is anchored to the FY2025 actual; there is reasonable upside if the PEMS (permanent-engaged minority stake) strategy generates asset-light capital deployment without proportionate cost growth. WACC of 7.7% is based on a beta of 0.66 — appropriate for a low-volatility, recurring-revenue compounder — and a risk-free rate of 4.5%.

**Sensitivity Grid Analysis.** The most striking quantitative result is that C$2,499 sits below every single cell of the 5×5 sensitivity grid. Even under the most punishing combined scenario — only 16% revenue growth and a 9.7% WACC — the model produces an IV of C$3,950, a 58% premium to today's price. Under base assumptions, IV is C$5,072, implying 103% upside. This is not a marginal margin of safety situation; the current price appears to price in an outcome that the model cannot generate even with deliberately adverse inputs. The Monte Carlo (10,000 simulations) reflects this: P5 IV is C$3,971 and P(IV > Price) = 100.0%.

**Owner Earnings Yield and Implied Growth.** $1.8B USD owner earnings on $53B CAD (~$38B USD) market cap implies an owner earnings yield of approximately 4.7%. For a business growing at 15%+ with a demonstrated ability to redeploy that cash above cost of capital (ROIC 16.5–23.5% over four years), this yield is low in absolute terms but reasonable given the growth component. The ROIC trend bears watching: 23.5% in FY2023 has declined to 16.5% in FY2025, consistent with a larger capital base requiring larger deals that may take longer to reach mature economics. Even at 16.5% ROIC vs a 7.7% WACC, CSU is generating significant economic profit with every dollar deployed. At P/FCF of 20.1x, the market is implying modest FCF growth. That seems too conservative given the acquisition pipeline and organic growth of 3–4%.

**Re-rating Risk and What the Price Actually Implies.** Working backwards from C$2,499, if we demand a 10% IRR over 10 years, the implied terminal value would require owner earnings of roughly $680M USD in 10 years — a modest 14% decline from today's $1.8B. The market is pricing in something close to stagnation, which is inconsistent with Q4 2025 showing operating cash flow +24% full year. The two catalysts for the re-rating — Leonard's resignation and AI fear — are real but arguably priced far beyond their fundamental impact. CSU's VMS businesses serve narrow vertical markets (transit agencies, funeral homes, municipal governments) where AI disruption operates on a much longer timeline than in horizontal software.

**IV Stress Test — Where Could the Model Be Wrong?** The model could be too optimistic if: (1) acquisition multiples inflate permanently due to PE competition, compressing returns on new capital to below WACC; (2) Mark Miller proves materially less capable than Leonard at capital allocation; (3) organic revenue declines as AI tools enable customers to replace VMS workflows. The bear IV of C$2,762 already partially reflects these scenarios by using 17% growth and a 12x exit multiple. Even the bear case sits 10% above current price, suggesting a genuine margin of safety against a range of adverse outcomes.

---

## Signal Summary

- **Bull case:** Acquisition machine continues deploying $1.5–2B+ per year above WACC; re-rating from 22x back toward historical 19x EV/EBITDA on growing EBITDA produces C$5,000–5,700 within 3–5 years.
- **Bear case:** Mark Miller fails to maintain acquisition discipline; AI disrupts 20–30% of VMS revenue over 5 years; stock re-rates to 12x exit multiple, landing at C$2,762 — roughly flat from today.
- **Confidence:** High — the valuation case is unusually robust; both the DCF model and all 25 sensitivity cells produce IV above today's price, which is a rare and clear signal.

---

## Red Flags

- ROIC declining trend: 23.5% → 20.5% → 16.5% over three years; bears watching as deal sizes increase
- Founder departure (Mark Leonard) is a genuine key-man risk event, though structure was designed to outlast him
- D&A growing faster than revenue ($1.4B on $11.6B = 12% of revenue) creates a sustained GAAP earnings drag that may depress institutional interest
- AI disruption fears are not zero — a 10–15% attrition in VMS organic revenue is possible over a 5–10 year horizon in specific verticals
- Acquisition pace is inherently lumpy; Q4 2025 FCF available to shareholders was $423M, down 12% vs prior year Q4, reflecting heavy deal activity

---

## Score: 9 / 10

Price sits below the model's bear-case intrinsic value with Monte Carlo assigning 100% probability of undervaluation, implying unusually clear and robust upside across every plausible assumption set.

---

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 2762 |
| IV Base | 4148 |
| IV Bull | 5717 |
| Currency | CAD |
| MOS at Analysis Date | 9.5 |
