"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Account Management Routes

This module handles user account management and user administration routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/account")
@login_required
def user_account():
    return render_template("settings/account_management.html")


@main_blueprint.route("/settings/users")
@login_required
def settings_users():
    if current_user.effective_tier != 0:
        abort(403)
    return render_template("settings/users_management.html")
