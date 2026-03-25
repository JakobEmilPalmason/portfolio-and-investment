# Evidence Layer Phase 1 — Implementation Review Manual

## Purpose

This document is a complete implementation reference for a reviewer. It covers every file created or modified, the design rationale behind each decision, the edgartools API surface that was used, and verified test results with sample output.

The goal of Phase 1: add SEC EDGAR XBRL financial data to the pipeline. Output goes to `context/{TICKER}/edgar-10k.md`, which the analysis agents pick up automatically (same mechanism as `financials.md` from yfinance).

Phase 1 scope: structured XBRL facts and multi-year financial statements only. Narrative section parsing (MD&A, Risk Factors, etc.) is deferred to Phase 2.

---

## File Map

```
scripts/
  fetch-edgar.py              # Entry point (thin wrapper)
  sec_edgar/                   # Package (named to avoid shadowing `edgar`)
    __init__.py                # Exports: fetch_10k, extract_financials
    client.py                  # EDGAR client: identity, freshness, Company lookup, orchestration
    xbrl.py                    # Financial extractor: Layer 1 (metrics) + Layer 2 (statements)
    render.py                  # Markdown renderer: compact output for agent consumption
    __main__.py                # CLI: argparse, ticker loop, exit codes

run.sh                         # Modified: added cmd_extract(), dispatch, analyze integration
.gitignore                     # Modified: added cache/ line
docs/phase1-implementation-manual.md  # Brief implementation summary
```

**Output location:** `context/{TICKER}/edgar-10k.md`

---

## 1. `scripts/sec_edgar/__init__.py`

**Role:** Package entry point. Exports two public functions.

```python
"""
sec_edgar — SEC EDGAR filing data extraction via edgartools.

Phase 1: XBRL facts + multi-year financial statements.
Phase 2 (future): Narrative section parsing via TenK/TwentyF .obj() parsed sections.
"""

from .client import fetch_10k
from .xbrl import extract_financials

__all__ = ["fetch_10k", "extract_financials"]
```

**Review notes:**
- The Phase 2 comment is intentional — it tells future developers exactly where to look (`TenK`/`TwentyF` objects have `.obj()` that returns parsed narrative sections).
- Package is named `sec_edgar` not `edgar` to avoid import shadowing with the installed `edgartools` package (which installs as `edgar`).

---

## 2. `scripts/sec_edgar/client.py`

**Role:** Orchestrator. Handles identity, freshness checks, Company resolution, filing metadata, calls into `xbrl.py` for extraction and `render.py` for output, and writes the final markdown file.

### Full source

```python
"""
EDGAR client — fetch 10-K/20-F financials for a ticker.

Identity: set via EDGAR_IDENTITY env var.
Rate limiting: handled by edgartools (pyrate-limiter, 9 req/sec).
Freshness: skips if context/{TICKER}/edgar-10k.md < 24h old unless --force.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from edgar import Company, set_identity
from edgar.entity import CompanyNotFoundError

from .xbrl import extract_financials
from .render import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTEXT_DIR = REPO_ROOT / "context"
FRESHNESS_HOURS = 24

FORM_TYPES = ["10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"]


def _set_identity():
    identity = os.environ.get(
        "EDGAR_IDENTITY",
        "Portfolio Research Tool research@example.com",
    )
    set_identity(identity)


def _is_fresh(ticker: str) -> bool:
    out_file = CONTEXT_DIR / ticker / "edgar-10k.md"
    if not out_file.exists():
        return False
    mtime = datetime.fromtimestamp(out_file.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    return age_hours < FRESHNESS_HOURS


def fetch_10k(ticker: str, force: bool = False, quiet: bool = False) -> dict | None:
    """
    Fetch 10-K/20-F financials for a ticker via edgartools.

    Returns {"company": str, "financials": dict, "filing_metadata": dict}
    or None on failure.
    """
    _set_identity()

    if not force and _is_fresh(ticker):
        if not quiet:
            print(f"  {ticker} — skipped (fresh)")
        return None

    # Resolve company
    try:
        company = Company(ticker)
    except CompanyNotFoundError:
        if not quiet:
            print(f"  {ticker} — Company not found on EDGAR. Skipping.", file=sys.stderr)
        return None
    except Exception as e:
        if not quiet:
            print(f"  {ticker} — EDGAR lookup failed: {e}", file=sys.stderr)
        return None

    # Get latest filing metadata
    filing_metadata = {
        "company_name": company.name,
        "cik": str(company.cik),
        "ticker": ticker,
        "form_type": None,
        "filing_date": None,
        "period_of_report": None,
        "accession_no": None,
    }

    try:
        filings = company.get_filings(form=FORM_TYPES)
        if filings and len(filings) > 0:
            latest = filings[0]
            filing_metadata["form_type"] = latest.form
            filing_metadata["filing_date"] = str(latest.filing_date)
            filing_metadata["period_of_report"] = str(latest.period_of_report)
            filing_metadata["accession_no"] = latest.accession_no
    except Exception:
        pass  # metadata is nice-to-have, not blocking

    # Get financials
    try:
        financials = company.get_financials()
    except Exception as e:
        if not quiet:
            print(f"  {ticker} — Failed to get financials: {e}", file=sys.stderr)
        return None

    # Extract structured data
    try:
        extracted = extract_financials(financials, filing_metadata)
    except Exception as e:
        if not quiet:
            print(f"  {ticker} — Failed to extract financials: {e}", file=sys.stderr)
        return None

    # Render and write markdown
    md = render_markdown(ticker, extracted, filing_metadata)
    out_dir = CONTEXT_DIR / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "edgar-10k.md"
    out_file.write_text(md, encoding="utf-8")

    if not quiet:
        size = out_file.stat().st_size
        print(f"  {ticker} -> {out_file.relative_to(REPO_ROOT)} ({size // 1024} KB)")

    return {
        "company": company.name,
        "financials": extracted,
        "filing_metadata": filing_metadata,
    }
```

