"""Flag History page — one row per Own-verdict analysis with live comparison."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.data import (  # noqa: E402
    get_benchmark_returns_since,
    get_live_prices,
    get_next_earnings,
    load_all_reports,
)
from dashboard.theme import render_hero, render_kicker  # noqa: E402


def _row_pcts(
    record: dict,
    live_prices: dict[str, float],
    spy_returns: dict[str, float],
) -> tuple[float | None, float | None]:
    """(stock Δ %, SPY Δ % over same window) for one record — either may be None."""
    flag = record.get("price_at_analysis")
    live = live_prices.get(record.get("ticker") or "")
    stock_pct: float | None = None
    if flag is not None and live is not None:
        try:
            flag_f = float(flag)
            live_f = float(live)
            if flag_f > 0:
                stock_pct = (live_f / flag_f - 1) * 100
        except (TypeError, ValueError):
            stock_pct = None
    spy_pct = spy_returns.get(record.get("analysis_date") or "")
    return stock_pct, spy_pct


def _equal_weight_stats(
    records: list[dict],
    live_prices: dict[str, float],
    spy_returns: dict[str, float],
    min_score: float | None = None,
) -> dict[str, float | int | None]:
    """Compute equal-weight raw Δ, SPY-relative alpha, and hit rate for a slice.

    A row contributes to the raw Δ if it has a stock Δ; it contributes to
    alpha/hit-rate only if it also has a matching SPY return for the flag date.
    """
    stock_pcts: list[float] = []
    alphas: list[float] = []
    wins = 0
    for record in records:
        score = record.get("average_score")
        if min_score is not None and (score is None or float(score) < min_score):
            continue
        stock_pct, spy_pct = _row_pcts(record, live_prices, spy_returns)
        if stock_pct is None:
            continue
        stock_pcts.append(stock_pct)
        if spy_pct is not None:
            alpha = stock_pct - spy_pct
            alphas.append(alpha)
            if alpha > 0:
                wins += 1
    return {
        "raw_avg": (sum(stock_pcts) / len(stock_pcts)) if stock_pcts else None,
        "raw_n": len(stock_pcts),
        "alpha_avg": (sum(alphas) / len(alphas)) if alphas else None,
        "alpha_n": len(alphas),
        "hit_rate": (wins / len(alphas) * 100) if alphas else None,
        "hit_wins": wins,
    }


def _best_per_ticker(records: list[dict]) -> list[dict]:
    """Deduplicate records by ticker, keeping the highest average_score per ticker."""
    best: dict[str, dict] = {}
    for r in records:
        ticker = r.get("ticker") or ""
        score = r.get("average_score")
        score_f = float(score) if score is not None else -1.0
        prev = best.get(ticker)
        if prev is None:
            best[ticker] = r
        else:
            prev_score = float(prev.get("average_score") or -1)
            if score_f > prev_score:
                best[ticker] = r
    return list(best.values())


def _alpha_metric(
    label: str,
    stats: dict[str, float | int | None],
    meta_suffix: str,
) -> dict[str, str]:
    """Card that leads with α vs SPY and shows the raw Δ in the meta line."""
    alpha = stats.get("alpha_avg")
    raw = stats.get("raw_avg")
    alpha_n = stats.get("alpha_n") or 0
    raw_n = stats.get("raw_n") or 0
    if alpha is None:
        if raw is None:
            return {"label": label, "value": "—",
                    "meta": f"no rows {meta_suffix}", "tone": "tone-info"}
        return {
            "label": label,
            "value": "—",
            "meta": (
                f"raw Δ {raw:+.2f}% · SPY baseline unavailable · "
                f"{raw_n} rows {meta_suffix}"
            ),
            "tone": "tone-info",
        }
    tone = "tone-positive" if alpha >= 0 else "tone-danger"
    raw_part = f"raw Δ {raw:+.2f}% · " if raw is not None else ""
    return {
        "label": label,
        "value": f"{alpha:+.2f}%",
        "meta": f"{raw_part}{alpha_n} rows {meta_suffix}",
        "tone": tone,
    }


def _hit_rate_metric(
    label: str,
    stats: dict[str, float | int | None],
    meta_suffix: str,
) -> dict[str, str]:
    hit_rate = stats.get("hit_rate")
    wins = stats.get("hit_wins") or 0
    alpha_n = stats.get("alpha_n") or 0
    if hit_rate is None or alpha_n == 0:
        return {"label": label, "value": "—",
                "meta": f"no SPY baseline {meta_suffix}", "tone": "tone-info"}
    tone = "tone-positive" if hit_rate >= 50 else "tone-danger"
    return {
        "label": label,
        "value": f"{hit_rate:.0f}%",
        "meta": f"{wins}/{alpha_n} beat SPY {meta_suffix}",
        "tone": tone,
    }


def _build_flag_frame(
    records: list[dict],
    live_prices: dict[str, float],
    earnings_dates: dict[str, str | None],
    spy_returns: dict[str, float],
) -> pd.DataFrame:
    """Flatten Own-verdict records into a DataFrame optimized for st.dataframe.

    Each column is typed so that Streamlit's per-column sort and filter menus
    behave correctly. Prices and IVs stay as raw floats — Streamlit formats
    them via `column_config` so click-to-sort is still numeric.
    """
    rows = []
    for r in records:
        ticker = r.get("ticker") or ""
        flag = r.get("price_at_analysis")
        live = live_prices.get(ticker)
        pct_change: float | None = None
        if flag is not None and live is not None:
            try:
                flag_f = float(flag)
                live_f = float(live)
                if flag_f > 0:
                    pct_change = (live_f / flag_f - 1) * 100
            except (TypeError, ValueError):
                pct_change = None

        spy_pct = spy_returns.get(r.get("analysis_date") or "")
        vs_spy: float | None = None
        if pct_change is not None and spy_pct is not None:
            vs_spy = pct_change - spy_pct

        rows.append(
            {
                "Ticker": ticker,
                "Company": r.get("company") or "",
                "Analyzed": r.get("analysis_date") or "",
                "Score": (
                    float(r["average_score"])
                    if r.get("average_score") is not None
                    else None
                ),
                "Confidence": r.get("confidence") or "",
                "Currency": r.get("iv_currency") or "",
                "Flag": (
                    float(flag) if isinstance(flag, (int, float)) else None
                ),
                "Live": (
                    float(live) if isinstance(live, (int, float)) else None
                ),
                "Δ %": pct_change,
                "vs SPY": vs_spy,
                "MOS %": (
                    float(r["mos_at_analysis"])
                    if r.get("mos_at_analysis") is not None
                    else None
                ),
                "IV cons": (
                    float(r["iv_conservative"])
                    if r.get("iv_conservative") is not None
                    else None
                ),
                "IV base": (
                    float(r["iv_base"])
                    if r.get("iv_base") is not None
                    else None
                ),
                "IV bull": (
                    float(r["iv_bull"])
                    if r.get("iv_bull") is not None
                    else None
                ),
                "Next earnings": earnings_dates.get(ticker) or "",
                "Comments": r.get("comments") or "",
                "Week": r.get("week") or "",
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # Date-typed so the column sort works chronologically, not lexicographically
    df["Analyzed"] = pd.to_datetime(df["Analyzed"], errors="coerce").dt.date
    df["Next earnings"] = pd.to_datetime(
        df["Next earnings"], errors="coerce"
    ).dt.date
    return df


_FLAG_COL_KEYS = {
    "Ticker": "ticker",
    "Company": "company",
    "Analyzed": "analyzed",
    "Score": "score",
    "Confidence": "confidence",
    "Currency": "currency",
    "Flag": "flag",
    "Live": "live",
    "Δ %": "pct_change",
    "vs SPY": "vs_spy",
    "MOS %": "mos_pct",
    "IV cons": "iv_cons",
    "IV base": "iv_base",
    "IV bull": "iv_bull",
    "Next earnings": "next_earnings",
    "Comments": "comments",
    "Week": "week",
}


def _flag_jsonify(value):
    """Serialize a DataFrame cell to a JSON-safe primitive."""
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _render_flag_table(df: pd.DataFrame) -> None:
    """Scoreboard-style HTML/JS table — sortable, color-coded, sticky header."""
    import json as _json

    import streamlit.components.v1 as components

    renamed = df.rename(columns=_FLAG_COL_KEYS)
    records = [
        {key: _flag_jsonify(row.get(key)) for key in _FLAG_COL_KEYS.values()}
        for _, row in renamed.iterrows()
    ]
    data_json = _json.dumps(records, default=str)

    row_count = len(df)
    table_height = min(60 + row_count * 50 + 40, 860)
    height = table_height + 50  # toolbar above the table

    flag_html = f"""
