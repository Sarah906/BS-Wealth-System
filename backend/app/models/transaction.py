from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Numeric, Enum, Text, func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base
from app.models.import_record import RawImport  # noqa: F401


class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    FEE = "FEE"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    FX = "FX"
    SPLIT = "SPLIT"
    BONUS = "BONUS"
    RIGHTS = "RIGHTS"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    trade_date = Column(Date, nullable=False, index=True)
    settlement_date = Column(Date, nullable=True)
    quantity = Column(Numeric(18, 6), nullable=True)
    price = Column(Numeric(18, 6), nullable=True)
    gross_amount = Column(Numeric(18, 4), nullable=True)
    fees = Column(Numeric(18, 4), default=0, nullable=False)
    taxes = Column(Numeric(18, 4), default=0, nullable=True)
    net_amount = Column(Numeric(18, 4), nullable=True)
    currency = Column(String(10), default="SAR", nullable=False)
    fx_rate_to_base = Column(Numeric(18, 6), default=1, nullable=True)
    notes = Column(Text, nullable=True)
    external_id = Column(String(100), nullable=True, index=True)
    raw_import_id = Column(Integer, ForeignKey("raw_imports.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", backref="transactions")
    asset = relationship("Asset", backref="transactions")
    raw_import = relationship("RawImport", backref="transactions")