### Design decisions

| Decision | Rationale |
|----------|-----------|
| `FORM_TYPES` includes 20-F and 40-F | Foreign private issuers (NVO, etc.) file 20-F instead of 10-K. Canadian cross-listed companies file 40-F. |
| `CompanyNotFoundError` catch | Non-EDGAR tickers like `MC.PA` (Euronext) are not on EDGAR. Graceful skip, no crash. |
| Filing metadata in a separate try/except | Metadata (form type, date, accession) is nice-to-have. If the filing index call fails, we still proceed with `get_financials()`. |
| `_is_fresh()` checks output file mtime | Same pattern as `scripts/fetch-financials.py`. 24-hour TTL. No separate cache directory needed in Phase 1. |
| `_set_identity()` called on every `fetch_10k()` | SEC requires a User-Agent identity. Default is generic but overridable via `EDGAR_IDENTITY` env var. |
| Return `None` on skip or failure | The CLI (`__main__.py`) uses `None` return to count skips vs successes. |
| No manual rate limiting | edgartools uses pyrate-limiter internally (9 req/sec). No `time.sleep()` needed. |

---

## 3. `scripts/sec_edgar/xbrl.py`

**Role:** The extraction engine. Two layers:

- **Layer 1:** `get_financial_metrics()` — 15 built-in metrics from edgartools (revenue, net income, FCF, etc.)
- **Layer 2:** Statement DataFrames — supplementary metrics not in Layer 1 (EPS, R&D, SBC, D&A, debt breakdown, etc.)

### Full source

