"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Database optimization — VACUUM, ANALYZE, index maintenance.
"""

import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.tasks.context import ContextTask

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=ContextTask, name="app.tasks.database_optimization.full_maintenance")
def full_maintenance(self):
    """Run a full maintenance cycle: ANALYZE, VACUUM, report stats."""
    from app.extensions import db
    from sqlalchemy import text

    results = {"steps": [], "timestamp": datetime.now(timezone.utc).isoformat()}

    try:
        # Step 1: ANALYZE
        db.session.execute(text("ANALYZE"))
        results["steps"].append("analyze")
        logger.info("ANALYZE completed")

        # Step 2: VACUUM (cannot run inside transaction)
        db.session.execute(text("VACUUM"))
        results["steps"].append("vacuum")
        logger.info("VACUUM completed")

        # Step 3: Table stats
        stats = db.session.execute(text(
            "SELECT schemaname, relname, n_live_tup, n_dead_tup "
            "FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10"
        )).fetchall()
        results["top_dead_tuples"] = [
            {"schema": r[0], "table": r[1], "live": r[2], "dead": r[3]}
            for r in stats
        ]

    except Exception as e:
        logger.error(f"Maintenance failed: {e}")
        results["error"] = str(e)

    return results
