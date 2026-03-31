"""
Analytics endpoints: portfolio summary, brokerage performance, deal performance,
monthly cashflows, allocation, win/loss stats.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date

from app.db.session import get_db
from app.models.user import User
from app.models.account import Account
from app.models.deal import Deal
from app.models.transaction import Transaction, TransactionType
from app.models.cashflow import DealCashflow, CashflowType
from app.models.asset import Asset
from app.models.price import PriceHistory
from app.models.platform import Platform
from app.api.deps import get_current_user
from app.calculators.brokerage_calc import calculate_fifo_position, TradeRecord
from app.calculators.deal_calc import calculate_deal_metrics, CashflowEntry
from app.calculators.portfolio_calc import build_portfolio_summary
from app.schemas.analytics import (
    PortfolioSummary, BrokeragePerformance, DealPerformance,
    MonthlyCashflow, AssetHolding, WinLossStats, RiskAlert, AllocationItem,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_latest_price(asset_id: int, db: Session) -> Optional[Decimal]:
    ph = (
        db.query(PriceHistory)
        .filter(PriceHistory.asset_id == asset_id)
        .order_by(PriceHistory.date.desc())
        .first()
    )
    return Decimal(str(ph.close)) if ph else None


def _get_platform_name(platform_id: int, db: Session) -> str:
    p = db.query(Platform).filter(Platform.id == platform_id).first()
    return p.name if p else "Unknown"


@router.get("/summary", response_model=PortfolioSummary)
def portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Overall portfolio summary across all accounts and deals."""
    user_accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    account_ids = [a.id for a in user_accounts]

    # Build brokerage data per account/asset
    brokerage_data = []
    all_brokerage_cashflows = []

    for acc in user_accounts:
        platform_name = _get_platform_name(acc.platform_id, db)
        transactions = (
            db.query(Transaction)
            .filter(Transaction.account_id == acc.id)
            .order_by(Transaction.trade_date)
            .all()
        )

        # Group by asset
        asset_txns: dict = {}
        for txn in transactions:
            # Track cashflows for monthly view
            cf_entry = {
                "date": txn.trade_date,
                "amount": float(txn.net_amount or txn.gross_amount or 0),
                "cashflow_type": txn.transaction_type.value,
            }
            all_brokerage_cashflows.append(cf_entry)

            if txn.asset_id:
                asset_txns.setdefault(txn.asset_id, []).append(txn)

        for asset_id, txns in asset_txns.items():
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                continue
            current_price = _get_latest_price(asset_id, db)

            trades = []
            for t in txns:
                if t.transaction_type in (TransactionType.BUY, TransactionType.SELL):
                    trades.append(TradeRecord(
                        date=t.trade_date,
                        quantity=Decimal(str(t.quantity or 0)),
                        price=Decimal(str(t.price or 0)),
                        fees=Decimal(str(t.fees or 0)),
                        transaction_type=t.transaction_type.value,
                    ))
                elif t.transaction_type == TransactionType.DIVIDEND:
                    trades.append(TradeRecord(
                        date=t.trade_date,
                        quantity=Decimal(str(t.net_amount or 0)),
                        price=Decimal("0"),
                        fees=Decimal("0"),
                        transaction_type="DIVIDEND",
                    ))

            result = calculate_fifo_position(trades, current_price=current_price, symbol=asset.symbol)
            current_value = (current_price or Decimal("0")) * result.current_quantity

            brokerage_data.append({
                "platform": platform_name,
                "asset_type": asset.asset_type.value,
                "currency": asset.currency,
                "current_value": float(current_value),
                "cost_basis": float(result.cost_basis),
                "realized_pnl": float(result.realized_pnl),
                "unrealized_pnl": float(result.unrealized_pnl),
                "fees": float(result.fees_paid),
                "dividends": float(result.dividend_income),
            })

    # Build deal data
    user_deals = db.query(Deal).filter(Deal.user_id == current_user.id).all()
    deal_data = []
    all_deal_cashflows = []

    for deal in user_deals:
        platform_name = _get_platform_name(deal.platform_id, db)
        cfs = db.query(DealCashflow).filter(DealCashflow.deal_id == deal.id).all()
        cf_entries = [
            CashflowEntry(date=cf.cashflow_date, amount=Decimal(str(cf.amount)), cashflow_type=cf.cashflow_type.value)
            for cf in cfs
        ]
        result = calculate_deal_metrics(
            deal_id=deal.id,
            deal_name=deal.name,
            cashflows=cf_entries,
            start_date=deal.start_date,
            maturity_date=deal.maturity_date,
            is_active=(deal.status.value == "active"),
        )

        for cf in cfs:
            all_deal_cashflows.append({
                "date": cf.cashflow_date,
                "amount": float(cf.amount),
                "cashflow_type": cf.cashflow_type.value,
            })

        deal_data.append({
            "platform": platform_name,
            "deal_type": deal.deal_type.value,
            "currency": deal.currency,
            "current_value": float(result.current_value),
            "invested_capital": float(result.invested_capital),
            "net_gain": float(result.net_gain),
            "distributions": float(result.cumulative_distributions),
            "fees": float(result.fees_paid),
            "is_active": result.is_active,
        })

    all_cashflows = all_brokerage_cashflows + all_deal_cashflows
    portfolio = build_portfolio_summary(brokerage_data, deal_data, all_cashflows)

    return PortfolioSummary(
        total_portfolio_value=portfolio.total_portfolio_value,
        total_invested_capital=portfolio.total_invested_capital,
        total_realized_pnl=portfolio.total_realized_pnl,
        total_unrealized_pnl=portfolio.total_unrealized_pnl,
        total_fees_paid=portfolio.total_fees_paid,
        total_distributions=portfolio.total_distributions,
        overall_roi_pct=portfolio.overall_roi_pct,
        monthly_income=portfolio.total_distributions / 12 if portfolio.total_distributions else Decimal("0"),
        allocation_by_platform=[AllocationItem(**vars(a)) for a in portfolio.allocation_by_platform],
        allocation_by_asset_type=[AllocationItem(**vars(a)) for a in portfolio.allocation_by_asset_type],
        allocation_by_currency=[AllocationItem(**vars(a)) for a in portfolio.allocation_by_currency],
    )


