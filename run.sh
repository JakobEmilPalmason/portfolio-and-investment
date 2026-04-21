#!/usr/bin/env bash
# Investment Analysis Workbench — Command Dispatcher
#
# Usage:
#   ./run.sh scan                    # Universe assembly (A1) then candidate filter (A2)
#   ./run.sh triage [latest|WEEK]    # Fast triage (B1) then focused triage (B2), ≤8 deep_dives
#   ./run.sh analyze TICKER          # Full 8-umbrella analysis + final report
#   ./run.sh portfolio [CAPITAL]     # Portfolio simulator (snapshot allocation)
#   ./run.sh dashboard               # Streamlit dashboard
#   ./run.sh diff TICKER              # Cross-period semantic diff (evidence changes)
#   ./run.sh monitor TICKER          # Change detection (stub — not yet implemented)
#   ./run.sh validate <type> <file>  # Validate a pipeline output file
#
# All pipeline output lives under runs/CURRENT_WEEK/:
#   runs/CURRENT_WEEK/scan/          A1+A2 output
#   runs/CURRENT_WEEK/triage/        B1+B2 output
#   runs/CURRENT_WEEK/reports/       Stage C (full analysis) output
#
# UPDATE CURRENT_WEEK at the start of each new week.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
RUNS_DIR="$SCRIPT_DIR/runs"
CONTEXT_DIR="$SCRIPT_DIR/context"
TODAY=$(date +%Y-%m-%d)

# ---------------------------------------------------------------------------
# CURRENT WEEK — update this at the start of each new week
# ---------------------------------------------------------------------------
CURRENT_WEEK="week16_13.04"

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

slugify() {
    local value="${1:-}"
    printf '%s' "$value" \
        | tr '[:upper:]' '[:lower:]' \
        | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
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
    echo "  triage [latest|WEEK]     Fast triage (B1) + focused triage (B2)"
    echo "  fetch TICKER [...]       Fetch financial data from Yahoo Finance"
    echo "  extract TICKER [...]     Fetch SEC EDGAR filing data (XBRL)"
    echo "  analyze TICKER           Full 8-umbrella analysis + final report"
    echo "  portfolio [CAPITAL]      Portfolio simulator (default capital: \$100,000)"
    echo "  dashboard                Streamlit portfolio dashboard"
    echo "  buy TICKER [opts]        Record a long purchase"
    echo "  sell TICKER [opts]       Record a long sale"
    echo "  short TICKER [opts]      Record a short opening"
    echo "  cover TICKER [opts]      Record a short close"
    echo "  holdings                 Show current portfolio state"
    echo "  ledger <subcmd>          Ledger management (init, refresh, bootstrap, check, history)"
    echo "  snapshot                 Capture a daily portfolio snapshot"
    echo "  prebuy TICKER [...]      Pre-buy checklist (quality, price vs IV, conviction)"
    echo "  prebuy --own             Dashboard: C1/C2 status for all Own/Watch-verdict tickers"
    echo "  allocate [CAPITAL]       AI portfolio allocation proposal (saved per run)"
    echo "  monitor TICKER           Change detection (stub — not yet implemented)"
    echo ""
    echo "Examples:"
    echo "  $0 scan"
    echo "  $0 triage latest"
    echo "  $0 triage week11_09.03"
    echo "  $0 fetch AAPL MSFT"
    echo "  $0 fetch --all-reports"
    echo "  $0 analyze AAPL"
    echo "  $0 portfolio"
    echo "  $0 portfolio 250000"
    echo "  $0 portfolio 500000 --min-verdict watch --top 15"
    echo "  $0 dashboard"
    echo "  $0 prebuy GILD"
    echo "  $0 prebuy GILD --dry-run-buy"
    echo "  $0 prebuy --own"
    echo "  $0 buy V --price 312.50 --amount 3000 --iv 380"
    echo "  $0 sell V --price 340 --shares 5"
    echo "  $0 holdings"
    echo "  $0 snapshot"
    echo "  $0 snapshot --start 2026-03-01 --end 2026-03-14"
    echo "  $0 ledger init --capital 100000"
    echo "  $0 ledger refresh"
    echo "  $0 ledger history"
    echo "  $0 allocate"
    echo "  $0 allocate 250000 --label claude-opus"
    echo "  $0 allocate --label agent-7 --output-dir portfolio/allocations/month1/agent-7"
    echo "  $0 monitor AAPL"
    echo ""
    echo "Current week: $CURRENT_WEEK"
    echo "  Output dirs: runs/$CURRENT_WEEK/{scan,triage,reports}"
    exit 1
}

