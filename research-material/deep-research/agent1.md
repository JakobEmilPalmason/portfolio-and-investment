# Where AI Is Actually Worth Using in an Investment Research and Portfolio-Construction Workflow

## A practical ROI lens for AI in investing
AI is most worth using when the work is **text-heavy, repetitive, and benefits from consistent structure**—and when you can force the model to stay tethered to **verbatim evidence**. It is least worth using when the work is **numerical, optimization-heavy, or requires calibrated probabilities**—because modern LLMs still produce **plausible, confident falsehoods** (“hallucinations”) and can be **poorly calibrated** about when they’re wrong.

Two facts should dominate your design choices:

- **Finance is long-context by nature, and LLM reliability degrades in long documents.** In a finance-specific benchmark for long-context hallucination detection, results highlight “severe challenges” for out-of-the-box models on long-context data, and the paper notes a typical 10‑K can exceed 100k tokens; it also describes the “lost in the middle” problem (relevant facts buried deep in long contexts) and shows performance degradation as context length grows (including near-collapse in recall for some open models beyond 20k tokens). 
 **Implication:** Spending huge prompts on entire filings is often *worse* than doing targeted retrieval + smaller evidence-grounded calls.

- **The cost of being wrong is asymmetric in investing, and AI errors are not transparent.** Hallucinations persist and are shaped by incentives: models “guess” under uncertainty because many evals reward it. This interacts badly with finance because confident narrative can raise conviction while quietly corrupting the analysis.

Regulators and standard-setters are effectively telling you the same thing in different language: **human oversight, governance, and model-risk controls matter**, and AI adoption can amplify vulnerabilities (model risk, data quality, cyber/fraud, correlated behavior, third‑party dependence).

A useful mental model for “AI ROI” in investing:

- **AI creates edge** when it helps you (a) see *more* relevant evidence than other humans can process, (b) maintain *better decision hygiene* (checklists, adversarial review, kill criteria), or (c) react *earlier* to material changes through monitoring—*without inventing facts*.
- **AI compresses labor** when it structures, summarizes, extracts, compares, drafts, and routes tasks—*but doesn’t magically improve the underlying truth*.
- **AI creates false confidence** when you let it (a) freewheel on numbers, (b) produce valuation outputs without verified inputs, (c) make macro calls, or (d) “sound smart” in areas where it has no ground truth access.

I will refer once (and only once) to key institutions whose published work strongly supports these points: on hallucinations, on model-risk governance, and / / / on AI risks in finance and controls.

## The top ten highest-value uses of AI in this workflow
These are ranked for **decision-quality ROI** (not novelty), factoring time leverage, token cost, and error risk.

1) **Evidence-grounded document extraction (filings/transcripts) into structured facts**
- Why it’s #1: It turns the “reading problem” into a database of citeable claims and metrics, which then powers everything else.
- Why it beats manual: Humans can’t scale to consistent, multi-company, multi-quarter extraction without missing things.

2) **Document comparison & change detection (quarter-to-quarter / call-to-call)**
- High ROI because “what changed?” is the real job after you establish a baseline.
- Best used as: delta summaries tied to source spans + a trigger system.

3) **Adversarial / bearish review with forced evidence**
- AI is unusually good at generating “attack surfaces”: missing risks, alternative explanations, base-rate failures, and disconfirming questions—*as long as you force citations and prohibit invention*.

4) **Build a “research QA” assistant over your own corpus (RAG over filings, transcripts, notes)**
- The practical edge is speed-to-evidence: “What did they say about pricing in 2022 vs 2025?” becomes a query, not a scavenger hunt.

5) **Monitoring after purchase: narrative + evidence compression**
- Ongoing ROI is high because it reduces the odds you sleepwalk into thesis drift, capacity creep, or slow fundamental deterioration.

6) **Competitor / industry mapping and comparison grids (evidence-tethered)**
- AI is strong at making consistent side-by-side comparisons from messy text sources—*if you standardize questions and pull evidence per company*.

7) **Research hygiene: converting messy thinking into structured artifacts**
- Examples: thesis ledger, driver tree, disconfirming evidence log, risk register, “kill criteria,” variant perception test.

8) **Idea filtering / triage from a large universe**
- Not “stock picking.” The value is eliminating obvious mismatches quickly and consistently, and routing attention.

9) **Scenario generation and second-order risk brainstorming**
- Useful for breadth (regimes, competitor reactions, margin structures, balance-sheet stress paths), not for “precise forecasting.”

