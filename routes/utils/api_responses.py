"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

Standard API response helpers for consistent error envelopes.
"""

from flask import jsonify


def api_error(message, code=400, **extra):
    """Return a JSON error response with standard envelope for API routes."""
    body = {"success": False, "error": message, "code": code}
    body.update(extra)
    return jsonify(body), code
