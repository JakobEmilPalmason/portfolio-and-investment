"""Core DCF engine. Pure functions, no I/O."""

from __future__ import annotations

import sys

from .models import DCFInputs, DCFResult, FinancialData, GrowthSchedule, ScenarioResult
from .wacc import compute_effective_tax

# Conservative fallback exit multiple when Gordon growth is unstable
_FALLBACK_EXIT_MULTIPLE = 12.0


def validate_inputs(inputs: DCFInputs) -> list[str]:
    """Validate DCFInputs. Returns warnings. Raises ValueError for hard errors."""
    warnings: list[str] = []

    if inputs.shares_outstanding <= 0:
        raise ValueError("Shares outstanding must be > 0")
    if inputs.base_revenue <= 0:
        raise ValueError("Base revenue must be > 0")

    if (inputs.terminal_method == "gordon_growth"
            and inputs.wacc - inputs.terminal_growth_rate < 0.01):
        warnings.append(
            f"Gordon growth unstable: WACC ({inputs.wacc:.2%}) - g ({inputs.terminal_growth_rate:.2%}) "
            f"= {inputs.wacc - inputs.terminal_growth_rate:.2%}. Will fall back to exit multiple ({_FALLBACK_EXIT_MULTIPLE:.0f}x)."
        )

    if inputs.base_da_pct > 0 and inputs.base_capex_pct > 2 * inputs.base_da_pct:
        warnings.append(
            f"Capex ({inputs.base_capex_pct:.1%} of rev) > 2x D&A ({inputs.base_da_pct:.1%}). "
            "D&A proxy for maintenance capex may be unreliable."
        )

    if any(r < 0 for r in inputs.revenue_growth_rates):
        warnings.append("Negative revenue growth in projection — verify this is intentional.")

    if inputs.terminal_growth_rate < 0:
        warnings.append(f"Terminal growth ({inputs.terminal_growth_rate:.2%}) < 0, clamped to 0%.")
        inputs.terminal_growth_rate = 0.0
    elif inputs.terminal_growth_rate > 0.04:
        warnings.append(f"Terminal growth ({inputs.terminal_growth_rate:.2%}) > 4%, clamped to 4%.")
        inputs.terminal_growth_rate = 0.04

    if inputs.base_operating_margin <= 0:
        warnings.append(f"Operating margin ({inputs.base_operating_margin:.1%}) is non-positive.")

    return warnings


