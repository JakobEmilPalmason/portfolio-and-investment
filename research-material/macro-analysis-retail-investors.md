# Macro Analysis for Retail Investors

---

## The Macro Indicators Retail Investors Track

Roughly five tiers:

### Valuation (long-term signal)

- **Shiller CAPE** — R² of ~0.43-0.50 for predicting 10-year returns. Currently ~37 (median is 16). Zero short-term timing ability.
- **Buffett Indicator** (market cap / GDP) — currently ~222-230%, well above the "reasonable" 90-135% range. Critics say it ignores overseas revenue and asset-light business composition.

### Recession / Cycle (medium-term)

- **Yield curve** (10Y-2Y or 3M-10Y spread) — preceded all 10 US recessions since 1955. Lag: 12-24 months. The 2022-2023 inversion broke the pattern though.
- **Sahm Rule** — unemployment 3mo MA rises 0.5pp above 12mo low. Triggered every recession since 1950. Confirms recessions more than predicts them.
- **Conference Board LEI** — composite of 10 indicators. The "3Ds Rule" (diffusion ≤50 + annualized growth < -4.3%) has ~7 month lead time.
- **ISM Manufacturing PMI** — below 50 = contraction. Currently 52.4.
- **Credit spreads** (HY-IG) — sometimes widen before equities crack.

### Sentiment (contrarian signals)

- **CNN Fear & Greed Index** — composite of 7 sub-indicators. Currently at 16 (Extreme Fear).
- **VIX** — >30 signals fear; used as contrarian buy signal.
- **Put/Call ratio** — extremes in either direction often precede reversals.
- **AAII Sentiment Survey** — extreme bearish readings have been good buy signals historically.
- **Margin debt** — peaks have coincided with market tops.

### Macro fundamentals

- GDP, CPI/PCE, Fed Funds rate, unemployment, consumer confidence, retail sales, industrial production.

### Liquidity

