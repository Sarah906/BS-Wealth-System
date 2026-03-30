from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)

    def get_by_account(self, account_id: int, skip: int = 0, limit: int = 500) -> List[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.trade_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_asset(self, asset_id: int, account_id: Optional[int] = None) -> List[Transaction]:
        q = self.db.query(Transaction).filter(Transaction.asset_id == asset_id)
        if account_id:
            q = q.filter(Transaction.account_id == account_id)
        return q.order_by(Transaction.trade_date).all()

    def get_by_type(self, account_id: int, txn_type: TransactionType) -> List[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id, Transaction.transaction_type == txn_type)
            .order_by(Transaction.trade_date)
            .all()
        )

    def get_between_dates(self, account_id: int, start: date, end: date) -> List[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.account_id == account_id,
                Transaction.trade_date >= start,
                Transaction.trade_date <= end,
            )
            .order_by(Transaction.trade_date)
            .all()
        )

    def exists_by_external_id(self, account_id: int, external_id: str) -> bool:
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id, Transaction.external_id == external_id)
            .first()
            is not None
        )