def run_dcf(inputs: DCFInputs) -> DCFResult:
    """Run a single DCF valuation. Pure function: DCFInputs -> DCFResult."""

    # Validate inputs; print warnings to stderr
    warnings = validate_inputs(inputs)
    for w in warnings:
        print(f"DCF warning: {w}", file=sys.stderr)

    n = inputs.projection_years
    target_margin = (
        inputs.target_operating_margin
        if inputs.target_operating_margin is not None
        else inputs.base_operating_margin
    )

    projected_revenue = []
    projected_ebitda = []
    projected_fcf = []
    pv_fcfs = []

    rev = inputs.base_revenue
    for year in range(n):
        # Grow revenue
        rev = rev * (1 + inputs.revenue_growth_rates[year])
        projected_revenue.append(rev)

        # Interpolate operating margin linearly from base to target
        if n > 1:
            margin = inputs.base_operating_margin + (
                target_margin - inputs.base_operating_margin
            ) * ((year + 1) / n)
        else:
            margin = target_margin

        op_income = rev * margin
        nopat = op_income * (1 - inputs.base_tax_rate)

        da = rev * inputs.base_da_pct
        capex = rev * inputs.base_capex_pct  # positive number
        sbc = rev * inputs.base_sbc_pct

        # EBITDA for terminal value calculation
        ebitda = op_income + da
        projected_ebitda.append(ebitda)

        # NWC change: delta in NWC as % of revenue change
        if year == 0:
            delta_rev = rev - inputs.base_revenue
        else:
            delta_rev = rev - projected_revenue[year - 1]
        delta_nwc = delta_rev * inputs.base_nwc_pct

        # Unlevered Free Cash Flow
        ufcf = nopat + da - capex - delta_nwc - sbc
        projected_fcf.append(ufcf)

        # Discount
        discount_factor = (1 + inputs.wacc) ** (year + 1)
        pv_fcfs.append(ufcf / discount_factor)

    # Terminal value
    if inputs.terminal_method == "gordon_growth":
        spread = inputs.wacc - inputs.terminal_growth_rate
        if spread < 0.01:
            # Gordon growth unstable — fall back to conservative exit multiple
            terminal_value = projected_ebitda[-1] * _FALLBACK_EXIT_MULTIPLE
        else:
            terminal_fcf = projected_fcf[-1] * (1 + inputs.terminal_growth_rate)
            terminal_value = terminal_fcf / spread
    else:  # exit_multiple
        terminal_ebitda = projected_ebitda[-1]
        terminal_value = terminal_ebitda * inputs.exit_multiple

    pv_terminal = terminal_value / ((1 + inputs.wacc) ** n)

    # Enterprise value
    sum_pv_fcfs = sum(pv_fcfs)
    enterprise_value = sum_pv_fcfs + pv_terminal

    # Equity value
    equity_value = enterprise_value - inputs.net_debt
    per_share = equity_value / inputs.shares_outstanding if inputs.shares_outstanding > 0 else 0

    # Implied metrics
    terminal_pct = pv_terminal / enterprise_value if enterprise_value > 0 else 0
    implied_ev_ebitda = (
        enterprise_value / projected_ebitda[0] if projected_ebitda and projected_ebitda[0] > 0 else 0
    )

    return DCFResult(
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        per_share_value=per_share,
        projected_revenue=projected_revenue,
        projected_ebitda=projected_ebitda,
        projected_fcf=projected_fcf,
        pv_fcfs=pv_fcfs,
        terminal_value=terminal_value,
        pv_terminal=pv_terminal,
        terminal_pct_of_value=terminal_pct,
        inputs=inputs,
        implied_ev_ebitda=implied_ev_ebitda,
    )


def build_growth_schedule(
    data: FinancialData,
    projection_years: int = 7,
    terminal_growth: float = 0.03,
    high_growth_years: int = 3,
    high_growth_rate: float | None = None,
    method: str = "linear_fade",
) -> GrowthSchedule:
    """Build a year-by-year growth schedule that fades from high growth to terminal.

    Args:
        data: Parsed financials (for estimating growth if not provided).
        projection_years: Total projection years.
        terminal_growth: Terminal growth rate.
        high_growth_years: Years at high growth before fade begins.
        high_growth_rate: Override for initial rate. If None, estimated from data.
        method: "linear_fade" or "roic_sustainable".
    """
    if high_growth_rate is None:
        if method == "roic_sustainable":
            high_growth_rate = _estimate_roic_growth(data)
        if high_growth_rate is None:
            high_growth_rate = _estimate_growth_rate(data)

    high_growth_years = min(high_growth_years, projection_years)
    fade_years = projection_years - high_growth_years

    rates = [high_growth_rate] * high_growth_years

    if fade_years > 0:
        for i in range(1, fade_years + 1):
            faded = high_growth_rate + (terminal_growth - high_growth_rate) * (i / fade_years)
            rates.append(round(faded, 4))

    return GrowthSchedule(
        rates=rates,
        high_growth_rate=high_growth_rate,
        terminal_rate=terminal_growth,
        fade_start_year=high_growth_years + 1,
        method=method,
    )


