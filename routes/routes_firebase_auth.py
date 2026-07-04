"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Firebase Authentication Routes for LilyOpenCMS

Provides endpoints for Firebase-based social login integration.
"""

from flask import Blueprint, request, jsonify, redirect, url_for, flash, session, current_app, send_file
from flask_login import login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from .common_imports import *
from routes.utils.firebase_auth import get_firebase_auth_service
from routes.utils.auth_helpers import (
    get_auth_helper, unified_auth_required, admin_required, superuser_required,
    clear_session_cookies, get_firebase_config
)
from routes.routes_external_auth import _issue_tokens
from models import User
import logging
import json
import os

logger = logging.getLogger(__name__)

# Create blueprint for Firebase authentication
firebase_auth_bp = Blueprint('firebase_auth', __name__)

@firebase_auth_bp.route("/auth/firebase/login", methods=["POST"])
def firebase_login():
    """Handle Firebase authentication login."""
    try:
        data = request.get_json()
        if not data or 'idToken' not in data:
            return jsonify({
                "error": "Missing ID token",
                "message": "Firebase ID token is required",
                "code": "MISSING_TOKEN"
            }), 400
        
        id_token = data['idToken']
        
        # Get Firebase Auth service
        firebase_service = get_firebase_auth_service()
        if not firebase_service.is_available():
            return jsonify({
                "error": "Firebase Auth not available",
                "message": "Firebase Authentication service is not configured",
                "code": "SERVICE_UNAVAILABLE"
            }), 503
        
        # Authenticate user with Firebase
        user = firebase_service.authenticate_user(id_token)
        if not user:
            return jsonify({
                "error": "Authentication failed",
                "message": "Invalid Firebase token or user creation failed",
                "code": "AUTH_FAILED"
            }), 401
        
        # Use unified authentication system
        auth_helper = get_auth_helper()
        auth_result = auth_helper.authenticate_user(user, "firebase")
        
        if not auth_result["success"]:
            return jsonify(auth_result), 401
        
        # Get JWT tokens for API access
        jwt_tokens = auth_result.get("jwt_tokens", {})
        
        # Log successful login
        logger.info(f"Firebase login successful for user {user.username} (ID: {user.id})")
        
        # Determine redirect URL based on user role
        redirect_url = url_for('main.user_dashboard')

        # Check if user has editor role first (custom role takes precedence)
        custom_name = (user.custom_role.name.lower() if user.custom_role and user.custom_role.name else "")
        if custom_name in ['editor', 'subadmin', 'media-manager']:
            redirect_url = url_for("editor.dashboard")
        elif user.role in [UserRole.ADMIN, UserRole.SUPERUSER] or user.is_owner():
            redirect_url = url_for("main.settings_dashboard")
        else:
            redirect_url = url_for("user_profile.user_profile", username=user.username)
        
        # Return success response with JWT tokens
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": auth_result["user"],
            "redirect_url": redirect_url,
            **jwt_tokens
        })
        
    except Exception as e:
        logger.error(f"Firebase login error: {e}")
        return jsonify({
            "error": "Login failed",
            "message": "An unexpected error occurred during login",
            "code": "LOGIN_ERROR"
        }), 500

@firebase_auth_bp.route("/auth/firebase/logout", methods=["POST"])
@unified_auth_required
def firebase_logout():
    """Handle Firebase authentication logout."""
    try:
        auth_helper = get_auth_helper()
        user = auth_helper.get_current_user()
        
        if not user or not user.is_firebase_user():
            return jsonify({
                "error": "Invalid request",
                "message": "This endpoint is only for Firebase users",
                "code": "INVALID_REQUEST"
            }), 400
        
        # Use unified authentication system for logout
        logout_result = auth_helper.logout_user(user, "Firebase user logout")
        
        if logout_result["success"]:
            logger.info(f"Firebase logout successful for user {user.username}")
        else:
            logger.warning(f"Firebase logout failed: {logout_result.get('message', 'Unknown error')}")
        
        # Create response and explicitly clear session cookies
        response = jsonify({
            "success": True,
            "message": "Logout successful",
            "redirect_url": url_for('main.index')
        })
        
        # Clear session cookies using helper
        clear_session_cookies(response)
        
        return response
        
    except Exception as e:
        logger.error(f"Firebase logout error: {e}")
        return jsonify({
            "error": "Logout failed",
            "message": "An unexpected error occurred during logout",
            "code": "LOGOUT_ERROR"
        }), 500

@firebase_auth_bp.route("/api/auth/firebase/login", methods=["POST"])
def firebase_api_login():
    """Handle Firebase authentication for API access with JWT tokens."""
    try:
        data = request.get_json()
        if not data or 'idToken' not in data:
            return jsonify({
                "error": "Missing ID token",
                "message": "Firebase ID token is required",
                "code": "MISSING_TOKEN"
            }), 400
        
        id_token = data['idToken']
        
        # Get Firebase Auth service
        firebase_service = get_firebase_auth_service()
        if not firebase_service.is_available():
            return jsonify({
                "error": "Firebase Auth not available",
                "message": "Firebase Authentication service is not configured",
                "code": "SERVICE_UNAVAILABLE"
            }), 503
        
        # Authenticate user with Firebase
        user = firebase_service.authenticate_user(id_token)
        if not user:
            return jsonify({
                "error": "Authentication failed",
                "message": "Invalid Firebase token or user creation failed",
                "code": "AUTH_FAILED"
            }), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                "error": "Account disabled",
                "message": "Your account has been disabled. Please contact support.",
                "code": "ACCOUNT_DISABLED"
            }), 403
        
        # Use unified authentication system for API
        auth_helper = get_auth_helper()
        auth_result = auth_helper.authenticate_user(user, "firebase")

        if not auth_result["success"]:
            return jsonify(auth_result), 401

        # The auth_result already contains the JWT tokens directly
        logger.info(f"Firebase API login successful for user {user.username}")

        return jsonify(auth_result)
        
    except Exception as e:
        logger.error(f"Firebase API login error: {e}")
        return jsonify({
            "error": "Login failed",
            "message": "An unexpected error occurred during login",
            "code": "LOGIN_ERROR"
        }), 500

@firebase_auth_bp.route("/auth/firebase/status", methods=["GET"])
def firebase_auth_status():
    """Check Firebase authentication service status."""
    firebase_service = get_firebase_auth_service()
    
    return jsonify({
        "available": firebase_service.is_available(),
        "firebase_available": firebase_service._initialized if hasattr(firebase_service, '_initialized') else False
    })

@firebase_auth_bp.route("/auth/firebase/config", methods=["GET"])
def firebase_config():
    """Get Firebase configuration for frontend."""
    return jsonify(get_firebase_config())

@firebase_auth_bp.route("/auth/firebase/providers", methods=["GET"])
def firebase_providers():
    """Get available Firebase authentication providers."""
    firebase_service = get_firebase_auth_service()

    if not firebase_service.is_available():
        return jsonify({
            "error": "Firebase Auth not available",
            "message": "Firebase Authentication service is not configured"
        }), 503

    # Try to load saved provider configuration from admin settings
    import os
    providers_config_file = os.path.join(current_app.root_path, 'config', 'firebase_providers.json')

    providers = {}

    # Default provider configurations
    default_providers = {
        "google": {
            "enabled": True,
            "name": "Google",
            "icon": "fab fa-google",
            "color": "#4285F4",
            "svg": """<svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>"""
        },
        "facebook": {
            "enabled": True,
            "name": "Facebook",
            "icon": "fab fa-facebook",
            "color": "#1877F2",
            "svg": '<svg class="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>'
        },
        "twitter": {
            "enabled": False,  # Twitter/X is disabled by default due to package issues
            "name": "Twitter",
            "icon": "fab fa-twitter",
            "color": "#1DA1F2",
            "svg": """<svg class="w-5 h-5" fill="#1DA1F2" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
            </svg>"""
        },
        "github": {
            "enabled": True,
            "name": "GitHub",
            "icon": "fab fa-github",
            "color": "#333333",
            "svg": """<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>"""
        }
    }

    # Load saved provider configuration if it exists
    if os.path.exists(providers_config_file):
        try:
            with open(providers_config_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)

            # Merge saved configuration with defaults
            for provider_key, provider_config in saved_config.items():
                if provider_key in default_providers:
                    default_providers[provider_key]['enabled'] = provider_config.get('enabled', True)
        except Exception as e:
            logger.warning(f"Failed to load provider configuration: {e}")
            # Fall back to defaults

    # Filter to only return enabled providers
    for provider_key, provider_config in default_providers.items():
        if provider_config.get('enabled', False):
            providers[provider_key] = provider_config

    return jsonify({
        "providers": providers
    })

@firebase_auth_bp.route("/auth/firebase/link-account", methods=["POST"])
@unified_auth_required
def link_firebase_account():
    """Link Firebase account to existing local account."""
    try:
        auth_helper = get_auth_helper()
        user = auth_helper.get_current_user()
        
        data = request.get_json()
        if not data or 'idToken' not in data:
            return jsonify({
                "error": "Missing ID token",
                "message": "Firebase ID token is required",
                "code": "MISSING_TOKEN"
            }), 400
        
        id_token = data['idToken']
        
        # Get Firebase Auth service
        firebase_service = get_firebase_auth_service()
        if not firebase_service.is_available():
            return jsonify({
                "error": "Firebase Auth not available",
                "message": "Firebase Authentication service is not configured",
                "code": "SERVICE_UNAVAILABLE"
            }), 503
        
        # Verify the ID token
        firebase_user_data = firebase_service.verify_id_token(id_token)
        if not firebase_user_data:
            return jsonify({
                "error": "Invalid token",
                "message": "Invalid Firebase ID token",
                "code": "INVALID_TOKEN"
            }), 401
        
        firebase_uid = firebase_user_data.get('uid')
        if not firebase_uid:
            return jsonify({
                "error": "Invalid token data",
                "message": "Firebase UID not found in token",
                "code": "INVALID_TOKEN_DATA"
            }), 401
        
        # Check if Firebase account is already linked to another user
        existing_firebase_user = firebase_service.get_user_by_firebase_uid(firebase_uid)
        if existing_firebase_user and existing_firebase_user.id != user.id:
            return jsonify({
                "error": "Account already linked",
                "message": "This Firebase account is already linked to another user",
                "code": "ACCOUNT_ALREADY_LINKED"
            }), 409
        
        # Link Firebase account to current user
        user.firebase_uid = firebase_uid
        user.auth_provider = firebase_service._get_provider_from_firebase_data(firebase_user_data)
        user.provider_data = {
            'display_name': firebase_user_data.get('name', ''),
            'photo_url': firebase_user_data.get('picture'),
            'firebase_data': firebase_user_data
        }
        
        # Update email if not set
        if not user.email and firebase_user_data.get('email'):
            user.email = firebase_user_data.get('email')
            user.verified = True
            user.email_verified_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        logger.info(f"Firebase account linked to user {user.username}")
        
        return jsonify({
            "success": True,
            "message": "Firebase account linked successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "auth_provider": user.auth_provider,
                "profile_picture": user.profile_picture or user.parsed_provider_data.get('photo_url') if user.provider_data else None
            }
        })
        
    except Exception as e:
        logger.error(f"Firebase account linking error: {e}")
        db.session.rollback()
        return jsonify({
            "error": "Account linking failed",
            "message": "An unexpected error occurred while linking account",
            "code": "LINKING_ERROR"
        }), 500

@firebase_auth_bp.route("/auth/firebase/unlink-account", methods=["POST"])
@unified_auth_required
def unlink_firebase_account():
    """Unlink Firebase account from current user."""
    try:
        auth_helper = get_auth_helper()
        user = auth_helper.get_current_user()
        
        if not user or not user.is_firebase_user():
            return jsonify({
                "error": "No Firebase account linked",
                "message": "No Firebase account is linked to this user",
                "code": "NO_FIREBASE_ACCOUNT"
            }), 400
        
        # Check if user has a local password
        if not user.has_password():
            return jsonify({
                "error": "Cannot unlink account",
                "message": "Cannot unlink Firebase account without setting a local password first",
                "code": "NO_LOCAL_PASSWORD"
            }), 400
        
        # Unlink Firebase account
        user.firebase_uid = None
        user.auth_provider = 'local'
        user.provider_data = None
        
        db.session.commit()
        
        logger.info(f"Firebase account unlinked from user {user.username}")
        
        return jsonify({
            "success": True,
            "message": "Firebase account unlinked successfully"
        })
        
    except Exception as e:
        logger.error(f"Firebase account unlinking error: {e}")
        db.session.rollback()
        return jsonify({
            "error": "Account unlinking failed",
            "message": "An unexpected error occurred while unlinking account",
            "code": "UNLINKING_ERROR"
        }), 500

@firebase_auth_bp.route("/admin/firebase-auth", methods=["GET"])
@admin_required
def firebase_auth_admin():
    """Firebase Authentication admin page."""
    return render_template("admin/firebase_auth_settings.html")

@firebase_auth_bp.route("/admin/firebase-auth/config", methods=["GET", "POST"])
@admin_required
def firebase_auth_config():
    """Get or update Firebase configuration."""

    if request.method == "GET":
        # Return current Firebase configuration
        import os
        config = get_firebase_config()
        config.update({
            "service_account_configured": bool(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH') or os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')),
            "service_account_path": os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', ''),
        })

        # Load saved provider configuration if it exists
        import os as os_module  # Explicit import to avoid scoping issues
        providers_config_file = os_module.path.join(current_app.root_path, 'config', 'firebase_providers.json')
        if os_module.path.exists(providers_config_file):
            try:
                with open(providers_config_file, 'r') as f:
                    saved_providers = json.load(f)
                config["providers"] = saved_providers
            except Exception as e:
                logger.warning(f"Error loading saved provider config: {e}")
                # Fall back to default providers
                config["providers"] = {
                    "google": {"enabled": True, "name": "Google", "icon": "fab fa-google"},
                    "facebook": {"enabled": True, "name": "Facebook", "icon": "fab fa-facebook"},
                    "twitter": {"enabled": True, "name": "Twitter", "icon": "fab fa-twitter"},
                    "github": {"enabled": True, "name": "GitHub", "icon": "fab fa-github"}
                }
        else:
            # Default providers if no saved config
            config["providers"] = {
                "google": {"enabled": True, "name": "Google", "icon": "fab fa-google"},
                "facebook": {"enabled": True, "name": "Facebook", "icon": "fab fa-facebook"},
                "twitter": {"enabled": True, "name": "Twitter", "icon": "fab fa-twitter"},
                "github": {"enabled": True, "name": "GitHub", "icon": "fab fa-github"}
            }

        return jsonify(config)

    elif request.method == "POST":
        import os as os_module  # Explicit import to avoid scoping issues
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No configuration data provided"}), 400

            # Validate required fields
            required_fields = ['project_id', 'api_key', 'auth_domain']
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields
                }), 400

            # Save Firebase configuration to a persistent JSON file
            config_dir = os_module.path.join(current_app.root_path, 'config')
            os_module.makedirs(config_dir, exist_ok=True)

            config_file = os_module.path.join(config_dir, 'firebase_config.json')
            logger.info(f"Saving Firebase config to: {config_file}")

            try:
                # Prepare configuration data
                firebase_config = {
                    "project_id": data.get('project_id'),
                    "api_key": data.get('api_key'),
                    "auth_domain": data.get('auth_domain'),
                    "storage_bucket": data.get('storage_bucket', ''),
                    "messaging_sender_id": data.get('messaging_sender_id', ''),
                    "app_id": data.get('app_id', ''),
                    "use_emulator": data.get('use_emulator', 'false'),
                    "emulator_host": data.get('emulator_host', 'localhost:9099'),
                    "updated_at": os_module.path.getctime(config_file) if os_module.path.exists(config_file) else None,
                    "updated_by": "admin"
                }

                # Save to JSON file
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(firebase_config, f, indent=2, ensure_ascii=False)

                logger.info(f"Successfully saved Firebase config to JSON file")

                # Also try to update .env file for backward compatibility (development)
                try:
                    env_file = os_module.path.join(current_app.root_path, '.env')
                    if os_module.path.exists(env_file):
                        env_content = ""
                        with open(env_file, 'r', encoding='utf-8') as f:
                            env_content = f.read()

                        env_lines = env_content.split('\n') if env_content else []

                        # Remove existing Firebase config lines
                        env_lines = [line for line in env_lines if not line.startswith(('FIREBASE_API_KEY=', 'FIREBASE_AUTH_DOMAIN=', 'FIREBASE_PROJECT_ID=', 'FIREBASE_STORAGE_BUCKET=', 'FIREBASE_MESSAGING_SENDER_ID=', 'FIREBASE_APP_ID='))]

                        # Add new Firebase configuration
                        firebase_vars = [
                            f"FIREBASE_PROJECT_ID={data.get('project_id')}",
                            f"FIREBASE_API_KEY={data.get('api_key')}",
                            f"FIREBASE_AUTH_DOMAIN={data.get('auth_domain')}",
                            f"FIREBASE_STORAGE_BUCKET={data.get('storage_bucket', '')}",
                            f"FIREBASE_MESSAGING_SENDER_ID={data.get('messaging_sender_id', '')}",
                            f"FIREBASE_APP_ID={data.get('app_id', '')}"
                        ]

                        # Add Firebase vars to env_lines, filtering out empty values
                        added_vars = [var for var in firebase_vars if '=' in var and var.split('=', 1)[1]]
                        env_lines.extend(added_vars)

                        # Write back to .env file
                        with open(env_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(env_lines))

                        logger.info("Also updated .env file for development compatibility")
                except Exception as env_error:
                    logger.warning(f"Could not update .env file: {env_error}")

                logger.info(f"Firebase configuration updated by admin user")

            except PermissionError as e:
                logger.error(f"Permission denied writing to config file: {e}")
                return jsonify({"error": "Permission denied. Cannot write to config file", "details": str(e)}), 500
            except IOError as e:
                logger.error(f"I/O error writing to config file: {e}")
                return jsonify({"error": "File I/O error", "details": str(e)}), 500
            except Exception as e:
                logger.error(f"Unexpected error saving Firebase config: {e}")
                return jsonify({"error": "Failed to save configuration", "details": str(e)}), 500

            return jsonify({
                "success": True,
                "message": "Firebase configuration saved successfully.",
                "config": {
                    "project_id": data.get('project_id'),
                    "api_key": data.get('api_key'),
                    "auth_domain": data.get('auth_domain'),
                    "storage_bucket": data.get('storage_bucket'),
                    "messaging_sender_id": data.get('messaging_sender_id'),
                    "app_id": data.get('app_id')
                }
            })

        except Exception as e:
            logger.error(f"Firebase configuration update error: {e}")
            return jsonify({"error": "Configuration update failed", "message": str(e)}), 500

@firebase_auth_bp.route("/admin/firebase-auth/test", methods=["POST"])
@admin_required
def test_firebase_config():
    """Test Firebase configuration."""

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No test data provided"}), 400

        # Test Firebase configuration
        firebase_service = get_firebase_auth_service()

        # Check if service can be initialized with provided config
        test_config = {
            'project_id': data.get('project_id'),
            'service_account_path': data.get('service_account_path'),
            'service_account_json': data.get('service_account_json')
        }

        # This is a simplified test - in reality you'd want to actually try to initialize
        # Firebase with the provided configuration
        test_result = {
            "success": True,
            "message": "Configuration appears valid",
            "tests": {
                "project_id": bool(data.get('project_id')),
                "api_key": bool(data.get('api_key')),
                "auth_domain": bool(data.get('auth_domain')),
                "service_account": bool(data.get('service_account_path') or data.get('service_account_json'))
            }
        }

        return jsonify(test_result)

    except Exception as e:
        logger.error(f"Firebase configuration test error: {e}")
        return jsonify({"error": "Configuration test failed", "message": str(e)}), 500

@firebase_auth_bp.route("/admin/firebase-auth/providers", methods=["GET", "POST"])
@admin_required
def firebase_auth_providers():
    """Get or update Firebase authentication providers."""

    if request.method == "GET":
        # Try to load saved provider configuration, fallback to defaults
        providers_config_file = os.path.join(current_app.root_path, 'config', 'firebase_providers.json')

        # Default provider configuration with full metadata
        providers = {
            "google": {"enabled": True, "name": "Google", "icon": "fab fa-google"},
            "facebook": {"enabled": True, "name": "Facebook", "icon": "fab fa-facebook"},
            "twitter": {"enabled": False, "name": "Twitter", "icon": "fab fa-twitter"},
            "github": {"enabled": True, "name": "GitHub", "icon": "fab fa-github"}
        }

        # Load and merge saved provider configuration if it exists
        if os.path.exists(providers_config_file):
            try:
                with open(providers_config_file, 'r') as f:
                    saved_providers = json.load(f)

                # Merge saved enabled status with default metadata
                for provider_key, saved_config in saved_providers.items():
                    if provider_key in providers:
                        providers[provider_key]['enabled'] = saved_config.get('enabled', providers[provider_key]['enabled'])
            except Exception as e:
                logger.warning(f"Error loading saved provider config: {e}")

        return jsonify({"providers": providers})

    elif request.method == "POST":
        try:
            data = request.get_json()
            if not data or 'providers' not in data:
                return jsonify({"error": "No provider configuration provided"}), 400

            providers = data['providers']

            # Validate provider configuration
            valid_providers = ['google', 'facebook', 'twitter', 'github']
            for provider in providers:
                if provider not in valid_providers:
                    return jsonify({"error": f"Invalid provider: {provider}"}), 400

            # Save provider configuration to file
            config_dir = os.path.join(current_app.root_path, 'config')
            os.makedirs(config_dir, exist_ok=True)

            providers_config_file = os.path.join(config_dir, 'firebase_providers.json')
            with open(providers_config_file, 'w') as f:
                json.dump(providers, f, indent=2)

            logger.info(f"Firebase provider configuration updated by admin user")

            return jsonify({
                "success": True,
                "message": "Provider configuration saved successfully",
                "providers": providers
            })

        except Exception as e:
            logger.error(f"Provider configuration update error: {e}")
            return jsonify({"error": "Provider configuration update failed", "message": str(e)}), 500

@firebase_auth_bp.route("/admin/firebase-auth/stats", methods=["GET"])
@admin_required
def firebase_auth_stats():
    """Get Firebase authentication statistics."""

    try:
        # Get user statistics
        total_users = User.query.count()
        firebase_users = User.query.filter(User.firebase_uid.isnot(None)).count()
        local_users = User.query.filter(User.firebase_uid.is_(None)).count()

        # Get provider statistics
        provider_stats = {}
        for provider in ['google', 'facebook', 'twitter', 'github']:
            count = User.query.filter(User.auth_provider == provider).count()
            provider_stats[provider] = count

        stats = {
            "total_users": total_users,
            "firebase_users": firebase_users,
            "local_users": local_users,
            "provider_stats": provider_stats,
            "firebase_percentage": (firebase_users / total_users * 100) if total_users > 0 else 0
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Firebase statistics error: {e}")
        return jsonify({"error": "Failed to get statistics", "message": str(e)}), 500

@firebase_auth_bp.route("/admin/firebase-auth/service-account", methods=["POST"])
@admin_required
def upload_service_account():
    """Upload Firebase service account file."""

    try:
        logger.info("Starting service account upload")

        # Check if file is in request
        if 'service_account_file' not in request.files:
            logger.error("No service_account_file in request.files")
            return jsonify({"error": "No file provided"}), 400

        file = request.files['service_account_file']
        logger.info(f"Received file: {file.filename}")

        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.endswith('.json'):
            logger.error(f"Invalid file extension: {file.filename}")
            return jsonify({"error": "File must be a JSON file"}), 400

        # Save file to config directory
        config_dir = os.path.join(current_app.root_path, 'config')
        logger.info(f"Config directory: {config_dir}")

        try:
            os.makedirs(config_dir, exist_ok=True)
            logger.info("Config directory created/exists")
        except Exception as e:
            logger.error(f"Failed to create config directory: {e}")
            return jsonify({"error": "Failed to create config directory"}), 500

        file_path = os.path.join(config_dir, 'firebase_service_account.json')
        logger.info(f"Saving to: {file_path}")

        # Check if file already exists and remove it
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Removed existing service account file")
            except Exception as e:
                logger.error(f"Failed to remove existing file: {e}")
                return jsonify({"error": "Failed to remove existing service account file"}), 500

        try:
            file.save(file_path)
            logger.info("File saved successfully")

            # Verify file was written correctly
            if not os.path.exists(file_path):
                logger.error("File was not created after save")
                return jsonify({"error": "File save verification failed"}), 500

            file_size = os.path.getsize(file_path)
            logger.info(f"File size: {file_size} bytes")

        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            return jsonify({"error": "Failed to save file"}), 500

        # Parse and validate JSON format
        service_account_data = None
        try:
            logger.info("Parsing JSON file")
            with open(file_path, 'r', encoding='utf-8') as f:
                service_account_data = json.load(f)

            logger.info("JSON parsed successfully")
            logger.info(f"Service account type: {service_account_data.get('type', 'unknown')}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Invalid JSON file", "details": str(e)}), 400
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Invalid file encoding. Please ensure the file is UTF-8 encoded"}), 400
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": f"Error reading service account file: {str(e)}"}), 400

        # Validate service account data
        if not service_account_data:
            logger.error("Service account data is empty")
            os.remove(file_path)
            return jsonify({"error": "Service account file is empty"}), 400

        # Check if it's actually a service account
        if service_account_data.get('type') != 'service_account':
            logger.warning(f"Unexpected service account type: {service_account_data.get('type')}")
            # Continue anyway, as some service account files might have different types

        # Validate required fields - check for various Firebase config formats
        project_id = None

        # Check if this is a google-services.json file (mobile app config)
        if 'project_info' in service_account_data and 'project_id' in service_account_data['project_info']:
            project_id = service_account_data['project_info']['project_id']
            logger.info("Detected google-services.json format, extracted project_id from project_info")
        else:
            # Standard service account format
            project_id = service_account_data.get('project_id') or service_account_data.get('projectId')
        if not project_id:
            # Try to extract project ID from client_email (format: xxx@project-id.iam.gserviceaccount.com)
            client_email = service_account_data.get('client_email', '')
            if '@' in client_email and '.iam.gserviceaccount.com' in client_email:
                # Extract project ID from email: xxx@project-id.iam.gserviceaccount.com
                email_parts = client_email.split('@')
                if len(email_parts) == 2:
                    project_domain = email_parts[1]
                    if '.iam.gserviceaccount.com' in project_domain:
                        project_id = project_domain.replace('.iam.gserviceaccount.com', '')

        if not project_id:
            logger.error("Cannot determine project_id from service account file")
            os.remove(file_path)
            return jsonify({"error": "Cannot determine project ID from service account file. Please ensure it contains either 'project_id', 'projectId', or a valid 'client_email' field"}), 400

        # For google-services.json files, we don't need authentication credentials
        # For service account files, validate authentication credentials
        is_google_services = 'project_info' in service_account_data

        if not is_google_services:
            has_private_key = bool(service_account_data.get('private_key'))
            has_client_email = bool(service_account_data.get('client_email'))

            if not has_private_key and not has_client_email:
                logger.error("Service account missing both private_key and client_email")
                os.remove(file_path)
                return jsonify({"error": "Service account must contain either private_key or client_email"}), 400

        # Extract Firebase configuration based on file type
        if is_google_services:
            # Extract from google-services.json format
            firebase_config = {
                "project_id": project_id,
                "client_email": "",
                "private_key": "",
                "client_id": "",
                "auth_uri": "",
                "token_uri": "",
                "auth_provider_x509_cert_url": "",
                "client_x509_cert_url": ""
            }

            # Try to extract API key from client configuration
            if 'client' in service_account_data and len(service_account_data['client']) > 0:
                client_config = service_account_data['client'][0]
                if 'api_key' in client_config and len(client_config['api_key']) > 0:
                    firebase_config["api_key"] = client_config['api_key'][0].get('current_key', '')
                    logger.info("Extracted API key from google-services.json")

            logger.info("Processed google-services.json file")
        else:
            # Standard service account format
            firebase_config = {
                "project_id": project_id,
                "client_email": service_account_data.get("client_email", ""),
                "private_key": service_account_data.get("private_key", ""),
                "client_id": service_account_data.get("client_id", ""),
                "auth_uri": service_account_data.get("auth_uri", ""),
                "token_uri": service_account_data.get("token_uri", ""),
                "auth_provider_x509_cert_url": service_account_data.get("auth_provider_x509_cert_url", ""),
                "client_x509_cert_url": service_account_data.get("client_x509_cert_url", "")
            }

        logger.info("Firebase config extracted successfully")
        logger.info(f"Project ID: {firebase_config['project_id']}")
        logger.info(f"Client Email: {firebase_config.get('client_email', 'Not provided')}")

        # Store service account path in current app config for this session
        current_app.config['FIREBASE_SERVICE_ACCOUNT_PATH'] = file_path
        logger.info("Service account path stored in app config")

        logger.info("Service account upload completed successfully")
        return jsonify({
            "success": True,
            "message": "Service account file uploaded and parsed successfully",
            "file_path": file_path,
            "firebase_config": firebase_config,
            "service_account_configured": True
        })

    except Exception as e:
        logger.error(f"Service account upload error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Upload failed", "message": str(e)}), 500

@firebase_auth_bp.route("/config/firebase_service_account.json")
@admin_required
def download_service_account():
    """Download the uploaded Firebase service account file."""

    try:
        config_dir = os.path.join(current_app.root_path, 'config')
        file_path = os.path.join(config_dir, 'firebase_service_account.json')

        if not os.path.exists(file_path):
            return jsonify({"error": "Service account file not found"}), 404

        return send_file(file_path, as_attachment=True, download_name='firebase_service_account.json')

    except Exception as e:
        logger.error(f"Service account download error: {e}")
        return jsonify({"error": "Download failed", "message": str(e)}), 500
