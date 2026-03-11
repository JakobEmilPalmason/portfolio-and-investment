# Circle of Competence — ARM

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-03-10
**Data Sources:** Web search results (ARM newsroom Q2/Q3 FY2026 earnings releases, Motley Fool earnings call transcripts, StockAnalysis.com financials, ARM annual report FY2025, stockdividendscreener.com revenue breakdown, BeyondSPX analysis); training knowledge for structural/background context. Financials current through Q3 FY2026 (quarter ended December 31, 2025).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | ARM sells chip architecture intellectual property, not chips — it earns royalties on every ARM-based chip shipped globally, creating a toll-road revenue model. | 5 |
| 2 | Revenue has two distinct streams: licensing fees (one-time, lumpy) and royalties (recurring, volume-driven) — FY2025 total revenue was $4.0 billion, growing ~24% YoY. | 5 |
| 3 | ARM's technology powers >99% of smartphones and ~50% of hyperscaler data center CPUs shipped in 2025, giving it extraordinary breadth across compute markets. | 4 |
| 4 | Customer concentration is meaningful: the top five customers (including Arm China) accounted for ~56% of total net revenue in FY2025. | 4 |
| 5 | Armv9 and Compute Subsystems (CSS) represent a structural royalty-rate step-up: Armv9 earns ~5% of chip ASP vs. ~3% for Armv8; CSS earns >10% of ASP — the highest rates ever. | 5 |
| 6 | Revenue predictability is moderate: royalties are recurring and volume-driven but licensing fees are lumpy and deal-dependent, creating quarterly noise. | 3 |

## Detailed Analysis

**What does ARM sell, and to whom?**
ARM Holdings licenses its processor instruction set architectures (ISAs) and physical IP cores to semiconductor companies — fabless designers, integrated device manufacturers, and increasingly hyperscalers building custom silicon. Customers include Apple, Qualcomm, NVIDIA, MediaTek, Samsung, Amazon Web Services, Google, Microsoft, and Arm China (a joint venture that serves Chinese licensees). ARM does not manufacture chips. It designs the blueprints — the architecture and ready-made IP blocks — that hundreds of chip designers worldwide use as their starting point. ARM then collects a toll (a royalty) on every chip sold that incorporates its architecture.

**How does it actually make money?**
ARM's revenue falls into two segments. Licensing revenue ($515 million in Q2 FY2026, up 56% YoY) represents upfront fees paid when a customer signs a license agreement to use ARM's IP or architecture in a new design. These are project-specific, contractual, and often multi-year agreements. They can be large and irregular, making quarterly results lumpy. Royalty revenue ($620 million in Q2 FY2026, up 21% YoY; reaching a record $737 million in Q3 FY2026, up 27% YoY) is paid by chip manufacturers per unit shipped. Rates are set contractually as a percentage of the chip's average selling price. The newer Armv9 architecture commands roughly 5% of ASP versus 3% for Armv8, and Compute Subsystems (CSS) products earn over 10% of ASP — the highest in company history. Gross margins for the overall business sit at approximately 97%, reflecting the near-zero marginal cost of IP licensing.

**Key drivers (2-4):**
First, chip shipment volume: ARM's royalty revenue scales directly with how many ARM-based chips are sold globally. Smartphone chip volumes (predominantly Qualcomm, MediaTek, Apple) set the base, while data center and AI inference chips are the fastest-growing increment. Second, architecture mix shift: as Armv9 and CSS adoption grows as a share of total royalty revenue (Armv9 was >30% of royalty revenue in Q3 FY2026 vs. ~25% earlier), the blended royalty rate per chip rises structurally even without volume growth. Third, data center penetration: ARM reported that nearly 50% of compute shipped to top hyperscalers in 2025 was ARM-based (up from ~18% the prior year), a dramatic acceleration that drove data center royalties to double YoY. Fourth, licensing deal cadence: large ALA (Architecture License Agreements) and TLA (Technology License Agreements) generate irregular upfront payments that distort quarterly revenue but signal future royalty streams several years out.

**How predictable is the revenue?**
Royalty revenue — roughly 55-60% of total — is moderately predictable and recurring in nature, tied to chip shipment volumes that change slowly quarter-to-quarter in mobile but can spike in data center. Licensing revenue is less predictable: it reflects the timing of when customers sign new license agreements and begin design programs. Management has noted that licensing revenue concentration from specific large deals can cause meaningful quarter-to-quarter swings. Full-year guidance as of Q3 FY2026 pointed to roughly 20%+ royalty growth and 25-30% licensing growth YoY. The business is not subscription-SaaS predictable, but royalties have an annuity-like character given the long lifecycle of chip designs.

**Customer concentration:**
The top five customers, including Arm China, represented ~56% of total net revenue in FY2025 (up from 54% in FY2024). ARM does not publicly break out individual customers by exact revenue share in most filings, but the named licensees include Apple, Qualcomm, NVIDIA, MediaTek, Amazon, Google, Microsoft, Intel, and Samsung. Arm China is a separate entity (a joint venture ARM does not fully control) through which all Chinese licensee revenue flows — adding geopolitical concentration risk on top of customer concentration risk. If Apple were to transition away from ARM (highly unlikely given deep investment), or if Chinese chip shipments were restricted by regulation, the revenue impact would be significant.

**Can you explain the business in 2 minutes?**
ARM is the semiconductor industry's de facto standard for processor design. It writes the instruction manual — the architecture — for how billions of chips think. Every chip designer who wants to build an ARM-based processor must pay ARM a license fee upfront, then a royalty on every chip they sell. ARM doesn't compete with its customers in chip manufacturing; it is the neutral IP supplier on whose shoulders almost all modern mobile and increasingly data center computing is built. Think of it as the QWERTY keyboard standard: once you have it embedded everywhere — in developer tools, operating systems, compilers, and hundreds of billions of shipped devices — the switching costs become prohibitive. Revenue comes from two sources: irregular upfront licensing payments when customers start new design programs, and recurring royalties that tick up as more chips ship and as customers adopt newer, higher-royalty-rate architectures. The newest generation (Armv9, CSS) earns roughly twice the royalty rate of prior generations, giving ARM a structural tailwind even if total chip volumes are flat.

## Signal Summary

- **Bull case:** Armv9 and CSS adoption driving structural royalty rate expansion, combined with data center CPU share surging from ~18% to ~50% in a single year, creates a multi-year royalty revenue compounding engine that is still in early innings.
- **Bear case:** Revenue predictability is hampered by lumpy licensing fees and deep customer concentration (top 5 = 56% of revenue), while Arm China JV adds geopolitical opacity that could impair a significant revenue channel.
- **Confidence:** Medium — the business model is genuinely clear and the financial data is well-documented through Q3 FY2026, but the precise size of individual customer dependencies and Arm China revenue contribution lack full public disclosure.

## Red Flags

- Top 5 customers represent ~56% of revenue; exact individual customer breakdown is not fully disclosed.
- Arm China operates as a semi-independent joint venture, creating governance opacity and potential revenue interruption risk in a US-China trade conflict.
- Licensing revenue is lumpy and can swing materially quarter-to-quarter, creating earnings volatility that is hard to model.
- ARM is beginning to build its own chips (targeting data center AI accelerators for Meta and others), which may complicate its "neutral supplier" relationship with existing licensees like Qualcomm and NVIDIA.

## Score: 7 / 10

ARM's business model is genuinely understandable — a royalty toll-road on the world's chip industry — but customer concentration, Arm China opacity, and lumpy licensing revenue introduce complexity that keeps this from being crystal clear.
