#!/usr/bin/env python3
"""
Batch IV backfill using claude --print for extraction.

For each ticker with a section 06 report:
  1. Passes section 06 content to claude --print → extracts IV as JSON
  2. Appends the structured IV Summary table to section 06
  3. Patches FINAL-REPORT.json with iv_conservative, iv_base, iv_bull, iv_currency, mos_at_analysis
  4. Validates the result

Usage:
    python3 scripts/batch-revalue.py                    # all reports
    python3 scripts/batch-revalue.py V MA MSFT           # specific tickers
    python3 scripts/batch-revalue.py --dry-run           # preview
    python3 scripts/batch-revalue.py --workers 6         # more parallelism
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "runs"

EXTRACTION_PROMPT = """\
You are a data extraction assistant. Below is a valuation analysis section for {ticker}.
Your ONLY job is to extract numeric intrinsic value estimates and output valid JSON.

<section_06>
{content}
</section_06>

Extract the bear-case, base-case, and bull-case DISCOUNTED per-share intrinsic value estimates.

RULES:
- Use the DISCOUNTED value (after "discount at/by X%" or "discounted at X%"), NOT the undiscounted multiple result.
- If there are multiple discounted figures in a scenario (e.g. a range), use the MORE CONSERVATIVE (lower for bear/base, lower for bull).
- Values must be per-share, not total company value. If you see billions, that's total — look for the per-share figure nearby.
- Currency: use the currency of the stock's primary listing (e.g. USD for US stocks, EUR for Euronext, CAD for TSX, DKK for Copenhagen, GBP for London, SEK for Stockholm).
- current_price: the stock price mentioned in the analysis text at time of writing.
- mos_pct: (iv_conservative - current_price) / iv_conservative * 100. Positive = stock is cheap.
- If a scenario value genuinely cannot be found, use null.

Output ONLY this JSON object — no markdown fences, no explanation, no extra text:
{{"iv_conservative": <number|null>, "iv_base": <number|null>, "iv_bull": <number|null>, "currency": "<ISO>", "current_price": <number|null>, "mos_pct": <number|null>}}
"""

IV_TABLE_TEMPLATE = """
## Intrinsic Value Summary

