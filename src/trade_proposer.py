"""
Trade proposal generation from pipeline outputs.

This module bridges the research pipeline and the portfolio ledger. It reads
FINAL-REPORT.json files plus queue/queue.json, surfaces suggested actions, and
stores them as PENDING rows in trade_proposals. It never executes trades.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from src.database import Database
from src.models import D, Position, round_money, round_shares
from src.portfolio_engine import PortfolioEngine
from src.price_fetcher import PriceFetcher, PriceNotAvailableError

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"

BUY_STATES = frozenset({"deep_research", "monitor_only", "approved"})
__all__ = ["TradeProposalGenerator"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dec(value) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


class TradeProposalGenerator:
    """Generate human-reviewed trade proposals from queue and report state."""

    def __init__(self, engine: PortfolioEngine, db: Database) -> None:
        self.engine = engine
        self.db = db
        self.fetcher = PriceFetcher(db)

    def generate_from_queue(self, capital: Decimal = None) -> list[dict]:
        capital_base = self._resolve_capital(capital)
        portfolio = self.engine.load()
        proposals: list[dict] = []

        for entry in self._load_queue():
            proposals.extend(
                self._evaluate_ticker(
                    ticker=(entry.get("ticker") or "").upper(),
                    capital_base=capital_base,
                    portfolio=portfolio,
                    queue_entry=entry,
                    require_queue_state=True,
                )
            )

        return proposals

    def generate_from_report(self, ticker: str, capital: Decimal = None) -> list[dict]:
        capital_base = self._resolve_capital(capital)
        portfolio = self.engine.load()
        normalized = ticker.upper()
        queue_entry = self._queue_entry(normalized)
        return self._evaluate_ticker(
            ticker=normalized,
            capital_base=capital_base,
            portfolio=portfolio,
            queue_entry=queue_entry,
            require_queue_state=False,
        )

    def get_pending_summary(self) -> list[dict]:
        capital_base = self._resolve_capital(required=False) or D("0")
        portfolio = self.engine.load()
        summaries: list[dict] = []

        for proposal in self.db.get_pending_proposals():
            ticker = proposal["ticker"]
            report, _ = self._load_latest_report(ticker)
            price = self._resolve_latest_price(ticker)
            position = portfolio.positions.get(ticker)
            current_weight = self._current_weight_pct(position, price, capital_base)
            rule_checks = proposal.get("rule_checks_json") or []

            summaries.append(
                {
                    "id": proposal["id"],
                    "ticker": ticker,
                    "action": proposal["proposed_action"],
                    "proposed_value": _dec(proposal.get("proposed_value")) or D("0"),
                    "current_weight_pct": current_weight,
                    "verdict": report.get("verdict") if report else None,
                    "avg_score": report.get("average_score") if report else None,
                    "rule_checks": {
                        "all_passed": bool(proposal.get("all_rules_passed")),
                        "warnings": sum(
                            1 for check in rule_checks if check.get("severity") == "soft"
                        ),
                        "blocks": sum(
                            1 for check in rule_checks if check.get("severity") == "hard"
                        ),
                    },
                    "created_at": proposal["created_at"],
                }
            )

        return summaries

    def _evaluate_ticker(
        self,
        ticker: str,
        capital_base: Decimal,
        portfolio,
        queue_entry: Optional[dict],
        require_queue_state: bool,
    ) -> list[dict]:
        if not ticker:
            return []

        report, report_path = self._load_latest_report(ticker)
        if report is None:
            return []

        queue_state = (queue_entry or {}).get("current_state")
        position = portfolio.positions.get(ticker)
        is_open_long = bool(position and position.status == "OPEN" and position.side == "LONG")
        if position and position.status == "OPEN" and position.side != "LONG":
            return []

        if require_queue_state and queue_state not in BUY_STATES | {"owned"}:
            return []

        price = self._resolve_latest_price(ticker)
        if price is None or price <= 0:
            return []

        current_weight = self._current_weight_pct(position, price, capital_base)
        verdict = report.get("verdict")

        if require_queue_state:
            if queue_state in BUY_STATES and verdict == "Own":
                if not is_open_long:
                    proposal = self._build_buy_proposal(
                        ticker=ticker,
                        report=report,
                        report_path=report_path,
                        queue_entry=queue_entry,
                        price=price,
                        capital_base=capital_base,
                        current_weight=current_weight,
                    )
                    return [proposal] if proposal else []

                if current_weight < D("3.0") and self._margin_of_safety_valid(report, price):
                    proposal = self._build_add_proposal(
                        ticker=ticker,
                        report=report,
                        report_path=report_path,
                        queue_entry=queue_entry,
                        position=position,
                        price=price,
                        capital_base=capital_base,
                        current_weight=current_weight,
                    )
                    return [proposal] if proposal else []

                return []

            if queue_state == "owned" and is_open_long:
                sell_proposal = None
                if verdict == "Pass":
                    sell_proposal = self._build_sell_proposal(
                        ticker=ticker,
                        report=report,
                        report_path=report_path,
                        queue_entry=queue_entry,
                        position=position,
                        price=price,
                        current_weight=current_weight,
                    )
                if sell_proposal:
                    return [sell_proposal]

                if current_weight > D("7.0"):
                    trim_proposal = self._build_trim_proposal(
                        ticker=ticker,
                        report=report,
                        report_path=report_path,
                        queue_entry=queue_entry,
                        position=position,
                        price=price,
                        capital_base=capital_base,
                        current_weight=current_weight,
                    )
                    return [trim_proposal] if trim_proposal else []

            return []

        if verdict == "Own":
            if not is_open_long:
                proposal = self._build_buy_proposal(
                    ticker=ticker,
                    report=report,
                    report_path=report_path,
                    queue_entry=queue_entry,
                    price=price,
                    capital_base=capital_base,
                    current_weight=current_weight,
                )
                return [proposal] if proposal else []

            if current_weight < D("3.0") and self._margin_of_safety_valid(report, price):
                proposal = self._build_add_proposal(
                    ticker=ticker,
                    report=report,
                    report_path=report_path,
                    queue_entry=queue_entry,
                    position=position,
                    price=price,
                    capital_base=capital_base,
                    current_weight=current_weight,
                )
                return [proposal] if proposal else []

        if is_open_long and verdict == "Pass":
            proposal = self._build_sell_proposal(
                ticker=ticker,
                report=report,
                report_path=report_path,
                queue_entry=queue_entry,
                position=position,
                price=price,
                current_weight=current_weight,
            )
            return [proposal] if proposal else []

        if is_open_long and current_weight > D("7.0"):
            proposal = self._build_trim_proposal(
                ticker=ticker,
                report=report,
                report_path=report_path,
                queue_entry=queue_entry,
                position=position,
                price=price,
                capital_base=capital_base,
                current_weight=current_weight,
            )
            return [proposal] if proposal else []

        return []

    def _build_buy_proposal(
        self,
        ticker: str,
        report: dict,
        report_path: Optional[Path],
        queue_entry: Optional[dict],
        price: Decimal,
        capital_base: Decimal,
        current_weight: Decimal,
    ) -> Optional[dict]:
        target_value = round_money(capital_base * D("0.03"))
        shares = round_shares(target_value / price)
        if shares <= 0:
            return None

        company = (queue_entry or {}).get("company") or report.get("company") or ticker
        return self._store_proposal(
            ticker=ticker,
            action="BUY",
            price=price,
            shares=shares,
            report=report,
            report_path=report_path,
            rationale=(
                f"{company} has an Own verdict in the latest FINAL-REPORT and is not "
                "currently held. Suggest initiating at the 3% starter size."
            ),
            sizing_method="initial_3pct",
            target_weight_pct=D("3.0"),
            current_weight=current_weight,
        )

    def _build_add_proposal(
        self,
        ticker: str,
        report: dict,
        report_path: Optional[Path],
        queue_entry: Optional[dict],
        position: Position,
        price: Decimal,
        capital_base: Decimal,
        current_weight: Decimal,
    ) -> Optional[dict]:
        current_value = round_money(position.shares * price)
        target_value = round_money(capital_base * D("0.03"))
        add_value = round_money(target_value - current_value)
        if add_value <= 0:
            return None

        shares = round_shares(add_value / price)
        if shares <= 0:
            return None

        company = (queue_entry or {}).get("company") or report.get("company") or ticker
        return self._store_proposal(
            ticker=ticker,
            action="ADD",
            price=price,
            shares=shares,
            report=report,
            report_path=report_path,
            rationale=(
                f"{company} remains below the 3% target size and the latest report still "
                "shows a valid margin of safety from numeric IV data. Suggest adding up "
                "to the 3% target."
            ),
            sizing_method="add_to_3pct",
            target_weight_pct=D("3.0"),
            current_weight=current_weight,
        )

    def _build_sell_proposal(
        self,
        ticker: str,
        report: dict,
        report_path: Optional[Path],
        queue_entry: Optional[dict],
        position: Position,
        price: Decimal,
        current_weight: Decimal,
    ) -> Optional[dict]:
        company = (queue_entry or {}).get("company") or report.get("company") or ticker
        return self._store_proposal(
            ticker=ticker,
            action="SELL",
            price=price,
            shares=position.shares,
            report=report,
            report_path=report_path,
            rationale=(
                f"{company} is currently held, but the latest FINAL-REPORT verdict is Pass. "
                "Suggest exiting the position for human review."
            ),
            sizing_method="full_exit_pass_verdict",
            target_weight_pct=D("0"),
            current_weight=current_weight,
        )

    def _build_trim_proposal(
        self,
        ticker: str,
        report: dict,
        report_path: Optional[Path],
        queue_entry: Optional[dict],
        position: Position,
        price: Decimal,
        capital_base: Decimal,
        current_weight: Decimal,
    ) -> Optional[dict]:
        current_value = round_money(position.shares * price)
        target_value = round_money(capital_base * D("0.05"))
        trim_value = round_money(current_value - target_value)
        if trim_value <= 0:
            return None

        shares = round_shares(trim_value / price)
        if shares <= 0 or shares >= position.shares:
            return None

        company = (queue_entry or {}).get("company") or report.get("company") or ticker
        return self._store_proposal(
            ticker=ticker,
            action="TRIM",
            price=price,
            shares=shares,
            report=report,
            report_path=report_path,
            rationale=(
                f"{company} is above the 7% max size threshold. Suggest trimming the "
                "position back toward a 5% target weight."
            ),
            sizing_method="trim_to_5pct",
            target_weight_pct=D("5.0"),
            current_weight=current_weight,
        )

    def _store_proposal(
        self,
        ticker: str,
        action: str,
        price: Decimal,
        shares: Decimal,
        report: dict,
        report_path: Optional[Path],
        rationale: str,
        sizing_method: str,
        target_weight_pct: Decimal,
        current_weight: Decimal,
    ) -> Optional[dict]:
        if self.db.get_pending_proposal(ticker, action):
            return None

        proposed_shares = round_shares(shares)
        proposed_price = round_money(price)
        proposed_value = round_money(proposed_shares * proposed_price)
        if proposed_shares <= 0 or proposed_value <= 0:
            return None

        iv = _dec(report.get("iv_conservative"))
        policy_action = "buy" if action in {"BUY", "ADD"} else "sell"
        rule_checks = self.engine.check_policy(
            policy_action,
            ticker,
            "LONG",
            proposed_value,
            iv=iv,
            price=proposed_price,
        )

        proposal = {
            "created_at": _now_iso(),
            "run_id": self._run_id_from_path(report_path),
            "ticker": ticker,
            "proposed_action": action,
            "proposed_shares": proposed_shares,
            "proposed_price": proposed_price,
            "proposed_value": proposed_value,
            "target_weight_pct": target_weight_pct,
            "rationale": rationale,
            "sizing_method": sizing_method,
            "rule_checks_json": rule_checks,
            "all_rules_passed": 1 if not rule_checks else 0,
            "status": "PENDING",
        }
        proposal_id = self.db.insert_proposal(proposal)

        return {
            "id": proposal_id,
            "ticker": ticker,
            "action": action,
            "proposed_shares": proposed_shares,
            "proposed_price": proposed_price,
            "proposed_value": proposed_value,
            "target_weight_pct": target_weight_pct,
            "current_weight_pct": current_weight,
            "verdict": report.get("verdict"),
            "avg_score": report.get("average_score"),
            "rationale": rationale,
            "sizing_method": sizing_method,
            "rule_checks_json": rule_checks,
            "all_rules_passed": bool(proposal["all_rules_passed"]),
            "created_at": proposal["created_at"],
        }

    def _resolve_capital(
        self,
        capital: Decimal = None,
        required: bool = True,
    ) -> Optional[Decimal]:
        if capital is not None:
            parsed = _dec(capital)
            if parsed is None or parsed <= 0:
                raise ValueError("capital must be a positive Decimal value.")
            return parsed

        row = self.db.conn.execute(
            """SELECT net_value
               FROM transactions
               WHERE action = 'INIT'
               ORDER BY timestamp ASC
               LIMIT 1"""
        ).fetchone()
        if row is None or row["net_value"] is None:
            if required:
                raise ValueError("Portfolio is not initialized; no INIT transaction found.")
            return None
        return Decimal(str(row["net_value"]))

    def _resolve_latest_price(self, ticker: str) -> Optional[Decimal]:
        latest_snapshot = self.db.get_latest_snapshot()
        if latest_snapshot:
            cached = self.db.get_cached_price(ticker, latest_snapshot["snapshot_date"])
            if cached is not None:
                return cached

        cached = self.db.get_latest_cached_price(ticker)
        if cached is not None:
            return cached

        try:
            return self.fetcher.get_latest_price(ticker)
        except PriceNotAvailableError:
            return None

    def _current_weight_pct(
        self,
        position: Optional[Position],
        price: Optional[Decimal],
        capital_base: Decimal,
    ) -> Decimal:
        if (
            position is None
            or position.status != "OPEN"
            or position.side != "LONG"
            or price is None
            or capital_base <= 0
        ):
            return D("0")
        market_value = round_money(position.shares * price)
        return round_money(market_value / capital_base * D("100"))

    def _margin_of_safety_valid(self, report: dict, price: Decimal) -> bool:
        iv = _dec(report.get("iv_conservative"))
        if iv is None or iv <= 0:
            return False
        mos = (iv - price) / iv * D("100")
        return mos >= D("20")

    def _load_queue(self) -> list[dict]:
        if not QUEUE_FILE.exists():
            return []
        try:
            with open(QUEUE_FILE) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

    def _queue_entry(self, ticker: str) -> Optional[dict]:
        for entry in self._load_queue():
            if entry.get("ticker", "").upper() == ticker.upper():
                return entry
        return None

    def _load_latest_report(self, ticker: str) -> tuple[Optional[dict], Optional[Path]]:
        candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
        if not candidates:
            return None, None
        latest = max(candidates, key=lambda path: path.stat().st_mtime)
        try:
            with open(latest) as f:
                return json.load(f), latest
        except (OSError, json.JSONDecodeError):
            return None, None

    def _run_id_from_path(self, report_path: Optional[Path]) -> Optional[str]:
        if report_path is None:
            return None
        try:
            return report_path.parent.parent.parent.name
        except IndexError:
            return None
