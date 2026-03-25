"""Eval: arithmetic correctness with real SYK financial data.

Validates that the arithmetic engine produces correct derived metrics
when given real XBRL numbers from SYK's 10-K filing.
"""

import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sec_edgar.arithmetic_engine import validate_formula, execute_formula
from evals.evidence.conftest import GOLDEN_XBRL


class TestDerivedMetrics(unittest.TestCase):
    """Execute real financial formulas through the arithmetic sandbox."""

    def setUp(self):
        self.metrics = GOLDEN_XBRL["metrics"]

    def _run_formula(self, formula: str, inputs: dict) -> float:
        """Validate and execute a formula."""
        validate_formula(formula)
        return execute_formula(formula, inputs)

    def test_gross_margin(self):
        result = self._run_formula(
            "gross_profit / revenue",
            {"gross_profit": self.metrics["gross_profit"], "revenue": self.metrics["revenue"]},
        )
        expected = GOLDEN_XBRL["derived"]["gross_margin"]["expected"]
        tolerance = GOLDEN_XBRL["derived"]["gross_margin"]["tolerance"]
        self.assertAlmostEqual(result, expected, delta=tolerance,
                               msg=f"Gross margin: {result:.4f} vs expected {expected}")

    def test_operating_margin(self):
        result = self._run_formula(
            "operating_income / revenue",
            {"operating_income": self.metrics["operating_income"], "revenue": self.metrics["revenue"]},
        )
        expected = GOLDEN_XBRL["derived"]["operating_margin"]["expected"]
        tolerance = GOLDEN_XBRL["derived"]["operating_margin"]["tolerance"]
        self.assertAlmostEqual(result, expected, delta=tolerance)

    def test_fcf_margin(self):
        result = self._run_formula(
            "free_cash_flow / revenue",
            {"free_cash_flow": self.metrics["free_cash_flow"], "revenue": self.metrics["revenue"]},
        )
        expected = GOLDEN_XBRL["derived"]["fcf_margin"]["expected"]
        tolerance = GOLDEN_XBRL["derived"]["fcf_margin"]["tolerance"]
        self.assertAlmostEqual(result, expected, delta=tolerance)

    def test_interest_coverage(self):
        result = self._run_formula(
            "operating_income / interest_expense",
            {"operating_income": self.metrics["operating_income"], "interest_expense": self.metrics["interest_expense"]},
        )
        expected = GOLDEN_XBRL["derived"]["interest_coverage"]["expected"]
        tolerance = GOLDEN_XBRL["derived"]["interest_coverage"]["tolerance"]
        self.assertAlmostEqual(result, expected, delta=tolerance)

    def test_current_ratio(self):
        result = self._run_formula(
            "current_assets / current_liabilities",
            {"current_assets": self.metrics["current_assets"], "current_liabilities": self.metrics["current_liabilities"]},
        )
        expected = GOLDEN_XBRL["derived"]["current_ratio"]["expected"]
        tolerance = GOLDEN_XBRL["derived"]["current_ratio"]["tolerance"]
        self.assertAlmostEqual(result, expected, delta=tolerance)

    def test_debt_to_assets(self):
        result = self._run_formula(
            "total_liabilities / total_assets",
            {"total_liabilities": self.metrics["total_liabilities"], "total_assets": self.metrics["total_assets"]},
        )
        expected = GOLDEN_XBRL["derived"]["debt_to_assets"]["expected"]
        tolerance = GOLDEN_XBRL["derived"]["debt_to_assets"]["tolerance"]
        self.assertAlmostEqual(result, expected, delta=tolerance)

    def test_all_formulas_are_valid(self):
        """Every formula in the golden XBRL fixture passes AST validation."""
        for name, spec in GOLDEN_XBRL["derived"].items():
            with self.subTest(metric=name):
                validate_formula(spec["formula"])

    def test_result_types_are_float(self):
        """All results from the engine are float."""
        for name, spec in GOLDEN_XBRL["derived"].items():
            # Build inputs from formula variable names
            formula = spec["formula"]
            inputs = {}
            for var in self.metrics:
                if var in formula:
                    inputs[var] = float(self.metrics[var])
            if inputs:
                validate_formula(formula)
                result = execute_formula(formula, inputs)
                self.assertIsInstance(result, float, msg=f"{name} result is not float")


if __name__ == "__main__":
    unittest.main()
