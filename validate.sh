#!/usr/bin/env bash
# validate.sh — Schema validator for pipeline output files.
#
# Usage:
#   ./validate.sh <type> <file>
#
# Types:
#   universe       scans/YYYY-MM-DD/universe.json
#   candidates     scans/YYYY-MM-DD/candidates.json
#   b1-results     triage/YYYY-MM-DD/b1-results.json
#   b1-advance     triage/YYYY-MM-DD/b1-advance.json
#   triage         triage/YYYY-MM-DD/triage.json
#   final-report   reports/TICKER/FINAL-REPORT.json
#
# Exit 0 = valid. Exit 1 = invalid (errors printed to stderr).

set -euo pipefail

TYPE="${1:-}"
FILE="${2:-}"
FILE2="${3:-}"

if [ -z "$TYPE" ] || [ -z "$FILE" ]; then
    echo "Usage: $0 <type> <file> [file2]" >&2
    echo "Types: universe  candidates  b1-results  b1-advance  triage  final-report  b1-coverage" >&2
    exit 1
fi

if [ "$TYPE" = "b1-coverage" ] && [ -z "$FILE2" ]; then
    echo "Usage: $0 b1-coverage <b1-results.json> <candidates.json>" >&2
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: file not found: $FILE" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ERRORS=0

fail() {
    echo "FAIL: $*" >&2
    ERRORS=$((ERRORS + 1))
}

ok() {
    if [ "$ERRORS" -eq 0 ]; then
        echo "OK: $*"
    fi
}

check_valid_json() {
    if ! jq empty "$FILE" 2>/dev/null; then
        fail "not valid JSON: $FILE"
        exit 1
    fi
}

check_is_array() {
    local len
    len=$(jq 'if type == "array" then length else -1 end' "$FILE")
    if [ "$len" -eq -1 ]; then
        fail "expected JSON array, got object or other type"
        exit 1
    fi
    echo "$len"
}

# Check that every object in a JSON array has all required fields.
check_array_fields() {
    local -a required=("$@")
    local checks=""
    for k in "${required[@]}"; do
        checks="$checks and (has(\"$k\"))"
    done
    checks="${checks# and }"
    # Use `(expr) | not` instead of `not(expr)` — macOS jq compatibility
    local bad
    bad=$(jq "[.[] | select(($checks) | not)] | length" "$FILE")
    if [ "$bad" -gt 0 ]; then
        fail "$bad record(s) missing required fields: ${required[*]}"
        jq "[.[] | select(($checks) | not)] | .[0]" "$FILE" >&2
    fi
}

# Check that an enum field only contains allowed values.
check_enum() {
    local field="$1"
    shift
    local allowed=("$@")
    local vals
    vals=$(printf '"%s",' "${allowed[@]}")
    vals="${vals%,}"
    # Collect unique values that are not in the allowed set
    local bad
    bad=$(jq "[.[] | .${field} | select(. != null) | select(IN(${vals}) | not)] | unique" "$FILE")
    if [ "$bad" != "[]" ]; then
        fail "field '$field' contains unexpected values: $bad (allowed: ${allowed[*]})"
    fi
}

# Check count range.
check_count_range() {
    local count="$1"
    local min="$2"
    local max="$3"
    local label="$4"
    if [ "$count" -lt "$min" ]; then
        fail "$label: count $count is below minimum $min"
    fi
    if [ "$count" -gt "$max" ]; then
        fail "$label: count $count exceeds maximum $max"
    fi
}

# ---------------------------------------------------------------------------
# Type-specific validation
# ---------------------------------------------------------------------------

validate_universe() {
    check_valid_json
    local count
    count=$(check_is_array)
    check_count_range "$count" 10 600 "universe"
    check_array_fields ticker company sector source_bucket mkt_cap_tier geography already_analyzed as_of_date
    check_enum "mkt_cap_tier" mega large mid
    check_enum "geography" US Europe Asia Other
    check_enum "sector" Technology Financials Healthcare Industrials Consumer "Communication Services" Energy Materials "Real Estate" Utilities
    ok "universe — $count entries"
}

