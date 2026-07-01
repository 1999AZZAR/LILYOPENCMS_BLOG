"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import os


class BaseConfig:
    """Shared configuration defaults."""
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///exposeur.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    COMPRESS_MIMETYPES = [
        "text/html", "text/css", "text/xml",
        "application/json", "application/javascript",
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
