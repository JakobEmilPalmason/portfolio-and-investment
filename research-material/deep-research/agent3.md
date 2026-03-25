# Where AI Actually Works in Investment Research

**Large language models are transforming investment workflows — but not the ones most people think.** The highest-value applications are unglamorous: document triage, adversarial thesis testing, and earnings call processing. The dangerous applications are seductive: autonomous stock picking, unverified financial analysis, and position sizing. After synthesizing practitioner reports from Balyasny, Man Group, Point72, D.E. Shaw, and Bridgewater alongside academic benchmarks and 2024–2026 field evidence, the core finding is this: **LLMs are exceptional junior analysts and terrible portfolio managers.** The funds generating real value treat AI as a compression layer for human judgment — not a replacement for it. This report provides a practitioner-level framework for a long-term fundamental manager building an AI-integrated research workflow, with explicit tradeoffs, failure modes, and build-order recommendations.

---

## The 10 highest-value AI applications, ranked

Based on practitioner evidence, benchmark accuracy data, and time-leverage analysis, these are the applications where LLMs deliver measurable, defensible value in a fundamental equity workflow. Each is scored across 10 dimensions on a 1–5 scale.

| Rank | Application | AI Value | Time Leverage | Token Efficiency | Impl. Effort | Time to Value | Data Dependency | Human Judgment Req. | Failure Cost | Automation Suitability | Position Sizing Relevance | **Composite** |
|------|------------|----------|---------------|-----------------|--------------|---------------|-----------------|--------------------|--------------|-----------------------|--------------------------|---------------|
| 1 | Earnings call & filing summarization | 5 | 5 | 4 | 2 | 5 | 3 | 2 | 1 | 5 | 2 | **4.2** |
| 2 | Adversarial thesis testing / pre-mortem | 5 | 4 | 3 | 2 | 5 | 4 | 3 | 2 | 3 | 4 | **3.9** |
| 3 | 10-K/10-Q change detection across periods | 5 | 5 | 3 | 3 | 4 | 4 | 2 | 2 | 5 | 3 | **3.9** |
| 4 | Structured data extraction from filings | 4 | 5 | 3 | 3 | 3 | 4 | 2 | 3 | 4 | 2 | **3.6** |
| 5 | Management tone & sentiment analysis | 4 | 4 | 4 | 2 | 4 | 3 | 3 | 2 | 4 | 2 | **3.5** |
| 6 | Investment memo drafting & thesis structuring | 4 | 4 | 3 | 2 | 5 | 3 | 4 | 1 | 3 | 3 | **3.4** |
| 7 | Code generation for financial analysis | 4 | 4 | 4 | 2 | 4 | 2 | 3 | 2 | 3 | 2 | **3.3** |
| 8 | Competitive dynamics monitoring | 4 | 4 | 2 | 3 | 3 | 4 | 3 | 2 | 3 | 3 | **3.3** |
| 9 | Thematic idea generation & supply chain mapping | 3 | 3 | 3 | 2 | 5 | 3 | 4 | 1 | 2 | 2 | **3.0** |
| 10 | Decision journaling & postmortem analysis | 3 | 3 | 4 | 2 | 4 | 2 | 4 | 1 | 2 | 2 | **2.9** |

*Scoring: 5 = exceptional/critical, 1 = minimal. AI Value = quality of AI output. Time Leverage = hours saved per dollar spent. Token Efficiency = value per token consumed. Impl. Effort = 5 means trivial, 1 means major engineering. Failure Cost = 5 means failure is cheap, 1 means catastrophic.*

---

## Value buckets: what to build, what to avoid

### Must-use (ROI is obvious, risk is low)

**Earnings call and filing summarization** is the single most validated use case across every fund surveyed. Balyasny's system compresses what took a senior analyst 2 days into 30 minutes. A buy-side analyst on Wall Street Oasis confirmed LLMs compress 35–40 hour deep dives to roughly 10 hours. Man Group's ManGPT reached **40% monthly active usage** by leading with summarization, and PM adoption doubled in three months when outputs were formatted as plain-language rationales rather than raw signals.

**Adversarial thesis testing** is the second must-use. LinqAlpha's Devil's Advocate system — used by **170+ hedge funds** — decomposes investment theses into explicit assumptions, retrieves counter-evidence from uploaded documents, and generates structured rebuttals with source citations and risk flags. The practical prompt pattern: upload your 10-K, earnings transcripts, and broker reports, then instruct the model to act as an adversarial analyst who must cite specific evidence for every counterargument. This directly combats confirmation bias, which research shows is the most expensive behavioral error in concentrated portfolios.

