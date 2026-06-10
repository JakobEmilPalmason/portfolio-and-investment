"""Output formatting: text tables, quant-valuation.md, JSON."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import (
    DCFResult,
    FinancialData,
    MonteCarloResult,
    OwnerEarningsResult,
    ScenarioResult,
    SensitivityGrid,
    WACCResult,
)


def format_scenario_text(scenario: ScenarioResult) -> str:
    """Format bear/base/bull results as a readable text table."""
    lines = []
    lines.append(f"DCF Valuation — {scenario.currency}")
    lines.append("=" * 60)

    headers = ["", "Bear", "Base", "Bull"]
    rows = [
        (
            "Per-Share IV",
            f"{scenario.bear.per_share_value:,.2f}",
            f"{scenario.base.per_share_value:,.2f}",
            f"{scenario.bull.per_share_value:,.2f}",
        ),
        (
            "Enterprise Value",
            _fmt_b(scenario.bear.enterprise_value),
            _fmt_b(scenario.base.enterprise_value),
            _fmt_b(scenario.bull.enterprise_value),
        ),
        (
            "Equity Value",
            _fmt_b(scenario.bear.equity_value),
            _fmt_b(scenario.base.equity_value),
            _fmt_b(scenario.bull.equity_value),
        ),
        (
            "Terminal % of EV",
            f"{scenario.bear.terminal_pct_of_value:.0%}",
            f"{scenario.base.terminal_pct_of_value:.0%}",
            f"{scenario.bull.terminal_pct_of_value:.0%}",
        ),
        (
            "Discount Rate" if scenario.base.inputs.discount_method == "fixed" else "WACC",
            f"{scenario.bear.inputs.wacc:.1%}",
            f"{scenario.base.inputs.wacc:.1%}",
            f"{scenario.bull.inputs.wacc:.1%}",
        ),
        (
            "Rev Growth (Y1)",
            f"{scenario.bear.inputs.revenue_growth_rates[0]:.1%}",
            f"{scenario.base.inputs.revenue_growth_rates[0]:.1%}",
            f"{scenario.bull.inputs.revenue_growth_rates[0]:.1%}",
        ),
        (
            "Exit Multiple",
            f"{scenario.bear.inputs.exit_multiple:.1f}x",
            f"{scenario.base.inputs.exit_multiple:.1f}x",
            f"{scenario.bull.inputs.exit_multiple:.1f}x",
        ),
    ]

    # Add final-year growth row if rates fade (not flat)
    base_rates = scenario.base.inputs.revenue_growth_rates
    if len(base_rates) > 1 and base_rates[0] != base_rates[-1]:
        n = len(base_rates)
        rows.append((
            f"Rev Growth (Y{n})",
            f"{scenario.bear.inputs.revenue_growth_rates[-1]:.1%}",
            f"{scenario.base.inputs.revenue_growth_rates[-1]:.1%}",
            f"{scenario.bull.inputs.revenue_growth_rates[-1]:.1%}",
        ))

    # Calculate column widths
    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) + 2 for i in range(4)]
    fmt = "".join(f"{{:<{w}}}" for w in widths)

    lines.append(fmt.format(*headers))
    lines.append("-" * sum(widths))
    for row in rows:
        lines.append(fmt.format(*row))

    if scenario.current_price is not None:
        lines.append("")
        lines.append(f"Current Price: {scenario.current_price:,.2f} {scenario.currency}")
        mos = scenario.mos_at_analysis
        if mos is not None:
            label = "cheap" if mos > 0 else "expensive"
            lines.append(f"MOS vs Bear IV: {mos:+.1f}% ({label})")

    return "\n".join(lines)


def format_sensitivity_text(grid: SensitivityGrid) -> str:
    """Format sensitivity grid as a text table."""
    lines = []
    lines.append(f"Sensitivity: {grid.row_label} (rows) vs {grid.col_label} (cols)")
    lines.append("")

    # Format column headers
    col_strs = [_fmt_param_val(grid.col_label, v) for v in grid.col_values]
    row_strs = [_fmt_param_val(grid.row_label, v) for v in grid.row_values]

    # Column widths
    val_width = max(8, *(len(s) for s in col_strs))
    label_width = max(len(grid.row_label), *(len(s) for s in row_strs)) + 2

    # Header row
    header = f"{'':>{label_width}}"
    for j, cs in enumerate(col_strs):
        marker = " *" if j == grid.base_col_idx else "  "
        header += f"  {cs:>{val_width}}{marker}"
    lines.append(header)
    lines.append("-" * len(header))

    # Data rows
    for i, rv in enumerate(grid.row_values):
        marker = " *" if i == grid.base_row_idx else "  "
        row = f"{row_strs[i]:>{label_width}}{marker}"
        for j, val in enumerate(grid.grid[i]):
            cell_marker = " *" if (i == grid.base_row_idx and j == grid.base_col_idx) else "  "
            row += f"  {val:>{val_width},.2f}{cell_marker}"
        lines.append(row)

    lines.append("")
    lines.append("* = base case")

    return "\n".join(lines)


def format_montecarlo_text(mc: MonteCarloResult, current_price: float | None = None) -> str:
    """Format Monte Carlo results as text."""
    lines = []
    lines.append(f"Monte Carlo Simulation ({mc.n_simulations:,} runs)")
    lines.append("=" * 50)
    lines.append("")

    lines.append("Percentile Distribution:")
    for label, val in sorted(mc.percentiles.items(), key=lambda x: int(x[0][1:])):
        lines.append(f"  {label:>4}: {val:>10,.2f}")

    lines.append("")
    lines.append(f"  Mean:   {mc.mean:>10,.2f}")
    lines.append(f"  Median: {mc.median:>10,.2f}")
    lines.append(f"  Std:    {mc.std:>10,.2f}")

    if current_price is not None:
        lines.append("")
        lines.append(f"Current Price: {current_price:,.2f}")
        lines.append(f"P(IV > Price): {mc.prob_above_price:.1%}")

    return "\n".join(lines)


def format_wacc_text(wacc: WACCResult) -> str:
    """Format WACC derivation as a readable text block."""
    lines = []
    lines.append(f"WACC Derivation (CAPM) — FY{wacc.data_year}")
    lines.append("=" * 50)
    lines.append(f"  Risk-Free Rate (Rf):       {wacc.risk_free_rate:.1%}")
    lines.append(f"  Beta:                      {wacc.beta:.2f}")
    lines.append(f"  Market Risk Premium:       {wacc.market_risk_premium:.1%}")
    lines.append(f"  Cost of Equity (Re):       {wacc.cost_of_equity:.1%}")
    lines.append(f"  Cost of Debt (Rd, pre-tax):{wacc.cost_of_debt_pretax:.1%}")
    lines.append(f"  Effective Tax Rate:        {wacc.effective_tax_rate:.1%}")
    lines.append(f"  Cost of Debt (after-tax):  {wacc.cost_of_debt_aftertax:.1%}")
    lines.append(f"  Equity Weight:             {wacc.equity_weight:.1%}")
    lines.append(f"  Debt Weight:               {wacc.debt_weight:.1%}")
    lines.append(f"  WACC:                      {wacc.wacc:.1%}")
    if wacc.warnings:
        lines.append("")
        for w in wacc.warnings:
            lines.append(f"  Warning: {w}")
    return "\n".join(lines)


def format_owner_earnings_text(results: list[OwnerEarningsResult]) -> str:
    """Format owner earnings breakdown as text."""
    if not results:
        return "No owner earnings data available."

    lines = []
    lines.append(f"Owner Earnings ({results[0].method})")
    lines.append("=" * 60)

    headers = ["", *(f"FY{r.year}" for r in results)]
    rows = [
        ("Net Income", *(f"{_fmt_b(r.net_income)}" for r in results)),
        ("+ D&A", *(f"{_fmt_b(r.da)}" for r in results)),
        ("- Total CapEx", *(f"{_fmt_b(r.total_capex)}" for r in results)),
        ("  Maintenance", *(f"{_fmt_b(r.maintenance_capex)}" for r in results)),
        ("  Growth", *(f"{_fmt_b(r.growth_capex)}" for r in results)),
        ("OE (simple)", *(f"{_fmt_b(r.owner_earnings_simple)}" for r in results)),
        ("OE (adjusted)", *(f"{_fmt_b(r.owner_earnings_adjusted)}" for r in results)),
        ("Maint % of CapEx", *(f"{r.maintenance_pct_of_total:.0%}" for r in results)),
    ]

    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) + 2 for i in range(len(headers))]
    fmt = "".join(f"{{:<{w}}}" for w in widths)

    lines.append(fmt.format(*headers))
    lines.append("-" * sum(widths))
    for row in rows:
        lines.append(fmt.format(*row))

    return "\n".join(lines)


def write_quant_valuation_md(
    ticker: str,
    scenario: ScenarioResult,
    sensitivity: SensitivityGrid | None = None,
    montecarlo: MonteCarloResult | None = None,
    output_dir: Path | None = None,
    wacc_result: WACCResult | None = None,
    owner_earnings: list[OwnerEarningsResult] | None = None,
) -> Path:
    """Write data/context/{TICKER}/quant-valuation.md."""
    if output_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        output_dir = repo_root / "data" / "context" / ticker

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "quant-valuation.md"

    lines = []
    lines.append(f"# Quantitative Valuation: {ticker}")
    lines.append("")
    lines.append(f"**Generated:** {date.today().isoformat()}")
    lines.append(f"**Model:** DCF (exit multiple)")
    lines.append("")
    lines.append("> Auto-generated by `src/quant`. Deterministic model — assumptions are derived")
    lines.append("> from historical financials, not AI judgment. Override assumptions via CLI flags.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Scenario summary
    lines.append(format_scenario_text(scenario))
    lines.append("")
    lines.append("---")
    lines.append("")

    # IV Summary table (machine-readable, same format as umbrella 06)
    lines.append("## Intrinsic Value Summary")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| IV Conservative (Bear) | {scenario.bear.per_share_value:.0f} |")
    lines.append(f"| IV Base | {scenario.base.per_share_value:.0f} |")
    lines.append(f"| IV Bull | {scenario.bull.per_share_value:.0f} |")
    lines.append(f"| Currency | {scenario.currency} |")
    mos = scenario.mos_at_analysis
    lines.append(f"| MOS at Analysis Date | {mos:.1f} |" if mos is not None else "| MOS at Analysis Date | n/a |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Key assumptions
    base = scenario.base.inputs
    lines.append("## Key Assumptions (Base Case)")
    lines.append("")
    lines.append("| Assumption | Value |")
    lines.append("|------------|-------|")
    lines.append(f"| Base Revenue | {base.base_revenue / 1e9:.1f}B |")
    if len(base.revenue_growth_rates) > 1 and base.revenue_growth_rates[0] != base.revenue_growth_rates[-1]:
        lines.append(f"| Revenue Growth (Y1) | {base.revenue_growth_rates[0]:.1%} |")
        lines.append(f"| Revenue Growth (Y{base.projection_years}) | {base.revenue_growth_rates[-1]:.1%} |")
        lines.append(f"| Growth Fade | Yes ({base.projection_years} years) |")
    else:
        lines.append(f"| Revenue Growth | {base.revenue_growth_rates[0]:.1%} |")
    lines.append(f"| Operating Margin | {base.base_operating_margin:.1%} |")
    lines.append(f"| Tax Rate | {base.base_tax_rate:.1%} |")
    if base.discount_method == "fixed":
        lines.append(f"| Discount Rate | {base.wacc:.1%} (Buffett-style fixed) |")
    elif base.discount_method == "capm":
        lines.append(f"| WACC | {base.wacc:.1%} (CAPM-derived) |")
    else:
        lines.append(f"| WACC | {base.wacc:.1%} |")
    lines.append(f"| Exit Multiple | {base.exit_multiple:.1f}x EV/EBITDA |")
    if base.capex_mode == "maintenance":
        lines.append(f"| CapEx Mode | Maintenance only (owner earnings) — {base.base_capex_pct:.1%} of rev |")
    lines.append(f"| Projection Years | {base.projection_years} |")
    lines.append(f"| Terminal Growth | {base.terminal_growth_rate:.1%} |")
    lines.append(f"| Net Debt | {base.net_debt / 1e9:.1f}B |")
    lines.append(f"| Shares Outstanding | {base.shares_outstanding / 1e6:.1f}M |")
    lines.append("")

    # WACC derivation
    if wacc_result is not None:
        lines.append("---")
        lines.append("")
        lines.append("## WACC Derivation (CAPM)")
        lines.append("")
        lines.append("| Component | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Risk-Free Rate (Rf) | {wacc_result.risk_free_rate:.1%} |")
        lines.append(f"| Beta | {wacc_result.beta:.2f} |")
        lines.append(f"| Market Risk Premium | {wacc_result.market_risk_premium:.1%} |")
        lines.append(f"| Cost of Equity (Re) | {wacc_result.cost_of_equity:.1%} |")
        lines.append(f"| Cost of Debt (Rd, pre-tax) | {wacc_result.cost_of_debt_pretax:.1%} |")
        lines.append(f"| Effective Tax Rate | {wacc_result.effective_tax_rate:.1%} |")
        lines.append(f"| Cost of Debt (after-tax) | {wacc_result.cost_of_debt_aftertax:.1%} |")
        lines.append(f"| Equity Weight | {wacc_result.equity_weight:.1%} |")
        lines.append(f"| Debt Weight | {wacc_result.debt_weight:.1%} |")
        lines.append(f"| **WACC** | **{wacc_result.wacc:.1%}** |")
        if wacc_result.warnings:
            lines.append("")
            for w in wacc_result.warnings:
                lines.append(f"> Warning: {w}")
        lines.append("")

    # Owner earnings
    if owner_earnings:
        lines.append("---")
        lines.append("")
        lines.append("## Owner Earnings")
        lines.append("")
        lines.append("```")
        lines.append(format_owner_earnings_text(owner_earnings))
        lines.append("```")
        lines.append("")

    # Sensitivity table
    if sensitivity is not None:
        lines.append("---")
        lines.append("")
        lines.append("## Sensitivity Analysis")
        lines.append("")
        lines.append("```")
        lines.append(format_sensitivity_text(sensitivity))
        lines.append("```")
        lines.append("")

    # Monte Carlo
    if montecarlo is not None:
        lines.append("---")
        lines.append("")
        lines.append("## Monte Carlo Simulation")
        lines.append("")
        lines.append("```")
        lines.append(format_montecarlo_text(montecarlo, scenario.current_price))
        lines.append("```")
        lines.append("")

    path.write_text("\n".join(lines))
    return path


def scenario_to_json(
    scenario: ScenarioResult,
    wacc_result: WACCResult | None = None,
    owner_earnings: list[OwnerEarningsResult] | None = None,
) -> dict:
    """Convert ScenarioResult to a JSON-serializable dict."""
    result = {
        "bear": scenario.bear.summary_dict(),
        "base": scenario.base.summary_dict(),
        "bull": scenario.bull.summary_dict(),
        "iv_conservative": round(scenario.bear.per_share_value, 2),
        "iv_base": round(scenario.base.per_share_value, 2),
        "iv_bull": round(scenario.bull.per_share_value, 2),
        "currency": scenario.currency,
        "current_price": scenario.current_price,
        "mos_at_analysis": round(scenario.mos_at_analysis, 1) if scenario.mos_at_analysis is not None else None,
        "model_date": date.today().isoformat(),
        "discount_method": scenario.base.inputs.discount_method,
        "capex_mode": scenario.base.inputs.capex_mode,
    }

    # Growth schedule (always include if rates fade)
    base_rates = scenario.base.inputs.revenue_growth_rates
    if len(base_rates) > 1 and base_rates[0] != base_rates[-1]:
        result["growth_schedule"] = [round(r, 4) for r in base_rates]

    # WACC derivation (when auto-computed)
    if wacc_result is not None:
        result["wacc_derivation"] = {
            "wacc": wacc_result.wacc,
            "cost_of_equity": wacc_result.cost_of_equity,
            "cost_of_debt_pretax": wacc_result.cost_of_debt_pretax,
            "cost_of_debt_aftertax": wacc_result.cost_of_debt_aftertax,
            "effective_tax_rate": wacc_result.effective_tax_rate,
            "beta": wacc_result.beta,
            "risk_free_rate": wacc_result.risk_free_rate,
            "market_risk_premium": wacc_result.market_risk_premium,
            "equity_weight": wacc_result.equity_weight,
            "debt_weight": wacc_result.debt_weight,
            "warnings": wacc_result.warnings,
        }

    # Owner earnings (when computed)
    if owner_earnings:
        latest = owner_earnings[0]
        result["owner_earnings"] = {
            "method": latest.method,
            "maintenance_capex": round(latest.maintenance_capex),
            "growth_capex": round(latest.growth_capex),
            "owner_earnings_adjusted": round(latest.owner_earnings_adjusted),
            "maintenance_pct_of_total": round(latest.maintenance_pct_of_total, 2),
        }

    return result


def write_quant_valuation_json(
    ticker: str,
    scenario: ScenarioResult,
    sensitivity: SensitivityGrid | None = None,
    montecarlo: MonteCarloResult | None = None,
    output_dir: Path | None = None,
    wacc_result: WACCResult | None = None,
    owner_earnings: list[OwnerEarningsResult] | None = None,
) -> Path:
    """Write data/context/{TICKER}/quant-valuation.json — machine-readable valuation."""
    if output_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        output_dir = repo_root / "data" / "context" / ticker

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "quant-valuation.json"

    result = scenario_to_json(scenario, wacc_result, owner_earnings)
    result["ticker"] = ticker
    result["model"] = "dcf_exit_multiple"

    if sensitivity is not None:
        result["sensitivity"] = {
            "row_param": sensitivity.row_label,
            "col_param": sensitivity.col_label,
            "row_values": [round(v, 4) for v in sensitivity.row_values],
            "col_values": [round(v, 4) for v in sensitivity.col_values],
            "grid": [[round(cell, 2) for cell in row] for row in sensitivity.grid],
            "base_row_idx": sensitivity.base_row_idx,
            "base_col_idx": sensitivity.base_col_idx,
        }

    if montecarlo is not None:
        result["monte_carlo"] = {
            "percentiles": montecarlo.percentiles,
            "mean": round(montecarlo.mean, 2),
            "median": round(montecarlo.median, 2),
            "std": round(montecarlo.std, 2),
            "prob_above_price": round(montecarlo.prob_above_price, 4),
            "n_simulations": montecarlo.n_simulations,
        }

    path.write_text(json.dumps(result, indent=2) + "\n")
    return path


def _fmt_b(val: float) -> str:
    """Format large number as XB or XM."""
    if abs(val) >= 1e9:
        return f"{val / 1e9:.1f}B"
    if abs(val) >= 1e6:
        return f"{val / 1e6:.0f}M"
    return f"{val:,.0f}"


def _fmt_param_val(label: str, val: float) -> str:
    """Format a parameter value for display in sensitivity tables."""
    if "Growth" in label or "Margin" in label or "WACC" in label or "Tax" in label or "Capex" in label:
        return f"{val:.1%}"
    if "Multiple" in label:
        return f"{val:.1f}x"
    return f"{val:.2f}"
