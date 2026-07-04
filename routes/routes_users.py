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
@main_blueprint.route('/settings/editor-writer')
@login_required
def editor_writer_management():
    if not (current_user.effective_tier <= 1 or (current_user.custom_role and current_user.custom_role.name.lower() in ['subadmin', 'editor'])):
        abort(403)
    # Provide basic data; frontend will fetch full lists via API
    return render_template('admin/settings/editor_writer_management.html', current_user=current_user)

@main_blueprint.route('/api/editor-writer/writers', methods=['GET'])
@login_required
def list_writers():
    """List writers that can be assigned (GENERAL users + custom role 'writer')."""
    q = request.args.get('q', '').strip()
    # Base: all general users
    query = User.query.filter(User.is_active == True)
    # Simple filter: by role general or custom role writer
    query = query.filter(or_(User.role == UserRole.GENERAL, and_(User.custom_role_id.isnot(None), CustomRole.name.ilike('%writer%'))))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.username.ilike(like), User.email.ilike(like)))
    users = query.order_by(User.username.asc()).limit(50).all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])

@main_blueprint.route('/api/editor-writer/editors', methods=['GET'])
@login_required
def list_editors():
    """List editors that can have writers assigned (ADMINs or custom role 'editor')."""
    q = request.args.get('q', '').strip()
    query = User.query.filter(User.is_active == True)
    query = query.filter(or_(User.role == UserRole.ADMIN, and_(User.custom_role_id.isnot(None), CustomRole.name.ilike('%editor%'))))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.username.ilike(like), User.email.ilike(like)))
    users = query.order_by(User.username.asc()).limit(50).all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])

