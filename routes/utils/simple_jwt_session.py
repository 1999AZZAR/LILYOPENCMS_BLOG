"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Simplified JWT Session Management for LilyOpenCMS

This module provides a simple JWT-based session management system that replaces
the overly complex SessionSecurityManager. Uses only PyJWT and minimal database
operations for reliability and simplicity.
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
import jwt
from flask import request, current_app
from models import User, db, UserActivity

logger = logging.getLogger(__name__)

# JWT Configuration - Simple and consistent
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'lily-simple-secret-2025')
JWT_ALGORITHM = "HS256"

# Token TTL configuration - Simplified for reliability
ACCESS_TOKEN_TTL = 3600  # 1 hour
REFRESH_TOKEN_TTL = 86400 * 30  # 30 days

class SimpleJWTManager:
    """Simple JWT-based session manager."""

    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM

    def create_access_token(self, user: User) -> str:
        """Create a simple access token for the user."""
        try:
            now = datetime.now(timezone.utc)
            payload = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'iat': now,
                'exp': now + timedelta(seconds=ACCESS_TOKEN_TTL),
                'iss': 'lilyopencms',
                'type': 'access'
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user {user.username}")
            return token

        except Exception as e:
            logger.error(f"Failed to create access token for user {user.username}: {e}")
            return None

    def create_refresh_token(self, user: User) -> str:
        """Create a simple refresh token for the user."""
        try:
            now = datetime.now(timezone.utc)
            payload = {
                'user_id': user.id,
                'username': user.username,
                'iat': now,
                'exp': now + timedelta(seconds=REFRESH_TOKEN_TTL),
                'iss': 'lilyopencms',
                'type': 'refresh'
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created refresh token for user {user.username}")
            return token

        except Exception as e:
            logger.error(f"Failed to create refresh token for user {user.username}: {e}")
            return None

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and return payload if valid."""
        try:
            if not token:
                return None

            # Remove Bearer prefix if present
            if token.startswith('Bearer '):
                token = token.split(' ', 1)[1]

            # Try to decode with the expected algorithm first
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            except jwt.InvalidAlgorithmError:
                # If the algorithm is not allowed, try with more permissive algorithms
                # This handles cases where tokens were created with different algorithms
                logger.warning("Token uses non-standard algorithm, attempting fallback decoding")
                try:
                    # Try with common algorithms
                    for alg in ['HS256', 'HS384', 'HS512', 'RS256']:
                        try:
                            payload = jwt.decode(token, self.secret_key, algorithms=[alg])
                            logger.info(f"Successfully decoded token with algorithm {alg}")
                            break
                        except:
                            continue
                    else:
                        # If none work, try without algorithm verification (less secure but more permissive)
                        payload = jwt.decode(token, self.secret_key, options={"verify_signature": True, "verify_exp": True}, algorithms=['HS256', 'HS384', 'HS512', 'RS256'])
                        logger.warning("Decoded token without strict algorithm verification")
                except Exception as fallback_error:
                    logger.error(f"Token algorithm fallback failed: {fallback_error}")
                    raise jwt.InvalidTokenError("Unsupported algorithm")

            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.now(timezone.utc) > datetime.fromtimestamp(exp, timezone.utc):
                logger.warning(f"Token expired for user {payload.get('username', 'unknown')}")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT token."""
        try:
            payload = self.validate_token(token)
            if not payload:
                return None

            user_id = payload.get('user_id')
            if not user_id:
                return None

            user = db.session.get(User, user_id)

            # Check if user is still active
            if user and user.is_active and not user.is_suspended:
                return user

            return None

        except Exception as e:
            logger.error(f"Failed to get user from token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        try:
            payload = self.validate_token(refresh_token)
            if not payload or payload.get('type') != 'refresh':
                return None

            user_id = payload.get('user_id')
            if not user_id:
                return None

            user = db.session.get(User, user_id)
            if not user or not user.is_active or user.is_suspended:
                return None

            # Create new access token
            return self.create_access_token(user)

        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            return None

    def record_user_activity(self, user_id: int, activity_type: str, description: str = None):
        """Record user activity for audit trail (optional)."""
        try:
            # Only record important activities to avoid database spam
            if activity_type in ['login', 'logout', 'password_change']:
                activity = UserActivity(
                    user_id=user_id,
                    activity_type=activity_type,
                    description=description,
                    ip_address=request.remote_addr if request else 'unknown',
                    user_agent=request.headers.get('User-Agent') if request else 'unknown',
                    created_at=datetime.now(timezone.utc)
                )

                db.session.add(activity)
                db.session.commit()

        except Exception as e:
            logger.error(f"Failed to record user activity for user {user_id}: {e}")
            # Don't raise exception - this is not critical

    def get_user_activity_summary(self, user_id: int) -> Dict[str, Any]:
        """Get user activity summary (optional)."""
        try:
            recent_activities = UserActivity.query.filter_by(user_id=user_id)\
                .order_by(UserActivity.created_at.desc())\
                .limit(10)\
                .all()

            return {
                'total_activities': UserActivity.query.filter_by(user_id=user_id).count(),
                'recent_activities': [
                    {
                        'type': activity.activity_type,
                        'description': activity.description,
                        'created_at': activity.created_at.isoformat(),
                        'ip_address': activity.ip_address
                    } for activity in recent_activities
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get user activity summary for user {user_id}: {e}")
            return {'total_activities': 0, 'recent_activities': []}


# Global instance
simple_jwt_manager = SimpleJWTManager()

def get_simple_jwt_manager():
    """Get the simple JWT manager instance."""
    return simple_jwt_manager

def init_simple_jwt_manager():
    """Initialize the simple JWT manager (no complex setup needed)."""
    logger.info("✅ Simple JWT session manager initialized")
    return simple_jwt_manager
