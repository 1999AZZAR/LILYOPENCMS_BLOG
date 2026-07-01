"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
ContextTask — ensures every Celery task runs within a Flask app context.
"""

from celery import Task
from flask import Flask


class ContextTask(Task):
    """Celery Task subclass that wraps execution in a Flask app context."""

    def __init__(self):
        self.app: Flask = None

    def __call__(self, *args, **kwargs):
        if self.app is None:
            from app import create_app
            self.app = create_app()
        with self.app.app_context():
            return self.run(*args, **kwargs)
