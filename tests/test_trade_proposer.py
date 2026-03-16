import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

import src.portfolio_engine as portfolio_engine_module
import src.trade_proposer as trade_proposer_module
from src.database import Database
from src.portfolio_engine import PortfolioEngine
from src.trade_proposer import TradeProposalGenerator


class TradeProposalGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "runs" / "week01" / "reports").mkdir(parents=True, exist_ok=True)
        (self.root / "queue").mkdir(parents=True, exist_ok=True)

        self.db = Database(":memory:")
        self.db.connect()
        self.db.init_db()
        self.db.set_initial_capital(Decimal("100000"), "2026-03-16")
        self.engine = PortfolioEngine(self.db)

        self.patches = [
            mock.patch.object(trade_proposer_module, "REPO_ROOT", self.root),
            mock.patch.object(trade_proposer_module, "RUNS_DIR", self.root / "runs"),
            mock.patch.object(
                trade_proposer_module,
                "QUEUE_FILE",
                self.root / "queue" / "queue.json",
            ),
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

        self.generator = TradeProposalGenerator(self.engine, self.db)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_generate_buy_from_queue_creates_pending_proposal(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "monitor_only",
                    "thesis_status": "intact",
                    "tags": ["technology", "cloud"],
                }
            ]
        )
        self.write_report("MSFT", verdict="Own", iv_conservative=Decimal("130"))
        self.cache_price("MSFT", Decimal("100"))

        proposals = self.generator.generate_from_queue()

        self.assertEqual(len(proposals), 1)
        proposal = proposals[0]
        self.assertEqual(proposal["action"], "BUY")
        self.assertEqual(proposal["proposed_value"], Decimal("3000.00"))
        self.assertTrue(proposal["all_rules_passed"])

        stored = self.db.get_pending_proposals()
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["ticker"], "MSFT")
        self.assertEqual(stored[0]["status"], "PENDING")

    def test_generate_add_requires_numeric_margin_of_safety(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "monitor_only",
                    "thesis_status": "intact",
                    "tags": ["technology", "cloud"],
                }
            ]
        )
        self.write_report("MSFT", verdict="Own", iv_conservative=Decimal("100"))
        self.cache_price("MSFT", Decimal("80"))
        self.engine.execute_buy(
            ticker="MSFT",
            side="LONG",
            price=Decimal("100"),
            shares=Decimal("10"),
            iv=None,
            reason="seed",
            date="2026-03-15",
            skip_policy=True,
        )

        proposals = self.generator.generate_from_queue()

        self.assertEqual(len(proposals), 1)
        proposal = proposals[0]
        self.assertEqual(proposal["action"], "ADD")
        self.assertEqual(proposal["proposed_value"], Decimal("2200.00"))
        self.assertEqual(proposal["target_weight_pct"], Decimal("3.0"))

    def test_generate_add_skips_when_iv_data_is_missing(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "monitor_only",
                    "thesis_status": "intact",
                    "tags": ["technology", "cloud"],
                }
            ]
        )
        self.write_report("MSFT", verdict="Own")
        self.cache_price("MSFT", Decimal("80"))
        self.engine.execute_buy(
            ticker="MSFT",
            side="LONG",
            price=Decimal("100"),
            shares=Decimal("10"),
            iv=None,
            reason="seed",
            date="2026-03-15",
            skip_policy=True,
        )

        proposals = self.generator.generate_from_queue()

        self.assertEqual(proposals, [])
        self.assertEqual(self.db.get_pending_proposals(), [])

    def test_generate_sell_from_owned_state_on_pass_verdict(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "owned",
                    "thesis_status": "intact",
                    "tags": ["technology", "cloud"],
                }
            ]
        )
        self.write_report("MSFT", verdict="Pass")
        self.cache_price("MSFT", Decimal("100"))
        self.engine.execute_buy(
            ticker="MSFT",
            side="LONG",
            price=Decimal("100"),
            shares=Decimal("10"),
            iv=None,
            reason="seed",
            date="2026-03-15",
            skip_policy=True,
        )

        proposals = self.generator.generate_from_queue()

        self.assertEqual(len(proposals), 1)
        proposal = proposals[0]
        self.assertEqual(proposal["action"], "SELL")
        self.assertEqual(proposal["proposed_shares"], Decimal("10.000000"))

    def test_generate_trim_to_five_percent(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "owned",
                    "thesis_status": "intact",
                    "tags": ["technology", "cloud"],
                }
            ]
        )
        self.write_report("MSFT", verdict="Watch")
        self.cache_price("MSFT", Decimal("100"))
        self.engine.execute_buy(
            ticker="MSFT",
            side="LONG",
            price=Decimal("100"),
            shares=Decimal("80"),
            iv=None,
            reason="seed",
            date="2026-03-15",
            skip_policy=True,
        )

        proposals = self.generator.generate_from_queue()

        self.assertEqual(len(proposals), 1)
        proposal = proposals[0]
        self.assertEqual(proposal["action"], "TRIM")
        self.assertEqual(proposal["proposed_value"], Decimal("3000.00"))
        self.assertEqual(proposal["target_weight_pct"], Decimal("5.0"))

    def test_duplicate_pending_proposal_is_skipped(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "monitor_only",
                    "thesis_status": "intact",
                    "tags": ["technology", "cloud"],
                }
            ]
        )
        self.write_report("MSFT", verdict="Own", iv_conservative=Decimal("130"))
        self.cache_price("MSFT", Decimal("100"))

        first = self.generator.generate_from_queue()
        second = self.generator.generate_from_queue()

        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        self.assertEqual(len(self.db.get_pending_proposals()), 1)

    def write_queue(self, entries: list[dict]) -> None:
        path = self.root / "queue" / "queue.json"
        path.write_text(json.dumps(entries, indent=2))

    def write_report(
        self,
        ticker: str,
        verdict: str,
        iv_conservative: Decimal | None = None,
    ) -> None:
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
        if iv_conservative is not None:
            report["iv_conservative"] = float(iv_conservative)
        (report_dir / "FINAL-REPORT.json").write_text(json.dumps(report, indent=2))

    def cache_price(self, ticker: str, price: Decimal) -> None:
        self.db.upsert_price_cache(ticker, "2026-03-16", price, "test")


if __name__ == "__main__":
    unittest.main()
