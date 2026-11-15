from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.storage.models import Base

engine = create_engine("sqlite:///./mvp_generator.db", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
