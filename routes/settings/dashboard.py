"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Dashboard Routes

This module handles the main settings dashboard and analytics routes.
"""

from routes import main_blueprint
from .common_imports import *
from optimizations import monitor_ssr_render


@main_blueprint.route("/settings")
@login_required
@monitor_ssr_render("settings_dashboard")
def settings_dashboard():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.effective_tier > 1:
        abort(403)  # Only admins and superusers can access this page
    return render_template("settings/settings_management.html")


@main_blueprint.route("/settings/analytics")
@login_required
@monitor_ssr_render("settings_analytics")
def settings_analytics():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.effective_tier > 1:
        abort(403)
    return render_template("settings/analytics_dashboard.html")
