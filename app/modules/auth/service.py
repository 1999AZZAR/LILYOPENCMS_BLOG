"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Auth service layer — business logic extracted from route handlers.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from models import db, User, UserRole, Permission, CustomRole, UserActivity

logger = logging.getLogger(__name__)


class AuthService:
    """Centralized auth business logic."""

    @staticmethod
    def create_user(username: str, password: str, email: str = None,
                    first_name: str = None, last_name: str = None) -> Tuple[Optional[User], Optional[str]]:
        """Create a new user. Returns (user, error_message)."""
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        if email and User.query.filter_by(email=email).first():
            return None, "Email already registered"

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.GENERAL,
        )
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            return user, None
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to create user: {e}")
            return None, "Database error"

    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """Authenticate user by username/email + password. Returns (user, error)."""
        user = User.query.filter_by(username=username).first()
        if not user and '@' in username:
            user = User.query.filter_by(email=username).first()

        if not user or not user.check_password(password):
            return None, "Invalid credentials"
        if not user.is_active:
            return None, "Account is inactive"
        if user.is_suspended:
            return None, "Account is suspended"
        return user, None

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password. Returns (success, message)."""
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        user.set_password(new_password)
        try:
            db.session.commit()
            return True, "Password changed successfully"
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Password change failed: {e}")
            return False, "Database error"

    @staticmethod
    def update_profile(user: User, **kwargs) -> Tuple[bool, str]:
        """Update user profile fields. Returns (success, message)."""
        allowed_fields = {"email", "first_name", "last_name", "bio", "profile_picture"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        try:
            db.session.commit()
            return True, "Profile updated"
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Profile update failed: {e}")
            return False, "Database error"

    @staticmethod
    def suspend_user(user: User, reason: str = None, until: datetime = None) -> bool:
        """Suspend a user."""
        user.is_suspended = True
        user.suspension_reason = reason
        user.suspension_until = until
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def unsuspend_user(user: User) -> bool:
        """Remove suspension from a user."""
        user.is_suspended = False
        user.suspension_reason = None
        user.suspension_until = None
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def get_user_stats(user: User) -> Dict[str, Any]:
        """Get user dashboard stats."""
        from models import News, Image, YouTubeVideo
        return {
            "news_count": News.query.filter_by(user_id=user.id).count(),
            "image_count": Image.query.filter_by(user_id=user.id).count(),
            "video_count": YouTubeVideo.query.filter_by(user_id=user.id).count(),
        }

    @staticmethod
    def record_activity(user_id: int, activity_type: str, description: str = None,
                        ip_address: str = None, user_agent: str = None) -> bool:
        """Record user activity."""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(activity)
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False


auth_service = AuthService()
