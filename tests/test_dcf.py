"""Tests for src.quant.dcf — DCF engine, growth schedules, input builders."""

import pytest

from src.quant.dcf import build_growth_schedule, build_inputs_from_financials, run_dcf, validate_inputs
from src.quant.models import DCFInputs, FinancialData


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _round_number_inputs(**overrides) -> DCFInputs:
    """Return a DCFInputs with clean round numbers, easy to hand-verify."""
    defaults = dict(
        base_revenue=1_000_000_000,
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
        terminal_method="exit_multiple",
        shares_outstanding=100_000_000,
        net_debt=500_000_000,
    )
    defaults.update(overrides)
    return DCFInputs(**defaults)


def _minimal_financial_data(**overrides) -> FinancialData:
    """Return a minimal FinancialData sufficient for build_inputs_from_financials."""
    defaults = dict(
        ticker="TEST",
        revenue={2025: 1e9},
        operating_income={2025: 3e8},
        capex={2025: -8e7},
        da={2025: 5e7},
        net_income={2025: 2e8},
        tax_provision={2025: 5e7},
        shares_outstanding=1e8,
        total_debt={2025: 5e8},
        cash={2025: 1e8},
        working_capital={2025: 1e8},
        sbc={2025: 2e7},
    )
    defaults.update(overrides)
    return FinancialData(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDCFKnownInputs:
    """test_dcf_known_inputs — hand-calculated reference case."""

    def test_dcf_known_inputs(self):
        inputs = _round_number_inputs()
        result = run_dcf(inputs)

        # Hand-calculated expected value: 44.6776 per share.
        # 5-year exit-multiple DCF with 5% flat growth, 30% operating margin,
        # 20% tax, 10% WACC, 15x EV/EBITDA exit, 500M net debt, 100M shares.
        assert result.per_share_value == pytest.approx(44.6776, rel=0.01)

        # Sanity: EV > equity (positive net debt)
        assert result.enterprise_value > result.equity_value
        assert result.equity_value == pytest.approx(
            result.enterprise_value - 500_000_000, abs=1
        )


class TestDCFEdgeCases:

    def test_dcf_negative_growth(self):
        inputs = _round_number_inputs(revenue_growth_rates=[-0.03] * 5)
        result = run_dcf(inputs)
        assert result.per_share_value > 0

    def test_dcf_zero_debt(self):
        inputs = _round_number_inputs(net_debt=0)
        result = run_dcf(inputs)
        assert result.equity_value == pytest.approx(
            result.enterprise_value, abs=1
        )


class TestGrowthSchedule:

    def test_growth_fade_monotonicity(self):
        data = _minimal_financial_data()
        schedule = build_growth_schedule(
            data,
            high_growth_rate=0.12,
            terminal_growth=0.03,
            high_growth_years=3,
            projection_years=7,
        )
        rates = schedule.rates

        assert len(rates) == 7
        assert rates[0] == 0.12
        assert rates[-1] == pytest.approx(0.03, abs=0.005)

        # High-growth plateau: first 3 years all equal
        for r in rates[:3]:
            assert r == 0.12

        # Fade portion (index 3 onward) is monotonically non-increasing
        fade = rates[3:]
        for i in range(1, len(fade)):
            assert fade[i] <= fade[i - 1] + 1e-9


class TestGordonGrowthGuardRail:

    def test_gordon_growth_guard_rail(self):
        # spread = 0.04 - 0.035 = 0.005 < 0.01 => unstable, falls back to exit multiple
        inputs = _round_number_inputs(
            terminal_method="gordon_growth",
            wacc=0.04,
            terminal_growth_rate=0.035,
        )
        result = run_dcf(inputs)
        assert result.per_share_value > 0


class TestValidateInputs:

    def test_validate_inputs_hard_errors(self):
        with pytest.raises(ValueError, match="Shares outstanding"):
            inputs = _round_number_inputs(shares_outstanding=0)
            validate_inputs(inputs)

        with pytest.raises(ValueError, match="Base revenue"):
            inputs = _round_number_inputs(base_revenue=0)
            validate_inputs(inputs)

    def test_validate_inputs_warnings_da_proxy(self):
        # capex_pct=0.20 > 2 * da_pct=0.05 => triggers D&A proxy warning
        inputs = _round_number_inputs(base_capex_pct=0.20, base_da_pct=0.05)
        warnings = validate_inputs(inputs)
        assert any("D&A proxy" in w for w in warnings)

    def test_validate_terminal_growth_clamp(self):
        inputs = _round_number_inputs(terminal_growth_rate=0.06)
        warnings = validate_inputs(inputs)
        assert any("clamped" in w.lower() or "clamp" in w.lower() for w in warnings)
        assert inputs.terminal_growth_rate == 0.04


class TestBuildInputsFromFinancials:

    def test_capex_mode_set(self):
        data = _minimal_financial_data()
        inputs = build_inputs_from_financials(data, capex_pct_override=0.05)
        assert inputs.capex_mode == "maintenance"
