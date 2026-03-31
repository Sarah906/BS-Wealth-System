"""
Base for all deal/cashflow parsers. Maps rows to DealCashflow records.
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.parsers.base import BaseParser
from app.parsers.brokerage_base import BrokerageParserBase
from app.models.cashflow import DealCashflow, CashflowType
from app.models.deal import Deal


class DealParserBase(BrokerageParserBase):
    """Base for deal cashflow parsers."""

    column_map: Dict[str, str] = {
        "date": "date",
        "deal_name": "deal_name",
        "deal_ref": "deal_ref",
        "type": "type",
        "amount": "amount",
        "currency": "currency",
        "notes": "notes",
    }

    cashflow_type_map: Dict[str, str] = {
        "investment": "INVESTMENT",
        "invest": "INVESTMENT",
        "distribution": "DISTRIBUTION",
        "dist": "DISTRIBUTION",
        "return": "DISTRIBUTION",
        "redemption": "REDEMPTION",
        "redeem": "REDEMPTION",
        "exit": "REDEMPTION",
        "fee": "FEE",
        "valuation": "VALUATION",
        "nav": "VALUATION",
    }

    def _map_cashflow_type(self, raw: str) -> Optional[CashflowType]:
        mapped = self.cashflow_type_map.get(raw.lower().strip())
        if mapped:
            try:
                return CashflowType(mapped)
            except ValueError:
                pass
        try:
            return CashflowType(raw.upper().strip())
        except ValueError:
            return None

    def _get_or_create_deal(
        self, db: Session, deal_name: str, deal_ref: str, platform_id: int, user_id: int
    ) -> Optional[Deal]:
        if not deal_name:
            return None
        deal = db.query(Deal).filter(
            Deal.user_id == user_id,
            Deal.name == deal_name,
        ).first()
        if not deal:
            from app.models.deal import DealType, DealStatus
            deal = Deal(
                user_id=user_id,
                platform_id=platform_id,
                name=deal_name,
                external_reference=deal_ref or None,
                deal_type=DealType.OTHER,
                status=DealStatus.ACTIVE,
                currency="SAR",
            )
            db.add(deal)
            db.flush()
        return deal

    def run(self, file_path: str, db: Session, raw_import_id: int,
            account_id: Optional[int], user_id: int) -> Dict[str, Any]:
        # Get platform_id from raw import record
        from app.models.import_record import RawImport
        ri = db.query(RawImport).filter(RawImport.id == raw_import_id).first()
        platform_id = ri.platform_id if ri else 1

        df = self._read_file(file_path)
        total = len(df)
        imported = 0
        skipped = 0
        failed = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                mapped = self._map_row(row.to_dict())
                cf_date = self._parse_date(mapped.get("date"))
                if not cf_date:
                    skipped += 1
                    continue

                cf_type = self._map_cashflow_type(str(mapped.get("type", "")))
                if not cf_type:
                    errors.append(f"Row {idx}: unknown cashflow type '{mapped.get('type')}'")
                    failed += 1
                    continue

                deal_name = str(mapped.get("deal_name", "")).strip()
                deal_ref = str(mapped.get("deal_ref", "")).strip()
                deal = self._get_or_create_deal(db, deal_name, deal_ref, platform_id, user_id)
                if not deal:
                    errors.append(f"Row {idx}: no deal name provided")
                    failed += 1
                    continue

                amount = self._parse_decimal(mapped.get("amount"))
                currency = str(mapped.get("currency", "SAR")).strip() or "SAR"
                notes = str(mapped.get("notes", "")).strip() or None

                cf = DealCashflow(
                    deal_id=deal.id,
                    cashflow_type=cf_type,
                    cashflow_date=cf_date,
                    amount=amount,
                    currency=currency,
                    notes=notes,
                    raw_import_id=raw_import_id,
                )
                db.add(cf)
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
