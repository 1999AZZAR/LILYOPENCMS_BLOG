"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Content Management Routes

This module handles news creation and management routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/create_news")
@login_required
def create_news():
    return render_template("settings/create_news_management.html", current_user=current_user)


@main_blueprint.route("/settings/manage_news")
@login_required
def manage_news():

    # Pass the current_user object to the template
    return render_template("settings/manage_news_management.html", current_user=current_user)
