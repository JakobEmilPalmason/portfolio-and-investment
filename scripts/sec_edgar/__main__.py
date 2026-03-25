"""
CLI entry point for sec_edgar package.

Usage:
    python3 -m sec_edgar INTU V NVO            # Tier 1 (XBRL) only
    python3 -m sec_edgar --tier2 INTU V NVO    # Tier 1 + Tier 2 (LLM narrative)
    python3 -m sec_edgar --force INTU
    python3 -m sec_edgar --quiet INTU
"""

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .client import fetch_10k, fetch_filing_object, CONTEXT_DIR

logger = logging.getLogger(__name__)


def _fiscal_period_from_date(date_str: str) -> str:
    """Convert '2025-09-30' to 'FY2025'. Returns empty string on failure."""
    try:
        return f"FY{date_str[:4]}"
    except Exception:
        return ""


def _normalize_label(label: str) -> str:
    """Turn 'Revenue, Net' into 'revenue_net' for use as fact_key suffix."""
    import re
    s = label.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


# Unit classification for metrics and supplementary keys
_UNIT_MAP = {
    # Metrics (dollar amounts)
    "revenue": "USD", "operating_income": "USD", "net_income": "USD",
    "total_assets": "USD", "total_liabilities": "USD", "stockholders_equity": "USD",
    "current_assets": "USD", "current_liabilities": "USD",
    "operating_cash_flow": "USD", "capital_expenditures": "USD", "free_cash_flow": "USD",
    # Metrics (non-dollar)
    "shares_outstanding_basic": "count", "shares_outstanding_diluted": "count",
    "current_ratio": "ratio", "debt_to_assets": "ratio",
    # Supplementary
    "eps_basic": "USD", "eps_diluted": "USD",
    "gross_profit": "USD", "research_and_development": "USD",
    "selling_general_and_admin": "USD", "interest_expense": "USD",
    "depreciation": "USD", "amortization": "USD", "depreciation_and_amortization": "USD",
    "stock_based_compensation": "USD", "dividends_paid": "USD",
    "long_term_debt": "USD", "short_term_debt": "USD", "total_debt_lt_st": "USD",
}


