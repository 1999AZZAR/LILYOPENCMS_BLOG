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

@main_blueprint.route("/api/news", methods=["GET"])
@login_required
def get_news_api():
    """
    API endpoint to retrieve a list of news articles with filtering.
    Requires user to be logged in and verified.
    Supports filtering by search query, category (by ID), status, premium status,
    popularity (read count), share count, and user ownership/role.
    """
    # Permission: Only verified users can access the management API
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted to access /api/news"
        )
        return jsonify({"error": "Account not verified"}), 403

    # --- Get filters from the request ---
    search_query = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "")  # Expect category_id (integer)
    status_filter = request.args.get("status", "")  # 'visible' or 'hidden'
    is_news_filter = request.args.get("is_news", "")  # 'true' or 'false'
    is_premium_filter = request.args.get("is_premium", "")  # 'true' or 'false'
    popularity_filter = request.args.get(
        "popularity", ""
    )  # 'most_popular' or 'least_popular'
    share_count_filter = request.args.get(
        "share_count", ""
    )  # 'most_shared' or 'least_shared'
    user_filter = request.args.get(
        "user", ""
    )  # 'owned', 'by_admin', 'by_general', 'all'
    featured_image_filter = request.args.get("featured_image", "") # 'has_image', 'no_image'
    external_link_filter = request.args.get("external_link", "") # 'has_link', 'no_link'

    # --- Base query ---
    query = News.query

    # --- Apply standard filters ---
    if search_query:
        query = query.filter(
            News.title.ilike(f"%{search_query}%")
            | News.content.ilike(f"%{search_query}%")
        )

    if category_filter:
        # Filter by category_id (integer)
        try:
            category_id = int(category_filter)
            query = query.filter(News.category_id == category_id)
        except ValueError:
            current_app.logger.warning(f"Invalid category_id: {category_filter}")
            return jsonify({"error": "Invalid category ID"}), 400

    if status_filter:
        query = query.filter(News.is_visible == (status_filter == "visible"))

    if is_news_filter:
        query = query.filter(News.is_news == (is_news_filter == "true"))
    
    if is_premium_filter:
        query = query.filter(News.is_premium == (is_premium_filter == "true"))

    # Apply featured image filter
    if featured_image_filter == 'has_image':
        query = query.filter(News.image_id != None)
    elif featured_image_filter == 'no_image':
        query = query.filter(News.image_id == None)

    # Apply external link filter
    if external_link_filter == 'has_link':
        query = query.filter(or_(News.external_source != None, News.external_source != ''))
    elif external_link_filter == 'no_link':
        query = query.filter(or_(News.external_source == None, News.external_source == ''))

    # --- Apply user/ownership filter based on current user's tier ---
    if current_user.effective_tier == 0:
        if user_filter == "owned":
            query = query.filter(News.user_id == current_user.id)
        elif user_filter == "by_admin":
            query = query.join(News.author).filter(User.role == UserRole.ADMIN)
        elif user_filter == "by_general":
            query = query.join(News.author).filter(User.role == UserRole.GENERAL)
        # 'all' for Tier 0 means no additional user filtering

    elif current_user.effective_tier == 1:
        allowed_user_ids = [current_user.id]
        general_users = (
            User.query.filter_by(role=UserRole.GENERAL).with_entities(User.id).all()
        )
        allowed_user_ids.extend([u.id for u in general_users])

        if user_filter == "owned":
            query = query.filter(News.user_id == current_user.id)
        elif user_filter == "by_general":
            query = query.join(News.author).filter(User.role == UserRole.GENERAL)
        else:  # 'all' for Tier 1 defaults to owned + general users' news
            query = query.filter(News.user_id.in_(allowed_user_ids))

    else:  # Tier 2+ — own content only
        query = query.filter(News.user_id == current_user.id)

    # --- Exclude archived news by default ---
    archived_filter = request.args.get("archived", "")
    if archived_filter == "true":
        query = query.filter(News.is_archived == True)
    elif archived_filter == "false":
        query = query.filter(News.is_archived == False)
    elif request.args.get("include_archived", "false").lower() != "true":
        query = query.filter(News.is_archived == False)

    # --- Apply ordering ---
    query = query.order_by(News.date.desc())

    if share_count_filter:
        query = query.outerjoin(ShareLog)
        total_shares_expr = (
            func.coalesce(ShareLog.whatsapp_count, 0)
            + func.coalesce(ShareLog.facebook_count, 0)
            + func.coalesce(ShareLog.twitter_count, 0)
            + func.coalesce(ShareLog.instagram_count, 0)
            + func.coalesce(ShareLog.bluesky_count, 0)
            + func.coalesce(ShareLog.clipboard_count, 0)
        )
        if share_count_filter == "most_shared":
            query = query.order_by(db.desc(total_shares_expr), News.date.desc())
        elif share_count_filter == "least_shared":
            query = query.order_by(db.asc(total_shares_expr), News.date.desc())

    elif popularity_filter:
        if popularity_filter == "most_popular":
            query = query.order_by(News.read_count.desc(), News.date.desc())
        elif popularity_filter == "least_popular":
            query = query.order_by(News.read_count.asc(), News.date.desc())

    # --- Apply Pagination ---
    page = request.args.get('page', 1, type=int)
    # Get per_page from config or default (e.g., 8)
    per_page = current_app.config.get('NEWS_PER_PAGE', 8)

    try:
        news_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        news_list = news_pagination.items # Get items for the current page
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error fetching news list for API: {e}", exc_info=True
        )
        abort(500, "Database error while fetching news.")

    response_data = []
    for news_item in news_list:
        news_dict = news_item.to_dict()
        # Add category name explicitly
        news_dict["category"] = news_item.category.name if news_item.category else None
        # Ensure category_id is included
        news_dict["category_id"] = news_item.category_id
        # Calculate total shares
        share_log = news_item.share_log
        total_shares = 0
        if share_log:
            total_shares = (
                (share_log.whatsapp_count or 0)
                + (share_log.facebook_count or 0)
                + (share_log.twitter_count or 0)
                + (share_log.instagram_count or 0)
                + (share_log.bluesky_count or 0)
                + (share_log.clipboard_count or 0)
            )
        news_dict["total_shares"] = total_shares
        response_data.append(news_dict)

    # --- Format the paginated response ---
    return jsonify({
        'items': response_data,
        'page': news_pagination.page,
        'per_page': news_pagination.per_page,
        'total_pages': news_pagination.pages,
        'total_items': news_pagination.total
    })


