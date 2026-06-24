"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from routes import main_blueprint
from .common_imports import *
from models import Permission, CustomRole, UserActivity
from datetime import datetime, timedelta, timezone


@main_blueprint.route("/api/permissions", methods=["GET"])
@login_required
def get_permissions():
    """Get all permissions."""
    if not current_user.has_permission("permissions", "read"):
        abort(403)
    
    permissions = Permission.query.all()
    return jsonify([permission.to_dict() for permission in permissions])


@main_blueprint.route("/api/permissions", methods=["POST"])
@login_required
def create_permission():
    """Create a new permission."""
    if not current_user.has_permission("permissions", "create"):
        abort(403)
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get("name") or not data.get("resource") or not data.get("action"):
        return jsonify({"error": "Name, resource, and action are required"}), 400
    
    # Check if permission already exists
    existing = Permission.query.filter_by(name=data["name"]).first()
    if existing:
        return jsonify({"error": "Permission with this name already exists"}), 400
    
    permission = Permission(
        name=data["name"],
        description=data.get("description"),
        resource=data["resource"],
        action=data["action"]
    )
    
    db.session.add(permission)
    db.session.commit()
    
    return jsonify(permission.to_dict()), 201


@main_blueprint.route("/api/permissions/<int:permission_id>", methods=["PUT"])
@login_required
def update_permission(permission_id):
    """Update a permission."""
    if not current_user.has_permission("permissions", "update"):
        abort(403)
    
    permission = Permission.query.get_or_404(permission_id)
    data = request.get_json()
    
    if "name" in data:
        permission.name = data["name"]
    if "description" in data:
        permission.description = data["description"]
    if "resource" in data:
        permission.resource = data["resource"]
    if "action" in data:
        permission.action = data["action"]
    
    db.session.commit()
    return jsonify(permission.to_dict())


@main_blueprint.route("/api/permissions/<int:permission_id>", methods=["DELETE"])
@login_required
def delete_permission(permission_id):
    """Delete a permission."""
    if not current_user.has_permission("permissions", "delete"):
        abort(403)
    
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    
    return jsonify({"message": "Permission deleted successfully"})


@main_blueprint.route("/api/roles", methods=["GET"])
@login_required
def get_roles():
    """Get all custom roles."""
    if not current_user.has_permission("roles", "read"):
        abort(403)
    
    roles = CustomRole.query.all()
    return jsonify([role.to_dict() for role in roles])


@main_blueprint.route("/api/roles/<int:role_id>", methods=["GET"])
@login_required
def get_role(role_id):
    """Get a specific custom role."""
    if not current_user.has_permission("roles", "read"):
        abort(403)
    
    role = CustomRole.query.get_or_404(role_id)
    return jsonify(role.to_dict())


@main_blueprint.route("/api/roles", methods=["POST"])
@login_required
def create_role():
    """Create a new custom role."""
    if not current_user.has_permission("roles", "create"):
        abort(403)
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "Role name is required"}), 400
    
    # Check if role already exists
    existing = CustomRole.query.filter_by(name=data["name"]).first()
    if existing:
        return jsonify({"error": "Role with this name already exists"}), 400
    
    role = CustomRole(
        name=data["name"],
        description=data.get("description"),
        is_active=data.get("is_active", True)
    )
    
    # Add permissions if provided
    if "permission_ids" in data:
        permissions = Permission.query.filter(Permission.id.in_(data["permission_ids"])).all()
        role.permissions = permissions
    
    db.session.add(role)
    db.session.commit()
    
    return jsonify(role.to_dict()), 201


@main_blueprint.route("/api/roles/<int:role_id>", methods=["PUT"])
@login_required
def update_role(role_id):
    """Update a custom role."""
    if not current_user.has_permission("roles", "update"):
        abort(403)
    
    role = CustomRole.query.get_or_404(role_id)
    data = request.get_json()
    
    if "name" in data:
        role.name = data["name"]
    if "description" in data:
        role.description = data["description"]
    if "is_active" in data:
        role.is_active = data["is_active"]
    
    # Update permissions if provided
    if "permission_ids" in data:
        permissions = Permission.query.filter(Permission.id.in_(data["permission_ids"])).all()
        role.permissions = permissions
    
    db.session.commit()
    return jsonify(role.to_dict())


@main_blueprint.route("/api/roles/<int:role_id>", methods=["DELETE"])
@login_required
def delete_role(role_id):
    """Delete a custom role."""
    if not current_user.has_permission("roles", "delete"):
        abort(403)
    
    role = CustomRole.query.get_or_404(role_id)
    
    # Check if any users are using this role
    if role.users:
        return jsonify({"error": "Cannot delete role that is assigned to users"}), 400
    
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({"message": "Role deleted successfully"})


@main_blueprint.route("/api/roles/<int:role_id>/permissions", methods=["GET"])
@login_required
def get_role_permissions(role_id):
    """Get permissions for a specific role."""
    if not current_user.has_permission("roles", "read"):
        abort(403)
    
    role = CustomRole.query.get_or_404(role_id)
    return jsonify([permission.to_dict() for permission in role.permissions])


