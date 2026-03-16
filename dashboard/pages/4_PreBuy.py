from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import format_money, get_prebuy_history, get_prebuy_latest
from dashboard.theme import render_hero, render_kicker


def _pass_fail(value: object) -> str:
    if value == 1:
        return "PASS"
    if value == 0:
        return "FAIL"
    return "N/A"


def main() -> None:
    render_kicker("Investment Readiness")
    st.title("Pre-Buy Checks")

    df = get_prebuy_latest()
    if df.empty:
        st.info("No pre-buy checks recorded yet. Run `./run.sh prebuy --own` to populate.")
        return

    df["c1_display"] = df["c1_pass"].apply(_pass_fail)
    df["c2_display"] = df["c2_pass"].apply(_pass_fail)

    total = len(df)
    c1_pass_count = int((df["c1_pass"] == 1).sum())
    c2_pass_count = int((df["c2_pass"] == 1).sum())
    go_count = int((df["result"] == "GO").sum())

    render_hero(
        "Readiness snapshot",
        "Monitor C1 quality and C2 valuation clearance across the current Own list before committing capital.",
        [
            {"label": "Tickers Checked", "value": str(total), "meta": "latest run per ticker", "tone": "tone-accent"},
            {"label": "C1 Pass", "value": f"{c1_pass_count}/{total}", "meta": "quality gate", "tone": "tone-positive"},
            {"label": "C2 Pass", "value": f"{c2_pass_count}/{total}", "meta": "valuation gate", "tone": "tone-warning"},
            {"label": "GO", "value": str(go_count), "meta": "clear to consider", "tone": "tone-info"},
        ],
    )

    display = df[
        [
            "ticker",
            "verdict",
            "average_score",
            "c1_display",
            "c2_display",
            "mos_pct",
            "current_price",
            "iv_conservative",
            "age_days",
            "result",
        ]
    ].rename(
        columns={
            "ticker": "Ticker",
            "verdict": "Verdict",
            "average_score": "Avg Score",
            "c1_display": "C1",
            "c2_display": "C2",
            "mos_pct": "MOS %",
            "current_price": "Price",
            "iv_conservative": "IV (Bear)",
            "age_days": "Age (d)",
            "result": "Result",
        }
    )
    st.subheader("Latest check per ticker")
    st.dataframe(
        display.style.format(
            {
                "Avg Score": "{:.1f}",
                "MOS %": lambda value: f"{value:.1f}%" if pd.notna(value) else "N/A",
                "Price": lambda value: format_money(value) if pd.notna(value) else "N/A",
                "IV (Bear)": lambda value: format_money(value) if pd.notna(value) else "N/A",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    if "run_at" in df.columns and not df["run_at"].empty:
        st.caption(f"Last check: {df['run_at'].iloc[0]}")

    st.subheader("Historical MOS %")
    tickers = sorted(df["ticker"].unique())
    selected = st.selectbox("Ticker", tickers)
    history = get_prebuy_history(ticker=selected)
    if not history.empty and history["mos_pct"].notna().any():
        chart_data = history[history["mos_pct"].notna()][["run_at", "mos_pct"]].copy().sort_values("run_at")
        st.line_chart(chart_data.set_index("run_at")["mos_pct"])
    else:
        st.info(f"No MOS history for {selected} yet.")


if __name__ == "__main__":
    main()