<!DOCTYPE html>
<html><head>
<style>
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono:wght@500;700&display=swap');
:root {{
  color-scheme: dark;
  --font-display: 'General Sans', 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --bg: #0c0a09; --surface: #1c1917; --surface-strong: #292524;
  --border: rgba(68, 64, 60, 0.82); --border-strong: rgba(120, 113, 108, 0.9);
  --text: #fafaf9; --muted: #a8a29e; --subtle: #78716c;
  --accent: #c15f3c; --positive: #86efac; --warning: #fbbf24; --danger: #fca5a5;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; font-family:var(--font-body); font-weight:400; color:var(--text); overflow:hidden; }}
.mono {{ font-family:var(--font-mono); }}
.toolbar {{ display:flex; justify-content:space-between; align-items:center; padding:2px 4px 10px; gap:12px; }}
.rowcount {{ color:var(--muted); font-family:var(--font-mono); font-size:12px; letter-spacing:0.04em; }}
.copybtn {{
  background:var(--surface-strong); color:var(--text); border:1px solid var(--border-strong);
  border-radius:8px; padding:7px 14px; font-family:var(--font-display); font-size:11px; font-weight:500;
  letter-spacing:0.08em; text-transform:uppercase; cursor:pointer;
  transition:background 120ms ease, color 120ms ease, border-color 120ms ease;
}}
.copybtn:hover {{ background:var(--accent); color:var(--bg); border-color:var(--accent); }}
.copybtn.copied {{ background:var(--positive); color:var(--bg); border-color:var(--positive); }}
.copybtn.failed {{ background:var(--danger); color:var(--bg); border-color:var(--danger); }}
.wrap {{ overflow:auto; max-height:{table_height - 20}px; border-radius:12px; border:1px solid var(--border); }}
table {{ width:100%; min-width:1600px; border-collapse:separate; border-spacing:0; }}
thead {{ position:sticky; top:0; z-index:2; }}
th {{
  font-family:var(--font-display);
  padding:14px 14px; background:rgba(12,10,9,0.96); border-bottom:1px solid rgba(68,64,60,0.9);
  font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase;
  text-align:center; color:var(--subtle); white-space:nowrap; cursor:pointer; user-select:none;
  position:relative;
}}
th:nth-child(1), th:nth-child(2), th:nth-child(16) {{ text-align:left; }}
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
td:nth-child(16) {{ text-align:left; }}
tbody tr:last-child td {{ border-bottom:none; }}
tbody tr:hover td {{ background:rgba(41,37,36,0.42); }}
.sym {{ font-family:var(--font-mono); font-size:13px; font-weight:700; color:var(--accent); }}
.co {{ max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--muted); }}
.comment {{ max-width:320px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--muted); font-size:13px; }}
.empty {{ padding:42px 16px; text-align:center; color:var(--muted); font-size:13px; }}
::-webkit-scrollbar {{ width:8px; height:8px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:rgba(148,163,184,0.18); border-radius:999px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(148,163,184,0.28); }}
</style>
</head><body>
<div class="toolbar">
  <span class="rowcount" id="rowcount"></span>
  <button class="copybtn" id="copybtn" title="Copy table as TSV — paste directly into Excel or Sheets">⧉ Copy table</button>
