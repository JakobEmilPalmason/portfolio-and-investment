#!/usr/bin/env python3
"""
Grader for BKNG consistency eval.

Checks two things:
  1. Correctness — did the agent produce valid, complete output?
  2. Consistency — does this trial agree with previous trials?

Usage: python3 check-bkng.py <agent>   (agent = claude | gemini)

Results are saved per-agent so Claude and Gemini consistency is measured
independently. Run `python3 check-bkng.py --reset` to clear saved results.
"""
import json, os, sys, subprocess, glob, shutil, time

# ── Args ──────────────────────────────────────────────────
agent = sys.argv[1] if len(sys.argv) > 1 else "unknown"

if agent == "--reset":
    shutil.rmtree("evals/consistency/results", ignore_errors=True)
    print('{"score": 1.0, "details": "Results cleared"}')
    sys.exit(0)

# ── Paths ─────────────────────────────────────────────────
week = subprocess.check_output(
    ["grep", "-m1", "CURRENT_WEEK=", "run.sh"]
).decode().split('"')[1]

TICKER = "BKNG"
report_dir = f"runs/{week}/reports/{TICKER}"
results_dir = f"evals/consistency/results/{agent}"
os.makedirs(results_dir, exist_ok=True)

checks = []

def check(name, passed, msg):
    checks.append({"name": name, "passed": passed, "message": msg})


# ═══════════════════════════════════════════════════════════
# Part 1: Correctness
# ═══════════════════════════════════════════════════════════

# 1a. All 11 expected files
expected_files = [
    "01-circle-of-competence.md",
    "02-durable-competitive-advantage.md",
    "03-management-capital-allocation.md",
    "04-business-economics.md",
    "05-balance-sheet-safety.md",
    "06-valuation-intrinsic-value.md",
    "07-margin-of-safety.md",
    "08-temperament-time-horizon.md",
    "09-compact-checklist.md",
    "FINAL-REPORT.md",
    "FINAL-REPORT.json",
]

for f in expected_files:
    path = f"{report_dir}/{f}"
    check(f"file-{f}", os.path.isfile(path),
          f"{f} exists" if os.path.isfile(path) else f"{f} missing")

# 1b. FINAL-REPORT.json schema checks
UMBRELLA_KEYS = [
    "circle_of_competence", "competitive_advantage", "management",
    "business_economics", "balance_sheet", "valuation",
    "margin_of_safety", "temperament",
]

rpt = None
try:
    with open(f"{report_dir}/FINAL-REPORT.json") as fh:
        rpt = json.load(fh)
    check("json-valid", True, "Valid JSON")

    # Required top-level keys
    required = [
        "ticker", "company", "verdict", "average_score",
        "umbrella_scores", "key_strengths", "key_risks",
        "buy_triggers", "sell_triggers", "compact_checklist", "confidence",
    ]
    missing = [k for k in required if k not in rpt]
    check("json-keys", len(missing) == 0,
          "All keys present" if not missing else f"Missing: {missing}")

    # Ticker
    check("ticker", rpt.get("ticker") == TICKER,
          f"Ticker is {rpt.get('ticker')}")

    # Verdict
    v = rpt.get("verdict", "")
    check("verdict", v in ["Own", "Watch", "Pass"], f"Verdict: {v}")

    # 8 umbrella scores, each 1-10
    s = rpt.get("umbrella_scores", {})
    scores_ok = (
        all(isinstance(s.get(k), (int, float)) and 1 <= s[k] <= 10
            for k in UMBRELLA_KEYS)
        and len(s) >= 8
    )
    check("scores", scores_ok,
          "8 valid scores" if scores_ok else f"Scores: {s}")

    # Average score sanity
    avg = rpt.get("average_score", 0)
    calc = round(sum(s[k] for k in UMBRELLA_KEYS if k in s) / 8, 1) if len(s) >= 8 else 0
    check("avg-score", abs(avg - calc) <= 0.3,
          f"avg={avg} calc={calc}")

    # Compact checklist = list of 8
    cl = rpt.get("compact_checklist", [])
    check("checklist-8", isinstance(cl, list) and len(cl) == 8,
          f"{len(cl) if isinstance(cl, list) else 'not a list'} checklist items")

    # Confidence
    c = rpt.get("confidence", "")
    check("confidence", c in ["high", "medium", "low"], f"Confidence: {c}")

