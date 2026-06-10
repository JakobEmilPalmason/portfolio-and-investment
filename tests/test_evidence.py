"""Smoke tests for the evidence database layer."""
import unittest

from src.database import Database, DuplicateEntryError
from src.evidence import EvidenceDB


def _make_db():
    """Create a fresh in-memory database at schema v3."""
    db = Database(":memory:")
    db.connect()
    db.init_db()
    db.migrate()
    return db


class TestSchemaVersion(unittest.TestCase):
    def test_fresh_install_is_v3(self):
        db = _make_db()
        row = db.conn.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        self.assertEqual(row["version"], 3)
        db._conn.close()

    def test_all_evidence_tables_exist(self):
        db = _make_db()
        tables = {r["name"] for r in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        expected = {
            "source_documents", "document_sections", "extracted_facts",
            "assertions", "assertion_evidence", "verification_runs",
            "semantic_diffs", "computation_cache",
        }
        self.assertTrue(expected.issubset(tables), f"Missing: {expected - tables}")
        db._conn.close()

    def test_v2_to_v3_migration(self):
        """Simulate an existing v2 database migrating to v3."""
        db = Database(":memory:")
        db.connect()
        # Run schema.sql (v1+v2 tables) and set version to 2
        from src.database import SCHEMA_PATH
        db.conn.executescript(SCHEMA_PATH.read_text())
        db.conn.execute("INSERT INTO schema_version (version) VALUES (?)", (2,))
        db.conn.commit()
        # Now migrate — should apply v2→v3 only
        db.migrate()
        row = db.conn.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        self.assertEqual(row["version"], 3)
        # Evidence tables should exist
        tables = {r["name"] for r in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        self.assertIn("extracted_facts", tables)
        self.assertIn("assertion_evidence", tables)
        db._conn.close()


class TestSourceDocuments(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)

    def tearDown(self):
        self.db._conn.close()

    def _sample_doc(self, **overrides):
        doc = {
            "ticker": "AAPL",
            "doc_type": "10-K",
            "filing_date": "2025-11-01",
            "period_end": "2025-09-30",
            "accession_number": "0000320193-25-000001",
            "source_url": "https://sec.gov/...",
            "local_path": "data/context/AAPL/10-K-2025.html",
            "content_hash": "abc123",
            "section_count": 12,
            "fetched_at": "2026-03-19T10:00:00",
        }
        doc.update(overrides)
        return doc

    def test_insert_and_get(self):
        doc_id = self.ev.insert_source_document(self._sample_doc())
        self.assertGreater(doc_id, 0)
        got = self.ev.get_source_document(doc_id)
        self.assertEqual(got["ticker"], "AAPL")
        self.assertEqual(got["doc_type"], "10-K")
        self.assertEqual(got["content_hash"], "abc123")
        self.assertEqual(got["section_count"], 12)

    def test_duplicate_raises(self):
        self.ev.insert_source_document(self._sample_doc())
        with self.assertRaises(DuplicateEntryError):
            self.ev.insert_source_document(self._sample_doc())

    def test_upsert_updates_existing(self):
        self.ev.insert_source_document(self._sample_doc())
        self.ev.upsert_source_document(self._sample_doc(content_hash="xyz789", section_count=15))
        docs = self.ev.get_source_documents_for_ticker("AAPL")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["content_hash"], "xyz789")
        self.assertEqual(docs[0]["section_count"], 15)

    def test_get_by_key(self):
        self.ev.insert_source_document(self._sample_doc())
        got = self.ev.get_source_document_by_key("AAPL", "10-K", "2025-09-30")
        self.assertIsNotNone(got)
        self.assertEqual(got["ticker"], "AAPL")

    def test_get_for_ticker_with_filter(self):
        self.ev.insert_source_document(self._sample_doc())
        self.ev.insert_source_document(self._sample_doc(doc_type="10-Q", period_end="2025-06-30"))
        all_docs = self.ev.get_source_documents_for_ticker("AAPL")
        self.assertEqual(len(all_docs), 2)
        k_docs = self.ev.get_source_documents_for_ticker("AAPL", doc_type="10-K")
        self.assertEqual(len(k_docs), 1)

    def test_amendment_distinct_from_original(self):
        self.ev.insert_source_document(self._sample_doc())
        self.ev.insert_source_document(self._sample_doc(doc_type="10-K/A"))
        docs = self.ev.get_source_documents_for_ticker("AAPL")
        self.assertEqual(len(docs), 2)


class TestDocumentSections(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)
        self.doc_id = self.ev.insert_source_document({
            "ticker": "AAPL", "doc_type": "10-K", "filing_date": "2025-11-01",
            "period_end": "2025-09-30", "accession_number": "x",
            "source_url": "", "local_path": "x", "content_hash": "h",
            "section_count": 3, "fetched_at": "2026-03-19T10:00:00",
        })

    def tearDown(self):
        self.db._conn.close()

    def test_insert_and_get_ordered(self):
        self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "risk_factors",
            "section_title": "Risk Factors", "section_order": 2,
            "content_text": "Risk content...", "content_hash": "h1", "token_estimate": 500,
        })
        self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "mda",
            "section_title": "MD&A", "section_order": 1,
            "content_text": "MDA content...", "content_hash": "h2", "token_estimate": 800,
        })
        sections = self.ev.get_document_sections(self.doc_id)
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]["section_key"], "mda")
        self.assertEqual(sections[1]["section_key"], "risk_factors")

    def test_upsert_updates_content(self):
        self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "mda",
            "section_title": "MD&A", "section_order": 1,
            "content_text": "Old content", "content_hash": "h1", "token_estimate": 100,
        })
        self.ev.upsert_document_section({
            "source_document_id": self.doc_id, "section_key": "mda",
            "section_title": "MD&A", "section_order": 1,
            "content_text": "New content", "content_hash": "h2", "token_estimate": 200,
        })
        sections = self.ev.get_document_sections(self.doc_id)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["content_text"], "New content")
        self.assertEqual(sections[0]["token_estimate"], 200)

    def test_get_by_key(self):
        self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "mda",
            "section_title": "MD&A", "section_order": 1,
            "content_text": "Content", "content_hash": "h1", "token_estimate": 100,
        })
        got = self.ev.get_document_section_by_key(self.doc_id, "mda")
        self.assertIsNotNone(got)
        self.assertEqual(got["content_text"], "Content")


