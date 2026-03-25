"""Sensitivity analysis: 2D grids over the DCF engine."""

from __future__ import annotations

import copy

from .dcf import run_dcf
from .models import DCFInputs, SensitivityGrid


# Map human-readable param names to DCFInputs field manipulation
_PARAM_SETTERS = {
    "revenue_growth": lambda inputs, val: _set_growth(inputs, val),
    "operating_margin": lambda inputs, val: _set_attr(inputs, "target_operating_margin", val),
    "wacc": lambda inputs, val: _set_attr(inputs, "wacc", val),
    "terminal_growth": lambda inputs, val: _set_attr(inputs, "terminal_growth_rate", val),
    "exit_multiple": lambda inputs, val: _set_attr(inputs, "exit_multiple", val),
    "capex_pct": lambda inputs, val: _set_attr(inputs, "base_capex_pct", val),
    "tax_rate": lambda inputs, val: _set_attr(inputs, "base_tax_rate", val),
}

_PARAM_LABELS = {
    "revenue_growth": "Revenue Growth",
    "operating_margin": "Operating Margin",
    "wacc": "WACC",
    "terminal_growth": "Terminal Growth",
    "exit_multiple": "Exit Multiple",
    "capex_pct": "Capex % Rev",
    "tax_rate": "Tax Rate",
}


def _set_attr(inputs: DCFInputs, attr: str, val: float) -> None:
    setattr(inputs, attr, val)


def _set_growth(inputs: DCFInputs, val: float) -> None:
    inputs.revenue_growth_rates = [val] * len(inputs.revenue_growth_rates)


def _get_base_value(inputs: DCFInputs, param: str) -> float:
    """Get the base-case value for a parameter."""
    if param == "revenue_growth":
        return inputs.revenue_growth_rates[0]
    if param == "operating_margin":
        return inputs.target_operating_margin or inputs.base_operating_margin
    mapping = {
        "wacc": "wacc",
        "terminal_growth": "terminal_growth_rate",
        "exit_multiple": "exit_multiple",
        "capex_pct": "base_capex_pct",
        "tax_rate": "base_tax_rate",
    }
    return getattr(inputs, mapping[param])


def build_sensitivity(
    base_inputs: DCFInputs,
    row_param: str = "revenue_growth",
    col_param: str = "wacc",
    row_range: list[float] | None = None,
    col_range: list[float] | None = None,
    n_steps: int = 5,
) -> SensitivityGrid:
    """Build a 2D sensitivity grid.

    Args:
        base_inputs: Base-case DCF assumptions.
        row_param: Parameter to vary on rows.
        col_param: Parameter to vary on columns.
        row_range: Explicit row values. If None, auto-generated around base.
        col_range: Explicit col values. If None, auto-generated around base.
        n_steps: Number of steps if auto-generating ranges.
    """
    if row_param not in _PARAM_SETTERS:
        raise ValueError(f"Unknown param: {row_param}. Options: {list(_PARAM_SETTERS)}")
    if col_param not in _PARAM_SETTERS:
        raise ValueError(f"Unknown param: {col_param}. Options: {list(_PARAM_SETTERS)}")

    if row_range is None:
        row_range = _auto_range(base_inputs, row_param, n_steps)
    if col_range is None:
        col_range = _auto_range(base_inputs, col_param, n_steps)

    base_row_val = _get_base_value(base_inputs, row_param)
    base_col_val = _get_base_value(base_inputs, col_param)

    # Find closest index to base value
    base_row_idx = min(range(len(row_range)), key=lambda i: abs(row_range[i] - base_row_val))
    base_col_idx = min(range(len(col_range)), key=lambda i: abs(col_range[i] - base_col_val))

    grid: list[list[float]] = []
    for rv in row_range:
        row: list[float] = []
        for cv in col_range:
            inputs = copy.deepcopy(base_inputs)
            _PARAM_SETTERS[row_param](inputs, rv)
            _PARAM_SETTERS[col_param](inputs, cv)
            result = run_dcf(inputs)
            row.append(round(result.per_share_value, 2))
        grid.append(row)

    return SensitivityGrid(
        row_label=_PARAM_LABELS.get(row_param, row_param),
        col_label=_PARAM_LABELS.get(col_param, col_param),
        row_values=row_range,
        col_values=col_range,
        grid=grid,
        base_row_idx=base_row_idx,
        base_col_idx=base_col_idx,
    )


def _auto_range(inputs: DCFInputs, param: str, n_steps: int) -> list[float]:
    """Generate a range of values centered on the base case."""
    base = _get_base_value(inputs, param)

    # Different spread logic per parameter type
    if param in ("revenue_growth", "terminal_growth"):
        spread = 0.02  # +/- 2pp per step
        half = n_steps // 2
        return [round(base + (i - half) * spread, 4) for i in range(n_steps)]

    if param in ("operating_margin", "tax_rate", "capex_pct"):
        spread = 0.02
        half = n_steps // 2
        return [round(base + (i - half) * spread, 4) for i in range(n_steps)]

    if param == "wacc":
        spread = 0.01  # +/- 1pp per step
        half = n_steps // 2
        return [round(base + (i - half) * spread, 4) for i in range(n_steps)]

    if param == "exit_multiple":
        spread = 2.0  # +/- 2x per step
        half = n_steps // 2
        return [round(base + (i - half) * spread, 1) for i in range(n_steps)]

    # Generic fallback: +/- 20% in n steps
    half = n_steps // 2
    step = base * 0.1
    return [round(base + (i - half) * step, 4) for i in range(n_steps)]
