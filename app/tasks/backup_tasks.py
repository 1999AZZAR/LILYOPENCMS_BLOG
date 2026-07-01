"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Backup tasks — automated database backups with retention policy.
"""

import os
import shutil
import logging
import subprocess
from datetime import datetime, timezone, timedelta

from app.tasks.celery_app import celery_app
from app.tasks.context import ContextTask

logger = logging.getLogger(__name__)

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "backups")
RETENTION_DAYS = 7


def _apply_retention_policy(backup_dir: str) -> int:
    """Delete backups older than RETENTION_DAYS. Returns count deleted."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    deleted = 0
    if not os.path.exists(backup_dir):
        return 0
    for name in os.listdir(backup_dir):
        path = os.path.join(backup_dir, name)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
            if mtime < cutoff:
                os.remove(path)
                deleted += 1
    return deleted


@celery_app.task(base=ContextTask, name="app.tasks.backup_tasks.scheduled_db_backup")
def scheduled_db_backup():
    """Perform a database backup. Supports SQLite and PostgreSQL."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    db_uri = os.getenv("DATABASE_URI", "")
    success = False

    if "sqlite" in db_uri:
        # SQLite backup — copy file
        db_path = db_uri.replace("sqlite:///", "")
        if os.path.exists(db_path):
            dest = os.path.join(BACKUP_DIR, f"lilycms_{timestamp}.db")
            shutil.copy2(db_path, dest)
            success = True
            logger.info(f"SQLite backup: {dest}")

    elif "postgresql" in db_uri or "psycopg2" in db_uri:
        # PostgreSQL backup — pg_dump
        dest = os.path.join(BACKUP_DIR, f"lilycms_{timestamp}.sql.gz")
        try:
            result = subprocess.run(
                ["pg_dump", "-Z", "9", "-f", dest, db_uri],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0:
                success = True
                logger.info(f"PostgreSQL backup: {dest}")
            else:
                logger.error(f"pg_dump failed: {result.stderr}")
        except FileNotFoundError:
            logger.error("pg_dump not found — install postgresql-client")
        except subprocess.TimeoutExpired:
            logger.error("pg_dump timed out after 300s")

    if success:
        deleted = _apply_retention_policy(BACKUP_DIR)
        logger.info(f"Retention policy: deleted {deleted} old backups")

    return {"success": success, "timestamp": timestamp}
