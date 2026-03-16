"""
Human-approved trade proposal execution.

TradeExecutor reads pending proposals, executes them through PortfolioEngine,
and updates proposal status. It contains no CLI I/O.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from src.database import Database
from src.portfolio_engine import PortfolioEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dec(value) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


class TradeExecutor:
    """Execute or reject human-reviewed trade proposals."""

    def __init__(self, engine: PortfolioEngine, db: Database) -> None:
        self.engine = engine
        self.db = db

    def get_pending(self) -> list[dict]:
        return self.db.get_pending_proposals()

    def execute_proposal(self, proposal_id: int) -> dict:
        proposal = self.db.get_proposal(proposal_id)
        if proposal is None:
            raise ValueError(f"Proposal {proposal_id} not found.")
        if proposal.get("status") != "PENDING":
            raise ValueError(
                f"Proposal {proposal_id} is {proposal.get('status')}, not PENDING."
            )

        ticker = proposal["ticker"]
        action = proposal["proposed_action"]
        price = _dec(proposal.get("proposed_price"))
        shares = _dec(proposal.get("proposed_shares"))
        if price is None or shares is None or price <= 0 or shares <= 0:
            raise ValueError(f"Proposal {proposal_id} has invalid price or shares.")

        reason = proposal.get("rationale") or ""
        trade_date = _today_str()

        if action in {"BUY", "ADD"}:
            report = self._load_latest_report(ticker)
            iv = _dec(report.get("iv_conservative")) if report else None
            result = self.engine.execute_buy(
                ticker=ticker,
                side="LONG",
                price=price,
                shares=shares,
                iv=iv,
                reason=reason,
                date=trade_date,
                skip_policy=False,
            )
            if result.get("action") == "REFUSED":
                details = "; ".join(
                    violation.get("message", "")
                    for violation in result.get("violations", [])
                )
                raise RuntimeError(
                    f"Proposal {proposal_id} was refused by the policy engine. {details}"
                )
        elif action in {"SELL", "TRIM"}:
            result = self.engine.execute_sell(
                ticker=ticker,
                price=price,
                shares=shares,
                reason=reason,
                date=trade_date,
            )
        else:
            raise ValueError(f"Unsupported proposal action: {action}")

        now = _now_iso()
        self.db.update_proposal_status(
            proposal_id,
            "EXECUTED",
            reviewed_at=now,
            executed_at=now,
            transaction_id=result.get("transaction_id"),
        )

        return result

    def reject_proposal(self, proposal_id: int, reason: str) -> None:
        proposal = self.db.get_proposal(proposal_id)
        if proposal is None:
            raise ValueError(f"Proposal {proposal_id} not found.")
        if proposal.get("status") != "PENDING":
            raise ValueError(
                f"Proposal {proposal_id} is {proposal.get('status')}, not PENDING."
            )

        self.db.update_proposal_status(
            proposal_id,
            "REJECTED",
            reviewed_at=_now_iso(),
            review_note=reason,
        )

    def _load_latest_report(self, ticker: str) -> Optional[dict]:
        candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
        if not candidates:
            return None
        latest = max(candidates, key=lambda path: path.stat().st_mtime)
        try:
            with open(latest) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
