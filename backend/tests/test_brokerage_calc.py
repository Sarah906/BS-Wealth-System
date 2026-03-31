"""Tests for FIFO brokerage calculator."""
import pytest
from decimal import Decimal
from datetime import date

from app.calculators.brokerage_calc import calculate_fifo_position, TradeRecord


def make_trade(d, txn_type, qty, price, fees=0):
    return TradeRecord(
        date=date.fromisoformat(d),
        quantity=Decimal(str(qty)),
        price=Decimal(str(price)),
        fees=Decimal(str(fees)),
        transaction_type=txn_type,
    )


def test_simple_buy_hold():
    trades = [make_trade("2022-01-10", "BUY", 100, 50.0, fees=25.0)]
    result = calculate_fifo_position(trades, current_price=Decimal("60.0"), symbol="TEST")
    assert result.current_quantity == Decimal("100")
    assert result.realized_pnl == Decimal("0")
    assert result.unrealized_pnl > 0
    assert result.fees_paid == Decimal("25")


def test_fifo_partial_sell():
    trades = [
        make_trade("2022-01-10", "BUY", 100, 50.0, fees=25.0),
        make_trade("2022-01-20", "BUY", 100, 60.0, fees=30.0),
        make_trade("2022-02-01", "SELL", 80, 70.0, fees=28.0),
    ]
    result = calculate_fifo_position(trades, symbol="TEST")
    # After selling 80 from first lot (which had avg cost ~50.25), we expect positive realized P&L
    assert result.realized_pnl > 0
    assert result.current_quantity == Decimal("120")
    assert result.win_count == 1
    assert result.loss_count == 0


def test_sell_at_loss():
    trades = [
        make_trade("2022-01-10", "BUY", 100, 80.0, fees=40.0),
        make_trade("2022-02-01", "SELL", 100, 60.0, fees=30.0),
    ]
    result = calculate_fifo_position(trades, symbol="LOSS")
    assert result.realized_pnl < 0
    assert result.win_count == 0
    assert result.loss_count == 1
    assert result.current_quantity == Decimal("0")


def test_multiple_buys_fifo_order():
    """FIFO: first lot sold first."""
    trades = [
        make_trade("2022-01-01", "BUY", 100, 10.0),  # lot 1: cost ~10
        make_trade("2022-02-01", "BUY", 100, 20.0),  # lot 2: cost ~20
        make_trade("2022-03-01", "SELL", 100, 25.0), # sells lot 1 first
    ]
    result = calculate_fifo_position(trades, symbol="FIFO")
    # lot 1 sold at 25 vs cost 10 → big gain
    assert result.realized_pnl > Decimal("100")
    assert result.current_quantity == Decimal("100")  # lot 2 remains


def test_dividend_tracking():
    trades = [
        make_trade("2022-01-01", "BUY", 100, 10.0),
        TradeRecord(date=date(2022, 6, 1), quantity=Decimal("500"), price=Decimal("0"),
                    fees=Decimal("0"), transaction_type="DIVIDEND"),
    ]
    result = calculate_fifo_position(trades, symbol="DIV")
    assert result.dividend_income == Decimal("500")


def test_win_loss_stats():
    trades = [
        # Trade 1: buy and sell at profit
        make_trade("2022-01-01", "BUY", 100, 10.0),
        make_trade("2022-02-01", "SELL", 100, 15.0),
        # Trade 2: buy and sell at loss
        make_trade("2022-03-01", "BUY", 100, 20.0),
        make_trade("2022-04-01", "SELL", 100, 15.0),
    ]
    result = calculate_fifo_position(trades, symbol="STATS")
    assert result.win_count == 1
    assert result.loss_count == 1
    assert result.win_rate_pct == Decimal("50")


def test_empty_trades():
    result = calculate_fifo_position([], symbol="EMPTY")
    assert result.current_quantity == Decimal("0")
    assert result.realized_pnl == Decimal("0")
    assert result.win_count == 0
