# Evidence Extraction — Pass 1: Identify Claims

You are scanning a section of an SEC filing. List every factual claim
in the section text below. Do NOT extract structured data — that happens
in a separate pass.

**Section:** {SECTION_KEY}
**Ticker:** {TICKER}
**Filing period:** {FISCAL_PERIOD}

## What counts as a factual claim

- A specific number or metric ("revenue grew 11% to $40 billion")
- A stated business fact ("operates in 200+ countries")
- A forward-looking statement ("expects revenue growth of 8-10%")
- A risk disclosure with specifics ("subject to regulatory action in the EU")
- A comparison to prior period ("compared to $35.9 billion in the prior year")
- A management assertion about business drivers ("growth was driven by...")
- A segment or geography breakdown ("cloud revenue was $12.4 billion")

## What does NOT count

- Boilerplate legal disclaimers or safe-harbor language
- Table-of-contents references or cross-references to other items
- Definitions of terms without factual content
- Repeated statements of the same fact in different words
- Pure GAAP accounting policy descriptions without company-specific facts
- Headers, titles, or structural formatting elements

## Rules

1. Maximum 30 claims per section. If there are more, prioritize:
   quantitative > comparative > causal > qualitative, and
   specific > vague.
2. Each claim must be independently understandable without reading the others.
3. Keep claims close to the source language — do not rephrase significantly.
4. For claim_type use exactly one of: "quantitative", "qualitative",
   "comparative", "causal".
5. approximate_location: copy the first ~10 words of the sentence that
   contains the claim. This helps locate it in the source text later.
6. Set total_claims to the number of claims in your list.
7. Set section_key to "{SECTION_KEY}".

## Output

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```
