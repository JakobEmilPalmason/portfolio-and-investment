# Phase 1 Implementation Review — EDGAR Fetch + XBRL Extraction

You are an expert code reviewer and improver. Make sure to be extremely specific and critical and honest on implementation and things that could be better. Any shortcuts taken I'll be unhappy about.

## Context

This project is a Buffett-style investment analysis pipeline. Analysis agents consume context files from `context/{TICKER}/`. The existing `scripts/fetch-financials.py` writes `context/{TICKER}/financials.md` from Yahoo Finance. Phase 1 adds a second data source: SEC EDGAR filings via the `edgartools` library, writing `context/{TICKER}/edgar-10k.md`.

Phase 1 scope: filing metadata + XBRL financial statements + supplementary metrics only. No narrative sections (MD&A, Risk Factors) — that's Phase 2.

## Your Inputs

Read these files in order:

1. **The implementation plan:** `research-material/filings-model/phase1-implementation-manual.md` — architecture, design decisions, output format, verification matrix
2. **The broader context:** `research-material/filings-model/agent3.md` — Section 2 (architecture), Section 3 steps 1-3 (Phase 1 steps), Section 10 (phased rollout)
3. **The existing peer script:** `scripts/fetch-financials.py` — this is the pattern the new code must match in style, CLI conventions, and integration
4. **The pipeline entry point:** `run.sh` — check lines 108, 395-397, 424-435, and 846 for integration
5. **The new package:**
   - `scripts/sec_edgar/__init__.py`
   - `scripts/sec_edgar/client.py`
   - `scripts/sec_edgar/xbrl.py`
   - `scripts/sec_edgar/render.py`
   - `scripts/sec_edgar/__main__.py`
6. **The entry point wrapper:** `scripts/fetch-edgar.py`
7. **The gitignore:** `.gitignore` — verify `cache/` was added (even though Phase 1 doesn't use it — it's pre-staging)

---

## Part 1: Plan vs Implementation

For each item below, verify whether the implementation matches the plan. State **DONE**, **PARTIAL**, **MISSING**, or **DEVIATED** with an explanation.

### 1.1 Architecture: Library-First Extraction

The plan says: use `Company.get_financials()` as the foundation, NOT raw XBRL DataFrame extraction with a custom CONCEPT_MAP. This was a critical review finding — the library already provides `get_financial_metrics()` (15 standardized metrics) and multi-year statement DataFrames.

Check:
- [ ] `xbrl.py` calls `financials.get_financial_metrics()` for Layer 1
- [ ] `xbrl.py` calls `financials.income_statement().to_dataframe()`, `.balance_sheet()`, `.cash_flow_statement()` for Layer 2
- [ ] There is NO manual CONCEPT_MAP dictionary with raw `us-gaap:` concept strings as a primary extraction mechanism
- [ ] Supplementary metrics (EPS, R&D, SBC, etc.) are extracted from statement DataFrames, not from raw XBRL facts

### 1.2 Form Types

The plan says: `["10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"]` — handles foreign private issuers.

Check:
- [ ] `client.py` uses this exact form list (not just `["10-K", "10-K/A"]`)
- [ ] Run `python3 scripts/fetch-edgar.py NVO` and verify it produces output (NVO files 20-F)

### 1.3 Identity Handling

The plan says: `EDGAR_IDENTITY` env var, default `"Portfolio Research Tool research@example.com"`.

Check:
- [ ] Default is NOT `research@localhost` (SEC rejects this)
- [ ] The env var actually works: `EDGAR_IDENTITY="Test User test@test.com" python3 scripts/fetch-edgar.py INTU`

### 1.4 Non-US Ticker Handling

The plan says: catch `CompanyNotFoundError`, warn, return None. No dot-suffix heuristic.

Check:
- [ ] `client.py` catches `CompanyNotFoundError` specifically (not a bare `except`)
- [ ] There is no `if "." in ticker: skip` logic anywhere
- [ ] `python3 scripts/fetch-edgar.py MC.PA` produces a warning, not a crash

### 1.5 Freshness

The plan says: check `context/{TICKER}/edgar-10k.md` mtime < 24h.

