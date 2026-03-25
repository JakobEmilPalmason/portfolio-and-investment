"""Shared pytest fixtures for evidence eval tests.

Loads golden fixture data from evals/evidence/fixtures/.
All test files in this directory use these fixtures.
"""

import json
import sys
from pathlib import Path

# unittest discovery needs repo root on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict | list:
    """Load a JSON fixture by filename."""
    path = FIXTURES_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Fixture not found: {path}\n"
            f"Run: python3 evals/evidence/generate_fixtures.py"
        )
    return json.loads(path.read_text(encoding="utf-8"))


# Pre-load fixtures at module level for all tests
GOLDEN_FACTS = load_fixture("golden-syk-facts.json")
GOLDEN_SECTIONS = load_fixture("golden-syk-sections.json")
GOLDEN_XBRL = load_fixture("golden-syk-xbrl.json")
GOLDEN_ASSERTIONS = load_fixture("golden-syk-assertions.json")

# Build section lookup by section_id for citation tests
SECTION_BY_ID = {s["section_id"]: s for s in GOLDEN_SECTIONS}
