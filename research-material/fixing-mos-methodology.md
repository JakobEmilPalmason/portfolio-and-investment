# Fixing MOS Methodology
## Current State
- MOS, or **margin of safety**, is a metric that should tell us whether we are buying a good business below a conservative estimate of intrinsic value with enough room for error.
- **Currently**, about 93% of our final reports with usable live MOS show negative MOS; examples include AAPL at -100%, MSFT at -44.7%, V at -31.9%, and MA at -43.2%.
- **This is bad** because the metric no longer helps us separate "slightly expensive," "roughly fair," and "truly overvalued" businesses, and instead paints almost the whole universe red.
- This is **even worse, because our allocator malfunctions**, it reads that wall of negative MOS as a reason to avoid investing, so capital gets parked in cash even when the qualitative analysis says the business is exceptional.

## TL;DR

| Topic | Current State | Planned Change |
|---|---|---|
| Core problem | The research pipeline does Buffett-style qualitative work, but downstream consumers still behave like a Graham-style mechanical price gate. `iv_conservative` is treated too much like a bear-case veto, so most high-quality names show deeply negative MOS and capital stays in cash. | Separate the execution anchor from the bear stress test, then use a composite MOS policy built from base value, Monte Carlo probability, qualitative MOS score, and downside to bear. |
| Main architectural fix | Bear/base/bull scenarios are useful, but the bear case is too harsh to serve as the default buy/no-buy anchor. | Keep the bear case for stress testing and sizing, and make a more realistic execution IV the number used for MOS, pre-buy, and allocation. |
| Data flow fix | Different layers can currently drift: quant output, final reports, allocation input, pre-buy, trade proposal logic, and dashboard labels do not all share the same semantics. | Make the quant layer the single source of truth for `iv_conservative`, export `iv_bear` explicitly, and propagate the same semantics everywhere. |
| Allocation / pre-buy fix | The allocator overweights raw MOS vs conservative IV, pre-buy C2 is too strict, and add-to-position logic still uses a very harsh MOS threshold. | Use composite MOS signals and OR-based eligibility rules so great businesses at fair prices can pass without forcing clearly expensive names. |
| Recommended default | Friend proposal: `iv_conservative = iv_base * 0.85`. Existing repo philosophy: `iv_conservative = 25% bear + 75% base`. | Default to the weighted-conservative formula and document `base * 0.85` as the alternative. Keep the swap isolated to the central quant formula. |

## Problem Summary

The current system has a real architectural contradiction:

- Upstream: Buffett-style qualitative analysis across 8 umbrellas, including business quality, moat durability, management quality, economics, balance sheet, valuation, margin of safety, and temperament.
- Downstream: a much harsher price discipline layer that effectively treats the bear case as the gatekeeper for allocation, pre-buy, and add-to-position behavior.

This creates a recurring pattern:

- Great businesses score well qualitatively.
- The bear case stacks several bad outcomes at once.
- `iv_conservative` becomes too low relative to current price.
- Live MOS becomes deeply negative across much of the universe.
- The allocator and pre-buy flow become overly cash-biased.

The core insight is that the bear case should survive as a stress test, but it should not dominate the execution decision.

## Design Goals

- Preserve the existing 8-umbrella research pipeline.
- Preserve the existing quant DCF model, bear/base/bull scenarios, and Monte Carlo engine.
- Stop using the stacked bear case as the default buy anchor.
- Make quant the single source of truth for conservative IV semantics.
- Let great businesses at fair or near-fair prices become eligible without opening the floodgates.
- Keep price discipline explicit and auditable.
- Make every downstream consumer use the same definitions.

## Core Methodology

### 1. Separate execution IV from bear IV

The system should explicitly carry four valuation anchors:

- `iv_bear`: stress-test downside anchor
- `iv_conservative`: execution anchor used for MOS, pre-buy, and allocation
- `iv_base`: fair-value / expected-case anchor
- `iv_bull`: upside anchor

### 2. Use a composite MOS framework

MOS should no longer mean only "price vs bear-like conservative IV." It should combine:

