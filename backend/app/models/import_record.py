from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, func, JSON
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class ImportStatus(str, enum.Enum):
    PENDING = "pending"
    PREVIEW = "preview"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class RawImport(Base):
    __tablename__ = "raw_imports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv, xlsx
    file_hash = Column(String(64), nullable=True)
    import_status = Column(Enum(ImportStatus), default=ImportStatus.PENDING, nullable=False)
    parser_name = Column(String(100), nullable=False)
    rows_total = Column(Integer, nullable=True)
    rows_imported = Column(Integer, default=0)
    rows_skipped = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", backref="imports")
    platform = relationship("Platform", backref="imports")


class ImportMapping(Base):
    __tablename__ = "import_mappings"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    mapping_name = Column(String(100), nullable=False)
    mapping_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    platform = relationship("Platform", backref="import_mappings")
