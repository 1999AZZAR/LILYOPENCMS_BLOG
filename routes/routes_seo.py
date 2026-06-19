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
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timezone
import time

# SEO Management Routes for Comprehensive SEO Management

@main_blueprint.route("/api/seo/articles", methods=["GET"])
@login_required
def get_articles_seo():
    """
    GET: Fetch articles with SEO data for comprehensive SEO management.
    Supports filtering by search, status, SEO status, and category.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    seo_status = request.args.get("seo_status", "")
    category = request.args.get("category", "")

    # Build base query
    query = db.session.query(
        News.id,
        News.title,
        News.writer,
        News.meta_description,
        News.meta_keywords,
        News.og_title,
        News.og_description,
        News.seo_score,
        News.is_visible,
        News.is_archived,
        News.created_at,
        Category.name.label('category_name')
    ).join(Category, News.category_id == Category.id)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                News.title.ilike(f"%{search}%"),
                News.content.ilike(f"%{search}%"),
                News.writer.ilike(f"%{search}%")
            )
        )

    if status:
        if status == "published":
            query = query.filter(News.is_visible == True, News.is_archived == False)
        elif status == "draft":
            query = query.filter(News.is_visible == False, News.is_archived == False)
        elif status == "archived":
            query = query.filter(News.is_archived == True)

    if category:
        query = query.filter(Category.id == category)

    # Apply SEO status filter
    if seo_status:
        if seo_status == "complete":
            query = query.filter(
                and_(
                    News.meta_description.isnot(None),
                    News.meta_description != "",
                    News.meta_keywords.isnot(None),
                    News.meta_keywords != "",
                    News.og_title.isnot(None),
                    News.og_title != ""
                )
            )
        elif seo_status == "incomplete":
            query = query.filter(
                or_(
                    News.meta_description.is_(None),
                    News.meta_description == "",
                    News.meta_keywords.is_(None),
                    News.meta_keywords == "",
                    News.og_title.is_(None),
                    News.og_title == ""
                )
            )
        elif seo_status == "missing":
            query = query.filter(
                and_(
                    News.meta_description.is_(None),
                    News.meta_keywords.is_(None),
                    News.og_title.is_(None)
                )
            )

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    query = query.order_by(desc(News.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute query
    results = query.all()

    # Process results
    articles = []
    for result in results:
        # Calculate SEO status
        seo_fields = [
            result.meta_description,
            result.meta_keywords,
            result.og_title,
            result.og_description
        ]
        
        filled_fields = sum(1 for field in seo_fields if field and field.strip())
        if filled_fields == len(seo_fields):
            seo_status = "complete"
        elif filled_fields == 0:
            seo_status = "missing"
        else:
            seo_status = "incomplete"

        articles.append({
            "id": result.id,
            "title": result.title,
            "writer": result.writer,
            "category_name": result.category_name,
            "meta_description": result.meta_description,
            "meta_keywords": result.meta_keywords,
            "og_title": result.og_title,
            "og_description": result.og_description,
            "seo_status": seo_status,
            "seo_score": result.seo_score or 0,
            "is_visible": result.is_visible,
            "is_archived": result.is_archived,
            "created_at": result.created_at.isoformat() if result.created_at else None
        })

    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    pagination = {
        "current_page": page,
        "per_page": per_page,
        "total_items": total_count,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next
    }

    return jsonify({
        "articles": articles,
        "pagination": pagination
    })

@main_blueprint.route("/api/seo/articles/<int:article_id>", methods=["GET"])
@login_required
def get_article_seo_detail(article_id):
    """GET: Fetch detailed SEO data for a specific article."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    article = News.query.get_or_404(article_id)
    
    return jsonify({
        "id": article.id,
        "title": article.title,
        "category": article.category.name if article.category else "N/A",
        "meta_description": article.meta_description,
        "meta_keywords": article.meta_keywords,
        "og_title": article.og_title,
        "og_description": article.og_description,
        "og_image": article.og_image,
        "canonical_url": article.canonical_url,
        "seo_slug": article.seo_slug,
        "twitter_card": article.twitter_card,
        "twitter_title": article.twitter_title,
        "twitter_description": article.twitter_description,
        "twitter_image": article.twitter_image,
        "meta_author": article.meta_author,
        "meta_language": article.meta_language or "id",
        "meta_robots": article.meta_robots or "index, follow",
        "structured_data_type": article.structured_data_type or "Article",
        "seo_score": article.seo_score or 0
    })