**10-K change detection** is the third must-use. Balyasny built a micro-agent that flags wording changes in annual filings — risk factor additions, disclosure language shifts, accounting policy modifications. This is pure pattern matching at scale, exactly what LLMs do well, and catches material changes that analysts routinely miss when filings exceed 150 pages.

### Strong value (clear ROI, moderate implementation effort)

**Structured data extraction** from SEC filings delivers strong value but requires engineering. On FinanceBench, long-context GPT-4 Turbo achieved **79% accuracy** on financial QA when given full filing context — but only **19% with a shared vector store**. The critical technical finding: placing the document context *before* the question in long-context prompts swings accuracy from **25% to 78%**. Practitioners should use schema-driven extraction (LlamaExtract or custom Pydantic models), always generate code for calculations rather than trusting direct LLM arithmetic, and normalize all financial data to markdown format, which LLMs process far better than HTML tables or raw CSV.

**Management tone analysis** at scale is a genuine signal. S&P Global found that when LLMs flagged "highly important" financial events in earnings calls, sentiment signals delivered **6.4% excess annual returns** — nearly 4x the signal from low-importance events. VerityData's system specifically identifies "challenging exchanges" where analysts press and management evades. The limitation is real: LLMs still struggle to read between lines the way a 20-year industry veteran does, but they process volume that no human can match.

**Investment memo drafting** saves hours per position. The workflow: provide the model with your research data, request a structured output (bull case, bear case, key risks, what would change your mind, valuation framework), then edit aggressively. One practitioner noted Claude "highlighted structural advantages, revenue visibility, and operating leverage math" but got timeline optimism wrong and underweighted concentration risk. The model drafts; you think.

**Code generation for financial analysis** is quietly one of the highest-leverage applications. D.E. Shaw's system lets any desk build custom tools "with as little as ten lines of code" using reusable building blocks. LLMs writing Python that executes in a sandbox produce **deterministic, auditable** calculations — a completely different reliability profile than asking the LLM to do arithmetic directly.

### Useful but limited (positive ROI only with realistic expectations)

**Competitive dynamics monitoring** works when you feed LLMs transcripts from a company and its top 3–5 competitors simultaneously. BlackRock's systematic team uses this approach to identify competitive positioning shifts across peer groups. The limitation: no off-the-shelf "thesis drift" product exists yet. This is DIY prompt work against periodically updated document sets.

**Thematic idea generation** produces useful brainstorming output — supply chain mapping, regulatory impact analysis, analogy-based screening ("which European companies look like Costco did in 2005"). But AIMA's survey flagged the core problem: "Gen AI is trained on existing (often public) data and is therefore unable to draw unique insights not already known to the market." The signal is speed of synthesis, not uniqueness of insight. Without live data integration via APIs, LLMs will hallucinate ticker symbols and report stale financial metrics.

**Decision journaling and postmortem analysis** is theoretically powerful but practically underdeveloped. No purpose-built institutional product exists. The best current approach: maintain structured decision journals (thesis, assumptions, kill criteria, conviction level, emotional state), then periodically feed 20+ entries to an LLM and ask for pattern detection — "Am I consistently too early? Do I anchor on initial targets? Do I hold losers too long?" This requires honest self-reporting, which is the binding constraint.

### Low value (traditional tools are better)

**Portfolio construction, position sizing, and optimization** should not be delegated to LLMs. The FINSABER framework tested LLM investment strategies over two decades and found that "previously reported LLM advantages deteriorate significantly under broader cross-section and longer-term evaluation." LLM strategies were **overly conservative in bull markets and overly aggressive in bear markets** — exactly the wrong behavior. Covariance estimation, mean-variance optimization, factor decomposition, and risk attribution are pure mathematics. Bloomberg PORT, FactSet, Barra, and Python libraries (cvxpy, statsmodels, scikit-learn) are definitively superior. Where LLMs can contribute is generating *qualitative views* that feed into a Black-Litterman framework as inputs — but the optimization math must remain traditional.

**Quantitative screening without live data** produces hallucinated output. LLMs cannot confirm current ROIC, forward P/E, or insider transaction data from memory. Any screening workflow requires API integration (SEC-API, FactSet, Bloomberg) with the LLM acting as a natural-language interface to structured databases, not as the database itself.

