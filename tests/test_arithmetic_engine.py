"""Tests for Phase 4 arithmetic engine (Pass C sandbox)."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.sec_edgar.arithmetic_engine import (
    validate_formula,
    execute_formula,
    ArithmeticSandboxError,
)


class TestValidateFormula(unittest.TestCase):
    """Test AST validation whitelist."""

    # --- Should pass ---

    def test_basic_arithmetic(self):
        validate_formula("a + b")
        validate_formula("a - b")
        validate_formula("a * b")
        validate_formula("a / b")

    def test_compound_expression(self):
        validate_formula("(operating_income * (1 - tax_rate)) / ((ic_curr + ic_prev) / 2)")

    def test_unary_minus(self):
        validate_formula("-a + b")

    def test_power(self):
        validate_formula("a ** 2")

    def test_allowed_functions(self):
        validate_formula("abs(a - b)")
        validate_formula("min(a, b)")
        validate_formula("max(a, b)")
        validate_formula("round(a, 2)")
        validate_formula("sqrt(a)")
        validate_formula("log(a)")
        validate_formula("log10(a)")

    def test_constants(self):
        validate_formula("a + 1.5")
        validate_formula("a * 100")

    # --- Should fail ---

    def test_rejects_import(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("__import__('os').system('rm -rf /')")

    def test_rejects_eval(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("eval('1+1')")

    def test_rejects_exec(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("exec('print(1)')")

    def test_rejects_open(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("open('/etc/passwd').read()")

    def test_rejects_class_escape(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("().__class__.__bases__[0].__subclasses__()")

    def test_rejects_type_subclasses(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("type.__subclasses__(type)")

    def test_rejects_attribute_access(self):
        """math.sqrt requires ast.Attribute which is not whitelisted."""
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("math.sqrt(a)")

    def test_rejects_subscript(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("data['key']")

    def test_rejects_unknown_function(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("print(a)")

    def test_rejects_syntax_error(self):
        with self.assertRaises(ArithmeticSandboxError):
            validate_formula("a +* b")


class TestExecuteFormula(unittest.TestCase):
    """Test sandboxed execution."""

    def test_basic_math(self):
        result = execute_formula("a + b", {"a": 10.0, "b": 20.0})
        self.assertAlmostEqual(result, 30.0)

    def test_roic_calculation(self):
        """ROIC = NOPAT / average invested capital."""
        result = execute_formula(
            "nopat / ((ic_curr + ic_prev) / 2)",
            {"nopat": 3000.0, "ic_curr": 25000.0, "ic_prev": 23000.0},
        )
        self.assertAlmostEqual(result, 0.125, places=3)

    def test_margin_calculation(self):
        result = execute_formula(
            "gross_profit / revenue",
            {"gross_profit": 16000.0, "revenue": 25000.0},
        )
        self.assertAlmostEqual(result, 0.64, places=2)

    def test_growth_rate(self):
        result = execute_formula(
            "(rev_curr - rev_prev) / rev_prev",
            {"rev_curr": 25100.0, "rev_prev": 22600.0},
        )
        self.assertAlmostEqual(result, 0.1106, places=3)

    def test_abs_function(self):
        result = execute_formula("abs(a - b) / b", {"a": 10.0, "b": 12.0})
        self.assertAlmostEqual(result, 1 / 6, places=4)

    def test_sqrt_function(self):
        result = execute_formula("sqrt(a)", {"a": 144.0})
        self.assertAlmostEqual(result, 12.0)

    def test_min_max(self):
        result = execute_formula("max(a, b)", {"a": 5.0, "b": 10.0})
        self.assertEqual(result, 10.0)

    def test_division_by_zero(self):
        with self.assertRaises(ArithmeticSandboxError):
            execute_formula("a / b", {"a": 10.0, "b": 0.0})

    def test_non_numeric_input_rejected(self):
        with self.assertRaises(ArithmeticSandboxError):
            execute_formula("a + b", {"a": "hello", "b": 10.0})

    def test_result_is_float(self):
        result = execute_formula("a + b", {"a": 5, "b": 3})
        self.assertIsInstance(result, float)


class TestSandboxSafety(unittest.TestCase):
    """Verify the sandbox cannot be escaped."""

    def test_no_builtins_leakage(self):
        """Even if validation is bypassed, builtins are restricted."""
        # This should fail at validation, but even if it didn't...
        with self.assertRaises(ArithmeticSandboxError):
            execute_formula("__import__('os')", {})

    def test_cannot_access_globals(self):
        with self.assertRaises(ArithmeticSandboxError):
            execute_formula("globals()", {})

    def test_cannot_access_locals(self):
        with self.assertRaises(ArithmeticSandboxError):
            execute_formula("locals()", {})


if __name__ == "__main__":
    unittest.main()
