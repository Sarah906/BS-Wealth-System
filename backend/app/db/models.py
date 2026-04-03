# Import all models here so Alembic can detect them for migrations.
# This module should only be imported by alembic/env.py and the test/seed helpers.
from app.models.user import User  # noqa: F401
from app.models.platform import Platform  # noqa: F401
from app.models.account import Account  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.deal import Deal  # noqa: F401
from app.models.import_record import RawImport, ImportMapping  # noqa: F401 — must be before Transaction
from app.models.transaction import Transaction  # noqa: F401
from app.models.cashflow import DealCashflow  # noqa: F401
from app.models.price import PriceHistory  # noqa: F401
from app.models.fx_rate import FXRate  # noqa: F401
