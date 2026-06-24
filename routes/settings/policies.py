"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Policy and Legal Routes

This module handles all policy and legal content management routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/privacy-policy", methods=["GET", "POST"])
@login_required
def settings_privacy_policy():
    # Allow access to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    policies = PrivacyPolicy.query.order_by(PrivacyPolicy.section_order).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title")
            content = request.form.get("content")
            section_order = request.form.get("section_order", type=int)

            policy = PrivacyPolicy(
                title=title, content=content, section_order=section_order
            )
            db.session.add(policy)

        elif action == "update":
            policy_id = request.form.get("policy_id", type=int)
            policy = PrivacyPolicy.query.get_or_404(policy_id)

            policy.title = request.form.get("title")
            policy.content = request.form.get("content")
            policy.section_order = request.form.get("section_order", type=int)
            policy.is_active = "is_active" in request.form

        elif action == "delete":
            policy_id = request.form.get("policy_id", type=int)
            policy = PrivacyPolicy.query.get_or_404(policy_id)
            db.session.delete(policy)

        db.session.commit()
        return redirect(url_for("main.settings_privacy_policy"))

    return render_template("settings/policy_management.html", policies=policies)


@main_blueprint.route("/settings/media-guidelines", methods=["GET", "POST"])
@login_required
def settings_media_guidelines():
    # Allow access to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    guidelines = MediaGuideline.query.order_by(MediaGuideline.section_order).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title")
            content = request.form.get("content")
            section_order = request.form.get("section_order", type=int)

            guideline = MediaGuideline(
                title=title, content=content, section_order=section_order
            )
            db.session.add(guideline)

        elif action == "update":
            guideline_id = request.form.get("guideline_id", type=int)
            guideline = MediaGuideline.query.get_or_404(guideline_id)

            guideline.title = request.form.get("title")
            guideline.content = request.form.get("content")
            guideline.section_order = request.form.get("section_order", type=int)
            guideline.is_active = "is_active" in request.form

        elif action == "delete":
            guideline_id = request.form.get("guideline_id", type=int)
            guideline = MediaGuideline.query.get_or_404(guideline_id)
            db.session.delete(guideline)

        db.session.commit()
        return redirect(url_for("main.settings_media_guidelines"))

    return render_template("settings/mediaguidelines_management.html", guidelines=guidelines)


@main_blueprint.route("/settings/visi-misi", methods=["GET", "POST"])
@login_required
def settings_visi_misi():
    if not current_user.is_owner():
        abort(403)

    visi_misi_sections = VisiMisi.query.order_by(VisiMisi.section_order).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title")
            content = request.form.get("content")
            section_order = request.form.get("section_order", type=int)

            visi_misi = VisiMisi(
                title=title, content=content, section_order=section_order
            )
            db.session.add(visi_misi)

        elif action == "update":
            visi_misi_id = request.form.get("visi_misi_id", type=int)
            visi_misi = VisiMisi.query.get_or_404(visi_misi_id)

            visi_misi.content = request.form.get("content")
            visi_misi.section_order = request.form.get("section_order", type=int)
            visi_misi.is_active = "is_active" in request.form

        elif action == "delete":
            visi_misi_id = request.form.get("visi_misi_id", type=int)
            visi_misi = VisiMisi.query.get_or_404(visi_misi_id)
            db.session.delete(visi_misi)

        db.session.commit()
        return redirect(url_for("main.settings_visi_misi"))

    return render_template(
        "settings/visimisi_management.html", visi_misi_sections=visi_misi_sections
    )


@main_blueprint.route("/settings/pedomanhak", methods=["GET", "POST"])
@login_required
def settings_pedomanhak():
    # Allow access to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    pedomanhak_sections = PedomanHak.query.order_by(PedomanHak.section_order).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title")
            content = request.form.get("content")
            section_order = request.form.get("section_order", type=int)

            pedomanhak = PedomanHak(
                title=title, content=content, section_order=section_order
            )
            db.session.add(pedomanhak)

        elif action == "update":
            pedomanhak_id = request.form.get("pedomanhak_id", type=int)
            pedomanhak = PedomanHak.query.get_or_404(pedomanhak_id)

            pedomanhak.title = request.form.get("title")
            pedomanhak.content = request.form.get("content")
            pedomanhak.section_order = request.form.get("section_order", type=int)
            pedomanhak.is_active = "is_active" in request.form

        elif action == "delete":
            pedomanhak_id = request.form.get("pedomanhak_id", type=int)
            pedomanhak = PedomanHak.query.get_or_404(pedomanhak_id)
            db.session.delete(pedomanhak)

        db.session.commit()
        return redirect(url_for("main.settings_pedomanhak"))

    return render_template(
        "settings/pedomanhak_management.html", pedomanhak_sections=pedomanhak_sections
    )


@main_blueprint.route("/settings/penyangkalan", methods=["GET", "POST"])
@login_required
def settings_penyangkalan():
    # Allow access to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    penyangkalan_sections = Penyangkalan.query.order_by(
        Penyangkalan.section_order
    ).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title")
            content = request.form.get("content")
            section_order = request.form.get("section_order", type=int)

            penyangkalan = Penyangkalan(
                title=title, content=content, section_order=section_order
            )
            db.session.add(penyangkalan)

        elif action == "update":
            penyangkalan_id = request.form.get("penyangkalan_id", type=int)
            penyangkalan = Penyangkalan.query.get_or_404(penyangkalan_id)

            penyangkalan.title = request.form.get("title")
            penyangkalan.content = request.form.get("content")
            penyangkalan.section_order = request.form.get("section_order", type=int)
            penyangkalan.is_active = "is_active" in request.form

        elif action == "delete":
            penyangkalan_id = request.form.get("penyangkalan_id", type=int)
            penyangkalan = Penyangkalan.query.get_or_404(penyangkalan_id)
            db.session.delete(penyangkalan)

        db.session.commit()
        return redirect(url_for("main.settings_penyangkalan"))

    return render_template(
        "settings/penyangkalan_management.html", penyangkalan_sections=penyangkalan_sections
    )
