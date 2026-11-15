from sqlalchemy.orm import Session

from app.core.schemas import HistoryItem
from app.services.saved_generation import read_saved_generation
from app.storage import repository


def list_history(db: Session, limit: int = 5) -> list[HistoryItem]:
    rows = repository.list_generations(db, limit=limit)
    return [
        HistoryItem(
            generation_id=row.id,
            created_at=row.created_at,
            title=row.title,
            provenance=read_saved_generation(row).provenance,
        )
        for row in rows
    ]
