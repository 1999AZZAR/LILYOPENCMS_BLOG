from routes import main_blueprint
from .common_imports import *

# --- Endpoint for fetching the list (PUBLIC) ---
@main_blueprint.route("/api/social-media", methods=["GET"])
def get_social_media():
    """
    GET: Fetch all social media links (Publicly accessible for footer).
    """
    try:
        # Consider adding ordering if needed, e.g., by name or creation date
        social_media = SocialMedia.query.order_by(SocialMedia.name).all()
        return jsonify([sm.to_dict() for sm in social_media])
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error fetching social media list: {e}", exc_info=True
        )
        abort(500, "Could not retrieve social media links due to a database error.")
    except Exception as e:
        current_app.logger.error(
            f"Unexpected error fetching social media list: {e}", exc_info=True
        )
        abort(500, "An unexpected error occurred while retrieving social media links.")


# --- Endpoint for creating a new link (ADMIN/SU ONLY) ---
@main_blueprint.route("/api/social-media", methods=["POST"])
@login_required
def create_social_media():
    """
    POST: Add a new social media link (Requires Admin/Superuser).
    """
    # Permission Check
    if not current_user.role in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(
            403, "You do not have permission to add social media links."
        )  # Return JSON, not HTML

    data = request.get_json()
    # Basic Validation
    if not data:
        abort(400, "No data provided in request body.")
    name = data.get("name")
    url = data.get("url")
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        abort(400, "Social media 'name' is required and must be a non-empty string.")
    if not url or not isinstance(url, str) or len(url.strip()) == 0:
        abort(400, "Social media 'url' is required and must be a non-empty string.")
    # Optional: Add URL validation here if desired

    # Create new entry
    new_social = SocialMedia(
        name=name.strip(),
        url=url.strip(),
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    try:
        db.session.add(new_social)
        db.session.commit()
        current_app.logger.info(
            f"Social media link '{new_social.name}' (ID: {new_social.id}) created by user {current_user.username}"
        )
        return jsonify(new_social.to_dict()), 201  # 201 Created status code
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error creating social media link: {e}", exc_info=True
        )
        abort(500, "Could not save the social media link due to a database error.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error creating social media link: {e}", exc_info=True
        )
        abort(500, "An unexpected error occurred while saving the social media link.")


# --- Endpoint for fetching a single item (PUBLIC) ---
@main_blueprint.route("/api/social-media/<int:social_id>", methods=["GET"])
def get_social_media_item(social_id):
    """
    GET: Fetch a single social media link by ID (Publicly accessible).
    """
    try:
        social = db.session.get(
            SocialMedia, social_id
        )  # Use db.session.get for primary key lookup
        if social is None:
            abort(404, f"Social media link with ID {social_id} not found.")
        return jsonify(social.to_dict())
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error fetching social media item ID {social_id}: {e}",
            exc_info=True,
        )
        abort(500, "Could not retrieve the social media link due to a database error.")
    except Exception as e:
        current_app.logger.error(
            f"Unexpected error fetching social media item ID {social_id}: {e}",
            exc_info=True,
        )
        abort(
            500,
            "An unexpected error occurred while retrieving the social media link.",
        )


# --- Endpoint for updating/deleting an item (ADMIN/SU ONLY) ---
@main_blueprint.route("/api/social-media/<int:social_id>", methods=["PUT", "DELETE"])
@login_required
def update_delete_social_media_item(social_id):
    """
    PUT: Update an existing social media link (Requires Admin/Superuser).
    DELETE: Delete a social media link (Requires Admin/Superuser).
    """
    # Fetch the item or return 404
    social = db.session.get(SocialMedia, social_id)
    if social is None:
        abort(404, f"Social media link with ID {social_id} not found.")

    # Permission check for both PUT and DELETE
    if not current_user.role in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(
            403, "You do not have permission to modify social media links."
        )  # Corrected typo and message

    # --- PUT (Update) Logic ---
    if request.method == "PUT":
        data = request.get_json()
        if not data:
            abort(400, "No update data provided in request body.")

        updated = False
        if "name" in data:
            name = data.get("name")
            if not isinstance(name, str) or len(name.strip()) == 0:
                abort(400, "If provided, 'name' must be a non-empty string.")
            if social.name != name.strip():
                social.name = name.strip()
                updated = True
        if "url" in data:
            url = data.get("url")
            if not isinstance(url, str) or len(url.strip()) == 0:
                abort(400, "If provided, 'url' must be a non-empty string.")
            if social.url != url.strip():
                social.url = url.strip()
                updated = True
        # Optional: Add URL validation

        if not updated:
            # No actual changes were made based on provided data
            return jsonify(social.to_dict()), 200  # Return current state, status OK

        social.updated_by = current_user.id
        social.updated_at = (
            db.func.now()
        )  # Explicitly update timestamp if needed, though model might handle it

        try:
            db.session.commit()
            current_app.logger.info(
                f"Social media link '{social.name}' (ID: {social.id}) updated by user {current_user.username}"
            )
            return jsonify(social.to_dict())
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error updating social media item ID {social_id}: {e}",
                exc_info=True,
            )
            abort(
                500, "Could not update the social media link due to a database error."
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Unexpected error updating social media item ID {social_id}: {e}",
                exc_info=True,
            )
            abort(
                500,
                "An unexpected error occurred while updating the social media link.",
            )

    # --- DELETE Logic ---
    elif request.method == "DELETE":
        try:
            social_name = social.name  # Get name before deleting for logging
            db.session.delete(social)
            db.session.commit()
            current_app.logger.info(
                f"Social media link '{social_name}' (ID: {social_id}) deleted by user {current_user.username}"
            )
            return "", 204  # No Content status code for successful deletion
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Database error deleting social media item ID {social_id}: {e}",
                exc_info=True,
            )
            abort(
                500, "Could not delete the social media link due to a database error."
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Unexpected error deleting social media item ID {social_id}: {e}",
                exc_info=True,
            )
            abort(
                500,
                "An unexpected error occurred while deleting the social media link.",
            )

    # Should not be reached if method is PUT or DELETE, but added as fallback
    abort(405)  # Method Not Allowed
