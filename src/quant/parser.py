"""Parse context/{TICKER}/financials.md (or .json) into FinancialData."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import FinancialData

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def parse_fmt_number(s: str) -> float | None:
    """Reverse fmt_number: '$17.7B' -> 17_700_000_000, '-$4.5B' -> -4_500_000_000, 'n/a' -> None."""
    s = s.strip()
    if not s or s == "n/a" or s == "—" or s == "no debt":
        return None

    # Detect negative: could be '-$4.5B' or '$-4.5B'
    negative = "-" in s

    # Strip everything except digits, dots, and suffix letters
    cleaned = re.sub(r"[^0-9.TBMK]", "", s)

    multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
    mult = 1.0
    for suffix, m in multipliers.items():
        if cleaned.endswith(suffix):
            mult = m
            cleaned = cleaned[:-1]
            break

    try:
        val = float(cleaned) * mult
        return -val if negative else val
    except ValueError:
        return None


def parse_pct(s: str) -> float | None:
    """Parse '57.0%' -> 0.57, 'n/a' -> None."""
    s = s.strip()
    if not s or s == "n/a":
        return None
    m = re.search(r"(-?[\d.]+)%", s)
    if m:
        return float(m.group(1)) / 100
    return None


def parse_ratio(s: str) -> float | None:
    """Parse '11.5x' -> 11.5, 'n/a' -> None."""
    s = s.strip()
    if not s or s == "n/a" or s == "no debt":
        return None
    m = re.search(r"(-?[\d.]+)x", s)
    if m:
        return float(m.group(1))
    return None


def parse_price(s: str) -> float | None:
    """Parse '$194.13' or '€166.44' or 'DKK 1,590.50' -> float."""
    s = s.strip()
    if not s or s == "n/a":
        return None
    # Strip currency prefix, parenthetical dates, "from current" text
    s = re.sub(r"\(.*?\)", "", s).strip()
    s = re.sub(r"from current.*", "", s).strip()
    m = re.search(r"([\d,]+\.?\d*)", s)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def _extract_fiscal_years(header_cells: list[str]) -> list[int | None]:
    """Extract fiscal years from table header cells like 'FY2025'."""
    years = []
    for cell in header_cells:
        m = re.search(r"FY(\d{4})", cell)
        years.append(int(m.group(1)) if m else None)
    return years


def _parse_table_rows(lines: list[str]) -> list[tuple[str, list[str]]]:
    """Parse markdown table rows into (label, [cell_values]) tuples.
    Skips header separator rows (|---|---|).

    Markdown table: '| Metric | FY2025 | FY2024 |'
    Split by '|' gives ['', ' Metric ', ' FY2025 ', ' FY2024 ', '']
    We strip the leading/trailing empty strings from the pipe split.
    """
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # Drop leading and trailing empty strings from pipe split
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if len(cells) < 2:
            continue
        # Skip separator rows
        if all(re.match(r"^-+$", c) for c in cells):
            continue
        rows.append((cells[0], cells[1:]))
    return rows


def _parse_kv_table(lines: list[str]) -> dict[str, str]:
    """Parse a 2-column key-value markdown table into a dict."""
    result = {}
    for label, vals in _parse_table_rows(lines):
        if vals:
            result[label] = vals[0]
    return result


def _parse_ts_table(
    lines: list[str],
    value_parser,
) -> tuple[list[int], dict[str, dict[int, float]]]:
    """Parse a multi-column time-series table.
    Returns (fiscal_years, {metric_name: {year: value}})."""
    rows = _parse_table_rows(lines)
    if not rows:
        return [], {}

    # First row is header with metric names and FY columns
    header_label, header_vals = rows[0]
    years = _extract_fiscal_years(header_vals)

    data: dict[str, dict[int, float]] = {}
    for label, vals in rows[1:]:
        series: dict[int, float] = {}
        for i, val_str in enumerate(vals):
            if i < len(years) and years[i] is not None:
                parsed = value_parser(val_str)
                if parsed is not None:
                    series[years[i]] = parsed
        if series:
            data[label] = series
    return [y for y in years if y is not None], data


def _split_sections(text: str) -> dict[str, list[str]]:
    """Split markdown by ## headers into {section_name: [lines]}."""
    sections: dict[str, list[str]] = {}
    current = None
    current_lines: list[str] = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current is not None:
                sections[current] = current_lines
            current = line[3:].strip()
            current_lines = []
        elif current is not None:
            current_lines.append(line)

    if current is not None:
        sections[current] = current_lines
    return sections