def _load_xbrl_facts(
    ticker: str, extracted: dict, filing_metadata: dict, quiet: bool = False,
) -> int:
    """Load XBRL financial metrics as extracted_facts in the evidence DB.

    Returns the number of facts inserted.
    """
    import pandas as pd
    from .render import _fmt_amount, _fmt_per_share, _fmt_shares, _fmt_ratio

    repo_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(repo_root))
    from src.database import Database
    from src.evidence import EvidenceDB

    period_end = filing_metadata.get("period_of_report", "")
    fiscal_period = _fiscal_period_from_date(period_end)
    currency = extracted.get("currency", "$")
    run_id = f"xbrl-{ticker}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"

    with Database() as db:
        db.migrate()
        ev = EvidenceDB(db)

        # Reuse the same source_document as Tier 2 (UNIQUE on ticker+doc_type+period_end)
        doc_id = ev.upsert_source_document({
            "ticker": ticker,
            "doc_type": filing_metadata.get("form_type", "10-K"),
            "filing_date": filing_metadata.get("filing_date"),
            "period_end": period_end,
            "accession_number": filing_metadata.get("accession_no"),
            "source_url": (
                f"https://www.sec.gov/cgi-bin/browse-edgar"
                f"?action=getcompany&CIK={filing_metadata.get('cik')}"
            ),
            "local_path": str(CONTEXT_DIR / ticker / "edgar-10k.md"),
            "content_hash": None,
            "section_count": 0,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })

        # Clear old XBRL facts (safe re-run)
        ev.deactivate_xbrl_facts_for_document(doc_id)
        ev.delete_inactive_xbrl_facts(doc_id)

        facts: list[dict] = []

        def _make_fact(key: str, value: float, formatted: str, unit: str,
                       fp: str, quote: str) -> dict:
            return {
                "ticker": ticker,
                "source_document_id": doc_id,
                "document_section_id": None,
                "fact_type": "metric",
                "fact_key": key,
                "fact_value": formatted,
                "fact_value_numeric": float(value),
                "fact_unit": unit,
                "fiscal_period": fp,
                "confidence": 1.0,
                "extraction_method": "xbrl",
                "source_quote": quote,
                "source_char_offset_start": None,
                "source_char_offset_end": None,
                "computation_trace_json": None,
                "extraction_run_id": run_id,
                "is_active": 1,
            }

        def _fmt_value(key: str, value: float) -> str:
            """Format a metric value for human-readable fact_value."""
            unit = _UNIT_MAP.get(key, "USD")
            if unit == "ratio":
                return _fmt_ratio(value)
            if unit == "count":
                return _fmt_shares(value)
            if key.startswith("eps_") or (key in _UNIT_MAP and
                    _UNIT_MAP.get(key) == "USD" and abs(value) < 1000):
                return _fmt_per_share(value, currency)
            return _fmt_amount(value, currency)

        # --- 1. Metrics dict (15 keys, latest period) ---
        metrics = extracted.get("metrics", {})
        for key, value in metrics.items():
            if value is None:
                continue
            try:
                fval = float(value)
            except (TypeError, ValueError):
                continue
            unit = _UNIT_MAP.get(key, "USD")
            facts.append(_make_fact(
                f"xbrl.{key}", fval, _fmt_value(key, fval), unit,
                fiscal_period, f"get_financial_metrics().{key}",
            ))

        # --- 2. Supplementary dict (multi-year) ---
        supplementary = extracted.get("supplementary", {})
        for key, info in supplementary.items():
            years = info.get("years", {})
            concept = info.get("concept", "unknown")
            per_share = info.get("per_share", False)
            unit = _UNIT_MAP.get(key, "USD")
            for date_col, value in years.items():
                if value is None:
                    continue
                try:
                    fval = float(value)
                except (TypeError, ValueError):
                    continue
                fp = _fiscal_period_from_date(date_col)
                if per_share:
                    formatted = _fmt_per_share(fval, currency)
                else:
                    formatted = _fmt_value(key, fval)
                facts.append(_make_fact(
                    f"xbrl.{key}", fval, formatted, unit, fp, concept,
                ))

        # --- 3. Statement DataFrames (all line items × years) ---
        # Track fact_keys already added to avoid duplicates with metrics/supplementary
        seen = {(f["fact_key"], f["fiscal_period"]) for f in facts}

        stmt_map = [
            ("income", extracted.get("income_statement"), extracted.get("income_date_cols", [])),
            ("balance", extracted.get("balance_sheet"), extracted.get("balance_date_cols", [])),
            ("cashflow", extracted.get("cash_flow"), extracted.get("cash_flow_date_cols", [])),
        ]
        for stmt_prefix, df, date_cols in stmt_map:
            if df is None or (isinstance(df, pd.DataFrame) and df.empty) or not date_cols:
                continue
            for _, row in df.iterrows():
                concept = row.get("concept", "")
                label = row.get("label", concept)
                norm_label = _normalize_label(label)
                if not norm_label:
                    continue
                fact_key = f"xbrl.{stmt_prefix}.{norm_label}"
                # Infer unit from label
                label_lower = label.lower()
                if "per share" in label_lower:
                    unit = "USD"
                elif "shares" in label_lower or "share" in label_lower:
                    unit = "count"
                else:
                    unit = "USD"
                for dc in date_cols:
                    if dc not in row.index:
                        continue
                    val = row[dc]
                    if pd.isna(val):
                        continue
                    try:
                        fval = float(val)
                    except (TypeError, ValueError):
                        continue
                    fp = _fiscal_period_from_date(dc)
                    if (fact_key, fp) in seen:
                        continue
                    seen.add((fact_key, fp))
                    if unit == "count":
                        formatted = _fmt_shares(fval)
                    elif "per share" in label_lower:
                        formatted = _fmt_per_share(fval, currency)
                    else:
                        formatted = _fmt_amount(fval, currency)
                    facts.append(_make_fact(
                        fact_key, fval, formatted, unit, fp, concept,
                    ))

        if facts:
            ev.batch_insert_facts(facts)

        if not quiet:
            print(f"  {ticker} — XBRL: {len(facts)} facts loaded into evidence DB")

        return len(facts)


