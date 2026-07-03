"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from enum import Enum
import os
from flask import url_for, request
import json
import re
import unicodedata

from app.extensions import db


# Helper function for timezone-aware default timestamp
def default_utcnow():
    return datetime.now(timezone.utc)


def slugify(text):
    """Generate URL-friendly slug from text."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


# Enums for consistent role and category values
class UserRole(Enum):
    SUPERUSER = "su"
    ADMIN = "admin"
    GENERAL = "general"


# Custom Role and Permission System
class Permission(db.Model):
    __tablename__ = "permission"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    resource = db.Column(db.String(100), nullable=False)  # e.g., 'news', 'users', 'images'
    action = db.Column(db.String(50), nullable=False)     # e.g., 'create', 'read', 'update', 'delete'
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    
    # Many-to-many relationship with roles
    roles = db.relationship(
        "CustomRole",
        secondary="role_permission",
        back_populates="permissions",
        lazy="select",
    )
    
    def __repr__(self):
        return f"<Permission {self.name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resource": self.resource,
            "action": self.action,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CustomRole(db.Model):
    __tablename__ = "custom_role"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)
    
    # Many-to-many relationship with permissions
    permissions = db.relationship(
        "Permission",
        secondary="role_permission",
        back_populates="roles",
        lazy="select",
    )
    
    # Relationship with users
    users = db.relationship("User", back_populates="custom_role", lazy=True)
    
    def __repr__(self):
        return f"<CustomRole {self.name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "permissions": [p.to_dict() for p in self.permissions],  # type: ignore[union-attr]
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# Association table for role-permission many-to-many relationship
role_permission = db.Table(
    "role_permission",
    db.Column("role_id", db.Integer, db.ForeignKey("custom_role.id", ondelete="CASCADE"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True)
)


class UserActivity(db.Model):
    __tablename__ = "user_activity"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)

    user = db.relationship("User", back_populates="activities")

    def __init__(
        self,
        user_id: int,
        activity_type: str,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        super().__init__()
        self.user_id = user_id
        self.activity_type = activity_type
        self.description = description
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"<UserActivity {self.activity_type} by {self.user_id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.GENERAL)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # type: ignore[assignment]
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    tier = db.Column(db.Integer, default=3, nullable=False)

    @property
    def effective_tier(self):
        """Computed tier based on role + custom_role.
        
        Tier 0 — SUPERUSER: absolute bypass, no checks
        Tier 1 — ADMIN: full management
        Tier 2 — custom_role (editor, writer, etc.): permission-scoped
        Tier 3 — GENERAL: own resources only
        """
        if self.role == UserRole.SUPERUSER:
            return 0
        if self.role == UserRole.ADMIN:
            return 1
        if self.custom_role and self.custom_role.is_active:
            return 2
        return 3
    verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # New fields for enhanced user management
    email = db.Column(db.String(255), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    social_links = db.Column(db.JSON, nullable=True)  # Store social media links as JSON
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0, nullable=False)
    is_suspended = db.Column(db.Boolean, default=False, nullable=False)
    suspension_reason = db.Column(db.Text, nullable=True)
    suspension_until = db.Column(db.DateTime, nullable=True)
    
    # Use timezone-aware default
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False
    )

    # Foreign key for custom role
    custom_role_id = db.Column(db.Integer, db.ForeignKey("custom_role.id"), nullable=True)
    
    # Subscription-related fields
    has_premium_access = db.Column(db.Boolean, default=False, nullable=False)
    premium_expires_at = db.Column(db.DateTime)
    ad_preferences = db.Column(db.JSON, default=lambda: {"show_ads": True, "ad_frequency": "normal"})
    
    # Relationships - Use back_populates for bidirectional links
    news = db.relationship(
        "News",
        back_populates="author",  # Links to News.author
        lazy=True,
        cascade="all, delete-orphan",
    )
    subscriptions = db.relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    images = db.relationship(
        "Image",
        backref=db.backref(
            "user", lazy=True
        ),  # Keep simple backref if Image doesn't link back explicitly
        lazy=True,
        cascade="all, delete-orphan",
    )
    youtube_videos = db.relationship(
        "YouTubeVideo",
        backref=db.backref(
            "uploader", lazy=True
        ),  # Keep simple backref if YouTubeVideo doesn't link back explicitly
        lazy=True,
        cascade="all, delete-orphan",
    )
    # Use back_populates for SocialMedia creator/updater
    created_social_media = db.relationship(
        "SocialMedia",
        foreign_keys="SocialMedia.created_by",
        back_populates="creator",  # Links to SocialMedia.creator
        lazy=True,
    )
    updated_social_media = db.relationship(
        "SocialMedia",
        foreign_keys="SocialMedia.updated_by",
        back_populates="updater",  # Links to SocialMedia.updater
        lazy=True,
    )
    
    # New relationships for enhanced user management
    custom_role = db.relationship("CustomRole", back_populates="users", lazy=True)
    activities = db.relationship("UserActivity", back_populates="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes and sets the user's password."""
        if not password or len(password.strip()) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the user's hashed password."""
        if not password:
            return False
        return check_password_hash(self.password_hash, password)

    def is_owner(self):
        """Tier 0 — absolute superuser."""
        return self.effective_tier == 0

    def is_admin_tier(self) -> bool:
        """Tier ≤ 1 — admin or superuser."""
        return self.effective_tier <= 1

    def is_writer(self) -> bool:
        """Tier ≤ 2 — has content write access."""
        return self.effective_tier <= 2

    def has_permission(self, resource, action):
        """Check if user has permission for a specific resource and action.
        
        Tier-based:
        - Tier 0 (SUPERUSER): ALL permissions
        - Tier 1 (ADMIN): ALL except restricted (users:delete, users:suspend)
        - Tier 2 (custom_role): only what's assigned via custom_role.permissions
        - Tier 3 (GENERAL): own content only
        """
        # Tier 0 bypass
        if self.effective_tier == 0:
            return True

        # Tier 1 — admin: full access except user deletion/suspension
        if self.effective_tier == 1:
            if resource == "users" and action in ("delete", "suspend"):
                return False
            return True

        # Tier 2 — custom_role: check assigned permissions
        if self.effective_tier == 2:
            if self.custom_role and self.custom_role.is_active:
                for p in self.custom_role.permissions:
                    if p.resource == resource and p.action == action:
                        return True
            return False

        # Tier 3 — GENERAL: own content
        if self.effective_tier == 3:
            if resource == "news" and action in ("create", "read"):
                return True
            if resource == "images" and action in ("create", "read"):
                return True
            return False

        return False
    
    def is_suspended_now(self):
        """Check if user is currently suspended."""
        if not self.is_suspended:
            return False
        if self.suspension_until and self.suspension_until < datetime.now(timezone.utc):
            # Suspension has expired, reactivate user
            self.is_suspended = False
            self.suspension_reason = None
            self.suspension_until = None
            return False
        return True
    
    def get_full_name(self):
        """Get user's full name or username if no name is set."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username
    
    def record_activity(self, activity_type, description=None, ip_address=None, user_agent=None):
        activity = UserActivity(
            user_id=self.id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(activity)

    def update_login_info(self, ip_address=None, user_agent=None):
        self.last_login = datetime.now(timezone.utc)
        self.login_count += 1
        self.record_activity("login", "User logged in", ip_address, user_agent)
    
    def has_active_premium_subscription(self):
        if not self.has_premium_access:
            return False

        if self.premium_expires_at:
            expires = (
                self.premium_expires_at
                if self.premium_expires_at.tzinfo
                else self.premium_expires_at.replace(tzinfo=timezone.utc)
            )
            if expires < datetime.now(timezone.utc):
                self.has_premium_access = False
                self.premium_expires_at = None
                return False

        return True
    
    def get_active_subscription(self):
        for subscription in self.subscriptions:  # type: ignore[union-attr]
            if subscription.is_active:
                return subscription
        return None
    
    def should_show_ads(self):
        """Check if ads should be shown to this user based on their preferences."""
        if not self.ad_preferences:
            return True
        
        if self.has_active_premium_subscription() and not self.ad_preferences.get("show_ads", True):
            return False
        
        return self.ad_preferences.get("show_ads", True)

    def to_dict(self):
        sub = self.get_active_subscription()
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "tier": self.effective_tier,
            "verified": self.verified,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "social_links": self.social_links,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "is_suspended": self.is_suspended,
            "suspension_reason": self.suspension_reason,
            "suspension_until": self.suspension_until.isoformat() if self.suspension_until else None,
            "custom_role": self.custom_role.to_dict() if self.custom_role else None,
            "has_premium_access": self.has_premium_access,
            "premium_expires_at": self.premium_expires_at.isoformat() if self.premium_expires_at else None,
            "ad_preferences": self.ad_preferences,
            "active_subscription": sub.to_dict() if sub else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.username}>"


class PrivacyPolicy(db.Model):
    __tablename__ = "privacy_policy"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "section_order": self.section_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MediaGuideline(db.Model):
    __tablename__ = "media_guideline"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "section_order": self.section_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class VisiMisi(db.Model):
    __tablename__ = "visi_misi"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "section_order": self.section_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Penyangkalan(db.Model):
    __tablename__ = "penyangkalan"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "section_order": self.section_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class PedomanHak(db.Model):
    __tablename__ = "pedoman_hak"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "section_order": self.section_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Image(db.Model):
    __tablename__ = "image"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    filepath = db.Column(db.String(255), nullable=True, unique=True)  # For file uploads
    url = db.Column(db.String(255), nullable=True, unique=True)  # For direct links
    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    # Foreign Keys
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    # Relationship defined via backref in User.images

    def to_dict(self):
        """Converts the image object to a dictionary."""
        file_url = None
        if self.filepath:
            try:
                # Generate URL relative to static folder
                static_path = (
                    self.filepath.split("static/", 1)[1]
                    if "static/" in self.filepath
                    else self.filepath
                )
                file_url = url_for("static", filename=static_path, _external=True)
            except Exception:
                file_url = self.filepath

        return {
            "id": self.id,
            "filename": self.filename,
            "description": self.description,
            "filepath": self.filepath,
            "file_url": file_url,
            "url": self.url,
            "is_visible": self.is_visible,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
        }

    def delete_file(self):
        """Deletes the associated file from the filesystem."""
        try:
            if self.filepath and os.path.exists(self.filepath):
                os.remove(self.filepath)
        except (OSError, IOError) as e:
            # Log the error but don't raise it
            print(f"Error deleting file {self.filepath}: {e}")


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # Relationship back to News using back_populates
    news = db.relationship("News", back_populates="category", lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


# ═══════════════════════════════════════════════════════════════════════
# Phase 8: Core CMS Models
# ═══════════════════════════════════════════════════════════════════════


# ── Tags ──────────────────────────────────────────────────────────────
class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "count": self.news.count(),
            "created_at": self.created_at.isoformat(),
        }


news_tags = db.Table(
    "news_tags",
    db.Column("news_id", db.Integer, db.ForeignKey("news.id", ondelete="CASCADE"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


# ── Static Pages ──────────────────────────────────────────────────────
class Page(db.Model):
    __tablename__ = "page"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=True)
    excerpt = db.Column(db.Text, nullable=True)
    template = db.Column(db.String(50), default="default", nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    show_in_menu = db.Column(db.Boolean, default=False, nullable=False)
    menu_order = db.Column(db.Integer, default=0, nullable=False)
    meta_title = db.Column(db.String(200), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    og_title = db.Column(db.String(200), nullable=True)
    og_description = db.Column(db.String(500), nullable=True)
    og_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    author = db.relationship("User", backref="pages", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "content": self.content,
            "excerpt": self.excerpt,
            "template": self.template,
            "is_published": self.is_published,
            "show_in_menu": self.show_in_menu,
            "menu_order": self.menu_order,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ── Comments ──────────────────────────────────────────────────────────
class CommentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SPAM = "spam"


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(CommentStatus), default=CommentStatus.PENDING, nullable=False, index=True)
    author_name = db.Column(db.String(100), nullable=True)
    author_email = db.Column(db.String(255), nullable=True)
    author_ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)

    news_id = db.Column(db.Integer, db.ForeignKey("news.id", ondelete="CASCADE"), nullable=False, index=True)
    news = db.relationship("News", backref=db.backref("comments", lazy="dynamic", cascade="all, delete-orphan"))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    user = db.relationship("User", backref="comments", lazy=True)

    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete="CASCADE"), nullable=True)
    replies = db.relationship("Comment", backref=db.backref("parent", remote_side=[id]), lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "status": self.status.value,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "news_id": self.news_id,
            "user_id": self.user_id,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tagar = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=default_utcnow, nullable=False, index=True)
    read_count = db.Column(db.Integer, default=0, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_main_news = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_news = db.Column(db.Boolean, default=False, nullable=False, index=True)  # Renamed from premium
    is_premium = db.Column(db.Boolean, default=False, nullable=False, index=True)  # New field for membership
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)  # Added for archiving
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )
    writer = db.Column(db.String(100), nullable=True)
    external_source = db.Column(db.String(255), nullable=True)

    # SEO Fields
    meta_description = db.Column(db.String(500), nullable=True)  # Meta description for search engines
    meta_keywords = db.Column(db.String(500), nullable=True)    # Meta keywords for search engines
    og_title = db.Column(db.String(200), nullable=True)         # Open Graph title for social media
    og_description = db.Column(db.String(500), nullable=True)   # Open Graph description for social media
    og_image = db.Column(db.String(255), nullable=True)         # Open Graph image URL for social media
    canonical_url = db.Column(db.String(255), nullable=True)    # Canonical URL to prevent duplicate content
    seo_slug = db.Column(db.String(255), nullable=True, unique=True, index=True)  # SEO-friendly URL slug
    
    # Advanced SEO Fields
    schema_markup = db.Column(db.Text, nullable=True)          # JSON-LD structured data
    twitter_card = db.Column(db.String(50), nullable=True)     # Type of Twitter card (summary, summary_large_image, etc.)
    twitter_title = db.Column(db.String(200), nullable=True)   # Twitter-specific title
    twitter_description = db.Column(db.String(500), nullable=True)  # Twitter-specific description
    twitter_image = db.Column(db.String(255), nullable=True)   # Twitter-specific image URL
    meta_author = db.Column(db.String(100), nullable=True)     # Article author for meta tags
    meta_language = db.Column(db.String(10), nullable=True)    # Content language (en, id, etc.)
    meta_robots = db.Column(db.String(50), nullable=True)      # Robots meta tag (index, noindex, etc.)
    structured_data_type = db.Column(db.String(50), nullable=True)  # Type of structured data (Article, NewsArticle, etc.)
    seo_score = db.Column(db.Integer, nullable=True)           # Calculated SEO score (0-100)
    last_seo_audit = db.Column(db.DateTime, nullable=True)     # Last SEO audit timestamp
    is_seo_lock = db.Column(db.Boolean, default=False, nullable=False)  # Lock SEO fields from automatic updates

    # Foreign Keys with explicit names
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id", name="fk_news_category_id"),
        nullable=False,
    )
    # Use back_populates to link back to Category.news
    category = db.relationship("Category", back_populates="news")

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_news_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    # Use back_populates and rename to 'author' to link back to User.news
    author = db.relationship("User", back_populates="news")

    # Add image_id to connect news to an image (nullable)
    image_id = db.Column(
        db.Integer,
        db.ForeignKey("image.id", name="fk_news_image_id"),
        nullable=True,
    )
    # Keep simple backref if Image doesn't link back explicitly
    image = db.relationship("Image", backref="news")

    # Tags (many-to-many)
    tags = db.relationship("Tag", secondary=news_tags, backref=db.backref("news", lazy="dynamic"))

    @property
    def reading_time(self):
        """Estimate reading time in minutes (avg 200 words/min)."""
        import re as _re
        text = _re.sub(r"<[^>]+>", "", self.content or "")
        words = len(text.split())
        return max(1, round(words / 200))

    @property
    def slug(self):
        return slugify(self.title)

    def __init__(self, **kwargs):
        super(News, self).__init__(**kwargs)
        # Validation removed from __init__, call it explicitly before adding to session if needed
        # self.validate()

    def validate(self):
        """Validate the news object before saving to the database."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Title is required")
        if len(self.title) > 200:
            raise ValueError("Title must be less than 200 characters")
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Content is required")
        if self.tagar and len(self.tagar) > 255:
            raise ValueError("Tags must be less than 255 characters")
        if not self.category_id:
            raise ValueError("Category is required")
        if not self.user_id:
            raise ValueError("User (author) is required")
        
        # SEO validation
        if self.meta_description and len(self.meta_description) > 500:
            raise ValueError("Meta description must be less than 500 characters")
        if self.meta_keywords and len(self.meta_keywords) > 500:
            raise ValueError("Meta keywords must be less than 500 characters")
        if self.og_title and len(self.og_title) > 200:
            raise ValueError("Open Graph title must be less than 200 characters")
        if self.og_description and len(self.og_description) > 500:
            raise ValueError("Open Graph description must be less than 500 characters")
        if self.canonical_url and len(self.canonical_url) > 255:
            raise ValueError("Canonical URL must be less than 255 characters")
        if self.seo_slug and len(self.seo_slug) > 255:
            raise ValueError("SEO slug must be less than 255 characters")
        
        # Advanced SEO validation
        if self.twitter_title and len(self.twitter_title) > 200:
            raise ValueError("Twitter title must be less than 200 characters")
        if self.twitter_description and len(self.twitter_description) > 500:
            raise ValueError("Twitter description must be less than 500 characters")
        if self.twitter_image and len(self.twitter_image) > 255:
            raise ValueError("Twitter image URL must be less than 255 characters")
        if self.meta_author and len(self.meta_author) > 100:
            raise ValueError("Meta author must be less than 100 characters")
        if self.meta_language and len(self.meta_language) > 10:
            raise ValueError("Meta language must be less than 10 characters")
        if self.meta_robots and len(self.meta_robots) > 50:
            raise ValueError("Meta robots must be less than 50 characters")
        if self.structured_data_type and len(self.structured_data_type) > 50:
            raise ValueError("Structured data type must be less than 50 characters")
        if self.seo_score and (self.seo_score < 0 or self.seo_score > 100):
            raise ValueError("SEO score must be between 0 and 100")

    def calculate_seo_score(self):
        """Calculate SEO score based on completeness of SEO fields."""
        score = 0

        # Basic SEO fields (40 points)
        if self.meta_description and len(self.meta_description.strip()) > 0:
            score += 8
        if self.meta_keywords and len(self.meta_keywords.strip()) > 0:
            score += 4
        if self.seo_slug and len(self.seo_slug.strip()) > 0:
            score += 4
        if self.canonical_url and len(self.canonical_url.strip()) > 0:
            score += 4
        
        # Open Graph fields (30 points)
        if self.og_title and len(self.og_title.strip()) > 0:
            score += 10
        if self.og_description and len(self.og_description.strip()) > 0:
            score += 10
        if self.og_image and len(self.og_image.strip()) > 0:
            score += 10
        
        # Twitter fields (20 points)
        if self.twitter_title and len(self.twitter_title.strip()) > 0:
            score += 5
        if self.twitter_description and len(self.twitter_description.strip()) > 0:
            score += 5
        if self.twitter_image and len(self.twitter_image.strip()) > 0:
            score += 5
        if self.twitter_card and len(self.twitter_card.strip()) > 0:
            score += 5
        
        # Advanced fields (10 points)
        if self.schema_markup and len(self.schema_markup.strip()) > 0:
            score += 5
        if self.structured_data_type and len(self.structured_data_type.strip()) > 0:
            score += 5
        
        return min(score, 100)  # Cap at 100

    def generate_schema_markup(self):
        """Generate JSON-LD structured data for the news article."""
        schema = {
            "@context": "https://schema.org",
            "@type": "NewsArticle" if self.is_news else "Article",
            "headline": self.title,
            "description": self.meta_description or self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "author": {
                "@type": "Person",
                "name": self.writer or self.author.username
            },
            "datePublished": self.date.isoformat(),
            "dateModified": self.updated_at.isoformat(),
            "publisher": {
                "@type": "Organization",
                "name": "LilyOpenCMS",
                "logo": {
                    "@type": "ImageObject",
                    "url": url_for('static', filename='pic/logo.png', _external=True)
                }
            }
        }
        
        if self.image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": self.image.to_dict()["file_url"],
                "width": 1200,
                "height": 630
            }
        
        if self.category:
            schema["articleSection"] = self.category.name
        
        return json.dumps(schema, ensure_ascii=False)

    def generate_seo_slug(self):
        """Generate SEO-friendly slug from title."""
        if not self.title:
            return None
        
        # Convert to lowercase and replace spaces with hyphens
        slug = self.title.lower()
        # Remove special characters except hyphens and underscores
        slug = re.sub(r'[^a-z0-9\s\-_]', '', slug)
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Remove leading and trailing hyphens
        slug = slug.strip('-')
        
        # Ensure uniqueness by appending ID if needed
        if self.id:
            base_slug = slug
            counter = 1
            while News.query.filter_by(seo_slug=slug).filter(News.id != self.id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
        
        return slug

    def update_seo_fields(self):
        """Update SEO-related fields automatically."""
        if not self.seo_slug:
            self.seo_slug = self.generate_seo_slug()
        
        if not self.schema_markup:
            self.schema_markup = self.generate_schema_markup()
        
        if not self.meta_author:
            self.meta_author = self.writer or self.author.username
        
        if not self.meta_language:
            self.meta_language = "id"  # Indonesian
        
        if not self.meta_robots:
            self.meta_robots = "index, follow"
        
        if not self.structured_data_type:
            self.structured_data_type = "NewsArticle" if self.is_news else "Article"
        
        # Calculate SEO score
        self.seo_score = self.calculate_seo_score()
        self.last_seo_audit = datetime.now(timezone.utc)

    def increment_reads(self):
        self.read_count += 1

    def to_dict(self):
        _share_log = getattr(self, "share_log", None)
        share_data = _share_log.to_dict() if _share_log else None
        
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tagar": self.tagar,
            "date": self.date.isoformat(),
            "read_count": self.read_count,
            "is_visible": self.is_visible,
            "is_main_news": self.is_main_news,
            "is_news": self.is_news,
            "is_premium": self.is_premium,
            "is_archived": self.is_archived,
            "writer": self.writer,
            "external_source": self.external_source,
            "category": self.category.to_dict() if self.category else None,
            "author": self.author.to_dict() if self.author else None,
            "image": self.image.to_dict() if self.image else None,
            "share_data": share_data,
            "seo_score": self.seo_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<News {self.title}>"


class Album(db.Model):
    """Model for grouping news articles into albums/chapters like a novel."""
    __tablename__ = "album"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_image_id = db.Column(db.Integer, db.ForeignKey("image.id"), nullable=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_premium = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_hiatus = db.Column(db.Boolean, default=False, nullable=False, index=True)
    total_chapters = db.Column(db.Integer, default=0, nullable=False)
    total_reads = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    # SEO Fields
    meta_description = db.Column(db.String(500), nullable=True)  # Meta description for search engines
    meta_keywords = db.Column(db.String(500), nullable=True)    # Meta keywords for search engines
    og_title = db.Column(db.String(200), nullable=True)         # Open Graph title for social media
    og_description = db.Column(db.String(500), nullable=True)   # Open Graph description for social media
    og_image = db.Column(db.String(255), nullable=True)         # Open Graph image URL for social media
    canonical_url = db.Column(db.String(255), nullable=True)    # Canonical URL to prevent duplicate content
    seo_slug = db.Column(db.String(255), nullable=True, unique=True, index=True)  # SEO-friendly URL slug
    
    # Advanced SEO Fields
    schema_markup = db.Column(db.Text, nullable=True)          # JSON-LD structured data
    twitter_card = db.Column(db.String(50), nullable=True)     # Type of Twitter card (summary, summary_large_image, etc.)
    twitter_title = db.Column(db.String(200), nullable=True)   # Twitter-specific title
    twitter_description = db.Column(db.String(500), nullable=True)  # Twitter-specific description
    twitter_image = db.Column(db.String(255), nullable=True)   # Twitter-specific image URL
    meta_author = db.Column(db.String(100), nullable=True)     # Album author for meta tags
    meta_language = db.Column(db.String(10), nullable=True)    # Content language (en, id, etc.)
    meta_robots = db.Column(db.String(50), nullable=True)      # Robots meta tag (index, noindex, etc.)
    structured_data_type = db.Column(db.String(50), nullable=True)  # Type of structured data (Book, CreativeWork, etc.)
    seo_score = db.Column(db.Integer, nullable=True)           # Calculated SEO score (0-100)
    last_seo_audit = db.Column(db.DateTime, nullable=True)     # Last SEO audit timestamp
    is_seo_lock = db.Column(db.Boolean, default=False, nullable=False)  # Lock SEO fields from automatic updates

    # Foreign Keys
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_album_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id", name="fk_album_category_id"),
        nullable=False,
    )

    # Relationships
    author = db.relationship("User", backref="albums")
    category = db.relationship("Category", backref="albums")
    cover_image = db.relationship("Image", backref="album_covers")
    chapters = db.relationship("AlbumChapter", back_populates="album", order_by="AlbumChapter.chapter_number", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(Album, self).__init__(**kwargs)

    def validate(self):
        """Validate the album object before saving to the database."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Title is required")
        if len(self.title) > 200:
            raise ValueError("Title must be less than 200 characters")
        if not self.category_id:
            raise ValueError("Category is required")
        if not self.user_id:
            raise ValueError("User (author) is required")

    def update_chapter_count(self):
        from typing import cast, List as _List
        chapters: _List["AlbumChapter"] = cast(_List["AlbumChapter"], self.chapters)
        self.total_chapters = len(chapters)
        self.total_reads = sum(c.news.read_count for c in chapters if c.news)

    def calculate_seo_score(self):
        """Calculate SEO score for the album (0-100)."""
        score = 0
        
        # Basic SEO elements (40 points)
        if self.title and len(self.title.strip()) > 0:
            score += 10
        if self.description and len(self.description.strip()) > 0:
            score += 10
        if self.meta_description and len(self.meta_description.strip()) > 0:
            score += 10
        if self.meta_keywords and len(self.meta_keywords.strip()) > 0:
            score += 10
        
        # Social media optimization (30 points)
        if self.og_title and len(self.og_title.strip()) > 0:
            score += 10
        if self.og_description and len(self.og_description.strip()) > 0:
            score += 10
        if self.og_image and len(self.og_image.strip()) > 0:
            score += 10
        
        # Advanced SEO elements (30 points)
        if self.seo_slug and len(self.seo_slug.strip()) > 0:
            score += 10
        if self.canonical_url and len(self.canonical_url.strip()) > 0:
            score += 10
        if self.schema_markup and len(self.schema_markup.strip()) > 0:
            score += 10
        
        return min(score, 100)

    def generate_schema_markup(self):
        """Generate JSON-LD structured data for the album."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Book" if self.is_completed else "CreativeWork",
            "name": self.title,
            "description": self.description or self.title,
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() if self.author else "Unknown Author"
            },
            "publisher": {
                "@type": "Organization",
                "name": "LilyOpenCMS"
            },
            "datePublished": self.created_at.isoformat() if self.created_at else None,
            "dateModified": self.updated_at.isoformat() if self.updated_at else None,
            "numberOfPages": self.total_chapters,
            "isAccessibleForFree": not self.is_premium,
            "inLanguage": self.meta_language or "id",
            "genre": self.category.name if self.category else None,
            "url": self.canonical_url or f"/album/{self.id}",
        }
        
        # Add book-specific properties if completed
        if self.is_completed:
            schema["bookFormat"] = "Digital"
            schema["isbn"] = f"ALBUM-{self.id:06d}"
        
        # Add image if available
        if self.cover_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": self.cover_image.url or self.cover_image.filepath,
                "width": 800,
                "height": 600
            }
        
        return json.dumps(schema, ensure_ascii=False)

    def generate_seo_slug(self):
        if not self.title:
            return None

        slug = unicodedata.normalize('NFKD', self.title)
        
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-').lower()
        
        # Limit length
        if len(slug) > 50:
            slug = slug[:50]
        
        return slug

    def update_seo_fields(self):
        """Update SEO-related fields automatically."""
        from datetime import datetime
        
        # Generate SEO slug if not set
        if not self.seo_slug:
            self.seo_slug = self.generate_seo_slug()
        
        # Generate schema markup
        self.schema_markup = self.generate_schema_markup()
        
        # Set default meta author if not set
        if not self.meta_author and self.author:
            self.meta_author = self.author.get_full_name()
        
        # Set default language if not set
        if not self.meta_language:
            self.meta_language = "id"
        
        # Set default robots if not set
        if not self.meta_robots:
            self.meta_robots = "index, follow"
        
        # Set default Twitter card if not set
        if not self.twitter_card:
            self.twitter_card = "summary_large_image"
        
        self.seo_score = self.calculate_seo_score()
        self.last_seo_audit = datetime.now(timezone.utc)

    def to_dict(self):
        """Converts the album object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cover_image": self.cover_image.to_dict() if self.cover_image else None,
            "is_visible": self.is_visible,
            "is_premium": self.is_premium,
            "is_archived": self.is_archived,
            "is_completed": self.is_completed,
            "is_hiatus": self.is_hiatus,
            "total_chapters": self.total_chapters,
            "total_reads": self.total_reads,
            "category": self.category.to_dict() if self.category else None,
            "author": self.author.to_dict() if self.author else None,
            "chapters": [chapter.to_dict() for chapter in self.chapters],  # type: ignore[union-attr]
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            # SEO Fields
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "canonical_url": self.canonical_url,
            "seo_slug": self.seo_slug,
            "schema_markup": self.schema_markup,
            "twitter_card": self.twitter_card,
            "twitter_title": self.twitter_title,
            "twitter_description": self.twitter_description,
            "twitter_image": self.twitter_image,
            "meta_author": self.meta_author,
            "meta_language": self.meta_language,
            "meta_robots": self.meta_robots,
            "structured_data_type": self.structured_data_type,
            "seo_score": self.seo_score,
            "last_seo_audit": self.last_seo_audit.isoformat() if self.last_seo_audit else None,
        }

    def __repr__(self):
        return f"<Album {self.title}>"


class AlbumChapter(db.Model):
    """Model for individual chapters within an album."""
    __tablename__ = "album_chapter"

    id = db.Column(db.Integer, primary_key=True)
    chapter_number = db.Column(db.Integer, nullable=False)
    chapter_title = db.Column(db.String(200), nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )
    is_seo_lock = db.Column(db.Boolean, default=False, nullable=False)  # Lock SEO fields from automatic updates

    # Foreign Keys
    album_id = db.Column(
        db.Integer,
        db.ForeignKey("album.id", name="fk_album_chapter_album_id", ondelete="CASCADE"),
        nullable=False,
    )
    news_id = db.Column(
        db.Integer,
        db.ForeignKey("news.id", name="fk_album_chapter_news_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    album = db.relationship("Album", back_populates="chapters")
    news = db.relationship("News", backref="album_chapters")

    def __init__(self, **kwargs):
        super(AlbumChapter, self).__init__(**kwargs)

    def validate(self):
        """Validate the album chapter object before saving to the database."""
        if not self.chapter_title or len(self.chapter_title.strip()) == 0:
            raise ValueError("Chapter title is required")
        if len(self.chapter_title) > 200:
            raise ValueError("Chapter title must be less than 200 characters")
        if not self.album_id:
            raise ValueError("Album is required")
        if not self.news_id:
            raise ValueError("News article is required")
        if self.chapter_number < 1:
            raise ValueError("Chapter number must be at least 1")

    def to_dict(self):
        """Converts the album chapter object to a dictionary."""
        return {
            "id": self.id,
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "is_visible": self.is_visible,
            "news": self.news.to_dict() if self.news else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<AlbumChapter {self.chapter_number}: {self.chapter_title}>"


class YouTubeVideo(db.Model):
    __tablename__ = "youtube_video"

    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(11), unique=True, nullable=False, index=True)
    link = db.Column(db.String(255), unique=True, nullable=False)
    # metadata fields fetched from YouTube
    title = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # length in seconds
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    # Foreign Key
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_youtube_video_user_id", ondelete="CASCADE"),
        nullable=False,
    )
    # Relationship defined via backref in User.youtube_videos

    def __init__(self, **kwargs):
        super(YouTubeVideo, self).__init__(**kwargs)
        # Validation removed from __init__, call it explicitly before adding to session if needed
        # self.validate()

    def validate(self):
        """Validate the YouTube video object before saving."""
        if not self.youtube_id or len(self.youtube_id.strip()) != 11:
            raise ValueError("YouTube ID must be exactly 11 characters")
        if not self.link or (
            "youtube.com" not in self.link.lower()
            and "youtu.be" not in self.link.lower()
        ):
            raise ValueError("Valid YouTube or YouTu.be URL is required")
        if not self.user_id:
            raise ValueError("Uploader user ID is required")

    def to_dict(self):
        """Converts the YouTube video object to a dictionary."""
        return {
            "id": self.id,
            "youtube_id": self.youtube_id,
            "title": self.title,
            "duration": self.duration,
            "link": self.link,
            "is_visible": self.is_visible,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
            "uploader": self.uploader.username if self.uploader else "Unknown",  # type: ignore[union-attr]
        }

    def __repr__(self):
        return f"<YouTubeVideo {self.youtube_id}>"


class ShareLog(db.Model):
    __tablename__ = "share_log"

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(
        db.Integer,
        db.ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    whatsapp_count = db.Column(db.Integer, default=0, nullable=False)
    facebook_count = db.Column(db.Integer, default=0, nullable=False)
    twitter_count = db.Column(db.Integer, default=0, nullable=False)
    instagram_count = db.Column(db.Integer, default=0, nullable=False)
    bluesky_count = db.Column(db.Integer, default=0, nullable=False)
    clipboard_count = db.Column(db.Integer, default=0, nullable=False)
    first_shared_at = db.Column(db.DateTime, nullable=True)
    latest_shared_at = db.Column(db.DateTime, nullable=True)

    # Relationship to the News table
    news = db.relationship("News", backref=db.backref("share_log", uselist=False))

    def to_dict(self):
        """Converts the ShareLog object to a dictionary."""
        return {
            "id": self.id,
            "news_id": self.news_id,
            "whatsapp_count": self.whatsapp_count,
            "facebook_count": self.facebook_count,
            "twitter_count": self.twitter_count,
            "instagram_count": self.instagram_count,
            "bluesky_count": self.bluesky_count,
            "clipboard_count": self.clipboard_count,
            "first_shared_at": self.first_shared_at.isoformat()
            if self.first_shared_at
            else None,
            "latest_shared_at": self.latest_shared_at.isoformat()
            if self.latest_shared_at
            else None,
            # Optionally include total count
            "total_shares": (
                self.whatsapp_count
                + self.facebook_count
                + self.twitter_count
                + self.instagram_count
                + self.bluesky_count
                + self.clipboard_count
            ),
        }


class SocialMedia(db.Model):
    __tablename__ = "social_media"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,  # Allow user deletion without deleting social media link
    )
    updated_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,  # Allow user deletion without deleting social media link
    )

    # Define relationships using back_populates
    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_social_media",  # Links to User.created_social_media
        lazy=True,
    )
    updater = db.relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_social_media",  # Links to User.updated_social_media
        lazy=True,
    )

    def to_dict(self):
        """Converts the social media object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "creator_name": self.creator.username if self.creator else None,
            "updater_name": self.updater.username if self.updater else None,
        }

    def __repr__(self):
        return f"<SocialMedia {self.name}>"


