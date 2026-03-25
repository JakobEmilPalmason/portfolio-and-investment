"""Monte Carlo simulation over the DCF engine."""

from __future__ import annotations

import copy
import random
import statistics

from .dcf import run_dcf
from .models import DCFInputs, MonteCarloResult


# Distribution samplers using stdlib random
_SAMPLERS = {
    "normal": lambda rng, params: rng.gauss(params[0], params[1]),
    "uniform": lambda rng, params: rng.uniform(params[0], params[1]),
    "triangular": lambda rng, params: rng.triangular(params[0], params[1], params[2]),
}


def run_monte_carlo(
    base_inputs: DCFInputs,
    distributions: dict[str, tuple[str, ...]],
    n_simulations: int = 10_000,
    current_price: float | None = None,
    seed: int | None = None,
) -> MonteCarloResult:
    """Run Monte Carlo simulation on DCF assumptions.

    Args:
        base_inputs: Base-case DCF inputs (unchanged fields use base values).
        distributions: Parameters to randomize. Keys are param names
            (same as sensitivity.py), values are (dist_type, *params):
            - ("normal", mean, std)
            - ("uniform", low, high)
            - ("triangular", low, high, mode)
        n_simulations: Number of DCF runs.
        current_price: If provided, computes P(IV > price).
        seed: Random seed for reproducibility.

    Returns:
        MonteCarloResult with percentiles, histogram data, etc.
    """
    rng = random.Random(seed)
    results: list[float] = []

    for _ in range(n_simulations):
        inputs = copy.deepcopy(base_inputs)

        for param, dist_spec in distributions.items():
            dist_type = dist_spec[0]
            params = dist_spec[1:]

            if dist_type not in _SAMPLERS:
                raise ValueError(f"Unknown distribution: {dist_type}. Options: {list(_SAMPLERS)}")

            value = _SAMPLERS[dist_type](rng, params)

            # Apply the sampled value
            _apply_param(inputs, param, value)

        dcf_result = run_dcf(inputs)
        results.append(dcf_result.per_share_value)

    results.sort()
    n = len(results)

    percentiles = {}
    for p in [5, 10, 25, 50, 75, 90, 95]:
        idx = int(n * p / 100)
        idx = min(idx, n - 1)
        percentiles[f"P{p}"] = round(results[idx], 2)

    mean = statistics.mean(results)
    median = statistics.median(results)
    std = statistics.stdev(results) if n > 1 else 0

    prob_above = 0.0
    if current_price is not None and n > 0:
        above = sum(1 for v in results if v > current_price)
        prob_above = above / n

    return MonteCarloResult(
        n_simulations=n,
        percentiles=percentiles,
        mean=round(mean, 2),
        median=round(median, 2),
        std=round(std, 2),
        prob_above_price=round(prob_above, 4),
        histogram_data=results,
    )


def _apply_param(inputs: DCFInputs, param: str, value: float) -> None:
    """Apply a sampled parameter value to DCFInputs."""
    if param == "revenue_growth":
        inputs.revenue_growth_rates = [value] * len(inputs.revenue_growth_rates)
    elif param == "operating_margin":
        inputs.target_operating_margin = value
    elif param == "wacc":
        inputs.wacc = max(value, 0.01)  # floor at 1%
    elif param == "terminal_growth":
        inputs.terminal_growth_rate = max(value, 0.0)
    elif param == "exit_multiple":
        inputs.exit_multiple = max(value, 1.0)
    elif param == "capex_pct":
        inputs.base_capex_pct = max(value, 0.0)
    elif param == "tax_rate":
        inputs.base_tax_rate = max(min(value, 0.5), 0.0)
    else:
        raise ValueError(f"Unknown param: {param}")


def default_distributions(base_inputs: DCFInputs) -> dict[str, tuple[str, ...]]:
    """Generate sensible default distributions from base-case inputs.

    Uses triangular distributions centered on base-case values with
    reasonable ranges for each parameter.
    """
    base_growth = base_inputs.revenue_growth_rates[0]
    base_margin = (
        base_inputs.target_operating_margin
        if base_inputs.target_operating_margin is not None
        else base_inputs.base_operating_margin
    )

    return {
        "revenue_growth": (
            "triangular",
            max(base_growth - 0.05, -0.05),
            base_growth + 0.05,
            base_growth,
        ),
        "operating_margin": (
            "triangular",
            max(base_margin - 0.05, 0.05),
            min(base_margin + 0.05, 0.70),
            base_margin,
        ),
        "wacc": (
            "triangular",
            max(base_inputs.wacc - 0.02, 0.04),
            base_inputs.wacc + 0.02,
            base_inputs.wacc,
        ),
        "exit_multiple": (
            "triangular",
            max(base_inputs.exit_multiple - 4, 5.0),
            base_inputs.exit_multiple + 4,
            base_inputs.exit_multiple,
        ),
    }
