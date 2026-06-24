#!/usr/bin/env python3

"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Permission Management System for LilyOpenCMS

This module provides comprehensive permission checking and role management
for the admin interface and API endpoints.
"""

from flask import current_app
from flask_login import current_user
from models import UserRole, Permission, CustomRole
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


class PermissionManager:
    """Centralized permission management system."""
    
    # Permission resources
    RESOURCES = {
        'users': 'User management',
        'roles': 'Role management', 
        'permissions': 'Permission management',
        'news': 'News content',
        'images': 'Image management',
        'videos': 'Video management',
        'categories': 'Category management',
        'settings': 'System settings',
        'ads': 'Advertisement management',
        'comments': 'Comment moderation',
        'ratings': 'Rating management',
        'analytics': 'Analytics and performance',
        'legal': 'Legal documents',
        'brand': 'Brand management',
        'seo': 'SEO management',
        'albums': 'Album management'
    }
    
    # Permission actions
    ACTIONS = {
        'read': 'View content',
        'create': 'Create content',
        'update': 'Edit content', 
        'delete': 'Delete content',
        'publish': 'Publish/unpublish content',
        'suspend': 'Suspend/unsuspend users',
        'moderate': 'Moderate content',
        'approve': 'Approve content',
        'reject': 'Reject content',
        'export': 'Export data',
        'import': 'Import data',
        'configure': 'Configure settings'
    }
    
    @staticmethod
    def get_user_permissions(user) -> List[Dict]:
        """Get all permissions for a user."""
        if not user or not user.is_authenticated:
            return []
        
        permissions = []
        
        # Superuser has all permissions
        if user.is_owner():
            for resource in PermissionManager.RESOURCES.keys():
                for action in PermissionManager.ACTIONS.keys():
                    permissions.append({
                        'resource': resource,
                        'action': action,
                        'name': f"{resource}_{action}",
                        'description': f"{PermissionManager.RESOURCES[resource]} - {PermissionManager.ACTIONS[action]}"
                    })
            return permissions
        
        # Check custom role permissions
        if user.custom_role and user.custom_role.is_active:
            for permission in user.custom_role.permissions:
                permissions.append({
                    'resource': permission.resource,
                    'action': permission.action,
                    'name': permission.name,
                    'description': permission.description
                })
        
        # Add basic role permissions
        if user.role == UserRole.ADMIN:
            admin_permissions = [
                'users_read', 'users_create', 'users_update', 'users_suspend',
                'news_read', 'news_create', 'news_update', 'news_delete', 'news_publish',
                'images_read', 'images_create', 'images_update', 'images_delete',
                'videos_read', 'videos_create', 'videos_update', 'videos_delete',
                'categories_read', 'categories_create', 'categories_update', 'categories_delete',
                'settings_read', 'settings_update',
                'comments_read', 'comments_update', 'comments_delete',
                'ratings_read', 'ratings_update', 'ratings_delete',
                'legal_read', 'legal_update',
                'brand_read', 'brand_update',
                'seo_read', 'seo_update',
                'albums_read', 'albums_create', 'albums_update', 'albums_delete'
            ]
            
            for perm_name in admin_permissions:
                if '_' in perm_name:
                    resource, action = perm_name.split('_', 1)
                    permissions.append({
                        'resource': resource,
                        'action': action,
                        'name': perm_name,
                        'description': f"{PermissionManager.RESOURCES.get(resource, resource)} - {PermissionManager.ACTIONS.get(action, action)}"
                    })
        
        return permissions
    
    @staticmethod
    def has_permission(user, resource: str, action: str) -> bool:
        """Check if user has specific permission."""
        if not user or not user.is_authenticated:
            return False
        
        # Superuser has all permissions
        if user.is_owner():
            return True
        
        # Check custom role permissions
        if user.custom_role and user.custom_role.is_active:
            for permission in user.custom_role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        
        # Check basic role permissions
        if user.role == UserRole.ADMIN:
            admin_resources = ['users', 'news', 'images', 'videos', 'categories', 'settings', 
                             'comments', 'ratings', 'legal', 'brand', 'seo', 'albums']
            if resource in admin_resources:
                return True
        
        return False
    
    @staticmethod
    def has_any_permission(user, resource: str, actions: List[str]) -> bool:
        """Check if user has any of the specified permissions for a resource."""
        if not user or not user.is_authenticated:
            return False
        
        # Superuser has all permissions
        if user.is_owner():
            return True
        
        # Check custom role permissions
        if user.custom_role and user.custom_role.is_active:
            for permission in user.custom_role.permissions:
                if permission.resource == resource and permission.action in actions:
                    return True
        
        # Check basic role permissions
        if user.role == UserRole.ADMIN:
            admin_resources = ['users', 'news', 'images', 'videos', 'categories', 'settings', 
                             'comments', 'ratings', 'legal', 'brand', 'seo', 'albums']
            if resource in admin_resources:
                return True
        
        return False
    
    @staticmethod
    def has_all_permissions(user, resource: str, actions: List[str]) -> bool:
        """Check if user has all of the specified permissions for a resource."""
        if not user or not user.is_authenticated:
            return False
        
        # Superuser has all permissions
        if user.is_owner():
            return True
        
        # Check custom role permissions
        if user.custom_role and user.custom_role.is_active:
            user_permissions = {p.action for p in user.custom_role.permissions if p.resource == resource}
            return all(action in user_permissions for action in actions)
        
        # Check basic role permissions
        if user.role == UserRole.ADMIN:
            admin_resources = ['users', 'news', 'images', 'videos', 'categories', 'settings', 
                             'comments', 'ratings', 'legal', 'brand', 'seo', 'albums']
            if resource in admin_resources:
                return True
        
        return False


# Template helper functions
def can_access_admin(user=None) -> bool:
    """Check if user can access admin dashboard."""
    if user is None:
        user = current_user
    
    if not user or not user.is_authenticated:
        return False
    
    return user.is_admin_tier()


def can_manage_users(user=None) -> bool:
    """Check if user can manage users."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'users', ['read', 'create', 'update', 'delete', 'suspend'])


