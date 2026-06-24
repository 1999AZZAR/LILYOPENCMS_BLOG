"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Mobile Authentication Helper

This module provides helper functions for mobile-compatible authentication
across all API endpoints. This module is now deprecated in favor of the
unified auth_helpers module.
"""

from flask import g, current_user
from flask_login import current_user as flask_current_user
from routes.utils.auth_helpers import get_auth_helper
import logging

logger = logging.getLogger(__name__)

def get_current_user():
    """Get the current authenticated user, supporting both JWT and session auth."""
    # Use the unified auth helper
    auth_helper = get_auth_helper()
    return auth_helper.get_current_user()

def require_authentication():
    """Check if user is authenticated, supporting both JWT and session auth."""
    auth_helper = get_auth_helper()
    is_active, _ = auth_helper.require_active_user()
    return is_active

def require_active_user():
    """Check if user is authenticated and active."""
    auth_helper = get_auth_helper()
    is_active, _ = auth_helper.require_active_user()
    return is_active

def get_client_type():
    """Detect client type (web, mobile, api)."""
    auth_helper = get_auth_helper()
    return auth_helper.get_client_type()

def should_validate_session():
    """Determine if session validation should be performed based on client type."""
    auth_helper = get_auth_helper()
    return auth_helper.should_validate_session()
