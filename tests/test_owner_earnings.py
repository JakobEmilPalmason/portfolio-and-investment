"""Tests for src.quant.owner_earnings — maintenance/growth capex separation."""

import pytest

from src.quant.models import FinancialData
from src.quant.owner_earnings import compute_owner_earnings, adjusted_capex_pct


# ---------------------------------------------------------------------------
# test_da_proxy_basic — standard case where DA < capex
# ---------------------------------------------------------------------------

def test_da_proxy_basic():
    data = FinancialData(
        ticker="TEST",
        revenue={2025: 10e9},
        net_income={2025: 1e9},
        da={2025: 5e8},
        capex={2025: -8e8},
    )
    results = compute_owner_earnings(data, method="da_proxy", n_years=1)
    assert len(results) == 1
    r = results[0]

    assert r.maintenance_capex == pytest.approx(5e8)      # min(DA, total_capex)
    assert r.growth_capex == pytest.approx(3e8)            # 8e8 - 5e8
    assert r.owner_earnings_simple == pytest.approx(7e8)   # 1e9 + 5e8 - 8e8
    assert r.owner_earnings_adjusted == pytest.approx(1e9) # 1e9 + 5e8 - 5e8


# ---------------------------------------------------------------------------
# test_da_proxy_da_exceeds_capex — DA > capex, maintenance capped at capex
# ---------------------------------------------------------------------------

def test_da_proxy_da_exceeds_capex():
    data = FinancialData(
        ticker="TEST",
        revenue={2025: 10e9},
        net_income={2025: 1e9},
        da={2025: 8e8},
        capex={2025: -3e8},
    )
    results = compute_owner_earnings(data, method="da_proxy", n_years=1)
    r = results[0]

    assert r.maintenance_capex == pytest.approx(3e8)  # capped at total capex
    assert r.growth_capex == pytest.approx(0)


# ---------------------------------------------------------------------------
# test_regression_known_linear — capex = 100M + 0.05 * revenue
# ---------------------------------------------------------------------------

def test_regression_known_linear():
    data = FinancialData(
        ticker="TEST",
        revenue={2022: 5e9, 2023: 6e9, 2024: 7e9, 2025: 8e9},
        capex={2022: -350e6, 2023: -400e6, 2024: -450e6, 2025: -500e6},
        net_income={2025: 1e9},
        da={2025: 3e8},
    )
    results = compute_owner_earnings(data, method="regression", n_years=1)
    r = results[0]

    assert r.method == "regression"
    # Intercept of the linear fit should be ~100M (maintenance capex)
    assert r.maintenance_capex == pytest.approx(100e6, rel=0.05)


# ---------------------------------------------------------------------------
# test_regression_fallback_few_points — < 3 points triggers fallback
# ---------------------------------------------------------------------------

def test_regression_fallback_few_points():
    data = FinancialData(
        ticker="TEST",
        revenue={2024: 7e9, 2025: 8e9},
        capex={2024: -450e6, 2025: -500e6},
        net_income={2025: 1e9},
        da={2025: 3e8},
    )
    results = compute_owner_earnings(data, method="regression", n_years=1)
    r = results[0]

    assert "fallback" in r.method


# ---------------------------------------------------------------------------
# test_adjusted_capex_pct — maintenance_capex / revenue for latest year
# ---------------------------------------------------------------------------

def test_adjusted_capex_pct():
    data = FinancialData(
        ticker="TEST",
        revenue={2025: 10e9},
        net_income={2025: 1e9},
        da={2025: 5e8},
        capex={2025: -8e8},
    )
    result = adjusted_capex_pct(data, method="da_proxy")

    # maintenance_capex = min(DA, capex) = 5e8; revenue = 10e9
    assert result == pytest.approx(5e8 / 10e9)
