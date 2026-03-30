"""
Brokerage account calculations using FIFO cost basis.
Handles: holdings, realized P&L, unrealized P&L, dividends, fees, win/loss stats.
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Tuple
from datetime import date


@dataclass
class TradeRecord:
    date: date
    quantity: Decimal
    price: Decimal
    fees: Decimal
    transaction_type: str  # BUY / SELL


@dataclass
class FifoLot:
    """A single acquired lot in the FIFO queue."""
    date: date
    quantity: Decimal
    cost_per_share: Decimal  # includes proportional fees


@dataclass
class RealizedTrade:
    sell_date: date
    quantity: Decimal
    sell_price: Decimal
    cost_per_share: Decimal
    pnl: Decimal
    pnl_pct: Decimal


@dataclass
class BrokerageResult:
    symbol: str
    current_quantity: Decimal
    avg_cost: Decimal
    cost_basis: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: Decimal
    dividend_income: Decimal
    fees_paid: Decimal
    win_count: int
    loss_count: int
    win_rate_pct: Decimal
    avg_gain_pct: Decimal
    avg_loss_pct: Decimal
    expectancy_pct: Decimal
    realized_trades: List[RealizedTrade]


def _round(val: Decimal, places: int = 4) -> Decimal:
    return val.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


def calculate_fifo_position(
    trades: List[TradeRecord],
    current_price: Optional[Decimal] = None,
    symbol: str = "",
) -> BrokerageResult:
    """
    Calculate position metrics using FIFO cost basis.
    trades must be sorted by date ascending.
    """
    lots: List[FifoLot] = []
    realized_trades: List[RealizedTrade] = []
    dividend_income = Decimal("0")
    fees_paid = Decimal("0")

    for trade in trades:
        fees_paid += trade.fees

        if trade.transaction_type == "BUY":
            # Include fees in cost basis
            cost_per_share = (trade.price * trade.quantity + trade.fees) / trade.quantity
            lots.append(FifoLot(
                date=trade.date,
                quantity=trade.quantity,
                cost_per_share=cost_per_share,
            ))

        elif trade.transaction_type == "SELL":
            qty_to_sell = trade.quantity
            sell_price = trade.price - (trade.fees / trade.quantity if trade.quantity else Decimal("0"))

            while qty_to_sell > 0 and lots:
                lot = lots[0]
                qty_from_lot = min(lot.quantity, qty_to_sell)

                pnl = (sell_price - lot.cost_per_share) * qty_from_lot
                pnl_pct = (
                    _round((sell_price - lot.cost_per_share) / lot.cost_per_share * 100)
                    if lot.cost_per_share != 0 else Decimal("0")
                )

                realized_trades.append(RealizedTrade(
                    sell_date=trade.date,
                    quantity=qty_from_lot,
                    sell_price=sell_price,
                    cost_per_share=lot.cost_per_share,
                    pnl=_round(pnl),
                    pnl_pct=pnl_pct,
                ))

                lot.quantity -= qty_from_lot
                qty_to_sell -= qty_from_lot

                if lot.quantity == 0:
                    lots.pop(0)

        elif trade.transaction_type == "DIVIDEND":
            dividend_income += trade.quantity  # quantity holds the cash amount for dividends

    # Current position metrics
    current_quantity = sum((lot.quantity for lot in lots), Decimal("0"))
    total_cost = sum((lot.quantity * lot.cost_per_share for lot in lots), Decimal("0"))
    avg_cost = (total_cost / current_quantity) if current_quantity > 0 else Decimal("0")

    # Unrealized P&L
    if current_price and current_quantity > 0:
        current_value = current_price * current_quantity
        unrealized_pnl = current_value - total_cost
        unrealized_pnl_pct = _round(unrealized_pnl / total_cost * 100) if total_cost else Decimal("0")
    else:
        unrealized_pnl = Decimal("0")
        unrealized_pnl_pct = Decimal("0")

    # Win/loss stats
    wins = [t for t in realized_trades if t.pnl > 0]
    losses = [t for t in realized_trades if t.pnl <= 0]
    total_trades = len(realized_trades)

    win_count = len(wins)
    loss_count = len(losses)
    win_rate = _round(Decimal(win_count) / Decimal(total_trades) * 100) if total_trades else Decimal("0")

    avg_gain = _round(sum(t.pnl_pct for t in wins) / len(wins)) if wins else Decimal("0")
    avg_loss = _round(sum(t.pnl_pct for t in losses) / len(losses)) if losses else Decimal("0")

    # Expectancy = (WinRate * AvgGain) + (LossRate * AvgLoss)
    win_rate_decimal = win_rate / 100
    loss_rate_decimal = 1 - win_rate_decimal
    expectancy = _round(win_rate_decimal * avg_gain + loss_rate_decimal * avg_loss)

    realized_pnl = sum((t.pnl for t in realized_trades), Decimal("0"))

    return BrokerageResult(
        symbol=symbol,
        current_quantity=_round(current_quantity, 6),
        avg_cost=_round(avg_cost),
        cost_basis=_round(total_cost),
        realized_pnl=_round(realized_pnl),
        unrealized_pnl=_round(unrealized_pnl),
        unrealized_pnl_pct=unrealized_pnl_pct,
        dividend_income=_round(dividend_income),
        fees_paid=_round(fees_paid),
        win_count=win_count,
        loss_count=loss_count,
        win_rate_pct=win_rate,
        avg_gain_pct=avg_gain,
        avg_loss_pct=avg_loss,
        expectancy_pct=expectancy,
        realized_trades=realized_trades,
    )
