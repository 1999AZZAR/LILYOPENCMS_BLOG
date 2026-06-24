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
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from routes.utils.email_service import email_service
from routes.utils.auth_helpers import (
    get_auth_helper, unified_auth_required, admin_required, superuser_required,
    find_user_by_username_or_email, get_firebase_config, handle_password_change,
    send_verification_email, send_password_reset_email, clear_session_cookies
)

def _init_email_service():
    """Initialize email service with app context"""
    try:
        from main import app
        email_service.init_app(app)
        current_app.logger.info("✅ Email service initialized on-demand")
    except Exception as e:
        current_app.logger.error(f"❌ Failed to initialize email service on-demand: {e}")

def _get_serializer():
    secret_key = current_app.config.get("SECRET_KEY", "change-me")
    return URLSafeTimedSerializer(secret_key, salt="email-verify")

def _get_password_reset_serializer():
    secret_key = current_app.config.get("SECRET_KEY", "change-me")
    return URLSafeTimedSerializer(secret_key, salt="password-reset")

def _get_firebase_config():
    """Get Firebase configuration for frontend."""
    import os
    
    config = {
        "api_key": os.getenv('FIREBASE_API_KEY', ''),
        "auth_domain": os.getenv('FIREBASE_AUTH_DOMAIN', ''),
        "project_id": os.getenv('FIREBASE_PROJECT_ID', ''),
        "storage_bucket": os.getenv('FIREBASE_STORAGE_BUCKET', ''),
        "messaging_sender_id": os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
        "app_id": os.getenv('FIREBASE_APP_ID', '')
    }
    
    return config

# Helper functions are now imported from auth_helpers module