def can_manage_content(user=None) -> bool:
    """Check if user can manage content (news, images, videos)."""
    if user is None:
        user = current_user
    
    return (PermissionManager.has_any_permission(user, 'news', ['read', 'create', 'update', 'delete', 'publish']) or
            PermissionManager.has_any_permission(user, 'images', ['read', 'create', 'update', 'delete']) or
            PermissionManager.has_any_permission(user, 'videos', ['read', 'create', 'update', 'delete']) or
            PermissionManager.has_any_permission(user, 'albums', ['read', 'create', 'update', 'delete']))


def can_manage_categories(user=None) -> bool:
    """Check if user can manage categories."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'categories', ['read', 'create', 'update', 'delete'])


def can_manage_settings(user=None) -> bool:
    """Check if user can manage settings."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'settings', ['read', 'update'])


def can_manage_roles(user=None) -> bool:
    """Check if user can manage roles and permissions."""
    if user is None:
        user = current_user
    
    return (PermissionManager.has_any_permission(user, 'roles', ['read', 'create', 'update', 'delete']) or
            PermissionManager.has_any_permission(user, 'permissions', ['read', 'create', 'update', 'delete']))


def can_manage_ads(user=None) -> bool:
    """Check if user can manage advertisements."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'ads', ['read', 'create', 'update', 'delete'])


def can_moderate_comments(user=None) -> bool:
    """Check if user can moderate comments."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'comments', ['read', 'update', 'delete', 'moderate'])


def can_manage_ratings(user=None) -> bool:
    """Check if user can manage ratings."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'ratings', ['read', 'update', 'delete'])


def can_access_analytics(user=None) -> bool:
    """Check if user can access analytics."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'analytics', ['read'])


def can_manage_legal(user=None) -> bool:
    """Check if user can manage legal documents."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'legal', ['read', 'update'])


def can_manage_brand(user=None) -> bool:
    """Check if user can manage brand settings."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'brand', ['read', 'update'])


def can_manage_seo(user=None) -> bool:
    """Check if user can manage SEO settings."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'seo', ['read', 'update'])


def can_manage_news(user=None) -> bool:
    """Check if user can manage news content (create, read, update, delete)."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'news', ['read', 'create', 'update', 'delete', 'publish'])


def can_create_news(user=None) -> bool:
    """Check if user can create news articles."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'news', 'create')


def can_edit_news(user=None) -> bool:
    """Check if user can edit news articles."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'news', 'update')


def can_delete_news(user=None) -> bool:
    """Check if user can delete news articles."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'news', 'delete')


def can_publish_news(user=None) -> bool:
    """Check if user can publish/unpublish news articles."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'news', 'publish')


