"""
Section parser — extract narrative sections from SEC filings via edgartools.

Uses filing.obj() to get TenK/TwentyF/FortyF objects with named section accessors.
Splits sections exceeding TOKEN_CAP at paragraph boundaries.
Stores sections in document_sections table via EvidenceDB.

Phase 2 of the evidence extraction masterplan.
"""

import hashlib
import logging

logger = logging.getLogger(__name__)

TOKEN_CAP = 8000  # max tokens per section chunk
CHARS_PER_TOKEN = 4  # conservative estimate (no tiktoken dependency)


# ---------------------------------------------------------------------------
# Section map: form_type → [(section_key, title, accessor)]
# ---------------------------------------------------------------------------

def _get_section_text(filing_obj, accessor):
    """Safely call an accessor on a filing object, return text or None."""
    try:
        if callable(accessor):
            result = accessor(filing_obj)
        else:
            result = filing_obj[accessor]
        if result is None:
            return None
        # edgartools may return Section objects with __str__, or raw strings
        text = str(result) if not isinstance(result, str) else result
        text = text.strip()
        return text if text else None
    except Exception as e:
        logger.warning("Section accessor failed: %s", e)
        return None


SECTION_MAP = {
    "10-K": [
        ("business", "Business", lambda obj: obj.business),
        ("risk_factors", "Risk Factors", lambda obj: obj.risk_factors),
        ("mda", "Management Discussion & Analysis", lambda obj: obj.management_discussion),
        ("market_risk", "Quantitative and Qualitative Disclosures About Market Risk",
         lambda obj: obj["Item 7A"]),
    ],
    "20-F": [
        ("business", "Business Overview", lambda obj: obj.business),
        ("risk_factors", "Risk Factors", lambda obj: obj.risk_factors),
        ("mda", "Operating and Financial Review", lambda obj: obj.management_discussion),
    ],
    "40-F": [
        ("business", "Business", lambda obj: obj.business),
        ("risk_factors", "Risk Factors", lambda obj: obj.risk_factors),
        ("mda", "Management Discussion & Analysis",
         lambda obj: getattr(obj, "mda_text", None)),
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """Estimate token count from character length."""
    return len(text) // CHARS_PER_TOKEN


def _content_hash(text: str) -> str:
    """SHA-256 hash of text, truncated to 16 hex chars for staleness detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _split_section(text: str, section_key: str, section_title: str,
                   token_cap: int = TOKEN_CAP) -> list[tuple[str, str, str]]:
    """Split a section that exceeds token_cap at paragraph boundaries.

    Returns list of (section_key_with_suffix, title_with_part, text_chunk).
    """
    paragraphs = text.split("\n\n")
    chunks: list[tuple[str, str, str]] = []
    current_chunk: list[str] = []
    current_tokens = 0
    part_num = 1

    for para in paragraphs:
        para_tokens = _estimate_tokens(para)

        # If a single paragraph exceeds the cap, split at sentence boundaries
        if para_tokens > token_cap:
            # Flush current chunk first
            if current_chunk:
                key = f"{section_key}_part{part_num}"
                title = f"{section_title} (Part {part_num})"
                chunks.append((key, title, "\n\n".join(current_chunk)))
                part_num += 1
                current_chunk = []
                current_tokens = 0

            # Split the oversized paragraph at sentence boundaries
            sentences = para.replace(". ", ".\n").split("\n")
            sent_chunk: list[str] = []
            sent_tokens = 0
            for sent in sentences:
                sent_t = _estimate_tokens(sent)
                if sent_tokens + sent_t > token_cap and sent_chunk:
                    key = f"{section_key}_part{part_num}"
                    title = f"{section_title} (Part {part_num})"
                    chunks.append((key, title, " ".join(sent_chunk)))
                    part_num += 1
                    sent_chunk = []
                    sent_tokens = 0
                sent_chunk.append(sent)
                sent_tokens += sent_t
            if sent_chunk:
                key = f"{section_key}_part{part_num}"
                title = f"{section_title} (Part {part_num})"
                chunks.append((key, title, " ".join(sent_chunk)))
                part_num += 1
            continue

        # Normal case: add paragraph to current chunk
        if current_tokens + para_tokens > token_cap and current_chunk:
            key = f"{section_key}_part{part_num}"
            title = f"{section_title} (Part {part_num})"
            chunks.append((key, title, "\n\n".join(current_chunk)))
            part_num += 1
            current_chunk = []
            current_tokens = 0

        current_chunk.append(para)
        current_tokens += para_tokens

    # Flush remaining
    if current_chunk:
        if part_num == 1:
            # Never split — shouldn't happen (caller checks), but be safe
            chunks.append((section_key, section_title, "\n\n".join(current_chunk)))
        else:
            key = f"{section_key}_part{part_num}"
            title = f"{section_title} (Part {part_num})"
            chunks.append((key, title, "\n\n".join(current_chunk)))

    return chunks


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def extract_sections(filing_obj, form_type: str) -> tuple[list[dict], list[str]]:
    """Parse narrative sections from a filing object.

    Args:
        filing_obj: TenK/TwentyF/FortyF object from edgartools filing.obj()
        form_type: e.g. "10-K", "10-K/A", "20-F", "40-F"

    Returns:
        (sections, warnings) where sections is a list of dicts ready for
        EvidenceDB.upsert_document_section(), and warnings lists sections
        that could not be parsed.
    """
    # Strip amendment suffix for section map lookup
    base_form = form_type.split("/")[0] if "/" in form_type else form_type
    section_defs = SECTION_MAP.get(base_form, SECTION_MAP.get("10-K", []))

    sections: list[dict] = []
    warnings: list[str] = []
    order = 0

    for section_key, section_title, accessor in section_defs:
        text = _get_section_text(filing_obj, accessor)

        if text is None:
            warnings.append(f"{section_key}: section not found in filing")
            continue

        tokens = _estimate_tokens(text)

        if tokens > TOKEN_CAP:
            # Split oversized section
            parts = _split_section(text, section_key, section_title, TOKEN_CAP)
            for part_key, part_title, part_text in parts:
                order += 1
                sections.append({
                    "section_key": part_key,
                    "section_title": part_title,
                    "section_order": order,
                    "content_text": part_text,
                    "content_hash": _content_hash(part_text),
                    "token_estimate": _estimate_tokens(part_text),
                })
        else:
            order += 1
            sections.append({
                "section_key": section_key,
                "section_title": section_title,
                "section_order": order,
                "content_text": text,
                "content_hash": _content_hash(text),
                "token_estimate": tokens,
            })

    if not sections:
        warnings.append("No sections could be parsed from this filing")

    return sections, warnings
