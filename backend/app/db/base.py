import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

database_url = settings.DATABASE_URL or ""
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {"connect_timeout": 30}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False,
)
logger.info("Using database URL: %s", database_url)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    logger.debug("Database connection checked out")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    logger.debug("Database connection checked in")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error: %s", str(e))
        db.rollback()
        raise
    finally:
        db.close()