# Resolve 'latest' or a WEEK name to a week directory that has a scan.
# Returns the week name (e.g. "week12_16.03"), not a full path.
resolve_scan_week() {
    local arg="${1:-latest}"
    if [ "$arg" = "latest" ]; then
        local found
        found=$(ls -d "$RUNS_DIR"/week*/scan/ 2>/dev/null | sort -r | while read -r d; do
            if [ -f "${d}candidates.json" ]; then
                basename "$(dirname "$d")"
                break
            fi
        done)
        if [ -z "$found" ]; then
            echo "ERROR: No scan output found in $RUNS_DIR. Run './run.sh scan' first." >&2
            exit 1
        fi
        echo "$found"
    else
        echo "$arg"
    fi
}

cmd_scan() {
    local scan_dir="$RUNS_DIR/$CURRENT_WEEK/scan"
    mkdir -p "$scan_dir"

    echo "=== Stage A1: Universe Assembly ==="
    echo "Output: runs/$CURRENT_WEEK/scan/"
    echo ""

    local a1_prompt
    a1_prompt=$(cat "$PROMPTS_DIR/scan-stage-a1.md")

    write_state "$scan_dir" "A1" "started"
    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
        -- \
        "Today's date: $TODAY

$a1_prompt

Run Stage A1 now. Today's date is $TODAY. Write all output to runs/$CURRENT_WEEK/scan/. Output only the JSON files — no commentary." \
        2>&1

    # --- A1 pass/fail checks ---
    echo ""
    echo "--- Validating A1 output ---"
    "$SCRIPT_DIR/scripts/validate.sh" universe "$scan_dir/universe.json" || {
        write_state "$scan_dir" "A1" "failed"
        echo "ERROR [A1]: universe.json failed validation" >&2; exit 1
    }
    require_valid_json "A1:universe-meta" "$scan_dir/universe-meta.json"
    local a1_count
    a1_count=$(jq 'length' "$scan_dir/universe.json")
    echo "A1 OK: $a1_count candidates in universe.json"
    write_state "$scan_dir" "A1" "complete" "$a1_count"

    echo ""
    echo "=== Stage A2: Candidate Filter ==="
    echo ""

    local a2_prompt
    a2_prompt=$(cat "$PROMPTS_DIR/scan-stage-a2.md")

    write_state "$scan_dir" "A2" "started"
    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
        -- \
        "Today's date: $TODAY

$a2_prompt

Run Stage A2 now. Read universe from runs/$CURRENT_WEEK/scan/universe.json. Write all output to runs/$CURRENT_WEEK/scan/. Output only the data files." \
        2>&1

    # --- A2 pass/fail checks ---
    echo ""
    echo "--- Validating A2 output ---"
    "$SCRIPT_DIR/scripts/validate.sh" candidates "$scan_dir/candidates.json" || {
        write_state "$scan_dir" "A2" "failed"
        echo "ERROR [A2]: candidates.json failed validation" >&2; exit 1
    }
    require_valid_json "A2:scan-meta" "$scan_dir/scan-meta.json"
    require_file "A2:candidates-csv" "$scan_dir/candidates.csv"
    require_file "A2:candidates-md"  "$scan_dir/candidates.md"
    local a2_count
    a2_count=$(jq 'length' "$scan_dir/candidates.json")
    echo "A2 OK: $a2_count candidates in candidates.json"
    write_state "$scan_dir" "A2" "complete" "$a2_count"

    echo ""
    echo "=== Scan complete ==="
    echo "Candidates: runs/$CURRENT_WEEK/scan/candidates.json"
    echo "State:      runs/$CURRENT_WEEK/scan/pipeline-state.json"
}

