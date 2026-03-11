# Investment Analysis Workbench

A Buffett-style investment analysis system powered by Claude Code agents. Each "umbrella" of analysis is handled by a specialized agent role, producing structured markdown and JSON reports.

## Philosophy

This framework is built around a simple idea: **buy a wonderful business at a sensible price, with high confidence you understand it.** If you don't have that confidence, the right move is to do nothing.

The analysis is organized into 8 umbrellas, each answering a core question:

| # | Umbrella | Core Question |
|---|----------|---------------|
| 1 | Circle of Competence | Can you explain how this business makes money in plain language? |
| 2 | Durable Competitive Advantage | Why will this company still be strong in 10 years? |
| 3 | Management & Capital Allocation | Do they act like owners? |
| 4 | Business Economics | High, stable returns on capital -- not just growth? |
| 5 | Balance Sheet Safety | Can it survive a bad 2-3 years without raising money? |
| 6 | Valuation vs Intrinsic Value | What is it worth based on owner earnings? |
| 7 | Margin of Safety | Is there a gap between price and conservative value? |
| 8 | Temperament & Time Horizon | If it drops 30% but the business is intact, do you panic? |

Plus a **compact checklist** -- 8 forced sentences every investor should be able to recite about any position they own.

## Commands

### Option 1: Inside Claude Code (Primary)

Open this project in Claude Code and say natural phrases. Claude Code dispatches the correct pipeline stage automatically.

```
# Full pipeline: universe → candidates → triage → analyze
run scan
triage latest
analyze AAPL

# Individual stages
run A1
run A2
run B1
run B2
triage 2026-03-11
analyze MSFT
```

### Option 2: Shell Script (Batch/CI)

```bash
# Build universe and filter candidates (A1 + A2)
./run.sh scan

# Triage candidates (B1 + B2, ≤8 deep_dives)
./run.sh triage latest
./run.sh triage 2026-03-11

# Full 8-umbrella analysis for a ticker
./run.sh analyze AAPL

# Change detection — not yet implemented
./run.sh monitor AAPL
```

Requires `claude` CLI installed and authenticated.

## Pipeline

```
scan         →  scans/YYYY-MM-DD/universe.json          (A1: raw universe)
             →  scans/YYYY-MM-DD/candidates.json         (A2: filtered + ranked)

triage       →  triage/YYYY-MM-DD/b1-advance.json        (B1: advance set)
             →  triage/YYYY-MM-DD/triage.json             (B2: ≤8 deep_dives + monitor)

analyze      →  reports/TICKER/FINAL-REPORT.md            (narrative report)
             →  reports/TICKER/FINAL-REPORT.json           (structured summary)

queue        →  queue/queue.json                          (living state — updated by triage + analyze)
```

## Adding Context

Place supporting documents in `context/{TICKER}/` before running:

```
context/AAPL/
  10k-notes.md
  q4-earnings-transcript.md
  financials.md
  competitor-analysis.md
```

Agents will read these files and incorporate them into the analysis. More context = better analysis. Without context, agents use web search and training knowledge.

## Output Structure

```
reports/AAPL/
  01-circle-of-competence.md
  02-durable-competitive-advantage.md
  03-management-capital-allocation.md
  04-business-economics.md
  05-balance-sheet-safety.md
  06-valuation-intrinsic-value.md
  07-margin-of-safety.md
  08-temperament-time-horizon.md
  09-compact-checklist.md
  FINAL-REPORT.md              <- narrative report
  FINAL-REPORT.json            <- structured summary (verdict, scores, flags, triggers)
```

Every section (01-08) follows the same format:
- **Key Findings** table with significance ratings
- **Detailed Analysis** (3-6 paragraphs, plain language)
- **Signal Summary** (bull/bear case, confidence level)
- **Red Flags**
- **Score** (1-10)

The **FINAL-REPORT.md** includes:
- Verdict: **Own / Watch / Pass**
- Score dashboard (all 8 umbrella scores)
- Compact checklist (8 forced sentences)
- Full analysis sections
- Buy/sell triggers

The **FINAL-REPORT.json** includes the same data in structured form: umbrella scores, key strengths, key risks, red flags, buy/sell triggers, valuation summary. Used by the queue and future monitor/diff engine.

## Research Queue

`queue/queue.json` tracks the state of every ticker the pipeline has touched.

States: `inbox` / `triage` / `watchlist` / `deep_research` / `approved` / `owned` / `monitor_only` / `rejected`

The queue is updated automatically after triage (B2) and after analyze (assembler). `approved` and `owned` states require manual update.

Human-readable view: `queue/queue.md`

## Verdicts

- **Own** -- Average score >= 7, no individual score below 4, margin of safety >= 6. A business you'd own for 5+ years.
- **Watch** -- Average score 5-7 or one critical weakness. Interesting but needs a better price or more conviction.
- **Pass** -- Average score < 5, multiple weak scores, or thin margin of safety. Don't understand it, not good enough, or too expensive.

## Customization

- Edit `prompts/_shared-format.md` to change the output format for all agents
- Edit individual prompt files to adjust sub-questions or scoring rubrics
- Add domain-specific prompts for sectors you analyze frequently

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- For shell script mode: `claude` available in PATH

## Important Disclaimer

This is an analysis framework, not financial advice. The system helps you think through investments systematically -- it does not tell you what to buy or sell. All analysis is generated by AI and may contain errors. Always do your own research and consult qualified professionals before making investment decisions.
