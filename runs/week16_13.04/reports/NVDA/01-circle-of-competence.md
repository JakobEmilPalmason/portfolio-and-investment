# Circle of Competence — NVDA

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-04-18
**Data Sources:** `context/NVDA/financials.md` (Yahoo Finance, generated 2026-04-18), `context/NVDA/quant-valuation.md`, web search (NVIDIA Q4 FY2026 earnings release, CNBC/Fortune/ServeTheHome Feb 2026 coverage, Rubin roadmap at GTC 2026, company 10-K disclosures on customer concentration). Current price $201.68. No user-provided primary research (10-K notes, transcripts) in context folder.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Data Center is 91% of FY2026 revenue ($197.3B of $215.9B). NVIDIA is now essentially a one-segment company selling AI training/inference systems to a dozen buyers. | 5 |
| 2 | Two direct customers represented ~36% of FY2026 revenue; top six customers ~63% (vs 50% a year earlier). Customer concentration has meaningfully increased. | 5 |
| 3 | Revenue is largely one-off hardware sales (GPUs, systems, networking) rather than recurring subscription — but tied to multi-year hyperscaler capex cycles that are locked in by announced commitments through 2027. | 4 |
| 4 | Jensen Huang confirmed ~$1 trillion in combined Blackwell + Rubin purchase orders through 2027; top-5 hyperscalers each committing $85–200B of 2026 capex, most of which flows through NVIDIA. | 4 |
| 5 | FY2027 Q1 revenue guide of $78B explicitly excludes Data Center compute revenue from China — the core business is now geographically gated by US export policy. | 4 |
| 6 | Gaming, Professional Visualization, and Automotive combined are under 10% of revenue; they remain simple businesses but are no longer material to the thesis. | 2 |

## Detailed Analysis

**What the company sells, and to whom.** NVIDIA sells accelerated computing systems — GPUs, networking gear (NVLink, InfiniBand from the 2019 Mellanox acquisition), and reference server designs — plus the CUDA software stack that programs them. The overwhelming majority of revenue now comes from "AI factories": racks of Blackwell (and soon Rubin) GPUs bought by cloud providers, large internet companies, national-scale AI labs, and sovereign buyers to train and serve AI models. Roughly 90% of FY2026 revenue was Data Center; the old gaming, workstation, and automotive segments together are around $18B of a $216B business. Functionally, NVIDIA is a picks-and-shovels supplier to the AI build-out, bundled with a proprietary software platform that makes the picks worth more than raw silicon.

**How it actually makes money.** The revenue model is one-off hardware sales (though increasingly whole-system sales of 72-GPU "NVL72" or 144-GPU Rubin racks rather than individual chips), captured as equipment revenue when shipped. There is no meaningful subscription or licensing line — CUDA is free, and the margin is embedded in the chip price. FY2026 gross margin was 71.1% and operating margin 60.4% (financials.md), both remarkable for a hardware company, telling you the pricing power comes from the hardware + software bundle, not pure silicon. FCF was $96.7B on $215.9B revenue (45% FCF margin). Owner earnings of $116.9B are similar to net income because growth capex is modest relative to the cash the machine throws off.

**Key drivers.** Four variables dominate the model: (1) **Hyperscaler capex** — Microsoft, Meta, Alphabet, Amazon, and Oracle are the swing voters; Bloomberg/Fortune aggregate their 2026 capex at ~$650–700B, up ~60% year-over-year. (2) **Product cadence** — Blackwell Ultra (GB300) is shipping through 2026, Rubin launches in H2 2026, Rubin Ultra 2027, Feynman on the roadmap for 2028. Each tick roughly doubles performance per watt and resets the upgrade cycle. (3) **Pricing/ASP per system** — selling full racks has pushed ASPs from tens of thousands per GPU to millions per rack. (4) **Export policy to China** — represents $5–50B of annual opportunity depending on licensing regime; currently largely gated, with H200 licensed but not yet shipping revenue per CFO Kress.

