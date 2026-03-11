#!/usr/bin/env bash
# Investment Analysis Workbench — Command Dispatcher
#
# Usage:
#   ./run.sh scan                    # Universe assembly (A1) then candidate filter (A2)
#   ./run.sh triage [latest|DATE]    # Fast triage (B1) then focused triage (B2), ≤8 deep_dives
#   ./run.sh analyze TICKER          # Full 8-umbrella analysis + final report
#   ./run.sh monitor TICKER          # Change detection (stub — not yet implemented)
#   ./run.sh validate <type> <file>  # Validate a pipeline output file
#
# Note: run-analysis.sh is deprecated. Use this script instead.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
SCANS_DIR="$SCRIPT_DIR/scans"
TRIAGE_DIR="$SCRIPT_DIR/triage"
TODAY=$(date +%Y-%m-%d)

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

# Require a file to exist and be non-empty.
require_file() {
    local label="$1"
    local path="$2"
    if [ ! -f "$path" ]; then
        echo "ERROR [$label]: expected file not found: $path" >&2
        exit 1
    fi
    if [ ! -s "$path" ]; then
        echo "ERROR [$label]: file is empty: $path" >&2
        exit 1
    fi
}

# Require a file to be valid JSON (any type).
require_valid_json() {
    local label="$1"
    local path="$2"
    require_file "$label" "$path"
    if ! jq empty "$path" 2>/dev/null; then
        echo "ERROR [$label]: file is not valid JSON: $path" >&2
        exit 1
    fi
}

# Write a stage checkpoint to pipeline-state.json in the run dir.
# Usage: write_state run_dir stage status [count]
write_state() {
    local run_dir="$1"
    local stage="$2"
    local status="$3"      # complete | failed
    local count="${4:-}"
    local state_file="$run_dir/pipeline-state.json"
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Bootstrap file if missing
    if [ ! -f "$state_file" ]; then
        echo '{"run_date":"'"$TODAY"'","stages":{}}' > "$state_file"
    fi

    local count_field=""
    if [ -n "$count" ]; then
        count_field=', "record_count": '"$count"
    fi

    local tmp
    tmp=$(mktemp)
    jq --arg stage "$stage" \
       --arg status "$status" \
       --arg ts "$ts" \
       '.stages[$stage] = {"status": $status, "timestamp": $ts}' \
       "$state_file" > "$tmp" && mv "$tmp" "$state_file"

    if [ -n "$count" ]; then
        tmp=$(mktemp)
        jq --arg stage "$stage" --argjson n "$count" \
           '.stages[$stage].record_count = $n' \
           "$state_file" > "$tmp" && mv "$tmp" "$state_file"
    fi
}

usage() {
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  scan                     Universe assembly (A1) + candidate filter (A2)"
    echo "  triage [latest|DATE]     Fast triage (B1) + focused triage (B2)"
    echo "  analyze TICKER           Full 8-umbrella analysis + final report"
    echo "  monitor TICKER           Change detection (stub — not yet implemented)"
    echo ""
    echo "Examples:"
    echo "  $0 scan"
    echo "  $0 triage latest"
    echo "  $0 triage 2026-03-11"
    echo "  $0 analyze AAPL"
    echo "  $0 monitor AAPL"
    exit 1
}

# Resolve 'latest' or a DATE to an actual scans directory date
resolve_scan_date() {
    local arg="${1:-latest}"
    if [ "$arg" = "latest" ]; then
        # Find most recent scans/YYYY-MM-DD/ that contains candidates.json
        local found
        found=$(ls -d "$SCANS_DIR"/????-??-??/ 2>/dev/null | sort -r | while read -r d; do
            if [ -f "${d}candidates.json" ]; then
                basename "$d"
                break
            fi
        done)
        if [ -z "$found" ]; then
            echo "ERROR: No scan output found in $SCANS_DIR. Run './run.sh scan' first." >&2
            exit 1
        fi
        echo "$found"
    else
        echo "$arg"
    fi
}

