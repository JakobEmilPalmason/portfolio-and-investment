from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.search_index import (  # noqa: E402
    build_index as build_search_index,
    get_index_stats as get_search_index_stats,
    search_documents,
)
from src.database import Database  # noqa: E402
from src.models import D, round_money  # noqa: E402
from src.portfolio_engine import POLICY, PortfolioEngine  # noqa: E402
from src.price_fetcher import PriceFetcher  # noqa: E402
from src.reporter import PerformanceReporter  # noqa: E402
from src.snapshot import SnapshotEngine  # noqa: E402

DEFAULT_DB_PATH = str(REPO_ROOT / "db" / "portfolio.db")
DEFAULT_REPO_ROOT = str(REPO_ROOT)
DEFAULT_AGENT_ALLOCATIONS_SUBDIR = "week13_23.03"
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
SCOREBOARD_ORDER = [
    "ticker",
    "company",
    "verdict",
    "average_score",
    "circle_of_competence",
    "competitive_advantage",
    "management",
    "business_economics",
    "balance_sheet",
    "valuation",
    "margin_of_safety",
    "temperament",
    "iv_conservative",
    "iv_base",
    "iv_bull",
    "mos_pct",
    "confidence",
    "red_flag_count",
    "analysis_date",
    "queue_state",
]
QUEUE_STATE_COLORS = {
    "deep_research": "#c15f3c",
    "watchlist": "#f59e0b",
    "monitor_only": "#22c55e",
    "approved": "#f8fafc",
    "owned": "#22c55e",
    "rejected": "#ef4444",
    "inbox": "#78716c",
    "triage": "#a855f7",
}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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
    return QUEUE_STATE_COLORS.get((state or "").lower(), "#57534e")


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
            "cash_pct": 0.0,
            "deployed": 0.0,
            "gross_exposure": 0.0,
            "gross_pct": 0.0,
            "net_exposure": 0.0,
            "net_pct": 0.0,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "total_pnl": 0.0,
            "position_count": 0,
            "long_count": 0,
            "short_count": 0,
            "capital": 0.0,
            "largest_position_ticker": "",
            "largest_position_pct": 0.0,
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


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _safe_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _report_sort_key(item: dict[str, Any]) -> tuple[str, float]:
    return item.get("analysis_date") or "", item.get("mtime", 0.0)


def _iter_week_dirs(repo_root: str | Path) -> list[Path]:
    root = Path(repo_root)
    runs_dir = root / "runs"
    if not runs_dir.exists():
        return []
    return sorted(
        [path for path in runs_dir.iterdir() if path.is_dir() and path.name.startswith("week")],
        key=lambda path: path.name,
        reverse=True,
    )


def _load_queue_entries(repo_root: str | Path) -> list[dict[str, Any]]:
    queue_file = Path(repo_root) / "queue" / "queue.json"
    entries = _read_json(queue_file, [])
    return [entry for entry in entries if isinstance(entry, dict) and entry.get("ticker")]


def _load_queue_map(repo_root: str) -> dict[str, dict[str, Any]]:
    return {entry["ticker"]: entry for entry in _load_queue_entries(repo_root)}


def _compute_freshness(last_date: str | None, today: date | None = None) -> tuple[str, int | None]:
    today = today or date.today()
    parsed = _safe_iso_date(last_date)
    if parsed is None:
        return "never", None
    days_since = (today - parsed).days
    if days_since < 7:
        return "fresh", days_since
    if days_since <= 30:
        return "aging", days_since
    return "stale", days_since


