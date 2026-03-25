"""Tests for src.quant.montecarlo — Monte Carlo simulation over the DCF engine."""

import pytest

from src.quant.models import DCFInputs
from src.quant.montecarlo import default_distributions, run_monte_carlo


@pytest.fixture
def base_inputs():
    return DCFInputs(
        base_revenue=1e9,
        base_operating_margin=0.30,
        base_tax_rate=0.20,
        base_da_pct=0.05,
        base_capex_pct=0.08,
        base_sbc_pct=0.02,
        base_nwc_pct=0.10,
        revenue_growth_rates=[0.05] * 5,
        terminal_growth_rate=0.03,
        wacc=0.10,
        exit_multiple=15.0,
        shares_outstanding=1e8,
        net_debt=5e8,
    )


def test_seeded_reproducibility(base_inputs):
    """Same seed + same inputs => identical results."""
    dists = default_distributions(base_inputs)
    r1 = run_monte_carlo(base_inputs, dists, n_simulations=1000, seed=42)
    r2 = run_monte_carlo(base_inputs, dists, n_simulations=1000, seed=42)

    assert r1.mean == r2.mean
    assert r1.percentiles == r2.percentiles


def test_different_seeds_differ(base_inputs):
    """Different seeds => different draws => different means."""
    dists = default_distributions(base_inputs)
    r1 = run_monte_carlo(base_inputs, dists, n_simulations=1000, seed=42)
    r2 = run_monte_carlo(base_inputs, dists, n_simulations=1000, seed=99)

    assert r1.mean != r2.mean


def test_extreme_low_price(base_inputs):
    """Absurdly low current_price => nearly all simulations above it."""
    dists = default_distributions(base_inputs)
    result = run_monte_carlo(
        base_inputs, dists, n_simulations=1000, current_price=1.0, seed=42,
    )

    assert result.prob_above_price > 0.99


def test_extreme_high_price(base_inputs):
    """Absurdly high current_price => nearly no simulations above it."""
    dists = default_distributions(base_inputs)
    result = run_monte_carlo(
        base_inputs, dists, n_simulations=1000, current_price=1e9, seed=42,
    )

    assert result.prob_above_price < 0.01


def test_percentile_ordering(base_inputs):
    """Percentiles must be monotonically increasing."""
    dists = default_distributions(base_inputs)
    result = run_monte_carlo(base_inputs, dists, n_simulations=1000, seed=42)

    p = result.percentiles
    assert p["P5"] < p["P25"] < p["P50"] < p["P75"] < p["P95"]
