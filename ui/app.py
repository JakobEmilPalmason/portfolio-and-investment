import json
import re
from pathlib import Path
from flask import Flask, jsonify, send_file

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"
RUNS_DIR   = REPO_ROOT / "runs"

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


if __name__ == '__main__':
    print('\n  Investment Pipeline Dashboard')
    print('  http://localhost:5050\n')
    app.run(host='127.0.0.1', port=5050, debug=True)
