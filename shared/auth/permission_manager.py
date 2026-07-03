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
        "comments": "Comment management",
        "pages": "Static page management",
        "tags": "Tag management",
        "media": "Media uploads",
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
        "upload": "Upload files",
        "export": "Export data",
        "import": "Import data",
        "configure": "Configure settings",
    }

    @staticmethod
    def get_user_permissions(user) -> List[Dict]:
        if not user or not user.is_authenticated:
            return []

        # Tier 0 — ALL permissions
        if user.effective_tier == 0:
            return [
                {"resource": r, "action": a, "name": f"{r}_{a}", "description": f"{PermissionManager.RESOURCES[r]} - {PermissionManager.ACTIONS[a]}"}
                for r in PermissionManager.RESOURCES
                for a in PermissionManager.ACTIONS
            ]

        # Tier 1 — ADMIN: all resources
        if user.effective_tier == 1:
            perms = []
            for r in PermissionManager.RESOURCES:
                for a in PermissionManager.ACTIONS:
                    if r == "users" and a in ("delete", "suspend"):
                        continue
                    if r == "permissions" and a not in ("read",):
                        continue
                    perms.append({
                        "resource": r,
                        "action": a,
                        "name": f"{r}_{a}",
                        "description": f"{PermissionManager.RESOURCES[r]} - {PermissionManager.ACTIONS[a]}",
                    })
            return perms

        # Tier 2 — custom_role assigned permissions
        permissions = []
        if user.custom_role and user.custom_role.is_active:
            for p in user.custom_role.permissions:
                permissions.append({
                    "resource": p.resource,
                    "action": p.action,
                    "name": p.name,
                    "description": p.description,
                })
        return permissions

    @staticmethod
    def has_permission(user, resource: str, action: str) -> bool:
        if not user or not user.is_authenticated:
            return False

        tier = user.effective_tier

        # Tier 0 — absolute bypass
        if tier == 0:
            return True

        # Tier 1 — admin: all except restricted
        if tier == 1:
            if resource == "users" and action in ("delete", "suspend"):
                return False
            return True

        # Tier 2 — custom role: check assigned permissions
        if tier == 2:
            if user.custom_role and user.custom_role.is_active:
                for p in user.custom_role.permissions:
                    if p.resource == resource and p.action == action:
                        return True
            return False

        # Tier 3 — general: own content only
        if tier == 3:
            if resource == "news" and action in ("create", "read"):
                return True
            if resource == "images" and action in ("create", "read"):
                return True
            return False

        return False

    @staticmethod
    def has_any_permission(user, resource: str, actions: List[str]) -> bool:
        if not user or not user.is_authenticated:
            return False
        tier = user.effective_tier
        if tier == 0:
            return True
        if tier == 1:
            if resource == "users" and set(actions).issubset({"delete", "suspend"}):
                return False
            return True
        if tier == 2:
            if user.custom_role and user.custom_role.is_active:
                user_actions = {p.action for p in user.custom_role.permissions if p.resource == resource}
                return any(a in user_actions for a in actions)
            return False
        if tier == 3:
            allowed = {"news": {"read", "create"}, "images": {"read", "create"}}
            return resource in allowed and bool(set(actions) & allowed[resource])
        return False

    @staticmethod
    def has_all_permissions(user, resource: str, actions: List[str]) -> bool:
        if not user or not user.is_authenticated:
            return False
        tier = user.effective_tier
        if tier == 0:
            return True
        if tier == 1:
            if resource == "users" and set(actions).issubset({"delete", "suspend"}):
                return False
            return True
        if tier == 2:
            if user.custom_role and user.custom_role.is_active:
                user_actions = {p.action for p in user.custom_role.permissions if p.resource == resource}
                return all(a in user_actions for a in actions)
            return False
        if tier == 3:
            allowed = {"news": {"read", "create"}, "images": {"read", "create"}}
            return resource in allowed and set(actions).issubset(allowed[resource])
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
    return u and u.is_authenticated and u.effective_tier == 0


def is_admin(user=None) -> bool:
    u = _get_user(user)
    return u and u.is_authenticated and u.effective_tier == 1


def is_admin_tier(user=None) -> bool:
    u = _get_user(user)
    return u and u.is_authenticated and u.effective_tier <= 1


def has_custom_role(user=None, role_name: str = "") -> bool:
    u = _get_user(user)
    if not u or not u.is_authenticated or not u.custom_role or u.effective_tier != 2:
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
    tier = u.effective_tier
    if tier == 0:
        return "Superuser (Tier 0)"
    if tier == 1:
        return "Admin (Tier 1)"
    if tier == 2 and u.custom_role:
        return f"{u.custom_role.name} (Tier 2)"
    return "User (Tier 3)"


def get_user_permissions_summary(user=None) -> Dict[str, List[str]]:
    u = _get_user(user)
    if not u or not u.is_authenticated:
        return {}
    summary: Dict[str, List[str]] = {}
    for perm in PermissionManager.get_user_permissions(u):
        summary.setdefault(perm["resource"], []).append(perm["action"])
    return summary


# ═══════════════════════════════════════════════════════════════════════
# Generic resource ownership & query scoping
# ═══════════════════════════════════════════════════════════════════════

_OWNER_FIELDS = ("user_id", "author_id", "created_by")


def is_resource_owner(resource, user=None) -> bool:
    """Check if a user owns a given resource/model instance.
    
    Inspects common FK fields (user_id, author_id, created_by) on the
    resource and matches against user.id. Returns False for anonymous users.
    
    Usage:
        is_resource_owner(news_obj)          # checks current_user
        is_resource_owner(comment_obj, user)  # checks specific user
    """
    u = _get_user(user)
    if not u or not u.is_authenticated:
        return False
    for field in _OWNER_FIELDS:
        owner_id = getattr(resource, field, None)
        if owner_id is not None:
            return owner_id == u.id
    return False


def scope_query(model, query, user=None):
    """Scope a SQLAlchemy query to resources owned by the user (Tier 3).
    
    For Tier 0–2, returns query unmodified (no scope).
    For Tier 3, filters by the best-match owner field.
    
    Usage:
        query = scope_query(News, News.query)
        query = scope_query(Comment, Comment.query.filter_by(news_id=nid))
    """
    u = _get_user(user)
    if not u or not u.is_authenticated:
        return query.filter("1=0")  # no results for anonymous

    if u.effective_tier <= 1:
        return query  # admin/su — everything

    # Determine the best owner field for this model
    owner_field = None
    model_attrs = {c.name for c in model.__table__.columns}
    for field in _OWNER_FIELDS:
        if field in model_attrs:
            owner_field = field
            break

    if owner_field is None:
        return query  # no owner field found, return all

    return query.filter(getattr(model, owner_field) == u.id)


def assert_owner(resource, user=None) -> None:
    """Abort with 403 if user does not own the resource and is not Tier 0/1.
    
    Usage:
        assert_owner(news)
        # or in a route:
        assert_owner(comment)
    """
    from flask import abort
    u = _get_user(user)
    if not u or not u.is_authenticated:
        abort(401)
    if u.effective_tier <= 1:
        return  # Tier 0/1 always pass
    if not is_resource_owner(resource, u):
        abort(403)
