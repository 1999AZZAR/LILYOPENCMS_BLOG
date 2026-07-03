"""
Simple rate limiter for auth endpoints.
Uses Redis when available, falls back to in-memory cache.
"""

import time
from flask import request, jsonify

_attempts = {}

RL_CONFIG = {
    "login": {"max": 10, "window": 300},      # 10 attempts per 5 min
    "register": {"max": 3, "window": 3600},   # 3 per hour
}


def check_rate_limit(endpoint: str = "login") -> bool:
    """Check if request is within rate limit. Returns True if allowed.
    
    Usage:
        if not check_rate_limit("login"):
            return jsonify({"error": "Too many requests"}), 429
    """
    config = RL_CONFIG.get(endpoint, {"max": 5, "window": 300})
    ip = request.remote_addr or "127.0.0.1"
    key = f"rl:{endpoint}:{ip}"
    now = time.time()

    # Try Redis
    redis = None
    try:
        from app.extensions import redis_client
        redis = redis_client
    except Exception:
        pass

    if redis:
        try:
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, config["window"])
            count, _ = pipe.execute()
            return count <= config["max"]
        except Exception:
            pass

    # In-memory fallback
    record = _attempts.get(key, {"count": 0, "reset": now + config["window"]})
    if now > record["reset"]:
        record = {"count": 0, "reset": now + config["window"]}
    record["count"] += 1
    _attempts[key] = record
    return record["count"] <= config["max"]
