# Technical Specification Document: Evidence and Extraction Layer

## Objective
To build an institutional-grade, Evidence and Extraction Layer for a financial research platform. This system systematically ingests unstructured financial text (10-Ks, 10-Qs, transcripts) and converts it into a structured, auditable, and numerically accurate research database.

---

## Section 1: The Research & Prior Art (The Investigation)

### 1. Academic & Industry Benchmarks
The "State of the Art" (SOTA) in financial document processing has moved beyond general-purpose large language models (LLMs) to **domain-specialized models** and **agentic workflows** (e.g., FinAgents architectures). 
- **Benchmarks:** Modern financial AI evaluation relies on benchmarks like **FinQA / ConvFinQA** (for numerical reasoning), **FinanceBench** (for SEC filing analysis), and **XFinBench** (for complex problem solving). Models like DeepSeek-R1 (RL-based) and GPT-4.5 / Claude 3.5 Sonnet lead in complex multi-step reasoning and long-context comprehension, while domain-tuned models (e.g., FinMA) excel at sentiment and entity extraction.
- **The "Lost in the Middle" Problem:** Research (Liu et al., 2023) demonstrates that LLMs exhibit a U-shaped performance curve, where information buried in the middle of long documents (like a 200-page 10-K) is frequently missed. Top-tier firms mitigate this via **Hybrid RAG** with reranking, **Summary-First Approaches** (chunking and summarizing sections individually), and **Strategic Document Ordering**.
- **Table Structure Collapse:** Converting 2D financial tables into 1D text destroys positional relationships, reducing accuracy to as low as 5-30% on complex balance sheets. Leading firms prevent this by utilizing **Vision-Language Models (VLMs)** (e.g., GPT-4o, Gemini 1.5 Pro) to visually parse layouts, or by employing **Financial-Aware Serialization** (converting tables into Hierarchical JSON or Markdown with semantic headers) combined with structured generation tools (like *Outlines*).

### 2. Data Sourcing & Ingestion
- **SEC EDGAR (XBRL/HTML) vs. Commercial APIs:**
  - **Commercial APIs (e.g., FactSet, AlphaSense):** Provide clean, standardized JSON which is excellent for LLMs to process without hallucination. However, they are expensive, act as a "black box" (obscuring the source text), and often strip out critical qualitative narratives.
  - **SEC EDGAR Direct:** Free and provides the absolute "Source of Truth," including rich narratives in Item 7 (MD&A) and Item 1A (Risk Factors). The trade-off is high parsing complexity (messy HTML, nested XBRL).
- **Recommendation:** A hybrid approach. Use commercial APIs/XBRL-to-JSON for standard quantitative screening, but ingest **SEC HTML converted to Markdown** (via tools like unstructured.io or trafilatura) for deep-dive RAG and narrative extraction of MD&A/Risk Factors to maintain the highest fidelity.

---

## Section 2: The Implementation Logic (The "How")

### 1. Parsing Strategy
- **Methodology:** Do not rely purely on text extraction. Implement a pipeline that uses structural-anchor techniques combined with Vision-Language Models (VLMs) for complex tables.
- **Section-Based Chunking:** Instead of arbitrary character counts (which sever semantic context), the parser will use semantic chunking based on document headers (e.g., `<h1>Item 7. MD&A</h1>`). Markdown conversion enables natural boundary detection.

### 2. Deterministic Extraction
- **Separation of Concerns:** To ensure 100% numerical accuracy, separate "Language Reasoning" from "Financial Arithmetic." The LLM is restricted to *identifying* the components of a formula in the text and generating the mathematical expression. A deterministic Python runtime (e.g., via a sandbox or simple `eval` with strict AST parsing) executes the actual calculation to prevent LLM arithmetic hallucinations.

### 3. Citation & Auditability
- **Zero-Trust Verification Loop:** Every extracted metric or quote must include a `source_quote` and a `span_index`.
- **Source-Grounding:** A secondary "Auditor Agent" strictly compares the `source_quote` against the raw document chunks using exact string matching or highly constrained semantic similarity (if slight formatting shifts occurred). If the text cannot be anchored to a specific page/paragraph, the extraction is rejected.

---

## Section 3: The 15-Step Implementation Roadmap

**Phase 1: Normalization**
1. **Ingestion:** Fetch raw HTML filings from SEC EDGAR feeds.
2. **Markdown Conversion:** Pass HTML through `unstructured.io` to strip noise and convert tables into Markdown/Hierarchical JSON.
3. **Semantic Chunking:** Index the document by sections (Item 1A, Item 7, Notes to Financials) using regex/header anchors.

**Phase 2: Schema Definition**
4. **Define Pydantic Models:** Create strict Pydantic schemas for the target data (e.g., `SegmentRevenue`, `RiskFactor`).
5. **Structured Output Enforcement:** Integrate `instructor` or `Outlines` to force the LLM to output valid JSON matching the schemas.

**Phase 3: Multi-Pass Agentic Extraction**
6. **Agent 1 (Locator):** Scans section summaries to identify chunks containing the target metric.
7. **Agent 2 (Extractor):** Reads the specific chunk, extracts the raw value, context, and exact source quote.
8. **Agent 3 (Calculator):** If a derived metric is needed, formulates the math equation; a deterministic Python engine executes it.
9. **Agent 4 (Auditor):** Verifies the extracted quote exists in the source chunk. Rejects or flags mismatches.

