"""
Base for all brokerage parsers. Maps rows to Transaction records.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.parsers.base import BaseParser
from app.models.transaction import Transaction, TransactionType
from app.models.asset import Asset, AssetType


class BrokerageParserBase(BaseParser):
    """
    Subclass this and override column_map to build a brokerage parser quickly.
    column_map maps standardized keys to actual CSV column names.
    """

    # Override in subclass
    column_map: Dict[str, str] = {
        "date": "date",
        "symbol": "symbol",
        "name": "name",
        "type": "type",
        "quantity": "quantity",
        "price": "price",
        "fees": "fees",
        "net_amount": "net_amount",
        "currency": "currency",
    }

    # Override transaction type mapping
    type_map: Dict[str, str] = {
        "buy": "BUY",
        "sell": "SELL",
        "dividend": "DIVIDEND",
        "fee": "FEE",
        "deposit": "DEPOSIT",
        "withdrawal": "WITHDRAWAL",
    }

    def _map_row(self, row: Dict) -> Dict:
        """Map raw CSV row to standardized dict."""
        mapped = {}
        for std_key, col_name in self.column_map.items():
            mapped[std_key] = row.get(col_name, "")
        return mapped

    def _parse_date(self, val) -> Optional[date]:
        if not val or str(val).strip() in ("", "nan", "NaT"):
            return None
        if isinstance(val, date):
            return val
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y%m%d"):
            try:
                return datetime.strptime(str(val).strip(), fmt).date()
            except ValueError:
                continue
        return None

    def _parse_decimal(self, val) -> Decimal:
        if val is None or str(val).strip() in ("", "nan", "-"):
            return Decimal("0")
        cleaned = str(val).replace(",", "").replace("%", "").strip()
        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal("0")

    def _get_or_create_asset(self, db: Session, symbol: str, name: str, currency: str) -> Optional[Asset]:
        if not symbol:
            return None
        asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
        if not asset:
            asset = Asset(
                symbol=symbol.upper(),
                name=name or symbol.upper(),
                asset_type=AssetType.STOCK,
                currency=currency or "SAR",
            )
            db.add(asset)
            db.flush()
        return asset

    def _map_txn_type(self, raw_type: str) -> Optional[TransactionType]:
        mapped = self.type_map.get(raw_type.lower().strip())
        if mapped:
            try:
                return TransactionType(mapped)
            except ValueError:
                pass
        # Try direct match
        try:
            return TransactionType(raw_type.upper().strip())
        except ValueError:
            return None

    def preview(self, file_path: str, max_rows: int = 20) -> List[Dict[str, Any]]:
        df = self._read_file(file_path)
        rows = []
        for _, row in df.head(max_rows).iterrows():
            mapped = self._map_row(row.to_dict())
            rows.append(mapped)
        return rows

    def run(self, file_path: str, db: Session, raw_import_id: int,
            account_id: Optional[int], user_id: int) -> Dict[str, Any]:
        df = self._read_file(file_path)
        total = len(df)
        imported = 0
        skipped = 0
        failed = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                mapped = self._map_row(row.to_dict())
                trade_date = self._parse_date(mapped.get("date"))
                if not trade_date:
                    skipped += 1
                    continue

                txn_type = self._map_txn_type(str(mapped.get("type", "")))
                if not txn_type:
                    errors.append(f"Row {idx}: unknown transaction type '{mapped.get('type')}'")
                    failed += 1
                    continue

                symbol = str(mapped.get("symbol", "")).strip()
                name = str(mapped.get("name", "")).strip()
                currency = str(mapped.get("currency", "SAR")).strip() or "SAR"
                asset = self._get_or_create_asset(db, symbol, name, currency) if symbol else None

                qty = self._parse_decimal(mapped.get("quantity"))
                price = self._parse_decimal(mapped.get("price"))
                fees = self._parse_decimal(mapped.get("fees"))
                net_amount = self._parse_decimal(mapped.get("net_amount"))
                gross = price * qty if price and qty else None

                txn = Transaction(
                    account_id=account_id,
                    asset_id=asset.id if asset else None,
                    transaction_type=txn_type,
                    trade_date=trade_date,
                    quantity=qty if qty else None,
                    price=price if price else None,
                    gross_amount=gross,
                    fees=fees,
                    net_amount=net_amount if net_amount else None,
                    currency=currency,
                    raw_import_id=raw_import_id,
                )
                db.add(txn)
                imported += 1

            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                failed += 1

        db.commit()
        return {
            "rows_total": total,
            "rows_imported": imported,
            "rows_skipped": skipped,
            "rows_failed": failed,
            "errors": errors,
        }
