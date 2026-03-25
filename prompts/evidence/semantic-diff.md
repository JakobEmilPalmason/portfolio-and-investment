# Evidence Extraction — Semantic Diff: Cross-Period Comparison

You are comparing two versions of the same SEC filing section across
filing periods. Your job is to identify **material changes** — not
cosmetic rewording.

**Section:** {SECTION_KEY}
**Ticker:** {TICKER}
**Period A:** {PERIOD_A}
**Period B:** {PERIOD_B}

## What counts as a material change

- A new risk factor not present in the earlier period
- A risk factor that was removed or significantly de-emphasized
- A quantitative claim that changed (revenue figure, margin, growth rate)
- A change in management tone (cautious → confident, or the reverse)
- New or changed forward-looking guidance
- A business model shift (new segment, discontinued operation, M&A mention)
- A change in key assumptions or accounting treatment

## What does NOT count

- Minor rewording that preserves the same meaning
- Reordering of paragraphs without substantive change
- Updated dates or period references (e.g., "fiscal 2024" → "fiscal 2025")
- Boilerplate legal language updates
- Formatting or structural changes

## Rules

1. Compare the two section texts provided below.
2. For each material change, classify it by `change_type` and `category`.
3. Include a brief `quote_a` (from period A) and `quote_b` (from period B)
   to anchor the change. Use verbatim excerpts, max ~100 characters each.
   Leave `quote_a` empty for `added` changes; leave `quote_b` empty for
   `removed` changes.
4. Score `significance` on a 1-5 scale:
   - 1 = cosmetic rewording (should rarely appear — skip these)
   - 2 = minor factual update (e.g., employee count changed)
   - 3 = notable shift (e.g., new risk category, guidance range moved)
   - 4 = material change (e.g., significant margin compression, new regulatory threat)
   - 5 = fundamental shift (e.g., business model pivot, major acquisition, going-concern flag)
5. Maximum 15 changes per section. Prioritize by significance.
6. **If the sections are substantially identical, return an empty changes
   array. Do not invent differences.**
7. Set `section_key` to "{SECTION_KEY}".

## Output

Return ONLY valid JSON matching this schema (no markdown fences, no preamble):

```json
{JSON_SCHEMA}
```

---

PERIOD A TEXT ({PERIOD_A}):

{TEXT_A}

---

PERIOD B TEXT ({PERIOD_B}):

{TEXT_B}