10) **Journaling & postmortems over your own history**
- This is underrated: mining your past decisions for patterns (overconfidence, anchoring, ignoring base rates, position-size mistakes) has compounding payoff and low failure cost.

The big theme: AI is highest ROI where it can be **a disciplined analyst of text + a ruthless process enforcer**, and lowest ROI where it becomes a **numerical oracle**.

## Workflow scoring table
Scores are intentionally blunt. If you disagree, that’s good: it means you have a clear view of your own edge and constraints.

| task / umbrella | AI value score | time leverage | token efficiency | implementation sizing | time to value | data dependency | human judgment requirement | failure cost | automation suitability | position sizing relevance | short explanation |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| idea generation | 4 | medium | acceptable | tiny | immediate | low | high | medium | done ad hoc with prompts | affects “look / don’t look” more than size | Good for breadth and “what could be true.” Weak for edge; tends to produce consensus-y ideas unless seeded with differentiated constraints. |
| idea filtering / triage | 7 | high | good | medium | within days | high | medium-high | medium | fully systematized in a repo | affects whether you take a position at all (via attention allocation) | Strong use if you tie it to structured heuristics, red flags, and evidence checks; otherwise it becomes vibes-based filtering. |
| thesis formation | 6 | medium | acceptable | small | within days | medium-high | extremely high | high | semi-automated | affects whether you take a position; weak sizing signal | AI helps structure logic, drivers, and checklists. Dangerous if it “fills gaps” with invented claims. |
| adversarial / bearish review | 9 | high | good | medium | within days | high | high | high | fully systematized in a repo | affects take/no-take, max size, trim/exit triggers | One of the best uses: generate disconfirming questions, failure modes, base-rate analogs. Must force evidence and track unresolved risks. |
| document ingestion & extraction | 10 | extreme | excellent | large | within weeks | very high | medium-high | high | fully systematized in a repo | affects take/no-take; informs sizing indirectly | Best ROI if you implement retrieval + schema extraction + citations. Long-context “dump the PDF” approaches are brittle in finance. |
| research QA over your corpus (RAG) | 9 | extreme | excellent | large | within weeks | very high | medium | high | monitored continuously | affects conviction and hold/exit rules | Turns “find the evidence” into a query. Must log sources and enforce quoted support to avoid hallucinated answers. |
| document comparison / change detection | 9 | extreme | excellent | large | within weeks | very high | medium | high | monitored continuously | affects trim/exit and averaging rules | “What changed since last quarter?” is where real monitoring value lives. Needs diffing + retrieval + standardized deltas. |
| financial statement analysis | 6 | medium-high | acceptable | medium | within weeks | very high | high | high | semi-automated | affects initial size and max size (via balance-sheet risk) | AI should *not* compute: use code for ratios/cash conversion; use AI for footnote interpretation, accounting-policy flags, and narrative consistency checks. |
| competitor / industry comparison | 8 | high | good | medium | within days | high | high | medium-high | semi-automated | affects max size (moat/fragility) | Great for turning messy industry text into consistent comparison grids and “who wins if X happens.” Needs strong evidence discipline. |
| valuation | 5 | low-medium | poor use of tokens (if free-form) / acceptable (if audited) | medium | within weeks | high | extremely high | severe | semi-automated | strongly affects initial size and max size | AI is useful for model scaffolding, sensitivity tables, and assumption critique—but is dangerous at “spitting out a DCF” without verified inputs. Hallucination + numeric fragility is a bad combo. |
| scenario analysis | 7 | medium-high | good | small-medium | within days | medium-high | extremely high | high | semi-automated | affects max size, averaging rules, trim triggers | Strong for generating *structured* regimes and second-order effects; weak for assigning probabilities or pretending precision. |
| portfolio construction | 4 | low | poor | large | within months | very high | high | high | fully systematized in a repo (but AI ≠ the engine) | affects initial size and portfolio limits | The “math” side should be deterministic (optimizer or rules). AI’s role is constraint articulation, sanity-check narratives, and surfacing unintended exposures—*not deciding weights*. |
| position sizing | 3 | low | poor | medium | immediate | high | extremely high | severe | done ad hoc with prompts (as a check), not as authority | directly affects initial size / max size | AI can help *audit* sizing logic (“does this violate your own risk rules?”). Letting it set sizes is asking for hidden leverage/overlap mistakes. |
| factor / correlation / concentration analysis | 4 | low | poor | large | within months | very high | medium | high | monitored continuously | affects max size, risk limits | Compute with code; use AI only to explain drivers, detect narrative inconsistencies, and propose hedges/questions. Over-trusting AI here creates false confidence. |
| monitoring after purchase | 9 | extreme | excellent | large | within weeks | very high | medium-high | high | monitored continuously | affects trim/exit; also averaging rules | High recurring ROI: summarizing new evidence vs thesis, flagging deviations, and routing “must-read” items. Needs alert thresholds + verification. |
| sell discipline | 6 | medium | acceptable | medium | within weeks | high | extremely high | severe | semi-automated | affects trim/exit decisions | AI can enforce process: check kill criteria, track thesis drift, and surface disconfirming evidence. It should not “decide the sell.” |
| journaling / postmortems | 8 | high | good | small-medium | within days | medium | medium-high | low-medium | fully systematized in a repo | indirectly affects sizing rules and exits via learning | Low failure cost, high compounding: extract decision patterns, bias triggers, and “my typical failure mode” diagnostics from your own logs. |
| workflow automation / repo integration | 6 | high | acceptable | large | within weeks | medium | medium | medium | fully systematized in a repo | indirect | AI helps create/maintain templates, parsers, and consistent outputs—*but the real value comes from engineering discipline and evaluation harnesses*. |

## Buckets: what to automate hard vs what to treat as “nice-to-have” vs what to forbid
This is the part that prevents you from burning tokens for dopamine.

### Must use AI here
These are the only areas where AI can give you a durable “operating system” advantage because they scale and recur:

- Document ingestion & extraction 
- Research QA over your corpus (RAG) 
- Document comparison / change detection 
- Monitoring after purchase 

These are also where finance-specific long-context failure modes show up most, so you need tight controls (retrieval, chunking, citations, sampling audits).

### Strong use of AI
High ROI when evidence-grounded and standardized:

- Adversarial / bearish review 
- Competitor / industry comparison 
- Idea filtering / triage 
- Journaling / postmortems 

The edge here is not “knowing the future.” It’s **systematic coverage**: fewer blind spots, fewer sloppy theses, fewer unexamined risks.

### Useful but not core
Helpful, but easy to overdo or over-trust:

- Thesis formation (as structuring + drafting, not truth generation) 
- Scenario analysis (as breadth, not probability oracle) 
- Workflow automation glue 

### Low-value token spend
This is where you can waste a huge token budget on polished output that doesn’t improve decisions:

- Idea generation (beyond initial sparring / creativity) 
- Portfolio construction “advice” (beyond constraint articulation and narrative checks) 
- Factor/correlation analysis *as computed by AI* (AI can explain, but should not be the calculator)

### Dangerous / false-confidence zones
These are areas where AI errors map directly to capital loss or hidden risk, so AI must be fenced in:

- Valuation outputs without verified inputs and audited math 
- AI-driven position sizing or “optimal weights” 
- Any macro forecasting presented with false precision 
- Any system where repeated prompting increases conviction without increasing evidence quality (hallucination + persuasion is a bad mix)

Also note: AI-related vulnerabilities that can matter operationally (vendor concentration, third-party dependencies, market correlations, cyber/fraud, governance and data quality) are explicitly highlighted by mainstream financial stability work. Don’t build a workflow that ignores those realities.

## AI optimization: where to spend tokens, and what “expensive prompts” are actually for
A large token budget is an advantage only if you stop paying for outputs that *feel* useful but don’t change decisions.

### Recommended priority order for ROI
Not a “roadmap”—just the order in which token spend usually becomes decision-useful fastest:

First: **evidence layer** (extraction → retrieval QA → comparison) 
Second: **adversarial review** (risk register, disconfirming evidence hunts) 
Third: **monitoring** (thesis tracking + change alerts) 
Fourth: **competitor/industry grids** (structured benchmarking) 
Fifth: **scenario generation + journaling loop** (breadth + learning) 
Last: **valuation assistance** (only with audited numerics) and **portfolio construction narration** (never as the optimizer)

### Suggested token-budget allocation
A practical allocation that aligns spending with durable ROI:

- Document extraction + research QA + doc comparison: **35%** 
 Because finance is a text firehose, and this is where you get compounding reuse of tokens (one extraction powers many downstream prompts). Also, long-context fragility means you often need *multiple smaller calls* with retrieval rather than one giant call. 

