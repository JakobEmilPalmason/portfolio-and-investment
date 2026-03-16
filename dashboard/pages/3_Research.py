from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import (
    format_ratio,
    get_research_catalog,
    get_research_detail,
    queue_state_color,
)


def _badge(label: str, color: str) -> str:
    return (
        f"<span style='display:inline-block;padding:0.28rem 0.7rem;border-radius:999px;"
        f"background:{color};color:white;font-weight:700;font-size:0.82rem;letter-spacing:0.02em;'>"
        f"{label}</span>"
    )


def _bullet_block(items: list[str], empty_message: str) -> None:
    if not items:
        st.write(empty_message)
        return
    for item in items:
        st.markdown(f"- {item}")


def main() -> None:
    st.markdown('<div class="dashboard-kicker">Report Browser</div>', unsafe_allow_html=True)
    st.title("Research")

    catalog = get_research_catalog()
    if not catalog:
        st.info("No FINAL-REPORT.json files were found under runs/*/reports/.")
        return

    options = [item["ticker"] for item in catalog]
    selected_ticker = st.selectbox(
        "Ticker",
        options,
        format_func=lambda ticker: next(
            (
                f"{entry['ticker']} — {entry['company']}"
                for entry in catalog
                if entry["ticker"] == ticker
            ),
            ticker,
        ),
    )
    detail = get_research_detail(selected_ticker)
    if detail is None:
        st.error(f"Unable to load report details for {selected_ticker}.")
        return

    report = detail["report"]
    queue_entry = detail["queue"] or {}
    queue_state = queue_entry.get("current_state", "not_in_queue")

    top_left, top_right = st.columns([3, 2])
    with top_left:
        st.subheader(f"{report.get('ticker')} — {report.get('company')}")
        badges = [
            _badge(report.get("verdict", "Unknown"), "#0f766e" if report.get("verdict") == "Own" else "#475569"),
            _badge(queue_state, queue_state_color(queue_state)),
        ]
        st.markdown(" ".join(badges), unsafe_allow_html=True)
        st.caption(f"Analysis date: {report.get('analysis_date', 'N/A')}")
    with top_right:
        st.metric("Average Score", format_ratio(report.get("average_score")))
        st.caption(f"Confidence: {report.get('confidence', 'N/A')}")

    if not detail["scores"].empty:
        st.subheader("Scores")
        st.dataframe(detail["scores"], use_container_width=True, hide_index=True)

    queue_columns = st.columns(3)
    queue_columns[0].metric("Queue State", queue_state)
    queue_columns[1].metric("Thesis Status", queue_entry.get("thesis_status", "N/A"))
    queue_columns[2].metric("Next Action", queue_entry.get("next_required_action", "N/A"))

    strengths_col, risks_col = st.columns(2)
    with strengths_col:
        st.subheader("Key Strengths")
        _bullet_block(detail["key_strengths"], "No strengths listed in FINAL-REPORT.json.")
    with risks_col:
        st.subheader("Key Risks")
        _bullet_block(detail["key_risks"], "No risks listed in FINAL-REPORT.json.")

    st.subheader("Full Report")
    if detail["md_path"]:
        st.caption(detail["md_path"])
        if detail["markdown"]:
            st.markdown(detail["markdown"])
        else:
            st.info("FINAL-REPORT.md exists but could not be read.")
    else:
        st.info("No FINAL-REPORT.md file was found for this ticker.")


if __name__ == "__main__":
    main()
