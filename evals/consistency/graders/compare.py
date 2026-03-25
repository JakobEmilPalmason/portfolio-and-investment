#!/usr/bin/env python3
"""
Side-by-side comparison of Claude vs Gemini consistency results for BKNG.

Reads saved trial JSONs from evals/consistency/results/{claude,gemini}/
and prints a comparison table.

Usage: python3 evals/consistency/graders/compare.py
"""
import json, os, glob, statistics

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

UMBRELLA_KEYS = [
    "circle_of_competence", "competitive_advantage", "management",
    "business_economics", "balance_sheet", "valuation",
    "margin_of_safety", "temperament",
]

UMBRELLA_SHORT = {
    "circle_of_competence": "Circle",
    "competitive_advantage": "Moat",
    "management": "Mgmt",
    "business_economics": "BizEcon",
    "balance_sheet": "BalSheet",
    "valuation": "Value",
    "margin_of_safety": "MOS",
    "temperament": "Temper",
}


def load_trials(agent):
    pattern = os.path.join(RESULTS_DIR, agent, "trial-*.json")
    files = sorted(glob.glob(pattern))
    reports = []
    for f in files:
        try:
            reports.append(json.load(open(f)))
        except Exception:
            pass
    return reports


def agent_stats(reports):
    if not reports:
        return None

    verdicts = [r.get("verdict", "?") for r in reports]
    confidences = [r.get("confidence", "?") for r in reports]
    avgs = [r.get("average_score", 0) for r in reports]

    scores_by_key = {}
    for k in UMBRELLA_KEYS:
        vals = [r.get("umbrella_scores", {}).get(k, 0) for r in reports]
        scores_by_key[k] = vals

    return {
        "n": len(reports),
        "verdicts": verdicts,
        "verdict_agree": len(set(verdicts)) == 1,
        "confidences": confidences,
        "conf_agree": len(set(confidences)) == 1,
        "avg_scores": avgs,
        "avg_mean": round(statistics.mean(avgs), 1),
        "avg_spread": round(max(avgs) - min(avgs), 1),
        "scores": scores_by_key,
    }


def print_table():
    claude = load_trials("claude")
    gemini = load_trials("gemini")

    if not claude and not gemini:
        print("No results found. Run the eval first.")
        return

    cs = agent_stats(claude) if claude else None
    gs = agent_stats(gemini) if gemini else None

    print()
    print("=" * 70)
    print("  BKNG Consistency Comparison — Claude vs Gemini")
    print("=" * 70)

    # Header
    print(f"\n{'':20s} {'Claude':>20s}   {'Gemini':>20s}")
    print("-" * 65)

    # Trials
    print(f"{'Trials':20s} {cs['n'] if cs else '-':>20}   {gs['n'] if gs else '-':>20}")

    # Verdicts
    cv = ", ".join(cs["verdicts"]) if cs else "-"
    gv = ", ".join(gs["verdicts"]) if gs else "-"
    print(f"{'Verdicts':20s} {cv:>20s}   {gv:>20s}")

    ca = "YES" if cs and cs["verdict_agree"] else "NO" if cs else "-"
    ga = "YES" if gs and gs["verdict_agree"] else "NO" if gs else "-"
    print(f"{'  Agree?':20s} {ca:>20s}   {ga:>20s}")

    # Confidence
    cc = ", ".join(cs["confidences"]) if cs else "-"
    gc = ", ".join(gs["confidences"]) if gs else "-"
    print(f"{'Confidence':20s} {cc:>20s}   {gc:>20s}")

    # Average score
    if cs:
        ca_str = f"{cs['avg_mean']} (spread {cs['avg_spread']})"
    else:
        ca_str = "-"
    if gs:
        ga_str = f"{gs['avg_mean']} (spread {gs['avg_spread']})"
    else:
        ga_str = "-"
    print(f"{'Avg Score':20s} {ca_str:>20s}   {ga_str:>20s}")

    # Per-umbrella scores
    print(f"\n{'Umbrella':20s} {'Claude scores':>20s}   {'Gemini scores':>20s}")
    print("-" * 65)
    for k in UMBRELLA_KEYS:
        short = UMBRELLA_SHORT[k]
        if cs:
            vals = cs["scores"][k]
            spread = max(vals) - min(vals)
            c_str = f"{','.join(str(v) for v in vals)} (Δ{spread})"
        else:
            c_str = "-"
        if gs:
            vals = gs["scores"][k]
            spread = max(vals) - min(vals)
            g_str = f"{','.join(str(v) for v in vals)} (Δ{spread})"
        else:
            g_str = "-"
        print(f"  {short:18s} {c_str:>20s}   {g_str:>20s}")

    # Cross-agent comparison
    if cs and gs:
        print(f"\n{'Cross-Agent':20s}")
        print("-" * 65)

        # Verdict agreement
        all_v = set(cs["verdicts"] + gs["verdicts"])
        print(f"{'  Verdict match':20s} {'YES' if len(all_v) == 1 else 'NO — ' + str(all_v):>43s}")

        # Average score gap
        gap = abs(cs["avg_mean"] - gs["avg_mean"])
        print(f"{'  Avg score gap':20s} {gap:>43.1f}")

        # Per-umbrella gap (mean vs mean)
        big_gaps = []
        for k in UMBRELLA_KEYS:
            c_mean = statistics.mean(cs["scores"][k])
            g_mean = statistics.mean(gs["scores"][k])
            if abs(c_mean - g_mean) >= 2:
                big_gaps.append(f"{UMBRELLA_SHORT[k]}: {c_mean:.0f}→{g_mean:.0f}")
        if big_gaps:
            print(f"{'  Big gaps (≥2)':20s} {', '.join(big_gaps):>43s}")
        else:
            print(f"{'  Big gaps (≥2)':20s} {'none':>43s}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    print_table()
