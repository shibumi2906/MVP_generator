from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.schemas import HistoryItem
from app.services.history_service import list_history
from app.storage.database import get_db


router = APIRouter()


@router.get("", response_model=list[HistoryItem])
def history(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[HistoryItem]:
    return list_history(db, limit=limit)



