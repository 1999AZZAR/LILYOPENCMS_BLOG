"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Brand Routes

This module handles brand identity and social media management routes.
"""

from routes import main_blueprint
from .common_imports import *
import os
from flask import jsonify


@main_blueprint.route("/settings/social-media")
@login_required
def settings_social_media():
    """Admin page for managing social media links."""
    if not current_user.role in [UserRole.ADMIN, UserRole.SUPERUSER]:
        current_app.logger.warning(
            f"Forbidden access attempt to /settings/social-media by user {current_user.username} (ID: {current_user.id})"
        )
        abort(
            403, "You do not have permission to access this page."
        )
    return render_template("settings/social_media_management.html")


@main_blueprint.route("/settings/brand-identity")
@login_required
def settings_brand_identity():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    brand_info = BrandIdentity.query.first()
    if not brand_info:
        brand_info = BrandIdentity()
        db.session.add(brand_info)
        db.session.commit()
    return render_template("settings/brand_management.html", brand_info=brand_info)


@main_blueprint.route("/settings/brand/info")
@login_required
def settings_brand_info():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    brand_info = BrandIdentity.query.first()
    if not brand_info:
        brand_info = BrandIdentity()
        db.session.add(brand_info)
        db.session.commit()
    return render_template("settings/brand_info.html", brand_info=brand_info)


@main_blueprint.route("/settings/brand/design")
@login_required
def settings_brand_design():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    brand_info = BrandIdentity.query.first()
    if not brand_info:
        brand_info = BrandIdentity()
        db.session.add(brand_info)
        db.session.commit()
    return render_template("settings/brand_design.html", brand_info=brand_info)


@main_blueprint.route("/settings/brand/assets")
@login_required
def settings_brand_assets():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    brand_info = BrandIdentity.query.first()
    if not brand_info:
        brand_info = BrandIdentity()
        db.session.add(brand_info)
        db.session.commit()
    return render_template("settings/brand_assets.html", brand_info=brand_info)


@main_blueprint.route("/settings/brand/colors")
@login_required
def settings_brand_colors():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    brand_info = BrandIdentity.query.first()
    if not brand_info:
        brand_info = BrandIdentity()
        db.session.add(brand_info)
        db.session.commit()
    return render_template("settings/brand_colors.html", brand_info=brand_info)


@main_blueprint.route("/api/brand-identity", methods=["GET"])
@login_required
def get_brand_identity():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    brand = BrandIdentity.query.first()
    if not brand:
        return jsonify({}), 200
    return jsonify(brand.to_dict()), 200


@main_blueprint.route("/api/brand-info", methods=["GET"])
def get_public_brand_info():
    """Public endpoint for getting brand info (no auth required)"""
    from models import BrandIdentity
    db.session.expire_all()
    brand = BrandIdentity.query.first()
    if brand:
        try:
            db.session.refresh(brand)
        except Exception:
            pass
    if not brand:
        return jsonify({
            "brand_name": "LilyOpenCMS",
            "card_design": "classic",
            "homepage_design": "news",
            "categories_display_location": "none"
        }), 200
    return jsonify(brand.to_dict()), 200


@main_blueprint.route("/api/brand-identity", methods=["POST"])
@login_required
def update_brand_identity():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    from models import BrandIdentity
    from routes.routes_helper import save_brand_asset_file
    brand = BrandIdentity.query.first()
    if not brand:
        brand = BrandIdentity()
        db.session.add(brand)
    updated = False
    fixed_urls = {
        "logo_header": "/static/pic/logo.png",
        "logo_footer": "/static/pic/logo_footer.png",
        "favicon": "/static/pic/favicon.png",
        "placeholder_image": "/static/pic/placeholder.png",
    }
    for field in ["logo_header", "logo_footer", "favicon", "placeholder_image"]:
        file = request.files.get(field)
        if file:
            try:
                save_brand_asset_file(file, field)
            except Exception as e:
                return jsonify({"error": str(e)}), 400
            setattr(brand, field, fixed_urls[field])
            updated = True
    for field, url in fixed_urls.items():
        setattr(brand, field, url)

    for toggle in ["enable_comments", "enable_ratings"]:
        val = request.form.get(toggle)
        if val is not None:
            setattr(brand, toggle, val.lower() in ['true', '1', 'on', 'yes'])
            updated = True

    if updated:
        db.session.commit()
        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("brand_info*")
        except ImportError:
            pass
    return jsonify(brand.to_dict()), 200


@main_blueprint.route("/api/brand-identity/text", methods=["POST"])
@login_required
def update_brand_identity_text():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)

    from models import BrandIdentity
    data = request.get_json()
    field = data.get("field")
    value = data.get("value")

    if field is None:
        return jsonify({"error": "Missing field"}), 400

    allowed = [
        "brand_name", "tagline", "brand_description",
        "homepage_design", "categories_display_location", "card_design",
        "enable_comments", "enable_ratings", "enable_ads", "enable_campaigns",
        "enable_videos", "enable_gallery", "enable_albums", "enable_news",
        "enable_premium", "enable_about", "enable_bookmarks",
        "enable_reading_history", "enable_community", "enable_user_stats",
        "min_story_word_count", "min_chapter_word_count"
    ]
    if field not in allowed:
        return jsonify({"error": "Invalid field"}), 400

    brand = BrandIdentity.query.first()
    if not brand:
        brand = BrandIdentity()
        db.session.add(brand)

    toggle_fields = [
        "enable_comments", "enable_ratings", "enable_ads", "enable_campaigns",
        "enable_videos", "enable_gallery", "enable_albums", "enable_news",
        "enable_premium", "enable_about", "enable_bookmarks",
        "enable_reading_history", "enable_community", "enable_user_stats"
    ]
    if field in toggle_fields:
        setattr(brand, field, str(value).lower() in ['true', '1', 'on', 'yes'])
    elif field in ["min_story_word_count", "min_chapter_word_count"]:
        try:
            setattr(brand, field, int(value))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid integer value"}), 400
    else:
        setattr(brand, field, value)

    db.session.commit()

    try:
        from optimizations import invalidate_cache_pattern
        invalidate_cache_pattern("brand_info*")
    except ImportError:
        pass

    return jsonify(brand.to_dict()), 200


CSS_VAR_TO_DB = {
    "--primary": "color_primary",
    "--primary-foreground": "color_primary_foreground",
    "--secondary": "color_secondary",
    "--secondary-foreground": "color_secondary_foreground",
    "--accent": "color_accent",
    "--accent-foreground": "color_accent_foreground",
    "--background": "color_background",
    "--foreground": "color_foreground",
}


@main_blueprint.route("/api/brand-colors", methods=["POST"])
@login_required
def update_brand_colors():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    data = request.get_json()
    variable = data.get("variable")
    value = data.get("value")
    if not variable or not value:
        return jsonify({"error": "Missing variable or value"}), 400

    # Save to BrandIdentity DB columns so inline style in base.html stays in sync
    from models import BrandIdentity
    brand = BrandIdentity.query.first()
    if brand and variable in CSS_VAR_TO_DB:
        setattr(brand, CSS_VAR_TO_DB[variable], value)
        db.session.commit()

    # Also write to CSS file for fallback
    css_path = os.path.join(current_app.root_path, "static/css/base_css.css")
    try:
        import fcntl
        with open(css_path, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            lines = f.readlines()
            f.seek(0)
            in_root = False
            for i, line in enumerate(lines):
                if line.strip().startswith(":root"):
                    in_root = True
                if in_root and variable in line:
                    parts = line.split(";")
                    new_parts = []
                    for part in parts:
                        if variable in part:
                            new_parts.append(f"    {variable}: {value}")
                        elif part.strip():
                            new_parts.append(part)
                    lines[i] = "; ".join(new_parts) + ";\n"
                    break
                if in_root and "}" in line:
                    break
            f.seek(0)
            f.truncate()
            f.writelines(lines)
            fcntl.flock(f, fcntl.LOCK_UN)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/api/brand-colors", methods=["GET"])
@login_required
def get_brand_colors():
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    # Prefer BrandIdentity DB values over CSS file (inline style wins)
    from models import BrandIdentity
    brand = BrandIdentity.query.first()
    if brand:
        color_vars = []
        for css_var, db_col in CSS_VAR_TO_DB.items():
            val = getattr(brand, db_col, None)
            if val:
                color_vars.append({"name": css_var, "value": val})
        if color_vars:
            return jsonify(color_vars), 200

    # Fallback: read from CSS file
    css_path = os.path.join(current_app.root_path, "static/css/base_css.css")
    try:
        with open(css_path, "r") as f:
            content = f.read()
        import re
        root_match = re.search(r':root\s*\{([^}]+)\}', content, re.DOTALL)
        if not root_match:
            return jsonify([]), 200
        root_content = root_match.group(1)
        color_vars = []
        lines = root_content.split(';')
        for line in lines:
            line = line.strip()
            if line.startswith('--') and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    var_value = parts[1].strip()
                    if not var_name.endswith('radius'):
                        color_vars.append({"name": var_name, "value": var_value})
        return jsonify(color_vars), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
