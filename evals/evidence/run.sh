#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# Evidence eval runner
#
# Usage:
#   ./evals/evidence/run.sh fast          # Deterministic tests only (no LLM, no network)
#   ./evals/evidence/run.sh integration   # Skillgrade eval (needs LLM + network)
#   ./evals/evidence/run.sh all           # Both
#   ./evals/evidence/run.sh grader        # Run grader directly (no agent)
# ──────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

run_fast() {
    echo "═══ Evidence eval: deterministic tests ═══"
    echo ""
    python3 -m unittest \
        evals.evidence.test_arithmetic_correctness \
        evals.evidence.test_citation_validity \
        evals.evidence.test_extraction_accuracy \
        evals.evidence.test_decomposition_accuracy \
        -v
}

run_grader() {
    echo "═══ Evidence eval: grader (extract) ═══"
    python3 evals/evidence/graders/check-evidence.py SYK extract
    echo ""
    echo "═══ Evidence eval: grader (verify) ═══"
    python3 evals/evidence/graders/check-evidence.py SYK verify
}

run_integration() {
    echo "═══ Evidence eval: Skillgrade integration ═══"
    echo "  CWD:     $REPO_ROOT"
    echo "  Eval:    $SCRIPT_DIR/eval.yaml"
    echo ""
    cd "$SCRIPT_DIR"
    export SKILLGRADE_PROJECT_DIR="$REPO_ROOT"
    npx skillgrade --eval=extract-syk --trials=1
    npx skillgrade --eval=verify-syk --trials=1
}

case "${1:-fast}" in
    fast)
        run_fast
        ;;
    grader)
        run_grader
        ;;
    integration)
        run_integration
        ;;
    all)
        run_fast
        echo ""
        echo "═══════════════════════════════════════"
        echo "  Fast tests complete. Running integration..."
        echo "═══════════════════════════════════════"
        echo ""
        run_integration
        ;;
    *)
        echo "Usage: $0 {fast|grader|integration|all}"
        exit 1
        ;;
esac

echo ""
echo "═══ Done ═══"
