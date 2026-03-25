"""
Arithmetic engine — deterministic formula execution in sandboxed environment.

Rule: LLM writes the formula string + identifies input facts.
      Python executes with ast.parse() whitelist + restricted builtins.
      LLM never does arithmetic.

Phase 4 of the evidence extraction masterplan.
"""

import ast
import json
import logging
import math
import signal
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

import sys
sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from src.evidence_models import ArithmeticFormulaResult, get_verification_schema

TIMEOUT_SECONDS = 5
DEFAULT_LLM_TIMEOUT = 120
MAX_RETRIES = 1

PROMPT_PATH = REPO_ROOT / "prompts" / "evidence" / "identify-formula.md"

# AST node whitelist — only arithmetic operations allowed
ALLOWED_NODES = {
    ast.Module, ast.Expr, ast.Expression,
    ast.BinOp, ast.UnaryOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd,
    ast.Constant,  # numbers
    ast.Name, ast.Load,
    ast.Call,  # only whitelisted functions
}

ALLOWED_FUNCTIONS = {"abs", "min", "max", "round", "sqrt", "log", "log10"}

# Math functions injected as flat names (no ast.Attribute needed)
SAFE_BUILTINS = {
    "abs": abs, "min": min, "max": max, "round": round,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "pi": math.pi, "e": math.e,
    "True": True, "False": False, "None": None,
}


class ArithmeticSandboxError(Exception):
    """Raised when formula validation or execution fails."""
    pass


# ---------------------------------------------------------------------------
# AST validation
# ---------------------------------------------------------------------------

def validate_formula(formula: str) -> bool:
    """Validate a formula string against the AST whitelist.

    Returns True if safe, raises ArithmeticSandboxError if not.
    """
    try:
        tree = ast.parse(formula, mode='eval')
    except SyntaxError as exc:
        raise ArithmeticSandboxError(f"Syntax error in formula: {exc}") from exc

    for node in ast.walk(tree):
        if type(node) not in ALLOWED_NODES:
            raise ArithmeticSandboxError(
                f"Disallowed AST node: {type(node).__name__}"
            )
        # For Call nodes, ensure function name is whitelisted
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in ALLOWED_FUNCTIONS:
                    raise ArithmeticSandboxError(
                        f"Disallowed function: {node.func.id}"
                    )
            else:
                raise ArithmeticSandboxError(
                    f"Only direct function calls allowed, got {type(node.func).__name__}"
                )

    return True


# ---------------------------------------------------------------------------
# Sandboxed execution
# ---------------------------------------------------------------------------

def _timeout_handler(signum, frame):
    raise ArithmeticSandboxError(f"Formula execution timed out after {TIMEOUT_SECONDS}s")


def execute_formula(formula: str, inputs: dict[str, float]) -> float:
    """Execute a formula in a sandboxed environment.

    Args:
        formula: Python expression string (must pass validate_formula)
        inputs: Variable name → float value mapping

    Returns:
        Result as float.

    Raises:
        ArithmeticSandboxError on validation failure, timeout, or execution error.
    """
    validate_formula(formula)

    # Ensure all inputs are float
    safe_inputs = {}
    for k, v in inputs.items():
        if not isinstance(v, (int, float)):
            raise ArithmeticSandboxError(f"Input '{k}' must be numeric, got {type(v).__name__}")
        safe_inputs[k] = float(v)

    namespace = {"__builtins__": {}}
    namespace.update(SAFE_BUILTINS)
    namespace.update(safe_inputs)

    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(TIMEOUT_SECONDS)
    try:
        result = eval(compile(formula, "<formula>", "eval"), namespace)  # noqa: S307
    except ArithmeticSandboxError:
        raise
    except ZeroDivisionError as exc:
        raise ArithmeticSandboxError(f"Division by zero: {exc}") from exc
    except Exception as exc:
        raise ArithmeticSandboxError(f"Execution error: {exc}") from exc
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

    if not isinstance(result, (int, float)):
        raise ArithmeticSandboxError(f"Result is not numeric: {type(result).__name__}")

    return float(result)