</div>
<div class="wrap"><table><thead><tr id="hdr"></tr></thead><tbody id="tbody"></tbody></table></div>
<script>
const DATA = {data_json};
const COLS = [
  'ticker','company','analyzed','score','confidence','currency',
  'flag','live','pct_change','vs_spy','mos_pct',
  'iv_cons','iv_base','iv_bull',
  'next_earnings','comments','week'
];
const HEADERS = {{
  ticker:'Ticker', company:'Company', analyzed:'Analyzed', score:'Score',
  confidence:'Confidence', currency:'Ccy',
  flag:'Flag', live:'Live', pct_change:'Δ %', vs_spy:'vs SPY', mos_pct:'MOS %',
  iv_cons:'IV Bear', iv_base:'IV Base', iv_bull:'IV Bull',
  next_earnings:'Next ER', comments:'Comments', week:'Week'
}};
const TIPS = {{
  ticker:'Stock ticker symbol',
  company:'Company name',
  analyzed:'Analysis completion date',
  score:'Average of the 8 umbrella scores (0-10)',
  confidence:'Agent-assigned confidence in the analysis (high / medium-high / medium / medium-low / low)',
  currency:'Reporting currency of IVs and prices',
  flag:'Price at analysis (native currency)',
  live:'Latest close from yfinance (native currency)',
  pct_change:'% change from flag price to live price (same currency — no FX normalization)',
  vs_spy:'Alpha vs SPY over the same window: stock Δ % − SPY Δ %. Positive = beat SPY, negative = lagged SPY. Computed in USD terms for SPY.',
  mos_pct:'Margin of safety at analysis (positive = price below IV)',
  iv_cons:'Bear-case intrinsic value per share',
  iv_base:'Base-case intrinsic value per share',
  iv_bull:'Bull-case intrinsic value per share',
  next_earnings:'Next earnings date (best-effort yfinance)',
  comments:'Change notes or first sentence of the valuation summary',
  week:'Run week folder (runs/<week>/…)'
}};
const PRICE_COLS = new Set(['flag','live','iv_cons','iv_base','iv_bull']);
const PCT_COLS = new Set(['pct_change','vs_spy']);

