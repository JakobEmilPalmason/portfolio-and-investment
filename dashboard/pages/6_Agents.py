from __future__ import annotations

import html as html_lib
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import (
    DEFAULT_AGENT_ALLOCATIONS_SUBDIR,
    _market_open_timestamp,
    build_consensus_matrix,
    compute_agent_returns,
    compute_position_returns,
    format_money,
    format_pct,
    get_agent_prices,
    get_agent_runs,
)
from dashboard.theme import render_hero, render_kicker, render_agent_color_dot

AGENT_COLORS = [
    "#e07a5f",  # warm terracotta
    "#81b29a",  # sage green
    "#f2cc8f",  # soft gold
    "#a8dadc",  # pale teal
    "#e9c46a",  # amber
    "#2a9d8f",  # deep teal
    "#e76f51",  # coral
    "#606c38",  # olive
    "#bc6c25",  # sienna
    "#dda15e",  # tan
]

# RGB values for fill areas (matching AGENT_COLORS)
AGENT_COLORS_RGB = [
    (224, 122, 95),
    (129, 178, 154),
    (242, 204, 143),
    (168, 218, 220),
    (233, 196, 106),
    (42, 157, 143),
    (231, 111, 81),
    (96, 108, 56),
    (188, 108, 37),
    (221, 161, 94),
]


def _hero_performance_chart(
    runs: list[dict], prices_df: pd.DataFrame, start_ts: pd.Timestamp | None,
) -> tuple[go.Figure | None, dict[str, float]]:
    """Build the hero performance chart. Returns (figure, {label: latest_return})."""
    if prices_df.empty or start_ts is None:
        return None, {}

    figure = go.Figure()
    agent_latest: dict[str, float] = {}

    for i, run in enumerate(runs):
        color = AGENT_COLORS[i % len(AGENT_COLORS)]
        r, g, b = AGENT_COLORS_RGB[i % len(AGENT_COLORS_RGB)]

        ret = compute_agent_returns(
            run["positions"], run["cash_weight_pct"], prices_df, run["proposal_date"], start_ts,
        )
        if ret.empty:
            continue

        agent_latest[run["label"]] = float(ret.iloc[-1]) if len(ret) > 0 else 0.0

        figure.add_trace(go.Scatter(
            x=list(ret.index),
            y=ret.values,
            mode="lines",
            name=run["label"],
            line=dict(color=color, width=3.5),
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.08)",
            hovertemplate="%{y:.2f}%<extra>" + run["label"] + "</extra>",
        ))

    # SPY benchmark
    spy_latest = 0.0
    if "SPY" in prices_df.columns:
        spy = prices_df["SPY"].dropna()
        spy_window = spy.loc[spy.index >= start_ts]
        if not spy_window.empty:
            spy_start = spy_window.iloc[0]
            if spy_start and spy_start > 0:
                spy_ret = pd.Series(
                    {ts: (value / spy_start - 1) * 100 for ts, value in spy_window.items()},
                )
                spy_latest = float(spy_ret.iloc[-1]) if len(spy_ret) > 0 else 0.0
                figure.add_trace(go.Scatter(
                    x=list(spy_ret.index),
                    y=spy_ret.values,
                    mode="lines",
                    name="S&P 500",
                    line=dict(color="#93c5fd", width=2.5, dash="dash"),
                    hovertemplate="%{y:.2f}%<extra>S&P 500</extra>",
                ))

    agent_latest["SPY"] = spy_latest

    figure.update_layout(
        height=480,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=13, color="#fafaf9"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            color="#78716c",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(68, 64, 60, 0.3)",
            zeroline=True,
            zerolinecolor="rgba(255,255,255,0.15)",
            zerolinewidth=1,
            color="#78716c",
            tickfont=dict(size=11),
            ticksuffix="%",
        ),
        hovermode="x unified",
    )
    figure.update_xaxes(dtick=30 * 60 * 1000, tickformat="%H:%M")

    return figure, agent_latest


