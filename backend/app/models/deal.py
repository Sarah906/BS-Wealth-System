from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Numeric, Enum, func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class DealType(str, enum.Enum):
    REAL_ESTATE = "real_estate"
    EQUITY = "equity"
    DEBT = "debt"
    SUKUK = "sukuk"
    MURABAHA = "murabaha"
    FUND = "fund"
    COMMODITY = "commodity"
    OTHER = "other"


class DealStatus(str, enum.Enum):
    ACTIVE = "active"
    EXITED = "exited"
    DEFAULTED = "defaulted"
    MATURED = "matured"
    PENDING = "pending"


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)
    external_reference = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    deal_type = Column(Enum(DealType), nullable=False, default=DealType.OTHER)
    sector = Column(String(100), nullable=True)
    currency = Column(String(10), default="SAR", nullable=False)
    start_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    target_return = Column(Numeric(8, 4), nullable=True)  # e.g. 0.12 = 12%
    status = Column(Enum(DealStatus), default=DealStatus.ACTIVE, nullable=False)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    platform = relationship("Platform", backref="deals")
    user = relationship("User", backref="deals")
    account = relationship("Account", backref="deals")
    cashflows = relationship("DealCashflow", back_populates="deal", lazy="dynamic")
