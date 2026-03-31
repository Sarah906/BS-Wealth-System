"""
Deal-based investment calculations: ROI, IRR/XIRR, duration, cashflow analysis.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple
from datetime import date
import math


@dataclass
class CashflowEntry:
    date: date
    amount: Decimal
    cashflow_type: str  # INVESTMENT, DISTRIBUTION, REDEMPTION, FEE, VALUATION


@dataclass
class DealResult:
    deal_id: int
    deal_name: str
    invested_capital: Decimal
    returned_capital: Decimal       # distributions + redemptions
    current_value: Decimal          # from latest VALUATION snapshot, else 0
    cumulative_distributions: Decimal
    fees_paid: Decimal
    net_gain: Decimal               # returned_capital + current_value - invested_capital
    roi_pct: Decimal
    irr_pct: Optional[Decimal]
    duration_days: Optional[int]
    is_active: bool


def _round(val: Decimal, places: int = 4) -> Decimal:
    return val.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


def xirr(cashflows: List[Tuple[date, float]], guess: float = 0.1, max_iter: int = 100) -> Optional[float]:
    """
    Newton-Raphson XIRR calculation.
    cashflows: list of (date, amount) where negative = outflow, positive = inflow.
    Returns annualized rate or None if it fails to converge.
    """
    if not cashflows or len(cashflows) < 2:
        return None

    # All positive or all negative means IRR is undefined
    amounts = [c[1] for c in cashflows]
    if all(a >= 0 for a in amounts) or all(a <= 0 for a in amounts):
        return None

    base_date = cashflows[0][0]
    days = [(cf[0] - base_date).days for cf in cashflows]
    amounts_f = [cf[1] for cf in cashflows]

    rate = guess
    for _ in range(max_iter):
        npv = sum(amt / (1 + rate) ** (d / 365.0) for amt, d in zip(amounts_f, days))
        dnpv = sum(
            -d / 365.0 * amt / (1 + rate) ** (d / 365.0 + 1)
            for amt, d in zip(amounts_f, days)
        )
        if dnpv == 0:
            return None
        new_rate = rate - npv / dnpv
        if abs(new_rate - rate) < 1e-6:
            return new_rate
        rate = new_rate

    return None  # did not converge


def calculate_deal_metrics(
    deal_id: int,
    deal_name: str,
    cashflows: List[CashflowEntry],
    start_date: Optional[date] = None,
    maturity_date: Optional[date] = None,
    is_active: bool = True,
) -> DealResult:
    """
    Calculate deal performance from a list of cashflow entries.
    """
    invested_capital = Decimal("0")
    returned_capital = Decimal("0")
    cumulative_distributions = Decimal("0")
    fees_paid = Decimal("0")
    current_value = Decimal("0")

    valuation_cashflows = [cf for cf in cashflows if cf.cashflow_type == "VALUATION"]
    if valuation_cashflows:
        latest_val = max(valuation_cashflows, key=lambda c: c.date)
        current_value = latest_val.amount

    for cf in cashflows:
        if cf.cashflow_type == "INVESTMENT":
            invested_capital += cf.amount
        elif cf.cashflow_type in ("DISTRIBUTION",):
            returned_capital += cf.amount
            cumulative_distributions += cf.amount
        elif cf.cashflow_type == "REDEMPTION":
            returned_capital += cf.amount
        elif cf.cashflow_type == "FEE":
            fees_paid += cf.amount
        # VALUATION and PROJECTED don't affect cash totals

    net_gain = returned_capital + current_value - invested_capital - fees_paid
    roi_pct = (
        _round(net_gain / invested_capital * 100) if invested_capital > 0 else Decimal("0")
    )

    # Build XIRR cashflow list: investments are outflows (negative), returns are inflows (positive)
    xirr_inputs: List[Tuple[date, float]] = []
    for cf in sorted(cashflows, key=lambda c: c.date):
        if cf.cashflow_type == "INVESTMENT":
            xirr_inputs.append((cf.date, -float(cf.amount)))
        elif cf.cashflow_type in ("DISTRIBUTION", "REDEMPTION"):
            xirr_inputs.append((cf.date, float(cf.amount)))

    # Add current value as a terminal cash inflow if deal is active
    if is_active and current_value > 0:
        from datetime import date as dt
        xirr_inputs.append((dt.today(), float(current_value)))

    irr_value = xirr(xirr_inputs)
    irr_pct = _round(Decimal(irr_value * 100)) if irr_value is not None else None

    # Duration
    all_dates = [cf.date for cf in cashflows]
    if all_dates:
        first_date = start_date or min(all_dates)
        last_date = (maturity_date if (not is_active and maturity_date) else date.today())
        duration_days = (last_date - first_date).days
    else:
        duration_days = None

    return DealResult(
        deal_id=deal_id,
        deal_name=deal_name,
        invested_capital=_round(invested_capital),
        returned_capital=_round(returned_capital),
        current_value=_round(current_value),
        cumulative_distributions=_round(cumulative_distributions),
        fees_paid=_round(fees_paid),
        net_gain=_round(net_gain),
        roi_pct=roi_pct,
        irr_pct=irr_pct,
        duration_days=duration_days,
        is_active=is_active,
    )
