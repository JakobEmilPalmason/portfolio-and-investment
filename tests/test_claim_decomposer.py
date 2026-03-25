"""Tests for Phase 4 claim decomposer (Pass A)."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.sec_edgar.claim_decomposer import (
    _parse_key_findings,
    _parse_red_flags,
    _infer_type,
    _deduplicate,
    _extract_detailed_analysis,
    decompose_section,
    _assertion_to_db_dict,
)


SAMPLE_SECTION = """# Business Economics — SYK

**Analyst Role:** Financial Analyst
**Date:** 2026-03-17

## Key Findings

| # | Finding | Significance (1-5) |
|---|---------|-------------------|
| 1 | Revenue compounded at ~11% annually from $18.4B (FY22) to $25.1B (FY25) | 5 |
| 2 | Gross margins stable at 63-64% across four years | 5 |
| 3 | FCF reached $4.3B in FY25 (17.1% margin) with exceptional 132% FCF-to-net-income conversion | 5 |
| 4 | ROIC of 10.0% in FY25 (down from 12.2% in FY24) reflects acquisition dilution | 4 |

## Detailed Analysis

Stryker's revenue trajectory is among the most consistent in large-cap medtech. The company grew from $18.4B in FY2022 to $25.1B in FY2025, a compound annual growth rate of approximately 10.9%.

The margin structure reflects a premium medtech franchise. Gross margins have held between 63% and 64% for four consecutive years.

## Signal Summary
- **Bull case:** Durable double-digit compounder with 64% gross margins.
- **Bear case:** ROIC of 10% is mediocre for a premium medtech multiple.

## Red Flags
- ROIC declining from 12.2% to 10.0% due to Inari acquisition goodwill
- Interest expense jumped 48% YoY ($409M to $607M)

