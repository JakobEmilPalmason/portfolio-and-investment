# Durable Competitive Advantage — ARM

**Analyst Role:** Moat Analyst
**Date:** 2026-03-10
**Data Sources:** Web search results (ARM newsroom, Futurum Research, EE Times, rijnberkinvestinsights, ainvest.com, klover.ai, BeyondSPX, patentpc.com, financialcontent.com, xda-developers.com, deepresearchglobal.com, TradingView); training knowledge for architectural/historical context. Financials and market share data current through Q3 FY2026 (December 2025).

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | ARM's ecosystem lock-in is the deepest in semiconductor IP: ~22 million developers (80% of the global total), every major OS, compiler, and toolchain optimized for ARM — this software moat took 30+ years to build and cannot be replicated quickly. | 5 |
| 2 | ARM holds >99% smartphone CPU market share and approximately 50% of hyperscaler data center CPU share in 2025, demonstrating the moat is expanding into new verticals rather than eroding. | 5 |
| 3 | Architecture upgrade cycles (Armv8 → Armv9 → CSS) give ARM structural pricing power: Armv9 commands ~5% ASP royalty vs. ~3% for Armv8; CSS exceeds 10% of ASP — a doubling of monetization per chip with no corresponding increase in R&D cost per unit. | 5 |
| 4 | RISC-V is a genuine long-term threat with ~20 billion cores deployed by end-2025 and growing hyperscaler and enterprise interest, but it currently lacks the software ecosystem depth to displace ARM in mobile, PC, or general-purpose server markets. | 4 |
| 5 | ARM's gross margin of ~97% and operating margin recovery to ~21% in FY2025 are empirical evidence that the moat permits pricing power above competitive levels. | 4 |
| 6 | ARM's move into its own chip products (AI accelerators for data centers) is strategically risky — it transforms ARM from a neutral supplier into a competitor to its own licensees, potentially weakening the trust that underpins the licensing moat. | 3 |

## Detailed Analysis

**What type of moat exists?**
ARM's competitive advantage is a multi-layered moat. The primary source is switching costs embedded in the software ecosystem: an estimated 22 million developers work with ARM daily, and every major operating system (iOS, Android, Windows on ARM, Linux), compiler suite (LLVM, GCC), debugging toolchain, and runtime library has been optimized for ARM instruction sets over decades. Any chip designer or OEM contemplating a switch to a different architecture must not only redesign hardware but also convince an entire global software supply chain to retool — a process that would take years and cost billions in aggregate. This is arguably the highest-friction switching cost in the semiconductor industry.

The secondary moat is a network effect / platform effect: because ARM is already everywhere, new chip designers default to ARM to access the existing software base without starting from scratch. More designers adopting ARM deepens the software library, which makes ARM more attractive to the next designer — a self-reinforcing flywheel. Management estimated in 2025 that 350+ billion ARM-based chips have been shipped cumulatively, and that installed base creates an ever-larger surface area of compatible software.

