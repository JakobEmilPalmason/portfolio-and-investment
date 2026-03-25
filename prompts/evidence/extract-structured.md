# Evidence Extraction — Pass 2: Extract Structured Facts

You are extracting structured data from specific claims identified in an
SEC filing section. For each claim below, produce a structured fact with
a VERBATIM source quote from the section text.

**Section:** {SECTION_KEY}
**Ticker:** {TICKER}
**Filing period:** {FISCAL_PERIOD}

## Claims to extract

{CLAIMS}

## Extraction rules

### fact_key
Use dot-notation with the section prefix. The prefix prevents collisions
with XBRL-extracted numeric facts.

- MD&A: `mda.revenue_growth`, `mda.segment.cloud`, `mda.margin_driver.pricing`,
  `mda.volume.transactions`, `mda.guidance.revenue_fy2026`
- Risk Factors: `risk.regulatory.eu`, `risk.competitive.market_share`,
  `risk.macro.interest_rate`, `risk.legal.antitrust`
- Business: `biz.model.subscription`, `biz.geography.countries`,
  `biz.employees.total`, `biz.competitive.moat`
- Market Risk: `market_risk.fx.eur_usd`, `market_risk.interest.sensitivity`,
  `market_risk.commodity.exposure`

### fact_value
Human-readable as stated in the filing: "$40.0 billion", "approximately 15%",
"200+ countries and territories". Keep the original formatting and language.

### fact_value_numeric
Normalized to base units:
- Dollar amounts -> actual dollars: "$40.0 billion" -> 40000000000.0
- Percentages -> decimal: "15.3%" -> 0.153, "grew 11%" -> 0.11
- Ratios -> as stated: "1.08x" -> 1.08
- Counts -> as stated: "200 countries" -> 200
- Set null for purely qualitative facts (no specific number).

### fact_unit
Exactly one of: "USD", "percent", "ratio", "count", "days", "text"
Use "text" only for qualitative facts with no numeric component.

### source_quote — CRITICAL REQUIREMENT
This MUST be a VERBATIM substring of the section text provided below.

Rules:
1. Copy the EXACT characters from the source text. Do not rephrase, reorder,
   capitalize differently, or combine text from different sentences.
2. A Python `section_text.find(source_quote)` operation will be run against
   the section text. If it returns -1, the fact is penalized.
3. Include enough surrounding context to verify the fact independently
   (usually 1-2 sentences, 50-200 characters).
4. Minimum 10 characters.
5. If you absolutely cannot find a verbatim quote for a claim, add the
   claim text to the skipped_claims list instead of fabricating a quote.

### fact_type
- "metric" — a specific number or measurement
- "narrative" — a qualitative business fact without a specific number
- "guidance" — a forward-looking statement about expected future performance
- "risk_factor" — a risk disclosure or warning

### fiscal_period
The period the fact refers to. Use "{FISCAL_PERIOD}" if the fact refers to
the current filing period. Use a different period (e.g., "FY2024", "Q3FY2025")
if the fact explicitly references a different time period.

## Output

Set section_key to "{SECTION_KEY}".

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```
