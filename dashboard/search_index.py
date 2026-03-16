from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Any


def search_db_path(repo_root: str | Path) -> Path:
    root = Path(repo_root).resolve()
    digest = hashlib.sha1(str(root).encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"portfolio-streamlit-search-{digest}.db"


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS meta (
               key TEXT PRIMARY KEY,
               value TEXT
           )"""
    )
    conn.execute(
        """CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(
               ticker,
               title,
               content,
               file_path,
               doc_type,
               analysis_date,
               tokenize='porter unicode61'
           )"""
    )
    return conn


def build_index(repo_root: str | Path) -> int:
    root = Path(repo_root).resolve()
    db_path = search_db_path(root)
    count = 0

    with _connect(db_path) as conn:
        conn.execute("DELETE FROM documents")

        for md_file in sorted(root.glob("runs/*/reports/*/FINAL-REPORT.md")):
            ticker = md_file.parent.name
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            analysis_date = ""
            json_file = md_file.parent / "FINAL-REPORT.json"
            if json_file.exists():
                try:
                    analysis_date = json.loads(json_file.read_text(encoding="utf-8")).get("analysis_date", "")
                except (OSError, json.JSONDecodeError):
                    analysis_date = ""
            conn.execute(
                """INSERT INTO documents
                   (ticker, title, content, file_path, doc_type, analysis_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    ticker,
                    f"{ticker} - Final Report",
                    content,
                    str(md_file.relative_to(root)),
                    "report",
                    analysis_date,
                ),
            )
            count += 1

        for md_file in sorted(root.glob("runs/*/reports/*/0*.md")):
            ticker = md_file.parent.name
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            conn.execute(
                """INSERT INTO documents
                   (ticker, title, content, file_path, doc_type, analysis_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    ticker,
                    md_file.stem.replace("-", " ").title(),
                    content,
                    str(md_file.relative_to(root)),
                    "report",
                    "",
                ),
            )
            count += 1

        for md_file in sorted(root.glob("context/*/financials.md")):
            ticker = md_file.parent.name
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            conn.execute(
                """INSERT INTO documents
                   (ticker, title, content, file_path, doc_type, analysis_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    ticker,
                    f"{ticker} - Financials",
                    content,
                    str(md_file.relative_to(root)),
                    "financials",
                    "",
                ),
            )
            count += 1

        queue_file = root / "queue" / "queue.json"
        if queue_file.exists():
            try:
                queue_entries = json.loads(queue_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                queue_entries = []
            for entry in queue_entries:
                if not isinstance(entry, dict):
                    continue
                ticker = entry.get("ticker", "")
                tags = " ".join(entry.get("tags", []))
                content = " ".join(
                    str(value)
                    for value in [
                        ticker,
                        entry.get("company", ""),
                        entry.get("owner_notes", ""),
                        tags,
                        entry.get("current_state", ""),
                        entry.get("current_verdict", ""),
                    ]
                    if value
                )
                conn.execute(
                    """INSERT INTO documents
                       (ticker, title, content, file_path, doc_type, analysis_date)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        ticker,
                        f"{ticker} - Queue",
                        content,
                        "queue/queue.json",
                        "queue",
                        entry.get("last_analysis_date", ""),
                    ),
                )
                count += 1

        for md_file in sorted(root.glob("runs/*/triage/triage.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            conn.execute(
                """INSERT INTO documents
                   (ticker, title, content, file_path, doc_type, analysis_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    "",
                    f"Triage {md_file.parent.parent.name}",
                    content,
                    str(md_file.relative_to(root)),
                    "triage",
                    "",
                ),
            )
            count += 1

        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('last_built', ?)",
            (str(time.time()),),
        )
        conn.commit()

    return count


def search_documents(
    repo_root: str | Path,
    query: str,
    doc_type: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []

    db_path = search_db_path(repo_root)
    if not db_path.exists():
        build_index(repo_root)

    params: list[Any] = [query]
    where_type = "AND doc_type = ?" if doc_type else ""
    if doc_type:
        params.append(doc_type)
    params.append(limit)

    sql = f"""
        SELECT ticker, title, file_path, doc_type, analysis_date,
               highlight(documents, 2, '<mark>', '</mark>') AS snippet
        FROM documents
        WHERE documents MATCH ?
        {where_type}
        ORDER BY rank
        LIMIT ?
    """

    with _connect(db_path) as conn:
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            clean = "".join(ch for ch in query if ch.isalnum() or ch.isspace())
            if not clean.strip():
                return []
            params[0] = clean
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                return []

    results: list[dict[str, Any]] = []
    for row in rows:
        snippet = row["snippet"] or ""
        mark_pos = snippet.find("<mark>")
        if mark_pos > 120:
            snippet = "..." + snippet[mark_pos - 80 :]
        if len(snippet) > 300:
            snippet = snippet[:300] + "..."
        results.append(
            {
                "ticker": row["ticker"],
                "title": row["title"],
                "file_path": row["file_path"],
                "doc_type": row["doc_type"],
                "analysis_date": row["analysis_date"],
                "snippet": snippet,
            }
        )
    return results


def get_index_stats(repo_root: str | Path) -> dict[str, Any]:
    db_path = search_db_path(repo_root)
    if not db_path.exists():
        return {"total_docs": 0, "last_built": None, "db_size_kb": 0}

    with _connect(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        row = conn.execute("SELECT value FROM meta WHERE key='last_built'").fetchone()

    return {
        "total_docs": total,
        "last_built": float(row[0]) if row else None,
        "db_size_kb": db_path.stat().st_size // 1024 if db_path.exists() else 0,
    }


__all__ = ["build_index", "get_index_stats", "search_documents", "search_db_path"]