cmd_scan() {
    echo "=== Stage A1: Universe Assembly ==="
    echo "Output: scans/$TODAY/"
    echo ""

    local a1_prompt
    a1_prompt=$(cat "$PROMPTS_DIR/scan-stage-a1.md")

    write_state "$SCANS_DIR/$TODAY" "A1" "started"
    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
        "Today's date: $TODAY

$a1_prompt

Run Stage A1 now. Today's date is $TODAY. Write all output to scans/$TODAY/. Output only the JSON files — no commentary." \
        2>&1

    # --- A1 pass/fail checks ---
    echo ""
    echo "--- Validating A1 output ---"
    "$SCRIPT_DIR/validate.sh" universe "$SCANS_DIR/$TODAY/universe.json" || {
        write_state "$SCANS_DIR/$TODAY" "A1" "failed"
        echo "ERROR [A1]: universe.json failed validation" >&2; exit 1
    }
    require_valid_json "A1:universe-meta" "$SCANS_DIR/$TODAY/universe-meta.json"
    local a1_count
    a1_count=$(jq 'length' "$SCANS_DIR/$TODAY/universe.json")
    echo "A1 OK: $a1_count candidates in universe.json"
    write_state "$SCANS_DIR/$TODAY" "A1" "complete" "$a1_count"

    echo ""
    echo "=== Stage A2: Candidate Filter ==="
    echo ""

    local a2_prompt
    a2_prompt=$(cat "$PROMPTS_DIR/scan-stage-a2.md")

    write_state "$SCANS_DIR/$TODAY" "A2" "started"
    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
        "Today's date: $TODAY

$a2_prompt

Run Stage A2 now. Read universe from scans/$TODAY/universe.json. Write all output to scans/$TODAY/. Output only the data files." \
        2>&1

    # --- A2 pass/fail checks ---
    echo ""
    echo "--- Validating A2 output ---"
    "$SCRIPT_DIR/validate.sh" candidates "$SCANS_DIR/$TODAY/candidates.json" || {
        write_state "$SCANS_DIR/$TODAY" "A2" "failed"
        echo "ERROR [A2]: candidates.json failed validation" >&2; exit 1
    }
    require_valid_json "A2:scan-meta" "$SCANS_DIR/$TODAY/scan-meta.json"
    require_file "A2:candidates-csv" "$SCANS_DIR/$TODAY/candidates.csv"
    require_file "A2:candidates-md"  "$SCANS_DIR/$TODAY/candidates.md"
    local a2_count
    a2_count=$(jq 'length' "$SCANS_DIR/$TODAY/candidates.json")
    echo "A2 OK: $a2_count candidates in candidates.json"
    write_state "$SCANS_DIR/$TODAY" "A2" "complete" "$a2_count"

    echo ""
    echo "=== Scan complete ==="
    echo "Candidates: scans/$TODAY/candidates.json"
    echo "State:      scans/$TODAY/pipeline-state.json"
}

