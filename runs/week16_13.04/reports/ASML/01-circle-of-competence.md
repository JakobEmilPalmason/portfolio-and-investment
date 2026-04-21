# Circle of Competence — ASML

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-04-18
**Data Sources:** User-provided `context/ASML/financials.md` and `quant-valuation.md` (yfinance, 2026-04-18); ASML Q1 2026 press release (asml.com); CNBC Q1 2026 earnings coverage (2026-04-15); TrendForce reporting on High-NA EUV adoption; training knowledge of lithography industry. Company filings treated as primary; some market-share and customer-concentration figures are widely reported but not disclosed at precise granularity.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | ASML is the sole supplier of extreme ultraviolet (EUV) lithography systems — there is no second vendor on Earth | 5 |
| 2 | Revenue is split between system sales (chunky, one-time, ~€200M–€400M per machine) and a growing, recurring installed-base services business (~€6–7B/yr) | 4 |
| 3 | Top three customers (TSMC, Samsung, Intel) account for the overwhelming majority of leading-edge revenue — extreme customer concentration | 4 |
| 4 | FY2025 revenue of €32.7B, FY2026 guided to €36–40B; Q1 2026 already €8.8B with 53% gross margin | 3 |
| 5 | China exposure dropped from 36% (Q4 2025) to 19% (Q1 2026) as export controls bite — meaningful demand-mix shift | 4 |
| 6 | Business is understandable at a functional level but technically deep; "how it makes money" is simple, "why only they can do it" requires study | 3 |

## Detailed Analysis

ASML sells the machines that print microchips. More specifically, it sells photolithography systems — room-sized pieces of equipment that use light to etch the transistor patterns onto silicon wafers. Every leading-edge logic chip (the processors in phones, AI accelerators, laptops) and increasingly every leading-edge memory chip is made by a tool that ASML built. The customer list is short and famous: TSMC, Samsung Foundry, Intel Foundry, SK Hynix, Micron, and a long tail of Chinese memory/logic fabs buying older DUV (deep ultraviolet) equipment. In one sentence: ASML is the landlord of Moore's Law, and the foundries are the tenants.

The revenue model has two halves. The first half is system sales — "boxes" shipped to customers at prices that range from roughly €50M for an older DUV immersion tool, €180–220M for a current-generation Low-NA EUV (NXE:3800E), up to roughly €380M+ for a High-NA EUV (EXE:5200B). This half is lumpy: you book revenue when a tool is shipped and accepted. The second half is the installed-base business — service contracts, upgrades, and spare parts for the ~6,000+ systems already in the field. This half is recurring, high-margin, and now roughly a fifth of total revenue. In FY2025 total revenue was €32.7B, operating margin 34.6%, gross margin 52.8%. Q1 2026 came in at €8.8B with 53% gross margin, and 2026 guidance was raised to €36–40B (per ASML and CNBC). So the business converts massive, concentrated demand cycles into very high unit economics.

There are really only three or four variables that drive this company, which is exactly the Buffett ideal. First, **leading-edge capex by the top three foundries** — when TSMC and Samsung build new fabs at 3nm, 2nm, 1.4nm, they must order ASML tools. Second, **wafer starts and utilization** on the existing installed base, which drive services revenue. Third, **the pace of High-NA EUV adoption** — each machine is ~2x the price of the previous generation and enables sub-2nm nodes. Fourth, **geopolitics**, which is the wild card: US and Dutch export rules have already pushed Chinese share from ~36% in Q4 2025 to ~19% in Q1 2026, and a proposed US bill would further restrict DUV sales. Outside those four, everything (FX, individual node timing, specific AI end-demand) matters less.

Revenue predictability is a "yes, with an asterisk." The backlog is enormous and customers give multi-year visibility on tool orders, but cycles are real — when foundries pause capex (as happened in memory in 2023), ASML's top line swings hard. Services is the smoother layer underneath. Notably, this was the first quarter ASML stopped disclosing quarterly order intake, which has made the lumpy half of the business a bit less transparent (CNBC, 2026-04-15). For an investor the right mental model is: system revenue moves with the fab build cycle, services compounds quietly, and the sum-of-parts should grow at mid-teens through the High-NA ramp if the current customer roadmaps hold.

Customer concentration is a real feature, not a bug. A handful of foundries buy almost everything. If TSMC decided to skip High-NA at 1.4nm (which it has publicly said it will delay to later nodes, per TrendForce), that's a meaningful near-term dent. Samsung accelerating High-NA for 2nm (two EXE:5200B tools confirmed for 1H26) partly offsets. Intel is the largest current High-NA bettor, with the first commercial EXE:5200B already installed. The implication: three customers effectively vote on what ASML's next three years look like.

Can you explain ASML in two minutes? Yes — "they are the sole maker of the lithography machines needed to produce advanced chips; the top three chipmakers buy them; they earn ~35% operating margins and have a decade-plus technology lead." The deeper "why only them" (Zeiss optics, Cymer light source, 40 years of co-development) takes longer, but the *business* is simple. This sits inside the circle of competence for anyone willing to study semiconductor capital equipment; it is not a black box.

## Signal Summary

- **Bull case:** High-NA EUV ramps cleanly from 2027 onward, AI-driven wafer demand sustains fab capex through the decade, and ASML grows revenue at 10–15%/yr with expanding margins while services compounds as a moat-widener.
- **Bear case:** China export restrictions tighten further (proposed DUV ban), TSMC defers High-NA adoption, and a cyclical foundry capex pause produces a 20–30% revenue air-pocket in 2027–2028 despite the "monopoly."
- **Confidence:** High — the business is narrow, the customer list is short, the financials are clean, and the key drivers can be counted on one hand.

## Red Flags

- ASML stopped disclosing quarterly bookings in Q1 2026 — a modest transparency step backwards on the single most-watched leading indicator.
- Customer concentration at the top three foundries means any one customer's roadmap slip (especially TSMC on High-NA) directly dents the thesis.
- China dropped from 36% → 19% of sales in one quarter; further export-control escalation remains an open-ended risk.
- Revenue is reported in EUR while the ADR trades in USD — FX creates cosmetic noise in cross-statement comparisons.

## Score: 9 / 10

Few businesses are this clean to explain: one product category, a handful of customers, a small set of drivers, and dominant economics — the only reason this isn't a 10 is the geopolitical overlay that no one, including management, can fully underwrite.
