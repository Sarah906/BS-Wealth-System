from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Numeric, Enum, Text, func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class CashflowType(str, enum.Enum):
    INVESTMENT = "INVESTMENT"
    DISTRIBUTION = "DISTRIBUTION"
    REDEMPTION = "REDEMPTION"
    FEE = "FEE"
    VALUATION = "VALUATION"
    PROJECTED = "PROJECTED"


class DealCashflow(Base):
    __tablename__ = "deal_cashflows"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    cashflow_type = Column(Enum(CashflowType), nullable=False)
    cashflow_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(10), default="SAR", nullable=False)
    fx_rate_to_base = Column(Numeric(18, 6), default=1, nullable=True)
    notes = Column(Text, nullable=True)
    external_id = Column(String(100), nullable=True)
    raw_import_id = Column(Integer, ForeignKey("raw_imports.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    deal = relationship("Deal", back_populates="cashflows")
    raw_import = relationship("RawImport", backref="cashflows")
