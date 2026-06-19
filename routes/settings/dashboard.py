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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)  # Only admins and superusers can access this page
    return render_template("settings/settings_management.html")


@main_blueprint.route("/settings/analytics")
@login_required
@monitor_ssr_render("settings_analytics")
def settings_analytics():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    return render_template("settings/analytics_dashboard.html")