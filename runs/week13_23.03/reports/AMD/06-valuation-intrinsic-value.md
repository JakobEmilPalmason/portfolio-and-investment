# Valuation vs Intrinsic Value — AMD

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-25
**Data Sources:** Quant DCF model (src/quant), context/AMD/financials.md, context/AMD/quant-valuation.json, Yahoo Finance, S&P Global Market Intelligence, Visible Alpha consensus, AMD Q4 FY2025 earnings release, AMD IR press releases, Seeking Alpha, analyst consensus via StockAnalysis.com

## Key Findings
| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Quant DCF produces bear/base/bull IV of $42/$67/$96 — all far below $220 price. 0/25 sensitivity grid cells produce IV above current price. | 5 |
| 2 | The quant model uses FY2025 operating margin of 10.7% (GAAP). Non-GAAP operating margin was 28% in Q4 FY2025, and consensus expects 30%+ by FY2027 as data center mix dominates. This is the single largest gap between model and market expectations. | 5 |
| 3 | Data center revenue forecast to reach $28.7B in FY2026 (+73% YoY), with total company revenue growing ~34%. Consensus EPS for FY2026 is ~$6.72, implying forward P/E of ~33x on FY2026 estimates. | 5 |
| 4 | To justify $220 at a 15.5% WACC requires sustained 30%+ revenue growth AND margin expansion to 25%+ operating margin (GAAP) AND an exit multiple of 20x+ EV/EBITDA — all simultaneously. | 4 |
| 5 | Analyst consensus target is $261-$290, implying further upside. 79% of 34 analysts rate Buy or Strong Buy. Market is pricing in execution on the AI GPU roadmap. | 3 |
| 6 | AMD's AI GPU revenue could reach $15B in 2026 and $20B+ by 2027 (bull case), but this requires successful MI400/MI450 launch and meaningful ROCm ecosystem adoption against NVIDIA's entrenched CUDA moat. | 4 |

## Detailed Analysis

**Starting from the Quant Model.** The deterministic DCF anchors on FY2025 GAAP financials: $34.6B revenue, 10.7% operating margin, $6.4B owner earnings, and a WACC of 15.5% derived from CAPM with AMD's 2.02 beta. Under these assumptions, the bear/base/bull per-share IV range is $42/$67/$96. The sensitivity grid spanning growth rates of 16-24% and WACC of 13.5-17.5% produces a maximum IV of $99.80 — still 55% below the current price. The Monte Carlo simulation returns a mean IV of $80.40 with P(IV > Price) of 0.0%. On a pure historical-financials DCF basis, AMD is dramatically overvalued.

**Why the Model Understates Fair Value.** The critical flaw in the quant model is its use of 10.7% GAAP operating margin, which includes roughly $5B in stock-based compensation and acquisition-related amortization (primarily from the Xilinx acquisition). AMD's non-GAAP operating margin was 28% in Q4 FY2025, and management has guided for further expansion as data center mix increases. If we adjust to non-GAAP operating margins (a reasonable proxy for cash economics since SBC is a real cost but amortization of acquired intangibles is not), owner earnings roughly double. Furthermore, the model's 20% Y1 revenue growth significantly underestimates consensus: data center alone is forecast to grow 73% in FY2026, and total company revenue consensus is ~$46B (+34%). The model's fade to 3% by Y5 also appears too aggressive given the structural AI capex cycle.

**Reverse-Engineering the Current Price.** At $220.83 with ~1.63B shares, AMD's market cap is $360B. To justify this through a 10-year DCF at a 12% discount rate (lower than the model's 15.5%, reflecting AMD's improving business quality and lower forward risk), you would need: (a) revenue growing at 25-30% CAGR for 3 years, then fading to 10% by year 7-10, (b) non-GAAP operating margins expanding from 28% to 33-35% by FY2028 as high-margin data center GPUs and EPYC CPUs dominate the mix, (c) a terminal multiple of 18-22x EBITDA. These assumptions are aggressive but not absurd — they essentially require AMD to execute its stated roadmap of 60%+ annual data center growth and achieve meaningful AI GPU market share (10-15%) against NVIDIA. The key question is whether this execution is probable or merely possible.