def can_manage_albums(user=None) -> bool:
    """Check if user can manage albums (create, read, update, delete)."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_any_permission(user, 'albums', ['read', 'create', 'update', 'delete', 'publish'])


def can_create_albums(user=None) -> bool:
    """Check if user can create albums."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'albums', 'create')


def can_edit_albums(user=None) -> bool:
    """Check if user can edit albums."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'albums', 'update')


def can_delete_albums(user=None) -> bool:
    """Check if user can delete albums."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'albums', 'delete')


def can_publish_albums(user=None) -> bool:
    """Check if user can publish/unpublish albums."""
    if user is None:
        user = current_user
    
    return PermissionManager.has_permission(user, 'albums', 'publish')


def can_access_content_creation(user=None) -> bool:
    """Check if user can access content creation features (news, albums, etc.)."""
    if user is None:
        user = current_user
    
    return (can_create_news(user) or can_create_albums(user) or 
            PermissionManager.has_any_permission(user, 'images', ['create']) or
            PermissionManager.has_any_permission(user, 'videos', ['create']))


def has_permission(user=None, resource: str = None, action: str = None) -> bool:
    """Check if user has specific permission."""
    if user is None:
        user = current_user
    
    if resource is None or action is None:
        return False
    
    return PermissionManager.has_permission(user, resource, action)


def has_any_permission(user=None, resource: str = None, actions: List[str] = None) -> bool:
    """Check if user has any of the specified permissions."""
    if user is None:
        user = current_user
    
    if resource is None or actions is None:
        return False
    
    return PermissionManager.has_any_permission(user, resource, actions)


def has_all_permissions(user=None, resource: str = None, actions: List[str] = None) -> bool:
    """Check if user has all of the specified permissions."""
    if user is None:
        user = current_user
    
    if resource is None or actions is None:
        return False
    
    return PermissionManager.has_all_permissions(user, resource, actions)


def get_user_role_display(user=None) -> str:
    """Get user's role display name."""
    if user is None:
        user = current_user
    
    if not user or not user.is_authenticated:
        return "Guest"
    
    if user.is_owner():
        return "Superuser"
    
    if user.custom_role:
        return f"{user.custom_role.name} ({user.role.value.title()})"
    
    return user.role.value.title()


def get_user_permissions_summary(user=None) -> Dict[str, List[str]]:
    """Get a summary of user's permissions by resource."""
    if user is None:
        user = current_user
    
    if not user or not user.is_authenticated:
        return {}
    
    permissions = PermissionManager.get_user_permissions(user)
    summary = {}
    
    for perm in permissions:
        resource = perm['resource']
        action = perm['action']
        
        if resource not in summary:
            summary[resource] = []
        
        summary[resource].append(action)
    
    return summary


# Role-based access control helpers
def is_superuser(user=None) -> bool:
    """Check if user is superuser."""
    if user is None:
        user = current_user
    
    return user and user.is_authenticated and user.is_owner()


def is_admin(user=None) -> bool:
    """Check if user is admin."""
    if user is None:
        user = current_user
    
    return user and user.is_authenticated and user.role == UserRole.ADMIN


def is_admin_tier(user=None) -> bool:
    """Check if user is admin tier (admin or custom role)."""
    if user is None:
        user = current_user
    
    return user and user.is_authenticated and user.is_admin_tier()


def has_custom_role(user=None, role_name: str = None) -> bool:
    """Check if user has specific custom role."""
    if user is None:
        user = current_user
    
    if not user or not user.is_authenticated or not user.custom_role:
        return False
    
    if role_name is None:
        return True
    
    return user.custom_role.name == role_name


# Export functions for templates
__all__ = [
    'can_access_admin',
    'can_manage_users', 
    'can_manage_content',
    'can_manage_categories',
    'can_manage_settings',
    'can_manage_roles',
    'can_manage_ads',
    'can_moderate_comments',
    'can_manage_ratings',
    'can_access_analytics',
    'can_manage_legal',
    'can_manage_brand',
    'can_manage_seo',
    'can_manage_news',
    'can_create_news',
    'can_edit_news',
    'can_delete_news',
    'can_publish_news',
    'can_manage_albums',
    'can_create_albums',
    'can_edit_albums',
    'can_delete_albums',
    'can_publish_albums',
    'can_access_content_creation',
    'has_permission',
    'has_any_permission',
    'has_all_permissions',
    'get_user_role_display',
    'get_user_permissions_summary',
    'is_superuser',
    'is_admin',
    'is_admin_tier',
    'has_custom_role',
    'PermissionManager'
]
