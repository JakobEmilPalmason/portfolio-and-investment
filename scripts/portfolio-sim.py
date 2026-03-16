#!/usr/bin/env python3
"""
portfolio-sim.py — Simple portfolio simulator.

Given $X starting capital and the pipeline's own ranking logic, shows what
"follow the system" looks like: holdings, sector exposure, concentration.

NOT a backtest. Pure snapshot allocation from current queue + report data.

Usage:
    python3 scripts/portfolio-sim.py
    python3 scripts/portfolio-sim.py --capital 250000
    python3 scripts/portfolio-sim.py --capital 500000 --min-verdict watch --top 15
    python3 scripts/portfolio-sim.py --output json | jq .concentration
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"
RUNS_DIR = REPO_ROOT / "runs"

VERDICT_RANK = {"Own": 2, "Watch": 1, "Pass": 0}
CONFIDENCE_RANK = {"high": 2, "medium": 1, "low": 0}

# Tag → sector mapping (first matching tag wins)
TAG_SECTOR = {
    "healthcare": "Healthcare",
    "managed_care": "Healthcare",
    "glp1": "Healthcare",
    "pharma": "Healthcare",
    "medtech": "Healthcare",
    "diagnostics": "Healthcare",
    "biotech": "Healthcare",
    "technology": "Technology",
    "software": "Technology",
    "saas": "Technology",
    "cloud": "Technology",
    "semis": "Semiconductors",
    "semiconductors": "Semiconductors",
    "payments": "Financials",
    "financials": "Financials",
    "fintech": "Financials",
    "insurance": "Financials",
    "industrial": "Industrials",
    "industrials": "Industrials",
    "logistics": "Industrials",
    "shipping": "Industrials",
    "consumer": "Consumer",
    "luxury": "Consumer",
    "energy": "Energy",
}


def derive_sector(tags: list) -> str:
    for tag in tags:
        if tag in TAG_SECTOR:
            return TAG_SECTOR[tag]
    return "Other"


def load_queue() -> list:
    with open(QUEUE_FILE) as f:
        return json.load(f)


def load_report(ticker: str) -> dict | None:
    candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def fmt_money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def build_candidates(
    allowed_states: list[str],
    min_verdict: str,
) -> tuple[list[dict], list[str]]:
    """Return (candidates, skipped_tickers)."""
    queue = load_queue()
    min_rank = VERDICT_RANK.get(min_verdict.capitalize(), 2)

    candidates = []
    skipped = []

    for entry in queue:
        ticker = entry.get("ticker", "")
        state = entry.get("current_state", "")
        verdict = entry.get("current_verdict") or ""

        if state not in allowed_states:
            continue
        if VERDICT_RANK.get(verdict, -1) < min_rank:
            continue

        report = load_report(ticker)
        if report is None:
            skipped.append(ticker)
            continue

        candidates.append(
            {
                "ticker": ticker,
                "company": entry.get("company", ""),
                "verdict": verdict,
                "verdict_rank": VERDICT_RANK.get(verdict, 0),
                "average_score": report.get("average_score", 0.0),
                "confidence": report.get("confidence", "low"),
                "confidence_rank": CONFIDENCE_RANK.get(
                    report.get("confidence", "low"), 0
                ),
                "red_flag_count": len(report.get("red_flags", [])),
                "sector": derive_sector(entry.get("tags", [])),
                "analysis_date": report.get("analysis_date", ""),
                "umbrella_scores": report.get("umbrella_scores", {}),
            }
        )

    # Sort: verdict desc, then score desc, then confidence desc
    candidates.sort(
        key=lambda x: (x["verdict_rank"], x["average_score"], x["confidence_rank"]),
        reverse=True,
    )
    return candidates, skipped


def compute_concentration(positions: list[dict]) -> dict:
    n = len(positions)
    if n == 0:
        return {}
    weights = [p["weight_pct"] for p in positions]
    top1 = weights[0] if n >= 1 else 0.0
    top3 = sum(weights[:3]) if n >= 3 else sum(weights)
    top5 = sum(weights[:5]) if n >= 5 else sum(weights)
    hhi = sum((w / 100) ** 2 for w in weights) * 10_000
    red_flags = sum(p["red_flag_count"] for p in positions)
    return {
        "positions": n,
        "top_1_pct": round(top1, 1),
        "top_3_pct": round(top3, 1),
        "top_5_pct": round(top5, 1),
        "hhi": round(hhi),
        "red_flags_total": red_flags,
    }


def compute_sector_exposure(positions: list[dict], capital: float) -> list[dict]:
    sectors: dict[str, dict] = {}
    for p in positions:
        s = p["sector"]
        if s not in sectors:
            sectors[s] = {"sector": s, "names": 0, "value": 0.0}
        sectors[s]["names"] += 1
        sectors[s]["value"] += p["position_value"]
    result = []
    for s, data in sectors.items():
        result.append(
            {
                "sector": s,
                "names": data["names"],
                "weight_pct": round(data["value"] / capital * 100, 1),
                "value": data["value"],
            }
        )
    result.sort(key=lambda x: x["value"], reverse=True)
    return result


def print_table(rows: list[list], headers: list[str], col_widths: list[int]) -> None:
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    sep = "  ".join("-" * w for w in col_widths)
    print(header_line)
    print(sep)
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))


def output_table(
    positions: list[dict],
    sector_exposure: list[dict],
    concentration: dict,
    capital: float,
    skipped: list[str],
) -> None:
    print(f"\n{'='*72}")
    print(f"  PORTFOLIO SIMULATOR  —  Capital: {fmt_money(capital)}")
    print(f"{'='*72}")

    # Holdings
    print("\n── Holdings ─────────────────────────────────────────────────────────")
    headers = ["Rank", "Ticker", "Company", "Verdict", "Score", "Conf", "Weight", "Value"]
    col_widths = [4, 10, 28, 7, 5, 6, 7, 9]
    rows = []
    for i, p in enumerate(positions, 1):
        rows.append(
            [
                i,
                p["ticker"],
                p["company"][:27],
                p["verdict"],
                f"{p['average_score']:.1f}",
                p["confidence"],
                f"{p['weight_pct']:.1f}%",
                fmt_money(p["position_value"]),
            ]
        )
    print_table(rows, headers, col_widths)

    # Sector exposure
    print("\n── Sector Exposure ──────────────────────────────────────────────────")
    headers = ["Sector", "Names", "Weight", "Value"]
    col_widths = [20, 5, 8, 10]
    rows = []
    for s in sector_exposure:
        rows.append(
            [
                s["sector"],
                s["names"],
                f"{s['weight_pct']:.1f}%",
                fmt_money(s["value"]),
            ]
        )
    print_table(rows, headers, col_widths)

    # Concentration
    print("\n── Concentration ────────────────────────────────────────────────────")
    c = concentration
    print(f"  Positions:     {c['positions']}")
    print(f"  Top 1 name:    {c['top_1_pct']:.1f}%")
    print(f"  Top 3 names:   {c['top_3_pct']:.1f}%")
    print(f"  Top 5 names:   {c['top_5_pct']:.1f}%")
    print(
        f"  HHI:           {c['hhi']}  "
        "(0=perfect spread, 10000=single name)"
    )
    print(f"  Red flags:     {c['red_flags_total']}  (across all positions)")

    # Confidence breakdown
    conf_counts = {"high": 0, "medium": 0, "low": 0}
    for p in positions:
        conf_counts[p["confidence"]] = conf_counts.get(p["confidence"], 0) + 1
    print(
        f"\n  Confidence mix: {conf_counts['high']} high  "
        f"{conf_counts['medium']} medium  {conf_counts['low']} low"
    )

    if skipped:
        print(
            f"\n  NOTE: {len(skipped)} eligible ticker(s) skipped — missing FINAL-REPORT.json:"
        )
        print(f"  {', '.join(skipped)}")

    print(f"\n{'='*72}\n")


def output_json(
    positions: list[dict],
    sector_exposure: list[dict],
    concentration: dict,
    capital: float,
    skipped: list[str],
) -> None:
    out = {
        "capital": capital,
        "portfolio": [
            {
                "rank": i + 1,
                "ticker": p["ticker"],
                "company": p["company"],
                "verdict": p["verdict"],
                "average_score": p["average_score"],
                "confidence": p["confidence"],
                "sector": p["sector"],
                "weight_pct": p["weight_pct"],
                "position_value": p["position_value"],
                "red_flag_count": p["red_flag_count"],
                "analysis_date": p["analysis_date"],
            }
            for i, p in enumerate(positions)
        ],
        "sector_exposure": sector_exposure,
        "concentration": concentration,
        "skipped_no_report": skipped,
    }
    print(json.dumps(out, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Portfolio simulator — deploy capital into top-ranked pipeline names."
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=100_000,
        metavar="X",
        help="Starting capital in dollars (default: 100000)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        metavar="N",
        help="Max positions (default: 20; 0 = all eligible)",
    )
    parser.add_argument(
        "--min-verdict",
        default="own",
        choices=["own", "watch"],
        help="Minimum verdict tier to include (default: own)",
    )
    parser.add_argument(
        "--states",
        default="monitor_only,approved,owned",
        help="Comma-separated queue states to include "
        "(default: monitor_only,approved,owned)",
    )
    parser.add_argument(
        "--output",
        default="table",
        choices=["table", "json"],
        help="Output format (default: table)",
    )
    args = parser.parse_args()

    allowed_states = [s.strip() for s in args.states.split(",")]
    min_verdict = args.min_verdict.capitalize()  # "own" → "Own"
    if min_verdict == "Own":
        min_verdict = "Own"
    elif min_verdict == "Watch":
        min_verdict = "Watch"

    candidates, skipped = build_candidates(allowed_states, min_verdict)

    if not candidates:
        print(
            f"No eligible candidates found (states={allowed_states}, "
            f"min_verdict={min_verdict}).",
            file=sys.stderr,
        )
        sys.exit(1)

    top_n = args.top if args.top > 0 else len(candidates)
    selected = candidates[:top_n]

    capital = args.capital
    position_value = capital / len(selected)
    weight_pct = 100.0 / len(selected)

    positions = [
        {**c, "position_value": position_value, "weight_pct": weight_pct}
        for c in selected
    ]

    sector_exposure = compute_sector_exposure(positions, capital)
    concentration = compute_concentration(positions)

    if args.output == "json":
        output_json(positions, sector_exposure, concentration, capital, skipped)
    else:
        output_table(positions, sector_exposure, concentration, capital, skipped)

    # Save to SQLite
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from datetime import datetime
        from src.database import Database
        with Database() as db:
            db.migrate()
            db.insert_sim_run({
                "run_at": datetime.now().isoformat(),
                "capital": capital,
                "min_verdict": min_verdict,
                "top_n": top_n,
                "allowed_states": ",".join(allowed_states),
                "total_positions": len(positions),
                "positions_json": [
                    {
                        "ticker": p["ticker"],
                        "company": p.get("company", ""),
                        "verdict": p.get("verdict", ""),
                        "average_score": p.get("average_score"),
                        "confidence": p.get("confidence", ""),
                        "sector": p.get("sector", ""),
                        "weight_pct": p.get("weight_pct"),
                        "position_value": p.get("position_value"),
                        "red_flag_count": p.get("red_flag_count", 0),
                        "analysis_date": p.get("analysis_date", ""),
                    }
                    for p in positions
                ],
                "sector_exposure_json": sector_exposure,
                "concentration_json": concentration,
                "skipped_json": skipped,
            })
    except Exception:
        pass


if __name__ == "__main__":
    main()
