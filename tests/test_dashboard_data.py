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
        dashboard_data.get_queue_data.clear()
        dashboard_data.get_freshness_data.clear()
        dashboard_data.get_pipeline_data.clear()
        dashboard_data.get_scoreboard_data.clear()
        dashboard_data.get_policy_markdown.clear()
        dashboard_data.get_search_results.clear()
        dashboard_data.get_search_stats.clear()
        dashboard_data.get_prebuy_latest.clear()
        dashboard_data.get_prebuy_history.clear()
        dashboard_data.get_sim_runs_data.clear()
        dashboard_data.get_latest_sim.clear()
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

    def test_queue_scoreboard_freshness_and_policy_loaders(self) -> None:
        old_date = (date.today() - timedelta(days=45)).strftime("%Y-%m-%d")
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "watchlist",
                    "priority": "high",
                    "last_analysis_date": old_date,
                    "current_verdict": "Watch",
                    "thesis_status": "intact",
                    "next_required_action": "monitor",
                    "tags": ["software", "quality"],
                }
            ]
        )
        self.write_report("week02", "MSFT", old_date, "Watch", 6.8)
        self.write_financials("MSFT")
        (self.root / "INVESTMENT-POLICY.md").write_text("# Policy\n\nStay disciplined.\n")

        queue_df = dashboard_data.get_queue_data(repo_root=str(self.root))
        freshness = dashboard_data.get_freshness_data(repo_root=str(self.root))
        scoreboard = dashboard_data.get_scoreboard_data(repo_root=str(self.root))
        policy = dashboard_data.get_policy_markdown(repo_root=str(self.root))

        self.assertEqual(queue_df.iloc[0]["freshness_status"], "stale")
        self.assertTrue(queue_df.iloc[0]["has_financials"])
        self.assertEqual(freshness["MSFT"]["status"], "stale")
        self.assertEqual(scoreboard.iloc[0]["ticker"], "MSFT")
        self.assertEqual(scoreboard.iloc[0]["verdict"], "Watch")
        self.assertIn("Stay disciplined", policy)

    def test_pipeline_and_search_loaders(self) -> None:
        self.write_queue(
            [
                {
                    "ticker": "MSFT",
                    "company": "Microsoft Corp.",
                    "current_state": "deep_research",
                    "priority": "high",
                    "last_analysis_date": "2026-03-03",
                    "current_verdict": "Own",
                    "thesis_status": "intact",
                    "next_required_action": "monitor",
                }
            ]
        )
        self.write_report("week01", "MSFT", "2026-03-03", "Own", 8.2)
        self.write_scan_meta("week01")
        self.write_triage("week01")

        pipeline = dashboard_data.get_pipeline_data(repo_root=str(self.root))
        summary = dashboard_data.rebuild_search(repo_root=str(self.root))
        results = dashboard_data.get_search_results("Durable", repo_root=str(self.root))

        self.assertEqual(pipeline["scan"]["total_candidates"], 25)
        self.assertEqual(pipeline["triage"]["b2"]["deep_dive"], 1)
        self.assertGreater(summary["indexed"], 0)
        self.assertTrue(any(item["ticker"] == "MSFT" for item in results))

    def test_dashboard_modules_import_cleanly(self) -> None:
        import dashboard.app  # noqa: F401

        repo_root = Path(__file__).resolve().parent.parent
        for page_path in [
            repo_root / "dashboard" / "pages" / "1_Portfolio.py",
            repo_root / "dashboard" / "pages" / "2_Performance.py",
            repo_root / "dashboard" / "pages" / "3_Research.py",
            repo_root / "dashboard" / "pages" / "4_PreBuy.py",
            repo_root / "dashboard" / "pages" / "5_Simulator.py",
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

    def write_financials(self, ticker: str) -> None:
        context_dir = self.root / "context" / ticker
        context_dir.mkdir(parents=True, exist_ok=True)
        (context_dir / "financials.md").write_text(f"# {ticker} financials\n\nHealthy.\n")

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
                "management": 8,
                "business_economics": 8,
                "balance_sheet": 9,
                "valuation": 6,
                "margin_of_safety": 6,
                "temperament": 7,
            },
            "key_strengths": ["Durable moat"],
            "key_risks": ["Valuation risk"],
            "red_flags": [],
            "buy_triggers": ["Price breaks lower"],
            "sell_triggers": [],
            "valuation_summary": "",
            "source_summary": "",
            "change_notes": "",
            "mos_at_analysis": 12.5,
            "iv_conservative": 280,
            "iv_base": 330,
            "iv_bull": 390,
        }
        (report_dir / "FINAL-REPORT.json").write_text(json.dumps(report, indent=2))
        (report_dir / "FINAL-REPORT.md").write_text(f"# {ticker}\n\nDurable moat and strong unit economics.\n")

    def write_scan_meta(self, week: str) -> None:
        scan_dir = self.root / "runs" / week / "scan"
        scan_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "scan_date": "2026-03-13",
            "universe_date": "2026-03-13",
            "total_candidates": 25,
            "counts_by_bucket": {"tracked": 10, "seed": 8, "post_earnings": 7},
            "counts_by_sector": {"Technology": 12, "Healthcare": 7, "Financials": 6},
            "triage_yes_count": 8,
            "triage_maybe_count": 5,
            "triage_no_count": 12,
        }
        (scan_dir / "scan-meta.json").write_text(json.dumps(payload, indent=2))

    def write_triage(self, week: str) -> None:
        triage_dir = self.root / "runs" / week / "triage"
        triage_dir.mkdir(parents=True, exist_ok=True)
        triage = [
            {
                "ticker": "MSFT",
                "company": "Microsoft Corp.",
                "next_action": "deep_dive",
                "reason_for_action": "High quality and worth a full write-up.",
            }
        ]
        b1_results = [
            {"ticker": "MSFT", "company": "Microsoft Corp.", "b1_verdict": "advance"},
            {"ticker": "META", "company": "Meta Platforms", "b1_verdict": "reject"},
        ]
        (triage_dir / "triage.json").write_text(json.dumps(triage, indent=2))
        (triage_dir / "b1-results.json").write_text(json.dumps(b1_results, indent=2))
        (triage_dir / "triage.md").write_text("# Triage\n\nMSFT deserves a deep dive.\n")


if __name__ == "__main__":
    unittest.main()
