"""Full-text search index over repo research content using SQLite FTS5."""

import json
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / 'search.db'

_conn = None


def get_db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute('PRAGMA journal_mode=WAL')
        _init_schema(_conn)
    return _conn


def _init_schema(conn: sqlite3.Connection):
    conn.execute('''CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(
        ticker,
        title,
        content,
        file_path,
        doc_type,
        analysis_date,
        tokenize='porter unicode61'
    )''')
    conn.commit()


def build_index(repo_root: Path) -> int:
    db = get_db()
    db.execute('DELETE FROM documents')
    count = 0

    # 1. Final reports
    for md_file in sorted(repo_root.glob('runs/*/reports/*/FINAL-REPORT.md')):
        ticker = md_file.parent.name
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        # Try to get analysis_date from companion JSON
        analysis_date = ''
        json_file = md_file.parent / 'FINAL-REPORT.json'
        if json_file.exists():
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
                analysis_date = data.get('analysis_date', '')
            except Exception:
                pass
        db.execute(
            'INSERT INTO documents(ticker, title, content, file_path, doc_type, analysis_date) VALUES (?,?,?,?,?,?)',
            (ticker, f'{ticker} — Final Report', content, str(md_file.relative_to(repo_root)), 'report', analysis_date)
        )
        count += 1

    # 2. Individual umbrella reports (0*.md)
    for md_file in sorted(repo_root.glob('runs/*/reports/*/0*.md')):
        ticker = md_file.parent.name
        title = md_file.stem.replace('-', ' ').title()
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        db.execute(
            'INSERT INTO documents(ticker, title, content, file_path, doc_type, analysis_date) VALUES (?,?,?,?,?,?)',
            (ticker, title, content, str(md_file.relative_to(repo_root)), 'report', '')
        )
        count += 1

    # 3. Financials
    for md_file in sorted(repo_root.glob('context/*/financials.md')):
        ticker = md_file.parent.name
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        db.execute(
            'INSERT INTO documents(ticker, title, content, file_path, doc_type, analysis_date) VALUES (?,?,?,?,?,?)',
            (ticker, f'{ticker} — Financials', content, str(md_file.relative_to(repo_root)), 'financials', '')
        )
        count += 1

    # 4. Queue entries
    queue_file = repo_root / 'queue' / 'queue.json'
    if queue_file.exists():
        try:
            queue_data = json.loads(queue_file.read_text(encoding='utf-8'))
            for entry in queue_data:
                ticker = entry.get('ticker', '')
                tags = ' '.join(entry.get('tags', []))
                content = f"{ticker} {entry.get('company', '')} {entry.get('owner_notes', '')} {tags}"
                db.execute(
                    'INSERT INTO documents(ticker, title, content, file_path, doc_type, analysis_date) VALUES (?,?,?,?,?,?)',
                    (ticker, f'{ticker} — Queue', content.strip(), 'queue/queue.json', 'queue', entry.get('last_analysis_date', ''))
                )
                count += 1
        except Exception:
            pass

    # 5. Triage markdown
    for md_file in sorted(repo_root.glob('runs/*/triage/triage.md')):
        week = md_file.parent.parent.name
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        db.execute(
            'INSERT INTO documents(ticker, title, content, file_path, doc_type, analysis_date) VALUES (?,?,?,?,?,?)',
            ('', f'Triage {week}', content, str(md_file.relative_to(repo_root)), 'triage', '')
        )
        count += 1

    db.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('last_built', ?)", (str(time.time()),))
    db.commit()
    return count


def incremental_update(repo_root: Path, since: float) -> int:
    db = get_db()
    count = 0

    patterns = [
        ('runs/*/reports/*/FINAL-REPORT.md', 'report'),
        ('runs/*/reports/*/0*.md', 'report'),
        ('context/*/financials.md', 'financials'),
        ('runs/*/triage/triage.md', 'triage'),
    ]

    for pattern, doc_type in patterns:
        for f in repo_root.glob(pattern):
            if f.stat().st_mtime <= since:
                continue
            ticker = f.parent.name if doc_type != 'triage' else ''
            try:
                content = f.read_text(encoding='utf-8')
            except Exception:
                continue
            rel_path = str(f.relative_to(repo_root))
            title = f'{ticker} — Final Report' if 'FINAL-REPORT' in f.name else (
                f'{ticker} — Financials' if doc_type == 'financials' else (
                    f'Triage {f.parent.parent.name}' if doc_type == 'triage' else
                    f.stem.replace('-', ' ').title()
                )
            )
            # Delete old entry for this path
            db.execute('DELETE FROM documents WHERE file_path = ?', (rel_path,))
            db.execute(
                'INSERT INTO documents(ticker, title, content, file_path, doc_type, analysis_date) VALUES (?,?,?,?,?,?)',
                (ticker, title, content, rel_path, doc_type, '')
            )
            count += 1

    if count:
        db.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('last_built', ?)", (str(time.time()),))
        db.commit()
    return count


def search(query: str, doc_type: str = None, limit: int = 20) -> list:
    if not query or not query.strip():
        return []
    db = get_db()
    where_type = "AND doc_type = ?" if doc_type else ""
    params = []

    sql = f'''
        SELECT ticker, title, file_path, doc_type, analysis_date,
               highlight(documents, 2, '<mark>', '</mark>') as snippet
        FROM documents
        WHERE documents MATCH ?
        {where_type}
        ORDER BY rank
        LIMIT ?
    '''
    params.append(query)
    if doc_type:
        params.append(doc_type)
    params.append(limit)

    try:
        rows = db.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        # FTS5 syntax error — strip special chars and retry
        clean = ''.join(c for c in query if c.isalnum() or c.isspace())
        if not clean.strip():
            return []
        params[0] = clean
        try:
            rows = db.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            return []

    results = []
    for row in rows:
        snippet = row['snippet'] or ''
        # Truncate snippet to ~200 chars around first <mark>
        mark_pos = snippet.find('<mark>')
        if mark_pos > 120:
            snippet = '…' + snippet[mark_pos - 80:]
        if len(snippet) > 300:
            snippet = snippet[:300] + '…'
        results.append({
            'ticker': row['ticker'],
            'title': row['title'],
            'file_path': row['file_path'],
            'doc_type': row['doc_type'],
            'analysis_date': row['analysis_date'],
            'snippet': snippet,
        })
    return results


def get_index_stats() -> dict:
    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM documents').fetchone()[0]
    row = db.execute("SELECT value FROM meta WHERE key='last_built'").fetchone()
    last_built = float(row[0]) if row else None
    db_size = DB_PATH.stat().st_size // 1024 if DB_PATH.exists() else 0
    return {
        'total_docs': total,
        'last_built': last_built,
        'db_size_kb': db_size,
    }


# Auto-build on first import if DB doesn't exist
def _auto_init():
    if not DB_PATH.exists():
        repo_root = Path(__file__).resolve().parent.parent
        build_index(repo_root)


_auto_init()
