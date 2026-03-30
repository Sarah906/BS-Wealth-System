from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.platform import Platform
from app.models.user import User
from app.schemas.platform import PlatformCreate, PlatformOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("", response_model=List[PlatformOut])
def list_platforms(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Platform).filter(Platform.active == True).all()


@router.get("/{platform_id}", response_model=PlatformOut)
def get_platform(platform_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    p = db.query(Platform).filter(Platform.id == platform_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Platform not found")
    return p


@router.post("", response_model=PlatformOut, status_code=201)
def create_platform(
    payload: PlatformCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")
    existing = db.query(Platform).filter(Platform.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Platform already exists")
    p = Platform(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
