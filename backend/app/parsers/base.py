"""
Base parser interface. All parsers must implement this contract.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session


class BaseParser(ABC):
    """Abstract base for all import parsers."""

    name: str = "base"
    supported_file_types: List[str] = ["csv"]

    @abstractmethod
    def preview(self, file_path: str, max_rows: int = 20) -> List[Dict[str, Any]]:
        """Parse the file and return a list of row dicts for preview (no DB writes)."""

    @abstractmethod
    def run(
        self,
        file_path: str,
        db: Session,
        raw_import_id: int,
        account_id: Optional[int],
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Execute the full import. Write records to DB.
        Returns dict: {rows_total, rows_imported, rows_skipped, rows_failed, errors: []}
        """

    def _read_file(self, file_path: str) -> "pd.DataFrame":
        import pandas as pd
        if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            return pd.read_excel(file_path)
        return pd.read_csv(file_path, encoding="utf-8-sig")
