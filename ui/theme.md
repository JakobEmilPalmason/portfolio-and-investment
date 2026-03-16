# Evolving a Flask Dashboard Into a Research Workspace

**The optimal path forward is Flask + htmx + Alpine.js + Tailwind CSS with Plotly.js charts and AG Grid tables — no SPA required.** This stack preserves your existing Flask backend while adding rich interactivity through progressive enhancement, achieving roughly 80% of a React SPA's UX at 20% of the complexity. The open-source landscape offers three strong architectural references: Ghostfolio for portfolio tracking patterns, OpenBB Platform for data provider abstraction, and Rotki for the Python-backend-plus-REST-API model that maps directly to Flask. What follows is a concrete component-by-component blueprint with specific repos, design tokens, and implementation patterns.

---

## The recommended tech stack and why it wins

**Flask + Jinja2 + htmx + Alpine.js + Tailwind CSS** is the right architecture for evolving your existing system without a rewrite. htmx handles server interactions (partial page updates, lazy loading, polling) via HTML attributes like `hx-get`, `hx-target`, and `hx-swap`. Alpine.js manages client-side state (tabs, modals, filters, theme toggles) through `x-data` directives. Together they eliminate the need for React/Vue while keeping your Jinja2 templates.

A production testimonial validates this approach: the auth platform Fief rewrote their entire React frontend using Jinja + htmx + Tailwind, achieving **67% code reduction** (21.5K → 7.2K LOC), **96% fewer JS dependencies** (255 → 9), and **88% faster builds** (40s → 5s). For your dashboard, the pattern looks like this: Flask renders the page shell and sidebar via Jinja2, htmx loads data table partials and chart containers via AJAX, Alpine.js handles client-side filtering and the command palette, and charting libraries load via CDN with zero build step.

Key resources for this stack:
- **Flask-HTMX extension**: `pip install flask-htmx` — GitHub: `github.com/edmondchuc/flask-htmx`
- **Talk Python htmx+Flask course** with source repo: `github.com/talkpython/htmx-python-course`
- **TestDriven.io tutorial** (Flask + htmx + Tailwind): `testdriven.io/blog/flask-htmx-tailwind/`
- **PyHAT Stack** (Python + htmx + ASGI + Tailwind) community: `github.com/PyHAT-stack/awesome-python-htmx`
- **htmx examples with Flask**: `github.com/Konfuzian/htmx-examples-with-flask/`

The alternative — FastAPI + React — only makes sense if you need offline mode, complex real-time collaboration, or have a multi-developer frontend team. Streamlit is unsuitable: it re-runs the entire app on every input change, has limited UI components, and cannot support command palettes, split panes, or the information density a research workspace requires.

---

## Three open-source projects to study and steal from

**Ghostfolio** (`github.com/ghostfolio/ghostfolio`, live demo at `ghostfol.io/en/demo`) is the closest architectural reference for portfolio tracking. Built on NestJS + Angular + PostgreSQL + Redis, its key patterns translate directly to Flask. The **PortfolioService orchestrator** coordinates OrderService, AccountService, DataProviderService, and ExchangeRateDataService — a clean separation of concerns replicable with Flask Blueprints. Its **allocation proportion charts** (donut/ring charts for sector, region, asset class breakdowns) and **X-Ray risk analysis** page (identifying concentration risks) map directly to your policy-warning needs. The Prisma database schema — Users → Accounts → Orders → SymbolProfiles — is the canonical relational model for portfolio data. Ghostfolio also has a **Storybook component library** at `ghostfol.io/development/storybook` worth browsing for UI patterns.

