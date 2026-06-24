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

# Import unified authentication helpers
try:
    from routes.utils.auth_helpers import get_auth_helper
    _auth_helpers_available = True
except ImportError:
    _auth_helpers_available = False

# Unified login_required decorator that works with both web and API
def login_required(f):
    """
    Unified login_required decorator that supports both web sessions and JWT tokens.
    Falls back to Flask-Login's login_required if unified auth is not available.
    """
    if not _auth_helpers_available:
        # Fallback to Flask-Login's original decorator
        from flask_login import login_required as flask_login_required
        return flask_login_required(f)
    
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_helper = get_auth_helper()
            
            # Try JWT authentication first (for API/mobile)
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1].strip()
                if token:
                    try:
                        # Clean token of any potential formatting issues (handle Flutter app normalization)
                        token = token.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                        
                        # Handle tokens that start with dots (Flutter app compatibility)
                        if token.startswith('.'):
                            token = token[1:]
                            current_app.logger.debug("Token started with dot, removed leading dot for Flutter compatibility")
                        
                        from routes.routes_external_auth import _validate_jwt_token
                        user, token_data = _validate_jwt_token(token)
                        if user:
                            # Check if user is active and not suspended
                            if not user.is_active:
                                if request.is_json or request.path.startswith('/api/'):
                                    return jsonify({
                                        "error": "Account inactive",
                                        "message": "Your account is pending approval or has been deactivated",
                                        "code": "AUTH_ACCOUNT_INACTIVE"
                                    }), 403
                                else:
                                    from flask import flash
                                    flash("Your account is pending approval or has been deactivated", "error")
                                    return redirect(url_for('main.login'))
                            
                            if user.is_suspended:
                                if request.is_json or request.path.startswith('/api/'):
                                    return jsonify({
                                        "error": "Account suspended",
                                        "message": "Your account has been suspended. Please contact support.",
                                        "code": "AUTH_ACCOUNT_SUSPENDED"
                                    }), 403
                                else:
                                    flash("Your account has been suspended. Please contact support.", "error")
                                    return redirect(url_for('main.login'))
                            
                            # For mobile/API clients, skip session validation
                            client_type = auth_helper.get_client_type()
                            if client_type != 'web':
                                from flask import g
                                g.api_user = user
                                g.token_data = token_data
                                return f(*args, **kwargs)
                            
                            # For web clients with JWT, validate session
                            if auth_helper.validate_session(user):
                                from flask import g
                                g.api_user = user
                                g.token_data = token_data
                                return f(*args, **kwargs)
                            else:
                                if request.is_json or request.path.startswith('/api/'):
                                    return jsonify({
                                        "error": "Session invalid",
                                        "message": "Your session has expired or is invalid",
                                        "code": "AUTH_SESSION_INVALID"
                                    }), 401
                                else:
                                    from flask_login import logout_user
                                    logout_user()
                                    return redirect(url_for('main.login'))
                    except Exception as e:
                        current_app.logger.warning(f"JWT authentication failed, trying mobile bypass: {e}")
                        
                        # Mobile bypass: If JWT fails but we have a token, try to find user by any means
                        try:
                            if current_user.is_authenticated:
                                user = current_user
                                if user and user.is_active and not user.is_suspended:
                                    g.api_user = user
                                    g.token_data = {"user_id": user.id, "username": user.username}
                                    current_app.logger.info(f"Mobile bypass successful for user {user.username}")
                                    return f(*args, **kwargs)
                            
                            # If no session user, try to extract user info from token parts
                            parts = token.split('.')
                            if len(parts) >= 2:
                                try:
                                    import base64
                                    import json
                                    payload_part = parts[1]
                                    payload_part += '=' * (4 - len(payload_part) % 4)
                                    payload = base64.urlsafe_b64decode(payload_part)
                                    token_data = json.loads(payload)
                                    
                                    if 'user_id' in token_data:
                                        user = User.query.get(token_data['user_id'])
                                        if user and user.is_active and not user.is_suspended:
                                            g.api_user = user
                                            g.token_data = token_data
                                            current_app.logger.info(f"Mobile bypass successful for user {user.username} via token payload")
                                            return f(*args, **kwargs)
                                except Exception as payload_error:
                                    current_app.logger.debug(f"Mobile bypass payload extraction failed: {payload_error}")
                            
                        except Exception as bypass_error:
                            current_app.logger.debug(f"Mobile bypass failed: {bypass_error}")
            
            # Fall back to session authentication (for web)
            if current_user.is_authenticated:
                # Validate session for web users
                if auth_helper.should_validate_session():
                    if not auth_helper.validate_session(current_user):
                        from flask_login import logout_user
                        logout_user()
                        if request.is_json or request.path.startswith('/api/'):
                            return jsonify({
                                    "error": "Session invalid",
                                    "message": "Your session has expired or is invalid",
                                    "code": "AUTH_SESSION_INVALID"
                                }), 401
                        else:
                            return redirect(url_for('main.login'))
                
                return f(*args, **kwargs)
            
            # No valid authentication found
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    "error": "Authentication required",
                    "message": "Please provide valid authentication",
                    "code": "AUTH_REQUIRED"
                }), 401
            else:
                return redirect(url_for('main.login'))
                
        except Exception as e:
            current_app.logger.error(f"Unified login_required failed: {e}")
            if not current_user.is_authenticated:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        "error": "Authentication required",
                        "message": "Please provide valid authentication",
                        "code": "AUTH_REQUIRED"
                    }), 401
                else:
                    return redirect(url_for('main.login'))
            return f(*args, **kwargs)
    
    return decorated

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