function esc(s) {{ return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }}
function scoreStyle(v) {{ if(v==null)return''; return v<4?'color:var(--danger);font-weight:700;':v<7?'color:var(--warning);font-weight:700;':'color:var(--positive);font-weight:700;'; }}
function confStyle(v) {{
  if(!v) return 'color:var(--muted);';
  const s=String(v).toLowerCase();
  if(s==='high'||s==='medium-high') return 'color:var(--positive);font-weight:600;';
  if(s==='low'||s==='medium-low') return 'color:var(--danger);font-weight:600;';
  return 'color:var(--warning);font-weight:600;';
}}
function fmtConf(v) {{ return v?String(v).charAt(0).toUpperCase()+String(v).slice(1):'—'; }}
function deltaStyle(v) {{ if(v==null)return''; return v>=0?'color:var(--positive);font-weight:700;':'color:var(--danger);font-weight:700;'; }}
function fmtNum(v, d) {{ return Number(v).toLocaleString(undefined,{{minimumFractionDigits:d,maximumFractionDigits:d}}); }}
function fmtDate(v) {{ return v?String(v).slice(0,10).replace(/-/g,'/'):'—'; }}

let sortKey='analyzed', sortDir='desc';

function cell(key,val) {{
  const mono='font-family:var(--font-mono);';
  if(key==='ticker') return `<td class="sym">${{esc(val||'—')}}</td>`;
  if(key==='company') return `<td class="co" title="${{esc(val||'')}}">${{esc(val||'—')}}</td>`;
  if(key==='analyzed') return `<td style="${{mono}}color:var(--muted);font-size:12px;">${{fmtDate(val)}}</td>`;
  if(key==='score') {{
    let d=val!=null?Number(val).toFixed(1):'—';
    return `<td style="${{mono}}${{scoreStyle(val)}}">${{d}}</td>`;
  }}
  if(key==='confidence') {{
    return `<td style="${{confStyle(val)}}font-size:12px;letter-spacing:0.02em;">${{esc(fmtConf(val))}}</td>`;
  }}
  if(key==='currency') return `<td style="color:var(--muted);font-size:12px;letter-spacing:0.05em;">${{esc(val||'—')}}</td>`;
  if(PRICE_COLS.has(key)) {{
    let d=val!=null?fmtNum(val,2):'—';
    return `<td style="${{mono}}color:var(--text);">${{d}}</td>`;
  }}
  if(PCT_COLS.has(key)) {{
    let d=val!=null?(val>=0?'+':'')+fmtNum(val,2)+'%':'—';
    return `<td style="${{mono}}${{deltaStyle(val)}}">${{d}}</td>`;
  }}
  if(key==='mos_pct') {{
    let d=val!=null?(val>=0?'+':'')+fmtNum(val,1)+'%':'—';
    return `<td style="${{mono}}${{deltaStyle(val)}}">${{d}}</td>`;
  }}
  if(key==='next_earnings') return `<td style="${{mono}}color:var(--muted);font-size:12px;">${{fmtDate(val)}}</td>`;
  if(key==='comments') return `<td class="comment" title="${{esc(val||'')}}">${{esc(val||'—')}}</td>`;
  if(key==='week') return `<td style="${{mono}}color:var(--subtle);font-size:11px;">${{esc(val||'—')}}</td>`;
  return `<td>${{esc(val!=null?val:'—')}}</td>`;
}}