cmd_triage() {
    local date_arg="${1:-latest}"
    local scan_date
    scan_date=$(resolve_scan_date "$date_arg")
    local triage_date="$TODAY"

    echo "=== Stage B1: Fast Triage ==="
    echo "Scan date: $scan_date"
    echo "Output: triage/$triage_date/"
    echo ""

    local b1_prompt
    b1_prompt=$(cat "$PROMPTS_DIR/triage-stage-b1.md")

    mkdir -p "$TRIAGE_DIR/$triage_date"
    write_state "$TRIAGE_DIR/$triage_date" "B1" "started"
    claude --print \
        --allowedTools "Read,Write,Glob,Grep" \
        "Today's date: $TODAY

$b1_prompt

Run Stage B1 now. Read candidates from scans/$scan_date/candidates.json. Write output to triage/$triage_date/. No web search." \
        2>&1

    # --- B1 pass/fail checks ---
    echo ""
    echo "--- Validating B1 output ---"
    "$SCRIPT_DIR/validate.sh" b1-results "$TRIAGE_DIR/$triage_date/b1-results.json" || {
        write_state "$TRIAGE_DIR/$triage_date" "B1" "failed"
        echo "ERROR [B1]: b1-results.json failed validation" >&2; exit 1
    }
    "$SCRIPT_DIR/validate.sh" b1-advance "$TRIAGE_DIR/$triage_date/b1-advance.json" || {
        write_state "$TRIAGE_DIR/$triage_date" "B1" "failed"
        echo "ERROR [B1]: b1-advance.json failed validation" >&2; exit 1
    }
    require_file "B1:b1-summary" "$TRIAGE_DIR/$triage_date/b1-summary.md"
    echo "--- Checking B1 coverage ---"
    "$SCRIPT_DIR/validate.sh" b1-coverage \
        "$TRIAGE_DIR/$triage_date/b1-results.json" \
        "$SCANS_DIR/$scan_date/candidates.json" || {
        write_state "$TRIAGE_DIR/$triage_date" "B1" "failed"
        echo "ERROR [B1]: coverage check failed" >&2; exit 1
    }
    local advance_count results_count
    advance_count=$(jq 'length' "$TRIAGE_DIR/$triage_date/b1-advance.json")
    results_count=$(jq 'length' "$TRIAGE_DIR/$triage_date/b1-results.json")
    echo "B1 OK: $results_count processed, $advance_count advanced"
    write_state "$TRIAGE_DIR/$triage_date" "B1" "complete" "$advance_count"

    echo ""
    echo "=== Stage B2: Focused Triage ==="
    echo ""

    echo "--- Enriching b1-advance with candidates context ---"
    local enriched_tmp; enriched_tmp=$(mktemp)
    jq --slurpfile cands "$SCANS_DIR/$scan_date/candidates.json" '
        . as $advance | $cands[0] as $candidates |
        $advance | map(
            . as $row |
            ($candidates[] | select(.ticker == $row.ticker)) as $cand |
            $row + {
                "already_analyzed": ($cand.already_analyzed // false),
                "source_bucket":    ($cand.source_bucket // []),
                "thesis_tag":       ($cand.thesis_tag // null),
                "style_tag":        ($cand.style_tag // null),
                "short_reason":     ($cand.short_reason // null),
                "possible_disqualifier": ($cand.possible_disqualifier // null),
                "priority":         ($cand.priority // null),
                "triage_rec":       ($cand.triage_rec // null),
                "confidence":       ($cand.confidence // null)
            }
        )
    ' "$TRIAGE_DIR/$triage_date/b1-advance.json" > "$enriched_tmp"
    mv "$enriched_tmp" "$TRIAGE_DIR/$triage_date/b1-advance.json"

    local advance_count_current
    advance_count_current=$(jq 'length' "$TRIAGE_DIR/$triage_date/b1-advance.json")
    if [ "$advance_count_current" -eq 0 ]; then
        echo "=== Stage B2: Skipped (zero B1 advances) ==="
        echo '[]' > "$TRIAGE_DIR/$triage_date/triage.json"
        { echo "# Triage — $triage_date"
          echo ""
          echo "B1 advanced 0 candidates. B2 was not run."
          echo "All candidates were held or rejected. See b1-summary.md for details."
        } > "$TRIAGE_DIR/$triage_date/triage.md"
        "$SCRIPT_DIR/validate.sh" triage "$TRIAGE_DIR/$triage_date/triage.json" || {
            echo "ERROR [B2-skip]: empty triage.json failed validation" >&2; exit 1
        }
        write_state "$TRIAGE_DIR/$triage_date" "B2" "complete" "0"
        echo "=== Triage complete (no deep dives) ==="
        return 0
    fi

    local b2_prompt
    b2_prompt=$(cat "$PROMPTS_DIR/triage-stage-b2.md")

    write_state "$TRIAGE_DIR/$triage_date" "B2" "started"
    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
        "Today's date: $TODAY

$b2_prompt

Run Stage B2 now. Read B1 advance list from triage/$triage_date/b1-advance.json. Read scan context from scans/$scan_date/scan-meta.json. Write output to triage/$triage_date/. Hard cap: 8 deep_dives maximum." \
        2>&1

    # --- B2 pass/fail checks ---
    echo ""
    echo "--- Validating B2 output ---"
    "$SCRIPT_DIR/validate.sh" triage "$TRIAGE_DIR/$triage_date/triage.json" || {
        write_state "$TRIAGE_DIR/$triage_date" "B2" "failed"
        echo "ERROR [B2]: triage.json failed validation" >&2; exit 1
    }
    require_file "B2:triage-md" "$TRIAGE_DIR/$triage_date/triage.md"
    local b2_count deep_dive_count
    b2_count=$(jq 'length' "$TRIAGE_DIR/$triage_date/triage.json")
    deep_dive_count=$(jq '[.[] | select(.next_action == "deep_dive")] | length' "$TRIAGE_DIR/$triage_date/triage.json")
    echo "B2 OK: $b2_count triaged, $deep_dive_count deep_dives"
    write_state "$TRIAGE_DIR/$triage_date" "B2" "complete" "$b2_count"

    echo ""
    echo "=== Triage complete ==="
    echo "Results:    triage/$triage_date/triage.json"
    echo "Deep dives: triage/$triage_date/deep-dive.csv"
    echo "State:      triage/$triage_date/pipeline-state.json"
}

cmd_analyze() {
    local ticker="${1:-}"
    if [ -z "$ticker" ]; then
        echo "ERROR: TICKER required. Usage: $0 analyze TICKER"
        exit 1
    fi

    # Delegate to run-analysis.sh (kept for backward compatibility)
    exec "$SCRIPT_DIR/run-analysis.sh" "$ticker"
}

cmd_validate() {
    local type="${1:-}"
    local path="${2:-}"
    if [ -z "$type" ] || [ -z "$path" ]; then
        echo "Usage: $0 validate <type> <file>"
        echo ""
        echo "Types: universe  candidates  b1-results  b1-advance  triage  final-report  b1-coverage"
        exit 1
    fi
    exec "$SCRIPT_DIR/validate.sh" "$type" "$path"
}

cmd_monitor() {
    local ticker="${1:-}"
    if [ -z "$ticker" ]; then
        echo "ERROR: TICKER required. Usage: $0 monitor TICKER"
        exit 1
    fi
    echo "monitor: not yet implemented."
    echo "See prompts/monitor.md for the planned design."
    echo "Requires FINAL-REPORT.json to exist for $ticker: reports/$ticker/FINAL-REPORT.json"
    exit 0
}

# --- Main dispatch ---

if [ $# -lt 1 ]; then
    usage
fi

COMMAND="$1"
shift

case "$COMMAND" in
    scan)     cmd_scan "$@" ;;
    triage)   cmd_triage "$@" ;;
    analyze)  cmd_analyze "$@" ;;
    monitor)  cmd_monitor "$@" ;;
    validate) cmd_validate "$@" ;;
    *)
        echo "ERROR: Unknown command '$COMMAND'"
        echo ""
        usage
        ;;
esac
