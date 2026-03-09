#!/usr/bin/env bash
set -euo pipefail

# Investment Analysis Orchestrator
# Usage:
#   ./run-analysis.sh TICKER           # Full analysis (all umbrellas + assembly)
#   ./run-analysis.sh TICKER 3         # Single umbrella (e.g., umbrella 3)
#   ./run-analysis.sh TICKER assemble  # Re-assemble final report from existing sections

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
REPORTS_DIR="$SCRIPT_DIR/reports"
CONTEXT_DIR="$SCRIPT_DIR/context"

# Validate input
if [ $# -lt 1 ]; then
    echo "Usage: $0 TICKER [umbrella_number|assemble]"
    echo ""
    echo "Examples:"
    echo "  $0 AAPL           # Full analysis"
    echo "  $0 AAPL 3         # Only umbrella 3 (Management & Capital Allocation)"
    echo "  $0 AAPL assemble  # Re-assemble final report from existing sections"
    echo ""
    echo "Umbrellas:"
    echo "  1  Circle of Competence"
    echo "  2  Durable Competitive Advantage"
    echo "  3  Management & Capital Allocation"
    echo "  4  Business Economics"
    echo "  5  Balance Sheet Safety"
    echo "  6  Valuation vs Intrinsic Value"
    echo "  7  Margin of Safety"
    echo "  8  Temperament & Time Horizon"
    echo "  9  Compact Checklist"
    exit 1
fi

TICKER=$(echo "$1" | tr '[:lower:]' '[:upper:]')
MODE="${2:-full}"

# Map umbrella numbers to file names
declare -a UMBRELLA_FILES=(
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

# Create output directory
mkdir -p "$REPORTS_DIR/$TICKER"

# Build context string if user-provided files exist
CONTEXT=""
if [ -d "$CONTEXT_DIR/$TICKER" ]; then
    echo "Found user-provided context in context/$TICKER/"
    for f in "$CONTEXT_DIR/$TICKER"/*; do
        if [ -f "$f" ]; then
            CONTEXT="$CONTEXT

--- Context file: $(basename "$f") ---
$(cat "$f")"
        fi
    done
fi

# Read shared format
SHARED_FORMAT=$(cat "$PROMPTS_DIR/_shared-format.md")
TODAY=$(date +%Y-%m-%d)

run_umbrella() {
    local num=$1
    local name="${UMBRELLA_FILES[$num]}"
    local prompt_file="$PROMPTS_DIR/$name.md"
    local output_file="$REPORTS_DIR/$TICKER/$name.md"

    if [ ! -f "$prompt_file" ]; then
        echo "ERROR: Prompt file not found: $prompt_file"
        return 1
    fi

    local prompt=$(cat "$prompt_file")

    echo "Running umbrella $num: $name ..."

    # For the compact checklist (09), include all previous sections as input
    local extra_context=""
    if [ "$num" -eq 9 ]; then
        for i in $(seq 1 8); do
            local section_file="$REPORTS_DIR/$TICKER/${UMBRELLA_FILES[$i]}.md"
            if [ -f "$section_file" ]; then
                extra_context="$extra_context

--- Section ${UMBRELLA_FILES[$i]} ---
$(cat "$section_file")"
            fi
        done
    fi

    claude --print \
        --allowedTools "WebSearch,WebFetch,Read,Write,Glob,Grep" \
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

Analyze $TICKER now. Write your complete analysis following the format exactly. Output ONLY the analysis content — no preamble, no meta-commentary." \
        > "$output_file"

    echo "  -> Wrote $output_file"
}

run_assembler() {
    echo "Assembling final report..."

    local sections=""
    for i in $(seq 1 9); do
        local section_file="$REPORTS_DIR/$TICKER/${UMBRELLA_FILES[$i]}.md"
        if [ -f "$section_file" ]; then
            sections="$sections

--- Section ${UMBRELLA_FILES[$i]} ---
$(cat "$section_file")"
        else
            echo "  WARNING: Missing section $i (${UMBRELLA_FILES[$i]})"
        fi
    done

    local assembler_prompt=$(cat "$PROMPTS_DIR/assembler.md")

    claude --print \
        --allowedTools "WebSearch,Read,Write,Glob,Grep" \
        "You are assembling the final investment report for $TICKER.
Today's date: $TODAY

YOUR INSTRUCTIONS:
$assembler_prompt

ALL COMPLETED SECTIONS:
$sections

Produce the final report now. Output ONLY the report content — no preamble." \
        > "$REPORTS_DIR/$TICKER/FINAL-REPORT.md"

    echo "  -> Wrote reports/$TICKER/FINAL-REPORT.md"
}

# Execute based on mode
case "$MODE" in
    full)
        echo "=== Full analysis for $TICKER ==="
        echo ""
        for i in $(seq 1 8); do
            run_umbrella "$i"
        done
        # Checklist needs all 8 sections first
        run_umbrella 9
        # Assemble final report
        run_assembler
        echo ""
        echo "=== Analysis complete ==="
        echo "Full report: reports/$TICKER/FINAL-REPORT.md"
        ;;
    assemble)
        echo "=== Re-assembling report for $TICKER ==="
        # Re-run checklist first (in case sections changed)
        run_umbrella 9
        run_assembler
        echo ""
        echo "=== Assembly complete ==="
        echo "Full report: reports/$TICKER/FINAL-REPORT.md"
        ;;
    [1-9])
        echo "=== Running umbrella $MODE for $TICKER ==="
        run_umbrella "$MODE"
        echo ""
        echo "=== Done ==="
        ;;
    *)
        echo "ERROR: Invalid mode '$MODE'. Use a number 1-9 or 'assemble'."
        exit 1
        ;;
esac
