"""
Routes for static pages system (Phase 8.1).
"""

from routes.common_imports import *
from models import Page, slugify


# ── Public Page View ──────────────────────────────────────────────────
@main_blueprint.route("/page/<slug>")
def public_page(slug):
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("public/page.html", page=page)


# ── Admin Page Management ─────────────────────────────────────────────
@main_blueprint.route("/settings/pages")
@login_required
def settings_pages():
    if not current_user.has_permission("settings", "read"):
        abort(403)
    pages = Page.query.order_by(Page.menu_order.asc(), Page.title.asc()).all()
    return render_template("settings/pages_management.html", pages=pages)


@main_blueprint.route("/settings/pages/create", methods=["GET", "POST"])
@login_required
def settings_page_create():
    if not current_user.has_permission("settings", "update"):
        abort(403)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "")
        excerpt = request.form.get("excerpt", "").strip()
        template = request.form.get("template", "default")
        is_published = request.form.get("is_published") == "on"
        show_in_menu = request.form.get("show_in_menu") == "on"
        menu_order = int(request.form.get("menu_order", 0))
        meta_title = request.form.get("meta_title", "").strip()
        meta_description = request.form.get("meta_description", "").strip()

        if not title:
            flash("Title is required", "error")
            return redirect(url_for("main.settings_page_create"))

        slug = slugify(title)
        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            flash("A page with this title already exists", "error")
            return redirect(url_for("main.settings_page_create"))

        page = Page(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            template=template,
            is_published=is_published,
            show_in_menu=show_in_menu,
            menu_order=menu_order,
            meta_title=meta_title or title,
            meta_description=meta_description,
            author_id=current_user.id,
        )
        db.session.add(page)
        db.session.commit()
        flash(f"Page '{title}' created", "success")
        return redirect(url_for("main.settings_pages"))

    return render_template("settings/page_edit.html", page=None, mode="create")


@main_blueprint.route("/settings/pages/<int:page_id>/edit", methods=["GET", "POST"])
@login_required
def settings_page_edit(page_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    page = Page.query.get_or_404(page_id)

    if request.method == "POST":
        page.title = request.form.get("title", "").strip()
        page.content = request.form.get("content", "")
        page.excerpt = request.form.get("excerpt", "").strip()
        page.template = request.form.get("template", "default")
        page.is_published = request.form.get("is_published") == "on"
        page.show_in_menu = request.form.get("show_in_menu") == "on"
        page.menu_order = int(request.form.get("menu_order", 0))
        page.meta_title = request.form.get("meta_title", "").strip()
        page.meta_description = request.form.get("meta_description", "").strip()
        page.og_title = request.form.get("og_title", "").strip()
        page.og_description = request.form.get("og_description", "").strip()
        page.og_image = request.form.get("og_image", "").strip()

        new_slug = slugify(page.title)
        existing = Page.query.filter(Page.slug == new_slug, Page.id != page.id).first()
        if existing:
            flash("A page with this title already exists", "error")
        else:
            page.slug = new_slug
            db.session.commit()
            flash(f"Page '{page.title}' updated", "success")
            return redirect(url_for("main.settings_pages"))

    return render_template("settings/page_edit.html", page=page, mode="edit")


@main_blueprint.route("/settings/pages/<int:page_id>/delete", methods=["POST"])
@login_required
def settings_page_delete(page_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    page = Page.query.get_or_404(page_id)
    title = page.title
    db.session.delete(page)
    db.session.commit()
    flash(f"Page '{title}' deleted", "success")
    return redirect(url_for("main.settings_pages"))


@main_blueprint.route("/settings/pages/<int:page_id>/toggle", methods=["POST"])
@login_required
def settings_page_toggle(page_id):
    if not current_user.has_permission("settings", "update"):
        abort(403)

    page = Page.query.get_or_404(page_id)
    page.is_published = not page.is_published
    db.session.commit()
    status = "published" if page.is_published else "unpublished"
    flash(f"Page '{page.title}' {status}", "success")
    return redirect(url_for("main.settings_pages"))


# ── API: Page CRUD ────────────────────────────────────────────────────
@main_blueprint.route("/api/settings/pages", methods=["GET"])
@login_required
def api_pages_list():
    if not current_user.has_permission("settings", "read"):
        return jsonify({"error": "Forbidden"}), 403
    pages = Page.query.order_by(Page.menu_order.asc()).all()
    return jsonify({"pages": [p.to_dict() for p in pages]})


@main_blueprint.route("/api/settings/pages/<int:page_id>", methods=["GET"])
@login_required
def api_page_detail(page_id):
    if not current_user.has_permission("settings", "read"):
        return jsonify({"error": "Forbidden"}), 403
    page = Page.query.get_or_404(page_id)
    return jsonify({"page": page.to_dict()})
