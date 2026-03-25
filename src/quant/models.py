"""Data schemas for quantitative valuation models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FinancialData:
    """Parsed financial data from context/{TICKER}/financials.md."""

    ticker: str = ""
    company: str = ""
    generated_date: str = ""
    reporting_currency: str = "USD"
    trading_currency: str = "USD"
    sector: str = ""
    industry: str = ""

    # Snapshot
    current_price: float | None = None
    market_cap: float | None = None
    enterprise_value: float | None = None
    shares_outstanding: float | None = None
    beta: float | None = None
    dividend_yield: float | None = None
    week52_high: float | None = None
    week52_low: float | None = None

    # Valuation multiples
    trailing_pe: float | None = None
    forward_pe: float | None = None
    ev_ebitda: float | None = None
    ev_revenue: float | None = None
    p_fcf: float | None = None
    p_s: float | None = None
    p_b: float | None = None

    # Analyst estimates
    forward_eps: float | None = None
    trailing_eps: float | None = None
    target_mean: float | None = None
    target_median: float | None = None
    target_high: float | None = None
    target_low: float | None = None
    num_analysts: int | None = None

    # Time series — dict keyed by fiscal year (int)
    revenue: dict[int, float] = field(default_factory=dict)
    gross_profit: dict[int, float] = field(default_factory=dict)
    operating_income: dict[int, float] = field(default_factory=dict)
    ebitda: dict[int, float] = field(default_factory=dict)
    net_income: dict[int, float] = field(default_factory=dict)
    diluted_eps: dict[int, float] = field(default_factory=dict)
    interest_expense: dict[int, float] = field(default_factory=dict)
    tax_provision: dict[int, float] = field(default_factory=dict)
    rnd: dict[int, float] = field(default_factory=dict)
    da: dict[int, float] = field(default_factory=dict)

    # Margins (as decimals, e.g. 0.57 for 57%)
    gross_margin: dict[int, float] = field(default_factory=dict)
    operating_margin: dict[int, float] = field(default_factory=dict)
    net_margin: dict[int, float] = field(default_factory=dict)
    ebitda_margin: dict[int, float] = field(default_factory=dict)
    fcf_margin: dict[int, float] = field(default_factory=dict)

    # Returns (as decimals)
    roic: dict[int, float] = field(default_factory=dict)
    roe: dict[int, float] = field(default_factory=dict)
    roa: dict[int, float] = field(default_factory=dict)

    # Cash flow
    operating_cf: dict[int, float] = field(default_factory=dict)
    capex: dict[int, float] = field(default_factory=dict)  # negative
    fcf: dict[int, float] = field(default_factory=dict)
    cf_da: dict[int, float] = field(default_factory=dict)  # D&A from cash flow section
    sbc: dict[int, float] = field(default_factory=dict)
    buybacks: dict[int, float] = field(default_factory=dict)
    fcf_conversion: dict[int, float] = field(default_factory=dict)  # as decimal
    owner_earnings: dict[int, float] = field(default_factory=dict)

    # Balance sheet
    total_assets: dict[int, float] = field(default_factory=dict)
    total_debt: dict[int, float] = field(default_factory=dict)
    long_term_debt: dict[int, float] = field(default_factory=dict)
    cash: dict[int, float] = field(default_factory=dict)
    net_debt: dict[int, float] = field(default_factory=dict)
    equity: dict[int, float] = field(default_factory=dict)
    invested_capital: dict[int, float] = field(default_factory=dict)
    current_assets: dict[int, float] = field(default_factory=dict)
    current_liabilities: dict[int, float] = field(default_factory=dict)
    working_capital: dict[int, float] = field(default_factory=dict)

    # Debt ratios (as floats, e.g. 1.7 for 1.7x)
    debt_ebitda: dict[int, float] = field(default_factory=dict)
    net_debt_ebitda: dict[int, float] = field(default_factory=dict)
    interest_coverage: dict[int, float] = field(default_factory=dict)
    current_ratio: dict[int, float] = field(default_factory=dict)
    debt_equity: dict[int, float] = field(default_factory=dict)  # as decimal

    def latest_year(self) -> int | None:
        """Return the most recent fiscal year with revenue data."""
        years = sorted(self.revenue.keys(), reverse=True)
        return years[0] if years else None

    def available_years(self) -> list[int]:
        """Return fiscal years with revenue data, most recent first."""
        return sorted(self.revenue.keys(), reverse=True)

    def get_latest(self, series: dict[int, float]) -> float | None:
        """Get the most recent value from a time series."""
        if not series:
            return None
        latest = max(series.keys())
        return series[latest]

    def avg_recent(self, series: dict[int, float], n: int = 3) -> float | None:
        """Average of the most recent n values in a series."""
        years = sorted(series.keys(), reverse=True)[:n]
        vals = [series[y] for y in years]
        return sum(vals) / len(vals) if vals else None


@dataclass
class DCFInputs:
    """All assumptions for a single DCF run. Pure data, no logic."""

    # Base financials
    base_revenue: float
    base_operating_margin: float  # decimal, e.g. 0.35
    base_tax_rate: float  # decimal, e.g. 0.14
    base_da_pct: float  # D&A as % of revenue, decimal
    base_capex_pct: float  # capex as % of revenue, decimal (positive)
    base_sbc_pct: float  # SBC as % of revenue, decimal
    base_nwc_pct: float  # NWC as % of revenue, decimal

    # Growth assumptions
    revenue_growth_rates: list[float]  # per-year, e.g. [0.08, 0.07, 0.06]
    terminal_growth_rate: float  # e.g. 0.03

    # Margin trajectory
    target_operating_margin: float | None = None  # if None, use base

    # Discount rate
    wacc: float = 0.10
    discount_method: str = "manual"  # "manual", "capm", or "fixed" (Buffett-style)

    # Terminal value
    terminal_method: str = "exit_multiple"  # or "gordon_growth"
    exit_multiple: float = 15.0  # EV/EBITDA

    # CapEx mode
    capex_mode: str = "total"  # "total" or "maintenance" (owner earnings mode)

    # Capital structure
    shares_outstanding: float = 1.0
    net_debt: float = 0.0  # positive = net debtor

    @property
    def projection_years(self) -> int:
        return len(self.revenue_growth_rates)


@dataclass
class DCFResult:
    """Output of a single DCF run."""

    # Core
    enterprise_value: float
    equity_value: float
    per_share_value: float

    # Year-by-year projections
    projected_revenue: list[float]
    projected_ebitda: list[float]
    projected_fcf: list[float]
    pv_fcfs: list[float]

    # Terminal
    terminal_value: float  # undiscounted
    pv_terminal: float  # discounted
    terminal_pct_of_value: float

    # Metadata
    inputs: DCFInputs
    implied_ev_ebitda: float

    def summary_dict(self) -> dict:
        """Return a flat dict for JSON serialization."""
        return {
            "enterprise_value": round(self.enterprise_value),
            "equity_value": round(self.equity_value),
            "per_share_value": round(self.per_share_value, 2),
            "terminal_pct_of_value": round(self.terminal_pct_of_value * 100, 1),
            "implied_ev_ebitda": round(self.implied_ev_ebitda, 1),
            "wacc": self.inputs.wacc,
            "terminal_growth": self.inputs.terminal_growth_rate,
            "projection_years": self.inputs.projection_years,
        }


@dataclass
class ScenarioResult:
    """Bear / base / bull DCF outputs."""

    bear: DCFResult
    base: DCFResult
    bull: DCFResult
    current_price: float | None = None
    currency: str = "USD"

    @property
    def mos_at_analysis(self) -> float | None:
        """MOS = (IV_conservative - price) / IV_conservative * 100."""
        if self.current_price is None or self.bear.per_share_value == 0:
            return None
        return (
            (self.bear.per_share_value - self.current_price)
            / self.bear.per_share_value
            * 100
        )


@dataclass
class SensitivityGrid:
    """2D sensitivity table."""

    row_label: str  # e.g. "Revenue Growth"
    col_label: str  # e.g. "WACC"
    row_values: list[float]
    col_values: list[float]
    grid: list[list[float]]  # grid[row][col] = per-share IV
    base_row_idx: int
    base_col_idx: int


@dataclass
class MonteCarloResult:
    """Output of Monte Carlo simulation."""

    n_simulations: int
    percentiles: dict[str, float]  # {"P10": 120.5, "P25": 145.2, ...}
    mean: float
    median: float
    std: float
    prob_above_price: float  # P(IV > current price)
    histogram_data: list[float]  # raw per-share values


@dataclass
class WACCResult:
    """Output of CAPM-based WACC calculation."""

    wacc: float
    cost_of_equity: float  # Re = Rf + beta * MRP
    cost_of_debt_pretax: float  # interest_expense / total_debt
    cost_of_debt_aftertax: float  # Rd * (1 - Tc)
    effective_tax_rate: float
    beta: float
    risk_free_rate: float
    market_risk_premium: float
    equity_value: float  # market_cap
    debt_value: float  # total_debt
    equity_weight: float  # E / (E + D)
    debt_weight: float  # D / (E + D)
    data_year: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class OwnerEarningsResult:
    """Owner earnings with maintenance/growth capex separation."""

    year: int
    net_income: float
    da: float
    total_capex: float  # absolute value
    maintenance_capex: float
    growth_capex: float
    owner_earnings_simple: float  # NI + D&A - total_capex
    owner_earnings_adjusted: float  # NI + D&A - maintenance_capex
    method: str  # "da_proxy" | "regression"
    maintenance_pct_of_total: float


@dataclass
class GrowthSchedule:
    """Year-by-year growth rates from a fade schedule."""

    rates: list[float]
    high_growth_rate: float
    terminal_rate: float
    fade_start_year: int  # 1-indexed
    method: str  # "linear_fade" | "roic_sustainable"
