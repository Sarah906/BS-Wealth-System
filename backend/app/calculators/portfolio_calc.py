"""
Portfolio-level aggregation: allocation, monthly cashflows, concentration, net worth timeline.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional
from datetime import date
from collections import defaultdict


@dataclass
class AllocationItem:
    label: str
    value: Decimal
    percentage: Decimal


@dataclass
class MonthlyCashflow:
    month: str  # YYYY-MM
    inflows: Decimal
    outflows: Decimal
    net: Decimal
    distributions: Decimal


@dataclass
class PortfolioSummary:
    total_portfolio_value: Decimal
    total_invested_capital: Decimal
    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal
    total_fees_paid: Decimal
    total_distributions: Decimal
    overall_roi_pct: Decimal
    allocation_by_platform: List[AllocationItem]
    allocation_by_asset_type: List[AllocationItem]
    allocation_by_currency: List[AllocationItem]
    monthly_cashflows: List[MonthlyCashflow]


def _round(val: Decimal, places: int = 2) -> Decimal:
    return val.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)


def _build_allocation(items: Dict[str, Decimal], total: Decimal) -> List[AllocationItem]:
    result = []
    for label, value in sorted(items.items(), key=lambda x: x[1], reverse=True):
        pct = _round(value / total * 100) if total > 0 else Decimal("0")
        result.append(AllocationItem(label=label, value=_round(value), percentage=pct))
    return result


def build_portfolio_summary(
    brokerage_data: List[Dict],    # list of dicts with keys: platform, asset_type, currency, current_value, cost_basis, realized_pnl, unrealized_pnl, fees, dividends
    deal_data: List[Dict],         # list of dicts with keys: platform, deal_type, currency, current_value, invested_capital, net_gain, distributions, fees
    raw_cashflows: List[Dict],     # list of dicts with keys: date (date obj), amount, cashflow_type (DEPOSIT/WITHDRAWAL/DISTRIBUTION etc)
) -> PortfolioSummary:
    total_brokerage_value = sum(Decimal(str(d.get("current_value", 0))) for d in brokerage_data)
    total_deal_value = sum(Decimal(str(d.get("current_value", 0))) for d in deal_data)
    total_portfolio_value = total_brokerage_value + total_deal_value

    total_invested = (
        sum(Decimal(str(d.get("cost_basis", 0))) for d in brokerage_data)
        + sum(Decimal(str(d.get("invested_capital", 0))) for d in deal_data)
    )
    total_realized = (
        sum(Decimal(str(d.get("realized_pnl", 0))) for d in brokerage_data)
        + sum(Decimal(str(d.get("net_gain", 0))) for d in deal_data if not d.get("is_active", True))
    )
    total_unrealized = sum(Decimal(str(d.get("unrealized_pnl", 0))) for d in brokerage_data)
    total_fees = (
        sum(Decimal(str(d.get("fees", 0))) for d in brokerage_data)
        + sum(Decimal(str(d.get("fees", 0))) for d in deal_data)
    )
    total_distributions = sum(Decimal(str(d.get("distributions", 0))) for d in deal_data)

    overall_roi = (
        _round((total_realized + total_unrealized) / total_invested * 100)
        if total_invested > 0 else Decimal("0")
    )

    # Allocations by platform
    platform_values: Dict[str, Decimal] = defaultdict(Decimal)
    for d in brokerage_data:
        platform_values[d.get("platform", "Unknown")] += Decimal(str(d.get("current_value", 0)))
    for d in deal_data:
        platform_values[d.get("platform", "Unknown")] += Decimal(str(d.get("current_value", 0)))

    asset_type_values: Dict[str, Decimal] = defaultdict(Decimal)
    for d in brokerage_data:
        asset_type_values[d.get("asset_type", "Unknown")] += Decimal(str(d.get("current_value", 0)))
    for d in deal_data:
        asset_type_values[d.get("deal_type", "deal")] += Decimal(str(d.get("current_value", 0)))

    currency_values: Dict[str, Decimal] = defaultdict(Decimal)
    for d in brokerage_data + deal_data:
        currency_values[d.get("currency", "SAR")] += Decimal(str(d.get("current_value", 0)))

    # Monthly cashflows
    monthly: Dict[str, Dict] = defaultdict(lambda: {
        "inflows": Decimal("0"), "outflows": Decimal("0"), "distributions": Decimal("0")
    })
    for cf in raw_cashflows:
        dt = cf.get("date")
        if not dt:
            continue
        key = dt.strftime("%Y-%m")
        amount = Decimal(str(cf.get("amount", 0)))
        cf_type = cf.get("cashflow_type", "")
        if cf_type in ("DEPOSIT", "INVESTMENT"):
            monthly[key]["inflows"] += amount
        elif cf_type in ("WITHDRAWAL", "FEE"):
            monthly[key]["outflows"] += amount
        elif cf_type in ("DISTRIBUTION", "REDEMPTION", "DIVIDEND"):
            monthly[key]["inflows"] += amount
            monthly[key]["distributions"] += amount

    monthly_list = [
        MonthlyCashflow(
            month=k,
            inflows=_round(v["inflows"]),
            outflows=_round(v["outflows"]),
            net=_round(v["inflows"] - v["outflows"]),
            distributions=_round(v["distributions"]),
        )
        for k, v in sorted(monthly.items())
    ]

    return PortfolioSummary(
        total_portfolio_value=_round(total_portfolio_value),
        total_invested_capital=_round(total_invested),
        total_realized_pnl=_round(total_realized),
        total_unrealized_pnl=_round(total_unrealized),
        total_fees_paid=_round(total_fees),
        total_distributions=_round(total_distributions),
        overall_roi_pct=overall_roi,
        allocation_by_platform=_build_allocation(platform_values, total_portfolio_value),
        allocation_by_asset_type=_build_allocation(asset_type_values, total_portfolio_value),
        allocation_by_currency=_build_allocation(currency_values, total_portfolio_value),
        monthly_cashflows=monthly_list,
    )
