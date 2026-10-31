from typing import Generator, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.core.config import settings
from backend.core.logging import logger
from backend.models.base import Base
# Ensure all models are imported so Base.metadata knows about them
import backend.models  # noqa: F401

_engine = None
_SessionLocal = None
_db_connected: bool = False
_db_error: Optional[str] = None

MYSQL_SETUP_INSTRUCTIONS = """
MySQL Setup Instructions for F.R.I.D.A.Y.:
1. Ensure your local MySQL server is running (e.g., MySQL 8.0).
2. Create the target database:
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS friday_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
3. Update your credentials in the `.env` file:
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_DATABASE=friday_db
   MYSQL_USER=root
   MYSQL_PASSWORD=your_actual_password
4. Restart the FastAPI service or refresh the connection in Settings.
"""

def init_db() -> bool:
    """
    Attempts to initialize MySQL engine and create tables.
    Returns True if successfully connected and tables verified, False otherwise.
    Does NOT silently switch to SQLite or crash unhandled.
    """
    global _engine, _SessionLocal, _db_connected, _db_error
    try:
        logger.info(f"Connecting to MySQL at {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}...")
        _engine = create_engine(
            settings.mysql_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args={"connect_timeout": 5}
        )
        # Test connection
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create tables
        Base.metadata.create_all(bind=_engine)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        _db_connected = True
        _db_error = None
        logger.info("Successfully connected to MySQL and verified schema tables.")
        return True
    except Exception as e:
        _db_connected = False
        _db_error = str(e)
        _engine = None
        _SessionLocal = None
        logger.warning(f"MySQL connection failed: {_db_error}")
        return False

def get_db_status() -> Dict[str, Any]:
    """Returns detailed status of MySQL connectivity without exposing passwords."""
    return {
        "connected": _db_connected,
        "host": settings.mysql_host,
        "port": settings.mysql_port,
        "database": settings.mysql_database,
        "user": settings.mysql_user,
        "error": _db_error,
        "setup_guide": MYSQL_SETUP_INSTRUCTIONS if not _db_connected else "Connected and operational."
    }

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    from fastapi import HTTPException
    if not _db_connected or _SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "MySQL Database connection is not available.",
                "error": _db_error,
                "host": f"{settings.mysql_host}:{settings.mysql_port}",
                "database": settings.mysql_database,
                "instructions": MYSQL_SETUP_INSTRUCTIONS
            }
        )
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
