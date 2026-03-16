import json
import re
import time
from datetime import date, datetime
from pathlib import Path
from flask import Flask, jsonify, request, send_file

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import build_index, search as fts_search, get_index_stats

REPO_ROOT   = Path(__file__).resolve().parent.parent
QUEUE_FILE  = REPO_ROOT / "queue" / "queue.json"
RUNS_DIR    = REPO_ROOT / "runs"
LEDGER_FILE = REPO_ROOT / "portfolio" / "ledger.json"

app = Flask(__name__)
TICKER_RE = re.compile(r'^[A-Z0-9.\-]{1,20}$')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


@app.route('/')
def index():
    return send_file(Path(__file__).parent / 'index.html')


@app.route('/api/queue')
def api_queue():
    try:
        return jsonify(read_json(QUEUE_FILE))
    except Exception:
        return jsonify([])


@app.route('/api/reports')
def api_reports():
    if not RUNS_DIR.exists():
        return jsonify({'reports': [], 'count': 0})
    # Collect latest report per ticker across all week runs
    best: dict = {}
    for json_file in RUNS_DIR.glob("*/reports/*/FINAL-REPORT.json"):
        ticker = json_file.parent.name
        md_file = json_file.parent / 'FINAL-REPORT.md'
        try:
            data = read_json(json_file)
            data['has_json'] = True
            data['has_md'] = md_file.exists()
        except Exception:
            data = {'ticker': ticker, 'company': ticker, 'has_json': False, 'has_md': md_file.exists()}
        existing = best.get(ticker)
        if existing is None or (data.get('analysis_date', '') >= existing.get('analysis_date', '')):
            best[ticker] = data
    # Also pick up md-only reports not yet in best
    for md_file in RUNS_DIR.glob("*/reports/*/FINAL-REPORT.md"):
        ticker = md_file.parent.name
        if ticker not in best:
            best[ticker] = {'ticker': ticker, 'company': ticker, 'has_json': False, 'has_md': True}
    reports = sorted(best.values(), key=lambda r: r.get('analysis_date') or '', reverse=True)
    return jsonify({'reports': reports, 'count': len(reports)})


