from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.user import User
from app.schemas.asset import AssetCreate, AssetOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=List[AssetOut])
def list_assets(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Asset)
    if search:
        q = q.filter(
            Asset.symbol.ilike(f"%{search}%") | Asset.name.ilike(f"%{search}%")
        )
    return q.limit(200).all()


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    a = db.query(Asset).filter(Asset.id == asset_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    return a


@router.post("", response_model=AssetOut, status_code=201)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if payload.isin:
        existing = db.query(Asset).filter(Asset.isin == payload.isin).first()
        if existing:
            raise HTTPException(status_code=400, detail="Asset with this ISIN already exists")

    # Deduplicate by symbol+exchange
    existing = db.query(Asset).filter(
        Asset.symbol == payload.symbol,
        Asset.exchange == payload.exchange,
    ).first()
    if existing:
        return existing

    a = Asset(**payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a
