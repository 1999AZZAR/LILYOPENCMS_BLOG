"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from flask import jsonify
from typing import Any


def api_success(data: Any = None, message: str = "", code: int = 200):
    """Return a JSON success response."""
    body = {"success": True}
    if message:
        body["message"] = message
    if data is not None:
        body["data"] = data
    return jsonify(body), code


def api_error(message: str = "Error", code: int = 400, **extra):
    """Return a JSON error response."""
    body = {"success": False, "error": message, "code": code}
    body.update(extra)
    return jsonify(body), code


def api_paginated(items: list, total: int, page: int, per_page: int):
    """Return a paginated JSON response."""
    return jsonify({
        "success": True,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        },
    }), 200
