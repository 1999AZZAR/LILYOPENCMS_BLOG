"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Consolidated authentication and authorization decorators.

Single source of truth replacing:
- routes/common_imports.py login_required
- routes/utils/auth_helpers.py AuthenticationHelper
- routes/utils/unified_auth.py UnifiedAuthManager
"""

from functools import wraps
from flask import request, redirect, url_for, jsonify, current_app, g
from flask_login import login_user, logout_user, current_user


def login_required(f):
    """
    Unified login_required that supports both web sessions and JWT tokens.
    Falls back to Flask-Login's login_required if JWT auth is unavailable.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Try JWT authentication first (API / mobile)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    from routes.routes_external_auth import _validate_jwt_token
                    user, token_data = _validate_jwt_token(token)
                    if user:
                        if not user.is_active:
                            return _auth_response("Account inactive", 403, "AUTH_ACCOUNT_INACTIVE")
                        if user.is_suspended:
                            return _auth_response("Account suspended", 403, "AUTH_ACCOUNT_SUSPENDED")
                        g.api_user = user
                        g.token_data = token_data
                        return f(*args, **kwargs)
                except Exception as e:
                    current_app.logger.debug(f"JWT auth failed: {e}")

        # Fall back to session authentication
        if current_user.is_authenticated:
            return f(*args, **kwargs)

        return _auth_response("Authentication required", 401, "AUTH_REQUIRED")

    return decorated


def permission_required(resource: str, action: str):
    """
    Decorator that checks if the current user has a specific permission.

    Usage:
        @permission_required("news", "create")
        def create_news():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "api_user", None) or (current_user if current_user.is_authenticated else None)
            if not user:
                return _auth_response("Authentication required", 401, "AUTH_REQUIRED")

            from shared.auth.permission_manager import PermissionManager
            if not PermissionManager.has_permission(user, resource, action):
                return _auth_response("Forbidden", 403, "PERMISSION_DENIED")

            return f(*args, **kwargs)
        return decorated
    return decorator


def owner_or_permission_required(resource: str, action: str, owner_field: str = "user_id"):
    """
    ABAC decorator: allows access if user is the resource owner OR has the permission.
    Used for content routes where writers can edit their own content.

    Usage:
        @owner_or_permission_required("news", "update", "user_id")
        def update_news(news_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "api_user", None) or (current_user if current_user.is_authenticated else None)
            if not user:
                return _auth_response("Authentication required", 401, "AUTH_REQUIRED")

            from shared.auth.permission_manager import PermissionManager
            if PermissionManager.has_permission(user, resource, action):
                return f(*args, **kwargs)

            # Check ownership via route kwargs or query param
            resource_owner_id = kwargs.get(owner_field)
            if resource_owner_id is not None and hasattr(user, "id") and user.id == int(resource_owner_id):
                return f(*args, **kwargs)

            return _auth_response("Forbidden", 403, "PERMISSION_DENIED")
        return decorated
    return decorator


def admin_required(f):
    """Decorator that requires admin privileges (admin tier or above)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = getattr(g, "api_user", None) or (current_user if current_user.is_authenticated else None)
        if not user:
            return _auth_response("Authentication required", 401, "AUTH_REQUIRED")
        if not user.is_admin_tier():
            return _auth_response("Admin privileges required", 403, "AUTH_INSUFFICIENT_PRIVILEGES")
        return f(*args, **kwargs)
    return decorated


def superuser_required(f):
    """Decorator that requires superuser/owner privileges."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = getattr(g, "api_user", None) or (current_user if current_user.is_authenticated else None)
        if not user:
            return _auth_response("Authentication required", 401, "AUTH_REQUIRED")
        if not user.is_owner():
            return _auth_response("Superuser privileges required", 403, "AUTH_INSUFFICIENT_PRIVILEGES")
        return f(*args, **kwargs)
    return decorated


def _auth_response(message: str, code: int, error_code: str):
    """Return appropriate auth error response based on client type."""
    if request.is_json or request.path.startswith("/api/"):
        return jsonify({
            "error": message,
            "message": message,
            "code": error_code,
        }), code
    return redirect(url_for("main.login"))