def _run_tier2(ticker: str, force: bool, quiet: bool) -> tuple[int, list[str]]:
    """Run Tier 2 narrative extraction for a ticker.

    Returns (fact_count, warnings).
    """
    from .sections import extract_sections
    from .llm_extract import extract_section_facts
    from .render_evidence import render_evidence_markdown

    # Lazy import to avoid circular deps and keep Tier 1 fast
    repo_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(repo_root))
    from src.database import Database
    from src.evidence import EvidenceDB

    # 1. Get filing object for section parsing
    filing_obj, filing_meta = fetch_filing_object(ticker, force=force, quiet=quiet)
    if filing_obj is None:
        return 0, [f"{ticker}: could not get filing object for Tier 2"]

    # 2. Parse sections
    sections, section_warnings = extract_sections(filing_obj, filing_meta["form_type"])
    if not sections:
        return 0, section_warnings

    # 3. Store sections in DB
    with Database() as db:
        db.migrate()
        ev = EvidenceDB(db)

        doc_id = ev.upsert_source_document({
            "ticker": ticker,
            "doc_type": filing_meta["form_type"],
            "filing_date": filing_meta.get("filing_date"),
            "period_end": filing_meta.get("period_of_report"),
            "accession_number": filing_meta.get("accession_no"),
            "source_url": (
                f"https://www.sec.gov/cgi-bin/browse-edgar"
                f"?action=getcompany&CIK={filing_meta.get('cik')}"
            ),
            "local_path": str(CONTEXT_DIR / ticker / "edgar-10k.md"),
            "content_hash": None,
            "section_count": len(sections),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })

        section_ids: dict[str, int] = {}
        for s in sections:
            s["source_document_id"] = doc_id
            sid = ev.upsert_document_section(s)
            section_ids[s["section_key"]] = sid

        # 4. LLM extraction per section
        run_id = f"tier2-{ticker}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        fiscal_period = _fiscal_period_from_date(
            filing_meta.get("period_of_report", "")
        )

        # Deactivate + delete old LLM facts to clear UNIQUE space for re-insertion.
        # Facts with assertion_evidence links survive (NOT IN subquery).
        ev.deactivate_llm_facts_for_document(doc_id)
        ev.delete_inactive_llm_facts(doc_id)

        all_facts: list[dict] = []
        for s in sections:
            sec_id = section_ids.get(s["section_key"])
            facts = extract_section_facts(
                s["content_text"],
                s["section_key"],
                ticker,
                fiscal_period,
                run_id,
                doc_id,
                sec_id,
                quiet=quiet,
            )
            all_facts.extend(facts)

        if all_facts:
            ev.batch_insert_facts(all_facts)

        # 5. Render markdown for agent context
        fiscal_year = fiscal_period if fiscal_period else "unknown"
        md = render_evidence_markdown(
            ticker, all_facts, filing_meta, section_warnings
        )
        out_dir = CONTEXT_DIR / ticker
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"evidence-10K-{fiscal_year}.md"
        out_file.write_text(md, encoding="utf-8")

        if not quiet:
            print(
                f"  {ticker} — Tier 2: {len(all_facts)} facts from "
                f"{len(sections)} sections -> {out_file.name}"
            )

        return len(all_facts), section_warnings


def main():
    parser = argparse.ArgumentParser(
        description="Fetch SEC EDGAR filing data for analysis agents"
    )
    parser.add_argument(
        "tickers", nargs="*", help="Ticker symbols (e.g., INTU V NVO)"
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-fetch even if <24h old"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress progress output"
    )
    parser.add_argument(
        "--tier2", action="store_true",
        help="Run LLM narrative extraction (Tier 2) after XBRL extraction"
    )
    parser.add_argument(
        "--xbrl-only", action="store_true",
        help="Load XBRL facts into evidence DB without running Tier 2"
    )
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers if t.strip()]
    if not tickers:
        parser.error("No tickers specified.")

    # Set up logging for Tier 2 or XBRL DB loading
    if args.tier2 or args.xbrl_only:
        logging.basicConfig(
            level=logging.WARNING if args.quiet else logging.INFO,
            format="%(message)s",
        )

    if not args.quiet:
        if args.xbrl_only:
            mode = "Tier 1 (XBRL) + evidence DB"
        elif args.tier2:
            mode = "Tier 1 + Tier 2"
        else:
            mode = "Tier 1 (XBRL)"
        print(f"Fetching SEC EDGAR data ({mode}) for {len(tickers)} ticker(s)...\n")

    ok = 0
    skipped = 0
    failed = 0
    xbrl_facts = 0
    tier2_facts = 0

    for i, ticker in enumerate(tickers):
        # Tier 1: XBRL extraction (existing behavior)
        try:
            result = fetch_10k(ticker, force=args.force, quiet=args.quiet)
            if result == "skipped":
                skipped += 1
            elif result is None:
                failed += 1
            else:
                ok += 1
        except Exception as e:
            if not args.quiet:
                print(f"  {ticker} — ERROR: {e}", file=sys.stderr)
            failed += 1
            continue  # Skip remaining tiers if Tier 1 failed

        # Load XBRL facts into evidence DB (when --xbrl-only or --tier2)
        if (args.xbrl_only or args.tier2) and result not in ("skipped", None):
            try:
                xbrl_count = _load_xbrl_facts(
                    ticker, result["financials"], result["filing_metadata"],
                    quiet=args.quiet,
                )
                xbrl_facts += xbrl_count
            except Exception as e:
                if not args.quiet:
                    print(f"  {ticker} — XBRL DB ERROR: {e}", file=sys.stderr)

        # Tier 2: LLM narrative extraction (opt-in, skip if --xbrl-only)
        if args.tier2 and not args.xbrl_only and result is not None:
            try:
                facts_count, warnings = _run_tier2(
                    ticker, force=args.force, quiet=args.quiet,
                )
                tier2_facts += facts_count
            except Exception as e:
                if not args.quiet:
                    print(
                        f"  {ticker} — Tier 2 ERROR: {e}", file=sys.stderr
                    )
                # Don't count as failure — Tier 1 already succeeded

    if not args.quiet:
        summary = f"\nDone: {ok} fetched, {skipped} skipped, {failed} failed"
        if xbrl_facts:
            summary += f", {xbrl_facts} XBRL facts loaded"
        if args.tier2 and not args.xbrl_only:
            summary += f", {tier2_facts} narrative facts extracted"
        print(summary)

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