- Price vs `iv_base`
- `monte_carlo_prob_above_price`
- Umbrella 07 MOS score
- Upside/downside ratio using `iv_base` upside and `iv_bear` downside
- Distance to `iv_bear` as a sizing input, not as the only buy gate

### 3. Keep price discipline, but make it smarter

The system should still reject low-probability, low-quality, expensive setups. The change is that price discipline becomes multi-path and conviction-aware instead of single-path and bear-case-only.

## Execution IV Formula

### Recommended default

Use the existing quant-layer philosophy:

```text
iv_conservative = 0.25 * iv_bear + 0.75 * iv_base
```

Why this is the default:

- It already exists conceptually in the quant layer.
- It treats the bear case as a real input without letting it dominate.
- It is less arbitrary than a flat 15% haircut.
- It stays closer to the actual spirit of "conservative, but realistic."

### Documented alternative

If the team explicitly prefers the simpler rule, the alternative is:

```text
iv_conservative = iv_base * 0.85
```

Important implementation rule:

- The formula must live in one place only: the quant layer.
- Downstream consumers should treat `iv_conservative` as an opaque execution anchor.
- Swapping formulas should not require changes to allocator, pre-buy, dashboards, or report assembly semantics.

## Implementation Workstreams

### A. Quant layer becomes the source of truth

Files:

- `src/quant/models.py`
- `src/quant/formatters.py`

Changes:

- Ensure `ScenarioResult` owns the canonical `iv_conservative` formula.
- Export `iv_bear` alongside `iv_conservative`, `iv_base`, and `iv_bull`.
- Recompute `mos_at_analysis` against the new `iv_conservative`.
- Ensure quant markdown and quant JSON use the same semantics.
- Do not let prompts or report assembly redefine valuation meanings.

Important note:

- Existing generated `context/*/quant-valuation.json` artifacts may be stale relative to current code or intended semantics.
- Regeneration must happen before downstream verification.

### B. Final report schema and report prompts

Files:

- `prompts/assembler.md`
- `prompts/07-margin-of-safety.md`

Changes:

- Update the assembler instructions so `iv_conservative` and `iv_bear` are copied directly from quant output.
- Add `iv_bear` to `FINAL-REPORT.json`.
- Update umbrella 07 so bear is explicitly described as a stress test, not the default MOS anchor.
- Update wording so margin-of-safety analysis uses:
  - primary anchors: `iv_conservative` and `iv_base`
  - stress anchor: `iv_bear`
  - supporting evidence: sensitivity grid and Monte Carlo probability

### C. Allocator logic

Files:

- `prompts/allocator.md`
- `scripts/allocation-input.py`

Changes:

- Add `iv_bear` and `monte_carlo_prob_above_price` to allocation candidate blobs.
- Keep `live_mos_pct`, but compute it from the new `iv_conservative`.
- Use composite MOS signals in ranking:
  - Primary: price vs `iv_base`
  - Primary: Monte Carlo probability
  - Supporting: umbrella 07 MOS score
  - Supporting: upside/downside ratio
  - Sizing-only: distance to `iv_bear`

Allocator eligibility policy:

- Required: verdict is `Own` or `Watch`
- Buy-eligible if any of:
  - `price <= iv_base`
  - `monte_carlo_prob_above_price >= 0.65`
  - `margin_of_safety score >= 7` and asymmetry is not broken
- Skip if all of:
  - `monte_carlo_prob_above_price < 0.50`
  - negative MOS against `iv_conservative`
  - `margin_of_safety score < 6`

Allocator sizing policy:

- Full size: positive MOS against `iv_conservative` and `MC >= 0.70`
- Starter size: negative MOS against `iv_conservative`, but `MC >= 0.60` and MOS score `>= 7`
- Cap at starter size when price sits materially above `iv_bear`
- If nothing clears the bar, hold cash

### D. Pre-buy and trade-proposal gating

Files:

- `scripts/prebuy-check.py`
- `src/trade_proposer.py`
- `src/portfolio_engine.py`

