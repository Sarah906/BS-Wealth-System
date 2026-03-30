from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.cashflow import CashflowType


class DealCashflowCreate(BaseModel):
    deal_id: int
    cashflow_type: CashflowType
    cashflow_date: date
    amount: Decimal
    currency: str = "SAR"
    fx_rate_to_base: Optional[Decimal] = Decimal("1")
    notes: Optional[str] = None
    external_id: Optional[str] = None


class DealCashflowOut(BaseModel):
    id: int
    deal_id: int
    cashflow_type: CashflowType
    cashflow_date: date
    amount: Decimal
    currency: str
    fx_rate_to_base: Optional[Decimal]
    notes: Optional[str]
    external_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
