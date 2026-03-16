# Stage A1: Universe Assembly — Execution Template

This prompt drives Stage A1. Stage A1 is **assembly only** — build a broad raw stock universe from multiple sources, deduplicate, tag metadata. No scoring, no thesis construction, no prioritization. That is Stage A2's job.

---

## Do Not Use the Stage C Framework

The umbrella prompts (01–09) and `assembler.md` define how deep-dive analysis is conducted in Stage C. **Do not apply their criteria, scoring logic, or evaluation structure here.** A1 does not evaluate businesses — it assembles a list. Your only job is inclusion, deduplication, and metadata tagging using the rules in this prompt.

---

## Step 1: Read tracked names

List all directories under `runs/*/reports/` to get currently tracked tickers. Each becomes a candidate with `source_bucket: ["tracked"]` and `already_analyzed: true`.

---

## Step 2: Read seed list

Read `seeds/watchlist.json`. Each seed entry becomes a candidate with `source_bucket: ["seed"]`. If a seed ticker is also tracked, merge: `source_bucket: ["tracked", "seed"]`.

---

## Step 3: Add built-in curated sector lists

These are your prior knowledge — do NOT web search for these. Add every name below as a candidate with the corresponding source_bucket. If a ticker is already in the universe from Step 1–2, merge its source_bucket (do not create a duplicate entry).

### `large_cap_us_quality` (~30 names)
COST, ADP, CTAS, CPRT, ROL, BR, PAYX, SSNC, MKTX, NFLX, VRSK, CSGP, FDS, ICE, CME, CBOE, NDAQ, MSCI, NKE, SBUX, MCD, YUM, HSY, CHD, EL, TPX, MCK, IQV, ISRG, EW

