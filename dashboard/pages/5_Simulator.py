from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import format_money, format_pct, get_latest_sim, get_sim_runs_data
from dashboard.theme import render_hero, render_kicker


def _holdings_table(positions: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(positions)
    if df.empty:
        return df
    columns = {
        "ticker": "Ticker",
        "company": "Company",
        "verdict": "Verdict",
        "average_score": "Avg Score",
        "confidence": "Confidence",
        "sector": "Sector",
        "weight_pct": "Weight %",
        "position_value": "Value",
    }
    available = {key: value for key, value in columns.items() if key in df.columns}
    return df.rename(columns=available)[[value for value in available.values()]]


def main() -> None:
    render_kicker("Hypothetical Allocation")
    st.title("Portfolio Simulator")

    sim = get_latest_sim()
    if sim is None:
        st.info("No sim runs recorded yet. Run `./run.sh portfolio` to populate.")
        return

    positions = sim.get("positions_json") or []
    concentration = sim.get("concentration_json") or {}

    render_hero(
        "Snapshot allocation lab",
        "Review the latest simulated portfolio, sector mix, and concentration stats before turning ideas into ledger entries.",
        [
            {"label": "Capital", "value": format_money(sim.get("capital")), "meta": "simulation capital", "tone": "tone-info"},
            {"label": "Positions", "value": str(sim.get("total_positions", 0)), "meta": "simulated holdings", "tone": "tone-accent"},
            {"label": "Min Verdict", "value": str(sim.get("min_verdict", "")), "meta": "screen floor", "tone": "tone-warning"},
            {"label": "HHI", "value": f"{concentration.get('hhi', 0):.0f}", "meta": "concentration score", "tone": "tone-danger"},
        ],
    )

    st.subheader("Holdings")
    if positions:
        holdings = _holdings_table(positions)
        st.dataframe(
            holdings.style.format(
                {
                    "Avg Score": "{:.1f}",
                    "Weight %": "{:.1f}%",
                    "Value": lambda value: format_money(value),
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No positions in this sim run.")

    sector_data = sim.get("sector_exposure_json") or []
    if sector_data:
        st.subheader("Sector exposure")
        sector_df = pd.DataFrame(sector_data)
        if "sector" in sector_df.columns and "weight_pct" in sector_df.columns:
            figure = px.bar(
                sector_df.sort_values("weight_pct", ascending=True),
                x="weight_pct",
                y="sector",
                orientation="h",
                labels={"weight_pct": "Weight %", "sector": ""},
                color="weight_pct",
                color_continuous_scale=["#292524", "#c15f3c"],
            )
            figure.update_layout(
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
            )
            st.plotly_chart(figure, use_container_width=True)

    if concentration:
        st.subheader("Concentration")
        cols = st.columns(4)
        cols[0].metric("Top 1", format_pct(concentration.get("top_1_pct")))
        cols[1].metric("Top 3", format_pct(concentration.get("top_3_pct")))
        cols[2].metric("Top 5", format_pct(concentration.get("top_5_pct")))
        cols[3].metric("Red Flags", concentration.get("total_red_flags", 0))

    st.subheader("Run history")
    runs = get_sim_runs_data(limit=10)
    if runs:
        history = pd.DataFrame(
            [
                {
                    "Date": run.get("run_at", "")[:19],
                    "Capital": run.get("capital"),
                    "Positions": run.get("total_positions"),
                    "Min Verdict": run.get("min_verdict"),
                }
                for run in runs
            ]
        )
        st.dataframe(
            history.style.format({"Capital": lambda value: format_money(value)}),
            use_container_width=True,
            hide_index=True,
        )

    st.caption(f"Latest run: {sim.get('run_at', 'N/A')}")


if __name__ == "__main__":
    main()