@main_blueprint.route("/api/news", methods=["POST"])
@login_required
def create_news_api():
    """
    API endpoint to create a new news article.
    Requires user to be logged in and verified.
    Expects form data including title, content, category, date, etc.
    """
    # Permission: Only verified users can create news
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted POST /api/news"
        )
        return jsonify({"error": "Account not verified"}), 403

    # Assume data is coming as form data based on original code
    data = request.form
    image_id = data.get("image_id")  # Optional image ID

    # --- Validate required fields ---
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    category_id_str = data.get("category", "").strip()
    date_str = data.get(
        "date", ""
    ).strip()  # Expecting ISO format string like "YYYY-MM-DDTHH:MM:SS"

    missing_fields = []
    if not title:
        missing_fields.append("title")
    if not content:
        missing_fields.append("content")
    if not category_id_str:
        missing_fields.append("category")
    if not date_str:
        missing_fields.append("date")
    if missing_fields:
        return jsonify(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"}
        ), 400

    # --- Find the Category by ID ---
    try:
        category_id = int(category_id_str)
    except ValueError:
        return jsonify({"error": f"Invalid category id: {category_id_str}"}), 400
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": f"Category with id '{category_id}' not found"}), 400

    # --- Parse date string ---
    try:
        # Attempt to parse full ISO format first
        try:
            news_date = datetime.fromisoformat(date_str)
        except ValueError:
            # Fallback to parsing only the date part if time is missing
            news_date = datetime.strptime(date_str, "%Y-%m-%d")
        # Ensure timezone-aware (assume UTC if parsed as naive)
        if news_date.tzinfo is None:
            news_date = news_date.replace(tzinfo=timezone.utc)
    except ValueError:
        return jsonify(
            {
                "error": "Invalid date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            }
        ), 400

    # --- Convert string boolean values to actual booleans ---
    is_news = data.get("is_news", "false").lower() == "true"
    is_premium = data.get("is_premium", "false").lower() == "true"
    is_main_news = data.get("is_main_news", "false").lower() == "true"
    is_visible = data.get("is_visible", "true").lower() == "true"  # Default to visible

    # --- Create the News object ---
    try:
            # Use the 'author' relationship via user_id
            news = News(
                title=title,
                content=content,
                tagar=data.get("tagar", "").strip()
                or None,  # Store empty string as None if desired
                date=news_date,
                read_count=0,  # Reset read count for new article
                category_id=category.id,
                is_news=is_news,
                is_premium=is_premium,
                is_main_news=is_main_news,
                is_visible=is_visible,
                is_archived=False,  # Ensure not archived
                user_id=current_user.id,  # Sets the author relationship implicitly
                image_id=int(image_id)
                if image_id and image_id.isdigit()
                else None,  # Convert to int or None
                writer=data.get("writer", "").strip()
                or current_user.username,  # Use provided writer or default to author's username
                external_source=data.get("external_source", "").strip() or None,
            )

            # Handle SEO fields if provided
            if data.get("meta_description"):
                news.meta_description = data.get("meta_description", "").strip()
            if data.get("meta_keywords"):
                news.meta_keywords = data.get("meta_keywords", "").strip()
            if data.get("og_title"):
                news.og_title = data.get("og_title", "").strip()
            if data.get("og_description"):
                news.og_description = data.get("og_description", "").strip()
            if data.get("og_image"):
                news.og_image = data.get("og_image", "").strip()
            if data.get("seo_slug"):
                news.seo_slug = data.get("seo_slug", "").strip()
            if data.get("canonical_url"):
                news.canonical_url = data.get("canonical_url", "").strip()
            
            # Advanced SEO fields
            if data.get("twitter_card"):
                news.twitter_card = data.get("twitter_card", "").strip()
            if data.get("twitter_title"):
                news.twitter_title = data.get("twitter_title", "").strip()
            if data.get("twitter_description"):
                news.twitter_description = data.get("twitter_description", "").strip()
            if data.get("twitter_image"):
                news.twitter_image = data.get("twitter_image", "").strip()
            if data.get("meta_author"):
                news.meta_author = data.get("meta_author", "").strip()
            if data.get("meta_language"):
                news.meta_language = data.get("meta_language", "").strip()
            if data.get("meta_robots"):
                news.meta_robots = data.get("meta_robots", "").strip()
            if data.get("structured_data_type"):
                news.structured_data_type = data.get("structured_data_type", "").strip()

            # Optional: Validate the model instance if you have complex rules
            # news.validate() # Call if needed

            db.session.add(news)
            db.session.commit()

            # Associate tags from tag_ids
            tag_ids_str = data.get("tag_ids", "").strip()
            if tag_ids_str:
                tag_ids = [int(x) for x in tag_ids_str.split(",") if x.strip().isdigit()]
                if tag_ids:
                    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                    news.tags.extend(tags)
                    db.session.commit()
            
            # Calculate SEO score after creation
            news.seo_score = news.calculate_seo_score()
            news.last_seo_audit = datetime.now(timezone.utc)
            db.session.commit()
            
            current_app.logger.info(
                f"News article '{news.title}' (ID: {news.id}) created by user {current_user.username}"
            )
            # Return success message and the full object of the newly created news
            return jsonify(news.to_dict()), 201  # 201 Created

    except ValueError as ve:  # Catch validation errors from model if any
        db.session.rollback()
        current_app.logger.warning(
            f"Validation error creating news by {current_user.username}: {ve}"
        )
        return jsonify({"error": f"Validation Error: {str(ve)}"}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error creating news by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "Could not save the news article due to a database error."}
        ), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error creating news by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "An internal error occurred while creating the news article."}
        ), 500