### `large_cap_europe_quality` (~20 names)
Use these tickers/identifiers: MC.PA (LVMH), RMS.PA (Hermès), SAP.DE (SAP), WKL.AS (Wolters Kluwer), OR.PA (L'Oréal), CFR.SW (Richemont), ADYEN.AS (Adyen), CRH (CRH plc), DSY.PA (Dassault Systèmes), EL.PA (EssilorLuxottica), KER.PA (Kering), STMN.SW (Straumann), LONN.SW (Lonza), NOVO-B.CO (Novo Nordisk), ASML.AS (ASML), DSV.CO (DSV), MAERSK-B.CO (Maersk), ORSTED.CO (Ørsted), RKT.L (Reckitt), ICG.L (InterContinental Hotels)

### `semis_and_infra` (~15 names)
NVDA, TSM, AMAT, LRCX, KLAC, MRVL, AVGO, ARM, QCOM, ADI, TXN, MPWR, ON, ACLS, ONTO

### `healthcare_quality` (~15 names)
LLY, NVO, AZN, ABBV, UNH, IQVIA, BSX, EW, STE, VEEV, DOCS, MCK, IDXX, WST, MTD

### `industrial_compounders` (~15 names)
ITW, EMR, PH, AME, WCN, RSG, GWW, MSC, CSX, NSC, UNP, XPO, EXPD, ODFL, TDG

### `financial_quality` (~15 names)
JPM, CB, AJG, AFL, MKL, RLI, MSCI, NDAQ, ICE, CME, FDS, MKTX, BX, KKR, GS

### `consumer_quality` (~15 names)
COST, NKE, SBUX, MCD, YUM, HSY, CHD, PG, KO, PEP, EL, SHW, POOL, TPX, DXCM

> **Note on deduplication:** If COST, NKE, SBUX etc. appear in both `large_cap_us_quality` and `consumer_quality`, create ONE entry with both buckets in the source_bucket array. Same for any overlap with tracked/seed.

---

## Step 4: Web searches (up to 6 queries)

Run these web searches for event/signal enrichment. Add discovered names not already in the universe. Skip micro-caps (<$2B), SPACs, pre-revenue companies, and pure commodity plays.

1. `"notable US earnings beats misses large cap [current month year]"` → `post_earnings`
2. `"quality large cap stocks near 52-week low [current month year]"` → `52wk_low`
3. `"quality large cap stocks near 52-week high momentum [current month year]"` → `52wk_high`
4. `"highest free cash flow yield large cap stocks [current year]"` → `fcf_roic`
5. `"dominant sector leader stocks by market cap [current year]"` → `sector_leader`
6. (optional) `"quality European large cap stocks [current year]"` if Europe coverage feels thin → `large_cap_europe_quality`

For web-discovered names: include only recognizable businesses. Prefer mega and large cap. Set `confidence: "medium"` for web-discovered names unless well-known.

---

## Step 5: Deduplication

One entry per ticker. If a ticker appears in multiple sources/buckets, create ONE object with all applicable buckets in the `source_bucket` array.

**Anti-domination check:** Count tracked + seed combined. If they would exceed 20% of total, that's a signal the curated lists are under-represented — ensure all curated sector names were added.

---

## A1 Candidate Schema (minimal — no scoring fields)

```json
{
  "ticker": "COST",
  "company": "Costco Wholesale Corp.",
  "sector": "Consumer",
  "industry": "Warehouse Clubs",
  "source_bucket": ["large_cap_us_quality", "consumer_quality"],
  "mkt_cap_tier": "mega",
  "geography": "US",
  "already_analyzed": false,
  "as_of_date": "YYYY-MM-DD"
}
```

**Field definitions:**
- `ticker` — exchange ticker (use primary listing ticker)
- `company` — full company name
- `sector` — one of: Technology / Financials / Healthcare / Industrials / Consumer / Communication Services / Energy / Materials / Real Estate / Utilities
- `industry` — short industry label
- `source_bucket` — array of all applicable buckets from the list above
- `mkt_cap_tier` — `mega` (>$200B) / `large` ($10–200B) / `mid` ($2–10B)
- `geography` — `US` / `Europe` / `Asia` / `Other`
- `already_analyzed` — true if ticker directory exists in any `runs/*/reports/`
- `as_of_date` — today's date (YYYY-MM-DD)

**Do NOT include:** thesis_tag, style_tag, short_reason, possible_disqualifier, priority, triage_rec, confidence — those are added by Stage A2.

---

## Output Requirements

### universe.json
- Valid JSON array of candidate objects
- No specific sort order required (A2 will sort)
- Target: **150–400 unique tickers**

### universe-meta.json
```json
{
  "run_date": "YYYY-MM-DD",
  "total_candidates": 0,
  "buckets_used": [],
  "counts_by_bucket": {},
  "counts_by_sector": {},
  "counts_by_geography": { "US": 0, "Europe": 0, "Asia": 0, "Other": 0 },
  "mkt_cap_distribution": { "mega": 0, "large": 0, "mid": 0 },
  "already_analyzed_count": 0,
  "tracked_plus_seed_pct": 0.0,
  "web_queries_run": [],
  "concentration_warnings": [],
  "stage": "A1"
}
```

`concentration_warnings` is an array of human-readable strings. Populate it when any of these thresholds are exceeded:
- `tracked_plus_seed_pct > 20%` → add: `"tracked_plus_seed_pct > 20%: actual X%"`
- Any single discovery bucket > 25% of total → add: `"bucket {name} exceeds 25%: actual X%"`
- Any single sector > 35% of total → add: `"sector {name} exceeds 35%: actual X%"`

If no thresholds are exceeded, leave the array empty: `[]`

---

## Output Paths

Write to the current week's scan directory:
- `runs/{CURRENT_WEEK}/scan/universe.json`
- `runs/{CURRENT_WEEK}/scan/universe-meta.json`

Create the directory if it does not exist.

---

## Quality Constraints

- No essays. No valuation math. No thesis writing.
- Every entry must have ticker, company, sector, source_bucket, mkt_cap_tier, geography
- Skip anything that is: micro-cap (<$2B), SPAC, pre-revenue startup, pure commodity, or highly speculative
- Europe names: use the primary exchange ticker (e.g. MC.PA not LVMHF)
- This output feeds Stage A2 — keep it clean and structured
