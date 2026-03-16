import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

import src.portfolio_engine as portfolio_engine_module
import src.trade_executor as trade_executor_module
from src.database import Database
from src.portfolio_engine import PortfolioEngine
from src.trade_executor import TradeExecutor


class TradeExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "runs" / "week01" / "reports").mkdir(parents=True, exist_ok=True)
        (self.root / "queue").mkdir(parents=True, exist_ok=True)
        (self.root / "queue" / "queue.json").write_text("[]")

        self.db = Database(":memory:")
        self.db.connect()
        self.db.init_db()
        self.db.set_initial_capital(Decimal("100000"), "2026-03-16")
        self.engine = PortfolioEngine(self.db)

        self.patches = [
            mock.patch.object(trade_executor_module, "REPO_ROOT", self.root),
            mock.patch.object(trade_executor_module, "RUNS_DIR", self.root / "runs"),
            mock.patch.object(portfolio_engine_module, "REPO_ROOT", self.root),
            mock.patch.object(portfolio_engine_module, "RUNS_DIR", self.root / "runs"),
            mock.patch.object(
                portfolio_engine_module,
                "QUEUE_FILE",
                self.root / "queue" / "queue.json",
            ),
        ]
        for patcher in self.patches:
            patcher.start()
            self.addCleanup(patcher.stop)

        self.executor = TradeExecutor(self.engine, self.db)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_execute_buy_proposal_marks_it_executed(self) -> None:
        self.write_report("MSFT", verdict="Own")
        proposal_id = self.db.insert_proposal(
            {
                "created_at": "2026-03-16T00:00:00Z",
                "run_id": "week01",
                "ticker": "MSFT",
                "proposed_action": "BUY",
                "proposed_shares": Decimal("30"),
                "proposed_price": Decimal("100"),
                "proposed_value": Decimal("3000"),
                "target_weight_pct": Decimal("3.0"),
                "rationale": "Open starter position",
                "sizing_method": "initial_3pct",
                "rule_checks_json": [],
                "all_rules_passed": 1,
                "status": "PENDING",
            }
        )

        result = self.executor.execute_proposal(proposal_id)

        stored = self.db.get_proposal(proposal_id)
        self.assertEqual(result["ticker"], "MSFT")
        self.assertEqual(stored["status"], "EXECUTED")
        self.assertIsNotNone(stored["transaction_id"])
        self.assertIsNotNone(self.db.get_position("MSFT"))

    def test_reject_proposal_updates_status_and_note(self) -> None:
        proposal_id = self.db.insert_proposal(
            {
                "created_at": "2026-03-16T00:00:00Z",
                "run_id": "week01",
                "ticker": "MSFT",
                "proposed_action": "BUY",
                "proposed_shares": Decimal("30"),
                "proposed_price": Decimal("100"),
                "proposed_value": Decimal("3000"),
                "target_weight_pct": Decimal("3.0"),
                "rationale": "Open starter position",
                "sizing_method": "initial_3pct",
                "rule_checks_json": [],
                "all_rules_passed": 1,
                "status": "PENDING",
            }
        )

        self.executor.reject_proposal(proposal_id, "Need more conviction.")

        stored = self.db.get_proposal(proposal_id)
        self.assertEqual(stored["status"], "REJECTED")
        self.assertEqual(stored["review_note"], "Need more conviction.")
        self.assertIsNotNone(stored["reviewed_at"])

    def test_execute_failure_leaves_proposal_pending(self) -> None:
        proposal_id = self.db.insert_proposal(
            {
                "created_at": "2026-03-16T00:00:00Z",
                "run_id": "week01",
                "ticker": "MSFT",
                "proposed_action": "SELL",
                "proposed_shares": Decimal("10"),
                "proposed_price": Decimal("100"),
                "proposed_value": Decimal("1000"),
                "target_weight_pct": Decimal("0"),
                "rationale": "Exit position",
                "sizing_method": "full_exit",
                "rule_checks_json": [],
                "all_rules_passed": 1,
                "status": "PENDING",
            }
        )

        with self.assertRaises(ValueError):
            self.executor.execute_proposal(proposal_id)

        stored = self.db.get_proposal(proposal_id)
        self.assertEqual(stored["status"], "PENDING")
        self.assertIsNone(stored["transaction_id"])

    def write_report(self, ticker: str, verdict: str) -> None:
        report_dir = self.root / "runs" / "week01" / "reports" / ticker
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "ticker": ticker,
            "company": "Microsoft Corp.",
            "analysis_date": "2026-03-16",
            "verdict": verdict,
            "average_score": 8.1 if verdict == "Own" else 5.0,
            "umbrella_scores": {"margin_of_safety": 6},
            "key_strengths": [],
            "key_risks": [],
            "red_flags": [],
            "buy_triggers": [],
            "sell_triggers": [],
            "valuation_summary": "",
            "source_summary": "",
            "confidence": "high",
            "change_notes": "",
        }
        (report_dir / "FINAL-REPORT.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    unittest.main()