def _estimate_roic_growth(data: FinancialData) -> float | None:
    """Estimate sustainable growth from reinvestment rate * ROIC.

    Returns None if insufficient data (caller should fall back).
    """
    latest = data.latest_year()
    if latest is None:
        return None

    roic = data.roic.get(latest)
    if roic is None or roic <= 0:
        return None

    # Reinvestment rate = (capex - D&A + delta_NWC) / NOPAT
    capex = abs(data.capex.get(latest, 0))
    da = data.da.get(latest) or data.cf_da.get(latest) or 0
    op_inc = data.operating_income.get(latest)
    if not op_inc or op_inc <= 0:
        return None

    tax_rate = compute_effective_tax(data, latest)
    nopat = op_inc * (1 - tax_rate)
    if nopat <= 0:
        return None

    # Delta NWC approximation: use NWC change from last two years
    years = data.available_years()
    delta_nwc = 0
    if len(years) >= 2:
        wc_curr = data.working_capital.get(years[0], 0)
        wc_prev = data.working_capital.get(years[1], 0)
        delta_nwc = wc_curr - wc_prev

    net_reinvestment = capex - da + delta_nwc
    if net_reinvestment <= 0:
        return None  # company returning all capital, no reinvestment-driven growth

    reinvestment_rate = net_reinvestment / nopat
    sustainable_growth = reinvestment_rate * roic

    # Cap at reasonable range
    return max(min(sustainable_growth, 0.20), 0.0)


def build_inputs_from_financials(
    data: FinancialData,
    revenue_growth: float | None = None,
    wacc: float = 0.10,
    terminal_growth: float = 0.03,
    exit_multiple: float = 15.0,
    terminal_method: str = "exit_multiple",
    projection_years: int = 5,
    target_operating_margin: float | None = None,
    fade_growth: bool = False,
    high_growth_years: int = 3,
    growth_method: str = "linear_fade",
    capex_pct_override: float | None = None,
) -> DCFInputs:
    """Derive DCFInputs from parsed FinancialData.

    Uses most recent FY as base, with fallback to 3-year averages
    for volatile metrics.

    Args:
        fade_growth: If True, use a growth fade schedule instead of flat rates.
        high_growth_years: Years at high growth before fade (only when fade_growth=True).
        growth_method: "linear_fade" or "roic_sustainable" (only when fade_growth=True).
        capex_pct_override: Override capex % of revenue (e.g. from owner_earnings.adjusted_capex_pct).
    """
    latest = data.latest_year()
    if latest is None:
        raise ValueError(f"No financial data available for {data.ticker}")

    base_revenue = data.revenue.get(latest)
    if base_revenue is None or base_revenue <= 0:
        raise ValueError(f"No valid revenue for {data.ticker} FY{latest}")

    # Operating margin: use latest, fallback to 3-year avg
    op_margin = data.operating_margin.get(latest)
    if op_margin is None and data.operating_income.get(latest):
        op_margin = data.operating_income[latest] / base_revenue
    if op_margin is None:
        op_margin = data.avg_recent(data.operating_margin) or 0.15

    # Tax rate: from tax provision / pretax income
    tax_rate = compute_effective_tax(data, latest)

    # D&A as % of revenue
    da_val = data.da.get(latest) or data.cf_da.get(latest)
    da_pct = (da_val / base_revenue) if da_val else (data.avg_recent(data.da) or 0) / base_revenue if base_revenue else 0.05

    # Capex as % of revenue (positive number)
    capex_mode = "total"
    if capex_pct_override is not None:
        capex_pct = capex_pct_override
        capex_mode = "maintenance"
    else:
        capex_val = data.capex.get(latest)
        if capex_val is not None:
            capex_pct = abs(capex_val) / base_revenue
        else:
            capex_pct = da_pct  # fallback: maintenance = D&A

    # SBC as % of revenue
    sbc_val = data.sbc.get(latest)
    sbc_pct = (sbc_val / base_revenue) if sbc_val and sbc_val > 0 else 0.02

    # NWC as % of revenue
    wc_val = data.working_capital.get(latest)
    nwc_pct = (wc_val / base_revenue) if wc_val else 0.10

    # Revenue growth
    if fade_growth:
        schedule = build_growth_schedule(
            data,
            projection_years=projection_years,
            terminal_growth=terminal_growth,
            high_growth_years=high_growth_years,
            high_growth_rate=revenue_growth,
            method=growth_method,
        )
        growth_rates = schedule.rates
    else:
        if revenue_growth is None:
            revenue_growth = _estimate_growth_rate(data)
        growth_rates = [revenue_growth] * projection_years

    # Net debt
    nd = data.net_debt.get(latest)
    if nd is None:
        debt = data.total_debt.get(latest, 0)
        cash_val = data.cash.get(latest, 0)
        nd = debt - cash_val

    shares = data.shares_outstanding or 1.0

    return DCFInputs(
        base_revenue=base_revenue,
        base_operating_margin=op_margin,
        base_tax_rate=tax_rate,
        base_da_pct=da_pct,
        base_capex_pct=capex_pct,
        base_sbc_pct=sbc_pct,
        base_nwc_pct=nwc_pct,
        revenue_growth_rates=growth_rates,
        terminal_growth_rate=terminal_growth,
        target_operating_margin=target_operating_margin,
        wacc=wacc,
        terminal_method=terminal_method,
        exit_multiple=exit_multiple,
        capex_mode=capex_mode,
        shares_outstanding=shares,
        net_debt=nd,
    )