@main_blueprint.route("/api/seo/articles/<int:article_id>", methods=["PUT", "PATCH"])
@login_required
def update_article_seo(article_id):
    """PUT: Update SEO data for a specific article."""
    if not current_user.verified:
        return jsonify({"success": False, "error": "Account not verified", "code": "UNVERIFIED_USER"}), 403

    article = News.query.get_or_404(article_id)
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided", "code": "MISSING_DATA"}), 400

    # Update SEO fields
    seo_fields = [
        'meta_description', 'meta_keywords', 'og_title', 'og_description',
        'og_image', 'canonical_url', 'seo_slug', 'twitter_card',
        'twitter_title', 'twitter_description', 'twitter_image',
        'meta_author', 'meta_language', 'meta_robots', 'structured_data_type'
    ]

    updated = False
    changes = []
    for field in seo_fields:
        if field in data:
            old_val = getattr(article, field)
            if old_val != data[field]:
                setattr(article, field, data[field])
                changes.append(field)
                updated = True

    if not updated:
        return jsonify({"success": True, "message": "No changes detected", "data": article.to_dict()}), 200

    # Recalculate SEO score
    article.seo_score = article.calculate_seo_score()
    article.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        
        # Audit Log
        try:
            audit = UserActivity(
                user_id=current_user.id,
                activity_type='UPDATE_SEO',
                description=f"Updated News SEO ID {article_id}: {', '.join(changes)}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")

        return jsonify({"success": True, "message": "SEO data updated successfully", "data": article.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating article SEO: {e}")
        return jsonify({"success": False, "error": "Database error", "code": "DATABASE_ERROR"}), 500

@main_blueprint.route("/api/seo/albums", methods=["GET"])
@login_required
def get_albums_seo():
    """
    GET: Fetch albums with SEO data for comprehensive SEO management.
    Supports filtering by search, status, SEO status, and category.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    seo_status = request.args.get("seo_status", "")
    category = request.args.get("category", "")

    # Build base query
    query = db.session.query(
        Album.id,
        Album.title,
        Album.description,
        Album.meta_description,
        Album.meta_keywords,
        Album.og_title,
        Album.og_description,
        Album.seo_score,
        Album.is_visible,
        Album.is_archived,
        Album.created_at,
        Category.name.label('category_name')
    ).join(Category, Album.category_id == Category.id)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                Album.title.ilike(f"%{search}%"),
                Album.description.ilike(f"%{search}%")
            )
        )

    if status:
        if status == "published":
            query = query.filter(Album.is_visible == True, Album.is_archived == False)
        elif status == "draft":
            query = query.filter(Album.is_visible == False, Album.is_archived == False)
        elif status == "archived":
            query = query.filter(Album.is_archived == True)

    if category:
        query = query.filter(Category.id == category)

    # Apply SEO status filter
    if seo_status:
        if seo_status == "complete":
            query = query.filter(
                and_(
                    Album.meta_description.isnot(None),
                    Album.meta_description != "",
                    Album.meta_keywords.isnot(None),
                    Album.meta_keywords != "",
                    Album.og_title.isnot(None),
                    Album.og_title != ""
                )
            )
        elif seo_status == "incomplete":
            query = query.filter(
                or_(
                    Album.meta_description.is_(None),
                    Album.meta_description == "",
                    Album.meta_keywords.is_(None),
                    Album.meta_keywords == "",
                    Album.og_title.is_(None),
                    Album.og_title == ""
                )
            )
        elif seo_status == "missing":
            query = query.filter(
                and_(
                    Album.meta_description.is_(None),
                    Album.meta_keywords.is_(None),
                    Album.og_title.is_(None)
                )
            )

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    query = query.order_by(desc(Album.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute query
    results = query.all()

    # Process results
    albums = []
    for result in results:
        # Calculate SEO status
        seo_fields = [
            result.meta_description,
            result.meta_keywords,
            result.og_title,
            result.og_description
        ]
        
        filled_fields = sum(1 for field in seo_fields if field and field.strip())
        if filled_fields == len(seo_fields):
            seo_status = "complete"
        elif filled_fields == 0:
            seo_status = "missing"
        else:
            seo_status = "incomplete"

        albums.append({
            "id": result.id,
            "title": result.title,
            "category_name": result.category_name,
            "meta_description": result.meta_description,
            "meta_keywords": result.meta_keywords,
            "og_title": result.og_title,
            "og_description": result.og_description,
            "seo_status": seo_status,
            "seo_score": result.seo_score or 0,
            "is_visible": result.is_visible,
            "is_archived": result.is_archived,
            "created_at": result.created_at.isoformat() if result.created_at else None
        })

    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    pagination = {
        "current_page": page,
        "per_page": per_page,
        "total_items": total_count,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next
    }

    return jsonify({
        "albums": albums,
        "pagination": pagination
    })

# Individual Content Injection Endpoints (must come before more general routes)
@main_blueprint.route("/api/seo/albums/<int:album_id>/inject", methods=["POST"])
@login_required
def inject_album_seo(album_id):
    """POST: Inject SEO data for a specific album."""
    # Debug logging
    current_app.logger.info(f"Album injection request for album_id: {album_id}")
    current_app.logger.info(f"User authenticated: {current_user.is_authenticated}")
    current_app.logger.info(f"User verified: {getattr(current_user, 'verified', 'N/A')}")
    current_app.logger.info(f"Request headers: {dict(request.headers)}")
    
    if not current_user.verified:
        current_app.logger.warning(f"User {current_user.username} not verified for album injection")
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get the album
        album = Album.query.get_or_404(album_id)
        
        # Import the album SEO injector
        import sys
        import os

        # Add project root to path for proper imports
        project_root = os.path.dirname(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from seo_injector.inject_album_seo import (
            clear_existing_seo, generate_seo_slug, generate_meta_description,
            generate_meta_keywords, generate_open_graph_data, generate_schema_markup,
            calculate_seo_score
        )
        
        # Check if SEO is locked
        if album.is_seo_lock:
            return jsonify({
                "error": "SEO is locked for this album",
                "album_id": album_id
            }), 400
        
        # Clear existing SEO data
        clear_existing_seo(album)

        # Generate ALL SEO data within no_autoflush context to prevent database locks
        with db.session.no_autoflush:
            album.seo_slug = generate_seo_slug(album.title)
            album.meta_description = generate_meta_description(album)
            album.meta_keywords = generate_meta_keywords(album)

            # Generate Open Graph data
            og_title, og_description, og_image = generate_open_graph_data(album)
            album.og_title = og_title
            album.og_description = og_description
            album.og_image = og_image

            # Generate schema markup
            album.schema_markup = generate_schema_markup(album)
        
        # Set default values
        if album.creator_user:
            album.meta_author = album.creator_user.get_full_name()
        else:
            album.meta_author = "Unknown Author"
        
        album.meta_language = "id"
        album.meta_robots = "index, follow"
        album.twitter_card = "summary_large_image"
        album.structured_data_type = "Book" if album.is_completed else "CreativeWork"
        # Get website URL from SEO injection settings
        try:
            from sqlalchemy import text
            result = db.session.execute(text('SELECT website_url FROM seo_injection_settings LIMIT 1'))
            row = result.fetchone()
            website_url = row[0] if row and row[0] else "https://hystory.id"
        except Exception as e:
            current_app.logger.warning(f"Could not load SEO injection settings: {e}")
            website_url = "https://hystory.id"
        
        album.canonical_url = f"{website_url}/album/{album.id}"
        
        # Calculate SEO score
        album.seo_score = calculate_seo_score(album)
        album.last_seo_audit = datetime.now(timezone.utc)

        # Save to database with retry logic for SQLite locking
        max_retries = 3
        retry_delay = 0.1
        for attempt in range(max_retries):
            try:
                db.session.commit()
                break
            except Exception as commit_error:
                if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                    current_app.logger.warning(f"Database locked, retrying commit for album {album_id} (attempt {attempt + 1})")
                    db.session.rollback()
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    # Refresh the album object
                    album = Album.query.get(album_id)
                    if not album:
                        raise ValueError(f"Album {album_id} not found after rollback")
                else:
                    raise commit_error
        
        return jsonify({
            "success": True,
            "message": f"SEO data injected successfully for album: {album.title}",
            "album_id": album_id,
            "seo_score": album.seo_score
        })
        
    except Exception as e:
        current_app.logger.error(f"Error injecting SEO for album {album_id}: {e}")
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to inject SEO data",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/seo/albums/<int:album_id>", methods=["GET"])
@login_required
def get_album_seo_detail(album_id):
    """GET: Fetch detailed SEO data for a specific album."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    # Eager load category to avoid N+1 queries
    from sqlalchemy.orm import joinedload
    album = Album.query.options(
        joinedload(Album.category)
    ).get_or_404(album_id)
    
    return jsonify({
        "id": album.id,
        "title": album.title,
        "category": album.category.name if album.category else "N/A",
        "meta_description": album.meta_description,
        "meta_keywords": album.meta_keywords,
        "og_title": album.og_title,
        "og_description": album.og_description,
        "og_image": album.og_image,
        "canonical_url": album.canonical_url,
        "seo_slug": album.seo_slug,
        "twitter_card": album.twitter_card,
        "twitter_title": album.twitter_title,
        "twitter_description": album.twitter_description,
        "twitter_image": album.twitter_image,
        "meta_author": album.meta_author,
        "meta_language": album.meta_language or "id",
        "meta_robots": album.meta_robots or "index, follow",
        "structured_data_type": album.structured_data_type or "Book",
        "seo_score": album.seo_score or 0
    })

@main_blueprint.route("/api/seo/albums/<int:album_id>", methods=["PUT", "PATCH"])
@login_required
def update_album_seo(album_id):
    """PUT: Update SEO data for a specific album."""
    if not current_user.verified:
        return jsonify({"success": False, "error": "Account not verified", "code": "UNVERIFIED_USER"}), 403

    album = Album.query.get_or_404(album_id)
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided", "code": "MISSING_DATA"}), 400

    # Update SEO fields
    seo_fields = [
        'meta_description', 'meta_keywords', 'og_title', 'og_description',
        'og_image', 'canonical_url', 'seo_slug', 'twitter_card',
        'twitter_title', 'twitter_description', 'twitter_image',
        'meta_author', 'meta_language', 'meta_robots', 'structured_data_type'
    ]

    updated = False
    changes = []
    for field in seo_fields:
        if field in data:
            old_val = getattr(album, field)
            if old_val != data[field]:
                setattr(album, field, data[field])
                changes.append(field)
                updated = True

    if not updated:
        return jsonify({"success": True, "message": "No changes detected", "data": album.to_dict()}), 200

    # Recalculate SEO score
    album.seo_score = album.calculate_seo_score()
    album.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        
        # Audit Log
        try:
            audit = UserActivity(
                user_id=current_user.id,
                activity_type='UPDATE_SEO',
                description=f"Updated Album SEO ID {album_id}: {', '.join(changes)}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")

        return jsonify({"success": True, "message": "SEO data updated successfully", "data": album.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating album SEO: {e}")
        return jsonify({"success": False, "error": "Failed to update SEO data", "code": "DATABASE_ERROR"}), 500

# Additional API endpoints for albums management SEO tab
@main_blueprint.route("/api/seo/albums-management", methods=["GET"])
@login_required
def get_albums_seo_management():
    """
    GET: Fetch albums with SEO data specifically for albums management page.
    This endpoint is used by the albums management SEO tab.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    seo_status = request.args.get("seo_status", "")
    category = request.args.get("category", "")

    # Build base query
    query = db.session.query(
        Album.id,
        Album.title,
        Album.description,
        Album.meta_description,
        Album.meta_keywords,
        Album.og_title,
        Album.og_description,
        Album.seo_score,
        Album.is_visible,
        Album.is_archived,
        Album.created_at,
        Category.name.label('category_name')
    ).join(Category, Album.category_id == Category.id)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                Album.title.ilike(f"%{search}%"),
                Album.description.ilike(f"%{search}%")
            )
        )

    if status:
        if status == "visible":
            query = query.filter(Album.is_visible == True, Album.is_archived == False)
        elif status == "hidden":
            query = query.filter(Album.is_visible == False, Album.is_archived == False)
        elif status == "archived":
            query = query.filter(Album.is_archived == True)

    if category:
        query = query.filter(Category.id == category)

    # Apply SEO status filter
    if seo_status:
        if seo_status == "complete":
            query = query.filter(
                and_(
                    Album.meta_description.isnot(None),
                    Album.meta_description != "",
                    Album.meta_keywords.isnot(None),
                    Album.meta_keywords != "",
                    Album.og_title.isnot(None),
                    Album.og_title != ""
                )
            )
        elif seo_status == "incomplete":
            query = query.filter(
                or_(
                    Album.meta_description.is_(None),
                    Album.meta_description == "",
                    Album.meta_keywords.is_(None),
                    Album.meta_keywords == "",
                    Album.og_title.is_(None),
                    Album.og_title == ""
                )
            )
        elif seo_status == "missing":
            query = query.filter(
                and_(
                    Album.meta_description.is_(None),
                    Album.meta_keywords.is_(None),
                    Album.og_title.is_(None)
                )
            )

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    query = query.order_by(desc(Album.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute query
    results = query.all()

    # Process results
    albums = []
    for result in results:
        # Calculate SEO status
        seo_fields = [
            result.meta_description,
            result.meta_keywords,
            result.og_title,
            result.og_description
        ]
        
        filled_fields = sum(1 for field in seo_fields if field and field.strip())
        if filled_fields == len(seo_fields):
            seo_status = "complete"
        elif filled_fields == 0:
            seo_status = "missing"
        else:
            seo_status = "incomplete"

        albums.append({
            "id": result.id,
            "title": result.title,
            "category_name": result.category_name,
            "meta_description": result.meta_description,
            "meta_keywords": result.meta_keywords,
            "og_title": result.og_title,
            "og_description": result.og_description,
            "seo_status": seo_status,
            "seo_score": result.seo_score or 0,
            "is_visible": result.is_visible,
            "is_archived": result.is_archived,
            "created_at": result.created_at.isoformat() if result.created_at else None
        })

    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    pagination = {
        "current_page": page,
        "per_page": per_page,
        "total_items": total_count,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next
    }

    return jsonify({
        "albums": albums,
        "pagination": pagination
    })

@main_blueprint.route("/api/seo/root", methods=["GET"])
@login_required
def get_root_seo():
    """
    GET: Fetch root pages with SEO data for comprehensive SEO management.
    Supports filtering by search, status, and SEO status.
    """
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    seo_status = request.args.get("seo_status", "")

    # Build base query
    query = RootSEO.query

    # Apply filters
    if search:
        query = query.filter(
            or_(
                RootSEO.page_name.ilike(f"%{search}%"),
                RootSEO.page_identifier.ilike(f"%{search}%")
            )
        )

    if status:
        if status == "active":
            query = query.filter(RootSEO.is_active == True)
        elif status == "inactive":
            query = query.filter(RootSEO.is_active == False)

    # Apply SEO status filter
    if seo_status:
        if seo_status == "complete":
            query = query.filter(
                and_(
                    RootSEO.meta_title.isnot(None),
                    RootSEO.meta_title != "",
                    RootSEO.meta_description.isnot(None),
                    RootSEO.meta_description != "",
                    RootSEO.og_title.isnot(None),
                    RootSEO.og_title != ""
                )
            )
        elif seo_status == "incomplete":
            query = query.filter(
                or_(
                    RootSEO.meta_title.is_(None),
                    RootSEO.meta_title == "",
                    RootSEO.meta_description.is_(None),
                    RootSEO.meta_description == "",
                    RootSEO.og_title.is_(None),
                    RootSEO.og_title == ""
                )
            )
        elif seo_status == "missing":
            query = query.filter(
                and_(
                    RootSEO.meta_title.is_(None),
                    RootSEO.meta_description.is_(None),
                    RootSEO.og_title.is_(None)
                )
            )

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    query = query.order_by(asc(RootSEO.page_identifier))
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute query
    results = query.all()

    # Process results
    root_entries = []
    for result in results:
        # Calculate SEO score
        seo_score = result.calculate_seo_score()

        root_entries.append({
            "id": result.id,
            "page_identifier": result.page_identifier,
            "page_name": result.page_name,
            "is_active": result.is_active,
            "meta_title": result.meta_title,
            "meta_description": result.meta_description,
            "meta_keywords": result.meta_keywords,
            "og_title": result.og_title,
            "og_description": result.og_description,
            "og_image": result.og_image,
            "canonical_url": result.canonical_url,
            "seo_score": seo_score,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None
        })

    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    pagination = {
        "current_page": page,
        "per_page": per_page,
        "total_items": total_count,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next
    }

    return jsonify({
        "root_entries": root_entries,
        "pagination": pagination
    })

@main_blueprint.route("/api/seo/root/<int:root_id>", methods=["GET"])
@login_required
def get_root_seo_detail(root_id):
    """GET: Fetch detailed SEO data for a specific root page."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    root_seo = RootSEO.query.get_or_404(root_id)
    
    return jsonify({
        "id": root_seo.id,
        "title": root_seo.page_name,
        "category": "Root Page",
        "page_identifier": root_seo.page_identifier,
        "meta_title": root_seo.meta_title,
        "meta_description": root_seo.meta_description,
        "meta_keywords": root_seo.meta_keywords,
        "og_title": root_seo.og_title,
        "og_description": root_seo.og_description,
        "og_image": root_seo.og_image,
        "og_type": root_seo.og_type,
        "canonical_url": root_seo.canonical_url,
        "twitter_card": root_seo.twitter_card,
        "twitter_title": root_seo.twitter_title,
        "twitter_description": root_seo.twitter_description,
        "twitter_image": root_seo.twitter_image,
        "meta_author": root_seo.meta_author,
        "meta_language": root_seo.meta_language or "id",
        "meta_robots": root_seo.meta_robots or "index, follow",
        "structured_data_type": root_seo.structured_data_type or "WebPage",
        "seo_score": root_seo.calculate_seo_score()
    })

@main_blueprint.route("/api/seo/root/<int:root_id>", methods=["PUT", "PATCH"])
@login_required
def update_root_seo(root_id):
    """PUT: Update SEO data for a specific root page."""
    if not current_user.verified:
        return jsonify({"success": False, "error": "Account not verified", "code": "UNVERIFIED_USER"}), 403

    root_seo = RootSEO.query.get_or_404(root_id)
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided", "code": "MISSING_DATA"}), 400

    # Update SEO fields
    seo_fields = [
        'meta_title', 'meta_description', 'meta_keywords', 'og_title', 
        'og_description', 'og_image', 'og_type', 'canonical_url',
        'twitter_card', 'twitter_title', 'twitter_description', 'twitter_image',
        'meta_author', 'meta_language', 'meta_robots', 'structured_data_type'
    ]

    updated = False
    changes = []
    for field in seo_fields:
        if field in data:
            old_val = getattr(root_seo, field)
            if old_val != data[field]:
                setattr(root_seo, field, data[field])
                changes.append(field)
                updated = True

    if not updated:
        return jsonify({"success": True, "message": "No changes detected", "data": root_seo.to_dict()}), 200

    root_seo.updated_at = datetime.now(timezone.utc)
    root_seo.updated_by = current_user.id

    try:
        db.session.commit()
        
        # Audit Log
        try:
            audit = UserActivity(
                user_id=current_user.id,
                activity_type='UPDATE_SEO',
                description=f"Updated Root SEO ID {root_id}: {', '.join(changes)}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Audit log failed: {e}")

        return jsonify({"success": True, "message": "SEO data updated successfully", "data": root_seo.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating root SEO: {e}")
        return jsonify({"success": False, "error": "Database error", "code": "DATABASE_ERROR"}), 500

@main_blueprint.route("/api/seo/root", methods=["POST"])
@login_required
def create_root_seo():
    """POST: Create a new root page SEO entry."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate required fields
    if not data.get('page_identifier'):
        return jsonify({"error": "Page identifier is required"}), 400
    if not data.get('page_name'):
        return jsonify({"error": "Page name is required"}), 400

    # Check if page identifier already exists
    existing = RootSEO.query.filter_by(page_identifier=data['page_identifier']).first()
    if existing:
        return jsonify({"error": "Page identifier already exists"}), 400

    # Create new root SEO entry
    root_seo = RootSEO(
        page_identifier=data['page_identifier'],
        page_name=data['page_name'],
        is_active=data.get('is_active', True),
        meta_title=data.get('meta_title'),
        meta_description=data.get('meta_description'),
        meta_keywords=data.get('meta_keywords'),
        og_title=data.get('og_title'),
        og_description=data.get('og_description'),
        og_image=data.get('og_image'),
        og_type=data.get('og_type', 'website'),
        canonical_url=data.get('canonical_url'),
        twitter_card=data.get('twitter_card', 'summary_large_image'),
        twitter_title=data.get('twitter_title'),
        twitter_description=data.get('twitter_description'),
        twitter_image=data.get('twitter_image'),
        meta_author=data.get('meta_author'),
        meta_language=data.get('meta_language', 'id'),
        meta_robots=data.get('meta_robots', 'index, follow'),
        structured_data_type=data.get('structured_data_type', 'WebPage'),
        created_by=current_user.id,
        updated_by=current_user.id
    )

    try:
        db.session.add(root_seo)
        db.session.commit()
        return jsonify({
            "message": "Root SEO entry created successfully",
            "id": root_seo.id
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating root SEO: {e}")
        return jsonify({"error": "Failed to create SEO entry"}), 500

# SEO Injector Routes
@main_blueprint.route("/api/seo/inject", methods=["POST"])
@login_required
def run_seo_injection():
    """POST: Run SEO injection for specified content type."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    data = request.get_json() or {}
    injection_type = data.get('type', 'all')
    
    # Validate injection type
    valid_types = ['news', 'albums', 'chapters', 'root', 'all']
    if injection_type not in valid_types:
        return jsonify({"error": f"Invalid injection type. Must be one of: {valid_types}"}), 400

    try:
        # Import the SEO injector
        import sys
        import os

        # Add project root to path for proper imports
        project_root = os.path.dirname(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from seo_injector.seo_injector import run_seo_injection as run_injection

        # Run the injection
        result = run_injection(injection_type)
        
        return jsonify({
            "message": "SEO injection completed",
            "type": injection_type,
            "result": result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error running SEO injection: {e}")
        return jsonify({
            "error": "Failed to run SEO injection",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/seo/stats", methods=["GET"])
@login_required
def get_seo_statistics():
    """GET: Get SEO statistics for all content types."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Import the SEO injector
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'seo_injector'))
        
        from seo_injector import get_seo_statistics as get_stats
        
        # Get the statistics
        result = get_stats()
        
        return jsonify({
            "message": "SEO statistics retrieved",
            "result": result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO statistics: {e}")
        return jsonify({
            "error": "Failed to get SEO statistics",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/seo/inject/status", methods=["GET"])
@login_required
def get_seo_injection_status():
    """GET: Get the status of SEO injection operations."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Import the SEO injector
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'seo_injector'))
        
        from seo_injector import get_seo_statistics as get_stats
        
        # Get current statistics
        stats_result = get_stats()
        
        # Calculate overall SEO health
        total_items = 0
        items_with_seo = 0
        
        if stats_result['status'] == 'success':
            stats_text = stats_result['stats']
            
            # Parse the stats text to get counts
            for content_type, stats in stats_text.items():
                lines = stats.split('\n')
                for line in lines:
                    if 'Total' in line and ':' in line:
                        try:
                            count = int(line.split(':')[1].strip().split()[0])
                            total_items += count
                        except:
                            pass
                    elif 'With meta description:' in line:
                        try:
                            count = int(line.split(':')[1].strip().split()[0])
                            items_with_seo += count
                        except:
                            pass
        
        seo_health_percentage = (items_with_seo / total_items * 100) if total_items > 0 else 0
        
        return jsonify({
            "message": "SEO status retrieved",
            "total_items": total_items,
            "items_with_seo": items_with_seo,
            "seo_health_percentage": round(seo_health_percentage, 1),
            "stats": stats_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO status: {e}")
        return jsonify({
            "error": "Failed to get SEO status",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/root-seo-settings", methods=["GET"])
@main_blueprint.route("/admin/api/root-seo-settings", methods=["GET"])
@login_required
def get_root_seo_settings():
    """GET: Get root SEO settings configuration."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get brand identity for default values
        brand_info = BrandIdentity.query.first()
        
        # Get current root SEO settings from brand identity
        settings = {}
        
        if brand_info and brand_info.seo_settings:
            # Load settings from the dedicated seo_settings field
            if isinstance(brand_info.seo_settings, dict):
                settings = brand_info.seo_settings
            else:
                # Handle case where it might be stored as JSON string
                try:
                    settings = json.loads(brand_info.seo_settings) if isinstance(brand_info.seo_settings, str) else {}
                except:
                    settings = {}
        
        # Default settings based on inject_root_seo.py - Hystory.id branding
        default_settings = {
            "home_meta_title": "{brand_name} - Platform Digital Penulis Indonesia",
            "home_meta_description": "Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital.",
            "home_meta_keywords": "hystory, novel indonesia, cerpen, penulis indonesia, platform digital, literasi digital, komunitas kreatif",

            "about_meta_title": "Tentang Kami - {brand_name}",
            "about_meta_description": "Pelajari tentang Hystory.id, misi kami, tim, dan komitmen untuk memberikan solusi platform digital bagi penulis dan kreator konten Indonesia untuk berkembang dan dikenal luas.",
            "about_meta_keywords": "tentang hystory, misi, tim, platform digital indonesia, penulis, literasi, kreativitas",

            "news_meta_title": "Berita Terbaru - {brand_name}",
            "news_meta_description": "Dapatkan berita terbaru, artikel, dan informasi terkini seputar dunia literasi dan penulisan di Indonesia. Jelajahi koleksi lengkap konten berita kami.",
            "news_meta_keywords": "berita, artikel, informasi terkini, literasi indonesia, penulisan, jurnalisme",

            "albums_meta_title": "Album & Cerita - {brand_name}",
            "albums_meta_description": "Jelajahi koleksi album, cerita, dan konten berseri kami. Temukan novel, cerpen, dan karya kreatif dari penulis berbakat Indonesia.",
            "albums_meta_keywords": "album, cerita, novel, cerpen, karya kreatif, konten berseri",

            "default_og_image": "https://hystory.id/static/pic/logo.png",
            "default_og_type": "website",
            "default_twitter_card": "summary_large_image",
            "default_twitter_image": "https://hystory.id/static/pic/logo.png",
            "default_language": "id",
            "default_meta_robots": "index, follow"
        }
        
        # Merge with saved settings
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        
        # Add website_url to settings if not already present
        if 'website_url' not in settings:
            settings['website_url'] = brand_info.website_url if brand_info else "https://hystory.id"
        
        return jsonify({
            "success": True,
            "settings": settings,
            "brand_identity": {
                "brand_name": brand_info.brand_name if brand_info else "LilyOpenCMS",
                "website_url": brand_info.website_url if brand_info else "https://hystory.id"
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting root SEO settings: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get root SEO settings",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/root-seo-settings", methods=["POST"])
@main_blueprint.route("/admin/api/root-seo-settings", methods=["POST"])
@login_required
def save_root_seo_settings():
    """POST: Save root SEO settings configuration."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Get or create brand identity for storing settings
        brand_info = BrandIdentity.query.first()
        if not brand_info:
            brand_info = BrandIdentity(
                brand_name="LilyOpenCMS",
                website_url="https://hystory.id"
            )
            db.session.add(brand_info)
        
        # Store settings in brand_info.seo_settings field
        current_settings = {}
        
        # Get existing settings if any
        if brand_info.seo_settings:
            if isinstance(brand_info.seo_settings, dict):
                current_settings = brand_info.seo_settings
            else:
                try:
                    current_settings = json.loads(brand_info.seo_settings) if isinstance(brand_info.seo_settings, str) else {}
                except:
                    current_settings = {}
        
        # Update with new settings
        current_settings.update(data)
        
        # Update website_url if provided
        if 'website_url' in data and data['website_url']:
            brand_info.website_url = data['website_url']
        
        # Save to database using the dedicated seo_settings field
        brand_info.seo_settings = current_settings
        
        brand_info.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Root SEO settings saved successfully"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error saving root SEO settings: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to save root SEO settings",
            "details": str(e)
        }), 500

# Individual Content Injection Endpoints (must come before more general routes)
@main_blueprint.route("/api/seo/root/<int:root_id>/inject", methods=["POST"])
@login_required
def inject_root_seo(root_id):
    """POST: Inject SEO data for a specific root page."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get the root page
        root_page = RootSEO.query.get_or_404(root_id)

        # Import the root SEO injector
        import sys
        import os

        # Add project root to path for proper imports
        project_root = os.path.dirname(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from seo_injector.inject_root_seo import (
            clear_existing_seo, generate_meta_description,
            generate_meta_keywords, generate_open_graph_data, generate_schema_markup
        )

        # Check if SEO is locked (assuming root pages might have this field)
        if hasattr(root_page, 'is_seo_lock') and root_page.is_seo_lock:
            return jsonify({
                "error": "SEO is locked for this root page",
                "root_id": root_id
            }), 400

        # Clear existing SEO data
        clear_existing_seo(root_page)

        # Generate ALL SEO data within no_autoflush context to prevent database locks
        with db.session.no_autoflush:
            root_page.meta_description = generate_meta_description(root_page)
            root_page.meta_keywords = generate_meta_keywords(root_page)

            # Generate Open Graph data
            og_title, og_description, og_image = generate_open_graph_data(root_page)
            root_page.og_title = og_title
            root_page.og_description = og_description
            root_page.og_image = og_image

            # Generate schema markup
            root_page.schema_markup = generate_schema_markup(root_page)

        # Set default values
        root_page.meta_author = "Hystory.id"
        root_page.meta_language = "id"
        root_page.meta_robots = "index, follow"
        root_page.twitter_card = "summary_large_image"

        # Calculate SEO score (RootSEO uses calculate_seo_score() method, not a field)
        seo_score = root_page.calculate_seo_score()
        datetime.now(timezone.utc)

        # Save to database with retry logic for SQLite locking
        max_retries = 3
        retry_delay = 0.1
        for attempt in range(max_retries):
            try:
                db.session.commit()
                break
            except Exception as commit_error:
                if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                    current_app.logger.warning(f"Database locked, retrying commit for root page {root_id} (attempt {attempt + 1})")
                    db.session.rollback()
                    import time
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    # Refresh the root_page object
                    root_page = RootSEO.query.get(root_id)
                    if not root_page:
                        raise ValueError(f"Root page {root_id} not found after rollback")
                else:
                    raise commit_error

        return jsonify({
            "success": True,
            "message": f"SEO data injected successfully for root page: {root_page.page_name}",
            "root_id": root_id,
            "seo_score": seo_score
        })

    except Exception as e:
        current_app.logger.error(f"Error injecting SEO for root page {root_id}: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to inject SEO data",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/seo/chapters/<int:chapter_id>/inject", methods=["POST"])
@login_required
def inject_chapter_seo(chapter_id):
    """POST: Inject SEO data for a specific chapter."""
    # Debug logging
    current_app.logger.info(f"Chapter injection request for chapter_id: {chapter_id}")
    current_app.logger.info(f"User authenticated: {current_user.is_authenticated}")
    current_app.logger.info(f"User verified: {getattr(current_user, 'verified', 'N/A')}")
    current_app.logger.info(f"Request headers: {dict(request.headers)}")
    
    if not current_user.verified:
        current_app.logger.warning(f"User {current_user.username} not verified for chapter injection")
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get the chapter - eager load album and creator_user to avoid N+1 queries
        from sqlalchemy.orm import joinedload
        chapter = AlbumChapter.query.options(
            joinedload(AlbumChapter.album).joinedload(Album.creator_user)
        ).get_or_404(chapter_id)
        
        # Import the chapter SEO injector
        import sys
        import os

        # Add project root to path for proper imports
        project_root = os.path.dirname(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from seo_injector.inject_chapter_seo import (
            clear_existing_seo, generate_seo_slug, generate_meta_description,
            generate_meta_keywords, generate_open_graph_data, generate_schema_markup,
            calculate_seo_score
        )
        
        # Check if SEO is locked
        if chapter.is_seo_lock:
            return jsonify({
                "error": "SEO is locked for this chapter",
                "chapter_id": chapter_id
            }), 400
        
        # Clear existing SEO data
        clear_existing_seo(chapter)

        # Generate ALL SEO data within no_autoflush context to prevent database locks
        with db.session.no_autoflush:
            chapter.seo_slug = generate_seo_slug(f"chapter-{chapter.chapter_number}-{chapter.chapter_title}")
            chapter.meta_description = generate_meta_description(chapter)
            chapter.meta_keywords = generate_meta_keywords(chapter)

            # Generate Open Graph data
            og_title, og_description, og_image = generate_open_graph_data(chapter)
            chapter.og_title = og_title
            chapter.og_description = og_description
            chapter.og_image = og_image

            # Generate schema markup
            chapter.schema_markup = generate_schema_markup(chapter)
        
        # Set default values
        if chapter.album and chapter.album.creator_user:
            chapter.meta_author = chapter.album.creator_user.get_full_name()
        else:
            chapter.meta_author = "Unknown Author"
        
        chapter.meta_language = "id"
        chapter.meta_robots = "index, follow"
        chapter.twitter_card = "summary_large_image"
        chapter.structured_data_type = "Chapter"
        # Get website URL from SEO injection settings
        try:
            from sqlalchemy import text
            result = db.session.execute(text('SELECT website_url FROM seo_injection_settings LIMIT 1'))
            row = result.fetchone()
            website_url = row[0] if row and row[0] else "https://hystory.id"
        except Exception as e:
            current_app.logger.warning(f"Could not load SEO injection settings: {e}")
            website_url = "https://hystory.id"
        
        chapter.canonical_url = f"{website_url}/album/{chapter.album_id}/chapter/{chapter.chapter_number}"
        
        # Calculate SEO score
        chapter.seo_score = calculate_seo_score(chapter)
        chapter.last_seo_audit = datetime.now(timezone.utc)

        # Save to database with retry logic for SQLite locking
        max_retries = 3
        retry_delay = 0.1
        for attempt in range(max_retries):
            try:
                db.session.commit()
                break
            except Exception as commit_error:
                if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                    current_app.logger.warning(f"Database locked, retrying commit for chapter {chapter_id} (attempt {attempt + 1})")
                    db.session.rollback()
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    # Refresh the chapter object
                    chapter = AlbumChapter.query.get(chapter_id)
                    if not chapter:
                        raise ValueError(f"Chapter {chapter_id} not found after rollback")
                else:
                    raise commit_error
        
        return jsonify({
            "success": True,
            "message": f"SEO data injected successfully for Chapter {chapter.chapter_number}",
            "chapter_id": chapter_id,
            "seo_score": chapter.seo_score
        })
        
    except Exception as e:
        current_app.logger.error(f"Error injecting SEO for chapter {chapter_id}: {e}")
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to inject SEO data",
            "details": str(e)
        }), 500

@main_blueprint.route("/api/seo/articles/<int:article_id>/inject", methods=["POST"])
@login_required
def inject_article_seo(article_id):
    """POST: Inject SEO data for a specific article/news."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get the article
        article = News.query.get_or_404(article_id)
        
        # Import the news SEO injector
        import sys
        import os

        # Add project root to path for proper imports
        project_root = os.path.dirname(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from seo_injector.inject_news_seo import (
            clear_existing_seo, generate_seo_slug, generate_meta_description,
            generate_meta_keywords, generate_open_graph_data, generate_schema_markup,
            calculate_seo_score
        )
        
        # Check if SEO is locked
        if article.is_seo_lock:
            return jsonify({
                "error": "SEO is locked for this article",
                "article_id": article_id
            }), 400
        
        # Clear existing SEO data
        clear_existing_seo(article)

        # Generate ALL SEO data within no_autoflush context to prevent database locks
        with db.session.no_autoflush:
            article.seo_slug = generate_seo_slug(article.title)
            article.meta_description = generate_meta_description(article)
            article.meta_keywords = generate_meta_keywords(article)

            # Generate Open Graph data
            og_title, og_description, og_image = generate_open_graph_data(article)
            article.og_title = og_title
            article.og_description = og_description
            article.og_image = og_image

            # Generate schema markup
            article.schema_markup = generate_schema_markup(article)
        
        # Set default values
        article.meta_author = article.writer or article.author.username
        article.meta_language = "id"
        article.meta_robots = "index, follow"
        article.twitter_card = "summary_large_image"
        article.structured_data_type = "NewsArticle" if article.is_news else "Article"
        # Get website URL from SEO injection settings
        try:
            from sqlalchemy import text
            result = db.session.execute(text('SELECT website_url FROM seo_injection_settings LIMIT 1'))
            row = result.fetchone()
            website_url = row[0] if row and row[0] else "https://hystory.id"
        except Exception as e:
            current_app.logger.warning(f"Could not load SEO injection settings: {e}")
            website_url = "https://hystory.id"
        
        article.canonical_url = f"{website_url}/news/{article.id}"
        
        # Calculate SEO score
        article.seo_score = calculate_seo_score(article)
        article.last_seo_audit = datetime.now(timezone.utc)

        # Save to database with retry logic for SQLite locking
        max_retries = 3
        retry_delay = 0.1
        for attempt in range(max_retries):
            try:
                db.session.commit()
                break
            except Exception as commit_error:
                if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                    current_app.logger.warning(f"Database locked, retrying commit for article {article_id} (attempt {attempt + 1})")
                    db.session.rollback()
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    # Refresh the article object
                    article = News.query.get(article_id)
                    if not article:
                        raise ValueError(f"Article {article_id} not found after rollback")
                else:
                    raise commit_error
        
        return jsonify({
            "success": True,
            "message": f"SEO data injected successfully for article: {article.title}",
            "article_id": article_id,
            "seo_score": article.seo_score
        })
        
    except Exception as e:
        current_app.logger.error(f"Error injecting SEO for article {article_id}: {e}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Failed to inject SEO data",
            "details": str(e)
        }), 500 

# Analytics API Endpoints
@main_blueprint.route("/api/seo/stats/overview", methods=["GET"])
@login_required
def get_seo_stats_overview():
    """GET: Get SEO overview statistics."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get counts from database
        total_articles = News.query.count()
        total_albums = Album.query.count()
        total_chapters = AlbumChapter.query.count()
        total_root_pages = RootSEO.query.count()
        
        # Calculate average SEO scores
        articles_with_seo = News.query.filter(News.seo_score.isnot(None)).all()
        albums_with_seo = Album.query.filter(Album.seo_score.isnot(None)).all()
        chapters_with_seo = AlbumChapter.query.filter(AlbumChapter.seo_score.isnot(None)).all()
        root_with_seo = RootSEO.query.all()  # RootSEO doesn't have seo_score column, use calculate_seo_score() method
        
        avg_article_score = sum(a.seo_score for a in articles_with_seo) / len(articles_with_seo) if articles_with_seo else 0
        avg_album_score = sum(a.seo_score for a in albums_with_seo) / len(albums_with_seo) if albums_with_seo else 0
        avg_chapter_score = sum(c.seo_score for c in chapters_with_seo) / len(chapters_with_seo) if chapters_with_seo else 0
        avg_root_score = sum(r.calculate_seo_score() for r in root_with_seo) / len(root_with_seo) if root_with_seo else 0
        
        # Calculate completion rates
        complete_articles = len([a for a in articles_with_seo if a.seo_score >= 80])
        complete_albums = len([a for a in albums_with_seo if a.seo_score >= 80])
        complete_chapters = len([c for c in chapters_with_seo if c.seo_score >= 80])
        complete_root = len([r for r in root_with_seo if r.calculate_seo_score() >= 80])
        
        return jsonify({
            "success": True,
            "data": {
                "total_content": {
                    "articles": total_articles,
                    "albums": total_albums,
                    "chapters": total_chapters,
                    "root_pages": total_root_pages
                },
                "average_scores": {
                    "articles": round(avg_article_score, 1),
                    "albums": round(avg_album_score, 1),
                    "chapters": round(avg_chapter_score, 1),
                    "root_pages": round(avg_root_score, 1)
                },
                "completion_rates": {
                    "articles": round((complete_articles / total_articles * 100) if total_articles > 0 else 0, 1),
                    "albums": round((complete_albums / total_albums * 100) if total_albums > 0 else 0, 1),
                    "chapters": round((complete_chapters / total_chapters * 100) if total_chapters > 0 else 0, 1),
                    "root_pages": round((complete_root / total_root_pages * 100) if total_root_pages > 0 else 0, 1)
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO stats overview: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get SEO stats overview",
            "details": str(e)
        }), 500


@main_blueprint.route("/api/seo/stats/score-distribution", methods=["GET"])
@login_required
def get_seo_score_distribution():
    """GET: Get SEO score distribution data."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get all content with SEO scores
        articles = News.query.filter(News.seo_score.isnot(None)).all()
        albums = Album.query.filter(Album.seo_score.isnot(None)).all()
        chapters = AlbumChapter.query.filter(AlbumChapter.seo_score.isnot(None)).all()
        root_pages = RootSEO.query.all()  # RootSEO doesn't have seo_score column, use calculate_seo_score() method
        
        # Calculate distribution
        def get_distribution(items, use_calculate_method=False):
            if use_calculate_method:
                excellent = len([i for i in items if i.calculate_seo_score() >= 90])
                good = len([i for i in items if 80 <= i.calculate_seo_score() < 90])
                fair = len([i for i in items if 60 <= i.calculate_seo_score() < 80])
                poor = len([i for i in items if i.calculate_seo_score() < 60])
            else:
                excellent = len([i for i in items if i.seo_score >= 90])
                good = len([i for i in items if 80 <= i.seo_score < 90])
                fair = len([i for i in items if 60 <= i.seo_score < 80])
                poor = len([i for i in items if i.seo_score < 60])
            return [excellent, good, fair, poor]
        
        return jsonify({
            "success": True,
            "data": {
                "articles": get_distribution(articles),
                "albums": get_distribution(albums),
                "chapters": get_distribution(chapters),
                "root_pages": get_distribution(root_pages, use_calculate_method=True)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO score distribution: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get SEO score distribution",
            "details": str(e)
        }), 500


@main_blueprint.route("/api/seo/stats/content-performance", methods=["GET"])
@login_required
def get_seo_content_performance():
    """GET: Get content performance metrics."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get top performing content
        top_articles = News.query.filter(News.seo_score.isnot(None)).order_by(News.seo_score.desc()).limit(5).all()
        top_albums = Album.query.filter(Album.seo_score.isnot(None)).order_by(Album.seo_score.desc()).limit(5).all()
        top_chapters = AlbumChapter.query.filter(AlbumChapter.seo_score.isnot(None)).order_by(AlbumChapter.seo_score.desc()).limit(5).all()
        
        # For RootSEO, we need to get all and sort by calculated score
        all_root_pages = RootSEO.query.all()
        top_root_pages = sorted(all_root_pages, key=lambda x: x.calculate_seo_score(), reverse=True)[:5]
        
        def format_content(content_list, content_type, use_calculate_method=False):
            return [{
                "id": item.id,
                "title": getattr(item, 'title', getattr(item, 'chapter_title', getattr(item, 'page_name', 'Unknown'))),
                "score": item.calculate_seo_score() if use_calculate_method else item.seo_score,
                "type": content_type
            } for item in content_list]
        
        return jsonify({
            "success": True,
            "data": {
                "top_articles": format_content(top_articles, "article"),
                "top_albums": format_content(top_albums, "album"),
                "top_chapters": format_content(top_chapters, "chapter"),
                "top_root_pages": format_content(top_root_pages, "root_page", use_calculate_method=True)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO content performance: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get SEO content performance",
            "details": str(e)
        }), 500


@main_blueprint.route("/api/seo/stats/status-breakdown", methods=["GET"])
@login_required
def get_seo_status_breakdown():
    """GET: Get SEO status breakdown."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get status breakdown
        articles = News.query.all()
        albums = Album.query.all()
        chapters = AlbumChapter.query.all()
        root_pages = RootSEO.query.all()
        
        def get_status_breakdown(items, use_calculate_method=False):
            if use_calculate_method:
                complete = len([i for i in items if i.calculate_seo_score() >= 80])
                incomplete = len([i for i in items if 40 <= i.calculate_seo_score() < 80])
                missing = len([i for i in items if i.calculate_seo_score() < 40])
            else:
                complete = len([i for i in items if hasattr(i, 'seo_score') and i.seo_score and i.seo_score >= 80])
                incomplete = len([i for i in items if hasattr(i, 'seo_score') and i.seo_score and 40 <= i.seo_score < 80])
                missing = len([i for i in items if not hasattr(i, 'seo_score') or not i.seo_score or i.seo_score < 40])
            return [complete, incomplete, missing]
        
        return jsonify({
            "success": True,
            "data": {
                "articles": get_status_breakdown(articles),
                "albums": get_status_breakdown(albums),
                "chapters": get_status_breakdown(chapters),
                "root_pages": get_status_breakdown(root_pages, use_calculate_method=True)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO status breakdown: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get SEO status breakdown",
            "details": str(e)
        }), 500


@main_blueprint.route("/api/seo/activity/recent", methods=["GET"])
@login_required
def get_seo_recent_activity():
    """GET: Get recent SEO activity."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        # Get recent SEO audits
        recent_articles = News.query.filter(News.last_seo_audit.isnot(None)).order_by(News.last_seo_audit.desc()).limit(10).all()
        recent_albums = Album.query.filter(Album.last_seo_audit.isnot(None)).order_by(Album.last_seo_audit.desc()).limit(10).all()
        recent_chapters = AlbumChapter.query.filter(AlbumChapter.last_seo_audit.isnot(None)).order_by(AlbumChapter.last_seo_audit.desc()).limit(10).all()
        # RootSEO doesn't have last_seo_audit column, use updated_at instead
        recent_root_pages = RootSEO.query.filter(RootSEO.updated_at.isnot(None)).order_by(RootSEO.updated_at.desc()).limit(10).all()
        
        # Combine and sort by date
        all_activity = []
        
        for article in recent_articles:
            all_activity.append({
                "id": article.id,
                "title": article.title,
                "type": "article",
                "score": article.seo_score,
                "date": article.last_seo_audit.isoformat() if article.last_seo_audit else None
            })
        
        for album in recent_albums:
            all_activity.append({
                "id": album.id,
                "title": album.title,
                "type": "album",
                "score": album.seo_score,
                "date": album.last_seo_audit.isoformat() if album.last_seo_audit else None
            })
        
        for chapter in recent_chapters:
            all_activity.append({
                "id": chapter.id,
                "title": chapter.chapter_title,
                "type": "chapter",
                "score": chapter.seo_score,
                "date": chapter.last_seo_audit.isoformat() if chapter.last_seo_audit else None
            })
        
        for root_page in recent_root_pages:
            all_activity.append({
                "id": root_page.id,
                "title": root_page.page_name,
                "type": "root_page",
                "score": root_page.calculate_seo_score(),
                "date": root_page.updated_at.isoformat() if root_page.updated_at else None
            })
        
        # Sort by date and take top 15
        all_activity.sort(key=lambda x: x["date"] or "", reverse=True)
        all_activity = all_activity[:15]
        
        return jsonify({
            "success": True,
            "data": all_activity
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO recent activity: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get SEO recent activity",
            "details": str(e)
        }), 500


@main_blueprint.route("/api/seo/recommendations", methods=["GET"])
@login_required
def get_seo_recommendations():
    """GET: Get SEO recommendations."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        recommendations = []
        
        # Check for content without SEO scores
        articles_without_seo = News.query.filter(News.seo_score.is_(None)).count()
        albums_without_seo = Album.query.filter(Album.seo_score.is_(None)).count()
        chapters_without_seo = AlbumChapter.query.filter(AlbumChapter.seo_score.is_(None)).count()
        
        if articles_without_seo > 0:
            recommendations.append({
                "type": "warning",
                "title": f"{articles_without_seo} articles need SEO optimization",
                "description": "Run SEO injection for articles to improve search visibility",
                "action": "inject_articles"
            })
        
        if albums_without_seo > 0:
            recommendations.append({
                "type": "warning",
                "title": f"{albums_without_seo} albums need SEO optimization",
                "description": "Run SEO injection for albums to improve search visibility",
                "action": "inject_albums"
            })
        
        if chapters_without_seo > 0:
            recommendations.append({
                "type": "warning",
                "title": f"{chapters_without_seo} chapters need SEO optimization",
                "description": "Run SEO injection for chapters to improve search visibility",
                "action": "inject_chapters"
            })
        
        # Check for low-scoring content
        low_scoring_articles = News.query.filter(News.seo_score < 60).count()
        low_scoring_albums = Album.query.filter(Album.seo_score < 60).count()
        
        if low_scoring_articles > 0:
            recommendations.append({
                "type": "info",
                "title": f"{low_scoring_articles} articles have low SEO scores",
                "description": "Review and improve meta descriptions, titles, and keywords",
                "action": "review_articles"
            })
        
        if low_scoring_albums > 0:
            recommendations.append({
                "type": "info",
                "title": f"{low_scoring_albums} albums have low SEO scores",
                "description": "Review and improve meta descriptions, titles, and keywords",
                "action": "review_albums"
            })
        
        # Add general recommendations
        recommendations.append({
            "type": "success",
            "title": "SEO settings configured",
            "description": "Your root SEO settings are properly configured",
            "action": "view_settings"
        })
        
        return jsonify({
            "success": True,
            "data": recommendations
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting SEO recommendations: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get SEO recommendations",
            "details": str(e)
        }), 500 