@main_blueprint.route("/api/news/<int:news_id>", methods=["GET"])
@login_required  # Keep login required for consistency, even if public page exists
def get_news_detail_api(news_id):
    """API endpoint to get details for a single news article."""
    # Permission: Only verified users can access the management API endpoint
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted GET /api/news/{news_id}"
        )
        return jsonify({"error": "Account not verified"}), 403

    try:
        news = db.session.get(News, news_id)  # Use db.session.get for PK lookup
        if news is None:
            abort(404, f"News article with ID {news_id} not found.")

        # Optional: Check visibility based on role (e.g., author/admin can see hidden ones)
        if (
            not news.is_visible
            and current_user.effective_tier >= 3
            and news.user_id != current_user.id
        ):
            abort(
                404, f"News article with ID {news_id} not found or not visible."
            )  # Treat hidden as not found for general users

        if news.is_archived and request.args.get("include_archived", "false").lower() != "true":
            abort(404, f"News article with ID {news_id} not found or archived.")

        news_dict = news.to_dict()
        news_dict['category_id'] = news.category_id # Explicitly add category_id
        return jsonify(news_dict)

    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error fetching news ID {news_id} for API: {e}", exc_info=True
        )
        abort(500, "Database error while fetching news details.")


@main_blueprint.route("/api/news/<int:news_id>", methods=["PUT"])
@login_required
def update_news_api(news_id):
    """API endpoint to update an existing news article."""
    # Permission: Only verified users can attempt updates
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted PUT /api/news/{news_id}"
        )
        return jsonify({"error": "Account not verified"}), 403

    news = db.session.get(News, news_id)
    if news is None:
        abort(404, f"News article with ID {news_id} not found.")

    # Permission: Only author or Admin/Superuser can update
    if not (
        news.user_id == current_user.id
        or current_user.effective_tier <= 1
    ):
        current_app.logger.warning(
            f"Forbidden PUT attempt on news ID {news_id} by user {current_user.username}"
        )
        abort(403, "You do not have permission to modify this news article.")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    updated = False  # Flag to track if any changes were made

    # --- Update fields if present in the request data ---
    if "title" in data and data["title"].strip():
        if news.title != data["title"].strip():
            news.title = data["title"].strip()
            updated = True
    if "content" in data and data["content"].strip():
        if news.content != data["content"].strip():
            news.content = data["content"].strip()
            updated = True
    if "tagar" in data:  # Allow setting tags to empty string
        if news.tagar != data["tagar"].strip():
            news.tagar = data["tagar"].strip() or None
            updated = True
    if "date" in data:
        try:
            # Parse date and ensure timezone-aware (assuming UTC)
            new_date = datetime.fromisoformat(data["date"])
            if new_date.tzinfo is None:
                new_date = new_date.replace(tzinfo=timezone.utc)
            if news.date != new_date:
                news.date = new_date
                updated = True
        except ValueError:
            return jsonify(
                {
                    "error": "Invalid date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
                }
            ), 400
    if "category" in data:
        category_id_str = data.get("category")
        try:
            category_id = int(category_id_str)
        except ValueError:
            return jsonify({"error": f"Invalid category id: {category_id_str}"}), 400
        category = Category.query.get(category_id)
        if not category:
            return jsonify(
                {"error": f"Category with id '{category_id}' not found"}
            ), 400
        if news.category_id != category.id:
            news.category_id = category.id
            updated = True
    if "is_news" in data and isinstance(data["is_news"], bool):
        if news.is_news != data["is_news"]:
            news.is_news = data["is_news"]
            updated = True
    if "is_premium" in data and isinstance(data["is_premium"], bool):
        if news.is_premium != data["is_premium"]:
            news.is_premium = data["is_premium"]
            updated = True
    if "is_main_news" in data and isinstance(data["is_main_news"], bool):
        if news.is_main_news != data["is_main_news"]:
            news.is_main_news = data["is_main_news"]
            updated = True
    if "is_visible" in data and isinstance(data["is_visible"], bool):
        if news.is_visible != data["is_visible"]:
            news.is_visible = data["is_visible"]
            updated = True
    if "external_source" in data:
        if news.external_source != data["external_source"]:
            news.external_source = data["external_source"]
            updated = True
    if "image_id" in data:
        try:
            new_image_id = int(data["image_id"]) if data["image_id"] else None
            if news.image_id != new_image_id:
                # Optional: Check if image ID exists?
                # if new_image_id and not db.session.get(Image, new_image_id):
                #     return jsonify({"error": f"Image with ID {new_image_id} not found"}), 400
                news.image_id = new_image_id
                updated = True
        except (ValueError, TypeError):
            return jsonify(
                {"error": "Invalid image_id format, must be an integer or null"}
            ), 400
    if "writer" in data:  # Allow updating writer
        new_writer = data["writer"].strip() if data["writer"] else None
        if news.writer != new_writer:
            news.writer = new_writer
            updated = True

    # --- Handle SEO fields ---
    seo_fields = [
        "meta_description", "meta_keywords", "og_title", "og_description", 
        "og_image", "seo_slug", "canonical_url", "twitter_card", 
        "twitter_title", "twitter_description", "twitter_image", 
        "meta_author", "meta_language", "meta_robots", "structured_data_type"
    ]
    
    for field in seo_fields:
        if field in data:
            new_value = data[field].strip() if data[field] else None
            current_value = getattr(news, field)
            if current_value != new_value:
                setattr(news, field, new_value)
                updated = True

    # --- Commit changes if any were made ---
    if not updated:
        return jsonify(news.to_dict()), 200  # No changes, return current state

    try:
        # Calculate SEO score if any SEO fields were updated
        if any(field in data for field in seo_fields):
            news.seo_score = news.calculate_seo_score()
            news.last_seo_audit = datetime.now(timezone.utc)
        
        # updated_at is handled automatically by the model's onupdate
        db.session.commit()
        current_app.logger.info(
            f"News article '{news.title}' (ID: {news.id}) updated by user {current_user.username}"
        )
        return jsonify(news.to_dict()), 200  # Return updated object

    except ValueError as ve:  # Catch validation errors from model if any
        db.session.rollback()
        current_app.logger.warning(
            f"Validation error updating news ID {news_id} by {current_user.username}: {ve}"
        )
        return jsonify({"error": f"Validation Error: {str(ve)}"}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error updating news ID {news_id} by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "Could not update news article due to database error."}
        ), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error updating news ID {news_id} by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "An internal error occurred while updating news article."}
        ), 500


