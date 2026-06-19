from routes import main_blueprint
from .common_imports import *

@main_blueprint.route("/api/penyangkalan", methods=["POST"])
@login_required
def create_penyangkalan():
    if not current_user.is_owner():
        abort(403)
    data = request.get_json() or {}
    for k in ("title", "content", "section_order"):
        if k not in data:
            abort(400, "title, content, section_order are required.")
    p = Penyangkalan(
        title=data["title"],
        content=data["content"],
        section_order=data["section_order"],
    )
    p.is_active = data.get("is_active", True)
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@main_blueprint.route("/api/penyangkalan/<int:pid>", methods=["PUT"])
@login_required
def update_penyangkalan(pid):
    if not current_user.is_owner():
        abort(403)
    p = Penyangkalan.query.get_or_404(pid)
    data = request.get_json() or {}
    for f in ("title", "content", "section_order", "is_active"):
        if f in data:
            setattr(p, f, data[f])
    db.session.commit()
    return jsonify(p.to_dict()), 200


@main_blueprint.route("/api/penyangkalan/<int:pid>", methods=["DELETE"])
@login_required
def delete_penyangkalan(pid):
    if not current_user.is_owner():
        abort(403)
    p = Penyangkalan.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return "", 204


@main_blueprint.route("/api/pedomanhak", methods=["POST"])
@login_required
def create_pedomanhak():
    if not current_user.is_owner():
        abort(403)
    data = request.get_json() or {}
    for k in ("title", "content", "section_order"):
        if k not in data:
            abort(400, "title, content, section_order are required.")
    ph = PedomanHak(
        title=data["title"],
        content=data["content"],
        section_order=data["section_order"],
    )
    ph.is_active = data.get("is_active", True)
    db.session.add(ph)
    db.session.commit()
    return jsonify(ph.to_dict()), 201


@main_blueprint.route("/api/pedomanhak/<int:pid>", methods=["PUT"])
@login_required
def update_pedomanhak(pid):
    if not current_user.is_owner():
        abort(403)
    ph = PedomanHak.query.get_or_404(pid)
    data = request.get_json() or {}
    for f in ("title", "content", "section_order", "is_active"):
        if f in data:
            setattr(ph, f, data[f])
    db.session.commit()
    return jsonify(ph.to_dict()), 200


@main_blueprint.route("/api/pedomanhak/<int:pid>", methods=["DELETE"])
@login_required
def delete_pedomanhak(pid):
    if not current_user.is_owner():
        abort(403)
    ph = PedomanHak.query.get_or_404(pid)
    db.session.delete(ph)
    db.session.commit()
    return "", 204


@main_blueprint.route("/api/privacy-policy", methods=["POST"])
@login_required
def create_privacy_policy():
    if not current_user.is_owner():
        abort(403)
    data = request.get_json() or {}
    for k in ("title", "content", "section_order"):
        if k not in data:
            abort(400, "title, content, section_order are required.")
    pp = PrivacyPolicy(
        title=data["title"],
        content=data["content"],
        section_order=data["section_order"],
    )
    pp.is_active = data.get("is_active", True)
    db.session.add(pp)
    db.session.commit()
    return jsonify(pp.to_dict()), 201


@main_blueprint.route("/api/privacy-policy/<int:pid>", methods=["PUT"])
@login_required
def update_privacy_policy(pid):
    if not current_user.is_owner():
        abort(403)
    pp = PrivacyPolicy.query.get_or_404(pid)
    data = request.get_json() or {}
    for f in ("title", "content", "section_order", "is_active"):
        if f in data:
            setattr(pp, f, data[f])
    db.session.commit()
    return jsonify(pp.to_dict()), 200


@main_blueprint.route("/api/privacy-policy/<int:pid>", methods=["DELETE"])
@login_required
def delete_privacy_policy(pid):
    if not current_user.is_owner():
        abort(403)
    pp = PrivacyPolicy.query.get_or_404(pid)
    db.session.delete(pp)
    db.session.commit()
    return "", 204


@main_blueprint.route("/api/media-guidelines", methods=["POST"])
@login_required
def create_media_guideline():
    if not current_user.is_owner():
        abort(403)
    data = request.get_json() or {}
    for k in ("title", "content", "section_order"):
        if k not in data:
            abort(400, "title, content, section_order are required.")
    mg = MediaGuideline(
        title=data["title"],
        content=data["content"],
        section_order=data["section_order"],
    )
    mg.is_active = data.get("is_active", True)
    db.session.add(mg)
    db.session.commit()
    return jsonify(mg.to_dict()), 201


@main_blueprint.route("/api/media-guidelines/<int:mid>", methods=["PUT"])
@login_required
def update_media_guideline(mid):
    if not current_user.is_owner():
        abort(403)
    mg = MediaGuideline.query.get_or_404(mid)
    data = request.get_json() or {}
    for f in ("title", "content", "section_order", "is_active"):
        if f in data:
            setattr(mg, f, data[f])
    db.session.commit()
    return jsonify(mg.to_dict()), 200


@main_blueprint.route("/api/media-guidelines/<int:mid>", methods=["DELETE"])
@login_required
def delete_media_guideline(mid):
    if not current_user.is_owner():
        abort(403)
    mg = MediaGuideline.query.get_or_404(mid)
    db.session.delete(mg)
    db.session.commit()
    return "", 204