validate_candidates() {
    check_valid_json
    local count
    count=$(check_is_array)
    check_count_range "$count" 5 400 "candidates"
    if [ "$count" -lt 50 ]; then
        echo "WARNING: candidates count $count is below recommended minimum of 50" >&2
    fi
    check_array_fields ticker company sector industry source_bucket thesis_tag style_tag \
        short_reason possible_disqualifier mkt_cap_tier geography already_analyzed \
        priority triage_rec confidence as_of_date
    check_enum "priority" high medium low
    check_enum "triage_rec" yes maybe no
    check_enum "confidence" high medium low
    check_enum "mkt_cap_tier" mega large mid
    check_enum "style_tag" compounder value cyclical recovery speculative income
    # short_reason and possible_disqualifier must be non-empty strings
    local empty_reasons
    empty_reasons=$(jq '[.[] | select(.short_reason == "" or .short_reason == null)] | length' "$FILE")
    if [ "$empty_reasons" -gt 0 ]; then
        fail "$empty_reasons record(s) have empty short_reason"
    fi
    ok "candidates — $count entries"
}

validate_b1_results() {
    check_valid_json
    local count
    count=$(check_is_array)
    check_count_range "$count" 1 600 "b1-results"
    check_array_fields ticker company b1_verdict b1_reason
    check_enum "b1_verdict" advance hold reject
    # b1_reason must be non-empty
    local empty_reasons
    empty_reasons=$(jq '[.[] | select(.b1_reason == "" or .b1_reason == null)] | length' "$FILE")
    if [ "$empty_reasons" -gt 0 ]; then
        fail "$empty_reasons record(s) have empty b1_reason"
    fi
    local advance_count
    advance_count=$(jq '[.[] | select(.b1_verdict == "advance")] | length' "$FILE")
    if [ "$advance_count" -gt 50 ]; then
        fail "advance count $advance_count exceeds soft cap of 50"
    fi
    ok "b1-results — $count total, $advance_count advance"
}

validate_b1_advance() {
    check_valid_json
    local count
    count=$(check_is_array)
    check_count_range "$count" 0 50 "b1-advance"
    if [ "$count" -gt 0 ]; then
        check_array_fields ticker company b1_verdict b1_reason
        # All records must be advance
        local non_advance
        non_advance=$(jq '[.[] | select(.b1_verdict != "advance")] | length' "$FILE")
        if [ "$non_advance" -gt 0 ]; then
            fail "b1-advance contains $non_advance non-advance records"
        fi
    fi
    ok "b1-advance — $count entries"
}

validate_triage() {
    check_valid_json
    local count
    count=$(check_is_array)
    check_count_range "$count" 0 50 "triage"
    local deep_dive_count=0
    if [ "$count" -gt 0 ]; then
        check_array_fields ticker company business_type sector thesis_tag quality_score \
            valuation_score balance_sheet_score red_flag why_interesting confidence \
            next_action reason_for_action
        check_enum "next_action" deep_dive refresh monitor discard
        check_enum "confidence" high medium low
        # Hard cap: ≤8 deep_dives
        deep_dive_count=$(jq '[.[] | select(.next_action == "deep_dive")] | length' "$FILE")
        if [ "$deep_dive_count" -gt 8 ]; then
            fail "deep_dive count $deep_dive_count exceeds hard cap of 8"
        fi
        # Scores must be 0-10
        local bad_scores
        bad_scores=$(jq '[.[] | select(.quality_score < 0 or .quality_score > 10 or .valuation_score < 0 or .valuation_score > 10 or .balance_sheet_score < 0 or .balance_sheet_score > 10)] | length' "$FILE")
        if [ "$bad_scores" -gt 0 ]; then
            fail "$bad_scores record(s) have scores outside 0-10 range"
        fi
    fi
    ok "triage — $count entries, $deep_dive_count deep_dives"
}

