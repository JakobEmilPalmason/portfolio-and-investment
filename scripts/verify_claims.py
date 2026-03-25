"""
CLI entry point for Phase 4 post-analysis verification.

Usage:
    python3 scripts/verify_claims.py TICKER
    python3 scripts/verify_claims.py TICKER --report-dir runs/week12_16.03/reports/SYK
    python3 scripts/verify_claims.py TICKER --quiet
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.database import Database
from src.evidence import EvidenceDB

from scripts.sec_edgar.claim_decomposer import decompose_report
from scripts.sec_edgar.fact_checker import verify_assertions

logger = logging.getLogger(__name__)


def _find_latest_report(ticker: str) -> Path | None:
    """Find the most recent report directory for a ticker.

    Scans runs/week*/reports/{TICKER}/ sorted by week number descending.
    Returns the first directory containing at least one .md section file.
    """
    runs_dir = REPO_ROOT / "runs"
    if not runs_dir.exists():
        return None

    week_dirs = sorted(runs_dir.glob("week*"), reverse=True)
    for week_dir in week_dirs:
        report_dir = week_dir / "reports" / ticker
        if report_dir.exists():
            md_files = list(report_dir.glob("0*.md"))
            if md_files:
                return report_dir

    return None


def _print_summary(ticker: str, summary: dict, stored_assertions: list[dict]):
    """Print human-readable verification summary to stdout."""
    total = summary.get("total_assertions", 0)
    verified = summary.get("verified_count", 0)
    supported = summary.get("supported_count", 0)
    contradicted = summary.get("contradicted_count", 0)
    partial = summary.get("partial_count", 0)
    unverifiable_count = total - verified

    coverage = verified / total if total > 0 else 0.0

    print(f"\nVerification: {ticker} ({datetime.now().strftime('%Y-%m-%d')})")
    print("\u2501" * 40)
    print(f"Assertions:    {total}")
    print(f"Verified:      {verified} ({coverage:.1%})")
    print(f"  Supported:   {supported}")
    print(f"  Partial:      {partial}")
    print(f"  Contradicted: {contradicted}")
    print(f"Unverifiable:   {unverifiable_count}")

    # Show contradictions
    if contradicted > 0:
        print(f"\nContradictions:")
        # We'd need to query assertion_evidence for details, but the summary
        # gives us the count. Detailed view is in the DB.
        print(f"  ({contradicted} assertion(s) contradicted by evidence — query DB for details)")

    print(f"\nOverall coverage: {coverage:.2f}")
    print()


def verify_ticker(
    ticker: str,
    report_dir: Path | None = None,
    quiet: bool = False,
) -> dict:
    """Run full verification pipeline for a ticker.

    Returns verification summary dict.
    """
    # 1. Locate report
    if report_dir is None:
        report_dir = _find_latest_report(ticker)
    if report_dir is None or not report_dir.exists():
        msg = f"No report found for {ticker}"
        if not quiet:
            print(f"ERROR: {msg}")
        return {"error": msg}

    if not quiet:
        print(f"Verifying: {ticker}")
        print(f"Report:    {report_dir}")

    # 2. Decompose: extract assertions from sections 01-08
    if not quiet:
        print("Pass A: Decomposing report into assertions...")
    assertions = decompose_report(report_dir, ticker)
    if not assertions:
        msg = "No assertions extracted"
        if not quiet:
            print(f"WARNING: {msg}")
        return {"error": msg}

    if not quiet:
        print(f"  {len(assertions)} assertions extracted")

    # 3. Store assertions in DB
    with Database() as db:
        db.migrate()
        ev = EvidenceDB(db)

        # Clear previous assertions for this report (idempotent re-runs)
        report_path = str(report_dir / "FINAL-REPORT.md")
        deleted = ev.delete_assertions_for_report(report_path)
        if deleted and not quiet:
            print(f"  Cleared {deleted} previous assertions")

        ev.batch_insert_assertions(assertions)
        stored = ev.get_assertions_for_ticker(ticker)
        # Filter to only this report's assertions
        stored = [a for a in stored if a.get("report_path") == report_path]

        if not quiet:
            print(f"  {len(stored)} assertions stored in DB")

        # 4. Get all extracted facts for this ticker
        all_facts = ev.get_facts_for_ticker(ticker, limit=1000)

        if not all_facts:
            if not quiet:
                print("  WARNING: No extracted facts found — all assertions unverifiable")
                print("  Run Phase 2 extraction first: ./run.sh extract TICKER")
        else:
            if not quiet:
                print(f"  {len(all_facts)} extracted facts available")
                print("Pass B: Verifying assertions against evidence...")

            # 5. Verify assertions against evidence
            evidence_links = verify_assertions(stored, all_facts, ticker, quiet=quiet)
            for link in evidence_links:
                try:
                    ev.insert_assertion_evidence(link)
                except Exception as exc:
                    logger.warning("Failed to insert evidence link: %s", exc)

            if not quiet:
                print(f"  {len(evidence_links)} evidence links created")

        # 6. Compute and store verification run
        run_id = f"verify-{ticker}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        summary = ev.get_evidence_summary_for_ticker(ticker)

        ev.insert_verification_run({
            "run_id": run_id,
            "ticker": ticker,
            "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_assertions": summary["total_assertions"],
            "verified_count": summary["verified_count"],
            "supported_count": summary["supported_count"],
            "contradicted_count": summary["contradicted_count"],
            "unverifiable_count": summary.get("unverifiable_count", 0),
            "overall_score": (
                summary["verified_count"] / summary["total_assertions"]
                if summary["total_assertions"] > 0
                else 0.0
            ),
            "run_metadata_json": json.dumps({
                "report_dir": str(report_dir),
                "fact_count": len(all_facts) if all_facts else 0,
                "phase": 4,
            }),
        })

        # 8. Print summary
        if not quiet:
            _print_summary(ticker, summary, stored)

        return summary


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4: Verify analysis report claims against SEC filing evidence",
    )
    parser.add_argument("ticker", help="Ticker symbol")
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Override report directory (default: latest)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress stdout output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print summary as JSON (last line of stdout)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    result = verify_ticker(args.ticker, args.report_dir, args.quiet)
    if args.json and "error" not in result:
        print(json.dumps(result))
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
