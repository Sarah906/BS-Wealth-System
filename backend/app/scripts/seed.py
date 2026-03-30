"""
Seed script: inserts Saudi platforms, a demo user, sample accounts,
assets, transactions, and deal cashflows.
Run via: python -m app.scripts.seed
"""
import sys
import os
import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app.models.platform import Platform, PlatformCategory
from app.models.user import User
from app.models.account import Account, AccountType
from app.models.asset import Asset, AssetType
from app.models.deal import Deal, DealType, DealStatus
from app.models.transaction import Transaction, TransactionType
from app.models.cashflow import DealCashflow, CashflowType
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PLATFORMS = [
    # Brokerage platforms
    {"name": "Derayah", "category": PlatformCategory.BROKERAGE, "country": "SA", "currency": "SAR",
     "description": "Derayah Financial brokerage platform", "website": "https://derayah.com"},
    {"name": "Alinma", "category": PlatformCategory.BROKERAGE, "country": "SA", "currency": "SAR",
     "description": "Alinma Investment Company brokerage", "website": "https://alinvest.com.sa"},
    {"name": "Al Rajhi", "category": PlatformCategory.BROKERAGE, "country": "SA", "currency": "SAR",
     "description": "Al Rajhi Capital brokerage", "website": "https://alrajhi.com"},

    # Robo / managed
    {"name": "Derayah Smart", "category": PlatformCategory.ROBO, "country": "SA", "currency": "SAR",
     "description": "Derayah Smart robo-advisor portfolios"},
    {"name": "Aseel", "category": PlatformCategory.ROBO, "country": "SA", "currency": "SAR",
     "description": "Aseel robo-advisory and managed funds", "website": "https://aseel.com.sa"},

    # Sukuk / fixed income
    {"name": "Sukuk", "category": PlatformCategory.SUKUK, "country": "SA", "currency": "SAR",
     "description": "Direct sukuk / Islamic bond investments"},
    {"name": "Awaed", "category": PlatformCategory.SUKUK, "country": "SA", "currency": "SAR",
     "description": "Awaed (Awائد) fixed income platform"},

    # Deal / crowdfunding
    {"name": "Tamra", "category": PlatformCategory.CROWDFUNDING, "country": "SA", "currency": "SAR",
     "description": "Tamra real estate crowdfunding platform", "website": "https://tamra.com.sa"},
    {"name": "Tarmeez", "category": PlatformCategory.DEAL, "country": "SA", "currency": "SAR",
     "description": "Tarmeez investment platform"},
    {"name": "Safqah", "category": PlatformCategory.CROWDFUNDING, "country": "SA", "currency": "SAR",
     "description": "Safqah deal-based investment platform"},
    {"name": "Manafa", "category": PlatformCategory.CROWDFUNDING, "country": "SA", "currency": "SAR",
     "description": "Manafa equity crowdfunding platform", "website": "https://manafa.sa"},
]


SAMPLE_ASSETS = [
    {"symbol": "2222", "name": "Saudi Aramco", "exchange": "TADAWUL", "asset_type": AssetType.STOCK, "currency": "SAR", "sector": "Energy"},
    {"symbol": "1120", "name": "Al Rajhi Bank", "exchange": "TADAWUL", "asset_type": AssetType.STOCK, "currency": "SAR", "sector": "Financials"},
    {"symbol": "1010", "name": "Riyad Bank", "exchange": "TADAWUL", "asset_type": AssetType.STOCK, "currency": "SAR", "sector": "Financials"},
    {"symbol": "2010", "name": "SABIC", "exchange": "TADAWUL", "asset_type": AssetType.STOCK, "currency": "SAR", "sector": "Materials"},
    {"symbol": "4030", "name": "Dar Al Arkan", "exchange": "TADAWUL", "asset_type": AssetType.STOCK, "currency": "SAR", "sector": "Real Estate"},
    {"symbol": "MSFT", "name": "Microsoft Corp", "exchange": "NASDAQ", "asset_type": AssetType.STOCK, "currency": "USD", "sector": "Technology"},
    {"symbol": "AAPL", "name": "Apple Inc", "exchange": "NASDAQ", "asset_type": AssetType.STOCK, "currency": "USD", "sector": "Technology"},
]