**OpenBB Platform** (`github.com/OpenBB-finance/OpenBB`, ~63K stars) provides the strongest data-layer architecture. Its **TET pipeline** (Transform-Extract-Transform) standardizes every data request: validate parameters → fetch from provider → normalize output. The **provider plugin pattern** means each data source (Yahoo Finance, SEC, FRED) is a self-contained module with a common interface — directly replicable with Flask Blueprints where your JSON files are one "provider" and external APIs are another. OpenBB's **standardized response object** (OBBject: `{results, provider, warnings, chart, extra}`) is an excellent pattern for consistent API design. You can even use OpenBB as your data layer directly: `pip install openbb` then call `obb.equity.price.historical("AAPL")` from Flask routes. The **OpenBB Workspace** (`pro.openbb.co`) demonstrates widget-based dashboards with parameter linking across widgets — when a user changes a ticker, all linked widgets update.

**Rotki** (`github.com/rotki/rotki`) validates the Python-backend-plus-REST-API pattern. Its Python backend runs locally, stores everything in encrypted SQLite, and exposes a REST API consumed by a Vue.js frontend — architecturally identical to what you'd build with Flask. Key borrowable patterns include multi-source data aggregation (normalizing data from different exchanges/sources into a unified portfolio view) and customizable PnL reporting with configurable accounting methods.

---

## Charting, tables, and visualization: the specific libraries

**For charts: Plotly.js via CDN** is the clear winner for a Flask + htmx stack. Load it with a single `<script src="https://cdn.plot.ly/plotly-3.4.0.min.js">` tag — no build step, no React dependency. It natively supports **treemaps** (zoomable with pathbar navigation, perfect for sector allocation), **sunburst charts** (hierarchical portfolio → sector → position), **candlestick/OHLC** charts, **waterfall** charts (P&L attribution), and has a built-in `plotly_dark` template for dark themes. Generate figures in Python for analysis, serialize to JSON, render identically in the browser with `Plotly.newPlot()`. Docs: `plotly.com/javascript/treemaps/`, `plotly.com/javascript/sunburst-charts/`, `plotly.com/javascript/financial-charts/`.

**For price charts: TradingView's Lightweight Charts** (`github.com/tradingview/lightweight-charts`, 13.9K stars, Apache 2.0) is **35kB**, actively maintained, and supports candlestick, line, area, baseline, and histogram series. It renders position entry/exit markers natively via `createSeriesMarkers()` with `arrowUp`/`arrowDown` shapes, color coding, and text labels. For quick market data without maintaining your own data feed, TradingView's **free embeddable widgets** require zero API keys — just paste HTML. The Advanced Chart, Mini Chart, Ticker Tape, Stock Heatmap, and Technical Analysis widgets all support `"theme": "dark"` and `isTransparent: true` for seamless integration. Full widget docs: `tradingview.com/widget-docs/`. Avoid react-financial-charts (`github.com/react-financial/react-financial-charts`) — it's **semi-dormant** with no updates since March 2024.

**For data tables: AG Grid Community** (free, MIT license) handles stock ratings tables, transaction histories, and portfolio positions with zero configuration overhead. The free tier includes sorting, column filtering, **column pinning** (critical for financial tables), row/column virtualization (100K+ rows), custom cell renderers, 4 built-in themes with dark mode, and CSV export. Load via CDN into htmx-swapped containers. AG Grid maintains a financial demo at `ag-grid.com/example-finance/` with live-updating sparklines. If you later adopt React, shadcn/ui's Data Table (wrapping **TanStack Table**) gives full styling control, but AG Grid requires less code for the same result.

**For portfolio-specific visualizations:** use Plotly treemaps with hierarchy `path=['sector', 'industry', 'ticker']`, values mapped to `market_value`, and color mapped to `pct_return` on an `RdYlGn` scale (red=loss, green=gain). For **long/short visualization**, diverging horizontal bar charts work best — longs extend right, shorts extend left from a center axis. **Gross/net exposure** displays well as stacked bars. PyPortfolioOpt's `pypfopt.plotting` module provides efficient frontier scatter plots and weight bar charts that can be adapted to Plotly for web display.

---

## A warm dark theme that feels like Claude, not a terminal

Claude.ai's design achieves warmth through three deliberate choices: **warm cream backgrounds** (`#F4F3EE` light, `#1C1917` dark) instead of pure white/black, **brown-tinted text** (`#3d3929`) instead of pure black, and a **terracotta accent** (`#C15F3C`) instead of cold blue. The dark mode uses Tailwind's `stone` scale — a gray palette with yellow-brown undertones:

