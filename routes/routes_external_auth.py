"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from routes import main_blueprint
from .common_imports import *
from flask import g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from functools import wraps
import jwt
import time
from datetime import datetime, timedelta, timezone
from models import User, Comment, Rating
from routes.utils.email_service import email_service
from routes.utils.auth_helpers import (
    get_auth_helper, unified_auth_required, mobile_auth_required,
    find_user_by_username_or_email, handle_password_change, send_verification_email, send_password_reset_email
)

def _init_email_service_for_api():
    """Initialize email service for API context"""
    try:
        from main import app
        email_service.init_app(app)
        current_app.logger.info("✅ Email service initialized for API")
    except Exception as e:
        current_app.logger.error(f"❌ Failed to initialize email service for API: {e}")
        raise


# Simplified JWT Configuration - Using simple JWT manager
# All complex JWT logic moved to routes.utils.simple_jwt_session

# Token TTL Configuration (in seconds)
ACCESS_TOKEN_TTL_SECONDS = 7200          # 2 hours for API clients
MOBILE_ACCESS_TOKEN_TTL_SECONDS = 14400  # 4 hours for mobile clients
WEB_ACCESS_TOKEN_TTL_SECONDS = 1800      # 30 minutes for web clients
REFRESH_TOKEN_TTL_SECONDS = 2592000      # 30 days for refresh tokens

# Token salts for itsdangerous compatibility (legacy)
ACCESS_TOKEN_SALT = "lily-access-token-2025"
REFRESH_TOKEN_SALT = "lily-refresh-token-2025"

# Sliding refresh window (30 days)
SLIDING_REFRESH_WINDOW_SECONDS = 2592000


def _safe_log(level: str, message: str, *args):
    """Safely log a message without causing exceptions."""
    try:
        logger = getattr(current_app.logger, level, None)
        if logger:
            logger(message.format(*args) if args else message)
    except Exception as e:
        pass


def get_client_type():
    """Detect if request is from mobile app, web browser, or API client."""
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
        if client_header in ['mobile', 'android', 'ios', 'flutter']:
            return 'mobile'
        elif client_header in ['api', 'external']:
            return 'api'
        
        # Default to web for browser requests
        return 'web'
    except Exception as e:
        return 'unknown'


def get_token_ttl_for_client():
    """Get appropriate token TTL based on client type."""
    client_type = get_client_type()
    
    if client_type == 'mobile':
        return MOBILE_ACCESS_TOKEN_TTL_SECONDS
    elif client_type == 'web':
        return WEB_ACCESS_TOKEN_TTL_SECONDS
    else:
        return ACCESS_TOKEN_TTL_SECONDS

def _encode_jwt(payload: dict, expires_in: int = None) -> str:
    """Encode a JWT token using simple JWT manager."""
    try:
        from routes.utils.simple_jwt_session import get_simple_jwt_manager
        jwt_manager = get_simple_jwt_manager()

        # For backward compatibility, create a temporary user object
        class TempUser:
            def __init__(self, user_id, username, email, role):
                self.id = user_id
                self.username = username
                self.email = email
                self.role = role

        # Extract user info from payload if available
        user_id = payload.get('user_id')
        username = payload.get('username', 'unknown')
        email = payload.get('email', '')
        role = payload.get('role', 'USER')

        temp_user = TempUser(user_id, username, email, role)
        return jwt_manager.create_access_token(temp_user)

    except Exception as e:
        _safe_log("error", "Failed to encode JWT: {}", e)
        return None


def _decode_jwt(token: str) -> dict:
    """Decode and validate a JWT token using simple JWT manager."""
    try:
        from routes.utils.simple_jwt_session import get_simple_jwt_manager
        jwt_manager = get_simple_jwt_manager()

        payload = jwt_manager.validate_token(token)
        return payload

    except Exception as e:
        _safe_log("error", "Failed to decode JWT: {}", e)
        return None


def _get_serializer(salt: str) -> URLSafeTimedSerializer:
    """Legacy Flask-ItsDangerous serializer for backward compatibility."""
    return URLSafeTimedSerializer("lily-mobile-secret-key-2025", salt=salt)

def _get_mobile_serializer(salt: str) -> URLSafeTimedSerializer:
    """Legacy Flask-ItsDangerous serializer for mobile clients."""
    return URLSafeTimedSerializer("lily-mobile-secret-key-2025", salt=salt)

def _validate_jwt_token(token: str) -> tuple:
    """Validate JWT token using simple JWT manager and return (user, token_data, error_code)."""
    try:
        from routes.utils.simple_jwt_session import get_simple_jwt_manager

        jwt_manager = get_simple_jwt_manager()
        user = jwt_manager.get_user_from_token(token)

        if not user:
            _safe_log("warning", "JWT token validation failed")
            return None, None, "AUTH_TOKENS_CORRUPTED"

        # Get token payload for additional data
        payload = jwt_manager.validate_token(token)
        if not payload:
            _safe_log("warning", "Failed to get token payload")
            return None, None, "AUTH_TOKENS_CORRUPTED"

        _safe_log("info", "Token validation successful for user: {}", user.username)
        return user, payload, None

    except Exception as e:
        _safe_log("error", "Token validation error: {}", e)
        return None, None, "AUTH_TOKENS_CORRUPTED"


def _issue_tokens(user) -> dict:
    """Issue JWT tokens for user authentication using simple JWT manager."""
    try:
        from routes.utils.simple_jwt_session import get_simple_jwt_manager

        jwt_manager = get_simple_jwt_manager()
        client_type = get_client_type()

        # Generate JWT tokens using simple manager
        access_token = jwt_manager.create_access_token(user)
        refresh_token = jwt_manager.create_refresh_token(user)

        if not access_token or not refresh_token:
            _safe_log("error", "Failed to generate JWT tokens for user {}", user.username)
            return {}

        _safe_log("info", "JWT tokens issued successfully for {} client", client_type)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour
            "client_type": client_type,
            "user": user.to_safe_dict() if hasattr(user, "to_safe_dict") else user.to_dict_safe() if hasattr(user, "to_dict_safe") else {
                "id": user.id,
                "username": user.username,
                "role": user.role.value if user.role else None,
                "is_premium": user.is_premium,
                "verified": user.verified,
            },
        }

    except Exception as e:
        _safe_log("error", "Failed to issue JWT tokens: {}", e)
        return {}


