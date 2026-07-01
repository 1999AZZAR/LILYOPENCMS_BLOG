"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Scheduled publish — auto-publish content when its scheduled date arrives.
"""

import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.tasks.context import ContextTask

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=ContextTask, name="app.tasks.scheduled_publish.publish_scheduled_chapters")
def publish_scheduled_chapters(self):
    """Find and publish chapters whose scheduled_publish_date has passed."""
    from models import AlbumChapter, db

    now = datetime.now(timezone.utc)
    chapters = AlbumChapter.query.filter(
        AlbumChapter.scheduled_publish_date.isnot(None),
        AlbumChapter.scheduled_publish_date <= now,
        AlbumChapter.is_visible == False,
    ).all()

    published = 0
    for chapter in chapters:
        try:
            chapter.is_visible = True
            chapter.published_at = now
            published += 1
        except Exception as e:
            logger.error(f"Failed to publish chapter {chapter.id}: {e}")

    if published:
        db.session.commit()
        logger.info(f"Published {published} scheduled chapters")

    return {"published": published, "timestamp": now.isoformat()}
