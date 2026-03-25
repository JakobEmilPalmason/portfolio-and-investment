"""Tests for src.quant.parser — financials.md/.json parsing and helper functions."""

import pytest
from pathlib import Path

from src.quant.parser import parse_financials, parse_fmt_number, parse_pct, parse_ratio, parse_price

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = REPO_ROOT / "context"


# ---------------------------------------------------------------------------
# test_parse_txn_financials — integration test against real TXN data
# ---------------------------------------------------------------------------

def test_parse_txn_financials():
    fd = parse_financials("TXN")

    assert fd.ticker == "TXN"
    assert len(fd.revenue) >= 3, f"Expected >=3 fiscal years of revenue, got {len(fd.revenue)}"
    assert fd.current_price is not None and fd.current_price > 100
    assert fd.shares_outstanding is not None and fd.shares_outstanding > 500e6


# ---------------------------------------------------------------------------
# test_json_vs_markdown_parity — JSON and markdown parsers produce matching data
# ---------------------------------------------------------------------------

def test_json_vs_markdown_parity():
    """Load TXN via JSON path and markdown path; assert key fields match."""
    json_path = CONTEXT_DIR / "TXN" / "financials.json"
    md_path = CONTEXT_DIR / "TXN" / "financials.md"
    if not json_path.exists() or not md_path.exists():
        pytest.skip("TXN financials.json or financials.md not present")

    # Load via JSON (default path)
    fd_json = parse_financials("TXN")

    # Load via markdown by temporarily hiding the JSON file
    import os
    tmp_path = json_path.with_suffix(".json.bak")
    os.rename(json_path, tmp_path)
    try:
        fd_md = parse_financials("TXN")
    finally:
        os.rename(tmp_path, json_path)

    # Scalars — JSON has exact values, markdown has formatting loss
    assert fd_json.ticker == fd_md.ticker == "TXN"
    assert fd_json.current_price == pytest.approx(fd_md.current_price, rel=0.01)
    if fd_json.shares_outstanding and fd_md.shares_outstanding:
        assert fd_json.shares_outstanding == pytest.approx(fd_md.shares_outstanding, rel=0.05)

    # Time-series — compare latest year revenue within 5% (markdown rounds to 1 decimal in B/M)
    if fd_json.revenue and fd_md.revenue:
        latest = max(fd_json.revenue.keys())
        if latest in fd_md.revenue:
            assert fd_json.revenue[latest] == pytest.approx(fd_md.revenue[latest], rel=0.05)

    # Margins — within 0.01 absolute (percentage rounding)
    if fd_json.gross_margin and fd_md.gross_margin:
        latest = max(fd_json.gross_margin.keys())
        if latest in fd_md.gross_margin:
            assert fd_json.gross_margin[latest] == pytest.approx(fd_md.gross_margin[latest], abs=0.01)


# ---------------------------------------------------------------------------
# test_json_fallback_to_markdown — parser works when JSON is absent
# ---------------------------------------------------------------------------

def test_json_fallback_to_markdown():
    """Verify parse_financials works via markdown when no JSON exists."""
    md_path = CONTEXT_DIR / "TXN" / "financials.md"
    json_path = CONTEXT_DIR / "TXN" / "financials.json"
    if not md_path.exists():
        pytest.skip("TXN financials.md not present")

    import os
    tmp_path = json_path.with_suffix(".json.bak") if json_path.exists() else None
    if tmp_path:
        os.rename(json_path, tmp_path)
    try:
        fd = parse_financials("TXN")
        assert fd.ticker == "TXN"
        assert fd.current_price is not None
        assert len(fd.revenue) >= 3
    finally:
        if tmp_path and tmp_path.exists():
            os.rename(tmp_path, json_path)


# ---------------------------------------------------------------------------
# test_parse_fmt_number — dollar-formatted strings to raw floats
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("input_str, expected", [
    ("$17.7B", 17.7e9),
    ("-$4.5B", -4.5e9),
    ("$543.0M", 543e6),
    ("n/a", None),
    ("—", None),
])
def test_parse_fmt_number(input_str, expected):
    result = parse_fmt_number(input_str)
    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# test_parse_pct — percentage strings to decimals
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("input_str, expected", [
    ("57.0%", 0.57),
    ("-14.2%", -0.142),
    ("n/a", None),
])
def test_parse_pct(input_str, expected):
    result = parse_pct(input_str)
    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# test_parse_ratio — multiplier strings to floats
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("input_str, expected", [
    ("35.6x", 35.6),
    ("11.5x", 11.5),
    ("n/a", None),
])
def test_parse_ratio(input_str, expected):
    result = parse_ratio(input_str)
    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# test_parse_price — currency strings to floats
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("input_str, expected", [
    ("$194.13", 194.13),
    ("$1,234.56", 1234.56),
])
def test_parse_price(input_str, expected):
    result = parse_price(input_str)
    assert result == pytest.approx(expected, rel=1e-6)
