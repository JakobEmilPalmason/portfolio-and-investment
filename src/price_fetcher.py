"""
Price fetcher with SQLite caching and two-provider fallback chain (yfinance -> Tiingo).

All financial values returned as Decimal, never float.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

import pandas as pd
import yfinance as yf

from src.database import Database

logger = logging.getLogger(__name__)


class PriceNotAvailableError(Exception):
    """Raised when no provider can return a price for the given ticker and date."""

    def __init__(self, ticker: str, price_date: str, reason: str = ""):
        self.ticker = ticker
        self.price_date = price_date
        super().__init__(f"Price not available for {ticker} on {price_date}. {reason}")


# Known ticker differences between Yahoo Finance and Tiingo
YAHOO_TO_TIINGO: dict[str, str] = {
    "BRK-B": "brk.b",
    "BRK-A": "brk.a",
}


class PriceFetcher:
    def __init__(
        self,
        db: Database,
        tiingo_key: str | None = None,
        cache_ttl_hours: int = 4,
    ):
        self.db = db
        self.tiingo_key = tiingo_key or os.environ.get("TIINGO_API_KEY")
        self.cache_ttl_hours = cache_ttl_hours
        self._provider_failures: dict[str, int] = {}  # provider -> consecutive failure count
        self._provider_backoff_until: dict[str, float] = {}  # provider -> epoch time

    def get_latest_price(self, ticker: str) -> Decimal:
        """
        Returns the most recent available close price.
        Uses last trading day (handles weekends: Friday close on Saturday/Sunday).
        Checks cache first. Falls through provider chain on miss.
        Raises PriceNotAvailableError if all providers fail.
        """
        price_date = self._last_trading_day()
        return self.get_price_on_date(ticker, price_date)

    def get_price_on_date(self, ticker: str, price_date: str) -> Decimal:
        """
        Returns close price for a specific YYYY-MM-DD date.
        Cache hit returns immediately.
        Cache miss fetches from provider chain, caches result, returns price.
        Raises PriceNotAvailableError if all providers fail.
        """
        # 1. Check cache
        cached = self.db.get_cached_price(ticker, price_date)
        if cached is not None:
            return cached

        # 2. Try provider chain
        price = self._fetch_with_fallback(ticker, price_date, price_date)
        if price is None:
            raise PriceNotAvailableError(ticker, price_date, "All providers exhausted.")

        self.db.upsert_price_cache(ticker, price_date, price, "fetched")
        return price

    def get_history(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Returns DataFrame with columns: date (str YYYY-MM-DD), close (Decimal).
        Fills from cache where available, fetches only uncached dates from provider.
        Does not raise if some dates are missing (non-trading days).
        Raises PriceNotAvailableError only if the entire range fails.
        """
        # Collect cached prices
        rows: list[dict] = []
        current = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        uncached_start: Optional[str] = None
        uncached_end: Optional[str] = None

        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            if self._is_trading_day(date_str):
                cached = self.db.get_cached_price(ticker, date_str)
                if cached is not None:
                    rows.append({"date": date_str, "close": cached})
                else:
                    if uncached_start is None:
                        uncached_start = date_str
                    uncached_end = date_str
            current += timedelta(days=1)

        # Fetch uncached range if needed
        if uncached_start is not None and uncached_end is not None:
            fetched_df = self._fetch_history_from_providers(
                ticker, uncached_start, uncached_end
            )
            if fetched_df is not None and not fetched_df.empty:
                for _, row in fetched_df.iterrows():
                    price = Decimal(str(row["close"]))
                    self.db.upsert_price_cache(ticker, row["date"], price, "fetched")
                    rows.append({"date": row["date"], "close": price})

        if not rows:
            raise PriceNotAvailableError(
                ticker, f"{start} to {end}", "No data from any provider for range."
            )

        df = pd.DataFrame(rows)
        del rows  # free list immediately — DataFrame owns the data now
        df = df.sort_values("date").drop_duplicates(subset="date").reset_index(drop=True)
        return df

    def _fetch_history_from_providers(
        self, ticker: str, start: str, end: str
    ) -> Optional[pd.DataFrame]:
        """Tries yfinance then Tiingo for a date range. Returns DataFrame or None."""
        if not self._is_provider_backed_off("yfinance"):
            try:
                df = self._fetch_yfinance(ticker, start, end)
                if not df.empty:
                    self._reset_provider_failures("yfinance")
                    return df
            except Exception as e:
                logger.warning("yfinance failed for %s history: %s", ticker, e)
                self._record_provider_failure("yfinance")

        if self.tiingo_key and not self._is_provider_backed_off("tiingo"):
            try:
                df = self._fetch_tiingo(ticker, start, end)
                if not df.empty:
                    self._reset_provider_failures("tiingo")
                    return df
            except Exception as e:
                logger.warning("Tiingo failed for %s history: %s", ticker, e)
                self._record_provider_failure("tiingo")

        return None

    def _fetch_with_fallback(
        self, ticker: str, start: str, end: str
    ) -> Decimal | None:
        """
        Tries yfinance then Tiingo. Returns a single close price Decimal or None.
        For a single date, start == end.
        """
        # Try yfinance
        if not self._is_provider_backed_off("yfinance"):
            try:
                df = self._fetch_yfinance(ticker, start, end)
                if not df.empty:
                    self._reset_provider_failures("yfinance")
                    return Decimal(str(df["close"].iloc[-1]))
            except Exception as e:
                logger.warning("yfinance failed for %s: %s", ticker, e)
                self._record_provider_failure("yfinance")

        # Try Tiingo
        if self.tiingo_key and not self._is_provider_backed_off("tiingo"):
            try:
                df = self._fetch_tiingo(ticker, start, end)
                if not df.empty:
                    self._reset_provider_failures("tiingo")
                    return Decimal(str(df["close"].iloc[-1]))
            except Exception as e:
                logger.warning("Tiingo failed for %s: %s", ticker, e)
                self._record_provider_failure("tiingo")

        return None

    def _fetch_yfinance(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetches OHLCV from yfinance with 3 retries and exponential backoff.
        Returns DataFrame with columns: date (str), close (float).
        end date is inclusive -- add one day before passing to yfinance (it uses exclusive end).
        Raises on final failure after all retries.
        """
        end_exclusive = (
            datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        def _attempt() -> pd.DataFrame:
            ticker_obj = yf.Ticker(ticker)
            raw = ticker_obj.history(start=start, end=end_exclusive, auto_adjust=True)
            if raw.empty:
                raise ValueError(f"yfinance returned empty DataFrame for {ticker}")
            raw = raw.reset_index()
            result = pd.DataFrame({
                "date": raw["Date"].dt.strftime("%Y-%m-%d"),
                "close": raw["Close"],
            })
            del raw  # free full OHLCV DataFrame immediately
            return result

        return self._retry(_attempt, max_attempts=3, backoff_base=0.5)

    def _fetch_tiingo(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetches EOD data from Tiingo REST API using requests (not the tiingo package).
        Maps ticker via YAHOO_TO_TIINGO before calling.
        Returns DataFrame with columns: date (str), close (float).
        Raises on failure.
        """
        import requests

        tiingo_ticker = YAHOO_TO_TIINGO.get(ticker, ticker).lower()
        url = (
            f"https://api.tiingo.com/tiingo/daily/{tiingo_ticker}/prices"
            f"?startDate={start}&endDate={end}&token={self.tiingo_key}"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError(f"Tiingo returned empty data for {tiingo_ticker}")
        rows = [{"date": row["date"][:10], "close": row["adjClose"]} for row in data]
        return pd.DataFrame(rows)

    def _retry(self, fn, max_attempts: int = 3, backoff_base: float = 0.5):
        """
        Calls fn() up to max_attempts times with exponential backoff.
        Raises the last exception if all attempts fail.
        Backoff: 0.5s, 1s, 2s (base * 2^attempt).
        """
        last_exc = None
        for attempt in range(max_attempts):
            try:
                return fn()
            except Exception as e:
                last_exc = e
                if attempt < max_attempts - 1:
                    time.sleep(backoff_base * (2 ** attempt))
        raise last_exc

    def _is_trading_day(self, date_str: str) -> bool:
        """Returns False for weekends. Does not account for holidays."""
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return d.weekday() < 5  # 0=Monday, 4=Friday

    def _last_trading_day(self) -> str:
        """
        Returns today's date if it's a weekday, otherwise the most recent Friday.
        Does not account for public holidays.
        """
        today = date.today()
        if today.weekday() < 5:
            return today.strftime("%Y-%m-%d")
        days_back = today.weekday() - 4  # Saturday=1, Sunday=2
        friday = today - timedelta(days=days_back)
        return friday.strftime("%Y-%m-%d")

    def _record_provider_failure(self, provider: str) -> None:
        self._provider_failures[provider] = self._provider_failures.get(provider, 0) + 1
        if self._provider_failures[provider] >= 3:
            self._provider_backoff_until[provider] = time.time() + 3600  # back off 1 hour
            logger.warning(
                "%s backed off for 1 hour after 3 consecutive failures", provider
            )

    def _reset_provider_failures(self, provider: str) -> None:
        self._provider_failures[provider] = 0
        self._provider_backoff_until.pop(provider, None)

    def _is_provider_backed_off(self, provider: str) -> bool:
        until = self._provider_backoff_until.get(provider, 0)
        return time.time() < until