function render() {{
  const hdr=document.getElementById('hdr');
  const tbody=document.getElementById('tbody');
  const arrow=k=>sortKey===k?(sortDir==='desc'?' ↓':' ↑'):'';
  hdr.innerHTML=COLS.map(k=>`<th>${{esc(HEADERS[k])}}${{arrow(k)}}<span class="tip">${{esc(TIPS[k]||'')}}</span></th>`).join('');
  hdr.querySelectorAll('th').forEach((th,i)=>th.addEventListener('click',()=>sortBy(COLS[i])));

  if(!DATA.length) {{ tbody.innerHTML=`<tr><td colspan="${{COLS.length}}" class="empty">No rows match the current filters.</td></tr>`; return; }}
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

function tsvCell(v) {{
  if (v == null) return '';
  if (typeof v === 'number') return Number.isFinite(v) ? String(v) : '';
  return String(v).replace(/[\\t\\r\\n]+/g, ' ');
}}

function buildTSV() {{
  const headerLine = COLS.map(k => HEADERS[k]).join('\\t');
  const dataLines = DATA.map(r => COLS.map(k => tsvCell(r[k])).join('\\t'));
  return [headerLine, ...dataLines].join('\\n');
}}

function flashCopied(ok) {{
  const btn = document.getElementById('copybtn');
  if (!btn) return;
  const original = btn.textContent;
  btn.textContent = ok ? '✓ Copied' : '✗ Copy failed';
  btn.classList.add(ok ? 'copied' : 'failed');
  setTimeout(() => {{
    btn.textContent = original;
    btn.classList.remove('copied');
    btn.classList.remove('failed');
  }}, 1500);
}}

function copyTable() {{
  const tsv = buildTSV();
  // execCommand fallback first — works inside Streamlit's sandboxed iframe.
  try {{
    const ta = document.createElement('textarea');
    ta.value = tsv;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    if (ok) {{ flashCopied(true); return; }}
  }} catch (e) {{ /* fall through */ }}
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(tsv).then(
      () => flashCopied(true),
      () => flashCopied(false),
    );
  }} else {{
    flashCopied(false);
  }}
}}

document.getElementById('rowcount').textContent = `${{DATA.length}} ${{DATA.length === 1 ? 'row' : 'rows'}}`;
document.getElementById('copybtn').addEventListener('click', copyTable);

