#!/usr/bin/env python3
"""
prebuy-check.py — Pre-buy checklist for a single ticker or all Own-verdict tickers.

Checks 3 conditions before a paper-trade buy:
  C1 — Quality gate (verdict, score, no weak umbrellas, MOS score)
  C2 — Price vs IV (current price <= iv_conservative * (1 - threshold/100))
  C3 — 3-sentence conviction check (interactive, single-ticker only)

Usage:
    python3 scripts/prebuy-check.py GILD
    python3 scripts/prebuy-check.py GILD --dry-run-buy
    python3 scripts/prebuy-check.py --own
    python3 scripts/prebuy-check.py GILD --capital 250000
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "queue" / "queue.json"
RUNS_DIR = REPO_ROOT / "runs"
CONFIG_FILE = REPO_ROOT / "portfolio" / "config.json"
PENDING_DIR = REPO_ROOT / "portfolio" / "pending"

DEFAULT_CONFIG = {
    "capital_base": 100_000,
    "prebuy_min_score": 7.0,
    "prebuy_min_mos_score": 6,
    "prebuy_mos_threshold_pct": 20,
}

POSITION_PCT = 0.03  # 3% position size — not configurable in this version


def load_config(capital_override: float | None = None) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                file_cfg = json.load(f)
            for k in DEFAULT_CONFIG:
                if k in file_cfg:
                    cfg[k] = file_cfg[k]
        except (json.JSONDecodeError, OSError):
            pass
    if capital_override is not None:
        cfg["capital_base"] = capital_override
    return cfg


def load_report(ticker: str) -> tuple[dict | None, Path | None]:
    """Return (report_dict, report_path) for the most-recently-modified FINAL-REPORT.json."""
    candidates = list(RUNS_DIR.glob(f"*/reports/{ticker}/FINAL-REPORT.json"))
    if not candidates:
        return None, None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest) as f:
            return json.load(f), latest
    except (json.JSONDecodeError, OSError):
        return None, None


def get_current_price(ticker: str) -> tuple[float | None, str | None, str | None]:
    """
    Return (price, last_close_date_str, yfinance_currency).
    Uses history(period='5d') to get last close — avoids implying intraday precision.
    """
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist.empty:
            return None, None, None
        last_close = hist["Close"].iloc[-1]
        last_date = hist.index[-1]
        # index is DatetimeIndex; format as YYYY-MM-DD
        if hasattr(last_date, "date"):
            date_str = last_date.date().isoformat()
        else:
            date_str = str(last_date)[:10]
        currency = None
        try:
            currency = t.info.get("currency")
        except Exception:
            pass
        return float(last_close), date_str, currency
    except ImportError:
        print("  [WARN] yfinance not installed. Install with: pip install yfinance")
        return None, None, None
    except Exception as e:
        print(f"  [WARN] Could not fetch price for {ticker}: {e}")
        return None, None, None


def report_age_days(report_path: Path) -> int:
    analysis_date_str = None
    try:
        with open(report_path) as f:
            data = json.load(f)
        analysis_date_str = data.get("analysis_date")
    except Exception:
        pass
    if analysis_date_str:
        try:
            analysis_date = date.fromisoformat(analysis_date_str)
            return (date.today() - analysis_date).days
        except ValueError:
            pass
    # Fallback: file mtime
    mtime = report_path.stat().st_mtime
    file_date = date.fromtimestamp(mtime)
    return (date.today() - file_date).days


def check_condition_1(report: dict, config: dict) -> tuple[bool | None, str]:
    """
    C1 — Quality gate.
    Pass: verdict=Own, avg >= min_score, no umbrella < 4, margin_of_safety >= min_mos_score.
    Returns (pass/fail/None, detail_str). None = data missing.
    """
    verdict = report.get("verdict")
    if not verdict:
        return None, "verdict field missing from report"

    avg = report.get("average_score")
    if avg is None:
        return None, "average_score missing from report"

    umbrella_scores = report.get("umbrella_scores", {})
    mos_score = umbrella_scores.get("margin_of_safety")

    min_score = config["prebuy_min_score"]
    min_mos = config["prebuy_min_mos_score"]

    failures = []

    if verdict not in ("Own", "Watch"):
        failures.append(f"verdict={verdict} (need Own or Watch)")

    if float(avg) < min_score:
        failures.append(f"avg={avg} < {min_score}")

    min_umbrella = None
    min_umbrella_name = None
    for k, v in umbrella_scores.items():
        if v is not None:
            if min_umbrella is None or v < min_umbrella:
                min_umbrella = v
                min_umbrella_name = k

    if min_umbrella is not None and min_umbrella < 4:
        failures.append(f"umbrella {min_umbrella_name}={min_umbrella} < 4")

    if mos_score is None:
        failures.append("margin_of_safety score missing")
    elif mos_score < min_mos:
        failures.append(f"mos_score={mos_score} < {min_mos}")

    if failures:
        detail = f"verdict={verdict}, avg={avg}"
        if min_umbrella is not None:
            detail += f", min_umbrella={min_umbrella} ({min_umbrella_name})"
        if mos_score is not None:
            detail += f", mos_score={mos_score}"
        detail += " | FAIL: " + "; ".join(failures)
        return False, detail

    detail = f"verdict={verdict}, avg={avg}"
    if min_umbrella is not None:
        detail += f", min_score={min_umbrella}"
    if mos_score is not None:
        detail += f", mos_score={mos_score}"
    return True, detail


def check_condition_2(
    report: dict,
    current_price: float | None,
    price_date: str | None,
    yf_currency: str | None,
    config: dict,
    capital: float,
    age_days: int,
) -> tuple[bool | None, str, dict]:
    """
    C2 — Price vs IV.
    Returns (pass/fail/None, detail_multiline_str, raw_values_dict).
    None = IV data not available.
    """
    iv_cons = report.get("iv_conservative")
    iv_currency = report.get("iv_currency")
    threshold = config["prebuy_mos_threshold_pct"]
    empty_raw = {"iv_conservative": iv_cons, "current_price": current_price,
                 "mos_pct": None, "threshold_price": None, "shares_at_threshold": None}

    if iv_cons is None:
        return None, (
            "IV data not available — run `./run.sh analyze TICKER assemble` to backfill"
        ), empty_raw

    if current_price is None:
        return None, "Could not fetch current price (no network or invalid ticker)", empty_raw

    # Currency mismatch warning block
    currency_warning = ""
    if iv_currency and yf_currency and iv_currency.upper() != yf_currency.upper():
        currency_warning = (
            f"  [WARN] Currency mismatch: IV currency={iv_currency}, "
            f"yfinance currency={yf_currency}.\n"
            f"         MOS calculation may be wrong. Verify manually before acting."
        )

    # Compute MOS
    mos_pct = (iv_cons - current_price) / iv_cons * 100
    threshold_price = iv_cons * (1 - threshold / 100)

    # Currency symbol for display
    curr_sym = iv_currency or (yf_currency or "")
    curr_display = f"{curr_sym} " if curr_sym else ""

    # Position sizing
    position_dollars = capital * POSITION_PCT
    shares_at_current = position_dollars / current_price
    shares_at_threshold = position_dollars / threshold_price if threshold_price > 0 else 0

    # Staleness suffix
    stale_marker = ""
    stale_line = ""
    if age_days > 30:
        stale_marker = "!!"
        stale_line = f"\n          !!! Report is {age_days} days old. IV estimate is stale. Re-run analysis. !!!"
    elif age_days > 14:
        stale_marker = "*"
        stale_line = f"\n          *** Report is {age_days} days old. Verify price before acting. ***"
    # MOS proximity: within 5% of threshold triggers 14-day warning as additional trigger
    elif abs(mos_pct - threshold) <= 5 and age_days > 14:
        stale_marker = "*"
        stale_line = f"\n          *** Report is {age_days} days old. MOS close to threshold — verify before acting. ***"

    price_display = f"{curr_display}{current_price:.2f}"
    if price_date:
        price_display += f"  (last close: {price_date})"

    passes = current_price <= threshold_price

    if passes:
        tag = f"[PASS{stale_marker}]"
        detail_lines = [
            f"{tag}  IV conservative: {curr_display}{iv_cons:.2f} | Current: {curr_display}{current_price:.2f} | MOS: {mos_pct:.1f}%",
            f"          Need price ≤ {curr_display}{threshold_price:.2f} for {threshold}% discount.",
            f"          At current price {curr_display}{current_price:.2f}: {shares_at_current:.1f} shares / {curr_display}{position_dollars:,.0f}  (threshold: ≤{curr_display}{threshold_price:.2f})",
        ]
        if stale_line:
            detail_lines.append(stale_line.strip())
    else:
        gap = current_price - threshold_price
        tag = "[FAIL]"
        detail_lines = [
            f"{tag}  IV conservative: {curr_display}{iv_cons:.2f} | Current: {curr_display}{current_price:.2f} | MOS: {mos_pct:.1f}%",
            f"          Need price ≤ {curr_display}{threshold_price:.2f} for {threshold}% discount. {curr_display}{gap:.2f} above threshold.",
            f"          At {curr_display}{threshold_price:.2f}: {shares_at_threshold:.1f} shares / {curr_display}{position_dollars:,.0f}",
        ]

    detail = "\n  ".join(detail_lines)
    if currency_warning:
        detail = currency_warning + "\n  " + detail

    raw = {"iv_conservative": iv_cons, "current_price": current_price,
           "mos_pct": mos_pct, "threshold_price": threshold_price,
           "shares_at_threshold": shares_at_threshold}
    return passes, detail, raw


def check_condition_3(report: dict, ticker: str) -> tuple[bool | None, str, str]:
    """
    C3 — Interactive conviction check.
    Prints the compact checklist from the report, then prompts for a 3-sentence thesis.
    Returns (confirmed, display_str, thesis_text).
    None = cannot run (non-interactive or checklist missing).
    """
    if not sys.stdin.isatty():
        return None, "[?????]  C3 requires interactive input (not available in batch mode)", ""

    checklist = report.get("compact_checklist", [])
    if checklist:
        print("  Compact checklist:")
        for i, sentence in enumerate(checklist, 1):
            print(f"    {i}. {sentence}")
        print()
    else:
        print("  (No compact checklist found in report — proceeding without it)")
        print()

    print(f"  State your 3-sentence thesis for {ticker} (required — Ctrl+C to abort):")
    print("  >", end=" ", flush=True)
    try:
        thesis = input().strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return False, "[ABORT]   C3 aborted by user", ""

    if not thesis:
        return False, "[FAIL]    C3 requires a non-empty thesis statement", ""

    display = f'[CONFIRMED] "{thesis}"'
    return True, display, thesis


def run_check(ticker: str, config: dict, dry_run_buy: bool = False):
    report, report_path = load_report(ticker)
    if report is None:
        print(f"\n  ERROR: No FINAL-REPORT.json found for {ticker}")
        print(f"         Run: ./run.sh analyze {ticker}")
        return False

    company = report.get("company", ticker)
    analysis_date = report.get("analysis_date", "unknown")
    age_days = report_age_days(report_path)

    # Fetch live price
    current_price, price_date, yf_currency = get_current_price(ticker)

    iv_currency = report.get("iv_currency")
    curr_sym = iv_currency or (yf_currency or "")
    curr_display = f"{curr_sym} " if curr_sym else ""
    price_line = (
        f"Current price: {curr_display}{current_price:.2f}"
        if current_price is not None
        else "Current price: unavailable"
    )
    if price_date:
        price_line += f"  (last close: {price_date})"

    print()
    print("══════════════════════════════════════════════════════════")
    print(f"  PRE-BUY CHECK: {ticker} — {company}")
    print(f"  Report date: {analysis_date}  |  Analysis age: {age_days} days")
    print(f"  {price_line}")
    print("══════════════════════════════════════════════════════════")

    # C1
    c1_pass, c1_detail = check_condition_1(report, config)
    print()
    print("  C1 — Quality gate")
    if c1_pass is True:
        print(f"  [PASS]  {c1_detail}")
    elif c1_pass is False:
        print(f"  [FAIL]  {c1_detail}")
    else:
        print(f"  [????]  {c1_detail}")

    # C2
    c2_pass, c2_detail, c2_raw = check_condition_2(
        report, current_price, price_date, yf_currency, config, config["capital_base"], age_days
    )
    threshold = config["prebuy_mos_threshold_pct"]
    print()
    print(f"  C2 — Price vs IV (need ≥{threshold}% discount to conservative IV)")
    for line in c2_detail.split("\n"):
        print(f"  {line}" if not line.startswith("  ") else line)

    # C3
    print()
    print("  C3 — 3-sentence conviction check (MANUAL)")
    c3_pass = None
    c3_detail = ""
    thesis_text = ""

    if c1_pass is True and c2_pass is True:
        c3_pass, c3_detail, thesis_text = check_condition_3(report, ticker)
        print(f"  {c3_detail}")
    else:
        print("  [SKIP]  C1 or C2 not met — C3 skipped")

    # Determine result
    print()
    print("──────────────────────────────────────────────────────────")

    # Stale marker propagation
    stale_marker = ""
    if age_days > 30:
        stale_marker = "!!"
    elif age_days > 14:
        stale_marker = "*"

    if c1_pass is True and c2_pass is True and c3_pass is True:
        print(f"  RESULT: GO{stale_marker}  (all conditions met)")
        result = "GO"
    elif c1_pass is False:
        print("  RESULT: NO-GO  (C1 not met)")
        result = "NO-GO"
    elif c2_pass is False:
        print("  RESULT: NO-GO  (C2 not met)")
        result = "NO-GO"
    elif c1_pass is None or c2_pass is None:
        print("  RESULT: INCOMPLETE  (data missing — see above)")
        result = "INCOMPLETE"
    elif c3_pass is False:
        print("  RESULT: NO-GO  (C3 not confirmed)")
        result = "NO-GO"
    else:
        print("  RESULT: NO-GO  (conditions not met)")
        result = "NO-GO"

    print("══════════════════════════════════════════════════════════")

    # Save to SQLite
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.database import Database
        umbrellas = report.get("umbrella_scores", {})
        min_umb_val = min(umbrellas.values()) if umbrellas else None
        min_umb_name = min(umbrellas, key=umbrellas.get) if umbrellas else None
        with Database() as db:
            db.migrate()
            db.insert_prebuy_check({
                "run_at": datetime.now().isoformat(),
                "ticker": ticker,
                "company": company,
                "mode": "single",
                "analysis_date": analysis_date,
                "age_days": age_days,
                "report_path": str(report_path.relative_to(REPO_ROOT)) if report_path else None,
                "verdict": report.get("verdict"),
                "average_score": report.get("average_score"),
                "min_umbrella_score": min_umb_val,
                "min_umbrella_name": min_umb_name,
                "mos_score": umbrellas.get("margin_of_safety"),
                "c1_pass": None if c1_pass is None else int(c1_pass),
                "c1_detail": c1_detail,
                "iv_conservative": c2_raw.get("iv_conservative"),
                "iv_currency": report.get("iv_currency"),
                "current_price": c2_raw.get("current_price"),
                "price_date": price_date,
                "mos_pct": c2_raw.get("mos_pct"),
                "threshold_price": c2_raw.get("threshold_price"),
                "threshold_pct": config["prebuy_mos_threshold_pct"],
                "c2_pass": None if c2_pass is None else int(c2_pass),
                "c2_detail": c2_detail[:500] if c2_detail else None,
                "c3_pass": None if c3_pass is None else int(c3_pass),
                "thesis_text": thesis_text or None,
                "result": result,
                "capital_base": config["capital_base"],
                "position_size": config["capital_base"] * POSITION_PCT,
                "shares_at_threshold": c2_raw.get("shares_at_threshold"),
                "stale_flag": 2 if age_days > 30 else (1 if age_days > 14 else 0),
            })
    except Exception:
        pass  # never break stdout on save failure

    # Dry-run buy record
    if dry_run_buy and result.startswith("GO") and c3_pass is True and current_price is not None:
        iv_cons = report.get("iv_conservative")
        mos_buy_pct = None
        if iv_cons:
            mos_buy_pct = round((iv_cons - current_price) / iv_cons * 100, 2)
        position_dollars = config["capital_base"] * POSITION_PCT
        shares = position_dollars / current_price
        cost_basis = shares * current_price

        pending_record = {
            "date": date.today().isoformat(),
            "ticker": ticker,
            "action": "BUY",
            "price": round(current_price, 2),
            "shares": round(shares, 2),
            "cost_basis": round(cost_basis, 2),
            "position_pct": round(POSITION_PCT * 100, 2),
            "iv_conservative_at_buy": iv_cons,
            "mos_at_buy_pct": mos_buy_pct,
            "thesis": thesis_text,
            "report_date": analysis_date,
            "analysis_age_days": age_days,
            "status": "pending",
        }

        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        filename = PENDING_DIR / f"{ticker}-{date.today().isoformat()}.json"
        with open(filename, "w") as f:
            json.dump(pending_record, f, indent=2)

        print()
        print(f"  [DRY-RUN] Pending record written to: {filename.relative_to(REPO_ROOT)}")
        print(f"  {json.dumps(pending_record, indent=4)}")

    return result.startswith("GO")


def run_own_dashboard(config: dict):
    """Show C1/C2 status for all Own-verdict tickers from reports."""
    # Scan all FINAL-REPORT.json files under runs/
    all_reports = list(RUNS_DIR.glob("*/reports/*/FINAL-REPORT.json"))
    # Group by ticker, keep latest per ticker
    by_ticker: dict[str, Path] = {}
    for p in all_reports:
        ticker = p.parent.name
        if ticker not in by_ticker or p.stat().st_mtime > by_ticker[ticker].stat().st_mtime:
            by_ticker[ticker] = p

    own_tickers = []
    for ticker, path in sorted(by_ticker.items()):
        try:
            with open(path) as f:
                data = json.load(f)
            if data.get("verdict") in ("Own", "Watch"):
                own_tickers.append((ticker, path, data))
        except (json.JSONDecodeError, OSError):
            pass

    if not own_tickers:
        print("No Own/Watch-verdict tickers found in runs/*/reports/.")
        return

    print()
    print("══════════════════════════════════════════════════════════")
    print("  PRE-BUY DASHBOARD — Own & Watch verdict tickers")
    print(f"  Date: {date.today().isoformat()}  |  Capital: ${config['capital_base']:,.0f}")
    print("══════════════════════════════════════════════════════════")
    print()

    # Table header
    col_ticker = 10
    col_verdict = 7
    col_score = 7
    col_c1 = 8
    col_c2 = 8
    col_mos = 10
    col_age = 6

    header = (
        f"  {'Ticker':<{col_ticker}} {'Verdict':<{col_verdict}} {'Avg':>{col_score}} {'C1':^{col_c1}} "
        f"{'C2':^{col_c2}} {'MOS%':>{col_mos}} {'Age':>{col_age}}"
    )
    print(header)
    print("  " + "-" * (col_ticker + col_verdict + col_score + col_c1 + col_c2 + col_mos + col_age + 12))

    c1c2_passers = []
    iv_data_count = 0
    save_records = []
    run_at = datetime.now().isoformat()

    for ticker, report_path, report in own_tickers:
        age_days = report_age_days(report_path)
        avg = report.get("average_score", "?")
        iv_cons = report.get("iv_conservative")
        umbrellas = report.get("umbrella_scores", {})

        c1_pass, c1_detail = check_condition_1(report, config)
        c1_sym = "PASS" if c1_pass is True else ("FAIL" if c1_pass is False else "N/A")

        current_price = None
        mos_pct = None
        threshold_price = None
        c2_pass = None

        if iv_cons is not None:
            iv_data_count += 1
            current_price, _, _ = get_current_price(ticker)
            if current_price is not None:
                threshold = config["prebuy_mos_threshold_pct"]
                threshold_price = iv_cons * (1 - threshold / 100)
                mos_pct = (iv_cons - current_price) / iv_cons * 100
                c2_pass = current_price <= threshold_price
                c2_sym = "PASS" if c2_pass else "FAIL"
                mos_display = f"{mos_pct:.1f}%"
                if c1_pass is True and c2_pass:
                    c1c2_passers.append(ticker)
            else:
                c2_sym = "N/A"
                mos_display = "N/A"
        else:
            c2_sym = "N/A"
            mos_display = "N/A"

        stale = "!" * (2 if age_days > 30 else (1 if age_days > 14 else 0))
        age_display = f"{age_days}d{stale}"

        verdict_display = report.get("verdict", "?")
        print(
            f"  {ticker:<{col_ticker}} {verdict_display:<{col_verdict}} {avg!s:>{col_score}} {c1_sym:^{col_c1}} "
            f"{c2_sym:^{col_c2}} {mos_display:>{col_mos}} {age_display:>{col_age}}"
        )

        # Build save record
        result = "NO-GO"
        if c1_pass is True and c2_pass is True:
            result = "GO"
        elif c1_pass is None or c2_pass is None:
            result = "INCOMPLETE"
        save_records.append({
            "run_at": run_at,
            "ticker": ticker,
            "company": report.get("company", ticker),
            "mode": "dashboard",
            "analysis_date": report.get("analysis_date"),
            "age_days": age_days,
            "report_path": str(report_path.relative_to(REPO_ROOT)) if report_path else None,
            "verdict": report.get("verdict"),
            "average_score": report.get("average_score"),
            "min_umbrella_score": min(umbrellas.values()) if umbrellas else None,
            "min_umbrella_name": min(umbrellas, key=umbrellas.get) if umbrellas else None,
            "mos_score": umbrellas.get("margin_of_safety"),
            "c1_pass": None if c1_pass is None else int(c1_pass),
            "c1_detail": c1_detail[:500] if c1_detail else None,
            "iv_conservative": iv_cons,
            "iv_currency": report.get("iv_currency"),
            "current_price": current_price,
            "price_date": None,
            "mos_pct": mos_pct,
            "threshold_price": threshold_price,
            "threshold_pct": config["prebuy_mos_threshold_pct"],
            "c2_pass": None if c2_pass is None else int(c2_pass),
            "c2_detail": None,
            "c3_pass": None,
            "thesis_text": None,
            "result": result,
            "capital_base": config["capital_base"],
            "position_size": config["capital_base"] * POSITION_PCT,
            "shares_at_threshold": None,
            "stale_flag": 2 if age_days > 30 else (1 if age_days > 14 else 0),
        })

    print()
    print(f"  {iv_data_count} of {len(own_tickers)} tickers have IV data.", end="")
    missing_iv = len(own_tickers) - iv_data_count
    if missing_iv > 0:
        print(f" Run `./run.sh analyze TICKER assemble` to backfill.")
    else:
        print()

    if c1c2_passers:
        print()
        print("  Tickers passing C1 + C2:")
        for t in c1c2_passers:
            print(f"    Run ./run.sh prebuy {t} to complete C3 and get a GO verdict.")

    print()
    print("  RESULT: Dashboard only — no GO possible in batch mode.")
    print("══════════════════════════════════════════════════════════")

    # Save all records to SQLite
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.database import Database
        with Database() as db:
            db.migrate()
            for rec in save_records:
                db.insert_prebuy_check(rec)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Pre-buy checklist: quality gate, price vs IV, conviction check."
    )
    parser.add_argument(
        "tickers",
        nargs="*",
        help="One or more ticker symbols to check",
    )
    parser.add_argument(
        "--own",
        action="store_true",
        help="Dashboard mode: show C1/C2 status for all Own and Watch verdict tickers",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=None,
        help="Starting capital in dollars (default: 100000 or portfolio/config.json capital_base)",
    )
    parser.add_argument(
        "--dry-run-buy",
        action="store_true",
        dest="dry_run_buy",
        help="When all conditions met, write a pending ledger record to portfolio/pending/",
    )
    args = parser.parse_args()

    config = load_config(args.capital)

    if args.own:
        if args.tickers:
            parser.error("--own and TICKER are mutually exclusive")
        run_own_dashboard(config)
        return

    if not args.tickers:
        parser.error("Provide TICKER(s) or use --own")

    for ticker in args.tickers:
        run_check(ticker.upper(), config, dry_run_buy=args.dry_run_buy)


if __name__ == "__main__":
    main()
