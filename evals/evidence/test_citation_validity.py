"""Eval: citation validity — every source_quote must be traceable to filing text.

For each extracted fact with a source_quote, verifies that the quote
actually appears in the section text it claims to come from.
"""

import unittest
import sys
from difflib import SequenceMatcher
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evals.evidence.conftest import GOLDEN_FACTS, SECTION_BY_ID

# Matches QUOTE_MATCH_THRESHOLD in scripts/sec_edgar/llm_extract.py
FUZZY_THRESHOLD = 0.85


def _fuzzy_match_ratio(quote: str, text: str) -> float:
    """Best fuzzy match ratio of quote against a sliding window in text."""
    if not quote or not text:
        return 0.0
    if quote in text:
        return 1.0
    quote_len = len(quote)
    if quote_len > len(text):
        return 0.0
    best = 0.0
    # Sliding window with step for performance
    step = max(1, quote_len // 4)
    for i in range(0, len(text) - quote_len + 1, step):
        window = text[i:i + quote_len + 20]  # slight overscan
        ratio = SequenceMatcher(None, quote.lower(), window.lower()).ratio()
        if ratio > best:
            best = ratio
        if best >= 0.95:
            break
    return best


class TestSourceQuotePresence(unittest.TestCase):
    """Every source_quote should be findable in its section's text."""

    def setUp(self):
        # Only facts with a non-empty source_quote and a known section
        self.facts_with_quotes = [
            f for f in GOLDEN_FACTS
            if f.get("source_quote")
            and f.get("document_section_id") in SECTION_BY_ID
        ]

    def test_has_facts_to_check(self):
        """Sanity: we have a meaningful number of facts with quotes."""
        self.assertGreater(len(self.facts_with_quotes), 50,
                           "Expected at least 50 facts with source quotes")

    def test_exact_or_fuzzy_match(self):
        """At least 80% of source_quotes are exact substrings or fuzzy match >= 0.85."""
        passed = 0
        failures = []
        for f in self.facts_with_quotes:
            section = SECTION_BY_ID[f["document_section_id"]]
            text = section["content_text"]
            quote = f["source_quote"]

            # Try exact match first
            if quote in text:
                passed += 1
                continue

            # Try fuzzy match
            ratio = _fuzzy_match_ratio(quote, text)
            if ratio >= FUZZY_THRESHOLD:
                passed += 1
            else:
                failures.append(
                    f"fact_key={f['fact_key']}: fuzzy={ratio:.2f} < {FUZZY_THRESHOLD} "
                    f"(quote={quote[:60]}...)"
                )

        total = len(self.facts_with_quotes)
        rate = passed / total if total else 0
        # At least 80% of citations must be valid
        self.assertGreaterEqual(
            rate, 0.80,
            f"Citation validity rate {rate:.1%} ({passed}/{total}) below 80% threshold.\n"
            f"Failures:\n" + "\n".join(failures[:5])
        )


class TestCharOffsetConsistency(unittest.TestCase):
    """For facts with char offsets, the slice should match the quote."""

    def setUp(self):
        self.facts_with_offsets = [
            f for f in GOLDEN_FACTS
            if f.get("source_char_offset_start") is not None
            and f.get("source_char_offset_end") is not None
            and f.get("source_quote")
            and f.get("document_section_id") in SECTION_BY_ID
        ]

    def test_has_facts_with_offsets(self):
        self.assertGreater(len(self.facts_with_offsets), 30,
                           "Expected at least 30 facts with char offsets")

    def test_offset_slice_matches_quote(self):
        """At least 90% of offset slices match the source_quote (exact or fuzzy)."""
        passed = 0
        failures = []
        for f in self.facts_with_offsets:
            section = SECTION_BY_ID[f["document_section_id"]]
            text = section["content_text"]
            start = f["source_char_offset_start"]
            end = f["source_char_offset_end"]
            quote = f["source_quote"]

            if start < 0 or end > len(text) or start >= end:
                failures.append(f"fact_key={f['fact_key']}: invalid offsets [{start}:{end}] for text len {len(text)}")
                continue

            sliced = text[start:end]
            if sliced == quote:
                passed += 1
                continue
            ratio = SequenceMatcher(None, quote.lower(), sliced.lower()).ratio()
            if ratio >= FUZZY_THRESHOLD:
                passed += 1
            else:
                failures.append(
                    f"fact_key={f['fact_key']}: offset slice ratio={ratio:.2f} "
                    f"(quote={quote[:40]}... vs slice={sliced[:40]}...)"
                )

        total = len(self.facts_with_offsets)
        rate = passed / total if total else 0
        self.assertGreaterEqual(
            rate, 0.90,
            f"Offset accuracy {rate:.1%} ({passed}/{total}) below 90% threshold.\n"
            f"Failures:\n" + "\n".join(failures[:5])
        )


class TestConfidenceRules(unittest.TestCase):
    """Confidence values follow the documented assignment rules."""

    def test_all_confidence_in_range(self):
        """Every fact has 0 < confidence <= 1.0."""
        for f in GOLDEN_FACTS:
            c = f["confidence"]
            self.assertGreater(c, 0.0, f"fact_key={f['fact_key']}: confidence=0")
            self.assertLessEqual(c, 1.0, f"fact_key={f['fact_key']}: confidence>1")

    def test_llm_confidence_capped(self):
        """LLM-extracted facts should not exceed 0.95 (reserved for XBRL)."""
        for f in GOLDEN_FACTS:
            if f["extraction_method"] == "llm_structured":
                self.assertLessEqual(
                    f["confidence"], 0.95,
                    f"fact_key={f['fact_key']}: LLM confidence {f['confidence']} > 0.95"
                )

    def test_minimum_confidence(self):
        """LLM facts should have confidence >= 0.70 (lowest documented tier)."""
        for f in GOLDEN_FACTS:
            if f["extraction_method"] == "llm_structured":
                self.assertGreaterEqual(
                    f["confidence"], 0.70,
                    f"fact_key={f['fact_key']}: confidence {f['confidence']} < 0.70"
                )


if __name__ == "__main__":
    unittest.main()