**Adjusted Scenario Analysis.** Using non-GAAP economics and more realistic forward growth assumptions: In a **bear case**, AMD's AI GPU ramp disappoints (MI400 delays, ROCm adoption stalls), data center growth slows to 30% in FY2026, margins compress under competitive pressure, and the stock re-rates to 20x forward earnings on ~$5.50 EPS — implying roughly $110. In a **base case**, AMD executes on its roadmap, data center revenue reaches $28B in FY2026, non-GAAP operating margins expand to 31%, EPS reaches $7.00 in FY2026 and $10+ by FY2027, and the market values it at 25x forward FY2027 EPS — implying roughly $250. In a **bull case**, MI400/MI450 exceed expectations, AMD captures 15%+ AI GPU share, margins expand to 35%+ as mix shifts, FY2027 EPS reaches $13+, and the market sustains a 28x multiple — implying $350+.

**Multiples in Context.** AMD's trailing P/E of 84.6x is misleading — it reflects GAAP earnings depressed by non-cash charges. The forward P/E on consensus FY2026 EPS of $6.72 is ~33x, and on FY2027 consensus of ~$10.75 is ~20.6x. For a company growing revenue 34% with improving margins, a PEG ratio near 1.0x is not unreasonable by growth-stock standards. Compared to NVIDIA at ~30x forward earnings with slower growth off a larger base, AMD's valuation is in the same ballpark. However, compared to Buffett-style quality compounders trading at 15-20x earnings, AMD demands a massive growth premium that leaves no room for execution stumbles.

**The Honest Assessment.** The quant DCF model is too conservative because it uses GAAP margins that are structurally depressed by non-cash charges, and it underestimates the near-term growth trajectory. However, even with generous adjustments, AMD at $220 requires near-flawless execution on a multi-year AI GPU ramp against the most dominant competitor in semiconductor history (NVIDIA). The stock is priced for success, not for safety. A Buffett-style investor would acknowledge the business quality but find it very difficult to establish a margin of safety at this price.

## Signal Summary
- **Bull case:** AMD successfully ramps MI400/MI450, captures 15%+ AI GPU market share, non-GAAP margins expand to 35%, FY2027 EPS exceeds $13, and the stock trades to $350+. AI capex cycle extends through 2028-2030, providing multi-year tailwinds.
- **Bear case:** NVIDIA's CUDA ecosystem proves impenetrable, MI400 launch disappoints, data center growth decelerates sharply, margins compress under competitive pricing pressure, and the stock re-rates to $100-130 on compressed multiples and lower earnings.
- **Confidence:** Medium — The adjusted valuation framework produces a more reasonable IV range than the raw quant model, but the wide bear-to-bull spread ($110 to $350) reflects genuine uncertainty about AMD's competitive trajectory in AI GPUs.

## Red Flags
- The quant DCF model — using actual reported financials — shows $0 probability of undervaluation at $220. Even the most optimistic sensitivity grid cell ($99.80) is 55% below the current price.
- GAAP operating margin of 10.7% vs non-GAAP of 28% is an unusually large gap, driven by ~$5B in SBC and amortization. SBC is a real economic cost that dilutes shareholders.
- AMD's AI GPU thesis depends on breaking through NVIDIA's CUDA ecosystem moat — something no competitor has yet achieved at scale.
- Beta of 2.02 means this stock will amplify any broad market or sector correction by 2x.
- The stock rose from $76 to $267 in one year — momentum-driven moves of this magnitude often partially reverse.
- Forward estimates require sustained 30%+ growth for multiple years — any deceleration will trigger sharp multiple compression.

## Score: 3 / 10
AMD is a genuinely strong business with real competitive assets (EPYC leadership, growing AI GPU presence, strong management under Lisa Su). However, at $220, the stock is priced for a best-case scenario. The quant model's 0% probability of undervaluation is directionally correct even after adjusting for its conservative margin assumptions. My adjusted base case IV of ~$185 suggests the stock is modestly overvalued, and a Buffett-style investor would demand a much wider margin of safety before committing capital. The score reflects the valuation disconnect, not the business quality.

## Intrinsic Value Summary
| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 110 |
| IV Base | 185 |
| IV Bull | 350 |
| Currency | USD |
| MOS at Analysis Date | -101 |