def mobile_auth_required(f):
    """JWT-only authentication decorator for mobile apps without session validation."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    user, token_data, error_code = _validate_jwt_token(token)
                    if error_code == "AUTH_TOKENS_CORRUPTED":
                        return jsonify({
                            "error": "Authentication tokens corrupted",
                            "message": "Please log in again to refresh your authentication tokens",
                            "code": "AUTH_TOKENS_CORRUPTED",
                            "force_reauth": True
                        }), 401
                    if user:
                        if not user.is_active:
                            return jsonify({
                                "error": "Account inactive",
                                "message": "Your account is pending approval or has been deactivated",
                                "code": "AUTH_ACCOUNT_INACTIVE"
                            }), 403

                        if user.is_suspended:
                            return jsonify({
                                "error": "Account suspended",
                                "message": "Your account has been suspended. Please contact support.",
                                "code": "AUTH_ACCOUNT_SUSPENDED"
                            }), 403

                        # For mobile apps, skip session validation
                        g.api_user = user
                        g.token_data = token_data
                        return f(*args, **kwargs)

                except Exception as e:
                    current_app.logger.warning(f"Mobile JWT authentication failed: {e}")

        # No valid authentication found
        return jsonify({
            "error": "Authentication required",
            "message": "Please provide valid JWT token for mobile access",
            "code": "AUTH_REQUIRED"
        }), 401

    return decorated


def auth_required(f):
    """Combined authentication decorator that accepts both session and JWT tokens."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Detect client type
        client_type = get_client_type()
        
        # First try JWT authentication
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    user, token_data, error_code = _validate_jwt_token(token)
                    if error_code == "AUTH_TOKENS_CORRUPTED":
                        return jsonify({
                            "error": "Authentication tokens corrupted",
                            "message": "Please log in again to refresh your authentication tokens",
                            "code": "AUTH_TOKENS_CORRUPTED",
                            "force_reauth": True
                        }), 401
                    if user:
                        if not user.is_active:
                            return jsonify({
                                "error": "Account inactive",
                                "message": "Your account is pending approval or has been deactivated",
                                "code": "AUTH_ACCOUNT_INACTIVE"
                            }), 403

                        if user.is_suspended:
                            return jsonify({
                                "error": "Account suspended",
                                "message": "Your account has been suspended. Please contact support.",
                                "code": "AUTH_ACCOUNT_SUSPENDED"
                            }), 403

                        # Skip session validation for mobile and API clients
                        if client_type in ['mobile', 'api']:
                            g.api_user = user
                            g.token_data = token_data
                            return f(*args, **kwargs)

                        # Validate session only for web clients using Flask-Login
                        try:
                            if not current_user.is_authenticated:
                                return jsonify({
                                    "error": "Session invalid",
                                    "message": "Your session has expired or is invalid",
                                    "code": "AUTH_SESSION_INVALID"
                                }), 401
                        except Exception as e:
                            current_app.logger.warning(f"Session validation failed: {e}")
                            # Continue with JWT authentication even if session validation fails

                        g.api_user = user
                        g.token_data = token_data
                        return f(*args, **kwargs)

                except Exception as e:
                    current_app.logger.warning(f"JWT authentication failed: {e}")

        # Fall back to session authentication (Flask-Login) for web clients only
        if client_type == 'web' and current_user.is_authenticated:
            # Validate session for web users using Flask-Login
            try:
                if not current_user.is_authenticated:
                    from flask_login import logout_user
                    logout_user()
                    return jsonify({
                        "error": "Session invalid",
                        "message": "Your session has expired or is invalid",
                        "code": "AUTH_SESSION_INVALID"
                    }), 401
            except Exception as e:
                current_app.logger.warning(f"Session validation failed: {e}")
                # Continue with session authentication even if validation fails
            
            return f(*args, **kwargs)

        # No valid authentication found
        return jsonify({
            "error": "Authentication required",
            "message": f"Please provide valid authentication for {client_type} client",
            "code": "AUTH_REQUIRED"
        }), 401

    return decorated


def token_required(f):
    """JWT-only authentication decorator (for backward compatibility)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Authorization header missing or invalid",
                "message": "Please provide a valid Bearer token in the Authorization header",
                "code": "AUTH_MISSING_TOKEN"
            }), 401

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({
                "error": "Token missing in Authorization header",
                "message": "Please provide a valid Bearer token",
                "code": "AUTH_EMPTY_TOKEN"
            }), 401

        try:
            # Load token with max age
            data = _get_serializer(ACCESS_TOKEN_SALT).loads(token, max_age=get_token_ttl_for_client())
            user = User.query.get(data.get("user_id"))
            if not user:
                return jsonify({
                    "error": "User not found",
                    "message": "The user associated with this token no longer exists",
                    "code": "AUTH_USER_NOT_FOUND"
                }), 401

            if not user.is_active:
                return jsonify({
                    "error": "Account inactive",
                    "message": "Your account is pending approval or has been deactivated",
                    "code": "AUTH_ACCOUNT_INACTIVE"
                }), 403

            if user.is_suspended:
                return jsonify({
                    "error": "Account suspended",
                    "message": "Your account has been suspended. Please contact support.",
                    "code": "AUTH_ACCOUNT_SUSPENDED"
                }), 403

            g.api_user = user
            g.token_data = data

        except SignatureExpired:
            return jsonify({
                "error": "Token expired",
                "message": "Your access token has expired. Please refresh your token or login again.",
                "code": "AUTH_TOKEN_EXPIRED",
                "expires_in": get_token_ttl_for_client()
            }), 401
        except BadSignature:
            return jsonify({
                "error": "Invalid token",
                "message": "The provided token is malformed or invalid",
                "code": "AUTH_TOKEN_INVALID"
            }), 401
        except Exception as e:
            current_app.logger.error(f"Token validation error: {e}")
            return jsonify({
                "error": "Token validation failed",
                "message": "An error occurred while validating your token",
                "code": "AUTH_TOKEN_VALIDATION_ERROR"
            }), 500

        return f(*args, **kwargs)
    return decorated


@main_blueprint.route("/api/auth/register", methods=["POST"])
def external_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = (data.get("email") or "").strip() or None
    first_name = (data.get("first_name") or "").strip() or None
    last_name = (data.get("last_name") or "").strip() or None

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 409
    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 409

    new_user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=False,
        verified=False,
        role=UserRole.GENERAL,
    )
    try:
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Send verification email if email is provided
        verification_sent = False
        if email:
            try:
                # Initialize email service for API context
                _init_email_service_for_api()
                verification_sent = send_verification_email(new_user)
                if verification_sent:
                    current_app.logger.info(f"✅ Verification email sent to {email} for API registration")
                else:
                    current_app.logger.warning(f"⚠️ Failed to send verification email to {email} for API registration")
            except Exception as e:
                current_app.logger.error(f"❌ Error sending verification email for API registration: {e}")
                # Don't fail registration if email fails

        return jsonify({
            "message": "Registration successful. Please check your email to verify your account.",
            "user_id": new_user.id,
            "status": "pending_approval",
            "verification_email_sent": verification_sent
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"External register failed: {e}")
        return jsonify({"error": "registration failed"}), 500

@main_blueprint.route("/api/auth/forgot-password", methods=["POST"])
def external_forgot_password():
    """API endpoint for password reset requests."""
    data = request.get_json(silent=True) or {}
    email_or_username = (data.get("email_or_username") or "").strip()

    if not email_or_username:
        return jsonify({"error": "Email or username is required"}), 400

    # Find user by email or username
    user = find_user_by_username_or_email(email_or_username)

    if not user:
        # For security, don't reveal if user exists or not
        return jsonify({
            "message": "If an account with that email/username exists, a password reset link has been sent."
        }), 200

    if not user.email:
        return jsonify({"error": "User has no email address on file"}), 400

    try:
        # Initialize email service for API context
        _init_email_service_for_api()

        # Send password reset email using helper
        success = send_password_reset_email(user)
        if success:
            current_app.logger.info(f"✅ Password reset email sent to {user.email} for API request")
            return jsonify({
                "message": "Password reset email sent successfully",
                "email_sent": True
            }), 200
        else:
            current_app.logger.error(f"❌ Failed to send password reset email to {user.email} for API request")
            return jsonify({
                "message": "Failed to send password reset email. Please try again later.",
                "email_sent": False
            }), 500

    except Exception as e:
        current_app.logger.error(f"❌ Error in API forgot password: {e}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


@main_blueprint.route("/api/auth/reset-password", methods=["POST"])
def external_reset_password():
    """API endpoint for resetting password with token."""
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not token:
        return jsonify({"error": "Reset token is required"}), 400

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    try:
        # Verify the token
        s = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY", "change-me"), salt="password-reset")
        token_data = s.loads(token, max_age=3600)  # 1 hour expiration

        user_id = token_data.get("user_id")
        email = token_data.get("email")

        if not user_id or not email:
            return jsonify({"error": "Invalid password reset token"}), 400

        # Find user
        user = User.query.filter_by(id=user_id, email=email).first()
        if not user:
            return jsonify({"error": "Invalid password reset token"}), 400

        # Use unified password change handler
        success, message = handle_password_change(user, new_password)
        
        if success:
            current_app.logger.info(f"✅ Password reset successful for user {user.username} via API")
            return jsonify({
                "success": True,
                "message": "Password reset successfully. Please log in with your new password."
            }), 200
        else:
            return jsonify({"error": message}), 500

    except SignatureExpired:
        return jsonify({"error": "Password reset link has expired. Please request a new one."}), 400
    except BadSignature:
        return jsonify({"error": "Invalid password reset token"}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Error resetting password via API: {e}")
        return jsonify({"error": "An error occurred while resetting your password"}), 500


@main_blueprint.route("/api/auth/login", methods=["POST"])
def external_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username/email and password are required"}), 400

    # Find user by username or email
    user = find_user_by_username_or_email(username)

    if not user or not user.check_password(password):
        return jsonify({"error": "invalid username/email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "account pending approval"}), 403
    if user.is_suspended:
        return jsonify({"error": "account suspended"}), 403

    # Use unified authentication system for API users
    try:
        auth_helper = get_auth_helper()
        auth_result = auth_helper.authenticate_user(user, "api")
        
        if not auth_result["success"]:
            return jsonify(auth_result), 401
        
        # Get JWT tokens from the result
        jwt_tokens = {
            "access_token": auth_result.get("access_token"),
            "refresh_token": auth_result.get("refresh_token"),
            "token_type": auth_result.get("token_type", "Bearer"),
            "expires_in": auth_result.get("expires_in"),
            "user": auth_result.get("user"),
            "success": True,
            "message": "Login successful"
        }
        
        current_app.logger.info(f"Unified API authentication successful for user {user.username}")
        
        return jsonify(jwt_tokens)
        
    except Exception as e:
        current_app.logger.warning(f"Unified authentication failed for API user, falling back to basic tokens: {e}")
        # Fallback to basic token issuance
        return jsonify(_issue_tokens(user))


@main_blueprint.route("/api/auth/validate-token", methods=["POST"])
def external_validate_token():
    """Debug endpoint to validate token format and content."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "").strip()
    
    if not token:
        return jsonify({"error": "Token is required"}), 400
    
    # Clean token
    original_token = token
    token = token.replace('\n', '').replace('\r', '').replace(' ', '')
    
    parts = token.split('.')
    
    response = {
        "original_length": len(original_token),
        "cleaned_length": len(token),
        "parts_count": len(parts),
        "is_valid_format": len(parts) == 3,
        "parts_preview": [part[:20] + "..." if len(part) > 20 else part for part in parts],
        "has_newlines": '\n' in original_token,
        "has_carriage_returns": '\r' in original_token,
        "has_spaces": ' ' in original_token,
    }
    
    if len(parts) == 3:
        try:
            user, token_data, error_code = _validate_jwt_token(token)
            if error_code == "AUTH_TOKENS_CORRUPTED":
                return jsonify({
                    "error": "Authentication tokens corrupted",
                    "message": "Please log in again to refresh your authentication tokens",
                    "code": "AUTH_TOKENS_CORRUPTED",
                    "force_reauth": True
                }), 401
            response["token_valid"] = user is not None
            response["user_id"] = token_data.get("user_id") if token_data else None
            response["username"] = token_data.get("username") if token_data else None
        except Exception as e:
            response["token_valid"] = False
            response["error"] = str(e)
    else:
        response["token_valid"] = False
        response["error"] = f"Invalid format: {len(parts)} parts instead of 3"
    
    return jsonify(response)


