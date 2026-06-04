from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models import Generation


def save_generation(
    db: Session,
    generation_id: str,
    created_at: datetime,
    title: str,
    input_json: str,
    output_json: str,
) -> None:
    obj = Generation(
        id=generation_id,
        created_at=created_at,
        title=title,
        input_json=input_json,
        output_json=output_json,
    )
    db.add(obj)
    db.commit()


def get_generation(db: Session, generation_id: str) -> Optional[Generation]:
    stmt = select(Generation).where(Generation.id == generation_id)
    return db.execute(stmt).scalar_one_or_none()


def list_generations(db: Session, limit: int = 5) -> List[Generation]:
    limit = max(1, min(limit, 20))
    stmt = select(Generation).order_by(Generation.created_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars().all())



