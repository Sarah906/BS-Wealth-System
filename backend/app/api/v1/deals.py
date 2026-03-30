from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.deal import Deal
from app.models.user import User
from app.schemas.deal import DealCreate, DealOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=List[DealOut])
def list_deals(
    platform_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Deal).filter(Deal.user_id == current_user.id)
    if platform_id:
        q = q.filter(Deal.platform_id == platform_id)
    if status:
        q = q.filter(Deal.status == status)
    return q.order_by(Deal.start_date.desc().nullslast()).all()


@router.get("/{deal_id}", response_model=DealOut)
def get_deal(deal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    d = db.query(Deal).filter(Deal.id == deal_id, Deal.user_id == current_user.id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deal not found")
    return d


@router.post("", response_model=DealOut, status_code=201)
def create_deal(
    payload: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = Deal(**payload.model_dump(), user_id=current_user.id)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.patch("/{deal_id}", response_model=DealOut)
def update_deal(
    deal_id: int,
    payload: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = db.query(Deal).filter(Deal.id == deal_id, Deal.user_id == current_user.id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deal not found")
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(d, field, val)
    db.commit()
    db.refresh(d)
    return d
