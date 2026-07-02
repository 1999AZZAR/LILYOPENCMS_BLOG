"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from .common_imports import *

from .routes_auth import *
from .routes_chategories import *
from .routes_helper import *
from .routes_images import *
from .routes_infos import *
from .routes_news import *
from .routes_public import *
from .settings import *
from .routes_socialmedia import *
from .routes_subscriptions import *
from .routes_users import *
from .routes_roles import *
from .routes_analytics import *
from .routes_video import *
from .routes_albums import *
from .routes_seo import *
from .seo_enhanced_dashboard import *
from .seo_settings_api import *
from .routes_pages import *
from .routes_tags import *
from .routes_comments import *

__all__ = [
    "main_blueprint",
    "routes_auth",
    "routes_chategories",
    "routes_helper",
    "routes_images",
    "routes_infos",
    "routes_news",
    "routes_public",
    "settings",
    "routes_socialmedia",
    "routes_users",
    "routes_roles",
    "routes_analytics",
    "routes_video",
    "routes_albums",
    "routes_seo",
    "seo_enhanced_dashboard",
    "seo_settings_api",
    "routes_pages",
    "routes_tags",
    "routes_comments",
]
