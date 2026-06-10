#!/usr/bin/env python3
"""
paper_trade.py — SQLite-backed portfolio tracking with policy compliance.

Drop-in replacement for portfolio-ledger.py. Routes all state through
PortfolioEngine + Database (SQLite) instead of portfolio/ledger.json.

Usage:
    python3 scripts/paper_trade.py init --capital 100000
    python3 scripts/paper_trade.py buy V --price 312.50 --amount 3000 --iv 380
    python3 scripts/paper_trade.py sell V --price 340.00 --shares 5
    python3 scripts/paper_trade.py short CAT --price 705 --shares 10 --iv 272
    python3 scripts/paper_trade.py cover CAT --price 600 --shares 10
    python3 scripts/paper_trade.py status
    python3 scripts/paper_trade.py report
    python3 scripts/paper_trade.py report --html --output reports/performance/custom.html
    python3 scripts/paper_trade.py refresh
    python3 scripts/paper_trade.py check buy V --price 312.50 --amount 3000
    python3 scripts/paper_trade.py history
    python3 scripts/paper_trade.py migrate --from portfolio/ledger.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.database import Database
from src.portfolio_engine import PortfolioEngine
from src.price_fetcher import PriceFetcher
from src.snapshot import SnapshotEngine
from src.trade_executor import TradeExecutor
from src.trade_proposer import TradeProposalGenerator

STATE_MD = REPO_ROOT / "portfolio" / "portfolio-state.md"
DB_PATH = "data/db/portfolio.db"


# ---------------------------------------------------------------------------
# Helpers (CLI-only — formatting and I/O)
# ---------------------------------------------------------------------------

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


def print_violations(violations: list[dict]) -> None:
    for v in violations:
        severity_label = "BLOCKED" if v["severity"] == "hard" else "WARNING"
        print(f"  [{severity_label}] {v['rule']}: {v['message']}")


def print_table(rows: list[list], headers: list[str], col_widths: list[int]) -> None:
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    sep = "  ".join("-" * w for w in col_widths)
    print(header_line)
    print(sep)
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))


def summarize_rule_checks(rule_checks: list[dict]) -> str:
    if not rule_checks:
        return "PASS"
    warnings = sum(1 for check in rule_checks if check.get("severity") == "soft")
    blocks = sum(1 for check in rule_checks if check.get("severity") == "hard")
    return f"{warnings}W/{blocks}B"


def get_engine() -> PortfolioEngine:
    """Open the database, ensure schema exists, return an engine."""
    db = Database(DB_PATH)
    db.connect()
    db.init_db()
    return PortfolioEngine(db)


def get_reporter():
    """Build the reporting stack from the existing DB and engine."""
    from src.reporter import PerformanceReporter

    snapshot_engine = get_snapshot_engine()
    return PerformanceReporter(snapshot_engine, snapshot_engine.engine)


def get_snapshot_engine() -> SnapshotEngine:
    """Build the snapshot stack from the existing DB and engine."""
    engine = get_engine()
    fetcher = PriceFetcher(engine.db)
    return SnapshotEngine(engine, fetcher, engine.db)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_markdown(engine: PortfolioEngine) -> None:
    """Write portfolio/portfolio-state.md from current DB state."""
    portfolio = engine.load()
    summary = engine.get_summary()

    s = summary
    lines = []
    lines.append("# Portfolio State")
    lines.append(f"_Last updated: {now_iso()}_")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Capital | {fmt_money(s['total_capital'])} |")
    if s["total_capital"]:
        lines.append(f"| Deployed (Long) | {fmt_money(s['deployed_long'])} ({s['deployed_long'] / s['total_capital'] * 100:.1f}%) |")
        lines.append(f"| Deployed (Short) | {fmt_money(s['deployed_short'])} ({s['deployed_short'] / s['total_capital'] * 100:.1f}%) |")
    else:
        lines.append("| Deployed (Long) | $0 |")
        lines.append("| Deployed (Short) | $0 |")
    lines.append(f"| Gross Exposure | {fmt_money(s['gross_exposure'])} ({s['gross_exposure_pct']}%) |")
    lines.append(f"| Net Exposure | {fmt_money(s['net_exposure'])} ({s['net_exposure_pct']}%) |")
    lines.append(f"| Cash | {fmt_money(s['cash_position'])} ({s['cash_pct']}%) |")
    lines.append(f"| Positions | {s['position_count']} ({s['long_count']} long, {s['short_count']} short) |")
    lines.append(f"| Realized P&L | {fmt_money(s['realized_pnl'])} |")
    lines.append("")

    # Long positions
    longs = [(t, p) for t, p in portfolio.positions.items()
             if p.side == "LONG" and p.status == "OPEN"]
    if longs:
        longs.sort(key=lambda tp: float(tp[1].total_cost), reverse=True)
        lines.append("## Long Positions")
        lines.append("")
        lines.append("| Ticker | Company | Weight | Entry | Cost | Shares |")
        lines.append("|--------|---------|--------|-------|------|--------|")
        for ticker, pos in longs:
            w = float(pos.total_cost) / s["total_capital"] * 100 if s["total_capital"] else 0
            lines.append(
                f"| {ticker} | {pos.company[:25]} | {w:.1f}% "
                f"| ${float(pos.avg_cost_basis):.2f} | {fmt_money(float(pos.total_cost))} "
                f"| {float(pos.shares):.4g} |"
            )
        lines.append("")

    # Short positions
    shorts = [(t, p) for t, p in portfolio.positions.items()
              if p.side == "SHORT" and p.status == "OPEN"]
    if shorts:
        shorts.sort(key=lambda tp: float(tp[1].total_cost), reverse=True)
        lines.append("## Short Positions")
        lines.append("")
        lines.append("| Ticker | Company | Weight | Entry | Cost | Shares |")
        lines.append("|--------|---------|--------|-------|------|--------|")
        for ticker, pos in shorts:
            w = float(pos.total_cost) / s["total_capital"] * 100 if s["total_capital"] else 0
            lines.append(
                f"| {ticker} | {pos.company[:25]} | {w:.1f}% "
                f"| ${float(pos.avg_cost_basis):.2f} | {fmt_money(float(pos.total_cost))} "
                f"| {float(pos.shares):.4g} |"
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
    lines.append("All positions within policy limits.")
    lines.append("")

    # Recent transactions
    txns = engine.db.get_transactions(limit=20)
    if txns:
        lines.append("## Recent Transactions")
        lines.append("")
        lines.append("| Date | Ticker | Action | Price | Shares | Value | Reason |")
        lines.append("|------|--------|--------|-------|--------|-------|--------|")
        for t in txns:
            price = t.get("price", 0)
            shares = t.get("shares", 0)
            value = t.get("net_value", 0)
            lines.append(
                f"| {t['timestamp'][:10]} | {t['ticker']} | {t['action']} "
                f"| ${price:.2f} | {shares:.4g} | {fmt_money(value)} "
                f"| {(t.get('reason', '') or '')[:40]} |"
            )
        lines.append("")

    STATE_MD.parent.mkdir(parents=True, exist_ok=True)
    STATE_MD.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Status display
# ---------------------------------------------------------------------------

def print_status(engine: PortfolioEngine, output_fmt: str = "table") -> None:
    portfolio = engine.load()
    s = engine.get_summary()

    if output_fmt == "json":
        # Produce compatible JSON output
        positions_list = []
        for ticker, pos in portfolio.positions.items():
            if pos.status != "OPEN":
                continue
            positions_list.append({
                "ticker": ticker,
                "company": pos.company,
                "side": pos.side.lower(),
                "shares": float(pos.shares),
                "cost_basis_total": float(pos.total_cost),
                "cost_basis_per_share": float(pos.avg_cost_basis),
                "sector": pos.sector,
                "entry_report_ref": pos.entry_report_ref,
            })
        output = {
            "metadata": {
                "initial_capital": s["initial_capital"],
                "currency": "USD",
            },
            "positions": positions_list,
            "summary": s,
            "transactions": [],
        }
        print(json.dumps(output, indent=2))
        return

    tc = s["total_capital"]
    print(f"\n{'='*72}")
    print(f"  PORTFOLIO LEDGER  —  Capital: {fmt_money(tc)}")
    print(f"{'='*72}")

    if tc:
        print(f"\n  Deployed (Long):  {fmt_money(s['deployed_long'])} ({s['deployed_long'] / tc * 100:.1f}%)")
        print(f"  Deployed (Short): {fmt_money(s['deployed_short'])} ({s['deployed_short'] / tc * 100:.1f}%)")
    print(f"  Gross Exposure:   {fmt_money(s['gross_exposure'])} ({s['gross_exposure_pct']}%)")
    print(f"  Net Exposure:     {fmt_money(s['net_exposure'])} ({s['net_exposure_pct']}%)")
    print(f"  Cash:             {fmt_money(s['cash_position'])} ({s['cash_pct']}%)")
    print(f"  Realized P&L:     {fmt_money(s['realized_pnl'])}")

    # Longs
    longs = [(t, p) for t, p in portfolio.positions.items()
             if p.side == "LONG" and p.status == "OPEN"]
    if longs:
        longs.sort(key=lambda tp: float(tp[1].total_cost), reverse=True)
        print("\n-- Long Positions " + "-" * 54)
        headers = ["Ticker", "Company", "Weight", "Entry", "Cost", "Shares"]
        widths = [8, 22, 7, 10, 10, 10]
        rows = []
        for ticker, pos in longs:
            w = float(pos.total_cost) / tc * 100 if tc else 0
            rows.append([ticker, pos.company[:21], f"{w:.1f}%",
                         f"${float(pos.avg_cost_basis):.2f}",
                         fmt_money(float(pos.total_cost)),
                         f"{float(pos.shares):.4g}"])
        print_table(rows, headers, widths)

    # Shorts
    shorts = [(t, p) for t, p in portfolio.positions.items()
              if p.side == "SHORT" and p.status == "OPEN"]
    if shorts:
        shorts.sort(key=lambda tp: float(tp[1].total_cost), reverse=True)
        print("\n-- Short Positions " + "-" * 53)
        headers = ["Ticker", "Company", "Weight", "Entry", "Cost", "Shares"]
        widths = [8, 22, 7, 10, 10, 10]
        rows = []
        for ticker, pos in shorts:
            w = float(pos.total_cost) / tc * 100 if tc else 0
            rows.append([ticker, pos.company[:21], f"{w:.1f}%",
                         f"${float(pos.avg_cost_basis):.2f}",
                         fmt_money(float(pos.total_cost)),
                         f"{float(pos.shares):.4g}"])
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

    print(f"\n{'='*72}\n")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args) -> None:
    db = Database(DB_PATH)
    db.connect()
    db.init_db()

    # Check if already initialized
    init_row = db.conn.execute(
        "SELECT id FROM transactions WHERE action = 'INIT' LIMIT 1"
    ).fetchone()
    if init_row and not args.force:
        print("ERROR: Portfolio already initialized.", file=sys.stderr)
        print("Use --force to reinitialize.", file=sys.stderr)
        sys.exit(1)

    if init_row and args.force:
        # Wipe all data for reinit
        for table in ("lots", "transactions", "positions", "portfolio_snapshots",
                       "trade_proposals", "price_cache"):
            db.conn.execute(f"DELETE FROM {table}")
        db.conn.commit()

    db.set_initial_capital(Decimal(str(args.capital)), today_str())
    engine = PortfolioEngine(db)
    render_markdown(engine)
    print(f"Ledger initialized with {fmt_money(args.capital)} capital.")
    print(f"  Database: {db.db_path}")


def cmd_buy(args) -> None:
    engine = get_engine()
    ticker = args.ticker.upper()
    price = Decimal(str(args.price))

    if args.shares:
        shares = Decimal(str(args.shares))
    elif args.amount:
        shares = Decimal(str(round(args.amount / args.price, 6)))
    else:
        print("ERROR: Either --shares or --amount is required.", file=sys.stderr)
        sys.exit(1)

    iv = Decimal(str(args.iv)) if args.iv else None
    date = args.date or today_str()

    result = engine.execute_buy(
        ticker, "LONG", price, shares, iv,
        args.reason or "", date, skip_policy=False,
    )

    # Handle policy refusal
    if result["action"] == "REFUSED":
        print(f"\nPolicy check for {ticker}:")
        print_violations(result["violations"])
        hard = [v for v in result["violations"] if v["severity"] == "hard"]
        if hard:
            print("\nTrade REFUSED (hard policy violation).", file=sys.stderr)
        else:
            print("\nTrade REFUSED (soft warning — use --force to override).", file=sys.stderr)
        sys.exit(1)

    # Handle soft warnings without --force
    soft = [v for v in result.get("violations", []) if v["severity"] == "soft"]
    if soft and not args.force:
        print(f"\nPolicy check for {ticker}:")
        print_violations(result["violations"])
        print("\nTrade REFUSED (soft warning — use --force to override).", file=sys.stderr)
        sys.exit(1)

    # Print warnings if forced through
    if result.get("violations"):
        print(f"\nPolicy check for {ticker}:")
        print_violations(result["violations"])
        print()

    render_markdown(engine)

    trade_value = float(result["trade_value"])
    s = engine.get_summary()
    tc = s["total_capital"]
    weight = trade_value / tc * 100 if tc else 0
    label = "Added to" if result["action"] == "ADD" else "Opened"
    print(f"{label} long position: "
          f"{ticker} — {float(result['shares']):.4g} shares @ ${float(result['price']):.2f} "
          f"= {fmt_money(trade_value)} ({weight:.1f}%)")
    if result.get("mos_at_entry") is not None:
        print(f"  MOS at entry: {float(result['mos_at_entry']):.1f}%")


def cmd_sell(args) -> None:
    engine = get_engine()
    ticker = args.ticker.upper()
    price = Decimal(str(args.price))
    date = args.date or today_str()

    if args.shares:
        shares = Decimal(str(args.shares))
    else:
        # Sell all
        portfolio = engine.load()
        pos = portfolio.positions.get(ticker)
        if not pos or pos.side != "LONG" or pos.status != "OPEN":
            print(f"ERROR: No long position found for {ticker}", file=sys.stderr)
            sys.exit(1)
        shares = pos.shares

    try:
        result = engine.execute_sell(ticker, price, shares, args.reason or "", date)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    render_markdown(engine)

    label = "Closed" if result["action"] == "SELL" else "Trimmed"
    print(f"{label} long position: {ticker} — {float(result['shares']):.4g} shares "
          f"@ ${float(result['price']):.2f} = {fmt_money(float(result['trade_value']))}")
    print(f"  Realized P&L: {fmt_money(float(result['realized_pnl']))}")
    remaining = result["remaining_shares"]
    if remaining > 0:
        print(f"  Remaining: {float(remaining):.4g} shares")


def cmd_short(args) -> None:
    engine = get_engine()
    ticker = args.ticker.upper()
    price = Decimal(str(args.price))

    if args.shares:
        shares = Decimal(str(args.shares))
    elif args.amount:
        shares = Decimal(str(round(args.amount / args.price, 6)))
    else:
        print("ERROR: Either --shares or --amount is required.", file=sys.stderr)
        sys.exit(1)

    iv = Decimal(str(args.iv)) if args.iv else None
    date = args.date or today_str()

    result = engine.execute_buy(
        ticker, "SHORT", price, shares, iv,
        args.reason or "", date, skip_policy=False,
    )

    if result["action"] == "REFUSED":
        print(f"\nPolicy check for {ticker}:")
        print_violations(result["violations"])
        hard = [v for v in result["violations"] if v["severity"] == "hard"]
        if hard:
            print("\nTrade REFUSED (hard policy violation).", file=sys.stderr)
        else:
            print("\nTrade REFUSED (soft warning — use --force to override).", file=sys.stderr)
        sys.exit(1)

    soft = [v for v in result.get("violations", []) if v["severity"] == "soft"]
    if soft and not args.force:
        print(f"\nPolicy check for {ticker}:")
        print_violations(result["violations"])
        print("\nTrade REFUSED (soft warning — use --force to override).", file=sys.stderr)
        sys.exit(1)

    if result.get("violations"):
        print(f"\nPolicy check for {ticker}:")
        print_violations(result["violations"])
        print()

    render_markdown(engine)

    trade_value = float(result["trade_value"])
    s = engine.get_summary()
    tc = s["total_capital"]
    weight = trade_value / tc * 100 if tc else 0
    label = "Added to" if result["action"] == "ADD" else "Opened"
    print(f"{label} short position: "
          f"{ticker} — {float(result['shares']):.4g} shares @ ${float(result['price']):.2f} "
          f"= {fmt_money(trade_value)} ({weight:.1f}%)")
    if result.get("mos_at_entry") is not None:
        print(f"  MOS at entry: {float(result['mos_at_entry']):.1f}%")


def cmd_cover(args) -> None:
    engine = get_engine()
    ticker = args.ticker.upper()
    price = Decimal(str(args.price))
    date = args.date or today_str()

    if args.shares:
        shares = Decimal(str(args.shares))
    else:
        portfolio = engine.load()
        pos = portfolio.positions.get(ticker)
        if not pos or pos.side != "SHORT" or pos.status != "OPEN":
            print(f"ERROR: No short position found for {ticker}", file=sys.stderr)
            sys.exit(1)
        shares = pos.shares

    try:
        result = engine.execute_cover(ticker, price, shares, args.reason or "", date)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    render_markdown(engine)

    remaining = result["remaining_shares"]
    label = "Closed" if float(remaining) <= 0.0001 else "Reduced"
    print(f"{label} short position: {ticker} — {float(result['shares']):.4g} shares "
          f"@ ${float(result['price']):.2f} = {fmt_money(float(result['trade_value']))}")
    print(f"  Realized P&L: {fmt_money(float(result['realized_pnl']))}")
    if float(remaining) > 0.0001:
        print(f"  Remaining: {float(remaining):.4g} shares")


def cmd_status(args) -> None:
    engine = get_engine()
    render_markdown(engine)
    print_status(engine, args.output)
    if args.output != "json":
        print(f"  Markdown: {STATE_MD}")


def cmd_report(args) -> None:
    reporter = get_reporter()
    try:
        if args.html:
            output_path = reporter.generate_html_report(output_path=args.output)
            print(f"HTML tear sheet written to: {output_path}")
        else:
            reporter.print_summary()
    except (RuntimeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot(args) -> None:
    snapshot_engine = get_snapshot_engine()

    if bool(args.start) != bool(args.end):
        print(
            "ERROR: --start and --end must be provided together for backfill.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        if args.start and args.end:
            written = snapshot_engine.backfill(args.start, args.end)
            print(
                f"Captured {written} snapshot(s) for {args.start} through {args.end}."
            )
            return

        snapshot = snapshot_engine.capture(snapshot_date=args.date)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if snapshot is None:
        target_date = args.date or today_str()
        print(
            f"Snapshot skipped for {target_date}. "
            "Check cached prices and benchmark availability.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        "Snapshot captured: "
        f"{snapshot['snapshot_date']} total={fmt_money(snapshot['total_value'])} "
        f"cash={fmt_money(snapshot['cash'])} positions={snapshot['num_positions']}"
    )


def cmd_refresh(args) -> None:
    try:
        import yfinance as yf
    except ImportError:
        print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
        sys.exit(1)

    engine = get_engine()
    portfolio = engine.load()

    tickers_to_refresh = args.tickers if args.tickers else list(portfolio.positions.keys())
    if not tickers_to_refresh:
        print("No positions to refresh.")
        return

    print(f"Refreshing prices for {len(tickers_to_refresh)} ticker(s)...")
    today = today_str()

    for ticker in tickers_to_refresh:
        if ticker not in portfolio.positions:
            print(f"  {ticker}: not in portfolio, skipping")
            continue

        try:
            info = yf.Ticker(ticker).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price is None:
                print(f"  {ticker}: no price available")
                continue

            engine.db.upsert_price_cache(
                ticker, today, Decimal(str(round(price, 2))), "yfinance",
            )
            print(f"  {ticker}: ${price:.2f}")

        except Exception as e:
            print(f"  {ticker}: refresh failed ({e})")

    render_markdown(engine)
    print("Refresh complete.")


def cmd_check(args) -> None:
    engine = get_engine()
    ticker = args.ticker.upper()
    price = Decimal(str(args.price))
    side = "LONG" if args.action == "buy" else "SHORT"

    if args.shares:
        value = Decimal(str(args.price * args.shares))
    elif args.amount:
        value = Decimal(str(args.amount))
    else:
        print("ERROR: Either --shares or --amount is required.", file=sys.stderr)
        sys.exit(1)

    iv = Decimal(str(args.iv)) if args.iv else None

    violations = engine.check_policy(
        args.action, ticker, side, value, iv=iv, price=price,
    )

    if not violations:
        print(f"Policy check PASSED for {args.action} {ticker} ({fmt_money(float(value))})")
    else:
        print(f"\nPolicy check for {args.action} {ticker} ({fmt_money(float(value))}):")
        print_violations(violations)
        hard = [v for v in violations if v["severity"] == "hard"]
        if hard:
            print("\nTrade would be REFUSED.")
        else:
            print("\nTrade would PROCEED (warnings only).")


def cmd_history(args) -> None:
    engine = get_engine()
    ticker = args.ticker.upper() if args.ticker else None
    limit = args.last or 50

    txns = engine.db.get_transactions(ticker=ticker, limit=limit)

    if not txns:
        print("No transactions found.")
        return

    print(f"\n{'='*80}")
    print("  TRANSACTION HISTORY")
    print(f"{'='*80}")
    headers = ["ID", "Date", "Ticker", "Action", "Price", "Shares", "Value", "Reason"]
    widths = [4, 10, 8, 12, 10, 10, 10, 30]
    rows = []
    for t in txns:
        rows.append([
            t["id"], t["timestamp"][:10], t["ticker"], t["action"],
            f"${t['price']:.2f}", f"{t['shares']:.4g}",
            fmt_money(t["net_value"]), (t.get("reason", "") or "")[:29],
        ])
    print_table(rows, headers, widths)
    print(f"\n{'='*80}\n")


def cmd_propose(args) -> None:
    engine = get_engine()
    generator = TradeProposalGenerator(engine, engine.db)

    try:
        if args.ticker:
            proposals = generator.generate_from_report(args.ticker)
        else:
            proposals = generator.generate_from_queue()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if not proposals:
        print("No proposals created.")
        return

    print(f"\n{'='*96}")
    print("  NEW TRADE PROPOSALS")
    print(f"{'='*96}")
    headers = ["ID", "Ticker", "Action", "Price", "Shares", "Value", "Target", "Rules"]
    widths = [4, 12, 8, 10, 12, 10, 8, 8]
    rows = []
    for proposal in proposals:
        rows.append([
            proposal["id"],
            proposal["ticker"],
            proposal["action"],
            f"${float(proposal['proposed_price']):.2f}",
            f"{float(proposal['proposed_shares']):.4g}",
            fmt_money(float(proposal["proposed_value"])),
            f"{float(proposal['target_weight_pct']):.1f}%",
            summarize_rule_checks(proposal.get("rule_checks_json", [])),
        ])
    print_table(rows, headers, widths)
    print(f"\n{'='*96}\n")


def cmd_review(args) -> None:
    engine = get_engine()
    executor = TradeExecutor(engine, engine.db)
    pending = executor.get_pending()

    if not pending:
        print("No pending proposals.")
        return

    for proposal in pending:
        print(f"\n{'='*80}")
        print(
            f"Proposal #{proposal['id']}  {proposal['proposed_action']}  {proposal['ticker']}"
        )
        print(f"{'='*80}")
        print(f"  Created: {proposal['created_at']}")
        print(f"  Price:   ${proposal['proposed_price']:.2f}")
        print(f"  Shares:  {proposal['proposed_shares']:.4g}")
        print(f"  Value:   {fmt_money(proposal['proposed_value'])}")
        print(f"  Target:  {proposal['target_weight_pct']:.1f}%")
        if proposal.get("rationale"):
            print(f"  Why:     {proposal['rationale']}")

        rule_checks = proposal.get("rule_checks_json") or []
        print("  Rule checks:")
        if rule_checks:
            print_violations(rule_checks)
        else:
            print("  [PASS] no policy warnings or blocks")

        while True:
            choice = input("  [a]pprove / [r]eject / [s]kip: ").strip().lower()
            if choice not in {"a", "r", "s"}:
                print("  Enter a, r, or s.")
                continue

            if choice == "s":
                break

            if choice == "r":
                reason = input("  Rejection reason: ").strip()
                if not reason:
                    print("  Rejection reason is required.")
                    continue
                try:
                    executor.reject_proposal(proposal["id"], reason)
                    print(f"  Proposal #{proposal['id']} rejected.")
                except ValueError as e:
                    print(f"ERROR: {e}", file=sys.stderr)
                break

            try:
                result = executor.execute_proposal(proposal["id"])
                render_markdown(engine)
                print(
                    f"  Executed {result['action']} for {result['ticker']} "
                    f"({fmt_money(float(result['trade_value']))})."
                )
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)
            break


def cmd_migrate(args) -> None:
    """Migrate portfolio/ledger.json into SQLite."""
    ledger_path = Path(args.source)
    if not ledger_path.is_absolute():
        ledger_path = REPO_ROOT / ledger_path

    if not ledger_path.exists():
        print(f"ERROR: Ledger file not found: {ledger_path}", file=sys.stderr)
        sys.exit(1)

    with open(ledger_path) as f:
        ledger = json.load(f)

    meta = ledger["metadata"]
    positions = ledger.get("positions", [])
    transactions = ledger.get("transactions", [])
    initial_capital = meta["initial_capital"]

    print(f"Source: {ledger_path}")
    print(f"  Capital: {fmt_money(initial_capital)}")
    print(f"  Positions: {len(positions)}")
    print(f"  Transactions: {len(transactions)}")
    print()

    if args.dry_run:
        print("-- DRY RUN — reconciliation preview --")
        print()
        headers = ["Ticker", "Side", "JSON Shares", "JSON Cost", "Status"]
        widths = [8, 6, 14, 14, 10]
        rows = []
        for p in positions:
            rows.append([
                p["ticker"], p["side"],
                f"{p['shares']:.4g}", fmt_money(p["cost_basis_total"]),
                "OK",
            ])
        print_table(rows, headers, widths)
        print(f"\nNo changes written. Remove --dry-run to execute migration.")
        return

    # Actual migration
    db = Database(DB_PATH)
    db.connect()
    db.init_db()

    # Check if already has data
    init_row = db.conn.execute(
        "SELECT id FROM transactions WHERE action = 'INIT' LIMIT 1"
    ).fetchone()
    if init_row and not args.force:
        print("ERROR: Database already has data. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    if init_row and args.force:
        for table in ("lots", "transactions", "positions", "portfolio_snapshots",
                       "trade_proposals", "price_cache"):
            db.conn.execute(f"DELETE FROM {table}")
        db.conn.commit()

    # Set initial capital
    created_date = meta.get("created_at", today_str())[:10]
    db.set_initial_capital(Decimal(str(initial_capital)), created_date)

    engine = PortfolioEngine(db)

    # Import positions as buys/shorts with skip_policy
    for p in positions:
        ticker = p["ticker"].upper()
        side = "LONG" if p["side"] == "long" else "SHORT"
        price = Decimal(str(p.get("entry_price", p["cost_basis_per_share"])))
        shares = Decimal(str(p["shares"]))
        iv = Decimal(str(p["last_iv_estimate"])) if p.get("last_iv_estimate") else None
        date = p.get("entry_date", created_date)

        result = engine.execute_buy(
            ticker, side, price, shares, iv,
            f"Migrated from {ledger_path.name}", date,
            skip_policy=True,
        )
        status = "OK" if result["action"] != "REFUSED" else "FAILED"
        print(f"  {side:5s} {ticker:12s} {float(shares):>10.4g} shares @ ${float(price):>8.2f} "
              f"= {fmt_money(float(result['trade_value'])):>8s} [{status}]")

    # Reconciliation
    print()
    print("-- Reconciliation --")
    print()
    portfolio = engine.load()
    headers = ["Ticker", "Side", "JSON Shares", "JSON Cost", "DB Shares", "DB Cost", "Match"]
    widths = [8, 6, 14, 14, 14, 14, 6]
    rows = []
    all_match = True
    for p in positions:
        ticker = p["ticker"].upper()
        db_pos = portfolio.positions.get(ticker)
        json_shares = p["shares"]
        json_cost = p["cost_basis_total"]
        if db_pos:
            db_shares = float(db_pos.shares)
            db_cost = float(db_pos.total_cost)
            match = (abs(json_shares - db_shares) < 0.01 and
                     abs(json_cost - db_cost) < 0.05)
        else:
            db_shares = 0
            db_cost = 0
            match = False

        if not match:
            all_match = False

        rows.append([
            ticker, p["side"],
            f"{json_shares:.4g}", fmt_money(json_cost),
            f"{db_shares:.4g}", fmt_money(db_cost),
            "YES" if match else "NO",
        ])
    print_table(rows, headers, widths)

    if all_match:
        print(f"\nAll positions match. Migration successful.")
        # Rename source to .bak
        bak_path = ledger_path.with_suffix(".json.bak")
        ledger_path.rename(bak_path)
        print(f"  Renamed: {ledger_path.name} → {bak_path.name}")
    else:
        print(f"\nWARNING: Some positions did not match. Review above.", file=sys.stderr)
        print(f"  Source file NOT renamed — manual review required.", file=sys.stderr)

    render_markdown(engine)
    print(f"\n  Database: {db.db_path}")
    print(f"  Markdown: {STATE_MD}")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Paper trading — SQLite-backed portfolio with policy compliance."
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = sub.add_parser("init", help="Initialize portfolio database")
    p_init.add_argument("--capital", type=float, required=True, help="Starting capital")
    p_init.add_argument("--force", action="store_true", help="Reinitialize (wipes existing data)")

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

    # report
    p_report = sub.add_parser("report", help="Show performance summary or generate HTML")
    p_report.add_argument("--html", action="store_true",
                          help="Generate a QuantStats HTML tear sheet")
    p_report.add_argument("--output", type=str,
                          help="Output path for HTML report")

    # snapshot
    p_snapshot = sub.add_parser("snapshot", help="Capture or backfill portfolio snapshots")
    p_snapshot.add_argument("--date", type=str, help="Snapshot date (default: latest trading day)")
    p_snapshot.add_argument("--start", type=str, help="Backfill start date (YYYY-MM-DD)")
    p_snapshot.add_argument("--end", type=str, help="Backfill end date (YYYY-MM-DD)")

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

    # history
    p_hist = sub.add_parser("history", help="Show transaction log")
    p_hist.add_argument("--ticker", type=str, help="Filter by ticker")
    p_hist.add_argument("--last", type=int, help="Show last N transactions")

    # propose
    p_propose = sub.add_parser("propose", help="Generate PENDING trade proposals")
    p_propose.add_argument("--ticker", type=str, help="Generate proposals for one ticker")

    # review
    sub.add_parser("review", help="Review, approve, or reject pending proposals")

    # migrate
    p_migrate = sub.add_parser("migrate", help="Migrate ledger.json to SQLite")
    p_migrate.add_argument("--from", dest="source", default="portfolio/ledger.json",
                           help="Path to ledger.json (default: portfolio/ledger.json)")
    p_migrate.add_argument("--dry-run", action="store_true",
                           help="Preview migration without writing")
    p_migrate.add_argument("--force", action="store_true",
                           help="Overwrite existing DB data")

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
        "report": cmd_report,
        "snapshot": cmd_snapshot,
        "refresh": cmd_refresh,
        "check": cmd_check,
        "history": cmd_history,
        "propose": cmd_propose,
        "review": cmd_review,
        "migrate": cmd_migrate,
    }

    fn = dispatch.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
