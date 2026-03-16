"""
Pure domain models for the paper trading system.

All arithmetic uses Decimal. No database calls. No I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

D = Decimal

CENT = D("0.01")
SIX_PLACES = D("0.000001")


def round_money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def round_shares(value: Decimal) -> Decimal:
    return value.quantize(SIX_PLACES, rounding=ROUND_HALF_UP)


@dataclass
class Lot:
    lot_id: Optional[int]
    ticker: str
    shares: Decimal
    cost_per_share: Decimal
    purchase_date: str
    transaction_id: Optional[int] = None

    @property
    def total_cost(self) -> Decimal:
        return round_money(self.shares * self.cost_per_share)

    def to_dict(self) -> dict:
        return {
            "lot_id": self.lot_id,
            "ticker": self.ticker,
            "shares": float(self.shares),
            "cost_per_share": float(self.cost_per_share),
            "purchase_date": self.purchase_date,
            "transaction_id": self.transaction_id,
        }


@dataclass
class Position:
    ticker: str
    company: str = ""
    sector: str = ""
    side: str = "LONG"
    status: str = "OPEN"
    lots: list[Lot] = field(default_factory=list)
    realized_pnl: Decimal = D("0")
    entry_report_ref: str = ""
    thesis_summary: str = ""

    @property
    def shares(self) -> Decimal:
        return round_shares(sum(lot.shares for lot in self.lots))

    @property
    def avg_cost_basis(self) -> Decimal:
        total_cost = sum(lot.shares * lot.cost_per_share for lot in self.lots)
        total_shares = self.shares
        if total_shares == 0:
            return D("0")
        return round_money(total_cost / total_shares)

    @property
    def total_cost(self) -> Decimal:
        return round_money(sum(lot.total_cost for lot in self.lots))

    def market_value(self, current_price: Decimal) -> Decimal:
        return round_money(self.shares * current_price)

    def unrealized_pnl(self, current_price: Decimal) -> Decimal:
        return round_money(self.market_value(current_price) - self.total_cost)

    def add_shares(
        self,
        shares: Decimal,
        price: Decimal,
        purchase_date: str,
        transaction_id: int = None,
    ) -> Lot:
        """Create and append a new lot. Returns it."""
        lot = Lot(
            lot_id=None,
            ticker=self.ticker,
            shares=round_shares(shares),
            cost_per_share=round_money(price),
            purchase_date=purchase_date,
            transaction_id=transaction_id,
        )
        self.lots.append(lot)
        return lot

    def remove_shares_fifo(
        self,
        shares_to_sell: Decimal,
        sell_price: Decimal,
    ) -> tuple[Decimal, list[tuple[Lot, Decimal]]]:
        """
        FIFO sell. Returns (realized_pnl, consumed_lots).

        consumed_lots is a list of (lot, shares_consumed_from_that_lot).
        The caller is responsible for persisting changes (updating lot.shares
        or closing the lot). This method does NOT modify self.lots.

        realized_pnl = sum over consumed: shares_consumed * (sell_price - lot.cost_per_share)

        Raises ValueError if shares_to_sell > self.shares.
        Raises ValueError if shares_to_sell <= 0.
        """
        if shares_to_sell <= 0:
            raise ValueError(f"shares_to_sell must be positive, got {shares_to_sell}")
        if shares_to_sell > self.shares:
            raise ValueError(
                f"Cannot sell {shares_to_sell} shares of {self.ticker}; "
                f"only {self.shares} available"
            )

        remaining = round_shares(shares_to_sell)
        realized = D("0")
        consumed: list[tuple[Lot, Decimal]] = []

        for lot in self.lots:
            if remaining <= 0:
                break
            if lot.shares <= 0:
                continue

            take = min(lot.shares, remaining)
            realized += round_money(take * (sell_price - lot.cost_per_share))
            consumed.append((lot, take))
            remaining -= take

        return round_money(realized), consumed

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "company": self.company,
            "sector": self.sector,
            "side": self.side,
            "status": self.status,
            "shares": float(self.shares),
            "avg_cost_basis": float(self.avg_cost_basis),
            "total_cost": float(self.total_cost),
            "realized_pnl": float(self.realized_pnl),
            "entry_report_ref": self.entry_report_ref,
            "thesis_summary": self.thesis_summary,
            "lots": [lot.to_dict() for lot in self.lots],
        }


@dataclass
class Portfolio:
    cash: Decimal
    positions: dict[str, Position] = field(default_factory=dict)
    inception_date: str = ""
    initial_capital: Decimal = D("0")

    def positions_value(self, prices: dict[str, Decimal]) -> Decimal:
        return round_money(
            sum(
                pos.market_value(prices[ticker])
                for ticker, pos in self.positions.items()
                if ticker in prices and pos.status == "OPEN"
            )
        )

    def total_value(self, prices: dict[str, Decimal]) -> Decimal:
        return round_money(self.cash + self.positions_value(prices))

    def get_weight(self, ticker: str, prices: dict[str, Decimal]) -> Decimal:
        tv = self.total_value(prices)
        if tv == 0 or ticker not in self.positions:
            return D("0")
        return round_money(
            self.positions[ticker].market_value(prices[ticker]) / tv * D("100")
        )

    def get_sector_weight(self, sector: str, prices: dict[str, Decimal]) -> Decimal:
        tv = self.total_value(prices)
        if tv == 0:
            return D("0")
        sector_value = sum(
            pos.market_value(prices[ticker])
            for ticker, pos in self.positions.items()
            if pos.sector == sector and ticker in prices and pos.status == "OPEN"
        )
        return round_money(D(str(sector_value)) / tv * D("100"))

    def get_sector_map(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for ticker, pos in self.positions.items():
            if pos.status == "OPEN":
                result.setdefault(pos.sector, []).append(ticker)
        return result

    def open_tickers(self) -> list[str]:
        return [t for t, p in self.positions.items() if p.status == "OPEN"]

    def to_dict(self, prices: dict[str, Decimal]) -> dict:
        return {
            "cash": float(self.cash),
            "initial_capital": float(self.initial_capital),
            "inception_date": self.inception_date,
            "total_value": float(self.total_value(prices)),
            "positions_value": float(self.positions_value(prices)),
            "num_positions": len(self.open_tickers()),
            "positions": {
                ticker: pos.to_dict()
                for ticker, pos in self.positions.items()
                if pos.status == "OPEN"
            },
        }


@dataclass(frozen=True)
class Transaction:
    ticker: str
    action: str
    shares: Decimal
    price: Decimal
    fees: Decimal = D("0")
    reason: str = ""
    report_ref: str = ""
    run_id: str = ""

    @property
    def gross_value(self) -> Decimal:
        return round_money(self.shares * self.price)

    @property
    def net_value(self) -> Decimal:
        return round_money(self.gross_value + self.fees)

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "action": self.action,
            "shares": float(self.shares),
            "price": float(self.price),
            "gross_value": float(self.gross_value),
            "fees": float(self.fees),
            "net_value": float(self.net_value),
            "reason": self.reason,
            "report_ref": self.report_ref,
            "run_id": self.run_id,
        }


@dataclass(frozen=True)
class PortfolioSnapshot:
    snapshot_date: str
    total_value: Decimal
    cash: Decimal
    positions_value: Decimal
    num_positions: int
    daily_return: Optional[Decimal]
    cumulative_return: Optional[Decimal]
    benchmark_ticker: str
    benchmark_value: Optional[Decimal]
    benchmark_daily_return: Optional[Decimal]
    excess_return: Optional[Decimal]
    top_holdings: list[dict]

    def to_dict(self) -> dict:
        return {
            "snapshot_date": self.snapshot_date,
            "total_value": float(self.total_value),
            "cash": float(self.cash),
            "positions_value": float(self.positions_value),
            "num_positions": self.num_positions,
            "daily_return": float(self.daily_return) if self.daily_return is not None else None,
            "cumulative_return": float(self.cumulative_return) if self.cumulative_return is not None else None,
            "benchmark_ticker": self.benchmark_ticker,
            "benchmark_value": float(self.benchmark_value) if self.benchmark_value is not None else None,
            "benchmark_daily_return": float(self.benchmark_daily_return) if self.benchmark_daily_return is not None else None,
            "excess_return": float(self.excess_return) if self.excess_return is not None else None,
            "top_holdings": self.top_holdings,
        }
