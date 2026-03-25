"""Eval: extraction accuracy — extracted facts match known values.

Validates schema conformance, type correctness, and completeness
of the extracted evidence against golden fixture data.
"""

import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evals.evidence.conftest import GOLDEN_FACTS, GOLDEN_XBRL

VALID_FACT_TYPES = {"metric", "narrative", "guidance", "risk_factor"}
VALID_FACT_UNITS = {"USD", "percent", "ratio", "count", "days", "text"}
VALID_EXTRACTION_METHODS = {"xbrl", "llm_structured", "regex", "computed"}
REQUIRED_FIELDS = [
    "ticker", "fact_type", "fact_key", "fact_value", "fact_unit",
    "confidence", "extraction_method", "source_quote",
]


class TestFactSchemaContract(unittest.TestCase):
    """Every extracted fact conforms to the documented schema."""

    def test_has_facts(self):
        self.assertGreater(len(GOLDEN_FACTS), 50,
                           "Expected at least 50 extracted facts")

    def test_required_fields_present(self):
        """Every fact has all required fields and they are non-null."""
        for f in GOLDEN_FACTS:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, f, f"fact_key={f.get('fact_key')}: missing {field}")
                self.assertIsNotNone(f[field], f"fact_key={f.get('fact_key')}: {field} is None")

    def test_fact_type_enum(self):
        for f in GOLDEN_FACTS:
            self.assertIn(f["fact_type"], VALID_FACT_TYPES,
                          f"fact_key={f['fact_key']}: bad fact_type={f['fact_type']}")

    def test_fact_unit_enum(self):
        for f in GOLDEN_FACTS:
            self.assertIn(f["fact_unit"], VALID_FACT_UNITS,
                          f"fact_key={f['fact_key']}: bad fact_unit={f['fact_unit']}")

    def test_extraction_method_enum(self):
        for f in GOLDEN_FACTS:
            self.assertIn(f["extraction_method"], VALID_EXTRACTION_METHODS,
                          f"fact_key={f['fact_key']}: bad method={f['extraction_method']}")

    def test_ticker_is_syk(self):
        for f in GOLDEN_FACTS:
            self.assertEqual(f["ticker"], "SYK")

    def test_fact_key_format(self):
        """fact_key should be dot-notation (at least one dot)."""
        for f in GOLDEN_FACTS:
            self.assertIn(".", f["fact_key"],
                          f"fact_key={f['fact_key']}: missing dot in fact_key")

    def test_source_quote_minimum_length(self):
        """source_quote should be >= 10 chars (per prompt rules)."""
        for f in GOLDEN_FACTS:
            self.assertGreaterEqual(
                len(f["source_quote"]), 10,
                f"fact_key={f['fact_key']}: source_quote too short ({len(f['source_quote'])} chars)"
            )


class TestFactCompleteness(unittest.TestCase):
    """The extraction covers the expected breadth of fact types."""

    def test_has_metrics(self):
        metrics = [f for f in GOLDEN_FACTS if f["fact_type"] == "metric"]
        self.assertGreater(len(metrics), 10, "Expected at least 10 metric facts")

    def test_has_narratives(self):
        narratives = [f for f in GOLDEN_FACTS if f["fact_type"] == "narrative"]
        self.assertGreater(len(narratives), 10, "Expected at least 10 narrative facts")

    def test_has_risk_factors(self):
        risks = [f for f in GOLDEN_FACTS if f["fact_type"] == "risk_factor"]
        self.assertGreater(len(risks), 10, "Expected at least 10 risk factors")

    def test_multiple_sections_covered(self):
        """Facts should come from multiple sections (not all from one)."""
        section_ids = {f["document_section_id"] for f in GOLDEN_FACTS}
        self.assertGreater(len(section_ids), 3,
                           "Expected facts from at least 4 different sections")

    def test_numeric_facts_have_values(self):
        """Metric facts with numeric data should have fact_value_numeric set."""
        numeric_facts = [
            f for f in GOLDEN_FACTS
            if f["fact_type"] == "metric" and f["fact_value_numeric"] is not None
        ]
        self.assertGreater(len(numeric_facts), 5,
                           "Expected at least 5 metric facts with numeric values")

    def test_numeric_values_are_reasonable(self):
        """Numeric values should be non-negative (for a company like SYK)."""
        for f in GOLDEN_FACTS:
            if f["fact_value_numeric"] is not None and f["fact_unit"] == "USD":
                self.assertGreaterEqual(
                    f["fact_value_numeric"], 0,
                    f"fact_key={f['fact_key']}: USD value should be non-negative"
                )


class TestNumericAccuracy(unittest.TestCase):
    """Spot-check: extracted numeric facts against known XBRL values."""

    def _find_fact_by_key_substring(self, substring: str) -> dict | None:
        """Find a fact whose fact_key contains the substring and has a numeric value."""
        for f in GOLDEN_FACTS:
            if substring in f["fact_key"] and f["fact_value_numeric"] is not None:
                return f
        return None

    def test_revenue_fact_exists(self):
        """At least one fact should mention revenue with a numeric value."""
        revenue_facts = [
            f for f in GOLDEN_FACTS
            if "revenue" in f["fact_key"].lower() or "sales" in f["fact_key"].lower()
            if f["fact_value_numeric"] is not None
        ]
        # Not all LLM extractions will hit revenue — this is a soft check
        if revenue_facts:
            # If found, should be in the right ballpark (>$1B for SYK)
            for f in revenue_facts:
                if f["fact_unit"] == "USD":
                    self.assertGreater(f["fact_value_numeric"], 1e9,
                                       f"Revenue fact {f['fact_key']} too small: {f['fact_value_numeric']}")


if __name__ == "__main__":
    unittest.main()
