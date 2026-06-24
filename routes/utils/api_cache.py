"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

Response caching for public GET API routes. Cache key from path + query args.
"""

import hashlib
from functools import wraps
from flask import request, jsonify

try:
    from optimizations.cache_config import safe_cache_get, safe_cache_set, CACHE_TIMEOUTS
except ImportError:
    safe_cache_get = safe_cache_set = None
    CACHE_TIMEOUTS = {"news_list": 300, "news_detail": 600, "categories": 1800}


def _api_cache_key(prefix="api"):
    """Build cache key from request path and sorted query string."""
    parts = [prefix, request.path]
    if request.args:
        parts.append("_".join(f"{k}={request.args.get(k)}" for k in sorted(request.args.keys())))
    return hashlib.md5("|".join(parts).encode()).hexdigest()


def cache_api_response(timeout=300, key_prefix="api"):
    """Decorator: cache JSON body of GET responses with status 200."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.method != "GET":
                return f(*args, **kwargs)
            if not safe_cache_get or not safe_cache_set:
                return f(*args, **kwargs)
            key = _api_cache_key(key_prefix)
            cached = safe_cache_get(key)
            if cached is not None:
                try:
                    from routes.routes_deeplink import add_cors_headers
                    return add_cors_headers(jsonify(cached))
                except ImportError:
                    return jsonify(cached)
            result = f(*args, **kwargs)
            if isinstance(result, tuple):
                resp, status = result
                if status == 200 and hasattr(resp, "get_json"):
                    try:
                        safe_cache_set(key, resp.get_json(), timeout=timeout)
                    except Exception:
                        pass
                return result
            if hasattr(result, "get_json") and getattr(result, "status_code", None) == 200:
                try:
                    safe_cache_set(key, result.get_json(), timeout=timeout)
                except Exception:
                    pass
            return result
        return wrapper
    return decorator
