# Business Economics — ASML

**Analyst Role:** Business Economics Analyst
**Date:** 2026-04-18
**Data Sources:** `context/ASML/financials.md` + `financials.json` (yfinance, 2026-04-18); `context/ASML/quant-valuation.md` (deterministic DCF); ASML Q4 2025 press release (asml.com, 2026-01-28); ASML Q1 2026 press release (asml.com, 2026-04-15); ASML 2030 Financial Strategy page; Futurum Q4 FY2025 earnings review; Investing.com Q1 2026 slide summary. Reporting currency EUR; trading price USD.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | FY2025 revenue EUR 32.7B (+15.5% YoY), operating margin 34.6%, net margin 29.4%, FCF EUR 11.0B — highest absolute profits in company history. | 5 |
| 2 | ROIC 39.5% in FY2025 and has averaged 41.6% over FY2022–FY2025, sustained well above the ~12% CAPM-derived WACC — clear economic-machine territory. | 5 |
| 3 | Gross margin expanded to 52.8% FY2025 from 50.5% in FY2022; management guides 51–53% for FY2026 and 56–60% by 2030 (High-NA cost down-curve + service mix). | 4 |
| 4 | FCF conversion averaged 109% over FY2022/24/25 but collapsed to 41% in FY2023 due to working-capital swings — single-year cash figures are noisy; 3-year averages are the honest read. | 4 |
| 5 | Installed Base Management revenue EUR 2.1B in FY2025 (+8.8% YoY) — roughly 22% of system sales and the most predictable, annuity-like slice of the business. | 3 |
| 6 | Maintenance capex is only ~3% of revenue (EUR ~1.0B of EUR 1.6B total in FY2025); the remainder is growth capex for capacity expansion — the business is asset-light relative to what it ships. | 4 |

## Detailed Analysis

**Returns on capital.** ASML's returns profile is at the very top end of the public universe. ROIC was 42.3% (FY2022), 48.9% (FY2023), 35.6% (FY2024), and 39.5% (FY2025) on an invested-capital base that has nearly doubled from EUR 13.1B to EUR 24.0B over that span. ROE is even more extreme (50.5% FY2025, 70.4% FY2023) because equity is held down by EUR 6B/yr buybacks. The FY2024 ROIC dip is mechanical — invested capital grew ahead of NOPAT as ASML built High-NA manufacturing capacity. The point is that ASML can absorb ~EUR 10B of extra invested capital in two years and still generate ~40% pre-tax-adjusted returns on the base. That only happens when a business has something unique to sell.

**Margin structure and trajectory.** Gross margin stepped up cleanly: 50.5% → 51.3% → 51.3% → 52.8% across FY2022–FY2025. Q4 2025 alone printed 52.2% despite recognizing revenue on two High-NA systems (which carry dilutive initial margins because first-of-kind tools are sold near cost). Operating margin followed the same pattern: 30.7% → 32.8% → 31.9% → 34.6%. The FY2024 softness was explained by Intel's purchase delays and EUR 400M+ of unabsorbed capacity; FY2025 re-leveraged on a 16% revenue lift. Management's 2026 guide (51–53% GM on EUR 36–40B sales) implies slight gross-margin flatness as High-NA ramps further, then a climb toward 56–60% by 2030 as High-NA costs move down the learning curve and service/upgrade mix grows. This is the one line to watch: if 2027 gross margin does not re-expand after High-NA installed base crosses ~20 units, the long-term thesis loses a pillar.

**Cash generation.** FY2025 FCF was EUR 11.0B (33.8% FCF margin, 114.8% of net income). FY2024 was 120%. FY2023 dropped to 41% — this was not an earnings problem but a working-capital normalization as customer down-payments that inflated FY2022 cash unwound. The honest read: ASML's cash generation is genuinely excellent, but working capital is lumpy because customer prepayments on EUR 150M+ EUV/High-NA machines can swing a quarter's operating cash flow by EUR 2–3B. Over any 3-year window FCF ≈ net income. Buybacks accelerated hard in FY2025 to EUR 6.0B vs EUR 0.5B in FY2024 and EUR 1.0B in FY2023 — effectively all of net income beyond the EUR ~2B dividend. Management recently announced a new multi-year buyback program, signaling capital return is the primary use of FCF now that capacity expansion is largely funded.

