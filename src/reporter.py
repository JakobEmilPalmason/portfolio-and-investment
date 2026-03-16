"""
Portfolio performance reporting.

Generates QuantStats HTML tear sheets and CLI-friendly performance summaries
from the daily return series recorded by SnapshotEngine.
"""
from __future__ import annotations

import os
import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

from src.models import D, round_money
from src.portfolio_engine import PortfolioEngine
from src.price_fetcher import PriceNotAvailableError
from src.snapshot import SnapshotEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports" / "performance"
SUPPORTED_PERIODS = frozenset({"all", "1m", "3m", "6m", "1y", "ytd"})


def _import_quantstats():
    cache_root = Path(tempfile.gettempdir()) / "portfolio-and-investment-cache"
    mpl_dir = cache_root / "matplotlib"
    xdg_dir = cache_root / "xdg"
    mpl_dir.mkdir(parents=True, exist_ok=True)
    xdg_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_dir))

    try:
        import quantstats as qs
    except ImportError as exc:
        raise RuntimeError(
            "quantstats is required. Run: "
            "python3 -m pip install --user --break-system-packages quantstats"
        ) from exc
    return qs


def _fmt_money(value: float | None) -> str:
    if value is None:
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def _fmt_ratio(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def _print_table(rows: list[list[Any]], headers: list[str], col_widths: list[int]) -> None:
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    sep = "  ".join("-" * w for w in col_widths)
    print(header_line)
    print(sep)
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))


