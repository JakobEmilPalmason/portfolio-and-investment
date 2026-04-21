# Margin of Safety — ASML

**Analyst Role:** Risk-Reward Analyst
**Date:** 2026-04-18
**Data Sources:** `context/ASML/financials.md`, `context/ASML/quant-valuation.md`, `context/ASML/quant-valuation.json`. Web search: CNBC/IndexBox on April 2026 MATCH Act (proposed US law restricting ASML DUV China sales), ASML Q1 2026 earnings (China mix fell from 36% in Q4-25 to 19% in Q1-26), Bloomberg on China rare-earths curbs impact on ASML, semiconductor cyclicality analysis (Sasfin, 2022 SOX -50% drawdown). Umbrella 06 IV anchor: bear $500 / base $750 / bull $1,000 (USD, current price $1,459.80).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Price margin of safety is deeply negative: current price ($1,459.80) is 192% above my bear IV ($500), 95% above my base IV ($750), and 46% above my bull IV ($1,000). No price margin exists. | 5 |
| 2 | Monte Carlo P(IV > Price) = 0.0% over 10,000 simulations; P95 IV of $972.83 still 33% below current quote — statistically, the stock is overvalued under every scenario the model considered. | 5 |
| 3 | Sensitivity grid maxes at $997 IV in its most aggressive corner (22.8% growth, 10% WACC) — zero cells in the 25-cell grid exceed current price. | 5 |
| 4 | Business margin of safety is strong: 100% EUV monopoly, €38.8B backlog, EUV capacity booked through 2027, 50% ROE, 39% ROIC, net cash position (-$8.9B net debt), 97x interest coverage. | 5 |
| 5 | Concentration risk is real: three customers (TSMC, Samsung, Intel, SK Hynix) drive most bookings; China exposure compressed from 36% → 19% of sales in one quarter on export controls; single-product category (lithography). | 4 |
| 6 | Historical cyclicality: ASML stock dropped ~50% in 2022 alongside the SOX, and ~45% in the October 2024–April 2025 trough (from $1,047 → $608). Volatility reality is severe even when fundamentals remain intact. | 4 |

## Detailed Analysis

**Price margin of safety.** There is none. The current price of $1,459.80 exceeds my bear IV by 192%, my base IV by 95%, and my bull IV by 46%. Quant-model numbers are even harsher: bear IV $464 (-215% MOS), base IV $665 (-119%), bull IV $893 (-63%). The sensitivity grid sweeps revenue growth from 14.8% to 22.8% against WACC from 10% to 14% — 25 cells in total, the most optimistic of which ($997.46 at 22.8% growth, 10% WACC) still sits 32% below current price. The Monte Carlo simulation ran 10,000 paths across reasonable input distributions and not a single run produced an IV above $1,459.80. P(IV > Price) = 0.0%. If I'm wrong about growth by even +40% relative to base assumptions, I still do not make money from here.

**Business margin of safety — genuinely strong.** This is where ASML earns its quality reputation:
- Only EUV supplier globally; no competitor within 5–10 years on high-NA
- €38.8B backlog representing ~1.2x FY2025 sales
- EUV capacity sold through 2027; High-NA tools (EXE:5200B) shipping
- 50% ROE, 39.5% ROIC — one of the highest-quality capital compounders in global industrials
- Fortress balance sheet: $13.3B cash, $4.4B debt, net cash position, 97x interest coverage
- 52.8% gross margin, 34.6% operating margin — pricing power evident
- FY2025 FCF $11B, buybacks $6B — returning capital while growing

But a great business at a bad price is not a margin of safety — it's a *partial* cushion that may allow you to recover over time, not protect you from a 40–50% drawdown when the cycle turns or the multiple compresses.

