"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Media Routes

This module handles categories and YouTube management routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/categories")
@login_required
def settings_categories():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    return render_template("settings/categories_management.html")


@main_blueprint.route("/settings/youtube")
@login_required
def settings_youtube():
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
        abort(403)

    videos = YouTubeVideo.query.all()
    return render_template("settings/youtube_management.html", videos=videos)
