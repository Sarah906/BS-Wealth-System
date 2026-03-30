from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class PlatformCategory(str, enum.Enum):
    BROKERAGE = "brokerage"
    ROBO = "robo"
    SUKUK = "sukuk"
    DEAL = "deal"
    CROWDFUNDING = "crowdfunding"
    OTHER = "other"


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(Enum(PlatformCategory), nullable=False)
    country = Column(String(10), default="SA", nullable=False)
    currency = Column(String(10), default="SAR", nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    description = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True)
