# Evidence and Extraction Layer
  Blueprint

  ## Summary

  - Build a self-hosted services/
    evidence/ boundary that feeds the
    current research workbench but
    owns ingestion, normalization,
    extraction, verification, and
    diffing.
  - Source policy: SEC HTML/TXT is the
    legal narrative source of truth;
    SEC XBRL/companyfacts is the
    numeric reconciliation layer, not
    the narrative truth layer, because
    the SEC states only plain text/
    HTML are official filings and XBRL
    is furnished, not filed. Use
    commercial APIs only as
    accelerators: sec-api for cleaner
    Item 7/Item 1A pulls and Quartr
    for transcripts, but always
    reconcile back to official
    filings.
  - Prior-art anchor: short-context
    financial QA is still materially
    below experts (FinQA 65.05
    execution accuracy vs 91.16
    expert; TAT-QA 58.0 F1 vs 90.8
    human). Microsoft’s 2024
    evaluation still shows GPT-4/EEDP
    at 76.05 on FinQA, 77.91 on
    ConvFinQA, and 70.32 on
    MultiHiertt. DocFinQA shows long-
    document retrieval is mandatory:
    on 100k+ token docs, retrieval-
    assisted GPT-4 reached 47.5 while
    retrieval-free GPT-4 was 23.0.
  - Design implication: solve “lost in
    the middle” with section-aware
    retrieval and reranking, not raw
    long prompts; solve table collapse
    by preserving coordinates, merged
    headers, row/column paths, units,
    and cell provenance instead of
    flattening tables to prose.

  ## Public Interfaces

  - EvidenceSourceAdapter: discover(),
    fetch_raw(), fetch_metadata(),
    rate_limit_profile().
  - NormalizedDocument: canonical
    graph with sections, blocks,
    tables, speaker_turns, page_spans,
    source_hash.
  - EvidenceSpan: doc_id, section_id,
    page, bbox, char_start, char_end,
    text_sha256.
  - MetricFact: metric_id,
    value_decimal, unit, period,
    entity_scope, operands[],
    supporting_spans[],
    verification_status.
  - DiffRecord: prior/current fact
    refs, text delta, numeric delta,
    materiality flags.

  ## Implementation Roadmap

  1. Phase 1: Normalization. Add SEC
     adapters for submissions, filing
     HTML/TXT, Inline XBRL/
     companyfacts, plus transcript
     adapters; persist raw blobs in
     MinIO/S3-compatible storage and
     manifests in Postgres.
  2. Normalize every filing/transcript
     into a document graph with pages,
     headings, paragraphs, tables,
     footnotes, exhibits, and speaker
     turns.
  3. Use Docling as the primary
     converter for HTML/PDF/XBRL/
     WebVTT; keep page and bbox
     provenance on every block.
  4. Reconstruct tables as structured
     objects with caption, row path,
     column path, spans, units, notes,
     and cell coordinates.
  5. When table confidence is low or
     merged-header structure is lost,
     run Microsoft Table Transformer
     as a fallback and merge the
     result back into the canonical
     table graph.
  6. Phase 2: Schema Definition.
     Define versioned Pydantic v2
     schemas for Document, Section,
     Table, Cell, Span, MetricFact,
     NarrativeFact,
     VerificationResult, and
     DiffRecord; reject writes that
     fail schema validation.
  7. Build heading-aware chunking:
     first by SEC item boundaries and
     transcript agenda/speaker
     boundaries, then token-aware
     splitting only for oversized
     units; keep a separate table
     index.
  8. Add hybrid retrieval over
     sections/tables/spans using
     Postgres full-text plus pgvector,
     with reranking by section type,
     table affinity, ticker, form, and
     recency.
  9. Phase 3: Multi-Pass Agentic
     Extraction. identify retrieves
     candidate sections/tables/spans
     for a target metric or claim.
  10. extract lets the model map
     candidate spans and operands into
     typed fields only; the model does
     not own arithmetic or final
     publication.
  11. compute replays formulas
     deterministically with Python
     Decimal; use XBRL only to cross-
     check, not to override canonical
     filing evidence without
     verification.
  12. verify enforces zero-trust
     grounding: every quote must
     substring-match a stored span,
     every operand must map to a
     verified span/cell, every metric
     must pass unit/scale/period
     checks, and every published fact
     must be reproducible from raw
     blobs.
  13. Phase 4: Semantic Diffing. Diff
     at section, sentence, table-cell,
     and fact level across periods;
     use deterministic alignment
     first, embeddings only to cluster
     candidate semantic changes after
     section matching.
  14. Phase 5: Defensive Guards. Add
     abstention, contradiction, unit/
     sign/period/scale guards,
     unsupported-claim rejection, and
     span-only reruns to catch
     sycophancy or instruction-induced
     drift.
  15. Phase 6: Storage, Caching,
     Evaluation, Ops. Use Postgres 16
     + pgvector + MinIO; cache raw
     metadata, normalized docs,
     embeddings, and verified facts by
     source_hash; orchestrate with
     Temporal; expose a small FastAPI
     service; gate deploys on
     retrieval recall, span precision,
     quote verification rate, numeric
     exact-match, diff accuracy,
     latency, and token cost.

  ## Stack and Repo Shape

  - Stack: edgartools, Docling, lxml/
    BeautifulSoup, Table Transformer,
    FastAPI, Pydantic v2, SQLAlchemy
    2.0, Alembic, Temporal, PostgreSQL
    16, pgvector, MinIO, httpx,
    tenacity, orjson, structlog,
    Python decimal.
  - Repo shape: services/evidence/api,
    adapters, normalizers, extractors,
    verifiers, diff, schemas, storage,
    workflows, tests, fixtures; the
    current repo consumes verified
    facts downstream instead of owning
    extraction logic.

  ## Sample Execution Logic

  extract(metric="segment_revenue",
ticker="MSFT", period="FY2025")
    -> discover latest 10-K and segment-
