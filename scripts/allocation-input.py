#!/usr/bin/env python3
"""
allocation-input.py — Build the data blob that the AI allocator consumes.

Merges FINAL-REPORT.json + live prices from context/TICKER/financials.md +
portfolio state from SQLite into a single JSON written to stdout or a file.

Usage:
    python3 scripts/allocation-input.py                          # stdout
    python3 scripts/allocation-input.py --output portfolio/allocation-input.json
    python3 scripts/allocation-input.py --capital 250000
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"
CONTEXT_DIR = REPO_ROOT / "context"
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"
DB_PATH = REPO_ROOT / "db" / "portfolio.db"

TAG_SECTOR = {
    "healthcare": "Healthcare", "managed_care": "Healthcare", "glp1": "Healthcare",
    "pharma": "Healthcare", "medtech": "Healthcare", "diagnostics": "Healthcare",
    "biotech": "Healthcare", "technology": "Technology", "software": "Technology",
    "saas": "Technology", "cloud": "Technology", "semis": "Semiconductors",
    "semiconductors": "Semiconductors", "payments": "Financials",
    "financials": "Financials", "fintech": "Financials", "insurance": "Financials",
    "industrial": "Industrials", "industrials": "Industrials",
    "logistics": "Industrials", "shipping": "Industrials", "consumer": "Consumer",
    "luxury": "Consumer", "energy": "Energy",
}


def derive_sector(tags: list) -> str:
    for tag in tags:
        if tag in TAG_SECTOR:
            return TAG_SECTOR[tag]
    return "Other"


def load_queue() -> dict:
    """Return {TICKER: queue_entry}."""
    if not QUEUE_FILE.exists():
        return {}
    with open(QUEUE_FILE) as f:
        entries = json.load(f)
    return {e["ticker"]: e for e in entries if e.get("ticker")}


def load_reports() -> dict:
    """Return {TICKER: (report_dict, report_path)} for latest report per ticker.

    Deduplicates at two levels:
    1. Per ticker — keeps the newest report file by mtime.
    2. Per company — when multiple tickers map to the same company name
       (e.g. NOVO-B vs NOVO-B.CO), keeps only the newest.
    """
    all_reports = list(RUNS_DIR.glob("*/reports/*/FINAL-REPORT.json"))
    by_ticker = {}
    for p in all_reports:
        ticker = p.parent.name
        if ticker not in by_ticker or p.stat().st_mtime > by_ticker[ticker].stat().st_mtime:
            by_ticker[ticker] = p

    result = {}
    for ticker, path in by_ticker.items():
        try:
            with open(path) as f:
                result[ticker] = (json.load(f), path)
        except (json.JSONDecodeError, OSError):
            pass

    # Company-level dedup: group by normalized company name, keep newest
    by_company = {}  # normalized_name -> (ticker, mtime)
    for ticker, (report, path) in result.items():
        company = report.get("company", "").strip()
        if not company:
            continue
        norm = company.lower().rstrip(".").replace(",", "")
        mtime = path.stat().st_mtime
        if norm not in by_company or mtime > by_company[norm][1]:
            by_company[norm] = (ticker, mtime)

    # Build set of tickers to keep (winners of company dedup + those without a company name)
    keep = set()
    for norm, (ticker, _) in by_company.items():
        keep.add(ticker)
    for ticker, (report, _) in result.items():
        if not report.get("company", "").strip():
            keep.add(ticker)

    return {t: v for t, v in result.items() if t in keep}


def extract_current_price(ticker: str) -> tuple:
    """Extract current price and date from context/TICKER/financials.md.
    Returns (price, price_date, currency) or (None, None, None)."""
    fin_path = CONTEXT_DIR / ticker / "financials.md"
    if not fin_path.exists():
        return None, None, None

    try:
        text = fin_path.read_text()
    except OSError:
        return None, None, None

    price = None
    price_date = None
    currency = None

    # Table format: "| Current Price | $497.99 |" or "| Current Price | €166.44 |"
    # or "| Current Price | DKK 1,590.50 |" — handle all currency prefixes
    m = re.search(
        r"\|\s*Current Price\s*\|\s*(?:[$€£¥]|[A-Z]{2,3}\s?|kr\s?|C\$)?([\d,]+\.?\d*)",
        text,
    )
    if m:
        price = float(m.group(1).replace(",", ""))

    # Fallback: "Current Price: $XXX.XX"
    if price is None:
        m = re.search(
            r"Current Price[:\s]*(?:[$€£¥]|[A-Z]{2,3}\s?|kr\s?|C\$)?([\d,]+\.?\d*)",
            text,
        )
        if m:
            price = float(m.group(1).replace(",", ""))

    # Currency from "Reporting Currency: USD" or "Trading Currency: USD"
    m = re.search(r"(?:Reporting|Trading) Currency[:\s|]*(USD|EUR|DKK|GBP|SEK|NOK|CHF|CAD|JPY|GBp)", text)
    if m:
        currency = m.group(1)

    # Generated date: "**Generated:** 2026-03-15 22:33 UTC"
    m = re.search(r"\*\*Generated:\*\*\s*([\d-]+)", text)
    if m:
        price_date = m.group(1)

    return price, price_date, currency


def get_portfolio_state() -> dict:
    """Read portfolio state from SQLite."""
    state = {
        "total_capital": 100_000,
        "cash_available": 100_000,
        "positions": [],
        "sector_exposure": {},
        "initialized": False,
    }

    if not DB_PATH.exists():
        return state

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.database import Database
        from src.portfolio_engine import PortfolioEngine

        db = Database(str(DB_PATH))
        db.connect()
        db.init_db()
        engine = PortfolioEngine(db)
        portfolio = engine.load()
        summary = engine.get_summary()

        state["total_capital"] = summary.get("total_capital", 100_000)
        state["cash_available"] = summary.get("cash_position", state["total_capital"])
        state["initialized"] = summary.get("total_capital", 0) > 0

        for ticker, pos in portfolio.positions.items():
            if pos.status != "OPEN":
                continue
            state["positions"].append({
                "ticker": ticker,
                "side": pos.side,
                "shares": float(pos.shares),
                "cost_basis": float(pos.total_cost),
                "avg_price": float(pos.avg_cost_basis),
                "weight_pct": round(
                    float(pos.total_cost) / state["total_capital"] * 100, 2
                ) if state["total_capital"] else 0,
                "sector": pos.sector,
            })

        state["sector_exposure"] = summary.get("sector_weights", {})
    except Exception:
        pass

    return state


def build_candidates(reports: dict, queue: dict) -> list:
    """Build enriched candidate list."""
    today = date.today()
    candidates = []

    for ticker, (report, report_path) in sorted(reports.items()):
        verdict = report.get("verdict", "")
        if not verdict:
            continue

        # Analysis age
        analysis_date_str = report.get("analysis_date", "")
        age_days = None
        if analysis_date_str:
            try:
                age_days = (today - date.fromisoformat(analysis_date_str)).days
            except ValueError:
                pass

        # Live price
        current_price, price_date, price_currency = extract_current_price(ticker)

        # IV data
        iv_conservative = report.get("iv_conservative")
        iv_base = report.get("iv_base")
        iv_bull = report.get("iv_bull")
        iv_currency = report.get("iv_currency")

        # Compute live MOS and asymmetry
        live_mos_pct = None
        upside_downside_ratio = None
        if current_price and iv_conservative:
            live_mos_pct = round((iv_conservative - current_price) / iv_conservative * 100, 2)
            if iv_base and current_price > iv_conservative:
                upside = iv_base - current_price
                downside = current_price - iv_conservative
                if downside > 0:
                    upside_downside_ratio = round(upside / downside, 2)

        # Queue data
        qe = queue.get(ticker, {})
        sector = derive_sector(qe.get("tags", []))

        candidates.append({
            "ticker": ticker,
            "company": report.get("company", ""),
            "verdict": verdict,
            "confidence": report.get("confidence", ""),
            "average_score": report.get("average_score"),
            "umbrella_scores": report.get("umbrella_scores", {}),
            "iv_conservative": iv_conservative,
            "iv_base": iv_base,
            "iv_bull": iv_bull,
            "iv_currency": iv_currency,
            "current_price": current_price,
            "price_date": price_date,
            "price_currency": price_currency,
            "live_mos_pct": live_mos_pct,
            "upside_downside_ratio": upside_downside_ratio,
            "key_strengths": report.get("key_strengths", []),
            "key_risks": report.get("key_risks", []),
            "red_flags": report.get("red_flags", []),
            "buy_triggers": report.get("buy_triggers", []),
            "sell_triggers": report.get("sell_triggers", []),
            "valuation_summary": report.get("valuation_summary", ""),
            "analysis_date": analysis_date_str,
            "analysis_age_days": age_days,
            "sector": sector,
            "queue_state": qe.get("current_state", ""),
            "queue_tags": qe.get("tags", []),
        })

    return candidates


def main():
    parser = argparse.ArgumentParser(
        description="Build allocation input blob for AI allocator."
    )
    parser.add_argument("--output", type=str, help="Write to file (default: stdout)")
    parser.add_argument("--capital", type=float, help="Override capital base")
    args = parser.parse_args()

    reports = load_reports()
    queue = load_queue()
    portfolio_state = get_portfolio_state()

    if args.capital:
        portfolio_state["total_capital"] = args.capital
        if not portfolio_state["positions"]:
            portfolio_state["cash_available"] = args.capital

    candidates = build_candidates(reports, queue)

    blob = {
        "generated_at": datetime.now().isoformat(),
        "capital": portfolio_state["total_capital"],
        "portfolio_state": portfolio_state,
        "candidates": candidates,
        "summary": {
            "total_candidates": len(candidates),
            "by_verdict": {},
            "with_live_price": sum(1 for c in candidates if c["current_price"]),
            "with_positive_mos": sum(
                1 for c in candidates
                if c["live_mos_pct"] is not None and c["live_mos_pct"] > 0
            ),
        },
    }

    # Verdict counts
    for c in candidates:
        v = c["verdict"]
        blob["summary"]["by_verdict"][v] = blob["summary"]["by_verdict"].get(v, 0) + 1

    output = json.dumps(blob, indent=2)

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n")
        print(f"Allocation input written to: {out_path}", file=sys.stderr)
        print(f"  {len(candidates)} candidates, "
              f"{blob['summary']['with_live_price']} with live prices, "
              f"{blob['summary']['with_positive_mos']} with positive MOS",
              file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