@main_blueprint.route("/api/settings/stats", methods=["GET"])
@login_required
def settings_stats():
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
        abort(403)

    total_users = User.query.count()
    total_news = News.query.count()
    total_images = Image.query.count()
    total_videos = YouTubeVideo.query.count()

    return jsonify(
        {
            "total_users": total_users,
            "total_news": total_news,
            "total_images": total_images,
            "total_videos": total_videos,
        }
    )


@main_blueprint.route("/api/privacy-policy", methods=["GET"])
def get_privacy_policy():
    policies = (
        PrivacyPolicy.query.filter_by(is_active=True)
        .order_by(PrivacyPolicy.section_order)
        .all()
    )
    return jsonify([policy.to_dict() for policy in policies])


@main_blueprint.route("/api/media-guidelines", methods=["GET"])
def get_media_guidelines():
    guidelines = (
        MediaGuideline.query.filter_by(is_active=True)
        .order_by(MediaGuideline.section_order)
        .all()
    )
    return jsonify([guideline.to_dict() for guideline in guidelines])


@main_blueprint.route("/api/visi-misi", methods=["GET"])
def get_visi_misi():
    visi_misi_items = (
        VisiMisi.query.filter_by(is_active=True).order_by(VisiMisi.section_order).all()
    )
    return jsonify([item.to_dict() for item in visi_misi_items])


@main_blueprint.route("/api/penyangkalan", methods=["GET"])
def get_penyangkalan():
    penyangkalan_items = (
        Penyangkalan.query.filter_by(is_active=True)
        .order_by(Penyangkalan.section_order)
        .all()
    )
    return jsonify([item.to_dict() for item in penyangkalan_items])


@main_blueprint.route("/api/pedomanhak", methods=["GET"])
def get_pedomanhak():
    pedomanhak_items = (
        PedomanHak.query.filter_by(is_active=True)
        .order_by(PedomanHak.section_order)
        .all()
    )
    return jsonify([item.to_dict() for item in pedomanhak_items])


@main_blueprint.route("/api/contact-details", methods=["GET"])
def get_contact_details():
    details = ContactDetail.query.order_by(ContactDetail.section_order).all()
    return jsonify([d.to_dict() for d in details])


@main_blueprint.route("/api/contact-details/<int:detail_id>", methods=["GET"])
def get_contact_detail(detail_id):
    detail = ContactDetail.query.get_or_404(detail_id)
    return jsonify(detail.to_dict())


@main_blueprint.route("/api/contact-details", methods=["POST"])
@login_required
def create_contact_detail():
    if not current_user.is_owner():
        abort(403)
    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")
    order = data.get("section_order")
    if not title or not content or order is None:
        abort(400, "Title, content, and section_order are required.")
    detail = ContactDetail(
        title=title,
        content=content,
        section_order=order,
        icon_class=data.get("icon_class"),
        link=data.get("link"),
    )
    db.session.add(detail)
    db.session.commit()
    return jsonify(detail.to_dict()), 201


@main_blueprint.route("/api/contact-details/<int:detail_id>", methods=["PUT"])
@login_required
def update_contact_detail(detail_id):
    if not current_user.is_owner():
        abort(403)
    detail = ContactDetail.query.get_or_404(detail_id)
    data = request.get_json() or {}
    for f in ("title", "content", "section_order", "icon_class", "link", "is_active"):
        if f in data:
            setattr(detail, f, data[f])
    db.session.commit()
    return jsonify(detail.to_dict()), 200


@main_blueprint.route("/api/contact-details/<int:detail_id>", methods=["DELETE"])
@login_required
def delete_contact_detail(detail_id):
    if not current_user.is_owner():
        abort(403)
    detail = ContactDetail.query.get_or_404(detail_id)
    db.session.delete(detail)
    db.session.commit()
    return "", 204


@main_blueprint.route("/api/team-members", methods=["GET"])
def get_team_members():
    members = TeamMember.query.order_by(TeamMember.group, TeamMember.member_order).all()
    return jsonify([m.to_dict() for m in members])


@main_blueprint.route("/api/team-members/<int:member_id>", methods=["GET"])
def get_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    return jsonify(member.to_dict())


@main_blueprint.route("/api/team-members", methods=["POST"])
@login_required
def create_team_member():
    if not current_user.is_owner():
        abort(403)
    data = request.get_json() or {}
    for k in ("name", "title", "group", "member_order"):
        if k not in data:
            abort(400, f"Field '{k}' is required.")
    member = TeamMember(
        name=data["name"],
        title=data["title"],
        group=data["group"],
        member_order=data["member_order"],
    )
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@main_blueprint.route("/api/team-members/<int:member_id>", methods=["PUT"])
@login_required
def update_team_member(member_id):
    if not current_user.is_owner():
        abort(403)
    member = TeamMember.query.get_or_404(member_id)
    data = request.get_json() or {}
    for f in ("name", "title", "group", "member_order", "is_active"):
        if f in data:
            setattr(member, f, data[f])
    db.session.commit()
    return jsonify(member.to_dict()), 200


@main_blueprint.route("/api/team-members/<int:member_id>", methods=["DELETE"])
@login_required
def delete_team_member(member_id):
    if not current_user.is_owner():
        abort(403)
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return "", 204