- `stone-950` (`#0C0A09`): deepest background
- `stone-900` (`#1C1917`): primary dark background
- `stone-800` (`#292524`): card/panel surfaces
- `stone-700` (`#44403C`): elevated elements, borders
- `stone-400` (`#A8A29E`): secondary text
- `stone-50` (`#FAFAF9`): primary text (warm off-white)
- Accent: `#C15F3C` (terracotta)

A ready-made **shadcn/ui Claude theme** is installable: `npx shadcn@latest add https://www.shadcn.io/r/claude.json`. It uses OKLCH color values (`oklch(0.70 0.14 45)` for terracotta, `oklch(0.97 0.02 70)` for cream) and works with shadcn's CSS variable system. The interactive theme editor at `tweakcn.com` lets you customize these values visually. The critical difference between warm and cold dark themes is the RGB balance: warm themes have **R > B** (e.g., `#1C1917`), while cold themes like Twitter's have **B > R** (e.g., `#15202B`).

Design references worth studying: **Linear** (`linear.app`) uses LCH color space to generate themes from just three variables (base color, accent color, contrast) and achieves information density through an "inverted L-shape" navigation pattern. **Notion** demonstrates database table views with property badges and multi-layout switching. **Raycast** is the gold standard for command palette design — dark-first, keyboard-first, maximum information density with minimal chrome. Bloomberg's lesson, per CTO Shawn Edwards: **"Simplify the interface, not the data"** — high information density with minimal UI chrome. For typography, use a **monospace font for numbers** (JetBrains Mono or IBM Plex Mono for tabular data) and **Inter or Source Sans 3** for UI labels.

---

## Architecture patterns: search, background tasks, and multi-portfolio

