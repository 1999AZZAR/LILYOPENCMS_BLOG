"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Popularity updater — batch-update news read counts into a popularity score.
"""

import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.tasks.context import ContextTask

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=ContextTask, name="app.tasks.popularity_updater.update_popularity_scores")
def update_popularity_scores(self):
    """Recalculate popularity scores for all visible news."""
    from models import News, db
    from sqlalchemy import func

    now = datetime.now(timezone.utc)
    news_items = News.query.filter_by(is_visible=True).all()

    updated = 0
    for item in news_items:
        try:
            # Simple score: read_count boosted by recency
            days_old = max((now - item.created_at.replace(tzinfo=timezone.utc)).days, 1)
            recency_boost = 1.0 / (1.0 + (days_old / 7.0))
            item.popularity_score = (item.read_count or 0) * recency_boost
            updated += 1
        except Exception as e:
            logger.error(f"Failed to update popularity for news {item.id}: {e}")

    if updated:
        db.session.commit()
        logger.info(f"Updated popularity scores for {updated} news items")

    return {"updated": updated, "timestamp": now.isoformat()}
