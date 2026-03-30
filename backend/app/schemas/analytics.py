from pydantic import BaseModel
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import date


class AllocationItem(BaseModel):
    label: str
    value: Decimal
    percentage: Decimal


class PortfolioSummary(BaseModel):
    total_portfolio_value: Decimal
    total_invested_capital: Decimal
    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal
    total_fees_paid: Decimal
    total_distributions: Decimal
    overall_roi_pct: Decimal
    monthly_income: Decimal
    allocation_by_platform: List[AllocationItem]
    allocation_by_asset_type: List[AllocationItem]
    allocation_by_currency: List[AllocationItem]


class BrokeragePerformance(BaseModel):
    account_id: int
    account_name: str
    platform_name: str
    current_value: Decimal
    invested_capital: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_fees: Decimal
    dividend_income: Decimal
    roi_pct: Decimal
    win_count: int
    loss_count: int
    win_rate_pct: Decimal


class DealPerformance(BaseModel):
    deal_id: int
    deal_name: str
    platform_name: str
    deal_type: str
    status: str
    invested_capital: Decimal
    returned_capital: Decimal
    current_value: Decimal
    cumulative_distributions: Decimal
    roi_pct: Decimal
    irr_pct: Optional[Decimal]
    duration_days: Optional[int]
    maturity_date: Optional[date]
    target_return_pct: Optional[Decimal]


class MonthlyCashflow(BaseModel):
    month: str  # YYYY-MM
    inflows: Decimal
    outflows: Decimal
    net: Decimal
    distributions: Decimal


class AssetHolding(BaseModel):
    asset_id: int
    symbol: str
    name: str
    quantity: Decimal
    avg_cost: Decimal
    current_price: Optional[Decimal]
    current_value: Decimal
    cost_basis: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: Decimal


class WinLossStats(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: Decimal
    avg_gain_pct: Decimal
    avg_loss_pct: Decimal
    expectancy_pct: Decimal
    total_realized_pnl: Decimal


class RiskAlert(BaseModel):
    alert_type: str
    severity: str  # low, medium, high
    title: str
    description: str
    recommendation: str
    affected_items: List[str]