def _agent_panel_html(run: dict, color: str, agent_return: float) -> str:
    """Render one agent summary panel as styled HTML."""
    ret_color = "var(--positive)" if agent_return >= 0 else "var(--danger)"
    return f"""
    <div class="agent-panel">
      <div class="agent-panel-header">
        <div>
          <span class="agent-legend-dot" style="background:{color}"></span>
          <span class="agent-panel-name">{html_lib.escape(run['label'])}</span>
        </div>
        <span class="agent-panel-date">{html_lib.escape(run['proposal_date'])}</span>
      </div>
      <div class="metric-strip">
        <div class="metric-card">
          <div class="metric-label">Positions</div>
          <div class="metric-value">{run['position_count']}</div>
          <div class="metric-meta">{run['own_weight_pct']:.0f}% Own · {run['watch_weight_pct']:.0f}% Watch</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Cash</div>
          <div class="metric-value">{run['cash_weight_pct']:.0f}%</div>
          <div class="metric-meta">{format_money(run['cash'].get('amount', 0))}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Avg Score</div>
          <div class="metric-value">{run['avg_score']:.1f}</div>
          <div class="metric-meta">portfolio quality</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Return</div>
          <div class="metric-value" style="color:{ret_color}">{agent_return:+.2f}%</div>
          <div class="metric-meta">since market open</div>
        </div>
      </div>
    </div>
    """


def _position_table_html(positions_with_returns: list[dict]) -> str:
    """Render per-position performance as a custom HTML table."""
    header = """<div style="overflow-x:auto; border-radius:14px; border:1px solid var(--border);">
    <table class="custom-table"><thead><tr>
        <th>Ticker</th><th>Company</th><th>Verdict</th><th>Weight</th>
        <th>Open</th><th>Current</th><th style="text-align:right">Change</th>
        <th style="text-align:right">P&L</th><th style="text-align:right">Contrib.</th>
    </tr></thead><tbody>"""

    rows = []
    for p in positions_with_returns:
        pct = p["pct_change"]
        pct_color = "var(--positive)" if pct >= 0 else "var(--danger)"
        pnl_color = "var(--positive)" if p["dollar_pnl"] >= 0 else "var(--danger)"

        verdict = p.get("verdict", "")
        verdict_cls = {"Own": "b-own", "Watch": "b-watch", "Pass": "b-pass"}.get(verdict, "")

        ticker_display = html_lib.escape(p["ticker"])
        company_display = html_lib.escape(p.get("company", ""))
        if len(company_display) > 28:
            company_display = company_display[:26] + "…"

        no_data = "" if p.get("has_price", True) else ' <span style="color:var(--subtle);font-size:10px;">NO DATA</span>'

        rows.append(f"""<tr>
            <td><span class="table-symbol">{ticker_display}</span></td>
            <td><span class="table-meta">{company_display}</span></td>
            <td><span class="badge {verdict_cls}">{html_lib.escape(verdict)}</span></td>
            <td class="table-mono">{p['target_weight_pct']:.1f}%</td>
            <td class="table-mono">${p['price_at_open']:,.2f}</td>
            <td class="table-mono">${p['current_price']:,.2f}{no_data}</td>
            <td class="table-mono" style="text-align:right;color:{pct_color};font-weight:700;font-size:14px;">{pct:+.2f}%</td>
            <td class="table-mono" style="text-align:right;color:{pnl_color}">${p['dollar_pnl']:+,.0f}</td>
            <td class="table-mono" style="text-align:right">{p['contribution']:+.2f}%</td>
        </tr>""")

    return header + "\n".join(rows) + "</tbody></table></div>"


def _sector_pie(positions: list[dict]) -> go.Figure:
    sector_wt: dict[str, float] = {}
    for p in positions:
        s = p.get("sector", "Other")
        sector_wt[s] = sector_wt.get(s, 0) + p.get("target_weight_pct", 0)
    figure = px.pie(
        names=list(sector_wt.keys()),
        values=list(sector_wt.values()),
        hole=0.4,
        color_discrete_sequence=AGENT_COLORS,
    )
    figure.update_layout(
        margin=dict(l=0, r=0, t=12, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        showlegend=True,
        legend=dict(font=dict(size=11, color="#fafaf9")),
    )
    return figure


def _consensus_heatmap(matrix: pd.DataFrame, agent_labels: list[str]) -> go.Figure:
    weight_cols = [c for c in matrix.columns if c in agent_labels]
    z = matrix[weight_cols].values.tolist()
    text = [[f"{v:.1f}" if v > 0 else "" for v in row] for row in z]

    figure = go.Figure(data=[go.Heatmap(
        z=z,
        x=weight_cols,
        y=matrix.index.tolist(),
        colorscale=[[0, "#1c1917"], [0.5, "#c15f3c"], [1, "#86efac"]],
        text=text,
        texttemplate="%{text}",
        hovertemplate="Ticker: %{y}<br>Agent: %{x}<br>Weight: %{z:.1f}%<extra></extra>",
    )])
    height = max(300, len(matrix) * 32)
    figure.update_layout(
        margin=dict(l=0, r=0, t=12, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
    )
    return figure


def _render_v1() -> None:
    """First iteration of the agent comparison view."""
    runs = get_agent_runs()
    if not runs:
        st.info(f"No allocation runs found under `portfolio/allocations/{DEFAULT_AGENT_ALLOCATIONS_SUBDIR}`.")
        return

    # ── Fetch prices for all tickers across all agents ──
    all_tickers: set[str] = set()
    for r in runs:
        for p in r["positions"]:
            t = p.get("ticker", "")
            if t:
                all_tickers.add(t)

    earliest = min(r["proposal_date"] for r in runs)
    prices = get_agent_prices(tuple(sorted(all_tickers)), earliest, interval="30m")
    market_open_ts = _market_open_timestamp(prices, earliest)

    # ── Build performance chart + get latest returns ──
    chart, agent_latest = _hero_performance_chart(runs, prices, market_open_ts)

    # Determine leader
    agent_returns = {k: v for k, v in agent_latest.items() if k != "SPY"}
    spy_return = agent_latest.get("SPY", 0.0)

    if agent_returns:
        leader_label = max(agent_returns, key=agent_returns.get)
        leader_return = agent_returns[leader_label]
        best_alpha = max(agent_returns.values()) - spy_return
    else:
        leader_label = "—"
        leader_return = 0.0
        best_alpha = 0.0

    # Consensus count
    matrix = build_consensus_matrix(runs)
    consensus_count = 0
    if not matrix.empty:
        threshold = max(2, int(len(runs) * 0.7))
        consensus_count = int((matrix["Count"] >= threshold).sum())

    # ── Hero ──
    render_hero(
        "Multi-agent allocation tracking",
        "Compare the four week13 allocations head-to-head against SPY from today’s market open using 30-minute bars.",
        [
            {"label": "Agents", "value": str(len(runs)), "meta": "allocation runs", "tone": "tone-accent"},
            {"label": "Leader", "value": leader_label, "meta": f"{leader_return:+.2f}% return", "tone": "tone-positive"},
            {"label": "vs S&P", "value": f"{best_alpha:+.1f}%", "meta": "best agent alpha", "tone": "tone-info"},
            {"label": "Consensus", "value": str(consensus_count), "meta": "shared picks", "tone": "tone-warning"},
        ],
    )

    # ── Performance Chart ──
    st.markdown("")  # spacing
    st.markdown(
        '<div class="agent-chart-hero">'
        '<div class="agent-chart-title">30-Minute Returns vs SPY</div>'
        '<div class="agent-chart-subtitle">Static weights from the 2026-03-24 market-open bar, refreshed on half-hour intervals</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if chart:
        st.plotly_chart(chart, use_container_width=True, key="hero_perf")
    elif prices.empty:
        st.warning("Could not fetch price data. Check your internet connection.")
    else:
        st.info("Not enough intraday price data to render the 30-minute chart yet.")

    # ── Agent Summary Strip ──
    st.markdown("")
    cols = st.columns(len(runs))
    for i, (col, run) in enumerate(zip(cols, runs)):
        color = AGENT_COLORS[i % len(AGENT_COLORS)]
        ret = agent_returns.get(run["label"], 0.0)
        with col:
            st.markdown(_agent_panel_html(run, color, ret), unsafe_allow_html=True)

    # ── Portfolio Breakdown ──
    st.markdown("")
    st.subheader("Portfolio Breakdown")

    tab_labels = [run["label"] for run in runs]
    tabs = st.tabs(tab_labels)

    for i, (tab, run) in enumerate(zip(tabs, runs)):
        color = AGENT_COLORS[i % len(AGENT_COLORS)]
        with tab:
            # Agent color indicator
            st.markdown(
                f'<div style="margin-bottom:0.8rem;">'
                f'{render_agent_color_dot(color, run["label"])}'
                f'<span style="color:var(--muted);margin-left:0.8rem;font-size:0.82rem;">'
                f'{run["proposal_date"]} · ${run["capital"]:,.0f} capital · '
                f'{run["position_count"]} positions</span></div>',
                unsafe_allow_html=True,
            )

            # Position performance table
            pos_returns = compute_position_returns(
                run["positions"], prices, run["proposal_date"], market_open_ts,
            )
            if pos_returns:
                # Summary stats
                total_pnl = sum(p["dollar_pnl"] for p in pos_returns)
                winners = sum(1 for p in pos_returns if p["pct_change"] > 0)
                losers = sum(1 for p in pos_returns if p["pct_change"] < 0)

                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    pnl_color = "var(--positive)" if total_pnl >= 0 else "var(--danger)"
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">Total P&L</div>'
                        f'<div class="metric-value" style="color:{pnl_color}">${total_pnl:+,.0f}</div>'
                        f'<div class="metric-meta">across {len(pos_returns)} positions</div></div>',
                        unsafe_allow_html=True,
                    )
                with mc2:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">Winners</div>'
                        f'<div class="metric-value" style="color:var(--positive)">{winners}</div>'
                        f'<div class="metric-meta">positive return</div></div>',
                        unsafe_allow_html=True,
                    )
                with mc3:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">Losers</div>'
                        f'<div class="metric-value" style="color:var(--danger)">{losers}</div>'
                        f'<div class="metric-meta">negative return</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("")
                st.markdown(_position_table_html(pos_returns), unsafe_allow_html=True)
            else:
                st.info("No position data available.")

            # Bottom section: sector pie + risk overlay
            st.markdown("")
            left_col, right_col = st.columns(2)

            with left_col:
                st.markdown("**Sector Exposure**")
                if run["positions"]:
                    st.plotly_chart(_sector_pie(run["positions"]), use_container_width=True)

            with right_col:
                st.markdown("**Risk Overlay**")
                cash = run["cash"]
                st.markdown(
                    f'<div class="metric-card" style="margin-bottom:0.6rem;">'
                    f'<div class="metric-label">Cash Position</div>'
                    f'<div class="metric-value">{format_money(cash.get("amount", 0))}</div>'
                    f'<div class="metric-meta">{cash.get("weight_pct", 0):.0f}% of capital</div></div>',
                    unsafe_allow_html=True,
                )
                if cash.get("rationale"):
                    rationale = cash["rationale"]
                    st.caption(rationale[:250] + ("…" if len(rationale) > 250 else ""))

                risk = run.get("risk_overlay") or {}
                if risk:
                    st.markdown(
                        f'<div style="margin-top:0.5rem;">'
                        f'<div class="stat-line"><span class="stat-label">Gross Exposure</span>'
                        f'<span class="stat-value">{risk.get("gross_exposure_pct", 0)}%</span></div>'
                        f'<div class="stat-line"><span class="stat-label">Avg Score</span>'
                        f'<span class="stat-value">{risk.get("portfolio_avg_score", 0)}</span></div>'
                        f'<div class="stat-line"><span class="stat-label">Red Flags</span>'
                        f'<span class="stat-value">{risk.get("total_red_flags", 0)}</span></div>'
                        f'<div class="stat-line"><span class="stat-label">Positions</span>'
                        f'<span class="stat-value">{risk.get("position_count", 0)}</span></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    corr = risk.get("top_correlated_risks") or []
                    if corr:
                        st.markdown("**Correlated Risks**")
                        for r_text in corr:
                            st.markdown(f"- {r_text[:150]}{'…' if len(r_text) > 150 else ''}")

    # ── Consensus Heatmap ──
    st.markdown("")
    st.subheader("Position Consensus")

    if matrix.empty:
        st.info("No positions to compare.")
    else:
        agent_labels = [r["label"] for r in runs]

        # Consensus picks callout first
        threshold = max(2, int(len(runs) * 0.7))
        consensus = matrix[matrix["Count"] >= threshold]
        if not consensus.empty:
            picks = [
                f"**{t}** ({int(row['Count'])}/{len(runs)} agents, avg {row['Avg Weight']:.1f}%)"
                for t, row in consensus.iterrows()
            ]
            st.success(f"Consensus picks (held by {threshold}+ agents): " + " · ".join(picks))

        st.plotly_chart(_consensus_heatmap(matrix, agent_labels), use_container_width=True)
        st.caption("Weight % each agent allocates to each ticker. Higher overlap = stronger conviction signal.")


def _render_v2() -> None:
    """Second iteration – not yet implemented."""
    st.info("V2 is under construction. Nothing here yet.")


def main() -> None:
    render_kicker("AI Allocator Arena")
    st.title("Agent Comparison")

    v1_tab, v2_tab = st.tabs(["V1 — Current", "V2 — Next"])

    with v1_tab:
        _render_v1()

    with v2_tab:
        _render_v2()


if __name__ == "__main__":
    main()
