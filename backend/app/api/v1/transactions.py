from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _verify_account_owner(account_id: int, user_id: int, db: Session) -> Account:
    acc = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    account_id: Optional[int] = Query(None),
    asset_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only return transactions for accounts owned by this user
    user_account_ids = [
        a.id for a in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    q = db.query(Transaction).filter(Transaction.account_id.in_(user_account_ids))
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    if asset_id:
        q = q.filter(Transaction.asset_id == asset_id)
    return q.order_by(Transaction.trade_date.desc()).offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_account_ids = [
        a.id for a in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    t = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.account_id.in_(user_account_ids))
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return t


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_account_owner(payload.account_id, current_user.id, db)
    t = Transaction(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_account_ids = [
        a.id for a in db.query(Account).filter(Account.user_id == current_user.id).all()
    ]
    t = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.account_id.in_(user_account_ids))
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(t)
    db.commit()
