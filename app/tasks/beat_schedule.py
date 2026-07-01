"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Celery beat schedule — periodic task definitions.
"""

from celery.schedules import crontab


beat_schedule = {
    # Publish scheduled content (every minute)
    "scheduled-chapter-publishing": {
        "task": "app.tasks.scheduled_publish.publish_scheduled_chapters",
        "schedule": crontab(minute="*"),
        "options": {"expires": 300},
    },
    # Update popularity scores (every hour)
    "hourly-popularity-update": {
        "task": "app.tasks.popularity_updater.update_popularity_scores",
        "schedule": crontab(minute=0, hour="*"),
        "options": {"expires": 3600},
    },
    # Database backup (daily at 3 AM)
    "daily-database-backup": {
        "task": "app.tasks.backup_tasks.scheduled_db_backup",
        "schedule": crontab(minute=0, hour=3),
        "options": {"expires": 7200},
    },
    # Database maintenance (weekly Sunday at 4 AM)
    "weekly-db-maintenance": {
        "task": "app.tasks.database_optimization.full_maintenance",
        "schedule": crontab(minute=0, hour=4, day_of_week=0),
        "options": {"expires": 7200},
    },
}
