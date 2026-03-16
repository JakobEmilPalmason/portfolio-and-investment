# Circle of Competence — NVDA

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-03-06
**Data Sources:** Web search results (March 2026) for NVIDIA FY2026 earnings, revenue segmentation, customer concentration filings, competitive landscape, China export restrictions, and margin data. Sources include NVIDIA investor relations press releases, CNBC, Tom's Hardware, Motley Fool, Statista, ServeTheHome, Data Center Dynamics, and Shacknews. No user-provided context files. Training knowledge used to supplement understanding of semiconductor industry dynamics.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Data Center accounted for ~90% of NVIDIA's $215.9B FY2026 revenue ($193.7B), making this essentially a one-segment business despite having four reporting segments. | 5 |
| 2 | Four direct customers accounted for 61% of Q3 FY2026 revenue (up from 36% a year earlier), indicating extreme and worsening customer concentration. | 5 |
| 3 | NVIDIA is a fabless chip designer — it designs GPUs and AI accelerators but outsources all manufacturing to TSMC, creating a critical single-supplier dependency. | 4 |
| 4 | The CUDA software ecosystem (5M+ developers, ~20 years of investment) creates high switching costs and is widely considered NVIDIA's primary competitive moat. | 5 |
| 5 | Full-year FY2026 gross margin was 71.1% (GAAP), with Q4 reaching 75.0%, reflecting extraordinary pricing power in AI accelerators. | 4 |
| 6 | China export restrictions caused a $4.5B inventory charge in Q1 FY2026 and NVIDIA is not assuming any Data Center compute revenue from China in its FY2027 Q1 outlook. | 3 |

## Detailed Analysis

**What does NVIDIA sell, and to whom?** NVIDIA designs and sells graphics processing units (GPUs) and accelerated computing platforms. The core product today is data center AI accelerators — the Blackwell (B200/GB200) and predecessor Hopper (H100/H200) GPU systems — sold to hyperscale cloud providers (Amazon, Microsoft, Google, Meta), enterprise customers, and sovereign AI projects. It also sells gaming GPUs (GeForce), professional visualization GPUs (Quadro/RTX), automotive computing platforms (DRIVE), and networking equipment (acquired via Mellanox). The company does not manufacture its own chips; it designs them and outsources fabrication to TSMC. In FY2026, the Data Center segment generated $193.7 billion (90% of revenue), Gaming $16.0 billion (7.4%), Professional Visualization $3.2 billion (1.5%), and Automotive $2.4 billion (1.1%). This is, for practical purposes, an AI accelerator company with legacy side businesses.

**How does it actually make money?** NVIDIA's revenue model is hardware product sales — it designs chips and systems, has them manufactured, then sells them (largely through OEM/ODM partners like Foxconn and Quanta) to end customers. There is no meaningful subscription or recurring revenue component, though NVIDIA has been building software and services offerings (NVIDIA AI Enterprise, DGX Cloud). The vast majority of revenue is one-time hardware sales of GPU accelerators and networking equipment. Gross margins of 71-75% are extraordinary for a hardware business and reflect both the premium pricing NVIDIA commands due to limited competition and the fact that it is fabless (no factory capex). Operating margins are similarly strong, as R&D is the primary cost. Revenue recognition happens at the point of sale, not over time.

**What are the key drivers?** The 2-4 variables that matter most are: (1) Hyperscaler capital expenditure on AI infrastructure — Goldman Sachs projects $1.15 trillion in cumulative hyperscaler capex from 2025-2027, and NVIDIA captures a large share of this spend. (2) NVIDIA's product cycle execution — the cadence of new GPU architectures (Blackwell now, Rubin next) and whether each generation delivers sufficient performance gains to drive upgrade cycles. (3) Competitive dynamics — whether AMD (MI455/MI500), custom silicon from Google (TPU), Amazon (Trainium), Microsoft (Maia), and others erode NVIDIA's >80% market share. Custom ASIC shipments are projected to grow 44.6% in 2026 vs. 16.1% for GPUs. (4) China/regulatory risk — export restrictions have already eliminated a significant revenue stream (China was 13% of FY2025 revenue, now effectively zero in guidance).

