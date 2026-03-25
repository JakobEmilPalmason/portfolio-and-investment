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


def _fmt_per_share(value, currency="$"):
    """Format per-share values: $13.67 (or kr13.67 for non-USD)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    return f"{currency}{value:.2f}"


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


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_metadata(ticker, filing_metadata, currency):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# SEC Filing Data: {ticker} — {filing_metadata.get('company_name', ticker)}",
        "",
        f"**Generated:** {now}",
        f"**Source:** SEC EDGAR (XBRL via edgartools)",
        f"**Currency:** {currency}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| CIK | {filing_metadata.get('cik', 'n/a')} |",
        f"| Form Type | {filing_metadata.get('form_type', 'n/a')} |",
        f"| Filing Date | {filing_metadata.get('filing_date', 'n/a')} |",
        f"| Period of Report | {filing_metadata.get('period_of_report', 'n/a')} |",
        f"| Accession Number | {filing_metadata.get('accession_no', 'n/a')} |",
    ]
    return "\n".join(lines)


def _render_metrics(metrics, currency):
    if not metrics:
        return "## Key Financial Metrics\n\nNo metrics available."

    fmt = {
        "revenue": lambda v: _fmt_amount(v, currency),
        "operating_income": lambda v: _fmt_amount(v, currency),
        "net_income": lambda v: _fmt_amount(v, currency),
        "total_assets": lambda v: _fmt_amount(v, currency),
        "total_liabilities": lambda v: _fmt_amount(v, currency),
        "stockholders_equity": lambda v: _fmt_amount(v, currency),
        "current_assets": lambda v: _fmt_amount(v, currency),
        "current_liabilities": lambda v: _fmt_amount(v, currency),
        "operating_cash_flow": lambda v: _fmt_amount(v, currency),
        "capital_expenditures": lambda v: _fmt_amount(v, currency),
        "free_cash_flow": lambda v: _fmt_amount(v, currency),
        "shares_outstanding_basic": _fmt_shares,
        "shares_outstanding_diluted": _fmt_shares,
        "current_ratio": _fmt_ratio,
        "debt_to_assets": lambda v: f"{v:.2%}" if v is not None else "n/a",
    }

    labels = {
        "revenue": "Revenue",
        "operating_income": "Operating Income",
        "net_income": "Net Income",
        "total_assets": "Total Assets",
        "total_liabilities": "Total Liabilities",
        "stockholders_equity": "Stockholders' Equity",
        "current_assets": "Current Assets",
        "current_liabilities": "Current Liabilities",
        "operating_cash_flow": "Operating Cash Flow",
        "capital_expenditures": "Capital Expenditures",
        "free_cash_flow": "Free Cash Flow",
        "shares_outstanding_basic": "Shares Outstanding (Basic)",
        "shares_outstanding_diluted": "Shares Outstanding (Diluted)",
        "current_ratio": "Current Ratio",
        "debt_to_assets": "Debt / Total Assets",
    }

    lines = [
        "## Key Financial Metrics",
        "",
        "*From get_financial_metrics() — latest filing period. CapEx shown as positive (absolute value).*",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for key in labels:
        val = metrics.get(key)
        formatter = fmt.get(key, lambda v: str(v) if v is not None else "n/a")
        lines.append(f"| {labels[key]} | {formatter(val)} |")

    return "\n".join(lines)


def _render_statement(title, df, date_cols, currency, note=""):
    """Render a financial statement DataFrame as a markdown table."""
    if df is None or df.empty or not date_cols:
        return f"## {title}\n\nNo data available."

    headers = ["Line Item"] + [_fmt_date_col(c) for c in date_cols]
    lines = [
        f"## {title}",
        "",
    ]
    if note:
        lines.append(f"*{note}*")
        lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["------"] * len(headers)) + " |")

    for _, row in df.iterrows():
        label = str(row.get("label", row.get("concept", "?")))
        # Truncate long labels
        if len(label) > 50:
            label = label[:47] + "..."
        vals = []
        is_per_share = "PerShare" in str(row.get("concept", ""))
        is_shares = "Shares" in str(row.get("concept", "")) or "shares" in str(row.get("label", ""))
        for dc in date_cols:
            v = row.get(dc)
            if pd.isna(v) if isinstance(v, float) else v is None:
                vals.append("—")
            elif is_per_share:
                vals.append(_fmt_per_share(v, currency))
            elif is_shares:
                vals.append(_fmt_shares(v))
            else:
                vals.append(_fmt_amount(v, currency))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def _render_supplementary(supplementary, currency):
    if not supplementary:
        return "## Supplementary Metrics\n\nNo supplementary data extracted."

    lines = [
        "## Supplementary Metrics",
        "",
        "*Extracted from statement line items. D&A and Total Debt may be summed from components.*",
        "",
    ]

    # Group: first show latest values, then multi-year if available
    labels = {
        "eps_basic": "EPS (Basic)",
        "eps_diluted": "EPS (Diluted)",
        "gross_profit": "Gross Profit",
        "research_and_development": "R&D Expense",
        "selling_general_and_admin": "SG&A Expense",
        "interest_expense": "Interest Expense",
        "depreciation": "Depreciation",
        "amortization": "Amortization",
        "depreciation_and_amortization": "D&A (Combined)",
        "stock_based_compensation": "Stock-Based Compensation",
        "dividends_paid": "Dividends Paid",
        "long_term_debt": "Long-Term Debt",
        "short_term_debt": "Short-Term Debt",
        "total_debt_lt_st": "Total Debt (LT + ST)",
    }

    # Find all date columns across supplementary items
    all_dates = set()
    for data in supplementary.values():
        all_dates.update(data.get("years", {}).keys())
    date_cols = sorted(all_dates, reverse=True)[:4]  # max 4 years

    if date_cols:
        headers = ["Metric"] + [_fmt_date_col(c) for c in date_cols]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["------"] * len(headers)) + " |")

        for key, label in labels.items():
            if key not in supplementary:
                continue
            data = supplementary[key]
            is_ps = data.get("per_share", False)
            years = data.get("years", {})
            vals = []
            for dc in date_cols:
                v = years.get(dc)
                if v is None:
                    vals.append("—")
                elif is_ps:
                    vals.append(_fmt_per_share(v, currency))
                else:
                    vals.append(_fmt_amount(v, currency))
            lines.append(f"| {label} | " + " | ".join(vals) + " |")
    else:
        lines.append("| Metric | Latest Value |")
        lines.append("| ------ | ------------ |")
        for key, label in labels.items():
            if key not in supplementary:
                continue
            data = supplementary[key]
            v = data.get("value")
            if data.get("per_share"):
                lines.append(f"| {label} | {_fmt_per_share(v, currency)} |")
            else:
                lines.append(f"| {label} | {_fmt_amount(v, currency)} |")

    return "\n".join(lines)


def _render_warnings(warnings):
    if not warnings:
        return "## Data Gaps & Warnings\n\nNone — all sections populated successfully."
    lines = ["## Data Gaps & Warnings", ""]
    for w in warnings:
        lines.append(f"- {w}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render_markdown(ticker: str, extracted: dict, filing_metadata: dict) -> str:
    """Render extracted financial data as a compact markdown file."""
    currency = extracted["currency"]
    metrics = extracted["metrics"]

    sections = [
        _render_metadata(ticker, filing_metadata, currency),
        _render_metrics(metrics, currency),
        _render_statement(
            "Income Statement (Multi-Year)",
            extracted["income_statement"],
            extracted["income_date_cols"],
            currency,
            note="Consolidated, from XBRL. Signs as reported.",
        ),
        _render_statement(
            "Balance Sheet (Multi-Year)",
            extracted["balance_sheet"],
            extracted["balance_date_cols"],
            currency,
            note="Consolidated, from XBRL.",
        ),
        _render_statement(
            "Cash Flow Statement (Multi-Year)",
            extracted["cash_flow"],
            extracted["cash_flow_date_cols"],
            currency,
            note="Consolidated, from XBRL. Outflows are negative.",
        ),
        _render_supplementary(extracted["supplementary"], currency),
        _render_warnings(extracted["warnings"]),
    ]
    return "\n\n---\n\n".join(sections) + "\n"
