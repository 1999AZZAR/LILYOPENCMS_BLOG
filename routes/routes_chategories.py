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

@main_blueprint.route("/api/categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    """
    GET: Fetch all categories.
    POST: Add a new category (only for settingss and superusers).
    """

    if request.method == "GET":
        # Fetch all categories
        categories = Category.query.all()
        return jsonify(
            [{"id": category.id, "name": category.name} for category in categories]
        )

    # Only allow settingss and superusers to add categories
    if current_user.effective_tier > 1:
        return jsonify({"error": "Forbidden"}), 403  # Return JSON, not HTML

    if request.method == "POST":
        # Add a new category
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400  # Return JSON, not HTML

        category_name = data.get("name")

        if not category_name:
            return jsonify(
                {"error": "Category name is required"}
            ), 400  # Return JSON, not HTML

        # Check if the category already exists
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            return jsonify(
                {"error": "Category already exists"}
            ), 400  # Return JSON, not HTML

        # Create and add the new category
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()

        return jsonify(
            {"message": "Category added successfully", "id": new_category.id}
        ), 201


@main_blueprint.route("/api/categories/<int:category_id>", methods=["PUT", "DELETE"])
@login_required
def manage_category(category_id):
    """
    PUT: Update an existing category (only for settingss and superusers).
    DELETE: Delete a category (only for settingss and superusers).
    """
    # Only allow settingss and superusers to modify categories
    if current_user.effective_tier > 1:
        abort(403)

    category = Category.query.get_or_404(category_id)

    if request.method == "PUT":
        # Update the category
        data = request.get_json()
        new_name = data.get("name")

        if not new_name:
            return jsonify({"error": "Category name is required"}), 400

        # Check if the new name already exists
        existing_category = Category.query.filter_by(name=new_name).first()
        if existing_category and existing_category.id != category.id:
            return jsonify({"error": "Category name already exists"}), 400

        # Update the category name
        category.name = new_name
        db.session.commit()

        return jsonify({"message": "Category updated successfully"})

    if request.method == "DELETE":
        # Delete the category
        db.session.delete(category)
        db.session.commit()

        return jsonify({"message": "Category deleted successfully"})