@main_blueprint.route("/api/auth/mobile-test", methods=["POST"])
def mobile_auth_test():
    """Mobile authentication test endpoint with relaxed security."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if not username or not password:
        return jsonify({"error": "username/email and password are required"}), 400
    
    # Find user by username or email
    user = find_user_by_username_or_email(username)
    
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid username/email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "account pending approval"}), 403
    if user.is_suspended:
        return jsonify({"error": "account suspended"}), 403
    
    # Issue tokens with mobile-friendly settings
    try:
        tokens = _issue_tokens(user)
        tokens["mobile_optimized"] = True
        tokens["security_level"] = "relaxed"
        tokens["message"] = "Mobile authentication successful"
        return jsonify(tokens)
    except Exception as e:
        current_app.logger.error(f"Mobile auth test failed: {e}")
        return jsonify({"error": "Authentication failed", "details": str(e)}), 500


@main_blueprint.route("/api/auth/mobile-bypass", methods=["POST"])
def mobile_auth_bypass():
    """Mobile authentication bypass for development/testing."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if not username or not password:
        return jsonify({"error": "username/email and password are required"}), 400
    
    # Find user by username or email
    user = find_user_by_username_or_email(username)
    
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid username/email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "account pending approval"}), 403
    if user.is_suspended:
        return jsonify({"error": "account suspended"}), 403
    
    # Create tokens with mobile serializer directly (bypass all validation)
    try:
        from itsdangerous import URLSafeTimedSerializer
        import json as json_lib
        
        # Use mobile serializer directly
        mobile_secret = "lily-mobile-secret-key-2025"
        access_serializer = URLSafeTimedSerializer(mobile_secret, salt=ACCESS_TOKEN_SALT)
        refresh_serializer = URLSafeTimedSerializer(mobile_secret, salt=REFRESH_TOKEN_SALT)
        
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value if user.role else None,
            "is_premium": user.is_premium,
            "client_type": "mobile",
            "iat": datetime.now(timezone.utc).timestamp()
        }
        
        refresh_data = {
            "user_id": user.id,
            "username": user.username,
            "client_type": "mobile",
            "iat": datetime.now(timezone.utc).timestamp()
        }
        
        access_token = access_serializer.dumps(token_data)
        refresh_token = refresh_serializer.dumps(refresh_data)
        
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": MOBILE_ACCESS_TOKEN_TTL_SECONDS,
            "client_type": "mobile",
            "mobile_optimized": True,
            "security_level": "bypass",
            "message": "Mobile authentication bypass successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role.value if user.role else None,
                "is_premium": user.is_premium,
                "verified": user.verified,
            }
        }
        
        current_app.logger.info(f"Mobile auth bypass successful for user {user.username}")
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Mobile auth bypass failed: {e}")
        return jsonify({"error": "Authentication bypass failed", "details": str(e)}), 500


