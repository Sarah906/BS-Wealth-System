from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class AccountType(str, enum.Enum):
    INDIVIDUAL = "individual"
    JOINT = "joint"
    RETIREMENT = "retirement"
    MARGIN = "margin"
    OTHER = "other"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    account_number = Column(String(100), nullable=True)
    base_currency = Column(String(10), default="SAR", nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.INDIVIDUAL, nullable=False)
    is_active = Column(String(10), default="active", nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="accounts")
    platform = relationship("Platform", backref="accounts")