class ContactDetail(db.Model):
    __tablename__ = "contact_detail"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    icon_class = db.Column(db.String(100), nullable=True)  # e.g. 'envelope'
    link = db.Column(db.String(255), nullable=True)  # e.g. 'mailto:you@example.com'
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "section_order": self.section_order,
            "is_active": self.is_active,
            "icon_class": self.icon_class,
            "link": self.link,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TeamMember(db.Model):
    __tablename__ = "team_member"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)  # Role or position
    group = db.Column(
        db.String(50), nullable=False
    )  # e.g.: leadership, editorial, news, video, sales
    member_order = db.Column(db.Integer, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False
    )

    @property
    def initials(self):
        parts = [p for p in self.name.split() if p]
        return "".join(p[0].upper() for p in parts)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "group": self.group,
            "member_order": self.member_order,
            "is_active": self.is_active,
            "initials": self.initials,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BrandIdentity(db.Model):
    """
    Stores brand identity information including name, tagline, and asset URLs.
    Each image field always points to a fixed file in static/pic/:
      - logo_header: /static/pic/logo.png
      - logo_footer: /static/pic/logo_footer.png
      - favicon: /static/pic/favicon.png
      - placeholder_image: /static/pic/placeholder.png
    """
    __tablename__ = "brand_identity"
    id = db.Column(db.Integer, primary_key=True)
    
    # Brand Information
    brand_name = db.Column(db.String(100), nullable=True, default="LilyOpenCMS")
    tagline = db.Column(db.String(255), nullable=True, default="Modern content management for the digital age")
    brand_description = db.Column(db.Text, nullable=True, default="")
    website_url = db.Column(db.String(255), nullable=True, default="https://hystory.id")

    # Homepage Design Preference
    homepage_design = db.Column(db.String(50), nullable=True, default="news")  # 'news' or 'albums'

    # Categories Display Location
    categories_display_location = db.Column(db.String(50), nullable=True, default="body")  # 'body', 'navbar', or 'none'

    # News Card Design Preference
    card_design = db.Column(db.String(50), nullable=True, default="classic")  # 'classic', 'modern', 'minimal', 'featured'

    # Per-context card design overrides
    card_design_homepage = db.Column(db.String(50), nullable=True)  # fallback to card_design if null
    card_design_listing = db.Column(db.String(50), nullable=True)   # fallback to card_design if null

    # Brand Assets
    logo_header = db.Column(db.String(255), nullable=True)  # /static/pic/logo.png
    logo_footer = db.Column(db.String(255), nullable=True)
    favicon = db.Column(db.String(255), nullable=True)
    placeholder_image = db.Column(db.String(255), nullable=True)

    # Brand color palette — HSL strings e.g. "220 70% 60%"
    color_primary = db.Column(db.String(50), nullable=True, default="220 70% 60%")
    color_primary_foreground = db.Column(db.String(50), nullable=True, default="0 0% 100%")
    color_secondary = db.Column(db.String(50), nullable=True, default="220 14% 96%")
    color_secondary_foreground = db.Column(db.String(50), nullable=True, default="220 9% 31%")
    color_accent = db.Column(db.String(50), nullable=True, default="260 60% 65%")
    color_accent_foreground = db.Column(db.String(50), nullable=True, default="0 0% 100%")
    color_background = db.Column(db.String(50), nullable=True, default="220 20% 98%")
    color_foreground = db.Column(db.String(50), nullable=True, default="220 15% 15%")

    # UI Page visibility
    enable_videos = db.Column(db.Boolean, nullable=False, default=True)
    enable_gallery = db.Column(db.Boolean, nullable=False, default=True)
    enable_albums = db.Column(db.Boolean, nullable=False, default=True)
    enable_news = db.Column(db.Boolean, nullable=False, default=True)
    enable_premium = db.Column(db.Boolean, nullable=False, default=True)
    enable_about = db.Column(db.Boolean, nullable=False, default=True)

    # Third-party tracking & scripts
    google_adsense_publisher_id = db.Column(db.String(100), nullable=True)
    google_tag_manager_id = db.Column(db.String(50), nullable=True)
    google_analytics_measurement_id = db.Column(db.String(50), nullable=True)

    # SEO & quality settings
    seo_settings = db.Column(db.JSON, nullable=True)
    min_story_word_count = db.Column(db.Integer, nullable=False, default=1000)
    min_chapter_word_count = db.Column(db.Integer, nullable=False, default=1000)

    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)

    def to_dict(self):
        return {
            "brand_name": self.brand_name,
            "tagline": self.tagline,
            "brand_description": self.brand_description,
            "homepage_design": self.homepage_design,
            "categories_display_location": self.categories_display_location or "none",
            "card_design": self.card_design or "classic",
            "card_design_homepage": self.card_design_homepage,
            "card_design_listing": self.card_design_listing,
            "website_url": self.website_url,
            "logo_header": self.logo_header,
            "logo_footer": self.logo_footer,
            "favicon": self.favicon,
            "placeholder_image": self.placeholder_image,
            "color_primary": self.color_primary,
            "color_primary_foreground": self.color_primary_foreground,
            "color_secondary": self.color_secondary,
            "color_secondary_foreground": self.color_secondary_foreground,
            "color_accent": self.color_accent,
            "color_accent_foreground": self.color_accent_foreground,
            "color_background": self.color_background,
            "color_foreground": self.color_foreground,
            "enable_videos": self.enable_videos,
            "enable_gallery": self.enable_gallery,
            "enable_albums": self.enable_albums,
            "enable_news": self.enable_news,
            "enable_premium": self.enable_premium,
            "enable_about": self.enable_about,
            "google_adsense_publisher_id": self.google_adsense_publisher_id,
            "google_tag_manager_id": self.google_tag_manager_id,
            "google_analytics_measurement_id": self.google_analytics_measurement_id,
            "seo_settings": self.seo_settings,
            "min_story_word_count": self.min_story_word_count,
            "min_chapter_word_count": self.min_chapter_word_count,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserSubscription(db.Model):
    __tablename__ = "user_subscriptions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subscription_type = db.Column(db.String(50), nullable=False)  # 'monthly', 'yearly'
    status = db.Column(db.String(50), nullable=False, default='active')  # 'active', 'cancelled', 'expired'
    start_date = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    payment_provider = db.Column(db.String(50))  # 'stripe', 'paypal', etc.
    payment_id = db.Column(db.String(255))  # External payment ID
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Subscription amount
    currency = db.Column(db.String(3), default='IDR')
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)
    
    # Relationship
    user = db.relationship("User", back_populates="subscriptions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_type": self.subscription_type,
            "status": self.status,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "payment_provider": self.payment_provider,
            "payment_id": self.payment_id,
            "amount": float(self.amount) if self.amount else None,
            "currency": self.currency,
            "auto_renew": self.auto_renew,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # Ensure end_date is timezone-aware
        if self.end_date.tzinfo is None:
            # If naive, assume UTC
            end_date = self.end_date.replace(tzinfo=timezone.utc)
        else:
            end_date = self.end_date
        
        return self.status == 'active' and end_date > now


class NavigationLink(db.Model):
    __tablename__ = "navigation_link"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Display name
    url = db.Column(db.String(255), nullable=False)   # URL path
    location = db.Column(db.String(50), nullable=False)  # 'navbar' or 'footer'
    order = db.Column(db.Integer, nullable=False, default=0)  # Display order
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_external = db.Column(db.Boolean, default=False, nullable=False)  # External link
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=default_utcnow,
        onupdate=default_utcnow,
        nullable=False,
    )

    # Foreign key to user who created/updated
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_navigation_link_user_id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self):
        return f"<NavigationLink {self.name} ({self.location})>"

    def to_dict(self):
        """Converts the NavigationLink object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "location": self.location,
            "order": self.order,
            "is_active": self.is_active,
            "is_external": self.is_external,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
        }


class RootSEO(db.Model):
    """Model for managing SEO settings for root website pages."""
    __tablename__ = "root_seo"

    id = db.Column(db.Integer, primary_key=True)
    page_identifier = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., 'home', 'about', 'news'
    page_name = db.Column(db.String(100), nullable=False)  # Display name for the page
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Basic SEO Fields
    meta_title = db.Column(db.String(200), nullable=True)  # Page title for search engines
    meta_description = db.Column(db.String(500), nullable=True)  # Meta description for search engines
    meta_keywords = db.Column(db.String(500), nullable=True)    # Meta keywords for search engines
    
    # Open Graph Fields
    og_title = db.Column(db.String(200), nullable=True)         # Open Graph title for social media
    og_description = db.Column(db.String(500), nullable=True)   # Open Graph description for social media
    og_image = db.Column(db.String(255), nullable=True)         # Open Graph image URL for social media
    og_type = db.Column(db.String(50), nullable=True, default='website')  # Open Graph type
    
    # Twitter Card Fields
    twitter_card = db.Column(db.String(50), nullable=True, default='summary_large_image')  # Type of Twitter card
    twitter_title = db.Column(db.String(200), nullable=True)   # Twitter-specific title
    twitter_description = db.Column(db.String(500), nullable=True)  # Twitter-specific description
    twitter_image = db.Column(db.String(255), nullable=True)   # Twitter-specific image URL
    
    # Advanced SEO Fields
    canonical_url = db.Column(db.String(255), nullable=True)    # Canonical URL to prevent duplicate content
    meta_author = db.Column(db.String(100), nullable=True)     # Page author for meta tags
    meta_language = db.Column(db.String(10), nullable=True, default='id')    # Content language (en, id, etc.)
    meta_robots = db.Column(db.String(50), nullable=True, default='index, follow')      # Robots meta tag
    structured_data_type = db.Column(db.String(50), nullable=True)  # Type of structured data (WebSite, Organization, etc.)
    schema_markup = db.Column(db.Text, nullable=True)          # JSON-LD structured data
    
    # Analytics and Tracking
    google_analytics_id = db.Column(db.String(50), nullable=True)
    facebook_pixel_id = db.Column(db.String(50), nullable=True)

    # SEO score and audit
    seo_score = db.Column(db.Integer, nullable=True)
    last_seo_audit = db.Column(db.DateTime, nullable=True)

    # Timestamps and User Tracking
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_root_seo")
    updater = db.relationship("User", foreign_keys=[updated_by], backref="updated_root_seo")
    
    def __init__(self, **kwargs):
        super(RootSEO, self).__init__(**kwargs)
    
    def validate(self):
        """Validate the root SEO object before saving to the database."""
        if not self.page_identifier or len(self.page_identifier.strip()) == 0:
            raise ValueError("Page identifier is required")
        if len(self.page_identifier) > 50:
            raise ValueError("Page identifier must be less than 50 characters")
        if not self.page_name or len(self.page_name.strip()) == 0:
            raise ValueError("Page name is required")
        if len(self.page_name) > 100:
            raise ValueError("Page name must be less than 100 characters")
        
        # SEO validation
        if self.meta_title and len(self.meta_title) > 200:
            raise ValueError("Meta title must be less than 200 characters")
        if self.meta_description and len(self.meta_description) > 500:
            raise ValueError("Meta description must be less than 500 characters")
        if self.meta_keywords and len(self.meta_keywords) > 500:
            raise ValueError("Meta keywords must be less than 500 characters")
        if self.og_title and len(self.og_title) > 200:
            raise ValueError("Open Graph title must be less than 200 characters")
        if self.og_description and len(self.og_description) > 500:
            raise ValueError("Open Graph description must be less than 500 characters")
        if self.canonical_url and len(self.canonical_url) > 255:
            raise ValueError("Canonical URL must be less than 255 characters")
    
    def calculate_seo_score(self):
        """Calculate SEO score based on completeness of SEO fields."""
        score = 0
        total_fields = 8  # Number of important SEO fields
        
        if self.meta_title:
            score += 1
        if self.meta_description:
            score += 1
        if self.meta_keywords:
            score += 1
        if self.og_title:
            score += 1
        if self.og_description:
            score += 1
        if self.og_image:
            score += 1
        if self.canonical_url:
            score += 1
        if self.schema_markup:
            score += 1
        
        return int((score / total_fields) * 100)
    
    def generate_schema_markup(self):
        """Generate JSON-LD structured data for the page."""
        if not self.schema_markup:
            schema = {
                "@context": "https://schema.org",
                "@type": self.structured_data_type or "WebPage",
                "name": self.page_name,
                "description": self.meta_description,
                "url": self.canonical_url or f"https://{request.host}{request.path}",
                "inLanguage": self.meta_language or "id"
            }
            
            if self.meta_author:
                schema["author"] = {
                    "@type": "Person",
                    "name": self.meta_author
                }
            
            self.schema_markup = json.dumps(schema, ensure_ascii=False)
        
        return self.schema_markup
    
    def update_seo_fields(self):
        """Update SEO-related fields and calculate score."""
        self.seo_score = self.calculate_seo_score()
        self.last_seo_audit = datetime.now(timezone.utc)
        
        # Generate schema markup if not present
        if not self.schema_markup:
            self.generate_schema_markup()
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "page_identifier": self.page_identifier,
            "page_name": self.page_name,
            "is_active": self.is_active,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "og_type": self.og_type,
            "twitter_card": self.twitter_card,
            "twitter_title": self.twitter_title,
            "twitter_description": self.twitter_description,
            "twitter_image": self.twitter_image,
            "canonical_url": self.canonical_url,
            "meta_author": self.meta_author,
            "meta_language": self.meta_language,
            "meta_robots": self.meta_robots,
            "structured_data_type": self.structured_data_type,
            "schema_markup": self.schema_markup,
            "google_analytics_id": self.google_analytics_id,
            "facebook_pixel_id": self.facebook_pixel_id,
            "seo_score": self.calculate_seo_score(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }
    
    def __repr__(self):
        return f"<RootSEO {self.page_identifier}: {self.page_name}>"


# Email Tracking and Analytics Models

class EmailType(Enum):
    """Email type enumeration"""
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    SUSPENSION = "suspension"
    WRITE_ACCESS_APPROVED = "write_access_approved"
    WRITE_ACCESS_REJECTED = "write_access_rejected"
    ACCOUNT_DELETION_REQUEST = "account_deletion_request"
    ACCOUNT_DELETION_CONFIRMATION = "account_deletion_confirmation"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    CONTENT_DELETION = "content_deletion"
    PROFILE_UPDATE = "profile_update"
    EDIT_REQUEST_APPROVED = "edit_request_approved"
    EDIT_REQUEST_REJECTED = "edit_request_rejected"
    ALBUM_EDIT_REQUEST_SUBMITTED = "album_edit_request_submitted"
    EDITOR_EDIT_REQUEST_NOTIFICATION = "editor_edit_request_notification"
    CHAPTER_PUBLISHED = "chapter_published"
    SCHEDULED_CONTENT_PUBLISHED = "scheduled_content_published"
    CUSTOM = "custom"


class EmailStatus(Enum):
    """Email delivery status"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    COMPLAINT = "complaint"


