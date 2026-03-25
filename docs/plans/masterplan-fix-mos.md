# Masterplan: Fix MOS — From Graham-Style Price Gate to Buffett-Style Conviction Gate

## The Problem

Almost every stock in the universe shows deeply negative MOS. The allocator sees this and parks 65% of capital in cash.

| Ticker | Qual. Verdict | Price | Bear IV | Base IV | Bull IV | MOS (bear) | MC P(IV>Price) |
|--------|--------------|-------|---------|---------|---------|------------|----------------|
| AAPL | Own | $248 | $93 | $140 | $194 | -165% | — |
| MSFT | Own | $396 | $264 | $381 | $513 | -50% | 70% |
| V | Own | $307 | $229 | $324 | $432 | -34% | 89% |
| MA | Own | $498 | $347 | $495 | $662 | -44% | ~similar |
| CPRT | Own | $33 | $25 | $34 | $45 | -31% | — |
| GILD | Own | $137 | $138 | $204 | $279 | +0.3% | 99.9% |

The system does careful Buffett-style qualitative work across 8 umbrellas, decides "wonderful business, Own verdict, scores 7-8/10" — then a mechanical DCF vetoes the investment.

---

## The Diagnosis (Combined from Two Independent Reviews)

### The Architectural Contradiction

The analysis pipeline is Buffett-style: understand the business, assess the moat, check management, evaluate economics. But the execution layer is Graham-style: buy below mechanical IV with a percentage discount.

Buffett explicitly evolved past Graham. His margin of safety IS the moat — a business with 50% operating margins, network effects, and zero debt has margin of safety built into the business itself. The system already captures this in umbrellas 1-5, then ignores its own qualitative analysis and lets a one-size-fits-all DCF make the final call.

### Where the Bear Case Becomes the Gatekeeper

The bear case DCF stacks 4 simultaneous haircuts: growth -3pp, margin -3pp, WACC +1pp, exit multiple -3x. That's a ~10% probability scenario where the moat the system just rated 8/10 partially fails on every dimension at once. This bear IV then gets promoted into the master buy hurdle through a chain of files:

1. **Assembler** (`prompts/assembler.md:121`): Maps bear IV → `iv_conservative` in FINAL-REPORT.json
2. **Umbrella 07** (`prompts/07-margin-of-safety.md:8`): "use the bear case as your conservative anchor for price MOS"
3. **Allocator** (`prompts/allocator.md:85`): Ranks candidates on `live_mos_pct` vs conservative IV
4. **Allocator philosophy** (`prompts/allocator.md:247`): "A portfolio of negative-MOS 'quality' stocks is not Buffett-style — it's hope-style"
5. **Pre-buy C2** (`scripts/prebuy-check.py:195`): Hard-requires 20% discount to `iv_conservative`
6. **Allocation input** (`scripts/allocation-input.py:231`): Calculates `live_mos_pct = (iv_conservative - price) / iv_conservative * 100`

Result: 87 candidates, only 6 with positive MOS. 65% cash in the latest allocation proposal.

### The Monte Carlo Already Knows the Truth

The system computes 10,000 Monte Carlo simulations that probabilistically assess undervaluation. V shows 89% probability of being undervalued. GILD shows 99.9%. MSFT shows 70%. But this signal is buried in the report and not used in allocation or pre-buy decisions. The system anchors on the deterministic bear point estimate and ignores its own probabilistic assessment.

### The DCF Itself Is Not Broken

The quant model already uses `--auto-wacc` (CAPM-derived, not fixed 10%), `--owner-earnings`, and `--fade-growth` in the pipeline. The model is internally consistent. The issue isn't the DCF parameters — it's that the bear case (a useful stress test) got promoted into the primary buy/no-buy gate.

Some reports already correct for this ad hoc: AAPL's quant model says bear/base/bull = 93/140/194, but the FINAL-REPORT uses 124/191/276. The system knows the raw quant output is sometimes too harsh but corrects it inconsistently instead of by design.

### What This Means

The contradiction: the analysis layer says MOS includes business resilience, sensitivity, and asymmetry. The downstream machinery reduces it to `price vs bear IV`. Buffett's famous line is "it's far better to buy a wonderful company at a fair price than a fair company at a wonderful price." The system identifies wonderful companies and then demands wonderful prices relative to a worst-case valuation.

---

## The Fix (5 Changes)

**Principle:** Keep the bear case as a stress test. Stop using it as the buy gate. Let the qualitative analysis and Monte Carlo probability drive investment decisions.

### 1. Redefine `iv_conservative` in the assembler

**File:** `prompts/assembler.md` (lines 121-129)

**Currently:** `iv_conservative = bear_iv` from quant model.

