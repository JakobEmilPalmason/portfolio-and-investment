# Balance Sheet Safety — ITW

**Analyst Role:** Financial Analyst
**Date:** 2026-04-19
**Data Sources:** `context/ITW/financials.md` (yfinance, 2026-04-19), `context/ITW/financials.json`, `context/ITW/quant-valuation.md`, WebSearch (ITW 8-K Feb 2026 credit facility, Moody's A1/positive affirmation March 2025, S&P A+ rating, debt maturity mention from Moody's). FY25 balance sheet data is through Dec 2025. Specific debt maturity ladder (bond-by-bond) was not fully accessible without direct 10-K retrieval, noted below.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Net Debt/EBITDA sits at 1.7x (FY25), within ITW's stated 1.5-2.5x target range and well below any industrial stress threshold. | 4 |
| 2 | Interest coverage is 14.6x (EBIT/interest) in FY25, versus a warning line at 3x — zero short-term stress on debt service. | 5 |
| 3 | Moody's rates ITW A1 (positive outlook, March 2025) and S&P rates it A+ (stable) — the upper end of investment grade, with short-term commercial paper at P-1. | 4 |
| 4 | ITW put in place a fresh $3.0B five-year undrawn revolving credit facility on Feb 20, 2026, providing ample liquidity backstop on top of $851M cash. | 4 |
| 5 | Total debt grew from $8.1B (FY24) to $9.2B (FY25) — the first meaningful debt step-up in several years — and one bond of $998M is listed as maturing in 2026 per Moody's commentary. | 3 |
| 6 | Equity of $3.2B on $16.1B assets looks thin (D/E of 286%) but is a function of decades of buybacks, not operational weakness; the optics overstate actual financial risk. | 2 |

## Detailed Analysis

**Debt levels and structure.** Total debt was $9.2B at year-end FY25, up from $8.1B in FY24. Cash and short-term investments stood at $851M, giving net debt of $8.1B. On $4.7B EBITDA, Net Debt/EBITDA is 1.7x — comfortably below the 2.0x threshold Moody's expects ITW to maintain, and well under the industrial "concerning" level of 4x. Long-term debt is $6.7B of the $9.2B total, implying ~$2.5B in current-portion debt or commercial paper outstanding. Moody's specifically noted "$998 million outstanding of debt maturing in 2026," so roughly a third of current debt is a single 2026 tower; the rest is short-term commercial paper (P-1 rated, so refinancing access is effectively guaranteed in normal markets) and staggered longer-dated notes. I did not retrieve the exact bond-by-bond maturity ladder from the 10-K — that would be needed to verify no bunched maturities beyond 2026, but the company's practice historically has been to ladder issuance across 5-10 year tranches.

**Interest coverage.** Interest expense was $292M in FY25 on EBIT of $4.2B, producing 14.6x coverage. In FY22-FY24 the ratio ranged from 15.4x to 19.9x. Even under a stressed scenario where EBIT drops 40% (to ~$2.5B) and interest expense climbs 50% (to ~$440M, reflecting refi at current rates), coverage would still be 5.7x — firmly in "comfortable" territory. This is the single strongest indicator of survivability: ITW is nowhere close to an interest-service problem.

**Liquidity.** Cash of $851M is a relatively modest balance, but ITW's liquidity thesis rests on access, not hoarding. The new $3.0B undrawn five-year revolver (signed Feb 2026, with an accordion to $5.0B) plus commercial paper access back-stopped by that revolver means the company has ~$3.85B of accessible liquidity against ~$5.1B of current liabilities. Current ratio is 1.2x (FY25) — the lowest of the four-year window (was 1.4x in FY22 and FY24), which deserves noting but is not alarming for a company with CP access and a fresh revolver. Working capital fell from $1.8B (FY22) to $1.1B (FY25), suggesting management is running the business leaner — partly a virtue (capital efficiency) and partly a reduction in cushion.

**Refinancing risk.** The $998M 2026 maturity is the nearest watch-item. ITW's CP program (P-1/A-1 rated) provides almost guaranteed refinancing access at market rates for a company of this quality — short of a 2008-style capital-markets shutdown, the refinancing is a non-event. Cost of debt in the quant model is 3.2% pre-tax, and refinancing at today's rates would likely push it modestly higher, but the impact on interest coverage is immaterial. Beyond 2026, Moody's expects ITW to maintain debt/EBITDA below 2.0x over 12-18 months, which implies management plans measured issuance matched to buybacks and M&A, not a step-up in structural leverage.