@app.route('/api/report/<string:ticker>')
def api_report(ticker):
    ticker = ticker.upper()
    if not TICKER_RE.match(ticker):
        return jsonify({'error': 'Invalid ticker'}), 400
    # Find the most recently modified report dir across all weeks
    report_dirs = [p.parent for p in RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json")]
    if not report_dirs:
        report_dirs = [p.parent for p in RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.md")]
    if not report_dirs:
        return jsonify({'error': 'Report not found'}), 404
    report_dir = max(report_dirs, key=lambda p: p.stat().st_mtime)
    result = {'json': None, 'markdown': None}
    json_file = report_dir / 'FINAL-REPORT.json'
    md_file   = report_dir / 'FINAL-REPORT.md'
    if json_file.exists():
        try:
            result['json'] = read_json(json_file)
        except Exception:
            pass
    if md_file.exists():
        try:
            result['markdown'] = md_file.read_text(encoding='utf-8')
        except Exception:
            pass
    if result['json'] is None and result['markdown'] is None:
        return jsonify({'error': 'No report data'}), 404
    return jsonify(result)


@app.route('/api/pipeline')
def api_pipeline():
    result = {'scan': None, 'triage': None}

    if not RUNS_DIR.exists():
        return jsonify(result)

    week_dirs = sorted(
        [d for d in RUNS_DIR.iterdir() if d.is_dir() and re.match(r'^week\d+_', d.name)],
        key=lambda d: d.name, reverse=True
    )

    for d in week_dirs:
        f = d / 'scan' / 'scan-meta.json'
        if f.exists():
            try:
                result['scan'] = read_json(f)
                break
            except Exception:
                pass

    for d in week_dirs:
        f = d / 'triage' / 'triage.json'
        if f.exists():
            try:
                triage_data = read_json(f)
                b2 = {}
                shortlist = []
                for e in triage_data:
                    a = e.get('next_action', 'unknown')
                    b2[a] = b2.get(a, 0) + 1
                    if a in ('deep_dive', 'refresh'):
                        shortlist.append({
                            'ticker':      e.get('ticker'),
                            'company':     e.get('company'),
                            'next_action': a,
                            'reason':      e.get('reason_for_action', ''),
                        })
                tr = {'triage_date': d.name, 'b2': b2,
                      'deep_dive_shortlist': shortlist}
                b1f = d / 'triage' / 'b1-results.json'
                if b1f.exists():
                    b1_data = read_json(b1f)
                    b1 = {}
                    for e in b1_data:
                        v = e.get('b1_verdict', 'unknown')
                        b1[v] = b1.get(v, 0) + 1
                    tr['b1'] = b1
                result['triage'] = tr
                break
            except Exception:
                pass

    return jsonify(result)


@app.route('/api/portfolio')
def api_portfolio():
    if not LEDGER_FILE.exists():
        return jsonify({'error': 'No ledger found'}), 404
    try:
        ledger = read_json(LEDGER_FILE)
    except Exception:
        return jsonify({'error': 'Failed to read ledger'}), 500

    meta = ledger.get('metadata', {})
    summary_raw = ledger.get('summary', {})
    positions_raw = ledger.get('positions', [])

    capital = summary_raw.get('initial_capital') or meta.get('initial_capital') or 0
    cash = summary_raw.get('cash_position', 0)
    deployed_long = summary_raw.get('deployed_long', 0)
    deployed_short = summary_raw.get('deployed_short', 0)
    gross_exp = summary_raw.get('gross_exposure', 0)
    net_exp = summary_raw.get('net_exposure', 0)
    gross_pct = summary_raw.get('gross_exposure_pct', 0)
    net_pct = summary_raw.get('net_exposure_pct', 0)
    realized = summary_raw.get('realized_pnl', 0)

    positions = []
    total_unrealized = 0
    for p in positions_raw:
        unrealized = p.get('unrealized_pnl') or 0
        total_unrealized += unrealized
        entry_price = p.get('entry_price') or p.get('cost_basis_per_share') or 0
        cost_basis = p.get('cost_basis_total', 0)
        current_price = p.get('current_price')
        shares = p.get('shares', 0)
        market_value = p.get('current_value') or (current_price * shares if current_price else cost_basis)
        weight = (cost_basis / capital * 100) if capital else 0
        positions.append({
            'ticker': p.get('ticker', ''),
            'company': p.get('company', ''),
            'side': p.get('side', 'long'),
            'shares': shares,
            'entry_date': p.get('entry_date', ''),
            'entry_price': entry_price,
            'current_price': current_price,
            'market_value': market_value,
            'cost_basis': cost_basis,
            'unrealized_pnl': unrealized,
            'unrealized_pct': p.get('unrealized_pnl_pct') or 0,
            'weight_pct': round(weight, 1),
            'target_weight_pct': p.get('target_weight_pct'),
            'score_at_entry': p.get('score_at_entry'),
            'sector': p.get('sector', ''),
            'thesis_tag': p.get('verdict_at_entry', ''),
            'policy_flags': p.get('policy_flags', []),
            'report_ref': p.get('report_ref', ''),
        })

    total_pnl = realized + total_unrealized

    sector_exposure = {}
    for sector, data in summary_raw.get('sector_weights', {}).items():
        long_val = (data.get('long_pct', 0) / 100) * capital
        short_val = (data.get('short_pct', 0) / 100) * capital
        sector_exposure[sector] = {
            'long': round(long_val, 2),
            'short': round(short_val, 2),
            'net': round(long_val - short_val, 2),
            'gross': round(long_val + short_val, 2),
            'pct_of_capital': data.get('gross_pct', 0),
        }

    warnings = []
    for p in positions_raw:
        for flag in p.get('policy_flags', []):
            warnings.append(f"{p.get('ticker','')}: {flag}")

    return jsonify({
        'summary': {
            'capital': capital,
            'cash': cash,
            'cash_pct': summary_raw.get('cash_pct', 0),
            'long_market_value': deployed_long,
            'short_market_value': deployed_short,
            'gross_exposure': gross_exp,
            'net_exposure': net_exp,
            'gross_pct': gross_pct,
            'net_pct': net_pct,
            'total_pnl': total_pnl,
            'realized_pnl': realized,
            'unrealized_pnl': total_unrealized,
            'position_count': summary_raw.get('position_count', len(positions_raw)),
            'long_count': summary_raw.get('long_count', 0),
            'short_count': summary_raw.get('short_count', 0),
            'largest_position_ticker': summary_raw.get('largest_position_ticker', ''),
            'largest_position_pct': summary_raw.get('largest_position_pct', 0),
            'last_updated': meta.get('last_updated', summary_raw.get('as_of', '')),
        },
        'positions': positions,
        'sector_exposure': sector_exposure,
        'warnings': warnings,
    })


@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    doc_type = request.args.get('type', '').strip() or None
    if not q:
        return jsonify([])
    return jsonify(fts_search(q, doc_type))


@app.route('/api/search/rebuild', methods=['POST'])
def api_search_rebuild():
    t0 = time.time()
    count = build_index(REPO_ROOT)
    duration = int((time.time() - t0) * 1000)
    return jsonify({'indexed': count, 'duration_ms': duration})


@app.route('/api/search/stats')
def api_search_stats():
    return jsonify(get_index_stats())


@app.route('/api/freshness')
def api_freshness():
    today = date.today()
    result = {}
    try:
        queue_data = read_json(QUEUE_FILE)
    except Exception:
        queue_data = []
    for entry in queue_data:
        ticker = entry.get('ticker', '')
        if not ticker:
            continue
        last_date = entry.get('last_analysis_date')
        days_since = None
        status = 'never'
        if last_date:
            try:
                d = datetime.strptime(last_date, '%Y-%m-%d').date()
                days_since = (today - d).days
                if days_since < 7:
                    status = 'fresh'
                elif days_since <= 30:
                    status = 'aging'
                else:
                    status = 'stale'
            except ValueError:
                pass
        # Check financials
        fin_path = REPO_ROOT / 'context' / ticker / 'financials.md'
        has_financials = fin_path.exists()
        financials_age_days = None
        if has_financials:
            mtime = fin_path.stat().st_mtime
            financials_age_days = (today - date.fromtimestamp(mtime)).days
        result[ticker] = {
            'last_analysis_date': last_date,
            'days_since': days_since,
            'has_financials': has_financials,
            'financials_age_days': financials_age_days,
            'status': status,
        }
    return jsonify(result)


@app.route('/api/policy')
def api_policy():
    policy_file = REPO_ROOT / 'INVESTMENT-POLICY.md'
    if not policy_file.exists():
        return jsonify({'error': 'Policy file not found'}), 404
    try:
        return jsonify({'markdown': policy_file.read_text(encoding='utf-8')})
    except Exception:
        return jsonify({'error': 'Failed to read policy file'}), 500


if __name__ == '__main__':
    print('\n  Investment Pipeline Dashboard')
    print('  http://localhost:5050\n')
    app.run(host='127.0.0.1', port=5050, debug=True)