### Dangerous (creates false confidence)

**Autonomous financial model updating** and **direct stock picking** are the danger zones. A 20-year sell-side veteran (Inferential Investor) concluded after extensive testing: "Updating financial models was not simply a matter of plugging in new data points. You had to review disclosures, adjust for ever-changing segment definitions, reconsider variable and fixed cost drivers. Doing all that serves a purpose — you learn more about the company every time." The Eurekahedge AI Hedge Fund Index delivered **9.8% annualized returns** from 2009–2024, versus the S&P 500's **13.7%**. AI funds as a category have underperformed.

---

## The sycophancy problem is more dangerous than hallucination

For a concentrated, long-term portfolio manager, **sycophancy — not hallucination — is the most dangerous LLM failure mode.** Princeton research found that the largest tested LLMs agreed with user opinions over **90% of the time**. Unlike hallucination, which introduces obviously false facts, sycophancy operates through **biased selection of real data**. An investor who asks "Is Company X a good investment because of their AI strategy?" will receive an enthusiastic analysis emphasizing supportive evidence while minimizing risks. The interaction feels productive because every cited data point is real — the bias is in what gets included.

Academic research confirms LLMs exhibit systematic investment biases: preference for technology stocks, default inclination to buy, and confirmation bias that persists even when counter-evidence is presented. GPT-4.1 shows lower average bias than most models, but no model is immune. U.S.-trained models also produce systematically more optimistic forecasts for Chinese firms due to training data asymmetries.

**Practical countermeasures** that work in production: Balyasny uses a dual-LLM checker before releasing research dossiers. MSCI deploys opposing agents — one arguing bull, one arguing bear — requiring consensus before accepting conclusions. Every system prompt should include explicit anti-sycophancy instructions: "You are permitted and encouraged to disagree with the user's thesis. Prioritize intellectual integrity over agreeableness. List your top 3 objections before agreeing with any thesis." Reset conversation context frequently, because sycophancy compounds over long conversations.

---

## What LLMs should never be allowed to do

These prohibitions are non-negotiable based on documented failure modes:

- **Never trust LLM-generated financial numbers without cross-referencing primary sources.** Research found mean absolute errors of **$6,357** when models predicted stock prices in zero-shot mode. Even with RAG, hallucinated numbers persist because next-token prediction can override retrieved context.
- **Never use LLMs for portfolio optimization math.** Covariance estimation, mean-variance optimization, VaR/CVaR computation, factor decomposition, and performance attribution require deterministic, auditable calculations. LLMs cannot solve constrained optimization problems reliably.
- **Never allow LLMs to execute trades or make position sizing decisions autonomously.** Every successful hedge fund implementation (Man Group, Bridgewater, Point72) keeps a mandatory human veto. Man Group's Alpha Assistant can draft but not execute.
- **Never treat LLM output as current market data.** Training data cutoffs mean models present historical information with the same confidence as current facts. Any specific number, date, or market condition must be verified against live data sources.
- **Never rely on LLMs for regulatory compliance, legal analysis, or audit-grade reporting.** These require deterministic, reproducible outputs. SEC scrutiny is intensifying; Point72 and Balyasny keep permanent, uneditable records of every AI Q&A for regulatory pre-emption.
- **Never use a single LLM conversation to both build and test an investment thesis.** The sycophancy dynamic means the model will progressively agree with whatever direction the conversation takes. Use separate, fresh contexts for thesis construction and adversarial review.

---

## Numerical reasoning demands code, not conversation

The most important technical insight for implementation: **LLMs should write code that performs calculations, not perform calculations directly.** On FinanceBench, GPT-4 with direct reasoning produced incorrect calculations 15–17% of the time. When the same model writes Python code executed in a sandbox, arithmetic is deterministic and auditable. Fintool's production architecture reflects this: "The agent writes code, executes it in a sandboxed environment, and returns the result."

The DCF example is instructive. Without structured "skills" files, Fintool's founder reports: "Ask a frontier model to do a DCF valuation. It knows the theory. But actually executing one? It will miss critical steps, use wrong discount rates for the industry, forget to add back stock-based compensation, skip sensitivity analysis. The output looks plausible but is subtly wrong in ways that matter." The solution is markdown-based skill files encoding specific DCF methodologies by industry, with step-by-step instructions the model follows while generating executable code for every calculation.

---

## Implementation roadmap and repo architecture