@main_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username sudah digunakan", "error")
            return render_template("public/login.html", firebase_config=_get_firebase_config())

        # Check if email already exists
        if email and User.query.filter_by(email=email).first():
            flash("Email sudah digunakan", "error")
            return render_template("public/login.html", firebase_config=_get_firebase_config())

        # Create new user with approval required
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,  # User needs approval to be active
            verified=False,
            role=UserRole.GENERAL
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Record registration activity (disabled - method not available)
            # Send verification email/log link
            if new_user.email:
                _init_email_service()
                send_verification_email(new_user)
            
            flash("Registrasi berhasil! Silakan periksa email Anda untuk memverifikasi akun.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            db.session.rollback()
            flash("Registrasi gagal. Silakan coba lagi.", "error")
            return render_template("public/login.html", firebase_config=_get_firebase_config())

    return render_template("public/login.html", firebase_config=_get_firebase_config())


@main_blueprint.route("/verify-email")
def verify_email():
    token = request.args.get("token", "")
    if not token:
        flash("Link verifikasi tidak valid.", "error")
        return redirect(url_for("main.login"))
    try:
        s = _get_serializer()
        data = s.loads(token, max_age=60*60*24*3)  # 3 days
        user = User.query.get(data.get("user_id"))
        if not user:
            flash("Token verifikasi tidak valid.", "error")
            return redirect(url_for("main.login"))
        if not user.verified:
            user.verified = True
            user.email_verified_at = datetime.now(timezone.utc)
            # Hybrid policy: auto-approve verified low-risk users; leave others pending
            try:
                from routes.utils.risk_policy import should_auto_approve
                if should_auto_approve(user):
                    user.is_active = True
            except Exception as _e:
                current_app.logger.info(f"Risk policy unavailable or errored: {_e}")
            db.session.commit()
        flash("Email berhasil diverifikasi.", "success")
        return redirect(url_for("main.login"))
    except SignatureExpired:
        flash("Link verifikasi telah kedaluwarsa.", "error")
        return redirect(url_for("main.login"))
    except BadSignature:
        flash("Token verifikasi tidak valid.", "error")
        return redirect(url_for("main.login"))


@main_blueprint.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email_or_username = request.form.get("email_or_username", "").strip()

        if not email_or_username:
            flash("Silakan masukkan alamat email atau username Anda", "error")
            return render_template("public/forgot_password.html")

        # Find user by email or username
        user = find_user_by_username_or_email(email_or_username)

        if not user:
            # Don't reveal if user exists or not for security
            flash("Jika akun dengan email/username tersebut ada, Anda akan menerima link reset kata sandi.", "info")
            return render_template("public/forgot_password.html")

        if not user.email:
            flash("Akun ini tidak memiliki alamat email yang terkait.", "error")
            return render_template("public/forgot_password.html")

        try:
            # Clear any existing reset tokens
            user.password_reset_token = None
            user.password_reset_expires_at = None
            db.session.commit()

            # Send password reset email
            _init_email_service()
            send_password_reset_email(user)

            flash("Jika akun dengan email/username tersebut ada, Anda akan menerima link reset kata sandi.", "info")
            return render_template("public/forgot_password.html")

        except Exception as e:
            current_app.logger.error(f"❌ Error sending password reset email: {e}")
            flash("Terjadi kesalahan saat mengirim email reset kata sandi. Silakan coba lagi nanti.", "error")
            return render_template("public/forgot_password.html")

    return render_template("public/forgot_password.html")


@main_blueprint.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token", "")
    if not token:
        flash("Link reset kata sandi tidak valid.", "error")
        return redirect(url_for("main.login"))

    try:
        current_app.logger.info(f"Verifying password reset token: {token[:50]}...")
        s = _get_password_reset_serializer()
        data = s.loads(token, max_age=60*60)  # 1 hour
        current_app.logger.info(f"Token verified successfully, user_id: {data.get('user_id')}")
        user = User.query.get(data.get("user_id"))

        if not user:
            flash("Token reset kata sandi tidak valid.", "error")
            return redirect(url_for("main.login"))

        if not user.email:
            flash("Akun ini tidak memiliki alamat email.", "error")
            return redirect(url_for("main.login"))

        if request.method == "POST":
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not new_password or not confirm_password:
                flash("Kedua field kata sandi harus diisi.", "error")
                return render_template("public/reset_password.html", token=token)

            if new_password != confirm_password:
                flash("Kata sandi tidak cocok.", "error")
                return render_template("public/reset_password.html", token=token)

            if len(new_password) < 6:
                flash("Kata sandi minimal harus 6 karakter.", "error")
                return render_template("public/reset_password.html", token=token)

            try:
                # Use unified password change handler
                success, message = handle_password_change(user, new_password)
                
                if not success:
                    flash(f"Failed to reset password: {message}", "error")
                    return render_template("public/reset_password.html", token=token)

                flash("Reset kata sandi berhasil. Silakan masuk dengan kata sandi baru Anda.", "success")
                return redirect(url_for("main.login"))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"❌ Error resetting password: {e}")
                flash("Terjadi kesalahan saat mereset kata sandi Anda. Silakan coba lagi.", "error")
                return render_template("public/reset_password.html", token=token)

        return render_template("public/reset_password.html", token=token)

    except SignatureExpired:
        flash("Link reset kata sandi telah kedaluwarsa. Silakan minta yang baru.", "error")
        return redirect(url_for("main.forgot_password"))
    except BadSignature:
        flash("Token reset kata sandi tidak valid.", "error")
        return redirect(url_for("main.forgot_password"))


