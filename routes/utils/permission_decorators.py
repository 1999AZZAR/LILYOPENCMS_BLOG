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
Permission-based Decorators for LilyOpenCMS

This module provides decorators that check specific permissions rather than
just admin tiers, allowing for more granular access control.
"""

from functools import wraps
from flask import redirect, url_for, flash, current_app, abort
from flask_login import current_user
from routes.utils.permission_manager import (
    can_create_news, can_edit_news, can_delete_news, can_publish_news,
    can_create_albums, can_edit_albums, can_delete_albums, can_publish_albums,
    can_manage_news, can_manage_albums, can_access_content_creation
)


def require_permission(permission_func, redirect_url=None, error_message=None):
    """
    Generic decorator that requires a specific permission function to return True.
    
    Args:
        permission_func: Function that takes a user and returns bool
        redirect_url: URL to redirect to if permission denied
        error_message: Message to flash if permission denied
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('main.login'))
            
            if not permission_func(current_user):
                if error_message:
                    flash(error_message, 'error')
                
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    # Default redirect based on user role
                    if current_user.is_admin_tier():
                        return redirect(url_for('main.settings_dashboard'))
                    else:
                        return redirect(url_for('user_profile.user_profile', username=current_user.username, tab='list'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# News-specific decorators
def require_news_create(f):
    """Require permission to create news articles."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_create_news(current_user):
            flash('Permission denied. You need create news permission.', 'error')
            return redirect(url_for('main.settings_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_news_edit(f):
    """Require permission to edit news articles."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_edit_news(current_user):
            flash('Permission denied. You need edit news permission.', 'error')
            return redirect(url_for('main.settings_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_news_delete(f):
    """Require permission to delete news articles."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_delete_news(current_user):
            flash('Permission denied. You need delete news permission.', 'error')
            return redirect(url_for('main.settings_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_news_publish(f):
    """Require permission to publish/unpublish news articles."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_publish_news(current_user):
            flash('Permission denied. You need publish news permission.', 'error')
            return redirect(url_for('main.settings_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_news_manage(f):
    """Require permission to manage news (any CRUD operation)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_manage_news(current_user):
            flash('Permission denied. You need news management permission.', 'error')
            return redirect(url_for('main.settings_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


# Album-specific decorators
def require_album_create(f):
    """Require permission to create albums."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_create_albums(current_user):
            flash('Permission denied. You need create album permission.', 'error')
            return redirect(url_for('user_profile.user_profile', username=current_user.username, tab='list'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_album_edit(f):
    """Require permission to edit albums."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_edit_albums(current_user):
            flash('Permission denied. You need edit album permission.', 'error')
            return redirect(url_for('user_profile.user_profile', username=current_user.username, tab='list'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_album_delete(f):
    """Require permission to delete albums."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_delete_albums(current_user):
            flash('Permission denied. You need delete album permission.', 'error')
            return redirect(url_for('user_profile.user_profile', username=current_user.username, tab='list'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_album_publish(f):
    """Require permission to publish/unpublish albums."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_publish_albums(current_user):
            flash('Permission denied. You need publish album permission.', 'error')
            return redirect(url_for('user_profile.user_profile', username=current_user.username, tab='list'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_album_manage(f):
    """Require permission to manage albums (any CRUD operation)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_manage_albums(current_user):
            flash('Permission denied. You need album management permission.', 'error')
            return redirect(url_for('user_profile.user_profile', username=current_user.username, tab='list'))
        
        return f(*args, **kwargs)
    return decorated_function


# Content creation decorator
def require_content_creation(f):
    """Require permission to create any type of content."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not can_access_content_creation(current_user):
            flash('Write access required. Request access to create content.', 'error')
            return redirect(url_for('user_profile.write_access_request'))
        
        return f(*args, **kwargs)
    return decorated_function


# API-specific decorators (return JSON errors instead of redirects)
def require_api_permission(permission_func, error_message=None):
    """
    Generic decorator for API endpoints that returns JSON errors instead of redirects.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return {'error': 'Authentication required'}, 401
            
            if not permission_func(current_user):
                error_msg = error_message or 'Permission denied'
                return {'error': error_msg}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_api_news_create(f):
    """API decorator for news creation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        
        if not can_create_news(current_user):
            return {'error': 'Permission denied. You need create news permission.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_news_edit(f):
    """API decorator for news editing."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        
        if not can_edit_news(current_user):
            return {'error': 'Permission denied. You need edit news permission.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_news_delete(f):
    """API decorator for news deletion."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        
        if not can_delete_news(current_user):
            return {'error': 'Permission denied. You need delete news permission.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_album_create(f):
    """API decorator for album creation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        
        if not can_create_albums(current_user):
            return {'error': 'Permission denied. You need create album permission.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_album_edit(f):
    """API decorator for album editing."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        
        if not can_edit_albums(current_user):
            return {'error': 'Permission denied. You need edit album permission.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function


def require_api_album_delete(f):
    """API decorator for album deletion."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        
        if not can_delete_albums(current_user):
            return {'error': 'Permission denied. You need delete album permission.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function
