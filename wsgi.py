"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
WSGI entry point — uses the app factory.

Production: gunicorn wsgi:application
Development: python wsgi.py
"""

import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

os.environ.setdefault("FLASK_ENV", "production")

from app import create_app  # noqa: E402

application = create_app()

if __name__ == "__main__":
    print("This is a WSGI entry point. Use 'gunicorn wsgi:application' for production.")
    print("Use 'python main.py' for the legacy development server.")
    sys.exit(0)
