"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Consolidated Permission Management System.

Single source of truth for all permission checks. Replaces the fragmented
systems in routes/utils/permission_manager.py, routes/common_imports.py
(User.has_permission), and routes/utils/auth_helpers.py.
"""

import logging
from typing import List, Dict, Optional

from flask_login import current_user

logger = logging.getLogger(__name__)


class PermissionManager:
    """Centralized permission management system."""

    RESOURCES = {
        "users": "User management",
        "roles": "Role management",
        "permissions": "Permission management",
        "news": "News content",
        "images": "Image management",
        "videos": "Video management",
        "categories": "Category management",
        "settings": "System settings",
        "ads": "Advertisement management",
        "comments": "Comment moderation",
        "ratings": "Rating management",
        "analytics": "Analytics and performance",
        "legal": "Legal documents",
        "brand": "Brand management",
        "seo": "SEO management",
        "albums": "Album management",
    }

    ACTIONS = {
        "read": "View content",
        "create": "Create content",
        "update": "Edit content",
        "delete": "Delete content",
        "publish": "Publish/unpublish content",
        "suspend": "Suspend/unsuspend users",
        "moderate": "Moderate content",
        "approve": "Approve content",
        "reject": "Reject content",
        "export": "Export data",
        "import": "Import data",
        "configure": "Configure settings",
    }

    @staticmethod
    def get_user_permissions(user) -> List[Dict]:
        if not user or not user.is_authenticated:
            return []

        if user.is_owner():
            return [
                {"resource": r, "action": a, "name": f"{r}_{a}", "description": f"{PermissionManager.RESOURCES[r]} - {PermissionManager.ACTIONS[a]}"}
                for r in PermissionManager.RESOURCES
                for a in PermissionManager.ACTIONS
            ]

        permissions = []

        if user.custom_role and user.custom_role.is_active:
            for p in user.custom_role.permissions:
                permissions.append({
                    "resource": p.resource,
                    "action": p.action,
                    "name": p.name,
                    "description": p.description,
                })

        if user.role and user.role.value == "admin":
            admin_perms = [
                "users_read", "users_create", "users_update", "users_suspend",
                "news_read", "news_create", "news_update", "news_delete", "news_publish",
                "images_read", "images_create", "images_update", "images_delete",
                "videos_read", "videos_create", "videos_update", "videos_delete",
                "categories_read", "categories_create", "categories_update", "categories_delete",
                "settings_read", "settings_update",
                "comments_read", "comments_update", "comments_delete",
                "ratings_read", "ratings_update", "ratings_delete",
                "legal_read", "legal_update",
                "brand_read", "brand_update",
                "seo_read", "seo_update",
                "albums_read", "albums_create", "albums_update", "albums_delete",
            ]
            for name in admin_perms:
                resource, action = name.split("_", 1)
                permissions.append({
                    "resource": resource,
                    "action": action,
                    "name": name,
                    "description": f"{PermissionManager.RESOURCES.get(resource, resource)} - {PermissionManager.ACTIONS.get(action, action)}",
                })

        return permissions

    @staticmethod
    def has_permission(user, resource: str, action: str) -> bool:
        if not user or not user.is_authenticated:
            return False
        if user.is_owner():
            return True
        if user.custom_role and user.custom_role.is_active:
            for p in user.custom_role.permissions:
                if p.resource == resource and p.action == action:
                    return True
        if user.role and user.role.value == "admin":
            admin_resources = list(PermissionManager.RESOURCES.keys())
            return resource in admin_resources
        return False

    @staticmethod
    def has_any_permission(user, resource: str, actions: List[str]) -> bool:
        if not user or not user.is_authenticated:
            return False
        if user.is_owner():
            return True
        if user.custom_role and user.custom_role.is_active:
            for p in user.custom_role.permissions:
                if p.resource == resource and p.action in actions:
                    return True
        if user.role and user.role.value == "admin":
            return resource in PermissionManager.RESOURCES
        return False

    @staticmethod
    def has_all_permissions(user, resource: str, actions: List[str]) -> bool:
        if not user or not user.is_authenticated:
            return False
        if user.is_owner():
            return True
        if user.custom_role and user.custom_role.is_active:
            user_actions = {p.action for p in user.custom_role.permissions if p.resource == resource}
            return all(a in user_actions for a in actions)
        if user.role and user.role.value == "admin":
            return resource in PermissionManager.RESOURCES
        return False


def _get_user(user):
    return user if user is not None else current_user


def has_permission(user=None, resource: str = "", action: str = "") -> bool:
    return PermissionManager.has_permission(_get_user(user), resource, action)


def has_any_permission(user=None, resource: str = "", actions: Optional[List[str]] = None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), resource, actions or [])


def has_all_permissions(user=None, resource: str = "", actions: Optional[List[str]] = None) -> bool:
    return PermissionManager.has_all_permissions(_get_user(user), resource, actions or [])


def is_superuser(user=None) -> bool:
    u = _get_user(user)
    return u and u.is_authenticated and u.is_owner()


def is_admin(user=None) -> bool:
    u = _get_user(user)
    return u and u.is_authenticated and u.role and u.role.value == "admin"


def is_admin_tier(user=None) -> bool:
    u = _get_user(user)
    return u and u.is_authenticated and u.is_admin_tier()


def has_custom_role(user=None, role_name: str = "") -> bool:
    u = _get_user(user)
    if not u or not u.is_authenticated or not u.custom_role:
        return False
    if not role_name:
        return True
    return u.custom_role.name == role_name


def can_access_admin(user=None) -> bool:
    return _get_user(user).is_admin_tier() if _get_user(user) else False


def can_manage_users(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "users", ["read", "create", "update", "delete", "suspend"])


def can_manage_content(user=None) -> bool:
    u = _get_user(user)
    return (
        PermissionManager.has_any_permission(u, "news", ["read", "create", "update", "delete", "publish"])
        or PermissionManager.has_any_permission(u, "images", ["read", "create", "update", "delete"])
        or PermissionManager.has_any_permission(u, "videos", ["read", "create", "update", "delete"])
        or PermissionManager.has_any_permission(u, "albums", ["read", "create", "update", "delete"])
    )


def can_manage_categories(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "categories", ["read", "create", "update", "delete"])


def can_manage_settings(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "settings", ["read", "update"])


def can_manage_roles(user=None) -> bool:
    u = _get_user(user)
    return (
        PermissionManager.has_any_permission(u, "roles", ["read", "create", "update", "delete"])
        or PermissionManager.has_any_permission(u, "permissions", ["read", "create", "update", "delete"])
    )


def can_manage_ads(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "ads", ["read", "create", "update", "delete"])


def can_moderate_comments(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "comments", ["read", "update", "delete", "moderate"])


def can_manage_ratings(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "ratings", ["read", "update", "delete"])


def can_access_analytics(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "analytics", ["read"])


def can_manage_legal(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "legal", ["read", "update"])


def can_manage_brand(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "brand", ["read", "update"])


def can_manage_seo(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "seo", ["read", "update"])


def can_manage_news(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "news", ["read", "create", "update", "delete", "publish"])


def can_manage_albums(user=None) -> bool:
    return PermissionManager.has_any_permission(_get_user(user), "albums", ["read", "create", "update", "delete", "publish"])


def get_user_role_display(user=None) -> str:
    u = _get_user(user)
    if not u or not u.is_authenticated:
        return "Guest"
    if u.is_owner():
        return "Superuser"
    if u.custom_role:
        return f"{u.custom_role.name} ({u.role.value.title()})"
    return u.role.value.title() if u.role else "Unknown"


def get_user_permissions_summary(user=None) -> Dict[str, List[str]]:
    u = _get_user(user)
    if not u or not u.is_authenticated:
        return {}
    summary: Dict[str, List[str]] = {}
    for perm in PermissionManager.get_user_permissions(u):
        summary.setdefault(perm["resource"], []).append(perm["action"])
    return summary