**Full-text search across your JSON and markdown files** is best served by **SQLite FTS5** — zero dependencies (bundled with Python's `sqlite3`), single-file database, BM25 ranking, prefix queries, phrase matching, and snippet extraction. Create a virtual table with `CREATE VIRTUAL TABLE documents USING fts5(title, content, file_path, file_type, tokenize='porter unicode61')`, index your JSON reports and markdown files, and query with `SELECT snippet(documents, 1, '<b>', '</b>', '...', 32) FROM documents WHERE documents MATCH ?`. Use the `watchdog` library to auto-reindex when files change. If you outgrow SQLite's search, **tantivy-py** (`github.com/quickwit-oss/tantivy-py`) is a Rust-based alternative that's ~15-20x faster than Whoosh for indexing, with Python bindings via `pip install tantivy`. Avoid MeiliSearch/Typesense for this use case — they require running separate services.

**Triggering long-running analysis from the web UI** is cleanest with **Redis Queue (RQ)** + htmx polling. RQ is dramatically simpler than Celery and sufficient for a personal dashboard. The pattern: a Flask endpoint enqueues an analysis task via `q.enqueue(run_analysis, ticker, job_timeout=3600)`, the task runs your existing Python scripts via `subprocess.Popen`, streams output lines into `job.meta` for progress tracking, and the frontend polls `/api/task-status/<job_id>` every 2 seconds via `hx-trigger="every 2s"`. For real-time streaming without polling, Flask's Server-Sent Events work without any dependencies: `Response(stream_with_context(generate()), mimetype='text/event-stream')` paired with htmx's SSE extension `hx-ext="sse"`. Key references: Miguel Grinberg's Flask+RQ tutorial (`blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxii-background-jobs`), RQ Dashboard for monitoring (`pip install rq-dashboard`).

**Multi-portfolio switching** maps well to your existing file structure. Create a `config.json` registry listing portfolios with `{id, name, path, currency}`, organize files as `portfolios/{portfolio_id}/ledger.json`, and use Flask's `session['active_portfolio']` for state. The htmx switcher pattern: sidebar links with `hx-get="/dashboard/{portfolio_id}" hx-target="#main-content" hx-push-url="/portfolio/{portfolio_id}"` swap the entire content area while preserving the navigation shell. Ghostfolio handles this through a Users → Accounts → Orders relational model where filtering by account achieves virtual portfolio switching.

---

## Specific UI components: command palette, split panes, and alerts

**Command palette (⌘K)**: For a non-React Flask app, **ninja-keys** (`github.com/ssleptsov/ninja-keys`) is a Web Component that works with vanilla JS — no build step. It supports nested menus, breadcrumbs, hotkeys, and CSS Parts for styling. For a React path, **cmdk** (`github.com/pacocoursey/cmdk`, used by Linear and Raycast) is the standard — shadcn/ui's Command component wraps cmdk directly. Structure commands as: "Search Tickers" (fuzzy search with sector/name keywords), "Actions" (Run Analysis, Generate Report, Execute Trade), "Navigate" (Portfolio Dashboard, Research Table), and "Recent" (last 5 viewed tickers). Use `shouldFilter={false}` with async API calls for live ticker search with debouncing.

**Split-pane layouts**: **react-resizable-panels** (`github.com/bvaughn/react-resizable-panels`) supports horizontal/vertical orientation, collapsible panels with min/max constraints, and layout persistence via `onLayout` callback to localStorage. For the non-React path, CSS Grid with `resize: horizontal` on columns achieves a simpler version. The recommended research layout: a collapsible sidebar (200px), a sortable ticker list (300px), and a flexible detail pane — the "three-pane Bloomberg" pattern. For htmx, each pane loads its content independently via `hx-get` with `hx-trigger="load"`.

**Policy warning badges**: Display compliance alerts using a three-tier system. Dashboard-level: a persistent banner at the top ("AAPL at 6.8% — approaching 7% single-name limit") with a color-coded left border. Table-level: inline red badges on rows breaching limits. Metric-level: progress bars showing 6.8/7.0% that change color at warning thresholds. For toast notifications on real-time breaches, **Sonner** (`sonner.emilkowal.dev`) is the modern standard. **Freshness indicators** should use a traffic-light pattern: green dot + "Updated 2m ago" for fresh data, amber for aging (>1 hour), red for stale (>1 day), with `aria-label` for accessibility. Compute freshness server-side and render as Jinja2 template partials.

**AI research interface**: For a "ask about this stock" feature, the minimal viable pattern is a textarea that POSTs to a Flask endpoint, triggers a Claude API call via your existing prompt infrastructure, and streams the response back via SSE into an htmx-connected div. Display inline numbered citations linking to your report files, with expandable source sections below the response. The open-source **Perplexica** (`github.com/ItzCrazyKns/Perplexica`) demonstrates this pattern with web search + AI answers + citations. For a React future path, the **Vercel AI SDK** (`ai-sdk.dev`) plus **shadcn/ui AI Components** (`shadcn.io/ai`) provide 25+ purpose-built components including streaming message display, inline citations, collapsible reasoning blocks, and source attribution.

---

## Conclusion: a phased implementation path

The research points to a clear two-phase strategy. **Phase 1** (days, not weeks): keep Flask, add htmx + Alpine.js + Tailwind with the `stone` palette, load Plotly.js and AG Grid via CDN, implement SQLite FTS5 search, and add RQ for background analysis tasks. This gets you a warm-dark-themed research workspace with interactive tables, sector treemaps, command palette search, and "run analysis from UI" — all without a build pipeline. **Phase 2** (only if needed): migrate to FastAPI + React with shadcn/ui, TanStack Table, Nivo for advanced visualizations, and the Vercel AI SDK for a chat-based research interface. The critical architectural investment that pays off in both phases is the **data provider abstraction layer** borrowed from OpenBB — normalize your JSON files, markdown reports, and computed results behind a common interface so the frontend never cares where data comes from. The three repos most worth forking or deeply studying are Ghostfolio (for portfolio calculation patterns), OpenBB (for the data layer), and the Flask paper-trader at `github.com/MitulMistry/paper-trader` (for the Flask-specific implementation reference).