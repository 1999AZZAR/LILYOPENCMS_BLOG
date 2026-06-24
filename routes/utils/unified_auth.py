"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Unified Authentication System for LilyOpenCMS

This module provides a unified authentication system that integrates
all authentication methods (local, Firebase, JWT) with the sophisticated
session management system.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from flask import request, current_app, session, g, jsonify
from flask_login import login_user, logout_user, current_user

from models import User, UserRole, db
from routes.utils.simple_jwt_session import get_simple_jwt_manager, ACCESS_TOKEN_TTL

logger = logging.getLogger(__name__)

class UnifiedAuthManager:
    """Unified authentication manager that handles all auth methods consistently."""

    def __init__(self):
        self.jwt_manager = get_simple_jwt_manager()

    def _refresh_jwt_manager(self):
        """Refresh the JWT manager reference."""
        self.jwt_manager = get_simple_jwt_manager()
    
    def authenticate_user(self, user: User, auth_method: str = "local", 
                        request_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Authenticate a user and create both session and JWT tokens.
        
        Args:
            user: The user to authenticate
            auth_method: The authentication method used ("local", "firebase", "api")
            request_data: Additional request data for logging
            
        Returns:
            Dictionary containing authentication result
        """
        try:
            # Validate user
            if not user.is_active:
                return {
                    "success": False,
                    "error": "Account inactive",
                    "message": "Your account is pending approval or has been deactivated",
                    "code": "AUTH_ACCOUNT_INACTIVE"
                }
            
            if user.is_suspended:
                suspension_message = "Your account is suspended"
                if user.suspension_reason:
                    suspension_message += f": {user.suspension_reason}"
                if user.suspension_until:
                    suspension_message += f" until {user.suspension_until.strftime('%Y-%m-%d %H:%M')}"
                
                return {
                    "success": False,
                    "error": "Account suspended",
                    "message": suspension_message,
                    "code": "AUTH_ACCOUNT_SUSPENDED"
                }
            
            # Update user login information
            user.last_login = datetime.now(timezone.utc)
            user.login_count += 1
            db.session.commit()
            
            # Create JWT tokens using simple JWT manager
            if not self.jwt_manager:
                logger.warning("JWT manager not initialized, attempting to refresh")
                self._refresh_jwt_manager()

                if not self.jwt_manager:
                    logger.error("JWT manager still not available after refresh")
                    return {
                        "success": False,
                        "error": "Authentication system error",
                        "message": "JWT management system not available",
                        "code": "AUTH_SYSTEM_ERROR"
                    }

            # Create access and refresh tokens
            access_token = self.jwt_manager.create_access_token(user)
            refresh_token = self.jwt_manager.create_refresh_token(user)

            if not access_token or not refresh_token:
                user_info = getattr(user, 'username', 'unknown') if user else 'unknown'
                logger.error(f"Failed to create JWT tokens for user {user_info}")
                return {
                    "success": False,
                    "error": "Token creation failed",
                    "message": "Failed to create user tokens",
                    "code": "AUTH_TOKEN_FAILED"
                }

            # Record login activity
            if self.jwt_manager:
                self.jwt_manager.record_user_activity(
                    user.id,
                    f"{auth_method}_login",
                    f"Successful {auth_method} login from {request.remote_addr}"
                )
            
            # Award daily login rewards (both coins and points)
            try:
                # Award coins
                from routes.utils.coin_earning_service import CoinEarningService
                coin_result = CoinEarningService.award_daily_login_coins(user.id)
                if coin_result['success']:
                    logger.info(f"User {user.id} earned {coin_result['coins_awarded']} coins for daily login")
                
                # Award points
                from routes.utils.points_service import PointsService
                points_result = PointsService.award_daily_login_points(user.id)
                if points_result['success']:
                    logger.info(f"User {user.id} earned {points_result['points_awarded']} points for daily login")
                    
            except Exception as reward_error:
                logger.error(f"Failed to award daily login rewards for user {user.id}: {reward_error}")
            
            # Login user with Flask-Login for web sessions (still needed for web interface)
            login_user(user, remember=True)

            user_info = getattr(user, 'username', 'unknown') if user else 'unknown'
            logger.info(f"Unified authentication successful for user {user_info} via {auth_method}")

            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "is_premium": user.is_premium,
                    "auth_provider": user.auth_provider,
                    "profile_picture": user.profile_picture or user.parsed_provider_data.get('photo_url') if user.provider_data else None
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_TTL,
                "auth_method": auth_method
            }
            
        except Exception as e:
            user_info = getattr(user, 'username', 'unknown') if user else 'unknown'
            logger.error(f"Unified authentication failed for user {user_info}: {e}")
            return {
                "success": False,
                "error": "Authentication failed",
                "message": "An unexpected error occurred during authentication",
                "code": "AUTH_ERROR"
            }
    
    
    def logout_user(self, user: User, reason: str = "User logout") -> Dict[str, Any]:
        """
        Logout a user and invalidate their session.
        
        Args:
            user: The user to logout
            reason: Reason for logout
            
        Returns:
            Dictionary containing logout result
        """
        try:
            # Check if user is authenticated (not anonymous)
            if not user or not hasattr(user, 'id') or not user.is_authenticated:
                logger.warning(f"Attempted logout for anonymous or invalid user")
                # Still clear session and logout from Flask-Login
                logout_user()
                session.clear()
                return {
                    "success": True,
                    "message": "Logout successful (anonymous user)"
                }
            
            # Record logout activity (simplified - no complex session invalidation)
            if self.jwt_manager:
                self.jwt_manager.record_user_activity(
                    user.id,
                    "logout",
                    f"User logout: {reason}"
                )
            
            # Logout from Flask-Login
            logout_user()
            
            # Clear session data
            session.clear()
            
            user_info = getattr(user, 'username', 'unknown') if user else 'unknown'
            invalidated_count = 1
            logger.info(f"Unified logout successful for user {user_info}, invalidated {invalidated_count} sessions")
            
            return {
                "success": True,
                "message": "Logout successful"
            }
            
        except Exception as e:
            # Handle the case where user might be anonymous
            user_info = getattr(user, 'username', 'anonymous') if user else 'anonymous'
            logger.error(f"Unified logout failed for user {user_info}: {e}")
            
            # Still try to clear session and logout from Flask-Login
            try:
                logout_user()
                session.clear()
            except:
                pass
            
            return {
                "success": False,
                "error": "Logout failed",
                "message": "An unexpected error occurred during logout",
                "code": "LOGOUT_ERROR"
            }
    
    def validate_authentication(self, user: Optional[User] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate current authentication state.

        Args:
            user: Optional user to validate (if None, uses current_user)

        Returns:
            Tuple of (is_valid, error_dict)
        """
        try:
            # Use provided user or current user
            if user is None:
                user = current_user if current_user.is_authenticated else None

            if not user:
                return False, {
                    "error": "Not authenticated",
                    "message": "No user is currently authenticated",
                    "code": "AUTH_NOT_AUTHENTICATED"
                }

            # Check if user is active
            if not user.is_active:
                return False, {
                    "error": "Account inactive",
                    "message": "Your account is pending approval or has been deactivated",
                    "code": "AUTH_ACCOUNT_INACTIVE"
                }

            # Check if user is suspended
            if user.is_suspended:
                return False, {
                    "error": "Account suspended",
                    "message": "Your account has been suspended",
                    "code": "AUTH_ACCOUNT_SUSPENDED"
                }

            # If no user was provided (using current_user), also validate session
            # JWT validation is handled separately in the API endpoints
            if user is None and not current_user.is_authenticated:
                return False, {
                    "error": "Session invalid",
                    "message": "Your session has expired or is invalid",
                    "code": "AUTH_SESSION_INVALID"
                }

            return True, None

        except Exception as e:
            logger.error(f"Authentication validation failed: {e}")
            return False, {
                "error": "Validation failed",
                "message": "An error occurred while validating authentication",
                "code": "AUTH_VALIDATION_ERROR"
            }
    
    def get_user_from_jwt(self, token: str) -> Optional[User]:
        """Get user from JWT token."""
        try:
            return self.jwt_manager.get_user_from_token(token)
        except Exception as e:
            logger.error(f"Failed to get user from JWT token: {e}")
            return None
    
    def get_user_from_session(self) -> Optional[User]:
        """Get user from current session."""
        try:
            if current_user.is_authenticated:
                return current_user
            
            # Try to get user from session data directly
            from flask import session
            user_id = session.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user and user.is_active:
                    # Manually set the current user for this request
                    from flask_login import login_user
                    login_user(user, remember=True)
                    return user
            
            return None
        except Exception as e:
            logger.error(f"Failed to get user from session: {e}")
            return None

# Global instance
unified_auth_manager = UnifiedAuthManager()

def get_unified_auth_manager():
    """Get the unified authentication manager instance."""
    return unified_auth_manager

def unified_auth_required(f):
    """Decorator that requires unified authentication (session or JWT)."""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_manager = get_unified_auth_manager()
        
        # Try JWT authentication first
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                user = auth_manager.get_user_from_jwt(token)
                if user:
                    is_valid, error = auth_manager.validate_authentication(user)
                    if is_valid:
                        g.api_user = user
                        from flask_login import login_user
                        login_user(user, remember=False)  # Don't remember for JWT sessions
                        return f(*args, **kwargs)
                    else:
                        return jsonify(error), 401
        
        # Fall back to session authentication
        user = auth_manager.get_user_from_session()
        if user:
            is_valid, error = auth_manager.validate_authentication(user)
            if is_valid:
                g.api_user = user
                return f(*args, **kwargs)
            else:
                # Logout invalid session
                from flask_login import logout_user
                logout_user()
                return current_app.jsonify(error), 401
        
        # No valid authentication found
        return jsonify({
            "error": "Authentication required",
            "message": "Please provide valid authentication (JWT token or session)",
            "code": "AUTH_REQUIRED"
        }), 401
    
    return decorated
