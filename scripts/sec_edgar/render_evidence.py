"""
Markdown renderer for narrative evidence extracted from SEC filings.

Output: compact markdown for agent consumption, organized by section.
Follows the same pattern as render.py (Phase 1 XBRL renderer).

Phase 2 of the evidence extraction masterplan.
"""

from datetime import datetime, timezone


def _fiscal_year(period_str: str) -> str:
    """Turn '2025-09-30' into 'FY2025'. Returns 'unknown' on failure."""
    try:
        return f"FY{period_str[:4]}"
    except Exception:
        return "unknown"


def _group_by_section(facts: list[dict]) -> dict[str, list[dict]]:
    """Group facts by their section prefix (first component of fact_key).

    mda.revenue_growth -> "mda"
    risk.regulatory.eu -> "risk"
    biz.model.subscription -> "biz"
    market_risk.fx.eur -> "market_risk"
    """
    groups: dict[str, list[dict]] = {}
    for f in facts:
        key = f.get("fact_key", "")
        # Determine section prefix
        if key.startswith("market_risk"):
            prefix = "market_risk"
        elif key.startswith("mda"):
            prefix = "mda"
        elif key.startswith("risk"):
            prefix = "risk"
        elif key.startswith("biz"):
            prefix = "biz"
        else:
            prefix = key.split(".")[0] if "." in key else "other"

        groups.setdefault(prefix, []).append(f)

    return groups


def render_evidence_markdown(
    ticker: str,
    facts: list[dict],
    filing_metadata: dict,
    warnings: list[str] | None = None,
) -> str:
    """Render extracted narrative facts as a markdown file.

    Args:
        ticker: Stock ticker symbol.
        facts: List of fact dicts from extract_section_facts().
        filing_metadata: Dict with company_name, form_type, period_of_report, etc.
        warnings: List of warning strings from section parsing.

    Returns:
        Markdown string for context/{TICKER}/evidence-10K-FY{YYYY}.md.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    period = filing_metadata.get("period_of_report", "unknown")
    form = filing_metadata.get("form_type", "10-K")
    company = filing_metadata.get("company_name", ticker)
    fiscal_year = _fiscal_year(period)

    lines: list[str] = []

    # Header
    lines.append(f"# Narrative Evidence: {ticker} — {company} ({form} {fiscal_year})")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Source:** SEC EDGAR (LLM extraction from {form})")
    lines.append(f"**Extraction method:** Tier 2 — multi-pass structured extraction")
    lines.append(f"**Filing period:** {period}")
    lines.append(f"**Confidence range:** 0.80-0.90 (LLM-extracted)")

    # Group facts by section
    grouped = _group_by_section(facts)

    section_labels = {
        "mda": "MD&A Key Findings",
        "risk": "Risk Factors",
        "biz": "Business Description",
        "market_risk": "Market Risk Disclosures",
    }

    section_order = ["mda", "risk", "biz", "market_risk"]

    for key in section_order:
        group = grouped.get(key, [])
        if not group:
            continue

        label = section_labels.get(key, key)
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## {label} ({len(group)} facts extracted)")
        lines.append("")
        lines.append("| Fact Key | Value | Source Quote (excerpt) | Conf |")
        lines.append("|----------|-------|----------------------|------|")

        for f in group:
            fact_key = f.get("fact_key", "—")
            value = f.get("fact_value", "—")
            quote = f.get("source_quote", "")
            if len(quote) > 80:
                quote = quote[:77] + "..."
            # Escape pipe characters in table cells
            quote = quote.replace("|", "\\|")
            value = value.replace("|", "\\|")
            conf = f"{f['confidence']:.2f}" if f.get("confidence") else "—"
            lines.append(f"| {fact_key} | {value} | {quote} | {conf} |")

    # Include any ungrouped sections
    for key, group in grouped.items():
        if key in section_order:
            continue
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## Other: {key} ({len(group)} facts)")
        lines.append("")
        lines.append("| Fact Key | Value | Conf |")
        lines.append("|----------|-------|------|")
        for f in group:
            value = f.get("fact_value", "—").replace("|", "\\|")
            conf = f"{f['confidence']:.2f}" if f.get("confidence") else "—"
            lines.append(f"| {f.get('fact_key', '—')} | {value} | {conf} |")

    # Warnings
    lines.append("")
    lines.append("---")
    lines.append("")
    if warnings:
        lines.append("## Data Gaps & Warnings")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
    elif not facts:
        lines.append("## Data Gaps & Warnings")
        lines.append("")
        lines.append("- No narrative facts could be extracted from this filing.")
    else:
        lines.append("## Data Gaps & Warnings")
        lines.append("")
        lines.append("None — extraction completed successfully.")

    return "\n".join(lines) + "\n"
