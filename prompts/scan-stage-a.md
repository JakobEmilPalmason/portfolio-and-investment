# Stage A: Universe Scan — Execution Template

> **DEPRECATED** — This single-step Stage A prompt has been replaced by two separate prompts:
> - `scan-stage-a1.md` — Universe Assembly (broad raw universe, 150–400 names)
> - `scan-stage-a2.md` — Candidate Filter (ranked/filtered candidates, 80–150 names)
>
> Do not use this file for new runs. It is kept for reference only.

This prompt drives a Stage A universe scan. Stage A is shallow broad discovery only — no deep analysis, no valuation narratives, no umbrella write-ups. Output is a ranked candidate table in JSON, CSV, and markdown.

---

## Inputs

1. **Tracked tickers** — list all directories under `reports/` to get currently tracked names (`already_analyzed=true`)
2. **Seed list** — read `seeds/watchlist.json` for curated inputs (`source_bucket=seed`, `already_analyzed=false` unless also in tracked)
3. **Web search** — use WebSearch for the 4 queries below; max 4 searches total

---

## Web Search Queries (run all 4, skip if results are low quality)

1. `"large cap US stocks biggest earnings beats misses [current month and year]"` → `post_earnings` bucket
2. `"quality large cap stocks near 52 week low [current month and year]"` → `52wk_low` bucket
3. `"highest free cash flow yield large cap stocks [current year]"` → `fcf_roic` bucket
4. `"best US sector leader stocks by market cap technology healthcare industrials consumer [current year]"` → `sector_leader` bucket

For web-discovered names: include only recognizable businesses with reasonable signal quality. Skip micro-caps, SPACs, and noise. Prefer large and mega cap.

---

## Candidate Schema

Each candidate is one JSON object:

```json
{
  "ticker": "AAPL",
  "company": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "source_bucket": ["tracked", "sector_leader"],
  "thesis_tag": "dominant_ecosystem",
  "style_tag": "compounder",
  "short_reason": "Services mix shift expands margins; installed base moat",
  "possible_disqualifier": "China revenue concentration; iPhone saturation",
  "mkt_cap_tier": "mega",
  "already_analyzed": true,
  "priority": "high",
  "triage_rec": "maybe",
  "confidence": "high",
  "as_of_date": "YYYY-MM-DD"
}
```

**Field definitions:**
- `source_bucket` — array; one or more of: `tracked` / `seed` / `sector_leader` / `post_earnings` / `52wk_low` / `52wk_high` / `fcf_roic`
- `thesis_tag` — one of: `dominant_ecosystem` / `monopoly_power` / `secular_growth` / `quality_compounder` / `turnaround` / `mean_reversion` / `post_earnings_dislocation` / `52wk_recovery` / `high_fcf_yield` / `sector_leader`
- `style_tag` — one of: `compounder` / `value` / `cyclical` / `recovery` / `speculative` / `income`
- `mkt_cap_tier` — `mega` (>$200B) / `large` ($10–200B) / `mid` ($2–10B) / `small` (<$2B)
- `confidence` — `high` / `medium` / `low` — your confidence in the signal quality, not the stock

---

## Ranking Rules (apply deterministically)

**priority:**
- `high` if: `post_earnings` or `52wk_low` or `fcf_roic` in source_bucket AND mkt_cap_tier ∈ {mega, large}
- `high` if: `already_analyzed=true` AND thesis_tag ∈ {dominant_ecosystem, quality_compounder, secular_growth}
- `medium` if: `sector_leader` or `seed` in source_bucket (and no high trigger applies)
- `low` otherwise

**triage_rec:**
- `yes` if: `already_analyzed=false` AND priority=high AND confidence ∈ {high, medium}
- `yes` if: `already_analyzed=true` AND source_bucket includes `post_earnings` or `52wk_low`
- `maybe` if: priority=high but no fresh event catalyst (seed/sector_leader only, no dislocation)
- `no` otherwise

**style_tag heuristic:**
- `52wk_low` or turnaround thesis → `recovery`
- `post_earnings_dislocation` → `recovery` or `value`
- `high_fcf_yield` or `mean_reversion` → `value`
- `dominant_ecosystem`, `quality_compounder`, `secular_growth` → `compounder`
- Cyclical industry (energy, materials, shipping, airlines) → `cyclical`
- Small cap, pre-profit → `speculative`
- Default → `compounder` or `income`

---

## Deduplication

If a ticker appears in multiple buckets, create ONE entry with all applicable buckets in the `source_bucket` array.

---

## Output Requirements

### candidates.json
- Valid JSON array of candidate objects
- Sorted: priority=high first, then medium, then low; within same priority: triage_rec=yes → maybe → no
- Target: 50–80 unique tickers

### candidates.csv
- Header: `ticker,company,sector,industry,source_bucket,thesis_tag,style_tag,short_reason,possible_disqualifier,mkt_cap_tier,already_analyzed,priority,triage_rec,confidence,as_of_date`
- `source_bucket`: pipe-delimited string (e.g. `tracked|sector_leader`)
- Quote fields containing commas
- Same sort order as JSON

### candidates.md
- Open with this note verbatim:
  > **Note on seed-origin names:** Tickers tagged `source_bucket=seed` are curated inputs from `seeds/watchlist.json`, not discovered names. They reflect prior knowledge or personal watchlist intent rather than fresh market signals.
- Summary section: total count, counts by bucket, counts by sector, counts by priority, list of triage_rec=yes tickers
- Full flat table: `ticker | company | sector | style_tag | source_bucket | short_reason | possible_disqualifier | mkt_cap_tier | priority | triage_rec | confidence`
- Close with: "Next step: Run Stage B triage on all triage_rec=yes names."

### scan-meta.json
```json
{
  "scan_date": "YYYY-MM-DD",
  "total_candidates": 0,
  "buckets_used": [],
  "counts_by_bucket": {},
  "counts_by_sector": {},
  "counts_by_priority": { "high": 0, "medium": 0, "low": 0 },
  "triage_yes_count": 0,
  "triage_maybe_count": 0,
  "triage_no_count": 0,
  "ranking_rules_version": "v1",
  "ranking_rules": {
    "priority_high": [
      "post_earnings|52wk_low|fcf_roic in source_bucket AND mkt_cap_tier in {mega,large}",
      "already_analyzed=true AND thesis_tag in {dominant_ecosystem,quality_compounder,secular_growth}"
    ],
    "priority_medium": [
      "sector_leader|seed in source_bucket (no high trigger)"
    ],
    "triage_yes": [
      "already_analyzed=false AND priority=high AND confidence in {high,medium}",
      "already_analyzed=true AND post_earnings|52wk_low in source_bucket"
    ],
    "triage_maybe": [
      "priority=high but no fresh event catalyst"
    ]
  }
}
```

---

## Quality Constraints

- Every entry must have a non-empty `short_reason` and `possible_disqualifier`
- `short_reason`: one tight phrase, under 12 words, why it's interesting NOW
- `possible_disqualifier`: one tight phrase, under 12 words, the main risk or reason to skip
- If uncertain about a web-discovered name, set `confidence=low` and note it in `possible_disqualifier`
- No essays. No valuation math. No multi-sentence descriptions.
- Seeds are optional inputs — do not let them dominate if stronger discovered names exist

---

## Output paths

Replace `YYYY-MM-DD` with today's date:
- `scans/YYYY-MM-DD/candidates.json`
- `scans/YYYY-MM-DD/candidates.csv`
- `scans/YYYY-MM-DD/candidates.md`
- `scans/YYYY-MM-DD/scan-meta.json`

Create the directory if it does not exist.