class TestExtractedFacts(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)
        self.doc_id = self.ev.insert_source_document({
            "ticker": "AAPL", "doc_type": "10-K", "filing_date": "2025-11-01",
            "period_end": "2025-09-30", "accession_number": "x",
            "source_url": "", "local_path": "x", "content_hash": "h",
            "section_count": 1, "fetched_at": "2026-03-19T10:00:00",
        })
        self.section_id = self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "income_stmt",
            "section_title": "Income Statement", "section_order": 1,
            "content_text": "Revenue was $394.3 billion", "content_hash": "h1",
            "token_estimate": 50,
        })

    def tearDown(self):
        self.db._conn.close()

    def _sample_fact(self, **overrides):
        fact = {
            "ticker": "AAPL",
            "source_document_id": self.doc_id,
            "document_section_id": self.section_id,
            "fact_type": "metric",
            "fact_key": "revenue",
            "fact_value": "$394.3 billion",
            "fact_value_numeric": 394300000000.0,
            "fact_unit": "USD",
            "fiscal_period": "FY2025",
            "confidence": 1.0,
            "extraction_method": "xbrl",
            "source_quote": "Revenue was $394.3 billion",
            "source_char_offset_start": 0,
            "source_char_offset_end": 27,
            "computation_trace_json": None,
            "extraction_run_id": "run-001",
            "is_active": 1,
        }
        fact.update(overrides)
        return fact

    def test_insert_and_get(self):
        fact_id = self.ev.insert_extracted_fact(self._sample_fact())
        got = self.ev.get_extracted_fact(fact_id)
        self.assertEqual(got["ticker"], "AAPL")
        self.assertEqual(got["fact_key"], "revenue")
        self.assertAlmostEqual(got["fact_value_numeric"], 394300000000.0)
        self.assertEqual(got["confidence"], 1.0)

    def test_duplicate_raises(self):
        self.ev.insert_extracted_fact(self._sample_fact())
        with self.assertRaises(DuplicateEntryError):
            self.ev.insert_extracted_fact(self._sample_fact())

    def test_json_roundtrip(self):
        trace = {"formula": "net_income / invested_capital", "inputs": {"net_income": 99000000000}}
        fact_id = self.ev.insert_extracted_fact(self._sample_fact(
            fact_key="roic", fiscal_period="FY2025_derived",
            computation_trace_json=trace, extraction_method="computed",
        ))
        got = self.ev.get_extracted_fact(fact_id)
        self.assertIsInstance(got["computation_trace_json"], dict)
        self.assertEqual(got["computation_trace_json"]["formula"], "net_income / invested_capital")

    def test_batch_insert(self):
        facts = [
            self._sample_fact(fact_key=f"metric_{i}", fiscal_period=f"FY202{i}")
            for i in range(10)
        ]
        count = self.ev.batch_insert_facts(facts)
        self.assertEqual(count, 10)
        all_facts = self.ev.get_facts_for_ticker("AAPL")
        self.assertEqual(len(all_facts), 10)

    def test_deactivate_facts(self):
        self.ev.insert_extracted_fact(self._sample_fact())
        self.ev.insert_extracted_fact(self._sample_fact(fact_key="gross_margin", fiscal_period="FY2025"))
        # Deactivate
        count = self.ev.deactivate_facts_for_document(self.doc_id)
        self.assertEqual(count, 2)
        # Default query excludes inactive
        active = self.ev.get_facts_for_ticker("AAPL")
        self.assertEqual(len(active), 0)
        # Include inactive
        all_facts = self.ev.get_facts_for_ticker("AAPL", include_inactive=True)
        self.assertEqual(len(all_facts), 2)

    def test_confidence_required(self):
        fact = self._sample_fact(fact_key="test_no_conf")
        del fact["confidence"]
        with self.assertRaises(Exception):
            self.ev.insert_extracted_fact(fact)

    def test_foreign_key_enforcement(self):
        fact = self._sample_fact(source_document_id=9999, fact_key="bad_fk")
        with self.assertRaises(Exception):
            self.ev.insert_extracted_fact(fact)

    def test_get_fact_with_provenance(self):
        fact_id = self.ev.insert_extracted_fact(self._sample_fact())
        got = self.ev.get_fact_with_provenance(fact_id)
        self.assertIsNotNone(got)
        self.assertEqual(got["doc_type"], "10-K")
        self.assertEqual(got["section_key"], "income_stmt")

    def test_multi_filter_query(self):
        self.ev.insert_extracted_fact(self._sample_fact())
        self.ev.insert_extracted_fact(self._sample_fact(
            fact_key="net_income", fact_type="metric", fiscal_period="FY2025",
        ))
        self.ev.insert_extracted_fact(self._sample_fact(
            fact_key="risk_desc", fact_type="risk_factor", fiscal_period="FY2025",
        ))
        metrics = self.ev.get_facts_for_ticker("AAPL", fact_type="metric")
        self.assertEqual(len(metrics), 2)
        risks = self.ev.get_facts_for_ticker("AAPL", fact_type="risk_factor")
        self.assertEqual(len(risks), 1)