@main_blueprint.route("/api/auth/debug-token", methods=["POST"])
def debug_token_secret():
    """Debug endpoint to analyze token and find the correct secret key."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "").strip()
    
    if not token:
        return jsonify({"error": "Token is required"}), 400
    
    # Store original token for analysis
    original_token = token
    
    # Clean token (remove newlines, carriage returns, spaces)
    token = token.replace('\n', '').replace('\r', '').replace(' ', '')
    
    # Handle tokens that start with dots (like your Flutter app does)
    if token.startswith('.'):
        token = token[1:]  # Remove leading dot
        _safe_log("info", "Token started with dot, removed leading dot")
    
    response = {
        "original_token_length": len(original_token),
        "cleaned_token_length": len(token),
        "token_parts": len(token.split('.')),
        "starts_with_eyJ": token.startswith('eyJ'),
        "starts_with_dot": original_token.startswith('.'),
        "has_newlines": '\n' in original_token,
        "has_carriage_returns": '\r' in original_token,
        "has_spaces": ' ' in original_token,
        "attempts": []
    }
    
    # Try to decode without signature validation to see the payload
    try:
        import base64
        parts = token.split('.')
        if len(parts) >= 2:
            # Decode payload without signature validation
            payload = base64.urlsafe_b64decode(parts[1] + '==')
            import json
            payload_data = json.loads(payload)
            response["payload"] = payload_data
            response["user_id"] = payload_data.get("user_id")
            response["username"] = payload_data.get("username")
            response["iat"] = payload_data.get("iat")
            response["client_type"] = payload_data.get("client_type")
    except Exception as e:
        response["payload_error"] = str(e)
    
    # Try various secret keys that might have been used
    secret_keys_to_try = [
        "lily-mobile-secret-key-2025",
        "change-me",
        "your_secret_key",
        current_app.config.get("SECRET_KEY", "unknown"),
        "lily-opencms-secret",
        "flask-secret-key",
        "development-key",
        "test-secret-key"
    ]
    
    from itsdangerous import URLSafeTimedSerializer
    
    for secret_key in secret_keys_to_try:
        if secret_key == "unknown":
            continue
            
        try:
            # Try with different salts
            for salt in [ACCESS_TOKEN_SALT, "external-access-token", "access-token", ""]:
                serializer = URLSafeTimedSerializer(secret_key, salt=salt)
                data = serializer.loads(token)
                response["attempts"].append({
                    "secret_key": secret_key[:10] + "..." if len(secret_key) > 10 else secret_key,
                    "salt": salt,
                    "success": True,
                    "data": data
                })
                break
        except Exception as e:
            response["attempts"].append({
                "secret_key": secret_key[:10] + "..." if len(secret_key) > 10 else secret_key,
                "salt": salt if 'salt' in locals() else "unknown",
                "success": False,
                "error": str(e)[:100]
            })
    
    return jsonify(response)


@main_blueprint.route("/api/auth/flutter-debug", methods=["POST"])
def flutter_debug_token():
    """Special debug endpoint for Flutter app token analysis."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "").strip()
    
    if not token:
        return jsonify({"error": "Token is required"}), 400
    
    # Store original token
    original_token = token
    
    # Apply Flutter app's normalization logic
    normalized_token = token
    if token.startswith('.'):
        normalized_token = token[1:]
    
    # Clean token
    clean_token = normalized_token.replace('\n', '').replace('\r', '').replace(' ', '')
    
    response = {
        "original_token": original_token[:50] + "..." if len(original_token) > 50 else original_token,
        "normalized_token": normalized_token[:50] + "..." if len(normalized_token) > 50 else normalized_token,
        "clean_token": clean_token[:50] + "..." if len(clean_token) > 50 else clean_token,
        "original_length": len(original_token),
        "normalized_length": len(normalized_token),
        "clean_length": len(clean_token),
        "starts_with_dot": original_token.startswith('.'),
        "starts_with_eyJ": clean_token.startswith('eyJ'),
        "is_valid_jwt_format": clean_token.startswith('eyJ'),
        "token_parts": len(clean_token.split('.')),
        "analysis": {}
    }
    
    # Try to extract user info using bypass method
    try:
        parts = clean_token.split('.')
        if len(parts) >= 2:
            import base64
            import json
            
            # Try to decode payload
            payload_part = parts[1]
            payload_part += '=' * (4 - len(payload_part) % 4)
            payload = base64.urlsafe_b64decode(payload_part)
            payload_data = json.loads(payload)
            
            response["analysis"]["payload_decode_success"] = True
            response["analysis"]["user_id"] = payload_data.get("user_id")
            response["analysis"]["username"] = payload_data.get("username")
            response["analysis"]["iat"] = payload_data.get("iat")
            response["analysis"]["client_type"] = payload_data.get("client_type")
            
            # Try to get user from database
            if payload_data.get("user_id"):
                user = User.query.get(payload_data["user_id"])
                if user:
                    response["analysis"]["user_exists"] = True
                    response["analysis"]["user_active"] = user.is_active
                    response["analysis"]["user_suspended"] = user.is_suspended
                    response["analysis"]["user_username"] = user.username
                else:
                    response["analysis"]["user_exists"] = False
        else:
            response["analysis"]["payload_decode_success"] = False
            response["analysis"]["error"] = "Invalid token format"
            
    except Exception as e:
        response["analysis"]["payload_decode_success"] = False
        response["analysis"]["error"] = str(e)
    
    return jsonify(response)


@main_blueprint.route("/api/auth/refresh", methods=["POST"])
def external_refresh():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token") or ""

    if not refresh_token:
        return jsonify({
            "error": "refresh_token is required",
            "message": "Please provide your refresh token to get a new access token",
            "code": "AUTH_REFRESH_TOKEN_MISSING"
        }), 400

    try:
        # Validate JWT refresh token using simple JWT manager
        from routes.utils.simple_jwt_session import get_simple_jwt_manager
        jwt_manager = get_simple_jwt_manager()

        # Validate the refresh token
        payload = jwt_manager.validate_token(refresh_token)

        if not payload:
            return jsonify({
                "error": "Invalid refresh token",
                "message": "The provided refresh token is invalid or expired",
                "code": "AUTH_REFRESH_TOKEN_INVALID"
            }), 401

        # Check if it's actually a refresh token
        if payload.get('type') != 'refresh':
            return jsonify({
                "error": "Invalid token type",
                "message": "The provided token is not a refresh token",
                "code": "AUTH_REFRESH_TOKEN_INVALID_TYPE"
            }), 401

        # Get user from token
        user = jwt_manager.get_user_from_token(refresh_token)
        if not user:
            return jsonify({
                "error": "User not found",
                "message": "The user associated with this refresh token no longer exists",
                "code": "AUTH_REFRESH_USER_NOT_FOUND"
            }), 401

        if not user.is_active:
            return jsonify({
                "error": "Account inactive",
                "message": "Your account is pending approval or has been deactivated",
                "code": "AUTH_REFRESH_ACCOUNT_INACTIVE"
            }), 403

        if user.is_suspended:
            return jsonify({
                "error": "Account suspended",
                "message": "Your account has been suspended. Please contact support.",
                "code": "AUTH_REFRESH_ACCOUNT_SUSPENDED"
            }), 403

        # Check if refresh token is within sliding window (30 days from issuance)
        token_age = datetime.now(timezone.utc) - datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc)
        if token_age.total_seconds() > SLIDING_REFRESH_WINDOW_SECONDS:
            return jsonify({
                "error": "Refresh token expired",
                "message": "Your refresh token has exceeded the maximum lifetime. Please login again.",
                "code": "AUTH_REFRESH_TOKEN_SLIDING_WINDOW_EXCEEDED",
                "max_lifetime_days": SLIDING_REFRESH_WINDOW_SECONDS // (60 * 60 * 24)
            }), 401

        # Issue new tokens
        tokens = _issue_tokens(user)

        # Log refresh activity
        current_app.logger.info(f"Token refreshed for user {user.username} (ID: {user.id})")

        return jsonify({
            **tokens,
            "message": "Token refreshed successfully",
            "refresh_window_days": SLIDING_REFRESH_WINDOW_SECONDS // (60 * 60 * 24)
        })

    except Exception as e:
        current_app.logger.error(f"Refresh token validation error: {e}")
        return jsonify({
            "error": "Refresh token validation failed",
            "message": "An error occurred while validating your refresh token",
            "code": "AUTH_REFRESH_TOKEN_VALIDATION_ERROR"
        }), 500


