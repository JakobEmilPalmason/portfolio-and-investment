#!/usr/bin/env python3
"""
portfolio-ledger.py — Persistent portfolio tracking with policy compliance.

Tracks positions, transactions, and portfolio-level summary. Enforces
investment policy rules on every trade. Renders human-readable state.

Usage:
    python3 scripts/portfolio-ledger.py init --capital 100000
    python3 scripts/portfolio-ledger.py buy V --price 312.50 --amount 3000 --iv 380
    python3 scripts/portfolio-ledger.py sell V --price 340.00 --shares 5
    python3 scripts/portfolio-ledger.py short CAT --price 705 --shares 10 --iv 272
    python3 scripts/portfolio-ledger.py cover CAT --price 600 --shares 10
    python3 scripts/portfolio-ledger.py status
    python3 scripts/portfolio-ledger.py refresh
    python3 scripts/portfolio-ledger.py bootstrap FILE --capital 100000 --prices FILE
    python3 scripts/portfolio-ledger.py history
    python3 scripts/portfolio-ledger.py check buy V --price 312.50 --amount 3000
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_FILE = REPO_ROOT / "portfolio" / "ledger.json"
STATE_MD = REPO_ROOT / "portfolio" / "portfolio-state.md"
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"
RUNS_DIR = REPO_ROOT / "runs"

# ---------------------------------------------------------------------------
# Policy thresholds
# ---------------------------------------------------------------------------
POLICY = {
    "single_name_hard_pct": 7.0,
    "single_name_warn_pct": 5.0,
    "sector_gross_hard_pct": 35.0,
    "gross_exposure_hard_pct": 130.0,
    "net_exposure_max_pct": 100.0,
    "net_exposure_min_pct": -30.0,
    "minimum_breadth": 5,
    "stale_analysis_days": 180,
}

# ---------------------------------------------------------------------------
# Reused from portfolio-sim.py (standalone scripts, no cross-imports)
# ---------------------------------------------------------------------------
VERDICT_RANK = {"Own": 2, "Watch": 1, "Pass": 0}
CONFIDENCE_RANK = {"high": 2, "medium": 1, "low": 0}

TAG_SECTOR = {
    "healthcare": "Healthcare", "managed_care": "Healthcare",
    "glp1": "Healthcare", "pharma": "Healthcare", "medtech": "Healthcare",
    "diagnostics": "Healthcare", "biotech": "Healthcare",
    "technology": "Technology", "software": "Technology",
    "saas": "Technology", "cloud": "Technology",
    "semis": "Semiconductors", "semiconductors": "Semiconductors",
    "payments": "Financials", "financials": "Financials",
    "fintech": "Financials", "insurance": "Financials",
    "industrial": "Industrials", "industrials": "Industrials",
    "logistics": "Industrials", "shipping": "Industrials",
    "consumer": "Consumer", "luxury": "Consumer",
    "energy": "Energy",
}


def derive_sector(tags: list) -> str:
    for tag in tags:
        if tag in TAG_SECTOR:
            return TAG_SECTOR[tag]
    return "Other"


def find_report(ticker: str) -> dict | None:
    candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def find_report_ref(ticker: str) -> str | None:
    candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        return str(latest.relative_to(REPO_ROOT))
    except ValueError:
        return str(latest)


def load_queue() -> list:
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE) as f:
        return json.load(f)


def queue_entry(ticker: str) -> dict | None:
    for entry in load_queue():
        if entry.get("ticker") == ticker:
            return entry
    return None


def fmt_money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Ledger I/O
# ---------------------------------------------------------------------------
def load_ledger() -> dict:
    if not LEDGER_FILE.exists():
        print(f"ERROR: Ledger not found at {LEDGER_FILE}", file=sys.stderr)
        print("Run: portfolio-ledger.py init --capital <amount>", file=sys.stderr)
        sys.exit(1)
    with open(LEDGER_FILE) as f:
        return json.load(f)


def save_ledger(ledger: dict) -> None:
    ledger["metadata"]["last_updated"] = now_iso()
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=LEDGER_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(ledger, f, indent=2)
            f.write("\n")
        os.rename(tmp, LEDGER_FILE)
    except Exception:
        os.unlink(tmp)
        raise


def next_tx_id(ledger: dict) -> int:
    txns = ledger.get("transactions", [])
    if not txns:
        return 1
    return max(t.get("id", 0) for t in txns) + 1


# ---------------------------------------------------------------------------
# Summary recomputation
# ---------------------------------------------------------------------------
def recompute_summary(ledger: dict) -> None:
    positions = ledger["positions"]
    meta = ledger["metadata"]
    total_capital = meta["initial_capital"] + ledger.get("summary", {}).get("realized_pnl", 0.0)

    deployed_long = sum(p["cost_basis_total"] for p in positions if p["side"] == "long")
    deployed_short = sum(p["cost_basis_total"] for p in positions if p["side"] == "short")
    gross = deployed_long + deployed_short
    net = deployed_long - deployed_short
    cash = total_capital - deployed_long

    long_count = sum(1 for p in positions if p["side"] == "long")
    short_count = sum(1 for p in positions if p["side"] == "short")

    # Sector weights
    sector_data: dict[str, dict] = {}
    for p in positions:
        s = p.get("sector", "Other")
        if s not in sector_data:
            sector_data[s] = {"long": 0.0, "short": 0.0, "names": 0}
        sector_data[s]["names"] += 1
        if p["side"] == "long":
            sector_data[s]["long"] += p["cost_basis_total"]
        else:
            sector_data[s]["short"] += p["cost_basis_total"]

    sector_weights = {}
    for s, d in sector_data.items():
        sector_weights[s] = {
            "gross_pct": round((d["long"] + d["short"]) / total_capital * 100, 1) if total_capital else 0,
            "long_pct": round(d["long"] / total_capital * 100, 1) if total_capital else 0,
            "short_pct": round(d["short"] / total_capital * 100, 1) if total_capital else 0,
            "names": d["names"],
        }

    # Largest position
    largest_pct = 0.0
    largest_ticker = ""
    for p in positions:
        w = p["cost_basis_total"] / total_capital * 100 if total_capital else 0
        if w > largest_pct:
            largest_pct = w
            largest_ticker = p["ticker"]

    realized_pnl = ledger.get("summary", {}).get("realized_pnl", 0.0)

    ledger["summary"] = {
        "as_of": today_str(),
        "initial_capital": meta["initial_capital"],
        "total_capital": total_capital,
        "deployed_long": round(deployed_long, 2),
        "deployed_short": round(deployed_short, 2),
        "gross_exposure": round(gross, 2),
        "gross_exposure_pct": round(gross / total_capital * 100, 1) if total_capital else 0,
        "net_exposure": round(net, 2),
        "net_exposure_pct": round(net / total_capital * 100, 1) if total_capital else 0,
        "cash_position": round(cash, 2),
        "cash_pct": round(cash / total_capital * 100, 1) if total_capital else 0,
        "position_count": len(positions),
        "long_count": long_count,
        "short_count": short_count,
        "realized_pnl": round(realized_pnl, 2),
        "sector_weights": sector_weights,
        "largest_position_pct": round(largest_pct, 1),
        "largest_position_ticker": largest_ticker,
    }

    # Update policy flags on each position
    for p in positions:
        flags = []
        w = p["cost_basis_total"] / total_capital * 100 if total_capital else 0
        if w > POLICY["single_name_hard_pct"]:
            flags.append(f"overweight:{w:.1f}%")
        p["policy_flags"] = flags


# ---------------------------------------------------------------------------
# Policy checking
# ---------------------------------------------------------------------------
def check_policy(
    ledger: dict,
    action: str,
    ticker: str,
    side: str,
    trade_value: float,
    iv: float | None = None,
    price: float | None = None,
    force: bool = False,
) -> tuple[list[dict], bool]:
    """Return (violations, should_block). Violations have rule/severity/message."""
    violations = []
    positions = ledger["positions"]
    summary = ledger.get("summary", {})
    total_capital = summary.get("total_capital", ledger["metadata"]["initial_capital"])

    # Existing position value for this ticker
    existing = next((p for p in positions if p["ticker"] == ticker and p["side"] == side), None)
    existing_value = existing["cost_basis_total"] if existing else 0.0

    # Post-trade values
    new_position_value = existing_value + trade_value
    new_position_pct = new_position_value / total_capital * 100 if total_capital else 0

    deployed_long = summary.get("deployed_long", 0.0)
    deployed_short = summary.get("deployed_short", 0.0)
    if side == "long":
        new_deployed_long = deployed_long + trade_value
        new_deployed_short = deployed_short
    else:
        new_deployed_long = deployed_long
        new_deployed_short = deployed_short + trade_value

    new_gross = new_deployed_long + new_deployed_short
    new_gross_pct = new_gross / total_capital * 100 if total_capital else 0
    new_net = new_deployed_long - new_deployed_short
    new_net_pct = new_net / total_capital * 100 if total_capital else 0

    # Single name hard limit
    if new_position_pct > POLICY["single_name_hard_pct"]:
        violations.append({
            "rule": "single_name_weight",
            "severity": "hard",
            "message": f"{ticker} would be {new_position_pct:.1f}% of portfolio "
                       f"(hard limit: {POLICY['single_name_hard_pct']}%)",
        })

    # Single name soft warning
    elif new_position_pct > POLICY["single_name_warn_pct"]:
        violations.append({
            "rule": "single_name_weight_warn",
            "severity": "soft",
            "message": f"{ticker} would be {new_position_pct:.1f}% of portfolio "
                       f"(warning at {POLICY['single_name_warn_pct']}%)",
        })

    # Sector gross limit
    sector = "Other"
    qe = queue_entry(ticker)
    if qe:
        sector = derive_sector(qe.get("tags", []))
    elif existing:
        sector = existing.get("sector", "Other")
    sector_current = summary.get("sector_weights", {}).get(sector, {}).get("gross_pct", 0.0)
    sector_add_pct = trade_value / total_capital * 100 if total_capital else 0
    if sector_current + sector_add_pct > POLICY["sector_gross_hard_pct"]:
        violations.append({
            "rule": "sector_gross_weight",
            "severity": "hard",
            "message": f"Sector '{sector}' would be {sector_current + sector_add_pct:.1f}% gross "
                       f"(hard limit: {POLICY['sector_gross_hard_pct']}%)",
        })

    # Gross exposure
    if new_gross_pct > POLICY["gross_exposure_hard_pct"]:
        violations.append({
            "rule": "gross_exposure",
            "severity": "hard",
            "message": f"Gross exposure would be {new_gross_pct:.1f}% "
                       f"(hard limit: {POLICY['gross_exposure_hard_pct']}%)",
        })

    # Net exposure bounds
    if new_net_pct > POLICY["net_exposure_max_pct"]:
        violations.append({
            "rule": "net_exposure_max",
            "severity": "hard",
            "message": f"Net exposure would be {new_net_pct:.1f}% "
                       f"(hard limit: {POLICY['net_exposure_max_pct']}%)",
        })
    if new_net_pct < POLICY["net_exposure_min_pct"]:
        violations.append({
            "rule": "net_exposure_min",
            "severity": "hard",
            "message": f"Net exposure would be {new_net_pct:.1f}% "
                       f"(hard limit: {POLICY['net_exposure_min_pct']}%)",
        })

    # Verdict mismatch (only for buy/short, not sell/cover)
    if action in ("buy", "short"):
        report = find_report(ticker)
        if report:
            verdict = report.get("verdict", "")
            if verdict == "Pass" and side == "long":
                violations.append({
                    "rule": "verdict_mismatch",
                    "severity": "hard",
                    "message": f"{ticker} has Pass verdict — cannot buy",
                })
            # Check stale analysis
            analysis_date = report.get("analysis_date", "")
            if analysis_date:
                try:
                    days_old = (datetime.now() - datetime.strptime(analysis_date, "%Y-%m-%d")).days
                    if days_old > POLICY["stale_analysis_days"]:
                        violations.append({
                            "rule": "stale_analysis",
                            "severity": "soft",
                            "message": f"{ticker} analysis is {days_old} days old "
                                       f"(warning at {POLICY['stale_analysis_days']})",
                        })
                except ValueError:
                    pass
        else:
            violations.append({
                "rule": "no_report",
                "severity": "soft",
                "message": f"No FINAL-REPORT.json found for {ticker}",
            })

        # Thesis break
        if qe and qe.get("thesis_status") in ("weakened", "changed"):
            violations.append({
                "rule": "thesis_break",
                "severity": "hard",
                "message": f"{ticker} thesis_status is '{qe['thesis_status']}' — cannot buy",
            })

        # Margin of safety (long buys only)
        if side == "long" and iv is not None and price is not None and iv > 0:
            mos = (iv - price) / iv * 100
            if mos < 0:
                violations.append({
                    "rule": "margin_of_safety",
                    "severity": "soft",
                    "message": f"{ticker} price ${price:.2f} exceeds IV estimate ${iv:.2f} "
                               f"(MOS: {mos:.1f}%)",
                })

    # Minimum breadth (only relevant for sells that reduce position count)
    if action in ("sell", "cover"):
        pos = next((p for p in positions if p["ticker"] == ticker and p["side"] == side), None)
        if pos:
            remaining_count = len(positions) - 1  # assuming full close
            if remaining_count < POLICY["minimum_breadth"]:
                violations.append({
                    "rule": "minimum_breadth",
                    "severity": "soft",
                    "message": f"Portfolio would have {remaining_count} positions "
                               f"(warning at {POLICY['minimum_breadth']})",
                })

    # Determine if we should block
    hard_violations = [v for v in violations if v["severity"] == "hard"]
    soft_violations = [v for v in violations if v["severity"] == "soft"]
    should_block = bool(hard_violations) or (bool(soft_violations) and not force)

    return violations, should_block


def print_violations(violations: list[dict]) -> None:
    for v in violations:
        severity_label = "BLOCKED" if v["severity"] == "hard" else "WARNING"
        print(f"  [{severity_label}] {v['rule']}: {v['message']}")


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------
def render_markdown(ledger: dict) -> None:
    s = ledger["summary"]
    positions = ledger["positions"]
    transactions = ledger["transactions"]

    lines = []
    lines.append("# Portfolio State")
    lines.append(f"_Last updated: {ledger['metadata']['last_updated']}_")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Capital | {fmt_money(s['total_capital'])} |")
    lines.append(f"| Deployed (Long) | {fmt_money(s['deployed_long'])} ({s['deployed_long'] / s['total_capital'] * 100:.1f}%) |" if s['total_capital'] else "| Deployed (Long) | $0 |")
    lines.append(f"| Deployed (Short) | {fmt_money(s['deployed_short'])} ({s['deployed_short'] / s['total_capital'] * 100:.1f}%) |" if s['total_capital'] else "| Deployed (Short) | $0 |")
    lines.append(f"| Gross Exposure | {fmt_money(s['gross_exposure'])} ({s['gross_exposure_pct']}%) |")
    lines.append(f"| Net Exposure | {fmt_money(s['net_exposure'])} ({s['net_exposure_pct']}%) |")
    lines.append(f"| Cash | {fmt_money(s['cash_position'])} ({s['cash_pct']}%) |")
    lines.append(f"| Positions | {s['position_count']} ({s['long_count']} long, {s['short_count']} short) |")
    lines.append(f"| Realized P&L | {fmt_money(s['realized_pnl'])} |")
    lines.append("")

    # Long positions
    longs = [p for p in positions if p["side"] == "long"]
    if longs:
        longs.sort(key=lambda p: p["cost_basis_total"], reverse=True)
        lines.append("## Long Positions")
        lines.append("")
        lines.append("| Ticker | Company | Weight | Entry | Current | P&L | MOS | Verdict | Score |")
        lines.append("|--------|---------|--------|-------|---------|-----|-----|---------|-------|")
        for p in longs:
            w = p["cost_basis_total"] / s["total_capital"] * 100 if s["total_capital"] else 0
            current = f"${p['current_price']:.2f}" if p["current_price"] else "\u2014"
            pnl = f"{fmt_money(p['unrealized_pnl'])}" if p["unrealized_pnl"] is not None else "\u2014"
            mos = f"{p['margin_of_safety_at_entry_pct']:.1f}%" if p["margin_of_safety_at_entry_pct"] is not None else "\u2014"
            lines.append(
                f"| {p['ticker']} | {p.get('company', '')[:25]} | {w:.1f}% "
                f"| ${p['entry_price']:.2f} | {current} | {pnl} | {mos} "
                f"| {p.get('verdict_at_entry', '')} | {p.get('score_at_entry', '')} |"
            )
        lines.append("")

    # Short positions
    shorts = [p for p in positions if p["side"] == "short"]
    if shorts:
        shorts.sort(key=lambda p: p["cost_basis_total"], reverse=True)
        lines.append("## Short Positions")
        lines.append("")
        lines.append("| Ticker | Company | Weight | Entry | Current | P&L | Verdict | Score |")
        lines.append("|--------|---------|--------|-------|---------|-----|---------|-------|")
        for p in shorts:
            w = p["cost_basis_total"] / s["total_capital"] * 100 if s["total_capital"] else 0
            current = f"${p['current_price']:.2f}" if p["current_price"] else "\u2014"
            pnl = f"{fmt_money(p['unrealized_pnl'])}" if p["unrealized_pnl"] is not None else "\u2014"
            lines.append(
                f"| {p['ticker']} | {p.get('company', '')[:25]} | {w:.1f}% "
                f"| ${p['entry_price']:.2f} | {current} | {pnl} "
                f"| {p.get('verdict_at_entry', '')} | {p.get('score_at_entry', '')} |"
            )
        lines.append("")

    # Sector exposure
    sw = s.get("sector_weights", {})
    if sw:
        lines.append("## Sector Exposure")
        lines.append("")
        lines.append("| Sector | Gross | Long | Short | Names |")
        lines.append("|--------|-------|------|-------|-------|")
        for sector in sorted(sw, key=lambda k: sw[k]["gross_pct"], reverse=True):
            d = sw[sector]
            lines.append(f"| {sector} | {d['gross_pct']}% | {d['long_pct']}% | {d['short_pct']}% | {d['names']} |")
        lines.append("")

    # Policy status
    lines.append("## Policy Status")
    lines.append("")
    flagged = [p for p in positions if p.get("policy_flags")]
    if flagged:
        for p in flagged:
            for flag in p["policy_flags"]:
                lines.append(f"- **{p['ticker']}**: {flag}")
    else:
        lines.append("All positions within policy limits.")
    lines.append("")

    # Recent transactions
    if transactions:
        lines.append("## Recent Transactions")
        lines.append("")
        lines.append("| Date | Ticker | Action | Price | Shares | Value | Reason |")
        lines.append("|------|--------|--------|-------|--------|-------|--------|")
        for t in transactions[-20:]:
            lines.append(
                f"| {t['date']} | {t['ticker']} | {t['action']} "
                f"| ${t['price']:.2f} | {t['shares']:.4g} | {fmt_money(t['value'])} "
                f"| {t.get('reason', '')[:40]} |"
            )
        lines.append("")

    STATE_MD.parent.mkdir(parents=True, exist_ok=True)
    STATE_MD.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Print helpers
# ---------------------------------------------------------------------------
def print_table(rows: list[list], headers: list[str], col_widths: list[int]) -> None:
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    sep = "  ".join("-" * w for w in col_widths)
    print(header_line)
    print(sep)
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))


def print_status(ledger: dict, output_fmt: str = "table") -> None:
    s = ledger["summary"]
    positions = ledger["positions"]

    if output_fmt == "json":
        print(json.dumps(ledger, indent=2))
        return

    print(f"\n{'='*72}")
    print(f"  PORTFOLIO LEDGER  —  Capital: {fmt_money(s['total_capital'])}")
    print(f"{'='*72}")

    print(f"\n  Deployed (Long):  {fmt_money(s['deployed_long'])} ({s['deployed_long'] / s['total_capital'] * 100:.1f}%)" if s['total_capital'] else "")
    print(f"  Deployed (Short): {fmt_money(s['deployed_short'])} ({s['deployed_short'] / s['total_capital'] * 100:.1f}%)" if s['total_capital'] else "")
    print(f"  Gross Exposure:   {fmt_money(s['gross_exposure'])} ({s['gross_exposure_pct']}%)")
    print(f"  Net Exposure:     {fmt_money(s['net_exposure'])} ({s['net_exposure_pct']}%)")
    print(f"  Cash:             {fmt_money(s['cash_position'])} ({s['cash_pct']}%)")
    print(f"  Realized P&L:     {fmt_money(s['realized_pnl'])}")

    # Longs
    longs = [p for p in positions if p["side"] == "long"]
    if longs:
        longs.sort(key=lambda p: p["cost_basis_total"], reverse=True)
        print("\n-- Long Positions " + "-" * 54)
        headers = ["Ticker", "Company", "Weight", "Entry", "Current", "P&L", "MOS", "Verdict"]
        widths = [8, 22, 7, 10, 10, 10, 7, 7]
        rows = []
        for p in longs:
            w = p["cost_basis_total"] / s["total_capital"] * 100 if s["total_capital"] else 0
            current = f"${p['current_price']:.2f}" if p["current_price"] else "\u2014"
            pnl = fmt_money(p["unrealized_pnl"]) if p["unrealized_pnl"] is not None else "\u2014"
            mos = f"{p['margin_of_safety_at_entry_pct']:.1f}%" if p["margin_of_safety_at_entry_pct"] is not None else "\u2014"
            rows.append([p["ticker"], p.get("company", "")[:21], f"{w:.1f}%",
                         f"${p['entry_price']:.2f}", current, pnl, mos,
                         p.get("verdict_at_entry", "")])
        print_table(rows, headers, widths)

    # Shorts
    shorts = [p for p in positions if p["side"] == "short"]
    if shorts:
        shorts.sort(key=lambda p: p["cost_basis_total"], reverse=True)
        print("\n-- Short Positions " + "-" * 53)
        headers = ["Ticker", "Company", "Weight", "Entry", "Current", "P&L", "Verdict"]
        widths = [8, 22, 7, 10, 10, 10, 7]
        rows = []
        for p in shorts:
            w = p["cost_basis_total"] / s["total_capital"] * 100 if s["total_capital"] else 0
            current = f"${p['current_price']:.2f}" if p["current_price"] else "\u2014"
            pnl = fmt_money(p["unrealized_pnl"]) if p["unrealized_pnl"] is not None else "\u2014"
            rows.append([p["ticker"], p.get("company", "")[:21], f"{w:.1f}%",
                         f"${p['entry_price']:.2f}", current, pnl,
                         p.get("verdict_at_entry", "")])
        print_table(rows, headers, widths)

    # Sector exposure
    sw = s.get("sector_weights", {})
    if sw:
        print("\n-- Sector Exposure " + "-" * 53)
        headers = ["Sector", "Gross", "Long", "Short", "Names"]
        widths = [18, 7, 7, 7, 5]
        rows = []
        for sector in sorted(sw, key=lambda k: sw[k]["gross_pct"], reverse=True):
            d = sw[sector]
            rows.append([sector, f"{d['gross_pct']}%", f"{d['long_pct']}%",
                         f"{d['short_pct']}%", d["names"]])
        print_table(rows, headers, widths)

    # Policy flags
    flagged = [p for p in positions if p.get("policy_flags")]
    if flagged:
        print("\n-- Policy Warnings " + "-" * 53)
        for p in flagged:
            for flag in p["policy_flags"]:
                print(f"  {p['ticker']}: {flag}")

    print(f"\n{'='*72}\n")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_init(args) -> None:
    if LEDGER_FILE.exists() and not args.force:
        print(f"ERROR: Ledger already exists at {LEDGER_FILE}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    ledger = {
        "metadata": {
            "created_at": now_iso(),
            "last_updated": now_iso(),
            "initial_capital": args.capital,
            "currency": "USD",
            "version": 1,
        },
        "positions": [],
        "transactions": [],
        "summary": {},
    }
    recompute_summary(ledger)
    save_ledger(ledger)
    render_markdown(ledger)
    print(f"Ledger initialized with {fmt_money(args.capital)} capital.")
    print(f"  {LEDGER_FILE}")


def _do_buy(ledger: dict, ticker: str, side: str, price: float, shares: float,
            iv: float | None, reason: str, date: str, force: bool,
            skip_policy: bool = False) -> None:
    """Shared logic for buy and short commands."""
    value = round(price * shares, 2)
    ticker = ticker.upper()

    # Look up context
    qe = queue_entry(ticker)
    report = find_report(ticker)
    report_ref = find_report_ref(ticker)
    company = ""
    if qe:
        company = qe.get("company", "")
    elif report:
        company = report.get("company", "")
    sector = derive_sector(qe.get("tags", [])) if qe else "Other"
    verdict = report.get("verdict", "") if report else ""
    score = report.get("average_score", 0.0) if report else 0.0

    # Compute MOS
    mos_at_entry = None
    if iv and iv > 0 and side == "long":
        mos_at_entry = round((iv - price) / iv * 100, 1)
    elif iv and iv > 0 and side == "short":
        mos_at_entry = round((price - iv) / price * 100, 1)

    # Policy check
    if not skip_policy:
        violations, blocked = check_policy(
            ledger, "buy" if side == "long" else "short",
            ticker, side, value, iv=iv, price=price, force=force,
        )
        if violations:
            print(f"\nPolicy check for {ticker}:")
            print_violations(violations)
        if blocked:
            hard = [v for v in violations if v["severity"] == "hard"]
            if hard:
                print("\nTrade REFUSED (hard policy violation).", file=sys.stderr)
            else:
                print("\nTrade REFUSED (soft warning — use --force to override).", file=sys.stderr)
            sys.exit(1)
        if violations:
            print()  # spacing after warnings

    # Check if position exists (add to it)
    existing = next((p for p in ledger["positions"]
                     if p["ticker"] == ticker and p["side"] == side), None)

    action_name = "buy" if side == "long" else "short_open"
    if existing:
        action_name = "add"
        old_total = existing["cost_basis_total"]
        old_shares = existing["shares"]
        existing["shares"] = round(old_shares + shares, 6)
        existing["cost_basis_total"] = round(old_total + value, 2)
        existing["cost_basis_per_share"] = round(
            existing["cost_basis_total"] / existing["shares"], 4
        )
        if iv:
            existing["last_iv_estimate"] = iv
            existing["last_iv_date"] = date
        # Reset computed fields
        existing["current_price"] = None
        existing["current_price_date"] = None
        existing["current_value"] = None
        existing["unrealized_pnl"] = None
        existing["unrealized_pnl_pct"] = None
        existing["current_margin_of_safety_pct"] = None
    else:
        position = {
            "ticker": ticker,
            "company": company,
            "side": side,
            "entry_date": date,
            "entry_price": price,
            "shares": round(shares, 6),
            "cost_basis_total": value,
            "cost_basis_per_share": price,
            "target_weight_pct": round(
                value / ledger["summary"].get("total_capital",
                                               ledger["metadata"]["initial_capital"]) * 100, 1
            ),
            "current_price": None,
            "current_price_date": None,
            "current_value": None,
            "unrealized_pnl": None,
            "unrealized_pnl_pct": None,
            "last_iv_estimate": iv,
            "last_iv_date": date if iv else None,
            "margin_of_safety_at_entry_pct": mos_at_entry,
            "current_margin_of_safety_pct": None,
            "sector": sector,
            "report_ref": report_ref,
            "verdict_at_entry": verdict,
            "score_at_entry": score,
            "policy_flags": [],
            "notes": "",
        }
        ledger["positions"].append(position)

    # Transaction
    tx = {
        "id": next_tx_id(ledger),
        "date": date,
        "timestamp": now_iso(),
        "ticker": ticker,
        "company": company,
        "side": side,
        "action": action_name,
        "price": price,
        "shares": round(shares, 6),
        "value": value,
        "reason": reason,
        "report_ref": report_ref,
        "policy_check_result": "pass",
        "policy_warnings": [v["message"] for v in
                            ([] if skip_policy else
                             check_policy(ledger, "buy", ticker, side, value,
                                          iv=iv, price=price, force=True)[0])
                            if v["severity"] == "soft"],
    }
    ledger["transactions"].append(tx)

    recompute_summary(ledger)
    save_ledger(ledger)
    render_markdown(ledger)

    total_capital = ledger["summary"]["total_capital"]
    weight = value / total_capital * 100 if total_capital else 0
    print(f"{'Added to' if action_name == 'add' else 'Opened'} {side} position: "
          f"{ticker} — {shares:.4g} shares @ ${price:.2f} = {fmt_money(value)} ({weight:.1f}%)")
    if mos_at_entry is not None:
        print(f"  MOS at entry: {mos_at_entry:.1f}%")


def cmd_buy(args) -> None:
    ledger = load_ledger()
    ticker = args.ticker.upper()
    price = args.price
    if args.shares:
        shares = args.shares
    elif args.amount:
        shares = round(args.amount / price, 6)
    else:
        print("ERROR: Either --shares or --amount is required.", file=sys.stderr)
        sys.exit(1)

    _do_buy(ledger, ticker, "long", price, shares,
            args.iv, args.reason or "", args.date or today_str(), args.force)


def cmd_sell(args) -> None:
    ledger = load_ledger()
    ticker = args.ticker.upper()
    price = args.price
    side = "long"

    pos = next((p for p in ledger["positions"]
                if p["ticker"] == ticker and p["side"] == side), None)
    if not pos:
        print(f"ERROR: No long position found for {ticker}", file=sys.stderr)
        sys.exit(1)

    shares = args.shares if args.shares else pos["shares"]
    if shares > pos["shares"]:
        print(f"ERROR: Cannot sell {shares} shares — only hold {pos['shares']}", file=sys.stderr)
        sys.exit(1)

    value = round(price * shares, 2)
    cost_sold = round(pos["cost_basis_per_share"] * shares, 2)
    realized = round(value - cost_sold, 2)
    date = args.date or today_str()

    # Update position
    remaining = round(pos["shares"] - shares, 6)
    if remaining <= 0.0001:
        ledger["positions"].remove(pos)
        action_name = "sell"
    else:
        pos["shares"] = remaining
        pos["cost_basis_total"] = round(pos["cost_basis_per_share"] * remaining, 2)
        pos["current_price"] = None
        pos["current_value"] = None
        pos["unrealized_pnl"] = None
        pos["unrealized_pnl_pct"] = None
        pos["current_margin_of_safety_pct"] = None
        action_name = "trim"

    # Record realized P&L
    old_realized = ledger.get("summary", {}).get("realized_pnl", 0.0)
    # Temporarily store it so recompute_summary picks it up
    if "summary" not in ledger:
        ledger["summary"] = {}
    ledger["summary"]["realized_pnl"] = round(old_realized + realized, 2)

    # Transaction
    tx = {
        "id": next_tx_id(ledger),
        "date": date,
        "timestamp": now_iso(),
        "ticker": ticker,
        "company": pos.get("company", ""),
        "side": side,
        "action": action_name,
        "price": price,
        "shares": round(shares, 6),
        "value": value,
        "reason": args.reason or "",
        "report_ref": pos.get("report_ref"),
        "policy_check_result": "pass",
        "policy_warnings": [],
    }
    ledger["transactions"].append(tx)

    recompute_summary(ledger)
    save_ledger(ledger)
    render_markdown(ledger)

    label = "Closed" if action_name == "sell" else "Trimmed"
    print(f"{label} long position: {ticker} — {shares:.4g} shares @ ${price:.2f} = {fmt_money(value)}")
    print(f"  Realized P&L: {fmt_money(realized)}")
    if remaining > 0.0001:
        print(f"  Remaining: {remaining:.4g} shares ({fmt_money(pos['cost_basis_total'])})")


def cmd_short(args) -> None:
    ledger = load_ledger()
    ticker = args.ticker.upper()
    price = args.price
    if args.shares:
        shares = args.shares
    elif args.amount:
        shares = round(args.amount / price, 6)
    else:
        print("ERROR: Either --shares or --amount is required.", file=sys.stderr)
        sys.exit(1)

    _do_buy(ledger, ticker, "short", price, shares,
            args.iv, args.reason or "", args.date or today_str(), args.force)


def cmd_cover(args) -> None:
    ledger = load_ledger()
    ticker = args.ticker.upper()
    price = args.price
    side = "short"

    pos = next((p for p in ledger["positions"]
                if p["ticker"] == ticker and p["side"] == side), None)
    if not pos:
        print(f"ERROR: No short position found for {ticker}", file=sys.stderr)
        sys.exit(1)

    shares = args.shares if args.shares else pos["shares"]
    if shares > pos["shares"]:
        print(f"ERROR: Cannot cover {shares} shares — only short {pos['shares']}", file=sys.stderr)
        sys.exit(1)

    value = round(price * shares, 2)
    # Short P&L: profit when price fell
    cost_basis = round(pos["cost_basis_per_share"] * shares, 2)
    realized = round(cost_basis - value, 2)
    date = args.date or today_str()

    remaining = round(pos["shares"] - shares, 6)
    if remaining <= 0.0001:
        ledger["positions"].remove(pos)
        action_name = "short_close"
    else:
        pos["shares"] = remaining
        pos["cost_basis_total"] = round(pos["cost_basis_per_share"] * remaining, 2)
        pos["current_price"] = None
        pos["current_value"] = None
        pos["unrealized_pnl"] = None
        pos["unrealized_pnl_pct"] = None
        action_name = "short_close"

    old_realized = ledger.get("summary", {}).get("realized_pnl", 0.0)
    if "summary" not in ledger:
        ledger["summary"] = {}
    ledger["summary"]["realized_pnl"] = round(old_realized + realized, 2)

    tx = {
        "id": next_tx_id(ledger),
        "date": date,
        "timestamp": now_iso(),
        "ticker": ticker,
        "company": pos.get("company", ""),
        "side": side,
        "action": action_name,
        "price": price,
        "shares": round(shares, 6),
        "value": value,
        "reason": args.reason or "",
        "report_ref": pos.get("report_ref"),
        "policy_check_result": "pass",
        "policy_warnings": [],
    }
    ledger["transactions"].append(tx)

    recompute_summary(ledger)
    save_ledger(ledger)
    render_markdown(ledger)

    label = "Closed" if remaining <= 0.0001 else "Reduced"
    print(f"{label} short position: {ticker} — {shares:.4g} shares @ ${price:.2f} = {fmt_money(value)}")
    print(f"  Realized P&L: {fmt_money(realized)}")
    if remaining > 0.0001:
        print(f"  Remaining: {remaining:.4g} shares ({fmt_money(pos['cost_basis_total'])})")


def cmd_status(args) -> None:
    ledger = load_ledger()
    render_markdown(ledger)
    print_status(ledger, args.output)
    print(f"  Markdown: {STATE_MD}")


def cmd_refresh(args) -> None:
    try:
        import yfinance as yf
    except ImportError:
        print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
        sys.exit(1)

    ledger = load_ledger()
    tickers_to_refresh = args.tickers if args.tickers else [
        p["ticker"] for p in ledger["positions"]
    ]

    if not tickers_to_refresh:
        print("No positions to refresh.")
        return

    print(f"Refreshing prices for {len(tickers_to_refresh)} ticker(s)...")
    today = today_str()

    for ticker in tickers_to_refresh:
        pos = next((p for p in ledger["positions"] if p["ticker"] == ticker), None)
        if not pos:
            print(f"  {ticker}: not in portfolio, skipping")
            continue

        try:
            info = yf.Ticker(ticker).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price is None:
                print(f"  {ticker}: no price available")
                continue

            pos["current_price"] = round(price, 2)
            pos["current_price_date"] = today

            if pos["side"] == "long":
                pos["current_value"] = round(price * pos["shares"], 2)
                pos["unrealized_pnl"] = round(pos["current_value"] - pos["cost_basis_total"], 2)
                pos["unrealized_pnl_pct"] = round(
                    pos["unrealized_pnl"] / pos["cost_basis_total"] * 100, 1
                ) if pos["cost_basis_total"] else 0
            else:
                pos["current_value"] = round(price * pos["shares"], 2)
                pos["unrealized_pnl"] = round(
                    (pos["entry_price"] - price) * pos["shares"], 2
                )
                pos["unrealized_pnl_pct"] = round(
                    pos["unrealized_pnl"] / pos["cost_basis_total"] * 100, 1
                ) if pos["cost_basis_total"] else 0

            if pos["last_iv_estimate"]:
                if pos["side"] == "long":
                    pos["current_margin_of_safety_pct"] = round(
                        (pos["last_iv_estimate"] - price) / pos["last_iv_estimate"] * 100, 1
                    )
                else:
                    pos["current_margin_of_safety_pct"] = round(
                        (price - pos["last_iv_estimate"]) / price * 100, 1
                    )

            print(f"  {ticker}: ${price:.2f}")

        except Exception as e:
            print(f"  {ticker}: refresh failed ({e})")

    recompute_summary(ledger)
    save_ledger(ledger)
    render_markdown(ledger)
    print("Refresh complete.")


def cmd_check(args) -> None:
    ledger = load_ledger()
    ticker = args.ticker.upper()
    price = args.price
    side = "long" if args.action == "buy" else "short"

    if args.shares:
        value = price * args.shares
    elif args.amount:
        value = args.amount
    else:
        print("ERROR: Either --shares or --amount is required.", file=sys.stderr)
        sys.exit(1)

    violations, blocked = check_policy(
        ledger, args.action, ticker, side, value,
        iv=args.iv, price=price, force=False,
    )

    if not violations:
        print(f"Policy check PASSED for {args.action} {ticker} ({fmt_money(value)})")
    else:
        print(f"\nPolicy check for {args.action} {ticker} ({fmt_money(value)}):")
        print_violations(violations)
        if blocked:
            print("\nTrade would be REFUSED.")
        else:
            print("\nTrade would PROCEED (warnings only).")


def cmd_bootstrap(args) -> None:
    if LEDGER_FILE.exists() and not args.force:
        print(f"ERROR: Ledger already exists at {LEDGER_FILE}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    decision_path = Path(args.file)
    if not decision_path.exists():
        print(f"ERROR: Decision file not found: {decision_path}", file=sys.stderr)
        sys.exit(1)

    with open(decision_path) as f:
        decision = json.load(f)

    # Load entry prices
    prices = {}
    if args.prices:
        prices_path = Path(args.prices)
        if not prices_path.exists():
            print(f"ERROR: Prices file not found: {prices_path}", file=sys.stderr)
            sys.exit(1)
        with open(prices_path) as f:
            prices = json.load(f)

    capital = args.capital
    decision_date = decision.get("decision_date", today_str())

    # Init ledger
    ledger = {
        "metadata": {
            "created_at": now_iso(),
            "last_updated": now_iso(),
            "initial_capital": capital,
            "currency": "USD",
            "version": 1,
        },
        "positions": [],
        "transactions": [],
        "summary": {"realized_pnl": 0.0},
    }

    for pos_data in decision.get("positions", []):
        ticker = pos_data["ticker"]
        side = pos_data["side"]
        target_weight = pos_data["target_weight"]
        cost_basis = round(target_weight / 100 * capital, 2)

        entry_price = prices.get(ticker)
        if not entry_price:
            print(f"  WARNING: No entry price for {ticker} — skipping")
            continue

        shares = round(cost_basis / entry_price, 6)

        # Look up report data
        report = find_report(ticker)
        report_ref = find_report_ref(ticker)
        qe = queue_entry(ticker)

        company = ""
        if qe:
            company = qe.get("company", "")
        elif report:
            company = report.get("company", "")

        sector = derive_sector(qe.get("tags", [])) if qe else "Other"
        verdict = report.get("verdict", "") if report else ""
        score = report.get("average_score", 0.0) if report else 0.0

        # IV from prices file (optional second field) or None
        iv = prices.get(f"{ticker}_iv")

        mos_at_entry = None
        if iv and side == "long":
            mos_at_entry = round((iv - entry_price) / iv * 100, 1)
        elif iv and side == "short":
            mos_at_entry = round((entry_price - iv) / entry_price * 100, 1)

        position = {
            "ticker": ticker,
            "company": company,
            "side": side,
            "entry_date": decision_date,
            "entry_price": entry_price,
            "shares": shares,
            "cost_basis_total": cost_basis,
            "cost_basis_per_share": entry_price,
            "target_weight_pct": target_weight,
            "current_price": None,
            "current_price_date": None,
            "current_value": None,
            "unrealized_pnl": None,
            "unrealized_pnl_pct": None,
            "last_iv_estimate": iv,
            "last_iv_date": decision_date if iv else None,
            "margin_of_safety_at_entry_pct": mos_at_entry,
            "current_margin_of_safety_pct": None,
            "sector": sector,
            "report_ref": report_ref,
            "verdict_at_entry": verdict,
            "score_at_entry": score,
            "policy_flags": [],
            "notes": pos_data.get("thesis", "")[:200],
        }
        ledger["positions"].append(position)

        tx = {
            "id": next_tx_id(ledger),
            "date": decision_date,
            "timestamp": now_iso(),
            "ticker": ticker,
            "company": company,
            "side": side,
            "action": "buy" if side == "long" else "short_open",
            "price": entry_price,
            "shares": shares,
            "value": cost_basis,
            "reason": f"Bootstrap from {decision_path.name}: {target_weight}% target weight",
            "report_ref": report_ref,
            "policy_check_result": "pass",
            "policy_warnings": [],
        }
        ledger["transactions"].append(tx)

        print(f"  {side.upper():5s} {ticker:12s} {shares:>10.4g} shares @ ${entry_price:>8.2f} = {fmt_money(cost_basis):>8s} ({target_weight}%)")

    recompute_summary(ledger)
    save_ledger(ledger)
    render_markdown(ledger)

    print(f"\nBootstrapped {len(ledger['positions'])} positions from {decision_path.name}")
    print(f"  Ledger:   {LEDGER_FILE}")
    print(f"  Markdown: {STATE_MD}")


def cmd_history(args) -> None:
    ledger = load_ledger()
    transactions = ledger["transactions"]

    if args.ticker:
        transactions = [t for t in transactions if t["ticker"] == args.ticker.upper()]

    if args.last:
        transactions = transactions[-args.last:]

    if not transactions:
        print("No transactions found.")
        return

    print(f"\n{'='*80}")
    print("  TRANSACTION HISTORY")
    print(f"{'='*80}")
    headers = ["ID", "Date", "Ticker", "Action", "Price", "Shares", "Value", "Reason"]
    widths = [4, 10, 8, 12, 10, 10, 10, 30]
    rows = []
    for t in transactions:
        rows.append([
            t["id"], t["date"], t["ticker"], t["action"],
            f"${t['price']:.2f}", f"{t['shares']:.4g}",
            fmt_money(t["value"]), (t.get("reason", "") or "")[:29],
        ])
    print_table(rows, headers, widths)
    print(f"\n{'='*80}\n")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Portfolio ledger — persistent tracking with policy compliance."
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = sub.add_parser("init", help="Initialize empty ledger")
    p_init.add_argument("--capital", type=float, required=True, help="Starting capital")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing ledger")

    # buy
    p_buy = sub.add_parser("buy", help="Open or add to a long position")
    p_buy.add_argument("ticker", help="Ticker symbol")
    p_buy.add_argument("--price", type=float, required=True, help="Entry price per share")
    p_buy.add_argument("--shares", type=float, help="Number of shares")
    p_buy.add_argument("--amount", type=float, help="Dollar amount (computes shares)")
    p_buy.add_argument("--iv", type=float, help="Intrinsic value estimate")
    p_buy.add_argument("--reason", type=str, default="", help="Trade reason")
    p_buy.add_argument("--date", type=str, help="Trade date (default: today)")
    p_buy.add_argument("--force", action="store_true", help="Override soft policy warnings")

    # sell
    p_sell = sub.add_parser("sell", help="Close or reduce a long position")
    p_sell.add_argument("ticker", help="Ticker symbol")
    p_sell.add_argument("--price", type=float, required=True, help="Sale price per share")
    p_sell.add_argument("--shares", type=float, help="Shares to sell (default: all)")
    p_sell.add_argument("--reason", type=str, default="", help="Trade reason")
    p_sell.add_argument("--date", type=str, help="Trade date (default: today)")

    # short
    p_short = sub.add_parser("short", help="Open or add to a short position")
    p_short.add_argument("ticker", help="Ticker symbol")
    p_short.add_argument("--price", type=float, required=True, help="Entry price per share")
    p_short.add_argument("--shares", type=float, help="Number of shares")
    p_short.add_argument("--amount", type=float, help="Dollar amount (computes shares)")
    p_short.add_argument("--iv", type=float, help="Intrinsic value estimate")
    p_short.add_argument("--reason", type=str, default="", help="Trade reason")
    p_short.add_argument("--date", type=str, help="Trade date (default: today)")
    p_short.add_argument("--force", action="store_true", help="Override soft policy warnings")

    # cover
    p_cover = sub.add_parser("cover", help="Close or reduce a short position")
    p_cover.add_argument("ticker", help="Ticker symbol")
    p_cover.add_argument("--price", type=float, required=True, help="Cover price per share")
    p_cover.add_argument("--shares", type=float, help="Shares to cover (default: all)")
    p_cover.add_argument("--reason", type=str, default="", help="Trade reason")
    p_cover.add_argument("--date", type=str, help="Trade date (default: today)")

    # status
    p_status = sub.add_parser("status", help="Show current portfolio state")
    p_status.add_argument("--output", default="table", choices=["table", "json"],
                          help="Output format")

    # refresh
    p_refresh = sub.add_parser("refresh", help="Update current prices via yfinance")
    p_refresh.add_argument("tickers", nargs="*", help="Specific tickers (default: all)")

    # check
    p_check = sub.add_parser("check", help="Dry-run policy check")
    p_check.add_argument("action", choices=["buy", "short"], help="Trade action")
    p_check.add_argument("ticker", help="Ticker symbol")
    p_check.add_argument("--price", type=float, required=True, help="Price per share")
    p_check.add_argument("--shares", type=float, help="Number of shares")
    p_check.add_argument("--amount", type=float, help="Dollar amount")
    p_check.add_argument("--iv", type=float, help="Intrinsic value estimate")

    # bootstrap
    p_boot = sub.add_parser("bootstrap", help="Import from portfolio-decision.json")
    p_boot.add_argument("file", help="Path to portfolio-decision.json")
    p_boot.add_argument("--capital", type=float, required=True, help="Starting capital")
    p_boot.add_argument("--prices", type=str, help="Path to entry-prices.json")
    p_boot.add_argument("--force", action="store_true", help="Overwrite existing ledger")

    # history
    p_hist = sub.add_parser("history", help="Show transaction log")
    p_hist.add_argument("--ticker", type=str, help="Filter by ticker")
    p_hist.add_argument("--last", type=int, help="Show last N transactions")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "init": cmd_init,
        "buy": cmd_buy,
        "sell": cmd_sell,
        "short": cmd_short,
        "cover": cmd_cover,
        "status": cmd_status,
        "refresh": cmd_refresh,
        "check": cmd_check,
        "bootstrap": cmd_bootstrap,
        "history": cmd_history,
    }

    fn = dispatch.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