class PerformanceReporter:
    """Generate HTML and CLI-oriented performance reports."""

    def __init__(self, snapshot_engine: SnapshotEngine, engine: PortfolioEngine) -> None:
        self.snapshot_engine = snapshot_engine
        self.engine = engine
        self.db = engine.db

    def generate_html_report(self, output_path: str = None, period: str = "all") -> str:
        qs = _import_quantstats()
        returns_df = self._get_filtered_returns(period)
        returns, benchmark_returns = self._to_return_series(returns_df)

        if returns.empty:
            raise ValueError(f"No return data available for period '{period}'.")

        resolved_path = self._resolve_output_path(output_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        qs.reports.html(
            returns,
            benchmark=benchmark_returns,
            output=str(resolved_path),
            title="Portfolio Performance",
        )
        return self._display_path(resolved_path)

    def generate_summary(self) -> dict:
        summary = {
            "cagr": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "max_drawdown": None,
            "alpha": None,
            "beta": None,
            "total_return": None,
            "benchmark_total_return": None,
            "excess_return": None,
            "num_trades": self._count_trades(),
            "win_rate": None,
            "largest_win": None,
            "largest_loss": None,
        }

        returns_df = self.snapshot_engine.get_return_series()
        returns, benchmark_returns = self._to_return_series(returns_df)
        data_points = len(returns)

        if not returns.empty:
            qs = _import_quantstats()
            summary["cagr"] = self._safe_pct_metric(qs.stats.cagr, returns)
            summary["sharpe_ratio"] = self._safe_metric(qs.stats.sharpe, returns)
            summary["sortino_ratio"] = self._safe_metric(qs.stats.sortino, returns)
            summary["max_drawdown"] = self._safe_pct_metric(qs.stats.max_drawdown, returns)
            summary["total_return"] = self._safe_pct_metric(qs.stats.comp, returns)
            summary["benchmark_total_return"] = self._safe_pct_metric(
                qs.stats.comp, benchmark_returns
            )

            if (
                summary["total_return"] is not None
                and summary["benchmark_total_return"] is not None
            ):
                summary["excess_return"] = round(
                    summary["total_return"] - summary["benchmark_total_return"],
                    2,
                )

            greeks = self._safe_greeks(qs, returns, benchmark_returns)
            if greeks is not None:
                summary["alpha"] = self._ratio_to_pct(greeks.get("alpha"))
                summary["beta"] = self._clean_number(greeks.get("beta"))

        summary.update(self._closed_position_summary())

        if data_points < 20:
            summary["data_warning"] = (
                f"Only {data_points} return data points available; "
                "performance metrics may be unstable."
            )

        return summary

    def position_report(self) -> list[dict]:
        portfolio = self.engine.load()
        open_positions = [
            (ticker, pos)
            for ticker, pos in portfolio.positions.items()
            if pos.status == "OPEN"
        ]
        if not open_positions:
            return []

        latest_snapshot = self.db.get_latest_snapshot()
        snapshot_date = latest_snapshot["snapshot_date"] if latest_snapshot else None

        market_values: dict[str, Decimal] = {}
        reports: list[dict] = []

        for ticker, pos in open_positions:
            entry_date = self._entry_date(pos)
            days_held = self._days_held(entry_date)
            price = self._resolve_position_price(ticker, snapshot_date)

            current_value: Decimal | None = None
            unrealized_pnl: Decimal | None = None
            unrealized_pnl_pct: Decimal | None = None

            if price is not None:
                current_value = round_money(pos.shares * price)
                if pos.side == "SHORT":
                    unrealized_pnl = round_money(pos.total_cost - current_value)
                else:
                    unrealized_pnl = round_money(current_value - pos.total_cost)

                if pos.total_cost != 0:
                    unrealized_pnl_pct = round_money(
                        unrealized_pnl / pos.total_cost * D("100")
                    )

                market_values[ticker] = current_value

            reports.append(
                {
                    "ticker": ticker,
                    "entry_date": entry_date,
                    "days_held": days_held,
                    "cost_basis": float(pos.total_cost),
                    "current_value": float(current_value) if current_value is not None else None,
                    "unrealized_pnl": float(unrealized_pnl) if unrealized_pnl is not None else None,
                    "unrealized_pnl_pct": (
                        float(unrealized_pnl_pct) if unrealized_pnl_pct is not None else None
                    ),
                    "weight_pct": None,
                }
            )

        if len(market_values) == len(open_positions):
            total_value = round_money(
                portfolio.cash + sum(market_values.values(), D("0"))
            )
            if total_value != 0:
                for report in reports:
                    current_value = report["current_value"]
                    if current_value is None:
                        continue
                    weight_pct = round_money(
                        Decimal(str(current_value)) / total_value * D("100")
                    )
                    report["weight_pct"] = float(weight_pct)

        return reports

    def print_summary(self) -> None:
        summary = self.generate_summary()
        positions = self.position_report()

        print(f"\n{'=' * 72}")
        print("  PERFORMANCE REPORT")
        print(f"{'=' * 72}")

        rows = [
            ["CAGR", _fmt_pct(summary["cagr"])],
            ["Sharpe Ratio", _fmt_ratio(summary["sharpe_ratio"])],
            ["Sortino Ratio", _fmt_ratio(summary["sortino_ratio"])],
            ["Max Drawdown", _fmt_pct(summary["max_drawdown"])],
            ["Alpha", _fmt_pct(summary["alpha"])],
            ["Beta", _fmt_ratio(summary["beta"])],
            ["Total Return", _fmt_pct(summary["total_return"])],
            ["Benchmark Return", _fmt_pct(summary["benchmark_total_return"])],
            ["Excess Return", _fmt_pct(summary["excess_return"])],
            ["Trades", summary["num_trades"]],
            ["Win Rate", _fmt_pct(summary["win_rate"])],
            ["Largest Win", _fmt_money(summary["largest_win"])],
            ["Largest Loss", _fmt_money(summary["largest_loss"])],
        ]
        _print_table(rows, ["Metric", "Value"], [22, 18])

        if "data_warning" in summary:
            print(f"\n  WARNING: {summary['data_warning']}")

        if positions:
            print("\n-- Open Positions " + "-" * 54)
            table_rows = []
            for position in positions:
                table_rows.append(
                    [
                        position["ticker"],
                        position["entry_date"] or "N/A",
                        position["days_held"] if position["days_held"] is not None else "N/A",
                        _fmt_money(position["cost_basis"]),
                        _fmt_money(position["current_value"]),
                        _fmt_money(position["unrealized_pnl"]),
                        _fmt_pct(position["unrealized_pnl_pct"]),
                        _fmt_pct(position["weight_pct"]),
                    ]
                )
            _print_table(
                table_rows,
                [
                    "Ticker",
                    "Entry Date",
                    "Days",
                    "Cost Basis",
                    "Current",
                    "Unreal P&L",
                    "P&L %",
                    "Weight",
                ],
                [8, 10, 6, 10, 10, 12, 8, 8],
            )

        print(f"\n{'=' * 72}\n")

    def _count_trades(self) -> int:
        row = self.db.conn.execute(
            "SELECT COUNT(*) AS trade_count FROM transactions WHERE action != 'INIT'"
        ).fetchone()
        return int(row["trade_count"]) if row else 0

    def _closed_position_summary(self) -> dict:
        row = self.db.conn.execute(
            """SELECT
                   COUNT(*) AS total,
                   SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) AS wins,
                   MAX(realized_pnl) AS largest_win,
                   MIN(realized_pnl) AS largest_loss
               FROM positions WHERE status = 'CLOSED'"""
        ).fetchone()
        if not row or row["total"] == 0:
            return {
                "win_rate": None,
                "largest_win": None,
                "largest_loss": None,
            }
        return {
            "win_rate": round(row["wins"] / row["total"] * 100, 2),
            "largest_win": float(round_money(Decimal(str(row["largest_win"])))) if row["largest_win"] is not None and row["largest_win"] > 0 else None,
            "largest_loss": float(round_money(Decimal(str(row["largest_loss"])))) if row["largest_loss"] is not None and row["largest_loss"] < 0 else None,
        }

    def _resolve_position_price(
        self, ticker: str, snapshot_date: str | None
    ) -> Decimal | None:
        if snapshot_date:
            cached = self.db.get_cached_price(ticker, snapshot_date)
            if cached is not None:
                return cached

        cached_row = self.db.conn.execute(
            """SELECT close_price
               FROM price_cache
               WHERE ticker = ?
               ORDER BY price_date DESC
               LIMIT 1""",
            (ticker,),
        ).fetchone()
        if cached_row is not None and cached_row["close_price"] is not None:
            return Decimal(str(cached_row["close_price"]))

        try:
            return self.snapshot_engine.fetcher.get_latest_price(ticker)
        except PriceNotAvailableError:
            return None

    def _get_filtered_returns(self, period: str) -> pd.DataFrame:
        normalized = (period or "all").lower()
        if normalized not in SUPPORTED_PERIODS:
            supported = ", ".join(sorted(SUPPORTED_PERIODS))
            raise ValueError(f"Unsupported period '{period}'. Supported: {supported}")

        df = self.snapshot_engine.get_return_series()
        if df.empty or normalized == "all":
            return df

        dates = pd.to_datetime(df["date"])
        end_date = dates.max()

        if normalized == "ytd":
            start_date = pd.Timestamp(year=end_date.year, month=1, day=1)
        elif normalized.endswith("m"):
            months = int(normalized[:-1])
            start_date = end_date - pd.DateOffset(months=months)
        else:
            years = int(normalized[:-1])
            start_date = end_date - pd.DateOffset(years=years)

        return df[dates >= start_date].reset_index(drop=True)

    def _to_return_series(
        self, returns_df: pd.DataFrame
    ) -> tuple[pd.Series, pd.Series]:
        if returns_df.empty:
            empty_index = pd.DatetimeIndex([], name="date")
            return (
                pd.Series(dtype=float, index=empty_index, name="portfolio_return"),
                pd.Series(dtype=float, index=empty_index, name="benchmark_return"),
            )

        df = returns_df.assign(
            date=pd.to_datetime(returns_df["date"]),
            portfolio_return=pd.to_numeric(returns_df["portfolio_return"], errors="coerce"),
            benchmark_return=pd.to_numeric(returns_df["benchmark_return"], errors="coerce"),
        )
        df = df.dropna(subset=["portfolio_return", "benchmark_return"]).sort_values("date")
        idx = pd.DatetimeIndex(df["date"], name="date")
        return (
            pd.Series(df["portfolio_return"].values, index=idx, name="portfolio_return"),
            pd.Series(df["benchmark_return"].values, index=idx, name="benchmark_return"),
        )

    def _resolve_output_path(self, output_path: str | None) -> Path:
        if output_path:
            path = Path(output_path)
            return path if path.is_absolute() else REPO_ROOT / path

        filename = f"{date.today().strftime('%Y-%m-%d')}-tearsheet.html"
        return DEFAULT_REPORTS_DIR / filename

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return str(path)

    def _safe_metric(self, fn, *args, **kwargs) -> float | None:
        try:
            return self._clean_number(fn(*args, **kwargs))
        except Exception:
            return None

    def _safe_pct_metric(self, fn, *args, **kwargs) -> float | None:
        raw = self._safe_metric(fn, *args, **kwargs)
        return self._ratio_to_pct(raw)

    def _safe_greeks(
        self, qs, returns: pd.Series, benchmark_returns: pd.Series
    ) -> pd.Series | None:
        try:
            return qs.stats.greeks(
                returns, benchmark_returns, prepare_returns=False
            )
        except Exception:
            return None

    def _ratio_to_pct(self, value: Any) -> float | None:
        cleaned = self._clean_number(value)
        if cleaned is None:
            return None
        return round(cleaned * 100, 2)

    def _clean_number(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if pd.isna(numeric):
            return None
        if numeric == float("inf") or numeric == float("-inf"):
            return None
        return round(numeric, 4)

    def _entry_date(self, position) -> str | None:
        if not position.lots:
            return None
        return min(lot.purchase_date for lot in position.lots)

    def _days_held(self, entry_date: str | None) -> int | None:
        if not entry_date:
            return None
        try:
            entry_dt = datetime.strptime(entry_date, "%Y-%m-%d").date()
        except ValueError:
            return None
        return (date.today() - entry_dt).days


__all__ = ["PerformanceReporter"]