**Capital intensity and owner earnings.** Total capex was EUR 1.6B in FY2025 (5% of revenue). The quant model decomposes ~63% (EUR 1.03B) as maintenance and EUR 0.6B as growth. That makes ASML genuinely asset-light for a company that ships equipment measured in hundreds of millions of euros per unit — final assembly, test, and integration are done in Veldhoven, but thousands of supply-chain partners (Zeiss, TRUMPF, Cymer, etc.) carry much of the physical capex. Owner earnings (NI + D&A − maintenance capex) were EUR 9.0B in FY2025, or roughly EUR 23/share on a USD basis — the number that matters for long-term compounding.

**Revenue quality and operating leverage.** Three revenue streams: systems (~78% of sales, lumpy and cyclical), installed-base management (service/upgrades, 22%, recurring), and software (small). The backlog stood at EUR 38.8B at YE2025 (1.2× FY2025 sales), with EUV at 65% of backlog and capacity fully booked through 2027 after Q4 net bookings of EUR 13.2B (double consensus). This converts a cyclical equipment business into something closer to a 2-year revenue-visibility compounder. Customer concentration is extreme — TSMC, Samsung, Intel, SK Hynix, Micron, plus a handful of Chinese foundries account for essentially all sales — and 2026 China mix is guided down to ~20% from 33% in 2025, testing revenue resilience. Operating leverage showed up clearly in FY2025: revenue +15.5%, operating income +25.3%, net income +26.9%. As High-NA volumes scale from the current ~4–5 units/yr toward the guided 20+ by 2028, each incremental system should drop more to the bottom line.

## Signal Summary

- **Bull case:** High-NA cost curve works as advertised, service/upgrade revenue compounds at 10%+, gross margin reaches 58% by 2030 on EUR 50B+ revenue — operating income roughly triples to EUR 20B+.
- **Bear case:** AI capex digestion in 2027–2028 + tightened China DUV restrictions cut system sales 20–25% in a down year, gross margin falls to 48–49% on negative mix (more DUV less High-NA), and fixed costs absorb earnings — operating income drops 30–40% in a trough year.
- **Confidence:** High — the underlying engine economics are verifiable from four years of audited financials, multi-year backlog, and public 2030 targets with repeated reaffirmation.

## Red Flags

- **Gross-margin burden from early High-NA units.** First High-NA systems are sold at deliberately compressed margins; until the install base crosses ~15–20 units and learning-curve kicks in, reported GM will be held back. Investors betting on 56–60% in 2030 are implicitly betting on this curve.
- **Working-capital opacity.** FY2023's FCF conversion of 41% shows that a single customer pushback on down payments can distort a full year of cash flow. Not a quality concern, but anyone valuing ASML on single-year FCF is lying to themselves.
- **China mix reset.** Guidance has China dropping from 33% → 20% of sales between 2025 and 2026. If the proposed U.S. DUV restrictions become law, 2027 China could be closer to 10%, and the quality of that replaced revenue (less-mature nodes in other geographies) is not yet proven.
- **Valuation risk is not a business risk, but worth flagging here:** EV/EBITDA 43.8× and P/FCF 69.5× imply the market is already pricing the 2030 bull case. The business is superb; the price expects it to be.

## Score: 9 / 10

A near-peerless economic engine — monopoly EUV pricing power, 40% ROIC on a doubling invested-capital base, 34–35% operating margin, asset-light execution, and EUR 38.8B backlog providing two-year visibility. One notch off a 10 because (a) gross-margin expansion to the 56–60% target depends on an unfinished learning curve, and (b) customer concentration and China exposure introduce real single-year earnings volatility that a true 10-of-10 compounder would not have.
