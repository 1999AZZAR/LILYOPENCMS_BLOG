"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Celery application entry point.

Usage:
    celery -A app.tasks.celery_app worker --loglevel=info
    celery -A app.tasks.celery_app beat --loglevel=info
"""

import os
from celery import Celery

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
result_backend = os.getenv("REDIS_URL", "redis://localhost:6379/0").replace("/0", "/1")

celery_app = Celery("lilyopencms", broker=broker_url, backend=result_backend)

celery_app.conf.update(
    broker_transport_options={"visibility_timeout": 3600},
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
    task_soft_time_limit=3300,
    task_time_limit=3600,
    worker_max_tasks_per_child=1000,
    worker_enable_remote_control=False,
    beat_schedule={
        "scheduled-chapter-publishing": {
            "task": "app.tasks.scheduled_publish.publish_scheduled_chapters",
            "schedule": 60.0,  # every minute
            "options": {"expires": 300},
        },
        "hourly-popularity-update": {
            "task": "app.tasks.popularity_updater.update_popularity_scores",
            "schedule": 3600.0,  # every hour
            "options": {"expires": 3600},
        },
        "daily-database-backup": {
            "task": "app.tasks.backup_tasks.scheduled_db_backup",
            "schedule": {"hour": 3, "minute": 0},  # daily 3 AM
            "options": {"expires": 7200},
        },
        "weekly-db-maintenance": {
            "task": "app.tasks.database_optimization.full_maintenance",
            "schedule": {"hour": 4, "minute": 0, "day_of_week": 0},  # Sunday 4 AM
            "options": {"expires": 7200},
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