def _load_from_json(path: Path) -> FinancialData:
    """Load FinancialData directly from a financials.json file."""
    raw = json.loads(path.read_text())
    fd = FinancialData()

    # Scalar string fields
    for key in ("ticker", "company", "generated_date", "reporting_currency",
                "trading_currency", "sector", "industry"):
        val = raw.get(key)
        if val is not None:
            setattr(fd, key, val)

    # Scalar numeric fields
    for key in ("current_price", "market_cap", "enterprise_value",
                "shares_outstanding", "beta", "dividend_yield",
                "week52_high", "week52_low",
                "trailing_pe", "forward_pe", "ev_ebitda", "ev_revenue",
                "p_fcf", "p_s", "p_b",
                "forward_eps", "trailing_eps",
                "target_mean", "target_median", "target_high", "target_low",
                "num_analysts"):
        val = raw.get(key)
        if val is not None:
            setattr(fd, key, int(val) if key == "num_analysts" else float(val))

    # Time-series fields: JSON has {str_year: float}, convert to {int_year: float}
    ts_fields = [
        "revenue", "gross_profit", "operating_income", "ebitda", "net_income",
        "diluted_eps", "interest_expense", "tax_provision", "rnd", "da",
        "gross_margin", "operating_margin", "net_margin", "ebitda_margin", "fcf_margin",
        "roic", "roe", "roa",
        "operating_cf", "capex", "fcf", "cf_da", "sbc", "buybacks",
        "fcf_conversion", "owner_earnings",
        "total_assets", "total_debt", "long_term_debt", "cash", "net_debt",
        "equity", "invested_capital", "current_assets", "current_liabilities",
        "working_capital",
        "debt_ebitda", "net_debt_ebitda", "interest_coverage", "current_ratio",
        "debt_equity",
    ]
    for key in ts_fields:
        series = raw.get(key, {})
        if isinstance(series, dict):
            setattr(fd, key, {int(y): float(v) for y, v in series.items() if v is not None})

    return fd


