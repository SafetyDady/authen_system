"""
Database connection and session management.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 20,
        },
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency to get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


# Database event listeners
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragma for better performance and foreign key support."""
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


@event.listens_for(SessionLocal, "after_transaction_end")
def restart_savepoint(session, transaction):
    """Restart savepoint after transaction end."""
    if transaction.nested and not transaction._parent.nested:
        session.expire_all()


class DatabaseManager:
    """Database management utilities."""
    
    @staticmethod
    def health_check() -> dict:
        """Check database connection health."""
        try:
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            return {
                "status": "healthy",
                "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
            }
    
    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information."""
        return {
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "engine_echo": settings.DEBUG,
        }


# Global database manager instance
db_manager = DatabaseManager()

