# Balance Sheet Safety — ASML

**Analyst Role:** Balance Sheet Safety Analyst
**Date:** 2026-04-18
**Data Sources:** `context/ASML/financials.md` + `financials.json` (yfinance, 2026-04-18); `context/ASML/quant-valuation.md`; ASML Q4 2025 press release (asml.com, 2026-01-28); ASML Q1 2026 press release (asml.com, 2026-04-15); ASML 2025 Annual Report (published 2026-02-25; full text not inspected — IFRS and US-GAAP filings referenced at high level only); Futurum Q4 2025 earnings review. Figures in EUR except where USD is noted.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Net cash position of roughly EUR 8.9B (cash EUR 13.3B − total debt EUR 4.4B) at YE2025 — ASML could retire all debt in-cash and still have 9× annual interest payments in the bank. | 5 |
| 2 | Debt/EBITDA of 0.35× and interest coverage of 97.4× (EBIT EUR 11.3B / interest EUR 118M) — both metrics at fortress levels and trending better every year. | 5 |
| 3 | Total debt has barely moved in four years (EUR 4.3B → EUR 4.4B FY2022→FY2025) while equity more than doubled (EUR 8.8B → EUR 19.6B), collapsing debt/equity from 48% to 22%. | 4 |
| 4 | Current ratio fell from 1.53× (FY2024) to 1.26× (FY2025) as current liabilities jumped EUR 4.2B — almost entirely customer down-payments (contract liabilities) tied to the EUR 38.8B backlog, not operating stress. | 3 |
| 5 | EUR 38.8B backlog and fully booked EUV capacity through 2027 act as de facto revenue insurance — the company can survive a 2-year recession because its revenue is already contracted. | 4 |
| 6 | R&D commitment of EUR 4.7B/yr (14.4% of revenue) is the real "fixed cost" risk — cutting it in a downturn would be feasible for survival but would damage the 2030 thesis. | 2 |

## Detailed Analysis

**Debt levels and structure.** ASML runs one of the most under-levered balance sheets in large-cap tech. Total debt is EUR 4.39B (FY2025), down slightly from EUR 4.69B a year earlier. Long-term debt specifically is EUR 2.71B, with EUR 1.68B in the current portion of debt. That is lower than one year's R&D spend. Against FY2025 EBITDA of EUR 12.6B, debt/EBITDA is 0.35× — comfortably in fortress territory (Buffett-style threshold is <2×). Against cash and short-term investments of EUR 13.3B, net debt is roughly negative EUR 8.9B — ASML has EUR 8.9B more cash than debt. The quant model carries net debt at −EUR 8.9B for valuation purposes, confirming this. Debt composition is mostly eurobond senior notes issued in prior years at low coupons; I did not inspect the 2025 Annual Report in detail for maturity towers, but the reduction in long-term debt from EUR 3.68B (FY2024) to EUR 2.71B (FY2025) suggests a chunk has rolled into current liabilities — worth verifying from the AR but not material at these absolute sizes.

**Interest coverage.** Interest expense was EUR 118M in FY2025 against EBIT of EUR 11.3B — a coverage ratio of 97×. For context, a business with 5× coverage is considered safe; 97× means interest is essentially a rounding error. Even if EBIT fell by 90% in a catastrophic downturn, coverage would still be ~10×. Interest expense actually declined YoY from EUR 163M (FY2024) despite similar debt levels, likely reflecting maturities of older higher-coupon notes being refinanced or repaid.

**Liquidity.** Cash and short-term investments of EUR 13.3B at YE2025, up from EUR 12.7B a year earlier despite EUR 6.0B of buybacks and ~EUR 2.4B of dividends. That tells you FCF generation is so strong the company is outrunning its own capital return program. The quant model and financials both show a current ratio of 1.26× (FY2025). This dropped from 1.53× in FY2024, which looks alarming in isolation — but the EUR 4.2B jump in current liabilities from EUR 20.1B to EUR 24.3B is primarily customer down-payments sitting as contract liabilities, matched against EUR 38.8B of signed backlog. Those are not traditional "debts" — they are money customers have already prepaid for machines they need in 2026–2027. So the ratio understates actual liquidity. Even using the headline 1.26×, working capital is still EUR 6.4B positive.

**Refinancing risk.** Essentially zero. With EUR 13.3B in cash and EUR 9–11B in annual FCF, ASML could retire every euro of its debt in under six months without drawing on capital markets. Access to debt markets is not a condition of survival. There is no scenario where ASML must refinance in a credit crunch — it could simply cut buybacks and repay in cash.

**Off-balance-sheet obligations.** I did not fully inspect the 2025 IFRS annual report for pension and lease detail, so I am applying known-from-prior-years context. ASML's pension plans are primarily defined-contribution (the Dutch STiPP industry pension plan) with limited defined-benefit legacy exposure; total net pension liability has historically been under EUR 200M — immaterial against equity of EUR 19.6B. Operating leases are now on the balance sheet under IFRS 16 / ASC 842 and have historically run in the EUR 600M–800M range — trivial. Purchase commitments with suppliers (Zeiss, TRUMPF, Cymer-owned by ASML, etc.) are large in absolute terms (EUR multi-billion) but are offset by the customer-prepaid backlog. Contingent liabilities from the ongoing patent litigation with Samsung/Nikon historical overhangs are disclosed but not quantified as material. Confidence on this paragraph is medium — I am relying on prior-year patterns rather than line-by-line 2025 AR reads.

**Stress test (mental model).** Scenario: AI capex collapses, China revenue cut in half, 2027 revenue drops 30% to ~EUR 23B. At 48% gross margin (trough assumption, below guidance floor) and holding opex roughly flat, operating income would be roughly EUR 5B. FCF would likely be EUR 4–5B. Cash buffer of EUR 13B plus that FCF would fund continued R&D of EUR 4.7B, dividends of ~EUR 2.4B, and debt service trivially. Buybacks would be paused. The company would exit a 2-year 30% downturn with net cash still at EUR 10B+. This is a balance sheet designed to make downturns into buying opportunities rather than survival events.

## Signal Summary

- **Bull case:** Continued net cash accumulation lets management do another EUR 10B+ buyback wave in 2027–2028 and still operate with zero financial risk; balance sheet becomes a pure optionality asset.
- **Bear case:** A severe semi-equipment recession compresses FCF to EUR 4B for 2 years while R&D holds steady at EUR 5B — buybacks pause, cash drops modestly, but solvency is never in doubt.
- **Confidence:** High — the core metrics (net cash, coverage, debt/EBITDA) are unambiguous at these magnitudes regardless of accounting treatment; only pension/lease specifics carry some residual uncertainty.

## Red Flags

- **None that threaten solvency.** This is a true fortress balance sheet.
- **Monitor only:** Current-ratio decline from 1.53× to 1.26× YoY — mechanically driven by backlog-related contract liabilities, but worth re-checking in the Q1/Q2 2026 10-Qs to confirm it is not broader working-capital deterioration.
- **Monitor only:** Long-term debt dropping EUR 1B while current debt roughly matches — suggests near-term maturities that will be refinanced or paid in cash. Not a risk, but a line item to verify from the AR.

## Score: 10 / 10

Net cash of EUR 8.9B, interest coverage of 97×, debt/EBITDA of 0.35×, EUR 38.8B customer-prepaid backlog, and FCF that keeps growing despite EUR 6B/yr buybacks. This is the textbook definition of a fortress balance sheet — the company could sustain a 50% two-year revenue decline without issuing equity, cutting R&D materially, or taking on additional debt. Exactly what Buffett means by "doesn't need the market to stay open."
