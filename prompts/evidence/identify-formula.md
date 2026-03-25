# Evidence Verification — Pass C: Identify Arithmetic Formula

You are identifying the formula needed to verify a derived financial metric
claimed in an investment analysis report. Python will execute your formula —
you do NOT compute the result yourself.

**Ticker:** {TICKER}

## Assertion to verify

{ASSERTION}

## Available numeric evidence (from SEC filings)

{EVIDENCE}

## Your task

1. Identify which derived metric the assertion is claiming (e.g., ROIC, FCF conversion, margin %, growth rate)
2. Write a valid Python arithmetic expression that computes it from the available evidence
3. Map each variable in your formula to an evidence fact_key from the list above

## Rules

- Your formula must use ONLY: +, -, *, /, //, %, **, parentheses, and these functions: abs, min, max, round, sqrt, log, log10
- Variable names must be valid Python identifiers (use snake_case, e.g., `net_income`, `total_revenue`)
- Each variable must map to exactly one fact_key from the evidence list
- If the required inputs are not available in the evidence, return null for the formula
- Common formulas:
  - ROIC: `nopat / ((ic_curr + ic_prev) / 2)` where NOPAT = operating_income * (1 - tax_rate)
  - FCF conversion: `fcf / net_income`
  - Gross margin: `gross_profit / revenue`
  - Revenue growth: `(rev_curr - rev_prev) / rev_prev`

## Output

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```
