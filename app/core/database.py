from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.config import settings

engine = create_engine(
    url=settings.database_postgres_url,
    echo=settings.DEBUG,
)

session_factory = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
