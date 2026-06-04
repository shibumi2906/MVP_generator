from typing import List

from sqlalchemy.orm import Session

from app.core.schemas import HistoryItem
from app.storage import repository


def list_history(db: Session, limit: int = 5) -> List[HistoryItem]:
    rows = repository.list_generations(db, limit=limit)
    return [
        HistoryItem(
            generation_id=row.id,
            created_at=row.created_at,
            title=row.title,
        )
        for row in rows
    ]