class EmailLog(db.Model):
    """Tracks all email deliveries for analytics and monitoring"""
    __tablename__ = 'email_logs'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(255), unique=True, nullable=True)  # SMTP Message-ID
    celery_task_id = db.Column(db.String(255), nullable=True)  # Celery task ID for async emails

    # Email details
    recipient = db.Column(db.String(255), nullable=False, index=True)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    email_type = db.Column(db.Enum(EmailType), nullable=False, default=EmailType.CUSTOM)

    # Status tracking
    status = db.Column(db.Enum(EmailStatus), nullable=False, default=EmailStatus.QUEUED)
    status_updated_at = db.Column(db.DateTime(timezone=True), default=default_utcnow, onupdate=default_utcnow)

    # Timestamps
    queued_at = db.Column(db.DateTime(timezone=True), default=default_utcnow)
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=True)
    failed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Error tracking
    error_message = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)

    # Rate limiting info
    rate_limit_hit = db.Column(db.Boolean, default=False)
    rate_limit_reason = db.Column(db.String(255), nullable=True)

    # User association (nullable for system emails)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('email_logs', lazy='dynamic'))

    # Additional metadata
    extra_data = db.Column(db.JSON, nullable=True)  # Store additional tracking data
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4/IPv6
    user_agent = db.Column(db.String(500), nullable=True)

    # Template info
    template_name = db.Column(db.String(255), nullable=True)

    def update_status(self, status: EmailStatus, error_message: str = None):
        """Update status of email log with timestamp"""
        self.status = status
        self.status_updated_at = default_utcnow()
        if status == EmailStatus.SENT:
            self.sent_at = default_utcnow()
        elif status == EmailStatus.DELIVERED:
            self.delivered_at = default_utcnow()
        elif status == EmailStatus.FAILED:
            self.failed_at = default_utcnow()
            self.error_message = error_message
        db.session.commit()

    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "celery_task_id": self.celery_task_id,
            "recipient": self.recipient,
            "sender": self.sender,
            "subject": self.subject,
            "email_type": self.email_type.value if self.email_type else None,
            "status": self.status.value if self.status else None,
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "rate_limit_hit": self.rate_limit_hit,
            "rate_limit_reason": self.rate_limit_reason,
            "user_id": self.user_id,
            "extra_data": self.extra_data,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "template_name": self.template_name,
        }


