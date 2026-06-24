"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Routes Utils Package

This package contains utility modules for the routes system.
"""

from .permission_manager import (
    can_access_admin,
    can_manage_users,
    can_manage_content,
    can_manage_categories,
    can_manage_settings,
    can_manage_roles,
    can_manage_ads,
    can_moderate_comments,
    can_manage_ratings,
    can_access_analytics,
    can_manage_legal,
    can_manage_brand,
    can_manage_seo,
    can_manage_news,
    can_create_news,
    can_edit_news,
    can_delete_news,
    can_publish_news,
    can_manage_albums,
    can_create_albums,
    can_edit_albums,
    can_delete_albums,
    can_publish_albums,
    can_access_content_creation,
    has_permission,
    has_any_permission,
    has_all_permissions,
    get_user_role_display,
    get_user_permissions_summary,
    is_superuser,
    is_admin,
    is_admin_tier,
    has_custom_role,
    PermissionManager
)

from .role_manager import (
    RoleManager,
    get_user_role_display as get_user_role_display_role,
    can_assign_roles,
    can_assign_custom_roles,
    get_available_roles,
    get_available_custom_roles,
    get_role_statistics
)

from .permission_decorators import (
    require_permission,
    require_news_create,
    require_news_edit,
    require_news_delete,
    require_news_publish,
    require_news_manage,
    require_album_create,
    require_album_edit,
    require_album_delete,
    require_album_publish,
    require_album_manage,
    require_content_creation,
    require_api_permission,
    require_api_news_create,
    require_api_news_edit,
    require_api_news_delete,
    require_api_album_create,
    require_api_album_edit,
    require_api_album_delete
)

__all__ = [
    # Permission management
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
    'PermissionManager',
    
    # Role management
    'RoleManager',
    'get_user_role_display_role',
    'can_assign_roles',
    'can_assign_custom_roles',
    'get_available_roles',
    'get_available_custom_roles',
    'get_role_statistics',
    
    # Permission decorators
    'require_permission',
    'require_news_create',
    'require_news_edit',
    'require_news_delete',
    'require_news_publish',
    'require_news_manage',
    'require_album_create',
    'require_album_edit',
    'require_album_delete',
    'require_album_publish',
    'require_album_manage',
    'require_content_creation',
    'require_api_permission',
    'require_api_news_create',
    'require_api_news_edit',
    'require_api_news_delete',
    'require_api_album_create',
    'require_api_album_edit',
    'require_api_album_delete'
]
