"""Tests for deal/XIRR calculator."""
import pytest
from decimal import Decimal
from datetime import date

from app.calculators.deal_calc import calculate_deal_metrics, CashflowEntry, xirr


def make_cf(d, amount, cf_type):
    return CashflowEntry(date=date.fromisoformat(d), amount=Decimal(str(amount)), cashflow_type=cf_type)


def test_simple_deal_roi():
    cfs = [
        make_cf("2022-01-01", 100000, "INVESTMENT"),
        make_cf("2022-07-01", 6000, "DISTRIBUTION"),
        make_cf("2023-01-01", 106000, "REDEMPTION"),
    ]
    result = calculate_deal_metrics(1, "Test Deal", cfs, is_active=False)
    assert result.invested_capital == Decimal("100000")
    assert result.returned_capital == Decimal("112000")
    assert result.roi_pct > Decimal("10")
    assert result.roi_pct < Decimal("15")


def test_active_deal_with_valuation():
    cfs = [
        make_cf("2021-01-01", 50000, "INVESTMENT"),
        make_cf("2022-01-01", 5000, "DISTRIBUTION"),
        make_cf("2023-01-01", 52000, "VALUATION"),
    ]
    result = calculate_deal_metrics(2, "Active Deal", cfs, is_active=True)
    assert result.current_value == Decimal("52000")
    assert result.cumulative_distributions == Decimal("5000")
    assert result.invested_capital == Decimal("50000")
    assert result.net_gain > 0


def test_deal_with_fees():
    cfs = [
        make_cf("2022-01-01", 100000, "INVESTMENT"),
        make_cf("2022-01-01", 2000, "FEE"),
        make_cf("2023-01-01", 110000, "REDEMPTION"),
    ]
    result = calculate_deal_metrics(3, "Fee Deal", cfs, is_active=False)
    assert result.fees_paid == Decimal("2000")
    assert result.net_gain == Decimal("8000")  # 110k returned - 100k invested - 2k fees


def test_xirr_returns_reasonable_rate():
    # Annual return of 12% should give ~12% XIRR
    cashflows = [
        (date(2022, 1, 1), -100000.0),
        (date(2023, 1, 1), 112000.0),
    ]
    rate = xirr(cashflows)
    assert rate is not None
    assert 0.10 < rate < 0.14


def test_xirr_undefined_all_positive():
    cashflows = [
        (date(2022, 1, 1), 100.0),
        (date(2023, 1, 1), 200.0),
    ]
    rate = xirr(cashflows)
    assert rate is None


def test_deal_duration_days():
    cfs = [
        make_cf("2022-01-01", 50000, "INVESTMENT"),
        make_cf("2023-01-01", 55000, "REDEMPTION"),
    ]
    result = calculate_deal_metrics(
        4, "Duration Deal", cfs,
        start_date=date(2022, 1, 1),
        maturity_date=date(2023, 1, 1),
        is_active=False,
    )
    assert result.duration_days == 365


def test_empty_deal():
    result = calculate_deal_metrics(5, "Empty", [], is_active=True)
    assert result.invested_capital == Decimal("0")
    assert result.roi_pct == Decimal("0")
    assert result.irr_pct is None
