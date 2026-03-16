"""
Portfolio engine — authoritative bridge between domain models and SQLite.

PortfolioEngine owns business logic: trade execution, FIFO lot tracking,
policy enforcement, and summary computation. Database owns persistence
(reads/writes to SQLite). The CLI layer (paper_trade.py) owns all I/O,
printing, and user interaction. This module must never print or read stdin.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from src.database import Database
from src.models import (
    D,
    Lot,
    Portfolio,
    Position,
    round_money,
    round_shares,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"

# ---------------------------------------------------------------------------
# Policy thresholds — ported verbatim from portfolio-ledger.py
# ---------------------------------------------------------------------------
POLICY = {
    "single_name_hard_pct": D("7.0"),
    "single_name_warn_pct": D("5.0"),
    "sector_gross_hard_pct": D("35.0"),
    "gross_exposure_hard_pct": D("130.0"),
    "net_exposure_max_pct": D("100.0"),
    "net_exposure_min_pct": D("-30.0"),
    "minimum_breadth": 5,
    "stale_analysis_days": 180,
}

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


# ---------------------------------------------------------------------------
# Module-level helpers (no I/O beyond reading JSON files on disk)
# ---------------------------------------------------------------------------

def _derive_sector(tags: list[str]) -> str:
    for tag in tags:
        if tag in TAG_SECTOR:
            return TAG_SECTOR[tag]
    return "Other"


def _find_report(ticker: str) -> Optional[dict]:
    candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _find_report_ref(ticker: str) -> Optional[str]:
    candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        return str(latest.relative_to(REPO_ROOT))
    except ValueError:
        return str(latest)


def _load_queue() -> list[dict]:
    if not QUEUE_FILE.exists():
        return []
    try:
        with open(QUEUE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _queue_entry(ticker: str) -> Optional[dict]:
    for entry in _load_queue():
        if entry.get("ticker") == ticker:
            return entry
    return None


# ---------------------------------------------------------------------------
# PortfolioEngine
# ---------------------------------------------------------------------------

class PortfolioEngine:
    """Authoritative bridge between domain models and SQLite persistence.

    Separation of concerns:
      - PortfolioEngine: business logic (trades, policy, summary).
      - Database: persistence (SQL reads/writes, schema migrations).
      - CLI (paper_trade.py): user interaction (args, printing, confirmation).
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> Portfolio:
        """Reconstruct a Portfolio from the positions and lots tables."""
        cash = self.db.get_portfolio_cash()

        # Get initial capital and inception date from the INIT transaction
        init_row = self.db.conn.execute(
            "SELECT net_value, timestamp FROM transactions "
            "WHERE action = 'INIT' ORDER BY timestamp ASC LIMIT 1"
        ).fetchone()
        initial_capital = D(str(init_row["net_value"])) if init_row else D("0")
        inception_date = init_row["timestamp"] if init_row else ""

        # Build positions with their lots
        pos_rows = self.db.get_open_positions()
        positions: dict[str, Position] = {}

        for pr in pos_rows:
            ticker = pr["ticker"]
            lot_rows = self.db.get_open_lots(ticker)
            lots = [
                Lot(
                    lot_id=lr["id"],
                    ticker=lr["ticker"],
                    shares=D(str(lr["shares"])),
                    cost_per_share=D(str(lr["cost_per_share"])),
                    purchase_date=lr["purchase_date"],
                    transaction_id=lr.get("transaction_id"),
                )
                for lr in lot_rows
            ]
            positions[ticker] = Position(
                ticker=ticker,
                company=pr.get("company") or "",
                sector=pr.get("sector") or "",
                side=pr.get("side", "LONG"),
                status=pr.get("status", "OPEN"),
                lots=lots,
                realized_pnl=D(str(pr.get("realized_pnl", 0))),
                entry_report_ref=pr.get("entry_report_ref") or "",
                thesis_summary=pr.get("thesis_summary") or "",
            )

        return Portfolio(
            cash=cash,
            positions=positions,
            inception_date=inception_date,
            initial_capital=initial_capital,
        )

    # ------------------------------------------------------------------
    # Policy
    # ------------------------------------------------------------------

    def check_policy(
        self,
        action: str,
        ticker: str,
        side: str,
        trade_value: Decimal,
        iv: Optional[Decimal] = None,
        price: Optional[Decimal] = None,
    ) -> list[dict]:
        """Check trade against investment policy rules.

        Returns a list of violation dicts, each with keys:
          rule     — rule identifier string
          severity — "hard" or "soft"
          message  — human-readable explanation

        The caller decides whether to block (hard always blocks,
        soft blocks unless the user forces).
        """
        violations: list[dict] = []
        portfolio = self.load()
        total_capital = portfolio.initial_capital + sum(
            (pos.realized_pnl for pos in portfolio.positions.values()),
            D("0"),
        )
        if total_capital == 0:
            total_capital = portfolio.initial_capital or D("1")

        # Current position value for this ticker
        existing = portfolio.positions.get(ticker)
        existing_cost = existing.total_cost if existing else D("0")

        # Post-trade position value
        new_position_value = existing_cost + trade_value
        new_position_pct = new_position_value / total_capital * D("100")

        # Exposure math
        deployed_long = D("0")
        deployed_short = D("0")
        for pos in portfolio.positions.values():
            if pos.status != "OPEN":
                continue
            if pos.side == "LONG":
                deployed_long += pos.total_cost
            else:
                deployed_short += pos.total_cost

        if side == "LONG":
            new_deployed_long = deployed_long + trade_value
            new_deployed_short = deployed_short
        else:
            new_deployed_long = deployed_long
            new_deployed_short = deployed_short + trade_value

        new_gross = new_deployed_long + new_deployed_short
        new_gross_pct = new_gross / total_capital * D("100")
        new_net = new_deployed_long - new_deployed_short
        new_net_pct = new_net / total_capital * D("100")

        # --- Single name hard limit ---
        if new_position_pct > POLICY["single_name_hard_pct"]:
            violations.append({
                "rule": "single_name_weight",
                "severity": "hard",
                "message": (
                    f"{ticker} would be {new_position_pct:.1f}% of portfolio "
                    f"(hard limit: {POLICY['single_name_hard_pct']}%)"
                ),
            })
        elif new_position_pct > POLICY["single_name_warn_pct"]:
            violations.append({
                "rule": "single_name_weight_warn",
                "severity": "soft",
                "message": (
                    f"{ticker} would be {new_position_pct:.1f}% of portfolio "
                    f"(warning at {POLICY['single_name_warn_pct']}%)"
                ),
            })

        # --- Sector gross limit ---
        sector = "Other"
        qe = _queue_entry(ticker)
        if qe:
            sector = _derive_sector(qe.get("tags", []))
        elif existing:
            sector = existing.sector or "Other"

        # Current sector gross exposure
        sector_gross = D("0")
        for pos in portfolio.positions.values():
            if pos.status == "OPEN" and pos.sector == sector:
                sector_gross += pos.total_cost
        sector_current_pct = sector_gross / total_capital * D("100")
        sector_add_pct = trade_value / total_capital * D("100")
        if sector_current_pct + sector_add_pct > POLICY["sector_gross_hard_pct"]:
            violations.append({
                "rule": "sector_gross_weight",
                "severity": "hard",
                "message": (
                    f"Sector '{sector}' would be "
                    f"{sector_current_pct + sector_add_pct:.1f}% gross "
                    f"(hard limit: {POLICY['sector_gross_hard_pct']}%)"
                ),
            })

        # --- Gross exposure ---
        if new_gross_pct > POLICY["gross_exposure_hard_pct"]:
            violations.append({
                "rule": "gross_exposure",
                "severity": "hard",
                "message": (
                    f"Gross exposure would be {new_gross_pct:.1f}% "
                    f"(hard limit: {POLICY['gross_exposure_hard_pct']}%)"
                ),
            })

        # --- Net exposure bounds ---
        if new_net_pct > POLICY["net_exposure_max_pct"]:
            violations.append({
                "rule": "net_exposure_max",
                "severity": "hard",
                "message": (
                    f"Net exposure would be {new_net_pct:.1f}% "
                    f"(hard limit: {POLICY['net_exposure_max_pct']}%)"
                ),
            })
        if new_net_pct < POLICY["net_exposure_min_pct"]:
            violations.append({
                "rule": "net_exposure_min",
                "severity": "hard",
                "message": (
                    f"Net exposure would be {new_net_pct:.1f}% "
                    f"(hard limit: {POLICY['net_exposure_min_pct']}%)"
                ),
            })

        # --- Buy/short-specific checks ---
        if action in ("buy", "short"):
            report = _find_report(ticker)
            if report:
                verdict = report.get("verdict", "")
                if verdict == "Pass" and side == "LONG":
                    violations.append({
                        "rule": "verdict_mismatch",
                        "severity": "hard",
                        "message": f"{ticker} has Pass verdict — cannot buy",
                    })
                # Stale analysis
                analysis_date = report.get("analysis_date", "")
                if analysis_date:
                    try:
                        days_old = (
                            datetime.now()
                            - datetime.strptime(analysis_date, "%Y-%m-%d")
                        ).days
                        if days_old > POLICY["stale_analysis_days"]:
                            violations.append({
                                "rule": "stale_analysis",
                                "severity": "soft",
                                "message": (
                                    f"{ticker} analysis is {days_old} days old "
                                    f"(warning at {POLICY['stale_analysis_days']})"
                                ),
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
                    "message": (
                        f"{ticker} thesis_status is "
                        f"'{qe['thesis_status']}' — cannot buy"
                    ),
                })

            # Margin of safety (long buys only)
            if (
                side == "LONG"
                and iv is not None
                and price is not None
                and iv > 0
            ):
                mos = (iv - price) / iv * D("100")
                if mos < 0:
                    violations.append({
                        "rule": "margin_of_safety",
                        "severity": "soft",
                        "message": (
                            f"{ticker} price ${price:.2f} exceeds IV estimate "
                            f"${iv:.2f} (MOS: {mos:.1f}%)"
                        ),
                    })

        # --- Sell/cover: minimum breadth ---
        if action in ("sell", "cover"):
            open_count = len(portfolio.open_tickers())
            if open_count - 1 < POLICY["minimum_breadth"]:
                violations.append({
                    "rule": "minimum_breadth",
                    "severity": "soft",
                    "message": (
                        f"Portfolio would have {open_count - 1} positions "
                        f"(warning at {POLICY['minimum_breadth']})"
                    ),
                })

        return violations

    # ------------------------------------------------------------------
    # Execute trades
    # ------------------------------------------------------------------

    def execute_buy(
        self,
        ticker: str,
        side: str,
        price: Decimal,
        shares: Decimal,
        iv: Optional[Decimal],
        reason: str,
        date: str,
        skip_policy: bool = False,
    ) -> dict:
        """Open or add to a long/short position.

        Returns a dict with keys: action, ticker, side, shares, price,
        trade_value, violations, position_id, transaction_id.
        """
        ticker = ticker.upper()
        side = side.upper()
        shares = round_shares(shares)
        price = round_money(price)
        trade_value = round_money(price * shares)

        # Policy check
        violations: list[dict] = []
        if not skip_policy:
            policy_action = "buy" if side == "LONG" else "short"
            violations = self.check_policy(
                policy_action, ticker, side, trade_value, iv=iv, price=price,
            )
            hard = [v for v in violations if v["severity"] == "hard"]
            if hard:
                return {
                    "action": "REFUSED",
                    "ticker": ticker,
                    "side": side,
                    "shares": shares,
                    "price": price,
                    "trade_value": trade_value,
                    "violations": violations,
                    "position_id": None,
                    "transaction_id": None,
                }

        # Context lookups
        qe = _queue_entry(ticker)
        report = _find_report(ticker)
        report_ref = _find_report_ref(ticker)
        company = ""
        if qe:
            company = qe.get("company", "")
        elif report:
            company = report.get("company", "")
        sector = _derive_sector(qe.get("tags", [])) if qe else "Other"
        verdict = report.get("verdict", "") if report else ""
        score = D(str(report.get("average_score", 0))) if report else D("0")

        # MOS at entry
        mos_at_entry: Optional[Decimal] = None
        if iv and iv > 0:
            if side == "LONG":
                mos_at_entry = round_money((iv - price) / iv * D("100"))
            else:
                mos_at_entry = round_money((price - iv) / price * D("100"))

        # Load current state
        portfolio = self.load()
        pre_trade_cash = portfolio.cash
        existing = portfolio.positions.get(ticker)

        if existing and existing.side == side and existing.status == "OPEN":
            action_name = "ADD"
        else:
            action_name = "BUY" if side == "LONG" else "SHORT_OPEN"

        # Upsert position
        if existing and existing.side == side and existing.status == "OPEN":
            new_shares = existing.shares + shares
            new_total_cost = existing.total_cost + trade_value
            new_avg = round_money(new_total_cost / new_shares)
            pos_id = self.db.upsert_position({
                "ticker": ticker,
                "company": company or existing.company,
                "sector": sector if sector != "Other" else existing.sector,
                "side": side,
                "status": "OPEN",
                "shares": new_shares,
                "avg_cost_basis": new_avg,
                "total_cost": new_total_cost,
                "realized_pnl": existing.realized_pnl,
                "first_entry_date": existing.lots[0].purchase_date if existing.lots else date,
                "last_update": date,
                "entry_report_ref": report_ref or existing.entry_report_ref,
                "thesis_summary": existing.thesis_summary,
            })
        else:
            pos_id = self.db.upsert_position({
                "ticker": ticker,
                "company": company,
                "sector": sector,
                "side": side,
                "status": "OPEN",
                "shares": shares,
                "avg_cost_basis": price,
                "total_cost": trade_value,
                "realized_pnl": D("0"),
                "first_entry_date": date,
                "last_update": date,
                "entry_report_ref": report_ref or "",
                "thesis_summary": "",
            })

        # Record transaction
        post_trade_cash = pre_trade_cash - trade_value if side == "LONG" else pre_trade_cash
        tx_id = self.db.insert_transaction({
            "timestamp": date,
            "run_id": None,
            "ticker": ticker,
            "action": action_name,
            "shares": shares,
            "price": price,
            "gross_value": trade_value,
            "fees": D("0"),
            "net_value": trade_value,
            "realized_pnl": D("0"),
            "reason": reason,
            "report_ref": report_ref,
            "pre_trade_cash": pre_trade_cash,
            "post_trade_cash": post_trade_cash,
            "position_id": pos_id,
        })

        # Insert lot
        self.db.insert_lot({
            "position_id": pos_id,
            "ticker": ticker,
            "shares": shares,
            "cost_per_share": price,
            "purchase_date": date,
            "transaction_id": tx_id,
        })

        return {
            "action": action_name,
            "ticker": ticker,
            "side": side,
            "shares": shares,
            "price": price,
            "trade_value": trade_value,
            "company": company,
            "sector": sector,
            "verdict": verdict,
            "score": score,
            "mos_at_entry": mos_at_entry,
            "violations": violations,
            "position_id": pos_id,
            "transaction_id": tx_id,
        }

    def execute_sell(
        self,
        ticker: str,
        price: Decimal,
        shares: Decimal,
        reason: str,
        date: str,
    ) -> dict:
        """Sell (partially or fully) a long position using FIFO lot matching."""
        ticker = ticker.upper()
        price = round_money(price)
        shares = round_shares(shares)
        trade_value = round_money(price * shares)

        portfolio = self.load()
        pos = portfolio.positions.get(ticker)
        if not pos or pos.side != "LONG" or pos.status != "OPEN":
            raise ValueError(f"No open LONG position for {ticker}")

        # FIFO
        realized_pnl, consumed = pos.remove_shares_fifo(shares, price)

        # Persist lot changes
        for lot, taken in consumed:
            new_lot_shares = round_shares(lot.shares - taken)
            if new_lot_shares <= 0:
                self.db.close_lot(lot.lot_id)
            else:
                self.db.update_lot_shares(lot.lot_id, new_lot_shares)

        remaining_shares = round_shares(pos.shares - shares)
        action_name = "SELL" if remaining_shares <= 0 else "TRIM"

        # Capture position_id before we might close the row
        pos_row = self.db.get_position(ticker)
        position_id = pos_row["id"] if pos_row else None

        # Update position
        if remaining_shares <= 0:
            # Close the position — update the existing OPEN row in place
            self.db.conn.execute(
                """UPDATE positions SET status = 'CLOSED', shares = 0,
                   avg_cost_basis = 0, total_cost = 0,
                   realized_pnl = ?, last_update = ?
                   WHERE ticker = ? AND status = 'OPEN'""",
                (float(pos.realized_pnl + realized_pnl), date, ticker),
            )
            self.db.conn.commit()
        else:
            # Recompute from remaining lots
            lot_rows = self.db.get_open_lots(ticker)
            remaining_cost = round_money(sum(
                (D(str(lr["shares"])) * D(str(lr["cost_per_share"]))
                 for lr in lot_rows),
                D("0"),
            ))
            new_avg = round_money(remaining_cost / remaining_shares) if remaining_shares > 0 else D("0")

            self.db.upsert_position({
                "ticker": ticker,
                "company": pos.company,
                "sector": pos.sector,
                "side": "LONG",
                "status": "OPEN",
                "shares": remaining_shares,
                "avg_cost_basis": new_avg,
                "total_cost": remaining_cost,
                "realized_pnl": pos.realized_pnl + realized_pnl,
                "first_entry_date": pos.lots[0].purchase_date if pos.lots else date,
                "last_update": date,
                "entry_report_ref": pos.entry_report_ref,
                "thesis_summary": pos.thesis_summary,
            })

        # Record transaction
        pre_trade_cash = portfolio.cash
        post_trade_cash = pre_trade_cash + trade_value

        tx_id = self.db.insert_transaction({
            "timestamp": date,
            "run_id": None,
            "ticker": ticker,
            "action": action_name,
            "shares": shares,
            "price": price,
            "gross_value": trade_value,
            "fees": D("0"),
            "net_value": trade_value,
            "realized_pnl": realized_pnl,
            "reason": reason,
            "report_ref": pos.entry_report_ref,
            "pre_trade_cash": pre_trade_cash,
            "post_trade_cash": post_trade_cash,
            "position_id": position_id,
        })

        return {
            "action": action_name,
            "ticker": ticker,
            "side": "LONG",
            "shares": shares,
            "price": price,
            "trade_value": trade_value,
            "realized_pnl": realized_pnl,
            "remaining_shares": remaining_shares,
            "transaction_id": tx_id,
        }

    def execute_short(
        self,
        ticker: str,
        price: Decimal,
        shares: Decimal,
        iv: Optional[Decimal],
        reason: str,
        date: str,
    ) -> dict:
        """Open or add to a short position."""
        return self.execute_buy(
            ticker, "SHORT", price, shares, iv, reason, date,
        )

    def execute_cover(
        self,
        ticker: str,
        price: Decimal,
        shares: Decimal,
        reason: str,
        date: str,
    ) -> dict:
        """Cover (partially or fully) a short position using FIFO lot matching.

        Short P&L is inverted: profit when cover_price < entry_price.
        """
        ticker = ticker.upper()
        price = round_money(price)
        shares = round_shares(shares)
        trade_value = round_money(price * shares)

        portfolio = self.load()
        pos = portfolio.positions.get(ticker)
        if not pos or pos.side != "SHORT" or pos.status != "OPEN":
            raise ValueError(f"No open SHORT position for {ticker}")

        # FIFO — returns (cover_price - entry_price) * shares, which is
        # negative when profitable for shorts. We negate it.
        raw_pnl, consumed = pos.remove_shares_fifo(shares, price)
        realized_pnl = round_money(-raw_pnl)

        # Persist lot changes
        for lot, taken in consumed:
            new_lot_shares = round_shares(lot.shares - taken)
            if new_lot_shares <= 0:
                self.db.close_lot(lot.lot_id)
            else:
                self.db.update_lot_shares(lot.lot_id, new_lot_shares)

        remaining_shares = round_shares(pos.shares - shares)
        action_name = "SHORT_CLOSE"

        # Capture position_id before we might close the row
        pos_row = self.db.get_position(ticker)
        position_id = pos_row["id"] if pos_row else None

        if remaining_shares <= 0:
            # Close the position — update the existing OPEN row in place
            self.db.conn.execute(
                """UPDATE positions SET status = 'CLOSED', shares = 0,
                   avg_cost_basis = 0, total_cost = 0,
                   realized_pnl = ?, last_update = ?
                   WHERE ticker = ? AND status = 'OPEN'""",
                (float(pos.realized_pnl + realized_pnl), date, ticker),
            )
            self.db.conn.commit()
        else:
            lot_rows = self.db.get_open_lots(ticker)
            remaining_cost = round_money(sum(
                (D(str(lr["shares"])) * D(str(lr["cost_per_share"]))
                 for lr in lot_rows),
                D("0"),
            ))
            new_avg = round_money(remaining_cost / remaining_shares) if remaining_shares > 0 else D("0")

            self.db.upsert_position({
                "ticker": ticker,
                "company": pos.company,
                "sector": pos.sector,
                "side": "SHORT",
                "status": "OPEN",
                "shares": remaining_shares,
                "avg_cost_basis": new_avg,
                "total_cost": remaining_cost,
                "realized_pnl": pos.realized_pnl + realized_pnl,
                "first_entry_date": pos.lots[0].purchase_date if pos.lots else date,
                "last_update": date,
                "entry_report_ref": pos.entry_report_ref,
                "thesis_summary": pos.thesis_summary,
            })

        pre_trade_cash = portfolio.cash
        # Shorts don't consume cash; covering doesn't return cash either
        post_trade_cash = pre_trade_cash

        tx_id = self.db.insert_transaction({
            "timestamp": date,
            "run_id": None,
            "ticker": ticker,
            "action": action_name,
            "shares": shares,
            "price": price,
            "gross_value": trade_value,
            "fees": D("0"),
            "net_value": trade_value,
            "realized_pnl": realized_pnl,
            "reason": reason,
            "report_ref": pos.entry_report_ref,
            "pre_trade_cash": pre_trade_cash,
            "post_trade_cash": post_trade_cash,
            "position_id": position_id,
        })

        return {
            "action": action_name,
            "ticker": ticker,
            "side": "SHORT",
            "shares": shares,
            "price": price,
            "trade_value": trade_value,
            "realized_pnl": realized_pnl,
            "remaining_shares": remaining_shares,
            "transaction_id": tx_id,
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Compute portfolio summary from current DB state.

        Returns a dict with exposure, cash, sector weights, and
        largest position — suitable for persistence or display.
        """
        portfolio = self.load()
        total_capital = portfolio.initial_capital + sum(
            (pos.realized_pnl for pos in portfolio.positions.values()),
            D("0"),
        )
        if total_capital == 0:
            total_capital = portfolio.initial_capital or D("1")

        deployed_long = D("0")
        deployed_short = D("0")
        long_count = 0
        short_count = 0

        sector_data: dict[str, dict] = {}

        for pos in portfolio.positions.values():
            if pos.status != "OPEN":
                continue
            s = pos.sector or "Other"
            if s not in sector_data:
                sector_data[s] = {"long": D("0"), "short": D("0"), "names": 0}
            sector_data[s]["names"] += 1

            if pos.side == "LONG":
                deployed_long += pos.total_cost
                sector_data[s]["long"] += pos.total_cost
                long_count += 1
            else:
                deployed_short += pos.total_cost
                sector_data[s]["short"] += pos.total_cost
                short_count += 1

        gross = deployed_long + deployed_short
        net = deployed_long - deployed_short
        cash = portfolio.cash

        sector_weights: dict[str, dict] = {}
        for s, d in sector_data.items():
            sector_weights[s] = {
                "gross_pct": float(round_money((d["long"] + d["short"]) / total_capital * D("100"))),
                "long_pct": float(round_money(d["long"] / total_capital * D("100"))),
                "short_pct": float(round_money(d["short"] / total_capital * D("100"))),
                "names": d["names"],
            }

        # Largest position
        largest_pct = D("0")
        largest_ticker = ""
        for pos in portfolio.positions.values():
            if pos.status != "OPEN":
                continue
            w = pos.total_cost / total_capital * D("100")
            if w > largest_pct:
                largest_pct = w
                largest_ticker = pos.ticker

        realized_pnl = sum(
            (pos.realized_pnl for pos in portfolio.positions.values()),
            D("0"),
        )

        return {
            "initial_capital": float(portfolio.initial_capital),
            "total_capital": float(total_capital),
            "deployed_long": float(round_money(deployed_long)),
            "deployed_short": float(round_money(deployed_short)),
            "gross_exposure": float(round_money(gross)),
            "gross_exposure_pct": float(round_money(gross / total_capital * D("100"))),
            "net_exposure": float(round_money(net)),
            "net_exposure_pct": float(round_money(net / total_capital * D("100"))),
            "cash_position": float(round_money(cash)),
            "cash_pct": float(round_money(cash / total_capital * D("100"))),
            "position_count": long_count + short_count,
            "long_count": long_count,
            "short_count": short_count,
            "realized_pnl": float(round_money(realized_pnl)),
            "sector_weights": sector_weights,
            "largest_position_pct": float(round_money(largest_pct)),
            "largest_position_ticker": largest_ticker,
        }