def parse_financials(ticker: str, context_dir: Path | None = None) -> FinancialData:
    """Parse context/{TICKER}/financials.json (preferred) or financials.md into FinancialData."""
    if context_dir is None:
        context_dir = REPO_ROOT / "context"

    # Try JSON first — structured, no parsing loss
    json_path = context_dir / ticker / "financials.json"
    if json_path.exists():
        try:
            return _load_from_json(json_path)
        except (json.JSONDecodeError, KeyError, ValueError):
            pass  # fall through to markdown parser

    path = context_dir / ticker / "financials.md"
    if not path.exists():
        raise FileNotFoundError(f"No financials for {ticker} at {context_dir / ticker}")

    text = path.read_text()
    fd = FinancialData(ticker=ticker)

    # Parse header metadata
    m = re.search(r"# Financial Data: (\S+) — (.+)", text)
    if m:
        fd.ticker = m.group(1)
        fd.company = m.group(2)

    m = re.search(r"\*\*Generated:\*\*\s*([\d-]+ [\d:]+ UTC)", text)
    if m:
        fd.generated_date = m.group(1)

    m = re.search(r"\*\*Reporting Currency:\*\*\s*(\w+)", text)
    if m:
        fd.reporting_currency = m.group(1)

    m = re.search(r"\*\*Trading Currency:\*\*\s*(\w+)", text)
    if m:
        fd.trading_currency = m.group(1)

    m = re.search(r"\*\*Sector:\*\*\s*([^|*]+)", text)
    if m:
        fd.sector = m.group(1).strip()

    m = re.search(r"\*\*Industry:\*\*\s*(.+)", text)
    if m:
        fd.industry = m.group(1).strip()

    sections = _split_sections(text)

    # --- Current Snapshot ---
    if "Current Snapshot" in sections:
        kv = _parse_kv_table(sections["Current Snapshot"])
        fd.current_price = parse_price(kv.get("Current Price", ""))
        fd.market_cap = parse_fmt_number(kv.get("Market Cap", ""))
        fd.enterprise_value = parse_fmt_number(kv.get("Enterprise Value", ""))
        fd.week52_high = parse_price(kv.get("52-Week High", ""))
        fd.week52_low = parse_price(kv.get("52-Week Low", ""))
        fd.shares_outstanding = parse_fmt_number(kv.get("Shares Outstanding", ""))
        fd.beta = parse_ratio(kv.get("Beta", "").replace("Beta", "").strip() + "x") if kv.get("Beta") else None
        # Beta is plain number, not ratio
        beta_str = kv.get("Beta", "")
        if beta_str and beta_str != "n/a":
            try:
                fd.beta = float(beta_str)
            except ValueError:
                pass
        dy_str = kv.get("Dividend Yield", "")
        fd.dividend_yield = parse_pct(dy_str)

    # --- Valuation Multiples ---
    if "Valuation Multiples" in sections:
        kv = _parse_kv_table(sections["Valuation Multiples"])
        fd.trailing_pe = parse_ratio(kv.get("Trailing P/E", ""))
        fd.forward_pe = parse_ratio(kv.get("Forward P/E", ""))
        fd.ev_ebitda = parse_ratio(kv.get("EV/EBITDA", ""))
        fd.ev_revenue = parse_ratio(kv.get("EV/Revenue", ""))
        fd.p_fcf = parse_ratio(kv.get("P/FCF", ""))
        fd.p_s = parse_ratio(kv.get("P/S", ""))
        fd.p_b = parse_ratio(kv.get("P/B", ""))

    # --- Analyst Estimates ---
    if "Analyst Estimates" in sections:
        kv = _parse_kv_table(sections["Analyst Estimates"])
        fd.target_mean = parse_price(kv.get("Target Mean", ""))
        fd.target_median = parse_price(kv.get("Target Median", ""))
        fd.target_high = parse_price(kv.get("Target High", ""))
        fd.target_low = parse_price(kv.get("Target Low", ""))
        fd.forward_eps = parse_price(kv.get("Forward EPS", ""))
        fd.trailing_eps = parse_price(kv.get("Trailing EPS", ""))
        na_str = kv.get("Number of Analysts", "")
        if na_str and na_str != "n/a":
            try:
                fd.num_analysts = int(na_str)
            except ValueError:
                pass

    # --- Income Statement ---
    income_key = next((k for k in sections if "Income Statement" in k), None)
    if income_key:
        _, data = _parse_ts_table(sections[income_key], parse_fmt_number)
        fd.revenue = data.get("Revenue", {})
        fd.gross_profit = data.get("Gross Profit", {})
        fd.operating_income = data.get("Operating Income", {})
        fd.ebitda = data.get("EBITDA", {})
        fd.net_income = data.get("Net Income", {})
        fd.diluted_eps = data.get("Diluted EPS", {})
        fd.interest_expense = data.get("Interest Expense", {})
        fd.tax_provision = data.get("Tax Provision", {})
        fd.rnd = data.get("R&D", {})
        fd.da = data.get("D&A", {})

    # --- Margins ---
    margins_key = next((k for k in sections if k.startswith("Margins")), None)
    if margins_key:
        _, data = _parse_ts_table(sections[margins_key], parse_pct)
        fd.gross_margin = data.get("Gross Margin", {})
        fd.operating_margin = data.get("Operating Margin", {})
        fd.net_margin = data.get("Net Margin", {})
        fd.ebitda_margin = data.get("EBITDA Margin", {})
        fd.fcf_margin = data.get("FCF Margin", {})

    # --- Returns on Capital ---
    returns_key = next((k for k in sections if "Returns on Capital" in k), None)
    if returns_key:
        _, data = _parse_ts_table(sections[returns_key], parse_pct)
        fd.roic = data.get("ROIC", {})
        fd.roe = data.get("ROE", {})
        fd.roa = data.get("ROA", {})

    # --- Cash Flow ---
    cf_key = next((k for k in sections if k.startswith("Cash Flow")), None)
    if cf_key:
        _, data = _parse_ts_table(sections[cf_key], parse_fmt_number)
        fd.operating_cf = data.get("Operating Cash Flow", {})
        fd.capex = data.get("Capital Expenditure", {})
        fd.fcf = data.get("Free Cash Flow", {})
        fd.cf_da = data.get("D&A", {})
        fd.sbc = data.get("Stock-Based Compensation", {})
        fd.buybacks = data.get("Buybacks", {})
        fd.owner_earnings = data.get("Owner Earnings (NI+D&A-CapEx)", {})

        # FCF Conversion is a percentage
        for label, vals in _parse_table_rows(sections[cf_key]):
            if "FCF Conversion" in label:
                years_header = _parse_table_rows(sections[cf_key])[0]
                fy_years = _extract_fiscal_years(years_header[1])
                for i, val_str in enumerate(vals):
                    if i < len(fy_years) and fy_years[i] is not None:
                        parsed = parse_pct(val_str)
                        if parsed is not None:
                            fd.fcf_conversion[fy_years[i]] = parsed

    # --- Balance Sheet ---
    bs_key = next((k for k in sections if "Balance Sheet" in k), None)
    if bs_key:
        _, data = _parse_ts_table(sections[bs_key], parse_fmt_number)
        fd.total_assets = data.get("Total Assets", {})
        fd.total_debt = data.get("Total Debt", {})
        fd.long_term_debt = data.get("Long-Term Debt", {})
        fd.cash = data.get("Cash & Short-Term Investments", {})
        fd.net_debt = data.get("Net Debt", {})
        fd.equity = data.get("Stockholders' Equity", {})
        fd.invested_capital = data.get("Invested Capital", {})
        fd.current_assets = data.get("Current Assets", {})
        fd.current_liabilities = data.get("Current Liabilities", {})
        fd.working_capital = data.get("Working Capital", {})

    # --- Debt & Safety Ratios ---
    debt_key = next((k for k in sections if "Debt" in k and "Safety" in k), None)
    if debt_key:
        _, data = _parse_ts_table(sections[debt_key], parse_ratio)
        fd.debt_ebitda = data.get("Debt/EBITDA", {})
        fd.net_debt_ebitda = data.get("Net Debt/EBITDA", {})
        fd.interest_coverage = data.get("Interest Coverage (EBIT/Interest)", {})
        fd.current_ratio = data.get("Current Ratio", {})
        # Debt/Equity is a percentage in the source
        _, pct_data = _parse_ts_table(sections[debt_key], parse_pct)
        fd.debt_equity = pct_data.get("Debt/Equity", {})

    return fd
