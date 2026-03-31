"""
Rules-based insights and risk alerts engine.
No fake AI — practical, deterministic rules that flag real issues.
"""
from typing import List
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.deal import Deal, DealStatus
from app.models.transaction import Transaction, TransactionType
from app.models.cashflow import DealCashflow, CashflowType
from app.models.platform import Platform
from app.schemas.analytics import RiskAlert


CONCENTRATION_THRESHOLD_PCT = Decimal("30")  # alert if >30% in one platform
INACTIVE_DEAL_DAYS = 365                       # deals with no cashflows in 1 year
MATURITY_WARN_DAYS = 90                        # warn if maturing within 90 days
UNREALIZED_LOSS_THRESHOLD_PCT = Decimal("-20") # alert if unrealized loss > 20%
IDLE_CASH_RATIO_THRESHOLD = Decimal("0.15")   # alert if >15% in cash/deposits


def generate_alerts(user_id: int, db: Session) -> List[RiskAlert]:
    alerts: List[RiskAlert] = []

    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    deals = db.query(Deal).filter(Deal.user_id == user_id).all()

    # --- Alert 1: Inactive deals (no cashflow activity in > 1 year) ---
    for deal in deals:
        if deal.status != DealStatus.ACTIVE:
            continue
        latest_cf = (
            db.query(DealCashflow)
            .filter(DealCashflow.deal_id == deal.id)
            .order_by(DealCashflow.cashflow_date.desc())
            .first()
        )
        if not latest_cf:
            alerts.append(RiskAlert(
                alert_type="no_cashflow",
                severity="medium",
                title="Deal has no cashflow records",
                description=f"'{deal.name}' is active but has no cashflow entries recorded.",
                recommendation="Add investment and distribution records for this deal, or mark it as exited.",
                affected_items=[deal.name],
            ))
        elif (date.today() - latest_cf.cashflow_date).days > INACTIVE_DEAL_DAYS:
            alerts.append(RiskAlert(
                alert_type="stale_deal",
                severity="low",
                title="Deal appears stale",
                description=f"'{deal.name}' has had no cashflow activity for over {INACTIVE_DEAL_DAYS} days.",
                recommendation="Verify the deal status and update its records.",
                affected_items=[deal.name],
            ))

    # --- Alert 2: Upcoming deal maturities ---
    today = date.today()
    soon = today + timedelta(days=MATURITY_WARN_DAYS)
    for deal in deals:
        if deal.maturity_date and deal.status == DealStatus.ACTIVE:
            if today <= deal.maturity_date <= soon:
                days_left = (deal.maturity_date - today).days
                alerts.append(RiskAlert(
                    alert_type="maturing_soon",
                    severity="medium",
                    title="Deal maturing soon",
                    description=f"'{deal.name}' matures in {days_left} days ({deal.maturity_date}).",
                    recommendation="Ensure you have a reinvestment plan and check redemption terms.",
                    affected_items=[deal.name],
                ))
            elif deal.maturity_date < today:
                alerts.append(RiskAlert(
                    alert_type="maturity_overdue",
                    severity="high",
                    title="Deal past maturity date",
                    description=f"'{deal.name}' passed its maturity date ({deal.maturity_date}) but is still marked Active.",
                    recommendation="Update the deal status to Matured or Exited.",
                    affected_items=[deal.name],
                ))

    # --- Alert 3: Missing price data for active holdings ---
    from app.models.asset import Asset
    from app.models.price import PriceHistory
    from app.models.transaction import Transaction

    account_ids = [a.id for a in accounts]
    buy_asset_ids = (
        db.query(Transaction.asset_id)
        .filter(
            Transaction.account_id.in_(account_ids),
            Transaction.transaction_type == TransactionType.BUY,
            Transaction.asset_id.isnot(None),
        )
        .distinct()
        .all()
    )
    buy_asset_ids = [row[0] for row in buy_asset_ids]

    for asset_id in buy_asset_ids:
        ph = db.query(PriceHistory).filter(PriceHistory.asset_id == asset_id).first()
        if not ph:
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            symbol = asset.symbol if asset else str(asset_id)
            alerts.append(RiskAlert(
                alert_type="missing_price_data",
                severity="low",
                title="No price data for asset",
                description=f"Asset '{symbol}' has no price history. Unrealized P&L cannot be calculated.",
                recommendation="Upload price data or connect a market data provider for this asset.",
                affected_items=[symbol],
            ))

    # --- Alert 4: Accounts with no transactions ---
    for acc in accounts:
        txn_count = db.query(Transaction).filter(Transaction.account_id == acc.id).count()
        if txn_count == 0:
            platform = db.query(Platform).filter(Platform.id == acc.platform_id).first()
            alerts.append(RiskAlert(
                alert_type="empty_account",
                severity="low",
                title="Account has no transactions",
                description=f"Account '{acc.name}' ({platform.name if platform else 'Unknown'}) has no transaction records.",
                recommendation="Import transaction history or add transactions manually.",
                affected_items=[acc.name],
            ))

    # --- Alert 5: Platform concentration ---
    platform_invested: dict = {}
    for deal in deals:
        cfs = db.query(DealCashflow).filter(
            DealCashflow.deal_id == deal.id,
            DealCashflow.cashflow_type == CashflowType.INVESTMENT,
        ).all()
        platform_invested.setdefault(deal.platform_id, Decimal("0"))
        platform_invested[deal.platform_id] += sum(Decimal(str(cf.amount)) for cf in cfs)

    total_invested = sum(platform_invested.values())
    if total_invested > 0:
        for platform_id, invested in platform_invested.items():
            pct = invested / total_invested * 100
            if pct > CONCENTRATION_THRESHOLD_PCT:
                platform = db.query(Platform).filter(Platform.id == platform_id).first()
                alerts.append(RiskAlert(
                    alert_type="concentration_risk",
                    severity="medium",
                    title="High platform concentration",
                    description=f"{platform.name if platform else 'Platform'} holds {pct:.1f}% of deal investments.",
                    recommendation=f"Consider diversifying. Platform concentration above {CONCENTRATION_THRESHOLD_PCT}% adds counterparty risk.",
                    affected_items=[platform.name if platform else str(platform_id)],
                ))

    return alerts
