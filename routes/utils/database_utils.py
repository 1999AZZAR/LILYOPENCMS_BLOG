"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Database utilities for handling SQLite concurrency issues and connection management.
"""

import time
import logging
from functools import wraps
from sqlalchemy.exc import OperationalError, PendingRollbackError
from flask import current_app

logger = logging.getLogger(__name__)

def retry_on_db_lock(max_retries=3, delay=0.1, backoff=2):
    """
    Decorator to retry database operations on lock errors.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, PendingRollbackError) as e:
                    last_exception = e

                    # Check if it's a database lock error
                    if "database is locked" in str(e).lower() or "locked" in str(e).lower():
                        if attempt < max_retries:
                            logger.warning(f"Database lock detected in {func.__name__}, attempt {attempt + 1}/{max_retries + 1}. Retrying in {current_delay}s...")
                            time.sleep(current_delay)
                            current_delay *= backoff
                            continue
                        else:
                            logger.error(f"Database lock persisted after {max_retries + 1} attempts in {func.__name__}: {e}")
                    else:
                        # Not a lock error, re-raise immediately
                        raise

            # If we get here, all retries failed
            raise last_exception

        return wrapper
    return decorator

def safe_commit(session, max_retries=3):
    """
    Safely commit a database session with retry logic.

    Args:
        session: SQLAlchemy session to commit
        max_retries: Maximum number of retry attempts

    Returns:
        bool: True if commit succeeded, False otherwise
    """
    current_delay = 0.1
    backoff = 2

    for attempt in range(max_retries + 1):
        try:
            session.commit()
            return True
        except (OperationalError, PendingRollbackError) as e:
            if "database is locked" in str(e).lower() or "locked" in str(e).lower():
                if attempt < max_retries:
                    logger.warning(f"Commit failed due to database lock, attempt {attempt + 1}/{max_retries + 1}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    continue
                else:
                    logger.error(f"Commit failed persistently after {max_retries + 1} attempts: {e}")
                    session.rollback()
                    return False
            else:
                # Not a lock error, rollback and re-raise
                session.rollback()
                raise

    return False

class DatabaseConnectionManager:
    """Manages database connections with proper error handling."""

    @staticmethod
    def execute_with_retry(query_func, max_retries=3, *args, **kwargs):
        """
        Execute a database query function with retry logic.

        Args:
            query_func: Function that performs the database query
            max_retries: Maximum retry attempts
            *args, **kwargs: Arguments to pass to query_func

        Returns:
            Result of query_func if successful

        Raises:
            Last exception encountered if all retries fail
        """
        current_delay = 0.1
        backoff = 2
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return query_func(*args, **kwargs)
            except (OperationalError, PendingRollbackError) as e:
                last_exception = e

                if "database is locked" in str(e).lower() or "locked" in str(e).lower():
                    if attempt < max_retries:
                        logger.warning(f"Query failed due to database lock, attempt {attempt + 1}/{max_retries + 1}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                        continue
                    else:
                        logger.error(f"Query failed persistently after {max_retries + 1} attempts: {e}")
                else:
                    # Not a lock error, re-raise immediately
                    raise

        # All retries failed
        raise last_exception

    @staticmethod
    def configure_sqlite_for_concurrency():
        """
        Configure SQLite connection for better concurrency handling.
        This should be called when setting up the database engine.
        """
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine
            import sqlite3

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                if isinstance(dbapi_connection, sqlite3.Connection):
                    # Enable WAL mode for better concurrency
                    dbapi_connection.execute('PRAGMA journal_mode=WAL')
                    # Set busy timeout to 30 seconds
                    dbapi_connection.execute('PRAGMA busy_timeout=30000')
                    # Enable foreign keys
                    dbapi_connection.execute('PRAGMA foreign_keys=ON')
                    # Set synchronous mode to NORMAL for better performance
                    dbapi_connection.execute('PRAGMA synchronous=NORMAL')

            logger.info("SQLite concurrency configuration applied")

        except Exception as e:
            logger.error(f"Failed to configure SQLite concurrency: {e}")

# Initialize SQLite configuration when module is imported
DatabaseConnectionManager.configure_sqlite_for_concurrency()