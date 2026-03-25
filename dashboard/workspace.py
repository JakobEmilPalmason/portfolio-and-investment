from __future__ import annotations

import html
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.data import (
    DEFAULT_REPO_ROOT,
    SCOREBOARD_ORDER,
    format_money,
    format_pct,
    format_ratio,
    get_freshness_data,
    get_pipeline_data,
    get_policy_markdown,
    get_portfolio_data,
    get_queue_data,
    get_research_catalog,
    get_research_detail,
    get_scoreboard_data,
    get_search_results,
    get_search_stats,
    queue_state_color,
    rebuild_search,
)
from dashboard.theme import (
    freshness_dot,
    pill,
    priority_badge,
    render_hero,
    render_kicker,
    render_markdown_styled,
    score_dots,
    score_row_html,
    state_badge,
    verdict_badge,
    _score_color,
)

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    HAS_AGGRID = True
except ImportError:  # pragma: no cover - exercised manually when dep absent
    HAS_AGGRID = False


WORKSPACE_SECTIONS = ["Overview", "Portfolio", "Queue", "Reports", "Scoreboard", "Pipeline"]
VERDICT_TONES = {"Own": "positive", "Watch": "warning", "Pass": "danger"}
FRESHNESS_TONES = {"fresh": "positive", "aging": "warning", "stale": "danger", "never": "neutral"}


