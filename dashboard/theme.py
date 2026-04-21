from __future__ import annotations

import html

import streamlit as st


APP_STYLE = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
  color-scheme: dark;
  --font-display: 'General Sans', 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
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
  font-family: var(--font-body);
  font-weight: 400;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  font-weight: 500;
}

code, pre, kbd, .dashboard-mono {
  font-family: var(--font-mono) !important;
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
  font-family: var(--font-display);
  color: var(--subtle);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.7rem;
  font-weight: 500;
}

[data-testid="stMetricValue"] {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--text);
}

.dashboard-kicker {
  font-family: var(--font-display);
  margin-bottom: 0.4rem;
  font-size: 0.8rem;
  font-weight: 500;
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
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 500;
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
  font-family: var(--font-display);
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--subtle);
}

.metric-card .metric-value {
  font-family: var(--font-display);
  margin-top: 0.45rem;
  font-size: 1.45rem;
  font-weight: 500;
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
  font-weight: 500;
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
  font-weight: 500;
}

/* ── Custom HTML Tables ── */
.custom-table {
  width: 100%;
  min-width: 700px;
  border-collapse: separate;
  border-spacing: 0;
}
.custom-table thead {
  background: rgba(12, 10, 9, 0.94);
}
.custom-table th {
  font-family: var(--font-display);
  padding: 12px 16px;
  border-bottom: 1px solid rgba(68, 64, 60, 0.9);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-align: left;
  color: var(--subtle);
  white-space: nowrap;
}
.custom-table td {
  padding: 13px 16px;
  border-bottom: 1px solid rgba(68, 64, 60, 0.46);
  vertical-align: top;
  font-size: 13px;
  line-height: 1.35;
  color: var(--text);
}
.custom-table tbody tr:last-child td { border-bottom: none; }

.mini-table {
  width: 100%;
  border-collapse: collapse;
}
.mini-table th {
  font-family: var(--font-display);
  padding: 0 0 10px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--subtle);
  text-align: left;
}
.mini-table td {
  padding: 11px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  vertical-align: top;
  color: var(--text);
}

.table-symbol {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--accent);
}
.table-meta {
  margin-top: 2px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--muted);
}
.table-mono {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

/* ── Freshness Dots ── */
.queue-freshness {
  margin-top: 5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  line-height: 1.3;
  color: var(--muted);
}
.queue-freshness-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  display: inline-block;
  flex-shrink: 0;
}
.queue-freshness-age {
  color: var(--subtle);
}

/* ── Badge Stacks & Tags ── */
.queue-badge-stack {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 6px;
  min-height: 24px;
}
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 500;
  line-height: 1.5;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.03);
  color: var(--muted);
}
.b-deep-research { background: var(--accent-soft); color: var(--accent); border-color: rgba(202, 140, 98, 0.28); }
.b-monitor-only,
.b-owned,
.b-own,
.b-monitor { background: var(--positive-soft); color: var(--positive); border-color: rgba(120, 194, 170, 0.28); }
.b-watchlist,
.b-watch,
.b-medium,
.b-deep-dive { background: var(--warning-soft); color: var(--warning); border-color: rgba(209, 171, 104, 0.28); }
.b-rejected,
.b-pass,
.b-high,
.b-discard { background: var(--danger-soft); color: var(--danger); border-color: rgba(208, 131, 131, 0.28); }
.b-approved,
.b-refresh { background: rgba(68, 64, 60, 0.42); color: var(--text); border-color: var(--border-strong); }
.b-inbox,
.b-low,
.b-triage { background: rgba(28, 25, 23, 0.7); color: var(--muted); border-color: var(--border); }

.queue-tag-list {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 6px;
  max-width: 280px;
}
.queue-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 999px;
  border: 1px solid rgba(68, 64, 60, 0.82);
  background: rgba(28, 25, 23, 0.82);
  color: var(--muted);
  font-size: 10px;
  line-height: 1.25;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