@main_blueprint.route("/api/auth/logout", methods=["POST"])
def external_logout():
    # Stateless tokens cannot be revoked server-side without a store/denylist.
    # Clients should discard tokens. We respond success for consistency.
    return jsonify({"message": "logged out"})


@main_blueprint.route("/api/auth/me", methods=["GET"])
@unified_auth_required
def external_me():
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if user.role else None,
        "is_premium": user.is_premium,
        "verified": user.verified,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    })


# =============================
# External Profile & Account API
# =============================


def _get_or_create_user_profile(user):
    try:
        from models import UserProfile
    except ImportError:
        UserProfile = None
    except Exception:
        UserProfile = None
    if not UserProfile:
        return None
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
    return profile


@main_blueprint.route("/api/auth/profile", methods=["GET"])
@unified_auth_required
def external_get_profile():
    """Get current user's profile. Works with both Firebase and username/email+password auth."""
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    
    if not user:
        return jsonify({
            "success": False,
            "error": "User not found",
            "message": "Unable to retrieve user information",
            "code": "USER_NOT_FOUND"
        }), 401
    
    profile = _get_or_create_user_profile(user)
    profile_dict = profile.to_dict() if hasattr(profile, "to_dict") and profile else {}
    
    # Get profile picture URL from user's profile_picture or provider_data
    profile_picture_url = None
    if user.profile_picture:
        profile_picture_url = user.profile_picture
    elif hasattr(user, 'provider_data') and user.provider_data:
        profile_picture_url = user.parsed_provider_data.get('photo_url')
    
    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,  # Always include email for own profile
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name or ''} {user.last_name or ''}".strip(),
            "birthdate": user.birthdate.isoformat() if getattr(user, "birthdate", None) else None,
            "age": user.get_age() if hasattr(user, 'get_age') else None,
            "bio": user.bio,
            "role": user.role.value if user.role else None,
            "custom_role": user.custom_role.name if user.custom_role else None,
            "is_active": user.is_active,
            "is_premium": user.is_premium,
            "verified": user.verified,
            "is_suspended": user.is_suspended,
            "write_access": user.write_access,
            "auth_provider": user.auth_provider if hasattr(user, 'auth_provider') else None,
            "profile_picture_url": profile_picture_url,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
        },
        "profile": profile_dict,
    })


@main_blueprint.route("/api/auth/profile", methods=["PUT", "PATCH"])
@unified_auth_required
def external_update_profile():
    """Update current user's profile. Works with both Firebase and username/email+password auth."""
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    
    if not user:
        return jsonify({
            "success": False,
            "error": "User not found",
            "message": "Unable to retrieve user information",
            "code": "USER_NOT_FOUND"
        }), 401
    
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "error": "No update data provided", "code": "MISSING_DATA"}), 400

    updated = False
    changes = []
    # Update user fields
    user_fields = ["first_name", "last_name", "email", "bio"]
    for field in user_fields:
        if field in data:
            new_val = data.get(field) or None
            old_val = getattr(user, field)
            if old_val != new_val:
                setattr(user, field, new_val)
                changes.append(field)
                updated = True

    if "birthdate" in data:
        birthdate_value = data.get("birthdate")
        new_bd = None
        if birthdate_value:
            try:
                if "T" in birthdate_value:
                    birthdate_value = birthdate_value.split("T", 1)[0]
                new_bd = datetime.strptime(birthdate_value, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"success": False, "error": "Invalid birthdate format, expected YYYY-MM-DD", "code": "INVALID_FORMAT"}), 400
        
        if user.birthdate != new_bd:
            user.birthdate = new_bd
            changes.append("birthdate")
            updated = True

    # Update profile fields
    profile = _get_or_create_user_profile(user)
    if profile:
        profile_fields = ["pronouns", "short_bio", "location", "website"]
        for field in profile_fields:
            if field in data:
                new_val = data.get(field)
                old_val = getattr(profile, field)
                if old_val != new_val:
                    setattr(profile, field, new_val)
                    changes.append(field)
                    updated = True
                    
        if "social_links" in data and isinstance(data.get("social_links"), dict):
            profile.social_links = data.get("social_links")
            changes.append("social_links")
            updated = True
            
        bool_fields = ["is_public", "show_email", "show_birthdate"]
        for f in bool_fields:
            if f in data:
                new_val = bool(data.get(f))
                old_val = getattr(profile, f)
                if old_val != new_val:
                    setattr(profile, f, new_val)
                    changes.append(f)
                    updated = True

    if not updated:
        return jsonify({"success": True, "message": "No changes detected", "user": {"id": user.id, "username": user.username}}), 200

    try:
        db.session.commit()
        
        # Audit Log
        try:
            from models import UserActivity
            audit = UserActivity(
                user_id=user.id,
                activity_type='UPDATE_PROFILE',
                description=f"External profile update: {', '.join(changes)}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")

        # Get profile picture URL
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = user.profile_picture
        elif hasattr(user, 'provider_data') and user.provider_data:
            profile_picture_url = user.parsed_provider_data.get('photo_url')

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "birthdate": user.birthdate.isoformat() if getattr(user, "birthdate", None) else None,
                "age": user.get_age() if hasattr(user, 'get_age') else None,
                "bio": user.bio,
                "role": user.role.value if user.role else None,
                "custom_role": user.custom_role.name if user.custom_role else None,
                "is_active": user.is_active,
                "is_premium": user.is_premium,
                "verified": user.verified,
                "is_suspended": user.is_suspended,
                "write_access": user.write_access,
                "auth_provider": user.auth_provider if hasattr(user, 'auth_provider') else None,
                "profile_picture_url": profile_picture_url,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "login_count": user.login_count,
            },
            "profile": (profile.to_dict() if hasattr(profile, "to_dict") and profile else {}),
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in external_update_profile: {e}")
        return jsonify({"success": False, "error": "Internal server error", "code": "INTERNAL_ERROR"}), 500


@main_blueprint.route("/api/auth/profile/privacy", methods=["PATCH"])
@unified_auth_required
def external_update_privacy():
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    data = request.get_json(silent=True) or {}
    profile = _get_or_create_user_profile(user)
    if not profile:
        return jsonify({"error": "Profile not available"}), 400

    for flag in ["show_email", "show_birthdate"]:
        if flag in data:
            setattr(profile, flag, bool(data.get(flag)))

    db.session.commit()

    return jsonify({
        "message": "Privacy updated",
        "profile": profile.to_dict() if hasattr(profile, "to_dict") else {
            "show_email": getattr(profile, "show_email", False),
            "show_birthdate": getattr(profile, "show_birthdate", False),
        }
    })


@main_blueprint.route("/api/auth/profile/username", methods=["PATCH"])
@unified_auth_required
def external_change_username():
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    data = request.get_json(silent=True) or {}
    new_username = (data.get("username") or "").strip()
    current_password = data.get("current_password") or ""

    if not new_username or not current_password:
        return jsonify({"error": "username and current_password are required"}), 400
    # Validate format
    import re
    if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", new_username):
        return jsonify({"error": "invalid username format"}), 400
    # Check password
    if not user.check_password(current_password):
        return jsonify({"error": "current password is incorrect"}), 400
    # Uniqueness
    if User.query.filter(User.username == new_username, User.id != user.id).first():
        return jsonify({"error": "username already taken"}), 409

    old_username = user.username
    user.username = new_username
    db.session.commit()

    return jsonify({
        "message": "Username updated",
        "old_username": old_username,
        "new_username": new_username,
    })


