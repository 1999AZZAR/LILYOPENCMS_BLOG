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
from models import Album, AlbumChapter, News, Category, User, UserRole

@main_blueprint.route("/api/albums", methods=["GET"])
@login_required
def get_albums_api():
    """
    API endpoint to retrieve a list of albums with filtering.
    Requires user to be logged in and verified.
    """
    # Permission: Only verified users can access the management API
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted to access /api/albums"
        )
        return jsonify({"error": "Account not verified"}), 403

    # --- Get filters from the request ---
    search_query = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "")
    status_filter = request.args.get("status", "")  # 'visible', 'hidden', or 'archived'
    premium_filter = request.args.get("premium", "")  # 'regular' or 'premium'
    user_filter = request.args.get("user", "")  # 'owned', 'by_admin', 'by_general', 'all'
    archived_filter = request.args.get("archived", "")

    # --- Base query ---
    query = Album.query

    # --- Apply standard filters ---
    if search_query:
        query = query.filter(
            Album.title.ilike(f"%{search_query}%")
            | Album.description.ilike(f"%{search_query}%")
        )

    if category_filter:
        try:
            category_id = int(category_filter)
            query = query.filter(Album.category_id == category_id)
        except ValueError:
            current_app.logger.warning(f"Invalid category_id: {category_filter}")
            return jsonify({"error": "Invalid category ID"}), 400

    if status_filter:
        if status_filter == "visible":
            query = query.filter(Album.is_visible == True)
        elif status_filter == "hidden":
            query = query.filter(Album.is_visible == False)
        elif status_filter == "archived":
            query = query.filter(Album.is_archived == True)
    
    if premium_filter:
        if premium_filter == "regular":
            query = query.filter(Album.is_premium == False)
        elif premium_filter == "premium":
            query = query.filter(Album.is_premium == True)

    # --- Apply user/ownership filter based on current user's role ---
    if current_user.effective_tier == 0:
        if user_filter == "owned":
            query = query.filter(Album.user_id == current_user.id)
        elif user_filter == "by_admin":
            query = query.join(Album.author).filter(User.role == UserRole.ADMIN)
        elif user_filter == "by_general":
            query = query.join(Album.author).filter(User.role == UserRole.GENERAL)
        # 'all' for SUPERUSER means no additional user filtering

    elif current_user.role == UserRole.ADMIN:
        allowed_user_ids = [current_user.id]
        general_users = (
            User.query.filter_by(role=UserRole.GENERAL).with_entities(User.id).all()
        )
        allowed_user_ids.extend([u.id for u in general_users])

        if user_filter == "owned":
            query = query.filter(Album.user_id == current_user.id)
        elif user_filter == "by_general":
            query = query.join(Album.author).filter(User.role == UserRole.GENERAL)
        else:  # 'all' for ADMIN defaults to owned + general users' albums
            query = query.filter(Album.user_id.in_(allowed_user_ids))

    else:  # UserRole.GENERAL
        query = query.filter(Album.user_id == current_user.id)

    # --- Exclude archived albums by default ---
    if archived_filter == "true":
        query = query.filter(Album.is_archived == True)
    elif archived_filter == "false":
        query = query.filter(Album.is_archived == False)
    elif request.args.get("include_archived", "false").lower() != "true":
        query = query.filter(Album.is_archived == False)

    # --- Apply ordering ---
    query = query.order_by(Album.created_at.desc())

    # --- Apply Pagination ---
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ALBUMS_PER_PAGE', 6)
    
    albums_pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    # --- Format the response ---
    response_data = []
    for album in albums_pagination.items:
        album_dict = album.to_dict()
        response_data.append(album_dict)

    return jsonify({
        'items': response_data,
        'page': albums_pagination.page,
        'per_page': albums_pagination.per_page,
        'total_pages': albums_pagination.pages,
        'total_items': albums_pagination.total
    })


