"""
Routes for comment system (Phase 8.3).
"""

from routes.common_imports import *
from models import Comment, CommentStatus, News


# ── Public: Post Comment ──────────────────────────────────────────────
@main_blueprint.route("/api/news/<int:news_id>/comments", methods=["POST"])
def api_post_comment(news_id):
    news = News.query.get_or_404(news_id)
    data = request.get_json(silent=True) or {}

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Comment content is required"}), 400

    if len(content) > 2000:
        return jsonify({"error": "Comment too long (max 2000 chars)"}), 400

    # Determine author
    user_id = None
    author_name = data.get("author_name", "").strip()
    author_email = data.get("author_email", "").strip()

    if current_user.is_authenticated:
        user_id = current_user.id
        author_name = author_name or current_user.get_full_name()
        author_email = author_email or current_user.email
    elif not author_name or not author_email:
        return jsonify({"error": "Name and email are required for guests"}), 400

    # Check for spam (basic: too many links)
    link_count = len(re.findall(r"https?://", content))
    if link_count > 3:
        status = CommentStatus.SPAM
    else:
        status = CommentStatus.PENDING

    parent_id = data.get("parent_id")
    if parent_id:
        parent = Comment.query.get(parent_id)
        if not parent or parent.news_id != news_id:
            parent_id = None

    comment = Comment(
        content=content,
        status=status,
        author_name=author_name,
        author_email=author_email,
        author_ip=request.remote_addr,
        news_id=news_id,
        user_id=user_id,
        parent_id=parent_id,
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Comment submitted" if status == CommentStatus.PENDING else "Comment posted",
        "comment": comment.to_dict(),
    })


# ── Public: Get Comments ─────────────────────────────────────────────
@main_blueprint.route("/api/news/<int:news_id>/comments", methods=["GET"])
def api_get_comments(news_id):
    page = request.args.get("page", 1, type=int)

    query = Comment.query.filter_by(news_id=news_id, status=CommentStatus.APPROVED)

    if current_user.is_authenticated and current_user.has_permission("settings", "read"):
        # Admins see all comments
        query = Comment.query.filter_by(news_id=news_id)

    comments = query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    return jsonify({
        "comments": [c.to_dict() for c in comments.items],
        "total": comments.total,
        "pages": comments.pages,
        "current_page": comments.page,
    })


# ── Admin: Comment Moderation ─────────────────────────────────────────
@main_blueprint.route("/settings/comments")
@login_required
def settings_comments():
    if not current_user.has_permission("settings", "read"):
        abort(403)

    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Comment.query
    if status_filter:
        try:
            query = query.filter_by(status=CommentStatus(status_filter))
        except ValueError:
            pass

    comments = query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("settings/comments_management.html", comments=comments, status_filter=status_filter)


@main_blueprint.route("/settings/comments/<int:comment_id>/approve", methods=["POST"])
@login_required
def settings_comment_approve(comment_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    comment = Comment.query.get_or_404(comment_id)
    comment.status = CommentStatus.APPROVED
    db.session.commit()
    flash("Comment approved", "success")
    return redirect(url_for("main.settings_comments"))


@main_blueprint.route("/settings/comments/<int:comment_id>/reject", methods=["POST"])
@login_required
def settings_comment_reject(comment_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    comment = Comment.query.get_or_404(comment_id)
    comment.status = CommentStatus.REJECTED
    db.session.commit()
    flash("Comment rejected", "success")
    return redirect(url_for("main.settings_comments"))


@main_blueprint.route("/settings/comments/<int:comment_id>/spam", methods=["POST"])
@login_required
def settings_comment_spam(comment_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    comment = Comment.query.get_or_404(comment_id)
    comment.status = CommentStatus.SPAM
    db.session.commit()
    flash("Comment marked as spam", "success")
    return redirect(url_for("main.settings_comments"))


@main_blueprint.route("/settings/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def settings_comment_delete(comment_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted", "success")
    return redirect(url_for("main.settings_comments"))


# ── API: Comment Moderation ───────────────────────────────────────────
@main_blueprint.route("/api/settings/comments/<int:comment_id>/status", methods=["POST"])
@login_required
def api_comment_set_status(comment_id):
    if not current_user.has_permission("settings", "update"):
        return jsonify({"error": "Forbidden"}), 403

    comment = Comment.query.get_or_404(comment_id)
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    try:
        comment.status = CommentStatus(new_status)
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid status"}), 400

    db.session.commit()
    return jsonify({"success": True, "status": comment.status.value})
