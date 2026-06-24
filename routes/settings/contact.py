"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Contact and Team Routes

This module handles contact details and team management routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/contact-details", methods=["GET", "POST"])
@login_required
def settings_contact_details():
    if not current_user.is_owner():
        abort(403)

    contact_details = ContactDetail.query.order_by(ContactDetail.section_order).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title")
            content = request.form.get("content")
            section_order = request.form.get("section_order", type=int)
            icon_class = request.form.get("icon_class")
            link = request.form.get("link")

            detail = ContactDetail(
                title=title,
                content=content,
                section_order=section_order,
                icon_class=icon_class,
                link=link,
            )
            db.session.add(detail)

        elif action == "update":
            detail_id = request.form.get("detail_id", type=int)
            detail = ContactDetail.query.get_or_404(detail_id)

            detail.title = request.form.get("title")
            detail.content = request.form.get("content")
            detail.section_order = request.form.get("section_order", type=int)
            detail.icon_class = request.form.get("icon_class")
            detail.link = request.form.get("link")
            detail.is_active = "is_active" in request.form

        elif action == "delete":
            detail_id = request.form.get("detail_id", type=int)
            detail = ContactDetail.query.get_or_404(detail_id)
            db.session.delete(detail)

        db.session.commit()
        return redirect(url_for("main.settings_contact_details"))

    return render_template(
        "settings/contact_details_management.html", contact_details=contact_details
    )


@main_blueprint.route("/settings/team-members", methods=["GET", "POST"])
@login_required
def settings_team_members():
    if not current_user.is_owner():
        abort(403)

    team_members = TeamMember.query.order_by(
        TeamMember.group, TeamMember.member_order
    ).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            name = request.form.get("name")
            title = request.form.get("title")
            group = request.form.get("group")
            member_order = request.form.get("member_order", type=int)
            member = TeamMember(
                name=name, title=title, group=group, member_order=member_order
            )
            db.session.add(member)

        elif action == "update":
            member_id = request.form.get("member_id", type=int)
            member = TeamMember.query.get_or_404(member_id)

            member.name = request.form.get("name")
            member.title = request.form.get("title")
            member.group = request.form.get("group")
            member.member_order = request.form.get("member_order", type=int)
            member.is_active = "is_active" in request.form

        elif action == "delete":
            member_id = request.form.get("member_id", type=int)
            member = TeamMember.query.get_or_404(member_id)
            db.session.delete(member)

        db.session.commit()
        return redirect(url_for("main.settings_team_members"))

    return render_template("settings/team_members_management.html", team_members=team_members)
