from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.schemas import ExportRequest
from app.services.bundle_service import build_zip_from_bundle
from app.services.saved_generation import read_saved_generation
from app.storage import repository
from app.storage.database import get_db

router = APIRouter()


@router.post("")
def export_bundle(payload: ExportRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    row = repository.get_generation(db, payload.generation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Generation not found")

    generation = read_saved_generation(row)
    data = build_zip_from_bundle(generation.result, generation.provenance)

    filename = f"mvp_bundle_{row.id}.zip"

    def iterfile():
        yield data

    return StreamingResponse(
        iterfile(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