- Monitoring after purchase (continuous): **20%** 
 This is recurring and decision-relevant. The goal is fewer surprise thesis breaks and faster reaction to real changes. 

- Adversarial / bearish review: **20%** 
 Spend tokens to generate *quality disconfirming questions*, then spend more tokens to force evidence retrieval against those questions. This is where repeated querying is justified (different angles, different premises). 

- Competitor / industry comparison: **10%** 
 Worth it when tethered to sources and standardized prompts; otherwise it becomes fluffy strategy language.

- Scenario analysis (structured regimes + second-order effects): **8%** 
 Spend tokens on breadth and structured output (scenario table + drivers + sign/magnitude), not on fake probabilities. 

- Idea filtering / triage: **5%** 
 Keep it tight: enough to prune and route attention, not enough to convince you. 

- Idea generation: **2%** 
 Cap it intentionally. You’re not paying for creativity; you’re paying for decision-quality.

### What long prompts are actually good for
Long prompts are a **good use of tokens** when:
- You are doing **cross-document synthesis with citations** (e.g., “compare 8 quarters of commentary on pricing power”).
- You are running **adversarial multi-pass review** (base case vs bear case vs “what would make this uninvestable?”).
- You are **building canonical artifacts** you will reuse (thesis ledger, risk register, driver tree).

Long prompts are a **bad use of tokens** when:
- You feed entire filings end-to-end and ask for “the summary” (this collides with long-context degradation and “lost in the middle”). 
- The model is doing arithmetic, valuation math, portfolio optimization, or factor/correlation computation (models can be weak to numerical variations and can hallucinate; you want deterministic code + auditability). 

### The “token discipline” rules that prevent expensive nonsense
If you adopt only a few strict rules, adopt these:

- **No-citation, no-trust rule:** any factual claim that could affect a decision must include a source span (filing section, transcript excerpt, etc.). This directly targets hallucination risk. 
- **Extract → then reason:** first pass extracts structured facts + quotes; second pass reasons over the extracted dataset. This reduces long-context brittleness and forces grounding. 
- **Separate “text intelligence” from “math engine”:** AI handles language; code handles computation and constraints. Tie them with audits. This aligns with basic model-risk principles: incorrect or misused models can cause financial loss, so governance and validation matter. 
- **Multi-pass only where it increases evidence quality:** repeated prompts are justified for adversarial review and evidence retrieval; they are mostly waste for “generate more ideas” and “give me a price target.”

## What AI should NOT be allowed to do
If you want a serious operating system, you need explicit prohibitions—because LLMs will happily output something convincing even when it’s unsupported.

AI should not be allowed to:

- **Make the final buy decision** (it can structure the case and surface evidence; a human must own the decision).
- **Make the final sell decision** (it can enforce kill-criteria checks and highlight thesis breaks; a human must execute).
- **Set position sizes or portfolio weights without hard-coded constraints and deterministic risk checks.**
- **Compute valuation math (DCF, multiples, discount rates) without a separate audited calculation layer.**
- **Assign precise probabilities to scenarios** as if it has a calibrated forecasting model; scenario work is about structured thinking, not oracle probabilities.
- **Generate “facts” without citations** to your ingested corpus.
- **Increase conviction through repetition** (“ask again until you like the answer”): this is a conviction-inflation machine.
- **Override risk limits** (single-name caps, exposure limits, drawdown rules, liquidity constraints).
- **Operate on unaudited or unknown-quality data** while producing authoritative prose (this is how fake certainty happens).
- **Act as a fraud/trust filter for external claims** without explicit verification; AI is also an enabler of fraud and disinformation in markets, and regulators explicitly warn about AI-enabled fraud patterns. 

## Blunt conclusion: if you build only three AI-assisted systems, build these
1) **Evidence layer: extraction + retrieval QA + citation enforcement + change detection** 
This is your compounding asset. It turns unstructured text into reusable, queryable, auditable evidence—exactly where humans don’t scale and where finance’s long-document reality punishes ad hoc reading. 

2) **Adversarial research engine: bear-case generator + disconfirming-evidence hunts + risk register** 
This improves decision quality directly by systematically attacking your thesis and forcing explicit handling of risks and failure modes. It also counteracts the human tendency to collect confirming evidence. 

3) **Thesis-tracking monitoring system: “what changed?” + alerts mapped to kill criteria** 
This is where AI pays you back every week. It reduces thesis drift, catches slow deterioration, and forces discipline—without pretending to be an oracle. It should summarize deltas and route what matters, not “predict the stock.”