# Phase 1 Implementation Review — EDGAR Fetch + XBRL Extraction

**Reviewer:** Claude Opus 4.6
**Date:** 2026-03-19
**Verdict:** NEEDS FIXES — architecture sound, 2 critical data integrity bugs

---

## Plan vs Implementation

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.1 | Library-first extraction (`get_financial_metrics()` + statement DataFrames) | **DONE** | No manual CONCEPT_MAP. Layer 1 + Layer 2 as planned. |
| 1.2 | Form types include 20-F, 40-F | **DONE** | `client.py:24` — exact match. NVO produces 20-F output. |
| 1.3 | Identity via `EDGAR_IDENTITY` env var, safe default | **DONE** | Default `"Portfolio Research Tool research@example.com"` — not `research@localhost`. |
| 1.4 | Non-US ticker handling (catch `CompanyNotFoundError`, no dot heuristic) | **DONE** | `client.py:61` catches specific exception. No `if "." in ticker` anywhere. |
| 1.5 | Freshness check (24h mtime on output file) | **DONE** | Matches `fetch-financials.py` pattern exactly. `--force` bypasses. |
| 1.6 | Sign conventions documented in output | **DONE** | CapEx note, cash flow "outflows are negative", income "signs as reported". |
| 1.7 | Total debt = LT + ST, labeled clearly | **DONE** | Handles missing ST gracefully. |
| 1.8 | D&A: try combined first, sum components as fallback | **DONE** | Summed version labeled distinctly. |
| 1.9 | Deduplication on statement DataFrames | **DONE** | `drop_duplicates(subset=["concept", first_date_col])`. |
| 1.10 | Currency from library, not hardcoded | **PARTIAL** | `_fmt_amount()` uses correct currency. **`_fmt_per_share()` hardcodes `$`** — NVO EPS shows `$23.06` not `kr23.06`. |
| 1.11 | run.sh integration (cmd_extract, dispatch, analyze flow) | **DONE** | All four integration points confirmed. |

---

## Code Quality Issues

### CQ-1: CRITICAL — `_fmt_per_share()` hardcodes `$` (`render.py:40`)

`_fmt_per_share(value)` always returns `f"${value:.2f}"`. Currency is not threaded through. Every non-USD filer shows `$` on per-share values. NVO EPS: `$23.06` instead of `kr23.06`.

Affects: statement rendering (`render.py:179`) and supplementary EPS (`render.py:240`).

### CQ-2: CRITICAL — Partial match produces garbage data (`xbrl.py` `_find_value()` / `_extract_multi_year()`)

V's supplementary "Amortization" shows **$15.75B**. V's actual D&A is ~$1.22B (D&A Combined shows correctly). The $15.75B is Visa's **client incentive amortization** — a completely different concept.

Root cause: `_extract_supplementary()` line 149 uses `"Amortization"` as a fallback pattern. After exact matches fail, `str.contains("Amortization", case=False)` matches the first concept containing "amortization" in its name — which for Visa is a client incentive concept, not D&A.

**This is live in `context/V/edgar-10k.md` right now.** Agents reading this file would use $15.75B amortization in valuation math.

Other at-risk patterns: `"InterestExpense"`, `"LongTermDebt"`, `"ResearchAndDevelopment"`, `"ShortTermDebt"` — any could partial-match the wrong concept for certain filers.

### CQ-3: HIGH — Silent `except Exception: pass` on filing metadata (`client.py:89-90`)

Network errors, rate limits, or API changes produce `form_type=None`, `filing_date=None` with zero indication to the user.

### CQ-4: HIGH — Silent `except Exception` in `_get_statement_df()` (`xbrl.py:231-232`)

Returns empty DataFrame on any error — pandas bugs, edgartools API changes, type errors all vanish. User sees "Income statement not available" without knowing why.

### CQ-5: HIGH — `fetch_10k()` returns `None` for both "fresh skip" and "company not found" (`client.py:55-56, 63-64`)

`__main__.py` counts both as "skipped". Summary might show "3 skipped" when 2 were fresh and 1 doesn't exist on EDGAR. `fetch-financials.py` tracks `(ticker, "ok"|"skipped"|"error: ...")` — more granular.

### CQ-6: MEDIUM — `filings[0]` instead of `filings.latest()` (`client.py:84`)

Assumes descending chronological order. Library provides `.latest()` which is explicit.

### CQ-7: MEDIUM — NVO Operating Income mismatch

