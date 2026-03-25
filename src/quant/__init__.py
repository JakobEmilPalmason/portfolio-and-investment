"""Quantitative valuation models.

Deterministic DCF, sensitivity analysis, and Monte Carlo simulation.
Replaces AI-guessed valuations with auditable, reproducible models.
Data source: fetch-financials.py (yfinance) -> context/{TICKER}/financials.md
"""

from .dcf import build_growth_schedule, build_inputs_from_financials, run_dcf, run_three_scenarios
from .formatters import (
    format_montecarlo_text,
    format_owner_earnings_text,
    format_scenario_text,
    format_sensitivity_text,
    format_wacc_text,
    scenario_to_json,
    write_quant_valuation_md,
)
from .models import (
    DCFInputs,
    DCFResult,
    FinancialData,
    GrowthSchedule,
    MonteCarloResult,
    OwnerEarningsResult,
    ScenarioResult,
    SensitivityGrid,
    WACCResult,
)
from .montecarlo import default_distributions, run_monte_carlo
from .owner_earnings import adjusted_capex_pct, compute_owner_earnings
from .parser import parse_financials
from .sensitivity import build_sensitivity
from .wacc import compute_wacc, wacc_from_financials

__all__ = [
    "DCFInputs",
    "DCFResult",
    "FinancialData",
    "GrowthSchedule",
    "MonteCarloResult",
    "OwnerEarningsResult",
    "ScenarioResult",
    "SensitivityGrid",
    "WACCResult",
    "adjusted_capex_pct",
    "build_growth_schedule",
    "build_inputs_from_financials",
    "build_sensitivity",
    "compute_owner_earnings",
    "compute_wacc",
    "default_distributions",
    "format_montecarlo_text",
    "format_owner_earnings_text",
    "format_scenario_text",
    "format_sensitivity_text",
    "format_wacc_text",
    "parse_financials",
    "run_dcf",
    "run_monte_carlo",
    "run_three_scenarios",
    "scenario_to_json",
    "wacc_from_financials",
    "write_quant_valuation_md",
]