validate_final_report() {
    check_valid_json
    # Must be an object, not array
    local t
    t=$(jq -r 'type' "$FILE")
    if [ "$t" != "object" ]; then
        fail "expected JSON object, got $t"
        exit 1
    fi
    # Required top-level fields
    local required=(ticker company analysis_date verdict average_score umbrella_scores \
        key_strengths key_risks red_flags buy_triggers sell_triggers \
        valuation_summary source_summary confidence)
    for field in "${required[@]}"; do
        local present
        present=$(jq --arg f "$field" 'has($f)' "$FILE")
        if [ "$present" != "true" ]; then
            fail "missing required field: $field"
        fi
    done
    # Verdict must be Own/Watch/Pass
    local verdict
    verdict=$(jq -r '.verdict // ""' "$FILE")
    if [[ "$verdict" != "Own" && "$verdict" != "Watch" && "$verdict" != "Pass" ]]; then
        fail "verdict must be Own, Watch, or Pass; got: '$verdict'"
    fi
    # average_score must be 0-10
    local avg
    avg=$(jq '.average_score // -1' "$FILE")
    if (( $(echo "$avg < 0 || $avg > 10" | bc -l) )); then
        fail "average_score out of range: $avg"
    fi
    # umbrella_scores must have all 8 keys
    local umbrella_keys=(circle_of_competence competitive_advantage management \
        business_economics balance_sheet valuation margin_of_safety temperament)
    for k in "${umbrella_keys[@]}"; do
        local present
        present=$(jq --arg k "$k" '.umbrella_scores | has($k)' "$FILE")
        if [ "$present" != "true" ]; then
            fail "umbrella_scores missing key: $k"
        fi
    done
    ok "final-report — verdict=$verdict, avg=$avg"
}

validate_b1_coverage() {
    # FILE = b1-results.json, FILE2 = candidates.json
    [ -f "$FILE2" ] || { fail "candidates file not found: $FILE2"; exit 1; }
    jq empty "$FILE" 2>/dev/null  || { fail "b1-results is not valid JSON"; exit 1; }
    jq empty "$FILE2" 2>/dev/null || { fail "candidates is not valid JSON"; exit 1; }

    # Duplicate check in b1-results
    local dup_count
    dup_count=$(jq '[.[].ticker] | group_by(.) | map(select(length > 1)) | length' "$FILE")
    if [ "$dup_count" -gt 0 ]; then
        local dups
        dups=$(jq -r '[.[].ticker] | group_by(.) | map(select(length > 1)) | .[] | .[0]' "$FILE")
        fail "b1-results contains duplicate tickers: $dups"
    fi

    # Missing: in candidates but not b1-results
    local missing
    missing=$(jq -r --slurpfile b1 "$FILE" \
        '[.[].ticker] - [$b1[0][].ticker] | .[]' "$FILE2")
    [ -n "$missing" ] && fail "tickers missing from b1-results: $(echo "$missing" | tr '\n' ' ')"

    # Extra: in b1-results but not candidates
    local extra
    extra=$(jq -r --slurpfile cands "$FILE2" \
        '[.[].ticker] - [$cands[0][].ticker] | .[]' "$FILE")
    [ -n "$extra" ] && fail "tickers in b1-results not in candidates: $(echo "$extra" | tr '\n' ' ')"

    local count; count=$(jq 'length' "$FILE")
    ok "b1-coverage — $count tickers match exactly"
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

case "$TYPE" in
    universe)      validate_universe ;;
    candidates)    validate_candidates ;;
    b1-results)    validate_b1_results ;;
    b1-advance)    validate_b1_advance ;;
    triage)        validate_triage ;;
    final-report)  validate_final_report ;;
    b1-coverage)   validate_b1_coverage ;;
    *)
        echo "ERROR: unknown type '$TYPE'" >&2
        echo "Types: universe  candidates  b1-results  b1-advance  triage  final-report  b1-coverage" >&2
        exit 1
        ;;
esac

if [ "$ERRORS" -gt 0 ]; then
    echo "INVALID: $ERRORS error(s) found in $FILE" >&2
    exit 1
fi