**Change to:** `iv_conservative = iv_base * 0.85` (15% haircut to base case). The bear IV becomes a separate field `iv_bear` — still reported, still useful for stress testing and position sizing, but no longer the buy/no-buy anchor.

New FINAL-REPORT.json fields:
```json
"iv_bear": 229,
"iv_conservative": 275,
"iv_base": 324,
"iv_bull": 432,
"monte_carlo_prob_above_price": 0.89
```

`mos_at_analysis` recalculated against new `iv_conservative`.

### 2. Introduce composite MOS signal in the allocator

**File:** `prompts/allocator.md` (lines 78-95, 244-250)

Replace the single `live_mos_pct` ranking with a composite:

| Signal | Weight | Source | Rationale |
|--------|--------|--------|-----------|
| Price vs base IV | Primary | `iv_base` vs `current_price` | "Am I paying a fair price?" |
| MC P(IV > Price) | Primary | `monte_carlo_prob_above_price` | Probability-weighted, not point-estimate |
| Qualitative MOS score | Supporting | Umbrella 07 score (1-10) | Business resilience, moat durability |
| Upside/downside ratio | Supporting | `(iv_base - price) / (price - iv_bear)` | Asymmetry of outcomes |
| Bear IV distance | Sizing input | `iv_bear` vs `current_price` | How bad could it get? → sizes position |

New allocator logic:
- **Buy eligible:** Own/Watch verdict AND (price < iv_base OR MC prob > 65% OR MOS score >= 7)
- **Full size (3-5%):** Positive MOS against new conservative IV + MC prob > 70%
- **Starter size (2-3%):** Negative MOS against conservative but MC prob > 60% and MOS score >= 7
- **Skip:** MC prob < 50% AND negative MOS AND MOS score < 6
- Keep: "If nothing passes, hold cash. Don't force it."

### 3. Soften pre-buy C2 gate

**File:** `scripts/prebuy-check.py` (lines 181-276)

**Currently:** `price <= iv_conservative * 0.80` (20% discount to bear IV). Almost nothing passes.

**Change C2 to pass if ANY of:**
- `price <= iv_conservative` (new conservative = base * 0.85) — basic price check
- `monte_carlo_prob_above_price > 0.70` — probability says undervalued
- `price <= iv_base AND mos_score >= 7` — fair price + strong business margin

Keep C2 as soft (warn) not hard (refuse). C1 quality gate + C3 conviction check remain the hard gates.

### 4. Feed MC probability into allocation input

**File:** `scripts/allocation-input.py` (lines 227-269)

**Currently:** Passes `live_mos_pct` and `upside_downside_ratio`. MC probability exists in FINAL-REPORT.json but isn't included in the candidate blob.

**Change:** Add `monte_carlo_prob_above_price` to each candidate blob so the allocator can actually use it.

### 5. Update umbrella 07 prompt

**File:** `prompts/07-margin-of-safety.md` (line 8)

**Change:** "use the bear case as your conservative anchor for price MOS"
**To:** "use the base case as your primary IV anchor. The bear case is a stress test — assess how much damage the bear scenario would do, but don't score MOS against it as if it's the expected outcome."

---

## What Does NOT Change

- The 8-umbrella analysis pipeline — working well
- The quant DCF model — same parameters, same bear/base/bull spreads (useful stress test)
- The Monte Carlo simulation — the most honest signal, now actually used
- The verdict logic (Own/Watch/Pass) — stays qualitative-driven
- The bear case IV — still computed and reported, just renamed to `iv_bear` and demoted from gatekeeper to context

---

## Files to Modify

| File | Change |
|------|--------|
| `prompts/assembler.md` | Redefine iv_conservative = base * 0.85, add iv_bear field |
| `prompts/allocator.md` | Composite MOS signal, MC probability in ranking |
| `prompts/07-margin-of-safety.md` | Anchor to base case, bear = stress test |
| `scripts/allocation-input.py` | Add MC prob to candidate blob |
| `scripts/prebuy-check.py` | Soften C2 with OR conditions |

---

## Verification

1. **Rebuild allocation-input.json** — check MC probability appears in candidate blobs and `live_mos_pct` uses the new `iv_conservative` definition
2. **Run allocator** on rebuilt input — verify it produces a more invested portfolio (not 65% cash) while still respecting quality
3. **Run prebuy check** on V and MSFT — confirm C2 no longer auto-fails on quality compounders
4. **Spot-check expected MOS shifts:**
   - GILD (already positive MOS) → should remain positive
   - V (currently -34%) → should move to roughly neutral or slightly positive
   - AAPL (currently -165%) → should improve significantly but may still be negative (that's fine — the model thinks it's genuinely expensive, not that the model is broken)
5. **Sanity check:** a stock with low qualitative scores AND negative MOS AND low MC probability should still get skipped — the system shouldn't become indiscriminate