@main_blueprint.route("/api/albums", methods=["POST"])
@login_required
def create_album_api():
    """
    API endpoint to create a new album.
    Requires user to be logged in and verified.
    """
    # Permission: Only verified users can create albums
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted POST /api/albums"
        )
        return jsonify({"error": "Account not verified"}), 403

    # Handle both form data and JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    cover_image_id = data.get("cover_image_id")

    # --- Validate required fields ---
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    category_id_str = data.get("category_id", data.get("category", "")).strip()

    missing_fields = []
    if not title:
        missing_fields.append("title")
    if not category_id_str:
        missing_fields.append("category")
    if missing_fields:
        return jsonify(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"}
        ), 400

    # --- Validate category exists ---
    try:
        category_id = int(category_id_str)
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid category ID"}), 400

    # --- Convert boolean values (handle both string and boolean) ---
    is_premium_raw = data.get("is_premium", False)
    is_visible_raw = data.get("is_visible", True)
    is_completed_raw = data.get("is_completed", False)
    is_hiatus_raw = data.get("is_hiatus", False)
    
    is_premium = bool(is_premium_raw) if isinstance(is_premium_raw, bool) else str(is_premium_raw).lower() == "true"
    is_visible = bool(is_visible_raw) if isinstance(is_visible_raw, bool) else str(is_visible_raw).lower() == "true"
    is_completed = bool(is_completed_raw) if isinstance(is_completed_raw, bool) else str(is_completed_raw).lower() == "true"
    is_hiatus = bool(is_hiatus_raw) if isinstance(is_hiatus_raw, bool) else str(is_hiatus_raw).lower() == "true"

    # --- Create the Album object ---
    try:
        # Get SEO fields
        meta_description = data.get("meta_description", "").strip()
        meta_keywords = data.get("meta_keywords", "").strip()
        seo_slug = data.get("seo_slug", "").strip()
        canonical_url = data.get("canonical_url", "").strip()
        og_title = data.get("og_title", "").strip()
        og_description = data.get("og_description", "").strip()
        og_image = data.get("og_image", "").strip()
        meta_author = data.get("meta_author", "").strip()
        meta_language = data.get("meta_language", "id").strip()
        meta_robots = data.get("meta_robots", "index, follow").strip()
        structured_data_type = data.get("structured_data_type", "Book").strip()
        
        album = Album(
            title=title,
            description=description,
            category_id=category.id,
            is_premium=is_premium,
            is_visible=is_visible,
            is_completed=is_completed,
            is_hiatus=is_hiatus,
            is_archived=False,
            user_id=current_user.id,
            cover_image_id=int(cover_image_id) if cover_image_id and cover_image_id.isdigit() else None,
            # SEO Fields
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            seo_slug=seo_slug,
            canonical_url=canonical_url,
            og_title=og_title,
            og_description=og_description,
            og_image=og_image,
            meta_author=meta_author,
            meta_language=meta_language,
            meta_robots=meta_robots,
            structured_data_type=structured_data_type,
        )

        album.validate()
        db.session.add(album)
        db.session.flush()  # Get the album ID
        
        # --- Handle chapters if provided ---
        chapters_data = data.get("chapters", [])
        if chapters_data:
            for chapter_data in chapters_data:
                news_id = chapter_data.get("news_id")
                chapter_number = chapter_data.get("chapter_number")
                chapter_title = chapter_data.get("chapter_title")
                
                if news_id and chapter_number and chapter_title:
                    # Verify news exists
                    news = News.query.get(news_id)
                    if not news:
                        continue  # Skip invalid news
                    
                    chapter = AlbumChapter(
                        album_id=album.id,
                        news_id=news_id,
                        chapter_number=chapter_number,
                        chapter_title=chapter_title,
                        is_visible=True
                    )
                    chapter.validate()
                    db.session.add(chapter)
            
            # Update album chapter count
            album.update_chapter_count()
        
        db.session.commit()

        current_app.logger.info(
            f"Album '{album.title}' created by user {current_user.username}"
        )
        return jsonify({"message": "Album created successfully", "album": album.to_dict()}), 201

    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Validation error creating album: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating album: {e}")
        return jsonify({"error": "Failed to create album"}), 500