def _safe_round_money(value: Decimal | float | int) -> float:
    if isinstance(value, Decimal):
        return float(round_money(value))
    return float(round_money(Decimal(str(value))))


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
            unrealized_total = D("0")

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
                unrealized_total += unrealized_pnl
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

            sector_rows = [
                {
                    "sector": sector,
                    "gross_value": float(value),
                    "weight_pct": float(round_money(value / total_value * D("100"))) if total_value > 0 else 0.0,
                }
                for sector, value in sorted(sector_totals.items(), key=lambda item: item[1], reverse=True)
            ]
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

            realized_pnl = Decimal(str(summary.get("realized_pnl", 0.0) or 0.0))
            payload["summary"] = {
                "total_value": float(total_value),
                "cash": float(round_money(portfolio.cash)),
                "cash_pct": float(summary.get("cash_pct", 0.0)),
                "deployed": float(round_money(deployed_value)),
                "gross_exposure": float(round_money(gross_exposure)),
                "gross_pct": float(summary.get("gross_exposure_pct", 0.0)),
                "net_exposure": float(summary.get("net_exposure", 0.0)),
                "net_pct": float(summary.get("net_exposure_pct", 0.0)),
                "realized_pnl": float(realized_pnl),
                "unrealized_pnl": float(unrealized_total),
                "total_pnl": float(round_money(realized_pnl + unrealized_total)),
                "position_count": int(summary.get("position_count", 0)),
                "long_count": int(summary.get("long_count", 0)),
                "short_count": int(summary.get("short_count", 0)),
                "capital": float(summary.get("total_capital", 0.0)),
                "largest_position_ticker": summary.get("largest_position_ticker", ""),
                "largest_position_pct": float(summary.get("largest_position_pct", 0.0)),
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
    score_rows = [
        {
            "key": key,
            "Category": UMBRELLA_LABELS.get(key, key.replace("_", " ").title()),
            "Score": value,
        }
        for key, value in scores.items()
    ]
    scores_df = pd.DataFrame(score_rows)
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
        "red_flags": report.get("red_flags") or [],
        "buy_triggers": report.get("buy_triggers") or [],
        "sell_triggers": report.get("sell_triggers") or [],
    }


@st.cache_data(ttl=60, show_spinner=False)
def get_freshness_data(repo_root: str = DEFAULT_REPO_ROOT) -> dict[str, dict[str, Any]]:
    today = date.today()
    result: dict[str, dict[str, Any]] = {}
    for entry in _load_queue_entries(repo_root):
        ticker = entry["ticker"]
        status, days_since = _compute_freshness(entry.get("last_analysis_date"), today)
        financials_path = Path(repo_root) / "context" / ticker / "financials.md"
        financials_age_days = None
        if financials_path.exists():
            financials_age_days = (today - date.fromtimestamp(financials_path.stat().st_mtime)).days
        result[ticker] = {
            "last_analysis_date": entry.get("last_analysis_date"),
            "days_since": days_since,
            "has_financials": financials_path.exists(),
            "financials_age_days": financials_age_days,
            "status": status,
        }
    return result


