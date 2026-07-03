"""
Routes for tag system (Phase 8.2).
"""

from routes.common_imports import *
from models import Tag, News, slugify, news_tags


# ── Public Tag Pages ──────────────────────────────────────────────────
@main_blueprint.route("/tag/<slug>")
def public_tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    articles = (
        News.query
        .filter(News.is_visible == True, News.tags.contains(tag))
        .order_by(News.date.desc())
        .paginate(page=page, per_page=12, error_out=False)
    )
    return render_template("public/tag.html", tag=tag, articles=articles)


@main_blueprint.route("/tags")
def public_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template("public/tags.html", tags=tags)


# ── Admin Tag Management ──────────────────────────────────────────────
@main_blueprint.route("/settings/tags")
@login_required
def settings_tags():
    if not current_user.has_permission("settings", "read"):
        abort(403)
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template("settings/tags_management.html", tags=tags)


@main_blueprint.route("/settings/tags/create", methods=["POST"])
@login_required
def settings_tag_create():
    if not current_user.has_permission("settings", "update"):
        abort(403)

    name = request.form.get("name", "").strip()
    if not name:
        flash("Tag name is required", "error")
        return redirect(url_for("main.settings_tags"))

    slug = slugify(name)
    if Tag.query.filter_by(slug=slug).first():
        flash("Tag already exists", "error")
        return redirect(url_for("main.settings_tags"))

    tag = Tag(name=name, slug=slug)
    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{name}' created", "success")
    return redirect(url_for("main.settings_tags"))


@main_blueprint.route("/settings/tags/<int:tag_id>/delete", methods=["POST"])
@login_required
def settings_tag_delete(tag_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    tag = Tag.query.get_or_404(tag_id)
    name = tag.name
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{name}' deleted", "success")
    return redirect(url_for("main.settings_tags"))


@main_blueprint.route("/settings/tags/<int:tag_id>/rename", methods=["POST"])
@login_required
def settings_tag_rename(tag_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    tag = Tag.query.get_or_404(tag_id)
    new_name = request.form.get("name", "").strip()
    if not new_name:
        flash("Tag name is required", "error")
        return redirect(url_for("main.settings_tags"))

    new_slug = slugify(new_name)
    existing = Tag.query.filter(Tag.slug == new_slug, Tag.id != tag.id).first()
    if existing:
        flash("Tag with this name already exists", "error")
        return redirect(url_for("main.settings_tags"))

    tag.name = new_name
    tag.slug = new_slug
    db.session.commit()
    flash(f"Tag renamed to '{new_name}'", "success")
    return redirect(url_for("main.settings_tags"))


# ── API: Tag CRUD ─────────────────────────────────────────────────────
@main_blueprint.route("/api/tags", methods=["GET"])
def api_tags_public():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return jsonify({"tags": [t.to_dict() for t in tags]})


@main_blueprint.route("/api/settings/tags", methods=["GET"])
@login_required
def api_tags_list():
    if not current_user.has_permission("settings", "read"):
        return jsonify({"error": "Forbidden"}), 403
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return jsonify({"tags": [t.to_dict() for t in tags]})


@main_blueprint.route("/api/settings/tags", methods=["POST"])
@login_required
def api_tags_create():
    if not current_user.has_permission("settings", "update"):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Tag name is required"}), 400

    slug = slugify(name)
    if Tag.query.filter_by(slug=slug).first():
        return jsonify({"error": "Tag already exists"}), 409

    tag = Tag(name=name, slug=slug)
    db.session.add(tag)
    db.session.commit()
    return jsonify(tag.to_dict()), 201


@main_blueprint.route("/api/tags/suggest", methods=["GET"])
def api_tags_suggest():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify({"tags": []})
    tags = Tag.query.filter(Tag.name.ilike(f"%{q}%")).limit(10).all()
    return jsonify({"tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in tags]})


@main_blueprint.route("/api/news/<int:news_id>/tags", methods=["POST"])
@login_required
def api_news_set_tags(news_id):
    if not current_user.has_permission("news", "update"):
        return jsonify({"error": "Forbidden"}), 403

    news = News.query.get_or_404(news_id)
    data = request.get_json(silent=True) or {}
    tag_ids = data.get("tag_ids", [])

    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    news.tags = tags
    db.session.commit()
    return jsonify({"success": True, "tags": [t.to_dict() for t in news.tags]})