def _init_workspace_state() -> None:
    defaults = {
        "workspace_section": "Overview",
        "selected_ticker": None,
        "report_dialog_pending": False,
        "queue_grid_selection": None,
        "report_grid_selection": None,
        "scoreboard_grid_selection": None,
        "sidebar_search_query": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _score_tone(score: float | int | None) -> str:
    if score is None:
        return "neutral"
    if score >= 7:
        return "positive"
    if score >= 4:
        return "warning"
    return "danger"


def _select_report_ticker(ticker: str | None) -> None:
    if not ticker:
        return
    st.session_state["selected_ticker"] = ticker
    st.session_state["report_dialog_pending"] = True
    st.rerun()


def _button_label(text: str, detail: str) -> str:
    return f"{text}\n{detail}" if detail else text


def _status_badges(report: dict[str, Any], queue_entry: dict[str, Any] | None) -> str:
    verdict = pill(report.get("verdict", "Unknown"), VERDICT_TONES.get(report.get("verdict"), "neutral"))
    queue_state = queue_entry.get("current_state", "not_in_queue") if queue_entry else "not_in_queue"
    queue_badge = (
        f"<span class='pill' style='background:{queue_state_color(queue_state)}22;"
        f"color:{queue_state_color(queue_state)};border-color:{queue_state_color(queue_state)}44'>"
        f"{html.escape(queue_state.replace('_', ' '))}</span>"
    )
    return f"{verdict} {queue_badge}"


def _score_radar(detail: dict[str, Any]) -> go.Figure | None:
    scores = detail["scores"]
    if scores.empty:
        return None
    categories = scores["Category"].tolist()
    values = scores["Score"].tolist()
    categories.append(categories[0])
    values.append(values[0])

    figure = go.Figure()
    figure.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            line=dict(color="#c15f3c", width=2.4),
            fillcolor="rgba(193, 95, 60, 0.24)",
            name="Score profile",
        )
    )
    figure.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.08)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        margin=dict(l=10, r=10, t=12, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def _portfolio_treemap(data: pd.DataFrame) -> go.Figure:
    figure = px.treemap(
        data,
        path=["sector", "ticker"],
        values="current_value",
        color="unrealized_pnl",
        color_continuous_scale=["#7f1d1d", "#fafaf9", "#14532d"],
        color_continuous_midpoint=0,
    )
    figure.update_layout(margin=dict(l=0, r=0, t=12, b=0), paper_bgcolor="rgba(0,0,0,0)")
    return figure


def _sector_chart(data: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        data.sort_values("weight_pct", ascending=True),
        x="weight_pct",
        y="sector",
        orientation="h",
        color="weight_pct",
        color_continuous_scale=["#292524", "#c15f3c"],
        labels={"weight_pct": "Weight %", "sector": ""},
    )
    figure.update_layout(
        margin=dict(l=0, r=0, t=12, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    return figure


def _pipeline_funnel(pipeline: dict[str, Any], report_count: int) -> go.Figure:
    scan = pipeline.get("scan") or {}
    triage = pipeline.get("triage") or {}
    values = [
        scan.get("total_candidates", 0),
        scan.get("total_candidates", 0),
        (triage.get("b1") or {}).get("advance", 0),
        (triage.get("b2") or {}).get("deep_dive", 0) + (triage.get("b2") or {}).get("refresh", 0),
        report_count,
    ]
    labels = ["A1 Universe", "A2 Candidates", "B1 Advance", "B2 Focus", "C Reports"]
    figure = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            marker=dict(color=["#57534e", "#78716c", "#f59e0b", "#c15f3c", "#22c55e"]),
        )
    )
    figure.update_layout(margin=dict(l=0, r=0, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return figure


def _bar_stack_html(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<div class='table-note'>No data available.</div>"
    maximum = max(item["value"] for item in items) or 1
    rows = []
    for item in items:
        rows.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{html.escape(item['label'])}</div>
              <div class="bar-track">
                <div class="bar-fill" style="width:{(item['value'] / maximum) * 100:.0f}%;background:{item['color']};"></div>
              </div>
              <div class="bar-value">{item['value']}</div>
            </div>
            """
        )
    return "<div class='bar-stack'>" + "".join(rows) + "</div>"


def _top_attention(queue_df: pd.DataFrame) -> pd.DataFrame:
    if queue_df.empty:
        return queue_df
    priorities = queue_df.copy()
    priorities["urgency"] = (
        priorities["priority"].map({"high": 3, "medium": 2, "low": 1}).fillna(0)
        + priorities["freshness_status"].map({"stale": 3, "aging": 2, "fresh": 1, "never": 2}).fillna(0)
    )
    return priorities.sort_values(["urgency", "days_since_analysis"], ascending=[False, False]).head(6)


def _safe_selected_rows(response: Any) -> list[dict[str, Any]]:
    if response is None:
        return []
    if isinstance(response, dict):
        selected = response.get("selected_rows", [])
        if isinstance(selected, pd.DataFrame):
            return selected.to_dict("records")
        if isinstance(selected, list):
            return selected
    return []


def _render_grid(df: pd.DataFrame, key: str, selection: bool = False) -> list[dict[str, Any]]:
    if df.empty:
        st.info("No rows to display.")
        return []

    if HAS_AGGRID:
        builder = GridOptionsBuilder.from_dataframe(df)
        builder.configure_default_column(
            sortable=True,
            filter=True,
            resizable=True,
            floatingFilter=True,
            minWidth=110,
        )
        builder.configure_column("ticker", pinned="left", minWidth=100)
        builder.configure_column("company", pinned="left", minWidth=180)
        if selection:
            builder.configure_selection("single", use_checkbox=False)
        options = builder.build()
        response = AgGrid(
            df,
            gridOptions=options,
            fit_columns_on_grid_load=False,
            theme="streamlit",
            allow_unsafe_jscode=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED if selection else GridUpdateMode.MODEL_CHANGED,
            height=min(max(280, 44 + len(df) * 28), 540),
            key=key,
        )
        return _safe_selected_rows(response)

    st.dataframe(df, use_container_width=True, hide_index=True)
    if selection and "ticker" in df.columns:
        ticker = st.selectbox(
            "Open ticker",
            options=[""] + df["ticker"].tolist(),
            key=f"{key}-fallback-selection",
        )
        return [{"ticker": ticker}] if ticker else []
    return []


def _handle_grid_selection(selected_rows: list[dict[str, Any]], state_key: str) -> None:
    if not selected_rows:
        return
    row = selected_rows[0]
    ticker = row.get("ticker") or row.get("Ticker")
    if not ticker:
        return
    if st.session_state.get(state_key) != ticker:
        st.session_state[state_key] = ticker
        _select_report_ticker(ticker)


def show_report_dialog(ticker: str) -> None:
    detail = get_research_detail(ticker, repo_root=DEFAULT_REPO_ROOT)
    if detail is None:
        st.error(f"No report detail found for {ticker}.")
        return

    report = detail["report"]
    queue_entry = detail["queue"] or {}

    @st.dialog(f"{ticker} report", width="large")
    def _dialog() -> None:
        st.markdown(_status_badges(report, queue_entry), unsafe_allow_html=True)
        cols = st.columns(4)
        cols[0].metric("Average Score", format_ratio(report.get("average_score")))
        cols[1].metric("Confidence", str(report.get("confidence", "N/A")).title())
        cols[2].metric("Analysis Date", report.get("analysis_date", "N/A"))
        cols[3].metric("MOS", format_pct(report.get("mos_at_analysis")))

        radar = _score_radar(detail)
        if radar is not None:
            st.plotly_chart(radar, use_container_width=True)

        score_cols = st.columns([1.15, 0.85])
        with score_cols[0]:
            if not detail["scores"].empty:
                st.subheader("Scoreboard")
                scores_html = "".join(
                    score_row_html(row["Category"], row["Score"])
                    for _, row in detail["scores"].iterrows()
                )
                st.markdown(scores_html, unsafe_allow_html=True)
        with score_cols[1]:
            st.subheader("Queue State")
            queue_html = (
                f'<div>{state_badge(queue_entry.get("current_state"))}</div>'
                f'<div style="margin-top:0.5rem;color:var(--muted);font-size:0.9rem;">'
                f'Thesis: {html.escape(str(queue_entry.get("thesis_status", "N/A")))}</div>'
                f'<div style="color:var(--muted);font-size:0.9rem;">'
                f'Next: {html.escape(str(queue_entry.get("next_required_action", "N/A")).replace("_", " "))}</div>'
            )
            st.markdown(queue_html, unsafe_allow_html=True)

        info_cols = st.columns(2)
        with info_cols[0]:
            st.subheader("Key Strengths")
            strengths = detail["key_strengths"] or ["No strengths listed."]
            for item in strengths:
                st.markdown(f"- {item}")
            st.subheader("Buy Triggers")
            triggers = detail["buy_triggers"] or ["No buy triggers listed."]
            for item in triggers:
                st.markdown(f"- {item}")
        with info_cols[1]:
            st.subheader("Key Risks")
            risks = detail["key_risks"] or ["No risks listed."]
            for item in risks:
                st.markdown(f"- {item}")
            st.subheader("Red Flags")
            red_flags = detail["red_flags"] or ["No red flags listed."]
            for item in red_flags:
                st.markdown(f"- {item}")

        with st.expander("Full report", expanded=False):
            if detail["md_path"] and detail["markdown"]:
                st.caption(detail["md_path"])
                render_markdown_styled(detail["markdown"])
            else:
                st.info("No markdown report was found for this ticker.")

    _dialog()


def maybe_open_pending_dialog() -> None:
    if st.session_state.get("report_dialog_pending") and st.session_state.get("selected_ticker"):
        st.session_state["report_dialog_pending"] = False
        show_report_dialog(st.session_state["selected_ticker"])


def render_sidebar_controls() -> None:
    _init_workspace_state()
    with st.sidebar:
        st.markdown("### Research Workspace")
        st.caption("Streamlit-native dashboard for the portfolio, queue, and report pipeline.")

        st.markdown("#### Quick Jump")
        section = st.segmented_control(
            "Workspace section",
            options=WORKSPACE_SECTIONS,
            selection_mode="single",
            default=st.session_state["workspace_section"],
            key="sidebar-workspace-section",
        )
        if section and section != st.session_state["workspace_section"]:
            st.session_state["workspace_section"] = section

        st.markdown("#### Search")
        query = st.text_input(
            "Find reports, queue notes, and financials",
            key="sidebar_search_query",
            placeholder="Search ticker or phrase...",
        ).strip()

        stats = get_search_stats(repo_root=DEFAULT_REPO_ROOT)
        if stats["total_docs"]:
            st.caption(f"{stats['total_docs']} docs indexed")

        if st.button("Rebuild Search Index", use_container_width=True, key="sidebar-rebuild-search"):
            summary = rebuild_search(repo_root=DEFAULT_REPO_ROOT)
            st.toast(f"Indexed {summary['indexed']} docs in {summary['duration_ms']} ms")

        if len(query) >= 2:
            results = get_search_results(query, repo_root=DEFAULT_REPO_ROOT, limit=8)
            if results:
                for idx, result in enumerate(results):
                    ticker = result.get("ticker")
                    label = _button_label(result["title"], result.get("doc_type", ""))
                    if st.button(label, use_container_width=True, key=f"sidebar-result-{idx}"):
                        if ticker:
                            _select_report_ticker(ticker)
                        else:
                            st.session_state["workspace_section"] = "Queue"
                            st.toast("Open the workspace to review queue and triage results.")
            else:
                st.caption("No search hits.")

        with st.expander("Policy", expanded=False):
            policy = get_policy_markdown(repo_root=DEFAULT_REPO_ROOT)
            if policy:
                st.markdown(policy[:1800] + ("\n\n..." if len(policy) > 1800 else ""))
            else:
                st.caption("Policy file unavailable.")


def render_workspace_page() -> None:
    _init_workspace_state()

    render_kicker("Research Workspace")
    st.title("Workspace")

    section = st.segmented_control(
        "Section",
        options=WORKSPACE_SECTIONS,
        selection_mode="single",
        default=st.session_state["workspace_section"],
        key="workspace-section-control",
    )
    if section:
        st.session_state["workspace_section"] = section
    active = st.session_state["workspace_section"]

    queue_df = get_queue_data(repo_root=DEFAULT_REPO_ROOT)
    reports = get_research_catalog(repo_root=DEFAULT_REPO_ROOT)
    portfolio = get_portfolio_data()
    pipeline = get_pipeline_data(repo_root=DEFAULT_REPO_ROOT)
    scoreboard = get_scoreboard_data(repo_root=DEFAULT_REPO_ROOT)
    freshness = get_freshness_data(repo_root=DEFAULT_REPO_ROOT)

    if active == "Overview":
        render_overview_section(queue_df, reports, portfolio, pipeline, freshness)
    elif active == "Portfolio":
        render_portfolio_section(portfolio)
    elif active == "Queue":
        render_queue_section(queue_df)
    elif active == "Reports":
        render_reports_section(reports)
    elif active == "Scoreboard":
        render_scoreboard_section(scoreboard)
    elif active == "Pipeline":
        render_pipeline_section(pipeline, len(reports))

    maybe_open_pending_dialog()


def render_research_page() -> None:
    render_kicker("Single-Ticker Explorer")
    st.title("Research Lab")

    catalog = get_research_catalog(repo_root=DEFAULT_REPO_ROOT)
    if not catalog:
        st.info("No FINAL-REPORT.json files were found under runs/*/reports/.")
        return

    options = [item["ticker"] for item in sorted(catalog, key=lambda item: item["ticker"])]
    selected = st.selectbox(
        "Ticker",
        options,
        index=options.index(st.session_state["selected_ticker"])
        if st.session_state.get("selected_ticker") in options
        else 0,
        format_func=lambda ticker: next(
            (
                f"{entry['ticker']} - {entry['company']}"
                for entry in catalog
                if entry["ticker"] == ticker
            ),
            ticker,
        ),
    )

    detail = get_research_detail(selected, repo_root=DEFAULT_REPO_ROOT)
    if detail is None:
        st.error(f"Unable to load report details for {selected}.")
        return

    report = detail["report"]
    hero_metrics = [
        {"label": "Verdict", "value": report.get("verdict", "N/A"), "meta": report.get("company", ""), "tone": f"tone-{VERDICT_TONES.get(report.get('verdict'), 'info')}"},
        {"label": "Average Score", "value": format_ratio(report.get("average_score")), "meta": report.get("confidence", "N/A"), "tone": f"tone-{_score_tone(report.get('average_score'))}"},
        {"label": "MOS", "value": format_pct(report.get("mos_at_analysis")), "meta": "At analysis date", "tone": f"tone-{_score_tone(report.get('average_score'))}"},
        {"label": "Analysis Date", "value": report.get("analysis_date", "N/A"), "meta": detail.get("json_path", ""), "tone": "tone-info"},
    ]
    render_hero(
        f"{report.get('ticker')} - {report.get('company')}",
        "Single-name research browser with score profile, triggers, and the full markdown report inline.",
        hero_metrics,
    )

    radar = _score_radar(detail)
    top_cols = st.columns([1.05, 0.95])
    with top_cols[0]:
        if radar is not None:
            st.plotly_chart(radar, use_container_width=True)
    with top_cols[1]:
        st.subheader("Status")
        st.markdown(_status_badges(report, detail.get("queue") or {}), unsafe_allow_html=True)
        st.write(f"Confidence: {report.get('confidence', 'N/A')}")
        st.write(f"Analysis date: {report.get('analysis_date', 'N/A')}")
        st.write(f"Current queue state: {(detail.get('queue') or {}).get('current_state', 'N/A')}")

    columns = st.columns(3)
    with columns[0]:
        st.subheader("Strengths")
        for item in detail["key_strengths"] or ["No strengths listed."]:
            st.markdown(f"- {item}")
    with columns[1]:
        st.subheader("Risks")
        for item in detail["key_risks"] or ["No risks listed."]:
            st.markdown(f"- {item}")
    with columns[2]:
        st.subheader("Red Flags")
        for item in detail["red_flags"] or ["No red flags listed."]:
            st.markdown(f"- {item}")

    if not detail["scores"].empty:
        st.subheader("Scores")
        scores_html = "".join(
            score_row_html(row["Category"], row["Score"])
            for _, row in detail["scores"].iterrows()
        )
        st.markdown(f'<div class="surface-card">{scores_html}</div>', unsafe_allow_html=True)

    st.subheader("Full Report")
    if detail["markdown"]:
        render_markdown_styled(detail["markdown"])
    else:
        st.info("No markdown report was found for this ticker.")


def render_overview_section(
    queue_df: pd.DataFrame,
    reports: list[dict[str, Any]],
    portfolio: dict[str, Any],
    pipeline: dict[str, Any],
    freshness: dict[str, dict[str, Any]],
) -> None:
    summary = portfolio["summary"]
    stale_names = sum(1 for item in freshness.values() if item["status"] == "stale")
    attention = _top_attention(queue_df)
    latest_reports = sorted(reports, key=lambda item: item.get("analysis_date") or "", reverse=True)[:6]

    render_hero(
        "Research command center",
        "Queue pressure, recent analysis, and portfolio health on one screen. The first viewport should tell you what needs work next.",
        [
            {"label": "Queue", "value": str(len(queue_df)), "meta": "tracked tickers", "tone": "tone-accent"},
            {"label": "Reports", "value": str(len(reports)), "meta": "latest final reports", "tone": "tone-positive"},
            {"label": "Gross Exposure", "value": format_pct(summary["gross_pct"]), "meta": f"Net {format_pct(summary['net_pct'])}", "tone": "tone-warning"},
            {"label": "Stale Coverage", "value": str(stale_names), "meta": "30d+ since analysis", "tone": "tone-danger"},
        ],
    )

    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("What needs attention now")
        if attention.empty:
            st.markdown('<div class="empty-panel">Nothing urgent surfaced from the queue.</div>', unsafe_allow_html=True)
        else:
            rows_html = []
            for _, row in attention.iterrows():
                why = []
                if row.get("current_state") == "deep_research":
                    why.append("deep research")
                fs = row.get("freshness_status", "never")
                ds = row.get("days_since_analysis")
                if fs == "stale" and ds is not None:
                    why.append(f"{int(ds)}d stale")
                elif fs == "aging" and ds is not None:
                    why.append(f"{int(ds)}d aging")
                if row.get("priority") == "high":
                    why.append("high priority")
                nra = row.get("next_required_action")
                if nra:
                    why.append(nra.replace("_", " "))
                last_date = row.get("last_analysis_date") or ""
                date_line = f"Last analysis {last_date}" if last_date else "No report on disk yet"
                rows_html.append(
                    f'<tr>'
                    f'<td><div class="table-symbol">{html.escape(str(row["ticker"]))}</div>'
                    f'<div class="table-meta">{html.escape(str(row.get("company") or ""))}</div></td>'
                    f'<td><div class="queue-badge-stack">{state_badge(row.get("current_state"))}'
                    f' {priority_badge(row.get("priority"))}</div></td>'
                    f'<td><div style="color:var(--text);font-size:13px;">{html.escape(" · ".join(why) or "Needs review")}</div>'
                    f'<div class="table-meta">{html.escape(date_line)}</div></td>'
                    f'</tr>'
                )
            table_html = (
                '<table class="mini-table"><thead><tr>'
                '<th>Name</th><th>Status</th><th>Why Now</th>'
                '</tr></thead><tbody>' + "".join(rows_html) + '</tbody></table>'
            )
            st.markdown(table_html, unsafe_allow_html=True)
            # Interaction buttons
            btn_cols = st.columns(min(len(attention), 6))
            for idx, (_, row) in enumerate(attention.iterrows()):
                if idx < len(btn_cols) and btn_cols[idx].button(
                    row["ticker"], key=f"attn-{row['ticker']}", use_container_width=True
                ):
                    _select_report_ticker(row["ticker"])
    with right:
        st.subheader("Portfolio health")
        st.markdown(
            _bar_stack_html(
                [
                    {"label": "Cash %", "value": round(summary["cash_pct"], 1), "color": "#93c5fd"},
                    {"label": "Gross %", "value": round(summary["gross_pct"], 1), "color": "#c15f3c"},
                    {"label": "Net %", "value": abs(round(summary["net_pct"], 1)), "color": "#22c55e"},
                    {"label": "Largest %", "value": round(summary["largest_position_pct"], 1), "color": "#f59e0b"},
                ]
            ),
            unsafe_allow_html=True,
        )
        st.caption(
            f"Largest position: {summary['largest_position_ticker'] or 'N/A'} at {format_pct(summary['largest_position_pct'])}"
        )

    lower_left, lower_right = st.columns(2)
    with lower_left:
        st.subheader("Newest completed work")
        if latest_reports:
            report_rows = []
            for item in latest_reports:
                score = item.get("average_score")
                score_str = f"{score:.1f}" if score is not None else "\u2014"
                score_color = _score_color(score)
                report_rows.append(
                    f'<tr>'
                    f'<td><div class="table-symbol">{html.escape(item["ticker"])}</div>'
                    f'<div class="table-meta">{html.escape(item.get("company") or "")}</div></td>'
                    f'<td>{verdict_badge(item.get("verdict"))}</td>'
                    f'<td style="text-align:right;"><span class="table-mono" style="color:{score_color}">{score_str}</span></td>'
                    f'<td style="text-align:right;color:var(--muted);font-size:12px;">{html.escape(item.get("analysis_date") or "")}</td>'
                    f'</tr>'
                )
            report_table = (
                '<table class="mini-table"><thead><tr>'
                '<th>Report</th><th>Verdict</th><th style="text-align:right">Score</th><th style="text-align:right">Date</th>'
                '</tr></thead><tbody>' + "".join(report_rows) + '</tbody></table>'
            )
            st.markdown(report_table, unsafe_allow_html=True)
            btn_cols = st.columns(min(len(latest_reports), 6))
            for idx, item in enumerate(latest_reports):
                if idx < len(btn_cols) and btn_cols[idx].button(
                    item["ticker"], key=f"recent-{item['ticker']}", use_container_width=True
                ):
                    _select_report_ticker(item["ticker"])
        else:
            st.markdown('<div class="empty-panel">No reports are available yet.</div>', unsafe_allow_html=True)
    with lower_right:
        st.subheader("Pipeline pulse")
        triage = pipeline.get("triage") or {}
        b2 = triage.get("b2") or {}
        st.metric("Deep Dive", b2.get("deep_dive", 0))
        st.metric("Refresh", b2.get("refresh", 0))
        st.metric("Monitor", b2.get("monitor", 0))
        shortlist = triage.get("deep_dive_shortlist") or []
        if shortlist:
            st.caption("Focused shortlist")
            for item in shortlist[:5]:
                if st.button(
                    f"{item['ticker']} - {item.get('next_action', '').replace('_', ' ')}",
                    key=f"overview-shortlist-{item['ticker']}",
                    use_container_width=True,
                ):
                    _select_report_ticker(item["ticker"])
        else:
            st.info("No shortlist captured in the latest triage run.")


def render_portfolio_section(portfolio: dict[str, Any]) -> None:
    payload = portfolio
    summary = payload["summary"]
    positions = payload["positions"]

    render_hero(
        "Holdings at a glance",
        "Surface concentration, exposure, and policy warnings without making charts the main event.",
        [
            {"label": "Total Value", "value": format_money(summary["total_value"]), "meta": f"Cash {format_money(summary['cash'])}", "tone": "tone-info"},
            {"label": "Total P&L", "value": format_money(summary["total_pnl"]), "meta": f"Realized {format_money(summary['realized_pnl'])}", "tone": f"tone-{_score_tone(summary['total_pnl'])}"},
            {"label": "Positions", "value": str(summary["position_count"]), "meta": f"{summary['long_count']} long / {summary['short_count']} short", "tone": "tone-accent"},
            {"label": "Largest Position", "value": summary["largest_position_ticker"] or "N/A", "meta": format_pct(summary["largest_position_pct"]), "tone": "tone-warning"},
        ],
    )

    if positions.empty:
        st.info("No open positions in the paper-trading database.")
        return

    st.subheader("Current holdings")
    holding_rows = []
    for _, pos in positions.iterrows():
        pnl = pos.get("unrealized_pnl", 0)
        pnl_pct = (pnl / pos["cost_basis"] * 100) if pos.get("cost_basis") else 0
        pnl_color = "var(--positive)" if pnl >= 0 else "var(--danger)"
        side_badge = (
            '<span class="badge b-pass">Short</span>'
            if str(pos.get("side", "")).lower() == "short"
            else '<span class="badge b-monitor-only">Long</span>'
        )
        holding_rows.append(
            f'<tr>'
            f'<td><div class="table-symbol">{html.escape(str(pos["ticker"]))}</div>'
            f'<div class="table-meta">{html.escape(str(pos.get("sector") or ""))}</div></td>'
            f'<td>{side_badge}</td>'
            f'<td class="table-mono" style="text-align:right;">{pos.get("shares", 0):.0f}</td>'
            f'<td class="table-mono" style="text-align:right;">${pos.get("current_price", 0):,.2f}</td>'
            f'<td class="table-mono" style="text-align:right;">${pos.get("current_value", 0):,.0f}</td>'
            f'<td class="table-mono" style="text-align:right;">{pos.get("weight_pct", 0):.1f}%</td>'
            f'<td class="table-mono" style="text-align:right;color:{pnl_color};">${pnl:+,.0f} ({pnl_pct:+.1f}%)</td>'
            f'</tr>'
        )
    holdings_html = (
        '<div style="overflow-x:auto;"><table class="custom-table"><thead><tr>'
        '<th>Holding</th><th>Side</th><th style="text-align:right">Shares</th>'
        '<th style="text-align:right">Price</th><th style="text-align:right">Value</th>'
        '<th style="text-align:right">Weight</th><th style="text-align:right">P&amp;L</th>'
        '</tr></thead><tbody>' + "".join(holding_rows) + '</tbody></table></div>'
    )
    st.markdown(holdings_html, unsafe_allow_html=True)

    charts = st.columns(2)
    with charts[0]:
        st.subheader("Allocation map")
        st.plotly_chart(_portfolio_treemap(positions), use_container_width=True)
    with charts[1]:
        st.subheader("Sector exposure")
        st.plotly_chart(_sector_chart(payload["sector_exposure"]), use_container_width=True)

    if payload["policy_flags"]:
        st.subheader("Policy status")
        warnings_html = "".join(
            f'<div class="warning-item">{html.escape(f["ticker"])}: {html.escape(f["flag"])}</div>'
            for f in payload["policy_flags"]
        )
        st.markdown(f'<div style="display:flex;flex-direction:column;gap:8px;">{warnings_html}</div>', unsafe_allow_html=True)

    if payload["price_fallbacks"]:
        st.caption(
            "Latest cached price unavailable for: "
            + ", ".join(payload["price_fallbacks"])
            + ". Showing cost basis as the current price fallback."
        )


def render_queue_section(queue_df: pd.DataFrame) -> None:
    render_hero(
        "Queue monitor",
        "A high-density queue view with filters for state, verdict, and freshness. Select a row to open the latest report.",
        [
            {"label": "Tracked Names", "value": str(len(queue_df)), "meta": "current queue size", "tone": "tone-accent"},
            {"label": "High Priority", "value": str((queue_df["priority"] == "high").sum() if not queue_df.empty else 0), "meta": "marked high", "tone": "tone-danger"},
            {"label": "Deep Research", "value": str((queue_df["current_state"] == "deep_research").sum() if not queue_df.empty else 0), "meta": "needs full work", "tone": "tone-warning"},
            {"label": "Stale", "value": str((queue_df["freshness_status"] == "stale").sum() if not queue_df.empty else 0), "meta": "30d+ old", "tone": "tone-danger"},
        ],
    )

    if queue_df.empty:
        st.info("Queue data is empty.")
        return

    controls = st.columns([1.3, 1, 1, 1])
    search = controls[0].text_input("Search", key="queue-search", placeholder="Ticker or company")
    states = controls[1].multiselect(
        "State",
        options=sorted(queue_df["current_state"].dropna().unique().tolist()),
        key="queue-state-filter",
    )
    verdict = controls[2].selectbox(
        "Verdict",
        options=["", "Own", "Watch", "Pass"],
        format_func=lambda value: value or "All",
        key="queue-verdict-filter",
    )
    freshness = controls[3].selectbox(
        "Freshness",
        options=["", "fresh", "aging", "stale", "never"],
        format_func=lambda value: value.title() if value else "All",
        key="queue-freshness-filter",
    )

    filtered = queue_df.copy()
    if search:
        mask = filtered["ticker"].str.contains(search, case=False, na=False) | filtered["company"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]
    if states:
        filtered = filtered[filtered["current_state"].isin(states)]
    if verdict:
        filtered = filtered[filtered["current_verdict"] == verdict]
    if freshness:
        filtered = filtered[filtered["freshness_status"] == freshness]

    st.caption(f"{len(filtered)} of {len(queue_df)} rows shown")
    display = filtered[
        [
            "ticker",
            "company",
            "current_state",
            "priority",
            "current_verdict",
            "freshness_status",
            "days_since_analysis",
            "next_required_action",
        ]
    ].rename(
        columns={
            "ticker": "ticker",
            "company": "company",
            "current_state": "state",
            "priority": "priority",
            "current_verdict": "verdict",
            "freshness_status": "freshness",
            "days_since_analysis": "days",
            "next_required_action": "next action",
        }
    )
    selected = _render_grid(display, key="queue-grid", selection=True)
    _handle_grid_selection(selected, "queue_grid_selection")


def render_reports_section(reports: list[dict[str, Any]]) -> None:
    render_kicker("Latest Reports")
    st.subheader("Report browser")
    st.caption("Sort the latest FINAL-REPORT outputs and open any name directly from Streamlit.")

    if not reports:
        st.info("No FINAL-REPORT.json files found.")
        return

    sort_by = st.selectbox(
        "Sort by",
        options=["Date", "Score", "Ticker", "Verdict"],
        index=0,
        key="reports-sort",
    )
    sorted_reports = list(reports)
    if sort_by == "Date":
        sorted_reports.sort(key=lambda item: item.get("analysis_date") or "", reverse=True)
    elif sort_by == "Score":
        sorted_reports.sort(key=lambda item: item.get("average_score") or 0, reverse=True)
    elif sort_by == "Ticker":
        sorted_reports.sort(key=lambda item: item.get("ticker") or "")
    elif sort_by == "Verdict":
        rank = {"Own": 0, "Watch": 1, "Pass": 2}
        sorted_reports.sort(key=lambda item: rank.get(item.get("verdict"), 3))

    for row in [sorted_reports[i : i + 3] for i in range(0, min(len(sorted_reports), 12), 3)]:
        cols = st.columns(len(row))
        for col, item in zip(cols, row):
            with col:
                st.markdown(
                    f"{pill(item['ticker'], 'accent')} {pill(item.get('verdict') or 'Unknown', VERDICT_TONES.get(item.get('verdict'), 'neutral'))}",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{item['company']}**")
                st.caption(
                    f"{item.get('analysis_date', 'N/A')} • Score {format_ratio(item.get('average_score'))} • {str(item.get('confidence', 'N/A')).title()}"
                )
                if st.button("Open report", key=f"report-card-{item['ticker']}", use_container_width=True):
                    _select_report_ticker(item["ticker"])


def _sb_build_data_json(scoreboard: pd.DataFrame) -> str:
    """Serialize scoreboard DataFrame to JSON for the JS-powered table."""
    import json as _json

    records = []
    for _, row in scoreboard.iterrows():
        rec = {}
        for col in [
            "ticker", "company", "verdict", "average_score",
            "circle_of_competence", "competitive_advantage", "management", "business_economics",
            "balance_sheet", "valuation", "margin_of_safety", "temperament",
            "iv_conservative", "iv_base", "iv_bull", "mos_pct",
            "confidence", "red_flag_count", "analysis_date",
        ]:
            v = row.get(col)
            rec[col] = None if pd.isna(v) else v
        records.append(rec)
    return _json.dumps(records)


def render_scoreboard_section(scoreboard: pd.DataFrame) -> None:
    import streamlit.components.v1 as components

    if scoreboard.empty:
        st.markdown(
            '<div class="empty-panel">No analyzed reports found. Run the analysis pipeline first.</div>',
            unsafe_allow_html=True,
        )
        return

    # Streamlit filters for server-side filtering
    filter_cols = st.columns([1.2, 1.2, 1.5, 0.6])
    verdict = filter_cols[0].selectbox(
        "Verdict", options=["", "Own", "Watch", "Pass"],
        format_func=lambda v: v or "All", key="sb-verdict",
    )
    confidence = filter_cols[1].selectbox(
        "Confidence", options=["", "high", "medium", "low"],
        format_func=lambda v: v.title() if v else "All", key="sb-confidence",
    )
    min_score = filter_cols[2].slider("Min score", 0.0, 10.0, 0.0, 0.5, key="sb-min")

    filtered = scoreboard.copy()
    if verdict:
        filtered = filtered[filtered["verdict"] == verdict]
    if confidence:
        filtered = filtered[filtered["confidence"].astype(str).str.lower().str.startswith(confidence)]
    if min_score > 0:
        filtered = filtered[pd.to_numeric(filtered["average_score"], errors="coerce") >= min_score]

    filter_cols[3].markdown(f"**{len(filtered)}** / {len(scoreboard)}")

    data_json = _sb_build_data_json(filtered)

    # Height: 50px per row + 60px header + 40px padding, capped
    row_count = len(filtered)
    height = min(60 + row_count * 50 + 40, 860)

    scoreboard_html = f"""
<!DOCTYPE html>
<html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {{
  color-scheme: dark;
  --bg: #0c0a09; --surface: #1c1917; --surface-strong: #292524;
  --border: rgba(68, 64, 60, 0.82); --border-strong: rgba(120, 113, 108, 0.9);
  --text: #fafaf9; --muted: #a8a29e; --subtle: #78716c;
  --accent: #c15f3c; --positive: #86efac; --warning: #fbbf24; --danger: #fca5a5;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; font-family:'Manrope',system-ui,sans-serif; color:var(--text); overflow:hidden; }}
.mono {{ font-family:'JetBrains Mono',monospace; }}
.wrap {{ overflow:auto; max-height:{height - 20}px; border-radius:12px; border:1px solid var(--border); }}
table {{ width:100%; min-width:1200px; border-collapse:separate; border-spacing:0; }}
thead {{ position:sticky; top:0; z-index:2; }}
th {{
  padding:14px 14px; background:rgba(12,10,9,0.96); border-bottom:1px solid rgba(68,64,60,0.9);
  font-size:12px; font-weight:800; letter-spacing:0.08em; text-transform:uppercase;
  text-align:center; color:var(--subtle); white-space:nowrap; cursor:pointer; user-select:none;
  position:relative;
}}
th:nth-child(1), th:nth-child(2) {{ text-align:left; }}
th:hover {{ color:var(--text); }}
th .tip {{
  display:none; position:absolute; left:50%; top:100%; transform:translateX(-50%); z-index:10;
  white-space:normal; width:max-content; max-width:260px; padding:8px 12px; border-radius:8px;
  font-size:12px; font-weight:500; letter-spacing:0; text-transform:none; line-height:1.45;
  color:var(--text); background:var(--surface-strong); border:1px solid var(--border-strong);
  box-shadow:0 8px 24px rgba(0,0,0,0.5); pointer-events:none;
}}
th:hover .tip {{ display:block; }}
td {{
  padding:12px 14px; border-bottom:1px solid rgba(68,64,60,0.46);
  font-size:14px; text-align:center; color:var(--text);
}}
td:first-child {{ text-align:left; }}
td:nth-child(2) {{ text-align:left; }}
tbody tr:last-child td {{ border-bottom:none; }}
tbody tr:hover td {{ background:rgba(41,37,36,0.42); }}
.sym {{ font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:700; color:var(--accent); cursor:pointer; }}
.co {{ max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--muted); }}
.empty {{ padding:42px 16px; text-align:center; color:var(--muted); font-size:13px; }}
::-webkit-scrollbar {{ width:8px; height:8px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:rgba(148,163,184,0.18); border-radius:999px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(148,163,184,0.28); }}
</style>
</head><body>
<div class="wrap"><table><thead><tr id="hdr"></tr></thead><tbody id="tbody"></tbody></table></div>
<script>
const DATA = {data_json};
const COLS = [
  'ticker','company','verdict','average_score',
  'circle_of_competence','competitive_advantage','management','business_economics',
  'balance_sheet','valuation','margin_of_safety','temperament',
  'iv_conservative','iv_base','iv_bull','mos_pct',
  'confidence','red_flag_count','analysis_date'
];
const HEADERS = {{
  ticker:'Ticker',company:'Company',verdict:'Verdict',average_score:'Avg',
  circle_of_competence:'CoC',competitive_advantage:'Moat',management:'Mgmt',
  business_economics:'Econ',balance_sheet:'B/S',valuation:'Val',
  margin_of_safety:'MoS',temperament:'Temp',
  iv_conservative:'IV Bear',iv_base:'IV Base',iv_bull:'IV Bull',
  mos_pct:'MOS %',confidence:'Conf',red_flag_count:'Flags',analysis_date:'Date'
}};
const TIPS = {{
  ticker:'Stock ticker symbol',company:'Company name',verdict:'Investment decision: Own, Watch, or Pass',
  average_score:'Average of all 8 umbrella scores (0-10)',
  circle_of_competence:'Circle of Competence',competitive_advantage:'Durable Competitive Advantage',
  management:'Management & Capital Allocation',business_economics:'Business Economics',
  balance_sheet:'Balance Sheet Safety',valuation:'Valuation vs intrinsic value',
  margin_of_safety:'Margin of Safety',temperament:'Temperament & Time Horizon',
  iv_conservative:'Bear-case IV per share',iv_base:'Base-case IV per share',iv_bull:'Bull-case IV per share',
  mos_pct:'Margin of Safety % (negative = overvalued)',confidence:'Confidence level',
  red_flag_count:'Number of red flags',analysis_date:'Analysis completion date'
}};
const UMBRELLAS = new Set(['circle_of_competence','competitive_advantage','management','business_economics','balance_sheet','valuation','margin_of_safety','temperament','average_score']);
const IVS = new Set(['iv_conservative','iv_base','iv_bull']);

function esc(s) {{ return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
function scoreStyle(v) {{ if(v==null)return''; return v<4?'color:var(--danger);font-weight:700;':v<7?'color:var(--warning);font-weight:700;':'color:var(--positive);font-weight:700;'; }}
function mosStyle(v) {{ if(v==null)return''; return v>=0?'color:var(--positive);font-weight:700;':'color:var(--danger);font-weight:700;'; }}
function verdictStyle(v) {{ if(v==='Own')return'color:var(--positive);font-weight:700;'; if(v==='Watch')return'color:var(--warning);font-weight:700;'; if(v==='Pass')return'color:var(--danger);font-weight:700;'; return''; }}

let sortKey='average_score', sortDir='desc';

function cell(key,val) {{
  const mono="font-family:'JetBrains Mono',monospace;";
  if(key==='ticker') return `<td class="sym">${{esc(val||'—')}}</td>`;
  if(key==='company') return `<td class="co">${{esc(val||'—')}}</td>`;
  if(key==='verdict') return `<td style="text-align:center;${{verdictStyle(val)}}">${{esc(val||'—')}}</td>`;
  if(UMBRELLAS.has(key)) {{
    let d=val!=null?(key==='average_score'?Number(val).toFixed(1):String(val)):'—';
    return `<td style="text-align:center;${{mono}}${{scoreStyle(val)}}">${{d}}</td>`;
  }}
  if(IVS.has(key)) {{
    let d=val!=null?'$'+Number(val).toLocaleString(undefined,{{maximumFractionDigits:0}}):'—';
    return `<td style="text-align:center;${{mono}}color:var(--text);">${{d}}</td>`;
  }}
  if(key==='mos_pct') {{
    let d=val!=null?(val>=0?'+':'')+Number(val).toFixed(1)+'%':'—';
    return `<td style="text-align:center;${{mono}}${{mosStyle(val)}}">${{d}}</td>`;
  }}
  if(key==='confidence') {{
    let raw=String(val||'—'), first=raw.split(/[\\s]/)[0].toLowerCase();
    let c=first==='high'?'var(--positive)':first==='medium'?'var(--warning)':first==='low'?'var(--danger)':'var(--subtle)';
    let label=first.charAt(0).toUpperCase()+first.slice(1);
    return `<td title="${{esc(raw)}}" style="text-align:center;color:${{c}};font-size:11px;font-weight:600;text-transform:uppercase;">${{esc(label)}}</td>`;
  }}
  if(key==='red_flag_count') {{
    let s=val>0?'color:var(--danger);font-weight:600;':'color:var(--subtle);';
    return `<td style="text-align:center;${{s}}">${{val!=null?val:'—'}}</td>`;
  }}
  if(key==='analysis_date') {{
    let d=val?String(val).replace(/-/g,'/'):'—';
    return `<td style="text-align:center;color:var(--muted);${{mono}}font-size:11px;">${{esc(d)}}</td>`;
  }}
  return `<td style="color:var(--text);">${{esc(val!=null?val:'—')}}</td>`;
}}

function render() {{
  const hdr=document.getElementById('hdr');
  const tbody=document.getElementById('tbody');
  const arrow=k=>sortKey===k?(sortDir==='desc'?' ↓':' ↑'):'';
  hdr.innerHTML=COLS.map(k=>`<th>${{esc(HEADERS[k])}}${{arrow(k)}}<span class="tip">${{esc(TIPS[k]||'')}}</span></th>`).join('');
  hdr.querySelectorAll('th').forEach((th,i)=>th.addEventListener('click',()=>sortBy(COLS[i])));

  if(!DATA.length) {{ tbody.innerHTML='<tr><td colspan="19" class="empty">No tickers match the current filters.</td></tr>'; return; }}
  tbody.innerHTML=DATA.map(r=>'<tr>'+COLS.map(k=>cell(k,r[k])).join('')+'</tr>').join('');
}}

function sortBy(key) {{
  if(sortKey===key) sortDir=sortDir==='desc'?'asc':'desc';
  else {{ sortKey=key; sortDir='desc'; }}
  const dir=sortDir==='desc'?-1:1;
  DATA.sort((a,b)=>{{
    let va=a[key],vb=b[key];
    if(va==null&&vb==null)return 0;
    if(va==null)return 1; if(vb==null)return -1;
    if(typeof va==='string')return va.localeCompare(vb)*dir;
    return(va-vb)*dir;
  }});
  render();
}}

// Initial sort
sortBy('average_score');
</script>
</body></html>
"""
    components.html(scoreboard_html, height=height, scrolling=False)

    # Ticker buttons for opening reports (JS can't trigger Streamlit callbacks)
    tickers = filtered["ticker"].tolist() if not filtered.empty else []
    if tickers:
        st.caption("Click a ticker to open its report:")
        rows_of_buttons = [tickers[i:i + 10] for i in range(0, min(len(tickers), 40), 10)]
        for btn_row in rows_of_buttons:
            cols = st.columns(len(btn_row))
            for idx, ticker in enumerate(btn_row):
                if cols[idx].button(ticker, key=f"sb-open-{ticker}", use_container_width=True):
                    _select_report_ticker(ticker)


def render_pipeline_section(pipeline: dict[str, Any], report_count: int) -> None:
    render_kicker("Pipeline Flow")
    st.title("Pipeline")
    st.caption("Latest scan and triage flow, with funnel view and bucket mix from the stored outputs.")

    scan = pipeline.get("scan") or {}
    triage = pipeline.get("triage") or {}
    st.plotly_chart(_pipeline_funnel(pipeline, report_count), use_container_width=True)

    charts = st.columns(2)
    with charts[0]:
        st.subheader("Bucket mix")
        buckets = scan.get("counts_by_bucket") or {}
        st.markdown(
            _bar_stack_html(
                [{"label": label, "value": value, "color": "#c15f3c"} for label, value in sorted(buckets.items(), key=lambda item: item[1], reverse=True)[:10]]
            ),
            unsafe_allow_html=True,
        )
    with charts[1]:
        st.subheader("Sector mix")
        sectors = scan.get("counts_by_sector") or {}
        st.markdown(
            _bar_stack_html(
                [{"label": label, "value": value, "color": "#93c5fd"} for label, value in sorted(sectors.items(), key=lambda item: item[1], reverse=True)]
            ),
            unsafe_allow_html=True,
        )

    lower = st.columns(2)
    with lower[0]:
        st.subheader("B1 counts")
        b1 = triage.get("b1") or {}
        st.metric("Advance", b1.get("advance", 0))
        st.metric("Hold", b1.get("hold", 0))
        st.metric("Reject", b1.get("reject", 0))
    with lower[1]:
        st.subheader("Focused shortlist")
        shortlist = triage.get("deep_dive_shortlist") or []
        if shortlist:
            for item in shortlist[:8]:
                label = f"{item['ticker']} - {item.get('next_action', '').replace('_', ' ')}"
                if st.button(label, key=f"pipeline-shortlist-{item['ticker']}", use_container_width=True):
                    _select_report_ticker(item["ticker"])
        else:
            st.info("No shortlist found in the latest triage output.")