| Field | Value |
|-------|-------|
| IV Conservative (Bear) | {iv_conservative} |
| IV Base | {iv_base} |
| IV Bull | {iv_bull} |
| Currency | {currency} |
| MOS at Analysis Date | {mos_pct} |
"""


def find_reports(tickers: list[str] | None) -> list[dict]:
    """Find all report directories with section 06 and FINAL-REPORT.json."""
    # Group by ticker, keep latest
    latest: dict[str, dict] = {}
    for json_path in sorted(RUNS_DIR.glob("*/reports/*/FINAL-REPORT.json")):
        ticker = json_path.parent.name
        sec06 = json_path.parent / "06-valuation-intrinsic-value.md"
        if not sec06.exists():
            continue
        mtime = json_path.stat().st_mtime
        if ticker not in latest or mtime > latest[ticker]["mtime"]:
            latest[ticker] = {
                "ticker": ticker,
                "report_dir": json_path.parent,
                "json_path": json_path,
                "sec06_path": sec06,
                "mtime": mtime,
            }

    results = []
    for ticker in sorted(latest):
        if tickers and ticker not in tickers:
            continue
        results.append(latest[ticker])
    return results


def already_has_table(sec06_path: Path) -> bool:
    """Check if section 06 already has the IV Summary table."""
    text = sec06_path.read_text()
    return "## Intrinsic Value Summary" in text


def extract_iv_via_claude(ticker: str, sec06_content: str, max_retries: int = 2) -> dict | None:
    """Run claude --print to extract IV values from section 06 prose."""
    prompt = EXTRACTION_PROMPT.format(ticker=ticker, content=sec06_content)

    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                ["claude", "--print", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return None

            output = result.stdout.strip()
            # Strip markdown fences if present
            if output.startswith("```"):
                lines = output.split("\n")
                output = "\n".join(
                    l for l in lines if not l.startswith("```")
                ).strip()

            data = json.loads(output)
            # Basic validation
            if not isinstance(data, dict):
                if attempt < max_retries:
                    continue
                return None

            return data

        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            return None

    return None


def validate_iv_values(data: dict, ticker: str) -> list[str]:
    """Sanity-check extracted IV values. Returns list of warnings."""
    warnings = []
    iv_c = data.get("iv_conservative")
    iv_b = data.get("iv_base")
    iv_bull = data.get("iv_bull")
    price = data.get("current_price")

    if iv_c is None and iv_b is None:
        warnings.append("both iv_conservative and iv_base are null")
        return warnings

    # Values should be positive
    for label, val in [("bear", iv_c), ("base", iv_b), ("bull", iv_bull)]:
        if val is not None and val <= 0:
            warnings.append(f"{label} IV is non-positive: {val}")

    # Bear < Base < Bull (when all present)
    vals = [v for v in [iv_c, iv_b, iv_bull] if v is not None]
    if len(vals) >= 2 and vals != sorted(vals):
        warnings.append(f"IV ordering unexpected: bear={iv_c}, base={iv_b}, bull={iv_bull}")

    # Price sanity
    if price is not None and price > 0 and iv_c is not None and iv_c > 0:
        ratio = price / iv_c
        if ratio > 10 or ratio < 0.1:
            warnings.append(f"price/iv_conservative ratio extreme: {ratio:.1f}")

    return warnings


def append_table_to_sec06(sec06_path: Path, data: dict) -> None:
    """Append the IV Summary table to section 06."""
    def fmt(val):
        if val is None:
            return "N/A"
        if isinstance(val, float):
            return f"{val:.2f}" if val != int(val) else str(int(val))
        return str(val)

    table = IV_TABLE_TEMPLATE.format(
        iv_conservative=fmt(data.get("iv_conservative")),
        iv_base=fmt(data.get("iv_base")),
        iv_bull=fmt(data.get("iv_bull")),
        currency=data.get("currency", "USD"),
        mos_pct=fmt(data.get("mos_pct")),
    )

    with open(sec06_path, "a") as f:
        f.write(table)


def patch_final_report_json(json_path: Path, data: dict) -> None:
    """Patch FINAL-REPORT.json with IV fields."""
    with open(json_path) as f:
        report = json.load(f)

    for key in ("iv_conservative", "iv_base", "iv_bull"):
        val = data.get(key)
        report[key] = round(val, 2) if val is not None else None

    report["iv_currency"] = data.get("currency")

    mos = data.get("mos_pct")
    report["mos_at_analysis"] = round(mos, 1) if mos is not None else None

    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")


def process_one(entry: dict, dry_run: bool) -> dict:
    """Process a single ticker: extract IV, append table, patch JSON."""
    ticker = entry["ticker"]
    sec06_path = entry["sec06_path"]
    json_path = entry["json_path"]

    # Check if already done
    if already_has_table(sec06_path):
        # Even if table exists, check if JSON is patched
        with open(json_path) as f:
            report = json.load(f)
        if report.get("iv_conservative") is not None:
            return {"ticker": ticker, "status": "skip", "reason": "already done"}

    sec06_content = sec06_path.read_text()

    # Extract via claude
    data = extract_iv_via_claude(ticker, sec06_content)
    if data is None:
        return {"ticker": ticker, "status": "fail", "reason": "claude extraction failed"}

    # Validate
    warnings = validate_iv_values(data, ticker)
    if any("both" in w for w in warnings):
        return {"ticker": ticker, "status": "fail", "reason": "no IV values extracted", "data": data}

    if not dry_run:
        # Append table to section 06 (only if not already there)
        if not already_has_table(sec06_path):
            append_table_to_sec06(sec06_path, data)

        # Patch FINAL-REPORT.json
        patch_final_report_json(json_path, data)

    return {
        "ticker": ticker,
        "status": "ok",
        "iv_conservative": data.get("iv_conservative"),
        "iv_base": data.get("iv_base"),
        "iv_bull": data.get("iv_bull"),
        "currency": data.get("currency"),
        "mos_pct": data.get("mos_pct"),
        "price": data.get("current_price"),
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Batch IV backfill via claude --print")
    parser.add_argument("tickers", nargs="*", help="Specific tickers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--force", action="store_true", help="Re-extract even if already done")
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers] if args.tickers else None
    reports = find_reports(tickers)

    if not reports:
        print("No reports found.")
        sys.exit(1)

    # If force, remove existing tables first
    if args.force:
        for entry in reports:
            sec06 = entry["sec06_path"]
            text = sec06.read_text()
            if "## Intrinsic Value Summary" in text:
                cleaned = text[:text.index("\n## Intrinsic Value Summary")]
                if not args.dry_run:
                    sec06.write_text(cleaned)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"{'=' * 60}")
    print(f"  IV Backfill — {mode} — {len(reports)} reports — {args.workers} workers")
    print(f"{'=' * 60}\n")

    ok_count = skip_count = fail_count = warn_count = 0
    results = []

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(process_one, entry, args.dry_run): entry
            for entry in reports
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            ticker = result["ticker"]

            if result["status"] == "skip":
                print(f"  {ticker:12s}  SKIP   {result.get('reason', '')}")
                skip_count += 1
            elif result["status"] == "ok":
                warnings = result.get("warnings", [])
                w_tag = f"  ⚠ {'; '.join(warnings)}" if warnings else ""
                if warnings:
                    warn_count += 1
                print(
                    f"  {ticker:12s}  OK     "
                    f"bear={result['iv_conservative']}  "
                    f"base={result['iv_base']}  "
                    f"bull={result['iv_bull']}  "
                    f"mos={result['mos_pct']}%  "
                    f"({result['currency']})"
                    f"{w_tag}"
                )
                ok_count += 1
            else:
                print(f"  {ticker:12s}  FAIL   {result.get('reason', '?')}")
                fail_count += 1

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"  Done in {elapsed:.0f}s: {ok_count} OK, {skip_count} skipped, {fail_count} failed, {warn_count} warnings")
    if args.dry_run:
        print(f"  (dry run — no files modified)")
    print(f"{'=' * 60}")

    # Final validation pass
    if not args.dry_run and ok_count > 0:
        print(f"\n  Validating FINAL-REPORT.json files...")
        valid = 0
        missing_iv = []
        for entry in reports:
            with open(entry["json_path"]) as f:
                report = json.load(f)
            if report.get("iv_conservative") is not None:
                valid += 1
            else:
                missing_iv.append(entry["ticker"])
        print(f"  {valid}/{len(reports)} reports have iv_conservative populated")
        if missing_iv:
            print(f"  Missing: {', '.join(missing_iv)}")

    if fail_count > 0:
        failed_tickers = [r["ticker"] for r in results if r["status"] == "fail"]
        print(f"\n  Failed tickers: {', '.join(failed_tickers)}")
        print(f"  Re-run with: python3 scripts/batch-revalue.py {' '.join(failed_tickers)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
