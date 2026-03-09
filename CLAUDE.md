# Investment Analysis Workbench

This project is a Buffett-style investment analysis system powered by Claude Code agents. Each "umbrella" of analysis is handled by a specialized agent role, all following the same output format.

## How It Works

When a user asks to analyze a stock (e.g., "analyze AAPL" or "run analysis on MSFT"), follow this workflow:

### Step 1: Setup
1. Create directory `reports/{TICKER}/` if it doesn't exist.
2. Read `prompts/_shared-format.md` — this is the output schema all agents must follow.
3. Check if `context/{TICKER}/` exists. If it does, read all files in it — this is user-provided research (10-K notes, earnings transcripts, financials). Pass this context to every agent.

### Step 2: Run Analysis Agents (3 parallel batches)
Spawn 3 Agent subagents in parallel. Each agent gets:
- The shared format from `prompts/_shared-format.md`
- Its specific umbrella prompt(s) from `prompts/`
- The ticker symbol and today's date
- Any user-provided context files
- Instruction to use web search for current financial data

**Business Analyst Agent** (umbrellas 1-3):
- Read prompts: `01-circle-of-competence.md`, `02-durable-competitive-advantage.md`, `03-management-capital-allocation.md`
- Write output to: `reports/{TICKER}/01-circle-of-competence.md`, `reports/{TICKER}/02-durable-competitive-advantage.md`, `reports/{TICKER}/03-management-capital-allocation.md`

**Financial Analyst Agent** (umbrellas 4-5):
- Read prompts: `04-business-economics.md`, `05-balance-sheet-safety.md`
- Write output to: `reports/{TICKER}/04-business-economics.md`, `reports/{TICKER}/05-balance-sheet-safety.md`

**Valuation Analyst Agent** (umbrellas 6-8):
- Read prompts: `06-valuation-intrinsic-value.md`, `07-margin-of-safety.md`, `08-temperament-time-horizon.md`
- Write output to: `reports/{TICKER}/06-valuation-intrinsic-value.md`, `reports/{TICKER}/07-margin-of-safety.md`, `reports/{TICKER}/08-temperament-time-horizon.md`

Each agent should:
- Use **WebSearch** to find current financial data, recent news, and analyst estimates
- Follow the shared format EXACTLY for each section
- Write each section to its own file in `reports/{TICKER}/`
- Be honest about data sources and confidence levels

### Step 3: Compact Checklist
After all 3 agents complete, spawn one more agent:

**Checklist Agent** (umbrella 9):
- Read prompt: `09-compact-checklist.md`
- Read all completed sections from `reports/{TICKER}/` (01-08)
- Write output to: `reports/{TICKER}/09-compact-checklist.md`

### Step 4: Final Report Assembly
Spawn one final agent:

**Synthesis Agent**:
- Read prompt: `assembler.md`
- Read ALL section files from `reports/{TICKER}/` (01-09)
- Write output to: `reports/{TICKER}/FINAL-REPORT.md`

### Step 5: Present Results
After the final report is written, show the user:
1. The **verdict** (Own / Watch / Pass)
2. The **score dashboard** (table of all 8 scores)
3. The **compact checklist** (8 forced sentences)
4. Let them know the full report is at `reports/{TICKER}/FINAL-REPORT.md`

## Single Umbrella Mode
If the user asks to run just one umbrella (e.g., "run umbrella 3 on AAPL" or "just analyze management for TSLA"), run only that specific agent and write only that section file.

## Re-Assembly Mode
If the user asks to reassemble a report (e.g., "reassemble AAPL report"), run only Steps 3-4 using existing section files.

## Adding Context
Users can place supporting documents in `context/{TICKER}/` before running analysis:
- 10-K excerpts or notes
- Earnings call transcripts
- Custom financial spreadsheet exports
- Industry research
- Competitor analysis

The more context provided, the better the analysis. Without context, agents rely on web search and training knowledge.

## Philosophy
This is a Buffett-style analysis framework. Key principles:
- Business reality over market noise
- Not losing money over maximizing gains
- Understanding over complexity
- Patience over activity
- Honesty over conviction

If you don't have high confidence you understand the business, the right move is to do nothing.
