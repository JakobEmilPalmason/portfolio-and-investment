#!/usr/bin/env python3
"""
fetch-financials.py — Fetch financial data from Yahoo Finance for analysis agents.

Writes context/{TICKER}/financials.md with verified financial data that the
8-umbrella analysis agents consume alongside web search results.

Usage:
    python3 scripts/fetch-financials.py AAPL
    python3 scripts/fetch-financials.py ADBE MSFT V MA
    python3 scripts/fetch-financials.py --all-reports
    python3 scripts/fetch-financials.py --all-queue deep_research
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = REPO_ROOT / "context"
RUNS_DIR = REPO_ROOT / "runs"
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"
FRESHNESS_HOURS = 24

CURRENCY_SYMBOLS = {
    "USD": "$", "CAD": "C$", "EUR": "\u20ac", "GBP": "\u00a3",
    "DKK": "DKK ", "SEK": "SEK ", "NOK": "NOK ", "CHF": "CHF ",
    "JPY": "\u00a5", "HKD": "HK$", "TWD": "NT$", "KRW": "\u20a9",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_get(df, key, col_idx=0):
    """Safely extract a value from a DataFrame. Returns None on any failure."""
    if df is None or df.empty:
        return None
    if key not in df.index:
        return None
    if col_idx >= len(df.columns):
        return None
    val = df.loc[key].iloc[col_idx]
    if pd.isna(val):
        return None
    return float(val)


def fmt_number(value, currency_symbol="$"):
    """Format a number as $1.23B / $456.7M / $12.3K."""
    if value is None:
        return "n/a"
    negative = value < 0
    v = abs(value)
    if v >= 1e12:
        s = f"{v / 1e12:.1f}T"
    elif v >= 1e9:
        s = f"{v / 1e9:.1f}B"
    elif v >= 1e6:
        s = f"{v / 1e6:.1f}M"
    elif v >= 1e3:
        s = f"{v / 1e3:.1f}K"
    else:
        s = f"{v:.0f}"
    sign = "-" if negative else ""
    return f"{sign}{currency_symbol}{s}"


def fmt_pct(value):
    """Format a ratio as a percentage string."""
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def fmt_ratio(value):
    """Format a ratio with one decimal."""
    if value is None:
        return "n/a"
    return f"{value:.1f}x"


def fmt_price(value, currency_symbol="$"):
    """Format a price with 2 decimals."""
    if value is None:
        return "n/a"
    return f"{currency_symbol}{value:,.2f}"


def fmt_per_share(value):
    """Format an EPS-style number."""
    if value is None:
        return "n/a"
    return f"${value:.2f}"


def col_label(col):
    """Turn a DataFrame column (Timestamp or str) into 'FY2024' style label."""
    if hasattr(col, "year"):
        return f"FY{col.year}"
    return str(col)


def csym(currency_code):
    """Get currency symbol from code."""
    return CURRENCY_SYMBOLS.get(currency_code, f"{currency_code} ")


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

def compute_effective_tax_rate(income_stmt, col_idx):
    tax = safe_get(income_stmt, "Tax Provision", col_idx)
    pretax = safe_get(income_stmt, "Pretax Income", col_idx)
    if pretax and pretax != 0 and tax is not None:
        rate = tax / pretax
        if 0 <= rate <= 0.6:  # sanity check
            return rate
    return 0.21  # fallback to US statutory


def compute_roic(income_stmt, balance_sheet, col_idx):
    op_income = safe_get(income_stmt, "Operating Income", col_idx)
    if op_income is None:
        return None
    tax_rate = compute_effective_tax_rate(income_stmt, col_idx)
    nopat = op_income * (1 - tax_rate)

    ic = safe_get(balance_sheet, "Invested Capital", col_idx)
    ic_prior = safe_get(balance_sheet, "Invested Capital", col_idx + 1)
    if ic is not None and ic_prior is not None:
        avg_ic = (ic + ic_prior) / 2
    elif ic is not None:
        avg_ic = ic
    else:
        # derive: equity + debt - cash
        eq = safe_get(balance_sheet, "Stockholders Equity", col_idx)
        debt = safe_get(balance_sheet, "Total Debt", col_idx)
        cash = safe_get(balance_sheet, "Cash Cash Equivalents And Short Term Investments", col_idx)
        if all(v is not None for v in [eq, debt, cash]):
            avg_ic = eq + debt - cash
        else:
            return None

    if avg_ic and avg_ic != 0:
        return nopat / avg_ic
    return None


def compute_roe(income_stmt, balance_sheet, col_idx):
    ni = safe_get(income_stmt, "Net Income", col_idx)
    eq = safe_get(balance_sheet, "Stockholders Equity", col_idx)
    eq_prior = safe_get(balance_sheet, "Stockholders Equity", col_idx + 1)
    if ni is None or eq is None:
        return None
    avg_eq = (eq + eq_prior) / 2 if eq_prior is not None else eq
    if avg_eq and avg_eq != 0:
        return ni / avg_eq
    return None


def compute_roa(income_stmt, balance_sheet, col_idx):
    ni = safe_get(income_stmt, "Net Income", col_idx)
    assets = safe_get(balance_sheet, "Total Assets", col_idx)
    if ni is None or assets is None or assets == 0:
        return None
    return ni / assets


def compute_owner_earnings(income_stmt, cash_flow, col_idx):
    ni = safe_get(income_stmt, "Net Income", col_idx)
    da = safe_get(cash_flow, "Depreciation And Amortization", col_idx)
    capex = safe_get(cash_flow, "Capital Expenditure", col_idx)  # negative
    if all(v is not None for v in [ni, da, capex]):
        return ni + da + capex
    return None


def compute_fcf_conversion(income_stmt, cash_flow, col_idx):
    fcf = safe_get(cash_flow, "Free Cash Flow", col_idx)
    ni = safe_get(income_stmt, "Net Income", col_idx)
    if ni and ni != 0 and fcf is not None:
        return fcf / ni
    return None


def compute_interest_coverage(income_stmt, col_idx):
    ebit = safe_get(income_stmt, "EBIT", col_idx)
    if ebit is None:
        ebit = safe_get(income_stmt, "Operating Income", col_idx)
    interest = safe_get(income_stmt, "Interest Expense", col_idx)
    if interest is None or interest == 0:
        return None  # no debt or no data
    return abs(ebit / interest) if ebit is not None else None


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def validate_ticker(info):
    if not info:
        return False
    return info.get("currentPrice") is not None or info.get("regularMarketPrice") is not None


def fetch_ticker_data(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    if not validate_ticker(info):
        raise ValueError(f"No price data found for '{symbol}' — check the ticker symbol")

    data = {
        "info": info,
        "income_stmt": ticker.financials,
        "balance_sheet": ticker.balance_sheet,
        "cash_flow": ticker.cashflow,
        "price_history": ticker.history(period="1y"),
        "analyst_targets": None,
        "warnings": [],
    }

    try:
        data["analyst_targets"] = ticker.analyst_price_targets
    except Exception:
        data["warnings"].append("Analyst price targets not available")

    # Check for thin data
    if data["income_stmt"] is not None and len(data["income_stmt"].columns) < 3:
        data["warnings"].append(f"Only {len(data['income_stmt'].columns)} year(s) of income data available")
    if data["balance_sheet"] is None or data["balance_sheet"].empty:
        data["warnings"].append("Balance sheet data not available")
    if data["cash_flow"] is None or data["cash_flow"].empty:
        data["warnings"].append("Cash flow data not available")

    return data


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_header(symbol, info):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    name = info.get("longName") or info.get("shortName") or symbol
    fin_cur = info.get("financialCurrency", "USD")
    trade_cur = info.get("currency", fin_cur)
    sector = info.get("sector", "n/a")
    industry = info.get("industry", "n/a")

    lines = [
        f"# Financial Data: {symbol} — {name}",
        "",
        f"**Generated:** {now}",
        f"**Source:** Yahoo Finance (yfinance)",
        f"**Reporting Currency:** {fin_cur} | **Trading Currency:** {trade_cur}",
        f"**Sector:** {sector} | **Industry:** {industry}",
    ]
    if fin_cur != trade_cur:
        lines.append(f"\n> **Note:** Financial statements are in {fin_cur}. Stock price is in {trade_cur}. Be careful comparing across currencies.")
    lines.append(f"\n> Auto-generated by `scripts/fetch-financials.py`. Derived metrics (ROIC, owner earnings, etc.) are computed from raw data and may differ from third-party sources.")
    return "\n".join(lines)


def render_current_snapshot(info, warnings):
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    tc = csym(info.get("currency", "USD"))
    mcap = info.get("marketCap")
    ev = info.get("enterpriseValue")
    hi = info.get("fiftyTwoWeekHigh")
    lo = info.get("fiftyTwoWeekLow")
    beta = info.get("beta")
    shares = info.get("sharesOutstanding")
    div_yield = info.get("dividendYield")

    range_pct = None
    if price and hi and lo and hi != lo:
        range_pct = (price - lo) / (hi - lo) * 100

    rows = [
        ("Current Price", fmt_price(price, tc)),
        ("Market Cap", fmt_number(mcap, tc)),
        ("Enterprise Value", fmt_number(ev, tc)),
        ("52-Week High", fmt_price(hi, tc)),
        ("52-Week Low", fmt_price(lo, tc)),
        ("Position in 52-Week Range", f"{range_pct:.0f}%" if range_pct is not None else "n/a"),
        ("Beta", f"{beta:.2f}" if beta else "n/a"),
        ("Shares Outstanding", fmt_number(shares, "")),
        ("Dividend Yield", f"{div_yield:.2f}%" if div_yield else "n/a"),
    ]
    lines = ["## Current Snapshot", "", "| Metric | Value |", "|--------|-------|"]
    for label, val in rows:
        lines.append(f"| {label} | {val} |")
    return "\n".join(lines)


def render_valuation_multiples(info, cash_flow, warnings):
    fc = csym(info.get("financialCurrency", "USD"))
    mcap = info.get("marketCap")
    fcf = info.get("freeCashflow")
    if not fcf and cash_flow is not None:
        fcf = safe_get(cash_flow, "Free Cash Flow", 0)
    p_fcf = None
    if mcap and fcf and fcf > 0:
        p_fcf = mcap / fcf

    rows = [
        ("Trailing P/E", fmt_ratio(info.get("trailingPE"))),
        ("Forward P/E", fmt_ratio(info.get("forwardPE"))),
        ("EV/EBITDA", fmt_ratio(info.get("enterpriseToEbitda"))),
        ("EV/Revenue", fmt_ratio(info.get("enterpriseToRevenue"))),
        ("P/FCF", fmt_ratio(p_fcf)),
        ("P/S", fmt_ratio(info.get("priceToSalesTrailing12Months"))),
        ("P/B", fmt_ratio(info.get("priceToBook"))),
    ]
    lines = ["## Valuation Multiples", "", "| Metric | Value |", "|--------|-------|"]
    for label, val in rows:
        lines.append(f"| {label} | {val} |")
    return "\n".join(lines)


def render_analyst_estimates(info, analyst_targets, warnings):
    rows = [
        ("Target Mean", fmt_price(info.get("targetMeanPrice"), csym(info.get("currency", "USD")))),
        ("Target Median", fmt_price(info.get("targetMedianPrice"), csym(info.get("currency", "USD")))),
        ("Target High", fmt_price(info.get("targetHighPrice"), csym(info.get("currency", "USD")))),
        ("Target Low", fmt_price(info.get("targetLowPrice"), csym(info.get("currency", "USD")))),
        ("Number of Analysts", str(info.get("numberOfAnalystOpinions", "n/a"))),
        ("Forward EPS", fmt_per_share(info.get("forwardEps"))),
        ("Trailing EPS", fmt_per_share(info.get("trailingEps"))),
    ]
    lines = ["## Analyst Estimates", "", "| Metric | Value |", "|--------|-------|"]
    for label, val in rows:
        lines.append(f"| {label} | {val} |")
    return "\n".join(lines)


def render_income_statement(income_stmt, warnings):
    if income_stmt is None or income_stmt.empty:
        warnings.append("Income statement not available — section skipped")
        return "## Income Statement (Annual)\n\nNo data available."

    fc_symbol = "$"  # will be overridden by header context
    cols = income_stmt.columns
    headers = ["Metric"] + [col_label(c) for c in cols]
    sep = ["|".join(["-----"] * (len(cols) + 1))]

    field_map = [
        ("Revenue", "Total Revenue"),
        ("Gross Profit", "Gross Profit"),
        ("Operating Income", "Operating Income"),
        ("EBITDA", "EBITDA"),
        ("Net Income", "Net Income"),
        ("Diluted EPS", "Diluted EPS"),
        ("Interest Expense", "Interest Expense"),
        ("Tax Provision", "Tax Provision"),
        ("R&D", "Research And Development"),
        ("D&A", "Reconciled Depreciation"),
        ("SBC", None),  # from cash flow, handled separately
    ]

    lines = ["## Income Statement (Annual)", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["------"] * len(headers)) + " |"]
    for label, key in field_map:
        if key is None:
            continue
        vals = []
        for i in range(len(cols)):
            v = safe_get(income_stmt, key, i)
            if label == "Diluted EPS":
                vals.append(fmt_per_share(v))
            else:
                vals.append(fmt_number(v))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def render_margins(income_stmt, cash_flow, warnings):
    if income_stmt is None or income_stmt.empty:
        return "## Margins (Annual)\n\nNo data available."

    cols = income_stmt.columns
    headers = ["Metric"] + [col_label(c) for c in cols]
    lines = ["## Margins (Annual)", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["------"] * len(headers)) + " |"]

    for label, num_key, denom_key in [
        ("Gross Margin", "Gross Profit", "Total Revenue"),
        ("Operating Margin", "Operating Income", "Total Revenue"),
        ("Net Margin", "Net Income", "Total Revenue"),
        ("EBITDA Margin", "EBITDA", "Total Revenue"),
    ]:
        vals = []
        for i in range(len(cols)):
            num = safe_get(income_stmt, num_key, i)
            denom = safe_get(income_stmt, denom_key, i)
            if num is not None and denom and denom != 0:
                vals.append(fmt_pct(num / denom))
            else:
                vals.append("n/a")
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    # FCF margin
    if cash_flow is not None and not cash_flow.empty:
        vals = []
        for i in range(len(cols)):
            fcf = safe_get(cash_flow, "Free Cash Flow", i) if i < len(cash_flow.columns) else None
            rev = safe_get(income_stmt, "Total Revenue", i)
            if fcf is not None and rev and rev != 0:
                vals.append(fmt_pct(fcf / rev))
            else:
                vals.append("n/a")
        lines.append(f"| FCF Margin | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def render_returns_on_capital(income_stmt, balance_sheet, warnings):
    if income_stmt is None or balance_sheet is None or income_stmt.empty or balance_sheet.empty:
        warnings.append("Returns on capital not computable — missing income or balance sheet data")
        return "## Returns on Capital (Annual, Derived)\n\nNo data available."

    cols = income_stmt.columns
    headers = ["Metric"] + [col_label(c) for c in cols]
    lines = [
        "## Returns on Capital (Annual, Derived)",
        "",
        "*ROIC = NOPAT / avg Invested Capital. NOPAT = Operating Income x (1 - Effective Tax Rate).*",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["------"] * len(headers)) + " |",
    ]

    for label, fn in [("ROIC", compute_roic), ("ROE", compute_roe), ("ROA", compute_roa)]:
        vals = []
        for i in range(len(cols)):
            v = fn(income_stmt, balance_sheet, i)
            vals.append(fmt_pct(v))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def render_cash_flow(income_stmt, cash_flow, warnings):
    if cash_flow is None or cash_flow.empty:
        warnings.append("Cash flow statement not available — section skipped")
        return "## Cash Flow (Annual)\n\nNo data available."

    cols = cash_flow.columns
    headers = ["Metric"] + [col_label(c) for c in cols]
    lines = ["## Cash Flow (Annual)", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["------"] * len(headers)) + " |"]

    field_map = [
        ("Operating Cash Flow", "Operating Cash Flow"),
        ("Capital Expenditure", "Capital Expenditure"),
        ("Free Cash Flow", "Free Cash Flow"),
        ("D&A", "Depreciation And Amortization"),
        ("Stock-Based Compensation", "Stock Based Compensation"),
        ("Buybacks", "Repurchase Of Capital Stock"),
    ]
    for label, key in field_map:
        vals = []
        for i in range(len(cols)):
            vals.append(fmt_number(safe_get(cash_flow, key, i)))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    # Derived: FCF conversion, owner earnings
    if income_stmt is not None and not income_stmt.empty:
        # FCF conversion
        vals = []
        for i in range(len(cols)):
            v = compute_fcf_conversion(income_stmt, cash_flow, i)
            vals.append(fmt_pct(v))
        lines.append(f"| FCF Conversion (FCF/NI) | " + " | ".join(vals) + " |")

        # Owner earnings
        vals = []
        for i in range(len(cols)):
            v = compute_owner_earnings(income_stmt, cash_flow, i)
            vals.append(fmt_number(v))
        lines.append(f"| Owner Earnings (NI+D&A-CapEx) | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def render_balance_sheet(balance_sheet, warnings):
    if balance_sheet is None or balance_sheet.empty:
        return "## Balance Sheet (Annual)\n\nNo data available."

    cols = balance_sheet.columns
    headers = ["Metric"] + [col_label(c) for c in cols]
    lines = ["## Balance Sheet (Annual)", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["------"] * len(headers)) + " |"]

    field_map = [
        ("Total Assets", "Total Assets"),
        ("Total Debt", "Total Debt"),
        ("Long-Term Debt", "Long Term Debt"),
        ("Cash & Short-Term Investments", "Cash Cash Equivalents And Short Term Investments"),
        ("Net Debt", "Net Debt"),
        ("Stockholders' Equity", "Stockholders Equity"),
        ("Invested Capital", "Invested Capital"),
        ("Current Assets", "Current Assets"),
        ("Current Liabilities", "Current Liabilities"),
        ("Working Capital", "Working Capital"),
    ]
    for label, key in field_map:
        vals = []
        for i in range(len(cols)):
            vals.append(fmt_number(safe_get(balance_sheet, key, i)))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def render_debt_safety(income_stmt, balance_sheet, warnings):
    if income_stmt is None or balance_sheet is None or income_stmt.empty or balance_sheet.empty:
        return "## Debt & Safety Ratios (Annual, Derived)\n\nNo data available."

    cols = income_stmt.columns
    headers = ["Metric"] + [col_label(c) for c in cols]
    lines = ["## Debt & Safety Ratios (Annual, Derived)", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["------"] * len(headers)) + " |"]

    # Debt/EBITDA
    vals = []
    for i in range(len(cols)):
        debt = safe_get(balance_sheet, "Total Debt", i) if i < len(balance_sheet.columns) else None
        ebitda = safe_get(income_stmt, "EBITDA", i)
        if debt is not None and ebitda and ebitda != 0:
            vals.append(fmt_ratio(debt / ebitda))
        else:
            vals.append("n/a")
    lines.append(f"| Debt/EBITDA | " + " | ".join(vals) + " |")

    # Net Debt/EBITDA
    vals = []
    for i in range(len(cols)):
        nd = safe_get(balance_sheet, "Net Debt", i) if i < len(balance_sheet.columns) else None
        ebitda = safe_get(income_stmt, "EBITDA", i)
        if nd is not None and ebitda and ebitda != 0:
            vals.append(fmt_ratio(nd / ebitda))
        else:
            vals.append("n/a")
    lines.append(f"| Net Debt/EBITDA | " + " | ".join(vals) + " |")

    # Interest coverage
    vals = []
    for i in range(len(cols)):
        v = compute_interest_coverage(income_stmt, i)
        if v is not None:
            vals.append(fmt_ratio(v))
        else:
            interest = safe_get(income_stmt, "Interest Expense", i)
            if interest is None or interest == 0:
                vals.append("no debt")
            else:
                vals.append("n/a")
    lines.append(f"| Interest Coverage (EBIT/Interest) | " + " | ".join(vals) + " |")

    # Current ratio
    vals = []
    for i in range(len(cols)):
        ca = safe_get(balance_sheet, "Current Assets", i) if i < len(balance_sheet.columns) else None
        cl = safe_get(balance_sheet, "Current Liabilities", i) if i < len(balance_sheet.columns) else None
        if ca is not None and cl and cl != 0:
            vals.append(fmt_ratio(ca / cl))
        else:
            vals.append("n/a")
    lines.append(f"| Current Ratio | " + " | ".join(vals) + " |")

    # Debt/Equity
    vals = []
    for i in range(len(cols)):
        debt = safe_get(balance_sheet, "Total Debt", i) if i < len(balance_sheet.columns) else None
        eq = safe_get(balance_sheet, "Stockholders Equity", i) if i < len(balance_sheet.columns) else None
        if debt is not None and eq and eq != 0:
            vals.append(fmt_pct(debt / eq))
        else:
            vals.append("n/a")
    lines.append(f"| Debt/Equity | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def render_price_context(info, price_history, warnings):
    if price_history is None or price_history.empty:
        warnings.append("Price history not available")
        return "## Price History Context\n\nNo data available."

    tc = csym(info.get("currency", "USD"))
    current = info.get("currentPrice") or info.get("regularMarketPrice")
    if current is None:
        return "## Price History Context\n\nNo current price available."

    lines = ["## Price History Context", "", "| Period | Price | Change |", "|--------|-------|--------|"]
    lines.append(f"| Current | {fmt_price(current, tc)} | — |")

    # Historical lookbacks
    for label, days in [("1 Month Ago", 21), ("3 Months Ago", 63), ("6 Months Ago", 126), ("1 Year Ago", 252)]:
        if len(price_history) >= days:
            idx = min(days, len(price_history) - 1)
            hist_price = price_history["Close"].iloc[-idx]
            if pd.notna(hist_price) and hist_price != 0:
                chg = (current - hist_price) / hist_price * 100
                lines.append(f"| {label} | {fmt_price(hist_price, tc)} | {chg:+.1f}% |")
            else:
                lines.append(f"| {label} | n/a | n/a |")
        else:
            lines.append(f"| {label} | n/a | n/a |")

    # 52-week high/low from history
    hi_val = price_history["High"].max()
    lo_val = price_history["Low"].min()
    if pd.notna(hi_val):
        hi_date = price_history["High"].idxmax()
        drawdown = (current - hi_val) / hi_val * 100
        date_str = hi_date.strftime("%Y-%m-%d") if hasattr(hi_date, "strftime") else str(hi_date)
        lines.append(f"| 52-Week High | {fmt_price(hi_val, tc)} ({date_str}) | {drawdown:+.1f}% from current |")
    if pd.notna(lo_val):
        lo_date = price_history["Low"].idxmin()
        upside = (current - lo_val) / lo_val * 100
        date_str = lo_date.strftime("%Y-%m-%d") if hasattr(lo_date, "strftime") else str(lo_date)
        lines.append(f"| 52-Week Low | {fmt_price(lo_val, tc)} ({date_str}) | {upside:+.1f}% from current |")

    return "\n".join(lines)


def render_warnings(warnings):
    if not warnings:
        return "## Data Gaps & Warnings\n\nNone — all sections populated successfully."
    lines = ["## Data Gaps & Warnings", ""]
    for w in warnings:
        lines.append(f"- {w}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------

def generate_markdown(symbol, data):
    info = data["info"]
    income_stmt = data["income_stmt"]
    balance_sheet = data["balance_sheet"]
    cash_flow = data["cash_flow"]
    price_history = data["price_history"]
    warnings = data["warnings"]

    sections = [
        render_header(symbol, info),
        render_current_snapshot(info, warnings),
        render_valuation_multiples(info, cash_flow, warnings),
        render_analyst_estimates(info, data["analyst_targets"], warnings),
        render_income_statement(income_stmt, warnings),
        render_margins(income_stmt, cash_flow, warnings),
        render_returns_on_capital(income_stmt, balance_sheet, warnings),
        render_cash_flow(income_stmt, cash_flow, warnings),
        render_balance_sheet(balance_sheet, warnings),
        render_debt_safety(income_stmt, balance_sheet, warnings),
        render_price_context(info, price_history, warnings),
        render_warnings(warnings),
    ]
    return "\n\n---\n\n".join(sections) + "\n"


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def write_context(symbol, markdown):
    out_dir = CONTEXT_DIR / symbol
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "financials.md"
    out_file.write_text(markdown, encoding="utf-8")
    return out_file


def is_fresh(symbol):
    out_file = CONTEXT_DIR / symbol / "financials.md"
    if not out_file.exists():
        return False
    mtime = datetime.fromtimestamp(out_file.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    return age_hours < FRESHNESS_HOURS


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def resolve_tickers(args):
    if args.all_reports:
        tickers = {p.parent.name for p in RUNS_DIR.glob("*/reports/*/FINAL-REPORT.json")}
        return sorted(tickers)
    if args.all_queue:
        if not QUEUE_FILE.exists():
            print("ERROR: queue/queue.json not found", file=sys.stderr)
            sys.exit(2)
        queue = json.loads(QUEUE_FILE.read_text())
        return [e["ticker"] for e in queue if e.get("current_state") == args.all_queue]
    return [t.strip() for t in args.tickers if t.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch financial data from Yahoo Finance for analysis agents"
    )
    parser.add_argument("tickers", nargs="*", help="Ticker symbols (e.g., AAPL MSFT NOVO-B.CO)")
    parser.add_argument("--all-reports", action="store_true", help="Fetch for all tickers in reports/")
    parser.add_argument("--all-queue", type=str, metavar="STATE", help="Fetch for all tickers in a queue state")
    parser.add_argument("--force", action="store_true", help="Overwrite even if <24h old")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    tickers = resolve_tickers(args)
    if not tickers:
        parser.error("No tickers specified. Provide ticker symbols, --all-reports, or --all-queue STATE.")

    if not args.quiet:
        print(f"Fetching financial data for {len(tickers)} ticker(s)...\n")

    results = []
    for i, symbol in enumerate(tickers):
        if not args.force and is_fresh(symbol):
            if not args.quiet:
                print(f"  [{i+1}/{len(tickers)}] {symbol} — skipped (fresh)")
            results.append((symbol, "skipped"))
            continue

        try:
            data = fetch_ticker_data(symbol)
            md = generate_markdown(symbol, data)
            out = write_context(symbol, md)
            size = out.stat().st_size
            if not args.quiet:
                print(f"  [{i+1}/{len(tickers)}] {symbol} -> {out.relative_to(REPO_ROOT)} ({size // 1024} KB)")
            results.append((symbol, "ok"))
        except Exception as e:
            print(f"  [{i+1}/{len(tickers)}] {symbol} — ERROR: {e}", file=sys.stderr)
            results.append((symbol, f"error: {e}"))

        # Rate limit between tickers
        if i < len(tickers) - 1:
            time.sleep(1)

    # Summary
    ok = sum(1 for _, s in results if s == "ok")
    skipped = sum(1 for _, s in results if s == "skipped")
    failed = sum(1 for _, s in results if s.startswith("error"))
    if not args.quiet:
        print(f"\nDone: {ok} fetched, {skipped} skipped, {failed} failed")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
