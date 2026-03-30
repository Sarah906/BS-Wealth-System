"""
File import endpoints: upload, preview, run import, list imports.
"""
import os
import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.import_record import RawImport, ImportStatus
from app.models.platform import Platform
from app.api.deps import get_current_user
from app.core.config import settings
from app.parsers import get_parser

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("", response_model=List[dict])
def list_imports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    imports = db.query(RawImport).filter(RawImport.user_id == current_user.id).order_by(RawImport.created_at.desc()).all()
    return [
        {
            "id": i.id,
            "filename": i.filename,
            "platform_id": i.platform_id,
            "file_type": i.file_type,
            "import_status": i.import_status.value,
            "parser_name": i.parser_name,
            "rows_total": i.rows_total,
            "rows_imported": i.rows_imported,
            "rows_failed": i.rows_failed,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "completed_at": i.completed_at.isoformat() if i.completed_at else None,
            "error_log": i.error_log,
        }
        for i in imports
    ]


@router.post("/upload")
async def upload_import(
    file: UploadFile = File(...),
    platform_id: int = Form(...),
    account_id: Optional[int] = Form(None),
    parser_name: str = Form("generic_brokerage"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a file for import. Returns a raw_import_id for preview/run."""
    platform = db.query(Platform).filter(Platform.id == platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    file_hash = hashlib.sha256(content).hexdigest()
    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{current_user.id}_{file_hash[:12]}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    raw_import = RawImport(
        user_id=current_user.id,
        platform_id=platform_id,
        account_id=account_id,
        filename=saved_filename,
        file_type=ext,
        file_hash=file_hash,
        import_status=ImportStatus.PENDING,
        parser_name=parser_name,
    )
    db.add(raw_import)
    db.commit()
    db.refresh(raw_import)
    return {"raw_import_id": raw_import.id, "filename": saved_filename, "file_hash": file_hash}


@router.get("/{import_id}/preview")
def preview_import(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview parsed rows before committing import."""
    raw_import = db.query(RawImport).filter(
        RawImport.id == import_id, RawImport.user_id == current_user.id
    ).first()
    if not raw_import:
        raise HTTPException(status_code=404, detail="Import not found")

    file_path = os.path.join(settings.UPLOAD_DIR, raw_import.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Upload file not found on disk")

    parser = get_parser(raw_import.parser_name)
    if not parser:
        raise HTTPException(status_code=400, detail=f"Unknown parser: {raw_import.parser_name}")

    try:
        preview = parser.preview(file_path, max_rows=20)
        raw_import.import_status = ImportStatus.PREVIEW
        db.commit()
        return {"rows": preview, "total_preview_rows": len(preview)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")


@router.post("/{import_id}/run")
def run_import(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute the import and persist records to DB."""
    raw_import = db.query(RawImport).filter(
        RawImport.id == import_id, RawImport.user_id == current_user.id
    ).first()
    if not raw_import:
        raise HTTPException(status_code=404, detail="Import not found")

    if raw_import.import_status == ImportStatus.COMPLETED:
        return {"message": "Already imported", "rows_imported": raw_import.rows_imported}

    file_path = os.path.join(settings.UPLOAD_DIR, raw_import.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Upload file not found on disk")

    parser = get_parser(raw_import.parser_name)
    if not parser:
        raise HTTPException(status_code=400, detail=f"Unknown parser: {raw_import.parser_name}")

    raw_import.import_status = ImportStatus.PROCESSING
    db.commit()

    try:
        result = parser.run(
            file_path=file_path,
            db=db,
            raw_import_id=raw_import.id,
            account_id=raw_import.account_id,
            user_id=current_user.id,
        )
        raw_import.import_status = ImportStatus.COMPLETED if result["rows_failed"] == 0 else ImportStatus.PARTIAL
        raw_import.rows_total = result["rows_total"]
        raw_import.rows_imported = result["rows_imported"]
        raw_import.rows_skipped = result["rows_skipped"]
        raw_import.rows_failed = result["rows_failed"]
        raw_import.error_log = "\n".join(result.get("errors", []))
        raw_import.completed_at = datetime.utcnow()
        db.commit()
        return result
    except Exception as e:
        raw_import.import_status = ImportStatus.FAILED
        raw_import.error_log = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