Changes:

- Keep C2 as a real pass/fail gate for `GO`; do not reduce it to warning-only behavior.
- Replace the current single strict threshold with OR-based eligibility.

New C2 should pass if any of:

- `price <= iv_conservative`
- `monte_carlo_prob_above_price >= 0.70`
- `price <= iv_base` and umbrella MOS score `>= 7`

Additional rules:

- If Monte Carlo data is missing, the MC branch is unavailable, but the other branches still work.
- Persist a `c2_pass_reason` field such as:
  - `execution_iv`
  - `monte_carlo`
  - `base_plus_quality`

Trade proposal logic:

- Replace the current harsh add-to-position MOS threshold with the same policy family used by C2.
- Keep policy warnings, but make them align with the new execution-IV semantics.

### E. UI and docs alignment

Files:

- `dashboard/pages/4_PreBuy.py`
- `dashboard/workspace.py`
- `README.md` and any related docs

Changes:

- Relabel `iv_conservative` so it is no longer shown as "IV Bear."
- Add `iv_bear` where users need to see the stress-test floor.
- Make tooltip and table text consistent across dashboard, pre-buy, and workspace views.
- Update docs so the team sees the same terminology everywhere.

## What Does Not Change

- The 8-umbrella analysis pipeline
- The verdict logic (`Own`, `Watch`, `Pass`)
- The bear/base/bull DCF scenario engine
- The Monte Carlo engine itself
- The general "cash is allowed" portfolio philosophy

## Verification Plan

### 1. Regenerate quant outputs first

Before validating anything downstream:

- Re-run quant for a small validation set such as:
  - `V`
  - `AAPL`
  - `MSFT`
  - `GILD`
- Confirm quant JSON and quant markdown show:
  - `iv_bear`
  - `iv_conservative`
  - `iv_base`
  - `iv_bull`
  - `mos_at_analysis`

### 2. Rebuild final reports and allocation input

- Rebuild `FINAL-REPORT.json` for the same validation set.
- Confirm report JSON matches quant semantics exactly.
- Rebuild allocation input and confirm candidate blobs now include:
  - `iv_bear`
  - `monte_carlo_prob_above_price`
  - `live_mos_pct` using the new `iv_conservative`

### 3. Validate allocator behavior

- Re-run allocator with rebuilt input.
- Confirm the portfolio is more invested than the current overly cash-heavy baseline, but still selective.
- Confirm obviously expensive names can still be skipped.
- Confirm great businesses at fair prices now rank meaningfully better.

### 4. Validate pre-buy and trade proposal behavior

- Run pre-buy checks on representative names:
  - `V`
  - `MSFT`
  - `GILD`
  - `AAPL`
- Confirm C2 no longer auto-fails quality compounders only because they are not 20% below bear IV.
- Confirm weak/expensive/low-probability setups still fail.
- Confirm add-to-position logic follows the new policy instead of the old hard MOS rule.

### 5. Validate UI and labeling

- Confirm dashboard labels no longer imply `iv_conservative == bear IV`.
- Confirm pre-buy pages and workspace tables display both execution IV and bear IV correctly where relevant.

## Acceptance Criteria

- `iv_conservative` has one clear meaning everywhere in the repo.
- `iv_bear` exists and is visible where stress context matters.
- Pre-buy C2 becomes multi-path without becoming toothless.
- Allocation input includes Monte Carlo probability and bear IV.
- The allocator is less mechanically cash-biased, but still disciplined.
- User-facing labels and docs match the new methodology.

## Final Recommendation

Implement the methodology as:

- `iv_bear` for stress testing and sizing
- `iv_conservative` for execution discipline
- `iv_base` for fair-value reference
- composite MOS for ranking and sizing
- OR-based C2 for pre-buy

Default formula:

```text
iv_conservative = 25% bear + 75% base
```

Documented alternative:

```text
iv_conservative = iv_base * 0.85
```

Either formula is acceptable if it is centralized in the quant layer. The rest of the architecture should be built so the formula can be swapped without rewriting downstream behavior.