@main_blueprint.route('/api/editor-writer/<int:editor_id>/assign', methods=['POST'])
@login_required
def assign_writers(editor_id):
    if not (current_user.effective_tier <= 1 or (current_user.custom_role and current_user.custom_role.name.lower() == 'subadmin') or current_user.id == editor_id):
        abort(403)
    editor = db.session.get(User, editor_id)
    if not editor:
        abort(404)
    data = request.get_json() or {}
    writer_ids = data.get('writer_ids', [])
    if not isinstance(writer_ids, list):
        return jsonify({"error": "writer_ids must be a list"}), 400
    # Replace assignments atomically
    try:
        editor.assigned_writers = []
        if writer_ids:
            writers = User.query.filter(User.id.in_(writer_ids)).all()
            for w in writers:
                editor.assigned_writers.append(w)
        db.session.commit()
        return jsonify({"message": "Assignments updated", "writer_ids": [w.id for w in editor.assigned_writers]}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_blueprint.route('/api/editor-writer/<int:editor_id>/list', methods=['GET'])
@login_required
def list_editor_assignments(editor_id):
    editor = db.session.get(User, editor_id)
    if not editor:
        abort(404)
    return jsonify({"editor_id": editor.id, "writers": [{"id": w.id, "username": w.username, "email": w.email} for w in editor.assigned_writers]})
from models import User, News, Image, YouTubeVideo, UserActivity, CustomRole, Album
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func
from werkzeug.security import generate_password_hash


def _transfer_and_delete_user(target_user: User, transfer_user_id: int) -> None:
    """Transfer owned content away from target_user and delete the user safely.

    This function now uses the comprehensive user deletion helper to ensure
    complete cleanup while transferring ownership of content.
    """
    from routes.utils.content_deletion_helper import delete_user_completely

    # Use the comprehensive deletion function with ownership transfer
    deletion_stats = delete_user_completely(target_user.id, transfer_user_id=transfer_user_id)

    current_app.logger.info(
        f"User {target_user.username} (ID: {target_user.id}) deleted with content transferred to user ID {transfer_user_id}. "
        f"Deletion stats: {deletion_stats}"
    )

@main_blueprint.route("/api/users", methods=["GET"])
@login_required
def get_users():
    # Only superusers and admins can access this endpoint
    if current_user.effective_tier > 1:
        abort(403)

    # Get query parameters for filtering
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    verification_filter = request.args.get('verification', '')
    write_access_filter = request.args.get('write_access', '')
    
    # Build query
    query = User.query
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    if role_filter:
        # Support multiple roles separated by comma
        if ',' in role_filter:
            roles = [role.strip() for role in role_filter.split(',')]
            role_conditions = []
            for role in roles:
                try:
                    role_conditions.append(User.role == UserRole(role))
                except ValueError:
                    # Skip invalid role values
                    continue
            if role_conditions:
                query = query.filter(or_(*role_conditions))
        else:
            try:
                query = query.filter(User.role == UserRole(role_filter))
            except ValueError:
                # Skip invalid role values
                pass
    
    if status_filter:
        if status_filter == 'active':
            query = query.filter(User.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(User.is_active == False)
        elif status_filter == 'suspended':
            query = query.filter(User.is_suspended == True)
    
    if verification_filter:
        if verification_filter == 'verified':
            query = query.filter(User.verified == True)
        elif verification_filter == 'unverified':
            query = query.filter(User.verified == False)
    
    if write_access_filter:
        if write_access_filter.lower() in ['true', '1', 'yes']:
            query = query.filter(User.write_access == True)
        elif write_access_filter.lower() in ['false', '0', 'no']:
            query = query.filter(User.write_access == False)
    
    # Pagination
    per_page = 20
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return jsonify({
        "users": [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "is_premium": user.is_premium,
            "verified": user.verified,
            "is_suspended": user.is_suspended,
            "suspension_reason": user.suspension_reason,
            "suspension_until": user.suspension_until.isoformat() if user.suspension_until else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "custom_role": {
                "id": user.custom_role.id,
                "name": user.custom_role.name
            } if user.custom_role else None,
            "write_access": user.write_access,
            "has_premium_access": user.has_premium_access,
            "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None
        } for user in users],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    })

@main_blueprint.route("/api/users/check-username", methods=["GET"])
@login_required
def check_username_availability():
    """Check if a username is available."""
    try:
        # Only superusers and admins can check usernames
        if current_user.effective_tier > 1:
            abort(403)
        
        username = request.args.get('username', '').strip()
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        available = existing_user is None
        
        return jsonify({
            "available": available,
            "username": username,
            "message": "Username available" if available else "Username already exists"
        })
        
    except Exception as e:
        print(f"Error checking username: {e}")
        return jsonify({"error": "Failed to check username"}), 500


@main_blueprint.route("/api/users/check-email", methods=["GET"])
@login_required
def check_email_availability():
    """Check if an email is available."""
    try:
        # Only superusers and admins can check emails
        if current_user.effective_tier > 1:
            abort(403)
        
        email = request.args.get('email', '').strip()
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        available = existing_user is None
        
        return jsonify({
            "available": available,
            "email": email,
            "message": "Email available" if available else "Email already exists"
        })
        
    except Exception as e:
        print(f"Error checking email: {e}")
        return jsonify({"error": "Failed to check email"}), 500


@main_blueprint.route("/api/users", methods=["POST"])
@login_required
def create_user():
    """Create a new user with enhanced features."""
    try:
        # Only superusers and admins can create users
        if current_user.effective_tier > 1:
            abort(403)
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            field_value = data.get(field)
            if not field_value:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        
        # Check if email already exists
        if data.get('email') and User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        
        # Validate role
        try:
            role_value = data['role']
            role = UserRole(role_value)
        except ValueError as e:
            return jsonify({"error": f"Invalid role value: {role_value}"}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data.get('email'),
            password_hash=generate_password_hash(data['password'], method='pbkdf2:sha256'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            bio=data.get('bio'),
            role=role,
            is_active=data.get('is_active', True),
            verified=data.get('verified', True),
            is_premium=data.get('is_premium', False),
            has_premium_access=data.get('is_premium', False)
        )

        # Optional birthdate (ISO date string YYYY-MM-DD)
        birthdate_str = data.get('birthdate')
        if birthdate_str:
            try:
                # Accept date-only (YYYY-MM-DD); ignore time if provided
                if 'T' in birthdate_str:
                    birthdate_str = birthdate_str.split('T', 1)[0]
                user.birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid birthdate format, expected YYYY-MM-DD"}), 400
        
        # Set premium expiration if premium
        if user.is_premium:
            duration = data.get('premium_duration', 365)
            if duration == 'lifetime':
                user.premium_expires_at = None
            else:
                user.premium_expires_at = datetime.now(timezone.utc) + timedelta(days=int(duration))
        
        # Assign custom role if specified
        custom_role_id = data.get('custom_role_id')
        if custom_role_id:
            custom_role = CustomRole.query.get(custom_role_id)
            if custom_role:
                user.custom_role = custom_role
        
        db.session.add(user)
        db.session.commit()

        # Send welcome email if requested
        if data.get('send_welcome_email', False) and user.email:
            try:
                # Initialize email service for API context
                from routes.utils.email_service import email_service
                from main import app
                email_service.init_app(app)

                # Send welcome email
                subject = f"Welcome to {current_app.config.get('BRAND_NAME', 'LilyOpenCMS')}!"
                body = f"""
Hello {user.first_name or user.username},

Welcome to {current_app.config.get('BRAND_NAME', 'LilyOpenCMS')}!

Your account has been created successfully. You can now log in using your credentials.

Best regards,
{current_app.config.get('BRAND_NAME', 'LilyOpenCMS')} Team
                """.strip()

                success = email_service.send_email(
                    to=user.email,
                    subject=subject,
                    body=body
                )

                if success:
                    current_app.logger.info(f"✅ Welcome email sent to {user.email}")
                else:
                    current_app.logger.warning(f"⚠️ Failed to send welcome email to {user.email}")

            except Exception as e:
                current_app.logger.error(f"❌ Error sending welcome email: {e}")
                # Don't fail user creation if email fails

        return jsonify({
            "success": True,
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "verified": user.verified,
                "is_premium": user.is_premium,
                "birthdate": user.birthdate.isoformat() if user.birthdate else None,
                "age": user.get_age()
            }
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        error_msg = str(e)
        if "UNIQUE constraint failed: user.email" in error_msg:
            return jsonify({"error": "Email already exists"}), 400
        elif "UNIQUE constraint failed: user.username" in error_msg:
            return jsonify({"error": "Username already exists"}), 400
        else:
            return jsonify({"error": "User with this information already exists"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500


@main_blueprint.route("/api/users/<int:user_id>/verify", methods=["PATCH"])
@login_required
def toggle_user_verification(user_id):
    # Only users with permission can toggle verification
    if current_user.effective_tier > 1:
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Cannot modify superusers unless you are a superuser
    if user.effective_tier == 0 and not current_user.is_owner():
        abort(403)
    
    # Cannot modify yourself
    if user.id == current_user.id:
        abort(403)
    
    data = request.get_json()
    user.verified = data["verified"]
    db.session.commit()
    
    # Record activity (disabled - method not available)
    pass
    
    return jsonify({"message": "Verification status updated successfully"})


@main_blueprint.route("/api/users/<int:user_id>/status", methods=["PATCH"])
@login_required
def toggle_user_status(user_id):
    # Only users with permission can toggle user status
    if current_user.effective_tier > 1:
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Cannot modify superusers unless you are a superuser
    if user.effective_tier == 0 and not current_user.is_owner():
        abort(403)
    
    # Cannot modify yourself
    if user.id == current_user.id:
        abort(403)
    
    data = request.get_json()
    user.is_active = data["is_active"]
    db.session.commit()
    
    # Record activity (disabled - method not available)
    pass
    
    return jsonify({"message": "User status updated successfully"})


@main_blueprint.route("/api/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    # Only users with permission can delete users
    if current_user.effective_tier > 1:
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Cannot delete superusers unless you are a superuser
    if user.effective_tier == 0 and not current_user.is_owner():
        abort(403)
    
    # Cannot delete yourself
    if user.id == current_user.id:
        abort(403)
    
    # Record activity before deletion (disabled - method not available)
    pass
    
    # Reassign owned content to the deleter (or optional transfer target)
    try:
        transfer_to = request.args.get('transfer_to', type=int)
        transfer_user_id = transfer_to if transfer_to else current_user.id
        if transfer_user_id == user.id:
            return jsonify({"error": "transfer_to cannot be the same as the deleted user"}), 400
        transfer_user = User.query.get(transfer_user_id)
        if not transfer_user:
            return jsonify({"error": "transfer target user not found"}), 404

        _transfer_and_delete_user(user, transfer_user_id)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user {user_id}: {e}")
        return jsonify({"error": "Failed to delete user"}), 500
    return jsonify({"message": "User deleted successfully", "transferred_to": transfer_user_id})


@main_blueprint.route("/api/user/role", methods=["GET"])
@login_required
def get_user_role():
    """
    Returns the role of the currently logged-in user.
    """
    return jsonify(
        {
            "role": current_user.role.value  # Assuming role is an Enum
        }
    )

@main_blueprint.route("/api/user/request-account-deletion", methods=["POST"])
@login_required
def request_account_deletion():
    """
    Request account deletion - sets user to inactive and marks for admin approval.
    Only general users can request deletion.
    """
    if current_user.effective_tier <= 2:
        return jsonify({"error": "Only general users can request account deletion"}), 403
    
    try:
        # Set user to inactive and mark for deletion
        current_user.is_active = False
        current_user.deletion_requested_at = datetime.utcnow()
        current_user.deletion_requested = True
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Account deletion request submitted successfully. Your account has been deactivated and is pending admin approval."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error requesting account deletion for user {current_user.id}: {e}")
        return jsonify({"error": "Failed to submit deletion request"}), 500

@main_blueprint.route("/api/users/deletion-requests", methods=["GET"])
@login_required
def get_deletion_requests():
    """
    Get all pending account deletion requests (admin only).
    """
    if current_user.effective_tier > 1:
        abort(403)
    
    try:
        # Get users with pending deletion requests
        deletion_requests = User.query.filter_by(
            deletion_requested=True,
            is_active=False
        ).order_by(User.deletion_requested_at.desc()).all()
        
        requests_data = []
        for user in deletion_requests:
            requests_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "deletion_requested_at": user.deletion_requested_at.isoformat() if user.deletion_requested_at else None,
                "role": user.role.value,
                "custom_role": user.custom_role.name if user.custom_role else None
            })
        
        return jsonify({
            "success": True,
            "deletion_requests": requests_data,
            "total": len(requests_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching deletion requests: {e}")
        return jsonify({"error": "Failed to fetch deletion requests"}), 500

@main_blueprint.route("/api/users/deletion-requests/<int:request_id>/approve", methods=["POST"])
@login_required
def approve_user_deletion_request(request_id):
    """
    Approve a user deletion request (admin only).
    """
    if current_user.effective_tier > 1:
        abort(403)

    try:
        # Get the user with the deletion request
        user = User.query.filter_by(
            id=request_id,
            deletion_requested=True,
            is_active=False
        ).first()

        if not user:
            return jsonify({"error": "User deletion request not found"}), 404

        # Check if already moderated
        if user.deletion_request_moderated:
            return jsonify({"error": "This deletion request has already been processed"}), 400

        data = request.get_json() or {}
        note = data.get('note', '')  # Optional admin note

        from datetime import datetime, timezone

        # Update moderation fields
        user.deletion_request_moderated = True
        user.deletion_request_moderated_at = datetime.now(timezone.utc)
        user.deletion_request_moderated_by = current_user.id
        user.deletion_request_moderation_note = note
        user.deletion_request_approved = True

        # Actually delete the user account
        db.session.delete(user)
        db.session.commit()

        # Log activity
        if hasattr(current_user, 'record_activity'):
            current_user.record_activity(
                activity_type='USER_DELETION_APPROVED',
                description=f'Approved deletion of user account "{user.username}" ({user.email})',
                context_data={
                    'deleted_user_id': user.id,
                    'deleted_username': user.username,
                    'deleted_email': user.email,
                    'moderation_note': note
                }
            )

        return jsonify({
            "success": True,
            "message": "User account deletion approved and user permanently deleted"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving user deletion request {request_id}: {e}")
        return jsonify({"error": "Failed to approve user deletion request"}), 500

@main_blueprint.route("/api/users/<int:user_id>/approve-deletion", methods=["POST"])
@login_required
def approve_account_deletion(user_id):
    """
    Approve account deletion request and permanently delete the user (admin only).
    """
    if current_user.effective_tier > 1:
        abort(403)
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Verify this is a pending deletion request
        if not user.deletion_requested or user.is_active:
            return jsonify({"error": "User does not have a pending deletion request"}), 400
        
        # Cannot delete superusers unless you are a superuser
        if user.effective_tier == 0 and not current_user.is_owner():
            return jsonify({"error": "Cannot delete superuser"}), 403
        
        # Cannot delete yourself
        if user.id == current_user.id:
            return jsonify({"error": "Cannot delete your own account"}), 403
        
        # Permanently delete the user with safe transfer (to current admin)
        _transfer_and_delete_user(user, current_user.id)

        # Send account deletion confirmation email
        try:
            email_service.send_account_deletion_confirmation(user)
        except Exception as e:
            current_app.logger.warning(f"Failed to send account deletion confirmation to {user.username}: {e}")

        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Account deletion approved and user '{user.username}' has been permanently deleted."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving account deletion for user {user_id}: {e}")
        return jsonify({"error": "Failed to approve account deletion"}), 500

@main_blueprint.route("/api/users/<int:user_id>/reject-deletion", methods=["POST"])
@login_required
def reject_account_deletion(user_id):
    """
    Reject account deletion request and reactivate the user (admin only).
    """
    if current_user.effective_tier > 1:
        abort(403)
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Verify this is a pending deletion request
        if not user.deletion_requested or user.is_active:
            return jsonify({"error": "User does not have a pending deletion request"}), 400
        
        # Reactivate user and clear deletion request
        user.is_active = True
        user.deletion_requested = False
        user.deletion_requested_at = None
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Account deletion request rejected. User '{user.username}' has been reactivated."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting account deletion for user {user_id}: {e}")
        return jsonify({"error": "Failed to reject account deletion"}), 500


@main_blueprint.route("/api/users/deletion-requests/cancel", methods=["POST"])
@login_required
def cancel_account_deletion_request():
    """
    Cancel a user's own account deletion request.
    """
    try:
        # Get current user
        user = User.query.get_or_404(current_user.id)

        # Check if user has a pending deletion request
        if not user.deletion_requested or user.deletion_request_moderated:
            return jsonify({"error": "No pending deletion request found"}), 400

        # Cancel the deletion request
        user.deletion_requested = False
        user.deletion_requested_at = None
        user.deletion_request_moderated = False
        user.deletion_request_moderated_at = None
        user.deletion_request_moderated_by = None
        user.deletion_request_moderation_note = None
        user.deletion_request_approved = None

        db.session.commit()

        current_app.logger.info(f"User {user.username} cancelled their account deletion request")
        return jsonify({"success": True, "message": "Account deletion request cancelled"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling account deletion request for user {current_user.id}: {e}")
        return jsonify({"error": "Failed to cancel account deletion request"}), 500


@main_blueprint.route("/api/users/<int:user_id>", methods=["PUT", "PATCH"])
@login_required
def update_user(user_id):
    """Update user information with enhanced error handling."""
    try:
        # Only users with permission can update users
        if current_user.effective_tier > 1:
            return jsonify({"success": False, "error": "Access denied", "code": "FORBIDDEN"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided", "code": "MISSING_DATA"}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Cannot modify superusers unless you are a superuser
        if user.effective_tier == 0 and not current_user.is_owner():
            return jsonify({"success": False, "error": "Cannot modify superuser accounts", "code": "FORBIDDEN"}), 403
        
        # Cannot modify yourself
        if user.id == current_user.id:
            return jsonify({"success": False, "error": "Cannot modify your own account through this API", "code": "FORBIDDEN"}), 403
        
        updated = False
        changes = []
        
        # Update basic fields
        fields = ["username", "email", "first_name", "last_name", "bio", "social_links"]
        for f in fields:
            if f in data:
                new_val = data[f] if data[f] else None
                old_val = getattr(user, f)
                if old_val != new_val:
                    setattr(user, f, new_val)
                    changes.append(f)
                    updated = True

        if "birthdate" in data:
            bd = data["birthdate"]
            new_bd = None
            if bd:
                try:
                    if 'T' in bd:
                        bd = bd.split('T', 1)[0]
                    new_bd = datetime.strptime(bd, "%Y-%m-%d").date()
                except ValueError:
                    return jsonify({"success": False, "error": "Invalid birthdate format", "code": "INVALID_FORMAT"}), 400
            
            if user.birthdate != new_bd:
                user.birthdate = new_bd
                changes.append("birthdate")
                updated = True
        
        # Update role (only superusers can change roles)
        if "role" in data and current_user.is_owner():
            try:
                new_role = UserRole(data["role"])
                if user.role != new_role:
                    user.role = new_role
                    changes.append("role")
                    updated = True
            except ValueError:
                return jsonify({"success": False, "error": "Invalid role value", "code": "INVALID_VALUE"}), 400
        
        # Update status fields
        bool_fields = ["is_active", "verified", "is_suspended", "is_premium"]
        for f in bool_fields:
            if f in data:
                new_val = bool(data[f])
                old_val = getattr(user, f)
                if old_val != new_val:
                    setattr(user, f, new_val)
                    changes.append(f)
                    updated = True

        if "suspension_reason" in data:
            if user.suspension_reason != data["suspension_reason"]:
                user.suspension_reason = data["suspension_reason"]
                changes.append("suspension_reason")
                updated = True

        if "suspension_until" in data:
            new_until = None
            if data["suspension_until"]:
                try:
                    new_until = datetime.fromisoformat(data["suspension_until"].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"success": False, "error": "Invalid date format for suspension_until", "code": "INVALID_FORMAT"}), 400
            
            if user.suspension_until != new_until:
                user.suspension_until = new_until
                changes.append("suspension_until")
                updated = True
        
        # Update custom role (only superusers can change roles)
        if "custom_role_id" in data and current_user.is_owner():
            if data["custom_role_id"]:
                custom_role = CustomRole.query.get(data["custom_role_id"])
                if custom_role:
                    if user.custom_role_id != custom_role.id:
                        user.custom_role = custom_role
                        changes.append("custom_role")
                        updated = True
                else:
                    return jsonify({"success": False, "error": "Custom role not found", "code": "NOT_FOUND"}), 404
            elif user.custom_role_id is not None:
                user.custom_role = None
                changes.append("custom_role")
                updated = True
        
        if not updated:
            return jsonify({"success": True, "message": "No changes detected", "user": {"id": user.id, "username": user.username}}), 200

        db.session.commit()
        
        # Audit Log
        try:
            from models import UserActivity
            audit = UserActivity(
                user_id=current_user.id,
                activity_type='UPDATE_USER',
                description=f"Updated user {user.username} (ID: {user_id}): {', '.join(changes)}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")
        
        return jsonify({"success": True, "message": "User updated successfully", "user": {"id": user.id, "username": user.username}}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({"success": False, "error": "Database error", "code": "DATABASE_ERROR"}), 500


@main_blueprint.route("/api/settings/verified-users", methods=["GET"])
@login_required
def settings_verified_users():
    if not current_user.is_owner() and current_user.effective_tier != 1:
        abort(403)

    verified_users = User.query.filter_by(verified=True).all()
    return jsonify(
        [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "is_active": user.is_active,
            }
            for user in verified_users
        ]
    )


@main_blueprint.route("/api/users/bulk/status", methods=["POST"])
@login_required
def bulk_update_user_status():
    """Bulk update user status (activate/deactivate) with enhanced error handling."""
    try:
        if current_user.effective_tier > 1:
            abort(403)
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_ids = data.get("user_ids", [])
        is_active = data.get("is_active", True)
        
        if not user_ids:
            return jsonify({"error": "No user IDs provided"}), 400
        
        if not isinstance(user_ids, list):
            return jsonify({"error": "user_ids must be a list"}), 400
        
        # Get users to update
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if not users:
            return jsonify({"error": "No valid users found"}), 404
        
        # Filter out users that cannot be modified
        updatable_users = []
        skipped_users = []
        
        for user in users:
            # Cannot modify superusers unless you are a superuser
            if user.effective_tier == 0 and not current_user.is_owner():
                skipped_users.append({"id": user.id, "reason": "Cannot modify superuser"})
                continue
            # Cannot modify yourself
            if user.id == current_user.id:
                skipped_users.append({"id": user.id, "reason": "Cannot modify self"})
                continue
            updatable_users.append(user)
        
        # Update user status
        for user in updatable_users:
            user.is_active = bool(is_active)
        
        db.session.commit()
        
        # Record activity (disabled - method not available)
        pass
        
        return jsonify({
            "message": f"Updated {len(updatable_users)} users",
            "updated_count": len(updatable_users),
            "total_requested": len(user_ids),
            "skipped_users": skipped_users
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk status update: {str(e)}")
        return jsonify({"error": "Failed to update user status"}), 500


@main_blueprint.route("/api/users/bulk/role", methods=["POST"])
@login_required
def bulk_assign_role():
    """Bulk assign custom role to users."""
    if current_user.effective_tier > 1:
        abort(403)
    
    data = request.get_json()
    user_ids = data.get("user_ids", [])
    role_id = data.get("role_id")
    
    if not user_ids:
        return jsonify({"error": "No user IDs provided"}), 400
    
    # Get role if specified
    role = None
    if role_id is not None:
        role = CustomRole.query.get_or_404(role_id)
    
    # Get users to update
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    # Filter out users that cannot be modified
    updatable_users = []
    for user in users:
        # Cannot modify superusers unless you are a superuser
        if user.effective_tier == 0 and not current_user.is_owner():
            continue
        # Cannot modify yourself
        if user.id == current_user.id:
            continue
        updatable_users.append(user)
    
    # Update user roles
    for user in updatable_users:
        user.custom_role = role
    
    db.session.commit()
    
    # Record activity (disabled for now)
    pass
    
    return jsonify({
        "message": f"Assigned role to {len(updatable_users)} users",
        "updated_count": len(updatable_users),
        "total_requested": len(user_ids),
        "role_name": role_name
    })


@main_blueprint.route("/api/users/bulk/verify", methods=["POST"])
@login_required
def bulk_verify_users():
    """Bulk verify/unverify users with enhanced error handling."""
    try:
        if current_user.effective_tier > 1:
            abort(403)
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_ids = data.get("user_ids", [])
        verified = data.get("verified", True)
        
        if not user_ids:
            return jsonify({"error": "No user IDs provided"}), 400
        
        if not isinstance(user_ids, list):
            return jsonify({"error": "user_ids must be a list"}), 400
        
        # Get users to update
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if not users:
            return jsonify({"error": "No valid users found"}), 404
        
        # Filter out users that cannot be modified
        updatable_users = []
        skipped_users = []
        
        for user in users:
            # Cannot modify superusers unless you are a superuser
            if user.effective_tier == 0 and not current_user.is_owner():
                skipped_users.append({"id": user.id, "reason": "Cannot modify superuser"})
                continue
            # Cannot modify yourself
            if user.id == current_user.id:
                skipped_users.append({"id": user.id, "reason": "Cannot modify self"})
                continue
            updatable_users.append(user)
        
        # Update user verification status
        for user in updatable_users:
            user.verified = bool(verified)
        
        db.session.commit()
        
        # Record activity (disabled - method not available)
        pass
        
        return jsonify({
            "message": f"{'Verified' if verified else 'Unverified'} {len(updatable_users)} users",
            "updated_count": len(updatable_users),
            "total_requested": len(user_ids),
            "skipped_users": skipped_users
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk verification: {str(e)}")
        return jsonify({"error": "Failed to update user verification"}), 500


@main_blueprint.route("/api/users/bulk/suspend", methods=["POST"])
@login_required
def bulk_suspend_users():
    """Bulk suspend/unsuspend users with enhanced error handling."""
    try:
        if current_user.effective_tier > 1:
            abort(403)
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_ids = data.get("user_ids", [])
        suspend = data.get("suspend", True)
        reason = data.get("reason", "Bulk suspension")
        duration_days = data.get("duration_days")
        
        if not user_ids:
            return jsonify({"error": "No user IDs provided"}), 400
        
        if not isinstance(user_ids, list):
            return jsonify({"error": "user_ids must be a list"}), 400
        
        # Get users to update
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if not users:
            return jsonify({"error": "No valid users found"}), 404
        
        # Filter out users that cannot be modified
        updatable_users = []
        skipped_users = []
        
        for user in users:
            # Cannot suspend superusers unless you are a superuser
            if user.effective_tier == 0 and not current_user.is_owner():
                skipped_users.append({"id": user.id, "reason": "Cannot suspend superuser"})
                continue
            # Cannot suspend yourself
            if user.id == current_user.id:
                skipped_users.append({"id": user.id, "reason": "Cannot suspend self"})
                continue
            updatable_users.append(user)
        
        # Update user suspension status
        for user in updatable_users:
            user.is_suspended = bool(suspend)
            if suspend:
                user.suspension_reason = reason
                if duration_days:
                    try:
                        duration_days = int(duration_days)
                        user.suspension_until = datetime.now(timezone.utc) + timedelta(days=duration_days)
                    except (ValueError, TypeError):
                        return jsonify({"error": "Invalid duration_days value"}), 400
            else:
                user.suspension_reason = None
                user.suspension_until = None

        # Send email notifications for suspended users
        if suspend and updatable_users:
            # Initialize email service
            from routes.utils.email_service import email_service
            email_service.init_app(current_app._get_current_object())

            for user in updatable_users:
                if user.email:  # Only send if user has email
                    try:
                        email_service.send_suspension_notification(
                            user=user,
                            reason=reason,
                            duration_days=duration_days if duration_days else None
                        )
                    except Exception as e:
                        current_app.logger.warning(f"Failed to send suspension notification to {user.username}: {e}")

        db.session.commit()
        
        # Record activity (disabled - method not available)
        pass
        
        return jsonify({
            "message": f"{'Suspended' if suspend else 'Unsuspended'} {len(updatable_users)} users",
            "updated_count": len(updatable_users),
            "total_requested": len(user_ids),
            "skipped_users": skipped_users
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk suspension: {str(e)}")
        return jsonify({"error": "Failed to update user suspension"}), 500


@main_blueprint.route("/api/users/bulk/delete", methods=["POST"])
@login_required
def bulk_delete_users():
    """Bulk delete users with enhanced error handling."""
    try:
        if current_user.effective_tier > 1:
            abort(403)
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_ids = data.get("user_ids", [])
        
        if not user_ids:
            return jsonify({"error": "No user IDs provided"}), 400
        
        if not isinstance(user_ids, list):
            return jsonify({"error": "user_ids must be a list"}), 400
        
        # Get users to delete
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if not users:
            return jsonify({"error": "No valid users found"}), 404
        
        # Filter out users that cannot be deleted
        deletable_users = []
        skipped_users = []
        
        for user in users:
            # Cannot delete superusers unless you are a superuser
            if user.effective_tier == 0 and not current_user.is_owner():
                skipped_users.append({"id": user.id, "reason": "Cannot delete superuser"})
                continue
            # Cannot delete yourself
            if user.id == current_user.id:
                skipped_users.append({"id": user.id, "reason": "Cannot delete self"})
                continue
            deletable_users.append(user)
        
        # Record activity before deletion (disabled - method not available)
        pass
        
        # Delete users with safe transfer to current admin
        for user in deletable_users:
            _transfer_and_delete_user(user, current_user.id)
        
        db.session.commit()
        
        return jsonify({
            "message": f"Deleted {len(deletable_users)} users",
            "deleted_count": len(deletable_users),
            "total_requested": len(user_ids),
            "skipped_users": skipped_users
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk delete: {str(e)}")
        return jsonify({"error": "Failed to delete users"}), 500


@main_blueprint.route("/api/users/bulk/export", methods=["POST"])
@login_required
def bulk_export_users():
    """Export all user data."""
    if current_user.effective_tier > 1:
        abort(403)
    
    data = request.get_json()
    export_format = data.get("format", "csv")
    
    # Get all users (can be filtered by search, role, status, etc.)
    users = User.query.all()
    
    if export_format == "json":
        user_data = [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "is_premium": user.is_premium,
            "verified": user.verified,
            "is_suspended": user.is_suspended,
            "suspension_reason": user.suspension_reason,
            "suspension_until": user.suspension_until.isoformat() if user.suspension_until else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "custom_role": {
                "id": user.custom_role.id,
                "name": user.custom_role.name
            } if user.custom_role else None,
            "has_premium_access": user.has_premium_access,
            "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None,
            "birthdate": user.birthdate.isoformat() if user.birthdate else None,
            "age": user.get_age()
        } for user in users]
        return jsonify({
            "users": user_data,
            "count": len(users),
            "exported_at": datetime.now(timezone.utc).isoformat()
        })
    elif export_format == "csv":
        # Create CSV data
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Username", "Email", "First Name", "Last Name", "Bio",
            "Role", "Custom Role", "Is Active", "Is Suspended", "Verified", 
            "Premium", "Login Count", "Last Login", "Created At", "Suspension Reason",
            "Birthdate", "Age"
        ])
        
        # Write user data
        for user in users:
            writer.writerow([
                user.id, user.username, user.email or "",
                user.first_name or "", user.last_name or "", user.bio or "",
                user.role.value, user.custom_role.name if user.custom_role else "",
                "Yes" if user.is_active else "No",
                "Yes" if user.is_suspended else "No",
                "Yes" if user.verified else "No",
                "Yes" if user.is_premium else "No",
                user.login_count, user.last_login.isoformat() if user.last_login else "",
                user.created_at.isoformat(),
                user.suspension_reason or "",
                user.birthdate.isoformat() if user.birthdate else "",
                user.get_age()
            ])
        
        output.seek(0)
        
        # Record activity (disabled - method not available)
        pass
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    else:
        return jsonify({"error": "Unsupported export format"}), 400


@main_blueprint.route("/api/users/<int:user_id>/performance", methods=["GET"])
@login_required
def get_user_performance(user_id):
    """Get user performance metrics."""
    if current_user.effective_tier > 1:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Calculate performance metrics
    from sqlalchemy import func
    
    # Get date range (last 30 days by default)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    # News created in the period
    news_count = News.query.filter(
        News.user_id == user_id,
        News.created_at >= start_date,
        News.created_at <= end_date
    ).count()
    
    # Total news created
    total_news = News.query.filter_by(user_id=user_id).count()
    
    # News read count (sum of all news read counts)
    total_reads = db.session.query(func.sum(News.read_count)).filter_by(user_id=user_id).scalar() or 0
    
    # Images uploaded in the period
    images_count = Image.query.filter(
        Image.user_id == user_id,
        Image.created_at >= start_date,
        Image.created_at <= end_date
    ).count()
    
    # Total images uploaded
    total_images = Image.query.filter_by(user_id=user_id).count()
    
    # Videos uploaded in the period
    videos_count = db.session.query(YouTubeVideo).filter(
        YouTubeVideo.user_id == user_id,
        YouTubeVideo.created_at >= start_date,
        YouTubeVideo.created_at <= end_date
    ).count()
    
    # Total videos uploaded
    total_videos = db.session.query(YouTubeVideo).filter_by(user_id=user_id).count()
    
    # Login frequency (last 7 days)
    recent_logins = UserActivity.query.filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_type == "login",
        UserActivity.created_at >= end_date - timedelta(days=7)
    ).count()
    
    # Activity breakdown by type
    activity_breakdown = db.session.query(
        UserActivity.activity_type,
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= start_date,
        UserActivity.created_at <= end_date
    ).group_by(UserActivity.activity_type).all()
    
    # Calculate engagement score (weighted combination of activities)
    engagement_score = (
        news_count * 10 +  # News creation is high value
        images_count * 5 +  # Image uploads are medium value
        videos_count * 8 +  # Video uploads are high value
        recent_logins * 2   # Login frequency shows engagement
    )
    
    # Get recent activities
    recent_activities = UserActivity.query.filter_by(user_id=user_id).order_by(
        UserActivity.created_at.desc()
    ).limit(10).all()
    
    performance_data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": user.bio,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "is_premium": user.is_premium,
            "verified": user.verified,
            "is_suspended": user.is_suspended,
            "suspension_reason": user.suspension_reason,
            "suspension_until": user.suspension_until.isoformat() if user.suspension_until else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "custom_role": {
                "id": user.custom_role.id,
                "name": user.custom_role.name
            } if user.custom_role else None,
            "has_premium_access": user.has_premium_access,
            "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": 30
        },
        "metrics": {
            "news": {
                "period_count": news_count,
                "total_count": total_news,
                "total_reads": total_reads,
                "avg_reads_per_news": total_reads / total_news if total_news > 0 else 0
            },
            "images": {
                "period_count": images_count,
                "total_count": total_images
            },
            "videos": {
                "period_count": videos_count,
                "total_count": total_videos
            },
            "engagement": {
                "recent_logins": recent_logins,
                "engagement_score": engagement_score,
                "activity_breakdown": [
                    {"activity_type": activity_type, "count": count}
                    for activity_type, count in activity_breakdown
                ]
            }
        },
        "recent_activities": [{
            "id": activity.id,
            "user_id": activity.user_id,
            "activity_type": activity.activity_type,
            "description": activity.description,
            "ip_address": activity.ip_address,
            "user_agent": activity.user_agent,
            "created_at": activity.created_at.isoformat() if activity.created_at else None
        } for activity in recent_activities]
    }
    
    return jsonify(performance_data)


@main_blueprint.route("/api/users/performance/leaderboard", methods=["GET"])
@login_required
def get_performance_leaderboard():
    """Get user performance leaderboard."""
    if current_user.effective_tier > 1:
        abort(403)
    
    # Get date range (last 30 days by default)
    from sqlalchemy import func
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    # Optimized: Use aggregate queries instead of N+1 queries
    from sqlalchemy import func

    # Get news counts per user
    news_counts = db.session.query(
        News.user_id,
        func.count(News.id).label('news_count')
    ).filter(
        News.created_at >= start_date,
        News.created_at <= end_date
    ).group_by(News.user_id).all()
    news_count_dict = {row.user_id: row.news_count for row in news_counts}

    # Get image counts per user
    image_counts = db.session.query(
        Image.user_id,
        func.count(Image.id).label('images_count')
    ).filter(
        Image.created_at >= start_date,
        Image.created_at <= end_date
    ).group_by(Image.user_id).all()
    image_count_dict = {row.user_id: row.images_count for row in image_counts}

    # Get video counts per user
    video_counts = db.session.query(
        YouTubeVideo.user_id,
        func.count(YouTubeVideo.id).label('videos_count')
    ).filter(
        YouTubeVideo.created_at >= start_date,
        YouTubeVideo.created_at <= end_date
    ).group_by(YouTubeVideo.user_id).all()
    video_count_dict = {row.user_id: row.videos_count for row in video_counts}

    # Get recent login counts per user
    login_counts = db.session.query(
        UserActivity.user_id,
        func.count(UserActivity.id).label('login_count')
    ).filter(
        UserActivity.activity_type == "login",
        UserActivity.created_at >= end_date - timedelta(days=7)
    ).group_by(UserActivity.user_id).all()
    login_count_dict = {row.user_id: row.login_count for row in login_counts}

    # Get all users
    users = User.query.filter_by(is_active=True).all()

    leaderboard_data = []

    for user in users:
        # Get metrics from pre-calculated dictionaries
        news_count = news_count_dict.get(user.id, 0)
        images_count = image_count_dict.get(user.id, 0)
        videos_count = video_count_dict.get(user.id, 0)
        recent_logins = login_count_dict.get(user.id, 0)
        
        # Calculate engagement score
        engagement_score = (
            news_count * 10 +
            images_count * 5 +
            videos_count * 8 +
            recent_logins * 2
        )
        
        leaderboard_data.append({
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name(),
                "role": user.role.value,
                "custom_role": user.custom_role.name if user.custom_role else None
            },
            "metrics": {
                "news_count": news_count,
                "images_count": images_count,
                "videos_count": videos_count,
                "recent_logins": recent_logins,
                "engagement_score": engagement_score
            }
        })
    
    # Sort by engagement score (descending)
    leaderboard_data.sort(key=lambda x: x["metrics"]["engagement_score"], reverse=True)
    
    return jsonify({
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": 30
        },
        "leaderboard": leaderboard_data
    })


@main_blueprint.route("/api/users/performance/report", methods=["GET"])
@login_required
def get_performance_report():
    """Get performance report for all users."""
    if current_user.effective_tier > 1:
        abort(403)
    
    # Get date range from query parameters
    days = request.args.get("days", 30, type=int)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get all users
    users = User.query.all()
    
    # Calculate metrics for each user
    user_performance = []
    total_users = len(users)
    active_users = 0
    total_activities = 0
    total_news = 0
    total_images = 0
    total_videos = 0
    
    for user in users:
        # Check if user is active (has activity in the period)
        user_activity = UserActivity.query.filter(
            UserActivity.user_id == user.id,
            UserActivity.created_at >= start_date,
            UserActivity.created_at <= end_date
        ).count()
        
        if user_activity > 0:
            active_users += 1
        
        # Get user's content in the period
        news_count = News.query.filter(
            News.user_id == user.id,
            News.created_at >= start_date,
            News.created_at <= end_date
        ).count()
        
        images_count = Image.query.filter(
            Image.user_id == user.id,
            Image.created_at >= start_date,
            Image.created_at <= end_date
        ).count()
        
        videos_count = YouTubeVideo.query.filter(
            YouTubeVideo.user_id == user.id,
            YouTubeVideo.created_at >= start_date,
            YouTubeVideo.created_at <= end_date
        ).count()
        
        # Calculate engagement score
        total_reads = db.session.query(func.sum(News.read_count)).filter(
            News.user_id == user.id,
            News.created_at >= start_date,
            News.created_at <= end_date
        ).scalar() or 0
        
        engagement_score = (total_reads + user_activity) / max(days, 1)
        
        user_performance.append({
            "user_id": user.id,
            "username": user.username,
            "activities": user_activity,
            "news_created": news_count,
            "images_uploaded": images_count,
            "videos_uploaded": videos_count,
            "total_reads": total_reads,
            "engagement_score": round(engagement_score, 2)
        })
        
        total_activities += user_activity
        total_news += news_count
        total_images += images_count
        total_videos += videos_count
    
    # Sort by engagement score
    user_performance.sort(key=lambda x: x["engagement_score"], reverse=True)
    
    return jsonify({
        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "total_activities": total_activities,
            "total_news": total_news,
            "total_images": total_images,
            "total_videos": total_videos
        },
        "users": user_performance
    })


@main_blueprint.route("/api/users/performance/report/export", methods=["POST"])
@login_required
def export_performance_report():
    """Export performance report as CSV."""
    if current_user.effective_tier > 1:
        abort(403)
    
    data = request.get_json()
    days = data.get("days", 30)
    export_format = data.get("format", "csv")
    
    if export_format != "csv":
        return jsonify({"error": "Only CSV format is supported"}), 400
    
    # Get performance data
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    users = User.query.all()
    
    # Create CSV data
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Rank", "Username", "Activities", "News Created", "Images Uploaded", 
        "Videos Uploaded", "Total Reads", "Engagement Score", "Last Activity"
    ])
    
    user_performance = []
    for user in users:
        # Calculate user metrics
        user_activity = UserActivity.query.filter(
            UserActivity.user_id == user.id,
            UserActivity.created_at >= start_date,
            UserActivity.created_at <= end_date
        ).count()
        
        news_count = News.query.filter(
            News.user_id == user.id,
            News.created_at >= start_date,
            News.created_at <= end_date
        ).count()
        
        images_count = Image.query.filter(
            Image.user_id == user.id,
            Image.created_at >= start_date,
            Image.created_at <= end_date
        ).count()
        
        videos_count = YouTubeVideo.query.filter(
            YouTubeVideo.user_id == user.id,
            YouTubeVideo.created_at >= start_date,
            YouTubeVideo.created_at <= end_date
        ).count()
        
        total_reads = db.session.query(func.sum(News.read_count)).filter(
            News.user_id == user.id,
            News.created_at >= start_date,
            News.created_at <= end_date
        ).scalar() or 0
        
        engagement_score = (total_reads + user_activity) / max(days, 1)
        
        # Get last activity
        last_activity = UserActivity.query.filter_by(user_id=user.id).order_by(UserActivity.created_at.desc()).first()
        last_activity_date = last_activity.created_at.isoformat() if last_activity else ""
        
        user_performance.append({
            "username": user.username,
            "activities": user_activity,
            "news_created": news_count,
            "images_uploaded": images_count,
            "videos_uploaded": videos_count,
            "total_reads": total_reads,
            "engagement_score": round(engagement_score, 2),
            "last_activity": last_activity_date
        })
    
    # Sort by engagement score and add rank
    user_performance.sort(key=lambda x: x["engagement_score"], reverse=True)
    
    for rank, user_data in enumerate(user_performance, 1):
        writer.writerow([
            rank, user_data["username"], user_data["activities"],
            user_data["news_created"], user_data["images_uploaded"],
            user_data["videos_uploaded"], user_data["total_reads"],
            user_data["engagement_score"], user_data["last_activity"]
        ])
    
    output.seek(0)
    
    # Record activity (disabled - method not available)
    pass
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=performance_report_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@main_blueprint.route("/api/users/<int:user_id>/performance/export", methods=["GET"])
@login_required
def export_user_performance(user_id):
    """Export user performance data as CSV."""
    if current_user.effective_tier > 1:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Get date range
    from sqlalchemy import func
    import csv
    import io
    
    days = request.args.get("days", 30, type=int)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get user activities
    activities = UserActivity.query.filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= start_date,
        UserActivity.created_at <= end_date
    ).order_by(UserActivity.created_at.desc()).all()
    
    # Get user content
    news_articles = News.query.filter(
        News.user_id == user_id,
        News.created_at >= start_date,
        News.created_at <= end_date
    ).all()
    
    images = Image.query.filter(
        Image.user_id == user_id,
        Image.created_at >= start_date,
        Image.created_at <= end_date
    ).all()
    
    videos = db.session.query(YouTubeVideo).filter(
        YouTubeVideo.user_id == user_id,
        YouTubeVideo.created_at >= start_date,
        YouTubeVideo.created_at <= end_date
    ).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "User Performance Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    ])
    writer.writerow([])
    
    # User info
    writer.writerow(["User Information"])
    writer.writerow(["Username", user.username])
    writer.writerow(["Full Name", user.get_full_name()])
    writer.writerow(["Role", user.role.value])
    writer.writerow(["Custom Role", user.custom_role.name if user.custom_role else "None"])
    writer.writerow(["Last Login", user.last_login.isoformat() if user.last_login else "Never"])
    writer.writerow(["Login Count", user.login_count])
    writer.writerow([])
    
    # Summary
    writer.writerow(["Activity Summary"])
    writer.writerow(["News Articles", len(news_articles)])
    writer.writerow(["Images", len(images)])
    writer.writerow(["Videos", len(videos)])
    writer.writerow(["Total Activities", len(activities)])
    writer.writerow([])
    
    # Activities
    writer.writerow(["Recent Activities"])
    writer.writerow(["Date", "Activity Type", "Description", "IP Address"])
    for activity in activities[:50]:  # Limit to 50 most recent
        writer.writerow([
            activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            activity.activity_type,
            activity.description or "",
            activity.ip_address or ""
        ])
    
    output.seek(0)
    
    # Record export activity (disabled - method not available)
    pass
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=performance_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@main_blueprint.route("/api/users/<int:user_id>/details", methods=["GET"])
@login_required
def get_user_details(user_id):
    """Get detailed user information."""
    if current_user.effective_tier > 1:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "role": user.role.value if user.role else None,
        "custom_role": user.custom_role.name if user.custom_role else None,
        "is_active": user.is_active,
        "verified": user.verified,
        "is_premium": user.is_premium,
        "has_premium_access": user.has_premium_access,
        "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None,
        "is_suspended": user.is_suspended,
        "suspension_reason": user.suspension_reason,
        "suspension_until": user.suspension_until.isoformat() if user.suspension_until else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "login_count": user.login_count,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "birthdate": user.birthdate.isoformat() if user.birthdate else None,
        "age": user.get_age()
    })

@main_blueprint.route("/api/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
def reset_user_password(user_id):
    """Reset user password."""
    if current_user.effective_tier != 0:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Cannot reset superuser password unless you are a superuser
    if user.effective_tier == 0 and not current_user.is_owner():
        abort(403)
    
    data = request.get_json()
    if not data or not data.get('new_password'):
        return jsonify({"error": "New password is required"}), 400
    
    # Update password
    user.password_hash = generate_password_hash(data['new_password'], method='pbkdf2:sha256')
    db.session.commit()

    # Send email notification if requested
    if data.get('send_email', False) and user.email:
        try:
            # Initialize email service for API context
            from routes.utils.email_service import email_service
            from main import app
            email_service.init_app(app)

            # Send password reset notification email
            subject = f"Your password has been reset - {current_app.config.get('BRAND_NAME', 'LilyOpenCMS')}"
            body = f"""
Hello {user.first_name or user.username},

Your password has been reset by an administrator.

If you did not request this change, please contact support immediately.

Best regards,
{current_app.config.get('BRAND_NAME', 'LilyOpenCMS')} Team
            """.strip()

            success = email_service.send_email(
                to=user.email,
                subject=subject,
                body=body
            )

            if success:
                current_app.logger.info(f"✅ Password reset notification sent to {user.email}")
            else:
                current_app.logger.warning(f"⚠️ Failed to send password reset notification to {user.email}")

        except Exception as e:
            current_app.logger.error(f"❌ Error sending password reset notification: {e}")
            # Don't fail the password reset if email fails

    return jsonify({
        "success": True,
        "message": "Password reset successfully",
        "email_notification_sent": data.get('send_email', False) and bool(user.email)
    })

@main_blueprint.route("/api/users/<int:user_id>/send-email", methods=["POST"])
@login_required
def send_custom_email(user_id):
    """Send a custom email to a specific user."""
    if current_user.effective_tier > 1:
        abort(403)
        
    user = User.query.get_or_404(user_id)
    if not user.email:
        return jsonify({"error": "User does not have a valid email address"}), 400
        
    data = request.get_json()
    if not data or not data.get('subject') or not data.get('message'):
        return jsonify({"error": "Subject and message are required"}), 400
        
    try:
        from routes.utils.email_service import email_service
        from main import app
        email_service.init_app(app)
        
        preview_text = data['message'][:100] + '...' if len(data['message']) > 100 else data['message']
        success = email_service.send_email(
            to=user.email,
            subject=data['subject'],
            body=data['message'],
            user_id=user.id,
            template_name='custom_email',
            message=data['message'],
            preview_text=preview_text
        )
        
        if success:
            current_app.logger.info(f"✅ Custom email sent to {user.email}")
            return jsonify({"success": True, "message": "Email sent successfully"})
        else:
            return jsonify({"error": "Failed to send email via mail server"}), 500
            
    except Exception as e:
        current_app.logger.error(f"❌ Error sending custom email to {user.email}: {e}")
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/users/stats", methods=["GET"])
@login_required
def get_user_stats():
    """Get user statistics."""
    if current_user.effective_tier > 1:
        abort(403)
    
    # Get basic counts
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    premium_users = User.query.filter_by(is_premium=True).count()
    pending_users = User.query.filter_by(verified=False).count()
    
    # Get role distribution
    role_counts = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
    role_distribution = {role.value: count for role, count in role_counts}
    
    # Get recent registrations (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_registrations = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    return jsonify({
        "total_users": total_users,
        "active_users": active_users,
        "premium_users": premium_users,
        "pending_users": pending_users,
        "role_distribution": role_distribution,
        "recent_registrations": recent_registrations
    })



@main_blueprint.route("/api/pending/stats", methods=["GET"])
@login_required
def get_pending_stats():
    """Get pending registration statistics."""
    if current_user.effective_tier > 1:
        abort(403)
    
    # Get pending users
    pending_users = User.query.filter_by(verified=False).all()
    total_pending = len(pending_users)
    
    # Get today's approvals/rejections
    today = datetime.now(timezone.utc).date()
    approved_today = User.query.filter(
        User.verified == True,
        func.date(User.updated_at) == today
    ).count()
    
    rejected_today = 0  # TODO: Implement rejection tracking
    
    # Calculate average approval time
    approved_users = User.query.filter_by(verified=True).all()
    total_approval_time = 0
    count = 0
    
    for user in approved_users:
        if user.created_at and user.updated_at:
            approval_time = (user.updated_at - user.created_at).total_seconds() / 3600  # hours
            total_approval_time += approval_time
            count += 1
    
    avg_approval_time = round(total_approval_time / count, 1) if count > 0 else 0
    
    return jsonify({
        "total_pending": total_pending,
        "approved_today": approved_today,
        "rejected_today": rejected_today,
        "avg_approval_time": avg_approval_time
    })

@main_blueprint.route("/api/roles", methods=["GET"])
@login_required
def get_roles_backup():
    """Get all custom roles (backup implementation)."""
    if current_user.effective_tier > 1:
        abort(403)
    
    try:
        roles = CustomRole.query.all()
        return jsonify([{
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "permissions": [{"id": p.id, "name": p.name} for p in role.permissions],
            "created_at": role.created_at.isoformat() if role.created_at else None
        } for role in roles])
    except Exception as e:
        print(f"Error in get_roles: {e}")
        return jsonify([])

@main_blueprint.route("/api/permissions", methods=["GET"])
@login_required
def get_permissions_backup():
    """Get all permissions (backup implementation)."""
    if current_user.effective_tier > 1:
        abort(403)
    
    try:
        from models import Permission
        permissions = Permission.query.all()
        return jsonify([{
            "id": perm.id,
            "name": perm.name,
            "description": perm.description,
            "resource": perm.resource,
            "action": perm.action,
            "created_at": perm.created_at.isoformat() if perm.created_at else None
        } for perm in permissions])
    except Exception as e:
        print(f"Error in get_permissions: {e}")
        return jsonify([])

@main_blueprint.route("/settings/users")
@login_required
def settings_users():
    """User management page for admins."""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    return render_template('admin/settings/users_management.html', current_user=current_user)