@main_blueprint.route("/api/news/<int:news_id>", methods=["DELETE"])
@login_required
def delete_news_api(news_id):
    """API endpoint to delete a news article."""
    # Permission: Only verified users can attempt deletes
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted DELETE /api/news/{news_id}"
        )
        return jsonify({"error": "Account not verified"}), 403

    news = db.session.get(News, news_id)
    if news is None:
        abort(404, f"News article with ID {news_id} not found.")

    # Permission: Only author or Admin/Superuser can delete
    if not (
        news.user_id == current_user.id
        or current_user.effective_tier <= 1
    ):
        current_app.logger.warning(
            f"Forbidden DELETE attempt on news ID {news_id} by user {current_user.username}"
        )
        abort(403, "You do not have permission to delete this news article.")

    try:
        news_title = news.title  # For logging
        db.session.delete(news)
        # Note: Associated ShareLog might be deleted automatically due to cascade delete on FK, check model definition
        db.session.commit()
        current_app.logger.info(
            f"News article '{news_title}' (ID: {news_id}) deleted by user {current_user.username}"
        )
        return "", 204  # No Content on successful deletion

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error deleting news ID {news_id} by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "Could not delete news article due to database error."}
        ), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error deleting news ID {news_id} by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "An internal error occurred while deleting news article."}
        ), 500


