"""
Content Management Routes

This module handles news creation and management routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/create_news")
@login_required
def create_news():
    if current_user.role not in [UserRole.GENERAL, UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    # Pass the current_user object to the template
    return render_template("settings/create_news_management.html", current_user=current_user)


@main_blueprint.route("/settings/manage_news")
@login_required
def manage_news():
    if current_user.role not in [UserRole.GENERAL, UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    # Pass the current_user object to the template
    return render_template("settings/manage_news_management.html", current_user=current_user)