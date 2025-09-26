from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from .config import settings


class Base(DeclarativeBase):
    pass


# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "check_same_thread": False,
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Dependency function to get database session.
    Yields database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()