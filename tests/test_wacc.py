"""Tests for src.quant.wacc — CAPM-based WACC calculator."""

import pytest

from src.quant.models import FinancialData
from src.quant.wacc import compute_wacc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wacc_financial_data(**overrides) -> FinancialData:
    """Return a FinancialData suitable for WACC tests."""
    defaults = dict(
        ticker="TEST",
        beta=1.2,
        market_cap=100e9,
        total_debt={2025: 20e9},
        interest_expense={2025: 1e9},
        tax_provision={2025: 2e9},
        operating_income={2025: 10e9},
        revenue={2025: 50e9},
    )
    defaults.update(overrides)
    return FinancialData(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCAPMKnownValues:

    def test_capm_known_values(self):
        data = _wacc_financial_data()
        result = compute_wacc(data, risk_free_rate=0.045, market_risk_premium=0.055)

        # Re = Rf + beta * MRP = 0.045 + 1.2 * 0.055 = 0.111
        assert result.cost_of_equity == pytest.approx(0.111, abs=0.001)

        # WACC should be in a reasonable range
        assert 0.05 < result.wacc < 0.15

        # Verify capital structure weights sum to ~1
        assert result.equity_weight + result.debt_weight == pytest.approx(1.0, abs=0.001)


class TestMissingBetaFallback:

    def test_missing_beta_fallback(self):
        data = _wacc_financial_data(beta=None)
        result = compute_wacc(data, risk_free_rate=0.045, market_risk_premium=0.055)

        assert result.beta == 1.0
        assert any("beta" in w.lower() or "Beta" in w for w in result.warnings)


class TestZeroDebt:

    def test_zero_debt(self):
        data = _wacc_financial_data(
            total_debt={2025: 0},
            interest_expense={},
        )
        result = compute_wacc(data, risk_free_rate=0.045, market_risk_premium=0.055)

        assert result.debt_weight == 0.0
        assert result.wacc == pytest.approx(result.cost_of_equity, abs=0.001)


class TestTaxShield:

    def test_tax_shield(self):
        data = _wacc_financial_data()
        result = compute_wacc(data, risk_free_rate=0.045, market_risk_premium=0.055)

        # After-tax cost of debt must be strictly less than pre-tax cost
        # (only meaningful when there is debt and a positive tax rate)
        assert result.cost_of_debt_pretax > 0
        assert result.cost_of_debt_aftertax < result.cost_of_debt_pretax
