"""Eval: decomposition accuracy — mechanical claim extraction from real SYK reports.

Runs the mechanical parsing functions from claim_decomposer.py on real
SYK umbrella sections and validates the extracted assertions.
"""

import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sec_edgar.claim_decomposer import _parse_key_findings, _parse_red_flags, _infer_type
from evals.evidence.conftest import GOLDEN_ASSERTIONS

REPORT_DIR = REPO_ROOT / "runs" / "week12_16.03" / "reports" / "SYK"


class TestMechanicalExtraction(unittest.TestCase):
    """Parse real SYK report sections with the mechanical extractor."""

    def setUp(self):
        self.sections = {}
        for i in range(1, 9):
            files = list(REPORT_DIR.glob(f"{i:02d}-*.md"))
            if files:
                self.sections[i] = files[0].read_text(encoding="utf-8")

    def test_report_sections_exist(self):
        """All 8 umbrella sections should be available."""
        self.assertEqual(len(self.sections), 8,
                         f"Expected 8 sections, found {len(self.sections)}: {list(self.sections.keys())}")

    def test_key_findings_extraction(self):
        """_parse_key_findings extracts rows from each section's Key Findings table."""
        total_findings = 0
        for umbrella, text in self.sections.items():
            findings = _parse_key_findings(text, umbrella)
            # Each section should have at least 1 finding (most have 3-6)
            self.assertGreater(len(findings), 0,
                               f"Umbrella {umbrella}: no key findings extracted")
            for f in findings:
                self.assertEqual(f["category"], "finding")
                self.assertIn("assertion_text", f)
                self.assertGreater(len(f["assertion_text"]), 10,
                                   f"Umbrella {umbrella}: finding text too short")
            total_findings += len(findings)
        # Should have at least 20 findings across all 8 sections
        self.assertGreater(total_findings, 20,
                           f"Only {total_findings} total key findings across 8 sections")

    def test_red_flags_extraction(self):
        """_parse_red_flags extracts bullets from Red Flags sections."""
        sections_with_flags = 0
        total_flags = 0
        for umbrella, text in self.sections.items():
            flags = _parse_red_flags(text, umbrella)
            if flags:
                sections_with_flags += 1
                for f in flags:
                    self.assertEqual(f["category"], "red_flag")
                    self.assertIn("assertion_text", f)
                total_flags += len(flags)
        # At least some sections should have red flags
        self.assertGreater(sections_with_flags, 0,
                           "No sections had red flags extracted")
        self.assertGreater(total_flags, 0)

    def test_findings_have_correct_source_location(self):
        """Source location should follow 'key_findings:N' pattern."""
        for umbrella, text in self.sections.items():
            findings = _parse_key_findings(text, umbrella)
            for i, f in enumerate(findings):
                self.assertTrue(
                    f["source_location"].startswith("key_findings:"),
                    f"Umbrella {umbrella}: bad source_location={f['source_location']}"
                )


class TestTypeInference(unittest.TestCase):
    """_infer_type correctly classifies assertions from real data."""

    def test_quantitative_detection(self):
        """Assertions with $ amounts or percentages are quantitative."""
        quantitative_texts = [
            a["assertion_text"] for a in GOLDEN_ASSERTIONS
            if "$" in a["assertion_text"] or "%" in a["assertion_text"]
        ]
        if quantitative_texts:
            for text in quantitative_texts[:10]:
                result = _infer_type(text)
                self.assertIn(result, ("quantitative", "comparative"),
                              f"'{text[:50]}...' should be quantitative or comparative, got {result}")

    def test_qualitative_detection(self):
        """Generic assertions without numbers are qualitative or causal."""
        qualitative_texts = [
            a["assertion_text"] for a in GOLDEN_ASSERTIONS
            if "$" not in a["assertion_text"]
            and "%" not in a["assertion_text"]
            and not any(c.isdigit() for c in a["assertion_text"])
        ]
        if qualitative_texts:
            for text in qualitative_texts[:10]:
                result = _infer_type(text)
                self.assertIn(result, ("qualitative", "causal", "comparative"),
                              f"'{text[:50]}...' got unexpected type: {result}")


class TestArithmeticFlagging(unittest.TestCase):
    """requires_arithmetic is correctly set on golden assertions."""

    def test_arithmetic_assertions_exist(self):
        """Some assertions should be flagged as requiring arithmetic."""
        arithmetic = [a for a in GOLDEN_ASSERTIONS if a["requires_arithmetic"]]
        self.assertGreater(len(arithmetic), 0,
                           "No assertions flagged as requires_arithmetic")

    def test_non_arithmetic_assertions_exist(self):
        """Most assertions should NOT require arithmetic."""
        non_arithmetic = [a for a in GOLDEN_ASSERTIONS if not a["requires_arithmetic"]]
        self.assertGreater(len(non_arithmetic), len(GOLDEN_ASSERTIONS) * 0.5,
                           "More than half of assertions require arithmetic — seems wrong")

    def test_all_umbrellas_represented(self):
        """Assertions should cover all 8 umbrella sections."""
        umbrellas = {a["umbrella_number"] for a in GOLDEN_ASSERTIONS}
        for i in range(1, 9):
            self.assertIn(i, umbrellas, f"No assertions for umbrella {i}")


if __name__ == "__main__":
    unittest.main()