@main_blueprint.route("/api/news/<int:news_id>/visibility", methods=["PATCH"])
@login_required
def toggle_news_visibility(news_id):
    """API endpoint to toggle the visibility of a news article."""
    # Permission: Only verified users can attempt
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted PATCH /api/news/{news_id}/visibility"
        )
        return jsonify({"error": "Account not verified"}), 403

    news = db.session.get(News, news_id)
    if news is None:
        abort(404, f"News article with ID {news_id} not found.")

    # Permission: Only author or Admin/Superuser can toggle visibility
    if not (
        news.user_id == current_user.id
        or current_user.effective_tier <= 1
    ):
        current_app.logger.warning(
            f"Forbidden PATCH visibility attempt on news ID {news_id} by user {current_user.username}"
        )
        abort(
            403,
            "You do not have permission to change the visibility of this news article.",
        )

    data = request.get_json()
    if "is_visible" not in data or not isinstance(data["is_visible"], bool):
        return jsonify({"error": "is_visible field (boolean) is required"}), 400

    if news.is_visible == data["is_visible"]:
        return jsonify(
            {"message": "Visibility status unchanged"}
        ), 200  # No change needed

    news.is_visible = data["is_visible"]

    try:
        db.session.commit()
        visibility_status = "visible" if news.is_visible else "hidden"
        current_app.logger.info(
            f"News article '{news.title}' (ID: {news.id}) visibility set to {visibility_status} by user {current_user.username}"
        )
        return jsonify(
            {"message": f"Visibility updated successfully to {visibility_status}"}
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error updating visibility for news ID {news_id} by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "Could not update visibility due to database error."}
        ), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error updating visibility for news ID {news_id} by {current_user.username}: {e}",
            exc_info=True,
        )
        return jsonify(
            {"error": "An internal error occurred while updating visibility."}
        ), 500


@main_blueprint.route("/api/news/<int:news_id>/track-share", methods=["POST"])
def track_share(news_id):
    """Public endpoint to track a share action for a news article."""
    data = request.get_json()
    if not data or "platform" not in data:
        return jsonify({"error": "Platform information is required"}), 400
    platform = data.get("platform")

    # Check if the news/article exists and is visible? (Optional check)
    news = db.session.get(News, news_id)
    if (
        news is None
    ):  # or not news.is_visible: # Optionally only track shares for visible news
        abort(404, f"News article with ID {news_id} not found.")

    # Get or create the ShareLog entry for this news/article
    share_log = ShareLog.query.filter_by(news_id=news_id).first()
    if not share_log:
        share_log = ShareLog(news_id=news_id)  # Counts default to 0
        db.session.add(share_log)

    # Update the share count and timestamps based on the platform
    current_time = datetime.now(timezone.utc)

    updated = False
    if platform == "whatsapp":
        share_log.whatsapp_count = (share_log.whatsapp_count or 0) + 1
        updated = True
    elif platform == "facebook":
        share_log.facebook_count = (share_log.facebook_count or 0) + 1
        updated = True
    elif platform == "twitter":
        share_log.twitter_count = (share_log.twitter_count or 0) + 1
        updated = True
    elif platform == "instagram":
        share_log.instagram_count = (share_log.instagram_count or 0) + 1
        updated = True
    elif platform == "bluesky":
        share_log.bluesky_count = (share_log.bluesky_count or 0) + 1
        updated = True
    elif platform == "clipboard":
        share_log.clipboard_count = (share_log.clipboard_count or 0) + 1
        updated = True
    else:
        return jsonify({"error": f"Unsupported platform: {platform}"}), 400

    if updated:
        # Update the first_shared_at timestamp if this is the first *ever* share
        if not share_log.first_shared_at:
            share_log.first_shared_at = current_time
        # Update the latest_shared_at timestamp regardless
        share_log.latest_shared_at = current_time

        try:
            db.session.commit()
            return jsonify({"message": "Share tracked successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error tracking share for news ID {news_id}: {e}",
                exc_info=True,
            )
            return jsonify(
                {"error": "Could not track share due to database error."}
            ), 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Unexpected error tracking share for news ID {news_id}: {e}",
                exc_info=True,
            )
            return jsonify(
                {"error": "An internal error occurred while tracking share."}
            ), 500
    else:
        # Should not happen if platform validation is correct, but good practice
        return jsonify({"error": "Invalid platform specified"}), 400


