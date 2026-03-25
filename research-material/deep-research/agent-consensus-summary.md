# Agent Consensus Summary

Sources synthesized: `agent1.md`, `agent2.md`, `agent3.md`.

## Executive Summary

Across all three reports, the core conclusion is stable: AI is most valuable in an investment workflow when it acts as an evidence-processing and decision-discipline layer, not as an autonomous investor. The strongest shared use cases are extracting and summarizing filings and transcripts, detecting changes across reporting periods, stress-testing the thesis with adversarial prompts, and monitoring live positions for thesis drift. The strongest shared prohibitions are also clear: do not let LLMs set position sizes, run portfolio optimization, produce unaudited valuation math, or make uncited factual claims.

The differences are mostly about emphasis, not direction. Agent 1 is the most explicit about long-context failure, citation discipline, and token ROI. Agent 2 is the most ambitious about an institutional AI operating system, multimodal ingestion, and future agentic orchestration. Agent 3 is the strongest on practitioner guardrails around sycophancy, code-executed math, model routing, and compliance logging. Taken together, the three reports describe a layered architecture: AI reads and compresses unstructured evidence, deterministic tools handle math and risk, and humans retain final decision authority.

## Consensus Findings

### Strong cross-agent agreement

- AI should be used first on text-heavy, recurring, high-volume work: filings, earnings calls, transcripts, notes, and monitoring deltas across time.
- The highest-confidence applications are evidence extraction, summarization, change detection, adversarial thesis review, and ongoing monitoring after purchase.
- AI should operate against primary-source material and return traceable support. Agent 1 is the strictest on citation enforcement, Agent 2 frames this as auditability, and Agent 3 adds explicit validation and logging.
- The right pattern is usually `extract -> structure -> retrieve -> reason`, not `dump giant context into one prompt and ask for a verdict`.
- The best role for AI is augmentation of analyst workflow, not replacement of portfolio manager judgment.
- Financial math, optimization, and risk calculations should remain deterministic. AI can explain, flag anomalies, or write code that then executes in a sandbox, but it should not be the calculator of record.
- A staged implementation path is preferred over a big-bang build: prompt templates first, then versioned workflows, then ingestion and retrieval, then automated monitoring and agentic orchestration.

### Shared prohibitions

- No autonomous buy, sell, or sizing decisions.
- No unaudited DCFs or valuation outputs treated as trustworthy by default.
- No portfolio optimization, factor decomposition, covariance work, or risk attribution performed directly by an LLM.
- No reliance on model memory for current market data or precise financial figures.
- No increase in conviction just because the model can restate the same thesis more persuasively.

## Reconciled Priority Order

The source reports use different scoring systems and different units of analysis, so the table below reconciles relative priority rather than averaging raw scores.

| Consensus rank | Workflow cluster | Why it survives synthesis | Agent signals |
|---|---|---|---|
| 1 | Evidence ingestion, summarization, and structured extraction | This is the common foundation for every higher-level workflow. All three reports treat filings and transcripts as the highest-ROI text firehose to compress. | Agent 1 ranks extraction #1. Agent 2 ranks extraction #3 and treats ingestion as foundational. Agent 3 ranks earnings/filing summarization #1 and extraction #4. |
| 2 | Change detection and narrative delta tracking | All three see quarter-to-quarter and call-to-call deltas as a direct source of investable signal and a strong candidate for automation. | Agent 1 ranks change detection #2. Agent 2 ranks narrative delta detection #1. Agent 3 ranks 10-K/10-Q change detection #3. |
| 3 | Adversarial thesis testing and bear-case generation | This is the clearest shared decision-quality use case beyond summarization. All three describe it as a defense against confirmation bias. | Agent 1 ranks adversarial review #3. Agent 2 ranks red teaming #2. Agent 3 ranks adversarial testing #2. |
| 4 | Monitoring after purchase and thesis-drift alerting | Each report treats monitoring as a recurring source of labor compression and risk control, though they differ on whether it is a top-3 build or a phase-4 system. | Agent 1 ranks monitoring #5 and includes it in the final top 3 systems. Agent 2 scores monitoring 10/10 and makes it essential. Agent 3 embeds it in the recommended build architecture and top 3 systems via filing and earnings processing. |
| 5 | Research QA, internal knowledge management, and repo retrieval | Querying your own evidence base is a recurring theme, although the explicit emphasis varies by report. | Agent 1 ranks research QA over the corpus #4. Agent 2 includes institutional knowledge management in the top 10. Agent 3 makes repo-integrated RAG a core phase even if it is not a standalone top-10 item. |
| 6 | Competitor, tone, and sentiment monitoring | All three see value here once the evidence layer exists, but this is less unanimous than the top five. | Agent 1 ranks competitor mapping #6. Agent 2 includes competitor and industry sentiment benchmarking #6 plus transcript nuance mapping. Agent 3 ranks management tone #5 and competitive monitoring #8. |
| 7 | Thesis structuring, memo drafting, and research hygiene artifacts | Useful across reports, but treated more as workflow support than edge creation. | Agent 1 emphasizes thesis ledgers, risk registers, and kill criteria. Agent 2 pairs thesis formation with red teaming. Agent 3 ranks memo drafting and thesis structuring #6. |
| 8 | Scenario generation and structured risk simulation | All three allow this as a disciplined brainstorming tool, but none trust it as a probability engine. | Agent 1 ranks scenario generation #9. Agent 2 ranks black-swan scenario generation #8 and gives scenario analysis a high workflow score. Agent 3 supports narrative stress scenarios while keeping formal risk math outside the LLM. |
| 9 | Journaling, postmortems, and bias mining | Recognized by all three, but this is the most obvious ranking disagreement. | Agent 1 ranks journaling #10 but calls it underrated. Agent 2 ranks post-mortems #5 and makes it one of the three essential systems. Agent 3 ranks journaling #10 and calls the area underdeveloped. |
| 10 | Idea generation, thematic mapping, and universe triage | Present in all three, but consistently framed as lower-quality edge than evidence-grounded analysis. | Agent 1 favors filtering over raw idea generation. Agent 2 includes alpha factor mining and macro-to-sector mapping. Agent 3 keeps thematic idea generation in the useful-but-limited tier. |

