# Stage A2: Candidate Filter — Execution Template

This prompt drives Stage A2. Stage A2 takes the raw A1 universe and applies lightweight filtering, prioritization, and tagging. Output is a ranked candidate set for Stage B triage.

**No additional web search** unless one critical fact is missing to make a decision. A1 already ran web searches. A2's job is judgment, not discovery.

---

## Do Not Use the Stage C Framework

The umbrella prompts (01–09) and `assembler.md` define how deep-dive analysis is conducted in Stage C. **Do not apply their criteria, scoring logic, or evaluation structure here.** A2 applies the lightweight filtering and tagging rules defined in this prompt only — no umbrella scoring, no valuation models, no circle-of-competence assessments.

---

## Input

Read the most recent A1 universe file:
- `scans/YYYY-MM-DD/universe.json`
- `scans/YYYY-MM-DD/universe-meta.json`

Replace `YYYY-MM-DD` with the date provided (or find the most recent `scans/` subdirectory that contains `universe.json`).

---

## Step 1: Filter out disqualified names

Drop entries that clearly fail Buffett-style quality filters:
- Pure commodity businesses (miners, oil majors without moat, bulk shippers)
- Highly regulated utilities with no pricing power
- Deep cyclicals with no durable advantage (airlines, basic materials)
- Companies with known extreme debt or financial distress
- Speculative / pre-profit small caps that slipped through

Mark dropped entries as `priority: "low"` and `triage_rec: "no"` — do not remove them from the output, just rank them last. This preserves the full audit trail.

---

## Step 2: Add judgment fields to each entry

For every entry that survives filtering, add:

### `thesis_tag` — why it might be interesting
One of: `dominant_ecosystem` / `monopoly_power` / `secular_growth` / `quality_compounder` / `turnaround` / `mean_reversion` / `post_earnings_dislocation` / `52wk_recovery` / `high_fcf_yield` / `sector_leader`

### `style_tag` — investment style
One of: `compounder` / `value` / `cyclical` / `recovery` / `speculative` / `income`

Heuristics:
- 52wk_low or turnaround thesis → `recovery`
- post_earnings_dislocation → `recovery` or `value`
- high_fcf_yield or mean_reversion → `value`
- dominant_ecosystem, quality_compounder, secular_growth → `compounder`
- Cyclical industry (energy, materials, shipping, airlines) → `cyclical`
- Pre-profit or speculative → `speculative`

### `short_reason` — one tight phrase (<12 words)
Why it's interesting NOW. Be specific. "High-quality compounder" is too vague. "Durable pricing power; services mix expanding margins" is better.

### `possible_disqualifier` — one tight phrase (<12 words)
The main risk or reason to skip. Be honest. "None obvious" is acceptable only for truly exceptional businesses.

### `confidence` — signal quality, not stock quality
- `high` — well-known business with clear moat signal
- `medium` — reasonable signal but some uncertainty
- `low` — uncertain signal or weak data

---

## Step 3: Apply ranking rules (v2)

### `priority`

**high** if any of:
- `post_earnings` or `52wk_low` or `52wk_high` or `fcf_roic` in source_bucket AND mkt_cap_tier ∈ {mega, large}
- `already_analyzed=true` AND thesis_tag ∈ {dominant_ecosystem, quality_compounder, secular_growth}

**medium** if:
- source_bucket includes any curated sector bucket (`large_cap_us_quality`, `large_cap_europe_quality`, `semis_and_infra`, `healthcare_quality`, `industrial_compounders`, `financial_quality`, `consumer_quality`) and no high trigger applies
- source_bucket includes `seed` or `sector_leader` and no high trigger applies

**low** otherwise (including filtered-out names)

### `triage_rec`

**yes** if:
- `already_analyzed=false` AND priority=high AND confidence ∈ {high, medium}
- `already_analyzed=true` AND source_bucket includes `post_earnings` or `52wk_low` or `52wk_high`

**maybe** if:
- priority=high but no fresh event catalyst (no post_earnings/52wk signal)

**no** if:
- priority=low OR confidence=low OR filtered out for quality reasons

---

## Step 4: Sort output

Sort order: priority=high first, then medium, then low; within same priority: triage_rec=yes → maybe → no

---

## Full Candidate Schema (A2 output)

