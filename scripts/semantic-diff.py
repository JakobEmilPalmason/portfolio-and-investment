"""
Semantic diff CLI — compare extracted evidence across filing periods.

Usage:
    python3 scripts/semantic-diff.py V                              # auto-detect periods
    python3 scripts/semantic-diff.py V --period-a FY2024 --period-b FY2025
    python3 scripts/semantic-diff.py V --force                      # re-run, replacing existing diffs
    python3 scripts/semantic-diff.py V --quiet

Phase 6 of the evidence extraction masterplan.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve repo root so imports work regardless of working directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from src.database import Database
from src.evidence import EvidenceDB
from sec_edgar.semantic_differ import diff_numeric_facts, diff_narrative_sections

logger = logging.getLogger(__name__)

CONTEXT_DIR = REPO_ROOT / "context"


# ---------------------------------------------------------------------------
# Period resolution
# ---------------------------------------------------------------------------

def _fiscal_period_from_date(date_str: str) -> str:
    """Convert '2025-09-30' to 'FY2025'."""
    try:
        return f"FY{date_str[:4]}"
    except Exception:
        return ""


def _resolve_periods(ev: EvidenceDB, ticker: str) -> tuple[str, str] | None:
    """Auto-detect the two most recent fiscal periods for a ticker.

    Returns (period_a, period_b) where A is older, or None if < 2 periods exist.
    """
    docs = ev.get_source_documents_for_ticker(ticker)
    if len(docs) < 2:
        return None

    # Derive unique fiscal periods from period_end, sorted ascending
    periods = sorted({
        _fiscal_period_from_date(d["period_end"])
        for d in docs
        if d.get("period_end")
    })
    periods = [p for p in periods if p]  # remove empty strings

    if len(periods) < 2:
        return None

    return periods[-2], periods[-1]


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _render_changes_markdown(
    ticker: str,
    period_a: str,
    period_b: str,
    numeric_diffs: list[dict],
    narrative_diffs: list[dict],
) -> str:
    """Render diff results as markdown for context/{TICKER}/evidence-changes.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    all_diffs = sorted(
        numeric_diffs + narrative_diffs,
        key=lambda d: d.get("significance", 0),
        reverse=True,
    )

    lines: list[str] = []
    lines.append(f"# Evidence Changes: {ticker} ({period_a} -> {period_b})")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Periods compared:** {period_a} vs {period_b}")
    lines.append(f"**Total changes:** {len(all_diffs)} ({len(numeric_diffs)} numeric, {len(narrative_diffs)} narrative)")

    # High-significance summary
    high_sig = [d for d in all_diffs if d.get("significance", 0) >= 4]
    if high_sig:
        lines.append("")
        lines.append(f"## High-Significance Changes ({len(high_sig)})")
        lines.append("")
        for d in high_sig:
            sig = d.get("significance", 0)
            lines.append(f"- **[{sig}/5]** {d['summary']}")

    # Numeric changes
    if numeric_diffs:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## Numeric Changes ({len(numeric_diffs)})")
        lines.append("")
        lines.append("| Fact Key | Period A | Period B | Change | Sig |")
        lines.append("|----------|----------|----------|--------|-----|")

        for d in sorted(numeric_diffs, key=lambda x: x.get("significance", 0), reverse=True):
            detail = json.loads(d.get("detail_json", "{}"))
            fact_key = detail.get("fact_key", "—")
            val_a = detail.get("value_a", "—")
            val_b = detail.get("value_b", "—")
            pct = detail.get("delta_percent")
            change_str = f"{pct:+.1%}" if pct is not None else "—"
            sig = d.get("significance", 0)
            lines.append(f"| {fact_key} | {val_a} | {val_b} | {change_str} | {sig}/5 |")

    # Narrative changes
    if narrative_diffs:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## Narrative Changes ({len(narrative_diffs)})")
        lines.append("")

        # Group by section
        by_section: dict[str, list[dict]] = {}
        for d in narrative_diffs:
            by_section.setdefault(d["section_key"], []).append(d)

        for section_key in sorted(by_section.keys()):
            section_diffs = sorted(
                by_section[section_key],
                key=lambda x: x.get("significance", 0),
                reverse=True,
            )
            lines.append(f"### {section_key} ({len(section_diffs)} changes)")
            lines.append("")
            for d in section_diffs:
                sig = d.get("significance", 0)
                dtype = d.get("diff_type", "")
                lines.append(f"- **[{sig}/5] [{dtype}]** {d['summary']}")
                detail = json.loads(d.get("detail_json", "{}"))
                qa = detail.get("quote_period_a", "")
                qb = detail.get("quote_period_b", "")
                if qa:
                    lines.append(f"  - {period_a}: \"{qa}\"")
                if qb:
                    lines.append(f"  - {period_b}: \"{qb}\"")
            lines.append("")

    if not all_diffs:
        lines.append("")
        lines.append("No material changes detected between these periods.")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare extracted evidence across filing periods"
    )
    parser.add_argument("ticker", help="Ticker symbol (e.g., V, INTU)")
    parser.add_argument("--period-a", help="Earlier fiscal period (e.g., FY2024)")
    parser.add_argument("--period-b", help="Later fiscal period (e.g., FY2025)")
    parser.add_argument("--force", action="store_true", help="Delete existing diffs and re-run")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    ticker = args.ticker.strip().upper()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(message)s",
    )

    with Database() as db:
        db.migrate()
        ev = EvidenceDB(db)

        # Resolve periods
        if args.period_a and args.period_b:
            period_a, period_b = args.period_a, args.period_b
        else:
            resolved = _resolve_periods(ev, ticker)
            if resolved is None:
                print(f"{ticker}: only one filing period found — nothing to diff")
                return 0
            period_a, period_b = resolved
            if not args.quiet:
                print(f"Auto-detected periods: {period_a} -> {period_b}")

        # Check for existing diffs
        existing = ev.get_diffs_between_periods(ticker, period_a, period_b)
        if existing and not args.force:
            print(
                f"{ticker}: {len(existing)} diffs already exist for "
                f"{period_a} -> {period_b}. Use --force to re-run."
            )
            return 0

        if args.force and existing:
            deleted = ev.delete_diffs_between_periods(ticker, period_a, period_b)
            if not args.quiet:
                print(f"Deleted {deleted} existing diffs")

        # Get facts for both periods
        if not args.quiet:
            print(f"\n{ticker}: diffing {period_a} -> {period_b}")

        facts_a = ev.get_facts_for_ticker(ticker, fiscal_period=period_a, limit=1000)
        facts_b = ev.get_facts_for_ticker(ticker, fiscal_period=period_b, limit=1000)

        # Numeric diff
        if not args.quiet:
            print(f"\nNumeric diff: {len(facts_a)} facts ({period_a}) vs {len(facts_b)} facts ({period_b})")

        numeric_diffs = diff_numeric_facts(facts_a, facts_b, period_a, period_b, ticker)

        if not args.quiet:
            print(f"  {len(numeric_diffs)} numeric changes found")

        # Narrative diff — get document sections for both periods
        docs_a = ev.get_source_documents_for_ticker(ticker)
        docs_b = docs_a  # same query — filter by period below

        sections_a: list[dict] = []
        sections_b: list[dict] = []

        for doc in docs_a:
            fp = _fiscal_period_from_date(doc.get("period_end", ""))
            if fp == period_a:
                sections_a = ev.get_document_sections(doc["id"])
            elif fp == period_b:
                sections_b = ev.get_document_sections(doc["id"])

        narrative_diffs: list[dict] = []
        if sections_a and sections_b:
            if not args.quiet:
                print(
                    f"\nNarrative diff: {len(sections_a)} sections ({period_a}) "
                    f"vs {len(sections_b)} sections ({period_b})"
                )
            narrative_diffs = diff_narrative_sections(
                sections_a, sections_b, period_a, period_b, ticker, quiet=args.quiet,
            )
            if not args.quiet:
                print(f"  {len(narrative_diffs)} narrative changes found")
        elif not args.quiet:
            print("\nNo document sections found for narrative diff — skipping")

        # Insert all diffs into DB
        all_diffs = numeric_diffs + narrative_diffs
        for d in all_diffs:
            ev.insert_semantic_diff(d)

        # Render markdown
        md = _render_changes_markdown(ticker, period_a, period_b, numeric_diffs, narrative_diffs)
        out_dir = CONTEXT_DIR / ticker
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "evidence-changes.md"
        out_file.write_text(md, encoding="utf-8")

        # Summary
        high_sig = sum(1 for d in all_diffs if d.get("significance", 0) >= 4)
        print(
            f"\nDone: {len(numeric_diffs)} numeric + {len(narrative_diffs)} narrative = "
            f"{len(all_diffs)} total diffs ({high_sig} high-significance)"
        )
        print(f"Output: {out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
