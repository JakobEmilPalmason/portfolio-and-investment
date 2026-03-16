"""
Daily portfolio snapshot engine.

Captures portfolio state to the portfolio_snapshots table once per trading day.
Designed for daily cron or manual invocation. Not a reporting module — recording only.
Reporting (QuantStats) is a separate concern.
"""
from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

import pandas as pd

from src.database import Database
from src.models import D, round_money
from src.portfolio_engine import PortfolioEngine
from src.price_fetcher import PriceFetcher, PriceNotAvailableError

logger = logging.getLogger(__name__)

# RAM safeguards for batch operations
MAX_BACKFILL_DAYS = 730       # Refuse backfills longer than 2 years
BACKFILL_CHUNK_DAYS = 90      # Fetch prices in 90-day windows to bound memory


def _is_trading_day(date_str: str) -> bool:
    """Returns False for weekends. Does not account for holidays."""
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return d.weekday() < 5


def _last_trading_day() -> str:
    """Today if weekday, otherwise most recent Friday."""
    today = date.today()
    if today.weekday() < 5:
        return today.strftime("%Y-%m-%d")
    days_back = today.weekday() - 4  # Saturday=1, Sunday=2
    return (today - timedelta(days=days_back)).strftime("%Y-%m-%d")


class SnapshotEngine:
    """Records daily portfolio snapshots to SQLite."""

    def __init__(
        self,
        engine: PortfolioEngine,
        fetcher: PriceFetcher,
        db: Database,
        benchmark_ticker: str = "SPY",
    ) -> None:
        self.engine = engine
        self.fetcher = fetcher
        self.db = db
        self.benchmark_ticker = benchmark_ticker

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def capture(self, snapshot_date: str | None = None) -> Optional[dict]:
        """Capture a single snapshot for the given date.

        Returns the snapshot dict on success, or None if price fetch failed.
        Idempotent — safe to call multiple times for the same date.
        """
        if snapshot_date is None:
            snapshot_date = _last_trading_day()

        if not _is_trading_day(snapshot_date):
            logger.warning("Skipping non-trading day %s", snapshot_date)
            return None

        portfolio = self.engine.load()
        initial_capital = portfolio.initial_capital
        if initial_capital == 0:
            logger.error("No initial capital found (missing INIT transaction)")
            return None

        cash = portfolio.cash
        open_positions = [
            (ticker, pos)
            for ticker, pos in portfolio.positions.items()
            if pos.status == "OPEN"
        ]

        # Fetch prices for every open position
        prices: dict[str, Decimal] = {}
        for ticker, pos in open_positions:
            try:
                prices[ticker] = self.fetcher.get_price_on_date(ticker, snapshot_date)
            except PriceNotAvailableError:
                logger.warning(
                    "Price fetch failed for %s on %s — skipping snapshot",
                    ticker, snapshot_date,
                )
                return None

        # Fetch benchmark
        try:
            benchmark_value = self.fetcher.get_price_on_date(
                self.benchmark_ticker, snapshot_date
            )
        except PriceNotAvailableError:
            logger.warning(
                "Benchmark %s price fetch failed for %s — skipping snapshot",
                self.benchmark_ticker, snapshot_date,
            )
            return None

        # Calculate portfolio values (all Decimal)
        positions_value = sum(
            (pos.shares * prices[ticker] for ticker, pos in open_positions),
            D("0"),
        )
        positions_value = round_money(positions_value)
        total_value = round_money(cash + positions_value)

        # Previous snapshot (for daily return calc)
        prev = self._get_previous_snapshot(snapshot_date)

        if prev is not None:
            prev_total = Decimal(str(prev["total_value"]))
            daily_return = (total_value / prev_total) - D("1") if prev_total != 0 else None
            prev_bench = prev.get("benchmark_value")
            if prev_bench is not None:
                prev_bench_dec = Decimal(str(prev_bench))
                benchmark_daily_return = (
                    (benchmark_value / prev_bench_dec) - D("1")
                    if prev_bench_dec != 0 else None
                )
            else:
                benchmark_daily_return = None
        else:
            daily_return = None
            benchmark_daily_return = None

        cumulative_return = (total_value / initial_capital) - D("1")

        if daily_return is not None and benchmark_daily_return is not None:
            excess_return = daily_return - benchmark_daily_return
        else:
            excess_return = None

        # Top 5 holdings by market value
        holdings = []
        for ticker, pos in open_positions:
            mv = round_money(pos.shares * prices[ticker])
            holdings.append({
                "ticker": ticker,
                "shares": float(pos.shares),
                "market_value": float(mv),
                "weight_pct": float(round_money(mv / total_value * D("100"))) if total_value != 0 else 0.0,
            })
        holdings.sort(key=lambda h: h["market_value"], reverse=True)
        top_holdings = holdings[:5]

        snapshot = {
            "snapshot_date": snapshot_date,
            "total_value": total_value,
            "cash": cash,
            "positions_value": positions_value,
            "num_positions": len(open_positions),
            "daily_return": daily_return,
            "cumulative_return": cumulative_return,
            "benchmark_ticker": self.benchmark_ticker,
            "benchmark_value": benchmark_value,
            "benchmark_daily_return": benchmark_daily_return,
            "excess_return": excess_return,
            "top_holdings_json": top_holdings,
        }

        self._upsert_snapshot(snapshot)
        logger.info(
            "Snapshot %s: total=%.2f cum_ret=%.4f",
            snapshot_date, float(total_value),
            float(cumulative_return) if cumulative_return is not None else 0.0,
        )

        # Return with float-cast values for caller convenience
        return {
            "snapshot_date": snapshot_date,
            "total_value": float(total_value),
            "cash": float(cash),
            "positions_value": float(positions_value),
            "num_positions": len(open_positions),
            "daily_return": float(daily_return) if daily_return is not None else None,
            "cumulative_return": float(cumulative_return),
            "benchmark_ticker": self.benchmark_ticker,
            "benchmark_value": float(benchmark_value),
            "benchmark_daily_return": float(benchmark_daily_return) if benchmark_daily_return is not None else None,
            "excess_return": float(excess_return) if excess_return is not None else None,
            "top_holdings": top_holdings,
        }

    def backfill(self, start_date: str, end_date: str) -> int:
        """Backfill snapshots for each trading day in [start_date, end_date].

        Processes in BACKFILL_CHUNK_DAYS windows to bound memory usage.
        Returns count of snapshots written.
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        total_days = (end_dt - start_dt).days

        if total_days > MAX_BACKFILL_DAYS:
            raise ValueError(
                f"Backfill range {total_days} days exceeds maximum of "
                f"{MAX_BACKFILL_DAYS} days. Split into smaller ranges."
            )

        portfolio = self.engine.load()
        tickers = [
            ticker for ticker, pos in portfolio.positions.items()
            if pos.status == "OPEN"
        ]
        tickers_to_fetch = tickers + [self.benchmark_ticker]

        count = 0
        chunk_start = start_dt

        while chunk_start <= end_dt:
            chunk_end = min(chunk_start + timedelta(days=BACKFILL_CHUNK_DAYS - 1), end_dt)
            chunk_start_str = chunk_start.strftime("%Y-%m-%d")
            chunk_end_str = chunk_end.strftime("%Y-%m-%d")

            # Fetch history for this chunk only (populates cache, then GC'd)
            for ticker in tickers_to_fetch:
                try:
                    self.fetcher.get_history(ticker, chunk_start_str, chunk_end_str)
                except PriceNotAvailableError:
                    logger.warning(
                        "History fetch failed for %s (%s to %s) — will skip affected dates",
                        ticker, chunk_start_str, chunk_end_str,
                    )

            # Capture snapshots for each trading day in this chunk
            current = chunk_start
            while current <= chunk_end:
                date_str = current.strftime("%Y-%m-%d")
                if _is_trading_day(date_str):
                    result = self.capture(date_str)
                    if result is not None:
                        count += 1
                current += timedelta(days=1)

            chunk_start = chunk_end + timedelta(days=1)

        logger.info("Backfill complete: %d snapshots written (%s to %s)", count, start_date, end_date)
        return count

    def get_return_series(self) -> pd.DataFrame:
        """Return a DataFrame suitable for QuantStats input.

        Columns: date, portfolio_return, benchmark_return.
        Only includes dates where both returns are non-null.
        """
        rows = self.db.conn.execute(
            """SELECT snapshot_date, daily_return, benchmark_daily_return
               FROM portfolio_snapshots
               WHERE daily_return IS NOT NULL
                 AND benchmark_daily_return IS NOT NULL
               ORDER BY snapshot_date""",
        ).fetchall()

        if not rows:
            return pd.DataFrame(columns=["date", "portfolio_return", "benchmark_return"])

        data = [
            {
                "date": r["snapshot_date"],
                "portfolio_return": r["daily_return"],
                "benchmark_return": r["benchmark_daily_return"],
            }
            for r in rows
        ]
        return pd.DataFrame(data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_previous_snapshot(self, before_date: str) -> Optional[dict]:
        """Get the most recent snapshot strictly before the given date."""
        row = self.db.conn.execute(
            "SELECT * FROM portfolio_snapshots WHERE snapshot_date < ? ORDER BY snapshot_date DESC LIMIT 1",
            (before_date,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def _upsert_snapshot(self, snapshot: dict) -> None:
        """Insert or update a snapshot row. Idempotent on snapshot_date."""
        # Convert Decimal → float and serialize JSON for storage
        top_holdings_json = snapshot.get("top_holdings_json")
        if top_holdings_json is not None and not isinstance(top_holdings_json, str):
            top_holdings_json = json.dumps(top_holdings_json)

        def _f(v):
            """Decimal or None → float or None."""
            if v is None:
                return None
            if isinstance(v, Decimal):
                return float(v)
            return v

        self.db.conn.execute(
            """INSERT INTO portfolio_snapshots
                   (snapshot_date, total_value, cash, positions_value,
                    num_positions, daily_return, cumulative_return,
                    benchmark_ticker, benchmark_value, benchmark_daily_return,
                    excess_return, top_holdings_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(snapshot_date) DO UPDATE SET
                    total_value = excluded.total_value,
                    cash = excluded.cash,
                    positions_value = excluded.positions_value,
                    num_positions = excluded.num_positions,
                    daily_return = excluded.daily_return,
                    cumulative_return = excluded.cumulative_return,
                    benchmark_ticker = excluded.benchmark_ticker,
                    benchmark_value = excluded.benchmark_value,
                    benchmark_daily_return = excluded.benchmark_daily_return,
                    excess_return = excluded.excess_return,
                    top_holdings_json = excluded.top_holdings_json""",
            (
                snapshot["snapshot_date"],
                _f(snapshot["total_value"]),
                _f(snapshot["cash"]),
                _f(snapshot["positions_value"]),
                snapshot["num_positions"],
                _f(snapshot.get("daily_return")),
                _f(snapshot.get("cumulative_return")),
                snapshot.get("benchmark_ticker", "SPY"),
                _f(snapshot.get("benchmark_value")),
                _f(snapshot.get("benchmark_daily_return")),
                _f(snapshot.get("excess_return")),
                top_holdings_json,
            ),
        )
        self.db.conn.commit()
