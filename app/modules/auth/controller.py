"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Auth controller — thin route handlers for authentication flows.
"""

from flask import request, redirect, url_for, jsonify, flash, render_template, current_app
from flask_login import login_user, logout_user, current_user

from app.modules.auth import auth_bp
from app.modules.auth.service import auth_service
from app.modules.auth.schemas import (
    RegisterSchema, LoginSchema, ChangePasswordSchema,
    ForgotPasswordSchema, ResetPasswordSchema, UserUpdateSchema,
)
from shared.auth.decorators import login_required


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    schema = RegisterSchema()
    data = schema.load(request.form.to_dict())

    user, error = auth_service.create_user(
        username=data["username"],
        password=data["password"],
        email=data.get("email"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
    )
    if error:
        flash(error, "error")
        return render_template("auth/register.html"), 400

    login_user(user)
    auth_service.record_activity(user.id, "register", ip_address=request.remote_addr)
    return redirect(url_for("main.home"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    schema = LoginSchema()
    data = schema.load(request.form.to_dict())

    user, error = auth_service.authenticate(data["username"], data["password"])
    if error:
        flash(error, "error")
        return render_template("auth/login.html"), 401

    login_user(user)
    user.update_login_info(request.remote_addr, request.headers.get("User-Agent"))
    auth_service.record_activity(user.id, "login", ip_address=request.remote_addr)

    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    return redirect(url_for("main.home"))


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        auth_service.record_activity(current_user.id, "logout", ip_address=request.remote_addr)
    logout_user()
    return redirect(url_for("main.home"))


# ---------------------------------------------------------------------------
# Account management (authenticated)
# ---------------------------------------------------------------------------

@auth_bp.route("/api/account/change-password", methods=["POST"])
@login_required
def change_password():
    data = ChangePasswordSchema().load(request.get_json() or request.form.to_dict())
    success, message = auth_service.change_password(
        current_user, data["current_password"], data["new_password"]
    )
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message})


@auth_bp.route("/api/account/profile", methods=["GET"])
@login_required
def get_profile():
    return jsonify(current_user.to_dict())


@auth_bp.route("/api/account/profile", methods=["PUT", "PATCH"])
@login_required
def update_profile():
    data = UserUpdateSchema().load(request.get_json() or request.form.to_dict())
    success, message = auth_service.update_profile(current_user, **data)
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message, "user": current_user.to_dict()})


@auth_bp.route("/api/account/stats", methods=["GET"])
@login_required
def account_stats():
    return jsonify(auth_service.get_user_stats(current_user))
