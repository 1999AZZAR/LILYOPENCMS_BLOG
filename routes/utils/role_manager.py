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
Role Management System for LilyOpenCMS

This module provides comprehensive role management functionality including
role assignment, validation, and role-based operations.
"""

from flask import current_app
from flask_login import current_user
from models import UserRole, CustomRole, User, db
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


class RoleManager:
    """Centralized role management system."""
    
    # Default role hierarchy
    ROLE_HIERARCHY = {
        UserRole.SUPERUSER: 100,
        UserRole.ADMIN: 80,
        UserRole.GENERAL: 10
    }
    
    # Role display names
    ROLE_DISPLAY_NAMES = {
        UserRole.SUPERUSER: "Superuser",
        UserRole.ADMIN: "Admin", 
        UserRole.GENERAL: "General User"
    }
    
    # Role descriptions
    ROLE_DESCRIPTIONS = {
        UserRole.SUPERUSER: "Full system access with all permissions",
        UserRole.ADMIN: "Administrative access with most permissions",
        UserRole.GENERAL: "Basic user access with limited permissions"
    }
    
    @staticmethod
    def get_role_level(role: UserRole) -> int:
        """Get the hierarchical level of a role."""
        return RoleManager.ROLE_HIERARCHY.get(role, 0)
    
    @staticmethod
    def can_assign_role(assigner: User, target_role: UserRole) -> bool:
        """Check if a user can assign a specific role."""
        if not assigner or not assigner.is_authenticated:
            return False
        
        # Superuser can assign any role
        if assigner.is_owner():
            return True
        
        # Admin can assign admin and general roles
        if assigner.role == UserRole.ADMIN:
            return target_role in [UserRole.ADMIN, UserRole.GENERAL]
        
        return False
    
    @staticmethod
    def can_assign_custom_role(assigner: User, target_custom_role: CustomRole) -> bool:
        """Check if a user can assign a specific custom role."""
        if not assigner or not assigner.is_authenticated:
            return False
        
        # Superuser can assign any custom role
        if assigner.is_owner():
            return True
        
        # Admin can assign custom roles except superuser-specific ones
        if assigner.role == UserRole.ADMIN:
            # Define admin-restricted custom roles
            admin_restricted_roles = ['System Administrator']
            return target_custom_role.name not in admin_restricted_roles
        
        return False
    
    @staticmethod
    def assign_role_to_user(user: User, new_role: UserRole, assigned_by: User = None) -> bool:
        """Assign a role to a user."""
        try:
            if assigned_by and not RoleManager.can_assign_role(assigned_by, new_role):
                logger.warning(f"User {assigned_by.username} cannot assign role {new_role.value} to {user.username}")
                return False
            
            user.role = new_role
            db.session.commit()
            
            logger.info(f"Role {new_role.value} assigned to user {user.username} by {assigned_by.username if assigned_by else 'system'}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning role to user {user.username}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def assign_custom_role_to_user(user: User, custom_role: CustomRole, assigned_by: User = None) -> bool:
        """Assign a custom role to a user."""
        try:
            if assigned_by and not RoleManager.can_assign_custom_role(assigned_by, custom_role):
                logger.warning(f"User {assigned_by.username} cannot assign custom role {custom_role.name} to {user.username}")
                return False
            
            user.custom_role = custom_role
            db.session.commit()
            
            logger.info(f"Custom role {custom_role.name} assigned to user {user.username} by {assigned_by.username if assigned_by else 'system'}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning custom role to user {user.username}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def remove_custom_role_from_user(user: User, removed_by: User = None) -> bool:
        """Remove custom role from a user."""
        try:
            if not user.custom_role:
                return True  # No custom role to remove
            
            if removed_by and not RoleManager.can_assign_custom_role(removed_by, user.custom_role):
                logger.warning(f"User {removed_by.username} cannot remove custom role {user.custom_role.name} from {user.username}")
                return False
            
            custom_role_name = user.custom_role.name
            user.custom_role = None
            db.session.commit()
            
            logger.info(f"Custom role {custom_role_name} removed from user {user.username} by {removed_by.username if removed_by else 'system'}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing custom role from user {user.username}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_available_roles_for_user(assigner: User) -> List[Dict]:
        """Get list of roles that a user can assign."""
        available_roles = []
        
        if not assigner or not assigner.is_authenticated:
            return available_roles
        
        # Superuser can assign any role
        if assigner.is_owner():
            for role in UserRole:
                available_roles.append({
                    'role': role,
                    'name': RoleManager.ROLE_DISPLAY_NAMES.get(role, role.value.title()),
                    'description': RoleManager.ROLE_DESCRIPTIONS.get(role, ''),
                    'level': RoleManager.get_role_level(role)
                })
        
        # Admin can assign admin and general roles
        elif assigner.role == UserRole.ADMIN:
            for role in [UserRole.ADMIN, UserRole.GENERAL]:
                available_roles.append({
                    'role': role,
                    'name': RoleManager.ROLE_DISPLAY_NAMES.get(role, role.value.title()),
                    'description': RoleManager.ROLE_DESCRIPTIONS.get(role, ''),
                    'level': RoleManager.get_role_level(role)
                })
        
        return available_roles
    
    @staticmethod
    def get_available_custom_roles_for_user(assigner: User) -> List[Dict]:
        """Get list of custom roles that a user can assign."""
        available_roles = []
        
        if not assigner or not assigner.is_authenticated:
            return available_roles
        
        try:
            # Get all active custom roles
            custom_roles = CustomRole.query.filter_by(is_active=True).all()
            
            for custom_role in custom_roles:
                if RoleManager.can_assign_custom_role(assigner, custom_role):
                    available_roles.append({
                        'id': custom_role.id,
                        'name': custom_role.name,
                        'description': custom_role.description,
                        'permissions_count': len(custom_role.permissions)
                    })
            
        except Exception as e:
            logger.error(f"Error getting available custom roles: {e}")
        
        return available_roles
    
    @staticmethod
    def validate_role_assignment(user: User, new_role: UserRole, assigned_by: User = None) -> Dict:
        """Validate a role assignment."""
        result = {
            'valid': True,
            'message': '',
            'warnings': []
        }
        
        # Check if assigner has permission
        if assigned_by and not RoleManager.can_assign_role(assigned_by, new_role):
            result['valid'] = False
            result['message'] = f"You don't have permission to assign the {new_role.value} role"
            return result
        
        # Check role hierarchy
        if assigned_by:
            assigner_level = RoleManager.get_role_level(assigned_by.role)
            target_level = RoleManager.get_role_level(new_role)
            
            if target_level >= assigner_level:
                result['warnings'].append(f"Assigning a role with equal or higher privileges ({new_role.value})")
        
        # Check if user already has this role
        if user.role == new_role:
            result['warnings'].append(f"User already has the {new_role.value} role")
        
        return result
    
    @staticmethod
    def validate_custom_role_assignment(user: User, custom_role: CustomRole, assigned_by: User = None) -> Dict:
        """Validate a custom role assignment."""
        result = {
            'valid': True,
            'message': '',
            'warnings': []
        }
        
        # Check if assigner has permission
        if assigned_by and not RoleManager.can_assign_custom_role(assigned_by, custom_role):
            result['valid'] = False
            result['message'] = f"You don't have permission to assign the {custom_role.name} role"
            return result
        
        # Check if custom role is active
        if not custom_role.is_active:
            result['valid'] = False
            result['message'] = f"The {custom_role.name} role is not active"
            return result
        
        # Check if user already has this custom role
        if user.custom_role and user.custom_role.id == custom_role.id:
            result['warnings'].append(f"User already has the {custom_role.name} role")
        
        return result
    
    @staticmethod
    def get_user_role_info(user: User) -> Dict:
        """Get comprehensive role information for a user."""
        if not user:
            return {}
        
        role_info = {
            'basic_role': {
                'role': user.role,
                'name': RoleManager.ROLE_DISPLAY_NAMES.get(user.role, user.role.value.title()),
                'description': RoleManager.ROLE_DESCRIPTIONS.get(user.role, ''),
                'level': RoleManager.get_role_level(user.role)
            },
            'custom_role': None,
            'is_admin_tier': user.is_admin_tier(),
            'is_superuser': user.is_owner(),
            'can_assign_roles': False,
            'can_assign_custom_roles': False
        }
        
        # Add custom role info if exists
        if user.custom_role:
            role_info['custom_role'] = {
                'id': user.custom_role.id,
                'name': user.custom_role.name,
                'description': user.custom_role.description,
                'is_active': user.custom_role.is_active,
                'permissions_count': len(user.custom_role.permissions),
                'permissions': [
                    {
                        'name': p.name,
                        'description': p.description,
                        'resource': p.resource,
                        'action': p.action
                    } for p in user.custom_role.permissions
                ]
            }
        
        # Check assignment permissions
        role_info['can_assign_roles'] = user.is_owner() or user.role == UserRole.ADMIN
        role_info['can_assign_custom_roles'] = user.is_owner() or user.role == UserRole.ADMIN
        
        return role_info
    
    @staticmethod
    def get_role_statistics() -> Dict:
        """Get statistics about role distribution."""
        try:
            stats = {
                'total_users': User.query.count(),
                'role_distribution': {},
                'custom_role_distribution': {},
                'admin_tier_users': 0
            }
            
            # Count users by basic role
            for role in UserRole:
                count = User.query.filter_by(role=role).count()
                stats['role_distribution'][role.value] = count
            
            # Count users by custom role
            custom_roles = CustomRole.query.filter_by(is_active=True).all()
            for custom_role in custom_roles:
                count = User.query.filter_by(custom_role_id=custom_role.id).count()
                stats['custom_role_distribution'][custom_role.name] = count
            
            # Count admin tier users
            admin_tier_users = User.query.filter(
                (User.role == UserRole.SUPERUSER) | 
                (User.role == UserRole.ADMIN) |
                (User.custom_role_id.isnot(None))
            ).count()
            stats['admin_tier_users'] = admin_tier_users
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting role statistics: {e}")
            return {}


# Helper functions for templates and routes
def get_user_role_display(user: User = None) -> str:
    """Get user's role display name."""
    if user is None:
        user = current_user
    
    if not user or not user.is_authenticated:
        return "Guest"
    
    role_info = RoleManager.get_user_role_info(user)
    
    if role_info['is_superuser']:
        return "Superuser"
    
    if role_info['custom_role']:
        return f"{role_info['custom_role']['name']} ({role_info['basic_role']['name']})"
    
    return role_info['basic_role']['name']


def can_assign_roles(user: User = None) -> bool:
    """Check if user can assign roles."""
    if user is None:
        user = current_user
    
    return user and user.is_authenticated and (user.is_owner() or user.role == UserRole.ADMIN)


def can_assign_custom_roles(user: User = None) -> bool:
    """Check if user can assign custom roles."""
    if user is None:
        user = current_user
    
    return user and user.is_authenticated and (user.is_owner() or user.role == UserRole.ADMIN)


def get_available_roles(user: User = None) -> List[Dict]:
    """Get available roles for the current user."""
    if user is None:
        user = current_user
    
    return RoleManager.get_available_roles_for_user(user)


def get_available_custom_roles(user: User = None) -> List[Dict]:
    """Get available custom roles for the current user."""
    if user is None:
        user = current_user
    
    return RoleManager.get_available_custom_roles_for_user(user)


def get_role_statistics() -> Dict:
    """Get role statistics."""
    return RoleManager.get_role_statistics()


# Export functions
__all__ = [
    'RoleManager',
    'get_user_role_display',
    'can_assign_roles',
    'can_assign_custom_roles',
    'get_available_roles',
    'get_available_custom_roles',
    'get_role_statistics'
]