/* ── Score Dots ── */
.score-dots {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.score-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* ── Warning & Empty Panels ── */
.warning-item {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(209, 171, 104, 0.2);
  background: linear-gradient(180deg, rgba(120, 53, 15, 0.38), rgba(69, 26, 3, 0.12));
  color: var(--warning);
  font-size: 13px;
  line-height: 1.55;
}
.empty-panel {
  padding: 18px;
  border-radius: 14px;
  border: 1px dashed var(--border);
  background: rgba(28, 25, 23, 0.64);
  color: var(--muted);
  font-size: 14px;
  line-height: 1.65;
}

/* ── ag-Grid Dark Theme ── */
.ag-theme-alpine-dark,
.ag-theme-streamlit,
[class*="ag-theme"] {
  --ag-background-color: transparent;
  --ag-odd-row-background-color: rgba(12, 10, 9, 0.44);
  --ag-header-background-color: rgba(12, 10, 9, 0.9);
  --ag-border-color: var(--border);
  --ag-row-border-color: rgba(68, 64, 60, 0.55);
  --ag-foreground-color: var(--text);
  --ag-secondary-foreground-color: var(--muted);
  --ag-header-foreground-color: var(--subtle);
  --ag-selected-row-background-color: rgba(193, 95, 60, 0.12);
  --ag-row-hover-color: rgba(41, 37, 36, 0.5);
  --ag-font-family: var(--font-body);
  --ag-font-size: 13px;
  --ag-cell-horizontal-padding: 14px;
  --ag-row-height: 50px;
  --ag-header-height: 42px;
  --ag-wrapper-border-radius: 12px;
}

/* ── Markdown Content Styling ── */
.md-content h1 { font-family: var(--font-display); font-size: 1.4rem; font-weight: 500; margin: 1.2rem 0 0.4rem; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }
.md-content h2 { font-family: var(--font-display); font-size: 1.15rem; font-weight: 500; margin: 1rem 0 0.3rem; color: var(--text); }
.md-content h3 { font-family: var(--font-display); font-size: 1rem; font-weight: 500; margin: 0.75rem 0 0.25rem; color: var(--muted); }
.md-content p  { margin: 0.5rem 0; color: #cbd5e1; line-height: 1.7; }
.md-content ul { list-style: disc; padding-left: 1.5rem; margin: 0.5rem 0; }
.md-content ol { list-style: decimal; padding-left: 1.5rem; margin: 0.5rem 0; }
.md-content li { margin: 0.25rem 0; color: #cbd5e1; line-height: 1.55; }
.md-content table { width: 100%; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.85rem; }
.md-content th { font-family: var(--font-display); background: rgba(12, 10, 9, 0.9); padding: 0.4rem 0.65rem; text-align: left; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; color: var(--muted); border: 1px solid var(--border); }
.md-content td { padding: 0.4rem 0.65rem; border: 1px solid var(--border); color: #cbd5e1; }
.md-content tr:nth-child(even) td { background: rgba(12, 10, 9, 0.36); }
.md-content code { background: rgba(12, 10, 9, 0.7); padding: 0.1rem 0.3rem; border-radius: 5px; font-size: 0.85em; color: var(--warning); }
.md-content pre  { background: rgba(12, 10, 9, 0.8); padding: 1rem; border-radius: 12px; overflow-x: auto; margin: 0.75rem 0; }
.md-content pre code { background: none; padding: 0; }
.md-content strong { color: var(--text); font-weight: 500; }
.md-content blockquote { border-left: 3px solid var(--accent); padding-left: 1rem; margin: 0.5rem 0; color: var(--muted); }
.md-content hr { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }
.md-content a { color: var(--accent); text-decoration: underline; }

/* ── Agent Arena ── */
.agent-chart-hero {
  border: 1px solid rgba(193, 95, 60, 0.3);
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(28, 25, 23, 0.99), rgba(15, 12, 10, 0.99));
  padding: 1.5rem 1.5rem 0.5rem;
  box-shadow: 0 0 40px rgba(193, 95, 60, 0.08), inset 0 1px 0 rgba(255,255,255,0.03);
  margin-bottom: 1.5rem;
}
.agent-chart-title {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--text);
  margin-bottom: 0.15rem;
}
.agent-chart-subtitle {
  font-size: 0.82rem;
  color: var(--muted);
  margin-bottom: 0.8rem;
}

.agent-panel {
  border: 1px solid var(--border);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(28, 25, 23, 0.98), rgba(18, 15, 13, 0.98));
  padding: 1.2rem;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.agent-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
  padding-bottom: 0.7rem;
  border-bottom: 1px solid var(--border);
}
.agent-panel-name {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 500;
  color: var(--text);
}
.agent-panel-date {
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 500;
}

.agent-legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}

