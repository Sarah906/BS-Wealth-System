"""
Daily price sync job: fetches latest prices for all active assets and persists them.
Also syncs FX rates for all used currency pairs.
"""
import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.price import PriceHistory
from app.models.fx_rate import FXRate
from app.models.transaction import Transaction
from app.services.market_data_service import market_data_service

logger = logging.getLogger(__name__)

COMMON_FX_PAIRS = [
    ("USD", "SAR"),
    ("SAR", "USD"),
    ("EUR", "SAR"),
    ("GBP", "SAR"),
]


def sync_prices_for_asset(db: Session, asset: Asset, start: date, end: date) -> int:
    """Fetch and upsert price history for one asset. Returns number of rows written."""
    history = market_data_service.get_history(asset.symbol, start, end)
    count = 0
    for point in history:
        # Upsert on (asset_id, date)
        stmt = (
            insert(PriceHistory)
            .values(
                asset_id=asset.id,
                date=point.date,
                open=point.open,
                high=point.high,
                low=point.low,
                close=point.close,
                volume=point.volume,
                source="mock",
            )
            .on_conflict_do_update(
                constraint="uq_price_asset_date",
                set_={"close": point.close, "open": point.open, "high": point.high, "low": point.low},
            )
        )
        db.execute(stmt)
        count += 1
    db.commit()
    return count


def sync_fx_rates(db: Session, on_date: date) -> None:
    for from_ccy, to_ccy in COMMON_FX_PAIRS:
        rate = market_data_service.get_fx_rate(from_ccy, to_ccy, on_date)
        if rate is None:
            continue
        stmt = (
            insert(FXRate)
            .values(date=on_date, from_currency=from_ccy, to_currency=to_ccy, rate=rate, source="mock")
            .on_conflict_do_update(
                constraint="uq_fx_date_pair",
                set_={"rate": rate},
            )
        )
        db.execute(stmt)
    db.commit()


def run_daily_price_sync() -> None:
    """Main entry point for the daily price sync job."""
    db = SessionLocal()
    try:
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Get all assets that have at least one transaction
        active_asset_ids = (
            db.query(Transaction.asset_id)
            .filter(Transaction.asset_id.isnot(None))
            .distinct()
            .all()
        )
        asset_ids = [r[0] for r in active_asset_ids]
        assets = db.query(Asset).filter(Asset.id.in_(asset_ids)).all()

        total_written = 0
        for asset in assets:
            try:
                # Find the last synced date for this asset
                last = (
                    db.query(PriceHistory)
                    .filter(PriceHistory.asset_id == asset.id)
                    .order_by(PriceHistory.date.desc())
                    .first()
                )
                sync_start = (last.date + timedelta(days=1)) if last else date(2019, 1, 1)
                if sync_start > yesterday:
                    continue
                count = sync_prices_for_asset(db, asset, sync_start, yesterday)
                total_written += count
                logger.info(f"Synced {count} price rows for {asset.symbol}")
            except Exception as e:
                logger.error(f"Failed to sync prices for {asset.symbol}: {e}")

        sync_fx_rates(db, yesterday)
        logger.info(f"Daily price sync complete. {total_written} rows written.")
    finally:
        db.close()


def seed_historical_prices(db: Session, years_back: int = 5) -> None:
    """Seed historical price data for all known assets. Run once during setup."""
    end = date.today()
    start = date(end.year - years_back, 1, 1)

    assets = db.query(Asset).all()
    for asset in assets:
        existing = db.query(PriceHistory).filter(PriceHistory.asset_id == asset.id).count()
        if existing > 0:
            continue
        count = sync_prices_for_asset(db, asset, start, end)
        logger.info(f"Seeded {count} price rows for {asset.symbol}")

    sync_fx_rates(db, end)
