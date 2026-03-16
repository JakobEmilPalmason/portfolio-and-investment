import importlib.util
import json
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from dashboard import data as dashboard_data
from src.database import Database
from src.portfolio_engine import PortfolioEngine


class DashboardDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.db_path = self.root / "portfolio.db"
        self.db = Database(str(self.db_path))
        self.db.connect()
        self.db.init_db()
        self.engine = PortfolioEngine(self.db)

    def tearDown(self) -> None:
        dashboard_data.get_portfolio_data.clear()
        dashboard_data.get_performance_data.clear()
        dashboard_data.get_research_catalog.clear()
        dashboard_data.get_research_detail.clear()
        self.db.__exit__(None, None, None)
        self.tempdir.cleanup()

    def test_portfolio_data_uses_cached_prices_and_cost_basis_fallback(self) -> None:
        self.db.set_initial_capital(Decimal("100000"), "2026-03-01")
        self.engine.execute_buy(
            ticker="ALPHA",
            side="LONG",
            price=Decimal("100"),
            shares=Decimal("10"),
            iv=None,
            reason="seed",
            date="2026-03-01",
            skip_policy=True,
        )
        self.engine.execute_buy(
            ticker="BETA",
            side="LONG",
            price=Decimal("200"),
            shares=Decimal("5"),
            iv=None,
            reason="seed",
            date="2026-03-01",
            skip_policy=True,
        )
        self.db.upsert_price_cache("ALPHA", "2026-03-02", Decimal("120"), "test")

        payload = dashboard_data.get_portfolio_data(db_path=str(self.db_path))
        positions = payload["positions"].set_index("ticker")

        self.assertEqual(payload["price_fallbacks"], ["BETA"])
        self.assertAlmostEqual(payload["summary"]["total_value"], 100200.0)
        self.assertAlmostEqual(positions.loc["ALPHA", "current_price"], 120.0)
        self.assertAlmostEqual(positions.loc["BETA", "current_price"], 200.0)
        self.assertAlmostEqual(positions.loc["ALPHA", "unrealized_pnl"], 200.0)
        self.assertAlmostEqual(positions.loc["BETA", "unrealized_pnl"], 0.0)

    def test_portfolio_data_exposes_policy_flags_for_overweight_positions(self) -> None:
        self.db.set_initial_capital(Decimal("1000"), "2026-03-01")
        self.engine.execute_buy(
            ticker="BIG",
            side="LONG",
            price=Decimal("100"),
            shares=Decimal("10"),
            iv=None,
            reason="seed",
            date="2026-03-01",
            skip_policy=True,
        )

        payload = dashboard_data.get_portfolio_data(db_path=str(self.db_path))

        self.assertEqual(len(payload["policy_flags"]), 1)
        self.assertEqual(payload["policy_flags"][0]["ticker"], "BIG")
        self.assertEqual(payload["policy_flags"][0]["flag"], "overweight:100.0%")

    def test_performance_data_builds_curve_and_monthly_heatmap(self) -> None:
        total_value = Decimal("100000")
        benchmark_value = Decimal("400")
        start_date = date(2026, 1, 1)
        for offset in range(35):
            snapshot_date = (start_date + timedelta(days=offset)).strftime("%Y-%m-%d")
            total_value *= Decimal("1.001")
            benchmark_value *= Decimal("1.0005")
            self.db.conn.execute(
                """INSERT INTO portfolio_snapshots
                   (snapshot_date, total_value, cash, positions_value, num_positions,
                    daily_return, cumulative_return, benchmark_ticker, benchmark_value,
                    benchmark_daily_return, excess_return, top_holdings_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    snapshot_date,
                    float(total_value),
                    50000.0,
                    float(total_value - Decimal("50000")),
                    3,
                    0.001,
                    float((total_value / Decimal("100000")) - Decimal("1")),
                    "SPY",
                    float(benchmark_value),
                    0.0005,
                    0.0005,
                    "[]",
                ),
            )
        self.db.conn.commit()

        payload = dashboard_data.get_performance_data(db_path=str(self.db_path))

        self.assertEqual(payload["snapshot_count"], 35)
        self.assertEqual(payload["returns_count"], 35)
        self.assertFalse(payload["equity_curve"].empty)
        self.assertTrue(payload["heatmap_ready"])
        self.assertIn("cagr", payload["summary"])

    def test_research_detail_prefers_latest_report_and_loads_queue_state(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "monitor_only",
                    "thesis_status": "intact",
                    "next_required_action": "monitor",
                }
            ]
        )
        self.write_report("week01", "MSFT", "2026-03-01", "Watch", 6.5)
        self.write_report("week02", "MSFT", "2026-03-03", "Own", 8.2)

        catalog = dashboard_data.get_research_catalog(repo_root=str(self.root))
        detail = dashboard_data.get_research_detail("MSFT", repo_root=str(self.root))

        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog[0]["analysis_date"], "2026-03-03")
        self.assertEqual(detail["report"]["verdict"], "Own")
        self.assertEqual(detail["queue"]["current_state"], "monitor_only")
        self.assertTrue(detail["md_path"].endswith("FINAL-REPORT.md"))
        self.assertFalse(detail["scores"].empty)

    def test_dashboard_modules_import_cleanly(self) -> None:
        import dashboard.app  # noqa: F401

        repo_root = Path(__file__).resolve().parent.parent
        for page_path in [
            repo_root / "dashboard" / "pages" / "1_Portfolio.py",
            repo_root / "dashboard" / "pages" / "2_Performance.py",
            repo_root / "dashboard" / "pages" / "3_Research.py",
        ]:
            spec = importlib.util.spec_from_file_location(page_path.stem, page_path)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            self.assertTrue(hasattr(module, "main"))

    def write_queue(self, entries: list[dict]) -> None:
        queue_dir = self.root / "queue"
        queue_dir.mkdir(parents=True, exist_ok=True)
        (queue_dir / "queue.json").write_text(json.dumps(entries, indent=2))

    def write_report(
        self,
        week: str,
        ticker: str,
        analysis_date: str,
        verdict: str,
        average_score: float,
    ) -> None:
        report_dir = self.root / "runs" / week / "reports" / ticker
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "ticker": ticker,
            "company": "Microsoft Corp.",
            "analysis_date": analysis_date,
            "verdict": verdict,
            "average_score": average_score,
            "confidence": "high",
            "umbrella_scores": {
                "circle_of_competence": 8,
                "competitive_advantage": 9,
            },
            "key_strengths": ["Durable moat"],
            "key_risks": ["Valuation risk"],
            "red_flags": [],
            "buy_triggers": [],
            "sell_triggers": [],
            "valuation_summary": "",
            "source_summary": "",
            "change_notes": "",
        }
        (report_dir / "FINAL-REPORT.json").write_text(json.dumps(report, indent=2))
        (report_dir / "FINAL-REPORT.md").write_text(f"# {ticker}\n\nLatest report.\n")


if __name__ == "__main__":
    unittest.main()