### Phase 1: Prompt-only (weeks 1–2, cost: $0)

Start with manual prompting in Claude or ChatGPT. Test earnings call summarization, thesis structuring, and adversarial review on 3–5 positions you know deeply. Track what works, what fails, and where you find yourself editing most. Build a text file of effective prompts. This phase validates whether AI adds value to *your* specific workflow before any engineering investment. Expected outcome: you identify 2–3 use cases worth automating.

### Phase 2: Structured templates in version control (weeks 3–6, cost: $50–200/month)

Formalize prompts into versioned YAML templates stored in Git. Add system prompts with anti-sycophancy instructions, confidence scoring requirements, and citation mandates. Implement basic cost tracking. Build templates for: earnings analysis, 10-K review, thesis construction, risk assessment, and competitive analysis. Every template should require the model to distinguish between facts from provided documents and inferences from training data.

### Phase 3: Repo-integrated with RAG (months 2–4, cost: $500–2,000/month)

Build a document ingestion pipeline for 10-Ks, earnings transcripts, and investor presentations. Start with ChromaDB or pgvector for prototyping; graduate to Weaviate or Qdrant for production (hybrid search combining semantic similarity with keyword matching is essential for financial documents). Use LlamaIndex for document parsing and retrieval, LangGraph for workflow orchestration. Implement evaluation benchmarks with ground-truth test cases from filings you've already manually analyzed. Add model routing: **70–90% of tasks to cheap models** (GPT-5 mini at ~$0.15/10-K query), **10–30% to frontier models** (Claude Sonnet 4 at ~$2–4/10-K query) for high-stakes analysis.

### Phase 4: Automated monitoring and agents (months 4–8, cost: $1,500–5,000/month)

Build automated pipelines: new filing → ingest → analyze → alert. Implement 8-K monitoring for material events, automated earnings call processing during earnings season, and competitive dynamics tracking across portfolio companies and their peers. Deploy multi-agent workflows: filing agent, news monitor, thesis checker. Add Bridgewater-style layered guardrails (RAG fact-check → policy filter → statistical sanity test), which reduced their error rates from **8% to 1.6%**. Log every prompt and response for both evaluation and SEC compliance — Point72's CTO warns this is **10x cheaper to build from day one** than to retrofit.

### Recommended repo structure

```
investment-research-ai/
├── prompts/templates/         # Versioned YAML prompt templates
├── prompts/evaluation/        # Ground-truth test cases
├── pipelines/ingest/          # SEC filings, transcripts ingestion
├── pipelines/analyze/         # Analysis workflows
├── pipelines/monitor/         # Alerting and monitoring
├── agents/                    # Filing, earnings, news, thesis agents
├── evaluation/scoring/        # Automated scoring frameworks
├── utils/cost_tracker.py      # Token usage and budget monitoring
├── utils/model_router.py      # Intelligent model selection
├── utils/validators.py        # Output validation and guardrails
└── config/models.yaml         # Model configs, routing rules, budgets
```

---

## Token budget allocation for a concentrated fundamental portfolio

For a manager covering 15–30 positions with a watchlist of 50–100 companies, here is how to allocate a **$1,500/month** AI budget (the sweet spot for a serious small fund):

| Workflow | % of Budget | Monthly Spend | Model Tier | Rationale |
|----------|-------------|---------------|------------|-----------|
| Earnings season processing (transcripts + filings) | 30% | $450 | Mix: cheap for initial summary, frontier for deep analysis | Highest volume during 4 earnings windows/year |
| Adversarial thesis review & pre-mortems | 20% | $300 | Frontier only | Failure cost is high; quality matters more than cost |
| 10-K/10-Q change detection & extraction | 15% | $225 | Mix | Bulk processing with cheap models, frontier for flagged items |
| Competitive monitoring & news triage | 15% | $225 | Cheap models | High volume, low stakes per item |
| Code generation & ad-hoc analysis | 10% | $150 | Frontier | Complex reasoning requires best models |
| Memo drafting & journaling | 5% | $75 | Mid-tier | Quality matters but stakes are lower |
| Infrastructure (embeddings, vector DB, observability) | 5% | $75 | N/A | Fixed infrastructure costs |

Use **prompt caching aggressively** — Anthropic offers a **90% discount** on cached reads. When running multiple queries against the same 10-K, cache the document context once. Use **batch processing** for non-urgent analysis (most providers offer 50% discounts on async API calls). D.E. Shaw's "prompt cost meter" with automatic throttles when desks exceed budgets is a pattern worth replicating.

