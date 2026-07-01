"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    abort,
    Response,
    flash,
    current_app,
    send_file,
    session,
    g,
)
from flask_login import login_user, logout_user, current_user
from functools import wraps

# Consolidated auth decorators — single source of truth
from shared.auth.decorators import login_required, permission_required, owner_or_permission_required, admin_required, superuser_required

# Create the main blueprint
main_blueprint = Blueprint("main", __name__)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
import markdown
import os
import requests
import xml.etree.ElementTree as ET
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func, and_, or_ 
import re
from urllib.parse import urlparse
from mimetypes import guess_extension
from PIL import Image as PILImage, ImageOps

from models import (
    db,
    User,
    Image,
    YouTubeVideo,
    News,
    Album,
    AlbumChapter,
    RootSEO,
    PrivacyPolicy,
    MediaGuideline,
    VisiMisi,
    Penyangkalan,
    PedomanHak,
    UserRole,
    Category,
    ShareLog,
    SocialMedia,
    ContactDetail,
    TeamMember,
    Permission,
    CustomRole,
    UserActivity,
    NavigationLink,
    BrandIdentity,
)

# Import permission management functions
from routes.utils.permission_manager import (
    can_access_admin,
    can_manage_users,
    can_manage_content,
    can_manage_categories,
    can_manage_settings,
    can_manage_roles,
    can_manage_ads,
    can_moderate_comments,
    can_manage_ratings,
    can_access_analytics,
    can_manage_legal,
    can_manage_brand,
    can_manage_seo,
    has_permission,
    has_any_permission,
    has_all_permissions,
    get_user_role_display,
    get_user_permissions_summary,
    is_superuser,
    is_admin,
    is_admin_tier,
    has_custom_role,
    PermissionManager
)

# Email service for notifications
from routes.utils.email_service import email_service

# Enforce maintenance mode globally: logout non-superusers
@main_blueprint.before_app_request
def enforce_maintenance_mode_logout():
    try:
        import os, json
        settings_path = os.path.join(current_app.instance_path, 'app_settings.json')
        if not os.path.exists(settings_path):
            return
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        maintenance = data.get('maintenance', {}) if isinstance(data, dict) else {}
        enabled = bool(maintenance.get('enabled', False))
        message = maintenance.get('message') or 'Situs dalam mode perawatan.'
        if not enabled:
            return

        path = request.path or ''
        if path.startswith('/static'):
            return
        if path in ['/login', '/logout']:
            return
        if current_user.is_authenticated and getattr(current_user, 'role', None) != UserRole.SUPERUSER:
            try:
                logout_user()
            except Exception:
                pass
            try:
                flash(message, 'error')
            except Exception:
                pass
            return redirect(url_for('main.login'))
    except Exception:
        return
