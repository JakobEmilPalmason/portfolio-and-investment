#!/usr/bin/env bash
# run-tests.sh — Gold-test suite for validate.sh schema validation.
#
# Tests that:
#   1. Valid fixtures pass validation
#   2. Invalid fixtures are correctly rejected
#   3. Missing fields / bad enum values / cap violations are caught
#
# Does NOT call the LLM or run the full pipeline — that requires live API calls.
# For end-to-end pipeline tests, see tests/e2e/README.md.
#
# Usage:
#   ./tests/run-tests.sh           # run all tests
#   ./tests/run-tests.sh verbose   # show pass details too

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
VALIDATE="$ROOT_DIR/validate.sh"
FIXTURES="$SCRIPT_DIR/fixtures"
VERBOSE="${1:-}"

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

run_test() {
    local name="$1"
    local expect="$2"   # "pass" or "fail"
    local type="$3"
    local file="$4"

    local actual_exit=0
    local output
    output=$("$VALIDATE" "$type" "$file" 2>&1) || actual_exit=$?

    local passed=false
    if [ "$expect" = "pass" ] && [ "$actual_exit" -eq 0 ]; then
        passed=true
    elif [ "$expect" = "fail" ] && [ "$actual_exit" -ne 0 ]; then
        passed=true
    fi

    if $passed; then
        PASS=$((PASS + 1))
        if [ -n "$VERBOSE" ]; then
            echo "  PASS  $name"
            if [ -n "$VERBOSE" ] && echo "$output" | grep -q '^OK:'; then
                echo "        $(echo "$output" | grep '^OK:')"
            fi
        fi
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL  $name"
        echo "        expected=$expect, exit=$actual_exit"
        echo "        output: $(echo "$output" | head -3 | sed 's/^/        /')"
    fi
}

run_coverage_test() {
    local name="$1"
    local expect="$2"   # "pass" or "fail"
    local b1_results="$3"
    local candidates="$4"

    local actual_exit=0
    local output
    output=$("$VALIDATE" b1-coverage "$b1_results" "$candidates" 2>&1) || actual_exit=$?

    local passed=false
    if [ "$expect" = "pass" ] && [ "$actual_exit" -eq 0 ]; then
        passed=true
    elif [ "$expect" = "fail" ] && [ "$actual_exit" -ne 0 ]; then
        passed=true
    fi

    if $passed; then
        PASS=$((PASS + 1))
        if [ -n "$VERBOSE" ]; then
            echo "  PASS  $name"
            if [ -n "$VERBOSE" ] && echo "$output" | grep -q '^OK:'; then
                echo "        $(echo "$output" | grep '^OK:')"
            fi
        fi
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL  $name"
        echo "        expected=$expect, exit=$actual_exit"
        echo "        output: $(echo "$output" | head -3 | sed 's/^/        /')"
    fi
}

# ---------------------------------------------------------------------------
# Prerequisite check
# ---------------------------------------------------------------------------

if [ ! -x "$VALIDATE" ]; then
    echo "ERROR: validate.sh not found or not executable: $VALIDATE" >&2
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "ERROR: jq is required but not installed. Install with: brew install jq" >&2
    exit 1
fi

echo "=== Investment Analysis — Validation Test Suite ==="
echo ""

# ---------------------------------------------------------------------------
# Group 1: Valid fixtures should pass
# ---------------------------------------------------------------------------
echo "--- Valid fixtures (expect: pass) ---"

run_test "universe valid"           pass universe     "$FIXTURES/universe-valid.json"
run_test "candidates valid"         pass candidates   "$FIXTURES/candidates-valid.json"
run_test "b1-results valid"         pass b1-results   "$FIXTURES/b1-results-valid.json"
run_test "b1-advance valid"         pass b1-advance   "$FIXTURES/b1-advance-valid.json"
run_test "triage valid"             pass triage       "$FIXTURES/triage-valid.json"
run_test "final-report valid"       pass final-report "$FIXTURES/final-report-valid.json"

# The real candidates.json from the last scan should also pass
if [ -f "$ROOT_DIR/scans/2026-03-11/candidates.json" ]; then
    run_test "real candidates.json (2026-03-11)" pass candidates "$ROOT_DIR/scans/2026-03-11/candidates.json"
fi

echo ""

# ---------------------------------------------------------------------------
# Group 2: Invalid fixtures should fail
# ---------------------------------------------------------------------------
echo "--- Invalid fixtures (expect: fail) ---"

run_test "candidates missing A2 fields"  fail candidates   "$FIXTURES/candidates-invalid-missing-fields.json"
run_test "triage deep_dive cap exceeded" fail triage        "$FIXTURES/triage-invalid-cap-exceeded.json"
run_test "final-report bad verdict"      fail final-report  "$FIXTURES/final-report-invalid-verdict.json"

echo ""

# ---------------------------------------------------------------------------
# Group 3: Edge cases
# ---------------------------------------------------------------------------
echo "--- Edge cases ---"

# Non-existent file
run_test "missing file returns error" fail universe "/tmp/does-not-exist-xyz.json"

# Malformed JSON
TMPFILE=$(mktemp /tmp/malformed-XXXX.json)
echo '{"ticker": "broken"' > "$TMPFILE"
run_test "malformed JSON" fail universe "$TMPFILE"
rm -f "$TMPFILE"

# Empty file
TMPFILE=$(mktemp /tmp/empty-XXXX.json)
run_test "empty file" fail universe "$TMPFILE"
rm -f "$TMPFILE"

# Empty array
TMPFILE=$(mktemp /tmp/empty-arr-XXXX.json)
echo '[]' > "$TMPFILE"
run_test "empty array (universe)" fail universe "$TMPFILE"
rm -f "$TMPFILE"

echo ""

# ---------------------------------------------------------------------------
# Group 4: Zero-count valid fixtures (expect: pass)
# ---------------------------------------------------------------------------
echo "--- Zero-count valid fixtures (expect: pass) ---"

run_test "b1-advance empty array" pass b1-advance "$FIXTURES/b1-advance-empty.json"
run_test "triage empty array"     pass triage     "$FIXTURES/triage-empty.json"

echo ""

# ---------------------------------------------------------------------------
# Group 5: B1 coverage checks
# ---------------------------------------------------------------------------
echo "--- B1 coverage checks ---"

run_coverage_test "b1-coverage exact match"        pass "$FIXTURES/b1-results-valid.json"              "$FIXTURES/candidates-valid.json"
run_coverage_test "b1-coverage missing ticker"     fail "$FIXTURES/b1-results-coverage-missing.json"   "$FIXTURES/candidates-valid.json"
run_coverage_test "b1-coverage extra ticker"       fail "$FIXTURES/b1-results-coverage-extra.json"     "$FIXTURES/candidates-valid.json"
run_coverage_test "b1-coverage duplicate ticker"   fail "$FIXTURES/b1-results-coverage-duplicate.json" "$FIXTURES/candidates-valid.json"

echo ""

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
TOTAL=$((PASS + FAIL))
echo "=== Results: $PASS/$TOTAL passed ==="

if [ "$FAIL" -gt 0 ]; then
    echo "$FAIL test(s) failed." >&2
    exit 1
fi

echo "All tests passed."
