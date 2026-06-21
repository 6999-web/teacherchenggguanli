from app.db.base import Base, engine


def init_db() -> None:
    """Initialize database tables after loading all model metadata."""
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
