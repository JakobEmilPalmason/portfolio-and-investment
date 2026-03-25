# TLDR: AI in Investment Research Consensus

**Core Thesis:** AI is a labor-compression and decision-discipline engine, not an autonomous portfolio manager. Its highest ROI is in processing unstructured text, while mathematical optimization and sizing must remain in deterministic traditional tools.

## The 3 "Must-Build" Systems
1. **The Evidence & Extraction Layer:** Automated ingestion, multimodal table extraction, and summarization of filings/transcripts. 
   - *Rule:* Always cite sources. Use schema-driven extraction.
2. **The Adversarial "Red Team" Engine:** Forcing models to generate bearish counter-arguments and hunt for disconfirming evidence to combat confirmation bias.
   - *Rule:* Use opposing-agent architecture (bull vs. bear) to prevent LLM sycophancy.
3. **The Continuous Monitoring System:** Semantic diffing of 10-Ks/10-Qs and tracking management tone shifts over time.

## Key Technical & Implementation Rules
- **Code, Not Chat, for Math:** Never trust LLM arithmetic. Models must write Python code that executes in a secure sandbox for any financial calculation.
- **Model Routing & Caching:** Route 70-90% of bulk tasks to cheap models and 10-30% to frontier models. Aggressively use prompt caching for long documents (like 10-Ks) to manage token costs.
- **Token Budgeting:** Allocate the majority of your token budget (~35%) to document extraction and QA, followed by monitoring (~20%) and adversarial review (~20%).
- **Strict Boundaries:** Never let an LLM run portfolio optimization, set position sizes, or compute unaudited valuation math. Use traditional tools (`cvxpy`, `Barra`, `Bloomberg PORT`) for quantitative risk and sizing.