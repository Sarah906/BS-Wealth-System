from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (
        UniqueConstraint("asset_id", "date", name="uq_price_asset_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(18, 6), nullable=True)
    high = Column(Numeric(18, 6), nullable=True)
    low = Column(Numeric(18, 6), nullable=True)
    close = Column(Numeric(18, 6), nullable=False)
    volume = Column(BigInteger, nullable=True)
    source = Column(String(50), default="mock", nullable=False)

    asset = relationship("Asset", backref="prices")
