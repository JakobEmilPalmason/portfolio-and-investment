# Valuation vs Intrinsic Value — AZN

**Analyst Role:** Valuation Analyst
**Date:** 2026-03-22
**Data Sources:** Quant DCF model output (bear/base/bull IV, sensitivity grid, Monte Carlo), AstraZeneca FY2025 results announcement, Yahoo Finance valuation statistics, StockAnalysis.com peer data, MarketBeat analyst targets, Pharmaceutical Technology and TipRanks 2026 guidance coverage, DrugPatentWatch Farxiga patent data, CNBC pharma patent cliff analysis

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | At $183.60, price sits between quant base IV ($192.52) and bear IV ($121.30), implying modest upside to base but severe downside to bear — a roughly symmetrical setup | 5 |
| 2 | Monte Carlo P(IV > Price) = 67.4% provides a probability-weighted edge, but the 81-87% terminal value dependence makes this highly sensitive to exit multiple assumptions | 4 |
| 3 | Farxiga ($7.7B, ~13% of revenue) faces generic entry starting late 2026/2027, creating a material near-term revenue headwind not fully captured in steady-state growth models | 5 |
| 4 | Forward P/E of ~20x on 2026 consensus EPS ($7.88 adjusted) is reasonable for a large-cap pharma with mid-single-digit growth, sitting between Novo Nordisk (~11x) and Eli Lilly (~47x) | 3 |
| 5 | Management guides mid-to-high single-digit revenue growth and low double-digit core EPS growth for 2026, which broadly aligns with the quant base case 5.7% growth assumption | 4 |
| 6 | AZN's $80B revenue target by 2030 requires ~6.4% CAGR from FY2025's $58.7B, demanding successful pipeline conversion to offset patent losses — achievable but not assured | 4 |

## Detailed Analysis

**Starting from the quant model.** The DCF produces a base IV of $192.52 at WACC 5.7% and 5.7% revenue growth with a 15x EV/EBITDA exit multiple. This represents roughly 5% upside from the current $183.60 price — hardly a compelling margin. The bear case at $121.30 (WACC 6.7%, growth 2.7%, 12x exit) represents 34% downside, while the bull case at $274.68 (WACC 5.2%, growth 8.7%, 18x exit) implies 50% upside. The asymmetry slightly favors upside, but the bear case is not implausible given the patent cliff overhang.

**Stress-testing growth assumptions.** The base case 5.7% growth rate aligns well with management's 2026 guidance (mid-to-high single digits) and the implied CAGR to the $80B 2030 target (~6.4%). However, this masks a composition challenge: Farxiga's $7.7B in annual sales will begin eroding as generics enter in late 2026/2027. UK courts have already invalidated a key Farxiga patent, and Glenmark has signaled intent to launch. Offsetting this requires Enhertu (40% growth in 2025 to $2.78B AZN share), Imfinzi ($6B+), and new pipeline approvals to fill a multi-billion-dollar hole. The quant model's steady-state growth rate implicitly assumes this replacement happens smoothly — I would apply a 0.5-1.0 percentage point haircut to growth for the next 2-3 years during the transition, then allow acceleration if the pipeline delivers. My adjusted base growth is closer to 4.5-5.0% near-term, reverting to 6%+ by 2028.

**Exit multiple and WACC assessment.** The 15x EV/EBITDA exit multiple for the base case is reasonable for a diversified pharma with strong oncology positioning. AZN currently trades at ~16x EV/EBITDA, and peers range widely: Novo Nordisk at ~8x (post-correction), Eli Lilly at 35x+ (GLP-1 premium), Roche at ~12x, and Merck at ~13x. A 15x exit for a company with AZN's pipeline depth and oncology franchise is neither aggressive nor conservative — it is fair. The WACC of 5.7% using a 0.23 beta is notably low. AZN's true risk profile — patent cliffs, China regulatory exposure, pipeline binary outcomes — arguably warrants a higher discount rate. A beta of 0.23 reflects historical price stability, not fundamental business risk. I would use 6.0-6.5% WACC, which shifts the base IV down to roughly $175-185.

**Sensitivity grid interpretation.** The grid shows the current price of $183.60 sits between the 1.7% growth ($164) and 3.7% growth rows at base WACC 5.7%. This means the market is pricing in approximately 3-4% perpetual growth — a modestly conservative assumption if the pipeline delivers, but arguably fair given patent cliff uncertainty. At my adjusted WACC of 6.5%, the price requires closer to 5-6% growth to be justified, which is more demanding. The grid confirms this is not a screaming bargain but also not grossly overvalued.

**Monte Carlo and probability assessment.** The 67.4% probability that IV exceeds price is encouraging but not decisive. The $31.78 standard deviation (16% of mean) suggests moderate uncertainty. I believe the input distributions may be slightly too narrow on the downside — they likely do not fully weight the tail scenario where Farxiga generics erode faster than expected AND a pipeline drug fails a Phase III. Adding fat tails to the downside would likely reduce P(IV > Price) to the 58-63% range. Still favorable, but not high-conviction.

**What must be true for today's price.** At $183.60, the market is pricing in: (1) successful Farxiga revenue replacement within 2-3 years, (2) continued Enhertu and Imfinzi growth trajectories, (3) no material financial impact from the China investigation, and (4) at least 3-4% long-term growth. These are all plausible outcomes, but none is certain. The market is pricing in a "things go mostly right" scenario — neither pessimism nor optimism. This is a fairly valued stock with option value from the pipeline.

## Signal Summary

- **Bull case:** If the pipeline converts (Enhertu label expansions, new oncology approvals) and Farxiga erosion is gradual, AZN reaches $80B revenue by 2030 and the stock re-rates to $220-275.
- **Bear case:** Farxiga generics hit faster than expected, China investigation escalates with fines or market access restrictions, and 1-2 pipeline setbacks compress growth below 3%, pushing the stock toward $120-150.
- **Confidence:** Medium — The quant model's base case is broadly reasonable, but the patent cliff transition introduces genuine 2-3 year uncertainty that steady-state models underweight.

## Red Flags

- Terminal value constitutes 81-87% of enterprise value — valuation is extremely sensitive to long-term assumptions and exit multiple choice
- Farxiga patent cliff ($7.7B revenue at risk) begins materializing in late 2026, with UK patent already invalidated
- WACC of 5.7% using 0.23 beta likely understates fundamental risk (China, pipeline, patent cliff)
- Forward P/E of 30.8x on trailing earnings looks expensive; on 2026E consensus (~$7.88 adjusted) it moderates to ~23x, but still demands consistent execution
- China investigation remains unresolved with potential for fines, reputational damage, and market access disruption

## Score: 6 / 10

At $183.60, AZN is approximately fairly valued relative to a risk-adjusted base case IV of $175-193; the quant model's 67.4% probability of undervaluation is encouraging but narrows to roughly 55-63% after adjusting for patent cliff risk, higher effective WACC, and China tail risk — not enough conviction for a clear margin of safety.

## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | 130 |
| IV Base | 185 |
| IV Bull | 260 |
| Currency | USD |
| MOS at Analysis Date | -41 |
