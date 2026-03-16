from __future__ import annotations

import json
import sqlite3
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.database import Database
from src.models import D, round_money
from src.portfolio_engine import POLICY, PortfolioEngine
from src.price_fetcher import PriceFetcher
from src.reporter import PerformanceReporter
from src.snapshot import SnapshotEngine

DEFAULT_DB_PATH = str(REPO_ROOT / "db" / "portfolio.db")
DEFAULT_REPO_ROOT = str(REPO_ROOT)
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
UMBRELLA_LABELS = {
    "circle_of_competence": "Circle of Competence",
    "competitive_advantage": "Competitive Advantage",
    "management": "Management",
    "business_economics": "Business Economics",
    "balance_sheet": "Balance Sheet",
    "valuation": "Valuation",
    "margin_of_safety": "Margin of Safety",
    "temperament": "Temperament",
}
QUEUE_STATE_COLORS = {
    "deep_research": "#c2410c",
    "watchlist": "#0f766e",
    "monitor_only": "#2563eb",
    "approved": "#15803d",
    "owned": "#14532d",
    "rejected": "#b91c1c",
    "inbox": "#6b7280",
}


def format_money(value: float | int | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.{decimals}f}"


def format_pct(value: float | int | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_ratio(value: float | int | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def queue_state_color(state: str | None) -> str:
    return QUEUE_STATE_COLORS.get((state or "").lower(), "#475569")


def _empty_positions_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "ticker",
            "company",
            "side",
            "shares",
            "cost_basis",
            "current_price",
            "current_value",
            "unrealized_pnl",
            "weight_pct",
            "sector",
        ]
    )


def _empty_performance_summary() -> dict[str, Any]:
    return {
        "cagr": None,
        "sharpe_ratio": None,
        "sortino_ratio": None,
        "max_drawdown": None,
        "alpha": None,
        "beta": None,
        "data_warning": None,
        "error": None,
    }


def _empty_portfolio_payload() -> dict[str, Any]:
    return {
        "summary": {
            "total_value": 0.0,
            "cash": 0.0,
            "deployed": 0.0,
            "gross_exposure": 0.0,
            "realized_pnl": 0.0,
            "position_count": 0,
        },
        "positions": _empty_positions_frame(),
        "allocation": pd.DataFrame(columns=["ticker", "current_value", "weight_pct"]),
        "sector_exposure": pd.DataFrame(columns=["sector", "gross_value", "weight_pct"]),
        "policy_flags": [],
        "price_fallbacks": [],
    }


def _empty_performance_payload() -> dict[str, Any]:
    return {
        "snapshot_count": 0,
        "returns_count": 0,
        "equity_curve": pd.DataFrame(
            columns=["date", "portfolio_cumulative_return", "benchmark_cumulative_return"]
        ),
        "summary": _empty_performance_summary(),
        "monthly_returns": pd.DataFrame(columns=MONTH_LABELS),
        "heatmap_ready": False,
    }


def _db_available(db_path: str) -> bool:
    path = Path(db_path)
    return path.exists() and path.stat().st_size > 0


def _round_float(value: Decimal | float | int) -> float:
    if isinstance(value, Decimal):
        return float(round_money(value))
    return float(round_money(Decimal(str(value))))


def _report_sort_key(item: dict[str, Any]) -> tuple[str, float]:
    return item.get("analysis_date") or "", item.get("mtime", 0.0)


def _load_queue_map(repo_root: str) -> dict[str, dict[str, Any]]:
    queue_path = Path(repo_root) / "queue" / "queue.json"
    if not queue_path.exists():
        return {}
    try:
        entries = json.loads(queue_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        entry.get("ticker"): entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("ticker")
    }


