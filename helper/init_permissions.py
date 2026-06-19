#!/usr/bin/env python3
"""
Initialize default permissions and roles for the enhanced user management system.
"""

import sys
import os
# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

from models import Permission, CustomRole

def create_default_permissions():
    """Create default permissions for the system."""
    permissions = [
        # User management permissions
        {"name": "users_read", "description": "View user information", "resource": "users", "action": "read"},
        {"name": "users_create", "description": "Create new users", "resource": "users", "action": "create"},
        {"name": "users_update", "description": "Update user information", "resource": "users", "action": "update"},
        {"name": "users_delete", "description": "Delete users", "resource": "users", "action": "delete"},
        {"name": "users_suspend", "description": "Suspend/unsuspend users", "resource": "users", "action": "suspend"},
        
        # Role management permissions
        {"name": "roles_read", "description": "View roles", "resource": "roles", "action": "read"},
        {"name": "roles_create", "description": "Create new roles", "resource": "roles", "action": "create"},
        {"name": "roles_update", "description": "Update roles", "resource": "roles", "action": "update"},
        {"name": "roles_delete", "description": "Delete roles", "resource": "roles", "action": "delete"},
        
        # Permission management permissions
        {"name": "permissions_read", "description": "View permissions", "resource": "permissions", "action": "read"},
        {"name": "permissions_create", "description": "Create new permissions", "resource": "permissions", "action": "create"},
        {"name": "permissions_update", "description": "Update permissions", "resource": "permissions", "action": "update"},
        {"name": "permissions_delete", "description": "Delete permissions", "resource": "permissions", "action": "delete"},
        
        # News management permissions
        {"name": "news_read", "description": "View news articles", "resource": "news", "action": "read"},
        {"name": "news_create", "description": "Create news articles", "resource": "news", "action": "create"},
        {"name": "news_update", "description": "Update news articles", "resource": "news", "action": "update"},
        {"name": "news_delete", "description": "Delete news articles", "resource": "news", "action": "delete"},
        {"name": "news_publish", "description": "Publish/unpublish news", "resource": "news", "action": "publish"},
        
        # Image management permissions
        {"name": "images_read", "description": "View images", "resource": "images", "action": "read"},
        {"name": "images_create", "description": "Upload images", "resource": "images", "action": "create"},
        {"name": "images_update", "description": "Update image information", "resource": "images", "action": "update"},
        {"name": "images_delete", "description": "Delete images", "resource": "images", "action": "delete"},
        
        # Video management permissions
        {"name": "videos_read", "description": "View videos", "resource": "videos", "action": "read"},
        {"name": "videos_create", "description": "Add videos", "resource": "videos", "action": "create"},
        {"name": "videos_update", "description": "Update video information", "resource": "videos", "action": "update"},
        {"name": "videos_delete", "description": "Delete videos", "resource": "videos", "action": "delete"},
        
        # Settings management permissions
        {"name": "settings_read", "description": "View settings", "resource": "settings", "action": "read"},
        {"name": "settings_update", "description": "Update settings", "resource": "settings", "action": "update"},
        
        # Category management permissions
        {"name": "categories_read", "description": "View categories", "resource": "categories", "action": "read"},
        {"name": "categories_create", "description": "Create categories", "resource": "categories", "action": "create"},
        {"name": "categories_update", "description": "Update categories", "resource": "categories", "action": "update"},
        {"name": "categories_delete", "description": "Delete categories", "resource": "categories", "action": "delete"},
    ]
    
    created_permissions = []
    for perm_data in permissions:
        existing = Permission.query.filter_by(name=perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.session.add(permission)
            created_permissions.append(permission)
            print(f"Created permission: {perm_data['name']}")
        else:
            print(f"Permission already exists: {perm_data['name']}")
    
    db.session.commit()
    print(f"Created {len(created_permissions)} new permissions")
    return created_permissions

def create_default_roles():
    """Create default custom roles."""
    roles = [
        {
            "name": "Content Editor",
            "description": "Can create, edit, and manage news content",
            "permissions": [
                "news_read", "news_create", "news_update", "news_publish",
                "images_read", "images_create", "images_update",
                "categories_read"
            ]
        },
        {
            "name": "Content Moderator",
            "description": "Can review and moderate content",
            "permissions": [
                "news_read", "news_update", "news_publish",
                "images_read", "images_update",
                "categories_read"
            ]
        },
        {
            "name": "Media Manager",
            "description": "Can manage all media content",
            "permissions": [
                "news_read", "news_create", "news_update", "news_delete", "news_publish",
                "images_read", "images_create", "images_update", "images_delete",
                "videos_read", "videos_create", "videos_update", "videos_delete",
                "categories_read", "categories_create", "categories_update"
            ]
        },
        {
            "name": "User Manager",
            "description": "Can manage users but not system settings",
            "permissions": [
                "users_read", "users_create", "users_update",
                "roles_read"
            ]
        },
        {
            "name": "System Administrator",
            "description": "Full system access except user deletion",
            "permissions": [
                "users_read", "users_create", "users_update", "users_suspend",
                "roles_read", "roles_create", "roles_update", "roles_delete",
                "permissions_read", "permissions_create", "permissions_update", "permissions_delete",
                "news_read", "news_create", "news_update", "news_delete", "news_publish",
                "images_read", "images_create", "images_update", "images_delete",
                "videos_read", "videos_create", "videos_update", "videos_delete",
                "settings_read", "settings_update",
                "categories_read", "categories_create", "categories_update", "categories_delete"
            ]
        }
    ]
    
    created_roles = []
    for role_data in roles:
        existing = CustomRole.query.filter_by(name=role_data["name"]).first()
        if not existing:
            permissions = Permission.query.filter(Permission.name.in_(role_data["permissions"])).all()
            
            role = CustomRole(
                name=role_data["name"],
                description=role_data["description"],
                is_active=True
            )
            role.permissions = permissions
            
            db.session.add(role)
            created_roles.append(role)
            print(f"Created role: {role_data['name']} with {len(permissions)} permissions")
        else:
            print(f"Role already exists: {role_data['name']}")
    
    db.session.commit()
    print(f"Created {len(created_roles)} new roles")
    return created_roles

def main():
    """Main function to initialize permissions and roles."""
    with app.app_context():
        print("Initializing permissions and roles...")
        
        # Create permissions
        create_default_permissions()
        
        # Create roles
        create_default_roles()
        
        print("\nInitialization complete!")
        print(f"Total permissions: {Permission.query.count()}")
        print(f"Total roles: {CustomRole.query.count()}")

if __name__ == "__main__":
    main() 