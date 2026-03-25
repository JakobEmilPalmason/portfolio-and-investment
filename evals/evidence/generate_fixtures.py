#!/usr/bin/env python3
"""One-time golden fixture generator for evidence eval tests.

Reads live DB (db/portfolio.db) and serializes SYK evidence data
into JSON fixtures for deterministic testing.

Usage:
    python3 evals/evidence/generate_fixtures.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.database import Database
from src.evidence import EvidenceDB

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
TICKER = "SYK"


def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    with Database() as db:
        db.migrate()
        ev = EvidenceDB(db)

        # 1. Source documents
        docs = ev.get_source_documents_for_ticker(TICKER)
        if not docs:
            print(f"ERROR: no source documents for {TICKER}")
            return 1
        print(f"Source docs: {len(docs)}")

        # 2. Document sections (for citation validity tests)
        sections = []
        for doc in docs:
            doc_sections = ev.get_document_sections(doc["id"])
            for s in doc_sections:
                sections.append({
                    "section_id": s["id"],
                    "source_document_id": s["source_document_id"],
                    "section_key": s["section_key"],
                    "section_title": s.get("section_title", ""),
                    "section_order": s.get("section_order", 0),
                    "content_text": s["content_text"],
                    "content_hash": s.get("content_hash", ""),
                    "token_estimate": s.get("token_estimate", 0),
                })
            print(f"  doc {doc['id']}: {len(doc_sections)} sections")

        out = FIXTURES_DIR / "golden-syk-sections.json"
        out.write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {out.name} ({len(sections)} sections)")

        # 3. Extracted facts
        facts = ev.get_facts_for_ticker(TICKER, limit=2000)
        fact_records = []
        for f in facts:
            fact_records.append({
                "fact_id": f["id"],
                "ticker": f["ticker"],
                "source_document_id": f["source_document_id"],
                "document_section_id": f["document_section_id"],
                "fact_type": f["fact_type"],
                "fact_key": f["fact_key"],
                "fact_value": f["fact_value"],
                "fact_value_numeric": f["fact_value_numeric"],
                "fact_unit": f["fact_unit"],
                "fiscal_period": f.get("fiscal_period", ""),
                "confidence": f["confidence"],
                "extraction_method": f["extraction_method"],
                "source_quote": f.get("source_quote", ""),
                "source_char_offset_start": f.get("source_char_offset_start"),
                "source_char_offset_end": f.get("source_char_offset_end"),
                "is_active": f.get("is_active", 1),
            })

        out = FIXTURES_DIR / "golden-syk-facts.json"
        out.write_text(json.dumps(fact_records, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {out.name} ({len(fact_records)} facts)")

        # 4. Assertions (if any)
        assertions = ev.get_assertions_for_ticker(TICKER)
        assertion_records = []
        for a in assertions:
            assertion_records.append({
                "assertion_id": a["id"],
                "ticker": a["ticker"],
                "report_path": a.get("report_path", ""),
                "umbrella_number": a["umbrella_number"],
                "assertion_text": a["assertion_text"],
                "assertion_type": a["assertion_type"],
                "category": a.get("category", ""),
                "requires_arithmetic": a.get("requires_arithmetic", 0),
            })

        out = FIXTURES_DIR / "golden-syk-assertions.json"
        out.write_text(json.dumps(assertion_records, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {out.name} ({len(assertion_records)} assertions)")

    print("\nDone. Review fixtures in evals/evidence/fixtures/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
