"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Unified Authentication Helpers for LilyOpenCMS

This module provides comprehensive authentication helpers that eliminate
code duplication across all authentication routes and ensure consistent
behavior for web, mobile, and API clients.
"""

import logging
import json
from typing import Optional, Dict, Any, Tuple, Union
from datetime import datetime, timezone
from flask import request, current_app, session, g, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from functools import wraps

from models import User, UserRole, db
from routes.utils.unified_auth import get_unified_auth_manager

logger = logging.getLogger(__name__)

class AuthenticationHelper:
    """Centralized authentication helper class."""
    
    def __init__(self):
        self.auth_manager = get_unified_auth_manager()
    
    def authenticate_user(self, user: User, auth_method: str = "local", 
                        request_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Authenticate a user using the unified authentication system.
        
        Args:
            user: The user to authenticate
            auth_method: The authentication method used ("local", "firebase", "api")
            request_data: Additional request data for logging
            
        Returns:
            Dictionary containing authentication result
        """
        return self.auth_manager.authenticate_user(user, auth_method, request_data)
    
    def logout_user(self, user: User, reason: str = "User logout") -> Dict[str, Any]:
        """
        Logout a user using the unified authentication system.
        
        Args:
            user: The user to logout
            reason: Reason for logout
            
        Returns:
            Dictionary containing logout result
        """
        return self.auth_manager.logout_user(user, reason)
    
    def get_current_user(self) -> Optional[User]:
        """Get the current authenticated user from JWT or session."""
        # Try to get user from JWT authentication first (mobile/API)
        api_user = getattr(g, 'api_user', None)
        if api_user:
            return api_user
        
        # Fall back to Flask-Login session authentication (web)
        if current_user.is_authenticated:
            return current_user
        
        return None
    
    def require_active_user(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if user is authenticated and active."""
        user = self.get_current_user()
        if not user:
            return False, {
                "error": "Authentication required",
                "message": "Please provide valid authentication",
                "code": "AUTH_REQUIRED"
            }
        
        if not user.is_active:
            return False, {
                "error": "Account inactive",
                "message": "Your account is pending approval or has been deactivated",
                "code": "AUTH_ACCOUNT_INACTIVE"
            }
        
        if user.is_suspended:
            return False, {
                "error": "Account suspended",
                "message": "Your account has been suspended. Please contact support.",
                "code": "AUTH_ACCOUNT_SUSPENDED"
            }
        
        return True, None
    
    def validate_session(self, user: User) -> bool:
        """Validate user session using Flask-Login."""
        try:
            # Use Flask-Login's built-in session validation
            return current_user.is_authenticated and current_user.id == user.id
        except Exception as e:
            logger.warning(f"Session validation failed: {e}")
            return False
    
    def invalidate_user_sessions(self, user_id: int, reason: str = "Security invalidation") -> int:
        """Invalidate all sessions for a user (simplified - just logout from Flask-Login)."""
        try:
            # Since we're not tracking sessions in database anymore, just logout from Flask-Login
            logout_user()
            session.clear()
            logger.info(f"User {user_id} logged out: {reason}")
            return 1  # Return 1 to indicate one session was invalidated
        except Exception as e:
            logger.error(f"Failed to invalidate sessions for user {user_id}: {e}")
            return 0
    
    def record_user_activity(self, user_id: int, activity_type: str,
                           description: str, ip_address: str = None,
                           user_agent: str = None) -> bool:
        """Record user activity for audit trail using simple JWT manager."""
        try:
            from routes.utils.simple_jwt_session import get_simple_jwt_manager
            jwt_manager = get_simple_jwt_manager()

            # Use the simple JWT manager for activity recording
            jwt_manager.record_user_activity(user_id, activity_type, description)
            return True
        except Exception as e:
            logger.error(f"Failed to record activity for user {user_id}: {e}")
            return False
    
    def get_client_type(self) -> str:
        """Detect client type (web, mobile, api)."""
        try:
            user_agent = request.headers.get('User-Agent', '').lower()
            
            # Mobile app detection
            mobile_indicators = ['android', 'ios', 'flutter', 'react-native', 'cordova', 'phonegap']
            if any(indicator in user_agent for indicator in mobile_indicators):
                return 'mobile'
            
            # API client detection
            api_indicators = ['api-client', 'mobile-app', 'external-client']
            if any(indicator in user_agent for indicator in api_indicators):
                return 'api'
            
            # Check for explicit client header
            client_header = request.headers.get('X-Client-Type', '').lower()
            if client_header in ['mobile', 'android', 'ios', 'flutter', 'desktop']:
                return 'mobile'
            elif client_header in ['api', 'external']:
                return 'api'
            
            return 'web'
        except:
            return 'unknown'
    
    def should_validate_session(self) -> bool:
        """Determine if session validation should be performed based on client type."""
        client_type = self.get_client_type()
        # Only validate sessions for web clients
        return client_type == 'web'
    
    def create_auth_response(self, success: bool, user: User = None, 
                           redirect_url: str = None, message: str = None,
                           error: str = None, error_code: str = None,
                           is_api: bool = False) -> Union[Dict, Any]:
        """Create appropriate response based on request type."""
        if is_api or request.is_json or request.path.startswith('/api/'):
            # API response
            response_data = {
                "success": success,
                "message": message or ("Success" if success else "Failed")
            }
            
            if success and user:
                response_data["user"] = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value if user.role else None,
                    "is_premium": user.is_premium,
                    "auth_provider": user.auth_provider,
                    "profile_picture": user.profile_picture or user.parsed_provider_data.get('photo_url') if user.provider_data else None
                }
                if redirect_url:
                    response_data["redirect_url"] = redirect_url
            
            if not success:
                response_data["error"] = error or "Authentication failed"
                if error_code:
                    response_data["code"] = error_code
            
            return jsonify(response_data), 200 if success else 401
        else:
            # Web response
            if success:
                if message:
                    flash(message, "success")
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    return redirect(url_for("main.home"))
            else:
                if error:
                    flash(error, "error")
                return redirect(url_for("main.login"))

# Global instance
auth_helper = AuthenticationHelper()

def get_auth_helper():
    """Get the authentication helper instance."""
    return auth_helper

# Decorators
def unified_auth_required(f):
    """Unified authentication decorator that works for web, mobile, and API."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_helper = get_auth_helper()
        
        # Try JWT authentication first (for mobile/API)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    # Clean token of any potential formatting issues
                    token = token.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                    
                    from routes.routes_external_auth import _validate_jwt_token
                    user, token_data, error_code = _validate_jwt_token(token)
                    if error_code == "AUTH_TOKENS_CORRUPTED":
                        return {"success": False, "error": "Authentication tokens corrupted", "code": "AUTH_TOKENS_CORRUPTED"}
                    if user:
                        # Set the user in g first so require_active_user can find it
                        g.api_user = user
                        g.token_data = token_data
                        
                        # Now check if user is active
                        is_active, error = auth_helper.require_active_user()
                        if is_active:
                            # For mobile/API clients, skip session validation
                            if not auth_helper.should_validate_session():
                                return f(*args, **kwargs)
                            
                            # For web clients with JWT, validate session
                            if auth_helper.validate_session(user):
                                g.api_user = user
                                g.token_data = token_data
                                return f(*args, **kwargs)
                            else:
                                return jsonify({
                                    "error": "Session invalid",
                                    "message": "Your session has expired or is invalid",
                                    "code": "AUTH_SESSION_INVALID"
                                }), 401
                        else:
                            return jsonify(error), 403
                except Exception as e:
                    logger.warning(f"JWT authentication failed, trying mobile bypass: {e}")
                    
                    # Mobile bypass: If JWT fails but we have a token, try to find user by any means
                    try:
                        from flask_login import current_user
                        
                        # Try to get user from session first
                        if current_user.is_authenticated:
                            user = current_user
                            if user and user.is_active and not user.is_suspended:
                                g.api_user = user
                                g.token_data = {"user_id": user.id, "username": user.username}
                                logger.info(f"Mobile bypass successful for user {user.username}")
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
                                    from models import User
                                    user = User.query.get(token_data['user_id'])
                                    if user and user.is_active and not user.is_suspended:
                                        g.api_user = user
                                        g.token_data = token_data
                                        logger.info(f"Mobile bypass successful for user {user.username} via token payload")
                                        return f(*args, **kwargs)
                            except Exception as payload_error:
                                logger.debug(f"Mobile bypass payload extraction failed: {payload_error}")
                        
                    except Exception as bypass_error:
                        logger.debug(f"Mobile bypass failed: {bypass_error}")
        
        # Fall back to session authentication (for web)
        user = auth_helper.get_current_user()
        if user:
            is_active, error = auth_helper.require_active_user()
            if is_active:
                # Only validate session for web clients
                if not auth_helper.should_validate_session() or auth_helper.validate_session(user):
                    return f(*args, **kwargs)
                else:
                    # Session invalid, logout user
                    logout_user()
                    return jsonify({
                        "error": "Session invalid",
                        "message": "Your session has expired or is invalid",
                        "code": "AUTH_SESSION_INVALID"
                    }), 401
            else:
                return jsonify(error), 403
        
        # No valid authentication found
        return jsonify({
            "error": "Authentication required",
            "message": "Please provide valid authentication",
            "code": "AUTH_REQUIRED"
        }), 401
    
    return decorated

def mobile_auth_required(f):
    """JWT-only authentication decorator for mobile apps."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_helper = get_auth_helper()
        
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    from routes.routes_external_auth import _validate_jwt_token
                    user, token_data, error_code = _validate_jwt_token(token)
                    if error_code == "AUTH_TOKENS_CORRUPTED":
                        return {"success": False, "error": "Authentication tokens corrupted", "code": "AUTH_TOKENS_CORRUPTED"}
                    if user:
                        # Set the user in g first so require_active_user can find it
                        g.api_user = user
                        g.token_data = token_data
                        
                        # Now check if user is active
                        is_active, error = auth_helper.require_active_user()
                        if is_active:
                            return f(*args, **kwargs)
                        else:
                            return jsonify(error), 403
                except Exception as e:
                    logger.warning(f"Mobile JWT authentication failed: {e}")
        
        return jsonify({
            "error": "Authentication required",
            "message": "Please provide valid JWT token for mobile access",
            "code": "AUTH_REQUIRED"
        }), 401
    
    return decorated

def admin_required(f):
    """Decorator that requires admin privileges."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_helper = get_auth_helper()
        user = auth_helper.get_current_user()
        
        if not user:
            return jsonify({
                "error": "Authentication required",
                "message": "Please login to access this resource",
                "code": "AUTH_REQUIRED"
            }), 401
        
        if not user.is_admin_tier():
            return jsonify({
                "error": "Access denied",
                "message": "Admin privileges required",
                "code": "AUTH_INSUFFICIENT_PRIVILEGES"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated

def superuser_required(f):
    """Decorator that requires superuser privileges."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_helper = get_auth_helper()
        user = auth_helper.get_current_user()
        
        if not user:
            return jsonify({
                "error": "Authentication required",
                "message": "Please login to access this resource",
                "code": "AUTH_REQUIRED"
            }), 401
        
        if not user.is_owner():
            return jsonify({
                "error": "Access denied",
                "message": "Superuser privileges required",
                "code": "AUTH_INSUFFICIENT_PRIVILEGES"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated

# Utility functions
def find_user_by_username_or_email(identifier: str) -> Optional[User]:
    """Find user by username or email."""
    if '@' in identifier:
        return User.query.filter_by(email=identifier).first()
    else:
        return User.query.filter_by(username=identifier).first()

def get_firebase_config() -> Dict[str, str]:
    """Get Firebase configuration for frontend."""
    import os
    from flask import current_app

    # First try to load from persistent JSON config file
    config_file = None
    if current_app:
        import os as os_module
        config_file = os_module.path.join(current_app.root_path, 'config', 'firebase_config.json')

    config = {}
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            config.update(saved_config)

            # Set environment variables for Firebase service compatibility
            if saved_config.get('project_id'):
                os.environ['FIREBASE_PROJECT_ID'] = saved_config['project_id']
            if saved_config.get('api_key'):
                os.environ['FIREBASE_API_KEY'] = saved_config['api_key']
            if saved_config.get('auth_domain'):
                os.environ['FIREBASE_AUTH_DOMAIN'] = saved_config['auth_domain']
            if saved_config.get('storage_bucket'):
                os.environ['FIREBASE_STORAGE_BUCKET'] = saved_config['storage_bucket']
            if saved_config.get('messaging_sender_id'):
                os.environ['FIREBASE_MESSAGING_SENDER_ID'] = saved_config['messaging_sender_id']
            if saved_config.get('app_id'):
                os.environ['FIREBASE_APP_ID'] = saved_config['app_id']
            if saved_config.get('use_emulator'):
                os.environ['FIREBASE_USE_EMULATOR'] = saved_config['use_emulator']
            if saved_config.get('emulator_host'):
                os.environ['FIREBASE_EMULATOR_HOST'] = saved_config['emulator_host']

            # Set service account path if service account file exists and is valid
            service_account_file = os.path.join(os.path.dirname(config_file), 'firebase_service_account.json')
            if os.path.exists(service_account_file):
                try:
                    with open(service_account_file, 'r', encoding='utf-8') as f:
                        sa_data = json.load(f)
                    if sa_data.get('type') == 'service_account':
                        os.environ['FIREBASE_SERVICE_ACCOUNT_PATH'] = service_account_file
                        logger.info("Valid service account file path set in environment")
                    else:
                        logger.warning("Service account file exists but is not valid (not type=service_account)")
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not validate service account file: {e}")

            logger.info("Firebase environment variables set from config file")

            # Remove metadata fields that shouldn't be sent to frontend
            config.pop('updated_at', None)
            config.pop('updated_by', None)
        except Exception as e:
            # If JSON loading fails, fall back to environment variables
            logger.warning(f"Failed to load Firebase config from JSON: {e}")
            pass

    # Fall back to environment variables for any missing values
    config.setdefault("api_key", os.getenv('FIREBASE_API_KEY', ''))
    config.setdefault("auth_domain", os.getenv('FIREBASE_AUTH_DOMAIN', ''))
    config.setdefault("project_id", os.getenv('FIREBASE_PROJECT_ID', ''))
    config.setdefault("storage_bucket", os.getenv('FIREBASE_STORAGE_BUCKET', ''))
    config.setdefault("messaging_sender_id", os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''))
    config.setdefault("app_id", os.getenv('FIREBASE_APP_ID', ''))
    config.setdefault("use_emulator", os.getenv('FIREBASE_USE_EMULATOR', 'false'))
    config.setdefault("emulator_host", os.getenv('FIREBASE_EMULATOR_HOST', 'localhost:9099'))

    return config

def clear_session_cookies(response):
    """Clear session cookies from response."""
    cookie_names = [
        current_app.config.get('SESSION_COOKIE_NAME', 'session'),
        'lily_session',
        'session'
    ]
    
    for cookie_name in cookie_names:
        response.set_cookie(
            cookie_name,
            '',
            expires=0,
            max_age=0,
            path='/',
            secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
            httponly=current_app.config.get('SESSION_COOKIE_HTTPONLY', True),
            samesite=current_app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')
        )
    
    return response

def handle_password_change(user: User, new_password: str, 
                         current_password: str = None) -> Tuple[bool, str]:
    """Handle password change with session invalidation."""
    try:
        # Verify current password if provided
        if current_password and not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        # Update password
        user.set_password(new_password)
        
        # Invalidate all sessions on password change
        auth_helper = get_auth_helper()
        invalidated_count = auth_helper.invalidate_user_sessions(
            user.id, "Password changed"
        )
        
        # Record password change activity
        auth_helper.record_user_activity(
            user.id,
            "password_change",
            f"Password changed from {request.remote_addr}",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
        db.session.commit()
        
        logger.info(f"Password changed for user {user.username}, invalidated {invalidated_count} sessions")
        return True, "Password changed successfully"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change failed for user {user.username}: {e}")
        return False, "Failed to change password"

def send_verification_email(user: User) -> bool:
    """Send verification email to user."""
    try:
        from routes.utils.email_service import email_service
        from itsdangerous import URLSafeTimedSerializer
        
        # Initialize email service if needed
        email_service.init_app(current_app)
        
        # Generate verification token
        s = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY", "change-me"), salt="email-verify")
        token = s.dumps({"user_id": user.id, "email": user.email or ""})
        
        # Send verification email
        if user.email:
            success = email_service.send_verification_email(user, token)
            if success:
                user.last_verification_sent_at = datetime.now(timezone.utc)
                db.session.commit()
                logger.info(f"Verification email sent to {user.email}")
                return True
            else:
                logger.warning(f"Failed to send verification email to {user.email}")
                return False
        else:
            logger.warning(f"User {user.username} has no email address")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False

def send_password_reset_email(user: User) -> bool:
    """Send password reset email to user."""
    try:
        from routes.utils.email_service import email_service
        from itsdangerous import URLSafeTimedSerializer
        
        # Initialize email service if needed
        email_service.init_app(current_app)
        
        # Generate password reset token
        s = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY", "change-me"), salt="password-reset")
        token = s.dumps({"user_id": user.id, "email": user.email or ""})
        logger.info(f"Generated password reset token for user {user.username} (ID: {user.id})")
        
        # Send password reset email
        if user.email:
            success = email_service.send_password_reset_email(user, token)
            if success:
                logger.info(f"Password reset email sent to {user.email}")
                return True
            else:
                logger.warning(f"Failed to send password reset email to {user.email}")
                return False
        else:
            logger.warning(f"User {user.username} has no email address")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False