@main_blueprint.route("/api/albums/<int:album_id>", methods=["GET"])
@login_required
def get_album_detail_api(album_id):
    """
    API endpoint to retrieve a specific album by ID.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify(album.to_dict())


@main_blueprint.route("/api/albums/<int:album_id>", methods=["PUT"])
@login_required
def update_album_api(album_id):
    """
    API endpoint to update an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    # Handle both form data and JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    cover_image_id = data.get("cover_image_id")

    # --- Validate required fields ---
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    category_id_str = data.get("category_id", data.get("category", "")).strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not category_id_str:
        return jsonify({"error": "Category is required"}), 400

    # --- Validate category exists ---
    try:
        category_id = int(category_id_str)
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid category ID"}), 400

    # --- Convert boolean values (handle both string and boolean) ---
    is_premium_raw = data.get("is_premium", False)
    is_visible_raw = data.get("is_visible", True)
    is_completed_raw = data.get("is_completed", False)
    is_hiatus_raw = data.get("is_hiatus", False)
    
    is_premium = bool(is_premium_raw) if isinstance(is_premium_raw, bool) else str(is_premium_raw).lower() == "true"
    is_visible = bool(is_visible_raw) if isinstance(is_visible_raw, bool) else str(is_visible_raw).lower() == "true"
    is_completed = bool(is_completed_raw) if isinstance(is_completed_raw, bool) else str(is_completed_raw).lower() == "true"
    is_hiatus = bool(is_hiatus_raw) if isinstance(is_hiatus_raw, bool) else str(is_hiatus_raw).lower() == "true"

    try:
        # Get SEO fields
        meta_description = data.get("meta_description", "").strip()
        meta_keywords = data.get("meta_keywords", "").strip()
        seo_slug = data.get("seo_slug", "").strip()
        canonical_url = data.get("canonical_url", "").strip()
        og_title = data.get("og_title", "").strip()
        og_description = data.get("og_description", "").strip()
        og_image = data.get("og_image", "").strip()
        meta_author = data.get("meta_author", "").strip()
        meta_language = data.get("meta_language", "id").strip()
        meta_robots = data.get("meta_robots", "index, follow").strip()
        structured_data_type = data.get("structured_data_type", "Book").strip()
        
        # Update album fields
        album.title = title
        album.description = description
        album.category_id = category.id
        album.is_premium = is_premium
        album.is_visible = is_visible
        album.is_completed = is_completed
        album.is_hiatus = is_hiatus
        album.cover_image_id = int(cover_image_id) if cover_image_id and cover_image_id.isdigit() else None
        # SEO Fields
        album.meta_description = meta_description
        album.meta_keywords = meta_keywords
        album.seo_slug = seo_slug
        album.canonical_url = canonical_url
        album.og_title = og_title
        album.og_description = og_description
        album.og_image = og_image
        album.meta_author = meta_author
        album.meta_language = meta_language
        album.meta_robots = meta_robots
        album.structured_data_type = structured_data_type

        album.validate()
        
        # --- Handle chapters update if provided ---
        chapters_data = data.get("chapters", [])
        if chapters_data:
            # Remove existing chapters
            AlbumChapter.query.filter_by(album_id=album.id).delete()
            
            # Add new chapters
            for chapter_data in chapters_data:
                news_id = chapter_data.get("news_id")
                chapter_number = chapter_data.get("chapter_number")
                chapter_title = chapter_data.get("chapter_title")
                
                if news_id and chapter_number and chapter_title:
                    # Verify news exists
                    news = News.query.get(news_id)
                    if not news:
                        continue  # Skip invalid news
                    
                    chapter = AlbumChapter(
                        album_id=album.id,
                        news_id=news_id,
                        chapter_number=chapter_number,
                        chapter_title=chapter_title,
                        is_visible=True
                    )
                    chapter.validate()
                    db.session.add(chapter)
            
            # Update album chapter count
            album.update_chapter_count()
        
        db.session.commit()

        current_app.logger.info(
            f"Album '{album.title}' updated by user {current_user.username}"
        )
        return jsonify({"message": "Album updated successfully", "album": album.to_dict()})

    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Validation error updating album: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating album: {e}")
        return jsonify({"error": "Failed to update album"}), 500


