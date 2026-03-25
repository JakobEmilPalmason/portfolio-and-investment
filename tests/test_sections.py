"""Tests for scripts/sec_edgar/sections.py — section parsing from filing objects."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from sec_edgar.sections import (
    CHARS_PER_TOKEN,
    SECTION_MAP,
    TOKEN_CAP,
    _content_hash,
    _estimate_tokens,
    _get_section_text,
    _split_section,
    extract_sections,
)


class TestEstimateTokens(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(_estimate_tokens(""), 0)

    def test_known_length(self):
        text = "a" * 400
        self.assertEqual(_estimate_tokens(text), 400 // CHARS_PER_TOKEN)

    def test_realistic(self):
        # ~100 words ≈ ~130 tokens ≈ ~520 chars
        text = "word " * 100
        tokens = _estimate_tokens(text)
        self.assertGreater(tokens, 50)
        self.assertLess(tokens, 200)


class TestContentHash(unittest.TestCase):
    def test_deterministic(self):
        text = "Revenue grew 11% to $40.0 billion."
        self.assertEqual(_content_hash(text), _content_hash(text))

    def test_different_text_different_hash(self):
        self.assertNotEqual(_content_hash("aaa"), _content_hash("bbb"))

    def test_length_is_16(self):
        self.assertEqual(len(_content_hash("test")), 16)


class TestGetSectionText(unittest.TestCase):
    def test_callable_accessor_returns_string(self):
        obj = MagicMock()
        obj.business = "Business description text."
        result = _get_section_text(obj, lambda o: o.business)
        self.assertEqual(result, "Business description text.")

    def test_callable_accessor_returns_none(self):
        obj = MagicMock()
        obj.business = None
        result = _get_section_text(obj, lambda o: o.business)
        self.assertIsNone(result)

    def test_callable_accessor_strips_whitespace(self):
        obj = MagicMock()
        obj.business = "  text  \n\n  "
        result = _get_section_text(obj, lambda o: o.business)
        self.assertEqual(result, "text")

    def test_callable_accessor_empty_string_returns_none(self):
        obj = MagicMock()
        obj.business = "   "
        result = _get_section_text(obj, lambda o: o.business)
        self.assertIsNone(result)

    def test_callable_accessor_exception_returns_none(self):
        obj = MagicMock()
        obj.business = property(lambda self: (_ for _ in ()).throw(RuntimeError("parse fail")))
        result = _get_section_text(obj, lambda o: (_ for _ in ()).throw(RuntimeError("fail")))
        self.assertIsNone(result)

    def test_stringifies_non_string_objects(self):
        obj = MagicMock()
        section_obj = MagicMock()
        section_obj.__str__ = lambda self: "Section content as string"
        obj.business = section_obj
        result = _get_section_text(obj, lambda o: o.business)
        self.assertEqual(result, "Section content as string")


class TestSplitSection(unittest.TestCase):
    def test_small_section_returns_single_chunk(self):
        text = "Small paragraph."
        chunks = _split_section(text, "mda", "MD&A", token_cap=TOKEN_CAP)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0][0], "mda")  # no suffix
        self.assertEqual(chunks[0][2], "Small paragraph.")

    def test_oversized_section_splits_at_paragraphs(self):
        # Create text that exceeds token cap
        para = "a" * (CHARS_PER_TOKEN * 3000)  # ~3000 tokens
        text = f"{para}\n\n{para}\n\n{para}"  # ~9000 tokens > 8000 cap
        chunks = _split_section(text, "mda", "MD&A", token_cap=TOKEN_CAP)
        self.assertGreater(len(chunks), 1)
        # All chunks should have suffixed keys
        for key, title, _ in chunks:
            self.assertTrue(key.startswith("mda_part"), f"Expected suffix, got {key}")
            self.assertIn("Part", title)

    def test_chunk_tokens_within_cap(self):
        para = "x" * (CHARS_PER_TOKEN * 2000)  # ~2000 tokens each
        text = "\n\n".join([para] * 6)  # ~12000 tokens
        chunks = _split_section(text, "risk_factors", "Risk Factors", token_cap=TOKEN_CAP)
        for key, title, chunk_text in chunks:
            tokens = _estimate_tokens(chunk_text)
            # Each chunk should be at or below cap (with some tolerance for paragraph boundaries)
            self.assertLessEqual(tokens, TOKEN_CAP + 100,
                                 f"Chunk {key} has {tokens} tokens, exceeds cap")

    def test_single_oversized_paragraph_splits_at_sentences(self):
        # One giant paragraph with sentences
        sentences = ["This is sentence number %d. " % i for i in range(500)]
        text = " ".join(sentences)  # ~5000+ tokens as one paragraph
        chunks = _split_section(text, "mda", "MD&A", token_cap=2000)
        self.assertGreater(len(chunks), 1)

    def test_suffixed_keys_are_sequential(self):
        para = "y" * (CHARS_PER_TOKEN * 3000)
        text = f"{para}\n\n{para}\n\n{para}"
        chunks = _split_section(text, "biz", "Business", token_cap=TOKEN_CAP)
        for i, (key, _, _) in enumerate(chunks, 1):
            self.assertEqual(key, f"biz_part{i}")


class TestExtractSections(unittest.TestCase):
    def _mock_filing(self, sections: dict):
        """Create a mock filing object with given section texts."""
        obj = MagicMock()
        obj.business = sections.get("business")
        obj.risk_factors = sections.get("risk_factors")
        obj.management_discussion = sections.get("mda")
        obj.__getitem__ = MagicMock(return_value=sections.get("market_risk"))
        return obj

    def test_all_sections_found(self):
        obj = self._mock_filing({
            "business": "Business description here.",
            "risk_factors": "Risk factor content here.",
            "mda": "Management discussion content.",
            "market_risk": "Market risk disclosures.",
        })
        sections, warnings = extract_sections(obj, "10-K")
        self.assertEqual(len(sections), 4)
        self.assertEqual(len(warnings), 0)
        # Check section_order is sequential
        orders = [s["section_order"] for s in sections]
        self.assertEqual(orders, sorted(orders))

    def test_missing_section_produces_warning(self):
        obj = self._mock_filing({
            "business": "Business here.",
            "risk_factors": None,
            "mda": "MD&A here.",
            "market_risk": None,
        })
        sections, warnings = extract_sections(obj, "10-K")
        self.assertEqual(len(sections), 2)
        self.assertEqual(len(warnings), 2)
        self.assertTrue(any("risk_factors" in w for w in warnings))
        self.assertTrue(any("market_risk" in w for w in warnings))

    def test_no_sections_produces_warning(self):
        obj = self._mock_filing({})
        sections, warnings = extract_sections(obj, "10-K")
        self.assertEqual(len(sections), 0)
        self.assertTrue(any("No sections" in w for w in warnings))

    def test_amendment_form_type(self):
        obj = self._mock_filing({
            "business": "Business text.",
            "risk_factors": "Risk text.",
            "mda": "MD&A text.",
        })
        sections, warnings = extract_sections(obj, "10-K/A")
        # Should use 10-K section map despite amendment suffix
        self.assertGreater(len(sections), 0)

    def test_20f_form_type(self):
        obj = self._mock_filing({
            "business": "Business.",
            "risk_factors": "Risks.",
            "mda": "Operating review.",
        })
        sections, warnings = extract_sections(obj, "20-F")
        # 20-F has 3 sections (no market_risk)
        self.assertEqual(len(sections), 3)

    def test_section_dict_structure(self):
        obj = self._mock_filing({"business": "Test content."})
        sections, _ = extract_sections(obj, "10-K")
        s = sections[0]
        self.assertIn("section_key", s)
        self.assertIn("section_title", s)
        self.assertIn("section_order", s)
        self.assertIn("content_text", s)
        self.assertIn("content_hash", s)
        self.assertIn("token_estimate", s)
        self.assertEqual(s["section_key"], "business")
        self.assertEqual(s["content_text"], "Test content.")

    def test_oversized_section_gets_split(self):
        # Use multiple paragraphs so the splitter has paragraph boundaries
        para = "a" * (CHARS_PER_TOKEN * 3000)  # ~3000 tokens per para
        big_text = f"{para}\n\n{para}\n\n{para}"  # ~9000 tokens > 8000 cap
        obj = self._mock_filing({"mda": big_text})
        sections, _ = extract_sections(obj, "10-K")
        # Should have multiple mda_part sections
        mda_keys = [s["section_key"] for s in sections if s["section_key"].startswith("mda")]
        self.assertGreater(len(mda_keys), 1)

    def test_section_map_covers_all_form_types(self):
        for form_type in ("10-K", "20-F", "40-F"):
            self.assertIn(form_type, SECTION_MAP, f"Missing section map for {form_type}")


if __name__ == "__main__":
    unittest.main()
