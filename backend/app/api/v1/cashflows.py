from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cashflow import DealCashflow
from app.models.deal import Deal
from app.models.user import User
from app.schemas.cashflow import DealCashflowCreate, DealCashflowOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/cashflows", tags=["cashflows"])


def _verify_deal_owner(deal_id: int, user_id: int, db: Session) -> Deal:
    d = db.query(Deal).filter(Deal.id == deal_id, Deal.user_id == user_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deal not found")
    return d


@router.get("", response_model=List[DealCashflowOut])
def list_cashflows(
    deal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_deal_ids = [
        d.id for d in db.query(Deal).filter(Deal.user_id == current_user.id).all()
    ]
    q = db.query(DealCashflow).filter(DealCashflow.deal_id.in_(user_deal_ids))
    if deal_id:
        q = q.filter(DealCashflow.deal_id == deal_id)
    return q.order_by(DealCashflow.cashflow_date.desc()).all()


@router.post("", response_model=DealCashflowOut, status_code=201)
def create_cashflow(
    payload: DealCashflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_deal_owner(payload.deal_id, current_user.id, db)
    cf = DealCashflow(**payload.model_dump())
    db.add(cf)
    db.commit()
    db.refresh(cf)
    return cf


@router.delete("/{cashflow_id}", status_code=204)
def delete_cashflow(
    cashflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_deal_ids = [
        d.id for d in db.query(Deal).filter(Deal.user_id == current_user.id).all()
    ]
    cf = (
        db.query(DealCashflow)
        .filter(DealCashflow.id == cashflow_id, DealCashflow.deal_id.in_(user_deal_ids))
        .first()
    )
    if not cf:
        raise HTTPException(status_code=404, detail="Cashflow not found")
    db.delete(cf)
    db.commit()
