"""
Evidence database layer — read/write methods for the 8 evidence tables.

Follows the same patterns as src/database.py: _decimal_fields_from_dict
before writes, _row_to_dict on reads, commit after every write,
DuplicateEntryError on IntegrityError.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from typing import Optional

from src.database import (
    Database,
    DuplicateEntryError,
    _decimal_fields_from_dict,
    _row_to_dict,
)

logger = logging.getLogger(__name__)


class EvidenceDB:
    """SQLite wrapper for the evidence extraction layer.

    Takes a Database instance and reuses its connection. Does not own
    the connection, does not call connect() or init_db(), does not
    close the connection.
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    @property
    def conn(self) -> sqlite3.Connection:
        return self.db.conn

    # ------------------------------------------------------------------
    # source_documents
    # ------------------------------------------------------------------

    def insert_source_document(self, doc: dict) -> int:
        """Insert a source document. Returns the new row id."""
        doc = _decimal_fields_from_dict(doc)
        try:
            cur = self.conn.execute(
                """INSERT INTO source_documents
                   (ticker, doc_type, filing_date, period_end, accession_number,
                    source_url, local_path, content_hash, section_count, fetched_at)
                   VALUES (:ticker, :doc_type, :filing_date, :period_end, :accession_number,
                           :source_url, :local_path, :content_hash, :section_count, :fetched_at)""",
                doc,
            )
            self.conn.commit()
            logger.debug("Inserted source_document id=%d ticker=%s doc_type=%s",
                         cur.lastrowid, doc.get("ticker"), doc.get("doc_type"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("source_documents", doc.get("ticker", ""), str(e)) from e

    def upsert_source_document(self, doc: dict) -> int:
        """Insert or update a source document. Returns the row id."""
        doc = _decimal_fields_from_dict(doc)
        try:
            cur = self.conn.execute(
                """INSERT INTO source_documents
                   (ticker, doc_type, filing_date, period_end, accession_number,
                    source_url, local_path, content_hash, section_count, fetched_at)
                   VALUES (:ticker, :doc_type, :filing_date, :period_end, :accession_number,
                           :source_url, :local_path, :content_hash, :section_count, :fetched_at)
                   ON CONFLICT(ticker, doc_type, period_end) DO UPDATE SET
                       filing_date = excluded.filing_date,
                       accession_number = excluded.accession_number,
                       source_url = excluded.source_url,
                       local_path = excluded.local_path,
                       content_hash = excluded.content_hash,
                       section_count = excluded.section_count,
                       fetched_at = excluded.fetched_at""",
                doc,
            )
            self.conn.commit()
            row_id = cur.lastrowid
            if row_id == 0:
                # ON CONFLICT UPDATE doesn't set lastrowid; look up existing row
                existing = self.conn.execute(
                    "SELECT id FROM source_documents WHERE ticker = ? AND doc_type = ? AND period_end = ?",
                    (doc["ticker"], doc["doc_type"], doc["period_end"]),
                ).fetchone()
                if existing:
                    row_id = existing[0]
            logger.debug("Upserted source_document id=%d ticker=%s", row_id, doc.get("ticker"))
            return row_id
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("source_documents", doc.get("ticker", ""), str(e)) from e

    def get_source_document(self, doc_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM source_documents WHERE id = ?", (doc_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_source_documents_for_ticker(self, ticker: str, doc_type: str = None) -> list[dict]:
        if doc_type:
            rows = self.conn.execute(
                "SELECT * FROM source_documents WHERE ticker = ? AND doc_type = ? ORDER BY filing_date DESC",
                (ticker, doc_type),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM source_documents WHERE ticker = ? ORDER BY filing_date DESC",
                (ticker,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_source_document_by_key(self, ticker: str, doc_type: str, period_end: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM source_documents WHERE ticker = ? AND doc_type = ? AND period_end = ?",
            (ticker, doc_type, period_end),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def update_source_document(self, doc_id: int, **fields) -> None:
        """Update mutable fields on a source document."""
        if not fields:
            return
        sets = []
        params = []
        for col in ("content_hash", "section_count", "local_path", "source_url", "fetched_at"):
            if col in fields:
                sets.append(f"{col} = ?")
                params.append(fields[col])
        if not sets:
            return
        params.append(doc_id)
        self.conn.execute(
            f"UPDATE source_documents SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # document_sections
    # ------------------------------------------------------------------

    def insert_document_section(self, section: dict) -> int:
        """Insert a document section. Returns the new row id."""
        section = _decimal_fields_from_dict(section)
        try:
            cur = self.conn.execute(
                """INSERT INTO document_sections
                   (source_document_id, section_key, section_title, section_order,
                    content_text, content_hash, token_estimate)
                   VALUES (:source_document_id, :section_key, :section_title, :section_order,
                           :content_text, :content_hash, :token_estimate)""",
                section,
            )
            self.conn.commit()
            logger.debug("Inserted document_section id=%d key=%s", cur.lastrowid, section.get("section_key"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("document_sections", "", str(e)) from e

    def upsert_document_section(self, section: dict) -> int:
        """Insert or update a document section. Returns the row id."""
        section = _decimal_fields_from_dict(section)
        try:
            cur = self.conn.execute(
                """INSERT INTO document_sections
                   (source_document_id, section_key, section_title, section_order,
                    content_text, content_hash, token_estimate)
                   VALUES (:source_document_id, :section_key, :section_title, :section_order,
                           :content_text, :content_hash, :token_estimate)
                   ON CONFLICT(source_document_id, section_key) DO UPDATE SET
                       section_title = excluded.section_title,
                       section_order = excluded.section_order,
                       content_text = excluded.content_text,
                       content_hash = excluded.content_hash,
                       token_estimate = excluded.token_estimate""",
                section,
            )
            self.conn.commit()
            logger.debug("Upserted document_section id=%d key=%s", cur.lastrowid, section.get("section_key"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("document_sections", "", str(e)) from e

    def get_document_sections(self, source_document_id: int) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM document_sections WHERE source_document_id = ? ORDER BY section_order ASC",
            (source_document_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_document_section_by_key(self, source_document_id: int, section_key: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM document_sections WHERE source_document_id = ? AND section_key = ?",
            (source_document_id, section_key),
        ).fetchone()
        return _row_to_dict(row) if row else None

    # ------------------------------------------------------------------
    # extracted_facts
    # ------------------------------------------------------------------

    def insert_extracted_fact(self, fact: dict) -> int:
        """Insert an extracted fact. Returns the new row id."""
        fact = _decimal_fields_from_dict(fact)
        try:
            cur = self.conn.execute(
                """INSERT INTO extracted_facts
                   (ticker, source_document_id, document_section_id, fact_type,
                    fact_key, fact_value, fact_value_numeric, fact_unit, fiscal_period,
                    confidence, extraction_method, source_quote,
                    source_char_offset_start, source_char_offset_end,
                    computation_trace_json, extraction_run_id, is_active)
                   VALUES (:ticker, :source_document_id, :document_section_id, :fact_type,
                           :fact_key, :fact_value, :fact_value_numeric, :fact_unit, :fiscal_period,
                           :confidence, :extraction_method, :source_quote,
                           :source_char_offset_start, :source_char_offset_end,
                           :computation_trace_json, :extraction_run_id, :is_active)""",
                fact,
            )
            self.conn.commit()
            logger.debug("Inserted extracted_fact id=%d ticker=%s key=%s",
                         cur.lastrowid, fact.get("ticker"), fact.get("fact_key"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("extracted_facts", fact.get("ticker", ""), str(e)) from e

    def batch_insert_facts(self, facts: list[dict]) -> int:
        """Insert multiple facts in a single transaction. Returns count inserted."""
        if not facts:
            return 0
        prepared = [_decimal_fields_from_dict(f) for f in facts]
        try:
            cur = self.conn.executemany(
                """INSERT INTO extracted_facts
                   (ticker, source_document_id, document_section_id, fact_type,
                    fact_key, fact_value, fact_value_numeric, fact_unit, fiscal_period,
                    confidence, extraction_method, source_quote,
                    source_char_offset_start, source_char_offset_end,
                    computation_trace_json, extraction_run_id, is_active)
                   VALUES (:ticker, :source_document_id, :document_section_id, :fact_type,
                           :fact_key, :fact_value, :fact_value_numeric, :fact_unit, :fiscal_period,
                           :confidence, :extraction_method, :source_quote,
                           :source_char_offset_start, :source_char_offset_end,
                           :computation_trace_json, :extraction_run_id, :is_active)""",
                prepared,
            )
            self.conn.commit()
            logger.info("Batch inserted %d facts for %s", cur.rowcount, prepared[0].get("ticker", "?"))
            return cur.rowcount
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise DuplicateEntryError("extracted_facts", "", str(e)) from e

    def get_extracted_fact(self, fact_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM extracted_facts WHERE id = ?", (fact_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_facts_for_ticker(
        self,
        ticker: str,
        fact_type: str = None,
        fact_key: str = None,
        fiscal_period: str = None,
        extraction_method: str = None,
        include_inactive: bool = False,
        limit: int = 500,
    ) -> list[dict]:
        """Get facts for a ticker with optional filters."""
        clauses = ["ticker = ?"]
        params: list = [ticker]
        if not include_inactive:
            clauses.append("is_active = 1")
        if fact_type:
            clauses.append("fact_type = ?")
            params.append(fact_type)
        if fact_key:
            clauses.append("fact_key = ?")
            params.append(fact_key)
        if fiscal_period:
            clauses.append("fiscal_period = ?")
            params.append(fiscal_period)
        if extraction_method:
            clauses.append("extraction_method = ?")
            params.append(extraction_method)
        where = " AND ".join(clauses)
        params.append(limit)
        rows = self.conn.execute(
            f"SELECT * FROM extracted_facts WHERE {where} ORDER BY fiscal_period DESC, created_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_facts_for_document(self, source_document_id: int, include_inactive: bool = False) -> list[dict]:
        active_clause = "" if include_inactive else " AND is_active = 1"
        rows = self.conn.execute(
            f"SELECT * FROM extracted_facts WHERE source_document_id = ?{active_clause} ORDER BY fact_key",
            (source_document_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_facts_for_section(self, document_section_id: int, include_inactive: bool = False) -> list[dict]:
        active_clause = "" if include_inactive else " AND is_active = 1"
        rows = self.conn.execute(
            f"SELECT * FROM extracted_facts WHERE document_section_id = ?{active_clause} ORDER BY fact_key",
            (document_section_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_facts_by_extraction_run(self, extraction_run_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM extracted_facts WHERE extraction_run_id = ? ORDER BY id",
            (extraction_run_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_fact_with_provenance(self, fact_id: int) -> Optional[dict]:
        """Get a fact with its source document and section info joined in."""
        row = self.conn.execute(
            """SELECT f.*,
                      sd.ticker AS doc_ticker, sd.doc_type, sd.filing_date,
                      sd.period_end AS doc_period_end, sd.accession_number,
                      sd.source_url AS doc_source_url,
                      ds.section_key, ds.section_title
               FROM extracted_facts f
               JOIN source_documents sd ON f.source_document_id = sd.id
               LEFT JOIN document_sections ds ON f.document_section_id = ds.id
               WHERE f.id = ?""",
            (fact_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def deactivate_facts_for_document(self, source_document_id: int) -> int:
        """Mark all facts for a document as inactive. Returns count affected."""
        cur = self.conn.execute(
            "UPDATE extracted_facts SET is_active = 0 WHERE source_document_id = ? AND is_active = 1",
            (source_document_id,),
        )
        self.conn.commit()
        logger.info("Deactivated %d facts for source_document_id=%d", cur.rowcount, source_document_id)
        return cur.rowcount

    def deactivate_llm_facts_for_document(self, source_document_id: int) -> int:
        """Mark LLM-extracted facts for a document as inactive.

        Preserves XBRL and computed facts. Returns count affected.
        """
        cur = self.conn.execute(
            "UPDATE extracted_facts SET is_active = 0 "
            "WHERE source_document_id = ? AND is_active = 1 "
            "AND extraction_method = 'llm_structured'",
            (source_document_id,),
        )
        self.conn.commit()
        logger.info("Deactivated %d LLM facts for source_document_id=%d", cur.rowcount, source_document_id)
        return cur.rowcount

    def delete_inactive_llm_facts(self, source_document_id: int) -> int:
        """Delete inactive LLM facts that have no assertion_evidence links.

        Safe: rows with evidence links are preserved (NOT IN subquery).
        Call after deactivate_llm_facts_for_document, before batch_insert_facts.
        """
        cur = self.conn.execute(
            """DELETE FROM extracted_facts
               WHERE source_document_id = ? AND is_active = 0
                 AND extraction_method = 'llm_structured'
                 AND id NOT IN (SELECT extracted_fact_id FROM assertion_evidence)""",
            (source_document_id,),
        )
        self.conn.commit()
        logger.info("Deleted %d inactive LLM facts for source_document_id=%d", cur.rowcount, source_document_id)
        return cur.rowcount

    def deactivate_xbrl_facts_for_document(self, source_document_id: int) -> int:
        """Mark XBRL-extracted facts for a document as inactive.

        Preserves LLM and computed facts. Returns count affected.
        """
        cur = self.conn.execute(
            "UPDATE extracted_facts SET is_active = 0 "
            "WHERE source_document_id = ? AND is_active = 1 "
            "AND extraction_method = 'xbrl'",
            (source_document_id,),
        )
        self.conn.commit()
        logger.info("Deactivated %d XBRL facts for source_document_id=%d", cur.rowcount, source_document_id)
        return cur.rowcount

    def delete_inactive_xbrl_facts(self, source_document_id: int) -> int:
        """Delete inactive XBRL facts that have no assertion_evidence links.

        Safe: rows with evidence links are preserved (NOT IN subquery).
        Call after deactivate_xbrl_facts_for_document, before batch_insert_facts.
        """
        cur = self.conn.execute(
            """DELETE FROM extracted_facts
               WHERE source_document_id = ? AND is_active = 0
                 AND extraction_method = 'xbrl'
                 AND id NOT IN (SELECT extracted_fact_id FROM assertion_evidence)""",
            (source_document_id,),
        )
        self.conn.commit()
        logger.info("Deleted %d inactive XBRL facts for source_document_id=%d", cur.rowcount, source_document_id)
        return cur.rowcount

    def delete_facts_for_extraction_run(self, extraction_run_id: str) -> int:
        """Hard-delete all facts for an extraction run. Returns count deleted.

        Raises RuntimeError if any facts have assertion_evidence links.
        Use deactivate_facts_for_document() instead for the common
        re-extraction case — it preserves evidence links for audit.
        """
        # Check for evidence links that would cause FK RESTRICT violation
        linked = self.conn.execute(
            """SELECT COUNT(*) AS c FROM assertion_evidence ae
               JOIN extracted_facts f ON ae.extracted_fact_id = f.id
               WHERE f.extraction_run_id = ?""",
            (extraction_run_id,),
        ).fetchone()["c"]
        if linked > 0:
            raise RuntimeError(
                f"Cannot hard-delete facts for extraction_run_id={extraction_run_id}: "
                f"{linked} assertion_evidence links exist. "
                f"Use deactivate_facts_for_document() to soft-delete instead."
            )
        cur = self.conn.execute(
            "DELETE FROM extracted_facts WHERE extraction_run_id = ?",
            (extraction_run_id,),
        )
        self.conn.commit()
        logger.info("Deleted %d facts for extraction_run_id=%s", cur.rowcount, extraction_run_id)
        return cur.rowcount

    # ------------------------------------------------------------------
    # assertions
    # ------------------------------------------------------------------

    def insert_assertion(self, assertion: dict) -> int:
        """Insert an assertion. Returns the new row id."""
        assertion = _decimal_fields_from_dict(assertion)
        try:
            cur = self.conn.execute(
                """INSERT INTO assertions
                   (ticker, report_path, umbrella_number, assertion_text,
                    assertion_type, category, requires_arithmetic)
                   VALUES (:ticker, :report_path, :umbrella_number, :assertion_text,
                           :assertion_type, :category, :requires_arithmetic)""",
                assertion,
            )
            self.conn.commit()
            logger.debug("Inserted assertion id=%d ticker=%s", cur.lastrowid, assertion.get("ticker"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("assertions", assertion.get("ticker", ""), str(e)) from e

    def batch_insert_assertions(self, assertions: list[dict]) -> int:
        """Insert multiple assertions in a single transaction. Returns count inserted."""
        if not assertions:
            return 0
        prepared = [_decimal_fields_from_dict(a) for a in assertions]
        try:
            cur = self.conn.executemany(
                """INSERT INTO assertions
                   (ticker, report_path, umbrella_number, assertion_text,
                    assertion_type, category, requires_arithmetic)
                   VALUES (:ticker, :report_path, :umbrella_number, :assertion_text,
                           :assertion_type, :category, :requires_arithmetic)""",
                prepared,
            )
            self.conn.commit()
            logger.info("Batch inserted %d assertions for %s", cur.rowcount, prepared[0].get("ticker", "?"))
            return cur.rowcount
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise DuplicateEntryError("assertions", "", str(e)) from e

    def get_assertion(self, assertion_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM assertions WHERE id = ?", (assertion_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_assertions_for_ticker(self, ticker: str, umbrella_number: int = None) -> list[dict]:
        if umbrella_number is not None:
            rows = self.conn.execute(
                "SELECT * FROM assertions WHERE ticker = ? AND umbrella_number = ? ORDER BY id",
                (ticker, umbrella_number),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM assertions WHERE ticker = ? ORDER BY umbrella_number ASC, id ASC",
                (ticker,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_unverified_assertions(self, ticker: str = None) -> list[dict]:
        """Get assertions with no evidence links."""
        if ticker:
            rows = self.conn.execute(
                """SELECT a.* FROM assertions a
                   LEFT JOIN assertion_evidence ae ON a.id = ae.assertion_id
                   WHERE ae.id IS NULL AND a.ticker = ?
                   ORDER BY a.umbrella_number ASC, a.id ASC""",
                (ticker,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """SELECT a.* FROM assertions a
                   LEFT JOIN assertion_evidence ae ON a.id = ae.assertion_id
                   WHERE ae.id IS NULL
                   ORDER BY a.ticker, a.umbrella_number ASC, a.id ASC"""
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def delete_assertions_for_report(self, report_path: str) -> int:
        """Delete all assertions for a report. CASCADE deletes assertion_evidence."""
        cur = self.conn.execute(
            "DELETE FROM assertions WHERE report_path = ?",
            (report_path,),
        )
        self.conn.commit()
        logger.info("Deleted %d assertions for report=%s", cur.rowcount, report_path)
        return cur.rowcount

    # ------------------------------------------------------------------
    # assertion_evidence
    # ------------------------------------------------------------------

    def insert_assertion_evidence(self, link: dict) -> int:
        """Insert an assertion-evidence link. Returns the new row id."""
        link = _decimal_fields_from_dict(link)
        try:
            cur = self.conn.execute(
                """INSERT INTO assertion_evidence
                   (assertion_id, extracted_fact_id, relationship, match_score,
                    verification_method, verification_detail_json, verified_at)
                   VALUES (:assertion_id, :extracted_fact_id, :relationship, :match_score,
                           :verification_method, :verification_detail_json, :verified_at)""",
                link,
            )
            self.conn.commit()
            logger.debug("Inserted assertion_evidence id=%d assertion=%d fact=%d",
                         cur.lastrowid, link.get("assertion_id"), link.get("extracted_fact_id"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("assertion_evidence", "", str(e)) from e

    def get_evidence_for_assertion(self, assertion_id: int, include_inactive: bool = False) -> list[dict]:
        """Get evidence links for an assertion, joined with fact details.

        By default excludes evidence linked to deactivated facts.
        Set include_inactive=True for audit views.
        """
        active_clause = "" if include_inactive else " AND f.is_active = 1"
        rows = self.conn.execute(
            f"""SELECT ae.*,
                      f.fact_key, f.fact_value, f.fact_value_numeric,
                      f.fact_unit, f.fiscal_period, f.source_quote,
                      f.confidence, f.is_active
               FROM assertion_evidence ae
               JOIN extracted_facts f ON ae.extracted_fact_id = f.id
               WHERE ae.assertion_id = ?{active_clause}
               ORDER BY ae.match_score DESC""",
            (assertion_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_evidence_for_fact(self, extracted_fact_id: int, include_inactive: bool = False) -> list[dict]:
        """Get all assertions referencing this fact.

        By default excludes links where the fact is deactivated.
        Set include_inactive=True for audit views.
        """
        active_clause = "" if include_inactive else " AND f.is_active = 1"
        rows = self.conn.execute(
            f"""SELECT ae.*, a.ticker, a.assertion_text, a.assertion_type, a.umbrella_number,
                       f.is_active
               FROM assertion_evidence ae
               JOIN assertions a ON ae.assertion_id = a.id
               JOIN extracted_facts f ON ae.extracted_fact_id = f.id
               WHERE ae.extracted_fact_id = ?{active_clause}
               ORDER BY ae.verified_at DESC""",
            (extracted_fact_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_evidence_summary_for_ticker(self, ticker: str) -> dict:
        """Aggregate verification counts for a ticker.

        All counts use assertion-level granularity (COUNT DISTINCT a.id).
        An assertion with both 'supports' and 'contradicts' evidence will
        appear in both categories, so relationship counts may exceed
        total_assertions. This surfaces conflicting evidence by design.
        """
        row = self.conn.execute(
            """SELECT
                   COUNT(DISTINCT a.id) AS total_assertions,
                   COUNT(DISTINCT CASE WHEN ae.id IS NOT NULL THEN a.id END) AS verified_count,
                   COALESCE(COUNT(DISTINCT CASE WHEN ae.relationship = 'supports' THEN a.id END), 0) AS supported_count,
                   COALESCE(COUNT(DISTINCT CASE WHEN ae.relationship = 'contradicts' THEN a.id END), 0) AS contradicted_count,
                   COALESCE(COUNT(DISTINCT CASE WHEN ae.relationship = 'partial' THEN a.id END), 0) AS partial_count,
                   COALESCE(COUNT(DISTINCT CASE WHEN ae.relationship = 'unverifiable' THEN a.id END), 0) AS unverifiable_count
               FROM assertions a
               LEFT JOIN assertion_evidence ae ON a.id = ae.assertion_id
               WHERE a.ticker = ?""",
            (ticker,),
        ).fetchone()
        return _row_to_dict(row)

    def update_assertion_evidence(self, assertion_id: int, extracted_fact_id: int, **fields) -> bool:
        """Update fields on an assertion-evidence link.

        Returns True if a row was updated, False if no matching row exists.
        """
        if not fields:
            return False
        sets = []
        params = []
        for col in ("relationship", "match_score", "verification_method",
                     "verification_detail_json", "verified_at"):
            if col in fields:
                sets.append(f"{col} = ?")
                val = fields[col]
                if col == "verification_detail_json" and val is not None and not isinstance(val, str):
                    val = json.dumps(val)
                params.append(val)
        if not sets:
            return False
        params.extend([assertion_id, extracted_fact_id])
        cur = self.conn.execute(
            f"UPDATE assertion_evidence SET {', '.join(sets)} WHERE assertion_id = ? AND extracted_fact_id = ?",
            params,
        )
        self.conn.commit()
        if cur.rowcount == 0:
            logger.warning("update_assertion_evidence: no row found for assertion_id=%d, extracted_fact_id=%d",
                           assertion_id, extracted_fact_id)
            return False
        return True

    # ------------------------------------------------------------------
    # verification_runs
    # ------------------------------------------------------------------

    def insert_verification_run(self, run: dict) -> int:
        """Insert a verification run. Returns the new row id."""
        run = _decimal_fields_from_dict(run)
        try:
            cur = self.conn.execute(
                """INSERT INTO verification_runs
                   (run_id, ticker, run_date, total_assertions, verified_count,
                    supported_count, contradicted_count, unverifiable_count,
                    overall_score, run_metadata_json)
                   VALUES (:run_id, :ticker, :run_date, :total_assertions, :verified_count,
                           :supported_count, :contradicted_count, :unverifiable_count,
                           :overall_score, :run_metadata_json)""",
                run,
            )
            self.conn.commit()
            logger.debug("Inserted verification_run id=%d run_id=%s ticker=%s",
                         cur.lastrowid, run.get("run_id"), run.get("ticker"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("verification_runs", run.get("ticker", ""), str(e)) from e

    def get_verification_run(self, run_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM verification_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_verification_runs_for_ticker(self, ticker: str, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM verification_runs WHERE ticker = ? ORDER BY run_date DESC LIMIT ?",
            (ticker, limit),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_latest_verification_run(self, ticker: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM verification_runs WHERE ticker = ? ORDER BY run_date DESC LIMIT 1",
            (ticker,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    # ------------------------------------------------------------------
    # semantic_diffs
    # ------------------------------------------------------------------

    def insert_semantic_diff(self, diff: dict) -> int:
        """Insert a semantic diff. Returns the new row id."""
        diff = _decimal_fields_from_dict(diff)
        cur = self.conn.execute(
            """INSERT INTO semantic_diffs
               (ticker, section_key, period_a, period_b, diff_type,
                summary, detail_json, significance)
               VALUES (:ticker, :section_key, :period_a, :period_b, :diff_type,
                       :summary, :detail_json, :significance)""",
            diff,
        )
        self.conn.commit()
        logger.debug("Inserted semantic_diff id=%d ticker=%s", cur.lastrowid, diff.get("ticker"))
        return cur.lastrowid

    def get_diffs_for_ticker(
        self,
        ticker: str,
        section_key: str = None,
        min_significance: int = None,
    ) -> list[dict]:
        clauses = ["ticker = ?"]
        params: list = [ticker]
        if section_key:
            clauses.append("section_key = ?")
            params.append(section_key)
        if min_significance is not None:
            clauses.append("significance >= ?")
            params.append(min_significance)
        where = " AND ".join(clauses)
        rows = self.conn.execute(
            f"SELECT * FROM semantic_diffs WHERE {where} ORDER BY significance DESC, period_b DESC",
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_diffs_between_periods(self, ticker: str, period_a: str, period_b: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM semantic_diffs WHERE ticker = ? AND period_a = ? AND period_b = ? ORDER BY significance DESC",
            (ticker, period_a, period_b),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_high_significance_diffs(self, min_significance: int = 4, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM semantic_diffs WHERE significance >= ? ORDER BY significance DESC, created_at DESC LIMIT ?",
            (min_significance, limit),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def delete_diffs_between_periods(self, ticker: str, period_a: str, period_b: str) -> int:
        """Delete diffs between two periods. Returns count deleted."""
        cur = self.conn.execute(
            "DELETE FROM semantic_diffs WHERE ticker = ? AND period_a = ? AND period_b = ?",
            (ticker, period_a, period_b),
        )
        self.conn.commit()
        logger.info("Deleted %d diffs for %s %s→%s", cur.rowcount, ticker, period_a, period_b)
        return cur.rowcount

    # ------------------------------------------------------------------
    # computation_cache
    # ------------------------------------------------------------------

    def upsert_computation(self, comp: dict) -> int:
        """Insert or update a cached computation. Returns the row id."""
        comp = _decimal_fields_from_dict(comp)
        try:
            cur = self.conn.execute(
                """INSERT INTO computation_cache
                   (ticker, computation_key, formula, inputs_json, result_value, result_unit, computed_at)
                   VALUES (:ticker, :computation_key, :formula, :inputs_json, :result_value, :result_unit, :computed_at)
                   ON CONFLICT(ticker, computation_key) DO UPDATE SET
                       formula = excluded.formula,
                       inputs_json = excluded.inputs_json,
                       result_value = excluded.result_value,
                       result_unit = excluded.result_unit,
                       computed_at = excluded.computed_at""",
                comp,
            )
            self.conn.commit()
            logger.debug("Upserted computation ticker=%s key=%s", comp.get("ticker"), comp.get("computation_key"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("computation_cache", comp.get("ticker", ""), str(e)) from e

    def get_computation(self, ticker: str, computation_key: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM computation_cache WHERE ticker = ? AND computation_key = ?",
            (ticker, computation_key),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_computations_for_ticker(self, ticker: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM computation_cache WHERE ticker = ? ORDER BY computation_key",
            (ticker,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def invalidate_computations(self, ticker: str, computation_key_prefix: str = None) -> int:
        """Delete cached computations. If prefix given, only matching keys."""
        if computation_key_prefix:
            cur = self.conn.execute(
                "DELETE FROM computation_cache WHERE ticker = ? AND computation_key LIKE ?",
                (ticker, computation_key_prefix + "%"),
            )
        else:
            cur = self.conn.execute(
                "DELETE FROM computation_cache WHERE ticker = ?",
                (ticker,),
            )
        self.conn.commit()
        logger.info("Invalidated %d computations for %s", cur.rowcount, ticker)
        return cur.rowcount

    # ------------------------------------------------------------------
    # Cross-table queries
    # ------------------------------------------------------------------

    def get_ticker_evidence_summary(self, ticker: str) -> dict:
        """Comprehensive evidence summary for a ticker."""
        doc_count = self.conn.execute(
            "SELECT COUNT(*) AS c FROM source_documents WHERE ticker = ?", (ticker,)
        ).fetchone()["c"]

        fact_count = self.conn.execute(
            "SELECT COUNT(*) AS c FROM extracted_facts WHERE ticker = ? AND is_active = 1", (ticker,)
        ).fetchone()["c"]

        assertion_count = self.conn.execute(
            "SELECT COUNT(*) AS c FROM assertions WHERE ticker = ?", (ticker,)
        ).fetchone()["c"]

        verified_count = self.conn.execute(
            """SELECT COUNT(DISTINCT a.id) AS c
               FROM assertions a
               JOIN assertion_evidence ae ON a.id = ae.assertion_id
               WHERE a.ticker = ?""",
            (ticker,),
        ).fetchone()["c"]

        latest_run = self.get_latest_verification_run(ticker)

        high_sig_diffs = self.conn.execute(
            "SELECT COUNT(*) AS c FROM semantic_diffs WHERE ticker = ? AND significance >= 4", (ticker,)
        ).fetchone()["c"]

        return {
            "ticker": ticker,
            "source_document_count": doc_count,
            "total_facts": fact_count,
            "total_assertions": assertion_count,
            "verified_assertions": verified_count,
            "verification_coverage": round(verified_count / assertion_count, 3) if assertion_count > 0 else 0.0,
            "latest_verification_score": latest_run["overall_score"] if latest_run else None,
            "high_significance_diffs": high_sig_diffs,
        }
