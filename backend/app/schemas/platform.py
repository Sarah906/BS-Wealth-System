from pydantic import BaseModel
from typing import Optional
from app.models.platform import PlatformCategory


class PlatformCreate(BaseModel):
    name: str
    category: PlatformCategory
    country: str = "SA"
    currency: str = "SAR"
    active: bool = True
    description: Optional[str] = None
    website: Optional[str] = None


class PlatformOut(BaseModel):
    id: int
    name: str
    category: PlatformCategory
    country: str
    currency: str
    active: bool
    description: Optional[str]
    website: Optional[str]

    class Config:
        from_attributes = True