.pos-row {
  display: grid;
  grid-template-columns: 80px 1fr 60px 70px 70px 80px 70px;
  gap: 0.5rem;
  align-items: center;
  padding: 0.7rem 0.8rem;
  border-bottom: 1px solid rgba(68, 64, 60, 0.35);
}
.pos-row:last-child { border-bottom: none; }
.pos-row:hover { background: rgba(41, 37, 36, 0.4); border-radius: 10px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.18); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.28); }

/* ── Scoreboard Table ── */
.sb-table-wrap {
  overflow: auto;
  max-height: calc(97vh - 220px);
  border-radius: 12px;
  border: 1px solid var(--border);
}
.sb-table {
  min-width: 1200px;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
.sb-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
}
.sb-table th {
  font-family: var(--font-display);
  padding: 14px 14px;
  background: rgba(12, 10, 9, 0.96);
  border-bottom: 1px solid rgba(68, 64, 60, 0.9);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-align: center;
  color: var(--subtle);
  white-space: nowrap;
}
.sb-table th:nth-child(1),
.sb-table th:nth-child(2) { text-align: left; }
.sb-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(68, 64, 60, 0.46);
  font-size: 14px;
  text-align: center;
  color: var(--text);
}
.sb-table td:first-child { text-align: left; }
.sb-table td:nth-child(2) { text-align: left; }
.sb-table tbody tr:last-child td { border-bottom: none; }

.sb-filter-bar {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.sb-filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.sb-filter-label {
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--subtle);
}
.sb-filter-btn {
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  cursor: pointer;
  transition: all 0.15s;
}
.sb-filter-btn:hover {
  border-color: var(--border-strong);
  color: var(--text);
}
.sb-filter-btn.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.sb-count {
  font-size: 12px;
  color: var(--subtle);
}

