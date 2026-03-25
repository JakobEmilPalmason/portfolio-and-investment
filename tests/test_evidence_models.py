"""Tests for src/evidence_models.py — Pydantic v2 models for evidence extraction."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evidence_models import (
    ClaimList,
    ExtractionBatch,
    ExtractedFactModel,
    FactType,
    FactUnit,
    IdentifiedClaim,
    get_claim_list_schema,
    get_extraction_schema,
)
from pydantic import ValidationError


class TestFactEnums(unittest.TestCase):
    """FactType and FactUnit enum membership."""

    def test_fact_type_members(self):
        self.assertEqual(FactType.metric, "metric")
        self.assertEqual(FactType.narrative, "narrative")
        self.assertEqual(FactType.guidance, "guidance")
        self.assertEqual(FactType.risk_factor, "risk_factor")

    def test_fact_unit_members(self):
        self.assertEqual(FactUnit.usd, "USD")
        self.assertEqual(FactUnit.percent, "percent")
        self.assertEqual(FactUnit.ratio, "ratio")
        self.assertEqual(FactUnit.count, "count")
        self.assertEqual(FactUnit.days, "days")
        self.assertEqual(FactUnit.text, "text")


class TestIdentifiedClaim(unittest.TestCase):
    """Pass 1 model: IdentifiedClaim."""

    def _valid_claim(self, **overrides):
        data = {
            "claim_text": "Revenue grew 11% to $40.0 billion",
            "claim_type": "quantitative",
            "is_quantitative": True,
            "approximate_location": "Revenue grew 11% to $40.0 billion",
        }
        data.update(overrides)
        return data

    def test_valid_construction(self):
        claim = IdentifiedClaim(**self._valid_claim())
        self.assertEqual(claim.claim_type, "quantitative")
        self.assertTrue(claim.is_quantitative)

    def test_all_claim_types(self):
        for ct in ("quantitative", "qualitative", "comparative", "causal"):
            claim = IdentifiedClaim(**self._valid_claim(claim_type=ct))
            self.assertEqual(claim.claim_type, ct)

    def test_invalid_claim_type_rejected(self):
        with self.assertRaises(ValidationError):
            IdentifiedClaim(**self._valid_claim(claim_type="invalid"))

    def test_short_claim_text_rejected(self):
        with self.assertRaises(ValidationError):
            IdentifiedClaim(**self._valid_claim(claim_text="Hi"))

    def test_missing_required_field(self):
        with self.assertRaises(ValidationError):
            IdentifiedClaim(
                claim_text="Revenue grew",
                claim_type="quantitative",
                # missing is_quantitative and approximate_location
            )


class TestClaimList(unittest.TestCase):
    """Pass 1 model: ClaimList."""

    def test_valid_construction(self):
        cl = ClaimList(
            section_key="mda",
            claims=[
                IdentifiedClaim(
                    claim_text="Revenue grew 11%",
                    claim_type="quantitative",
                    is_quantitative=True,
                    approximate_location="Revenue grew 11% to",
                ),
            ],
            total_claims=1,
        )
        self.assertEqual(cl.section_key, "mda")
        self.assertEqual(len(cl.claims), 1)

    def test_empty_claims_list(self):
        cl = ClaimList(section_key="risk_factors", claims=[], total_claims=0)
        self.assertEqual(len(cl.claims), 0)


class TestExtractedFactModel(unittest.TestCase):
    """Pass 2 model: ExtractedFactModel."""

    def _valid_fact(self, **overrides):
        data = {
            "fact_type": "metric",
            "fact_key": "mda.revenue_growth",
            "fact_value": "11.3%",
            "fact_value_numeric": 0.113,
            "fact_unit": "percent",
            "fiscal_period": "FY2025",
            "source_quote": "Net revenue grew 11.3% year-over-year to $40.0 billion",
            "confidence_note": None,
        }
        data.update(overrides)
        return data

    def test_valid_construction(self):
        fact = ExtractedFactModel(**self._valid_fact())
        self.assertEqual(fact.fact_type, FactType.metric)
        self.assertEqual(fact.fact_key, "mda.revenue_growth")
        self.assertAlmostEqual(fact.fact_value_numeric, 0.113)

    def test_narrative_fact_null_numeric(self):
        fact = ExtractedFactModel(**self._valid_fact(
            fact_type="narrative",
            fact_key="biz.model.subscription",
            fact_value="subscription-based platform",
            fact_value_numeric=None,
            fact_unit="text",
        ))
        self.assertIsNone(fact.fact_value_numeric)
        self.assertEqual(fact.fact_unit, FactUnit.text)

    def test_guidance_fact(self):
        fact = ExtractedFactModel(**self._valid_fact(
            fact_type="guidance",
            fact_key="mda.guidance.revenue_fy2026",
            fact_value="$42-44 billion",
            fact_value_numeric=43000000000.0,
            fact_unit="USD",
        ))
        self.assertEqual(fact.fact_type, FactType.guidance)

    def test_risk_factor(self):
        fact = ExtractedFactModel(**self._valid_fact(
            fact_type="risk_factor",
            fact_key="risk.regulatory.eu",
            fact_value="subject to EU regulatory scrutiny",
            fact_value_numeric=None,
            fact_unit="text",
        ))
        self.assertEqual(fact.fact_type, FactType.risk_factor)

    def test_short_source_quote_rejected(self):
        with self.assertRaises(ValidationError):
            ExtractedFactModel(**self._valid_fact(source_quote="short"))

    def test_short_fact_key_rejected(self):
        with self.assertRaises(ValidationError):
            ExtractedFactModel(**self._valid_fact(fact_key="ab"))

    def test_missing_source_quote_rejected(self):
        data = self._valid_fact()
        del data["source_quote"]
        with self.assertRaises(ValidationError):
            ExtractedFactModel(**data)

    def test_invalid_fact_type_rejected(self):
        with self.assertRaises(ValidationError):
            ExtractedFactModel(**self._valid_fact(fact_type="invalid"))

    def test_invalid_fact_unit_rejected(self):
        with self.assertRaises(ValidationError):
            ExtractedFactModel(**self._valid_fact(fact_unit="invalid"))

    def test_round_trip(self):
        original = ExtractedFactModel(**self._valid_fact())
        dumped = original.model_dump()
        restored = ExtractedFactModel.model_validate(dumped)
        self.assertEqual(original, restored)


class TestExtractionBatch(unittest.TestCase):
    """Pass 2 model: ExtractionBatch."""

    def test_valid_with_facts(self):
        batch = ExtractionBatch(
            section_key="mda",
            facts=[
                ExtractedFactModel(
                    fact_type="metric",
                    fact_key="mda.revenue",
                    fact_value="$40.0 billion",
                    fact_value_numeric=40000000000.0,
                    fact_unit="USD",
                    source_quote="Net revenue was $40.0 billion for the fiscal year",
                ),
            ],
            skipped_claims=["some claim that couldn't be extracted"],
        )
        self.assertEqual(len(batch.facts), 1)
        self.assertEqual(len(batch.skipped_claims), 1)

    def test_empty_facts_and_skipped(self):
        batch = ExtractionBatch(section_key="risk_factors", facts=[])
        self.assertEqual(len(batch.facts), 0)
        self.assertEqual(len(batch.skipped_claims), 0)


class TestSchemaGeneration(unittest.TestCase):
    """JSON Schema generation from Pydantic models."""

    def test_claim_list_schema_has_properties(self):
        schema = get_claim_list_schema()
        self.assertIn("properties", schema)
        self.assertIn("section_key", schema["properties"])
        self.assertIn("claims", schema["properties"])
        self.assertIn("total_claims", schema["properties"])

    def test_extraction_schema_has_properties(self):
        schema = get_extraction_schema("mda")
        self.assertIn("properties", schema)
        self.assertIn("section_key", schema["properties"])
        self.assertIn("facts", schema["properties"])
        self.assertIn("skipped_claims", schema["properties"])

    def test_extraction_schema_for_unknown_section(self):
        # Falls back to ExtractionBatch
        schema = get_extraction_schema("unknown_section")
        self.assertIn("properties", schema)
        self.assertIn("facts", schema["properties"])

    def test_extraction_schema_strips_part_suffix(self):
        # mda_part1 should map to mda's schema
        schema1 = get_extraction_schema("mda")
        schema2 = get_extraction_schema("mda_part1")
        self.assertEqual(schema1, schema2)

    def test_all_registered_sections_produce_schemas(self):
        for section in ("mda", "risk_factors", "business", "market_risk"):
            schema = get_extraction_schema(section)
            self.assertIn("properties", schema, f"Schema for {section} missing properties")


if __name__ == "__main__":
    unittest.main()