## Score: 7 / 10
Strong cash generation but ROIC below exceptional threshold.
"""


class TestParseKeyFindings(unittest.TestCase):
    def test_extracts_all_rows(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        self.assertEqual(len(findings), 4)

    def test_skips_header_and_separator(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        # All assertions should have meaningful text, not "Finding" or "---"
        for f in findings:
            self.assertGreater(len(f["assertion_text"]), 20)
            self.assertNotIn("---", f["assertion_text"])

    def test_finding_content(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        self.assertIn("Revenue compounded", findings[0]["assertion_text"])
        self.assertIn("Gross margins", findings[1]["assertion_text"])

    def test_category_is_finding(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        for f in findings:
            self.assertEqual(f["category"], "finding")

    def test_source_location_format(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        self.assertEqual(findings[0]["source_location"], "key_findings:1")
        self.assertEqual(findings[3]["source_location"], "key_findings:4")

    def test_requires_arithmetic_flagged_for_roic(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        roic_finding = findings[3]  # "ROIC of 10.0%..."
        self.assertTrue(roic_finding["requires_arithmetic"])

    def test_requires_arithmetic_false_for_raw_numbers(self):
        findings = _parse_key_findings(SAMPLE_SECTION, 4)
        revenue_finding = findings[0]  # "Revenue compounded..."
        self.assertFalse(revenue_finding["requires_arithmetic"])

    def test_empty_section(self):
        findings = _parse_key_findings("No table here", 1)
        self.assertEqual(findings, [])


class TestParseRedFlags(unittest.TestCase):
    def test_extracts_bullets(self):
        flags = _parse_red_flags(SAMPLE_SECTION, 4)
        self.assertEqual(len(flags), 2)

    def test_category_is_red_flag(self):
        flags = _parse_red_flags(SAMPLE_SECTION, 4)
        for f in flags:
            self.assertEqual(f["category"], "red_flag")

    def test_source_location(self):
        flags = _parse_red_flags(SAMPLE_SECTION, 4)
        self.assertEqual(flags[0]["source_location"], "red_flags:1")
        self.assertEqual(flags[1]["source_location"], "red_flags:2")

    def test_content(self):
        flags = _parse_red_flags(SAMPLE_SECTION, 4)
        self.assertIn("ROIC declining", flags[0]["assertion_text"])
        self.assertIn("Interest expense", flags[1]["assertion_text"])

    def test_no_red_flags_section(self):
        flags = _parse_red_flags("## Key Findings\nSome text", 1)
        self.assertEqual(flags, [])


class TestInferType(unittest.TestCase):
    def test_quantitative(self):
        self.assertEqual(_infer_type("Revenue of $25.1B in FY2025"), "quantitative")
        self.assertEqual(_infer_type("Margins stable at 63%"), "quantitative")

    def test_comparative(self):
        self.assertEqual(_infer_type("Higher than peer average"), "comparative")
        self.assertEqual(_infer_type("Outpaced industry growth"), "comparative")

    def test_causal(self):
        self.assertEqual(_infer_type("Growth driven by acquisitions"), "causal")
        self.assertEqual(_infer_type("Decline due to higher interest"), "causal")

    def test_qualitative(self):
        self.assertEqual(_infer_type("Strong competitive position in medtech"), "qualitative")


class TestExtractDetailedAnalysis(unittest.TestCase):
    def test_extracts_prose(self):
        prose = _extract_detailed_analysis(SAMPLE_SECTION)
        self.assertIn("Stryker's revenue trajectory", prose)
        self.assertIn("margin structure", prose)

    def test_excludes_other_sections(self):
        prose = _extract_detailed_analysis(SAMPLE_SECTION)
        self.assertNotIn("Key Findings", prose)
        self.assertNotIn("Red Flags", prose)
        self.assertNotIn("Score:", prose)


class TestDeduplicate(unittest.TestCase):
    def test_no_llm(self):
        mech = [{"assertion_text": "Revenue was $25B", "assertion_type": "quantitative"}]
        result = _deduplicate(mech, [])
        self.assertEqual(len(result), 1)

    def test_no_mechanical(self):
        llm = [{"assertion_text": "The company has strong moat", "assertion_type": "qualitative"}]
        result = _deduplicate([], llm)
        self.assertEqual(len(result), 1)

    def test_removes_duplicates(self):
        mech = [{"assertion_text": "Revenue compounded at 11% from $18B to $25B", "assertion_type": "quantitative"}]
        llm = [{"assertion_text": "Revenue compounded at 11% from $18B to $25B growth", "assertion_type": "quantitative"}]
        result = _deduplicate(mech, llm)
        # High word overlap → deduplicated
        self.assertEqual(len(result), 1)

    def test_keeps_distinct(self):
        mech = [{"assertion_text": "Revenue was $25.1B in fiscal 2025", "assertion_type": "quantitative"}]
        llm = [{"assertion_text": "ROIC declined to 10% from 12.2% prior year", "assertion_type": "quantitative"}]
        result = _deduplicate(mech, llm)
        self.assertEqual(len(result), 2)


class TestAssertionToDbDict(unittest.TestCase):
    def test_produces_correct_keys(self):
        assertion = {
            "assertion_text": "Revenue of $25.1B in FY2025",
            "assertion_type": "quantitative",
            "category": "finding",
            "requires_arithmetic": False,
            "source_location": "key_findings:1",
        }
        result = _assertion_to_db_dict(assertion, 4, "SYK", "reports/SYK/FINAL-REPORT.md")
        expected_keys = {"ticker", "report_path", "umbrella_number", "assertion_text",
                         "assertion_type", "category", "requires_arithmetic"}
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result["ticker"], "SYK")
        self.assertEqual(result["umbrella_number"], 4)
        self.assertEqual(result["requires_arithmetic"], 0)  # int, not bool

    def test_requires_arithmetic_converts_to_int(self):
        assertion = {
            "assertion_text": "ROIC declined from 12.2% to 10.0%",
            "assertion_type": "quantitative",
            "category": "finding",
            "requires_arithmetic": True,
        }
        result = _assertion_to_db_dict(assertion, 4, "SYK", "path")
        self.assertEqual(result["requires_arithmetic"], 1)


if __name__ == "__main__":
    unittest.main()