Check:
- [ ] `_is_fresh()` in `client.py` matches the pattern from `fetch-financials.py:is_fresh()` (lines 684-690)
- [ ] `--force` flag bypasses freshness check
- [ ] Run twice in a row — second run shows "skipped (fresh)"

### 1.6 Sign Conventions

The plan says: statement DataFrames have signs as reported. `get_financial_metrics().capital_expenditures` is positive. Both documented.

Check:
- [ ] The rendered markdown explicitly notes the capex sign convention
- [ ] Cash flow statement note says "Outflows are negative" or similar
- [ ] Metrics section note says "CapEx shown as positive (absolute value)" or similar

### 1.7 Total Debt

The plan says: sum long-term + short-term debt. Label as "Total Debt (LT + ST)".

Check:
- [ ] `xbrl.py` extracts both `long_term_debt` and `short_term_debt`
- [ ] There is a `total_debt_lt_st` (or similar) composite metric that sums them
- [ ] The label in the output clearly indicates it's LT + ST, not just "Total Debt"
- [ ] If only LT exists (no ST), the total still works (doesn't crash or show 0)

### 1.8 D&A Handling

The plan says: try combined `DepreciationAndAmortization` first, else sum components.

Check:
- [ ] Code tries the combined concept first
- [ ] Falls back to summing `depreciation` + `amortization`
- [ ] The summed version is labeled differently (e.g., "summed" note) so agents know it's a composite

### 1.9 Deduplication

The plan says: `drop_duplicates(subset=['concept', first_date_col])` on statement DataFrames.

Check:
- [ ] `_get_statement_df()` actually calls `drop_duplicates`
- [ ] The subset makes sense — does it correctly keep only one row per concept?
- [ ] If a company reports both consolidated and segment revenue with the same concept, which survives?

### 1.10 Currency

The plan says: `get_currency_symbol()` for native filing currency.

Check:
- [ ] Currency detection uses the library, not hardcoded "$"
- [ ] There's a fallback if `get_currency_symbol()` fails
- [ ] NVO output uses "kr" (or equivalent), not "$"

### 1.11 run.sh Integration

The plan says: `cmd_extract()`, dispatch entry, SEC fetch in analyze flow (non-blocking).

Check:
- [ ] `cmd_extract()` function exists and delegates to `scripts/fetch-edgar.py`
- [ ] `extract)` case exists in the dispatch table
- [ ] `cmd_analyze()` calls fetch-edgar.py after fetch-financials.py (line ~424)
- [ ] The analyze call uses `--quiet` and has `|| { echo "WARNING..."; }` for non-blocking
- [ ] The `extract` command appears in the usage help text
- [ ] `./run.sh extract INTU` actually works

---

## Part 2: Code Quality Deep Dive

### 2.1 Error Handling

Walk through every `try/except` block in the codebase. For each:
- Does it catch a specific exception or bare `Exception`?
- Does it swallow the error silently or log/warn?
- Is the `except` justified, or is it hiding a bug that should surface?

Specific red flags to look for:
- [ ] `client.py` line 89: `except Exception: pass` on filing metadata. Is it really OK to silently swallow ALL metadata failures? What if `get_filings()` raises because of a network error — should the user see nothing?
- [ ] `xbrl.py` `_get_statement_df`: bare `except Exception` that returns empty DataFrame. This means a pandas bug, a column name change in edgartools, or a type error all disappear silently. Should at least log a warning.
- [ ] Count total `except Exception` blocks. How many are there? Is this a pattern of defensive programming or a pattern of hiding problems?

### 2.2 The `_find_value` Partial Match Problem

`xbrl.py` `_find_value()` first tries exact match on concept, then falls back to `str.contains()` (case-insensitive partial match).

This is dangerous:
- Pattern `"InterestExpense"` would partial-match `"InterestExpenseDebt"`, `"InterestExpenseOperating"`, `"InterestExpenseRelatedParty"`, etc.
- Pattern `"Amortization"` would match `"AmortizationOfIntangibleAssets"`, `"AmortizationOfDebtIssuanceCosts"`, `"AmortizationOfFinancingCosts"`, etc.
- Pattern `"LongTermDebt"` would match `"LongTermDebtNoncurrent"`, `"LongTermDebtCurrent"`, `"LongTermDebtFairValue"`, etc.

Check:
- [ ] How many concept patterns in `_extract_supplementary()` rely on partial match as a fallback?
- [ ] For each one: could the partial match return a wrong value? List specific examples.
- [ ] Is there a test that catches a partial match returning the wrong thing?

### 2.3 The `filings[0]` vs `.latest()` Question

`client.py` line 84: `latest = filings[0]`

The plan's API testing showed `filings.latest()` returns a single `EntityFiling`. The implementation uses `filings[0]` instead.

Check:
- [ ] Is `filings[0]` equivalent to `filings.latest()`? Or does the ordering differ?
- [ ] If `get_filings()` returns results sorted by filing_date descending, `[0]` works. But is this guaranteed by the library?
- [ ] What happens if `filings` is empty — does `filings[0]` raise `IndexError`? Is this caught?

### 2.4 Statement DataFrame Structure Assumptions

The code assumes statement DataFrames have columns: `concept`, `label`, `abstract`, `dimension`, `is_breakdown`, `balance`, `weight`, `preferred_sign`, `parent_concept`, `parent_abstract_concept`, and date columns.

Check:
- [ ] Are all these columns actually present for every company? Test with at least 3 tickers.
- [ ] `_filter_consolidated()` filters on `abstract == False` and `dimension == False`. What types are these columns? Are they actually booleans, or strings like `"True"`/`"False"`, or integers?
- [ ] `_get_date_columns()` uses a hardcoded skip-set. If edgartools adds a new metadata column in a future version, it would be treated as a date column. Is this fragile?

### 2.5 `_fmt_per_share` Currency Hardcoding

`render.py` `_fmt_per_share()` always formats as `$13.67` regardless of currency.

Check:
- [ ] For NVO (Danish Krone), EPS should show "kr" not "$"
- [ ] Is the currency parameter threaded through to per-share formatting?
- [ ] Same check for `_fmt_shares` — does it need a currency symbol?

### 2.6 Statement Rendering Row Count

The plan says output should be "compact ~3-5K tokens". The implementation renders ALL rows from the statement DataFrames.

Check:
- [ ] How many rows does `income_statement().to_dataframe()` return for INTU? For AAPL? For a complex filer like JPM?
- [ ] For a bank with 80+ income statement line items, would the output exceed the 3-5K target?
- [ ] Is there any row limit or filtering beyond the `abstract`/`dimension` filter?

### 2.7 Multi-Year Column Ordering

Date columns come from `_get_date_columns()` which returns columns in DataFrame order (not sorted).

Check:
- [ ] Are dates always in descending order (most recent first)? Or could they be shuffled?
- [ ] In the supplementary section, `sorted(all_dates, reverse=True)[:4]` explicitly sorts. But the statement sections don't sort — they use whatever order the DataFrame provides.
- [ ] Is the DataFrame column order from edgartools guaranteed to be newest-first?

---

## Part 3: Functional Verification

Run these actual tests. Report exact output.

### 3.1 Core Smoke Test
```bash
python3 scripts/fetch-edgar.py INTU
```
Verify:
- Output file exists at `context/INTU/edgar-10k.md`
- Revenue shows ~$18.8B
- Has 3 years of income statement data
- Form type shows 10-K
- File size is reasonable (~3-5K tokens ≈ ~12-20KB)

### 3.2 Non-US Ticker
```bash
python3 scripts/fetch-edgar.py MC.PA
```
Verify: produces warning, no output file, no crash.

### 3.3 Foreign Filer (20-F)
```bash
python3 scripts/fetch-edgar.py NVO
```
Verify:
- Output exists
- Form type shows 20-F
- Currency is NOT "$" (should be "kr" or similar)
- EPS values use correct currency (NOT hardcoded "$")

### 3.4 Freshness Skip
```bash
python3 scripts/fetch-edgar.py INTU
python3 scripts/fetch-edgar.py INTU
```
Second run should show "skipped (fresh)".

### 3.5 Force Re-fetch
```bash
python3 scripts/fetch-edgar.py --force INTU
```
Should re-fetch even though fresh.

### 3.6 BRK.B (Dot in Ticker, US Filer)
```bash
python3 scripts/fetch-edgar.py BRK.B
```
Should work — BRK.B resolves to CIK 1067983.

### 3.7 Invalid Ticker
```bash
python3 scripts/fetch-edgar.py ZZZZZ
```
Should warn, not crash.

### 3.8 Multi-Ticker
```bash
python3 scripts/fetch-edgar.py INTU V JPM
```
All three should produce output. Check that JPM (complex bank filer) doesn't break the statement parser.

### 3.9 run.sh Integration
```bash
./run.sh extract INTU
```
Should work identically to the direct python call.

### 3.10 Cross-Validation
After running INTU through both scripts, compare key numbers:
- Revenue in `edgar-10k.md` vs `financials.md` — should be within 5%
- Net income in both — should be close
- If they disagree significantly, which is more trustworthy and why?

### 3.11 Output Token Count
```bash
wc -w context/INTU/edgar-10k.md
```
Estimate tokens as words × 1.3. Is it within the ~3-5K token target? If it's >8K tokens, that's a problem — every umbrella agent pays for these tokens 9 times.

---

## Part 4: Comparison Against Peer Script

`scripts/fetch-financials.py` is the gold standard pattern. Compare:

### 4.1 CLI Feature Parity

| Feature | fetch-financials.py | fetch-edgar.py | Match? |
|---------|-------------------|----------------|--------|
| Single ticker | Yes | ? | |
| Multiple tickers | Yes | ? | |
| `--force` flag | Yes | ? | |
| `--quiet` flag | Yes | ? | |
| `--all-reports` flag | Yes | ? | |
| `--all-queue STATE` flag | Yes | ? | |
| Rate limiting between tickers | Yes (1s sleep) | ? | |
| Summary line at end | Yes | ? | |
| Exit code 1 on any failure | Yes | ? | |

For any "No" in the last column: is this an intentional omission or an oversight? `--all-reports` and `--all-queue` are particularly important for batch operations.

### 4.2 Output Format Consistency

Both scripts write to `context/{TICKER}/`. Compare header format, section structure, and warning format against `financials.md`. Agents consume both files — inconsistent formatting (different date labels, different number formatting, different section headers) makes it harder for agents to parse.

### 4.3 Return Value Semantics

`fetch_10k()` returns `None` for both "skipped (fresh)" AND "company not found". The caller in `__main__.py` counts both as `skipped`.

Check:
- [ ] Is this correct? A fresh skip is expected; a company-not-found is a warning/failure.
- [ ] Compare to `fetch-financials.py` — how does it distinguish these cases?
- [ ] The summary line says "skipped" for both. Should "company not found" count as "failed"?

---

## Part 5: Edge Cases & Robustness

### 5.1 Company With No Financials

Some SEC filers have filings but no extractable XBRL financials (e.g., shell companies, SPACs in early stages).

Check: does `get_financials()` return `None` for any such company? Does the code handle `financials = None`?

### 5.2 Company With Only 1 Year of Data

Some IPOs or new filers have only 1 year in their statements.

Check: does the multi-year rendering handle 1 column gracefully? Or does it assume ≥2?

### 5.3 Very Large Filer

Banks (JPM), conglomerates (BRK), and insurance companies have much longer financial statements.

Check: run `python3 scripts/fetch-edgar.py JPM` and measure the output size. Is it still within the 3-5K token budget? If not, does the plan address this?

### 5.4 Ticker Already Has Context

If `context/INTU/` already has `financials.md` and custom research files, does `edgar-10k.md` get written alongside them without disturbing anything?

### 5.5 Concurrent Runs

If two `./run.sh analyze` processes run simultaneously for different tickers, does `set_identity()` cause a race? (It modifies global state in the `edgar` package.)

---

## Output Format

Structure your review as:

```
## Plan vs Implementation
[For each item in Part 1: DONE / PARTIAL / MISSING / DEVIATED + specifics]

## Code Quality Issues
[Every problem found in Part 2, with file:line references]

## Test Results
[Exact output from each Part 3 test]

## Peer Script Gaps
[Table from Part 4 filled in, plus any inconsistencies found]

## Edge Case Results
[Findings from Part 5]

## Verdict
[One of: READY / NEEDS FIXES / NEEDS REDESIGN]

## Required Changes Before Merge
[Numbered list, ordered by severity — things that MUST be fixed]

## Optional Improvements
[Nice-to-haves that don't block merge]
```
