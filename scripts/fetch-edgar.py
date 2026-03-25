#!/usr/bin/env python3
"""
fetch-edgar.py — Entry point for SEC EDGAR financial data extraction.

Delegates to scripts/sec_edgar package.

Usage:
    python3 scripts/fetch-edgar.py INTU
    python3 scripts/fetch-edgar.py INTU V NVO
    python3 scripts/fetch-edgar.py --force INTU
    python3 scripts/fetch-edgar.py --quiet INTU
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sec_edgar.__main__ import main

sys.exit(main())
