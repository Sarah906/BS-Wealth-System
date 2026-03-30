from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    account_id: int
    asset_id: Optional[int] = None
    transaction_type: TransactionType
    trade_date: date
    settlement_date: Optional[date] = None
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    gross_amount: Optional[Decimal] = None
    fees: Decimal = Decimal("0")
    taxes: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    currency: str = "SAR"
    fx_rate_to_base: Optional[Decimal] = Decimal("1")
    notes: Optional[str] = None
    external_id: Optional[str] = None


class TransactionOut(BaseModel):
    id: int
    account_id: int
    asset_id: Optional[int]
    transaction_type: TransactionType
    trade_date: date
    settlement_date: Optional[date]
    quantity: Optional[Decimal]
    price: Optional[Decimal]
    gross_amount: Optional[Decimal]
    fees: Decimal
    taxes: Optional[Decimal]
    net_amount: Optional[Decimal]
    currency: str
    fx_rate_to_base: Optional[Decimal]
    notes: Optional[str]
    external_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
