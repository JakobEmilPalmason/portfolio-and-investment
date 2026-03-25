# Phase 1 Implementation Manual — EDGAR Fetch + XBRL Extraction

## Overview

SEC EDGAR filing data extraction via `edgartools`. Outputs `context/{TICKER}/edgar-10k.md` — the pipeline picks it up automatically alongside `financials.md`.

Phase 1 scope: XBRL facts + multi-year financial statements only. No narrative sections (Phase 2).

---

## Architecture

**Foundation**: `Company(ticker).get_financials()` provides:
- `get_financial_metrics()` → 15 standardized metrics (dict of floats)
- `income_statement().to_dataframe()` → ~44 line items, 3 years, sign-normalized
- `balance_sheet().to_dataframe()` → ~39 line items, 2 years
- `cash_flow_statement().to_dataframe()` → ~54 line items, 3 years
- `get_currency_symbol()` → "$", "kr", "€", etc.

**Supplementary XBRL**: ~12 metrics not in `get_financial_metrics()` are extracted from statement DataFrames: EPS basic/diluted, R&D, SG&A, interest expense, gross profit, long-term debt, short-term debt, total debt, depreciation, amortization, D&A combined, SBC, dividends paid.

**No manual CONCEPT_MAP needed**. Statement DataFrames already normalize concepts.

---

## Files

### Package: `scripts/sec_edgar/`

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `fetch_10k`, `extract_financials` |
| `client.py` | EDGAR client: identity, freshness, Company lookup, orchestration |
| `xbrl.py` | Financial extractor: Layer 1 (metrics) + Layer 2 (statements) |
| `render.py` | Markdown renderer: compact ~3-5K token output |
| `__main__.py` | CLI: argparse entry point |

### Entry point
| File | Purpose |
|------|---------|
| `scripts/fetch-edgar.py` | Thin wrapper that delegates to `sec_edgar.__main__` |

### Modified files
| File | Change |
|------|--------|
| `run.sh` | Added `cmd_extract()`, dispatch entry, SEC fetch in analyze flow |
| `.gitignore` | Added `cache/` line |

---

## Key Design Decisions

### Identity
`set_identity()` uses `EDGAR_IDENTITY` env var. Default: `"Portfolio Research Tool research@example.com"`.

### Form types
`["10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"]` — handles US filers AND foreign private issuers.

### Non-US tickers
`CompanyNotFoundError` from `Company()` is caught and warned. No dot-suffix heuristic.

### Rate limiting
Library built-in (pyrate-limiter, 9 req/sec). No manual sleep.

### Freshness
Check `context/{TICKER}/edgar-10k.md` mtime < 24h. Skip if fresh unless `--force`.

### Sign convention
Statement DataFrames have signs as reported (expenses positive, outflows negative in cash flow). `get_financial_metrics().capital_expenditures` is positive (absolute). Both documented in output.

### D&A handling
Try `DepreciationAndAmortization` combined concept first. If missing, sum Depreciation + Amortization components.

### Total debt
Sum long-term + short-term debt from balance sheet. Labeled as "Total Debt (LT + ST)".

### Currency
`get_currency_symbol()` returns the filing's native currency. All amounts use that currency symbol.

### Dedup
`drop_duplicates(subset=['concept', first_date_col])` on statement DataFrames before extraction.

---

## Output Format

`context/{TICKER}/edgar-10k.md` contains:

1. **Filing metadata** table (company, CIK, form type, dates, accession)
2. **Key Financial Metrics** (15 items from `get_financial_metrics()`)
3. **Income Statement** (consolidated, multi-year, full line items)
4. **Balance Sheet** (consolidated, multi-year, full line items)
5. **Cash Flow Statement** (consolidated, multi-year, full line items)
6. **Supplementary Metrics** (EPS, R&D, SBC, D&A, debt breakdown, multi-year)
7. **Data Gaps & Warnings** (None values, missing statements, currency notes)

Number formatting:
- Dollar amounts: `$18.83B` / `$84M` based on magnitude
- Per-share: `$13.67`
- Shares: `283M`
- Ratios: `1.36x`

---

## Usage

```bash
# Single ticker
python3 scripts/fetch-edgar.py INTU

# Multiple tickers
python3 scripts/fetch-edgar.py INTU V NVO

# Force re-fetch
python3 scripts/fetch-edgar.py --force INTU

# Quiet mode (for pipeline integration)
python3 scripts/fetch-edgar.py --quiet INTU

# Via run.sh
./run.sh extract INTU
./run.sh extract INTU V NVO
```

Integrated into `./run.sh analyze TICKER` — runs automatically after yfinance fetch.

---

## Verification Results

| Test | Result |
|------|--------|
| `fetch-edgar.py INTU` | Revenue $18.83B, 3yr income statement, 10-K |
| `fetch-edgar.py MC.PA` | "Company not found" warning, no output |
| `fetch-edgar.py NVO` | 20-F form, currency = kr, revenue kr309.06B |
| Run twice | Second skips ("fresh") |
| `--force` | Re-fetches |
| `./run.sh extract INTU` | Works via dispatch |
| `fetch-edgar.py BRK.B` | Resolves correctly |
| Multi-ticker | Processes sequentially |

---

## Phase 2 (Future)

Narrative section parsing via `TenK`/`TwentyF` object's parsed sections. See `__init__.py` comment.
