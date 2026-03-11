# Circle of Competence -- SNOW

**Analyst Role:** Business Clarity Analyst
**Date:** 2026-03-06
**Data Sources:** Web search results (March 2026) for FY2026 earnings, pricing model details, net revenue retention, customer metrics, competitive landscape, and securities litigation. No user-provided context files. Some figures (e.g., industry revenue concentration percentages) come from analyst estimates and may be approximate. Core financials sourced from Snowflake press releases and investor presentations.

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Product revenue represents ~95% of total revenue; the business is essentially a single-product company with consumption-based billing. | 5 |
| 2 | Net revenue retention rate is 125% (Q4 FY2026), meaning existing customers spend 25% more each year on average -- a strong but declining metric (was 127% a year earlier). | 4 |
| 3 | Compute costs make up ~80% of a typical customer's Snowflake bill, making query volume and compute usage the dominant revenue driver. | 4 |
| 4 | FY2026 full-year revenue was $4.68B (up 29% YoY), but GAAP net loss was approximately $1.4B, driven largely by $1.7B+ in stock-based compensation. | 5 |
| 5 | Product efficiency improvements (Iceberg Tables, tiered storage pricing) are creating a structural headwind to consumption growth and are the basis of an active securities class action lawsuit (lead plaintiff deadline April 27, 2026). | 4 |
| 6 | Databricks is growing revenue at ~57% YoY vs. Snowflake's ~29%, representing an intensifying competitive threat in the cloud data platform market. | 3 |

## Detailed Analysis

**What does Snowflake sell, and to whom?** Snowflake sells a cloud-based data platform that lets organizations store, query, and share large volumes of data. The core product is a data warehouse -- think of it as a massive, flexible database that runs on top of Amazon Web Services, Microsoft Azure, or Google Cloud. Customers are overwhelmingly large enterprises: Fortune 500 companies, financial services firms, healthcare organizations, retailers, and technology companies. As of Q3 FY2026, Snowflake had 12,621 total customers and 688 customers spending more than $1 million per year. The product also enables data sharing between organizations and increasingly supports AI/ML workloads, but the foundation is still "store data, run queries on it."

**How does it actually make money?** Snowflake uses a consumption-based pricing model. Customers buy "credits" (either on-demand at $2-4 each, or pre-purchased at a discount of $1.50-2.50 each) and spend those credits when they run compute queries. Storage is billed separately at ~$23 per terabyte per month, and data transfer across cloud regions incurs additional fees. This is not a traditional subscription model -- revenue fluctuates based on how much customers actually use the platform. However, many large customers sign multi-year capacity contracts (remaining performance obligations totaled $9.77B as of Q4 FY2026, growing 42% YoY), which provides some forward visibility. Product revenue was ~95% of total revenue in FY2025 and FY2026; the remaining ~5% comes from professional services, which Snowflake runs at negative margins as a loss leader to drive product adoption.

**What are the key drivers?** The 2-4 variables that matter most are: (1) **Customer compute consumption** -- since ~80% of a customer's bill is compute, the volume and complexity of queries customers run is the single biggest revenue lever. (2) **Net revenue retention / expansion** -- at 125%, existing customers are growing their spend, but this rate has been slowly declining and is sensitive to product efficiency gains that let customers do more with fewer credits. (3) **New customer acquisition**, particularly large enterprises willing to commit to multi-year contracts. (4) **Competitive positioning** against Databricks, BigQuery, and Redshift, each of which offers overlapping functionality within their respective cloud ecosystems.

**How predictable is the revenue?** Moderately predictable. The $9.77B in remaining performance obligations provides a substantial revenue backlog. However, consumption-based billing introduces real variability -- customers can scale usage up or down in any given quarter, and product efficiency improvements (a good thing for customers) directly reduce revenue per workload. This is an inherent tension in the model: making the product better can slow revenue growth. Seasonal patterns exist but are secondary to the consumption trend.

**Who are the customers and how concentrated are they?** Snowflake serves a broad base of 12,621 customers, but revenue is heavily weighted toward large enterprises. Financial services accounts for roughly 25% of revenue, retail/CPG ~20%, healthcare ~15%, and technology/media ~18%. No single customer appears to represent a dangerously large share of revenue based on available disclosures, but the top tier of $1M+ customers (688 accounts) likely drives the majority of product revenue. Switching costs are moderate to high -- migrating a data warehouse is painful and expensive -- but not insurmountable, especially as competitors like Databricks push open-format standards (Iceberg Tables) that reduce lock-in.

**Can you explain this business in 2 minutes?** Yes. Snowflake is a cloud data warehouse. Companies pay Snowflake to store their data and run queries on it, with billing based on how much computing power they use. It runs on top of AWS, Azure, and GCP but is cloud-agnostic, which is its key differentiation from each cloud provider's native offering. The more data a company has and the more questions it asks of that data, the more it pays Snowflake. The business model is understandable, though the consumption-based pricing creates more revenue uncertainty than a traditional subscription and the competitive dynamics with Databricks add complexity. This is within the circle of competence for someone willing to spend an afternoon studying it.

## Signal Summary

- **Bull case:** AI workloads and data proliferation drive accelerating consumption growth across Snowflake's large enterprise base, and the $9.77B backlog converts into durable 30%+ revenue growth while margins expand toward GAAP profitability.
- **Bear case:** Product efficiency gains and open-format competition (Databricks, Iceberg Tables) structurally compress consumption per customer, NRR continues to decline, and massive stock-based compensation prevents GAAP profitability for years while the lawsuit overhang weighs on sentiment.
- **Confidence:** Medium -- The business model is clear and the financial data is current, but the tension between product efficiency and consumption revenue, plus the rapidly shifting competitive landscape, introduces meaningful uncertainty about the trajectory.

## Red Flags

- GAAP net loss of ~$1.4B in FY2026 on $4.68B in revenue, with stock-based compensation exceeding $1.7B (34% of revenue). Non-GAAP profitability masks real economic cost of employee compensation.
- Securities class action lawsuit alleging the company misled investors about the revenue impact of product efficiency improvements. Lead plaintiff deadline is April 27, 2026.
- Net revenue retention declining from 127% to 125% over the past year, suggesting the expansion engine may be decelerating.
- Databricks growing at nearly double Snowflake's rate (57% vs 29% YoY), with increasing overlap in core use cases.
- Consumption-based model means a macroeconomic slowdown could cause rapid revenue deceleration as customers curtail discretionary queries and workloads.

## Score: 7 / 10

The business model is understandable with moderate study -- you can explain what Snowflake does, how it makes money, and what drives revenue. The consumption-based pricing adds a layer of complexity and unpredictability that prevents a higher score, and the tension between "making the product more efficient" and "growing revenue" is a nuance that requires ongoing attention. This is within the circle of competence for a diligent generalist, but it is not as simple as a toll bridge or a consumer staple.
