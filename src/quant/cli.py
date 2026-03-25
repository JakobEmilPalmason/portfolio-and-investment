"""CLI entry point for quantitative valuation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .dcf import build_inputs_from_financials, run_three_scenarios
from .formatters import (
    format_montecarlo_text,
    format_owner_earnings_text,
    format_scenario_text,
    format_sensitivity_text,
    format_wacc_text,
    scenario_to_json,
    write_quant_valuation_json,
    write_quant_valuation_md,
)
from .montecarlo import default_distributions, run_monte_carlo
from .owner_earnings import adjusted_capex_pct, compute_owner_earnings
from .parser import parse_financials
from .sensitivity import build_sensitivity
from .wacc import compute_wacc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.quant",
        description="Quantitative DCF valuation engine",
    )
    parser.add_argument("ticker", help="Ticker symbol (e.g. TXN, AAPL)")
    parser.add_argument("--wacc", type=float, default=0.10, help="WACC (default: 0.10)")
    parser.add_argument("--exit-multiple", type=float, default=15.0, help="Exit EV/EBITDA multiple (default: 15)")
    parser.add_argument("--growth", type=float, default=None, help="Override revenue growth rate")
    parser.add_argument("--years", type=int, default=5, help="Projection years (default: 5)")
    parser.add_argument("--terminal-growth", type=float, default=0.03, help="Terminal growth rate (default: 0.03)")

    parser.add_argument("--sensitivity", action="store_true", help="Include sensitivity table")
    parser.add_argument("--row-param", default="revenue_growth", help="Sensitivity row param")
    parser.add_argument("--col-param", default="wacc", help="Sensitivity col param")

    parser.add_argument("--monte-carlo", action="store_true", help="Include Monte Carlo simulation")
    parser.add_argument("--simulations", type=int, default=10_000, help="Monte Carlo iterations")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")

    # Discount rate
    parser.add_argument("--discount-rate", type=float, default=None,
        help="Fixed discount rate, Buffett-style (e.g. 0.10 for 10%%). Skips CAPM.")
    parser.add_argument("--auto-wacc", action="store_true",
        help="Compute WACC from CAPM (beta, cost of debt) instead of manual")
    parser.add_argument("--risk-free", type=float, default=0.045,
        help="Risk-free rate for CAPM (default: 0.045)")
    parser.add_argument("--mrp", type=float, default=0.055,
        help="Market risk premium for CAPM (default: 0.055)")

    # Growth fade
    parser.add_argument("--fade-growth", action="store_true",
        help="Use growth fade schedule instead of flat growth rates")
    parser.add_argument("--high-growth-years", type=int, default=3,
        help="Years at high growth before fade begins (default: 3)")
    parser.add_argument("--growth-method", choices=["linear_fade", "roic_sustainable"],
        default="linear_fade", help="Growth fade method")

    # Owner earnings
    parser.add_argument("--owner-earnings", action="store_true",
        help="Use adjusted owner earnings (maintenance capex only)")
    parser.add_argument("--oe-method", choices=["da_proxy", "regression"],
        default="da_proxy", help="Maintenance capex estimation method")

    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    parser.add_argument("--write", action="store_true", help="Write quant-valuation.md to context/")
    parser.add_argument("--json-out", action="store_true", help="Write quant-valuation.json to context/")
    parser.add_argument("--context-dir", type=str, default=None, help="Override context directory")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout output (still writes files)")

    args = parser.parse_args(argv)
    ticker = args.ticker.upper()

    context_dir = Path(args.context_dir) if args.context_dir else None

    # Parse financials
    try:
        data = parse_financials(ticker, context_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # --- Resolve discount rate ---
    wacc_result = None
    wacc = args.wacc
    discount_method = "manual"
    if args.discount_rate is not None:
        wacc = args.discount_rate
        discount_method = "fixed"
    elif args.auto_wacc:
        discount_method = "capm"
        try:
            wacc_result = compute_wacc(data, args.risk_free, args.mrp)
            wacc = wacc_result.wacc
            for w in wacc_result.warnings:
                print(f"WACC warning: {w}", file=sys.stderr)
        except ValueError as e:
            print(f"WACC error: {e} — falling back to {wacc}", file=sys.stderr)

    # --- Resolve owner earnings capex override ---
    oe_results = None
    capex_override = None
    if args.owner_earnings:
        oe_results = compute_owner_earnings(data, method=args.oe_method)
        capex_override = adjusted_capex_pct(data, method=args.oe_method)

    # Run scenarios
    scenario = run_three_scenarios(
        data,
        wacc=wacc,
        exit_multiple=args.exit_multiple,
        projection_years=args.years,
        fade_growth=args.fade_growth,
        high_growth_years=args.high_growth_years,
        growth_method=args.growth_method,
        capex_pct_override=capex_override,
    )

    # Tag discount method metadata on all scenario inputs
    for result in (scenario.bear, scenario.base, scenario.bull):
        result.inputs.discount_method = discount_method

    # Optional: sensitivity
    sens = None
    if args.sensitivity:
        base_inputs = build_inputs_from_financials(
            data,
            wacc=wacc,
            exit_multiple=args.exit_multiple,
            projection_years=args.years,
            fade_growth=args.fade_growth,
            high_growth_years=args.high_growth_years,
            growth_method=args.growth_method,
            capex_pct_override=capex_override,
        )
        sens = build_sensitivity(
            base_inputs,
            row_param=args.row_param,
            col_param=args.col_param,
        )

    # Optional: Monte Carlo
    mc = None
    if args.monte_carlo:
        base_inputs = build_inputs_from_financials(
            data,
            wacc=wacc,
            exit_multiple=args.exit_multiple,
            projection_years=args.years,
            fade_growth=args.fade_growth,
            high_growth_years=args.high_growth_years,
            growth_method=args.growth_method,
            capex_pct_override=capex_override,
        )
        dists = default_distributions(base_inputs)
        mc = run_monte_carlo(
            base_inputs,
            dists,
            n_simulations=args.simulations,
            current_price=data.current_price,
            seed=args.seed,
        )

    # Output
    if not args.quiet:
        if args.json:
            output = scenario_to_json(scenario, wacc_result, oe_results)
            if mc is not None:
                output["monte_carlo"] = {
                    "percentiles": mc.percentiles,
                    "mean": mc.mean,
                    "median": mc.median,
                    "std": mc.std,
                    "prob_above_price": mc.prob_above_price,
                    "n_simulations": mc.n_simulations,
                }
            print(json.dumps(output, indent=2))
        else:
            if wacc_result is not None:
                print(format_wacc_text(wacc_result))
                print()
            print(format_scenario_text(scenario))
            if oe_results:
                print()
                print(format_owner_earnings_text(oe_results))
            if sens is not None:
                print()
                print(format_sensitivity_text(sens))
            if mc is not None:
                print()
                print(format_montecarlo_text(mc, data.current_price))

    # Write to context/
    out_dir = (context_dir / ticker) if context_dir else None
    if args.write:
        path = write_quant_valuation_md(
            ticker, scenario, sens, mc,
            out_dir, wacc_result, oe_results,
        )
        print(f"Written to: {path}", file=sys.stderr)

    if args.json_out:
        path = write_quant_valuation_json(
            ticker, scenario, sens, mc,
            out_dir, wacc_result, oe_results,
        )
        print(f"Written to: {path}", file=sys.stderr)

    return 0
