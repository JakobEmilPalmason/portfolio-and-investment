from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.theme import apply_dashboard_theme
from dashboard.workspace import maybe_open_pending_dialog, render_sidebar_controls


def main() -> None:
    st.set_page_config(
        page_title="Portfolio",
        page_icon=str(Path(__file__).parent / "favicon.png"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dashboard_theme()

    navigation = st.navigation(
        [
            st.Page("pages/1_Portfolio.py", title="Workspace", icon=":material/dashboard:", default=True),
            st.Page("pages/3_Research.py", title="Research", icon=":material/biotech:"),
            st.Page("pages/2_Performance.py", title="Performance", icon=":material/show_chart:"),
            st.Page("pages/4_PreBuy.py", title="Pre-Buy", icon=":material/verified:"),
            st.Page("pages/5_Simulator.py", title="Simulator", icon=":material/balance:"),
            st.Page("pages/6_Agents.py", title="Agents", icon=":material/smart_toy:"),
        ],
        position="sidebar",
    )
    render_sidebar_controls()
    navigation.run()
    maybe_open_pending_dialog()


if __name__ == "__main__":
    main()
