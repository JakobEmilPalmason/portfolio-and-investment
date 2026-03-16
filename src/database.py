"""
SQLite database layer for the paper trading system.

Converts between Decimal (Python) and REAL (SQLite). All writes use
transactions so failures roll back atomically. JSON fields are
serialized/deserialized internally.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from decimal import Decimal
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1
REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "db" / "schema.sql"

# JSON columns that get auto-serialized/deserialized
_JSON_COLUMNS = frozenset({
    "rule_checks_json",
    "verdicts_json",
    "top_holdings_json",
})


class DuplicateEntryError(Exception):
    """Raised on UNIQUE constraint violation."""

    def __init__(self, table: str, ticker: str = "", message: str = ""):
        self.table = table
        self.ticker = ticker
        detail = f" ticker={ticker}" if ticker else ""
        super().__init__(message or f"Duplicate entry in {table}{detail}")


def _dec(value) -> Optional[Decimal]:
    """Convert a SQLite REAL (or None) to Decimal."""
    if value is None:
        return None
    return Decimal(str(value))


def _float(value) -> Optional[float]:
    """Convert a Decimal (or None) to float for SQLite storage."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, deserializing JSON columns."""
    d = dict(row)
    for col in _JSON_COLUMNS:
        if col in d and d[col] is not None:
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


def _decimal_fields_from_dict(d: dict) -> dict:
    """Convert Decimal values to float and serialize JSON columns for storage."""
    out = {}
    for k, v in d.items():
        if k in _JSON_COLUMNS and v is not None and not isinstance(v, str):
            out[k] = json.dumps(v)
        elif isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out