@main_blueprint.route("/api/albums/<int:album_id>", methods=["DELETE"])
@login_required
def delete_album_api(album_id):
    """
    API endpoint to delete an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    try:
        album_title = album.title
        db.session.delete(album)
        db.session.commit()

        current_app.logger.info(
            f"Album '{album_title}' deleted by user {current_user.username}"
        )
        return jsonify({"message": "Album deleted successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting album: {e}")
        return jsonify({"error": "Failed to delete album"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/chapters", methods=["POST"])
@login_required
def add_chapter_to_album_api(album_id):
    """
    API endpoint to add a chapter (news article) to an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    # Handle both form data and JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # --- Validate required fields ---
    chapter_title = data.get("chapter_title", "").strip()
    news_id_str = data.get("news_id", "").strip()
    chapter_number_str = data.get("chapter_number", "").strip()

    missing_fields = []
    if not chapter_title:
        missing_fields.append("chapter_title")
    if not news_id_str:
        missing_fields.append("news_id")
    if not chapter_number_str:
        missing_fields.append("chapter_number")
    if missing_fields:
        return jsonify(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"}
        ), 400

    # --- Validate news article exists and belongs to user ---
    try:
        news_id = int(news_id_str)
        news = News.query.get(news_id)
        if not news:
            return jsonify({"error": "News article not found"}), 404
        
        # Check if user has permission to use this news article
        if current_user.effective_tier >= 3 and news.user_id != current_user.id:
            return jsonify({"error": "Access denied to news article"}), 403
    except ValueError:
        return jsonify({"error": "Invalid news ID"}), 400

    # --- Validate chapter number ---
    try:
        chapter_number = int(chapter_number_str)
        if chapter_number < 1:
            return jsonify({"error": "Chapter number must be at least 1"}), 400
    except ValueError:
        return jsonify({"error": "Invalid chapter number"}), 400

    # --- Check if chapter number already exists in this album ---
    existing_chapter = AlbumChapter.query.filter_by(
        album_id=album_id, chapter_number=chapter_number
    ).first()
    if existing_chapter:
        return jsonify({"error": f"Chapter number {chapter_number} already exists in this album"}), 400

    # --- Check if news article is already used in this album ---
    existing_news = AlbumChapter.query.filter_by(
        album_id=album_id, news_id=news_id
    ).first()
    if existing_news:
        return jsonify({"error": "This news article is already used in this album"}), 400

    try:
        chapter = AlbumChapter(
            album_id=album_id,
            news_id=news_id,
            chapter_title=chapter_title,
            chapter_number=chapter_number,
            is_visible=True
        )

        chapter.validate()
        db.session.add(chapter)
        
        # Update album chapter count
        album.update_chapter_count()
        
        db.session.commit()

        current_app.logger.info(
            f"Chapter '{chapter_title}' added to album '{album.title}' by user {current_user.username}"
        )
        return jsonify({"message": "Chapter added successfully", "chapter": chapter.to_dict()}), 201

    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Validation error adding chapter: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding chapter: {e}")
        return jsonify({"error": "Failed to add chapter"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/chapters/<int:chapter_id>", methods=["PUT"])
@login_required
def update_chapter_api(album_id, chapter_id):
    """
    API endpoint to update a chapter in an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)
    chapter = AlbumChapter.query.get_or_404(chapter_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    # Verify chapter belongs to this album
    if chapter.album_id != album_id:
        return jsonify({"error": "Chapter does not belong to this album"}), 400

    # Handle both form data and JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Validate required fields
    chapter_title = data.get("chapter_title", "").strip()
    chapter_number_str = data.get("chapter_number", "").strip()

    if not chapter_title:
        return jsonify({"error": "Chapter title is required"}), 400

    try:
        chapter_number = int(chapter_number_str) if chapter_number_str else chapter.chapter_number
        if chapter_number < 1:
            return jsonify({"error": "Chapter number must be at least 1"}), 400
    except ValueError:
        return jsonify({"error": "Invalid chapter number"}), 400

    # Check if chapter number already exists in this album (excluding current chapter)
    existing_chapter = AlbumChapter.query.filter_by(
        album_id=album_id, chapter_number=chapter_number
    ).filter(AlbumChapter.id != chapter_id).first()
    if existing_chapter:
        return jsonify({"error": f"Chapter number {chapter_number} already exists in this album"}), 400

    try:
        # Update chapter fields
        chapter.chapter_title = chapter_title
        chapter.chapter_number = chapter_number

        chapter.validate()
        db.session.commit()

        current_app.logger.info(
            f"Chapter '{chapter.chapter_title}' updated in album '{album.title}' by user {current_user.username}"
        )
        return jsonify({"message": "Chapter updated successfully", "chapter": chapter.to_dict()})

    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Validation error updating chapter: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating chapter: {e}")
        return jsonify({"error": "Failed to update chapter"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/chapters/<int:chapter_id>", methods=["DELETE"])
@login_required
def remove_chapter_from_album_api(album_id, chapter_id):
    """
    API endpoint to remove a chapter from an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)
    chapter = AlbumChapter.query.get_or_404(chapter_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    # Verify chapter belongs to this album
    if chapter.album_id != album_id:
        return jsonify({"error": "Chapter does not belong to this album"}), 400

    try:
        chapter_title = chapter.chapter_title
        db.session.delete(chapter)
        
        # Update album chapter count
        album.update_chapter_count()
        
        db.session.commit()

        current_app.logger.info(
            f"Chapter '{chapter_title}' removed from album '{album.title}' by user {current_user.username}"
        )
        return jsonify({"message": "Chapter removed successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing chapter: {e}")
        return jsonify({"error": "Failed to remove chapter"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/visibility", methods=["PATCH"])
@login_required
def toggle_album_visibility(album_id):
    """
    API endpoint to toggle album visibility.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    try:
        album.is_visible = not album.is_visible
        db.session.commit()

        status = "visible" if album.is_visible else "hidden"
        current_app.logger.info(
            f"Album '{album.title}' visibility set to {status} by user {current_user.username}"
        )
        return jsonify({
            "message": f"Album visibility updated to {status}",
            "is_visible": album.is_visible
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling album visibility: {e}")
        return jsonify({"error": "Failed to update album visibility"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/archive", methods=["PATCH"])
@login_required
def archive_album_api(album_id):
    """
    API endpoint to archive an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    try:
        album.is_archived = True
        db.session.commit()

        current_app.logger.info(
            f"Album '{album.title}' archived by user {current_user.username}"
        )
        return jsonify({"message": "Album archived successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error archiving album: {e}")
        return jsonify({"error": "Failed to archive album"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/type", methods=["PATCH"])
@login_required
def toggle_album_type(album_id):
    """
    API endpoint to toggle album type (premium/regular).
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    try:
        album.is_premium = not album.is_premium
        db.session.commit()

        type_status = "premium" if album.is_premium else "regular"
        current_app.logger.info(
            f"Album '{album.title}' type set to {type_status} by user {current_user.username}"
        )
        return jsonify({
            "message": f"Album type updated to {type_status}",
            "is_premium": album.is_premium
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling album type: {e}")
        return jsonify({"error": "Failed to update album type"}), 500


@main_blueprint.route("/api/albums/<int:album_id>/unarchive", methods=["PATCH"])
@login_required
def unarchive_album_api(album_id):
    """
    API endpoint to unarchive an album.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    album = Album.query.get_or_404(album_id)

    # Check permissions
    if current_user.effective_tier >= 3 and album.user_id != current_user.id:
        return jsonify({"error": "Access denied"}), 403

    try:
        album.is_archived = False
        db.session.commit()

        current_app.logger.info(
            f"Album '{album.title}' unarchived by user {current_user.username}"
        )
        return jsonify({"message": "Album unarchived successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unarchiving album: {e}")
        return jsonify({"error": "Failed to unarchive album"}), 500
