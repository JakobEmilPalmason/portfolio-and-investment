"""Owner earnings with maintenance/growth capex separation. Pure functions, no I/O."""

from __future__ import annotations

from .models import FinancialData, OwnerEarningsResult


def _da_proxy(data: FinancialData, year: int) -> OwnerEarningsResult:
    """Estimate maintenance capex as D&A. Simplest, most defensible."""
    ni = data.net_income.get(year, 0)
    da = data.da.get(year) or data.cf_da.get(year) or 0
    total_capex = abs(data.capex.get(year, 0))

    # If D&A > capex, company is under-investing — maintenance = total capex
    maintenance = min(da, total_capex)
    growth = total_capex - maintenance

    return OwnerEarningsResult(
        year=year,
        net_income=ni,
        da=da,
        total_capex=total_capex,
        maintenance_capex=maintenance,
        growth_capex=growth,
        owner_earnings_simple=ni + da - total_capex,
        owner_earnings_adjusted=ni + da - maintenance,
        method="da_proxy",
        maintenance_pct_of_total=(maintenance / total_capex) if total_capex > 0 else 1.0,
    )


def _regression_method(data: FinancialData, target_year: int) -> OwnerEarningsResult:
    """Estimate maintenance capex via revenue regression.

    Fits capex = a + b * revenue across available years.
    Intercept (a) approximates the fixed maintenance component.
    Falls back to D&A proxy if < 3 data points or negative intercept.
    """
    # Collect (revenue, abs(capex)) pairs
    pairs: list[tuple[float, float]] = []
    for yr in sorted(data.revenue.keys()):
        rev = data.revenue.get(yr)
        cap = data.capex.get(yr)
        if rev and rev > 0 and cap is not None:
            pairs.append((rev, abs(cap)))

    if len(pairs) < 3:
        # Not enough data — fall back
        result = _da_proxy(data, target_year)
        result.method = "regression(fallback:da_proxy,<3pts)"
        return result

    # Simple OLS: b = cov(x,y) / var(x), a = mean(y) - b * mean(x)
    n = len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    cov_xy = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / (n - 1)
    var_x = sum((x - mean_x) ** 2 for x in xs) / (n - 1)

    if var_x == 0:
        result = _da_proxy(data, target_year)
        result.method = "regression(fallback:da_proxy,zero_variance)"
        return result

    b = cov_xy / var_x
    a = mean_y - b * mean_x  # intercept = maintenance capex estimate

    if a < 0:
        # Negative intercept is nonsensical — fall back
        result = _da_proxy(data, target_year)
        result.method = "regression(fallback:da_proxy,negative_intercept)"
        return result

    ni = data.net_income.get(target_year, 0)
    da = data.da.get(target_year) or data.cf_da.get(target_year) or 0
    total_capex = abs(data.capex.get(target_year, 0))

    maintenance = min(a, total_capex)  # can't exceed total
    growth = total_capex - maintenance

    return OwnerEarningsResult(
        year=target_year,
        net_income=ni,
        da=da,
        total_capex=total_capex,
        maintenance_capex=round(maintenance),
        growth_capex=round(growth),
        owner_earnings_simple=ni + da - total_capex,
        owner_earnings_adjusted=ni + da - maintenance,
        method="regression",
        maintenance_pct_of_total=(maintenance / total_capex) if total_capex > 0 else 1.0,
    )


_METHODS = {
    "da_proxy": _da_proxy,
    "regression": _regression_method,
}


def compute_owner_earnings(
    data: FinancialData,
    method: str = "da_proxy",
    n_years: int = 4,
) -> list[OwnerEarningsResult]:
    """Compute owner earnings with maintenance capex separation.

    Args:
        data: Parsed financials.
        method: "da_proxy" or "regression".
        n_years: Number of most recent years to compute.

    Returns:
        List of OwnerEarningsResult, most recent first.
    """
    if method not in _METHODS:
        raise ValueError(f"Unknown method: {method}. Options: {list(_METHODS)}")

    fn = _METHODS[method]
    years = data.available_years()[:n_years]
    return [fn(data, yr) for yr in years]


def adjusted_capex_pct(
    data: FinancialData,
    method: str = "da_proxy",
) -> float:
    """Return maintenance_capex / revenue for latest year.

    Drop-in replacement for base_capex_pct in DCFInputs.
    """
    latest = data.latest_year()
    if latest is None:
        return 0.05  # conservative default

    rev = data.revenue.get(latest)
    if not rev or rev <= 0:
        return 0.05

    fn = _METHODS.get(method, _da_proxy)
    result = fn(data, latest)
    return result.maintenance_capex / rev
