# Evidence Verification — Pass A: Decompose Report Claims

You are extracting verifiable assertions from an investment analysis
report section. Each assertion must be atomic, independently testable,
and traceable to the report text.

**Umbrella Section:** {UMBRELLA_NUMBER} — {SECTION_TITLE}
**Ticker:** {TICKER}

## What to extract

For each paragraph in the Detailed Analysis section below, identify every
factual claim that could be verified against a company's SEC filing.

- Quantitative claims: specific numbers, percentages, dollar amounts, ratios
- Comparative claims: "higher than", "grew from X to Y", "outpaced"
- Causal claims: "driven by", "due to", "resulting from"
- Qualitative claims: business model facts, competitive position statements

## What NOT to extract

- Opinions or subjective judgments ("strong", "impressive", "concerning")
- Forward-looking speculation without specific numbers
- Restatements of the same fact in different words
- Generic industry statements not specific to the company
- Score justifications (the "Score: X/10" line)

## Rules

1. Maximum 15 assertions per section.
2. Set requires_arithmetic=true ONLY for derived metrics: ROIC, FCF conversion
   ratios, margin calculations, growth rates computed from two data points.
   Raw numbers from the filing (revenue, net income) do NOT require arithmetic.
3. category must be one of: finding, strength, risk, red_flag, trigger
4. source_location format: "key_findings:N" for table rows,
   "detailed_analysis:paraN" for prose paragraphs,
   "red_flags:N" for red flag bullets, "signal_summary:bull|bear" for signals

## Output

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```