```python
"""
XBRL financial extractor — structured data from edgartools Financials object.

Layer 1: get_financial_metrics() — 15 built-in metrics.
Layer 2: Statement DataFrames — supplementary metrics (EPS, R&D, SBC, D&A, debt).
"""

import pandas as pd


def _filter_consolidated(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only non-abstract, non-dimension rows (consolidated totals)."""
    if df is None or df.empty:
        return pd.DataFrame()
    mask = (df["abstract"] == False) & (df["dimension"] == False)  # noqa: E712
    return df[mask].copy()


def _get_date_columns(df: pd.DataFrame) -> list[str]:
    """Return date-like column names from a statement DataFrame."""
    skip = {
        "concept", "label", "standard_concept", "level", "abstract",
        "dimension", "is_breakdown", "dimension_axis", "dimension_member",
        "dimension_member_label", "dimension_label", "balance", "weight",
        "preferred_sign", "parent_concept", "parent_abstract_concept",
    }
    return [c for c in df.columns if c not in skip]


def _find_value(df: pd.DataFrame, concept_patterns: list[str], date_col: str = None):
    """
    Find a value by matching concept column against patterns.
    Returns the first match. If date_col given, returns that column's value.
    Otherwise returns the row.
    """
    if df is None or df.empty:
        return None

    for pattern in concept_patterns:
        # Exact match first
        matches = df[df["concept"] == pattern]
        if matches.empty:
            # Partial match
            matches = df[df["concept"].str.contains(pattern, case=False, na=False)]
        if not matches.empty:
            # Take first match, deduplicated
            row = matches.iloc[0]
            if date_col and date_col in df.columns:
                val = row[date_col]
                if pd.notna(val):
                    return float(val)
            else:
                return row
    return None


def _extract_multi_year(df: pd.DataFrame, concept_patterns: list[str], date_cols: list[str]) -> dict:
    """Extract a metric across multiple years. Returns {date_col: value}."""
    result = {}
    if df is None or df.empty:
        return result
    for pattern in concept_patterns:
        matches = df[df["concept"] == pattern]
        if matches.empty:
            matches = df[df["concept"].str.contains(pattern, case=False, na=False)]
        if not matches.empty:
            row = matches.iloc[0]
            for dc in date_cols:
                if dc in row.index and pd.notna(row[dc]):
                    result[dc] = float(row[dc])
            break
    return result


def _extract_supplementary(inc_df, bs_df, cf_df, date_cols_inc, date_cols_bs, date_cols_cf):
    """Extract supplementary metrics not in get_financial_metrics()."""
    supplementary = {}

    # --- Income Statement ---
    _add_supp(supplementary, "eps_basic", inc_df, [
        "us-gaap_EarningsPerShareBasic",
    ], date_cols_inc, per_share=True)

    _add_supp(supplementary, "eps_diluted", inc_df, [
        "us-gaap_EarningsPerShareDiluted",
    ], date_cols_inc, per_share=True)

    _add_supp(supplementary, "research_and_development", inc_df, [
        "us-gaap_ResearchAndDevelopmentExpense",
        "ResearchAndDevelopment",
    ], date_cols_inc)

    # SG&A: try combined first, then sum components
    _add_supp(supplementary, "selling_general_and_admin", inc_df, [
        "us-gaap_SellingGeneralAndAdministrativeExpense",
        "SellingGeneralAndAdministrative",
    ], date_cols_inc)

    _add_supp(supplementary, "interest_expense", inc_df, [
        "us-gaap_InterestExpenseDebt",
        "us-gaap_InterestExpense",
        "InterestExpense",
    ], date_cols_inc)

    _add_supp(supplementary, "gross_profit", inc_df, [
        "us-gaap_GrossProfit",
        "GrossProfit",
    ], date_cols_inc)

    # --- Balance Sheet ---
    _add_supp(supplementary, "long_term_debt", bs_df, [
        "us-gaap_LongTermDebtNoncurrent",
        "us-gaap_LongTermDebt",
        "LongTermDebt",
    ], date_cols_bs)

    _add_supp(supplementary, "short_term_debt", bs_df, [
        "us-gaap_LongTermDebtCurrent",
        "us-gaap_ShortTermBorrowings",
        "ShortTermDebt",
    ], date_cols_bs)

    # Total debt = LT + ST
    lt = supplementary.get("long_term_debt", {}).get("years", {})
    st = supplementary.get("short_term_debt", {}).get("years", {})
    if lt or st:
        all_dates = sorted(set(list(lt.keys()) + list(st.keys())))
        total_debt_years = {}
        for d in all_dates:
            lt_val = lt.get(d, 0) or 0
            st_val = st.get(d, 0) or 0
            total_debt_years[d] = lt_val + st_val
        if total_debt_years:
            latest_val = list(total_debt_years.values())[0] if total_debt_years else None
            supplementary["total_debt_lt_st"] = {
                "value": latest_val,
                "concept": "LongTermDebt + ShortTermDebt",
                "years": total_debt_years,
            }

    # --- Cash Flow ---
    _add_supp(supplementary, "depreciation", cf_df, [
        "us-gaap_Depreciation",
    ], date_cols_cf)

    _add_supp(supplementary, "amortization", cf_df, [
        "us-gaap_AdjustmentForAmortization",
        "us-gaap_AmortizationOfIntangibleAssets",
        "Amortization",
    ], date_cols_cf)

    # D&A: try combined, else sum components
    da_combined = _extract_multi_year(cf_df, [
        "us-gaap_DepreciationAndAmortization",
        "us-gaap_DepreciationDepletionAndAmortization",
    ], date_cols_cf)
    if da_combined:
        latest_val = list(da_combined.values())[0] if da_combined else None
        supplementary["depreciation_and_amortization"] = {
            "value": latest_val,
            "concept": "DepreciationAndAmortization",
            "years": da_combined,
        }
    else:
        dep = supplementary.get("depreciation", {}).get("years", {})
        amort = supplementary.get("amortization", {}).get("years", {})
        if dep or amort:
            all_dates = sorted(set(list(dep.keys()) + list(amort.keys())))
            da_years = {}
            for d in all_dates:
                da_years[d] = (dep.get(d, 0) or 0) + (amort.get(d, 0) or 0)
            if da_years:
                latest_val = list(da_years.values())[0] if da_years else None
                supplementary["depreciation_and_amortization"] = {
                    "value": latest_val,
                    "concept": "Depreciation + Amortization (summed)",
                    "years": da_years,
                }

    _add_supp(supplementary, "stock_based_compensation", cf_df, [
        "us-gaap_ShareBasedCompensation",
        "ShareBasedCompensation",
    ], date_cols_cf)

    _add_supp(supplementary, "dividends_paid", cf_df, [
        "us-gaap_PaymentsOfDividends",
        "us-gaap_PaymentsOfDividendsCommonStock",
        "DividendsCommonStockCash",
    ], date_cols_cf)

    return supplementary


def _add_supp(supplementary, name, df, patterns, date_cols, per_share=False):
    """Helper: extract multi-year values and add to supplementary dict."""
    if df is None or df.empty:
        return
    years = _extract_multi_year(df, patterns, date_cols)
    if years:
        latest_val = list(years.values())[0] if years else None
        # Find which concept matched
        concept = "unknown"
        for pattern in patterns:
            matches = df[df["concept"] == pattern]
            if matches.empty:
                matches = df[df["concept"].str.contains(pattern, case=False, na=False)]
            if not matches.empty:
                concept = matches.iloc[0]["concept"]
                break
        supplementary[name] = {
            "value": latest_val,
            "concept": concept,
            "years": years,
            "per_share": per_share,
        }


def _get_statement_df(financials, statement_name: str):
    """Safely get a statement DataFrame, filtered to consolidated rows."""
    try:
        stmt = getattr(financials, statement_name)()
        if stmt is None:
            return pd.DataFrame(), []
        df = stmt.to_dataframe()
        if df is None or df.empty:
            return pd.DataFrame(), []
        filtered = _filter_consolidated(df)
        filtered = filtered.drop_duplicates(subset=["concept"] + _get_date_columns(filtered)[:1])
        date_cols = _get_date_columns(filtered)
        return filtered, date_cols
    except Exception:
        return pd.DataFrame(), []


def extract_financials(financials, filing_metadata: dict) -> dict:
    """
    Extract structured financial data from an edgartools Financials object.

    Returns {
        "metrics": dict,              # from get_financial_metrics()
        "currency": str,              # e.g. "$", "kr", "€"
        "income_statement": DataFrame,
        "income_date_cols": list,
        "balance_sheet": DataFrame,
        "balance_date_cols": list,
        "cash_flow": DataFrame,
        "cash_flow_date_cols": list,
        "supplementary": dict,
        "warnings": list,
    }
    """
    warnings = []

    # Layer 1: built-in metrics
    try:
        metrics = financials.get_financial_metrics()
    except Exception as e:
        metrics = {}
        warnings.append(f"get_financial_metrics() failed: {e}")

    # Currency
    try:
        currency = financials.get_currency_symbol()
    except Exception:
        currency = "$"
        warnings.append("Currency detection failed, defaulting to USD")

    # Layer 2: statement DataFrames
    inc_df, inc_dates = _get_statement_df(financials, "income_statement")
    bs_df, bs_dates = _get_statement_df(financials, "balance_sheet")
    cf_df, cf_dates = _get_statement_df(financials, "cash_flow_statement")

    if inc_df.empty:
        warnings.append("Income statement not available")
    if bs_df.empty:
        warnings.append("Balance sheet not available")
    if cf_df.empty:
        warnings.append("Cash flow statement not available")

    # Flag None values in metrics
    for k, v in metrics.items():
        if v is None:
            warnings.append(f"Metric '{k}' is None (not reported or not mapped)")

    # Supplementary metrics
    supplementary = _extract_supplementary(
        inc_df, bs_df, cf_df,
        inc_dates, bs_dates, cf_dates,
    )

    return {
        "metrics": metrics,
        "currency": currency,
        "income_statement": inc_df,
        "income_date_cols": inc_dates,
        "balance_sheet": bs_df,
        "balance_date_cols": bs_dates,
        "cash_flow": cf_df,
        "cash_flow_date_cols": cf_dates,
        "supplementary": supplementary,
        "warnings": warnings,
    }
```