@main_blueprint.route("/api/auth/account/change-password", methods=["POST"])
@unified_auth_required
def external_change_password():
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    
    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not new_password or new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400

    # Use unified password change handler
    success, message = handle_password_change(user, new_password, current_password)
    
    if success:
        return jsonify({"message": "Password changed successfully"}), 200
    else:
        return jsonify({"error": message}), 400


@main_blueprint.route("/api/auth/account", methods=["DELETE"])
@unified_auth_required
def external_delete_account():
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    try:
        # Best-effort cascade similar to internal endpoint
        try:
            from models import News
            News.query.filter_by(user_id=user.id).delete()
        except Exception:
            pass
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =============================
# JWT-BASED LIBRARY ENDPOINTS
# =============================

# =============================
# JWT-BASED USER LIBRARY ENDPOINTS (for backward compatibility)
# =============================

# =============================
# JWT-BASED AUTH LIBRARY ENDPOINTS (for direct JWT API calls)
# =============================

@main_blueprint.route("/api/auth/library", methods=["POST"])
@unified_auth_required
def external_add_to_library():
    """Add content to library using unified authentication."""
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    data = request.get_json(silent=True) or {}

    content_type = data.get("content_type")
    content_id = data.get("content_id")

    if not content_type or not content_id:
        return jsonify({"error": "content_type and content_id are required"}), 400

    if content_type not in ("news", "album"):
        return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

    if not isinstance(content_id, int):
        return jsonify({"error": "content_id must be an integer"}), 400

    try:
        # Check if already in library
        existing = UserLibrary.query.filter_by(
            user_id=user.id,
            content_type=content_type,
            content_id=content_id
        ).first()

        if existing:
            return jsonify({
                "success": True,
                "message": "Content already in library",
                "library_item": {
                    "id": existing.id,
                    "content_type": existing.content_type,
                    "content_id": existing.content_id,
                    "added_at": existing.added_at.isoformat() if existing.added_at else None
                }
            }), 200

        # Add to library
        library_item = UserLibrary(
            user_id=user.id,
            content_type=content_type,
            content_id=content_id
        )

        db.session.add(library_item)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Added to library successfully",
            "library_item": {
                "id": library_item.id,
                "content_type": library_item.content_type,
                "content_id": library_item.content_id,
                "added_at": library_item.added_at.isoformat() if library_item.added_at else None
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding to library: {e}")
        return jsonify({"error": "Failed to add to library", "details": str(e)}), 500


@main_blueprint.route("/api/auth/library", methods=["DELETE"])
@unified_auth_required
def external_remove_from_library():
    """Remove content from library using unified authentication."""
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()
    data = request.get_json(silent=True) or {}

    content_type = data.get("content_type")
    content_id = data.get("content_id")

    if not content_type or not content_id:
        return jsonify({"error": "content_type and content_id are required"}), 400

    if content_type not in ("news", "album"):
        return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

    if not isinstance(content_id, int):
        return jsonify({"error": "content_id must be an integer"}), 400

    try:
        # Find library item
        library_item = UserLibrary.query.filter_by(
            user_id=user.id,
            content_type=content_type,
            content_id=content_id
        ).first()

        if not library_item:
            return jsonify({"error": "Content not found in library"}), 404

        db.session.delete(library_item)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Removed from library successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing from library: {e}")
        return jsonify({"error": "Failed to remove from library", "details": str(e)}), 500


@main_blueprint.route("/api/auth/library/check", methods=["GET"])
@unified_auth_required
def external_check_in_library():
    """Check if content is in user's library using unified authentication."""
    auth_helper = get_auth_helper()
    user = auth_helper.get_current_user()

    content_type = request.args.get("content_type")
    content_id = request.args.get("content_id", type=int)

    if not content_type or not content_id:
        return jsonify({"error": "content_type and content_id are required"}), 400

    if content_type not in ("news", "album"):
        return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

    try:
        # Check if in library
        exists = UserLibrary.query.filter_by(
            user_id=user.id,
            content_type=content_type,
            content_id=content_id
        ).first() is not None

        return jsonify({
            "success": True,
            "in_library": exists,
            "content_type": content_type,
            "content_id": content_id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error checking library status: {e}")
        return jsonify({"error": "Failed to check library status", "details": str(e)}), 500


# =============================
# JWT-BASED COMMENT ENDPOINTS
# =============================

@main_blueprint.route("/api/auth/comments/<type>/<int:id>", methods=["POST"])
def external_post_comment(type, id):
    """Post a comment using JWT authentication."""
    try:
        from flask_login import current_user

        # Combined authentication logic (both JWT and session)
        auth_header = request.headers.get("Authorization", "")
        user = None

        if auth_header.startswith("Bearer "):
            # Try JWT authentication
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                # Clean and validate JWT token format
                token = token.strip()
                # Remove any potential extra whitespace or newlines
                token = token.replace('\n', '').replace('\r', '').replace(' ', '')
                
                # Validate JWT token format first
                parts = token.split('.')
                if len(parts) != 3:
                    _safe_log("warning", "Invalid JWT token format: {} parts instead of 3", len(parts))
                    _safe_log("debug", "Token parts: {}", [part[:20] + "..." if len(part) > 20 else part for part in parts])
                    return jsonify({"error": "Invalid token format"}), 401

                user, token_data, error_code = _validate_jwt_token(token)
            if error_code == "AUTH_TOKENS_CORRUPTED":
                return jsonify({
                    "error": "Authentication tokens corrupted",
                    "message": "Please log in again to refresh your authentication tokens",
                    "code": "AUTH_TOKENS_CORRUPTED",
                    "force_reauth": True
                }), 401
                if user:
                    if not user.is_active:
                        return jsonify({"error": "Account inactive"}), 403
                    if user.is_suspended:
                        return jsonify({"error": "Account suspended"}), 403
                    # Token is valid and user is active
                    g.api_user = user
                    g.token_data = token_data
                    # Don't return here - continue processing the POST request
                else:
                    # JWT validation failed, try mobile bypass
                    try:
                        parts = token.split('.')
                        if len(parts) >= 2:
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
                                    _safe_log("info", "Mobile bypass successful for user {}", user.username)
                                else:
                                    return jsonify({"error": "User not found or inactive"}), 401
                            else:
                                return jsonify({"error": "Invalid token payload"}), 401
                        else:
                            return jsonify({"error": "Invalid token format"}), 401
                    except Exception as bypass_error:
                        _safe_log("debug", "Mobile bypass failed: {}", bypass_error)
                        return jsonify({"error": "Authentication failed"}), 401

        # Fall back to session authentication
        if not user:
            if current_user.is_authenticated:
                user = current_user

        if not user:
            return jsonify({"error": "Authentication required"}), 401

        # Set user in g object for consistency with other endpoints
        g.api_user = user

        data = request.get_json(silent=True) or {}

        if type not in ('news', 'album'):
            return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

        content = data.get('content', '').strip()
        rating = data.get('rating')
        parent_id = data.get('parent_comment_id')

        if not content:
            return jsonify({"error": "Comment content is required"}), 400

        # Validate parent comment if provided
        if parent_id:
            parent_comment = Comment.query.filter_by(id=parent_id, content_type=type, content_id=id).first()
            if not parent_comment:
                return jsonify({"error": "Parent comment not found"}), 404
            if parent_comment.is_deleted:
                return jsonify({"error": "Cannot reply to deleted comment"}), 400

        # Create comment
        comment = Comment(
            content=content,
            content_type=type,
            content_id=id,
            user_id=user.id,
            parent_id=parent_id,
            is_approved=True,  # Auto-approve for authenticated users
            is_deleted=False
        )

        # If rating is provided, create a separate Rating record
        if rating is not None:
            rating_obj = Rating(
                rating_value=rating,
                content_type=type,
                content_id=id,
                user_id=user.id
            )
            db.session.add(rating_obj)

        # Validate comment before saving
        comment.validate()

        db.session.add(comment)
        db.session.commit()
        
        # Award coins for posting comment
        try:
            from routes.utils.coin_earning_service import CoinEarningService
            coin_result = CoinEarningService.award_comment_coins(user.id, comment.id, id)
            if coin_result['success']:
                current_app.logger.info(f"User {user.id} earned {coin_result['coins_awarded']} coins for posting comment {comment.id}")
        except Exception as coin_error:
            current_app.logger.error(f"Failed to award comment coins for user {user.id}, comment {comment.id}: {coin_error}")

        return jsonify({
            "success": True,
            "message": "Comment posted successfully",
            "comment": comment.to_dict()
        }), 201

    except ValueError as ve:
        _safe_log("error", "Comment validation error: {}", ve)
        try:
            db.session.rollback()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")
        return jsonify({"error": "Comment validation failed", "details": str(ve)}), 400
    except Exception as e:
        _safe_log("error", "Error posting comment: {}", e)
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({"error": "Failed to post comment", "details": str(e)}), 500


@main_blueprint.route("/api/auth/comments/<type>/<int:id>/rate", methods=["POST"])
def external_rate_content(type, id):
    """Rate content using JWT authentication."""
    from flask_login import current_user

    # Combined authentication logic (both JWT and session)
    auth_header = request.headers.get("Authorization", "")
    user = None

    if auth_header.startswith("Bearer "):
        # Try JWT authentication
        token = auth_header.split(" ", 1)[1].strip()
        if token:
            try:
                # Clean and validate JWT token format
                token = token.strip()
                # Remove any potential extra whitespace or newlines
                token = token.replace('\n', '').replace('\r', '').replace(' ', '')
                
                # Validate JWT token format first
                parts = token.split('.')
                if len(parts) != 3:
                    _safe_log("warning", "Invalid JWT token format: {} parts instead of 3", len(parts))
                    _safe_log("debug", "Token parts: {}", [part[:20] + "..." if len(part) > 20 else part for part in parts])
                    return jsonify({"error": "Invalid token format"}), 401
                else:
                    user, token_data, error_code = _validate_jwt_token(token)
                    if error_code == "AUTH_TOKENS_CORRUPTED":
                        return jsonify({
                            "error": "Authentication tokens corrupted",
                            "message": "Please log in again to refresh your authentication tokens",
                            "code": "AUTH_TOKENS_CORRUPTED",
                            "force_reauth": True
                        }), 401
                    if user:
                        if not user.is_active:
                            return jsonify({"error": "Account inactive"}), 403
                        if user.is_suspended:
                            return jsonify({"error": "Account suspended"}), 403
                        # Token is valid and user is active
                        g.api_user = user
                        g.token_data = token_data
                        # Don't return here - continue processing the POST request
            except Exception as jwt_error:
                _safe_log("warning", "JWT authentication failed: {}", jwt_error)

        # Fall back to session authentication
    if not user:
        if current_user.is_authenticated:
            user = current_user

    if not user:
        return jsonify({"error": "Authentication required"}), 401

    # Set user in g object for consistency
    g.api_user = user

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if type not in ('news', 'album'):
        return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

    rating_value = data.get('rating')

    if not rating_value or rating_value < 1 or rating_value > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    try:
        # Check if user already rated this content
        existing_rating = Rating.query.filter_by(
            user_id=user.id,
            content_type=type,
            content_id=id
        ).first()

        if existing_rating:
            # Update existing rating
            existing_rating.rating_value = rating_value
            message = "Rating updated successfully"
            rating_obj = existing_rating
        else:
            # Create new rating
            rating_obj = Rating(
                user_id=user.id,
                content_type=type,
                content_id=id,
                rating_value=rating_value
            )
            db.session.add(rating_obj)
            message = "Rating submitted successfully"

        db.session.commit()
        
        # Award coins for giving rating (only for new ratings, not updates)
        if not existing_rating:
            try:
                from routes.utils.coin_earning_service import CoinEarningService
                coin_result = CoinEarningService.award_rating_coins(user.id, rating_obj.id, id)
                if coin_result['success']:
                    current_app.logger.info(f"User {user.id} earned {coin_result['coins_awarded']} coins for rating {type} {id}")
            except Exception as coin_error:
                current_app.logger.error(f"Failed to award rating coins for user {user.id}, rating {rating_obj.id}: {coin_error}")

        return jsonify({
            "success": True,
            "message": message,
            "rating": {
                "id": existing_rating.id if existing_rating else rating_obj.id,
                "rating": rating_value,
                "user_id": user.id,
                "content_type": type,
                "content_id": id
            }
        }), 201 if not existing_rating else 200

    except Exception as e:
        _safe_log("error", "Error rating content: {}", e)
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({"error": "Failed to rate content", "details": str(e)}), 500


@main_blueprint.route("/api/auth/comments/<type>/<int:id>", methods=["GET"])
def external_get_comments(type, id):
    """Get comments for content using JWT authentication."""
    from flask_login import current_user

    # Combined authentication logic (both JWT and session)
    auth_header = request.headers.get("Authorization", "")
    user = None

    if auth_header.startswith("Bearer "):
        # Try JWT authentication
        token = auth_header.split(" ", 1)[1].strip()
        if token:
            try:
                # Clean and validate JWT token format
                token = token.strip()
                # Remove any potential extra whitespace or newlines
                token = token.replace('\n', '').replace('\r', '').replace(' ', '')
                
                # Validate JWT token format first
                parts = token.split('.')
                if len(parts) != 3:
                    _safe_log("warning", "Invalid JWT token format: {} parts instead of 3", len(parts))
                    _safe_log("debug", "Token parts: {}", [part[:20] + "..." if len(part) > 20 else part for part in parts])
                    return jsonify({"error": "Invalid token format"}), 401
                else:
                    user, token_data, error_code = _validate_jwt_token(token)
                    if error_code == "AUTH_TOKENS_CORRUPTED":
                        return jsonify({
                            "error": "Authentication tokens corrupted",
                            "message": "Please log in again to refresh your authentication tokens",
                            "code": "AUTH_TOKENS_CORRUPTED",
                            "force_reauth": True
                        }), 401
                    if user:
                        if not user.is_active:
                            return jsonify({"error": "Account inactive"}), 403
                        if user.is_suspended:
                            return jsonify({"error": "Account suspended"}), 403
                        # Token is valid and user is active
                        g.api_user = user
                        g.token_data = token_data
                        # Don't return here - continue processing the GET request
                    else:
                        # JWT validation failed, try mobile bypass
                        try:
                            parts = token.split('.')
                            if len(parts) >= 2:
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
                                        _safe_log("info", "Mobile bypass successful for user {}", user.username)
                                    else:
                                        return jsonify({"error": "User not found or inactive"}), 401
                                else:
                                    return jsonify({"error": "Invalid token payload"}), 401
                            else:
                                return jsonify({"error": "Invalid token format"}), 401
                        except Exception as bypass_error:
                            _safe_log("debug", "Mobile bypass failed: {}", bypass_error)
                            return jsonify({"error": "Authentication failed"}), 401
            except Exception as jwt_error:
                _safe_log("warning", "JWT authentication failed: {}", jwt_error)

    # Fall back to session authentication
    if not user:
        if current_user.is_authenticated:
            user = current_user

    if not user:
        return jsonify({"error": "Authentication required"}), 401

    # Set user in g object for consistency
    g.api_user = user

    if type not in ('news', 'album'):
        return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)

    try:
        # Get comments with replies
        comments_query = Comment.query.filter_by(
            content_type=type,
            content_id=id,
            is_approved=True,
            is_deleted=False,
            parent_id=None  # Only top-level comments
        ).order_by(Comment.created_at.desc())

        comments_pagination = comments_query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        comments_data = []
        for comment in comments_pagination.items:
            comment_dict = comment.to_dict()

            # Add user's like/dislike status
            comment_dict['user_liked'] = comment.is_liked_by_user(user.id)
            comment_dict['user_disliked'] = comment.is_disliked_by_user(user.id)
            comment_dict['like_count'] = comment.get_likes_count()
            comment_dict['dislike_count'] = comment.get_dislikes_count()

            # Get replies if requested
            include_replies = request.args.get('include_replies', 'false').lower() == 'true'
            if include_replies:
                replies = Comment.query.filter_by(
                    parent_id=comment.id,
                    is_approved=True,
                    is_deleted=False
                ).order_by(Comment.created_at.asc()).all()

                replies_data = []
                for reply in replies:
                    reply_dict = reply.to_dict()
                    reply_dict['user_liked'] = reply.is_liked_by_user(user.id)
                    reply_dict['user_disliked'] = reply.is_disliked_by_user(user.id)
                    reply_dict['like_count'] = reply.get_likes_count()
                    reply_dict['dislike_count'] = reply.get_dislikes_count()
                    replies_data.append(reply_dict)

                comment_dict['replies'] = replies_data

            comments_data.append(comment_dict)

        return jsonify({
            "success": True,
            "comments": comments_data,
            "pagination": {
                "page": comments_pagination.page,
                "per_page": comments_pagination.per_page,
                "total": comments_pagination.total,
                "pages": comments_pagination.pages,
                "has_next": comments_pagination.has_next,
                "has_prev": comments_pagination.has_prev
            }
        }), 200

    except Exception as e:
        _safe_log("error", "Error getting comments: {}", e)
        return jsonify({"error": "Failed to get comments", "details": str(e)}), 500


# =============================
# JWT-BASED COMMENT ENDPOINTS (backward compatibility)
# =============================

@main_blueprint.route("/api/auth/comments", methods=["POST"])
@unified_auth_required
def jwt_create_comment():
    """Create a new comment using JWT authentication."""
    user = g.api_user
    data = request.get_json(silent=True) or {}

    content_type = data.get('content_type')
    content_id = data.get('content_id')
    content = data.get('content', '').strip()
    rating = data.get('rating')
    parent_id = data.get('parent_comment_id')

    if not content_type or not content_id or not content:
        return jsonify({"error": "content_type, content_id, and content are required"}), 400

    if content_type not in ('news', 'album'):
        return jsonify({"error": "Invalid content_type. Must be 'news' or 'album'"}), 400

    if not isinstance(content_id, int):
        return jsonify({"error": "content_id must be an integer"}), 400

    # Validate parent comment if provided
    if parent_id:
        parent_comment = Comment.query.filter_by(id=parent_id, content_type=content_type, content_id=content_id).first()
        if not parent_comment:
            return jsonify({"error": "Parent comment not found"}), 404
        if parent_comment.is_deleted:
            return jsonify({"error": "Cannot reply to deleted comment"}), 400

    try:
        # Create comment
        comment = Comment(
            content=content,
            content_type=content_type,
            content_id=content_id,
            user_id=user.id,
            parent_id=parent_id,
            rating=rating,
            is_approved=True,  # Auto-approve for authenticated users
            is_deleted=False
        )

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Comment created successfully",
            "comment": comment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating comment: {e}")
        return jsonify({"error": "Failed to create comment", "details": str(e)}), 500


@main_blueprint.route("/api/auth/comments/<int:comment_id>", methods=["PUT"])
@unified_auth_required
def jwt_update_comment(comment_id):
    """Update comment using JWT authentication."""
    user = g.api_user
    data = request.get_json(silent=True) or {}

    content = data.get('content', '').strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    try:
        comment = Comment.query.filter_by(id=comment_id, user_id=user.id).first()
        if not comment:
            return jsonify({"error": "Comment not found or not owned by user"}), 404

        if comment.is_deleted:
            return jsonify({"error": "Cannot update deleted comment"}), 400

        comment.content = content
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Comment updated successfully",
            "comment": comment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating comment: {e}")
        return jsonify({"error": "Failed to update comment", "details": str(e)}), 500


@main_blueprint.route("/api/auth/comments/<int:comment_id>", methods=["DELETE"])
@unified_auth_required
def jwt_delete_comment(comment_id):
    """Delete comment using JWT authentication."""
    user = g.api_user

    try:
        comment = Comment.query.filter_by(id=comment_id, user_id=user.id).first()
        if not comment:
            return jsonify({"error": "Comment not found or not owned by user"}), 404

        if comment.is_deleted:
            return jsonify({"error": "Comment already deleted"}), 400

        # Soft delete
        comment.is_deleted = True
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Comment deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting comment: {e}")
        return jsonify({"error": "Failed to delete comment", "details": str(e)}), 500


@main_blueprint.route("/api/auth/comments/<int:comment_id>/like", methods=["POST"])
@unified_auth_required
def jwt_like_comment(comment_id):
    """Like/dislike comment using JWT authentication."""
    user = g.api_user
    data = request.get_json(silent=True) or {}

    is_like = data.get('is_like', True)

    try:
        comment = Comment.query.filter_by(id=comment_id, is_deleted=False).first()
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        # Check if user already liked/disliked this comment
        existing_like = CommentLike.query.filter_by(
            comment_id=comment_id,
            user_id=user.id
        ).first()

        if existing_like:
            if existing_like.is_like == is_like:
                # User is trying to do the same action again, remove the like/dislike
                db.session.delete(existing_like)
                db.session.commit()
                return jsonify({
                    "success": True,
                    "message": "Reaction removed successfully",
                    "is_like": is_like,
                    "like_count": comment.get_likes_count(),
                    "dislike_count": comment.get_dislikes_count()
                }), 200
            else:
                # User is changing from like to dislike or vice versa
                existing_like.is_like = is_like
                db.session.commit()
                return jsonify({
                    "success": True,
                    "message": "Reaction updated successfully",
                    "is_like": is_like,
                    "like_count": comment.get_likes_count(),
                    "dislike_count": comment.get_dislikes_count()
                }), 200
        else:
            # Create new like/dislike
            new_like = CommentLike(
                comment_id=comment_id,
                user_id=user.id,
                is_like=is_like
            )
            db.session.add(new_like)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Reaction added successfully",
                "is_like": is_like,
                "like_count": comment.get_like_count(),
                "dislike_count": comment.get_dislike_count()
            }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error handling comment reaction: {e}")
        return jsonify({"error": "Failed to process reaction", "details": str(e)}), 500


@main_blueprint.route("/api/auth/force-reauth", methods=["POST"])
def force_reauth():
    """Force client to clear all tokens and re-authenticate.
    This endpoint returns a specific error code that the Android app can detect
    to trigger a complete token cleanup and re-authentication flow.
    """
    return jsonify({
        "error": "Authentication tokens corrupted",
        "message": "Please log in again to refresh your authentication tokens",
        "code": "AUTH_TOKENS_CORRUPTED",
        "force_reauth": True
    }), 401