**Phase 4: Semantic Diffing & Storage**
10. **Temporal Alignment:** Match extracted metrics across previous periods (QoQ, YoY).
11. **Diff Generation:** Highlight significant narrative shifts in MD&A using embedding distances.
12. **Vector/Relational Storage:** Store structured data in PostgreSQL (relational) and chunks/embeddings in Qdrant/Milvus (vector).

**Phase 5: Defensive Guards & Scaling**
13. **Anti-Hallucination Checks:** Implement strict temperature=0 settings for extraction and run cross-entropy checks.
14. **Caching Layer:** Implement Redis semantic caching (e.g., `GPTCache`) to prevent re-processing identical queries and save token costs.
15. **Evaluation Harness:** Set up `ragas` or `truera` to continuously monitor precision, recall, and faithfulness of the extraction pipeline against a gold-standard dataset.

---

## Section 4: The "Flop" Analysis (Risk Mitigation)

| Failure Point | Why It Fails | Engineering Guardrail |
| :--- | :--- | :--- |
| **1. Table Structure Inversion** | LLM misaligns rows/cols in dense tables. | Force Markdown/JSON serialization of tables; use VLMs for complex nested grids. |
| **2. Hallucinated Citations** | LLM invents a quote that sounds plausible. | Exact-match script: `assert extracted_quote in raw_chunk_text`. Reject if False. |
| **3. Arithmetic Errors** | LLMs are bad calculators. | LLM only outputs the formula (e.g., `A + B`). Python `asteval` executes it. |
| **4. "Lost in the Middle"** | Critical data missed in large docs. | Implement section-based chunking; analyze sections independently before aggregating. |
| **5. Runaway Token Costs** | Full 10-K RAG is expensive. | Implement semantic caching and LLM routing (use cheaper models for locating, expensive for extracting). |

---

## Proposed Library Stack
- **Parsing/Ingestion:** `unstructured.io` (for robust HTML/PDF to Markdown), `sec-edgar-downloader`.
- **Schema Enforcement:** `instructor` (plugs easily into Pydantic) or `Outlines` (for local open-source models).
- **Orchestration:** `LangGraph` or `LlamaIndex` (for managing the multi-agent state machine).
- **Execution Environment (Math):** `asteval` (safe mathematical evaluation in Python).
- **Database:** `PostgreSQL` (JSONB for structured data), `Qdrant` (Vector DB for semantic search).
- **Evaluation:** `ragas` (RAG Assessment).

---

## Repository File Structure
Designed to scale from one ticker to 500+:

```
investment-extractor/
├── config/
│   ├── settings.py          # API keys, global vars
│   └── prompts/             # Version-controlled prompt templates
├── src/
│   ├── ingestion/
│   │   ├── edgar_client.py  # Handles SEC API rate limits
│   │   └── parser.py        # HTML to Markdown/JSON conversion
│   ├── extraction/
│   │   ├── schemas.py       # Pydantic models (e.g., SegmentRevenue)
│   │   ├── agents.py        # Locator, Extractor, Auditor logic
│   │   └── calculator.py    # Deterministic math engine
│   ├── storage/
│   │   ├── db.py            # Postgres/VectorDB connection pooling
│   │   └── caching.py       # Redis semantic cache
│   └── pipeline.py          # Main orchestration DAG (LangGraph)
├── tests/
│   ├── test_extraction.py   # Golden dataset evaluations
│   └── test_math.py
├── data/
│   └── raw/                 # Local cache of downloaded filings
└── requirements.txt
```

---

## Sample Execution Logic: Extracting "Segment Revenue"

```python
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI

client = instructor.patch(OpenAI())

# 1. Define the target schema
class SegmentRevenue(BaseModel):
    segment_name: str
    revenue_value: float = Field(description="Revenue in millions")
    source_quote: str = Field(description="Exact sentence or table row from text")
    
# 2. Raw Chunk (Simulated output from Phase 1)
raw_mda_chunk = """
Our Cloud Intelligence segment saw significant growth this quarter. 
Revenue for Cloud Intelligence was $4,520 million, up 15% year-over-year.
"""

# 3. Extraction (Agent 2)
def extract_segment_revenue(chunk: str) -> SegmentRevenue:
    return client.chat.completions.create(
        model="gpt-4o",
        response_model=SegmentRevenue,
        messages=[
            {"role": "system", "content": "Extract segment revenue. You must provide the exact source quote."},
            {"role": "user", "content": f"Text: {chunk}"}
        ],
        temperature=0
    )

extracted_data = extract_segment_revenue(raw_mda_chunk)

# 4. Verification (Agent 4 / Guardrail)
def verify_extraction(data: SegmentRevenue, source_text: str):
    if data.source_quote not in source_text:
        raise ValueError(f"Audit Failed: Quote '{data.source_quote}' not found in source.")
    print("Verification Passed.")
    return True

# 5. Execution
verify_extraction(extracted_data, raw_mda_chunk)
print(f"Verified Extracted Value: {extracted_data.revenue_value}M for {extracted_data.segment_name}")
# Output -> Verified Extracted Value: 4520.0M for Cloud Intelligence
```