ARM also benefits from a trust-based franchise: as a neutral IP licensor that does not manufacture chips, ARM can partner with every major semiconductor company simultaneously without being perceived as a direct competitor. This neutrality is fundamental to why Apple, NVIDIA, Qualcomm, Amazon, and Google all pay ARM royalties rather than developing entirely proprietary architectures. (Note: ARM's 2025 decision to develop its own AI server chips is beginning to erode this neutrality — discussed in the red flags section.)

**How durable is the moat over a 10-year view?**
The smartphone moat (~99% share) is essentially permanent absent a catastrophic ecosystem disruption. The data center moat is younger and more contested — ARM went from ~18% to ~50% of hyperscaler CPU shipments in a single year (2024-2025), but this was facilitated by hyperscalers' active desire to reduce Intel dependence, not merely ARM's intrinsic merits. As Intel struggles and AMD holds steady on x86, ARM fills the vacuum, but the competitive dynamics here are more fluid than in mobile.

The architecture upgrade path (Armv9, CSS) is ARM's strongest near-term durability driver: customers who sign CSS license agreements are committing to ARM's ecosystem more deeply than ever before, reducing their design time by up to a year but also increasing their royalty obligations to >10% of chip ASP. These are long-duration contracts — once a design is committed, it produces royalties for 5-10 years.

**Evidence in the numbers:**
Gross margin of ~97% is extraordinarily high and reflects near-zero marginal cost of IP delivery. Operating margin was ~21% in FY2025 (recovering from ~2% in FY2024, which was distorted by IPO-related SBC). Royalty revenue grew 27% YoY in Q3 FY2026 to a record $737 million with no corresponding increase in cost of goods — pure margin expansion. Armv9 cores constituted >30% of royalty revenue in Q3 FY2026, up from ~25% prior — the mix shift toward higher-rate architectures is measurable and accelerating.

**Where is the moat weakest?**
RISC-V is the clearest structural threat. By end-2025, approximately 20 billion RISC-V cores had been deployed, primarily in IoT and embedded applications where ARM's ecosystem advantage is less critical (these are often bare-metal applications with no OS software ecosystem dependency). Qualcomm acquired RISC-V leader Ventana Micro Systems in December 2025, signaling serious institutional intent to build a royalty-free alternative for data center workloads. Meta is integrating RISC-V into its MTIA v3 AI accelerator. Android is expected to integrate RISC-V support into its Generic Kernel Image in early 2026. None of these represent an imminent threat to ARM's smartphone or general-purpose server business, but they represent credible diversification of the compute substrate over a 5-10 year horizon — particularly in AI accelerators where software portability is less of a barrier.

ARM's own entry into chip manufacturing is a second weakness point. By competing directly with Qualcomm and NVIDIA for data center AI chip deals, ARM risks antagonizing its largest licensees and threatening the collaborative neutrality that has been central to its business model. If Qualcomm perceives ARM as a competitor rather than a supplier, the incentive to develop RISC-V alternatives or custom architectures grows.

**Do advantages reset every product cycle?**
Partially. On one hand, each new architecture generation (Armv9, CSS) requires new licensing agreements, giving ARM regular opportunities to raise effective royalty rates — this is the "advantage improves" scenario. On the other hand, each new architecture also provides a moment when a customer could theoretically choose to switch architectures rather than relicense. In practice, switching has almost never happened at scale because the software ecosystem gravity is too powerful. Apple's M-series chips are ARM; Amazon's Graviton is ARM; Google's Axion is ARM. These investments in ARM-based infrastructure deepen the lock-in with every product cycle rather than resetting it.

## Signal Summary

- **Bull case:** The ARM architecture has become the de facto compute standard for mobile, is rapidly becoming the same for data centers, and the CSS/Armv9 upgrade cycle gives ARM structural royalty rate growth for the next decade — a rare combination of market share expansion and margin expansion simultaneously.
- **Bear case:** RISC-V's institutional momentum (Qualcomm acquisition, Meta adoption, Android integration) and ARM's own chip-building ambitions threaten to erode the trust-based neutrality that underpins the licensing model, potentially compressing long-run market share and royalty rates in AI-specific compute.
- **Confidence:** High — the moat's strength in existing markets (mobile, increasingly data center) is well-documented with empirical market share and margin data, and the RISC-V threat is real but decades away from being existential.

## Red Flags

- ARM's 2025 decision to build its own AI server chips (competing directly with Qualcomm and NVIDIA for Meta's data center deals) represents a potentially moat-weakening strategic pivot away from its "neutral IP supplier" identity.
- RISC-V has reached 20+ billion cores and has attracted Qualcomm's institutional backing — this is no longer a theoretical risk.
- Arm China is a semi-independent joint venture that ARM does not fully control; geopolitical disruption could cut off a material revenue channel AND fragment the ARM ecosystem in the world's largest chip manufacturing geography.
- Customer concentration (top 5 = 56% of revenue) means a defection by one or two large customers could have outsized royalty revenue impact, even if the architecture remains the industry standard.

## Score: 8 / 10

ARM has one of the most durable moats in the semiconductor industry — a 30-year software ecosystem lock-in that is widening into data centers — but the RISC-V institutional threat and ARM's own chip-making ambitions introduce genuine long-term moat risks that prevent a top score.
