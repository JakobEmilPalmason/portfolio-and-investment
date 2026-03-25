"""
Pydantic v2 models for the evidence extraction pipeline.

Used by:
- LLM extraction (scripts/sec_edgar/llm_extract.py) — JSON Schema in prompts, output validation
- DB storage (src/evidence.py) — validate before batch_insert_facts()

Not used by Phase 1 XBRL extraction (which writes dicts directly).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FactType(str, Enum):
    metric = "metric"
    narrative = "narrative"
    guidance = "guidance"
    risk_factor = "risk_factor"


class FactUnit(str, Enum):
    usd = "USD"
    percent = "percent"
    ratio = "ratio"
    count = "count"
    days = "days"
    text = "text"


# ---------------------------------------------------------------------------
# Pass 1 models — claim identification
# ---------------------------------------------------------------------------


class IdentifiedClaim(BaseModel):
    """A single factual claim found in a filing section (Pass 1 output)."""

    claim_text: str = Field(
        ..., min_length=5, description="The factual claim in one sentence"
    )
    claim_type: str = Field(
        ...,
        description="quantitative | qualitative | comparative | causal",
        pattern=r"^(quantitative|qualitative|comparative|causal)$",
    )
    is_quantitative: bool = Field(
        ..., description="True if the claim contains a specific number"
    )
    approximate_location: str = Field(
        ...,
        description="First ~10 words of the sentence containing the claim",
    )


class ClaimList(BaseModel):
    """All claims from a section (Pass 1 output)."""

    section_key: str
    claims: list[IdentifiedClaim]
    total_claims: int


# ---------------------------------------------------------------------------
# Pass 2 models — structured extraction
# ---------------------------------------------------------------------------


class ExtractedFactModel(BaseModel):
    """Structured extraction from a single claim (Pass 2 output)."""

    fact_type: FactType
    fact_key: str = Field(
        ...,
        min_length=3,
        description=(
            "Dot-notation key with section prefix: "
            "'mda.revenue_growth', 'risk.regulatory.eu', 'biz.employees'"
        ),
    )
    fact_value: str = Field(
        ...,
        min_length=1,
        description="Human-readable value as stated in filing",
    )
    fact_value_numeric: Optional[float] = Field(
        None,
        description=(
            "Normalized to base units: dollars (not millions), "
            "decimal (0.15 not 15%). Null for qualitative facts."
        ),
    )
    fact_unit: FactUnit
    fiscal_period: Optional[str] = Field(
        None, description="FY2025, Q3FY2025, etc."
    )
    source_quote: str = Field(
        ...,
        min_length=10,
        description="VERBATIM substring from the filing section text",
    )
    confidence_note: Optional[str] = Field(
        None, description="Caveats about extraction confidence, if any"
    )


class ExtractionBatch(BaseModel):
    """Extracted facts from a batch of claims (Pass 2 output)."""

    section_key: str
    facts: list[ExtractedFactModel]
    skipped_claims: list[str] = Field(
        default_factory=list,
        description="Claims that could not be extracted (no verbatim quote found, etc.)",
    )


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------

# Section → extraction model mapping.
# All sections currently use ExtractionBatch. Section-specific models
# (e.g., RiskFactorBatch with a severity field) can be added here later.
SECTION_SCHEMAS: dict[str, type[BaseModel]] = {
    "mda": ExtractionBatch,
    "risk_factors": ExtractionBatch,
    "business": ExtractionBatch,
    "market_risk": ExtractionBatch,
}


def get_extraction_schema(section_key: str) -> dict:
    """Return JSON Schema dict for a section's extraction model.

    The schema is passed to the LLM prompt so it knows the expected
    output structure. Also used for Pydantic validation on the Python side.
    """
    # Strip part suffixes (mda_part1 → mda) for registry lookup
    base_key = section_key.split("_part")[0] if "_part" in section_key else section_key
    model = SECTION_SCHEMAS.get(base_key, ExtractionBatch)
    return model.model_json_schema()


def get_claim_list_schema() -> dict:
    """Return JSON Schema dict for the Pass 1 ClaimList model."""
    return ClaimList.model_json_schema()


# ---------------------------------------------------------------------------
# Phase 6 models — semantic diffing
# ---------------------------------------------------------------------------


class NarrativeChange(BaseModel):
    """A single material change detected between two filing periods."""

    change_type: str = Field(
        ...,
        pattern=r"^(added|removed|changed)$",
        description="added=new in period B, removed=gone from period A, changed=present in both but different",
    )
    category: str = Field(
        ...,
        pattern=r"^(risk|guidance|tone|business_model|quantitative|other)$",
        description="Category of the change",
    )
    description: str = Field(
        ..., min_length=10, description="1-2 sentence summary of what changed"
    )
    quote_a: str = Field(
        default="", description="Relevant excerpt from period A (empty if added)"
    )
    quote_b: str = Field(
        default="", description="Relevant excerpt from period B (empty if removed)"
    )
    significance: int = Field(
        ...,
        ge=1,
        le=5,
        description="1=cosmetic, 2=minor, 3=notable, 4=material, 5=fundamental",
    )


class NarrativeDiffResult(BaseModel):
    """LLM output for comparing two versions of a filing section."""

    section_key: str
    changes: list[NarrativeChange]


def get_narrative_diff_schema() -> dict:
    """Return JSON Schema dict for the narrative diff model."""
    return NarrativeDiffResult.model_json_schema()


# ---------------------------------------------------------------------------
# Phase 4 models — claim decomposition and verification
# ---------------------------------------------------------------------------


class DecomposedAssertion(BaseModel):
    """A single verifiable assertion extracted from a report section."""

    assertion_text: str = Field(
        ..., min_length=10,
        description="The atomic claim, independently understandable",
    )
    assertion_type: str = Field(
        ...,
        description="quantitative | qualitative | comparative | causal",
        pattern=r"^(quantitative|qualitative|comparative|causal)$",
    )
    category: str = Field(
        ...,
        description="finding | strength | risk | red_flag | trigger",
        pattern=r"^(finding|strength|risk|red_flag|trigger)$",
    )
    requires_arithmetic: bool = Field(
        False,
        description="True only for derived metrics (ROIC, margins, ratios). Raw numbers = False.",
    )
    source_location: str = Field(
        ...,
        description="Where in the section: 'key_findings:3' or 'detailed_analysis:para2'",
    )


class AssertionBatch(BaseModel):
    """All assertions from a report section (Pass A output)."""

    umbrella_number: int
    section_title: str
    assertions: list[DecomposedAssertion]
    total_assertions: int


class VerificationResult(BaseModel):
    """Verification of one assertion against evidence (Pass B output)."""

    assertion_index: int = Field(
        ..., description="Index into the batch being verified"
    )
    relationship: str = Field(
        ...,
        description="supports | contradicts | partial | unverifiable",
        pattern=r"^(supports|contradicts|partial|unverifiable)$",
    )
    match_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the assessed relationship (not match quality)",
    )
    matched_fact_key: Optional[str] = Field(
        None,
        description="fact_key of the best matching extracted_fact, or null",
    )
    reasoning: str = Field(
        ..., min_length=10,
        description="Brief explanation of why this relationship was assigned",
    )
    numeric_expected: Optional[float] = Field(
        None, description="The number the assertion claims (if quantitative)"
    )
    numeric_actual: Optional[float] = Field(
        None, description="The number the evidence shows (if quantitative)"
    )


class VerificationBatch(BaseModel):
    """Verification results for a batch of assertions (Pass B output)."""

    results: list[VerificationResult]
    skipped_assertions: list[int] = Field(
        default_factory=list,
        description="Indices of assertions that could not be verified at all",
    )


class ArithmeticFormulaResult(BaseModel):
    """LLM output for identifying a formula to verify a derived metric (Pass C)."""

    formula: str = Field(
        ..., min_length=3,
        description="Python expression using variable names matching input keys",
    )
    inputs: dict[str, str] = Field(
        ...,
        description="Map of variable name → fact_key to look up in evidence DB",
    )
    expected_result: Optional[float] = Field(
        None, description="The value the assertion claims",
    )
    result_unit: str = Field(
        "ratio",
        description="Unit of the result: ratio, percent, USD, count",
    )


# Phase 4 schema registry
VERIFICATION_SCHEMAS: dict[str, type[BaseModel]] = {
    "decompose": AssertionBatch,
    "verify": VerificationBatch,
    "arithmetic": ArithmeticFormulaResult,
}


def get_verification_schema(schema_key: str) -> dict:
    """Return JSON Schema dict for a Phase 4 model."""
    model = VERIFICATION_SCHEMAS.get(schema_key, VerificationBatch)
    return model.model_json_schema()