**Downside vs upside asymmetry — unfavorable.** At my base IV of $750, downside to fair value is ~49% ($709/share of price impairment). Upside to my bull IV of $1,000 is *negative* from here (price already above bull). To get to $1,994 (Street high target), requires everything to go right. Realistic 3-year asymmetry is roughly 40% downside to $850 area (12–15% compression back toward historical multiple) versus 10–20% upside if the 2030 €60B guide pulls forward and multiples sustain. Downside exceeds upside by 2x — the opposite of what you want.

**What could go to zero?** ASML itself going to zero is extremely unlikely — the moat, balance sheet, and customer dependency make permanent capital impairment implausible. What is *very* plausible: 40–50% drawdown over 12–24 months if (a) semi-cycle turns, (b) China DUV revenue is cut entirely, (c) High-NA ramp delays disappoint, (d) rates stay higher-for-longer compressing the premium multiple.

**Five key risks:**
1. **MATCH Act / US-China export controls (high likelihood, medium-severity, happening now):** US Congress introduced the MATCH Act in April 2026 proposing to cut ASML's DUV China sales entirely. Q1 2026 China mix already compressed from 36% to 19%. If DUV to China is banned, ~10% EPS hit per sell-side models. Early warning: MATCH Act passage or expansion of Dutch/US controls.
2. **Semiconductor capex cycle downturn (medium likelihood 2027–29, high severity):** ASML revenue historically tracks industry capex; a 20–30% revenue decline in one cycle is common (2019, 2023 short cycle). A cyclical trough combined with multiple compression = 40–50% drawdown precedent. Early warning: foundry / memory capex guides rolling down.
3. **High-NA ramp disappointment (medium likelihood, medium-severity):** High-NA EXE:5200B is shipping but economics, tool uptime, and customer adoption pace are still uncertain. A 1–2 year slip in ramp would meaningfully delay the 2030 guide. Early warning: customer delays, yield issues, pricing pressure.
4. **Multiple compression on rates or sentiment (medium likelihood, high-severity):** At 30.5x forward P/E and 43.8x EV/EBITDA, any compression toward historical 22–25x fwd = 20–35% price impairment even with fundamentals intact.
5. **Concentration on 3–4 customers (persistent low likelihood, high-severity if occurs):** TSMC, Samsung, Intel, SK Hynix represent the bulk of bookings. A TSMC slowdown alone would cause a double-digit revenue hit.

**Tail risks:** Taiwan geopolitical event (could disrupt TSMC, ASML's largest customer); rare-earths / materials disruption from China (per Bloomberg Oct 2025 coverage); regulatory escalation forcing ASML to geographically fragment production.

**Accounting:** No red flags identified. Revenue recognition is conservative (deferred revenue strong). FCF conversion of 115% in FY2025 supports earnings quality. No related-party issues.

## Signal Summary

- **Bull case:** Business quality carries the investment through multiple compression; 2030 €60B guide pulls forward; stock grinds sideways for 2–3 years then compounds at 10%+ from a flatter base.
- **Bear case:** MATCH Act + cyclical downturn + High-NA delay combine 2026–2028 for a 40–50% drawdown ($730–$875 range), matching the 2022 and 2024–25 precedents.
- **Confidence:** High — the numbers speak for themselves: 0% Monte Carlo probability, entire sensitivity grid under current price, -192% MOS vs my bear IV. This is not a close call.

## Red Flags

- MOS deeply negative across all three quant scenarios (bear/base/bull) and all three of my adjusted scenarios.
- Monte Carlo P(IV > Price) = 0.0% — not a close call statistically.
- Stock is +139.8% from 52-week low ($608), 91% of 52-week range — sentiment/momentum peaks historically precede the deepest drawdowns.
- China mix compressed 36% → 19% in one quarter; MATCH Act would remove ~10% EPS — and this is before it has passed.
- Terminal value 76–84% of EV in DCF — valuation sensitive to small terminal assumption changes.

## Score: 2 / 10

Great business + no price margin of safety = low score. Even though ASML provides a strong *business* margin (monopoly, balance sheet, ROIC), the price margin is deeply negative and downside/upside asymmetry is inverted. A fragile thesis at this price.