class EmailAnalytics(db.Model):
    """Daily aggregated email analytics"""
    __tablename__ = 'email_analytics'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)

    # Volume metrics
    emails_sent = db.Column(db.Integer, default=0, nullable=False)
    emails_delivered = db.Column(db.Integer, default=0, nullable=False)
    emails_failed = db.Column(db.Integer, default=0, nullable=False)
    emails_bounced = db.Column(db.Integer, default=0, nullable=False)
    emails_complained = db.Column(db.Integer, default=0, nullable=False)

    # Rate metrics
    delivery_rate = db.Column(db.Float, default=0.0)
    bounce_rate = db.Column(db.Float, default=0.0)
    complaint_rate = db.Column(db.Float, default=0.0)

    # Performance metrics
    avg_send_time = db.Column(db.Float, default=0.0)  # seconds
    avg_delivery_time = db.Column(db.Float, default=0.0)  # seconds

    # Type breakdown (JSON: {"verification": 5, "password_reset": 2, ...})
    type_breakdown = db.Column(db.JSON, nullable=True)

    # Rate limiting
    rate_limit_hits = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime(timezone=True), default=default_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=default_utcnow, onupdate=default_utcnow)

    def update_metrics(self):
        """Recalculate metrics from EmailLog for this date"""
        from sqlalchemy import and_, func
        day_start = datetime.combine(self.date, datetime.min.time())
        day_end = datetime.combine(self.date, datetime.max.time())

        logs = EmailLog.query.filter(
            and_(EmailLog.queued_at >= day_start, EmailLog.queued_at <= day_end)
        ).all()

        self.emails_sent = len([l for l in logs if l.status in (EmailStatus.SENT, EmailStatus.DELIVERED)])
        self.emails_delivered = len([l for l in logs if l.status == EmailStatus.DELIVERED])
        self.emails_failed = len([l for l in logs if l.status == EmailStatus.FAILED])
        self.emails_bounced = len([l for l in logs if l.status == EmailStatus.BOUNCED])
        self.emails_complained = len([l for l in logs if l.status == EmailStatus.COMPLAINT])
        self.rate_limit_hits = len([l for l in logs if l.rate_limit_hit])

        total = self.emails_sent or 1
        self.delivery_rate = (self.emails_delivered / total) * 100
        self.bounce_rate = (self.emails_bounced / total) * 100
        self.complaint_rate = (self.emails_complained / total) * 100

        # Type breakdown
        breakdown = {}
        for log in logs:
            t = log.email_type.value if log.email_type else "unknown"
            breakdown[t] = breakdown.get(t, 0) + 1
        self.type_breakdown = breakdown

        # Average send time
        send_times = []
        for log in logs:
            if log.sent_at and log.queued_at:
                send_times.append((log.sent_at - log.queued_at).total_seconds())
        self.avg_send_time = sum(send_times) / len(send_times) if send_times else 0

        # Average delivery time
        delivery_times = []
        for log in logs:
            if log.delivered_at and log.queued_at:
                delivery_times.append((log.delivered_at - log.queued_at).total_seconds())
        self.avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0

        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "emails_sent": self.emails_sent,
            "emails_delivered": self.emails_delivered,
            "emails_failed": self.emails_failed,
            "emails_bounced": self.emails_bounced,
            "emails_complained": self.emails_complained,
            "delivery_rate": self.delivery_rate,
            "bounce_rate": self.bounce_rate,
            "complaint_rate": self.complaint_rate,
            "avg_send_time": self.avg_send_time,
            "avg_delivery_time": self.avg_delivery_time,
            "type_breakdown": self.type_breakdown,
            "rate_limit_hits": self.rate_limit_hits,
        }


