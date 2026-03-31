from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.account import AccountType


class AccountCreate(BaseModel):
    platform_id: int
    name: str
    account_number: Optional[str] = None
    base_currency: str = "SAR"
    account_type: AccountType = AccountType.INDIVIDUAL
    notes: Optional[str] = None


class AccountOut(BaseModel):
    id: int
    user_id: int
    platform_id: int
    name: str
    account_number: Optional[str]
    base_currency: str
    account_type: AccountType
    is_active: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
