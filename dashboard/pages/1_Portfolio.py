from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import format_money, format_pct, get_portfolio_data


def _portfolio_table(data: pd.DataFrame) -> pd.io.formats.style.Styler:
    display = data.rename(
        columns={
            "ticker": "Ticker",
            "company": "Company",
            "side": "Side",
            "shares": "Shares",
            "cost_basis": "Cost Basis",
            "current_price": "Current Price",
            "unrealized_pnl": "Unrealized P&L",
            "weight_pct": "Weight %",
        }
    )[
        ["Ticker", "Company", "Side", "Shares", "Cost Basis", "Current Price", "Unrealized P&L", "Weight %"]
    ]

    return (
        display.style.format(
            {
                "Shares": "{:,.4f}",
                "Cost Basis": lambda value: format_money(value),
                "Current Price": lambda value: format_money(value),
                "Unrealized P&L": lambda value: format_money(value),
                "Weight %": lambda value: format_pct(value, 2),
            }
        )
        .map(
            lambda value: "color: #15803d; font-weight: 600;"
            if value > 0
            else ("color: #b91c1c; font-weight: 600;" if value < 0 else ""),
            subset=["Unrealized P&L"],
        )
    )


def _allocation_chart(data: pd.DataFrame):
    figure = px.pie(
        data,
        names="ticker",
        values="current_value",
        hole=0.48,
        color_discrete_sequence=["#0f766e", "#1d4ed8", "#b45309", "#be123c", "#6d28d9", "#0f766e"],
    )
    figure.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{percent}",
        hovertemplate="%{label}<br>%{value:$,.2f}<extra></extra>",
    )
    figure.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def _sector_chart(data: pd.DataFrame):
    figure = px.bar(
        data,
        x="sector",
        y="weight_pct",
        color="weight_pct",
        text="weight_pct",
        color_continuous_scale=["#dbeafe", "#0f766e"],
    )
    figure.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate="%{x}<br>%{y:.2f}% of portfolio<extra></extra>",
    )
    figure.update_layout(
        xaxis_title="Sector",
        yaxis_title="Weight %",
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=12, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    return figure


def main() -> None:
    st.markdown('<div class="dashboard-kicker">Read-Only Dashboard</div>', unsafe_allow_html=True)
    st.title("Portfolio")

    payload = get_portfolio_data()
    summary = payload["summary"]
    positions = payload["positions"]
    policy_flags = payload["policy_flags"]

    stat_columns = st.columns(5)
    stats = [
        ("Total Value", summary["total_value"]),
        ("Cash", summary["cash"]),
        ("Deployed", summary["deployed"]),
        ("Gross Exposure", summary["gross_exposure"]),
        ("Realized P&L", summary["realized_pnl"]),
    ]
    for column, (label, value) in zip(stat_columns, stats):
        column.metric(label, format_money(value))

    if payload["price_fallbacks"]:
        st.caption(
            "Latest cached price unavailable for: "
            + ", ".join(payload["price_fallbacks"])
            + ". Showing cost basis as the current price fallback."
        )

    st.subheader("Current Holdings")
    if positions.empty:
        st.info("No open positions in the paper-trading database.")
    else:
        st.dataframe(_portfolio_table(positions), use_container_width=True, hide_index=True)

        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.subheader("Allocation")
            st.plotly_chart(_allocation_chart(payload["allocation"]), use_container_width=True)
        with chart_right:
            st.subheader("Sector Exposure")
            st.plotly_chart(_sector_chart(payload["sector_exposure"]), use_container_width=True)

    st.subheader("Policy Status")
    if policy_flags:
        st.warning("One or more positions are beyond the single-name hard limit.")
        st.dataframe(
            pd.DataFrame(policy_flags).rename(
                columns={
                    "ticker": "Ticker",
                    "company": "Company",
                    "flag": "Policy Flag",
                    "weight_pct": "Weight %",
                }
            ).style.format({"Weight %": lambda value: format_pct(value, 1)}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("All open positions are within the current policy flags tracked by the dashboard.")


if __name__ == "__main__":
    main()
