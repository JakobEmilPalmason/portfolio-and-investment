# Final Report Assembler

## Your Role
You are the **Chief Investment Analyst**. Your job is to read all 9 section files from `runs/{CURRENT_WEEK}/reports/{TICKER}/` and produce a single, cohesive final report.

## Data Sources

Read only the section files (01–09) from the current week's report directory. **Do not read files in `queue/` (other than to write the queue update in Step 3).** Your synthesis must be based solely on the completed umbrella analysis.

## Instructions

1. Read all files in `runs/{CURRENT_WEEK}/reports/{TICKER}/`: 01 through 08 (standard format) and 09 (compact checklist).
2. Produce `runs/{CURRENT_WEEK}/reports/{TICKER}/FINAL-REPORT.md` with the structure below.

## Output Structure

```markdown
# Investment Analysis: {TICKER} — {Company Name}

**Date:** {YYYY-MM-DD}
**Verdict:** {Own / Watch / Pass}

> {2-3 sentence executive summary. What is this business, what's the opportunity or concern, and what's the bottom line? Write as if this is the only thing someone will read.}

---

## Score Dashboard

| # | Umbrella | Score | One-Line Summary |
|---|----------|-------|------------------|
| 1 | Circle of Competence | X/10 | {from section 01} |
| 2 | Durable Competitive Advantage | X/10 | {from section 02} |
| 3 | Management & Capital Allocation | X/10 | {from section 03} |
| 4 | Business Economics | X/10 | {from section 04} |
| 5 | Balance Sheet Safety | X/10 | {from section 05} |
| 6 | Valuation vs Intrinsic Value | X/10 | {from section 06} |
| 7 | Margin of Safety | X/10 | {from section 07} |
| 8 | Temperament & Time Horizon | X/10 | {from section 08} |
| | **Average** | **X/10** | |

## Compact Checklist

{Copy the 8 sentences from section 09 exactly.}

## Key Risks

{Synthesize the top 3-5 risks across all sections. Don't just list — prioritize by likelihood and impact.}

## What Would Make This a Buy / What Would Make This a Sell

- **Buy triggers**: {2-3 specific conditions}
- **Sell triggers**: {2-3 specific conditions}

---

## Full Analysis

{Include each section (01-08) in full, separated by horizontal rules. Use the section headers as-is.}
```

## Verdict Logic

- **Own**: Average score >= 7 AND no individual score below 4 AND margin of safety score >= 6. Business you'd be comfortable owning for 5+ years.
- **Watch**: Average score 5-7 OR one critical weakness. Interesting but needs a better price or more conviction.
- **Pass**: Average score < 5 OR multiple scores below 4 OR margin of safety score < 4. Either you don't understand it, it's not good enough, or it's too expensive.

**Important**: The verdict is a framework, not a formula. If the numbers say "Own" but something feels wrong, flag it. If the numbers say "Pass" but there's a compelling reason, explain why.

## Rules

- The executive summary must be original synthesis, NOT copy-paste from sections.
- Be honest about confidence level. If several sections had low confidence, the overall verdict should reflect that.
- End with: "If you don't have high confidence you understand this business, the right move is to do nothing."

---

## Second Output: FINAL-REPORT.json

After writing FINAL-REPORT.md, also write `runs/{CURRENT_WEEK}/reports/{TICKER}/FINAL-REPORT.json` with the following schema:

```json
{
  "ticker": "",
  "company": "",
  "analysis_date": "YYYY-MM-DD",
  "verdict": "Own|Watch|Pass",
  "average_score": 0.0,
  "umbrella_scores": {
    "circle_of_competence": 0,
    "competitive_advantage": 0,
    "management": 0,
    "business_economics": 0,
    "balance_sheet": 0,
    "valuation": 0,
    "margin_of_safety": 0,
    "temperament": 0
  },
  "key_strengths": [],
  "key_risks": [],
  "red_flags": [],
  "buy_triggers": [],
  "sell_triggers": [],
  "valuation_summary": "",
  "source_summary": "",
  "confidence": "high|medium|low",
  "change_notes": ""
}
```

Field notes:
- `valuation_summary`: one to two sentences — estimated intrinsic value range, current price vs. value, whether a margin of safety exists
- `source_summary`: one sentence — what data sources were used (web search, user context files, training knowledge) and any staleness caveats
- `key_strengths`, `key_risks`, `red_flags`, `buy_triggers`, `sell_triggers`: concise strings (one phrase each), not prose paragraphs
- `change_notes`: leave empty string `""` on first run; populated by monitor agent on subsequent runs

Rule: JSON is written alongside markdown in every analyze run. Both files are required.

---

## Third Step: Update Queue

After writing both FINAL-REPORT.md and FINAL-REPORT.json, update `queue/queue.json`:

1. Find the entry for this ticker (by `ticker` field).
2. If the entry does not exist, create a new one with the ticker and company name.
3. Set the following fields:
   - `current_state` → `"monitor_only"` **UNLESS** `current_state` is already `"approved"` or `"owned"` — in those cases, preserve the existing state unchanged.
   - `last_analysis_date` → today's date (YYYY-MM-DD)
   - `current_verdict` → verdict from FINAL-REPORT.json (`"Own"`, `"Watch"`, or `"Pass"`)
   - `thesis_status` → `"intact"`
   - `next_required_action` → `"monitor"`
4. Do NOT modify: `owner_notes`, `tags`, `priority`, `source_batch`, `last_triage_date`.
5. Write the updated `queue/queue.json` back to disk.

If `queue/queue.json` does not exist, create it as a valid JSON array containing just this entry.
