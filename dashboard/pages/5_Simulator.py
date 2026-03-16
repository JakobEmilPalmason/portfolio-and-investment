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


def _holdings_table(positions: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(positions)
    if df.empty:
        return df
    cols = {
        "ticker": "Ticker",
        "company": "Company",
        "verdict": "Verdict",
        "average_score": "Avg Score",
        "confidence": "Confidence",
        "sector": "Sector",
        "weight_pct": "Weight %",
        "position_value": "Value",
    }
    available = {k: v for k, v in cols.items() if k in df.columns}
    return df.rename(columns=available)[[v for v in available.values()]]


def main() -> None:
    st.markdown(
        '<div class="dashboard-kicker">Hypothetical Allocation</div>',
        unsafe_allow_html=True,
    )
    st.title("Portfolio Simulator")

    sim = get_latest_sim()

    if sim is None:
        st.info("No sim runs recorded yet. Run `./run.sh portfolio` to populate.")
        return

    # Summary metrics
    positions = sim.get("positions_json") or []
    concentration = sim.get("concentration_json") or {}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Capital", format_money(sim.get("capital")))
    col2.metric("Positions", sim.get("total_positions", 0))
    col3.metric("Min Verdict", sim.get("min_verdict", ""))
    col4.metric("HHI", f"{concentration.get('hhi', 0):.0f}")

    # Holdings table
    st.subheader("Holdings")
    if positions:
        df = _holdings_table(positions)
        st.dataframe(
            df.style.format({
                "Avg Score": "{:.1f}",
                "Weight %": "{:.1f}%",
                "Value": lambda v: format_money(v),
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No positions in this sim run.")

    # Sector exposure
    st.subheader("Sector Exposure")
    sector_data = sim.get("sector_exposure_json") or []
    if sector_data:
        sector_df = pd.DataFrame(sector_data)
        if "sector" in sector_df.columns and "weight_pct" in sector_df.columns:
            fig = px.bar(
                sector_df.sort_values("weight_pct", ascending=True),
                x="weight_pct",
                y="sector",
                orientation="h",
                labels={"weight_pct": "Weight %", "sector": ""},
            )
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # Concentration stats
    if concentration:
        st.subheader("Concentration")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top 1", format_pct(concentration.get("top_1_pct")))
        c2.metric("Top 3", format_pct(concentration.get("top_3_pct")))
        c3.metric("Top 5", format_pct(concentration.get("top_5_pct")))
        c4.metric("Red Flags", concentration.get("total_red_flags", 0))

    # Run history
    st.subheader("Run History")
    runs = get_sim_runs_data(limit=10)
    if runs:
        history = pd.DataFrame([
            {
                "Date": r.get("run_at", "")[:19],
                "Capital": r.get("capital"),
                "Positions": r.get("total_positions"),
                "Min Verdict": r.get("min_verdict"),
            }
            for r in runs
        ])
        st.dataframe(
            history.style.format({"Capital": lambda v: format_money(v)}),
            use_container_width=True,
            hide_index=True,
        )

    st.caption(f"Latest run: {sim.get('run_at', 'N/A')}")


if __name__ == "__main__":
    main()