### Material opportunities with weaker consensus

- Code-assisted financial analysis: Agent 3 treats code generation plus sandbox execution as one of the highest-leverage patterns. Agent 1 and Agent 2 agree with deterministic math, but neither elevates this to the same priority tier.
- Financial statement anomaly detection: Agent 2 gives this the strongest explicit emphasis, especially through red-flag detectors and conceptual shift analysis. Agent 1 and Agent 3 treat it more as a controlled extension of the evidence layer.
- Sell-discipline support: Agent 1 and Agent 2 both see value in AI enforcing kill criteria, trim reviews, and thesis-break checks, but neither supports autonomous exit decisions. Agent 3 folds this into adversarial review and monitoring rather than treating it as a separate product.
- Workflow orchestration and agents: Agent 2 pushes furthest toward an institutional operating system. Agent 3 also recommends multi-agent monitoring later. Agent 1 is more focused on disciplined pipelines than on agent identity.
- Alternative data and macro mapping: Agent 2 is most aggressive here, including product reviews, employee sentiment, qualitative factor mining, and macro-to-sector mapping. Agent 1 and Agent 3 are more cautious about uniqueness and false confidence.

## Agreement and Disagreement Matrix

| Workflow area | Agent 1 | Agent 2 | Agent 3 | Consensus |
|---|---|---|---|---|
| Filings and transcript summarization | High priority, tied to extraction and monitoring | High priority, especially for earnings season compression | Highest-ranked use case | Strong consensus |
| Structured extraction with audit trail | Core foundation, citation enforced | Core foundation, multimodal extraction emphasized | Strong value, schema-driven extraction | Strong consensus |
| Cross-period change detection | Top-tier use case | Top-ranked use case | Top-tier use case | Strong consensus |
| Adversarial review / bear case | Top-tier use case | Top-tier use case | Top-tier use case | Strong consensus |
| RAG / research QA / second brain | Explicit top priority | Important but lower-ranked | Built into later architecture | Strong consensus, lighter emphasis in Agent 3 |
| Monitoring after purchase | Top-tier recurring ROI | Highest-value ongoing system | Important architectural output | Strong consensus, rank differs |
| Competitor / tone / sentiment analysis | High-value comparison grids | High-value benchmarking and transcript nuance | High-value but secondary | Partial agreement |
| Thesis structuring / memo drafting | Useful but not core | Useful when paired with review templates | Strong workflow support | Partial agreement |
| Scenario analysis | Useful for breadth, not probabilities | Higher priority, including black-swan work | Useful for narrative stress tests | Partial agreement |
| Journaling / postmortems | Useful but ranked low | Ranked high and elevated to essential | Useful but underdeveloped | Clear disagreement on priority |
| Code-generated analysis | Implicit through code-not-LLM math separation | Supports detector libraries, less central | Explicit high-value pattern | Agreement on method, disagreement on priority |
| Valuation math | Dangerous unless audited | Low value and high risk | Must be code-executed and reviewed | Strong consensus to constrain |
| Position sizing / portfolio construction | Low value or forbidden for LLMs | More open to monitored future systems, but human sign-off required | Traditional quant tools only | Strong consensus on deterministic control layer |
| Factor / correlation / risk math | Compute with code, not AI | More willing to integrate into mature system | Traditional libraries decisively superior | Partial agreement on workflow ambition, strong agreement on math engine |
| Agentic orchestration / compliance logging | Secondary to evidence discipline | Strong architectural emphasis | Strong later-phase emphasis | Agreement on usefulness later, not on day-1 priority |

