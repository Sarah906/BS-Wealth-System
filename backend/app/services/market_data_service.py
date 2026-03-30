"""
Market data abstraction layer.
Provides a clean interface for price and FX data, with pluggable providers.
Add real providers here when API keys are ready.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import date, timedelta
from decimal import Decimal
import random


class PricePoint:
    def __init__(self, date: date, open: float, high: float, low: float, close: float, volume: int = 0):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


class FXRate:
    def __init__(self, date: date, from_currency: str, to_currency: str, rate: float):
        self.date = date
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.rate = rate


class PriceProvider(ABC):
    """Abstract interface for price data providers."""

    @abstractmethod
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Return latest available closing price."""

    @abstractmethod
    def get_historical_prices(self, symbol: str, start: date, end: date) -> List[PricePoint]:
        """Return daily OHLCV data for a given date range."""


class FXProvider(ABC):
    """Abstract interface for FX rate providers."""

    @abstractmethod
    def get_rate(self, from_currency: str, to_currency: str, on_date: date) -> Optional[float]:
        """Return FX rate for a given currency pair and date."""

    @abstractmethod
    def get_latest_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Return the most recent available FX rate."""


# ─── Mock Providers (used in development/testing) ───────────────────────────

class MockPriceProvider(PriceProvider):
    """
    Generates deterministic mock price history.
    Used for development and demo purposes until real providers are wired in.
    """

    BASE_PRICES = {
        "1120": 95.0,   # Al Rajhi Bank
        "2222": 28.0,   # Aramco
        "1010": 52.0,   # Riyad Bank
        "2010": 40.0,   # SABIC
        "4030": 120.0,  # Dar Al Arkan
        "4240": 35.0,   # Emaar Economic City
        "AAPL": 170.0,
        "MSFT": 380.0,
        "NVDA": 850.0,
        "AMZN": 185.0,
    }

    def get_latest_price(self, symbol: str) -> Optional[float]:
        base = self.BASE_PRICES.get(symbol, 50.0)
        # Add small random noise for realism
        return round(base * (1 + random.uniform(-0.02, 0.02)), 2)

    def get_historical_prices(self, symbol: str, start: date, end: date) -> List[PricePoint]:
        base = self.BASE_PRICES.get(symbol, 50.0)
        points = []
        current = start
        price = base * 0.7  # start lower to simulate growth
        while current <= end:
            # Simple random walk
            change = random.uniform(-0.015, 0.018)
            price = max(price * (1 + change), 1.0)
            points.append(PricePoint(
                date=current,
                open=round(price * random.uniform(0.995, 1.0), 2),
                high=round(price * random.uniform(1.0, 1.02), 2),
                low=round(price * random.uniform(0.98, 1.0), 2),
                close=round(price, 2),
                volume=random.randint(100_000, 5_000_000),
            ))
            current += timedelta(days=1)
        return points


class MockFXProvider(FXProvider):
    """Mock FX provider with stable SAR/USD pegged rate and other common pairs."""

    RATES = {
        ("USD", "SAR"): 3.75,
        ("SAR", "USD"): 1 / 3.75,
        ("EUR", "SAR"): 4.05,
        ("SAR", "EUR"): 1 / 4.05,
        ("GBP", "SAR"): 4.72,
        ("SAR", "GBP"): 1 / 4.72,
        ("USD", "EUR"): 0.92,
        ("EUR", "USD"): 1 / 0.92,
    }

    def get_rate(self, from_currency: str, to_currency: str, on_date: date) -> Optional[float]:
        if from_currency == to_currency:
            return 1.0
        return self.RATES.get((from_currency, to_currency))

    def get_latest_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        return self.get_rate(from_currency, to_currency, date.today())


# ─── Provider configuration ──────────────────────────────────────────────────
# To add a real provider: implement PriceProvider or FXProvider, then swap here.

class MarketDataService:
    """
    Central service that coordinates price and FX providers.
    Future: configure providers based on asset country/exchange.
    """

    def __init__(self):
        # Replace with real providers via config when keys are available
        self._saudi_price_provider: PriceProvider = MockPriceProvider()
        self._us_price_provider: PriceProvider = MockPriceProvider()
        self._fx_provider: FXProvider = MockFXProvider()

    def get_price(self, symbol: str, exchange: Optional[str] = None) -> Optional[float]:
        return self._saudi_price_provider.get_latest_price(symbol)

    def get_history(self, symbol: str, start: date, end: date) -> List[PricePoint]:
        return self._saudi_price_provider.get_historical_prices(symbol, start, end)

    def get_fx_rate(self, from_currency: str, to_currency: str, on_date: Optional[date] = None) -> Optional[float]:
        d = on_date or date.today()
        return self._fx_provider.get_rate(from_currency, to_currency, d)


market_data_service = MarketDataService()
