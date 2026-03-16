# Stage B1: Fast Triage — Execution Template

Stage B1 is a mechanical filter pass. Your job is to eliminate obvious no's quickly and surface the names worth a second look. This is not analysis — it is sorting. Speed and harshness are the point.

One question per name: **Is this worth a second look?**

---

## Do Not Use the Stage C Framework

The umbrella prompts (01–09) and `assembler.md` define how deep-dive analysis is conducted in Stage C. **Do not apply their criteria, scoring logic, or evaluation structure here.** B1 uses only the simple advance/hold/reject rules defined in this prompt. No umbrella writeups, no valuation math, no circle-of-competence scoring.

---

## Inputs

1. **Candidates** — read `runs/{CURRENT_WEEK}/scan/candidates.json` directly
2. Agent's own knowledge of these businesses — no web search

---

## WebSearch Rule

**None.** B1 uses only the A2 fields and your prior knowledge. If you need web search to make a call, that name belongs in `hold`, not `advance`.

---

## B1 Verdict Values

- `advance` — quality business, moat demonstrable (you can name it and believe it's durable), not obviously mispriced or broken; worth a real second look in B2
- `hold` — passes basic quality bar but: already monitored with no change, expensive with no catalyst, thin signal, or low confidence in your own judgment; park it (auto-becomes `inbox` — never enters B2)
- `reject` — any of: pre-profit / speculative without a clear moat, extreme leverage, pure commodity, capital destroyer, previously analyzed with Pass verdict and nothing has changed, circle of competence too narrow to form a view

---

## Decision Guidance

**Reject fast if:**
- No durable competitive advantage visible
- Revenue-stage or pre-profit without a clear, near-term path
- Net debt so large that FCF is consumed by debt service (not owner earnings)
- Commodity business with no pricing power
- Already analyzed, verdict was Pass, and you see no thesis change
- You genuinely don't understand what they sell or to whom

**Hold if:**
- Business is fine but you have no reason to act now (already in monitor, expensive, no catalyst)
- Thin or conflicting signal from A2 — not confident enough to advance or reject
- Mid-tier quality that would only be interesting at a very different price

**Advance if:**
- Quality business you'd want to think harder about
- **Demonstrable moat** you can name and believe is durable (not just "it seems like a good business")
- Not obviously overpriced or broken
- You haven't analyzed it recently, or something material has changed

**Soft cap:** Target 15–25% of candidates as `advance`. Soft cap: 50 names maximum. If your advance list exceeds 50, demote the least-certain names to `hold`.

---

## B1 Record Schema

One record per candidate. All fields required.

```json
{
  "ticker": "MSFT",
  "company": "Microsoft Corp.",
  "b1_verdict": "advance",
  "b1_reason": "dominant moat, FCF machine, not yet analyzed"
}
```

- `b1_verdict`: `advance` | `hold` | `reject`
- `b1_reason`: ≤ 12 words — the single deciding factor
  - For `advance`: why it clears the bar
  - For `hold`: what's blocking it
  - For `reject`: the disqualifier

---

## Output Requirements

- One record per candidate — every name from candidates.json must appear
- No essays. No scores. No valuation math. No sector breakdowns.
- JSON is source of truth
- Hold names do not appear in b1-advance.json. They auto-become `inbox` (queue state) and skip B2 entirely.
- If every candidate is `hold` or `reject`, `b1-advance.json` **must still be written as an empty array** (`[]`), not omitted. Zero advances is a valid outcome — the pipeline will skip Stage B2 cleanly.

---

## Output Files

Write to the current week's triage directory:

```
runs/{CURRENT_WEEK}/triage/b1-results.json    all records (advance + hold + reject)
runs/{CURRENT_WEEK}/triage/b1-advance.json    advance survivors only — input for B2
runs/{CURRENT_WEEK}/triage/b1-summary.md      compact table + counts
```

Create the directory if it does not exist.

---

## b1-summary.md Structure

1. **Counts** — total / advance / hold / reject
2. **Advance list** — one line per name: `TICKER | company | b1_reason`
3. **Hold list** — one line per name: `TICKER | company | b1_reason`
4. **Reject list** — one line per name: `TICKER | company | b1_reason`

No prose beyond the table. This file is a scan aid, not a report.