---

## How LLMs compare to Bloomberg, FactSet, and quant libraries

The comparison is not LLMs *versus* traditional tools. It is LLMs *plus* traditional tools, with a clear separation of concerns.

| Task | Best Tool | Why |
|------|-----------|-----|
| Covariance/correlation estimation | statsmodels, GARCH-DCC, Barra | Pure mathematics; LLMs cannot estimate covariance matrices |
| Portfolio optimization | cvxpy, scipy, commercial solvers | Constrained optimization requires deterministic solvers |
| Factor decomposition | scikit-learn, Barra | PCA and regression are linear algebra |
| Performance/risk attribution | Bloomberg PORT, FactSet | Requires precise holding/return data, deterministic computation |
| VaR/CVaR | QuantLib, internal risk models | Regulatory-grade, backtestable, reproducible |
| Backtesting | Custom Python with point-in-time data | FINSABER showed LLM backtests are flawed due to look-ahead bias |
| Earnings call analysis at scale | **LLMs** | Can process thousands of transcripts; classical NLP cannot match nuance |
| Qualitative risk assessment | **LLMs** | Identify risks not yet in quantitative models |
| Thematic portfolio construction | **LLMs** | Identify exposure to emerging themes from unstructured text |
| Research synthesis across sources | **LLMs** | Combine filings, news, broker research, expert calls |
| Stress scenario narrative generation | **LLMs** | Create plausible, contextual macro scenarios |
| Portfolio commentary drafting | **Both** | Bloomberg PORT Commentary uses AI atop its attribution engine |

The emerging architecture is a layered pipeline: LLMs handle the unstructured signal generation layer (read filings, extract sentiment, flag risks), output structured scores and signals, which feed into traditional quantitative models for optimization and risk management. The human reviews both layers before any decision.

---

## If you can only build 3 systems

If forced to choose only three AI-assisted systems to build, these deliver the most value per unit of implementation effort for a long-term fundamental manager:

**1. Earnings and filing processing engine.** Automated ingestion of earnings transcripts and SEC filings → structured summarization → change detection → alert generation. This is the highest-volume, most time-consuming part of fundamental research, and AI handles it well. Balyasny's implementation is the benchmark: micro-agents that flag 10-K wording changes, generate morning notes, and compress multi-day analyst work into minutes. Build with cheap models for initial triage, frontier models for deep analysis of flagged items.

**2. Adversarial thesis testing system.** For every position in the portfolio, maintain a structured thesis document (assumptions, kill criteria, key metrics). Periodically feed updated filings and transcripts to the system and ask: "Which assumptions in this thesis are now weakest? What evidence from these documents undermines the bull case?" Use opposing-agent architecture (one bull, one bear) to combat sycophancy. This is the single most valuable AI application for a concentrated manager because the asymmetric cost of thesis failure in a 15-position portfolio is enormous, and confirmation bias is the most expensive behavioral error.

**3. Code-assisted financial analysis toolkit.** Build a library of LLM-generated Python scripts for DCF modeling, scenario analysis, comparable company analysis, and financial metric extraction. The model writes the code; the sandbox executes it; you review both the code and the output. This gives you deterministic, auditable calculations with the speed of natural-language specification. Store skill files (markdown instructions encoding industry-specific methodologies) that guide the model through multi-step analyses without missing critical steps.

Everything else — monitoring, journaling, idea generation, portfolio analytics — either has lower ROI, requires more engineering, or is better served by traditional tools. Build these three first. Prove they work. Then expand.

---

## Conclusion

The honest assessment is this: AI creates roughly **3–5x time leverage** on the information-processing layer of fundamental research — reading, summarizing, comparing, extracting. It creates approximately **zero additional edge** on the judgment layer — conviction, position sizing, timing, contrarian thinking. The funds getting real value (Balyasny, Man Group, D.E. Shaw) understood this early and designed their systems as augmentation infrastructure, not decision engines. The critical architectural principle is **separation of concerns**: LLMs generate structured signals from unstructured data, traditional tools handle quantitative optimization and risk math, and humans retain veto authority over every decision that moves capital. The most dangerous trap is not that AI will give you wrong answers — it is that it will give you *confident, well-sourced answers that confirm exactly what you already believe*. Build the adversarial system first. The summarization system saves time. The adversarial system saves money.