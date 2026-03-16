from __future__ import annotations

import html

import streamlit as st


APP_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  color-scheme: dark;
  --bg: #0c0a09;
  --bg-strong: #1c1917;
  --surface: #1c1917;
  --surface-strong: #292524;
  --surface-soft: rgba(28, 25, 23, 0.94);
  --border: rgba(68, 64, 60, 0.82);
  --border-strong: rgba(120, 113, 108, 0.92);
  --text: #fafaf9;
  --muted: #a8a29e;
  --subtle: #78716c;
  --accent: #c15f3c;
  --accent-soft: rgba(193, 95, 60, 0.16);
  --positive: #86efac;
  --positive-soft: rgba(20, 83, 45, 0.52);
  --warning: #fbbf24;
  --warning-soft: rgba(120, 53, 15, 0.48);
  --danger: #fca5a5;
  --danger-soft: rgba(127, 29, 29, 0.42);
  --info: #93c5fd;
  --info-soft: rgba(30, 64, 175, 0.35);
}

html, body, .stApp, [class*="css"] {
  font-family: 'Manrope', system-ui, sans-serif;
}

code, pre, kbd, .dashboard-mono {
  font-family: 'JetBrains Mono', ui-monospace, monospace !important;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at top left, rgba(193, 95, 60, 0.12), transparent 26%),
    linear-gradient(180deg, #181311 0%, #100d0b 18%, #0c0a09 46%, #0c0a09 100%);
}

.stApp, p, li, label, span, div {
  color: var(--text);
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(21, 18, 16, 0.98), rgba(12, 10, 9, 0.98));
  border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
  color: var(--text);
}

.block-container {
  max-width: 1420px;
  padding-top: 1.25rem;
  padding-bottom: 2.2rem;
}

[data-testid="stMetric"] {
  background: linear-gradient(180deg, rgba(28, 25, 23, 0.98), rgba(22, 18, 16, 0.98));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 0.85rem 1rem;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

[data-testid="stMetricLabel"] {
  color: var(--subtle);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.7rem;
  font-weight: 700;
}

[data-testid="stMetricValue"] {
  color: var(--text);
}

.dashboard-kicker {
  margin-bottom: 0.4rem;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--subtle);
}

.dashboard-hero,
.surface-card {
  border: 1px solid var(--border);
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(28, 25, 23, 0.98), rgba(20, 16, 14, 0.98));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

.dashboard-hero {
  position: relative;
  overflow: hidden;
  padding: 1.35rem 1.4rem;
  background:
    linear-gradient(145deg, rgba(255,255,255,0.04), rgba(255,255,255,0)),
    linear-gradient(180deg, rgba(28, 25, 23, 0.99), rgba(20, 16, 14, 0.99));
}

.dashboard-hero::after {
  content: '';
  position: absolute;
  right: -110px;
  bottom: -140px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(193, 95, 60, 0.2), transparent 68%);
  pointer-events: none;
}

.surface-card {
  padding: 1.15rem 1.2rem;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
}

.section-subtitle {
  margin-top: 0.3rem;
  color: var(--muted);
  line-height: 1.65;
  font-size: 0.95rem;
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-top: 1rem;
}

.metric-card {
  min-height: 92px;
  padding: 0.9rem 1rem;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(41, 37, 36, 0.42);
}

.metric-card .metric-label {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--subtle);
}

.metric-card .metric-value {
  margin-top: 0.45rem;
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--text);
}

.metric-card .metric-meta {
  margin-top: 0.35rem;
  font-size: 0.82rem;
  color: var(--muted);
}

.tone-accent .metric-value { color: var(--accent); }
.tone-positive .metric-value { color: var(--positive); }
.tone-warning .metric-value { color: var(--warning); }
.tone-danger .metric-value { color: var(--danger); }
.tone-info .metric-value { color: var(--info); }

.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  padding: 0.26rem 0.72rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border: 1px solid var(--border);
}

.pill-neutral {
  background: rgba(255,255,255,0.03);
  color: var(--muted);
}

.pill-accent {
  background: var(--accent-soft);
  color: var(--accent);
  border-color: rgba(202, 140, 98, 0.32);
}

.pill-positive {
  background: var(--positive-soft);
  color: var(--positive);
  border-color: rgba(120, 194, 170, 0.28);
}

.pill-warning {
  background: var(--warning-soft);
  color: var(--warning);
  border-color: rgba(209, 171, 104, 0.28);
}

.pill-danger {
  background: var(--danger-soft);
  color: var(--danger);
  border-color: rgba(208, 131, 131, 0.28);
}

.pill-info {
  background: var(--info-soft);
  color: var(--info);
  border-color: rgba(147, 197, 253, 0.24);
}

.bar-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.bar-row {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr) 54px;
  gap: 0.7rem;
  align-items: center;
}

.bar-row .bar-label {
  color: var(--muted);
  font-size: 0.86rem;
}

.bar-row .bar-track {
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
}

.bar-row .bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-row .bar-value {
  text-align: right;
  color: var(--text);
  font-size: 0.82rem;
}

.table-note {
  color: var(--subtle);
  font-size: 0.78rem;
  letter-spacing: 0.03em;
}

.split-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.stat-line {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.7rem 0;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.stat-line:first-child {
  border-top: none;
  padding-top: 0;
}

.stat-line .stat-label {
  color: var(--muted);
}

.stat-line .stat-value {
  color: var(--text);
  font-weight: 700;
}

@media (max-width: 920px) {
  .split-grid {
    grid-template-columns: 1fr;
  }

  .bar-row {
    grid-template-columns: 110px minmax(0, 1fr) 48px;
  }
}
</style>
"""


def apply_dashboard_theme() -> None:
    st.markdown(APP_STYLE, unsafe_allow_html=True)


def render_kicker(text: str) -> None:
    st.markdown(f'<div class="dashboard-kicker">{html.escape(text)}</div>', unsafe_allow_html=True)


def pill(label: str, tone: str = "neutral") -> str:
    return f'<span class="pill pill-{tone}">{html.escape(label)}</span>'


def render_hero(title: str, subtitle: str, metrics: list[dict[str, str]]) -> None:
    cards = "".join(
        f"""
        <div class="metric-card {html.escape(card.get('tone', ''))}">
          <div class="metric-label">{html.escape(card['label'])}</div>
          <div class="metric-value">{html.escape(card['value'])}</div>
          <div class="metric-meta">{html.escape(card.get('meta', ''))}</div>
        </div>
        """
        for card in metrics
    )
    st.markdown(
        f"""
        <section class="dashboard-hero">
          <div class="section-title">{html.escape(title)}</div>
          <div class="section-subtitle">{html.escape(subtitle)}</div>
          <div class="metric-strip">{cards}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_surface_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="surface-card">
          <div class="section-title">{html.escape(title)}</div>
          <div class="section-subtitle">{html.escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