def _build_scenario_growth(
    data: FinancialData,
    high_growth_rate: float,
    projection_years: int,
    terminal_growth: float,
    fade_growth: bool,
    high_growth_years: int,
    growth_method: str,
) -> list[float]:
    """Build growth rates for a scenario, with or without fade."""
    if fade_growth:
        schedule = build_growth_schedule(
            data,
            projection_years=projection_years,
            terminal_growth=terminal_growth,
            high_growth_years=high_growth_years,
            high_growth_rate=high_growth_rate,
            method=growth_method,
        )
        return schedule.rates
    return [high_growth_rate] * projection_years


def run_three_scenarios(
    data: FinancialData,
    wacc: float = 0.10,
    exit_multiple: float = 15.0,
    projection_years: int = 5,
    growth_spread: float = 0.03,
    margin_spread: float = 0.03,
    wacc_spread: float = 0.01,
    multiple_spread: float = 3.0,
    fade_growth: bool = False,
    high_growth_years: int = 3,
    growth_method: str = "linear_fade",
    capex_pct_override: float | None = None,
) -> ScenarioResult:
    """Run bear/base/bull scenarios with configurable spreads.

    Default spreads:
    - Bear: growth -3pp, margin -3pp, WACC +1pp, multiple -3x
    - Bull: growth +3pp, margin +2pp, WACC -0.5pp, multiple +3x
    """
    base_inputs = build_inputs_from_financials(
        data,
        wacc=wacc,
        exit_multiple=exit_multiple,
        projection_years=projection_years,
        fade_growth=fade_growth,
        high_growth_years=high_growth_years,
        growth_method=growth_method,
        capex_pct_override=capex_pct_override,
    )

    base_growth = base_inputs.revenue_growth_rates[0]
    base_margin = base_inputs.base_operating_margin

    # --- Base case ---
    base_result = run_dcf(base_inputs)

    # --- Bear case ---
    bear_growth = max(base_growth - growth_spread, -0.05)
    bear_margin = max(base_margin - margin_spread, 0.05)
    bear_rates = _build_scenario_growth(
        data, bear_growth, projection_years, base_inputs.terminal_growth_rate,
        fade_growth, high_growth_years, growth_method,
    )
    bear_inputs = DCFInputs(
        base_revenue=base_inputs.base_revenue,
        base_operating_margin=base_inputs.base_operating_margin,
        base_tax_rate=base_inputs.base_tax_rate,
        base_da_pct=base_inputs.base_da_pct,
        base_capex_pct=base_inputs.base_capex_pct,
        base_sbc_pct=base_inputs.base_sbc_pct,
        base_nwc_pct=base_inputs.base_nwc_pct,
        revenue_growth_rates=bear_rates,
        terminal_growth_rate=base_inputs.terminal_growth_rate,
        target_operating_margin=bear_margin,
        wacc=wacc + wacc_spread,
        terminal_method=base_inputs.terminal_method,
        exit_multiple=max(exit_multiple - multiple_spread, 5.0),
        shares_outstanding=base_inputs.shares_outstanding,
        net_debt=base_inputs.net_debt,
    )
    bear_result = run_dcf(bear_inputs)

    # --- Bull case ---
    bull_growth = base_growth + growth_spread
    bull_margin = base_margin + (margin_spread * 2 / 3)  # more conservative upside
    bull_rates = _build_scenario_growth(
        data, bull_growth, projection_years, base_inputs.terminal_growth_rate,
        fade_growth, high_growth_years, growth_method,
    )
    bull_inputs = DCFInputs(
        base_revenue=base_inputs.base_revenue,
        base_operating_margin=base_inputs.base_operating_margin,
        base_tax_rate=base_inputs.base_tax_rate,
        base_da_pct=base_inputs.base_da_pct,
        base_capex_pct=base_inputs.base_capex_pct,
        base_sbc_pct=base_inputs.base_sbc_pct,
        base_nwc_pct=base_inputs.base_nwc_pct,
        revenue_growth_rates=bull_rates,
        terminal_growth_rate=base_inputs.terminal_growth_rate,
        target_operating_margin=bull_margin,
        wacc=max(wacc - wacc_spread / 2, 0.05),
        terminal_method=base_inputs.terminal_method,
        exit_multiple=exit_multiple + multiple_spread,
        shares_outstanding=base_inputs.shares_outstanding,
        net_debt=base_inputs.net_debt,
    )
    bull_result = run_dcf(bull_inputs)

    return ScenarioResult(
        bear=bear_result,
        base=base_result,
        bull=bull_result,
        current_price=data.current_price,
        currency=data.trading_currency,
    )



