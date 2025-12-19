from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
  """Create database tables (simple auto-create, not migrations)."""
  # Import models here so that Base.metadata is populated
  from app.models.user import User  # noqa: F401
  from app.models.question import Question  # noqa: F401
  from app.models.answer import Answer  # noqa: F401
  from app.models.vote import Vote  # noqa: F401
  
  Base.metadata.create_all(bind=engine)