class TestAssertions(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)

    def tearDown(self):
        self.db._conn.close()

    def _sample_assertion(self, **overrides):
        a = {
            "ticker": "AAPL",
            "report_path": "runs/week12/reports/AAPL/FINAL-REPORT.md",
            "umbrella_number": 4,
            "assertion_text": "Revenue grew 8% YoY to $394B",
            "assertion_type": "quantitative",
            "category": "business_economics",
            "requires_arithmetic": 1,
        }
        a.update(overrides)
        return a

    def test_insert_and_get_ordered(self):
        self.ev.insert_assertion(self._sample_assertion(umbrella_number=4))
        self.ev.insert_assertion(self._sample_assertion(
            umbrella_number=1, assertion_text="Apple has a wide moat",
            assertion_type="qualitative", category="competitive_advantage",
        ))
        assertions = self.ev.get_assertions_for_ticker("AAPL")
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions[0]["umbrella_number"], 1)
        self.assertEqual(assertions[1]["umbrella_number"], 4)

    def test_batch_insert(self):
        batch = [
            self._sample_assertion(assertion_text=f"Claim {i}", umbrella_number=i)
            for i in range(1, 6)
        ]
        count = self.ev.batch_insert_assertions(batch)
        self.assertEqual(count, 5)

    def test_filter_by_umbrella(self):
        self.ev.insert_assertion(self._sample_assertion(umbrella_number=1))
        self.ev.insert_assertion(self._sample_assertion(umbrella_number=4))
        u1 = self.ev.get_assertions_for_ticker("AAPL", umbrella_number=1)
        self.assertEqual(len(u1), 1)