@main_blueprint.route("/api/roles/<int:role_id>/permissions", methods=["PUT"])
@login_required
def update_role_permissions(role_id):
    """Update permissions for a specific role."""
    if not current_user.has_permission("roles", "update"):
        abort(403)
    
    role = CustomRole.query.get_or_404(role_id)
    data = request.get_json()
    
    if "permission_ids" in data:
        permissions = Permission.query.filter(Permission.id.in_(data["permission_ids"])).all()
        role.permissions = permissions
        db.session.commit()
    
    return jsonify(role.to_dict())


@main_blueprint.route("/api/roles/bulk/export", methods=["POST"])
@login_required
def bulk_export_roles():
    """Export roles and permissions data."""
    if not current_user.has_permission("roles", "read"):
        abort(403)
    
    data = request.get_json()
    export_format = data.get("format", "csv")
    
    if export_format != "csv":
        return jsonify({"error": "Only CSV format is supported"}), 400
    
    # Get all roles and permissions
    roles = CustomRole.query.all()
    permissions = Permission.query.all()
    
    # Create CSV data
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write roles header
    writer.writerow(["=== ROLES ==="])
    writer.writerow([
        "Role ID", "Role Name", "Description", "Is Active", 
        "Permission Count", "User Count", "Created At"
    ])
    
    for role in roles:
        writer.writerow([
            role.id, role.name, role.description or "",
            "Yes" if role.is_active else "No",
            len(list(role.permissions)), len(list(role.users)),
            role.created_at.isoformat() if role.created_at else ""
        ])
    
    # Write permissions header
    writer.writerow([])
    writer.writerow(["=== PERMISSIONS ==="])
    writer.writerow([
        "Permission ID", "Name", "Description", "Resource", 
        "Action", "Created At"
    ])
    
    for permission in permissions:
        writer.writerow([
            permission.id, permission.name, permission.description or "",
            permission.resource, permission.action,
            permission.created_at.isoformat() if permission.created_at else ""
        ])
    
    # Write role-permission relationships
    writer.writerow([])
    writer.writerow(["=== ROLE-PERMISSION RELATIONSHIPS ==="])
    writer.writerow(["Role ID", "Role Name", "Permission ID", "Permission Name"])
    
    for role in roles:
        for permission in role.permissions:
            writer.writerow([
                role.id, role.name, permission.id, permission.name
            ])
    
    output.seek(0)
    
    # Record activity
    current_user.record_activity(
        "bulk_export_roles",
        f"Exported {len(roles)} roles and {len(permissions)} permissions",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=roles_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@main_blueprint.route("/api/users/<int:user_id>/role", methods=["PUT"])
@login_required
def assign_role_to_user(user_id):
    """Assign a custom role to a user."""
    if not current_user.has_permission("users", "update"):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if "role_id" in data:
        if data["role_id"] is None:
            user.custom_role = None
        else:
            role = CustomRole.query.get_or_404(data["role_id"])
            user.custom_role = role
    
    db.session.commit()
    return jsonify(user.to_dict())


@main_blueprint.route("/api/users/<int:user_id>/activities", methods=["GET"])
@login_required
def get_user_activities(user_id):
    """Get user activity history."""
    if not current_user.has_permission("users", "read"):
        abort(403)
    
    User.query.get_or_404(user_id)
    activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.created_at.desc()).limit(50).all()
    
    return jsonify([activity.to_dict() for activity in activities])


@main_blueprint.route("/api/users/<int:user_id>/suspend", methods=["POST"])
@login_required
def suspend_user(user_id):
    """Suspend a user."""
    if not current_user.has_permission("users", "suspend"):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Cannot suspend superusers unless you are a superuser
    if user.role == UserRole.SUPERUSER and not current_user.is_owner():
        return jsonify({"error": "Cannot suspend superusers"}), 403
    
    # Cannot suspend yourself
    if user.id == current_user.id:
        return jsonify({"error": "Cannot suspend yourself"}), 400
    
    user.is_suspended = True
    user.suspension_reason = data.get("reason")
    
    # Set suspension duration if provided
    if data.get("duration_days"):
        user.suspension_until = datetime.now(timezone.utc) + timedelta(days=data["duration_days"])
    
    db.session.commit()
    
    # Record activity
    current_user.record_activity(
        "suspend_user",
        f"Suspended user {user.username}",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return jsonify({"message": "User suspended successfully"})


@main_blueprint.route("/api/users/<int:user_id>/unsuspend", methods=["POST"])
@login_required
def unsuspend_user(user_id):
    """Unsuspend a user."""
    if not current_user.has_permission("users", "suspend"):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    user.is_suspended = False
    user.suspension_reason = None
    user.suspension_until = None
    
    db.session.commit()
    
    # Record activity
    current_user.record_activity(
        "unsuspend_user",
        f"Unsuspended user {user.username}",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return jsonify({"message": "User unsuspended successfully"})