def _estimate_growth_rate(data: FinancialData) -> float:
    """Estimate forward revenue growth rate.

    Uses a blend of signals to avoid being misled by cyclicality:
    1. Last-year revenue growth (most recent signal)
    2. Full-period CAGR (trend)
    3. Forward vs trailing EPS growth (analyst consensus)

    Blends last-year (50%) with CAGR (25%) and EPS-implied (25%)
    to balance recency with trend. Caps at [-5%, 20%].
    """
    estimates = []
    weights = []

    years = sorted(data.revenue.keys())

    # Last-year growth (most recent, highest weight)
    if len(years) >= 2:
        prev = data.revenue[years[-2]]
        curr = data.revenue[years[-1]]
        if prev > 0 and curr > 0:
            yoy = (curr / prev) - 1
            estimates.append(yoy)
            weights.append(0.50)

    # Full-period CAGR
    if len(years) >= 3:
        first_rev = data.revenue[years[0]]
        last_rev = data.revenue[years[-1]]
        n_years = years[-1] - years[0]
        if first_rev > 0 and last_rev > 0 and n_years > 0:
            cagr = (last_rev / first_rev) ** (1 / n_years) - 1
            estimates.append(cagr)
            weights.append(0.25)

    # Forward EPS growth (analyst consensus signal)
    if data.forward_eps and data.trailing_eps and data.trailing_eps > 0:
        eps_growth = (data.forward_eps / data.trailing_eps) - 1
        # EPS growth != revenue growth, dampen it
        estimates.append(eps_growth * 0.5)
        weights.append(0.25)

    if estimates:
        total_weight = sum(weights)
        blended = sum(e * w for e, w in zip(estimates, weights)) / total_weight
        return max(min(blended, 0.20), -0.05)

    return 0.05  # conservative default
