# Business Economics — AME

**Analyst Role:** Financial Analyst Agent
**Date:** 2026-05-06
**Data Sources:** `context/AME/financials.md` (yfinance, FY2022-FY2025); `context/AME/quant-valuation.md` (deterministic DCF, owner earnings, sensitivity); WebSearch — AMETEK Q1 2026 earnings press release and call transcript (StockTitan, Motley Fool, Benzinga, IndexBox), Stockstory and StockAnalysis.com ROIC histories, Paragon Medical (closed Dec 2023, ~$1.9B) and Indicor Instrumentation (announced May 2026, ~$5.0B) deal coverage, AMETEK 10-K (Feb 2025) for goodwill/intangibles. Numbers tagged "FY2025" come from yfinance and may differ from GAAP-as-reported by small amounts due to mapping.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Operating margin has expanded from 24.4% (FY2022) to 25.8% (FY2025) and Q1 2026 hit 26.7% (core 27.9%, +160 bps YoY), evidencing genuine operating leverage and pricing power. | 5 |
| 2 | Free cash flow conversion (FCF / net income) has run 112-124% over FY2023-FY2025, well above the 80% "healthy" benchmark — owner earnings of ~$1.8B in FY2025 are real cash, not accounting profit. | 5 |
| 3 | Capex is just ~1.8% of revenue (~$130M on $7.4B), and yfinance owner-earnings model classifies 100% as maintenance — this is an asset-light specialty industrial, very low reinvestment needed to defend the base. | 4 |
| 4 | ROIC sits at ~12-13% on a GAAP invested-capital base — solid, but goodwill+intangibles are 72% of total assets ($10.5B at YE2024), so cash-on-cash returns on the underlying operating assets are far higher than the headline number suggests. | 4 |
| 5 | Q1 2026 orders were +23.3% YoY to $2.22B with a record $3.87B backlog — organic order momentum, not just acquisition revenue, is accelerating. | 4 |
| 6 | Revenue mix is heavy on aftermarket / consumables / spare parts within a "razor-and-blade" niche-instruments model — supports recurring revenue and the consistently high gross/operating margins. | 4 |

## Detailed Analysis

**Returns on capital.** AMETEK's GAAP ROIC has been remarkably stable at ~12.4-12.8% across FY2022-FY2025, and ROE has held in a 14.6-16.2% band. These are good-not-great numbers in absolute terms — Buffett's favorite businesses tend to land in the 20%+ ROIC zone. The catch with AMETEK is that its invested capital base is dominated by goodwill and intangibles from a 30-year acquisition program: $10.5B of goodwill + intangibles at YE2024, or 72% of total assets. If you ran the calculation on tangible operating capital only (PP&E + net working capital), cash-on-cash returns are extremely high — the businesses themselves are excellent. The 12% headline reflects a price paid for serial acquisitions, not a weak operating engine. ROIC has been flat-to-slightly-rising even as the company has compounded acquisitions on top of the base, which is the right pattern.

**Margin structure.** Gross margin has stepped from 34.9% (FY2022) to 36.0% (FY2025), operating margin from 24.4% to 25.8%, and EBITDA margin from 29.8% to 31.1%. The Q1 2026 print accelerated this further: 26.7% reported / 27.9% core operating margin, +160 bps YoY. EIG (Electronic Instruments Group) Q4 2025 core margin hit 32.3% and EMG (Electromechanical Group) hit 22.7% (+240 bps YoY) — both segments are expanding margin simultaneously, which rules out the "one cyclical lever" explanation. The margin trajectory is the single strongest evidence of pricing power and operating leverage in this dataset.

**Cash generation and owner earnings.** FCF conversion at AMETEK is unusually clean. FY2023 = 121.8%, FY2024 = 123.7%, FY2025 = 112.9%. Net income converts to more than 100% cash because depreciation runs well above capex (~$420M D&A vs $130M capex). The quant model's owner-earnings calc — net income + D&A − maintenance capex — yields $1.8B in FY2025, comfortably above reported net income of $1.5B. Stock-based compensation is tiny at ~$48M (~3% of net income), so dilution is negligible. Buybacks ran $434M in FY2025, real return-of-capital backed by real cash. There is no "adjusted EBITDA" gimmick distorting these numbers — GAAP cash flow lines tell a clean story.