- **M2 money supply** — growing M2 pushes up asset demand; shrinking M2 deflates.
- **Global broad money supply** (Lyn Alden's preferred) — denominated in USD across major blocs.

### Breadth

- **Advance/Decline line** — divergence from index = narrowing participation.
- **% above 200-day MA** — below 50% = bearish bias; above 70% = potential overheating.

---

## Popular Frameworks for Combining Indicators

| Framework | Approach |
|-----------|----------|
| **"Valuation + Regime"** (most common retail) | CAPE/Buffett for "how expensive?" + yield curve/PMI/credit spreads for "recession coming?" |
| **42 Macro GRID** (Darius Dale) | Growth × Inflation matrix → 4 regimes (Goldilocks, Reflation, Stagflation, Deflation) |
| **Lyn Alden's liquidity framework** | Global broad money supply drives asset prices; fiscal dominance theme |
| **AQR "Sin a Little"** | Value + momentum/trend combined. Modest tactical tilts, not all-in/all-out |
| **Faber 10-month SMA** | Long when above 10-month SMA, cash otherwise. Simple mechanical system |
| **CFA 3-pillar** | Growth (PMI, orders) + Inflation (breakevens, input costs) + Financial conditions (real yields, credit spreads, vol) |
| **JP Morgan 5-factor** | Consumer, labor, manufacturing, corporate profits, credit conditions |
| **NBER "Big Four"** | Nonfarm employment, industrial production, real retail sales, real personal income |

---

## Best GitHub Repos

### Comprehensive platforms:

| Repo | Stars | What |
|------|-------|------|
| **OpenBB-finance/OpenBB** | 63.5K | The open-source Bloomberg — full macro data via Python API (FRED, yield curves, GDP, CPI, everything) |
| **cuemacro/finmarketpy** | 3.7K | Macro-oriented backtest library with FRED integration |
| **mortada/fredapi** | 1.1K | Standard Python wrapper for FRED's 800K+ time series |

### Macro scorecards / regime detection:

| Repo | Stars | What |
|------|-------|------|
| **AmpyFin/Euler** | 5 | Closest to a macro scorecard — 6 indicators (Buffett, P/C ratio, VIX, yield curve, credit spreads, breadth) combined into composite regime signal |
| **LenkaV/CIF** | 64 | OECD composite leading indicator framework — academic grade |
| **pjrowe/Economic-Regime-analysis-and-Factor-Models** | 7 | ML regime detection using yield curve, unemployment, NFCI |
| **LSEG-API-Samples/MarketRegimeDetection** | 60 | Hidden Markov Model regime detection (bull/bear/sideways) |

### Sentiment / Fear & Greed:

| Repo | Stars | What |
|------|-------|------|
| **hackingthemarkets/sentiment-fear-and-greed** | 132 | Backtests CNN Fear & Greed + Put/Call as trading signals |
| **DidierRLopes/fear-greed-index** | 104 | Clean F&G wrapper with all 7 sub-components (by the OpenBB founder) |
| **jamesdellinger/market_breadth** | 30 | S&P 500 breadth by sector |

### Recession prediction:

| Repo | Stars | What |
|------|-------|------|
| **JamesQuintero/Recession-Indicator** | 22 | Neural net on OECD CLI data |
| **itsergiu/Predict-SP500-correction** | 1 | ML using Shiller PE + Buffett Indicator (R² ~0.8) |

### Dashboards:

| Repo | Stars | What |
|------|-------|------|
| **moshesham/Economic-Dashboard** | 2 | Streamlit dashboard with 60+ FRED indicators — good reference for building your own |

### Meta-resources:

| Repo | Stars | What |
|------|-------|------|
| **wilsonfreitas/awesome-quant** | 25K | Master index of quant finance tools |
| **paperswithbacktest/awesome-systematic-trading** | 7.5K | 97+ libraries, 40+ strategies with code |

---

## Free Web Tools Everyone Uses

| Tool | What |
|------|------|
| **currentmarketvaluation.com** | The Reddit favorite — live Buffett Indicator, CAPE, yield curve, mean reversion, aggregate valuation index |
| **FRED** (fred.stlouisfed.org) | 825K time series, the foundation for everything |
| **longtermtrends.com** | Macro Compass, weekly AI macro report, credit spreads |
| **macromicro.me** | 40M indicators, global recession probability |
| **feargreedmeter.com** | Real-time CNN Fear & Greed tracking |
| **gurufocus.com** | CAPE, Buffett Indicator, insider trends |
| **openinsider.com** | SEC Form 4 insider buy/sell charts |
| **TradingView** | FRED data integration (FRED: prefix), community indicators |
| **finviz.com** | Screener, heatmaps, sector performance |

---

## Reddit Communities

| Subreddit | Stance |
|-----------|--------|
| **r/ValueInvesting** | Pro macro overlay — CAPE, Buffett Indicator for "is it expensive?" |
| **r/investing** | Mixed — macro discussion spikes during volatility |
| **r/Bogleheads** | Strongly anti-timing — "time in the market beats timing the market" |
| **r/SecurityAnalysis** | Deeper, institutional-quality macro framework discussion |

### The Great Debate

The emerging synthesis across these communities:

1. **Don't try to time short-term moves** — evidence overwhelmingly against it (Dimensional tested 720 strategies, 690 failed)
2. **Do use valuation as a risk management overlay** — when CAPE is extreme, demand a larger margin of safety on individual picks, hold more cash
3. **Cash is a valid position** — holding 10-30% cash when everything looks overvalued is risk management, not "timing"
4. **Combine indicators** — AQR research shows value + momentum together outperforms either alone
5. **The biggest risk isn't being wrong occasionally** — it's being out of the market during the best days, which cluster around the worst days

---

## Newsletters / Content Worth Following

- **Lyn Alden** — liquidity-centric macro, fiscal dominance (free + premium)
- **42 Macro** (Darius Dale) — GRID regime framework (paid)
- **Real Vision** (Raoul Pal) — institutional macro for individuals
- **George Gammon** (YouTube) — whiteboard macro breakdowns (470K subs)
- **Patrick Boyle** (YouTube) — quant/macro commentary
- **Advisor Perspectives / dshort** — Big Four recession indicators, CAPE updates

---

## Key FRED Series If You Build Your Own Dashboard

| Series | Indicator |
|--------|-----------|
| T10Y2Y | Yield curve (10Y-2Y) |
| SAHMREALTIME | Sahm Rule |
| ICSA | Initial unemployment claims |
| BAMLH0A0HYM2 | HY credit spread |
| M2SL | M2 money supply |
| UMCSENT | Consumer sentiment |
| STLFSI4 | Financial stress index |
| FEDFUNDS | Fed funds rate |
