"""
XBRL financial extractor — structured data from edgartools Financials object.

Layer 1: get_financial_metrics() — 15 built-in metrics.
Layer 2: Statement DataFrames — supplementary metrics (EPS, R&D, SBC, D&A, debt).
"""

import sys

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
        matches = df[df["concept"] == pattern]
        if not matches.empty:
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
        date_cols = sorted(_get_date_columns(filtered), reverse=True)
        return filtered, date_cols
    except Exception as e:
        print(f"  Warning: {statement_name} extraction failed: {e}", file=sys.stderr)
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
