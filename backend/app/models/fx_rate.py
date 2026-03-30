from sqlalchemy import Column, Integer, String, Date, Numeric, UniqueConstraint

from app.db.base import Base


class FXRate(Base):
    __tablename__ = "fx_rates"
    __table_args__ = (
        UniqueConstraint("date", "from_currency", "to_currency", name="uq_fx_date_pair"),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    from_currency = Column(String(10), nullable=False)
    to_currency = Column(String(10), nullable=False)
    rate = Column(Numeric(18, 6), nullable=False)
    source = Column(String(50), default="mock", nullable=False)
