from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import format_money, format_pct, get_prebuy_latest, get_prebuy_history


def _pass_fail(val) -> str:
    if val == 1:
        return "PASS"
    if val == 0:
        return "FAIL"
    return "N/A"


def _result_color(val: str) -> str:
    if val == "GO":
        return "color: #15803d; font-weight: 600;"
    if val == "NO-GO":
        return "color: #b91c1c; font-weight: 600;"
    return "color: #6b7280;"


def _c_color(val: str) -> str:
    if val == "PASS":
        return "color: #15803d; font-weight: 600;"
    if val == "FAIL":
        return "color: #b91c1c; font-weight: 600;"
    return "color: #6b7280;"


def _prebuy_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    display = df[
        ["ticker", "verdict", "average_score", "c1_display", "c2_display",
         "mos_pct", "current_price", "iv_conservative", "age_days", "result"]
    ].rename(columns={
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
    })

    return (
        display.style
        .format({
            "Avg Score": "{:.1f}",
            "MOS %": lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A",
            "Price": lambda v: format_money(v) if pd.notna(v) else "N/A",
            "IV (Bear)": lambda v: format_money(v) if pd.notna(v) else "N/A",
        })
        .map(_result_color, subset=["Result"])
        .map(_c_color, subset=["C1", "C2"])
    )


def main() -> None:
    st.markdown(
        '<div class="dashboard-kicker">Investment Readiness</div>',
        unsafe_allow_html=True,
    )
    st.title("Pre-Buy Checks")

    df = get_prebuy_latest()

    if df.empty:
        st.info("No pre-buy checks recorded yet. Run `./run.sh prebuy --own` to populate.")
        return

    # Add display columns
    df["c1_display"] = df["c1_pass"].apply(_pass_fail)
    df["c2_display"] = df["c2_pass"].apply(_pass_fail)

    # Metrics row
    total = len(df)
    c1_pass_count = (df["c1_pass"] == 1).sum()
    c2_pass_count = (df["c2_pass"] == 1).sum()
    go_count = (df["result"] == "GO").sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tickers Checked", total)
    col2.metric("C1 Pass", f"{c1_pass_count}/{total}")
    col3.metric("C2 Pass", f"{c2_pass_count}/{total}")
    col4.metric("GO", go_count)

    # Main table
    st.subheader("Latest Check per Ticker")
    st.dataframe(
        _prebuy_table(df),
        use_container_width=True,
        hide_index=True,
    )

    # Run timestamp
    if "run_at" in df.columns and not df["run_at"].empty:
        st.caption(f"Last check: {df['run_at'].iloc[0]}")

    # History for a selected ticker
    st.subheader("Historical MOS %")
    tickers = sorted(df["ticker"].unique())
    selected = st.selectbox("Select ticker", tickers)
    if selected:
        hist = get_prebuy_history(ticker=selected)
        if not hist.empty and hist["mos_pct"].notna().any():
            chart_data = hist[hist["mos_pct"].notna()][["run_at", "mos_pct"]].copy()
            chart_data = chart_data.sort_values("run_at")
            st.line_chart(chart_data.set_index("run_at")["mos_pct"])
        else:
            st.info(f"No MOS history for {selected} yet.")


if __name__ == "__main__":
    main()
