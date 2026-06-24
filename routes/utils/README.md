# Routes Utils

Helper utilities for routes.

# Routes Utils Package

This package contains utility modules for the LilyOpenCMS routes system, providing comprehensive permission and role management functionality.

## 📁 Structure

```
routes/utils/
├── __init__.py              # Package initialization and exports
├── permission_manager.py    # Permission checking and management
├── role_manager.py          # Role assignment and management
├── config_reader.py         # Configuration utilities
├── premium_content.py       # Premium content management
└── README.md               # This file
```

## 🔐 Permission Management System

### Overview
The permission management system provides granular access control based on user roles and custom permissions. It supports both basic role-based permissions and custom role permissions with specific resource/action combinations.

### Key Features
- **Resource-based permissions**: Define permissions for specific resources (users, news, images, etc.)
- **Action-based permissions**: Define specific actions (read, create, update, delete, etc.)
- **Custom role support**: Assign specific permissions to custom roles
- **Hierarchical permissions**: Superuser > Admin > Custom Roles > General
- **Template integration**: All permission functions available in Jinja2 templates

### Permission Resources
- `users` - User management
- `roles` - Role management
- `permissions` - Permission management
- `news` - News content
- `images` - Image management
- `videos` - Video management
- `categories` - Category management
- `settings` - System settings
- `ads` - Advertisement management
- `comments` - Comment moderation
- `ratings` - Rating management
- `analytics` - Analytics and performance
- `legal` - Legal documents
- `brand` - Brand management
- `seo` - SEO management
- `albums` - Album management

### Permission Actions
- `read` - View content
- `create` - Create content
- `update` - Edit content
- `delete` - Delete content
- `publish` - Publish/unpublish content
- `suspend` - Suspend/unsuspend users
- `moderate` - Moderate content
- `approve` - Approve content
- `reject` - Reject content
- `export` - Export data
- `import` - Import data
- `configure` - Configure settings

### Usage Examples

#### In Python Routes
```python
from routes.utils.permission_manager import can_manage_users, has_permission

# Check if user can manage users
if can_manage_users():
    # Allow user management operations
    pass

# Check specific permission
if has_permission('news', 'create'):
    # Allow news creation
    pass
```

#### In Jinja2 Templates
```html
{% if can_manage_users() %}
    <a href="{{ url_for('main.settings_users') }}">Manage Users</a>
{% endif %}

{% if has_permission('news', 'create') %}
    <a href="{{ url_for('main.create_news') }}">Create News</a>
{% endif %}
```

## 👥 Role Management System

### Overview
The role management system handles user role assignments, custom roles, and role-based operations with proper validation and hierarchy enforcement.

### Key Features
- **Role hierarchy**: Superuser > Admin > General
- **Custom role support**: Assign specific custom roles to users
- **Assignment validation**: Ensure proper permissions for role assignments
- **Role statistics**: Track role distribution across users
- **Template integration**: Role functions available in templates

### Role Hierarchy
1. **Superuser (100)**: Full system access, can assign any role
2. **Admin (80)**: Administrative access, can assign admin and general roles
3. **General (10)**: Basic user access, cannot assign roles

### Custom Roles
Custom roles are defined in `helper/init_permissions.py` and include:
- **Writer**: Can create and read content, upload images
- **Editor**: Can create, edit, and publish content
- **Subadmin**: Elevated role below Admin
- **Content Editor**: Can create, edit, and manage news content
- **Content Moderator**: Can review and moderate content
- **Media Manager**: Can manage all media content
- **User Manager**: Can manage users but not system settings
- **System Administrator**: Full system access except user deletion
- **Admin**: Can manage all content, media, and users

### Usage Examples

#### In Python Routes
```python
from routes.utils.role_manager import RoleManager, can_assign_roles

# Assign role to user
if can_assign_roles():
    RoleManager.assign_role_to_user(user, UserRole.ADMIN, current_user)

# Get user role info
role_info = RoleManager.get_user_role_info(user)
```

#### In Jinja2 Templates
```html
{% if can_assign_roles() %}
    <select name="role">
        {% for role in get_available_roles() %}
            <option value="{{ role.role.value }}">{{ role.name }}</option>
        {% endfor %}
    </select>
{% endif %}
```

## 🔧 Context Processors

The permission and role functions are automatically available in all Jinja2 templates through Flask context processors defined in `main.py`:

```python
@app.context_processor
def inject_permission_functions():
    """Inject permission checking functions into templates."""
    from routes.utils.permission_manager import (
        can_access_admin,
        can_manage_users,
        # ... other functions
    )
    
    return {
        'can_access_admin': can_access_admin,
        'can_manage_users': can_manage_users,
        # ... other functions
    }
```

## 📊 Available Functions

### Permission Functions
- `can_access_admin()` - Check admin dashboard access
- `can_manage_users()` - Check user management permissions
- `can_manage_content()` - Check content management permissions
- `can_manage_categories()` - Check category management permissions
- `can_manage_settings()` - Check settings management permissions
- `can_manage_roles()` - Check role management permissions
- `can_manage_ads()` - Check advertisement management permissions
- `can_moderate_comments()` - Check comment moderation permissions
- `can_manage_ratings()` - Check rating management permissions
- `can_access_analytics()` - Check analytics access permissions
- `can_manage_legal()` - Check legal document management permissions
- `can_manage_brand()` - Check brand management permissions
- `can_manage_seo()` - Check SEO management permissions
- `has_permission(resource, action)` - Check specific permission
- `has_any_permission(resource, actions)` - Check any of specified permissions
- `has_all_permissions(resource, actions)` - Check all specified permissions
- `get_user_role_display()` - Get user's role display name
- `get_user_permissions_summary()` - Get user's permissions summary
- `is_superuser()` - Check if user is superuser
- `is_admin()` - Check if user is admin
- `is_admin_tier()` - Check if user is admin tier
- `has_custom_role(role_name)` - Check if user has specific custom role

### Role Functions
- `can_assign_roles()` - Check if user can assign roles
- `can_assign_custom_roles()` - Check if user can assign custom roles
- `get_available_roles()` - Get available roles for current user
- `get_available_custom_roles()` - Get available custom roles for current user
- `get_role_statistics()` - Get role distribution statistics

## 🚀 Getting Started

1. **Initialize permissions and roles**:
   ```bash
   python helper/init_permissions.py
   ```

2. **Generate test users**:
   ```bash
   python helper/generate_user.py
   ```

3. **Use in routes**:
   ```python
   from routes.utils.permission_manager import can_manage_users
   
   @app.route('/admin/users')
   @login_required
   def admin_users():
       if not can_manage_users():
           abort(403)
       # ... rest of function
   ```

4. **Use in templates**:
   ```html
   {% if can_manage_users() %}
       <div class="user-management-section">
           <!-- User management content -->
       </div>
   {% endif %}
   ```

## 🔒 Security Considerations

- All permission checks are performed server-side
- Role assignments are validated against user permissions
- Custom roles can be restricted based on assigner permissions
- Permission functions are safe to use in templates
- Database transactions ensure data consistency

## 📝 Notes

- Permission functions automatically use `current_user` if no user is specified
- Role assignments are logged for audit purposes
- Custom roles can be activated/deactivated without affecting existing users
- The system supports both basic roles and custom roles simultaneously
- All functions are thread-safe and can be used in concurrent environments 