cmd_triage() {
    local week_arg="${1:-latest}"
    local scan_week
    scan_week=$(resolve_scan_week "$week_arg")
    local scan_dir="$RUNS_DIR/$scan_week/scan"
    local triage_dir="$RUNS_DIR/$CURRENT_WEEK/triage"

    mkdir -p "$triage_dir"

    echo "=== Stage B1: Fast Triage ==="
    echo "Scan:   runs/$scan_week/scan/"
    echo "Output: runs/$CURRENT_WEEK/triage/"
    echo ""

    local b1_prompt
    b1_prompt=$(cat "$PROMPTS_DIR/triage-stage-b1.md")

    write_state "$triage_dir" "B1" "started"
    claude --print \
        --allowedTools "Read,Write,Glob,Grep" \
        -- \
        "Today's date: $TODAY

$b1_prompt

Run Stage B1 now. Read candidates from runs/$scan_week/scan/candidates.json. Write output to runs/$CURRENT_WEEK/triage/. No web search." \
        2>&1

    # --- B1 pass/fail checks ---
    echo ""
    echo "--- Validating B1 output ---"
    "$SCRIPT_DIR/scripts/validate.sh" b1-results "$triage_dir/b1-results.json" || {
        write_state "$triage_dir" "B1" "failed"
        echo "ERROR [B1]: b1-results.json failed validation" >&2; exit 1
    }
    "$SCRIPT_DIR/scripts/validate.sh" b1-advance "$triage_dir/b1-advance.json" || {
        write_state "$triage_dir" "B1" "failed"
        echo "ERROR [B1]: b1-advance.json failed validation" >&2; exit 1
    }
    require_file "B1:b1-summary" "$triage_dir/b1-summary.md"
    echo "--- Checking B1 coverage ---"
    "$SCRIPT_DIR/scripts/validate.sh" b1-coverage \
        "$triage_dir/b1-results.json" \
        "$scan_dir/candidates.json" || {
        write_state "$triage_dir" "B1" "failed"
        echo "ERROR [B1]: coverage check failed" >&2; exit 1
    }
    local advance_count results_count
    advance_count=$(jq 'length' "$triage_dir/b1-advance.json")
    results_count=$(jq 'length' "$triage_dir/b1-results.json")
    echo "B1 OK: $results_count processed, $advance_count advanced"
    write_state "$triage_dir" "B1" "complete" "$advance_count"

    echo ""
    echo "=== Stage B2: Focused Triage ==="
    echo ""

    echo "--- Enriching b1-advance with candidates context ---"
    local enriched_tmp; enriched_tmp=$(mktemp)
    jq --slurpfile cands "$scan_dir/candidates.json" '
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
    ' "$triage_dir/b1-advance.json" > "$enriched_tmp"
    mv "$enriched_tmp" "$triage_dir/b1-advance.json"

    local advance_count_current
    advance_count_current=$(jq 'length' "$triage_dir/b1-advance.json")
    if [ "$advance_count_current" -eq 0 ]; then
        echo "=== Stage B2: Skipped (zero B1 advances) ==="
        echo '[]' > "$triage_dir/triage.json"
        { echo "# Triage — $TODAY"
          echo ""
          echo "B1 advanced 0 candidates. B2 was not run."
          echo "All candidates were held or rejected. See b1-summary.md for details."
        } > "$triage_dir/triage.md"
        "$SCRIPT_DIR/scripts/validate.sh" triage "$triage_dir/triage.json" || {
            echo "ERROR [B2-skip]: empty triage.json failed validation" >&2; exit 1
        }
        write_state "$triage_dir" "B2" "complete" "0"
        echo "=== Triage complete (no deep dives) ==="
        return 0
    fi

    local b2_prompt
    b2_prompt=$(cat "$PROMPTS_DIR/triage-stage-b2.md")

    write_state "$triage_dir" "B2" "started"
    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
        -- \
        "Today's date: $TODAY

$b2_prompt

Run Stage B2 now. Read B1 advance list from runs/$CURRENT_WEEK/triage/b1-advance.json. Read scan context from runs/$scan_week/scan/scan-meta.json. Write output to runs/$CURRENT_WEEK/triage/. Hard cap: 8 deep_dives maximum." \
        2>&1

    # --- B2 pass/fail checks ---
    echo ""
    echo "--- Validating B2 output ---"
    "$SCRIPT_DIR/scripts/validate.sh" triage "$triage_dir/triage.json" || {
        write_state "$triage_dir" "B2" "failed"
        echo "ERROR [B2]: triage.json failed validation" >&2; exit 1
    }
    require_file "B2:triage-md" "$triage_dir/triage.md"
    local b2_count deep_dive_count
    b2_count=$(jq 'length' "$triage_dir/triage.json")
    deep_dive_count=$(jq '[.[] | select(.next_action == "deep_dive")] | length' "$triage_dir/triage.json")
    echo "B2 OK: $b2_count triaged, $deep_dive_count deep_dives"
    write_state "$triage_dir" "B2" "complete" "$b2_count"

    echo ""
    echo "=== Triage complete ==="
    echo "Results:    runs/$CURRENT_WEEK/triage/triage.json"
    echo "Deep dives: runs/$CURRENT_WEEK/triage/deep-dive.csv"
    echo "State:      runs/$CURRENT_WEEK/triage/pipeline-state.json"
}

