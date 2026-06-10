# Quantitative Valuation Models

## Golden Rule: GitHub-First Development

**Before writing any module from scratch, search GitHub for popular, battle-tested implementations.**

1. **Search** — Find repos with >500 stars that solve the same problem (DCF engines, Monte Carlo valuation, sensitivity analysis, owner earnings, portfolio optimization).
2. **Evaluate** — Check license (MIT/Apache/BSD preferred), code quality, test coverage, and whether the API fits our data flow.
3. **Integrate** — Fork or vendor the relevant code. Adapt it to consume our `data/context/{TICKER}/financials.md` data and output to our `FINAL-REPORT.json` schema.
4. **Only build from scratch** if no credible open-source solution exists or if integration cost exceeds writing it.

This rule applies to every module below. The goal is auditable, deterministic valuations — not NIH syndrome.

---

## Data We Already Have

Every ticker with a `data/context/{TICKER}/financials.md` file has 4-5 years of:

| Category | Fields |
|----------|--------|
| Income | Revenue, gross profit, operating income, EBITDA, net income, D&A, R&D, SBC |
| Margins | Gross, operating, net, EBITDA, FCF (all 5 years) |
| Cash flow | Operating CF, capex, FCF, dividends, buybacks |
| Balance sheet | Total assets, equity, net debt, debt/EBITDA, interest coverage, current ratio |
| Returns | ROIC, ROE, ROA (derived) |
| Valuation | P/E, EV/EBITDA, P/FCF, P/S, P/B, market cap |
| Forward | Analyst consensus EPS, revenue estimates, target price |
| Price | Current price, 52-week range, beta |

This is real data from yfinance. The quant layer's job is to turn these numbers into reproducible IV estimates.

---

## Module 1: `dcf.py` — DCF Engine

**What it does:** Multi-stage discounted cash flow. Takes historical financials + assumptions, returns per-share intrinsic value.

**Real numbers example (AAPL FY2025):**
- Owner earnings: ~$111B
- Revenue CAGR (3yr): ~7%
- WACC estimate: 8-10%
- Terminal growth: 2-3%
- Shares outstanding: ~15.1B

**Inputs:**
```python
dcf(
    base_cash_flow=111e9,       # most recent owner earnings or FCF
    growth_rates=[0.07, 0.06, 0.05, 0.04, 0.03],  # year-by-year or phases
    discount_rate=0.09,          # WACC
    terminal_growth=0.025,       # perpetuity growth
    shares_outstanding=15.1e9,
    net_debt=50e9,               # enterprise → equity bridge
)
```

**Outputs:** `{ iv_per_share: float, pv_fcfs: float, terminal_value: float, ev: float }`

**Scenarios:** Run 3x with bear/base/bull assumptions → `iv_conservative`, `iv_base`, `iv_bull`.

**GitHub search terms:** `dcf valuation python`, `intrinsic value calculator`, `discounted cash flow model python`

---

## Module 2: `sensitivity.py` — Sensitivity Tables

**What it does:** 2D grids showing IV across assumption ranges. Answers: "how wrong can I be and still not lose money?"

**Real numbers example (AAPL):**
- Growth rate axis: 3%, 5%, 7%, 9%, 11%
- Discount rate axis: 7%, 8%, 9%, 10%, 11%
- Each cell = IV per share from `dcf.py`

**Output:** Matrix + heatmap data. Highlight cells where IV > current price (margin of safety exists).

```
         WACC 7%   8%    9%    10%   11%
Growth 3%  $148   $131  $117  $106  $96
       5%  $178   $156  $138  $124  $112
       7%  $215   $187  $164  $145  $130
       9%  $262   $225  $196  $172  $153
      11%  $322   $274  $236  $206  $181
```

Current price $248 → only the top-left corner offers MOS. That's the signal.

**GitHub search terms:** `sensitivity analysis python finance`, `valuation sensitivity grid`

---

## Module 3: `montecarlo.py` — Monte Carlo Simulation

**What it does:** Run 10,000+ DCF simulations with randomized assumptions drawn from distributions. Output a probability distribution of IV.

**Assumption distributions (AAPL example):**
- Revenue growth: Normal(μ=7%, σ=3%)
- Operating margin: Normal(μ=33%, σ=2%)
- WACC: Uniform(8%, 11%)
- Terminal multiple: Normal(μ=25x, σ=5x)

**Outputs:**
```
P10:  $118   (10% chance IV is below this)
P25:  $152
P50:  $191   (median)
P75:  $238
P90:  $295
Mean: $198
```

Current price $248 → sits at roughly P80. ~20% probability of being undervalued.

**GitHub search terms:** `monte carlo dcf python`, `monte carlo valuation simulation`, `probabilistic valuation`

---

## Module 4: `owner_earnings.py` — Owner Earnings Calculator

**What it does:** Separates maintenance capex from growth capex. Buffett's "owner earnings" = net income + D&A − maintenance capex.