# ---------------------------------------------------------------------------
# LLM formula identification
# ---------------------------------------------------------------------------

def _claude_extract(prompt: str, timeout: int = DEFAULT_LLM_TIMEOUT) -> str:
    """Call claude --print --output-format json. Returns raw stdout."""
    try:
        result = subprocess.run(
            ["claude", "--print", "--output-format", "json",
             "--allowedTools", "", "--", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ArithmeticSandboxError(f"claude timed out after {timeout}s")
    except FileNotFoundError:
        raise ArithmeticSandboxError("claude CLI not found")

    if result.returncode != 0:
        raise ArithmeticSandboxError(f"claude exit code {result.returncode}: {result.stderr[:300]}")
    return result.stdout


def _parse_json_response(raw: str) -> dict:
    """Parse JSON, handling {"result": ...} wrappers."""
    data = json.loads(raw)
    if isinstance(data, dict) and "result" in data:
        inner = data["result"]
        if isinstance(inner, str):
            inner = json.loads(inner)
        if isinstance(inner, dict):
            return inner
    return data


def verify_arithmetic_assertion(
    assertion_text: str,
    candidate_facts: list[dict],
    ticker: str,
) -> dict | None:
    """Use LLM to identify formula, then execute in sandbox.

    Returns a computation_cache dict on success, None on failure.
    """
    if not PROMPT_PATH.exists():
        logger.warning("Pass C prompt not found at %s", PROMPT_PATH)
        return None

    template = PROMPT_PATH.read_text(encoding="utf-8")
    schema_json = json.dumps(get_verification_schema("arithmetic"), indent=2)

    # Build evidence context: only numeric facts
    numeric_facts = [
        f for f in candidate_facts
        if f.get("fact_value_numeric") is not None
    ]
    if not numeric_facts:
        logger.info("No numeric facts for arithmetic verification of: %s", assertion_text[:60])
        return None

    facts_text = "\n".join(
        f"- {f['fact_key']}: {f['fact_value']} (numeric={f['fact_value_numeric']}, "
        f"unit={f.get('fact_unit','?')}, period={f.get('fiscal_period','?')})"
        for f in numeric_facts[:30]
    )

    prompt = (
        template
        .replace("{TICKER}", ticker)
        .replace("{ASSERTION}", assertion_text)
        .replace("{EVIDENCE}", facts_text)
        .replace("{JSON_SCHEMA}", schema_json)
    )

    # LLM call with retry
    for attempt in range(1 + MAX_RETRIES):
        try:
            raw = _claude_extract(prompt)
            data = _parse_json_response(raw)
            result = ArithmeticFormulaResult.model_validate(data)
            break
        except (ArithmeticSandboxError, json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Pass C attempt %d: %s", attempt + 1, exc)
            if attempt < MAX_RETRIES:
                continue
            return None
    else:
        return None

    # Map input variable names to actual fact values
    input_values = {}
    for var_name, fact_key in result.inputs.items():
        matching = [f for f in numeric_facts if f["fact_key"] == fact_key]
        if not matching:
            logger.warning("Pass C: no fact found for key '%s' (variable '%s')", fact_key, var_name)
            return None
        input_values[var_name] = matching[0]["fact_value_numeric"]

    # Execute in sandbox
    try:
        computed = execute_formula(result.formula, input_values)
    except ArithmeticSandboxError as exc:
        logger.warning("Pass C sandbox error: %s", exc)
        return None

    return {
        "ticker": ticker,
        "computation_key": f"verify:{assertion_text[:80]}",
        "formula": result.formula,
        "inputs_json": json.dumps({k: v for k, v in input_values.items()}),
        "result_value": computed,
        "result_unit": result.result_unit,
        "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