cmd_fetch() {
    local args=("$@")
    if [ ${#args[@]} -eq 0 ]; then
        echo "Usage: $0 fetch TICKER [TICKER ...]"
        echo "       $0 fetch --all-reports"
        echo "       $0 fetch --all-queue STATE"
        exit 1
    fi
    python3 "$SCRIPT_DIR/scripts/fetch-financials.py" "${args[@]}"
}

cmd_extract() {
    python3 "$SCRIPT_DIR/scripts/fetch-edgar.py" "$@"
}

cmd_diff() {
    python3 "$SCRIPT_DIR/scripts/semantic-diff.py" "$@"
}

cmd_analyze() {
    local ticker="${1:-}"
    if [ -z "$ticker" ]; then
        echo "ERROR: TICKER required. Usage: $0 analyze TICKER"
        exit 1
    fi

    TICKER=$(echo "$ticker" | tr '[:lower:]' '[:upper:]')
    local reports_dir="$RUNS_DIR/$CURRENT_WEEK/reports"
    local report_dir="$reports_dir/$TICKER"
    mkdir -p "$report_dir"

    # Map umbrella numbers to file names
    local UMBRELLA_FILES=(
        ""  # placeholder for index 0
        "01-circle-of-competence"
        "02-durable-competitive-advantage"
        "03-management-capital-allocation"
        "04-business-economics"
        "05-balance-sheet-safety"
        "06-valuation-intrinsic-value"
        "07-margin-of-safety"
        "08-temperament-time-horizon"
        "09-compact-checklist"
    )

    # Auto-fetch financials before analysis (non-blocking on failure)
    echo "Fetching financial data for $TICKER..."
    python3 "$SCRIPT_DIR/scripts/fetch-financials.py" --quiet "$TICKER" || {
        echo "WARNING: Financial data fetch failed. Continuing with web search only."
    }

    # Auto-fetch SEC filing data (non-blocking on failure)
    echo "Fetching SEC filing data for $TICKER..."
    python3 "$SCRIPT_DIR/scripts/fetch-edgar.py" --quiet "$TICKER" || {
        echo "WARNING: SEC evidence fetch failed. Continuing without SEC data."
    }

    # Run quantitative valuation model (non-blocking on failure)
    echo "Running quant valuation model for $TICKER..."
    python3 -m src.quant "$TICKER" \
        --write --json-out --quiet \
        --sensitivity --monte-carlo \
        --auto-wacc --owner-earnings --fade-growth || {
        echo "WARNING: Quant valuation failed. Continuing without quant model output."
    }

    # Build context string from context/{TICKER}/ if it exists
    local CONTEXT=""
    if [ -d "$CONTEXT_DIR/$TICKER" ]; then
        echo "Found context in context/$TICKER/"
        for f in "$CONTEXT_DIR/$TICKER"/*; do
            if [ -f "$f" ]; then
                CONTEXT="$CONTEXT

--- Context file: $(basename "$f") ---
$(cat "$f")"
            fi
        done
    fi

    local SHARED_FORMAT
    SHARED_FORMAT=$(cat "$PROMPTS_DIR/_shared-format.md")

    run_umbrella() {
        local num=$1
        local name="${UMBRELLA_FILES[$num]}"
        local prompt_file="$PROMPTS_DIR/$name.md"
        local output_file="$report_dir/$name.md"

        if [ ! -f "$prompt_file" ]; then
            echo "ERROR: Prompt file not found: $prompt_file"
            return 1
        fi

        local prompt
        prompt=$(cat "$prompt_file")

        echo "Running umbrella $num: $name ..."

        local extra_context=""
        if [ "$num" -eq 9 ]; then
            for i in $(seq 1 8); do
                local section_file="$report_dir/${UMBRELLA_FILES[$i]}.md"
                if [ -f "$section_file" ]; then
                    extra_context="$extra_context

--- Section ${UMBRELLA_FILES[$i]} ---
$(cat "$section_file")"
                fi
            done
        fi

        claude --print \
            --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
            -- \
            "You are performing investment analysis on $TICKER.
Today's date: $TODAY

SHARED OUTPUT FORMAT:
$SHARED_FORMAT

YOUR SPECIFIC ROLE AND INSTRUCTIONS:
$prompt

${CONTEXT:+USER-PROVIDED CONTEXT:
$CONTEXT}

${extra_context:+COMPLETED ANALYSIS SECTIONS:
$extra_context}

Analyze $TICKER now. Write your complete analysis following the format exactly.
Write output to: runs/$CURRENT_WEEK/reports/$TICKER/$name.md
Output ONLY the analysis content — no preamble, no meta-commentary." \
            > "$output_file"

        if [ ! -s "$output_file" ]; then
            echo "ERROR: umbrella $num produced empty output: $output_file" >&2
            exit 1
        fi
        echo "  -> Wrote $output_file ($(wc -c < "$output_file") bytes)"
    }

    run_assembler() {
        echo "Assembling final report..."

        local missing=0
        for i in $(seq 1 9); do
            local section_file="$report_dir/${UMBRELLA_FILES[$i]}.md"
            if [ ! -s "$section_file" ]; then
                echo "  ERROR: Missing or empty section $i (${UMBRELLA_FILES[$i]}): $section_file" >&2
                missing=$((missing + 1))
            fi
        done
        if [ "$missing" -gt 0 ]; then
            echo "ERROR: $missing section(s) missing. Fix before assembling." >&2
            exit 1
        fi

        local sections=""
        for i in $(seq 1 9); do
            local section_file="$report_dir/${UMBRELLA_FILES[$i]}.md"
            sections="$sections

--- Section ${UMBRELLA_FILES[$i]} ---
$(cat "$section_file")"
        done

        local assembler_prompt
        assembler_prompt=$(cat "$PROMPTS_DIR/assembler.md")

        claude --print \
            --allowedTools "WebSearch,Read,Write,Glob,Grep" \
            -- \
            "You are assembling the final investment report for $TICKER.
Today's date: $TODAY

YOUR INSTRUCTIONS:
$assembler_prompt

ALL COMPLETED SECTIONS:
$sections

Produce the final report now.
Write FINAL-REPORT.md to: runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.md
Write FINAL-REPORT.json to: runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.json
Output ONLY the report content — no preamble." \
            > "$report_dir/FINAL-REPORT.md"

        if [ ! -s "$report_dir/FINAL-REPORT.md" ]; then
            echo "ERROR: FINAL-REPORT.md is empty or missing" >&2; exit 1
        fi
        if [ ! -s "$report_dir/FINAL-REPORT.json" ]; then
            echo "ERROR: FINAL-REPORT.json is empty or missing — assembler must write both files" >&2; exit 1
        fi
        if ! jq empty "$report_dir/FINAL-REPORT.json" 2>/dev/null; then
            echo "ERROR: FINAL-REPORT.json is not valid JSON" >&2; exit 1
        fi
        local verdict
        verdict=$(jq -r '.verdict // empty' "$report_dir/FINAL-REPORT.json" 2>/dev/null || true)
        if [ -z "$verdict" ]; then
            echo "ERROR: FINAL-REPORT.json missing 'verdict' field" >&2; exit 1
        fi
        echo "  -> Wrote runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.md"
        echo "  -> Wrote runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.json (verdict: $verdict)"
    }

    run_post_verify() {
        echo ""
        echo "Running post-analysis verification..."
        local verify_json
        verify_json=$(python3 "$SCRIPT_DIR/scripts/verify_claims.py" "$TICKER" \
            --report-dir "$report_dir" --json 2>&1 | tail -1) || true

        local contradicted
        contradicted=$(echo "$verify_json" | jq -r '.contradicted_count // 0' 2>/dev/null || echo "0")

        if [ "$contradicted" -ge 3 ]; then
            echo "VERIFICATION WARNING: $contradicted contradiction(s) found"
            python3 -c "
import json, re, pathlib
qf = pathlib.Path('$SCRIPT_DIR/queue/queue.json')
if qf.exists():
    q = json.loads(qf.read_text())
    for e in q:
        if e['ticker'] == '$TICKER':
            flag = '[VERIFICATION: $contradicted contradictions]'
            notes = e.get('owner_notes', '')
            notes = re.sub(r'\[VERIFICATION:.*?\]', '', notes).strip()
            e['owner_notes'] = (notes + ' ' + flag).strip()
            break
    qf.write_text(json.dumps(q, indent=2) + '\n')
" 2>/dev/null || true
        fi
    }

    local mode="${2:-full}"
    case "$mode" in
        full)
            echo "=== Full analysis for $TICKER ==="
            echo "Output: runs/$CURRENT_WEEK/reports/$TICKER/"
            echo ""
            for i in $(seq 1 8); do run_umbrella "$i"; done
            run_umbrella 9
            run_assembler
            run_post_verify
            echo ""
            echo "=== Analysis complete ==="
            echo "Full report: runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.md"
            ;;
        assemble)
            echo "=== Re-assembling report for $TICKER ==="
            run_umbrella 9
            run_assembler
            run_post_verify
            echo ""
            echo "=== Assembly complete ==="
            echo "Full report: runs/$CURRENT_WEEK/reports/$TICKER/FINAL-REPORT.md"
            ;;
        [1-9])
            echo "=== Running umbrella $mode for $TICKER ==="
            run_umbrella "$mode"
            echo ""
            echo "=== Done ==="
            ;;
        *)
            echo "ERROR: Invalid mode '$mode'. Use a number 1-9 or 'assemble'."
            exit 1
            ;;
    esac
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
    exec "$SCRIPT_DIR/scripts/validate.sh" "$type" "$path"
}

cmd_portfolio() {
    local capital="${1:-100000}"
    shift || true
    python3 "$SCRIPT_DIR/scripts/portfolio-sim.py" --capital "$capital" "$@"
}

cmd_dashboard() {
    python3 -m streamlit run "$SCRIPT_DIR/dashboard/app.py" "$@"
}

cmd_ledger() {
    python3 "$SCRIPT_DIR/scripts/portfolio-ledger.py" "$@"
}

cmd_prebuy() {
    local args=("$@")
    if [ ${#args[@]} -eq 0 ]; then
        echo "Usage: $0 prebuy TICKER [TICKER ...]"
        echo "       $0 prebuy --own"
        exit 1
    fi
    python3 "$SCRIPT_DIR/scripts/prebuy-check.py" "${args[@]}"
}

cmd_allocate() {
    local capital=""
    local label=""
    local output_dir=""

    while [ $# -gt 0 ]; do
        case "$1" in
            --capital)
                shift
                if [ $# -eq 0 ]; then
                    echo "ERROR: --capital requires a value" >&2
                    exit 1
                fi
                capital="$1"
                ;;
            --label)
                shift
                if [ $# -eq 0 ]; then
                    echo "ERROR: --label requires a value" >&2
                    exit 1
                fi
                label="$1"
                ;;
            --output-dir)
                shift
                if [ $# -eq 0 ]; then
                    echo "ERROR: --output-dir requires a value" >&2
                    exit 1
                fi
                output_dir="$1"
                ;;
            -h|--help)
                echo "Usage: $0 allocate [CAPITAL] [--label NAME] [--output-dir PATH]"
                echo ""
                echo "Examples:"
                echo "  $0 allocate"
                echo "  $0 allocate 250000 --label claude-opus"
                echo "  $0 allocate --capital 100000 --label agent-3"
                echo "  $0 allocate --label agent-7 --output-dir portfolio/allocations/month1/agent-7"
                return 0
                ;;
            *)
                if [ -z "$capital" ]; then
                    capital="$1"
                else
                    echo "ERROR: unexpected argument '$1'" >&2
                    echo "Usage: $0 allocate [CAPITAL] [--label NAME] [--output-dir PATH]" >&2
                    exit 1
                fi
                ;;
        esac
        shift || true
    done

    capital="${capital:-100000}"
    local run_ts
    local run_id
    local label_slug=""
    local run_dir
    local input_path
    local proposal_json
    local proposal_md
    local prompt_snapshot
    local metadata_path

    run_ts=$(date -u +"%Y%m%dT%H%M%SZ")
    label_slug=$(slugify "$label")
    run_id="${run_ts}-p$$"
    if [ -n "$label_slug" ]; then
        run_id="${run_id}-${label_slug}"
    fi

    if [ -n "$output_dir" ]; then
        if [[ "$output_dir" = /* ]]; then
            run_dir="$output_dir"
        else
            run_dir="$SCRIPT_DIR/$output_dir"
        fi
    else
        run_dir="$SCRIPT_DIR/portfolio/allocations/$run_id"
    fi

    mkdir -p "$run_dir"
    input_path="$run_dir/allocation-input.json"
    proposal_json="$run_dir/allocation-proposal.json"
    proposal_md="$run_dir/allocation-proposal.md"
    prompt_snapshot="$run_dir/allocator-prompt.md"
    metadata_path="$run_dir/run-metadata.json"

    echo "=== Building allocation input ==="
    python3 "$SCRIPT_DIR/scripts/allocation-input.py" \
        --output "$input_path" \
        --capital "$capital"

    cp "$PROMPTS_DIR/allocator.md" "$prompt_snapshot"

    jq -n \
        --arg run_id "$run_id" \
        --arg run_label "${label:-}" \
        --arg generated_at_utc "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        --arg input_path "$input_path" \
        --arg prompt_snapshot "$prompt_snapshot" \
        --arg proposal_json "$proposal_json" \
        --arg proposal_md "$proposal_md" \
        --arg run_dir "$run_dir" \
        --arg capital "$capital" \
        '{
            run_id: $run_id,
            run_label: $run_label,
            generated_at_utc: $generated_at_utc,
            capital: ($capital | tonumber),
            run_dir: $run_dir,
            input_path: $input_path,
            prompt_snapshot: $prompt_snapshot,
            proposal_json: $proposal_json,
            proposal_md: $proposal_md,
            status: "input_built"
        }' > "$metadata_path"

    echo ""
    echo "=== Running AI Allocator ==="
    echo "Capital: \$$capital"
    if [ -n "$label" ]; then
        echo "Label:   $label"
    fi
    echo "Run ID:  $run_id"
    echo "Output:  $run_dir"
    echo ""

    local allocator_prompt
    allocator_prompt=$(cat "$PROMPTS_DIR/allocator.md")

    local input_data
    input_data=$(cat "$input_path")

    claude --print \
        --allowedTools "Read,Write,Glob,Grep" \
        -- \
        "Today's date: $TODAY

$allocator_prompt

ALLOCATION RUN CONTEXT:
- run_id: $run_id
- run_label: ${label:-unlabeled}
- input_path: $input_path
- output_json_path: $proposal_json
- output_markdown_path: $proposal_md
- prompt_snapshot_path: $prompt_snapshot
- output_directory: $run_dir

ALLOCATION INPUT DATA:
$input_data

Run the allocation now. Capital: \$$capital.
Read the full red_flags, key_risks, key_strengths, buy_triggers, and sell_triggers for each candidate — do not skip them.
Write the machine-readable JSON to $proposal_json.
Write the human-readable markdown to $proposal_md.
Do not overwrite any previous allocation runs or write to any shared global allocation file.
Output ONLY the proposal — no preamble." \
        2>&1

    jq '.status = "completed" | .completed_at_utc = "'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"' \
        "$metadata_path" > "${metadata_path}.tmp"
    mv "${metadata_path}.tmp" "$metadata_path"

    echo ""
    echo "=== Allocation complete ==="
    echo "Input:    $input_path"
    echo "Proposal: $proposal_json"
    echo "Summary:  $proposal_md"
    echo "Meta:     $metadata_path"
}

cmd_verify() {
    local ticker="${1:-}"
    if [ -z "$ticker" ]; then
        echo "ERROR: TICKER required. Usage: $0 verify TICKER"
        exit 1
    fi
    shift
    python3 "$SCRIPT_DIR/scripts/verify_claims.py" "$ticker" "$@"
}

cmd_monitor() {
    local ticker="${1:-}"
    if [ -z "$ticker" ]; then
        echo "ERROR: TICKER required. Usage: $0 monitor TICKER"
        exit 1
    fi
    echo "monitor: not yet implemented."
    echo "See prompts/monitor.md for the planned design."
    echo "Requires FINAL-REPORT.json for $ticker in runs/*/reports/$ticker/FINAL-REPORT.json"
    exit 0
}

# --- Main dispatch ---

if [ $# -lt 1 ]; then
    usage
fi

COMMAND="$1"
shift

case "$COMMAND" in
    scan)      cmd_scan "$@" ;;
    triage)    cmd_triage "$@" ;;
    fetch)     cmd_fetch "$@" ;;
    extract)   cmd_extract "$@" ;;
    diff)      cmd_diff "$@" ;;
    analyze)   cmd_analyze "$@" ;;
    portfolio) cmd_portfolio "$@" ;;
    dashboard) cmd_dashboard "$@" ;;
    buy)       cmd_ledger buy "$@" ;;
    sell)      cmd_ledger sell "$@" ;;
    short)     cmd_ledger short "$@" ;;
    cover)     cmd_ledger cover "$@" ;;
    holdings)  cmd_ledger status "$@" ;;
    snapshot)  python3 "$SCRIPT_DIR/scripts/paper_trade.py" snapshot "$@" ;;
    ledger)    cmd_ledger "$@" ;;
    prebuy)    cmd_prebuy "$@" ;;
    allocate)  cmd_allocate "$@" ;;
    verify)    cmd_verify "$@" ;;
    monitor)   cmd_monitor "$@" ;;
    eunl)      python3 "$SCRIPT_DIR/scripts/eunl-comparison.py" "$@" ;;
    validate)  cmd_validate "$@" ;;
    *)
        echo "ERROR: Unknown command '$COMMAND'"
        echo ""
        usage
        ;;
esac