class EmailTemplate(db.Model):
    """Versioned email template storage"""
    __tablename__ = 'email_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    subject_template = db.Column(db.String(500), nullable=False)
    html_template = db.Column(db.Text, nullable=False)
    text_template = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    email_type = db.Column(db.Enum(EmailType), nullable=True)
    version = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=default_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=default_utcnow, onupdate=default_utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subject_template": self.subject_template,
            "html_template": self.html_template,
            "text_template": self.text_template,
            "description": self.description,
            "email_type": self.email_type.value if self.email_type else None,
            "version": self.version,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Event listeners
@event.listens_for(Image, "after_delete")
def delete_image_file(mapper, connection, target) -> None:  # noqa: ARG001
    target.delete_file()


# Indexes (can be used with Flask-Migrate)
# Note: Defining indexes here is informational.
# Actual creation/management is typically handled by migrations (e.g., using Alembic).
def create_indexes():
    """Creates database indexes for better query performance. (Run via migrations)"""
    # Example index commands (adjust dialect if not PostgreSQL/SQLite)
    # Use IF NOT EXISTS for safety
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_news_category_date ON news (category_id, date DESC);"
        )
    )
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_news_is_news_date ON news (is_news, date DESC);"
        )
    )
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_news_is_premium_date ON news (is_premium, date DESC);"
        )
    )
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_news_visible_date ON news (is_visible, date DESC);"
        )
    )
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_news_main_date ON news (is_main_news, date DESC);"
        )
    )
    # user.username is already indexed by unique=True, but explicit index can be added if needed
    # db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_username ON \"user\" (username);")) # Use quotes for reserved words like user
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_youtube_video_created_at ON youtube_video (created_at DESC);"
        )
    )
    # Add index for youtube_id if frequently queried directly
    db.session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_youtube_video_youtube_id ON youtube_video (youtube_id);"
        )
    )
    # Add index for share_log news_id (already unique, but index helps lookups)
    db.session.execute(
        text("CREATE INDEX IF NOT EXISTS idx_share_log_news_id ON share_log (news_id);")
    )
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
