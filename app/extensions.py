"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
cors = CORS()