@st.cache_data(ttl=60, show_spinner=False)
def get_portfolio_data(db_path: str = DEFAULT_DB_PATH) -> dict[str, Any]:
    payload = _empty_portfolio_payload()
    if not _db_available(db_path):
        return payload

    try:
        with Database(db_path) as db:
            engine = PortfolioEngine(db)
            portfolio = engine.load()
            summary = engine.get_summary()
            current_values: dict[str, Decimal] = {}
            rows: list[dict[str, Any]] = []
            price_fallbacks: list[str] = []
            sector_totals: dict[str, Decimal] = {}
            deployed_value = D("0")
            gross_exposure = D("0")

            for ticker, position in portfolio.positions.items():
                if position.status != "OPEN":
                    continue

                cached_price = db.get_latest_cached_price(ticker)
                current_price = cached_price if cached_price is not None else position.avg_cost_basis
                if cached_price is None:
                    price_fallbacks.append(ticker)

                current_value = position.market_value(current_price)
                unrealized_pnl = (
                    round_money(position.total_cost - current_value)
                    if position.side == "SHORT"
                    else round_money(current_value - position.total_cost)
                )
                sector = position.sector or "Other"

                current_values[ticker] = current_value
                sector_totals[sector] = sector_totals.get(sector, D("0")) + current_value
                gross_exposure += current_value
                if position.side == "LONG":
                    deployed_value += current_value

                rows.append(
                    {
                        "ticker": ticker,
                        "company": position.company or ticker,
                        "side": position.side.title(),
                        "shares": float(position.shares),
                        "cost_basis": float(position.total_cost),
                        "current_price": float(current_price),
                        "current_value": float(current_value),
                        "unrealized_pnl": float(unrealized_pnl),
                        "weight_pct": 0.0,
                        "sector": sector,
                    }
                )

            total_value = round_money(portfolio.cash + sum(current_values.values(), D("0")))

            for row in rows:
                current_value = Decimal(str(row["current_value"]))
                row["weight_pct"] = (
                    float(round_money(current_value / total_value * D("100")))
                    if total_value > 0
                    else 0.0
                )

            positions_df = (
                pd.DataFrame(rows).sort_values("current_value", ascending=False).reset_index(drop=True)
                if rows
                else _empty_positions_frame()
            )
            allocation_df = (
                positions_df[["ticker", "current_value", "weight_pct"]].copy()
                if not positions_df.empty
                else pd.DataFrame(columns=["ticker", "current_value", "weight_pct"])
            )

            sector_rows = []
            for sector, value in sorted(sector_totals.items(), key=lambda item: item[1], reverse=True):
                sector_rows.append(
                    {
                        "sector": sector,
                        "gross_value": float(value),
                        "weight_pct": (
                            float(round_money(value / total_value * D("100")))
                            if total_value > 0
                            else 0.0
                        ),
                    }
                )
            sector_df = pd.DataFrame(sector_rows)

            policy_flags = []
            total_capital = Decimal(str(summary.get("total_capital", 0) or 0))
            for ticker, position in portfolio.positions.items():
                if position.status != "OPEN" or total_capital <= 0:
                    continue
                position_pct = round_money(position.total_cost / total_capital * D("100"))
                if position_pct > POLICY["single_name_hard_pct"]:
                    policy_flags.append(
                        {
                            "ticker": ticker,
                            "company": position.company or ticker,
                            "flag": f"overweight:{float(position_pct):.1f}%",
                            "weight_pct": float(position_pct),
                        }
                    )

            payload["summary"] = {
                "total_value": float(total_value),
                "cash": float(round_money(portfolio.cash)),
                "deployed": float(round_money(deployed_value)),
                "gross_exposure": float(round_money(gross_exposure)),
                "realized_pnl": float(summary.get("realized_pnl", 0.0)),
                "position_count": int(summary.get("position_count", 0)),
            }
            payload["positions"] = positions_df
            payload["allocation"] = allocation_df
            payload["sector_exposure"] = sector_df
            payload["policy_flags"] = policy_flags
            payload["price_fallbacks"] = sorted(price_fallbacks)
            return payload
    except sqlite3.OperationalError:
        return payload


@st.cache_data(ttl=60, show_spinner=False)
def get_performance_data(db_path: str = DEFAULT_DB_PATH) -> dict[str, Any]:
    payload = _empty_performance_payload()
    if not _db_available(db_path):
        return payload

    try:
        with Database(db_path) as db:
            snapshot_rows = db.conn.execute(
                """SELECT snapshot_date, total_value, cumulative_return, benchmark_value
                   FROM portfolio_snapshots
                   ORDER BY snapshot_date"""
            ).fetchall()

            if snapshot_rows:
                snapshot_df = pd.DataFrame([dict(row) for row in snapshot_rows])
                snapshot_df["date"] = pd.to_datetime(snapshot_df["snapshot_date"])
                snapshot_df["portfolio_cumulative_return"] = (
                    pd.to_numeric(snapshot_df["cumulative_return"], errors="coerce") * 100
                )

                benchmark_values = pd.to_numeric(snapshot_df["benchmark_value"], errors="coerce")
                if benchmark_values.notna().any():
                    first_benchmark = benchmark_values.dropna().iloc[0]
                    snapshot_df["benchmark_cumulative_return"] = (
                        (benchmark_values / first_benchmark) - 1
                    ) * 100
                else:
                    snapshot_df["benchmark_cumulative_return"] = pd.NA

                payload["snapshot_count"] = int(len(snapshot_df))
                payload["equity_curve"] = snapshot_df[
                    ["date", "portfolio_cumulative_return", "benchmark_cumulative_return"]
                ].copy()

            returns_rows = db.conn.execute(
                """SELECT snapshot_date AS date, daily_return AS portfolio_return,
                          benchmark_daily_return AS benchmark_return
                   FROM portfolio_snapshots
                   WHERE daily_return IS NOT NULL
                     AND benchmark_daily_return IS NOT NULL
                   ORDER BY snapshot_date"""
            ).fetchall()

            returns_df = pd.DataFrame([dict(row) for row in returns_rows]) if returns_rows else pd.DataFrame()
            payload["returns_count"] = int(len(returns_df))

            engine = PortfolioEngine(db)
            reporter = PerformanceReporter(
                SnapshotEngine(engine, PriceFetcher(db), db),
                engine,
            )
            try:
                summary = reporter.generate_summary()
            except RuntimeError as exc:
                summary = _empty_performance_summary()
                summary["error"] = str(exc)

            payload["summary"] = summary

            if len(returns_df) > 30:
                returns_df["date"] = pd.to_datetime(returns_df["date"])
                portfolio_returns = pd.Series(
                    pd.to_numeric(returns_df["portfolio_return"], errors="coerce").values,
                    index=pd.DatetimeIndex(returns_df["date"]),
                ).dropna()
                if not portfolio_returns.empty:
                    monthly_returns = ((1 + portfolio_returns).resample("ME").prod() - 1).to_frame("return")
                    monthly_returns["year"] = monthly_returns.index.year
                    monthly_returns["month"] = monthly_returns.index.month
                    heatmap = monthly_returns.pivot(index="year", columns="month", values="return")
                    heatmap = heatmap.reindex(columns=range(1, 13))
                    heatmap.columns = MONTH_LABELS
                    payload["monthly_returns"] = heatmap.sort_index()
                    payload["heatmap_ready"] = True

            return payload
    except sqlite3.OperationalError:
        return payload


@st.cache_data(ttl=60, show_spinner=False)
def get_research_catalog(repo_root: str = DEFAULT_REPO_ROOT) -> list[dict[str, Any]]:
    root = Path(repo_root)
    runs_dir = root / "runs"
    queue_map = _load_queue_map(repo_root)
    if not runs_dir.exists():
        return []

    best_by_ticker: dict[str, dict[str, Any]] = {}
    for report_path in runs_dir.glob("*/reports/*/FINAL-REPORT.json"):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        ticker = report.get("ticker") or report_path.parent.name
        md_path = report_path.parent / "FINAL-REPORT.md"
        item = {
            "ticker": ticker,
            "company": report.get("company") or ticker,
            "analysis_date": report.get("analysis_date"),
            "verdict": report.get("verdict"),
            "average_score": report.get("average_score"),
            "confidence": report.get("confidence"),
            "json_path": str(report_path),
            "md_path": str(md_path) if md_path.exists() else None,
            "mtime": report_path.stat().st_mtime,
            "queue_state": queue_map.get(ticker, {}).get("current_state"),
        }
        existing = best_by_ticker.get(ticker)
        if existing is None or _report_sort_key(item) > _report_sort_key(existing):
            best_by_ticker[ticker] = item

    return sorted(best_by_ticker.values(), key=lambda item: item["ticker"])


@st.cache_data(ttl=60, show_spinner=False)
def get_research_detail(ticker: str, repo_root: str = DEFAULT_REPO_ROOT) -> dict[str, Any] | None:
    catalog = get_research_catalog(repo_root)
    selected = next((item for item in catalog if item["ticker"] == ticker), None)
    if selected is None:
        return None

    queue_map = _load_queue_map(repo_root)
    report_path = Path(selected["json_path"])
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    md_text = None
    md_path = selected.get("md_path")
    if md_path:
        try:
            md_text = Path(md_path).read_text(encoding="utf-8")
        except OSError:
            md_text = None

    scores = report.get("umbrella_scores") or {}
    scores_rows = [
        {"Category": UMBRELLA_LABELS.get(key, key.replace("_", " ").title()), "Score": value}
        for key, value in scores.items()
    ]
    scores_df = pd.DataFrame(scores_rows)
    if not scores_df.empty:
        scores_df = scores_df.sort_values(["Category"]).reset_index(drop=True)

    return {
        "report": report,
        "queue": queue_map.get(ticker),
        "json_path": str(report_path),
        "md_path": md_path,
        "markdown": md_text,
        "scores": scores_df,
        "key_strengths": report.get("key_strengths") or [],
        "key_risks": report.get("key_risks") or [],
    }


__all__ = [
    "MONTH_LABELS",
    "UMBRELLA_LABELS",
    "format_money",
    "format_pct",
    "format_ratio",
    "get_performance_data",
    "get_portfolio_data",
    "get_research_catalog",
    "get_research_detail",
    "queue_state_color",
]