Metrics show `-kr300M`. Income statement shows `kr127.66B` operating profit. `get_financial_metrics()` likely matched a non-standard concept. No cross-check exists between metrics and statement values.

### CQ-8: MEDIUM — No row limit on statement rendering

INTU/V/NVO are within 3-5K token budget (~1.5-2.2K tokens each). Complex filers (JPM, BRK) with 80-100+ line items per statement are untested and could blow budget. Every agent pays these tokens 9x.

### CQ-9: MEDIUM — Date columns not explicitly sorted (`xbrl.py:27`)

`_get_date_columns()` returns DataFrame column order. Supplementary section sorts explicitly (`render.py:222`) but statements don't. Works today because edgartools happens to return newest-first.

### CQ-11: LOW — `latest_val` takes oldest year, not newest (`xbrl.py:127, 134`)

`sorted()` ascending + `values()[0]` = oldest. Limited impact (only used in fallback render path).

Exception handler audit: 2 of 7 `except Exception` blocks silently swallow errors (CQ-3, CQ-4). The rest log or warn appropriately.

---

## Peer Script Gaps

| Feature | fetch-financials.py | fetch-edgar.py | Match? |
|---------|-------------------|----------------|--------|
| Single/multiple tickers | Yes | Yes | Yes |
| `--force` / `--quiet` | Yes | Yes | Yes |
| `--all-reports` | Yes | **No** | **No** |
| `--all-queue STATE` | Yes | **No** | **No** |
| Rate limiting between tickers | Yes (1s sleep) | No (library-internal) | No |
| Summary line / exit codes | Yes | Yes | Yes |
| Progress counter `[1/5]` | Yes | **No** | **No** |

`--all-reports` and `--all-queue` are significant for batch pipeline operations. Should be a separate PR.

---

## Test Results (from existing output files)

| Test | Result | Issues |
|------|--------|--------|
| INTU (US 10-K) | Revenue $18.83B, 3yr income stmt, 202 lines, ~2,240 tokens | Clean |
| NVO (20-F foreign filer) | kr currency, 163 lines, ~1,535 tokens | EPS shows `$` not `kr`. Op income -kr300M vs kr127.66B in statement. |
| V (US 10-K) | $40B revenue, 192 lines, ~1,979 tokens | **Amortization $15.75B is wrong** (should be ~$1.22B) |
| MC.PA (non-EDGAR) | "Company not found" warning, no crash | Clean |
| BRK.B (dot ticker, US) | Resolves correctly | Clean |
| Freshness skip | Second run shows "skipped (fresh)" | Clean |
| `--force` | Re-fetches despite fresh | Clean |
| run.sh dispatch | `./run.sh extract INTU` works | Clean |

Token budget: all tested tickers within 3-5K target. Complex filers (JPM) untested.

---

## Verdict: **NEEDS FIXES**

Architecture is sound — two-layer extraction, library-first approach, freshness handling, run.sh integration, and output format are well-executed. Two critical data integrity bugs and several meaningful gaps need fixing.

---

## Required Changes (fix order)

1. **CQ-2: Remove partial match fallback** — `_find_value()` and `_extract_multi_year()` in `xbrl.py`. Drop the `str.contains()` fallback entirely. Prefer "—" over wrong data. V's output is actively wrong.

2. **CQ-1: Thread currency through `_fmt_per_share()`** — `render.py:36-40`. Add `currency` param, update call sites in `_render_statement()` and `_render_supplementary()`.

3. **CQ-3 + CQ-4: Add warnings to silent exception handlers** — `client.py:89-90` and `xbrl.py:231-232`. At minimum, print to stderr when not quiet.

4. **CQ-5: Distinguish fresh-skip from error** — Return a sentinel or named status from `fetch_10k()` so `__main__.py` can count correctly.

5. **CQ-9: Sort date columns** — One line in `_get_statement_df()`: `date_cols = sorted(_get_date_columns(filtered), reverse=True)`.

6. **CQ-6: Use `filings.latest()`** — One line change in `client.py:84`.

Items 1-5 are a couple hours of focused work. `--all-reports`/`--all-queue` flags are a separate PR.

## Optional Improvements

- Row limit for complex filers (CQ-8)
- Progress counter `[1/5]` to match peer script
- Inter-ticker sleep for batch operations
- Cross-check between metrics and statement values for foreign filers (CQ-7)
- Fix `latest_val` ordering (CQ-11)