class TestAssertionEvidence(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)
        # Set up source doc + fact + assertion
        self.doc_id = self.ev.insert_source_document({
            "ticker": "AAPL", "doc_type": "10-K", "filing_date": "2025-11-01",
            "period_end": "2025-09-30", "accession_number": "x",
            "source_url": "", "local_path": "x", "content_hash": "h",
            "section_count": 1, "fetched_at": "2026-03-19T10:00:00",
        })
        self.fact_id = self.ev.insert_extracted_fact({
            "ticker": "AAPL", "source_document_id": self.doc_id,
            "document_section_id": None, "fact_type": "metric",
            "fact_key": "revenue", "fact_value": "$394B",
            "fact_value_numeric": 394000000000.0, "fact_unit": "USD",
            "fiscal_period": "FY2025", "confidence": 1.0,
            "extraction_method": "xbrl", "source_quote": "Revenue: $394B",
            "source_char_offset_start": 0, "source_char_offset_end": 14,
            "computation_trace_json": None, "extraction_run_id": "run-001",
            "is_active": 1,
        })
        self.assertion_id = self.ev.insert_assertion({
            "ticker": "AAPL",
            "report_path": "runs/week12/reports/AAPL/FINAL-REPORT.md",
            "umbrella_number": 4,
            "assertion_text": "Revenue was $394B",
            "assertion_type": "quantitative",
            "category": "business_economics",
            "requires_arithmetic": 0,
        })

    def tearDown(self):
        self.db._conn.close()

    def test_insert_and_get_evidence(self):
        link_id = self.ev.insert_assertion_evidence({
            "assertion_id": self.assertion_id,
            "extracted_fact_id": self.fact_id,
            "relationship": "supports",
            "match_score": 0.95,
            "verification_method": "exact_match",
            "verification_detail_json": {"method": "string_compare"},
            "verified_at": "2026-03-19T12:00:00",
        })
        self.assertGreater(link_id, 0)
        evidence = self.ev.get_evidence_for_assertion(self.assertion_id)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["relationship"], "supports")
        self.assertEqual(evidence[0]["fact_key"], "revenue")

    def test_duplicate_raises(self):
        self.ev.insert_assertion_evidence({
            "assertion_id": self.assertion_id, "extracted_fact_id": self.fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        with self.assertRaises(DuplicateEntryError):
            self.ev.insert_assertion_evidence({
                "assertion_id": self.assertion_id, "extracted_fact_id": self.fact_id,
                "relationship": "contradicts", "match_score": 0.5,
                "verification_method": "test", "verification_detail_json": None,
                "verified_at": None,
            })

    def test_unverified_assertions(self):
        # assertion_id has no evidence yet
        unverified = self.ev.get_unverified_assertions("AAPL")
        self.assertEqual(len(unverified), 1)
        self.assertEqual(unverified[0]["id"], self.assertion_id)
        # Add evidence
        self.ev.insert_assertion_evidence({
            "assertion_id": self.assertion_id, "extracted_fact_id": self.fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        unverified = self.ev.get_unverified_assertions("AAPL")
        self.assertEqual(len(unverified), 0)

    def test_cascade_delete(self):
        """Deleting an assertion should cascade-delete its evidence links."""
        self.ev.insert_assertion_evidence({
            "assertion_id": self.assertion_id, "extracted_fact_id": self.fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        # Verify evidence exists
        evidence = self.ev.get_evidence_for_assertion(self.assertion_id)
        self.assertEqual(len(evidence), 1)
        # Delete the assertion
        self.ev.delete_assertions_for_report("runs/week12/reports/AAPL/FINAL-REPORT.md")
        # Evidence should be gone too
        evidence = self.ev.get_evidence_for_assertion(self.assertion_id)
        self.assertEqual(len(evidence), 0)

    def test_evidence_summary(self):
        self.ev.insert_assertion_evidence({
            "assertion_id": self.assertion_id, "extracted_fact_id": self.fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": "2026-03-19",
        })
        summary = self.ev.get_evidence_summary_for_ticker("AAPL")
        self.assertEqual(summary["total_assertions"], 1)
        self.assertEqual(summary["verified_count"], 1)
        self.assertEqual(summary["supported_count"], 1)

    def test_json_roundtrip_in_evidence(self):
        detail = {"matched_text": "Revenue: $394B", "score_breakdown": [0.9, 0.95]}
        self.ev.insert_assertion_evidence({
            "assertion_id": self.assertion_id, "extracted_fact_id": self.fact_id,
            "relationship": "supports", "match_score": 0.92,
            "verification_method": "fuzzy_match",
            "verification_detail_json": detail,
            "verified_at": "2026-03-19",
        })
        evidence = self.ev.get_evidence_for_assertion(self.assertion_id)
        self.assertIsInstance(evidence[0]["verification_detail_json"], dict)
        self.assertEqual(evidence[0]["verification_detail_json"]["matched_text"], "Revenue: $394B")


class TestVerificationRuns(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)

    def tearDown(self):
        self.db._conn.close()

    def test_insert_and_get(self):
        run_id = self.ev.insert_verification_run({
            "run_id": "vr-2026-03-19-001",
            "ticker": "AAPL",
            "run_date": "2026-03-19",
            "total_assertions": 42,
            "verified_count": 38,
            "supported_count": 35,
            "contradicted_count": 1,
            "unverifiable_count": 6,
            "overall_score": 0.83,
            "run_metadata_json": {"model": "claude-opus-4-6", "duration_s": 120},
        })
        got = self.ev.get_verification_run("vr-2026-03-19-001")
        self.assertIsNotNone(got)
        self.assertEqual(got["total_assertions"], 42)
        self.assertAlmostEqual(got["overall_score"], 0.83)
        self.assertIsInstance(got["run_metadata_json"], dict)
        self.assertEqual(got["run_metadata_json"]["model"], "claude-opus-4-6")

    def test_latest_run(self):
        self.ev.insert_verification_run({
            "run_id": "vr-001", "ticker": "AAPL", "run_date": "2026-03-01",
            "total_assertions": 10, "verified_count": 8, "supported_count": 7,
            "contradicted_count": 0, "unverifiable_count": 3,
            "overall_score": 0.70, "run_metadata_json": None,
        })
        self.ev.insert_verification_run({
            "run_id": "vr-002", "ticker": "AAPL", "run_date": "2026-03-19",
            "total_assertions": 42, "verified_count": 38, "supported_count": 35,
            "contradicted_count": 1, "unverifiable_count": 6,
            "overall_score": 0.83, "run_metadata_json": None,
        })
        latest = self.ev.get_latest_verification_run("AAPL")
        self.assertEqual(latest["run_id"], "vr-002")
        self.assertAlmostEqual(latest["overall_score"], 0.83)


class TestSemanticDiffs(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)

    def tearDown(self):
        self.db._conn.close()

    def test_insert_and_filter_by_significance(self):
        self.ev.insert_semantic_diff({
            "ticker": "AAPL", "section_key": "mda",
            "period_a": "FY2024", "period_b": "FY2025",
            "diff_type": "changed", "summary": "Revenue guidance raised",
            "detail_json": {"old": "flat", "new": "+5%"}, "significance": 5,
        })
        self.ev.insert_semantic_diff({
            "ticker": "AAPL", "section_key": "risk_factors",
            "period_a": "FY2024", "period_b": "FY2025",
            "diff_type": "added", "summary": "New AI regulation risk",
            "detail_json": None, "significance": 3,
        })
        self.ev.insert_semantic_diff({
            "ticker": "AAPL", "section_key": "mda",
            "period_a": "FY2024", "period_b": "FY2025",
            "diff_type": "numeric_shift", "summary": "Margin expanded 200bps",
            "detail_json": {"old_margin": 0.30, "new_margin": 0.32}, "significance": 4,
        })
        # All diffs
        all_diffs = self.ev.get_diffs_for_ticker("AAPL")
        self.assertEqual(len(all_diffs), 3)
        # High significance only
        high = self.ev.get_diffs_for_ticker("AAPL", min_significance=4)
        self.assertEqual(len(high), 2)
        # By section
        mda = self.ev.get_diffs_for_ticker("AAPL", section_key="mda")
        self.assertEqual(len(mda), 2)

    def test_diffs_between_periods(self):
        self.ev.insert_semantic_diff({
            "ticker": "AAPL", "section_key": "mda",
            "period_a": "FY2024", "period_b": "FY2025",
            "diff_type": "changed", "summary": "test",
            "detail_json": None, "significance": 3,
        })
        diffs = self.ev.get_diffs_between_periods("AAPL", "FY2024", "FY2025")
        self.assertEqual(len(diffs), 1)

    def test_json_roundtrip(self):
        self.ev.insert_semantic_diff({
            "ticker": "AAPL", "section_key": "mda",
            "period_a": "FY2024", "period_b": "FY2025",
            "diff_type": "numeric_shift", "summary": "Margin changed",
            "detail_json": {"old": 0.30, "new": 0.32, "delta_bps": 200},
            "significance": 4,
        })
        diffs = self.ev.get_diffs_for_ticker("AAPL")
        self.assertIsInstance(diffs[0]["detail_json"], dict)
        self.assertEqual(diffs[0]["detail_json"]["delta_bps"], 200)


class TestComputationCache(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)

    def tearDown(self):
        self.db._conn.close()

    def test_upsert_and_get(self):
        self.ev.upsert_computation({
            "ticker": "AAPL", "computation_key": "roic_FY2025",
            "formula": "nopat / invested_capital",
            "inputs_json": {"nopat": 99000000000, "invested_capital": 350000000000},
            "result_value": 0.2829, "result_unit": "ratio",
            "computed_at": "2026-03-19T12:00:00",
        })
        got = self.ev.get_computation("AAPL", "roic_FY2025")
        self.assertIsNotNone(got)
        self.assertAlmostEqual(got["result_value"], 0.2829)
        self.assertIsInstance(got["inputs_json"], dict)

    def test_upsert_updates(self):
        self.ev.upsert_computation({
            "ticker": "AAPL", "computation_key": "roic_FY2025",
            "formula": "nopat / ic", "inputs_json": {"a": 1},
            "result_value": 0.25, "result_unit": "ratio",
            "computed_at": "2026-03-19T10:00:00",
        })
        self.ev.upsert_computation({
            "ticker": "AAPL", "computation_key": "roic_FY2025",
            "formula": "nopat / ic_revised", "inputs_json": {"a": 2},
            "result_value": 0.28, "result_unit": "ratio",
            "computed_at": "2026-03-19T12:00:00",
        })
        all_comps = self.ev.get_computations_for_ticker("AAPL")
        self.assertEqual(len(all_comps), 1)
        self.assertAlmostEqual(all_comps[0]["result_value"], 0.28)

    def test_invalidate(self):
        self.ev.upsert_computation({
            "ticker": "AAPL", "computation_key": "roic_FY2025",
            "formula": "x", "inputs_json": {}, "result_value": 0.25,
            "result_unit": "ratio", "computed_at": "2026-03-19",
        })
        self.ev.upsert_computation({
            "ticker": "AAPL", "computation_key": "roic_FY2024",
            "formula": "x", "inputs_json": {}, "result_value": 0.22,
            "result_unit": "ratio", "computed_at": "2026-03-19",
        })
        self.ev.upsert_computation({
            "ticker": "AAPL", "computation_key": "fcf_yield_FY2025",
            "formula": "x", "inputs_json": {}, "result_value": 0.04,
            "result_unit": "ratio", "computed_at": "2026-03-19",
        })
        # Invalidate only roic_* keys
        count = self.ev.invalidate_computations("AAPL", "roic_")
        self.assertEqual(count, 2)
        remaining = self.ev.get_computations_for_ticker("AAPL")
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["computation_key"], "fcf_yield_FY2025")


class TestTickerEvidenceSummary(unittest.TestCase):
    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)

    def tearDown(self):
        self.db._conn.close()

    def test_end_to_end_summary(self):
        # Source doc
        doc_id = self.ev.insert_source_document({
            "ticker": "AAPL", "doc_type": "10-K", "filing_date": "2025-11-01",
            "period_end": "2025-09-30", "accession_number": "x",
            "source_url": "", "local_path": "x", "content_hash": "h",
            "section_count": 1, "fetched_at": "2026-03-19T10:00:00",
        })
        # Facts
        for i in range(5):
            self.ev.insert_extracted_fact({
                "ticker": "AAPL", "source_document_id": doc_id,
                "document_section_id": None, "fact_type": "metric",
                "fact_key": f"metric_{i}", "fact_value": str(i),
                "fact_value_numeric": float(i), "fact_unit": "USD",
                "fiscal_period": "FY2025", "confidence": 1.0,
                "extraction_method": "xbrl", "source_quote": f"Value: {i}",
                "source_char_offset_start": 0, "source_char_offset_end": 10,
                "computation_trace_json": None, "extraction_run_id": "run-001",
                "is_active": 1,
            })
        # Assertions
        a1 = self.ev.insert_assertion({
            "ticker": "AAPL", "report_path": "report.md", "umbrella_number": 4,
            "assertion_text": "Claim 1", "assertion_type": "quantitative",
            "category": "test", "requires_arithmetic": 0,
        })
        a2 = self.ev.insert_assertion({
            "ticker": "AAPL", "report_path": "report.md", "umbrella_number": 5,
            "assertion_text": "Claim 2", "assertion_type": "qualitative",
            "category": "test", "requires_arithmetic": 0,
        })
        # Link only a1
        self.ev.insert_assertion_evidence({
            "assertion_id": a1, "extracted_fact_id": 1,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": "2026-03-19",
        })
        # Verification run
        self.ev.insert_verification_run({
            "run_id": "vr-001", "ticker": "AAPL", "run_date": "2026-03-19",
            "total_assertions": 2, "verified_count": 1, "supported_count": 1,
            "contradicted_count": 0, "unverifiable_count": 1,
            "overall_score": 0.50, "run_metadata_json": None,
        })
        # High-sig diff
        self.ev.insert_semantic_diff({
            "ticker": "AAPL", "section_key": "mda",
            "period_a": "FY2024", "period_b": "FY2025",
            "diff_type": "changed", "summary": "Big change",
            "detail_json": None, "significance": 5,
        })

        summary = self.ev.get_ticker_evidence_summary("AAPL")
        self.assertEqual(summary["source_document_count"], 1)
        self.assertEqual(summary["total_facts"], 5)
        self.assertEqual(summary["total_assertions"], 2)
        self.assertEqual(summary["verified_assertions"], 1)
        self.assertAlmostEqual(summary["verification_coverage"], 0.5)
        self.assertAlmostEqual(summary["latest_verification_score"], 0.50)
        self.assertEqual(summary["high_significance_diffs"], 1)


class TestReviewFixes(unittest.TestCase):
    """Tests for all issues identified in the Phase 3 implementation review."""

    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)
        # Shared setup: doc + section + fact + assertion + evidence link
        self.doc_id = self.ev.insert_source_document({
            "ticker": "AAPL", "doc_type": "10-K", "filing_date": "2025-11-01",
            "period_end": "2025-09-30", "accession_number": "x",
            "source_url": "", "local_path": "x", "content_hash": "h",
            "section_count": 1, "fetched_at": "2026-03-19T10:00:00",
        })
        self.section_id = self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "income_stmt",
            "section_title": "Income Statement", "section_order": 1,
            "content_text": "Revenue was $394.3 billion", "content_hash": "h1",
            "token_estimate": 50,
        })

    def tearDown(self):
        self.db._conn.close()

    def _make_fact(self, **overrides):
        fact = {
            "ticker": "AAPL", "source_document_id": self.doc_id,
            "document_section_id": self.section_id, "fact_type": "metric",
            "fact_key": "revenue", "fact_value": "$394B",
            "fact_value_numeric": 394000000000.0, "fact_unit": "USD",
            "fiscal_period": "FY2025", "confidence": 1.0,
            "extraction_method": "xbrl", "source_quote": "Revenue: $394B",
            "source_char_offset_start": 0, "source_char_offset_end": 14,
            "computation_trace_json": None, "extraction_run_id": "run-001",
            "is_active": 1,
        }
        fact.update(overrides)
        return fact

    def _make_assertion(self, **overrides):
        a = {
            "ticker": "AAPL",
            "report_path": "runs/week12/reports/AAPL/FINAL-REPORT.md",
            "umbrella_number": 4, "assertion_text": "Revenue was $394B",
            "assertion_type": "quantitative", "category": "business_economics",
            "requires_arithmetic": 0,
        }
        a.update(overrides)
        return a

    # --- Fix #1: delete_facts_for_extraction_run FK safety ---

    def test_delete_facts_refuses_when_evidence_links_exist(self):
        """Hard-delete must raise when facts have assertion_evidence links."""
        fact_id = self.ev.insert_extracted_fact(self._make_fact())
        a_id = self.ev.insert_assertion(self._make_assertion())
        self.ev.insert_assertion_evidence({
            "assertion_id": a_id, "extracted_fact_id": fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        with self.assertRaises(RuntimeError) as ctx:
            self.ev.delete_facts_for_extraction_run("run-001")
        self.assertIn("assertion_evidence", str(ctx.exception))

    def test_delete_facts_succeeds_when_no_evidence_links(self):
        """Hard-delete works when facts have no evidence links."""
        self.ev.insert_extracted_fact(self._make_fact())
        count = self.ev.delete_facts_for_extraction_run("run-001")
        self.assertEqual(count, 1)

    # --- Fix #2: stale evidence filtering ---

    def test_get_evidence_excludes_deactivated_facts_by_default(self):
        fact_id = self.ev.insert_extracted_fact(self._make_fact())
        a_id = self.ev.insert_assertion(self._make_assertion())
        self.ev.insert_assertion_evidence({
            "assertion_id": a_id, "extracted_fact_id": fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        # Deactivate the fact
        self.ev.deactivate_facts_for_document(self.doc_id)
        # Default query should exclude stale evidence
        evidence = self.ev.get_evidence_for_assertion(a_id)
        self.assertEqual(len(evidence), 0)
        # include_inactive=True should show it
        evidence = self.ev.get_evidence_for_assertion(a_id, include_inactive=True)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["is_active"], 0)

    # --- Fix #3: summary unit mismatch ---

    def test_evidence_summary_counts_assertions_not_links(self):
        """1 assertion with 3 supporting facts → supported_count = 1, not 3."""
        facts = []
        for i in range(3):
            facts.append(self._make_fact(fact_key=f"metric_{i}", fiscal_period=f"FY202{i}"))
        self.ev.batch_insert_facts(facts)
        a_id = self.ev.insert_assertion(self._make_assertion())
        # Link all 3 facts to the same assertion
        for i in range(1, 4):
            self.ev.insert_assertion_evidence({
                "assertion_id": a_id, "extracted_fact_id": i,
                "relationship": "supports", "match_score": 0.9,
                "verification_method": "test", "verification_detail_json": None,
                "verified_at": None,
            })
        summary = self.ev.get_evidence_summary_for_ticker("AAPL")
        self.assertEqual(summary["total_assertions"], 1)
        self.assertEqual(summary["supported_count"], 1)  # assertion-level, not link-level

    # --- Fix #4 (NULL aggregates): summary returns 0 not None for empty ticker ---

    def test_evidence_summary_returns_zero_not_none_for_empty_ticker(self):
        summary = self.ev.get_evidence_summary_for_ticker("NONEXISTENT")
        self.assertEqual(summary["total_assertions"], 0)
        self.assertEqual(summary["supported_count"], 0)
        self.assertEqual(summary["contradicted_count"], 0)
        self.assertEqual(summary["partial_count"], 0)
        self.assertEqual(summary["unverifiable_count"], 0)
        # Verify they are integers, not None
        self.assertIsInstance(summary["supported_count"], int)

    # --- Fix #5+6: batch rollback ---

    def test_batch_insert_facts_rolls_back_on_duplicate(self):
        """On mid-batch failure, no partial rows should persist."""
        self.ev.insert_extracted_fact(self._make_fact(fact_key="dup_key", fiscal_period="FY2025"))
        batch = [
            self._make_fact(fact_key="new_key_1", fiscal_period="FY2024"),
            self._make_fact(fact_key="dup_key", fiscal_period="FY2025"),  # duplicate
        ]
        with self.assertRaises(DuplicateEntryError):
            self.ev.batch_insert_facts(batch)
        # Only the original should exist, not the partial batch
        all_facts = self.ev.get_facts_for_ticker("AAPL", include_inactive=True)
        self.assertEqual(len(all_facts), 1)
        self.assertEqual(all_facts[0]["fact_key"], "dup_key")

    # --- Fix #7: semantic_diff NOT NULL violation ---

    def test_semantic_diff_not_null_raises_integrity_error(self):
        """Missing required field should raise IntegrityError, not DuplicateEntryError."""
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            self.ev.insert_semantic_diff({
                "ticker": "AAPL", "section_key": "mda",
                "period_a": "FY2024", "period_b": "FY2025",
                "diff_type": "changed", "summary": None,  # NOT NULL violation
                "detail_json": None, "significance": 3,
            })

    # --- Fix #10: get_facts_for_section include_inactive ---

    def test_get_facts_for_section_include_inactive(self):
        self.ev.insert_extracted_fact(self._make_fact())
        self.ev.deactivate_facts_for_document(self.doc_id)
        # Default excludes inactive
        active = self.ev.get_facts_for_section(self.section_id)
        self.assertEqual(len(active), 0)
        # include_inactive shows them
        all_facts = self.ev.get_facts_for_section(self.section_id, include_inactive=True)
        self.assertEqual(len(all_facts), 1)

    # --- Fix #11: update_assertion_evidence returns False for missing row ---

    def test_update_assertion_evidence_returns_false_for_nonexistent(self):
        result = self.ev.update_assertion_evidence(9999, 9999, relationship="supports")
        self.assertFalse(result)

    def test_update_assertion_evidence_returns_true_on_success(self):
        fact_id = self.ev.insert_extracted_fact(self._make_fact())
        a_id = self.ev.insert_assertion(self._make_assertion())
        self.ev.insert_assertion_evidence({
            "assertion_id": a_id, "extracted_fact_id": fact_id,
            "relationship": "supports", "match_score": 0.5,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        result = self.ev.update_assertion_evidence(
            a_id, fact_id,
            match_score=0.95,
            verification_detail_json={"method": "exact_match", "score": 0.95},
        )
        self.assertTrue(result)
        # Verify the update applied
        evidence = self.ev.get_evidence_for_assertion(a_id)
        self.assertAlmostEqual(evidence[0]["match_score"], 0.95)
        self.assertIsInstance(evidence[0]["verification_detail_json"], dict)

    # --- Fix #12 (from optional): confidence=None tests SQL NOT NULL ---

    def test_confidence_null_raises_on_not_null_constraint(self):
        """confidence=None should trigger SQL NOT NULL violation.

        The code wraps IntegrityError as DuplicateEntryError (a known
        convention issue — see review #6), but the underlying cause
        is the NOT NULL constraint, verified via __cause__.
        """
        fact = self._make_fact(fact_key="null_conf", confidence=None)
        import sqlite3
        with self.assertRaises(DuplicateEntryError) as ctx:
            self.ev.insert_extracted_fact(fact)
        self.assertIsInstance(ctx.exception.__cause__, sqlite3.IntegrityError)
        self.assertIn("NOT NULL", str(ctx.exception.__cause__))


class TestPhase2Fixes(unittest.TestCase):
    """Tests for Phase 2 bug fixes: scoped deactivation, deletion, extraction_method filter."""

    def setUp(self):
        self.db = _make_db()
        self.ev = EvidenceDB(self.db)
        self.doc_id = self.ev.insert_source_document({
            "ticker": "V", "doc_type": "10-K", "filing_date": "2025-11-01",
            "period_end": "2025-09-30", "accession_number": "acc1",
            "source_url": "", "local_path": "x", "content_hash": "h",
            "section_count": 1, "fetched_at": "2026-03-20T10:00:00",
        })
        self.section_id = self.ev.insert_document_section({
            "source_document_id": self.doc_id, "section_key": "mda",
            "section_title": "MD&A", "section_order": 1,
            "content_text": "Revenue grew 11%", "content_hash": "h1",
            "token_estimate": 20,
        })

    def tearDown(self):
        self.db._conn.close()

    def _make_fact(self, **overrides):
        fact = {
            "ticker": "V", "source_document_id": self.doc_id,
            "document_section_id": self.section_id, "fact_type": "metric",
            "fact_key": "revenue", "fact_value": "$40B",
            "fact_value_numeric": 40000000000.0, "fact_unit": "USD",
            "fiscal_period": "FY2025", "confidence": 1.0,
            "extraction_method": "xbrl", "source_quote": "Revenue: $40B",
            "source_char_offset_start": 0, "source_char_offset_end": 14,
            "computation_trace_json": None, "extraction_run_id": "run-xbrl",
            "is_active": 1,
        }
        fact.update(overrides)
        return fact

    def _make_assertion(self, **overrides):
        a = {
            "ticker": "V",
            "report_path": "runs/week12/reports/V/FINAL-REPORT.md",
            "umbrella_number": 4, "assertion_text": "Revenue was $40B",
            "assertion_type": "quantitative", "category": "economics",
            "requires_arithmetic": 0,
        }
        a.update(overrides)
        return a

    # --- deactivate_llm_facts_for_document ---

    def test_deactivate_llm_preserves_xbrl(self):
        """Deactivating LLM facts should not touch XBRL facts."""
        self.ev.insert_extracted_fact(self._make_fact(
            fact_key="revenue", extraction_method="xbrl", confidence=1.0,
        ))
        self.ev.insert_extracted_fact(self._make_fact(
            fact_key="mda.revenue_growth", extraction_method="llm_structured",
            confidence=0.85,
        ))
        deactivated = self.ev.deactivate_llm_facts_for_document(self.doc_id)
        self.assertEqual(deactivated, 1)
        active = self.ev.get_facts_for_ticker("V")
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["extraction_method"], "xbrl")

    # --- delete_inactive_llm_facts ---

    def test_delete_clears_unique_space_for_reinsertion(self):
        """After deactivate+delete, reinserting with same keys should succeed."""
        self.ev.insert_extracted_fact(self._make_fact(
            fact_key="mda.revenue_growth", extraction_method="llm_structured",
            confidence=0.85, extraction_run_id="run-1",
        ))
        self.ev.deactivate_llm_facts_for_document(self.doc_id)
        deleted = self.ev.delete_inactive_llm_facts(self.doc_id)
        self.assertEqual(deleted, 1)
        # Re-insert with same key should succeed
        new_id = self.ev.insert_extracted_fact(self._make_fact(
            fact_key="mda.revenue_growth", extraction_method="llm_structured",
            confidence=0.88, extraction_run_id="run-2",
        ))
        self.assertIsNotNone(new_id)

    def test_delete_preserves_evidence_linked_facts(self):
        """Facts with assertion_evidence links survive deletion."""
        fact_id = self.ev.insert_extracted_fact(self._make_fact(
            fact_key="mda.revenue_growth", extraction_method="llm_structured",
            confidence=0.85,
        ))
        a_id = self.ev.insert_assertion(self._make_assertion())
        self.ev.insert_assertion_evidence({
            "assertion_id": a_id, "extracted_fact_id": fact_id,
            "relationship": "supports", "match_score": 0.9,
            "verification_method": "test", "verification_detail_json": None,
            "verified_at": None,
        })
        self.ev.deactivate_llm_facts_for_document(self.doc_id)
        deleted = self.ev.delete_inactive_llm_facts(self.doc_id)
        self.assertEqual(deleted, 0)  # linked fact survives
        all_facts = self.ev.get_facts_for_ticker("V", include_inactive=True)
        self.assertEqual(len(all_facts), 1)
        self.assertEqual(all_facts[0]["is_active"], 0)

    # --- get_facts_for_ticker extraction_method filter ---

    def test_extraction_method_filter(self):
        """Filter facts by extraction_method."""
        self.ev.insert_extracted_fact(self._make_fact(
            fact_key="revenue", extraction_method="xbrl", confidence=1.0,
        ))
        self.ev.insert_extracted_fact(self._make_fact(
            fact_key="mda.revenue_growth", extraction_method="llm_structured",
            confidence=0.85,
        ))
        xbrl = self.ev.get_facts_for_ticker("V", extraction_method="xbrl")
        self.assertEqual(len(xbrl), 1)
        self.assertEqual(xbrl[0]["fact_key"], "revenue")

        llm = self.ev.get_facts_for_ticker("V", extraction_method="llm_structured")
        self.assertEqual(len(llm), 1)
        self.assertEqual(llm[0]["fact_key"], "mda.revenue_growth")

        all_facts = self.ev.get_facts_for_ticker("V")
        self.assertEqual(len(all_facts), 2)


if __name__ == "__main__":
    unittest.main()
