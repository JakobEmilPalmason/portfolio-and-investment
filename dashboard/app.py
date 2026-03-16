from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

APP_STYLE = """
<style>
:root {
  --dashboard-ink: #112132;
  --dashboard-muted: #536072;
  --dashboard-surface: rgba(255, 252, 246, 0.86);
  --dashboard-border: rgba(17, 33, 50, 0.08);
  --dashboard-accent: #0f766e;
  --dashboard-alert: #b45309;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 28%),
    radial-gradient(circle at top right, rgba(180, 83, 9, 0.12), transparent 24%),
    linear-gradient(180deg, #f6f0e4 0%, #fdfbf7 45%, #f2f7f5 100%);
}

.stApp {
  color: var(--dashboard-ink);
}

.block-container {
  padding-top: 1.4rem;
  padding-bottom: 2rem;
  max-width: 1280px;
}

[data-testid="stMetric"] {
  background: var(--dashboard-surface);
  border: 1px solid var(--dashboard-border);
  border-radius: 18px;
  padding: 0.75rem 1rem;
  box-shadow: 0 16px 40px rgba(17, 33, 50, 0.06);
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255, 248, 238, 0.95), rgba(244, 249, 247, 0.95));
  border-right: 1px solid rgba(17, 33, 50, 0.08);
}

h1, h2, h3 {
  letter-spacing: -0.02em;
}

.dashboard-kicker {
  color: var(--dashboard-muted);
  font-size: 0.95rem;
  margin-bottom: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
</style>
"""


def main() -> None:
    st.set_page_config(
        page_title="Portfolio Dashboard",
        page_icon=":material/finance_mode:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(APP_STYLE, unsafe_allow_html=True)
    st.sidebar.markdown("### Portfolio Dashboard")
    st.sidebar.caption("SQLite-backed monitoring for the paper-trading system.")

    navigation = st.navigation(
        [
            st.Page("pages/1_Portfolio.py", title="Portfolio", icon=":material/account_balance_wallet:", default=True),
            st.Page("pages/2_Performance.py", title="Performance", icon=":material/show_chart:"),
            st.Page("pages/3_Research.py", title="Research", icon=":material/biotech:"),
        ],
        position="sidebar",
    )
    navigation.run()


if __name__ == "__main__":
    main()
