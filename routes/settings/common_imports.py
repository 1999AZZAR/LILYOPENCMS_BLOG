"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import time
import logging
from functools import wraps
from flask import render_template, request, redirect, url_for, abort, current_app, jsonify, flash
from flask_login import current_user
from shared.auth.decorators import login_required
from datetime import datetime
from sqlalchemy.exc import OperationalError, PendingRollbackError
from models import (
    db, User, News, Category, Album, AlbumChapter, PrivacyPolicy, MediaGuideline, VisiMisi,
    PedomanHak, Penyangkalan, ContactDetail, TeamMember, YouTubeVideo, UserRole, RootSEO
)

logger = logging.getLogger(__name__)

def retry_on_db_lock(max_retries=3, delay=0.1, backoff=2):
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
                    if "database is locked" in str(e).lower() or "locked" in str(e).lower():
                        if attempt < max_retries:
                            logger.warning(f"Database lock detected in {func.__name__}, attempt {attempt + 1}/{max_retries + 1}. Retrying in {current_delay}s...")
                            time.sleep(current_delay)
                            current_delay *= backoff
                            continue
                        else:
                            logger.error(f"Database lock persisted after {max_retries + 1} attempts in {func.__name__}: {e}")
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator

def safe_commit(session, max_retries=3):
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
                session.rollback()
                raise
    return False

class DatabaseConnectionManager:
    @staticmethod
    def execute_with_retry(query_func, max_retries=3, *args, **kwargs):
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
                    raise
        raise last_exception