**Capital intensity.** Capex of ~$130M on $7.4B revenue = 1.8% of sales. The owner-earnings model in `quant-valuation.md` classifies 100% of capex as maintenance, which is consistent with AMETEK's "buy-and-improve" model rather than greenfield construction. The growth in this business comes from (a) organic price + volume in niche instrument markets where AMETEK is #1 or #2, and (b) bolt-on acquisitions funded from FCF + debt. Tangible PP&E is a minor fraction of the balance sheet. This is genuinely an asset-light specialty industrial — closer to a Roper Technologies model than a traditional capex-heavy industrial.

**Revenue quality and operating leverage.** AMETEK markets itself on a "Four Growth Strategies" framework with explicit aftermarket / consumables / services / spare-parts revenue inside both segments. While the company doesn't break out a recurring-revenue % publicly, third-party analysis and management commentary cite "substantial recurring revenue from consumables, services, and aftermarket support." Q1 2026 organic sales +5%, +4% from acquisitions, +2% FX = 11% headline; backlog at $3.87B (record) provides ~6 months forward visibility. Operating leverage is visible in the data: revenue grew 7.2% from FY2024 to FY2025, but operating income grew 5.6% and EBITDA grew 4.5% (slightly weaker, possibly Paragon Medical mix-drag in early integration); Q1 2026 reverses that with EBITDA / op-income growing notably faster than revenue. Over the multi-year window FY2022-FY2025, op income grew from $1.5B to $1.9B (+27%) on revenue growth of $6.2B to $7.4B (+19%) — clear positive leverage.

**Acquisition treadmill — economic reality check.** A common pitfall with serial acquirers is that high reported margins disguise capital being shoveled into goodwill that doesn't earn its cost of capital. The Indicor Instrumentation deal announced May 6, 2026 ($5.0B for ~$1.1B revenue = ~4.5x sales) and Paragon Medical (Dec 2023, $1.9B for ~$500M revenue = ~3.8x sales, ~15.2x EBITDA per Scope Research) sit at the high end of multiples paid for industrial businesses. Investors should watch whether ROIC trends down post-Indicor close (expected H2 2026) — if it stays at 12-13%, the engine is fine; if it drops below 10%, the acquisition pace has gotten ahead of value-creation discipline.

## Signal Summary

- **Bull case:** Stable 12-13% ROIC + expanding 26%+ operating margins + 100%+ FCF conversion + accelerating organic orders compound at 8-10% per share for the next 5+ years.
- **Bear case:** Indicor at $5B + future M&A appetite drags ROIC below 10% and turns AMETEK into a capital-allocation story rather than a quality business; goodwill impairment risk in a recession.
- **Confidence:** High — the multi-year financial pattern (margins, FCF conversion, owner earnings, capex intensity) is unusually consistent and corroborated by Q1 2026 results.

## Red Flags

- Goodwill + intangibles at 72% of total assets ($10.5B at YE2024) — large impairment risk if any acquired business deteriorates materially; ROIC denominator is heavily inflated by acquisition prices paid.
- Indicor deal at ~$5B (announced May 6, 2026) to be funded by credit facility + new debt issuance — this is a step-change in leverage from the current 1.0x debt/EBITDA and will pressure near-term ROIC until synergies materialize.
- ROIC has been flat at 12-13% for 4 years rather than expanding — modest evidence the M&A program is "treading water" on returns even as margins climb.

## Score: 8 / 10

A genuinely high-quality economic engine: 26%+ operating margins, 100%+ FCF conversion, ~2% capex intensity, expanding margins across both segments, and accelerating organic orders. The only thing keeping this from a 9 is the GAAP ROIC stuck at 12-13% (a function of acquisition prices paid, not operating quality) and the risk that the just-announced $5B Indicor deal pushes the model further into "compounder by acquisition" territory rather than pure organic value creation.
