from sqlalchemy import Column, Integer, String, Enum, DateTime, func
import enum

from app.db.base import Base


class AssetType(str, enum.Enum):
    STOCK = "stock"
    ETF = "etf"
    FUND = "fund"
    SUKUK = "sukuk"
    BOND = "bond"
    CASH = "cash"
    REIT = "reit"
    OTHER = "other"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=True)
    isin = Column(String(20), nullable=True, unique=True)
    asset_type = Column(Enum(AssetType), nullable=False, default=AssetType.STOCK)
    currency = Column(String(10), default="SAR", nullable=False)
    country = Column(String(10), nullable=True)
    sector = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
