"""
sec_edgar — SEC EDGAR filing data extraction via edgartools.

Phase 1: XBRL facts + multi-year financial statements.
Phase 2: Narrative section parsing via TenK/TwentyF .obj() parsed sections.
Phase 4: Post-analysis verification (claim decomposition, fact checking, arithmetic).
"""

from .client import fetch_10k, fetch_filing_object
from .xbrl import extract_financials
from .sections import extract_sections
from .llm_extract import extract_section_facts
from .claim_decomposer import decompose_report, decompose_section
from .fact_checker import verify_assertions
from .arithmetic_engine import validate_formula, execute_formula, verify_arithmetic_assertion

__all__ = [
    "fetch_10k",
    "fetch_filing_object",
    "extract_financials",
    "extract_sections",
    "extract_section_facts",
    "decompose_report",
    "decompose_section",
    "verify_assertions",
    "validate_formula",
    "execute_formula",
    "verify_arithmetic_assertion",
]
