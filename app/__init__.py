"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import time
import sqlite3 as _sqlite3
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request, render_template, g
from sqlalchemy import event, text
from sqlalchemy.engine import Engine

JAKARTA = ZoneInfo("Asia/Jakarta")


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for LilyOpenCMS."""
    from dotenv import load_dotenv
    load_dotenv()

    root_dir = os.path.dirname(os.path.dirname(__file__))
    app = Flask(__name__, template_folder=os.path.join(root_dir, "templates"), static_folder=os.path.join(root_dir, "static"))

    from jinja2_loader import DesignFileSystemLoader
    app.jinja_loader = DesignFileSystemLoader(app.template_folder)

    _configure_app(app, config_name)
    _init_extensions(app)
    _register_hooks(app)
    _register_error_handlers(app)
    _register_blueprints(app)
    _init_database(app)
    _setup_logging(app)

    return app


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _configure_app(app: Flask, config_name: str | None = None) -> None:
    from app.config import config_map

    env = config_name or os.getenv("FLASK_ENV", "development")
    cfg = config_map.get(env, config_map["development"])
    app.config.from_object(cfg)

    # Secrets
    _secret = os.getenv("SECRET_KEY")
    if not _secret or _secret == "your_secret_key":
        import secrets as _secrets
        _secret = _secrets.token_hex(32)
        app.logger.warning("SECRET_KEY not set — using ephemeral key.")
    app.config["SECRET_KEY"] = _secret

    # Database
    _db_uri = os.getenv("DATABASE_URI", "sqlite:///exposeur.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = _db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["DEBUG"] = os.getenv("FLASK_ENV") != "production"

    # SQLite optimisations
    if _db_uri.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"check_same_thread": False, "timeout": 30},
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

        @event.listens_for(Engine, "connect")
        def _set_sqlite_pragmas(dbapi_conn, connection_record):  # noqa: ARG001
            if isinstance(dbapi_conn, _sqlite3.Connection):
                cur = dbapi_conn.cursor()
                cur.execute("PRAGMA journal_mode=WAL;")
                cur.execute("PRAGMA synchronous=NORMAL;")
                cur.execute("PRAGMA foreign_keys=ON;")
                cur.execute("PRAGMA busy_timeout=30000;")
                cur.execute("PRAGMA cache_size=-64000;")
                cur.close()
    else:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20,
        }


# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------

def _init_extensions(app: Flask) -> None:
    from app.extensions import db, migrate, csrf, login_manager, cors

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            app.logger.warning(f"Invalid user_id: {user_id}")
            return None

    # Performance modules (optional)
    try:
        from optimizations import (
            init_cache,
            create_database_optimizer,
            create_frontend_optimizer,
            create_performance_monitor,
        )
        init_cache(app)
        create_database_optimizer(app)
        create_frontend_optimizer(app)
        create_performance_monitor(app)
    except ImportError:
        app.logger.debug("Optimization modules not available, skipping.")


# ---------------------------------------------------------------------------
# Request / response hooks
# ---------------------------------------------------------------------------

def _register_hooks(app: Flask) -> None:

    @app.before_request
    def _ssr_start():
        g.ssr_start_time = time.time()

    @app.before_request
    def _inject_design():
        try:
            from models import BrandIdentity
            brand = BrandIdentity.query.first()
            g.design = brand.homepage_design if brand and brand.homepage_design else "default"
        except Exception:
            g.design = "default"

    @app.after_request
    def _ssr_end(response):
        if hasattr(g, "ssr_start_time"):
            render_time = time.time() - g.ssr_start_time
            route_name = request.endpoint or "unknown"
            try:
                from optimizations import get_ssr_optimizer
                get_ssr_optimizer().record_render(route_name, render_time, cached=False)
            except Exception as e:
                app.logger.debug(f"SSR monitoring failed for {route_name}: {e}")
        return response

    # CSRF bypass for API routes and Bearer tokens
    from app.extensions import csrf as csrf_ext
    _original_protect = csrf_ext.protect

    def _custom_csrf(**kwargs):
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return
        if any(request.path.startswith(p) for p in (
            "/api/", "/admin/api/", "/admin/database/api/",
            "/ads/", "/comments/", "/ratings/",
        )):
            return
        return _original_protect(**kwargs)

    csrf_ext.protect = _custom_csrf

    # ---- Context processors ----

    @app.context_processor
    def _inject_current_year():
        return {"current_year": datetime.now(JAKARTA).year}

    @app.context_processor
    def _utility_processor():
        import re
        def safe_title(title):
            filtered_title = re.sub(r'\s+', '_', title)
            filtered_title = re.sub(r'[\W]', '', filtered_title)
            max_length = 50
            if len(filtered_title) > max_length:
                filtered_title = filtered_title[:max_length]
            return filtered_title
        return dict(safe_title=safe_title)

    @app.context_processor
    def _inject_search_filters():
        from models import Category, News, UserRole
        from sqlalchemy import and_
        all_categories, unique_sorted_tags, categories_with_counts = [], [], []
        try:
            all_categories = Category.query.order_by(Category.name).all()
            categories_with_counts = [
                {
                    "id": c.id,
                    "name": c.name,
                    "count": News.query.filter(
                        and_(News.category_id == c.id, News.is_visible == True)
                    ).count(),
                }
                for c in all_categories
            ]
            tag_tuples = (
                db.session.query(News.tagar)
                .filter(and_(News.tagar.isnot(None), News.tagar != ""))
                .distinct().order_by(News.tagar).all()
            )
            tags = []
            for t in tag_tuples:
                tags.extend([x.strip().lower() for x in t[0].split(",") if x.strip()])
            unique_sorted_tags = sorted(set(tags), key=str.lower)
        except Exception:
            pass
        return dict(
            all_categories=all_categories,
            categories_with_counts=categories_with_counts,
            all_tags=unique_sorted_tags,
            current_query=request.args.get("q", ""),
            current_category=request.args.get("category", ""),
            current_tag=request.args.get("tag", ""),
            UserRole=UserRole,
        )

    @app.context_processor
    def _inject_brand():
        try:
            from models import BrandIdentity
            return {"brand_info": BrandIdentity.query.first()}
        except Exception:
            return {"brand_info": None}

    @app.context_processor
    def _inject_root_seo():
        try:
            from models import RootSEO
            path = request.path.strip("/")
            page_id = "home" if not path else path.split("/")[0]
            return {"root_seo": RootSEO.query.filter_by(page_identifier=page_id, is_active=True).first()}
        except Exception:
            return {"root_seo": None}

    @app.context_processor
    def _inject_contacts():
        try:
            from models import ContactDetail
            return {"contact_details": ContactDetail.query.filter_by(is_active=True).order_by(ContactDetail.section_order).all()}
        except Exception:
            return {"contact_details": []}

    @app.template_filter("asset_version")
    def _asset_version(url):
        if not url:
            return url
        v = os.getenv("TEMPLATE_VERSION_SUFFIX") or app.config.get("ASSET_VERSION")
        if not v:
            v = str(int(getattr(g, "ssr_start_time", time.time())))
        v = f"{v}_v2"
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}v={v}"


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

def _register_error_handlers(app: Flask) -> None:

    @app.route("/health")
    def health_check():
        from app.extensions import db
        db_status, db_msg = "ok", "Database connection successful."
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as e:
            db_status, db_msg = "error", f"Database connection error: {e}"
        code = 200 if db_status == "ok" else 503
        return jsonify({
            "status": "healthy" if db_status == "ok" else "unhealthy",
            "timestamp": datetime.now(JAKARTA).isoformat(),
            "dependencies": {"database": {"status": db_status, "message": db_msg}},
        }), code

    @app.errorhandler(404)
    def _404(_e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Not found"), 404
        return render_template("error.html", code=404, message="Halaman Tidak Ditemukan"), 404

    @app.errorhandler(500)
    def _500(e):
        from app.extensions import db
        try:
            db.session.rollback()
        except Exception:
            pass
        app.logger.error(f"Internal Server Error: {e}", exc_info=True)
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Internal server error"), 500
        return render_template("error.html", code=500, message="Kesalahan Server Internal"), 500

    @app.errorhandler(403)
    def _403(_e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Forbidden"), 403
        return render_template("error.html", code=403, message="Akses Ditolak"), 403

    @app.errorhandler(401)
    def _401(_e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Unauthorized"), 401
        return render_template("error.html", code=401, message="Otentikasi Diperlukan"), 401


# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------

def _register_blueprints(app: Flask) -> None:
    # The existing monolith blueprint — will be migrated module-by-module
    try:
        from routes import main_blueprint
        app.register_blueprint(main_blueprint)
        app.logger.info("Blueprint 'main_blueprint' registered.")
    except ImportError as e:
        app.logger.error(f"Failed to register 'main_blueprint': {e}")

    _safe_register(app, "routes.settings.root_seo", "root_seo_bp")
    _safe_register(app, "routes.seo_enhanced_dashboard", "seo_enhanced_bp")
    _safe_register(app, "routes.seo_settings_api", "seo_settings_bp")

    # New vertical-slice modules (activate one-by-one as old routes are removed)
    # _safe_register(app, "app.modules.auth", "auth_bp")


def _safe_register(app: Flask, module_path: str, attr: str) -> None:
    try:
        import importlib
        mod = importlib.import_module(module_path)
        app.register_blueprint(getattr(mod, attr))
    except Exception as e:
        app.logger.error(f"Failed to register blueprint from {module_path}: {e}")


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def _init_database(app: Flask) -> None:
    from app.extensions import db

    with app.app_context():
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")
        if os.path.isdir(migrations_dir):
            try:
                from flask_migrate import upgrade
                upgrade()
                app.logger.info("Database migrated to latest revision.")
            except Exception as e:
                app.logger.error(f"Migration failed: {e}", exc_info=True)
        else:
            try:
                if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
                    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
                    if not os.path.exists(db_path):
                        db.create_all()
                else:
                    db.create_all()
                app.logger.info("Database tables verified.")
            except Exception as e:
                app.logger.error(f"Database init failed: {e}", exc_info=True)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_logging(app: Flask) -> None:
    from logging.handlers import RotatingFileHandler

    log_fmt = logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    if not app.debug:
        os.makedirs("logs", exist_ok=True)
        fh = RotatingFileHandler("logs/database.log", maxBytes=102400, backupCount=10, encoding="utf-8")
        fh.setFormatter(log_fmt)
        fh.setLevel(logging.INFO)
        app.logger.addHandler(fh)
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)
