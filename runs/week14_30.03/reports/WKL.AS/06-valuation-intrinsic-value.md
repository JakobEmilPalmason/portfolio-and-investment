# Valuation vs Intrinsic Value — WKL.AS

**Analyst Role:** Valuation Analyst
**Date:** 2026-04-07
**Data Sources:** Yahoo Finance (yfinance auto-fetch), quant-valuation.json/md (DCF model output), Wolters Kluwer 2025 Full-Year Report (GlobeNewsWire), analyst consensus estimates (14 analysts), peer multiples for RELX and Thomson Reuters (StockAnalysis, Yahoo Finance), web search for recent price action and competitive context.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At €66.24, the stock trades 23% below the quant bear IV of €85.90 and 52% below the base IV of €137.52 — ALL 25 sensitivity grid cells produce IVs above the current price | 5 |
| 2 | Current EV/EBITDA of 9.7x is a 55% discount to its own 5-year average (~20x) and a 30-50% discount to peers RELX (14.2x) and Thomson Reuters (20.2x) | 5 |
| 3 | To justify today's price, the market must be pricing in either a permanent margin collapse to ~15% operating margin or a structural decline in revenue — neither is supported by 2025 results showing 6% organic growth and expanding margins | 5 |
| 4 | Owner earnings of €1.5B on a €14.9B market cap imply a 10% OE yield — extraordinarily high for a business with 24.6% ROIC, 83% recurring revenue, and minimal capex needs | 5 |
| 5 | Monte Carlo simulation returns P(IV > Price) = 100% across all 10,000 runs, with even the P5 percentile at €103.79 — 57% above current price | 4 |
| 6 | The stock has declined 52% in 12 months despite delivering 9% adjusted EPS growth and guiding for continued high single-digit EPS growth in 2026 — this is a market dislocation, not a business deterioration | 4 |

## Detailed Analysis

**Owner Earnings Estimate.** The quant model calculates FY2025 owner earnings at €1.5B (net income €1.3B + D&A €477M - maintenance capex €303M). This is a reasonable baseline. Wolters Kluwer's capex is genuinely low-maintenance in nature — the business is largely software and content, not heavy infrastructure. SBC is trivial at €26M. I would adjust slightly downward by roughly €50M for restructuring costs and currency hedging, arriving at a normalized OE of approximately €1.45B. Looking forward 3-5 years, with 5-6% organic revenue growth and modest margin expansion (management guides for continued margin improvement while investing 12-13% of revenue in product development), normalized OE should reach €1.7-1.9B by 2029-2030. The business has demonstrated consistent OE growth from €1.1B in FY2022 to €1.5B in FY2025, and there is no structural reason this should stop.

**Scenario Analysis.** The quant bear case of €85.90 assumes 0.9% Y1 revenue growth fading to 3.0% with a 12x exit multiple and 6.1% WACC. I find this too conservative on the exit multiple but reasonable on growth. Even a mediocre Wolters Kluwer — one losing market share to AI-native competitors while print revenue accelerates its decline — would still command 12-14x EV/EBITDA given its recurring revenue base and embedded nature. My adjusted bear IV is €80-90, broadly in line with the quant model. The quant base case of €137.52 uses 3.9% Y1 growth, 15x exit multiple, and 5.1% WACC. The growth assumption is slightly below recent performance (6% organic in FY2025) but reasonable as a through-cycle number given the growth-fade schedule. The 15x exit multiple is actually conservative — the business has traded at 16-23x EV/EBITDA for most of the past five years. I would argue for a 16-17x base exit multiple given the quality, which pushes base IV toward €145-155. The quant bull case of €192.98 uses 6.9% Y1 growth, 18x exit, and 5.0% WACC. This is plausible if AI integration drives accelerated adoption and cross-selling. The missing upside optionality is pricing power — Wolters Kluwer's compliance and regulatory content becomes more valuable, not less, as regulatory complexity grows. An adjusted bull IV of €190-210 accounts for this.

**Multiples in Context.** The current 9.7x EV/EBITDA is staggering for a business of this quality. Over the past five years, WKL traded at 16.6x-22.7x EV/EBITDA. Peers RELX and Thomson Reuters currently trade at 14.2x and 20.2x respectively. Even applying a 20% peer discount (for whatever reason the market has punished WKL) would imply 11-16x, still above the current multiple. The trailing P/E of 11.7x and forward P/E of 10.6x for a business growing earnings at high single digits with 24.6% ROIC and 73.5% gross margins is deeply anomalous. The P/FCF of 15.1x, while higher than P/E due to high buyback-driven share count reduction, is still well below reasonable for this quality tier. The implied expectations at 10.6x forward P/E are for a no-growth utility or a business in structural decline — the complete opposite of what the financials show.

**Reverse-Engineering Today's Price.** At €66.24 with €2.2B EBITDA and €18.8B EV, the market assigns roughly 8.5x forward EV/EBITDA (using consensus estimates). Looking at the sensitivity grid, the current price sits below every single cell — the lowest cell (€101.94) assumes -0.1% revenue growth with 7.1% WACC, conditions that would represent a genuine business crisis. For €66.24 to be the correct IV, you would need to assume either: (a) revenues decline 3-5% annually for multiple years while margins compress 500+ bps, or (b) the appropriate exit multiple is 6-7x EV/EBITDA, below commodity chemical companies. Neither assumption is remotely grounded in reality for a business that just grew 6% organically with expanding margins.

**Implied Expectations vs Reality.** The market is pricing in disaster. The 100% Monte Carlo probability of IV exceeding the current price is telling — even with substantial variation in growth, margins, and discount rates, the model cannot generate a scenario where this stock is worth less than €66. The stock has fallen 52% in 12 months while the business improved. The most likely explanation is a combination of broader European equity de-rating, sector rotation out of "boring" compounders, and possibly forced selling or index rebalancing. Whatever the cause, the price-to-fundamental disconnect is extreme.

## Signal Summary

- **Bull case:** At sub-10x EV/EBITDA for a 24% ROIC business growing mid-single digits with 83% recurring revenue, any normalization toward historical or peer multiples delivers 50-100%+ upside over 2-3 years.
- **Bear case:** AI disruption accelerates, enabling low-cost competitors in legal/tax compliance; print revenue decline broadens to digital; or a prolonged European market de-rating keeps multiples compressed indefinitely.
- **Confidence:** High — The valuation disconnect between price and fundamentals is unusually large and well-supported by multiple independent methods (DCF, multiples, peer comparison, OE yield). The business is not broken.

## Red Flags

- Debt/Equity of 618% looks alarming but is an artifact of aggressive buybacks reducing equity to €798M — the actual leverage of 2.2x Debt/EBITDA with 15x interest coverage is comfortable
- Net debt rose from €2.0B to €3.8B over four years, partly funding buybacks — manageable but worth monitoring
- Current ratio of 0.6x indicates negative working capital, though this is normal for subscription-based business models with deferred revenue
- The 52% price decline may reflect information the market has that is not yet public — though the FY2025 results and 2026 guidance were both solid

## Score: 9 / 10

The stock is clearly undervalued by every quantitative measure: 23% below bear IV, 52% below base IV, 100% Monte Carlo probability of undervaluation, trading at half its historical and peer multiples despite improving fundamentals. This is an unusually wide margin between price and intrinsic value for a high-quality, non-cyclical compounder.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 85 |
| IV Base | 148 |
| IV Bull | 200 |
| Currency | EUR |
| MOS at Analysis Date | 22 |
