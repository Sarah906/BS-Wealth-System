from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.deal import DealType, DealStatus


class DealCreate(BaseModel):
    platform_id: int
    account_id: Optional[int] = None
    external_reference: Optional[str] = None
    name: str
    deal_type: DealType = DealType.OTHER
    sector: Optional[str] = None
    currency: str = "SAR"
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    target_return: Optional[Decimal] = None
    status: DealStatus = DealStatus.ACTIVE
    notes: Optional[str] = None


class DealOut(BaseModel):
    id: int
    platform_id: int
    user_id: int
    account_id: Optional[int]
    external_reference: Optional[str]
    name: str
    deal_type: DealType
    sector: Optional[str]
    currency: str
    start_date: Optional[date]
    maturity_date: Optional[date]
    target_return: Optional[Decimal]
    status: DealStatus
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
