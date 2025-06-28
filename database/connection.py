"""
Database connection and session management for the Supply Chain Carbon Analytics Platform.
Provides SQLAlchemy session factory and connection pooling.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import structlog

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class DatabaseManager:
    """Database connection manager with connection pooling and session management."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager with connection URL."""
        self.database_url = database_url or settings.database.url
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with connection pooling."""
        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=settings.database.max_connections,
                max_overflow=settings.database.max_connections * 2,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
                connect_args={
                    "connect_timeout": settings.database.connection_timeout,
                    "application_name": "carbon_analytics"
                },
                echo=settings.debug
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(
                "Database engine initialized",
                database_url=self.database_url.split("@")[-1],  # Don't log credentials
                pool_size=settings.database.max_connections
            )
            
        except Exception as e:
            logger.error("Failed to initialize database engine", error=str(e))
            raise
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.SessionLocal:
            self._initialize_engine()
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic cleanup."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_db_session() as session:
                session.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error("Database connection test failed", error=str(e))
            return False
    
    def close(self) -> None:
        """Close database engine and connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session."""
    with db_manager.get_db_session() as session:
        yield session


def get_db_session() -> Session:
    """Get a database session directly."""
    return db_manager.get_session()


def test_database_connection() -> bool:
    """Test the database connection."""
    return db_manager.test_connection()


def close_database_connections() -> None:
    """Close all database connections."""
    db_manager.close() 