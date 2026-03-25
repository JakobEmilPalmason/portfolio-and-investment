"""Tests for Phase 4 fact checker (Pass B)."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.sec_edgar.fact_checker import (
    _extract_number,
    _numeric_cross_check,
    _build_candidate_facts,
    _evidence_to_db_dict,
)


class TestExtractNumber(unittest.TestCase):
    def test_dollar_billions(self):
        self.assertAlmostEqual(_extract_number("Revenue of $25.1B"), 25.1e9)
        self.assertAlmostEqual(_extract_number("$4.3 billion in FCF"), 4.3e9)

    def test_dollar_millions(self):
        self.assertAlmostEqual(_extract_number("CapEx of $761M"), 761e6)

    def test_percentage(self):
        self.assertAlmostEqual(_extract_number("Margins at 63%"), 0.63)
        self.assertAlmostEqual(_extract_number("~11% growth rate"), 0.11)

    def test_plain_dollar(self):
        result = _extract_number("Stock at $312.50")
        self.assertAlmostEqual(result, 312.50)

    def test_no_number(self):
        self.assertIsNone(_extract_number("Strong competitive moat"))


class TestNumericCrossCheck(unittest.TestCase):
    def test_exact_match(self):
        result = _numeric_cross_check("Revenue of $25.1B", 25.1e9)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "supports")
        self.assertEqual(result[1], 0.95)

    def test_within_2_percent(self):
        # 25.1B assertion, 25.5B fact = ~1.6% diff
        result = _numeric_cross_check("Revenue of $25.1B", 25.5e9)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "supports")
        self.assertEqual(result[1], 0.95)

    def test_within_5_percent(self):
        # 25.1B assertion, 26.3B fact = ~4.8% diff
        result = _numeric_cross_check("Revenue of $25.1B", 26.3e9)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "supports")
        self.assertEqual(result[1], 0.85)

    def test_within_10_percent(self):
        # 25.1B assertion, 27.5B fact = ~9.6% diff
        result = _numeric_cross_check("Revenue of $25.1B", 27.5e9)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "partial")
        self.assertEqual(result[1], 0.70)

    def test_beyond_10_percent(self):
        # 25.1B assertion, 30B fact = ~19.5% diff
        result = _numeric_cross_check("Revenue of $25.1B", 30e9)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "contradicts")
        self.assertEqual(result[1], 0.30)

    def test_no_number_in_assertion(self):
        result = _numeric_cross_check("Strong business moat", 25e9)
        self.assertIsNone(result)

    def test_none_fact_value(self):
        result = _numeric_cross_check("Revenue of $25.1B", None)
        self.assertIsNone(result)


class TestBuildCandidateFacts(unittest.TestCase):
    def setUp(self):
        self.facts = [
            {"id": 1, "fact_key": "mda.revenue", "fact_value": "$25.1B",
             "fact_value_numeric": 25.1e9, "confidence": 1.0, "assertion_type": "quantitative"},
            {"id": 2, "fact_key": "mda.gross_margin", "fact_value": "63.5%",
             "fact_value_numeric": 0.635, "confidence": 0.9, "assertion_type": "quantitative"},
            {"id": 3, "fact_key": "risk.competition", "fact_value": "Intense competition",
             "fact_value_numeric": None, "confidence": 0.85, "assertion_type": "qualitative"},
            {"id": 4, "fact_key": "biz.employees", "fact_value": "51,000",
             "fact_value_numeric": 51000, "confidence": 0.8, "assertion_type": "quantitative"},
        ]

    def test_returns_relevant_facts(self):
        assertion = {"assertion_text": "Revenue of $25.1B in FY2025", "assertion_type": "quantitative"}
        candidates = _build_candidate_facts(assertion, self.facts)
        self.assertGreater(len(candidates), 0)

    def test_capped_at_max(self):
        # Create many facts
        many_facts = [
            {"id": i, "fact_key": f"mda.metric_{i}", "fact_value": f"${i}M",
             "fact_value_numeric": i * 1e6, "confidence": 0.9}
            for i in range(50)
        ]
        assertion = {"assertion_text": "Revenue metric analysis across multiple periods", "assertion_type": "quantitative"}
        candidates = _build_candidate_facts(assertion, many_facts)
        self.assertLessEqual(len(candidates), 20)

    def test_empty_facts(self):
        assertion = {"assertion_text": "Revenue of $25.1B", "assertion_type": "quantitative"}
        candidates = _build_candidate_facts(assertion, [])
        self.assertEqual(candidates, [])


class TestEvidenceToDbDict(unittest.TestCase):
    def test_produces_valid_dict(self):
        result = _evidence_to_db_dict(
            assertion_id=1,
            relationship="supports",
            match_score=0.95,
            fact_id=42,
            verification_method="numeric_exact",
            reasoning="Numbers match within 2%",
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["assertion_id"], 1)
        self.assertEqual(result["extracted_fact_id"], 42)
        self.assertEqual(result["relationship"], "supports")
        self.assertEqual(result["match_score"], 0.95)
        self.assertEqual(result["verification_method"], "numeric_exact")
        self.assertIn("verified_at", result)

    def test_returns_none_for_no_fact(self):
        """Unverifiable assertions with no fact_id should not create evidence rows."""
        result = _evidence_to_db_dict(
            assertion_id=1,
            relationship="unverifiable",
            match_score=0.0,
            fact_id=None,
            verification_method="no_evidence",
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