**Real numbers (AAPL FY2025):**
- Net income: ~$97B
- D&A: ~$11B
- Total capex: ~$10B
- Estimated maintenance capex: ~$6B (D&A-based heuristic or regression)
- **Owner earnings: $97B + $11B − $6B = $102B**
- Growth capex: ~$4B (new stores, data centers, etc.)

**Methods to estimate maintenance capex:**
1. **D&A proxy:** maintenance ≈ D&A (simplest, often good enough)
2. **Revenue regression:** capex vs revenue growth — intercept ≈ maintenance
3. **PP&E maintenance:** capex needed to keep PP&E/revenue ratio stable
4. **Management disclosure:** some companies break it out in 10-K

**GitHub search terms:** `owner earnings python`, `maintenance capex estimation`, `buffett owner earnings calculator`

---

## Module 5: `backtest.py` — Historical Accuracy Tracker

**What it does:** Stores IV estimates over time, compares to actual price outcomes, measures systematic bias.

**Schema (new table in portfolio.db):**
```sql
CREATE TABLE valuation_history (
    ticker TEXT,
    analysis_date TEXT,
    iv_conservative REAL,
    iv_base REAL,
    iv_bull REAL,
    price_at_analysis REAL,
    price_3mo REAL,      -- filled in later
    price_6mo REAL,
    price_12mo REAL,
    method TEXT,          -- 'ai_estimate' | 'dcf_quant' | 'mc_median'
    assumptions_json TEXT -- full parameter snapshot
);
```

**Metrics:**
- Hit rate: % of times actual price landed within bear-bull range
- Bias: average (IV_base − actual_price) / actual_price → positive = too bullish
- Calibration: does P50 from MC actually land near the median outcome?

**GitHub search terms:** `backtesting valuation python`, `investment thesis tracker`, `valuation accuracy`

---

## Module 6: `portfolio.py` — Portfolio Construction (Deferred)

**What it does:** Given N stocks with IV estimates and return distributions, compute optimal weights.

**Methods (in order of implementation priority):**
1. **Equal weight** — already in portfolio-sim.py, baseline
2. **Conviction weight** — scale by MOS size (bigger discount = bigger position)
3. **Risk parity** — equalize risk contribution per position
4. **Mean-variance (Markowitz)** — efficient frontier with constraints
5. **Black-Litterman** — blend market-implied returns with our IV-based views

**GitHub search terms:** `portfolio optimization python`, `black litterman python`, `risk parity portfolio`, `PyPortfolioOpt`

**Known good repos to evaluate first:**
- `PyPortfolioOpt` — widely used, well-tested, supports all methods above
- `Riskfolio-Lib` — more advanced, includes risk parity and Black-Litterman
- `empyrical` / `quantstats` — return/risk metrics (already partially used in dashboard)

---

## Integration Plan

### Phase 1: Parse financials into structured data — DONE
Parser reads `data/context/{TICKER}/financials.md` and returns a `FinancialData` dataclass. This is the glue between fetch-financials.py output and the quant layer.

```python
from src.quant.parser import parse_financials
data = parse_financials("AAPL")
```

### Phase 2: DCF + sensitivity + owner earnings — DONE
Core valuation. `run.sh analyze TICKER` auto-runs the quant layer before spawning analysis agents. Output writes to `data/context/{TICKER}/quant-valuation.md` + `.json`.

### Phase 3: Monte Carlo — DONE
10,000-simulation probabilistic overlay. Produces P(IV > Price) and percentile distribution.

### Phase 4: Pipeline integration — DONE
- `run.sh analyze` runs quant automatically (after fetch, before agents)
- CLI flags: `--write`, `--json-out`, `--quiet`, `--sensitivity`, `--monte-carlo`, `--auto-wacc`, `--owner-earnings`, `--fade-growth`
- Umbrella 06 uses quant IV as starting anchor (not gospel)
- Umbrella 07 references sensitivity grid + MC probability for MOS assessment
- Umbrella 08 uses MC probability for position sizing
- Assembler prefers quant-model IV over AI-extracted IV; sets `iv_source: "quant_model"` in FINAL-REPORT.json
- New FINAL-REPORT.json fields: `iv_source`, `monte_carlo_prob_above_price`, `sensitivity_iv_range`

### Phase 5: Backtest — NOT YET IMPLEMENTED
Start recording IV estimates with method tags. After 3-6 months, enough data to measure accuracy.

### Phase 6: Portfolio optimization — NOT YET IMPLEMENTED
Replace equal-weight sim with conviction-weighted or risk-parity allocation.

---

## Output Contract

Every quant module must output results compatible with `FINAL-REPORT.json`:

```json
{
  "iv_conservative": 124.0,
  "iv_base": 191.0,
  "iv_bull": 276.0,
  "iv_currency": "USD",
  "mos_at_analysis": -23.0,
  "valuation_method": "dcf_quant",
  "assumptions": {
    "growth_rates": [0.07, 0.06, 0.05],
    "discount_rate": 0.09,
    "terminal_growth": 0.025
  }
}
```

This ensures prebuy-check.py, portfolio-sim.py, and the dashboard all work without changes.
