"""WACC calculator using CAPM. Pure functions, no I/O."""

from __future__ import annotations

from .models import FinancialData, WACCResult


def compute_effective_tax(data: FinancialData, year: int) -> float:
    """Compute effective tax rate from financials.

    Falls back to 21% US statutory if data is insufficient.
    """
    tax = data.tax_provision.get(year)
    op_inc = data.operating_income.get(year)
    interest = data.interest_expense.get(year, 0)
    if tax is not None and op_inc and op_inc > 0:
        pretax = op_inc - interest
        if pretax > 0:
            rate = tax / pretax
            if 0 <= rate <= 0.50:
                return rate
    return 0.21


def compute_wacc(
    data: FinancialData,
    risk_free_rate: float = 0.045,
    market_risk_premium: float = 0.055,
    year: int | None = None,
) -> WACCResult:
    """Compute WACC from CAPM using parsed financial data.

    Args:
        data: Parsed financials (needs beta, market_cap, total_debt,
              interest_expense, tax_provision, operating_income).
        risk_free_rate: Risk-free rate, e.g. 10Y Treasury yield.
        market_risk_premium: Equity risk premium (Rm - Rf).
        year: Fiscal year for debt/tax data. Defaults to latest.

    Returns:
        WACCResult with full breakdown.

    Raises:
        ValueError: If market_cap is missing (cannot compute equity weight).
    """
    warnings: list[str] = []

    if year is None:
        year = data.latest_year()
        if year is None:
            raise ValueError(f"No financial data available for {data.ticker}")

    # --- Cost of equity (CAPM) ---
    beta = data.beta
    if beta is None:
        beta = 1.0
        warnings.append("Beta unavailable, using 1.0 default")

    cost_of_equity = risk_free_rate + beta * market_risk_premium

    # --- Cost of debt ---
    interest = data.interest_expense.get(year)
    total_debt = data.total_debt.get(year)

    if total_debt and total_debt > 0 and interest and interest > 0:
        cost_of_debt_pretax = interest / total_debt
    elif total_debt and total_debt > 0:
        # Debt exists but no interest data — estimate from credit quality
        cost_of_debt_pretax = risk_free_rate + 0.015  # ~150bp spread
        warnings.append(f"Interest expense unavailable for FY{year}, "
                        f"estimated Rd at Rf + 1.5%")
    else:
        cost_of_debt_pretax = 0.0
        if not total_debt or total_debt == 0:
            warnings.append("Zero debt — WACC equals cost of equity")

    # --- Effective tax rate ---
    tax_rate = compute_effective_tax(data, year)

    cost_of_debt_aftertax = cost_of_debt_pretax * (1 - tax_rate)

    # --- Capital structure ---
    equity_value = data.market_cap
    if equity_value is None or equity_value <= 0:
        raise ValueError(
            f"Market cap unavailable for {data.ticker} — cannot compute WACC"
        )

    debt_value = total_debt if total_debt and total_debt > 0 else 0.0
    total_value = equity_value + debt_value

    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value

    # --- WACC ---
    wacc = (equity_weight * cost_of_equity) + (
        debt_weight * cost_of_debt_aftertax
    )

    # Clamp to reasonable range
    raw_wacc = wacc
    wacc = max(0.04, min(wacc, 0.20))
    if wacc != raw_wacc:
        warnings.append(f"WACC clamped from {raw_wacc:.4f} to {wacc:.4f}")

    return WACCResult(
        wacc=round(wacc, 4),
        cost_of_equity=round(cost_of_equity, 4),
        cost_of_debt_pretax=round(cost_of_debt_pretax, 4),
        cost_of_debt_aftertax=round(cost_of_debt_aftertax, 4),
        effective_tax_rate=round(tax_rate, 4),
        beta=beta,
        risk_free_rate=risk_free_rate,
        market_risk_premium=market_risk_premium,
        equity_value=equity_value,
        debt_value=debt_value,
        equity_weight=round(equity_weight, 4),
        debt_weight=round(debt_weight, 4),
        data_year=year,
        warnings=warnings,
    )


def wacc_from_financials(
    data: FinancialData,
    risk_free_rate: float = 0.045,
    market_risk_premium: float = 0.055,
) -> float:
    """Shorthand: returns just the WACC float for drop-in use."""
    return compute_wacc(data, risk_free_rate, market_risk_premium).wacc