def seed_platforms(db: Session) -> dict:
    platform_map = {}
    for p_data in PLATFORMS:
        existing = db.query(Platform).filter(Platform.name == p_data["name"]).first()
        if not existing:
            p = Platform(**p_data)
            db.add(p)
            db.flush()
            platform_map[p_data["name"]] = p
            logger.info(f"Created platform: {p_data['name']}")
        else:
            platform_map[p_data["name"]] = existing
    db.commit()
    return platform_map


def seed_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.username == "demo").first()
    if not user:
        user = User(
            email="demo@wealthos.local",
            username="demo",
            hashed_password=hash_password("Demo@1234"),
            full_name="Demo Investor",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created demo user (username: demo, password: Demo@1234)")
    return user


def seed_assets(db: Session) -> dict:
    asset_map = {}
    for a_data in SAMPLE_ASSETS:
        existing = db.query(Asset).filter(Asset.symbol == a_data["symbol"]).first()
        if not existing:
            a = Asset(**a_data)
            db.add(a)
            db.flush()
            asset_map[a_data["symbol"]] = a
        else:
            asset_map[a_data["symbol"]] = existing
    db.commit()
    return asset_map


def seed_brokerage_sample(db: Session, user: User, platforms: dict, assets: dict) -> None:
    """Create sample brokerage account with realistic transaction history."""
    derayah = platforms.get("Derayah")
    if not derayah:
        return

    acc = db.query(Account).filter(Account.user_id == user.id, Account.name == "Derayah Main").first()
    if acc:
        return  # already seeded

    acc = Account(
        user_id=user.id,
        platform_id=derayah.id,
        name="Derayah Main",
        account_number="DER-00001",
        base_currency="SAR",
        account_type=AccountType.INDIVIDUAL,
    )
    db.add(acc)
    db.flush()

    # Deposit
    db.add(Transaction(
        account_id=acc.id, asset_id=None,
        transaction_type=TransactionType.DEPOSIT,
        trade_date=date(2021, 1, 10), quantity=Decimal("50000"), price=Decimal("1"),
        gross_amount=Decimal("50000"), fees=Decimal("0"), net_amount=Decimal("50000"), currency="SAR",
    ))

    # Buy Aramco
    aramco = assets.get("2222")
    if aramco:
        db.add(Transaction(
            account_id=acc.id, asset_id=aramco.id,
            transaction_type=TransactionType.BUY,
            trade_date=date(2021, 2, 5), quantity=Decimal("500"), price=Decimal("35.20"),
            gross_amount=Decimal("17600"), fees=Decimal("88"), net_amount=Decimal("17688"), currency="SAR",
        ))
        db.add(Transaction(
            account_id=acc.id, asset_id=aramco.id,
            transaction_type=TransactionType.DIVIDEND,
            trade_date=date(2021, 6, 15), quantity=None, price=None,
            gross_amount=Decimal("750"), fees=Decimal("0"), net_amount=Decimal("750"), currency="SAR",
        ))
        db.add(Transaction(
            account_id=acc.id, asset_id=aramco.id,
            transaction_type=TransactionType.SELL,
            trade_date=date(2022, 3, 20), quantity=Decimal("200"), price=Decimal("42.80"),
            gross_amount=Decimal("8560"), fees=Decimal("43"), net_amount=Decimal("8517"), currency="SAR",
        ))

    # Buy Al Rajhi Bank
    alrajhi_bank = assets.get("1120")
    if alrajhi_bank:
        db.add(Transaction(
            account_id=acc.id, asset_id=alrajhi_bank.id,
            transaction_type=TransactionType.BUY,
            trade_date=date(2021, 4, 12), quantity=Decimal("200"), price=Decimal("89.00"),
            gross_amount=Decimal("17800"), fees=Decimal("89"), net_amount=Decimal("17889"), currency="SAR",
        ))
        db.add(Transaction(
            account_id=acc.id, asset_id=alrajhi_bank.id,
            transaction_type=TransactionType.DIVIDEND,
            trade_date=date(2022, 4, 10), quantity=None, price=None,
            gross_amount=Decimal("400"), fees=Decimal("0"), net_amount=Decimal("400"), currency="SAR",
        ))

    db.commit()
    logger.info("Seeded brokerage sample data for Derayah")


def seed_deal_samples(db: Session, user: User, platforms: dict) -> None:
    """Create sample deal-based investments across multiple platforms."""
    deal_samples = [
        {
            "platform": "Tamra",
            "name": "Riyadh Residential Complex - Phase 1",
            "deal_type": DealType.REAL_ESTATE,
            "sector": "Real Estate",
            "start_date": date(2021, 6, 1),
            "maturity_date": date(2024, 6, 1),
            "target_return": Decimal("0.14"),
            "status": DealStatus.ACTIVE,
            "cashflows": [
                (date(2021, 6, 1), Decimal("50000"), CashflowType.INVESTMENT),
                (date(2022, 6, 1), Decimal("7000"), CashflowType.DISTRIBUTION),
                (date(2023, 6, 1), Decimal("7000"), CashflowType.DISTRIBUTION),
                (date(2023, 12, 31), Decimal("52000"), CashflowType.VALUATION),
            ],
        },
        {
            "platform": "Manafa",
            "name": "Tech Startup Equity - Series A",
            "deal_type": DealType.EQUITY,
            "sector": "Technology",
            "start_date": date(2020, 9, 15),
            "maturity_date": None,
            "target_return": Decimal("0.25"),
            "status": DealStatus.ACTIVE,
            "cashflows": [
                (date(2020, 9, 15), Decimal("30000"), CashflowType.INVESTMENT),
                (date(2022, 3, 1), Decimal("5000"), CashflowType.FEE),
                (date(2023, 9, 1), Decimal("38000"), CashflowType.VALUATION),
            ],
        },
        {
            "platform": "Safqah",
            "name": "Jeddah Commercial Property Financing",
            "deal_type": DealType.DEBT,
            "sector": "Real Estate",
            "start_date": date(2022, 1, 10),
            "maturity_date": date(2024, 1, 10),
            "target_return": Decimal("0.12"),
            "status": DealStatus.ACTIVE,
            "cashflows": [
                (date(2022, 1, 10), Decimal("25000"), CashflowType.INVESTMENT),
                (date(2022, 7, 10), Decimal("1500"), CashflowType.DISTRIBUTION),
                (date(2023, 1, 10), Decimal("3000"), CashflowType.DISTRIBUTION),
                (date(2023, 7, 10), Decimal("3000"), CashflowType.DISTRIBUTION),
            ],
        },
        {
            "platform": "Sukuk",
            "name": "Saudi Government Sukuk - Tranche 7",
            "deal_type": DealType.SUKUK,
            "sector": "Government",
            "start_date": date(2019, 10, 1),
            "maturity_date": date(2024, 10, 1),
            "target_return": Decimal("0.065"),
            "status": DealStatus.MATURED,
            "cashflows": [
                (date(2019, 10, 1), Decimal("100000"), CashflowType.INVESTMENT),
                (date(2020, 4, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2020, 10, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2021, 4, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2021, 10, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2022, 4, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2022, 10, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2023, 4, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2023, 10, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2024, 4, 1), Decimal("3250"), CashflowType.DISTRIBUTION),
                (date(2024, 10, 1), Decimal("103250"), CashflowType.REDEMPTION),
            ],
        },
        {
            "platform": "Aseel",
            "name": "Aseel Conservative Portfolio",
            "deal_type": DealType.FUND,
            "sector": "Multi-Asset",
            "start_date": date(2021, 3, 1),
            "maturity_date": None,
            "target_return": Decimal("0.08"),
            "status": DealStatus.ACTIVE,
            "cashflows": [
                (date(2021, 3, 1), Decimal("20000"), CashflowType.INVESTMENT),
                (date(2021, 9, 1), Decimal("10000"), CashflowType.INVESTMENT),
                (date(2022, 3, 1), Decimal("2800"), CashflowType.DISTRIBUTION),
                (date(2023, 3, 1), Decimal("3200"), CashflowType.DISTRIBUTION),
                (date(2023, 12, 31), Decimal("34500"), CashflowType.VALUATION),
            ],
        },
        {
            "platform": "Awaed",
            "name": "Awaed Short-Term Murabaha",
            "deal_type": DealType.MURABAHA,
            "sector": "Fixed Income",
            "start_date": date(2023, 1, 15),
            "maturity_date": date(2024, 1, 15),
            "target_return": Decimal("0.055"),
            "status": DealStatus.MATURED,
            "cashflows": [
                (date(2023, 1, 15), Decimal("15000"), CashflowType.INVESTMENT),
                (date(2023, 7, 15), Decimal("413"), CashflowType.DISTRIBUTION),
                (date(2024, 1, 15), Decimal("15413"), CashflowType.REDEMPTION),
            ],
        },
        {
            "platform": "Tarmeez",
            "name": "Tarmeez Diversified Fund",
            "deal_type": DealType.FUND,
            "sector": "Multi-Asset",
            "start_date": date(2022, 6, 1),
            "maturity_date": None,
            "target_return": Decimal("0.10"),
            "status": DealStatus.ACTIVE,
            "cashflows": [
                (date(2022, 6, 1), Decimal("40000"), CashflowType.INVESTMENT),
                (date(2022, 12, 1), Decimal("2200"), CashflowType.DISTRIBUTION),
                (date(2023, 6, 1), Decimal("4000"), CashflowType.DISTRIBUTION),
                (date(2023, 12, 31), Decimal("42000"), CashflowType.VALUATION),
            ],
        },
        {
            "platform": "Derayah Smart",
            "name": "Derayah Smart Growth Portfolio",
            "deal_type": DealType.FUND,
            "sector": "Equities",
            "start_date": date(2020, 5, 1),
            "maturity_date": None,
            "target_return": Decimal("0.12"),
            "status": DealStatus.ACTIVE,
            "cashflows": [
                (date(2020, 5, 1), Decimal("35000"), CashflowType.INVESTMENT),
                (date(2021, 5, 1), Decimal("10000"), CashflowType.INVESTMENT),
                (date(2022, 5, 1), Decimal("3500"), CashflowType.DISTRIBUTION),
                (date(2023, 5, 1), Decimal("5200"), CashflowType.DISTRIBUTION),
                (date(2023, 12, 31), Decimal("58000"), CashflowType.VALUATION),
            ],
        },
    ]

    for ds in deal_samples:
        platform = platforms.get(ds["platform"])
        if not platform:
            logger.warning(f"Platform '{ds['platform']}' not found, skipping deal.")
            continue

        existing = db.query(Deal).filter(Deal.user_id == user.id, Deal.name == ds["name"]).first()
        if existing:
            continue

        deal = Deal(
            platform_id=platform.id,
            user_id=user.id,
            name=ds["name"],
            deal_type=ds["deal_type"],
            sector=ds.get("sector"),
            currency="SAR",
            start_date=ds.get("start_date"),
            maturity_date=ds.get("maturity_date"),
            target_return=ds.get("target_return"),
            status=ds["status"],
        )
        db.add(deal)
        db.flush()

        for cf_date, amount, cf_type in ds["cashflows"]:
            cf = DealCashflow(
                deal_id=deal.id,
                cashflow_type=cf_type,
                cashflow_date=cf_date,
                amount=amount,
                currency="SAR",
            )
            db.add(cf)

    db.commit()
    logger.info("Seeded deal sample data")


def run_seed() -> None:
    db = SessionLocal()
    try:
        logger.info("Starting seed...")
        platforms = seed_platforms(db)
        user = seed_demo_user(db)
        assets = seed_assets(db)
        seed_brokerage_sample(db, user, platforms, assets)
        seed_deal_samples(db, user, platforms)

        # Seed price history for assets
        from app.jobs.price_sync import seed_historical_prices
        seed_historical_prices(db, years_back=5)

        logger.info("Seed complete!")
        logger.info("Login: username=demo  password=Demo@1234")
    except Exception as e:
        logger.error(f"Seed failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
