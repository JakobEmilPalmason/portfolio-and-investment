#!/usr/bin/env python3
"""
Backfill iv_conservative / iv_base / iv_bull into existing FINAL-REPORT.json files
by parsing bear/base/bull scenario text from section 06 (valuation).

Usage:
    python3 scripts/backfill-iv.py                   # all reports
    python3 scripts/backfill-iv.py V MA MSFT          # specific tickers
    python3 scripts/backfill-iv.py --dry-run           # preview without writing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"

# Currency detection patterns
CURRENCY_PATTERNS = {
    "EUR": re.compile(r"€|EUR", re.IGNORECASE),
    "GBP": re.compile(r"£|GBP", re.IGNORECASE),
    "CAD": re.compile(r"CAD|C\$", re.IGNORECASE),
    "SEK": re.compile(r"SEK|kr", re.IGNORECASE),
    "DKK": re.compile(r"DKK", re.IGNORECASE),
    "NOK": re.compile(r"NOK", re.IGNORECASE),
}


def detect_currency(text: str) -> str:
    """Detect currency from valuation text. Default USD."""
    for code, pattern in CURRENCY_PATTERNS.items():
        if pattern.search(text):
            return code
    return "USD"


def extract_iv_from_table(text: str) -> dict:
    """Try to extract from the structured Intrinsic Value Summary table."""
    result = {}
    table_match = re.search(
        r"## Intrinsic Value Summary.*?\n(.*?)(?:\n##|\n---|\Z)",
        text,
        re.DOTALL,
    )
    if not table_match:
        return result

    table_text = table_match.group(1)
    for label, key in [
        ("IV Conservative", "iv_conservative"),
        ("IV Base", "iv_base"),
        ("IV Bull", "iv_bull"),
        ("Currency", "iv_currency"),
        ("MOS at Analysis", "mos_at_analysis"),
    ]:
        pattern = re.compile(
            rf"\|\s*{re.escape(label)}[^|]*\|\s*([^|]+)\|", re.IGNORECASE
        )
        m = pattern.search(table_text)
        if m:
            raw = m.group(1).strip()
            if key == "iv_currency":
                result[key] = raw if raw and raw.lower() != "null" else None
            else:
                num = parse_number(raw)
                if num is not None:
                    result[key] = num
    return result


def parse_number(s: str) -> float | None:
    """Strip non-numeric chars and parse as float."""
    if not s:
        return None
    cleaned = re.sub(r"[^\d.\-]", "", s.strip())
    if not cleaned:
        return None
    try:
        val = float(cleaned)
        # Sanity: per-share values should be positive and < 100,000
        if val <= 0 or val > 100_000:
            return None
        return round(val, 2)
    except ValueError:
        return None


def extract_iv_from_prose(text: str) -> dict:
    """
    Parse bear/base/bull discounted per-share values from scenario prose.

    Looks for patterns like:
      - "Discount at 9% → ~$182/share"
      - "~$264/share on a pure DCF basis"
      - "discounted at 9% → $302"
      - "~$382 discounted at 9%"
    """
    result = {}

    # Split into bear/base/bull sections
    sections = {
        "bear": _extract_scenario_section(text, "bear"),
        "base": _extract_scenario_section(text, "base"),
        "bull": _extract_scenario_section(text, "bull"),
    }

    key_map = {
        "bear": "iv_conservative",
        "base": "iv_base",
        "bull": "iv_bull",
    }

    for scenario, section_text in sections.items():
        if not section_text:
            continue
        value = _extract_discounted_value(section_text)
        if value is not None:
            result[key_map[scenario]] = value

    return result


def _extract_scenario_section(text: str, scenario: str) -> str | None:
    """Extract the text block for a given scenario (bear/base/bull)."""
    # Match patterns like "*Bear case:*", "**Bear case:**", "Bear case:", etc.
    pattern = re.compile(
        rf"[*_]*{scenario}\s+case[*_:]*\s*(.*?)(?=[*_]*(?:bear|base|bull)\s+case|## |\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _extract_discounted_value(text: str) -> float | None:
    """
    Find the discounted per-share value in a scenario block.
    Prioritizes "discount" context, falls back to last dollar figure.
    """
    # Pattern 1: "Discount at X% → ~$NNN/share" or "~$NNN discounted"
    discounted_patterns = [
        # "discount at 9% → ~$182/share"
        r"discount(?:ed)?\s+(?:at|by)\s+\d+%?\s*[→\-–—:]\s*~?\$?([\d,.]+)",
        # "~$302 discounted at 9%"
        r"~?\$?([\d,.]+)\s*(?:/share\s*)?discount(?:ed)?",
        # "→ ~$264/share on a pure DCF"
        r"[→\-–—]\s*~?\$?([\d,.]+)/share\b",
        # "yields ~$264–$302/share" — take the lower
        r"yields?\s+~?\$?([\d,.]+)(?:\s*[–\-]\s*\$?[\d,.]+)?/share",
    ]

    for pat in discounted_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = parse_number(m.group(1))
            if val is not None:
                return val

    # Fallback: find dollar amounts near "per share" or "/share"
    per_share = re.findall(r"\$?([\d,.]+)\s*/share", text)
    if per_share:
        # Take the last one (usually the final discounted figure)
        for candidate in reversed(per_share):
            val = parse_number(candidate)
            if val is not None:
                return val

    return None


def compute_mos(iv_conservative: float | None, current_price: float | None) -> float | None:
    """MOS = (IV - Price) / IV * 100. Positive = cheap."""
    if iv_conservative is None or current_price is None or iv_conservative <= 0:
        return None
    return round((iv_conservative - current_price) / iv_conservative * 100, 1)


def extract_current_price(report_json: dict, section_06_text: str) -> float | None:
    """Try to get current price from report JSON or section 06 text."""
    # Check valuation_summary in JSON
    vs = report_json.get("valuation_summary", "")
    if isinstance(vs, str):
        m = re.search(r"~?\$?([\d,.]+)/share", vs)
        if m:
            return parse_number(m.group(1))
        m = re.search(r"At\s+~?\$?([\d,.]+)", vs)
        if m:
            return parse_number(m.group(1))

    # Check section 06 for "current price"
    m = re.search(
        r"current\s+price\s+(?:of\s+)?~?\$?([\d,.]+)", section_06_text, re.IGNORECASE
    )
    if m:
        return parse_number(m.group(1))

    return None


def find_reports(tickers: list[str] | None) -> list[tuple[str, Path, Path]]:
    """Find (ticker, json_path, section06_path) tuples."""
    results = []
    report_dirs = sorted(RUNS_DIR.glob("*/reports/*/FINAL-REPORT.json"))

    # Group by ticker, keep latest
    latest: dict[str, tuple[Path, Path]] = {}
    for json_path in report_dirs:
        ticker = json_path.parent.name
        sec06 = json_path.parent / "06-valuation-intrinsic-value.md"
        if sec06.exists():
            if ticker not in latest or json_path.stat().st_mtime > latest[ticker][0].stat().st_mtime:
                latest[ticker] = (json_path, sec06)

    for ticker, (json_path, sec06) in sorted(latest.items()):
        if tickers and ticker not in tickers:
            continue
        results.append((ticker, json_path, sec06))

    return results


def backfill_one(
    ticker: str,
    json_path: Path,
    sec06_path: Path,
    dry_run: bool,
) -> dict:
    """Backfill IV for one ticker. Returns a status dict."""
    with open(json_path) as f:
        report = json.load(f)

    # Already populated?
    if report.get("iv_conservative") is not None and report.get("iv_base") is not None:
        return {"ticker": ticker, "status": "skip", "reason": "already populated"}

    sec06_text = sec06_path.read_text()

    # Try structured table first
    iv_data = extract_iv_from_table(sec06_text)

    # Fallback to prose parsing
    if "iv_conservative" not in iv_data or "iv_base" not in iv_data:
        prose_data = extract_iv_from_prose(sec06_text)
        for key in ("iv_conservative", "iv_base", "iv_bull"):
            if key not in iv_data and key in prose_data:
                iv_data[key] = prose_data[key]

    if not iv_data.get("iv_conservative") and not iv_data.get("iv_base"):
        return {"ticker": ticker, "status": "fail", "reason": "no IV numbers found in section 06"}

    # Currency
    if "iv_currency" not in iv_data:
        iv_data["iv_currency"] = detect_currency(sec06_text)

    # MOS
    current_price = extract_current_price(report, sec06_text)
    if iv_data.get("iv_conservative") and current_price:
        iv_data["mos_at_analysis"] = compute_mos(iv_data["iv_conservative"], current_price)

    # Patch
    for key in ("iv_conservative", "iv_base", "iv_bull", "iv_currency", "mos_at_analysis"):
        if key in iv_data:
            report[key] = iv_data[key]

    if not dry_run:
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return {
        "ticker": ticker,
        "status": "ok",
        "iv_conservative": iv_data.get("iv_conservative"),
        "iv_base": iv_data.get("iv_base"),
        "iv_bull": iv_data.get("iv_bull"),
        "iv_currency": iv_data.get("iv_currency"),
        "mos_at_analysis": iv_data.get("mos_at_analysis"),
        "price_used": current_price,
    }


def main():
    parser = argparse.ArgumentParser(description="Backfill IV into FINAL-REPORT.json")
    parser.add_argument("tickers", nargs="*", help="Specific tickers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing IV values")
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers] if args.tickers else None
    reports = find_reports(tickers)

    if not reports:
        print("No reports found.")
        sys.exit(1)

    print(f"{'DRY RUN — ' if args.dry_run else ''}Backfilling IV for {len(reports)} reports\n")

    ok = skip = fail = 0
    for ticker, json_path, sec06_path in reports:
        result = backfill_one(ticker, json_path, sec06_path, args.dry_run)

        if result["status"] == "skip" and not args.force:
            print(f"  {ticker:12s}  SKIP  (already has IV)")
            skip += 1
        elif result["status"] == "skip" and args.force:
            # Re-run with force
            with open(json_path) as f:
                report = json.load(f)
            report["iv_conservative"] = None
            report["iv_base"] = None
            if not args.dry_run:
                with open(json_path, "w") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                    f.write("\n")
            result = backfill_one(ticker, json_path, sec06_path, args.dry_run)
            if result["status"] == "ok":
                print(
                    f"  {ticker:12s}  OK    bear={result['iv_conservative']}  "
                    f"base={result['iv_base']}  bull={result.get('iv_bull')}  "
                    f"mos={result.get('mos_at_analysis')}%  ({result.get('iv_currency', 'USD')})"
                )
                ok += 1
            else:
                print(f"  {ticker:12s}  FAIL  {result.get('reason', '?')}")
                fail += 1
        elif result["status"] == "ok":
            print(
                f"  {ticker:12s}  OK    bear={result['iv_conservative']}  "
                f"base={result['iv_base']}  bull={result.get('iv_bull')}  "
                f"mos={result.get('mos_at_analysis')}%  ({result.get('iv_currency', 'USD')})"
            )
            ok += 1
        else:
            print(f"  {ticker:12s}  FAIL  {result.get('reason', '?')}")
            fail += 1

    print(f"\nDone: {ok} backfilled, {skip} skipped, {fail} failed")
    if args.dry_run:
        print("(dry run — no files were modified)")


if __name__ == "__main__":
    main()
