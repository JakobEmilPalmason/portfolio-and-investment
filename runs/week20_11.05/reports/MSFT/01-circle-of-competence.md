# Circle of Competence — MSFT

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-05-11
**Data Sources:** `context/MSFT/financials.md` (yfinance, FY2025); `context/MSFT/quant-valuation.md`; WebSearch on Microsoft Q3 FY2026 earnings (CNBC, Microsoft IR, Futurum, TradingKey); WebSearch on Copilot enterprise adoption (Stackmatix, Let's Data Science); WebSearch on Azure vs AWS vs GCP share (heygotrade, businessstats). Training knowledge for Microsoft segment history.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | FY2025 revenue of $281.7B is concentrated in three segments — Productivity & Business Processes (Office/M365/LinkedIn/Dynamics), Intelligent Cloud (Azure/server products), and More Personal Computing (Windows/Search/Gaming). | 5 |
| 2 | Azure and other cloud services grew 40% YoY in Q3 FY2026 (constant currency 39%), making cloud the dominant growth driver; AI-related annualized revenue is ~$37B (up 123% YoY) (CNBC, Microsoft IR 2026). | 5 |
| 3 | Microsoft 365 Copilot paid commercial seats crossed 20M, with paid seat additions up 250% YoY in Q3 FY2026 (Microsoft IR; Stackmatix 2026). | 4 |
| 4 | Revenue is overwhelmingly recurring: Microsoft Cloud (commercial cloud) reached ~$54.5B in a single quarter and represents subscription, consumption, and multi-year enterprise commitments — not one-off licenses. | 5 |
| 5 | Customer base is highly diversified — millions of commercial customers, no single customer >10% of revenue (per historical 10-K disclosures); largest single contract disclosed is OpenAI's $250B+ multi-year cloud commitment (Microsoft Q3 FY2026 IR commentary). | 4 |
| 6 | Capex has stepped up dramatically — $64.6B in FY2025 vs. $23.9B in FY2022, and calendar 2026 capex guidance is ~$190B (CNBC, Microsoft IR 2026). This changes the cash-flow profile materially. | 5 |

## Detailed Analysis

Microsoft sells software and cloud services. The business breaks cleanly into three buckets. The first is **Productivity & Business Processes** — Microsoft 365 (Office plus Teams plus security plus management tooling, mostly sold as per-seat subscriptions), Dynamics 365 (enterprise resource planning and customer relationship management), and LinkedIn. The second is **Intelligent Cloud** — Azure (rented compute, storage, networking, and AI services, billed on consumption) plus on-premise server licenses (SQL Server, Windows Server). The third is **More Personal Computing** — Windows OEM licenses to PC makers, Surface devices, Bing search, advertising, and gaming (Xbox plus Activision Blizzard plus Game Pass). You can describe the business in two minutes: "Microsoft rents productivity software to companies, rents cloud infrastructure to companies, and sells Windows and games to consumers — and the first two are growing very fast because of AI."

How it makes money is mostly subscription and consumption. Office and Dynamics are paid per user per month — predictable, sticky, and contractually committed. Azure is paid by the gigabyte, by the CPU-second, by the API call — less contractual but increasingly multi-year because customers reserve capacity. Microsoft Cloud (the combined commercial subset) revenue was $54.5B in Q2 FY2026 alone (Let's Data Science 2026). Windows and gaming are more transactional, but they're a shrinking share of the mix. The big shift since 2014 has been from one-time license sales to recurring subscriptions, and that is now nearly complete on the commercial side.

The key drivers are short: (1) **Azure consumption growth**, which is a function of total enterprise IT migration plus AI workload growth — Azure grew 40% in Q3 FY2026, the fifth consecutive accelerating quarter (TradingKey 2026); (2) **Copilot seat penetration** across the installed M365 base — 20M+ paid seats with Fortune 500 deployment at 64% (Stackmatix 2026); (3) **per-seat M365 price/mix** as AI features push customers up the price ladder; and (4) **capex efficiency**, because the company is now spending roughly $190B per calendar year on data centers and chips, and the return on that capital is the central financial question.

Revenue predictability is exceptional. The subscription base produces a known floor. Even Azure consumption, which is technically variable, is anchored by multi-year enterprise commitments — OpenAI alone has reportedly committed $250B+ to Azure under the revised deal terms (TechCrunch 2026; om.co 2026). Seasonal patterns exist (gaming Q2, enterprise Q4) but are mild relative to overall recurring base. No single customer >10% of revenue per 10-K precedent, and the customer base spans Fortune 500 down to small business. The one concentration that matters is **OpenAI as a customer** — material enough to be disclosed but not so material that loss would be terminal.

The complexity worth flagging is the AI economics. Microsoft is reporting an annualized $37B AI revenue run-rate (Microsoft IR Q3 FY2026), but it is also spending ~$190B in calendar 2026 on capex, with about $25B of that attributed to memory/component inflation rather than new capacity (Global Data Center Hub 2026). The intelligent investor must hold two things in mind at once: the operating businesses (M365, Azure ex-AI, Windows, gaming) are simple and excellent, and the AI buildout layered on top is a massive bet whose unit economics are still being proven. That's not opaque — Amy Hood discusses it on every call — but it makes the next 3–5 years less predictable than the prior decade.

Customer concentration is essentially nil. Enterprise stickiness is extreme — switching from M365 to Google Workspace or Azure to AWS happens but is rare and slow because the entire IT stack, identity (Entra/Active Directory), security tooling, and developer tools (GitHub, Visual Studio) are integrated. You can explain the business to a smart friend in two minutes; the wrinkle, which you'd add as a third minute, is "but they're spending $190B a year to win the AI infrastructure race, and we won't know for several years whether that math works."

## Signal Summary

- **Bull case:** AI capex translates into durable mid-teens topline growth and the Copilot attach rate on M365 raises per-seat ARPU 30-50% over five years, while Azure continues to take share from AWS at roughly current trajectory.
- **Bear case:** AI capex outruns AI demand, GPU/memory prices stay elevated, depreciation eats operating margin (already visible — D&A rose from $14.5B in FY2022 to $34.2B in FY2025), and FCF growth stalls or declines for several years even as revenue grows.
- **Confidence:** High — the business model is one of the clearest in the S&P 500. The uncertainty lies in capex returns, not in understanding what Microsoft sells or how it gets paid.

## Red Flags

- Capex has roughly tripled in three years ($23.9B FY2022 → $64.6B FY2025), and the company guides another huge step-up to ~$190B calendar 2026. FCF margin has already fallen from 32.9% (FY2022) to 25.4% (FY2025). The trend matters.
- D&A more than doubled FY2024→FY2025 ($22.3B → $34.2B); future depreciation from the current capex wave will be a meaningful drag on reported earnings.
- AI revenue disclosure ($37B annualized, up 123%) mixes first-party AI products with third-party AI workloads running on Azure — useful but not as crisp as a clean segment.
- OpenAI exposure cuts both ways: a major customer and a 27%-owned investee whose financial health (and IP rights through 2032) materially affects Microsoft's AI moat (GeekWire 2026).

## Score: 9 / 10

Microsoft has one of the simplest, most predictable business models among trillion-dollar companies — recurring software subscriptions and metered cloud consumption sold to a diversified base of millions of customers. The AI capex cycle adds genuine complexity, but it does not make the underlying business opaque; it just makes the next five years' free-cash-flow trajectory less predictable. The model itself is crystal clear.
