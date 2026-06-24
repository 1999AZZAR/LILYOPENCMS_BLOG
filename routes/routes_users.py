from routes import main_blueprint
from .common_imports import *
from models import User, News, Image, YouTubeVideo, UserActivity
from datetime import datetime, timedelta, timezone

@main_blueprint.route("/api/users", methods=["GET"])
@login_required
def get_users():
    # Only superusers and admins can access this endpoint
    if not current_user.has_permission("users", "read"):
        abort(403)

    # Fetch all users with enhanced information
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@main_blueprint.route("/api/users/<int:user_id>/verify", methods=["PATCH"])
@login_required
def toggle_user_verification(user_id):
    # Only users with permission can toggle verification
    if not current_user.has_permission("users", "update"):
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Cannot modify superusers unless you are a superuser
    if user.role == UserRole.SUPERUSER and not current_user.is_owner():
        abort(403)
    
    # Cannot modify yourself
    if user.id == current_user.id:
        abort(403)
    
    data = request.get_json()
    user.verified = data["verified"]
    db.session.commit()
    
    # Record activity
    current_user.record_activity(
        "toggle_verification",
        f"Changed verification status for {user.username} to {data['verified']}",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return jsonify({"message": "Verification status updated successfully"})


@main_blueprint.route("/api/users/<int:user_id>/status", methods=["PATCH"])
@login_required
def toggle_user_status(user_id):
    # Only users with permission can toggle user status
    if not current_user.has_permission("users", "update"):
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Cannot modify superusers unless you are a superuser
    if user.role == UserRole.SUPERUSER and not current_user.is_owner():
        abort(403)
    
    # Cannot modify yourself
    if user.id == current_user.id:
        abort(403)
    
    data = request.get_json()
    user.is_active = data["is_active"]
    db.session.commit()
    
    # Record activity
    current_user.record_activity(
        "toggle_status",
        f"Changed status for {user.username} to {'active' if data['is_active'] else 'inactive'}",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return jsonify({"message": "User status updated successfully"})


@main_blueprint.route("/api/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    # Only users with permission can delete users
    if not current_user.has_permission("users", "delete"):
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Cannot delete superusers unless you are a superuser
    if user.role == UserRole.SUPERUSER and not current_user.is_owner():
        abort(403)
    
    # Cannot delete yourself
    if user.id == current_user.id:
        abort(403)
    
    # Record activity before deletion
    current_user.record_activity(
        "delete_user",
        f"Deleted user {user.username}",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})


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


@main_blueprint.route("/api/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    """Update user information with enhanced error handling."""
    try:
        # Only users with permission can update users
        if not current_user.has_permission("users", "update"):
            abort(403)
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Cannot modify superusers unless you are a superuser
        if user.role == UserRole.SUPERUSER and not current_user.is_owner():
            return jsonify({"error": "Cannot modify superuser accounts"}), 403
        
        # Cannot modify yourself
        if user.id == current_user.id:
            return jsonify({"error": "Cannot modify your own account"}), 403
        
        # Update basic fields
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"] if data["email"] else None
        if "first_name" in data:
            user.first_name = data["first_name"] if data["first_name"] else None
        if "last_name" in data:
            user.last_name = data["last_name"] if data["last_name"] else None
        if "bio" in data:
            user.bio = data["bio"] if data["bio"] else None
        if "social_links" in data:
            user.social_links = data["social_links"]
        
        # Update role (only superusers can change roles)
        if "role" in data and current_user.is_owner():
            try:
                user.role = UserRole(data["role"])
            except ValueError:
                return jsonify({"error": "Invalid role value"}), 400
        
        # Update status fields
        if "is_active" in data:
            user.is_active = bool(data["is_active"])
        if "verified" in data:
            user.verified = bool(data["verified"])
        if "is_suspended" in data:
            user.is_suspended = bool(data["is_suspended"])
        if "is_premium" in data:
            user.is_premium = bool(data["is_premium"])
        if "suspension_reason" in data:
            user.suspension_reason = data["suspension_reason"] if data["suspension_reason"] else None
        if "suspension_until" in data:
            if data["suspension_until"]:
                try:
                    user.suspension_until = datetime.fromisoformat(data["suspension_until"].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid date format for suspension_until"}), 400
            else:
                user.suspension_until = None
        
        # Update custom role (only superusers can change roles)
        if "custom_role_id" in data and current_user.is_owner():
            if data["custom_role_id"]:
                custom_role = CustomRole.query.get(data["custom_role_id"])
                if custom_role:
                    user.custom_role = custom_role
                else:
                    return jsonify({"error": "Custom role not found"}), 404
            else:
                user.custom_role = None
        
        db.session.commit()
        
        # Record activity
        current_user.record_activity(
            "update_user",
            f"Updated user {user.username}",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
        return jsonify({"message": "User updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to update user"}), 500


@main_blueprint.route("/api/settings/verified-users", methods=["GET"])
@login_required
def settings_verified_users():
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
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
        if not current_user.has_permission("users", "update"):
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
            if user.role == UserRole.SUPERUSER and not current_user.is_owner():
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
        
        # Record activity
        current_user.record_activity(
            "bulk_status_update",
            f"Bulk updated status for {len(updatable_users)} users to {'active' if is_active else 'inactive'}",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
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
    if not current_user.has_permission("users", "update"):
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
        if user.role == UserRole.SUPERUSER and not current_user.is_owner():
            continue
        # Cannot modify yourself
        if user.id == current_user.id:
            continue
        updatable_users.append(user)
    
    # Update user roles
    for user in updatable_users:
        user.custom_role = role
    
    db.session.commit()
    
    # Record activity
    role_name = role.name if role else "No role"
    current_user.record_activity(
        "bulk_role_assignment",
        f"Bulk assigned role '{role_name}' to {len(updatable_users)} users",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
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
        if not current_user.has_permission("users", "update"):
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
            if user.role == UserRole.SUPERUSER and not current_user.is_owner():
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
        
        # Record activity
        current_user.record_activity(
            "bulk_verification",
            f"Bulk {'verified' if verified else 'unverified'} {len(updatable_users)} users",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
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
        if not current_user.has_permission("users", "suspend"):
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
            if user.role == UserRole.SUPERUSER and not current_user.is_owner():
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
        
        db.session.commit()
        
        # Record activity
        action = "suspended" if suspend else "unsuspended"
        current_user.record_activity(
            f"bulk_{action}",
            f"Bulk {action} {len(updatable_users)} users",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
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
        if not current_user.has_permission("users", "delete"):
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
            if user.role == UserRole.SUPERUSER and not current_user.is_owner():
                skipped_users.append({"id": user.id, "reason": "Cannot delete superuser"})
                continue
            # Cannot delete yourself
            if user.id == current_user.id:
                skipped_users.append({"id": user.id, "reason": "Cannot delete self"})
                continue
            deletable_users.append(user)
        
        # Record activity before deletion
        usernames = [user.username for user in deletable_users]
        current_user.record_activity(
            "bulk_delete_users",
            f"Bulk deleted users: {', '.join(usernames)}",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
        # Delete users
        for user in deletable_users:
            db.session.delete(user)
        
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
    if not current_user.has_permission("users", "read"):
        abort(403)
    
    data = request.get_json()
    export_format = data.get("format", "csv")
    
    # Get all users (can be filtered by search, role, status, etc.)
    users = User.query.all()
    
    if export_format == "json":
        user_data = [user.to_dict() for user in users]
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
            "Premium", "Login Count", "Last Login", "Created At", "Suspension Reason"
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
                user.suspension_reason or ""
            ])
        
        output.seek(0)
        
        # Record activity
        current_user.record_activity(
            "bulk_export_users",
            f"Exported {len(users)} users in CSV format",
            request.remote_addr,
            request.headers.get("User-Agent")
        )
        
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
    if not current_user.has_permission("users", "read"):
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
        "user": user.to_dict(),
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
        "recent_activities": [activity.to_dict() for activity in recent_activities]
    }
    
    return jsonify(performance_data)


@main_blueprint.route("/api/users/performance/leaderboard", methods=["GET"])
@login_required
def get_performance_leaderboard():
    """Get user performance leaderboard."""
    if not current_user.has_permission("users", "read"):
        abort(403)
    
    # Get date range (last 30 days by default)
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    # Get all users with their performance metrics
    users = User.query.filter_by(is_active=True).all()
    
    leaderboard_data = []
    
    for user in users:
        # Calculate metrics for each user
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
        
        videos_count = db.session.query(YouTubeVideo).filter(
            YouTubeVideo.user_id == user.id,
            YouTubeVideo.created_at >= start_date,
            YouTubeVideo.created_at <= end_date
        ).count()
        
        recent_logins = UserActivity.query.filter(
            UserActivity.user_id == user.id,
            UserActivity.activity_type == "login",
            UserActivity.created_at >= end_date - timedelta(days=7)
        ).count()
        
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
    if not current_user.has_permission("users", "read"):
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
    if not current_user.has_permission("users", "read"):
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
    
    # Record activity
    current_user.record_activity(
        "export_performance_report",
        f"Exported performance report for {days} days",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=performance_report_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@main_blueprint.route("/api/users/<int:user_id>/performance/export", methods=["GET"])
@login_required
def export_user_performance(user_id):
    """Export user performance data as CSV."""
    if not current_user.has_permission("users", "read"):
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Get date range
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
    
    # Record export activity
    current_user.record_activity(
        "export_performance",
        f"Exported performance data for user {user.username}",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=performance_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@main_blueprint.route("/api/users/<int:user_id>/send-email", methods=["POST"])
@login_required
def send_custom_email(user_id):
    """Send a custom email to a specific user."""
    if not current_user.is_admin_tier():
        abort(403)

    user = User.query.get_or_404(user_id)
    if not user.email:
        return jsonify({"error": "User does not have a valid email address"}), 400

    data = request.get_json()
    if not data or not data.get('subject') or not data.get('message'):
        return jsonify({"error": "Subject and message are required"}), 400

    try:
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
            current_app.logger.info(f"Custom email sent to {user.email}")
            return jsonify({"success": True, "message": "Email sent successfully"})
        else:
            return jsonify({"error": "Failed to send email via mail server"}), 500

    except Exception as e:
        current_app.logger.error(f"Error sending custom email to {user.email}: {e}")
        return jsonify({"error": str(e)}), 500