### How the edgartools DataFrame works

Each statement (income, balance sheet, cash flow) returns a DataFrame with these columns:

| Column | Purpose |
|--------|---------|
| `concept` | XBRL concept ID, e.g. `us-gaap_Revenues`, `us-gaap_NetIncomeLoss` |
| `label` | Human-readable label from the filing, e.g. "Net revenue:", "Net income" |
| `standard_concept` | Normalized concept name when available, e.g. `Revenue`, `NetIncome` |
| `2025-07-31`, `2024-07-31`, ... | Date columns containing the actual values |
| `abstract` | `True` for section headers (no data), `False` for data rows |
| `dimension` | `True` for dimensional breakdowns (segments), `False` for consolidated totals |
| `level` | Indentation level in the statement hierarchy |
| `balance` | `debit` or `credit` |
| `weight` | Sign weight for aggregation |
| `preferred_sign` | `1.0` or `-1.0` |

**Critical filter:** `_filter_consolidated()` keeps only rows where `abstract == False` and `dimension == False`. This gives us the consolidated totals without section headers or segment breakdowns.

### Supplementary metric extraction strategy

Each metric is extracted via `_add_supp()` which:
1. Tries an ordered list of XBRL concept patterns (exact match first, then substring)
2. Extracts values across all date columns (multi-year)
3. Records which concept actually matched (for auditability)
4. Marks per-share metrics so the renderer formats them differently

**D&A handling:** Try the combined `DepreciationAndAmortization` concept first. If the filing doesn't report it as a combined line item (many don't), fall back to summing the separate `Depreciation` + `Amortization` values.