**How predictable is the revenue?** This is a weakness. NVIDIA's revenue is not recurring or contract-based in the traditional sense. It depends on large, lumpy capital expenditure decisions by a handful of hyperscalers. There is some forward visibility — CFO Colette Kress noted $500 billion in Blackwell/Rubin revenue visibility from early 2025 through end of 2026, and supply commitments nearly doubled to $95.2 billion. But this is a capex-driven business, not a subscription business. If hyperscaler AI spending slows, decelerates, or shifts to custom silicon, NVIDIA's revenue could drop sharply. The sequential quarterly growth pattern ($44.1B -> ~$57B -> $68.1B -> guided $78B) shows strong momentum but also means the business needs to find enormous incremental dollars each quarter just to keep growing.

**Who are the customers and how concentrated are they?** This is the most concerning aspect of the business model. In Q3 FY2026, four direct customers accounted for 61% of $57 billion in revenue — Customer A (22%), Customer B (15%), Customer C (13%), and Customer D (11%). A year earlier, this concentration was 36%. These "direct customers" are likely ODMs/OEMs (Foxconn, Quanta, etc.) building on behalf of the hyperscalers, but the ultimate demand comes from perhaps 5-7 companies: Amazon (AWS), Microsoft (Azure), Google (GCP), Meta, Oracle, Tesla, and a few others. If any two of these companies paused or reduced AI infrastructure spending, NVIDIA would feel it immediately. This is the opposite of a diversified customer base.

**Can you explain the business to someone in 2 minutes?** Yes: NVIDIA designs the best chips for training and running AI models. It does not make the chips — TSMC does that — but NVIDIA's designs are the fastest, and its software platform (CUDA) is what all the AI developers already know how to use. The big cloud companies (Amazon, Microsoft, Google, Meta) are spending hundreds of billions of dollars building AI data centers, and most of that GPU spend goes to NVIDIA because there is no real alternative at scale yet. NVIDIA sells these chips for very high prices (71-75% gross margins), making it enormously profitable. The risk is that these same customers are building their own chips, and if they succeed, NVIDIA loses its biggest buyers. The business model itself is clear. What is less clear is how durable the demand is and how quickly the competitive landscape will shift.

## Signal Summary

- **Bull case:** AI infrastructure spending continues to accelerate through 2027+, NVIDIA maintains 80%+ share through CUDA lock-in and annual architecture upgrades (Blackwell -> Rubin -> Vera), and the $78B Q1 guidance is the beginning of a sustained higher plateau.
- **Bear case:** Hyperscalers successfully deploy custom ASICs at scale (Google TPU, Amazon Trainium, Microsoft Maia), reducing NVIDIA's share from 80% to 50-60% over 2-3 years, while AI capex growth decelerates as ROI on AI investments is scrutinized.
- **Confidence:** Medium-High — The business model is clearly understandable, but the sustainability and predictability of revenue at this scale is harder to assess with confidence. The concentration risk and capex-driven nature of demand introduce real uncertainty.

## Red Flags

- Customer concentration worsened dramatically: from 36% to 61% of revenue from top 4 customers in one year.
- Revenue is entirely capex-driven and non-recurring — there is no contractual floor if hyperscaler spending pauses.
- NVIDIA's largest customers (hyperscalers) are simultaneously its most motivated competitors, actively developing custom AI silicon.
- China revenue effectively zeroed out due to export controls, eliminating what was 13-26% of revenue in prior years.
- TSMC single-source manufacturing dependency — any disruption (geopolitical, natural disaster, capacity) would halt production.
- Custom ASIC growth rate (44.6%) is nearly 3x GPU growth rate (16.1%) in 2026, suggesting the competitive tide may be turning.

## Score: 7 / 10

NVIDIA's business model is clearly understandable — it designs and sells AI accelerator chips at premium prices to a concentrated set of hyperscale buyers, with a powerful software moat (CUDA) protecting its market position. The core model is not complex. However, the extreme customer concentration, capex-driven (non-recurring) revenue, and the fact that its biggest customers are actively building competing products introduce enough uncertainty about the durability of this business to prevent a higher score. You can explain what NVIDIA does easily; predicting what NVIDIA will earn in three years is much harder.