## Unique Additions by Agent

### Agent 1

- Makes the strongest case that long-context finance work breaks naive prompting. The recurring warning is that giant prompts over full filings are often worse than retrieval plus smaller grounded calls.
- Adds the clearest token-discipline rules: `no citation, no trust`, `extract then reason`, and `use multi-pass prompting only when it improves evidence quality`.
- Contributes the most explicit process artifacts: thesis ledger, driver tree, risk register, disconfirming evidence log, and kill criteria.
- Gives the most detailed qualitative bucketization of what to automate hard, what to treat as nice-to-have, and what to forbid.

### Agent 2

- Pushes furthest toward an institutional AI operating system with repository phases, dedicated parsers, automated monitoring, and later multi-agent risk workflows.
- Adds the strongest emphasis on multimodal extraction of complex tables and semantic layout, not just plain-text summarization.
- Surfaces extra opportunity areas that the other reports mention less: transcript nuance mapping, competitor sentiment from alternative data, qualitative alpha-factor mining, and macro-to-sector sentiment mapping.
- Raises operational controls around RBAC and restricting agent access to sensitive internal data.

### Agent 3

- Introduces the sharpest warning that sycophancy may be more dangerous than hallucination because it can selectively reinforce the user's thesis with real but one-sided evidence.
- Provides the clearest implementation rule for numerics: the model should write code, the sandbox should execute it, and the human should review both.
- Adds the most concrete cost and architecture guidance: model routing, prompt caching, cheap-model triage versus frontier-model escalation, and budget bands for a small concentrated fund.
- Is the most explicit about audit and compliance logging, plus practical separation between LLMs and traditional tools such as Bloomberg, FactSet, `cvxpy`, `statsmodels`, and risk libraries.
- Also draws the hardest boundary around regulatory, legal, and audit-grade use cases, where nondeterministic output is not acceptable.

## Contradictions and Tensions

- The reports disagree on what the first-ranked use case really is. Agent 1 starts with extraction, Agent 2 with narrative delta detection, and Agent 3 with earnings and filing summarization. In practice this is one evidence-processing cluster, not three unrelated bets.
- Journaling is the largest priority mismatch. Agent 2 treats post-mortems as one of the three essential systems, while Agent 1 and Agent 3 both rank it last despite acknowledging long-term value.
- Agent 3 elevates code-assisted financial analysis into the top build set. Agent 1 and Agent 2 clearly support deterministic math, but they frame it more as a safety requirement than as a flagship AI product.
- Agent 2 is more optimistic than the other two about mature-stage agentic portfolio and factor workflows. Agent 1 and Agent 3 are much stricter that optimization, sizing, and risk math should remain in traditional tools.
- Agent 1 centers hallucination and long-context degradation; Agent 3 centers sycophancy and confirmation bias; Agent 2 centers institutional workflow design and model governance. These are complementary concerns, but they change where each report spends most of its design attention.
- Agent 2 is the most expansive on alternative data, qualitative factor mining, and macro regime mapping. Agent 1 and Agent 3 are less convinced these are durable sources of differentiated insight.

## Practical Bottom Line

If the three reports are combined into one actionable build thesis, the result is:

1. Build the evidence layer first: ingestion, summarization, structured extraction, citations, retrieval, and change detection over filings, transcripts, and internal notes.
2. Build the adversarial layer second: red-team prompts, bear-case generation, risk registers, anti-sycophancy instructions, and fresh-context review workflows that challenge the thesis rather than echo it.
3. Build the monitoring layer third: thesis-drift alerts, delta trackers, competitor and management-language monitoring, and human-reviewed escalation when something materially changes.

Everything else should attach to those layers rather than bypass them. Journaling, competitive mapping, scenario generation, memo drafting, code-assisted analysis, and later agentic orchestration can all add value, but they are safest and most useful when built on top of an auditable evidence base and a deterministic quantitative stack.
