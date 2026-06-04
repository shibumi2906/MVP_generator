import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.schemas import ExportRequest, SpecBundle
from app.services.bundle_service import build_zip_from_bundle
from app.storage import repository
from app.storage.database import get_db


router = APIRouter()


@router.post("")
def export_bundle(
    payload: ExportRequest, db: Session = Depends(get_db)
) -> StreamingResponse:
    row = repository.get_generation(db, payload.generation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Generation not found")

    bundle = SpecBundle.model_validate_json(row.output_json)
    data = build_zip_from_bundle(bundle)

    filename = f"mvp_bundle_{row.id}.zip"

    def iterfile():
        yield data

    return StreamingResponse(
        iterfile(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )



