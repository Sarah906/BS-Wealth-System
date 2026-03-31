from pydantic import BaseModel
from typing import Optional
from app.models.asset import AssetType


class AssetCreate(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    isin: Optional[str] = None
    asset_type: AssetType = AssetType.STOCK
    currency: str = "SAR"
    country: Optional[str] = None
    sector: Optional[str] = None


class AssetOut(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: Optional[str]
    isin: Optional[str]
    asset_type: AssetType
    currency: str
    country: Optional[str]
    sector: Optional[str]

    class Config:
        from_attributes = True