@st.cache_data(ttl=60, show_spinner=False)
def get_queue_data(repo_root: str = DEFAULT_REPO_ROOT) -> pd.DataFrame:
    queue_entries = _load_queue_entries(repo_root)
    if not queue_entries:
        return pd.DataFrame()

    freshness = get_freshness_data(repo_root)
    report_map = {item["ticker"]: item for item in get_research_catalog(repo_root)}
    rows: list[dict[str, Any]] = []
    for entry in queue_entries:
        ticker = entry["ticker"]
        fresh = freshness.get(ticker, {})
        report = report_map.get(ticker, {})
        rows.append(
            {
                "ticker": ticker,
                "company": entry.get("company") or ticker,
                "current_state": entry.get("current_state", ""),
                "priority": entry.get("priority", ""),
                "current_verdict": entry.get("current_verdict", ""),
                "last_analysis_date": entry.get("last_analysis_date"),
                "last_triage_date": entry.get("last_triage_date"),
                "thesis_status": entry.get("thesis_status", ""),
                "next_required_action": entry.get("next_required_action", ""),
                "freshness_status": fresh.get("status", "never"),
                "days_since_analysis": fresh.get("days_since"),
                "has_financials": fresh.get("has_financials", False),
                "financials_age_days": fresh.get("financials_age_days"),
                "has_report": bool(report),
                "average_score": report.get("average_score"),
                "confidence": report.get("confidence"),
                "analysis_date": report.get("analysis_date"),
                "tags": ", ".join(entry.get("tags", [])),
                "owner_notes": entry.get("owner_notes", ""),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["priority_rank"] = df["priority"].str.lower().map(PRIORITY_ORDER).fillna(99)
    df["days_since_analysis"] = pd.to_numeric(df["days_since_analysis"], errors="coerce")
    return df.sort_values(
        ["priority_rank", "days_since_analysis", "ticker"],
        ascending=[True, False, True],
        na_position="last",
    ).reset_index(drop=True)


@st.cache_data(ttl=60, show_spinner=False)
def get_pipeline_data(repo_root: str = DEFAULT_REPO_ROOT) -> dict[str, Any]:
    result: dict[str, Any] = {"scan": None, "triage": None}
    week_dirs = _iter_week_dirs(repo_root)
    if not week_dirs:
        return result

    for week_dir in week_dirs:
        scan_meta = week_dir / "scan" / "scan-meta.json"
        if scan_meta.exists():
            result["scan"] = _read_json(scan_meta, None)
            if result["scan"] is not None:
                break

    for week_dir in week_dirs:
        triage_file = week_dir / "triage" / "triage.json"
        if not triage_file.exists():
            continue
        triage_entries = _read_json(triage_file, [])
        if not isinstance(triage_entries, list):
            continue

        triage_summary: dict[str, Any] = {
            "triage_date": week_dir.name,
            "b2": {},
            "deep_dive_shortlist": [],
        }
        for entry in triage_entries:
            if not isinstance(entry, dict):
                continue
            action = entry.get("next_action", "unknown")
            triage_summary["b2"][action] = triage_summary["b2"].get(action, 0) + 1
            if action in {"deep_dive", "refresh"}:
                triage_summary["deep_dive_shortlist"].append(
                    {
                        "ticker": entry.get("ticker"),
                        "company": entry.get("company"),
                        "next_action": action,
                        "reason": entry.get("reason_for_action", ""),
                    }
                )

        b1_file = week_dir / "triage" / "b1-results.json"
        if b1_file.exists():
            b1_entries = _read_json(b1_file, [])
            if isinstance(b1_entries, list):
                b1_counts: dict[str, int] = {}
                for entry in b1_entries:
                    if isinstance(entry, dict):
                        verdict = entry.get("b1_verdict", "unknown")
                        b1_counts[verdict] = b1_counts.get(verdict, 0) + 1
                triage_summary["b1"] = b1_counts
        result["triage"] = triage_summary
        break

    return result


@st.cache_data(ttl=60, show_spinner=False)
def get_scoreboard_data(repo_root: str = DEFAULT_REPO_ROOT) -> pd.DataFrame:
    queue_map = _load_queue_map(repo_root)
    best: dict[str, dict[str, Any]] = {}
    for report_path in Path(repo_root).glob("runs/*/reports/*/FINAL-REPORT.json"):
        report = _read_json(report_path, None)
        if not isinstance(report, dict):
            continue
        ticker = report.get("ticker") or report_path.parent.name
        scores = report.get("umbrella_scores") or {}
        item = {
            "ticker": ticker,
            "company": report.get("company") or ticker,
            "verdict": report.get("verdict"),
            "average_score": report.get("average_score"),
            "confidence": report.get("confidence"),
            "analysis_date": report.get("analysis_date"),
            "iv_conservative": report.get("iv_conservative"),
            "iv_base": report.get("iv_base"),
            "iv_bull": report.get("iv_bull"),
            "mos_pct": report.get("mos_at_analysis"),
            "red_flag_count": len(report.get("red_flags") or []),
            "queue_state": queue_map.get(ticker, {}).get("current_state"),
        }
        for key in UMBRELLA_LABELS:
            item[key] = scores.get(key)
        existing = best.get(ticker)
        if existing is None or (item.get("analysis_date") or "") >= (existing.get("analysis_date") or ""):
            best[ticker] = item

    if not best:
        return pd.DataFrame(columns=SCOREBOARD_ORDER)
    return pd.DataFrame(best.values()).reindex(columns=SCOREBOARD_ORDER).sort_values("ticker").reset_index(drop=True)


@st.cache_data(ttl=60, show_spinner=False)
def get_policy_markdown(repo_root: str = DEFAULT_REPO_ROOT) -> str | None:
    policy_path = Path(repo_root) / "INVESTMENT-POLICY.md"
    if not policy_path.exists():
        return None
    try:
        return policy_path.read_text(encoding="utf-8")
    except OSError:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def get_search_results(
    query: str,
    doc_type: str | None = None,
    repo_root: str = DEFAULT_REPO_ROOT,
    limit: int = 20,
) -> list[dict[str, Any]]:
    return search_documents(repo_root, query, doc_type=doc_type, limit=limit)


@st.cache_data(ttl=60, show_spinner=False)
def get_search_stats(repo_root: str = DEFAULT_REPO_ROOT) -> dict[str, Any]:
    return get_search_index_stats(repo_root)


def rebuild_search(repo_root: str = DEFAULT_REPO_ROOT) -> dict[str, Any]:
    started = datetime.now()
    indexed = build_search_index(repo_root)
    get_search_results.clear()
    get_search_stats.clear()
    duration_ms = int((datetime.now() - started).total_seconds() * 1000)
    return {"indexed": indexed, "duration_ms": duration_ms}


@st.cache_data(ttl=60, show_spinner=False)
def get_prebuy_latest(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    if not _db_available(db_path):
        return pd.DataFrame()
    try:
        with Database(db_path) as db:
            db.migrate()
            rows = db.conn.execute(
                """SELECT * FROM prebuy_checks
                   WHERE id IN (
                       SELECT MAX(id) FROM prebuy_checks GROUP BY ticker
                   )
                   ORDER BY ticker"""
            ).fetchall()
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def get_prebuy_history(
    db_path: str = DEFAULT_DB_PATH,
    ticker: str | None = None,
    limit: int = 200,
) -> pd.DataFrame:
    if not _db_available(db_path):
        return pd.DataFrame()
    try:
        with Database(db_path) as db:
            db.migrate()
            if ticker:
                rows = db.conn.execute(
                    "SELECT * FROM prebuy_checks WHERE ticker = ? ORDER BY run_at DESC LIMIT ?",
                    (ticker, limit),
                ).fetchall()
            else:
                rows = db.conn.execute(
                    "SELECT * FROM prebuy_checks ORDER BY run_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def get_sim_runs_data(
    db_path: str = DEFAULT_DB_PATH,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if not _db_available(db_path):
        return []
    try:
        with Database(db_path) as db:
            db.migrate()
            return db.get_sim_runs(limit=limit)
    except Exception:
        return []


@st.cache_data(ttl=60, show_spinner=False)
def get_latest_sim(db_path: str = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    runs = get_sim_runs_data(db_path, limit=1)
    return runs[0] if runs else None


def _friendly_agent_label(folder_name: str, proposal: dict[str, Any], meta: dict[str, Any]) -> str:
    explicit = meta.get("label")
    if explicit and explicit not in {"codex-fresh", "freeform-gross-100-v3"}:
        return str(explicit)

    known = {
        "chatgpt-normal-allocator-skill": "ChatGPT Allocator Skill",
        "chatgpt-plan-100p-allocation-free": "ChatGPT 100% Invested",
        "claude-allocator-skill": "Claude Allocator Skill",
        "claude-opus-independent": "Claude Opus Independent",
    }
    if folder_name in known:
        return known[folder_name]

    manager = proposal.get("manager")
    if manager:
        return str(manager)

    return folder_name.replace("-", " ").replace("_", " ").title()


def _parse_currency_amount(value: str) -> float:
    cleaned = re.sub(r"[^0-9.]", "", value or "")
    return float(cleaned) if cleaned else 0.0


def _parse_pct(value: str) -> float:
    cleaned = str(value or "").replace("%", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_markdown_table(md_text: str, header: str) -> list[list[str]]:
    if not md_text or header not in md_text:
        return []

    section = md_text.split(header, 1)[1]
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        if "---" in stripped:
            continue
        rows.append([part.strip() for part in stripped.strip("|").split("|")])
    return rows


def _parse_sector_map_from_markdown(md_text: str) -> dict[str, str]:
    sector_rows = _parse_markdown_table(md_text, "## Sector Exposure")
    sector_map: dict[str, str] = {}
    for row in sector_rows[1:]:
        if len(row) < 2:
            continue
        sector = row[0]
        tickers = [item.strip() for item in row[1].split(",")]
        for ticker in tickers:
            if ticker and ticker != "—":
                sector_map[ticker] = sector
    return sector_map


def _proposal_from_markdown(md_text: str, folder_name: str) -> dict[str, Any] | None:
    if not md_text:
        return None

    portfolio_rows = _parse_markdown_table(md_text, "## The Portfolio")
    if len(portfolio_rows) < 2:
        return None

    date_match = re.search(r"\*\*Date:\*\*\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", md_text)
    capital_match = re.search(r"\*\*Capital:\*\*\s*\$([0-9,]+)", md_text)
    manager_match = re.search(r"\*\*Manager:\*\*\s*(.+)", md_text)
    sector_map = _parse_sector_map_from_markdown(md_text)

    positions: list[dict[str, Any]] = []
    cash_amount = 0.0
    cash_weight = 0.0
    rank = 1

    for row in portfolio_rows[1:]:
        if len(row) < 6:
            continue
        ticker = row[1]
        company = row[2]
        weight_pct = _parse_pct(row[3])
        amount = _parse_currency_amount(row[4])

        if ticker in {"", "TOTAL"}:
            continue
        if ticker == "BIL":
            cash_amount = amount
            cash_weight = weight_pct
            continue

        positions.append(
            {
                "rank": rank,
                "ticker": ticker,
                "company": company,
                "verdict": "Own",
                "action": "BUY",
                "current_weight_pct": 0.0,
                "target_weight_pct": weight_pct,
                "weight_change_pct": weight_pct,
                "target_value": amount,
                "sector": sector_map.get(ticker, "Other"),
            }
        )
        rank += 1

    capital = int(capital_match.group(1).replace(",", "")) if capital_match else 0
    return {
        "proposal_date": date_match.group(1) if date_match else "",
        "capital": capital,
        "manager": manager_match.group(1).strip() if manager_match else folder_name,
        "positions": positions,
        "cash": {
            "amount": cash_amount,
            "weight_pct": cash_weight,
            "rationale": "Held as BIL cash equivalent in the independent markdown allocation.",
        },
        "risk_overlay": {
            "position_count": len(positions),
            "gross_exposure_pct": round(100.0 - cash_weight, 2),
        },
        "excluded_notable": [],
    }


@st.cache_data(ttl=60, show_spinner=False)
def get_agent_runs(
    repo_root: str = DEFAULT_REPO_ROOT,
    allocations_subdir: str = DEFAULT_AGENT_ALLOCATIONS_SUBDIR,
) -> list[dict[str, Any]]:
    """Load the dashboard allocator comparison set from one allocation directory."""
    root = Path(repo_root)
    runs: list[dict[str, Any]] = []
    alloc_dir = root / "portfolio" / "allocations" / allocations_subdir
    if not alloc_dir.is_dir():
        return runs

    SKIP_DIRS = {"chatgpt-plan-100p-allocation-free"}
    for run_dir in sorted(path for path in alloc_dir.iterdir() if path.is_dir()):
        if run_dir.name in SKIP_DIRS:
            continue
        proposal_path = run_dir / "allocation-proposal.json"
        meta_path = run_dir / "run-metadata.json"
        md_path = run_dir / "allocation-proposal.md"

        proposal = _read_json(proposal_path, None) if proposal_path.exists() else None
        if proposal is None and md_path.exists():
            try:
                proposal = _proposal_from_markdown(md_path.read_text(encoding="utf-8"), run_dir.name)
            except OSError:
                proposal = None
        if proposal is None:
            continue

        meta = _read_json(meta_path, {}) if meta_path.exists() else {}
        runs.append(_build_agent_record(proposal, meta, run_dir.name))

    runs.sort(key=lambda r: (r["proposal_date"], r["label"]))
    return runs


def _build_agent_record(proposal: dict, meta: dict, fallback_label: str) -> dict[str, Any]:
    positions = proposal.get("positions") or []
    cash = proposal.get("cash") or {}
    risk = proposal.get("risk_overlay") or {}
    own_wt = sum(p.get("target_weight_pct", 0) for p in positions if p.get("verdict") == "Own")
    watch_wt = sum(p.get("target_weight_pct", 0) for p in positions if p.get("verdict") == "Watch")
    scores = [p["average_score"] for p in positions if p.get("average_score")]
    top3 = [p["ticker"] for p in positions[:3]]
    return {
        "label": _friendly_agent_label(fallback_label, proposal, meta),
        "run_id": meta.get("run_id") or fallback_label,
        "proposal_date": proposal.get("proposal_date", ""),
        "capital": proposal.get("capital", 0),
        "positions": positions,
        "cash": cash,
        "risk_overlay": risk,
        "excluded_notable": proposal.get("excluded_notable") or [],
        "position_count": len(positions),
        "cash_weight_pct": cash.get("weight_pct", 0),
        "own_weight_pct": round(own_wt, 1),
        "watch_weight_pct": round(watch_wt, 1),
        "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "top_3_tickers": ", ".join(top3),
    }


def _extract_price_frame(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            return raw["Close"]
        if "Adj Close" in raw.columns.get_level_values(0):
            return raw["Adj Close"]
        return pd.DataFrame()

    price_col = "Close" if "Close" in raw.columns else "Adj Close" if "Adj Close" in raw.columns else None
    if not price_col:
        return pd.DataFrame()
    return raw[[price_col]].rename(columns={price_col: tickers[0]})


@st.cache_data(ttl=3600, show_spinner="Fetching prices…")
def get_agent_prices(tickers: tuple[str, ...], start_date: str, interval: str = "30m") -> pd.DataFrame:
    """Batch-fetch agent comparison prices. Uses 30-minute bars by default."""
    try:
        import yfinance as yf
    except ImportError:
        return pd.DataFrame()

    all_tickers = list(set(tickers) | {"SPY"})
    try:
        request: dict[str, Any] = {
            "tickers": all_tickers,
            "auto_adjust": True,
            "progress": False,
            "interval": interval,
        }
        if interval.endswith("m"):
            request["period"] = "5d"
        else:
            request["start"] = start_date
        raw = yf.download(**request)
    except Exception:
        return pd.DataFrame()

    close = _extract_price_frame(raw, all_tickers)
    if close.empty:
        return pd.DataFrame()

    close = close.ffill(limit=5)
    close.index = pd.to_datetime(close.index)
    if start_date:
        close = close.loc[close.index >= pd.Timestamp(start_date, tz="UTC").normalize()]
    return close


def _market_open_timestamp(prices_df: pd.DataFrame, proposal_date: str) -> pd.Timestamp | None:
    if prices_df.empty:
        return None

    target_day = pd.Timestamp(proposal_date, tz="UTC").normalize()
    if "SPY" in prices_df.columns:
        spy = prices_df["SPY"].dropna()
        same_day = spy[spy.index.normalize() == target_day]
        if not same_day.empty:
            return same_day.index[0]

    same_day_index = prices_df.index[prices_df.index.normalize() == target_day]
    if len(same_day_index) == 0:
        return None
    return same_day_index.min()


def _baseline_price(series: pd.Series, start_ts: pd.Timestamp) -> float | None:
    valid = series.loc[series.index >= start_ts].dropna()
    if valid.empty:
        return None
    return float(valid.iloc[0])


def compute_agent_returns(
    positions: list[dict],
    cash_weight_pct: float,
    prices_df: pd.DataFrame,
    proposal_date: str,
    start_ts: pd.Timestamp | None = None,
) -> pd.Series:
    """Compute weighted 30-minute return series for one agent from market open."""
    if prices_df.empty or not positions or start_ts is None:
        return pd.Series(dtype=float)

    timestamps = prices_df.index[prices_df.index >= start_ts]
    if len(timestamps) == 0:
        return pd.Series(dtype=float)

    entry_prices: dict[str, float] = {}
    for p in positions:
        ticker = p.get("ticker", "")
        if ticker in prices_df.columns:
            baseline = _baseline_price(prices_df[ticker], start_ts)
            if baseline and baseline > 0:
                entry_prices[ticker] = baseline

    returns = {}
    for ts in timestamps:
        period_return = 0.0
        for p in positions:
            ticker = p.get("ticker", "")
            weight = p.get("target_weight_pct", 0) / 100.0
            entry_price = entry_prices.get(ticker)
            if ticker not in prices_df.columns or not entry_price or entry_price <= 0:
                continue
            current = prices_df.loc[ts, ticker]
            if pd.isna(current):
                continue
            period_return += weight * (current / entry_price - 1)
        returns[ts] = period_return * 100
    return pd.Series(returns)


def compute_position_returns(
    positions: list[dict],
    prices_df: pd.DataFrame,
    proposal_date: str,
    start_ts: pd.Timestamp | None = None,
) -> list[dict]:
    """Compute per-position return metrics for one agent.

    Returns a list of dicts sorted by pct_change descending, each containing:
    ticker, company, verdict, sector, target_weight_pct, price_at_open,
    current_price, pct_change, dollar_pnl, contribution.
    """
    if prices_df.empty or not positions or start_ts is None:
        return []

    latest_ts = prices_df.index[-1] if len(prices_df) > 0 else None
    if latest_ts is None:
        return []

    results = []
    for p in positions:
        ticker = p.get("ticker", "")
        target_val = p.get("target_value", 0)
        weight = p.get("target_weight_pct", 0)
        entry = None

        current = 0.0
        has_price = False
        if ticker in prices_df.columns:
            entry = _baseline_price(prices_df[ticker], start_ts)
            if entry:
                current_series = prices_df[ticker].dropna()
                current_window = current_series.loc[current_series.index >= start_ts]
                if not current_window.empty:
                    current = float(current_window.iloc[-1])
                    has_price = True

        if not entry:
            entry = float(p.get("price_at_proposal", 0) or 0)
            current = entry

        pct = (current / entry - 1) * 100 if entry > 0 else 0.0
        dollar_pnl = target_val * pct / 100 if target_val else 0.0
        contribution = weight * pct / 100  # portfolio-level %

        results.append({
            "ticker": ticker,
            "company": p.get("company", ""),
            "verdict": p.get("verdict", ""),
            "sector": p.get("sector", ""),
            "target_weight_pct": weight,
            "price_at_open": round(entry, 2),
            "current_price": round(current, 2),
            "pct_change": round(pct, 2),
            "dollar_pnl": round(dollar_pnl, 2),
            "contribution": round(contribution, 2),
            "has_price": has_price,
            "confidence": p.get("confidence", ""),
            "average_score": p.get("average_score", 0),
            "rationale": p.get("rationale", ""),
        })

    results.sort(key=lambda r: r["pct_change"], reverse=True)
    return results


def build_consensus_matrix(runs: list[dict[str, Any]]) -> pd.DataFrame:
    """Build ticker × agent weight matrix. Rows sorted by frequency."""
    ticker_counts: dict[str, int] = {}
    data: dict[str, dict[str, float]] = {}

    for run in runs:
        label = run["label"]
        for p in run.get("positions") or []:
            t = p.get("ticker", "")
            if not t:
                continue
            ticker_counts[t] = ticker_counts.get(t, 0) + 1
            data.setdefault(t, {})[label] = p.get("target_weight_pct", 0)

    if not data:
        return pd.DataFrame()

    sorted_tickers = sorted(ticker_counts, key=lambda t: (-ticker_counts[t], t))
    labels = [r["label"] for r in runs]
    rows = []
    for t in sorted_tickers:
        row = {"Ticker": t}
        for lbl in labels:
            row[lbl] = data.get(t, {}).get(lbl, 0.0)
        row["Count"] = ticker_counts[t]
        row["Avg Weight"] = round(sum(data[t].values()) / len(runs), 2)
        rows.append(row)

    return pd.DataFrame(rows).set_index("Ticker")


__all__ = [
    "DEFAULT_AGENT_ALLOCATIONS_SUBDIR",
    "DEFAULT_DB_PATH",
    "DEFAULT_REPO_ROOT",
    "MONTH_LABELS",
    "SCOREBOARD_ORDER",
    "UMBRELLA_LABELS",
    "_market_open_timestamp",
    "build_consensus_matrix",
    "compute_agent_returns",
    "compute_position_returns",
    "format_money",
    "format_pct",
    "format_ratio",
    "get_agent_prices",
    "get_agent_runs",
    "get_freshness_data",
    "get_latest_sim",
    "get_performance_data",
    "get_policy_markdown",
    "get_portfolio_data",
    "get_prebuy_history",
    "get_prebuy_latest",
    "get_pipeline_data",
    "get_queue_data",
    "get_research_catalog",
    "get_research_detail",
    "get_scoreboard_data",
    "get_search_results",
    "get_search_stats",
    "get_sim_runs_data",
    "queue_state_color",
    "rebuild_search",
]