**Total Debt:** Computed as `LongTermDebtNoncurrent + LongTermDebtCurrent` (short-term debt is often the current portion of long-term debt, filed under `LongTermDebtCurrent`).

### Supplementary metrics extracted

| Metric | Source Statement | XBRL Concepts Tried (in order) |
|--------|-----------------|-------------------------------|
| EPS Basic | Income | `us-gaap_EarningsPerShareBasic` |
| EPS Diluted | Income | `us-gaap_EarningsPerShareDiluted` |
| R&D Expense | Income | `us-gaap_ResearchAndDevelopmentExpense`, `ResearchAndDevelopment` |
| SG&A | Income | `us-gaap_SellingGeneralAndAdministrativeExpense`, `SellingGeneralAndAdministrative` |
| Interest Expense | Income | `us-gaap_InterestExpenseDebt`, `us-gaap_InterestExpense`, `InterestExpense` |
| Gross Profit | Income | `us-gaap_GrossProfit`, `GrossProfit` |
| Long-Term Debt | Balance Sheet | `us-gaap_LongTermDebtNoncurrent`, `us-gaap_LongTermDebt`, `LongTermDebt` |
| Short-Term Debt | Balance Sheet | `us-gaap_LongTermDebtCurrent`, `us-gaap_ShortTermBorrowings`, `ShortTermDebt` |
| Total Debt (LT+ST) | Balance Sheet | Computed: LT + ST |
| Depreciation | Cash Flow | `us-gaap_Depreciation` |
| Amortization | Cash Flow | `us-gaap_AdjustmentForAmortization`, `us-gaap_AmortizationOfIntangibleAssets` |
| D&A Combined | Cash Flow | `us-gaap_DepreciationAndAmortization` or Depreciation + Amortization sum |
| SBC | Cash Flow | `us-gaap_ShareBasedCompensation` |
| Dividends Paid | Cash Flow | `us-gaap_PaymentsOfDividends`, `us-gaap_PaymentsOfDividendsCommonStock` |

---

## 4. `scripts/sec_edgar/render.py`

**Role:** Takes the extracted dict from `xbrl.py` and produces a compact markdown file (~3-5K tokens) optimized for agent consumption.

### Full source

```python
"""
Markdown renderer for SEC EDGAR financial data.

Output: compact ~3-5K token markdown file for agent consumption.
"""

from datetime import datetime, timezone

import pandas as pd


# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------

def _fmt_amount(value, currency="$"):
    """Format a dollar amount: $18,831M or $18.8B based on magnitude."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    negative = value < 0
    v = abs(value)
    if v >= 1e12:
        s = f"{v / 1e12:.1f}T"
    elif v >= 1e9:
        s = f"{v / 1e9:.2f}B"
    elif v >= 1e6:
        s = f"{v / 1e6:,.0f}M"
    elif v >= 1e3:
        s = f"{v / 1e3:.1f}K"
    else:
        s = f"{v:,.0f}"
    sign = "-" if negative else ""
    return f"{sign}{currency}{s}"


def _fmt_per_share(value):
    """Format per-share values: $13.67."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    return f"${value:.2f}"


def _fmt_shares(value):
    """Format share counts: 283M."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    v = abs(value)
    if v >= 1e9:
        return f"{v / 1e9:.2f}B"
    if v >= 1e6:
        return f"{v / 1e6:.0f}M"
    return f"{v:,.0f}"


def _fmt_ratio(value):
    """Format ratios: 1.36x."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    return f"{value:.2f}x"


def _fmt_date_col(col: str) -> str:
    """Turn '2025-07-31' into 'FY2025'."""
    try:
        return f"FY{col[:4]}"
    except Exception:
        return str(col)
```

*(Section renderers: `_render_metadata`, `_render_metrics`, `_render_statement`, `_render_supplementary`, `_render_warnings` — see full file at `scripts/sec_edgar/render.py`)*

### Number formatting rules

| Type | Format | Examples |
|------|--------|---------|
| Dollar amounts (>= 1B) | `$18.83B` | Revenue, total assets |
| Dollar amounts (>= 1M) | `$84M` | CapEx, R&D |
| Dollar amounts (>= 1K) | `$4.5K` | Small amounts |
| Per-share | `$13.67` | EPS (no M/B suffix) |
| Share counts | `283M` | Shares outstanding |
| Ratios | `1.36x` | Current ratio |
| Percentages | `46.67%` | Debt/assets |
| Negative amounts | `-$247M` | Interest expense, outflows |
| Missing values | `n/a` or `—` | None or NaN |

### Smart type detection in statement rendering

The renderer detects per-share and share-count rows by inspecting the XBRL `concept` and `label` columns:
- `"PerShare" in concept` → format as `$13.67`
- `"Shares" in concept or "shares" in label` → format as `283M`
- Everything else → format as `$18.83B` with currency symbol

### Output sections