class Database:
    """SQLite wrapper for the paper trading portfolio system."""

    def __init__(self, db_path: str = "db/portfolio.db"):
        if db_path == ":memory:":
            self.db_path = db_path
        else:
            self.db_path = str(REPO_ROOT / db_path) if not Path(db_path).is_absolute() else db_path
        self._conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.close()
            self._conn = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    @property
    def conn(self) -> sqlite3.Connection:
        return self.connect()

    def init_db(self) -> None:
        """Run schema.sql and insert initial schema_version."""
        if self.db_path == ":memory:":
            schema_sql = SCHEMA_PATH.read_text()
        else:
            schema_sql = SCHEMA_PATH.read_text()
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn.executescript(schema_sql)
        # Insert version if not already present
        existing = self.conn.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if existing is None:
            self.conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,),
            )
            self.conn.commit()
        logger.info("Database initialized at %s (schema v%d)", self.db_path, SCHEMA_VERSION)

    def migrate(self) -> None:
        """Check schema_version and apply migrations. No-op if current."""
        row = self.conn.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if row is None:
            self.init_db()
            return
        current = row["version"]
        if current >= SCHEMA_VERSION:
            logger.debug("Schema is current (v%d)", current)
            return
        # Future migrations would go here
        logger.info("Migrated from v%d to v%d", current, SCHEMA_VERSION)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_portfolio_cash(self) -> Decimal:
        """Derive cash from transactions. INIT sets capital; BUY subtracts; SELL/TRIM adds."""
        row = self.conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN action = 'INIT' THEN net_value ELSE 0 END), 0)
                - COALESCE(SUM(CASE WHEN action = 'BUY' THEN net_value ELSE 0 END), 0)
                + COALESCE(SUM(CASE WHEN action IN ('SELL', 'TRIM') THEN net_value ELSE 0 END), 0)
                + COALESCE(SUM(CASE WHEN action = 'DIVIDEND' THEN net_value ELSE 0 END), 0)
                AS cash
            FROM transactions
        """).fetchone()
        return Decimal(str(row["cash"])) if row and row["cash"] is not None else Decimal("0")

    def get_open_positions(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM positions WHERE status = 'OPEN' ORDER BY ticker"
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_position(self, ticker: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM positions WHERE ticker = ? AND status = 'OPEN'",
            (ticker,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_open_lots(self, ticker: str) -> list[dict]:
        """Get open lots for a ticker, ordered by purchase_date ASC (FIFO)."""
        rows = self.conn.execute(
            "SELECT * FROM lots WHERE ticker = ? AND shares > 0 ORDER BY purchase_date ASC",
            (ticker,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_latest_snapshot(self) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM portfolio_snapshots ORDER BY snapshot_date DESC LIMIT 1"
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_snapshots_range(self, start: str, end: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM portfolio_snapshots WHERE snapshot_date BETWEEN ? AND ? ORDER BY snapshot_date",
            (start, end),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_transactions(self, ticker: str = None, limit: int = 50) -> list[dict]:
        if ticker:
            rows = self.conn.execute(
                "SELECT * FROM transactions WHERE ticker = ? ORDER BY timestamp DESC LIMIT ?",
                (ticker, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_pending_proposals(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM trade_proposals WHERE status = 'PENDING' ORDER BY created_at",
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_proposal(self, proposal_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM trade_proposals WHERE id = ?",
            (proposal_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_pending_proposal(
        self,
        ticker: str,
        proposed_action: str,
    ) -> Optional[dict]:
        row = self.conn.execute(
            """SELECT * FROM trade_proposals
               WHERE ticker = ? AND proposed_action = ? AND status = 'PENDING'
               ORDER BY created_at DESC
               LIMIT 1""",
            (ticker, proposed_action),
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_cached_price(self, ticker: str, price_date: str) -> Optional[Decimal]:
        row = self.conn.execute(
            "SELECT close_price FROM price_cache WHERE ticker = ? AND price_date = ?",
            (ticker, price_date),
        ).fetchone()
        if row is None:
            return None
        return Decimal(str(row["close_price"]))

    def get_latest_cached_price(self, ticker: str) -> Optional[Decimal]:
        row = self.conn.execute(
            """SELECT close_price
               FROM price_cache
               WHERE ticker = ?
               ORDER BY price_date DESC
               LIMIT 1""",
            (ticker,),
        ).fetchone()
        if row is None or row["close_price"] is None:
            return None
        return Decimal(str(row["close_price"]))

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def insert_transaction(self, tx: dict) -> int:
        """Insert a transaction record. Returns the new row id."""
        tx = _decimal_fields_from_dict(tx)
        try:
            cur = self.conn.execute(
                """INSERT INTO transactions
                   (timestamp, run_id, ticker, action, shares, price,
                    gross_value, fees, net_value, realized_pnl, reason,
                    report_ref, pre_trade_cash, post_trade_cash, position_id)
                   VALUES (:timestamp, :run_id, :ticker, :action, :shares, :price,
                           :gross_value, :fees, :net_value, :realized_pnl, :reason,
                           :report_ref, :pre_trade_cash, :post_trade_cash, :position_id)""",
                tx,
            )
            self.conn.commit()
            logger.debug("Inserted transaction id=%d ticker=%s action=%s", cur.lastrowid, tx.get("ticker"), tx.get("action"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("transactions", tx.get("ticker", ""), str(e)) from e

    def upsert_position(self, position: dict) -> int:
        """Insert or replace a position. Returns the row id."""
        position = _decimal_fields_from_dict(position)
        try:
            cur = self.conn.execute(
                """INSERT INTO positions
                   (ticker, company, sector, side, status, shares,
                    avg_cost_basis, total_cost, realized_pnl,
                    first_entry_date, last_update, entry_report_ref, thesis_summary)
                   VALUES (:ticker, :company, :sector, :side, :status, :shares,
                           :avg_cost_basis, :total_cost, :realized_pnl,
                           :first_entry_date, :last_update, :entry_report_ref, :thesis_summary)
                   ON CONFLICT(ticker, status) DO UPDATE SET
                       company = excluded.company,
                       sector = excluded.sector,
                       side = excluded.side,
                       shares = excluded.shares,
                       avg_cost_basis = excluded.avg_cost_basis,
                       total_cost = excluded.total_cost,
                       realized_pnl = excluded.realized_pnl,
                       last_update = excluded.last_update,
                       entry_report_ref = excluded.entry_report_ref,
                       thesis_summary = excluded.thesis_summary""",
                position,
            )
            self.conn.commit()
            logger.debug("Upserted position ticker=%s id=%d", position.get("ticker"), cur.lastrowid)
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("positions", position.get("ticker", ""), str(e)) from e

    def insert_lot(self, lot: dict) -> int:
        """Insert a new lot. Returns the new row id."""
        lot = _decimal_fields_from_dict(lot)
        try:
            cur = self.conn.execute(
                """INSERT INTO lots
                   (position_id, ticker, shares, cost_per_share, purchase_date, transaction_id)
                   VALUES (:position_id, :ticker, :shares, :cost_per_share, :purchase_date, :transaction_id)""",
                lot,
            )
            self.conn.commit()
            logger.debug("Inserted lot id=%d ticker=%s", cur.lastrowid, lot.get("ticker"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("lots", lot.get("ticker", ""), str(e)) from e

    def update_lot_shares(self, lot_id: int, new_shares: Decimal) -> None:
        """Update remaining shares in a lot."""
        self.conn.execute(
            "UPDATE lots SET shares = ? WHERE id = ?",
            (float(new_shares), lot_id),
        )
        self.conn.commit()

    def close_lot(self, lot_id: int) -> None:
        """Set a lot's shares to 0."""
        self.conn.execute(
            "UPDATE lots SET shares = 0 WHERE id = ?",
            (lot_id,),
        )
        self.conn.commit()

    def insert_snapshot(self, snapshot: dict) -> int:
        """Insert a portfolio snapshot. Returns the new row id."""
        snapshot = _decimal_fields_from_dict(snapshot)
        try:
            cur = self.conn.execute(
                """INSERT INTO portfolio_snapshots
                   (snapshot_date, total_value, cash, positions_value,
                    num_positions, daily_return, cumulative_return,
                    benchmark_ticker, benchmark_value, benchmark_daily_return,
                    excess_return, top_holdings_json)
                   VALUES (:snapshot_date, :total_value, :cash, :positions_value,
                           :num_positions, :daily_return, :cumulative_return,
                           :benchmark_ticker, :benchmark_value, :benchmark_daily_return,
                           :excess_return, :top_holdings_json)""",
                snapshot,
            )
            self.conn.commit()
            logger.debug("Inserted snapshot date=%s", snapshot.get("snapshot_date"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("portfolio_snapshots", "", str(e)) from e

    def insert_proposal(self, proposal: dict) -> int:
        """Insert a trade proposal. Returns the new row id."""
        proposal = _decimal_fields_from_dict(proposal)
        try:
            cur = self.conn.execute(
                """INSERT INTO trade_proposals
                   (created_at, run_id, ticker, proposed_action,
                    proposed_shares, proposed_price, proposed_value,
                    target_weight_pct, rationale, sizing_method,
                    rule_checks_json, all_rules_passed, status)
                   VALUES (:created_at, :run_id, :ticker, :proposed_action,
                           :proposed_shares, :proposed_price, :proposed_value,
                           :target_weight_pct, :rationale, :sizing_method,
                           :rule_checks_json, :all_rules_passed, :status)""",
                proposal,
            )
            self.conn.commit()
            logger.debug("Inserted proposal id=%d ticker=%s", cur.lastrowid, proposal.get("ticker"))
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("trade_proposals", proposal.get("ticker", ""), str(e)) from e

    def update_proposal_status(self, proposal_id: int, status: str, **kwargs) -> None:
        """Update a proposal's status and optional fields (reviewed_at, review_note, executed_at, transaction_id)."""
        sets = ["status = ?"]
        params: list = [status]
        for col in ("reviewed_at", "review_note", "executed_at", "transaction_id"):
            if col in kwargs:
                sets.append(f"{col} = ?")
                val = kwargs[col]
                params.append(float(val) if isinstance(val, Decimal) else val)
        params.append(proposal_id)
        sql = f"UPDATE trade_proposals SET {', '.join(sets)} WHERE id = ?"
        self.conn.execute(sql, params)
        self.conn.commit()

    def upsert_price_cache(self, ticker: str, price_date: str, price: Decimal, source: str) -> None:
        """Insert or update a cached price."""
        self.conn.execute(
            """INSERT INTO price_cache (ticker, price_date, close_price, source, fetched_at)
               VALUES (?, ?, ?, ?, datetime('now'))
               ON CONFLICT(ticker, price_date) DO UPDATE SET
                   close_price = excluded.close_price,
                   source = excluded.source,
                   fetched_at = excluded.fetched_at""",
            (ticker, price_date, float(price), source),
        )
        self.conn.commit()

    def log_research_run(self, run: dict) -> None:
        """Log a research/pipeline run."""
        run = _decimal_fields_from_dict(run)
        try:
            self.conn.execute(
                """INSERT INTO research_runs
                   (run_id, run_date, week_folder, pipeline_stage,
                    input_count, output_count, verdicts_json, status)
                   VALUES (:run_id, :run_date, :week_folder, :pipeline_stage,
                           :input_count, :output_count, :verdicts_json, :status)""",
                run,
            )
            self.conn.commit()
            logger.debug("Logged research run %s", run.get("run_id"))
        except sqlite3.IntegrityError as e:
            raise DuplicateEntryError("research_runs", "", str(e)) from e

    def set_initial_capital(self, amount: Decimal, inception_date: str) -> None:
        """Record the initial capital as an INIT transaction."""
        self.insert_transaction({
            "timestamp": inception_date,
            "run_id": None,
            "ticker": "_PORTFOLIO",
            "action": "INIT",
            "shares": Decimal("0"),
            "price": Decimal("0"),
            "gross_value": amount,
            "fees": Decimal("0"),
            "net_value": amount,
            "realized_pnl": Decimal("0"),
            "reason": f"Portfolio initialized with {amount}",
            "report_ref": None,
            "pre_trade_cash": Decimal("0"),
            "post_trade_cash": amount,
            "position_id": None,
        })
        logger.info("Set initial capital to %s on %s", amount, inception_date)
