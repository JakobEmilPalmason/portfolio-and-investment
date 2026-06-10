#!/usr/bin/env python3
"""
Deterministic grader for evidence layer Skillgrade eval.

Validates that SEC EDGAR extraction and verification produced
expected output for a given ticker.

Usage: python3 check-evidence.py <ticker> <mode>
  mode: extract  — check XBRL extraction output
  mode: verify   — check verification run in DB
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

ticker = sys.argv[1] if len(sys.argv) > 1 else "SYK"
mode = sys.argv[2] if len(sys.argv) > 2 else "extract"

checks = []


def check(name, passed, msg):
    checks.append({"name": name, "passed": passed, "message": msg})


if mode == "extract":
    # -- Check XBRL extraction output --
    edgar_file = REPO_ROOT / "data" / "context" / ticker / "edgar-10k.md"
    check("edgar-file-exists", edgar_file.exists(),
          f"edgar-10k.md exists" if edgar_file.exists() else "edgar-10k.md missing")

    if edgar_file.exists():
        content = edgar_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        check("edgar-file-length", len(lines) > 30,
              f"{len(lines)} lines" if len(lines) > 30 else f"Only {len(lines)} lines")

        # Check expected sections
        check("has-key-metrics", "Key Financial Metrics" in content,
              "Key Financial Metrics section present" if "Key Financial Metrics" in content else "missing")
        check("has-income-stmt", "Income Statement" in content,
              "Income Statement present" if "Income Statement" in content else "missing")
        check("has-balance-sheet", "Balance Sheet" in content,
              "Balance Sheet present" if "Balance Sheet" in content else "missing")
        check("has-cash-flow", "Cash Flow" in content or "Operating Cash Flow" in content,
              "Cash flow data present")

        # Check revenue exists
        check("has-revenue", "Revenue" in content or "Net sales" in content,
              "Revenue data found")

    # Check DB for source document
    try:
        from src.database import Database
        from src.evidence import EvidenceDB

        with Database() as db:
            db.migrate()
            ev = EvidenceDB(db)
            docs = ev.get_source_documents_for_ticker(ticker)
            check("db-source-doc", len(docs) > 0,
                  f"{len(docs)} source document(s)" if docs else "No source documents in DB")

            if docs:
                facts = ev.get_facts_for_ticker(ticker, limit=2000)
                check("db-facts", len(facts) > 0,
                      f"{len(facts)} extracted facts" if facts else "No facts in DB")

                sections = ev.get_document_sections(docs[0]["id"])
                check("db-sections", len(sections) > 0,
                      f"{len(sections)} document sections" if sections else "No sections in DB")
    except Exception as e:
        check("db-access", False, f"DB error: {e}")

elif mode == "verify":
    # -- Check verification run --
    try:
        from src.database import Database
        from src.evidence import EvidenceDB

        with Database() as db:
            db.migrate()
            ev = EvidenceDB(db)

            # Check assertions exist
            assertions = ev.get_assertions_for_ticker(ticker)
            check("assertions-exist", len(assertions) > 0,
                  f"{len(assertions)} assertions" if assertions else "No assertions")

            if assertions:
                # Check umbrella coverage
                umbrellas = {a["umbrella_number"] for a in assertions}
                check("umbrella-coverage", len(umbrellas) >= 6,
                      f"{len(umbrellas)} umbrellas covered" if len(umbrellas) >= 6 else f"Only {len(umbrellas)}")

            # Check verification run
            summary = ev.get_ticker_evidence_summary(ticker)
            total = summary.get("total_assertions", 0)
            verified = summary.get("verified_assertions", 0) or 0
            coverage = summary.get("verification_coverage", 0) or 0
            check("has-assertions", total > 0,
                  f"{total} total assertions")

            if total > 0:
                check("verification-coverage", coverage > 0,
                      f"{coverage:.1%} verification coverage")
                check("has-verified", verified > 0,
                      f"{verified} verified assertions" if verified else "No verified assertions")

            # Check verification_runs table
            latest = ev.get_latest_verification_run(ticker)
            check("verification-run-exists", latest is not None,
                  "Verification run recorded" if latest else "No verification run found")

            if latest:
                score = latest.get("overall_score", 0)
                check("overall-score", score > 0,
                      f"Overall score: {score:.2f}")

    except Exception as e:
        check("db-access", False, f"DB error: {e}")

# Output
passed_count = sum(1 for c in checks if c["passed"])
total_count = len(checks)
score = round(passed_count / total_count, 2) if total_count else 0

print(json.dumps({
    "score": score,
    "details": f"{passed_count}/{total_count} checks passed ({mode} mode, ticker={ticker})",
    "checks": checks,
}))