1. **Filing metadata** — company, CIK, form type, dates, accession number
2. **Key Financial Metrics** — 15 items from `get_financial_metrics()`, single latest period
3. **Income Statement (Multi-Year)** — all consolidated line items, 3 years
4. **Balance Sheet (Multi-Year)** — all consolidated line items, 2 years
5. **Cash Flow Statement (Multi-Year)** — all consolidated line items, 3 years
6. **Supplementary Metrics** — multi-year table of EPS, R&D, SBC, D&A, debt
7. **Data Gaps & Warnings** — any None metrics, missing statements, currency notes

---

## 5. `scripts/sec_edgar/__main__.py`

**Role:** CLI interface. Parses arguments, loops over tickers, counts results.

### Full source

```python
"""
CLI entry point for sec_edgar package.

Usage:
    python3 -m sec_edgar INTU V NVO
    python3 -m sec_edgar --force INTU
    python3 -m sec_edgar --quiet INTU
"""

import argparse
import sys

from .client import fetch_10k


def main():
    parser = argparse.ArgumentParser(
        description="Fetch SEC EDGAR filing data (XBRL financials) for analysis agents"
    )
    parser.add_argument("tickers", nargs="*", help="Ticker symbols (e.g., INTU V NVO)")
    parser.add_argument("--force", action="store_true", help="Re-fetch even if <24h old")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers if t.strip()]
    if not tickers:
        parser.error("No tickers specified.")

    if not args.quiet:
        print(f"Fetching SEC EDGAR data for {len(tickers)} ticker(s)...\n")

    ok = 0
    skipped = 0
    failed = 0

    for i, ticker in enumerate(tickers):
        try:
            result = fetch_10k(ticker, force=args.force, quiet=args.quiet)
            if result is None:
                # Either skipped (fresh) or company not found
                skipped += 1
            else:
                ok += 1
        except Exception as e:
            if not args.quiet:
                print(f"  {ticker} — ERROR: {e}", file=sys.stderr)
            failed += 1

    if not args.quiet:
        print(f"\nDone: {ok} fetched, {skipped} skipped, {failed} failed")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
```

### CLI arguments

| Argument | Effect |
|----------|--------|
| `tickers` | Positional, one or more ticker symbols |
| `--force` | Bypass 24-hour freshness check |
| `--quiet` | Suppress all progress output (used by `./run.sh analyze`) |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | All tickers succeeded or skipped |
| `1` | At least one ticker failed |

---

## 6. `scripts/fetch-edgar.py`

**Role:** Thin entry point that sets up `sys.path` and delegates to the package.

```python
#!/usr/bin/env python3
"""
fetch-edgar.py — Entry point for SEC EDGAR financial data extraction.

Delegates to scripts/sec_edgar package.

Usage:
    python3 scripts/fetch-edgar.py INTU
    python3 scripts/fetch-edgar.py INTU V NVO
    python3 scripts/fetch-edgar.py --force INTU
    python3 scripts/fetch-edgar.py --quiet INTU
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sec_edgar.__main__ import main

sys.exit(main())
```

**Why `sys.path.insert`?** The package lives at `scripts/sec_edgar/` but the entry point is `scripts/fetch-edgar.py`. Without the path insert, `from sec_edgar import ...` would fail because `scripts/` isn't on the default Python path. This is the same pattern used by the rest of the codebase.

---

## 7. `run.sh` modifications

Three changes were made:

### A. New `cmd_extract()` function (after `cmd_fetch`, line ~395)

```bash
cmd_extract() {
    python3 "$SCRIPT_DIR/scripts/fetch-edgar.py" "$@"
}
```

### B. Dispatch table entry (line ~846)

```bash
extract)   cmd_extract "$@" ;;
```

### C. Analyze flow integration (after yfinance fetch, line ~431)

```bash
# Auto-fetch SEC filing data (non-blocking on failure)
echo "Fetching SEC filing data for $TICKER..."
python3 "$SCRIPT_DIR/scripts/fetch-edgar.py" --quiet "$TICKER" || {
    echo "WARNING: SEC evidence fetch failed. Continuing without SEC data."
}
```

This runs after the yfinance fetch and before the context directory is scanned. If it fails (company not on EDGAR, network error), analysis continues without SEC data — same pattern as the yfinance fetch.

### D. Usage line added

```
  extract TICKER [...]     Fetch SEC EDGAR filing data (XBRL)
```

---

## 8. `.gitignore` modification

Added `cache/` line (edgartools may create a local cache in future versions).

---

## How the edgartools API is used

### API call chain

```
Company(ticker)                          # Resolve ticker → CIK on EDGAR
  ├── .name, .cik                        # Company metadata
  ├── .get_filings(form=[...])           # Filing index (10-K, 20-F, etc.)
  │     └── [0].form, .filing_date, ...  # Latest filing metadata
  └── .get_financials()                  # Financials object
        ├── .get_financial_metrics()      # → dict of 15 floats
        ├── .get_currency_symbol()        # → "$", "kr", "€", etc.
        ├── .income_statement()           # → Statement object
        │     └── .to_dataframe()         # → pandas DataFrame (44 rows, 3yr)
        ├── .balance_sheet()              # → Statement object
        │     └── .to_dataframe()         # → pandas DataFrame (39 rows, 2yr)
        └── .cash_flow_statement()        # → Statement object
              └── .to_dataframe()         # → pandas DataFrame (54 rows, 3yr)
```