/* ── Score Row ── */
.score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}
.score-row:last-child { border-bottom: none; }
.score-row .score-label {
  font-size: 0.82rem;
  color: var(--muted);
}
.score-row .score-value {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  font-weight: 700;
  min-width: 1.5rem;
  text-align: right;
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


_FAVICON_JS = """
<script>
(function() {
    var ico32 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAsElEQVR4nO2XwRWAIAxDpcswkqM4A6MwktPoSZ9CofRBWw7kiJB8Agd0G1PnsV+17z5Ex/FrmkyF9sCAVHjr2iJhTzCmUhtoA6PDa54ZgER4zRuoCdIQ5CWU1gugsXssC7TDU4h5jsBKzqL+r8wbWAALYAEA9w03Uj5EZ9/AFAAWx/BkQjqgGf4DsNIPQKOFNCNrQBIC80aPQAKi5EkG9T5YqM2Ql7CnjZa1bPPRv+c3UMNJlZemu1sAAAAASUVORK5CYII=";
    var ico180 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAYAAAA9zQYyAAAEp0lEQVR4nO3Y23XTQABFUSfNpCRKoQZKSUlUAx8ssRTHD8ma59XeBYA1OlzGfrtw2O+fP/6U+HM+fn2+lfhzzswBblQq2leJfRuHdEPveLcS+XcO5DJPwM8I/MRBp0R8z1njPtVDp0d8z5niPsWDnjXka2cIO/YBRfxYatxxDyXkfdLCjnkYIR+TEvb0DyHksmYPe9oPL+S6Zg17ug8t5LZmC/u99wfYQ8ztzXbmU/zrm+1QU82w1sMvtJjHMcO7GPZf3AyHd2ajrvWQCy3m8Y36joYLetSD4rsR39Uw/22MeDhsN8oVZIiFFvP8RnmH3YMe5SA4boR32TXoEQ6Asnq/025B935w6un5bptf5IV8Lq2/LDZdaDGfT+t33ixoMZ9Xy3ffJGgx06qB6kGLmUWLFrr/Dg0lVQ3aOnOtdhPVghYz99Rso0rQYuaZWo0UD1rMbFWjlaJBi5m9SjfjVw6iFAvaOvOqku0UCVrMHFWqocNBi5lSSrTkDk2UQ0FbZ0o72tTLQYuZWo605cpBlJeCts7U9mpju4MWM6280porB1F2BW2daW1vcxaaKJuDts70sqc9C02UTUFbZ3rb2qCFJsrToK0zo9jSooUmysOgrTOjedakhSaKoIlyN2jXDUb1qE0LTZSbQVtnRnevUQtNFEET5VvQrhvM4larFpoogibKl6BdN5jNdbMWmiiCJoqgiSJoorz5yY4kFpoogiaKoIkiaKIImiiCJoqgiSJoogiaKIImiqCJImiiCJoogiaKoIkiaKIImijvH78+33p/CCjh49fnm4UmiqCJImiiCJoogiaKoInyfrn8+7mj9weBI5aGLTRRBE0UQRNF0ET5H7Qvhsxq3a6FJoqgiSJoonwJ2j2a2Vw3a6GJImiifAvatYNZ3GrVQhNF0ES5GbRrB6O716iFJsrdoK00o3rUpoUmiqCJ8jBo1w5G86xJC02Up0FbaUaxpUULTZRNQVtpetvaoIUmyuagrTS97GnPQhNlV9BWmtb2NmehibI7aCtNK6+09tJCi5raXm3MlYMoLwdtpanlSFuHFlrUlHa0KVcOohwO2kpTSomWiiy0qDmqVEPFrhyi5lUl23GHJkrRoK00e5VupvhCi5qtarRS5cohap6p1Ui1O7SouadmG1W/FIqaa7Wb8CsHUaoHbaVZtGihyUKLmlYNNLtyiPq8Wr77pndoUZ9P63feLbDfP3/86fV3U1+v8er2K4e1ztXz3Xb92U7UeXq/0+6/Q/c+AMoZ4V12D/pyGeMgOGaUdzjEh1jzZXEuo4S8GGKh10Y7IO4b8V0NF/TlMuZB8dWo72jID7XmCjKWUUNeDLnQa6Mf4JnM8C6G/4Br1rqPGUJeDL/QazMdbIrZznyqD7tmreuaLeTFlB96TdhlzRryYuoPvybsY2YPeRHxEGvC3icl5EXUw6wJ+7G0kBeRD3VN3P+kRrwW/4BrZw37DCEvTvOg19LjPlPEa6d86GspcZ814rXTH8AtswQu4O8cyEa9IxfvNg6pgFKxi/a4v/g3orByx+a4AAAAAElFTkSuQmCC";
    // Replace existing favicon
    var links = document.querySelectorAll("link[rel*='icon']");
    links.forEach(function(l) { l.parentNode.removeChild(l); });
    // Standard favicon
    var link = document.createElement('link');
    link.rel = 'icon'; link.type = 'image/png'; link.href = ico32;
    document.head.appendChild(link);
    // Apple touch icon
    var apple = document.createElement('link');
    apple.rel = 'apple-touch-icon'; apple.href = ico180;
    document.head.appendChild(apple);
})();
</script>
"""


def apply_dashboard_theme() -> None:
    st.markdown(APP_STYLE, unsafe_allow_html=True)
    st.markdown(_FAVICON_JS, unsafe_allow_html=True)


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


# ---------------------------------------------------------------------------
# Score helpers
# ---------------------------------------------------------------------------

def _score_color(score: float | int | None) -> str:
    if score is None:
        return "var(--subtle)"
    if score >= 8:
        return "var(--positive)"
    if score >= 6:
        return "var(--warning)"
    return "var(--danger)"


def score_dots(score: float | int | None, size: int = 8) -> str:
    """Render 10 inline dots filled to `score`, color-coded by threshold."""
    if score is None:
        return '<span style="color:var(--subtle);font-size:11px">\u2014</span>'
    color = _score_color(score)
    dots = []
    for i in range(10):
        bg = color if i < int(score) else "rgba(255,255,255,0.08)"
        dots.append(
            f'<span class="score-dot" style="width:{size}px;height:{size}px;background:{bg}"></span>'
        )
    return '<span class="score-dots">' + "".join(dots) + "</span>"


def score_row_html(label: str, score: float | int | None) -> str:
    """One row of Category | Score number | Dots."""
    if score is None:
        return ""
    color = _score_color(score)
    return (
        f'<div class="score-row">'
        f'<span class="score-label">{html.escape(label)}</span>'
        f'<span style="display:flex;align-items:center;gap:8px;">'
        f'<span class="score-value" style="color:{color}">{score}</span>'
        f"{score_dots(score, 6)}"
        f"</span></div>"
    )


# ---------------------------------------------------------------------------
# Badge helpers
# ---------------------------------------------------------------------------

_STATE_CLS = {
    "deep_research": "b-deep-research",
    "monitor_only": "b-monitor-only",
    "watchlist": "b-watchlist",
    "inbox": "b-inbox",
    "rejected": "b-rejected",
    "approved": "b-approved",
    "owned": "b-owned",
    "triage": "b-triage",
}

_VERDICT_CLS = {"Own": "b-own", "Watch": "b-watch", "Pass": "b-pass"}


def verdict_badge(verdict: str | None) -> str:
    if not verdict:
        return '<span style="color:var(--subtle)">\u2014</span>'
    cls = _VERDICT_CLS.get(verdict, "b-inbox")
    return f'<span class="badge {cls}">{html.escape(verdict)}</span>'


def state_badge(state: str | None) -> str:
    if not state:
        return '<span style="color:var(--subtle)">\u2014</span>'
    cls = _STATE_CLS.get(state, "b-inbox")
    label = state.replace("_", " ")
    return f'<span class="badge {cls}">{html.escape(label)}</span>'


def priority_badge(priority: str | None) -> str:
    if not priority:
        return ""
    cls = {"high": "b-high", "medium": "b-medium", "low": "b-low"}.get(priority, "b-inbox")
    return f'<span class="badge {cls}">{html.escape(priority)}</span>'


# ---------------------------------------------------------------------------
# Freshness
# ---------------------------------------------------------------------------

_FRESHNESS_COLORS = {
    "fresh": "var(--positive)",
    "aging": "var(--warning)",
    "stale": "var(--danger)",
    "never": "var(--subtle)",
}
_FRESHNESS_LABELS = {"fresh": "Fresh", "aging": "Aging", "stale": "Stale", "never": "Never"}


def freshness_dot(status: str, days_since: int | None = None) -> str:
    color = _FRESHNESS_COLORS.get(status, "var(--subtle)")
    label = _FRESHNESS_LABELS.get(status, "Unknown")
    age = f"{days_since}d ago" if days_since is not None else "No report"
    return (
        f'<div class="queue-freshness">'
        f'<span class="queue-freshness-dot" style="background:{color};"></span>'
        f'<span style="color:{color};">{html.escape(label)}</span>'
        f'<span class="queue-freshness-age">{html.escape(age)}</span>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Markdown content wrapper
# ---------------------------------------------------------------------------

def render_markdown_styled(md_text: str) -> None:
    """Render markdown wrapped in .md-content for styled dark-theme rendering."""
    import markdown as md_lib

    html_body = md_lib.markdown(md_text, extensions=["tables", "fenced_code"])
    st.markdown(f'<div class="md-content">{html_body}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Scoreboard cell helpers
# ---------------------------------------------------------------------------

def render_agent_color_dot(color: str, label: str) -> str:
    """Small inline colored circle + label for agent legend."""
    return (
        f'<span class="agent-legend-dot" style="background:{html.escape(color)};"></span>'
        f'<span style="font-weight:500;color:var(--text);">{html.escape(label)}</span>'
    )


def sb_score_style(v: float | int | None) -> str:
    """Inline CSS for score cells (<4 red, 4-7 yellow, >=7 green, bold)."""
    if v is None:
        return ""
    if v < 4:
        return "color:var(--danger);font-weight:700;"
    if v < 7:
        return "color:var(--warning);font-weight:700;"
    return "color:var(--positive);font-weight:700;"


def sb_mos_style(v: float | int | None) -> str:
    if v is None:
        return ""
    return "color:var(--positive);font-weight:700;" if v >= 0 else "color:var(--danger);font-weight:700;"


def sb_verdict_style(v: str | None) -> str:
    if v == "Own":
        return "color:var(--positive);font-weight:700;"
    if v == "Watch":
        return "color:var(--warning);font-weight:700;"
    if v == "Pass":
        return "color:var(--danger);font-weight:700;"
    return ""


def sb_confidence_html(v: str | None) -> str:
    raw = str(v or "\u2014")
    first = raw.split()[0].lower() if raw.strip() else ""
    color_map = {"high": "var(--positive)", "medium": "var(--warning)", "low": "var(--danger)"}
    color = color_map.get(first, "var(--subtle)")
    label = first.capitalize() if first in color_map else raw
    return (
        f'<span title="{html.escape(raw)}" style="color:{color};font-size:11px;'
        f'font-weight:500;text-transform:uppercase;">{html.escape(label)}</span>'
    )
