#!/usr/bin/env python3
"""
freeform_allocation.py - One-off fully-invested allocator run.

Builds a fresh allocation input blob from the latest reports, replaces the
cash-equivalent placeholder book, and writes a concentrated portfolio proposal
that can be 100% long or include shorts if they outrank the weakest longs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
from datetime import date, datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOC_INPUT_PATH = REPO_ROOT / "scripts" / "allocation-input.py"
DEFAULT_LABEL = "freeform-gross-100"


def load_allocation_module():
    spec = importlib.util.spec_from_file_location("allocation_input", ALLOC_INPUT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ALLOC_INPUT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def slugify(value: str) -> str:
    out = []
    prev_dash = False
    for ch in value.lower().strip():
        keep = ch.isalnum()
        if keep:
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-")


def confidence_rank(value: str) -> int:
    text = (value or "").strip().lower()
    if "high" in text:
        return 2
    if "medium" in text:
        return 1
    return 0


def latest_input_blob(capital_override: float | None) -> dict:
    module = load_allocation_module()
    reports = module.load_reports()
    queue = module.load_queue()
    portfolio_state = module.get_portfolio_state()

    if capital_override:
        portfolio_state["total_capital"] = capital_override

    candidates = module.build_candidates(reports, queue)
    blob = {
        "generated_at": datetime.now().isoformat(),
        "capital": portfolio_state["total_capital"],
        "portfolio_state": portfolio_state,
        "candidates": candidates,
        "summary": {
            "total_candidates": len(candidates),
            "by_verdict": {},
            "with_live_price": sum(1 for c in candidates if c.get("current_price")),
            "with_positive_mos": sum(
                1 for c in candidates
                if c.get("live_mos_pct") is not None and c["live_mos_pct"] > 0
            ),
        },
    }
    for candidate in candidates:
        verdict = candidate.get("verdict", "")
        blob["summary"]["by_verdict"][verdict] = blob["summary"]["by_verdict"].get(verdict, 0) + 1
    return blob


def get_min_umbrella_score(candidate: dict) -> float:
    scores = list((candidate.get("umbrella_scores") or {}).values())
    return float(min(scores)) if scores else 0.0


def is_long_eligible(candidate: dict) -> bool:
    if candidate.get("verdict") not in {"Own", "Watch"}:
        return False
    if candidate.get("current_price") is None:
        return False
    age = candidate.get("analysis_age_days")
    if age is None or age > 30:
        return False
    min_score = get_min_umbrella_score(candidate)
    if min_score < 5:
        return False
    text = " ".join(candidate.get("red_flags") or []).lower()
    bad_phrases = ("fraud", "accounting restatement", "existential", "bankruptcy")
    return not any(phrase in text for phrase in bad_phrases)


def is_short_eligible(candidate: dict) -> bool:
    if candidate.get("current_price") is None:
        return False
    age = candidate.get("analysis_age_days")
    if age is None or age > 30:
        return False
    price = candidate.get("current_price")
    iv_bull = candidate.get("iv_bull")
    mos = candidate.get("live_mos_pct")
    scores = candidate.get("umbrella_scores") or {}
    valuation_score = scores.get("valuation")
    mos_score = scores.get("margin_of_safety")
    explicit_overvaluation = bool(iv_bull is not None and price > iv_bull)
    severe_mos = mos is not None and mos <= -40
    weak_scoring = (
        (valuation_score is not None and valuation_score <= 4) or
        (mos_score is not None and mos_score <= 4) or
        candidate.get("average_score", 0) <= 6.5 or
        len(candidate.get("red_flags") or []) >= 5
    )
    return explicit_overvaluation or (severe_mos and weak_scoring)


def long_score(candidate: dict) -> float:
    mos = candidate.get("live_mos_pct")
    ratio = candidate.get("upside_downside_ratio")
    avg = float(candidate.get("average_score") or 0.0)
    verdict_bonus = 2.5 if candidate.get("verdict") == "Own" else 0.8
    conf_bonus = 1.25 * confidence_rank(candidate.get("confidence", ""))
    mos_component = max(min(float(mos or 0.0), 60.0), -25.0) / 6.0
    asymmetry = 0.0
    if ratio is not None:
        asymmetry = max(min(float(ratio), 5.0), -1.0) * 0.8
    freshness = max(0.0, 14.0 - float(candidate.get("analysis_age_days") or 30.0)) * 0.08
    red_flag_penalty = len(candidate.get("red_flags") or []) * 0.25
    umbrella_bonus = get_min_umbrella_score(candidate) * 0.35
    return avg * 1.35 + verdict_bonus + conf_bonus + mos_component + asymmetry + freshness + umbrella_bonus - red_flag_penalty


def short_score(candidate: dict) -> float:
    mos = float(candidate.get("live_mos_pct") or 0.0)
    avg = float(candidate.get("average_score") or 0.0)
    scores = candidate.get("umbrella_scores") or {}
    valuation_score = float(scores.get("valuation") or 5.0)
    mos_score = float(scores.get("margin_of_safety") or 5.0)
    price = float(candidate.get("current_price") or 0.0)
    iv_bull = candidate.get("iv_bull")
    above_bull = 0.0
    if iv_bull:
        above_bull = max((price - float(iv_bull)) / float(iv_bull) * 100.0, 0.0)
    verdict = candidate.get("verdict")
    verdict_bonus = 2.0 if verdict == "Pass" else 1.0 if verdict == "Watch" else 0.25
    structural_bonus = 0.0
    structural_text = " ".join((candidate.get("red_flags") or []) + (candidate.get("key_risks") or [])).lower()
    keywords = ("tariff", "debt", "investigation", "dilution", "governance", "cyclical", "competition", "overvalued")
    structural_bonus += sum(0.15 for word in keywords if word in structural_text)
    red_flags = len(candidate.get("red_flags") or [])
    freshness = max(0.0, 14.0 - float(candidate.get("analysis_age_days") or 30.0)) * 0.05
    return (
        max(-mos, 0.0) / 14.0
        + above_bull / 18.0
        + (6.0 - valuation_score) * 0.9
        + (6.0 - mos_score) * 0.6
        + verdict_bonus
        + red_flags * 0.35
        + structural_bonus
        + freshness
        - avg * 0.12
    )


def choose_positions(blob: dict) -> tuple[list[dict], dict]:
    candidates = blob["candidates"]
    longs = []
    shorts = []
    for candidate in candidates:
        if is_long_eligible(candidate):
            candidate = dict(candidate)
            candidate["_score"] = round(long_score(candidate), 4)
            longs.append(candidate)
        if is_short_eligible(candidate):
            candidate = dict(candidate)
            candidate["_score"] = round(short_score(candidate), 4)
            shorts.append(candidate)

    longs.sort(key=lambda c: c["_score"], reverse=True)
    shorts.sort(key=lambda c: c["_score"], reverse=True)

    selected_longs = longs[:8]
    best_short = shorts[0] if shorts else None
    weakest_long_score = selected_longs[-1]["_score"] if selected_longs else -math.inf

    # Use a short only if it is clearly institutional-grade and materially
    # stronger than the weakest selected long. This avoids filling the book
    # with low-quality micro-cap shorts just because the MOS math is extreme.
    use_short = bool(
        best_short
        and float(best_short.get("average_score") or 0.0) >= 5.0
        and float(best_short.get("current_price") or 0.0) >= 50.0
        and best_short["_score"] > weakest_long_score + 3.0
    )

    if use_short:
        selected = selected_longs[:7] + [best_short]
        weight_map = {
            selected[0]["ticker"]: 18.0,
            selected[1]["ticker"]: 16.0,
            selected[2]["ticker"]: 15.0,
            selected[3]["ticker"]: 13.0,
            selected[4]["ticker"]: 12.0,
            selected[5]["ticker"]: 11.0,
            selected[6]["ticker"]: 8.0,
            best_short["ticker"]: 7.0,
        }
        short_tickers = {best_short["ticker"]}
    else:
        selected = selected_longs[:8]
        weight_map = {
            selected[0]["ticker"]: 18.0,
            selected[1]["ticker"]: 16.0,
            selected[2]["ticker"]: 15.0,
            selected[3]["ticker"]: 14.0,
            selected[4]["ticker"]: 12.0,
            selected[5]["ticker"]: 10.0,
            selected[6]["ticker"]: 8.0,
            selected[7]["ticker"]: 7.0,
        }
        short_tickers = set()

    total_capital = float(blob["capital"])
    current_positions = {p["ticker"]: p for p in blob["portfolio_state"].get("positions") or []}
    ranked_positions: list[dict] = []
    long_exposure = 0.0
    short_exposure = 0.0
    weighted_score = 0.0
    weighted_mos = 0.0
    confidence_weight = 0.0

    for rank, candidate in enumerate(selected, start=1):
        ticker = candidate["ticker"]
        side = "SHORT" if ticker in short_tickers else "LONG"
        weight = weight_map[ticker]
        signed_weight = -weight if side == "SHORT" else weight
        current_weight = float(current_positions.get(ticker, {}).get("weight_pct", 0.0))
        price = float(candidate["current_price"])
        target_value = round(total_capital * weight / 100.0, 2)
        shares = max(1, int(target_value / price))
        conf = confidence_rank(candidate.get("confidence", ""))
        mos = candidate.get("live_mos_pct")
        if side == "LONG":
            long_exposure += weight
        else:
            short_exposure += weight
        weighted_score += weight * float(candidate.get("average_score") or 0.0)
        if mos is not None:
            weighted_mos += weight * float(mos)
        confidence_weight += weight * conf
        ranked_positions.append({
            "rank": rank,
            "ticker": ticker,
            "company": candidate.get("company", ""),
            "side": side,
            "verdict": candidate.get("verdict"),
            "action": "BUY" if side == "LONG" else "SHORT",
            "current_weight_pct": current_weight,
            "target_weight_pct": weight,
            "signed_weight_pct": signed_weight,
            "weight_change_pct": round(signed_weight - current_weight, 2),
            "target_value": target_value,
            "shares": shares,
            "price_at_proposal": price,
            "iv_conservative": candidate.get("iv_conservative"),
            "iv_base": candidate.get("iv_base"),
            "iv_bull": candidate.get("iv_bull"),
            "live_mos_pct": mos,
            "upside_downside_ratio": candidate.get("upside_downside_ratio"),
            "average_score": candidate.get("average_score"),
            "confidence": candidate.get("confidence"),
            "sector": candidate.get("sector"),
            "rationale": build_rationale(candidate, side, weight),
        })

    net_exposure = long_exposure - short_exposure
    weighted_conf = "high" if confidence_weight >= 150 else "medium" if confidence_weight >= 90 else "low"
    summary = {
        "long_exposure_pct": round(long_exposure, 2),
        "short_exposure_pct": round(short_exposure, 2),
        "gross_exposure_pct": round(long_exposure + short_exposure, 2),
        "net_exposure_pct": round(net_exposure, 2),
        "portfolio_avg_score": round(weighted_score / 100.0, 2),
        "portfolio_avg_mos_pct": round(weighted_mos / 100.0, 2),
        "portfolio_weighted_confidence": weighted_conf,
        "position_count": len(ranked_positions),
        "cash_weight_pct": 0.0,
    }
    return ranked_positions, summary


def build_rationale(candidate: dict, side: str, weight: float) -> str:
    mos = candidate.get("live_mos_pct")
    avg = candidate.get("average_score")
    strength = (candidate.get("key_strengths") or [""])[0]
    risk = (candidate.get("key_risks") or [""])[0]
    if side == "LONG":
        mos_text = f"{mos:.1f}% live MOS" if mos is not None else "fresh report support"
        return (
            f"{candidate.get('verdict')} thesis sized at {weight:.1f}% on a score of {avg}/10 with {mos_text}. "
            f"{strength}. Main risk: {risk}."
        )
    return (
        f"Short sized at {weight:.1f}% because the stock screens as explicitly overvalued versus the reported IV range "
        f"and carries weak valuation support. {risk}. Key counterpoint: {strength}."
    )


def sector_exposure(positions: list[dict]) -> dict:
    exposure: dict[str, dict[str, float | int]] = {}
    for position in positions:
        sector = position.get("sector") or "Other"
        bucket = exposure.setdefault(sector, {"gross_pct": 0.0, "long_pct": 0.0, "short_pct": 0.0, "names": 0})
        bucket["gross_pct"] += position["target_weight_pct"]
        if position["side"] == "LONG":
            bucket["long_pct"] += position["target_weight_pct"]
        else:
            bucket["short_pct"] += position["target_weight_pct"]
        bucket["names"] += 1
    for value in exposure.values():
        value["gross_pct"] = round(value["gross_pct"], 2)
        value["long_pct"] = round(value["long_pct"], 2)
        value["short_pct"] = round(value["short_pct"], 2)
    return exposure


def correlated_risks(positions: list[dict]) -> list[str]:
    theme_keywords = {
        "AI disruption / software re-rating": ("ai", "software", "workflow", "platform"),
        "Healthcare product / regulatory risk": ("drug", "trial", "fda", "glp-1", "patent", "pricing"),
        "Governance / capital allocation execution": ("governance", "succession", "capital allocation", "debt", "acquisition"),
    }
    results = []
    for label, keywords in theme_keywords.items():
        tickers = []
        for position in positions:
            text = position.get("rationale", "").lower()
            tokens = set(re.findall(r"[a-z0-9-]+", text))
            phrase_match = any(" " in keyword and keyword in text for keyword in keywords)
            token_match = any(" " not in keyword and keyword in tokens for keyword in keywords)
            if phrase_match or token_match:
                tickers.append(position["ticker"])
        if len(tickers) >= 2:
            results.append(f"{label} — {', '.join(tickers)}")
    return results[:3]


def notable_exclusions(blob: dict, selected: list[dict]) -> list[dict]:
    selected_tickers = {p["ticker"] for p in selected}
    excluded = []
    candidates = []
    for candidate in blob["candidates"]:
        if candidate["ticker"] in selected_tickers or candidate.get("current_price") is None:
            continue
        mos = candidate.get("live_mos_pct")
        avg = candidate.get("average_score") or 0
        candidates.append((mos if mos is not None else -999, avg, candidate))
    candidates.sort(reverse=True)
    for _, _, candidate in candidates[:6]:
        reason = []
        if candidate.get("live_mos_pct") is not None and candidate["live_mos_pct"] < 0:
            reason.append(f"negative MOS ({candidate['live_mos_pct']:.1f}%)")
        if len(candidate.get("red_flags") or []) >= 4:
            reason.append(f"{len(candidate.get('red_flags') or [])} red flags")
        if candidate.get("verdict") == "Watch":
            reason.append("watch verdict")
        excluded.append({"ticker": candidate["ticker"], "reason": ", ".join(reason) or "did not outrank selected names"})
    return excluded


def markdown_summary(
    proposal: dict,
    removals: list[dict],
) -> str:
    lines = []
    lines.append(f"# Allocation Proposal - {proposal['proposal_date']}")
    lines.append("")
    lines.append(
        f"Capital: ${proposal['capital']:,} | Positions: {proposal['risk_overlay']['position_count']} "
        f"| Gross: {proposal['risk_overlay']['gross_exposure_pct']}% | Net: {proposal['risk_overlay']['net_exposure_pct']}% | Cash: 0.0%"
    )
    lines.append("")
    meta = proposal["run_metadata"]
    lines.append(f"Run ID: {meta['run_id']} | Label: {meta['run_label']}")
    lines.append("")
    lines.append("## Changes vs Current Book")
    lines.append(f"- BUY: {proposal['changes_vs_current']['buy']}")
    lines.append(f"- SHORT: {proposal['changes_vs_current']['short']}")
    lines.append(f"- EXIT: {proposal['changes_vs_current']['exit']}")
    lines.append("")
    lines.append("## Target Portfolio")
    lines.append("")
    lines.append("| # | Ticker | Side | Verdict | Target Wt | Value | Score | MOS% | Sector | Rationale |")
    lines.append("|---|--------|------|---------|-----------|-------|-------|------|--------|-----------|")
    for position in proposal["positions"]:
        mos = "" if position["live_mos_pct"] is None else f"{position['live_mos_pct']:.1f}"
        lines.append(
            f"| {position['rank']} | {position['ticker']} | {position['side']} | {position['verdict']} | "
            f"{position['target_weight_pct']:.1f}% | ${position['target_value']:,.0f} | {position['average_score']} | "
            f"{mos} | {position['sector']} | {position['rationale']} |"
        )
    lines.append("")
    lines.append("## Removals")
    for removal in removals:
        lines.append(f"- {removal['ticker']}: {removal['reason']}")
    lines.append("")
    lines.append("## Risk Overlay")
    for item in proposal["risk_overlay"]["top_correlated_risks"]:
        lines.append(f"- {item}")
    lines.append(f"- Sector exposure: {json.dumps(proposal['risk_overlay']['sector_exposure'], ensure_ascii=True)}")
    lines.append(
        f"- Portfolio stats: avg score {proposal['risk_overlay']['portfolio_avg_score']}, "
        f"avg MOS {proposal['risk_overlay']['portfolio_avg_mos_pct']}%, "
        f"weighted confidence {proposal['risk_overlay']['portfolio_weighted_confidence']}"
    )
    lines.append("")
    lines.append("## Notable Exclusions")
    for item in proposal["excluded_notable"]:
        lines.append(f"- {item['ticker']}: {item['reason']}")
    lines.append("")
    lines.append("## Cash Rationale")
    lines.append("Fully deployed by design for this run. The 100% gross rule replaces the normal cash optionality in the base allocator.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a free-form 100% gross allocation run.")
    parser.add_argument("--capital", type=float, default=None, help="Override capital base")
    parser.add_argument("--label", type=str, default=DEFAULT_LABEL, help="Run label")
    parser.add_argument("--output-dir", type=str, default=None, help="Override output directory")
    args = parser.parse_args()

    blob = latest_input_blob(args.capital)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{ts}-p{math.floor(datetime.now().timestamp())}-{slugify(args.label)}"
    if args.output_dir:
        run_dir = Path(args.output_dir)
        if not run_dir.is_absolute():
            run_dir = REPO_ROOT / run_dir
    else:
        alloc_root = REPO_ROOT / "portfolio" / "allocations"
        week_dirs = sorted(
            [path for path in alloc_root.iterdir() if path.is_dir() and path.name.startswith("week")],
            key=lambda path: path.name,
        )
        base_dir = week_dirs[-1] if week_dirs else alloc_root
        run_dir = base_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    input_path = run_dir / "allocation-input.json"
    proposal_json = run_dir / "allocation-proposal.json"
    proposal_md = run_dir / "allocation-proposal.md"
    prompt_path = run_dir / "allocator-prompt.md"
    meta_path = run_dir / "run-metadata.json"

    input_path.write_text(json.dumps(blob, indent=2) + "\n")
    prompt_path.write_text(
        "\n".join(
            [
                "# Free-Form Allocator Prompt",
                "",
                "- Replace the BIL cash placeholder entirely.",
                "- Only use tickers with latest FINAL-REPORT.json coverage.",
                "- Force 100% gross exposure and 0% cash.",
                "- Longs outrank shorts unless a short clearly beats the weakest long on conviction.",
                "- Allow concentrated sizing; this run does not use the base allocator's 3%-7% caps.",
            ]
        ) + "\n"
    )

    positions, summary = choose_positions(blob)
    removals = []
    for current in blob["portfolio_state"].get("positions") or []:
        if current["ticker"] not in {position["ticker"] for position in positions}:
            removals.append({
                "ticker": current["ticker"],
                "current_weight_pct": current.get("weight_pct", 0.0),
                "reason": "Cash-equivalent placeholder removed to satisfy the 100% reported-stocks rule.",
            })

    risk_overlay = {
        "top_correlated_risks": correlated_risks(positions),
        "sector_exposure": sector_exposure(positions),
        "portfolio_avg_score": summary["portfolio_avg_score"],
        "portfolio_avg_mos_pct": summary["portfolio_avg_mos_pct"],
        "portfolio_weighted_confidence": summary["portfolio_weighted_confidence"],
        "position_count": summary["position_count"],
        "long_exposure_pct": summary["long_exposure_pct"],
        "short_exposure_pct": summary["short_exposure_pct"],
        "gross_exposure_pct": summary["gross_exposure_pct"],
        "net_exposure_pct": summary["net_exposure_pct"],
    }

    proposal = {
        "run_metadata": {
            "run_id": run_id,
            "run_label": args.label,
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "input_path": str(input_path.relative_to(REPO_ROOT)),
        },
        "proposal_date": str(date.today()),
        "capital": int(round(float(blob["capital"]))),
        "methodology": "free-form reported-stocks allocator, 100% gross, cash disabled",
        "changes_vs_current": {
            "buy": sum(1 for p in positions if p["side"] == "LONG"),
            "short": sum(1 for p in positions if p["side"] == "SHORT"),
            "hold": 0,
            "trim": 0,
            "exit": len(removals),
        },
        "positions": positions,
        "removals": removals,
        "cash": {
            "amount": 0,
            "weight_pct": 0.0,
            "rationale": "Cash disabled for this run. Gross exposure must equal 100% using reported stocks only.",
        },
        "risk_overlay": risk_overlay,
        "excluded_notable": notable_exclusions(blob, positions),
    }

    proposal_json.write_text(json.dumps(proposal, indent=2) + "\n")
    proposal_md.write_text(markdown_summary(proposal, removals))
    meta_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "label": args.label,
                "capital": proposal["capital"],
                "timestamp": proposal["run_metadata"]["generated_at_utc"],
                "output_dir": str(run_dir.relative_to(REPO_ROOT)),
                "status": "completed",
            },
            indent=2,
        ) + "\n"
    )

    print(f"Allocation input: {input_path}")
    print(f"Proposal JSON:    {proposal_json}")
    print(f"Proposal MD:      {proposal_md}")
    print(f"Run metadata:     {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