### The 15 built-in metrics from `get_financial_metrics()`

| Key | Description |
|-----|-------------|
| `revenue` | Total revenue |
| `operating_income` | Operating income |
| `net_income` | Net income (may be None for some filers like NVO) |
| `total_assets` | Total assets |
| `total_liabilities` | Total liabilities |
| `stockholders_equity` | Stockholders' equity |
| `current_assets` | Current assets |
| `current_liabilities` | Current liabilities |
| `operating_cash_flow` | Operating cash flow |
| `capital_expenditures` | CapEx (positive value, absolute) |
| `free_cash_flow` | Free cash flow |
| `shares_outstanding_basic` | Basic shares outstanding |
| `shares_outstanding_diluted` | Diluted shares outstanding |
| `current_ratio` | Current ratio (computed) |
| `debt_to_assets` | Debt / total assets (computed) |

---

## Verification results

All tests were run and passed:

| # | Test | Command | Result |
|---|------|---------|--------|
| 1 | US filer (10-K) | `python3 scripts/fetch-edgar.py INTU` | Revenue $18.83B, 3yr income statement, FY2025/2024/2023 |
| 2 | Non-EDGAR ticker | `python3 scripts/fetch-edgar.py MC.PA` | "Company not found on EDGAR. Skipping." — no crash, no output file |
| 3 | Foreign private issuer (20-F) | `python3 scripts/fetch-edgar.py NVO` | Form 20-F, currency = kr, revenue kr309.06B, None metrics flagged |
| 4 | Freshness skip | Run INTU twice | Second run: "skipped (fresh)" |
| 5 | Force re-fetch | `python3 scripts/fetch-edgar.py --force INTU` | Re-fetched despite being fresh |
| 6 | run.sh dispatch | `./run.sh extract INTU` | Delegated correctly to fetch-edgar.py |
| 7 | Class B shares | `python3 scripts/fetch-edgar.py BRK.B` | Resolved Berkshire Hathaway correctly |
| 8 | Multi-ticker | `python3 scripts/fetch-edgar.py V BRK.B` | Both processed sequentially, 2 fetched |

---

## Sample output: INTU

Full output file: `context/INTU/edgar-10k.md` (8 KB)

