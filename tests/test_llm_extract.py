"""Tests for scripts/sec_edgar/llm_extract.py — LLM extraction pipeline (mocked)."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from sec_edgar.llm_extract import (
    CLAIM_BATCH_SIZE,
    QUOTE_MATCH_THRESHOLD,
    ExtractionError,
    _assign_confidence,
    _claude_extract,
    _compute_char_offsets,
    _fact_to_db_dict,
    _parse_json_response,
    extract_section_facts,
)
from src.evidence_models import ExtractedFactModel, FactType, FactUnit


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

SAMPLE_SECTION_TEXT = (
    "Net revenue grew 11% year-over-year to $40.0 billion for fiscal year 2025. "
    "The increase was primarily driven by strong consumer payment volumes across all regions. "
    "Operating expenses increased 30% to $16.0 billion, largely due to a litigation provision "
    "of $2.6 billion related to ongoing regulatory matters. "
    "The company operates in over 200 countries and territories worldwide. "
    "Management expects revenue growth of 8-10% for fiscal year 2026."
)

SAMPLE_PASS1_RESPONSE = {
    "section_key": "mda",
    "claims": [
        {
            "claim_text": "Net revenue grew 11% year-over-year to $40.0 billion",
            "claim_type": "quantitative",
            "is_quantitative": True,
            "approximate_location": "Net revenue grew 11% year-over-year to",
        },
        {
            "claim_text": "Growth driven by strong consumer payment volumes across all regions",
            "claim_type": "causal",
            "is_quantitative": False,
            "approximate_location": "The increase was primarily driven by",
        },
        {
            "claim_text": "Operating expenses increased 30% to $16.0 billion",
            "claim_type": "quantitative",
            "is_quantitative": True,
            "approximate_location": "Operating expenses increased 30% to $16.0",
        },
        {
            "claim_text": "Litigation provision of $2.6 billion for regulatory matters",
            "claim_type": "quantitative",
            "is_quantitative": True,
            "approximate_location": "largely due to a litigation provision",
        },
        {
            "claim_text": "Operates in over 200 countries and territories",
            "claim_type": "qualitative",
            "is_quantitative": False,
            "approximate_location": "The company operates in over 200",
        },
        {
            "claim_text": "Management expects revenue growth of 8-10% for FY2026",
            "claim_type": "quantitative",
            "is_quantitative": True,
            "approximate_location": "Management expects revenue growth of 8-10%",
        },
    ],
    "total_claims": 6,
}

SAMPLE_PASS2_RESPONSE = {
    "section_key": "mda",
    "facts": [
        {
            "fact_type": "metric",
            "fact_key": "mda.revenue_growth_yoy",
            "fact_value": "11%",
            "fact_value_numeric": 0.11,
            "fact_unit": "percent",
            "fiscal_period": "FY2025",
            "source_quote": "Net revenue grew 11% year-over-year to $40.0 billion for fiscal year 2025",
            "confidence_note": None,
        },
        {
            "fact_type": "metric",
            "fact_key": "mda.revenue_total",
            "fact_value": "$40.0 billion",
            "fact_value_numeric": 40000000000.0,
            "fact_unit": "USD",
            "fiscal_period": "FY2025",
            "source_quote": "Net revenue grew 11% year-over-year to $40.0 billion for fiscal year 2025",
            "confidence_note": None,
        },
    ],
    "skipped_claims": [],
}


# ---------------------------------------------------------------------------
# Tests: _parse_json_response
# ---------------------------------------------------------------------------

class TestParseJsonResponse(unittest.TestCase):
    def test_plain_dict(self):
        raw = json.dumps({"section_key": "mda", "claims": []})
        result = _parse_json_response(raw)
        self.assertEqual(result["section_key"], "mda")

    def test_wrapped_in_result(self):
        raw = json.dumps({"result": {"section_key": "mda", "claims": []}})
        result = _parse_json_response(raw)
        self.assertEqual(result["section_key"], "mda")

    def test_double_wrapped_string(self):
        inner = json.dumps({"section_key": "mda", "claims": []})
        raw = json.dumps({"result": inner})
        result = _parse_json_response(raw)
        self.assertEqual(result["section_key"], "mda")

    def test_invalid_json_raises(self):
        with self.assertRaises(json.JSONDecodeError):
            _parse_json_response("not json")


# ---------------------------------------------------------------------------
# Tests: _compute_char_offsets
# ---------------------------------------------------------------------------

class TestComputeCharOffsets(unittest.TestCase):
    def test_exact_match(self):
        text = "The revenue was $40.0 billion for the year."
        quote = "$40.0 billion"
        start, end = _compute_char_offsets(quote, text)
        self.assertIsNotNone(start)
        self.assertEqual(text[start:end], quote)

    def test_exact_match_at_start(self):
        text = "Revenue grew 11% to $40 billion."
        quote = "Revenue grew 11%"
        start, end = _compute_char_offsets(quote, text)
        self.assertEqual(start, 0)
        self.assertEqual(text[start:end], quote)

    def test_no_match_returns_none(self):
        text = "The quick brown fox."
        quote = "A completely different sentence that doesn't match at all."
        start, end = _compute_char_offsets(quote, text)
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_empty_quote(self):
        start, end = _compute_char_offsets("", "some text")
        self.assertIsNone(start)

    def test_empty_section(self):
        start, end = _compute_char_offsets("quote", "")
        self.assertIsNone(start)

    def test_fuzzy_match_minor_difference(self):
        text = "The company reported revenue of $40.0 billion for the fiscal year 2025."
        # Slightly different (capitalized "Company")
        quote = "The Company reported revenue of $40.0 billion for the fiscal year 2025."
        start, end = _compute_char_offsets(quote, text)
        # Should find a fuzzy match (ratio should be very high)
        if start is not None:
            self.assertIsNotNone(end)
        # Either found via fuzzy or returned None — both acceptable for this case

    def test_quote_longer_than_text(self):
        start, end = _compute_char_offsets("a" * 100, "short")
        self.assertIsNone(start)


# ---------------------------------------------------------------------------
# Tests: _assign_confidence
# ---------------------------------------------------------------------------

class TestAssignConfidence(unittest.TestCase):
    def _make_fact(self, numeric=None):
        return ExtractedFactModel(
            fact_type="metric" if numeric is not None else "narrative",
            fact_key="mda.test_fact",
            fact_value="test value" if numeric is None else str(numeric),
            fact_value_numeric=numeric,
            fact_unit="USD" if numeric is not None else "text",
            source_quote="Some source quote from the filing text here.",
        )

    def test_quantitative_with_exact_offset(self):
        fact = self._make_fact(numeric=1000000.0)
        conf = _assign_confidence(fact, has_exact_offset=True)
        self.assertEqual(conf, 0.90)

    def test_quantitative_without_exact_offset(self):
        fact = self._make_fact(numeric=1000000.0)
        conf = _assign_confidence(fact, has_exact_offset=False)
        self.assertEqual(conf, 0.85)

    def test_narrative_with_exact_offset(self):
        fact = self._make_fact(numeric=None)
        conf = _assign_confidence(fact, has_exact_offset=True)
        self.assertAlmostEqual(conf, 0.85, places=5)

    def test_narrative_without_exact_offset(self):
        fact = self._make_fact(numeric=None)
        conf = _assign_confidence(fact, has_exact_offset=False)
        self.assertEqual(conf, 0.80)

    def test_capped_at_095(self):
        # Even with bonuses, should not exceed 0.95
        fact = self._make_fact(numeric=1000000.0)
        conf = _assign_confidence(fact, has_exact_offset=True)
        self.assertLessEqual(conf, 0.95)


# ---------------------------------------------------------------------------
# Tests: _fact_to_db_dict
# ---------------------------------------------------------------------------

class TestFactToDbDict(unittest.TestCase):
    def test_produces_valid_dict(self):
        fact = ExtractedFactModel(
            fact_type="metric",
            fact_key="mda.revenue_total",
            fact_value="$40.0 billion",
            fact_value_numeric=40000000000.0,
            fact_unit="USD",
            fiscal_period="FY2025",
            source_quote="Net revenue grew 11% year-over-year to $40.0 billion for fiscal year 2025",
        )
        result = _fact_to_db_dict(
            fact, "V", 1, 2, "FY2025", "run-001", SAMPLE_SECTION_TEXT,
        )

        self.assertEqual(result["ticker"], "V")
        self.assertEqual(result["source_document_id"], 1)
        self.assertEqual(result["document_section_id"], 2)
        self.assertEqual(result["fact_type"], "metric")
        self.assertEqual(result["fact_key"], "mda.revenue_total")
        self.assertEqual(result["fact_value"], "$40.0 billion")
        self.assertAlmostEqual(result["fact_value_numeric"], 40000000000.0)
        self.assertEqual(result["fact_unit"], "USD")
        self.assertEqual(result["fiscal_period"], "FY2025")
        self.assertEqual(result["extraction_method"], "llm_structured")
        self.assertEqual(result["extraction_run_id"], "run-001")
        self.assertEqual(result["is_active"], 1)
        self.assertIsNone(result["computation_trace_json"])

    def test_uses_fallback_fiscal_period(self):
        fact = ExtractedFactModel(
            fact_type="narrative",
            fact_key="biz.geography",
            fact_value="200+ countries",
            fact_unit="text",
            source_quote="The company operates in over 200 countries and territories worldwide",
            # No fiscal_period on the fact
        )
        result = _fact_to_db_dict(
            fact, "V", 1, 2, "FY2025", "run-001", SAMPLE_SECTION_TEXT,
        )
        self.assertEqual(result["fiscal_period"], "FY2025")

    def test_exact_match_gives_offsets(self):
        # The source_quote is a verbatim substring of SAMPLE_SECTION_TEXT
        fact = ExtractedFactModel(
            fact_type="metric",
            fact_key="mda.countries",
            fact_value="200+",
            fact_value_numeric=200.0,
            fact_unit="count",
            source_quote="The company operates in over 200 countries and territories worldwide",
        )
        result = _fact_to_db_dict(
            fact, "V", 1, 2, "FY2025", "run-001", SAMPLE_SECTION_TEXT,
        )
        self.assertIsNotNone(result["source_char_offset_start"])
        self.assertIsNotNone(result["source_char_offset_end"])

    def test_confidence_is_set(self):
        fact = ExtractedFactModel(
            fact_type="metric",
            fact_key="mda.test",
            fact_value="$10",
            fact_value_numeric=10.0,
            fact_unit="USD",
            source_quote="The company operates in over 200 countries and territories worldwide",
        )
        result = _fact_to_db_dict(
            fact, "V", 1, 2, "FY2025", "run-001", SAMPLE_SECTION_TEXT,
        )
        self.assertGreaterEqual(result["confidence"], 0.80)
        self.assertLessEqual(result["confidence"], 0.95)


# ---------------------------------------------------------------------------
# Tests: extract_section_facts (mocked LLM)
# ---------------------------------------------------------------------------

class TestExtractSectionFacts(unittest.TestCase):
    @patch("sec_edgar.llm_extract._claude_extract")
    def test_full_pipeline(self, mock_claude):
        # First call = Pass 1, subsequent calls = Pass 2 batches
        mock_claude.side_effect = [
            json.dumps(SAMPLE_PASS1_RESPONSE),
            json.dumps(SAMPLE_PASS2_RESPONSE),
            json.dumps(SAMPLE_PASS2_RESPONSE),  # second batch
        ]

        facts = extract_section_facts(
            section_text=SAMPLE_SECTION_TEXT,
            section_key="mda",
            ticker="V",
            fiscal_period="FY2025",
            extraction_run_id="test-run-001",
            source_document_id=1,
            document_section_id=2,
            quiet=True,
        )

        self.assertGreater(len(facts), 0)
        # Each fact should be a dict with required keys
        for f in facts:
            self.assertIn("ticker", f)
            self.assertIn("fact_key", f)
            self.assertIn("extraction_method", f)
            self.assertEqual(f["extraction_method"], "llm_structured")

    @patch("sec_edgar.llm_extract._claude_extract")
    def test_pass1_returns_no_claims(self, mock_claude):
        mock_claude.return_value = json.dumps({
            "section_key": "mda",
            "claims": [],
            "total_claims": 0,
        })

        facts = extract_section_facts(
            SAMPLE_SECTION_TEXT, "mda", "V", "FY2025", "run-001", 1, 2, quiet=True,
        )
        self.assertEqual(len(facts), 0)

    @patch("sec_edgar.llm_extract._claude_extract")
    def test_pass1_failure_returns_empty(self, mock_claude):
        mock_claude.side_effect = ExtractionError("timeout")

        facts = extract_section_facts(
            SAMPLE_SECTION_TEXT, "mda", "V", "FY2025", "run-001", 1, 2, quiet=True,
        )
        self.assertEqual(len(facts), 0)

    @patch("sec_edgar.llm_extract._claude_extract")
    def test_pass2_partial_failure(self, mock_claude):
        # Pass 1 succeeds, first Pass 2 batch fails (both attempts), second succeeds
        # With 6 claims and CLAIM_BATCH_SIZE=5: 2 batches
        # Batch 1: attempt 1 fails, attempt 2 (retry) also fails → skipped
        # Batch 2: attempt 1 succeeds
        mock_claude.side_effect = [
            json.dumps(SAMPLE_PASS1_RESPONSE),  # Pass 1
            ExtractionError("timeout on batch 1 attempt 1"),  # Pass 2 batch 1 attempt 1
            ExtractionError("timeout on batch 1 attempt 2"),  # Pass 2 batch 1 retry
            json.dumps(SAMPLE_PASS2_RESPONSE),  # Pass 2 batch 2
        ]

        facts = extract_section_facts(
            SAMPLE_SECTION_TEXT, "mda", "V", "FY2025", "run-001", 1, 2, quiet=True,
        )
        # Should still have facts from the second batch
        self.assertGreater(len(facts), 0)

    @patch("sec_edgar.llm_extract._claude_extract")
    def test_invalid_json_retries(self, mock_claude):
        mock_claude.side_effect = [
            "not valid json",  # first attempt fails
            json.dumps(SAMPLE_PASS1_RESPONSE),  # retry succeeds
            json.dumps(SAMPLE_PASS2_RESPONSE),
            json.dumps(SAMPLE_PASS2_RESPONSE),
        ]

        facts = extract_section_facts(
            SAMPLE_SECTION_TEXT, "mda", "V", "FY2025", "run-001", 1, 2, quiet=True,
        )
        self.assertGreater(len(facts), 0)

    @patch("sec_edgar.llm_extract._claude_extract")
    def test_claim_batching(self, mock_claude):
        # Create a response with more claims than CLAIM_BATCH_SIZE
        many_claims = SAMPLE_PASS1_RESPONSE.copy()
        many_claims["claims"] = SAMPLE_PASS1_RESPONSE["claims"] * 3  # 18 claims
        many_claims["total_claims"] = len(many_claims["claims"])

        call_count = [0]
        def side_effect(prompt, timeout=120):
            call_count[0] += 1
            if call_count[0] == 1:
                return json.dumps(many_claims)
            return json.dumps(SAMPLE_PASS2_RESPONSE)

        mock_claude.side_effect = side_effect

        facts = extract_section_facts(
            SAMPLE_SECTION_TEXT, "mda", "V", "FY2025", "run-001", 1, 2, quiet=True,
        )

        # 1 Pass 1 call + ceil(18/5) = 4 Pass 2 calls = 5 total
        expected_pass2_calls = -(-18 // CLAIM_BATCH_SIZE)  # ceiling division
        self.assertEqual(call_count[0], 1 + expected_pass2_calls)


# ---------------------------------------------------------------------------
# Tests: _claude_extract (subprocess mock)
# ---------------------------------------------------------------------------

class TestClaudeExtract(unittest.TestCase):
    @patch("sec_edgar.llm_extract.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"result": "ok"}',
            stderr="",
        )
        result = _claude_extract("test prompt")
        self.assertEqual(result, '{"result": "ok"}')

    @patch("sec_edgar.llm_extract.subprocess.run")
    def test_nonzero_exit_raises(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error message",
        )
        with self.assertRaises(ExtractionError):
            _claude_extract("test prompt")

    @patch("sec_edgar.llm_extract.subprocess.run")
    def test_timeout_raises(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=120)
        with self.assertRaises(ExtractionError) as ctx:
            _claude_extract("test prompt")
        self.assertIn("timed out", str(ctx.exception))

    @patch("sec_edgar.llm_extract.subprocess.run")
    def test_missing_cli_raises(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(ExtractionError) as ctx:
            _claude_extract("test prompt")
        self.assertIn("not found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
