# Circle of Competence — UNH

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-04-18
**Data Sources:** Web search (UnitedHealth 2025 full-year results released Jan 27, 2026; segment disclosures for UnitedHealthcare, OptumHealth, OptumRx, OptumInsight; DOJ investigation coverage; Change Healthcare cyberattack reporting), user-provided `context/UNH/financials.md`, `context/UNH/quant-valuation.md`, training knowledge on US managed care.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | UnitedHealth is really two big businesses stapled together: a $300B+ insurance book (UnitedHealthcare) and a $270B services business (Optum). Each has its own drivers and its own regulators. | 5 |
| 2 | FY2025 revenue was $447.6B but net income fell to $12.1B, down from $22.4B in FY2023, driven almost entirely by medical cost ratio climbing to ~89.1% in Medicare Advantage. | 5 |
| 3 | The insurance business is unusually predictable on revenue (government-set premiums, multi-year enrollment) but highly sensitive on cost (how sick members actually turn out to be). | 4 |
| 4 | OptumHealth flipped from $7.8B earnings in 2024 to a reported loss of $278M in 2025 — a segment that most outside investors did not realize could swing that hard. | 4 |
| 5 | Customer concentration sits with the US federal government: Medicare Advantage and Medicaid together are the single largest revenue pool, making CMS rate decisions a top-3 business driver. | 4 |
| 6 | The business has at least seven material revenue lines (commercial insurance, MA, Medicaid, self-funded admin, pharmacy benefits, care delivery, health data/IT), which is why no one-sentence description is honest. | 3 |

## Detailed Analysis

**What the company sells, and to whom.** UnitedHealth does two things. First, it sells health insurance — through UnitedHealthcare — to three types of customer: employers (commercial group plans, including big self-funded accounts where UNH is really doing admin and network rental), seniors (Medicare Advantage, which is a privatized version of Medicare where the federal government pays UNH a per-member fee to take on the risk), and low-income Americans (Medicaid, also paid by state/federal governments). Second, it sells health services through Optum — this is the part most people underestimate. Optum owns one of the three big US pharmacy benefit managers (OptumRx), one of the largest employers of physicians and operators of clinics/surgery centers in the country (OptumHealth), and a health-data/analytics/revenue-cycle business (OptumInsight, which includes Change Healthcare). The two sides trade with each other — UNH's own insurance plans buy services from Optum — which is part of why the company has historically grown earnings faster than revenue.

**How it actually makes money.** On the insurance side: collect premiums, pay claims, keep the spread. That spread is called underwriting margin, and the key number is the medical care ratio (MCR) — the percentage of premium paid out in claims. Historically UNH ran an MCR around 82–84%; in 2025 it hit 89.1%. Every 100 basis points of MCR on ~$300B of premium revenue is about $3B of operating profit. That math is why the MCR story matters so much. On the Optum side: OptumRx makes money on script volume and rebates; OptumHealth bills fee-for-service and value-based care contracts; OptumInsight is a mix of software subscriptions, transaction fees, and consulting. Corporate also earns meaningful investment income on float (the difference between when premiums come in and when claims are paid) — interest expense of ~$4B annually is partially offset by this.

**Key drivers.** Four things move the earnings more than anything else: (1) **Medicare Advantage MCR** — this is the swing factor right now. If it normalizes to ~86% by 2027, earnings recover to $20B+; if it stays at 89%, they do not. (2) **CMS rate notices** — the federal government sets MA payment rates each year; the 2024 and 2025 notices were tight, and a Trump-administration CMS under renewed scrutiny is not a clean tailwind. (3) **Optum profit pool** — OptumHealth's 2025 loss was a shock. Recovery in value-based-care contract economics is a separate assumption from insurance recovery. (4) **Regulatory/PBM outcomes** — the DOJ Medicare Advantage billing probe (both civil and criminal), FTC PBM scrutiny, and post-Thompson political heat could each force business-model changes.

**How predictable is the revenue.** Top-line revenue is quite predictable — premiums are contracted annually, CMS payments are formulaic, employer plans renew in waves. This is why analysts still confidently model $439B+ revenue for 2026. Earnings, however, have become much less predictable in the last two years. The FY2023 → FY2025 collapse in net income (from $22.4B to $12.1B) happened on *rising* revenue. That gap between revenue predictability and earnings predictability is the core tension of the current moment.

**Customer concentration.** Individual customer concentration is low by count — tens of millions of members, thousands of employer groups. But at the *payor* level, the US federal government (CMS) is the single most important counterparty, via Medicare Advantage and Medicaid managed care contracts. MA alone is roughly a third of UnitedHealthcare's revenue. That makes a single political actor — whoever runs CMS — more important to UNH's earnings than any commercial customer.

**Can I explain it in 2 minutes?** Yes, but with a caveat. The simple version is: "UNH collects premiums and pays claims, plus it owns a PBM and a lot of doctors' offices." A smart friend gets that in a minute. What takes longer is explaining *why* the business is currently under stress: MA risk-adjustment accounting, how OptumHealth got exposed to value-based-care losses, why a DOJ probe on diagnosis coding is not a rounding error, and why the PBM side is a target in its own right. Those second-layer pieces are not optional — they are the reason earnings halved. That puts UNH in the "understandable with study" tier, not the "obviously simple" tier.

## Signal Summary

- **Bull case:** MA MCR normalizes by 2027, Optum earnings recover, DOJ probes settle for fines not structural change, and investors re-rate what is still the largest diversified healthcare payor/services business in America — with $20B+ in normalized net income.
- **Bear case:** MA cost trends prove structurally higher (an aging member mix, stricter CMS rate policy), DOJ outcomes force changes in diagnosis coding or MA growth, FTC/Congress restructure PBM economics, and Optum's value-based-care model needs to be permanently reset at lower margin.
- **Confidence:** Medium — the business is understandable, but the *path* from here depends on multiple simultaneously-changing variables (MA pricing, CMS policy, legal outcomes, Optum recovery). That is more moving parts than a Buffett-style business should have.

## Red Flags

- Cost line of the insurance business (MCR) is currently opaque: 2025 included "loss contracts" and newly-enrolled MA members who turned out sicker than priced. How much of that is one-time vs. structural is the key question, and management has not yet demonstrated a clean answer.
- OptumHealth earnings volatility went from "steady compounder" narrative to a full-year operating loss in one year. That is a business-model signal, not a blip.
- The Change Healthcare breach (Feb 2024) cost over $2.45B and touched ~193M Americans' records. That it happened inside the supposedly-crown-jewel data/IT segment is a tell about operational complexity — these are not "simple" businesses stapled together.
- Customer concentration via the US federal government cuts both ways; in a period when public sentiment on the industry is this negative, government policy is unlikely to be the friend it was in 2015–2023.

## Score: 6 / 10

Understandable with effort, not trivially simple. The insurance business model is clean in the abstract but currently has multiple moving cost drivers the market is not confidently modeling; Optum is a second large business with its own distinct drivers; and regulatory/political risk is a live, not latent, part of the story today. A 6 reflects "I can explain it but I would not confidently project earnings five years out."