note tables
    -> normalize filing into sections/
tables/spans
    -> retrieve tables where header path
~= revenue/net sales and row path ~=
segment labels
    -> model selects candidate cells and
cites spans only
    -> deterministic engine reads cited
cell values, units, and periods
    -> verifier confirms page/bbox/text
match and replays normalization
    -> publish MetricFact with official
filing URL + page anchor + supporting
spans

  ## Test Plan

  - Verify Item 7 and Item 1A
    extraction against official SEC
    HTML on standard, amended, and
    non-standard filings.
  - Verify segment revenue on both
    XBRL-tagged facts and note tables
    with merged headers, blank rows,
    footnotes, negative values, and
    multi-period columns.
  - Verify quote grounding fails
    closed when no exact or normalized
    span match exists.
  - Verify long-context retrieval
    keeps gold evidence in retrieved
    section/table chunks rather than
    relying on full-document prompts.
  - Verify semantic diffing catches
    added/removed risks, changed
    guidance language, and numeric
    deltas without inventing changes.
  - Verify replayability: every
    published fact can be recomputed
    from raw blob hash, stored spans,
    and deterministic formula trace.

  ## Assumptions

  - Scope is US-first public-company
    research centered on SEC filings
    and earnings-call transcripts.
  - Public technical detail from
    Point72/BAM on this exact layer
    was sparse in this pass; the
    design is anchored on sources that
    did expose implementation detail:
    SEC docs, J.P. Morgan-linked
    FinQA, Microsoft Research,
    DocFinQA, Docling, and commercial
    API docs.
  - Default operating posture is SEC-
    first with commercial fallbacks,
    provider-agnostic models, and
    deterministic math outside the
    LLM.

  Source anchors: SEC EDGAR APIs
  (https://www.sec.gov/search-filings/edgar-application-programming-interfaces),
  SEC official filing guidance
  (https://www.sec.gov/edgar/searchedgar/aboutedgar.htm),
  SEC access policy
  (https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data),
  sec-api Extractor
  (https://sec-api.io/docs/sec-filings-item-extraction-api),
  EdgarTools
  (https://dgunning.github.io/edgartools/data-objects/),
  Docling
  (https://docling-project.github.io/docling/),
  Docling chunking
  (https://docling-project.github.io/docling/concepts/chunking/),
  FinQA
  (https://aclanthology.org/2021.emnlp-main.300/),
  TAT-QA
  (https://aclanthology.org/2021.acl-long.254/),
  MultiHiertt
  (https://aclanthology.org/2022.acl-long.454/),
  Microsoft 2024 evaluation
  (https://www.microsoft.com/en-us/research/publication/evaluating-llms-mathematical-reasoning-in-financial-document-question-answering/),
  DocFinQA
  (https://aclanthology.org/2024.acl-sho
  (https://direct.mit.edu/tacl/article/dansformer),
  Quartr transcripts
  (https://quartr.dev/api-reference/transcripts)