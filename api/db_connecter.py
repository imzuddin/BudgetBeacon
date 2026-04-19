from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from settings import settings

class Base(DeclarativeBase):
    pass 

db_engine = create_engine(
    settings.database_url,
    echo=settings.debug,
)

SessionLocal = sessionmaker(
    bind=db_engine,
    autoflush=False,
    autocommit=False, 
    class_=Session,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    print(settings.database_url)

    # using a generator to avoid having to manually close in fastapi router
    try:
        yield db
    finally:
        db.close()