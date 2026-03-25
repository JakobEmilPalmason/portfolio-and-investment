"""Tests for src.quant.sensitivity — 2D sensitivity grids over the DCF engine."""

import pytest

from src.quant.dcf import run_dcf
from src.quant.models import DCFInputs
from src.quant.sensitivity import build_sensitivity


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


def test_grid_dimensions(base_inputs):
    """Default n_steps=5 produces a 5x5 grid with 5 row and 5 col values."""
    sg = build_sensitivity(base_inputs, row_param="revenue_growth", col_param="wacc")

    assert len(sg.grid) == 5
    assert all(len(row) == 5 for row in sg.grid)
    assert len(sg.row_values) == 5
    assert len(sg.col_values) == 5


def test_base_case_at_center(base_inputs):
    """Base case should sit at the center of the 5x5 grid (index 2)."""
    sg = build_sensitivity(base_inputs, row_param="revenue_growth", col_param="wacc")

    assert sg.base_row_idx == 2
    assert sg.base_col_idx == 2


def test_growth_monotonicity(base_inputs):
    """For each fixed WACC column, IV should increase as revenue_growth increases."""
    sg = build_sensitivity(base_inputs, row_param="revenue_growth", col_param="wacc")

    for col in range(len(sg.col_values)):
        col_ivs = [sg.grid[row][col] for row in range(len(sg.row_values))]
        for i in range(len(col_ivs) - 1):
            assert col_ivs[i] < col_ivs[i + 1], (
                f"IV not monotonically increasing with growth in col {col}: "
                f"{col_ivs}"
            )


def test_wacc_monotonicity(base_inputs):
    """For each fixed growth row, IV should decrease as WACC increases."""
    sg = build_sensitivity(base_inputs, row_param="revenue_growth", col_param="wacc")

    for row in range(len(sg.row_values)):
        row_ivs = sg.grid[row]
        for i in range(len(row_ivs) - 1):
            assert row_ivs[i] > row_ivs[i + 1], (
                f"IV not monotonically decreasing with WACC in row {row}: "
                f"{row_ivs}"
            )


def test_base_case_matches_dcf(base_inputs):
    """Grid center cell should match a plain run_dcf within 1%."""
    sg = build_sensitivity(base_inputs, row_param="revenue_growth", col_param="wacc")
    dcf_result = run_dcf(base_inputs)

    grid_iv = sg.grid[sg.base_row_idx][sg.base_col_idx]
    dcf_iv = dcf_result.per_share_value

    assert dcf_iv != 0, "DCF per_share_value is zero — check inputs"
    pct_diff = abs(grid_iv - dcf_iv) / dcf_iv
    assert pct_diff < 0.01, (
        f"Grid center ({grid_iv}) vs run_dcf ({dcf_iv}) differ by {pct_diff:.2%}"
    )
