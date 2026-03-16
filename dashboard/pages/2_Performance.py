from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import MONTH_LABELS, format_pct, format_ratio, get_performance_data
from dashboard.theme import render_hero, render_kicker

EMPTY_STATE_MESSAGE = "Take daily snapshots to build performance history - run: ./run.sh snapshot"


def _performance_chart(data: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["portfolio_cumulative_return"],
            mode="lines",
            name="Portfolio",
            line=dict(color="#c15f3c", width=3),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["benchmark_cumulative_return"],
            mode="lines",
            name="SPY",
            line=dict(color="#93c5fd", width=2.5),
        )
    )
    figure.update_layout(
        margin=dict(l=0, r=0, t=12, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return %",
        legend_title_text="Series",
    )
    figure.update_yaxes(ticksuffix="%")
    return figure


def _heatmap(data: pd.DataFrame) -> go.Figure:
    z_values = (data.fillna(0).values * 100).tolist()
    text_values = [
        ["" if pd.isna(value) else f"{value * 100:.1f}%" for value in row]
        for row in data.values
    ]
    figure = go.Figure(
        data=[
            go.Heatmap(
                z=z_values,
                x=MONTH_LABELS,
                y=data.index.astype(str).tolist(),
                colorscale=[
                    [0.0, "#7f1d1d"],
                    [0.5, "#1c1917"],
                    [1.0, "#14532d"],
                ],
                text=text_values,
                texttemplate="%{text}",
                hovertemplate="Year %{y}<br>%{x}: %{z:.2f}%<extra></extra>",
                zmid=0,
            )
        ]
    )
    figure.update_layout(margin=dict(l=0, r=0, t=12, b=0), paper_bgcolor="rgba(0,0,0,0)")
    return figure


def main() -> None:
    render_kicker("Historical Tracking")
    st.title("Performance")

    payload = get_performance_data()
    summary = payload["summary"]

    render_hero(
        "Portfolio vs. benchmark",
        "QuantStats-backed monitoring with a cumulative curve, return heatmap, and risk summary once snapshot history exists.",
        [
            {"label": "Snapshots", "value": str(payload["snapshot_count"]), "meta": "portfolio history points", "tone": "tone-accent"},
            {"label": "Returns", "value": str(payload["returns_count"]), "meta": "usable daily returns", "tone": "tone-info"},
            {"label": "CAGR", "value": format_pct(summary.get("cagr")), "meta": "annualized", "tone": "tone-positive"},
            {"label": "Max Drawdown", "value": format_pct(summary.get("max_drawdown")), "meta": "peak to trough", "tone": "tone-danger"},
        ],
    )

    if payload["snapshot_count"] < 5:
        st.info(EMPTY_STATE_MESSAGE)
        return

    st.subheader("Portfolio vs. SPY")
    st.plotly_chart(_performance_chart(payload["equity_curve"]), use_container_width=True)

    st.subheader("Risk and return summary")
    summary_rows = pd.DataFrame(
        [
            {"Metric": "CAGR", "Value": format_pct(summary.get("cagr"))},
            {"Metric": "Sharpe", "Value": format_ratio(summary.get("sharpe_ratio"))},
            {"Metric": "Sortino", "Value": format_ratio(summary.get("sortino_ratio"))},
            {"Metric": "Max Drawdown", "Value": format_pct(summary.get("max_drawdown"))},
            {"Metric": "Alpha", "Value": format_pct(summary.get("alpha"))},
            {"Metric": "Beta", "Value": format_ratio(summary.get("beta"))},
        ]
    )
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    if summary.get("data_warning"):
        st.caption(summary["data_warning"])
    if summary.get("error"):
        st.caption(summary["error"])

    if payload["heatmap_ready"] and not payload["monthly_returns"].empty:
        st.subheader("Monthly return heatmap")
        st.plotly_chart(_heatmap(payload["monthly_returns"]), use_container_width=True)


if __name__ == "__main__":
    main()
