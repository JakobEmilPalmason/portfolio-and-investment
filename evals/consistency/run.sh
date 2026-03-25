#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# Consistency eval runner for BKNG
#
# Usage:
#   ./evals/consistency/run.sh claude        # 3 trials, Claude only
#   ./evals/consistency/run.sh gemini        # 3 trials, Gemini only
#   ./evals/consistency/run.sh both          # 3 trials each, back-to-back
#   ./evals/consistency/run.sh compare       # Side-by-side Claude vs Gemini
#   ./evals/consistency/run.sh preview       # Open browser results
# ──────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# skillgrade reads eval.yaml from CWD
cd "$SCRIPT_DIR"

# Agent + grader commands run with CWD = repo root
export SKILLGRADE_PROJECT_DIR="$REPO_ROOT"

GRADER="$REPO_ROOT/evals/consistency/graders/check-bkng.py"
COMPARE="$REPO_ROOT/evals/consistency/graders/compare.py"

run_agent() {
    local agent="$1"
    echo "═══ Resetting results for $agent ═══"
    python3 "$GRADER" --reset

    echo ""
    echo "═══ Running $agent — 3 trials on BKNG ═══"
    echo "  Timeout:  15 min per trial"
    echo "  CWD:      $SCRIPT_DIR"
    echo "  Project:  $REPO_ROOT"
    echo ""

    npx skillgrade \
        --eval="bkng-$agent" \
        --trials=3 \
        --preview
}

case "${1:-both}" in
    claude)
        run_agent claude
        ;;
    gemini)
        run_agent gemini
        ;;
    both)
        run_agent claude
        echo ""
        echo "═══════════════════════════════════════"
        echo "  Claude complete. Starting Gemini..."
        echo "═══════════════════════════════════════"
        echo ""
        run_agent gemini
        echo ""
        python3 "$COMPARE"
        ;;
    compare)
        python3 "$COMPARE"
        ;;
    preview)
        npx skillgrade preview browser
        ;;
    *)
        echo "Usage: $0 {claude|gemini|both|compare|preview}"
        exit 1
        ;;
esac

echo ""
echo "═══ Done ═══"