**How predictable the revenue is.** For a hardware company dependent on one end-market, the visibility is unusually strong right now because the customers have pre-announced multi-year capex budgets and Huang has quantified backlog at ~$1T through 2027. But this is not recurring revenue — it's a concentrated order book. If hyperscaler capex were to be re-evaluated (which all four majors would face shareholder pressure on if inference economics deteriorate), the order flow could compress meaningfully inside a quarter. The business has the predictability of a multi-year infrastructure build-out, not of a subscription annuity. That distinction matters at 22x revenue.

**Customer concentration.** This is the biggest circle-of-competence concern. The most recent 10-Q disclosure (Q2 FY2026) identified one customer at 23% of revenue and a second at 16% — the top six now ~63% of revenue versus 50% a year ago. Unknown from public filings is exactly which customers these are; media coverage consensus points to Microsoft, Meta, Amazon, Alphabet, Oracle, and CoreWeave in some combination. Each of those buyers is independently building its own silicon (Maia, MTIA, Trainium, TPU, custom ASIC partnerships) — meaning NVIDIA's largest customers are simultaneously its most sophisticated competitive threats. Consumer/enterprise customers are negligible.

**Two-minute explanation test.** NVIDIA makes the GPUs that power AI model training and inference, plus the software (CUDA) that programmers use to write AI code on them. About a dozen giant buyers — the hyperscale cloud companies and a few AI labs — are spending a combined ~$700B this year on data centers, and roughly 90 cents of every dollar of AI accelerator spend lands with NVIDIA. That is a genuinely simple story at the top level, so the business passes the "explain to a teenager" bar. But the underlying complexity — how durable the CUDA moat is against Google's TPU volume lead, how fast custom ASICs erode merchant GPU share, and what happens to the order book if inference margins at the customer level disappoint — is genuinely hard, and those variables are what determine whether the business is worth 15x or 50x forward earnings. The top-level model is simple; the forward trajectory is not.

## Signal Summary

- **Bull case:** AI compute demand continues to outrun supply through 2027, hyperscaler capex holds above $600B per year, Rubin ships on time with a 2x performance jump, CUDA lock-in holds, and revenue compounds from $216B toward Huang's stated $1T Blackwell+Rubin order figure.
- **Bear case:** Hyperscalers materially accelerate custom silicon share (Google TPU, Meta MTIA, Amazon Trainium), inference workloads bifurcate away from merchant GPUs, and China revenue stays gated — order book compresses as customers digest existing capacity, and 60% operating margins prove cyclical rather than structural.
- **Confidence:** Medium — the core business is crystal clear today, but the single-segment, single-end-market concentration makes the forward model harder to underwrite than the current numbers suggest.

## Red Flags

- Customer concentration has risen from ~50% of revenue in top six to ~63% in one year — direction is worsening, not improving.
- 91% of revenue tied to one end-market (AI data center) creates single-cycle exposure; no diversified hedge from gaming/pro-viz/auto anymore.
- China Data Center compute revenue is now excluded from forward guidance — a ~$50B TAM is effectively off-limits pending policy and license uncertainty.
- The company's largest customers are simultaneously funding programs to disintermediate it (Google TPU v7, Meta MTIA, Amazon Trainium 3, Microsoft Maia).

## Score: 8 / 10

The top-level business is unusually easy to describe for a technology company — "sells AI training and inference systems to ~12 buyers, makes ~45 cents of free cash flow per dollar of revenue" — but the extreme customer and end-market concentration, plus the regulatory overhang on China, knock a point off what would otherwise be a 9.

Sources:
- [NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2026](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026)
- [Nvidia smashes Q4 2026 with $68 billion in revenue (Fortune)](https://fortune.com/2026/02/25/nvidia-nvda-earnings-q4-results-jensen-huang/)
- [NVIDIA Q4 FY2026 Earnings: Data Center and ProViz Drive Revenue Records (ServeTheHome)](https://www.servethehome.com/nvidia-reports-q4-fy2026-earnings-data-center-and-proviz-drive-revenue-records/)
- [The $700 Billion AI Bet (LongYield)](https://longyield.substack.com/p/the-700-billion-ai-bet-when-and-how)
- [Nvidia still hasn't sold its U.S.-approved China AI chips (CNBC)](https://www.cnbc.com/2026/02/26/nvidia-china-chip-sales-export-controls-ai-competition.html)