@main_blueprint.route("/api/registrations/pending", methods=["GET"])
@login_required
def get_pending_registrations():
    """Get all pending user registrations."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    # Get users that are not active (pending approval)
    pending_users = User.query.filter_by(is_active=False).order_by(User.created_at.desc()).all()
    
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'bio': user.bio,
        'role': user.role.value if user.role else None,
        'is_verified': user.verified,
        'is_suspended': user.is_suspended,
        'is_premium': user.is_premium,
        'custom_role_id': user.custom_role_id,
        'created_at': user.created_at.isoformat() if user.created_at else None
    } for user in pending_users])


@main_blueprint.route("/api/registrations/<int:user_id>/approve", methods=["POST"])
@login_required
def approve_registration(user_id):
    """Approve a user registration."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    if user.is_active:
        return jsonify({"error": "User is already active"}), 400
    
    # Activate the user
    user.is_active = True
    user.verified = True  # Auto-verify approved users
    
    db.session.commit()
    
    # Record approval activity (disabled - method not available)
    
    return jsonify({
        "message": f"Registration approved for {user.username}",
        "user": {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'role': user.role.value if user.role else None,
            'is_verified': user.verified,
            'is_suspended': user.is_suspended,
            'is_premium': user.is_premium,
            'custom_role_id': user.custom_role_id,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    })


@main_blueprint.route("/api/registrations/<int:user_id>/reject", methods=["POST"])
@login_required
def reject_registration(user_id):
    """Reject a user registration."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    reason = data.get("reason", "Registration rejected")
    
    if user.is_active:
        return jsonify({"error": "Cannot reject active user"}), 400
    
    # Record rejection activity (disabled - method not available)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        "message": f"Registration rejected for {user.username}",
        "reason": reason
    })


@main_blueprint.route("/api/registrations/bulk/approve", methods=["POST"])
@login_required
def bulk_approve_registrations():
    """Bulk approve user registrations."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    data = request.get_json()
    user_ids = data.get("user_ids", [])
    
    if not user_ids:
        return jsonify({"error": "No user IDs provided"}), 400
    
    # Get pending users
    users = User.query.filter(
        User.id.in_(user_ids),
        User.is_active == False
    ).all()
    
    approved_users = []
    for user in users:
        user.is_active = True
        user.verified = True
        approved_users.append(user)
        
        # Record user activity (disabled for now)
        pass
    
    db.session.commit()
    
    # Record bulk approval activity (with safety check)
    usernames = [user.username for user in approved_users]
    try:
        if hasattr(current_user, 'record_activity'):
            current_user.record_activity(
                "bulk_approve_registrations",
                f"Bulk approved registrations for: {', '.join(usernames)}",
                request.remote_addr,
                request.headers.get("User-Agent")
            )
    except Exception as e:
        current_app.logger.warning(f"Could not record user activity: {str(e)}")
    
    return jsonify({
        "message": f"Approved {len(approved_users)} registrations",
        "approved_count": len(approved_users),
        "total_requested": len(user_ids)
    })


@main_blueprint.route("/api/registrations/bulk/reject", methods=["POST"])
@login_required
def bulk_reject_registrations():
    """Bulk reject user registrations."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    data = request.get_json()
    user_ids = data.get("user_ids", [])
    reason = data.get("reason", "Bulk rejection")
    
    if not user_ids:
        return jsonify({"error": "No user IDs provided"}), 400
    
    # Get pending users
    users = User.query.filter(
        User.id.in_(user_ids),
        User.is_active == False
    ).all()
    
    # Record rejection activity (disabled - method not available)
    
    # Delete users
    for user in users:
        db.session.delete(user)
    
    db.session.commit()
    
    return jsonify({
        "message": f"Rejected {len(users)} registrations",
        "rejected_count": len(users),
        "total_requested": len(user_ids),
        "reason": reason
    })


@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        # Maintenance mode check (block general users when enabled)
        try:
            import os, json
            settings_path = os.path.join(current_app.instance_path, 'app_settings.json')
            maintenance_enabled = False
            maintenance_message = 'Situs dalam mode perawatan. Silakan coba lagi nanti.'
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    m = data.get('maintenance', {}) if isinstance(data, dict) else {}
                    maintenance_enabled = bool(m.get('enabled', False))
                    maintenance_message = m.get('message') or maintenance_message
        except Exception:
            maintenance_enabled = False

        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username_or_email or not password:
            flash("Username/email dan kata sandi harus diisi", "error")
            return render_template("public/login.html", firebase_config=_get_firebase_config())

        # Find user by username or email
        user = find_user_by_username_or_email(username_or_email)

        if user and user.check_password(password):
            # If maintenance is enabled, allow only SUPERUSER
            if maintenance_enabled and user.role != UserRole.SUPERUSER:
                flash(maintenance_message, "error")
                return render_template("public/login.html", firebase_config=_get_firebase_config())
            if not user.is_active:
                if not user.verified:
                    flash("Akun Anda sedang menunggu verifikasi email atau persetujuan administrator. Silakan periksa email Anda untuk link verifikasi, atau tunggu persetujuan administrator.", "error")
                else:
                    flash("Akun Anda sedang menunggu persetujuan administrator. Silakan tunggu persetujuan administrator.", "error")
                return render_template("public/login.html", firebase_config=_get_firebase_config())

            if user.is_suspended:
                flash("Akun Anda telah ditangguhkan. Silakan hubungi administrator.", "error")
                return render_template("public/login.html", firebase_config=_get_firebase_config())

            # Use unified authentication system
            try:
                auth_helper = get_auth_helper()
                auth_result = auth_helper.authenticate_user(user, "local")
                
                if not auth_result["success"]:
                    flash(auth_result["message"], "error")
                    return render_template("public/login.html", firebase_config=_get_firebase_config())
                
                current_app.logger.info(f"Unified authentication successful for user {user.username}")

            except Exception as e:
                current_app.logger.warning(f"Unified authentication failed, falling back to basic login: {e}")
                # Fallback to basic login
                login_user(user)
            next_page = request.args.get("next")
            # Role-based redirect: editors to editor dashboard, admins to settings, general users to user profile
            if next_page:
                return redirect(next_page)

            # Check if user has editor role first (custom role takes precedence)
            custom_name = (user.custom_role.name.lower() if user.custom_role and user.custom_role.name else "")
            if custom_name in ['editor', 'subadmin', 'media-manager']:
                return redirect(url_for("editor.dashboard"))
            elif user.role in [UserRole.ADMIN, UserRole.SUPERUSER] or user.is_owner():
                return redirect(url_for("main.settings_dashboard"))

            return redirect(url_for("user_profile.user_profile", username=user.username))

        # Record failed login attempt for security monitoring
        try:
            if user:  # Valid user but wrong password
                from routes.utils.simple_jwt_session import get_simple_jwt_manager
                jwt_manager = get_simple_jwt_manager()
                jwt_manager.record_user_activity(
                    user.id,
                    "login_failed",
                    f"Failed login attempt from {request.remote_addr}"
                )
                current_app.logger.warning(f"Failed login attempt for user {user.username} from {request.remote_addr}")
        except Exception as e:
            current_app.logger.warning(f"Could not record failed login attempt: {e}")

        flash("Username/email atau kata sandi tidak valid", "error")
        return render_template("public/login.html", firebase_config=_get_firebase_config())

    return render_template("public/login.html", firebase_config=_get_firebase_config())

@main_blueprint.route("/logout")
def logout():
    # Use unified authentication system for logout
    try:
        auth_helper = get_auth_helper()
        
        # Store username before logout (since current_user becomes anonymous after logout)
        username = current_user.username if current_user.is_authenticated else "anonymous"
        
        # Only attempt logout if user is authenticated
        if current_user.is_authenticated:
            # Logout user with unified system
            logout_result = auth_helper.logout_user(current_user, "User logout")
            
            if logout_result["success"]:
                current_app.logger.info(f"Unified logout successful for user {username}")
            else:
                current_app.logger.warning(f"Unified logout failed: {logout_result.get('message', 'Unknown error')}")
        else:
            # User is not authenticated, just clear any remaining session data
            session.clear()
            current_app.logger.info("Logout called for unauthenticated user, cleared session")
        
    except Exception as e:
        current_app.logger.warning(f"Unified logout failed, falling back to basic logout: {e}")
        # Fallback to basic logout
        logout_user()
        session.clear()
    
    # Create response and explicitly clear session cookies
    response = redirect(url_for("main.home"))
    
    # Clear session cookies using helper
    clear_session_cookies(response)
    
    # Force clear Flask session data
    session.clear()
    session.permanent = False
    
    return response


@main_blueprint.route("/logout/force")
def force_logout():
    """Force logout endpoint that completely clears all session data."""
    try:
        # Clear all session data
        session.clear()
        session.permanent = False
        
        # Logout from Flask-Login
        logout_user()
        
        # Clear unified auth session
        try:
            from routes.utils.unified_auth import get_unified_auth_manager
            auth_manager = get_unified_auth_manager()
            if current_user.is_authenticated:
                auth_manager.logout_user(current_user, "Force logout")
        except Exception as e:
            current_app.logger.warning(f"Unified logout failed during force logout: {e}")
        
        current_app.logger.info("Force logout completed")
        
    except Exception as e:
        current_app.logger.error(f"Force logout error: {e}")
    
    # Create response with aggressive cookie clearing
    response = redirect(url_for("main.home"))
    
    # Clear all possible session cookies with different configurations
    cookie_configs = [
        {'name': 'lily_session', 'httponly': True, 'samesite': 'Strict'},
        {'name': 'lily_session', 'httponly': False, 'samesite': 'Lax'},
        {'name': 'session', 'httponly': True, 'samesite': 'Lax'},
        {'name': 'session', 'httponly': False, 'samesite': 'Lax'},
    ]
    
    for config in cookie_configs:
        response.set_cookie(
            config['name'],
            '',
            expires=0,
            max_age=0,
            path='/',
            secure=False,  # Development mode
            httponly=config['httponly'],
            samesite=config['samesite']
        )
    
    return response


@main_blueprint.route("/api/account/change-password", methods=["POST"])
@unified_auth_required
def change_password():
    data = request.get_json()
    current_password = data["current_password"]
    new_password = data["new_password"]
    confirm_password = data["confirm_password"]

    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400

    # Use unified password change handler
    success, message = handle_password_change(current_user, new_password, current_password)
    
    if success:
        return jsonify({"message": "Password changed successfully. Please log in again."}), 200
    else:
        return jsonify({"error": message}), 400


@main_blueprint.route("/api/account/delete", methods=["DELETE"])
@unified_auth_required
def delete_account():
    """Delete the current user's account completely."""
    try:
        from routes.utils.content_deletion_helper import delete_user_completely

        # Delete the user account completely (no transfer, full deletion)
        deletion_stats = delete_user_completely(current_user.id, transfer_user_id=None)

        current_app.logger.info(
            f"User {current_user.username} (ID: {current_user.id}) successfully deleted their account. "
            f"Deletion stats: {deletion_stats}"
        )

        return jsonify({
            "message": "Account deleted successfully",
            "deletion_stats": deletion_stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting account for user {current_user.username} (ID: {current_user.id}): {e}")
        return jsonify({"error": "Failed to delete account"}), 500


@main_blueprint.route("/api/account/stats", methods=["GET"])
@unified_auth_required
def account_stats():
    """Get comprehensive account statistics for the current user."""
    try:
        from models import News, Album, AlbumChapter, Comment, Rating
        
        # Get user's news/articles
        user_news = News.query.filter_by(user_id=current_user.id).all()
        total_articles = len(user_news)
        visible_articles = len([n for n in user_news if n.is_visible])
        total_reads = sum(n.read_count or 0 for n in user_news)
        
        # Get user's albums/books
        user_albums = Album.query.filter_by(user_id=current_user.id).all()
        total_albums = len(user_albums)
        
        # Get total chapters from user's albums
        album_ids = [album.id for album in user_albums]
        total_chapters = AlbumChapter.query.filter(AlbumChapter.album_id.in_(album_ids)).count() if album_ids else 0
        
        # Get user's comments
        total_comments = Comment.query.filter_by(user_id=current_user.id).count()
        
        return jsonify({
            "total_articles": total_articles,
            "visible_articles": visible_articles,
            "total_reads": total_reads,
            "total_albums": total_albums,
            "total_chapters": total_chapters,
            "total_comments": total_comments
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/api/account/albums", methods=["GET"])
@unified_auth_required
def account_albums():
    """Get user's albums with pagination and filtering."""
    try:
        from models import Album, Category
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '').strip()
        album_type = request.args.get('type', '').strip()
        
        # Base query for user's albums
        query = Album.query.filter_by(user_id=current_user.id)
        
        # Apply filters
        if search:
            query = query.filter(Album.title.ilike(f'%{search}%'))
        
        if status:
            if status == 'visible':
                query = query.filter(Album.is_visible == True)
            elif status == 'hidden':
                query = query.filter(Album.is_visible == False)
            elif status == 'archived':
                query = query.filter(Album.is_archived == True)
        
        if album_type:
            if album_type == 'premium':
                query = query.filter(Album.is_premium == True)
            elif album_type == 'regular':
                query = query.filter(Album.is_premium == False)
        
        # Get paginated results
        pagination = query.order_by(Album.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        albums_data = []
        for album in pagination.items:
            albums_data.append({
                'id': album.id,
                'title': album.title,
                'category': album.category.name if album.category else 'Uncategorized',
                'is_visible': album.is_visible,
                'is_premium': album.is_premium,
                'is_archived': album.is_archived,
                'total_chapters': album.total_chapters or 0,
                'created_at': album.created_at.strftime('%Y-%m-%d') if album.created_at else None
            })
        
        return jsonify({
            'albums': albums_data,
            'total': pagination.total,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/api/account/comments", methods=["GET"])
@unified_auth_required
def account_comments():
    """Get user's recent comments."""
    try:
        from models import Comment, News
        
        # Get user's recent comments
        comments = Comment.query.filter_by(user_id=current_user.id)\
            .order_by(Comment.created_at.desc())\
            .limit(10)\
            .all()
        
        comments_data = []
        for comment in comments:
            # Get the article title
            article_title = "Unknown Article"
            if comment.content_type == 'news' and comment.content_id:
                article = News.query.get(comment.content_id)
                if article:
                    article_title = article.title
            
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'article_title': article_title,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M') if comment.created_at else None,
                'is_approved': comment.is_approved
            })
        
        return jsonify({
            'comments': comments_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/api/account/activity", methods=["GET"])
@unified_auth_required
def account_activity():
    """Get user's recent activity."""
    try:
        from models import UserActivity, News, Album
        
        # Get user's recent activities
        activities = UserActivity.query.filter_by(user_id=current_user.id)\
            .order_by(UserActivity.created_at.desc())\
            .limit(10)\
            .all()
        
        activities_data = []
        for activity in activities:
            # Create human-readable descriptions
            description = activity.description or activity.activity_type
            
            # Add more context based on activity type
            if activity.activity_type == 'create_news':
                description = f"Membuat artikel: {activity.description}"
            elif activity.activity_type == 'update_news':
                description = f"Mengupdate artikel: {activity.description}"
            elif activity.activity_type == 'create_album':
                description = f"Membuat buku/seri: {activity.description}"
            elif activity.activity_type == 'update_album':
                description = f"Mengupdate buku/seri: {activity.description}"
            elif activity.activity_type == 'login':
                description = "Login ke sistem"
            elif activity.activity_type == 'logout':
                description = "Logout dari sistem"
            
            activities_data.append({
                'id': activity.id,
                'action': activity.activity_type.replace('_', ' ').title(),
                'description': description,
                'created_at': activity.created_at.strftime('%Y-%m-%d %H:%M') if activity.created_at else None
            })
        
        return jsonify({
            'activities': activities_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_user_dashboard_url(user):
    """Get the appropriate dashboard URL based on user role."""
    # Check if user has editor role first (custom role takes precedence)
    custom_name = (user.custom_role.name.lower() if user.custom_role and user.custom_role.name else "")
    if custom_name == 'editor':
        return url_for("editor.dashboard")
    elif custom_name in ['subadmin', 'media-manager'] or user.role in [UserRole.ADMIN, UserRole.SUPERUSER] or user.is_owner():
        return url_for("main.settings_dashboard")
    return url_for("user_profile.user_profile", username=user.username)

@main_blueprint.route("/api/account/profile", methods=["GET"])
@unified_auth_required
def account_profile():
    """Get current user's profile data. Works with both Firebase and username/email+password auth."""
    try:
        # Get user from JWT token (mobile/API) or session (web)
        from routes.utils.auth_helpers import get_auth_helper
        from flask import g
        auth_helper = get_auth_helper()
        user = auth_helper.get_current_user()
        
        if not user:
            # Fallback to current_user for backward compatibility
            user = getattr(g, 'api_user', None) or (current_user if current_user.is_authenticated else None)
        
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found",
                "message": "Unable to retrieve user information",
                "code": "USER_NOT_FOUND"
            }), 401
        
        # Get profile picture URL
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = user.profile_picture
        elif hasattr(user, 'provider_data') and user.provider_data:
            profile_picture_url = user.parsed_provider_data.get('photo_url')
        
        return jsonify({
            'success': True,
            'username': user.username,
            'email': user.email,  # Always include email for own profile
            'full_name': user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name or ''} {user.last_name or ''}".strip(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthdate': user.birthdate.isoformat() if user.birthdate else None,
            'age': user.get_age() if hasattr(user, 'get_age') and user.birthdate else None,
            'role': user.role.value if user.role else None,
            'custom_role_name': user.custom_role.name if user.custom_role else None,
            'auth_provider': user.auth_provider if hasattr(user, 'auth_provider') else None,
            'profile_picture_url': profile_picture_url,
            'is_premium': user.is_premium,
            'verified': user.verified,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'login_count': user.login_count,
        })
    except Exception as e:
        current_app.logger.error(f"Error getting account profile: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "PROFILE_ERROR"
        }), 500


@main_blueprint.route("/api/account/profile/<username>", methods=["GET"])
def get_user_profile_by_username(username):
    """Get a specific user's profile data by username."""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthdate': user.birthdate.isoformat() if user.birthdate else None,
            'age': user.get_age() if user.birthdate else None,
            'role': user.role.value if user.role else None,
            'custom_role_name': user.custom_role.name if user.custom_role else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/account/profile", methods=["PUT", "PATCH"])
@unified_auth_required
def update_account_profile():
    """Update current user's profile data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided", "code": "MISSING_DATA"}), 400
        
        updated = False
        changes = []
        # Update allowed fields
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            # Split full name into first and last name
            name_parts = full_name.split(' ', 1)
            new_first = name_parts[0].strip()
            new_last = name_parts[1].strip() if len(name_parts) > 1 else None
            
            if current_user.first_name != new_first or current_user.last_name != new_last:
                current_user.first_name = new_first
                current_user.last_name = new_last
                changes.append("full_name")
                updated = True
        
        if 'birthdate' in data:
            if data['birthdate']:
                try:
                    # Handle both ISO format and YYYY-MM-DD format
                    birthdate_str = data['birthdate']
                    if 'T' in birthdate_str:
                        birthdate_str = birthdate_str.split('T', 1)[0]
                    new_birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
                    if current_user.birthdate != new_birthdate:
                        current_user.birthdate = new_birthdate
                        changes.append("birthdate")
                        updated = True
                except ValueError:
                    return jsonify({"success": False, "error": "Invalid birthdate format, expected YYYY-MM-DD", "code": "INVALID_FORMAT"}), 400
            elif current_user.birthdate is not None:
                current_user.birthdate = None
                changes.append("birthdate")
                updated = True
        
        if not updated:
            return jsonify({
                "success": True, 
                "message": "No changes detected", 
                "profile": {
                    'username': current_user.username,
                    'email': current_user.email,
                    'full_name': current_user.get_full_name()
                }
            }), 200

        db.session.commit()

        # Audit Log
        try:
            from models import UserActivity
            audit = UserActivity(
                user_id=current_user.id,
                activity_type='UPDATE_PROFILE',
                description=f"Updated profile: {', '.join(changes)}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")

        # Send profile update confirmation email
        try:
            from routes.utils.email_service import email_service
            # Get updated fields for the email
            email_fields = []
            if 'full_name' in changes:
                email_fields.append('Nama lengkap')
            if 'birthdate' in changes:
                email_fields.append('Tanggal lahir')

            if email_fields:
                email_service.send_profile_update_confirmation(current_user, email_fields)
        except Exception as e:
            current_app.logger.warning(f"Failed to send profile update notification to {current_user.username}: {e}")

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': {
                'username': current_user.username,
                'email': current_user.email,
                'full_name': current_user.get_full_name(),
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'birthdate': current_user.birthdate.isoformat() if current_user.birthdate else None,
                'age': current_user.get_age() if current_user.birthdate else None,
                'role': current_user.role.value if current_user.role else None,
                'custom_role_name': current_user.custom_role.name if current_user.custom_role else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating account profile: {e}")
        return jsonify({"success": False, "error": str(e), "code": "INTERNAL_ERROR"}), 500


@main_blueprint.route("/settings/pending-registrations")
@admin_required
def pending_registrations():
    """Pending registrations management page for admins."""
    
    return render_template('admin/settings/pending_registrations.html', current_user=current_user)

@main_blueprint.route("/settings/firebase-auth")
@superuser_required
def firebase_auth_settings():
    """Firebase Authentication Settings page for superusers."""
    
    return render_template('admin/firebase_auth_settings.html', current_user=current_user)
