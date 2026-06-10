"""
EDGAR client — fetch 10-K/20-F financials for a ticker.

Identity: set via EDGAR_IDENTITY env var.
Rate limiting: handled by edgartools (pyrate-limiter, 9 req/sec).
Freshness: skips if data/context/{TICKER}/edgar-10k.md < 24h old unless --force.
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
CONTEXT_DIR = REPO_ROOT / "data" / "context"
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


def fetch_10k(ticker: str, force: bool = False, quiet: bool = False) -> dict | str | None:
    """
    Fetch 10-K/20-F financials for a ticker via edgartools.

    Returns {"company": str, "financials": dict, "filing_metadata": dict},
    "skipped" if fresh, or None on failure.
    """
    _set_identity()

    if not force and _is_fresh(ticker):
        if not quiet:
            print(f"  {ticker} — skipped (fresh)")
        return "skipped"

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
            latest = filings.latest()
            filing_metadata["form_type"] = latest.form
            filing_metadata["filing_date"] = str(latest.filing_date)
            filing_metadata["period_of_report"] = str(latest.period_of_report)
            filing_metadata["accession_no"] = latest.accession_no
    except Exception as e:
        if not quiet:
            print(f"  {ticker} — Warning: filing metadata fetch failed: {e}", file=sys.stderr)

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


def fetch_filing_object(ticker: str, force: bool = False, quiet: bool = False):
    """
    Fetch the latest 10-K/20-F/40-F filing object for narrative section parsing.

    Returns (filing_obj, filing_metadata) or (None, None) on failure.
    The filing_obj is a TenK/TwentyF/FortyF with section accessors
    (.business, .risk_factors, .management_discussion, etc.).
    """
    _set_identity()

    try:
        company = Company(ticker)
    except CompanyNotFoundError:
        if not quiet:
            print(f"  {ticker} — Company not found on EDGAR. Skipping.", file=sys.stderr)
        return None, None
    except Exception as e:
        if not quiet:
            print(f"  {ticker} — EDGAR lookup failed: {e}", file=sys.stderr)
        return None, None

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
        if not filings or len(filings) == 0:
            if not quiet:
                print(f"  {ticker} — No filings found.", file=sys.stderr)
            return None, None

        latest = filings.latest()
        filing_metadata["form_type"] = latest.form
        filing_metadata["filing_date"] = str(latest.filing_date)
        filing_metadata["period_of_report"] = str(latest.period_of_report)
        filing_metadata["accession_no"] = latest.accession_no

        filing_obj = latest.obj()
        return filing_obj, filing_metadata

    except Exception as e:
        if not quiet:
            print(f"  {ticker} — Failed to get filing object: {e}", file=sys.stderr)
        return None, None