@main_blueprint.route("/api/news/<int:news_id>/share-data", methods=["GET"])
def get_share_data(news_id):
    """Public endpoint to get the share counts for a news article."""
    share_log = ShareLog.query.filter_by(news_id=news_id).first()
    if not share_log:
        # Return default zero counts if no log exists
        return jsonify(
            {
                "news_id": news_id,
                "whatsapp_count": 0,
                "facebook_count": 0,
                "twitter_count": 0,
                "instagram_count": 0,
                "bluesky_count": 0,
                "clipboard_count": 0,
                "total_shares": 0,
                "first_shared_at": None,
                "latest_shared_at": None,
            }
        )
    # Use the model's to_dict method which includes total_shares
    return jsonify(share_log.to_dict())


@main_blueprint.route("/api/settings/recent-news", methods=["GET"])
@login_required
def settings_recent_news():
    if current_user.effective_tier > 1:
        abort(403)

    recent_news = News.query.order_by(News.date.desc()).limit(5).all()
    return jsonify(
        [
            {
                "id": news.id,
                "title": news.title,
                "category": news.category.value,
                "is_visible": news.is_visible,
            }
            for news in recent_news
        ]
    )


@main_blueprint.route("/api/news/owned")
@login_required
def owned_news():
    """
    API endpoint to retrieve news articles owned by the current user,
    with pagination and filtering.
    """
    # --- Get filters and pagination from request.args ---
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int) # Default to 6 per page for cards
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "")  # 'visible' or 'hidden'
    is_news_filter = request.args.get("is_news", "")  # 'true' or 'false'
    is_premium_filter = request.args.get("is_premium", "")  # 'true' or 'false'
    has_image_filter = request.args.get("has_image", "") # 'has_image' or 'no_image'
    has_link_filter = request.args.get("has_link", "") # 'has_link' or 'no_link'

    # --- Base query for owned news ---
    query = News.query.filter(News.user_id == current_user.id)

    # --- Apply filters ---
    if search_query:
        query = query.filter(News.title.ilike(f"%{search_query}%"))

    if status_filter:
        query = query.filter(News.is_visible == (status_filter == "visible"))

    if is_news_filter:
        query = query.filter(News.is_news == (is_news_filter == "true"))
    
    if is_premium_filter:
        query = query.filter(News.is_premium == (is_premium_filter == "true"))

    if has_image_filter == 'has_image':
        query = query.filter(News.image_id != None)
    elif has_image_filter == 'no_image':
        query = query.filter(News.image_id == None)

    if has_link_filter == 'has_link':
        query = query.filter(News.external_source != None, News.external_source != '')
    elif has_link_filter == 'no_link':
        query = query.filter(or_(News.external_source == None, News.external_source == ''))

    # --- Exclude archived news by default ---
    if request.args.get("include_archived", "false").lower() != "true":
        query = query.filter(News.is_archived == False)

    # --- Apply ordering ---
    query = query.order_by(News.date.desc())

    # --- Apply Pagination ---
    try:
        news_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        news_list = news_pagination.items # Get items for the current page
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error fetching owned news for user {current_user.id}: {e}", exc_info=True
        )
        abort(500, "Database error while fetching your news.")

    # --- Serialize results ---
    response_data = []
    for news_item in news_list:
        news_dict = news_item.to_dict() # Use existing to_dict
        news_dict["category"] = news_item.category.name if news_item.category else None # Add category name
        # --- Explicitly add serialized image data ---
        news_dict["image"] = news_item.image.to_dict() if news_item.image else None
        response_data.append(news_dict)

    # --- Format the paginated response ---
    return jsonify({
        'items': response_data,
        'page': news_pagination.page,
        'per_page': news_pagination.per_page,
        'total_pages': news_pagination.pages,
        'total_items': news_pagination.total
    })