@router.get("/brokerage", response_model=List[BrokeragePerformance])
def brokerage_performance(
    account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Performance by brokerage account."""
    accounts = db.query(Account).filter(Account.user_id == current_user.id)
    if account_id:
        accounts = accounts.filter(Account.id == account_id)
    accounts = accounts.all()

    results = []
    for acc in accounts:
        platform = db.query(Platform).filter(Platform.id == acc.platform_id).first()
        transactions = (
            db.query(Transaction)
            .filter(Transaction.account_id == acc.id)
            .order_by(Transaction.trade_date)
            .all()
        )

        total_realized = Decimal("0")
        total_unrealized = Decimal("0")
        total_fees = Decimal("0")
        total_dividends = Decimal("0")
        all_wins, all_losses = 0, 0
        total_invested = Decimal("0")
        total_current_value = Decimal("0")

        asset_txns: dict = {}
        for txn in transactions:
            total_fees += Decimal(str(txn.fees or 0))
            if txn.asset_id:
                asset_txns.setdefault(txn.asset_id, []).append(txn)

        for asset_id, txns in asset_txns.items():
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                continue
            current_price = _get_latest_price(asset_id, db)
            trades = []
            for t in txns:
                if t.transaction_type in (TransactionType.BUY, TransactionType.SELL):
                    trades.append(TradeRecord(
                        date=t.trade_date,
                        quantity=Decimal(str(t.quantity or 0)),
                        price=Decimal(str(t.price or 0)),
                        fees=Decimal(str(t.fees or 0)),
                        transaction_type=t.transaction_type.value,
                    ))
                elif t.transaction_type == TransactionType.DIVIDEND:
                    trades.append(TradeRecord(
                        date=t.trade_date,
                        quantity=Decimal(str(t.net_amount or 0)),
                        price=Decimal("0"),
                        fees=Decimal("0"),
                        transaction_type="DIVIDEND",
                    ))

            r = calculate_fifo_position(trades, current_price=current_price, symbol=asset.symbol)
            cv = (current_price or Decimal("0")) * r.current_quantity
            total_realized += r.realized_pnl
            total_unrealized += r.unrealized_pnl
            total_dividends += r.dividend_income
            total_invested += r.cost_basis
            total_current_value += cv
            all_wins += r.win_count
            all_losses += r.loss_count

        total_trades = all_wins + all_losses
        win_rate = Decimal(all_wins) / Decimal(total_trades) * 100 if total_trades else Decimal("0")
        roi = (
            (total_realized + total_unrealized) / total_invested * 100
            if total_invested > 0 else Decimal("0")
        )

        results.append(BrokeragePerformance(
            account_id=acc.id,
            account_name=acc.name,
            platform_name=platform.name if platform else "Unknown",
            current_value=total_current_value,
            invested_capital=total_invested,
            realized_pnl=total_realized,
            unrealized_pnl=total_unrealized,
            total_fees=total_fees,
            dividend_income=total_dividends,
            roi_pct=roi,
            win_count=all_wins,
            loss_count=all_losses,
            win_rate_pct=win_rate,
        ))

    return results


@router.get("/deals", response_model=List[DealPerformance])
def deal_performance(
    platform_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Performance by deal."""
    q = db.query(Deal).filter(Deal.user_id == current_user.id)
    if platform_id:
        q = q.filter(Deal.platform_id == platform_id)
    if status:
        q = q.filter(Deal.status == status)
    deals = q.all()

    results = []
    for deal in deals:
        platform = db.query(Platform).filter(Platform.id == deal.platform_id).first()
        cfs = db.query(DealCashflow).filter(DealCashflow.deal_id == deal.id).all()
        cf_entries = [
            CashflowEntry(
                date=cf.cashflow_date,
                amount=Decimal(str(cf.amount)),
                cashflow_type=cf.cashflow_type.value,
            )
            for cf in cfs
        ]
        r = calculate_deal_metrics(
            deal_id=deal.id,
            deal_name=deal.name,
            cashflows=cf_entries,
            start_date=deal.start_date,
            maturity_date=deal.maturity_date,
            is_active=(deal.status.value == "active"),
        )
        results.append(DealPerformance(
            deal_id=deal.id,
            deal_name=deal.name,
            platform_name=platform.name if platform else "Unknown",
            deal_type=deal.deal_type.value,
            status=deal.status.value,
            invested_capital=r.invested_capital,
            returned_capital=r.returned_capital,
            current_value=r.current_value,
            cumulative_distributions=r.cumulative_distributions,
            roi_pct=r.roi_pct,
            irr_pct=r.irr_pct,
            duration_days=r.duration_days,
            maturity_date=deal.maturity_date,
            target_return_pct=deal.target_return,
        ))

    return results


@router.get("/monthly-cashflow", response_model=List[MonthlyCashflow])
def monthly_cashflow(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Monthly cashflow summary across all accounts and deals."""
    from collections import defaultdict

    user_account_ids = [
        a.id for a in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    user_deal_ids = [
        d.id for d in db.query(Deal).filter(Deal.user_id == current_user.id).all()
    ]

    monthly: dict = defaultdict(lambda: {
        "inflows": Decimal("0"), "outflows": Decimal("0"), "distributions": Decimal("0")
    })

    # Brokerage transactions
    txns = db.query(Transaction).filter(Transaction.account_id.in_(user_account_ids)).all()
    for t in txns:
        key = t.trade_date.strftime("%Y-%m")
        amount = Decimal(str(t.net_amount or t.gross_amount or 0))
        if t.transaction_type in (TransactionType.DEPOSIT, TransactionType.BUY):
            monthly[key]["inflows"] += amount
        elif t.transaction_type in (TransactionType.WITHDRAWAL, TransactionType.FEE):
            monthly[key]["outflows"] += amount
        elif t.transaction_type == TransactionType.DIVIDEND:
            monthly[key]["inflows"] += amount
            monthly[key]["distributions"] += amount

    # Deal cashflows
    cfs = db.query(DealCashflow).filter(DealCashflow.deal_id.in_(user_deal_ids)).all()
    for cf in cfs:
        key = cf.cashflow_date.strftime("%Y-%m")
        amount = Decimal(str(cf.amount))
        if cf.cashflow_type == CashflowType.INVESTMENT:
            monthly[key]["outflows"] += amount
        elif cf.cashflow_type in (CashflowType.DISTRIBUTION, CashflowType.REDEMPTION):
            monthly[key]["inflows"] += amount
            monthly[key]["distributions"] += amount
        elif cf.cashflow_type == CashflowType.FEE:
            monthly[key]["outflows"] += amount

    return [
        MonthlyCashflow(
            month=k,
            inflows=v["inflows"],
            outflows=v["outflows"],
            net=v["inflows"] - v["outflows"],
            distributions=v["distributions"],
        )
        for k, v in sorted(monthly.items())
    ]


@router.get("/insights/alerts", response_model=List[RiskAlert])
def risk_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rules-based risk alerts and insights."""
    from app.services.insights_service import generate_alerts
    return generate_alerts(current_user.id, db)