except Exception as e:
    check("json-valid", False, str(e))

# 1c. Report length
md_path = f"{report_dir}/FINAL-REPORT.md"
if os.path.isfile(md_path):
    lines = len(open(md_path).readlines())
    check("report-length", lines > 200, f"{lines} lines")
else:
    check("report-length", False, "FINAL-REPORT.md missing")

# 1d. Queue updated
try:
    q = json.load(open("queue/queue.json"))
    entry = [e for e in q if e.get("ticker") == TICKER]
    check("queue", bool(entry and entry[0].get("current_verdict") in ["Own", "Watch", "Pass"]),
          "Queue updated" if entry else "Not in queue")
except Exception:
    check("queue", False, "queue.json error")


# ═══════════════════════════════════════════════════════════
# Part 2: Cross-trial consistency
# ═══════════════════════════════════════════════════════════

if rpt:
    # Save this trial
    trial_id = f"trial-{int(time.time() * 1000)}"
    trial_path = f"{results_dir}/{trial_id}.json"
    shutil.copy(f"{report_dir}/FINAL-REPORT.json", trial_path)

    # Load all previous trials (excluding this one)
    prev_files = sorted(glob.glob(f"{results_dir}/trial-*.json"))
    prev_files = [f for f in prev_files if f != trial_path]

    if prev_files:
        prev_reports = []
        for pf in prev_files:
            try:
                prev_reports.append(json.load(open(pf)))
            except Exception:
                pass

        if prev_reports:
            # — Verdict consistency —
            all_verdicts = [r.get("verdict") for r in prev_reports] + [rpt.get("verdict")]
            verdict_match = len(set(all_verdicts)) == 1
            check("verdict-consistency", verdict_match,
                  f"Verdicts: {all_verdicts}")

            # — Per-umbrella score deviation (max spread ≤ 2) —
            for key in UMBRELLA_KEYS:
                all_scores = (
                    [r.get("umbrella_scores", {}).get(key, 0) for r in prev_reports]
                    + [rpt.get("umbrella_scores", {}).get(key, 0)]
                )
                spread = max(all_scores) - min(all_scores)
                short = key.replace("_", "-")
                check(f"spread-{short}", spread <= 2,
                      f"Spread: {spread} → {all_scores}")

            # — Average score deviation (≤ 1.0) —
            all_avgs = [r.get("average_score", 0) for r in prev_reports] + [rpt.get("average_score", 0)]
            avg_spread = round(max(all_avgs) - min(all_avgs), 1)
            check("avg-consistency", avg_spread <= 1.0,
                  f"Avg spread: {avg_spread} → {all_avgs}")

            # — Confidence consistency —
            all_conf = [r.get("confidence") for r in prev_reports] + [rpt.get("confidence")]
            check("confidence-consistency", len(set(all_conf)) == 1,
                  f"Confidences: {all_conf}")

            # — Key strengths overlap (≥50% Jaccard on first 3) —
            def top3_set(report, field):
                items = report.get(field, [])[:3]
                # Normalize: lowercase, first 40 chars
                return set(str(i).lower()[:40] for i in items)

            curr_str = top3_set(rpt, "key_strengths")
            for i, prev in enumerate(prev_reports):
                prev_str = top3_set(prev, "key_strengths")
                if curr_str and prev_str:
                    # Use word overlap instead of exact match
                    curr_words = set(w for s in curr_str for w in s.split())
                    prev_words = set(w for s in prev_str for w in s.split())
                    if curr_words | prev_words:
                        overlap = len(curr_words & prev_words) / len(curr_words | prev_words)
                        check(f"strengths-overlap-t{i+1}",
                              overlap >= 0.25,
                              f"Word overlap: {overlap:.0%}")
    else:
        check("first-trial", True,
              "First trial for this agent — consistency checks start at trial 2")


# ═══════════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════════

passed = sum(1 for c in checks if c["passed"])
total = len(checks)
score = round(passed / total, 2) if total else 0.0
print(json.dumps({"score": score, "details": f"{passed}/{total} checks passed", "checks": checks}))