sortBy('analyzed');
</script>
</body></html>
"""
    components.html(flag_html, height=height, scrolling=False)


def main() -> None:
    render_kicker("Flag History")

    records = load_all_reports()
    own_records = [r for r in records if r.get("verdict") == "Own"]

    if not own_records:
        st.info(
            "No Own-verdict reports found. Run `./run.sh analyze TICKER` on a "
            "high-conviction name to populate this page."
        )
        return

    ticker_counts = Counter(r["ticker"] for r in own_records)
    unique_tickers = sorted(ticker_counts.keys())
    multi_tickers = {t for t, c in ticker_counts.items() if c > 1}

    tickers_tuple = tuple(unique_tickers)
    live_prices = get_live_prices(tickers_tuple)
    earnings_dates = get_next_earnings(tickers_tuple)
    spy_returns = get_benchmark_returns_since(
        tuple(r.get("analysis_date") or "" for r in own_records)
    )

    all_stats = _equal_weight_stats(own_records, live_prices, spy_returns)
    strong_stats = _equal_weight_stats(
        own_records, live_prices, spy_returns, min_score=8.0,
    )
    best_stats = _equal_weight_stats(
        _best_per_ticker(own_records), live_prices, spy_returns,
    )

    render_hero(
        "Own-verdict flag history",
        f"Every Claude analysis where the verdict landed on Own — "
        f"{len(own_records)} rows across {len(unique_tickers)} tickers "
        f"({len(multi_tickers)} re-analyzed). Headline values are α vs SPY "
        f"(stock Δ − SPY Δ over the same window); raw Δ sits in each tile's "
        f"meta line. Equal-weight baskets assume the same $ into each row at "
        f"its flag price; FX is not normalized on the stock side.",
        [
            _alpha_metric("α vs SPY", all_stats, "· all Own"),
            _alpha_metric(
                "Score ≥ 8 α", strong_stats, "· high-conviction",
            ),
            _alpha_metric(
                "Best per ticker α", best_stats, "· top score each",
            ),
            _hit_rate_metric("Hit rate vs SPY", all_stats, "· all Own"),
        ],
    )

    st.markdown("")

    df = _build_flag_frame(
        own_records, live_prices, earnings_dates, spy_returns,
    )

    # Filter controls above the table. Click column headers for sort; use the
    # header "..." menu for per-column filters (Streamlit ≥1.37).
    controls = st.columns([3, 3, 3, 1])
    with controls[0]:
        search = st.text_input(
            "Search ticker or company",
            "",
            placeholder="e.g. NOVO, Visa, …",
            key="flag_search",
        )
    with controls[1]:
        available_currencies = sorted(
            {c for c in df["Currency"].dropna().unique() if c}
        )
        selected_currencies = st.multiselect(
            "Currency",
            available_currencies,
            default=[],
            placeholder="All currencies",
            key="flag_currency_filter",
        )
    with controls[2]:
        min_score = st.slider(
            "Min score",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
            key="flag_min_score",
        )
    with controls[3]:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("↻ Refresh", use_container_width=True, type="secondary"):
            get_live_prices.clear()
            get_next_earnings.clear()
            st.rerun()

    filtered = df
    if search:
        needle = search.strip().lower()
        filtered = filtered[
            filtered["Ticker"].str.lower().str.contains(needle, na=False)
            | filtered["Company"].str.lower().str.contains(needle, na=False)
        ]
    if selected_currencies:
        filtered = filtered[filtered["Currency"].isin(selected_currencies)]
    if min_score > 0:
        filtered = filtered[filtered["Score"].fillna(0) >= min_score]

    if filtered.empty:
        st.info("No rows match the current filters.")
        return

    _render_flag_table(filtered)

    missing_live = sorted(
        {r["ticker"] for r in own_records if r["ticker"] not in live_prices}
    )
    if missing_live:
        st.caption(
            f"Live price unavailable from yfinance for: "
            f"{', '.join(missing_live)}. Hit ↻ Refresh to retry."
        )

    st.caption(
        "Click any column header to sort. Flag price is the yfinance close on "
        "`analysis_date`, falling back to IV × (1 − MOS). Δ % is in the "
        "report's native currency — no FX normalization. vs SPY is "
        "`stock Δ − SPY Δ` over the same window (SPY is USD), so the alpha "
        "carries FX noise for non-USD names and should be read as "
        "directional, not precise. Rows without a resolvable SPY close on "
        "the flag date are excluded from the alpha column and the headline "
        "α / hit-rate tiles."
    )


if __name__ == "__main__":
    main()