@main_blueprint.route("/api/news/bulk-delete", methods=["POST"])
@login_required
def bulk_delete_news():
    data = request.get_json()
    ids = data.get("ids", [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    # Permission: Only allow delete for own or admin/su
    news_to_delete = News.query.filter(News.id.in_(ids)).all()
    deleted_count = 0
    for news in news_to_delete:
        if news.user_id == current_user.id or current_user.effective_tier <= 1:
            db.session.delete(news)
            deleted_count += 1
    db.session.commit()
    return jsonify({"message": f"Deleted {deleted_count} articles"}), 200


@main_blueprint.route("/api/news/bulk-visibility", methods=["POST"])
@login_required
def bulk_update_news_visibility():
    data = request.get_json()
    ids = data.get("ids", [])
    is_visible = data.get("is_visible")
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    if not isinstance(is_visible, bool):
        return jsonify({"error": "'is_visible' must be a boolean"}), 400
    news_to_update = News.query.filter(News.id.in_(ids)).all()
    updated_count = 0
    for news in news_to_update:
        if news.user_id == current_user.id or current_user.effective_tier <= 1:
            news.is_visible = is_visible
            updated_count += 1
    db.session.commit()
    return jsonify({"message": f"Updated visibility for {updated_count} articles"}), 200


@main_blueprint.route("/api/news/bulk-category", methods=["POST"])
@login_required
def bulk_update_news_category():
    data = request.get_json()
    ids = data.get("ids", [])
    category_id = data.get("category_id")
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    if not isinstance(category_id, int):
        return jsonify({"error": "'category_id' must be an integer"}), 400
    news_to_update = News.query.filter(News.id.in_(ids)).all()
    updated_count = 0
    for news in news_to_update:
        if news.user_id == current_user.id or current_user.effective_tier <= 1:
            news.category_id = category_id
            updated_count += 1
    db.session.commit()
    return jsonify({"message": f"Updated category for {updated_count} articles"}), 200


@main_blueprint.route("/api/news/<int:news_id>/duplicate", methods=["POST"])
@login_required
def duplicate_news_api(news_id):
    try:
        current_app.logger.info(f"duplicate_news_api called for news_id={news_id}")
        current_app.logger.info(f"current_user: {getattr(current_user, 'username', 'NO USER')}, verified: {getattr(current_user, 'verified', 'NO VERIFIED')}")
    except Exception as e:
        current_app.logger.error(f"Error at very top of duplicate_news_api: {e}", exc_info=True)
        return jsonify({"error": f"Early error: {str(e)}"}), 500
    
    if not current_user.verified:
        current_app.logger.warning(
            f"Unverified user {current_user.username} attempted to duplicate news {news_id}"
        )
        return jsonify({"error": "Account not verified"}), 403

    current_app.logger.info(f"Looking for news with ID: {news_id}")
    news = db.session.get(News, news_id)
    if news is None:
        current_app.logger.error(f"News article with ID {news_id} not found.")
        abort(404, f"News article with ID {news_id} not found.")
    current_app.logger.info(f"Found news: {news.title}")

    # Permission: Only allow duplicate if user can see the article
    current_app.logger.info(f"Checking permissions - news.is_visible: {news.is_visible}, user.role: {current_user.role}, news.user_id: {news.user_id}, current_user.id: {current_user.id}")
    if not news.is_visible and current_user.effective_tier >= 3 and news.user_id != current_user.id:
        current_app.logger.warning(f"Permission denied for user {current_user.username} to duplicate news {news_id}")
        abort(403, "You do not have permission to duplicate this news article.")

    current_app.logger.info(f"Permission check passed, proceeding with duplication")
    try:
        # Generate a unique seo_slug for the duplicate using timestamp
        base_slug = news.seo_slug or f"copy-{news.id}"
        timestamp = int(datetime.now(timezone.utc).timestamp())
        new_slug = f"{base_slug}-{timestamp}"
        
        # Create the new news object with all required fields
        # Note: created_at and updated_at will be set automatically by the model
        # Also ensure we're in a proper database session context
        # Add debug logging to see what's happening
        current_app.logger.info(f"Creating duplicate news with slug: {new_slug}")
        current_app.logger.info(f"Original news ID: {news.id}, title: {news.title}")
        current_app.logger.info(f"Current user ID: {current_user.id}, username: {current_user.username}")
        new_news = News(
            title=f"Copy of {news.title}",
            content=news.content,
            tagar=news.tagar,
            date=datetime.now(timezone.utc),
            read_count=0,  # Reset read count for duplicate
            category_id=news.category_id,
            is_premium=news.is_premium,
            is_news=news.is_news,
            is_main_news=False,
            is_visible=False,
            is_archived=False,  # Ensure not archived
            user_id=current_user.id,
            image_id=news.image_id,
            writer=current_user.username,
            external_source=news.external_source,
            # Copy SEO fields with unique seo_slug
            meta_description=news.meta_description,
            meta_keywords=news.meta_keywords,
            og_title=news.og_title,
            og_description=news.og_description,
            og_image=news.og_image,
            canonical_url=news.canonical_url,
            seo_slug=new_slug,
            twitter_card=news.twitter_card,
            twitter_title=news.twitter_title,
            twitter_description=news.twitter_description,
            twitter_image=news.twitter_image,
            meta_author=news.meta_author,
            meta_language=news.meta_language,
            meta_robots=news.meta_robots,
            structured_data_type=news.structured_data_type,
        )
        current_app.logger.info(f"News object created successfully")
        current_app.logger.info(f"Adding new_news to session")
        db.session.add(new_news)
        current_app.logger.info(f"Committing to database")
        db.session.commit()
        current_app.logger.info(
            f"News article '{news.title}' duplicated by user {current_user.username} as ID {new_news.id}"
        )
        return jsonify(new_news.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error duplicating news ID {news_id} by {current_user.username}: {e}", exc_info=True
        )
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        current_app.logger.error(f"Exception details: {str(e)}")
        current_app.logger.error(f"Exception traceback: {e.__traceback__}")
        return jsonify({"error": "Could not duplicate news article."}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in duplicate function: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@main_blueprint.route("/api/news/<int:news_id>/archive", methods=["PATCH"])
@login_required
def archive_news_api(news_id):
    """API endpoint to archive a news article."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403
    news = db.session.get(News, news_id)
    if news is None:
        abort(404, f"News article with ID {news_id} not found.")
    if not (
        news.user_id == current_user.id
        or current_user.effective_tier <= 1
    ):
        abort(403, "You do not have permission to archive this news article.")
    news.is_archived = True
    db.session.commit()
    return jsonify(news.to_dict()), 200

@main_blueprint.route("/api/news/<int:news_id>/unarchive", methods=["PATCH"])
@login_required
def unarchive_news_api(news_id):
    """API endpoint to unarchive a news article."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403
    news = db.session.get(News, news_id)
    if news is None:
        abort(404, f"News article with ID {news_id} not found.")
    if not (
        news.user_id == current_user.id
        or current_user.effective_tier <= 1
    ):
        abort(403, "You do not have permission to unarchive this news article.")
    news.is_archived = False
    db.session.commit()
    return jsonify(news.to_dict()), 200

@main_blueprint.route("/api/news/bulk-archive", methods=["POST"])
@login_required
def bulk_archive_news():
    data = request.get_json()
    ids = data.get("ids", [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    news_to_update = News.query.filter(News.id.in_(ids)).all()
    updated_count = 0
    for news in news_to_update:
        if news.user_id == current_user.id or current_user.effective_tier <= 1:
            news.is_archived = True
            updated_count += 1
    db.session.commit()
    return jsonify({"message": f"Archived {updated_count} articles"}), 200

@main_blueprint.route("/api/news/bulk-unarchive", methods=["POST"])
@login_required
def bulk_unarchive_news():
    data = request.get_json()
    ids = data.get("ids", [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    news_to_update = News.query.filter(News.id.in_(ids)).all()
    updated_count = 0
    for news in news_to_update:
        if news.user_id == current_user.id or current_user.effective_tier <= 1:
            news.is_archived = False
            updated_count += 1
    db.session.commit()
    return jsonify({"message": f"Unarchived {updated_count} articles"}), 200

def get_related_news(news_item, exclude_ids=None, limit=6):
    if exclude_ids is None:
        exclude_ids = [news_item.id]
    else:
        exclude_ids = list(set(exclude_ids + [news_item.id]))
    # First, try by category and tags
    query = News.query.filter(
        News.id.notin_(exclude_ids),
        News.is_visible == True,
        News.is_archived == False,
        News.category_id == news_item.category_id,
    )
    # Optionally, add tag-based similarity here
    related_news = query.order_by(News.date.desc()).limit(limit).all()
    needed_more = limit - len(related_news)
    if needed_more > 0:
        # Fallback to popularity
        popularity_score = (
            func.coalesce(ShareLog.whatsapp_count, 0)
            + func.coalesce(ShareLog.facebook_count, 0)
            + func.coalesce(ShareLog.twitter_count, 0)
            + func.coalesce(ShareLog.instagram_count, 0)
            + func.coalesce(ShareLog.bluesky_count, 0)
            + func.coalesce(ShareLog.clipboard_count, 0)
            + func.coalesce(News.read_count, 0)
        ).label("popularity_score")
        popular_news_items = (
            db.session.query(News, popularity_score)
            .outerjoin(ShareLog, News.id == ShareLog.news_id)
            .filter(
                News.id.notin_([n.id for n in related_news] + exclude_ids),
                News.is_visible == True,
                News.is_archived == False,
            )
            .order_by(popularity_score.desc())
            .limit(needed_more)
            .all()
        )
        popular_news = [item[0] for item in popular_news_items]
        related_news.extend(popular_news)
    return related_news