**Off-balance-sheet obligations.** I was not able to pull the exact pension-underfunded figure from the FY25 10-K in this session. ITW has historically run well-funded US pension plans (legacy frozen, low benefit growth) and manageable foreign plans; the total pension/OPEB liability has typically been in the $200-400M net-underfunded range, a fraction of a single year's FCF. Operating leases are now capitalized and show up in debt figures post-ASC 842. No material unusual guarantees or contingent liabilities have been flagged in recent analyst reports. I would confirm precise pension numbers before a concentrated position is taken.

**Stress test.** If ITW's revenue dropped 30% for two years — a scenario on the order of the 2008-09 industrial recession, which is more severe than what ITW actually experienced — revenue would fall to ~$11.2B. Even assuming operating margin compresses to 18% (vs. 26% today, which is a heroic stress), operating income would still be ~$2.0B against $292M interest expense, yielding ~7x coverage. FCF in that scenario would be $1.0-1.5B, more than enough to cover the $1.9B dividend+buyback package even after trimming buybacks. The dividend (~$1.85B annualized at the current $6.44/share rate and 288M shares) is the bigger call; management would likely protect it and trim buybacks first. At no point in that stress does ITW approach a survival question — it is a capital-allocation question.

**Equity optics caveat.** Debt/Equity of 286% and book value per share of ~$11 look scary in isolation, but this is entirely a function of 30+ years of buybacks depleting retained earnings. The correct framing: ITW is a cash-generating machine that has returned nearly all of its earnings to shareholders, leaving a thin equity cushion because there's no operational reason to warehouse capital. The negative retained-earnings-after-buybacks mathematics is identical to what you see at Philip Morris, Lockheed, and other mature compounders.

## Signal Summary

- **Bull case:** Moody's upgrades to Aa3 over the next 12-24 months on sustained <2x leverage; ITW continues running ~$8B of net debt as a permanent, cheap capital source while FCF comfortably funds buybacks + dividend.
- **Bear case:** A 2026-27 credit stress event coincides with the $998M 2026 maturity, forcing refinancing at 150-200 bps wider spreads and dragging interest coverage toward 9-10x (still safe, but margin compression visible) while management cuts buybacks to preserve the dividend streak.
- **Confidence:** High — debt ratios, ratings, and recent credit-facility action are all well-documented; only pension specifics and the exact maturity ladder require 10-K verification for the final 5% of confidence.

## Red Flags

- **Debt stepped up ~14% in FY25** ($8.1B → $9.2B) — first meaningful increase in years. Worth understanding whether this funded M&A, an opportunistic issuance, or a funding gap from buybacks exceeding FCF. The FY25 buyback of $1.5B + dividend of ~$1.8B = ~$3.3B in shareholder return vs. $2.7B FCF means ~$600M was debt-funded.
- **Current ratio at a 4-year low (1.2x)** driven by current liabilities rising ~19% YoY (to $5.1B). Benign reading: CP rolling in the short-term bucket. Requires verification.
- **$998M 2026 maturity** is the largest near-term refinancing — a known, manageable item, but worth tracking if credit markets tighten.
- **Pension specifics not verified** in this review; no evidence of a problem, but not confirmed.

## Score: 8 / 10

Fortress-adjacent but not fortress. A1/A+ rated, 1.7x net leverage, 14.6x interest coverage, and a fresh $3B undrawn revolver make ITW extremely safe through any normal industrial cycle. It does not earn a 9-10 because (a) it carries real net debt ($8.1B) rather than a net cash position, (b) equity cushion is thin on an optical basis, and (c) there's a mid-size 2026 refinancing to clear — none of these are actual threats, but they prevent the "could survive anything without breaking a sweat" label.

Sources:
- [Illinois Tool Works Inc 8-K New Agreement Feb 2026 - $3.0B Credit Facility](https://last10k.com/sec-filings/itw/0000049826-25-000009.htm)
- [Illinois Tool Works sets new $3B credit facility - stocktitan.net](https://www.stocktitan.net/sec-filings/ITW/8-k-illinois-tool-works-inc-reports-material-event-511bc85de8c0.html)
- [Moody's affirms Illinois Tool Works' A1 rating, outlook now positive - Investing.com](https://www.investing.com/news/stock-market-news/moodys-affirms-illinois-tool-works-a1-rating-outlook-now-positive-93CH-3953333)
- [S&P Global Ratings affirms Illinois Tool Works at "A+"; outlook stable - cbonds](https://cbonds.com/news/2642439/)
- [ITW Reports Fourth Quarter and Full Year 2025 Results](https://investor.itw.com/news-and-events/news/news-details/2026/ITW-Reports-Fourth-Quarter-and-Full-Year-2025-Results/default.aspx)