```json
{
  "ticker": "COST",
  "company": "Costco Wholesale Corp.",
  "sector": "Consumer",
  "industry": "Warehouse Clubs",
  "source_bucket": ["large_cap_us_quality", "consumer_quality"],
  "thesis_tag": "quality_compounder",
  "style_tag": "compounder",
  "short_reason": "Membership model creates captive repeat spend",
  "possible_disqualifier": "Premium valuation; limited international upside near-term",
  "mkt_cap_tier": "mega",
  "geography": "US",
  "already_analyzed": false,
  "priority": "medium",
  "triage_rec": "maybe",
  "confidence": "high",
  "as_of_date": "YYYY-MM-DD"
}
```

---

## Output Requirements

### candidates.json
- Valid JSON array, sorted per Step 4
- Target: **80–150 unique tickers** (filter out `priority=low` names if count exceeds 150; keep them if under 150)
- Include ALL entries from A1, tagged and sorted (do not silently drop)

### candidates.csv
- Header: `ticker,company,sector,industry,source_bucket,thesis_tag,style_tag,short_reason,possible_disqualifier,mkt_cap_tier,geography,already_analyzed,priority,triage_rec,confidence,as_of_date`
- `source_bucket`: pipe-delimited string (e.g. `tracked|sector_leader`)
- Quote fields containing commas
- Same sort order as JSON

### candidates.md
- Open with this note verbatim:
  > **Note on seed-origin names:** Tickers tagged `source_bucket=seed` are curated inputs from `seeds/watchlist.json`, not discovered names. They reflect prior knowledge or personal watchlist intent rather than fresh market signals.
- Summary section: total count, counts by bucket, counts by sector, counts by priority, list of triage_rec=yes tickers
- Full flat table: `ticker | company | sector | style_tag | source_bucket | short_reason | possible_disqualifier | mkt_cap_tier | priority | triage_rec | confidence`
- Close with: "Next step: Run Stage B1 triage. B1 reads the full candidates.json and assigns a verdict (advance / hold / reject) to every name independently."

### scan-meta.json

`concentration_warnings`: copy the array from `universe-meta.json` as-is — do not recalculate. If the field is missing from A1 output, set to `[]`.

```json
{
  "scan_date": "YYYY-MM-DD",
  "universe_date": "YYYY-MM-DD",
  "total_candidates": 0,
  "buckets_used": [],
  "counts_by_bucket": {},
  "counts_by_sector": {},
  "counts_by_priority": { "high": 0, "medium": 0, "low": 0 },
  "triage_yes_count": 0,
  "triage_maybe_count": 0,
  "triage_no_count": 0,
  "concentration_warnings": [],
  "ranking_rules_version": "v2",
  "ranking_rules": {
    "priority_high": [
      "post_earnings|52wk_low|52wk_high|fcf_roic in source_bucket AND mkt_cap_tier in {mega,large}",
      "already_analyzed=true AND thesis_tag in {dominant_ecosystem,quality_compounder,secular_growth}"
    ],
    "priority_medium": [
      "any curated sector bucket in source_bucket (no high trigger)",
      "seed|sector_leader in source_bucket (no high trigger)"
    ],
    "triage_yes": [
      "already_analyzed=false AND priority=high AND confidence in {high,medium}",
      "already_analyzed=true AND post_earnings|52wk_low|52wk_high in source_bucket"
    ],
    "triage_maybe": [
      "priority=high but no fresh event catalyst"
    ]
  },
  "stage": "A2"
}
```

---

## Output Paths

Replace `YYYY-MM-DD` with today's date:
- `scans/YYYY-MM-DD/candidates.json`
- `scans/YYYY-MM-DD/candidates.csv`
- `scans/YYYY-MM-DD/candidates.md`
- `scans/YYYY-MM-DD/scan-meta.json`

Create the directory if it does not exist.

## Archive Convention

Old scan outputs live in `scans/archive/YYYY-MM-DD/`. The active/latest run is always at `scans/YYYY-MM-DD/`.

---

## Quality Constraints

- Every entry must have a non-empty `short_reason` and `possible_disqualifier`
- `short_reason`: one tight phrase, under 12 words
- `possible_disqualifier`: one tight phrase, under 12 words
- No essays. No valuation math. No multi-sentence descriptions.
- If a name feels too uncertain, set `confidence=low` and reflect that in `triage_rec=no`
- This output feeds Stage B triage — keep it clean, honest, and structured