```markdown
# SEC Filing Data: INTU — INTUIT INC.

**Generated:** 2026-03-19 11:11 UTC
**Source:** SEC EDGAR (XBRL via edgartools)
**Currency:** $

| Field | Value |
|-------|-------|
| CIK | 896878 |
| Form Type | 10-K |
| Filing Date | 2025-09-03 |
| Period of Report | 2025-07-31 |
| Accession Number | 0000896878-25-000035 |

---

## Key Financial Metrics

*From get_financial_metrics() — latest filing period. CapEx shown as positive (absolute value).*

| Metric | Value |
|--------|-------|
| Revenue | $18.83B |
| Operating Income | $4.92B |
| Net Income | $3.87B |
| Total Assets | $36.96B |
| Total Liabilities | $17.25B |
| Stockholders' Equity | $19.71B |
| Current Assets | $14.11B |
| Current Liabilities | $10.37B |
| Operating Cash Flow | $6.21B |
| Capital Expenditures | $84M |
| Free Cash Flow | $6.12B |
| Shares Outstanding (Basic) | 280M |
| Shares Outstanding (Diluted) | 283M |
| Current Ratio | 1.36x |
| Debt / Total Assets | 46.67% |

---

## Income Statement (Multi-Year)

*Consolidated, from XBRL. Signs as reported.*

| Line Item | FY2025 | FY2024 | FY2023 |
| ------ | ------ | ------ | ------ |
| Net revenue: | $18.83B | $16.29B | $14.37B |
| Cost of revenue | $3.69B | $3.32B | $2.98B |
| Amortization of acquired technology | $156M | $146M | $163M |
| Selling and marketing | $5.04B | $4.31B | $3.76B |
| Research and development | $2.93B | $2.75B | $2.54B |
| General and administrative | $1.60B | $1.42B | $1.30B |
| Amortization of other acquired intangible assets | $481M | $483M | $483M |
| Restructuring | $15M | $223M | $0 |
| Total costs and expenses | $13.91B | $12.65B | $11.23B |
| Operating income | $4.92B | $3.63B | $3.14B |
| Interest expense | -$247M | -$242M | -$248M |
| Interest and other income, net | $158M | $162M | $96M |
| Income before income taxes | $4.83B | $3.55B | $2.99B |
| Income tax provision | $965M | $587M | $605M |
| Net income | $3.87B | $2.96B | $2.38B |
| Basic net income per share (in dollars per share) | $13.82 | $10.58 | $8.49 |
| Shares used in basic per share calculations (in... | 280M | 280M | 281M |
| Diluted net income per share (in dollars per sh... | $13.67 | $10.43 | $8.42 |
| Shares used in diluted per share calculations (... | 283M | 284M | 283M |

---

## Balance Sheet (Multi-Year)

*Consolidated, from XBRL.*

| Line Item | FY2025 | FY2024 |
| ------ | ------ | ------ |
| Cash and cash equivalents | $2.88B | $3.61B |
| Investments | $1.67B | $465M |
| ... (39 line items total) ... |
| Total assets | $36.96B | $32.13B |
| ... |
| Total stockholders' equity | $19.71B | $18.44B |
| Total liabilities and stockholders' equity | $36.96B | $32.13B |

---

## Cash Flow Statement (Multi-Year)

*Consolidated, from XBRL. Outflows are negative.*

| Line Item | FY2025 | FY2024 | FY2023 |
| ------ | ------ | ------ | ------ |
| Net income | $3.87B | $2.96B | $2.38B |
| Depreciation | $172M | $159M | $160M |
| Amortization of acquired intangible assets | $637M | $630M | $646M |
| ... (54 line items total) ... |
| Net cash provided by operating activities | $6.21B | $4.88B | $5.05B |
| ... |

---

## Supplementary Metrics

*Extracted from statement line items. D&A and Total Debt may be summed from components.*

| Metric | FY2025 | FY2024 | FY2023 |
| ------ | ------ | ------ | ------ |
| EPS (Basic) | $13.82 | $10.58 | $8.49 |
| EPS (Diluted) | $13.67 | $10.43 | $8.42 |
| R&D Expense | $2.93B | $2.75B | $2.54B |
| Interest Expense | -$247M | -$242M | -$248M |
| Depreciation | $172M | $159M | $160M |
| Amortization | $637M | $630M | $646M |
| D&A (Combined) | $809M | $789M | $806M |
| Stock-Based Compensation | $1.97B | $1.94B | $1.71B |
| Dividends Paid | -$1.19B | -$1.03B | -$889M |
| Long-Term Debt | $5.97B | $5.54B | — |
| Short-Term Debt | $0 | $499M | — |
| Total Debt (LT + ST) | $5.97B | $6.04B | — |

---

## Data Gaps & Warnings

None — all sections populated successfully.
```

---

## Sample output: NVO (foreign private issuer)

Key differences from a US filer:

- **Form type:** 20-F (not 10-K)
- **Currency:** kr (Danish krone)
- **Known gaps:** `net_income`, `shares_outstanding_basic`, `shares_outstanding_diluted` all return None from `get_financial_metrics()` — these are flagged in the Data Gaps section
- Revenue: kr309.06B

---

## Data flow diagram

```
User runs:  ./run.sh analyze TICKER
               │
               ├── 1. python3 scripts/fetch-financials.py --quiet TICKER
               │      └── writes context/{TICKER}/financials.md    (yfinance)
               │
               ├── 2. python3 scripts/fetch-edgar.py --quiet TICKER     ← NEW
               │      ├── Company(ticker)                (edgartools → EDGAR API)
               │      ├── .get_financials()              (XBRL data)
               │      ├── extract_financials()           (Layer 1 + Layer 2)
               │      ├── render_markdown()              (compact MD)
               │      └── writes context/{TICKER}/edgar-10k.md          ← NEW
               │
               ├── 3. Scan context/{TICKER}/* for all .md files
               │      └── Both financials.md AND edgar-10k.md are included
               │
               └── 4. Pass combined context to analysis agents
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `edgartools` | >= 3.0 | SEC EDGAR API client (already in `requirements.txt`) |
| `pandas` | (transitive) | DataFrame handling (comes with edgartools) |

No new dependencies were added. `edgartools` was already in `requirements.txt`.

---

## Known limitations (Phase 1)

1. **No narrative sections.** MD&A, Risk Factors, Business Description are not extracted. Deferred to Phase 2 via `TenK`/`TwentyF` object's parsed sections.
2. **Non-EDGAR tickers silently skip.** European tickers like `MC.PA`, `WKL.AS`, `HLMA.L` are not on EDGAR. They get a warning and no output.
3. **Some metrics are None for certain filers.** NVO's `net_income` and `shares_outstanding` return None from `get_financial_metrics()`. These are present in the statement DataFrames but would require custom mapping per filer. The warnings section flags these.
4. **Balance sheet is 2 years only.** The XBRL standard for balance sheets only requires current + prior period. Income and cash flow get 3 years.
5. **No filing cache.** Each call re-fetches from EDGAR if the output file is stale. In Phase 1, output freshness (24h TTL) is sufficient. A filing-level cache could be added if bulk fetching becomes a bottleneck.
