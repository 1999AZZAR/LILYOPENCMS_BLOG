from flask import (
    Flask,
    jsonify,
    request,
    render_template,
)
import time
import sqlite3 as _sqlite3
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from zoneinfo import ZoneInfo

JAKARTA = ZoneInfo("Asia/Jakarta")

from sqlalchemy import event, and_, text
from sqlalchemy.engine import Engine

from models import db, User, Category, News, UserRole

# Import performance optimization modules
from optimizations import (
    init_cache,
    create_database_optimizer,
    create_frontend_optimizer,
    create_performance_monitor,
    get_asset_optimizer,
    get_ssr_optimizer,
)

load_dotenv()

# ----------------------
# 🔧 Initialize Flask app
# ----------------------
app = Flask(__name__)

# ✅ Apply CORS ONLY for /api/* routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ----------------------
# 🔧 Configuration
# ----------------------
_secret = os.getenv("SECRET_KEY")
if not _secret or _secret == "your_secret_key":
    import secrets as _secrets
    _secret = _secrets.token_hex(32)
    app.logger.warning("SECRET_KEY not set — using ephemeral key. Set SECRET_KEY in .env for production.")

app.config["SECRET_KEY"] = _secret
_db_uri = os.getenv("DATABASE_URI", "sqlite:///exposeur.db")
app.config["SQLALCHEMY_DATABASE_URI"] = _db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = os.getenv("FLASK_ENV") != "production"

# SQLite-specific: enable WAL mode and optimize connection pool for concurrency
if _db_uri.startswith("sqlite"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30,
        },
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, connection_record) -> None:  # noqa: ARG001
        if isinstance(dbapi_conn, _sqlite3.Connection):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.execute("PRAGMA busy_timeout=30000;")
            cursor.execute("PRAGMA cache_size=-64000;")  # 64 MB page cache
            cursor.close()
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

# Performance optimization configuration
app.config["COMPRESS_MIMETYPES"] = [
    'text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript'
]
app.config["COMPRESS_LEVEL"] = 6
app.config["COMPRESS_MIN_SIZE"] = 500

# ----------------------
# 🔗 Initialize Extensions
# ----------------------
db.init_app(app)
migrate = Migrate(app, db)

# Initialize performance optimizations
init_cache(app)
db_optimizer = create_database_optimizer(app)
frontend_optimizer = create_frontend_optimizer(app)
performance_monitor = create_performance_monitor(app)
asset_optimizer = get_asset_optimizer()
ssr_optimizer = get_ssr_optimizer()

# Add SSR monitoring to app context
@app.before_request
def start_ssr_monitoring():
    from flask import g
    g.ssr_start_time = time.time()

@app.after_request
def end_ssr_monitoring(response):
    from flask import g
    if hasattr(g, 'ssr_start_time'):
        render_time = time.time() - g.ssr_start_time
        route_name = request.endpoint or 'unknown'
        try:
            optimizer = get_ssr_optimizer()
            optimizer.record_render(route_name, render_time, cached=False)
        except Exception as e:
            app.logger.debug(f"SSR monitoring failed for {route_name}: {e}")
    return response

# ----------------------
# 🛡️ CSRF Protection
# ----------------------
csrf = CSRFProtect(app)

# Configure CSRF to exempt API endpoints - override the protect method
original_protect = csrf.protect

def custom_csrf_protect(**kwargs):
    # Skip CSRF protection when Authorization: Bearer header is present (JWT authentication)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return

    # Skip CSRF protection for API endpoints
    if (request.path.startswith('/api/') or
        request.path.startswith('/admin/api/') or
        request.path.startswith('/admin/database/api/') or
        request.path.startswith('/ads/') or
        request.path.startswith('/comments/') or
        request.path.startswith('/ratings/')):
        return
    return original_protect(**kwargs)

csrf.protect = custom_csrf_protect

# ----------------------
# 🔑 Login Management
# ----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main.login"  # type: ignore[assignment]
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        app.logger.warning(f"Invalid user_id format received: {user_id}")
        return None

# ----------------------
# 🌐 Context Processors with Caching
# ----------------------
@app.context_processor
def inject_global_search_filters():
    all_categories = []
    unique_sorted_tags = []
    logger = logging.getLogger(__name__)

    try:
        # Use optimized query with caching
        all_categories = Category.query.order_by(Category.name).all()
        tag_strings_tuples = (
            db.session.query(News.tagar)
            .filter(and_(News.tagar.isnot(None), News.tagar != ""))
            .distinct()
            .order_by(News.tagar)
            .all()
        )

        all_tags_list = []
        for tag_string_tuple in tag_strings_tuples:
            tag_string = tag_string_tuple[0]
            tags_in_string = [
                tag.strip().lower() for tag in tag_string.split(",") if tag.strip()
            ]
            all_tags_list.extend(tags_in_string)

        unique_sorted_tags = sorted(list(set(all_tags_list)), key=str.lower)

    except Exception as e:
        logger.error(
            f"❌ Error fetching global filters (categories/tags): {e}", exc_info=True
        )
        all_categories = []
        unique_sorted_tags = []

    current_query = request.args.get("q", "")
    current_category = request.args.get("category", "")
    current_tag = request.args.get("tag", "")

    return dict(
        all_categories=all_categories,
        all_tags=unique_sorted_tags,
        current_query=current_query,
        current_category=current_category,
        current_tag=current_tag,
        UserRole=UserRole,
    )

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now(JAKARTA).year}

@app.context_processor
def utility_processor():
    def safe_title(title):
        import re
        filtered_title = re.sub(r'\s+', '_', title)
        filtered_title = re.sub(r'[\W]', '', filtered_title)
        max_length = 50
        if len(filtered_title) > max_length:
            filtered_title = filtered_title[:max_length]
        return filtered_title
    
    return dict(safe_title=safe_title)

@app.context_processor
def inject_brand_info():
    try:
        from models import BrandIdentity
        brand_info = BrandIdentity.query.first()
        return {"brand_info": brand_info}
    except Exception as e:
        app.logger.warning(f"Could not load brand info: {e}")
        return {"brand_info": None}

@app.context_processor
def inject_root_seo():
    """Inject root SEO data for the current page."""
    try:
        from models import RootSEO
        from flask import request
        
        # Determine page identifier based on current path
        path = request.path.strip('/')
        page_identifier = 'home' if not path else path.split('/')[0]
        
        # Get root SEO data for this page
        root_seo = RootSEO.query.filter_by(
            page_identifier=page_identifier,
            is_active=True
        ).first()
        
        return {"root_seo": root_seo}
    except Exception as e:
        app.logger.warning(f"Could not load root SEO: {e}")
        return {"root_seo": None}

@app.context_processor
def inject_contact_details():
    """Inject contact details into all templates."""
    try:
        from models import ContactDetail
        contact_details = (
            ContactDetail.query.filter_by(is_active=True)
            .order_by(ContactDetail.section_order)
            .all()
        )
        return {"contact_details": contact_details}
    except Exception as e:
        app.logger.warning(f"Could not load contact details: {e}")
        return {"contact_details": []}

# ----------------------
# 📌 Register Blueprints
# ----------------------
try:    
    from routes import main_blueprint  # type: ignore[attr-defined]
    app.register_blueprint(main_blueprint)  # type: ignore[arg-type]
    app.logger.info("✅ Blueprint 'main_blueprint' registered successfully.")
except ImportError as e:
    app.logger.error(f"❌ Failed to import or register blueprint 'main_blueprint': {e}")
except Exception as e:
    app.logger.error(f"❌ Unexpected error during blueprint registration: {e}", exc_info=True)

try:
    from routes.settings.root_seo import root_seo_bp
    app.register_blueprint(root_seo_bp)
    app.logger.info("✅ Blueprint 'root_seo_bp' registered successfully.")
except ImportError as e:
    app.logger.error(f"❌ Failed to import or register blueprint 'root_seo_bp': {e}")
except Exception as e:
    app.logger.error(f"❌ Unexpected error during root_seo blueprint registration: {e}", exc_info=True)

# ----------------------
# 🔧 Database Initialization
# ----------------------
with app.app_context():
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    if os.path.isdir(migrations_dir):
        try:
            from flask_migrate import upgrade
            upgrade()
            app.logger.info("✅ Database migrated to latest revision")
        except Exception as e:
            app.logger.error(f"❌ Migration upgrade failed: {e}", exc_info=True)
    else:
        try:
            if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
                db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace(
                    "sqlite:///", ""
                )
                if not os.path.exists(db_path):
                    db.create_all()
                    app.logger.info("✅ Database created and tables initialized")
                else:
                    app.logger.info("✅ Existing database found, skipping creation")
            else:
                db.create_all()
                app.logger.info("✅ Database tables created/verified")
        except Exception as e:
            app.logger.error(f"❌ Error during database initialization: {e}", exc_info=True)

# ----------------------
# 🩺 Health Check (no CORS needed because it's /health, not /api/health)
# ----------------------
@app.route("/health")
def health_check():
    db_status = "ok"
    db_message = "Database connection successful."
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_message = f"Database connection error: {e}"
        app.logger.error(f"❌ Health check DB error: {e}")

    status_code = 200 if db_status == "ok" else 503
    return jsonify(
        {
            "status": "healthy" if db_status == "ok" else "unhealthy",
            "timestamp": datetime.now(JAKARTA).isoformat(),
            "dependencies": {"database": {"status": db_status, "message": db_message}},
        }
    ), status_code

# ----------------------
# 🛠️ Error Handling
# ----------------------
@app.errorhandler(404)
def not_found_error(_error):
    app.logger.warning(f"⚠️ 404 Not Found: {request.path}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error="Not found"), 404
    return render_template(
        "error.html", code=404, message="Halaman Tidak Ditemukan"
    ), 404

@app.errorhandler(500)
def internal_server_error(error):
    try:
        db.session.rollback()
        app.logger.info("ℹ️ Database session rolled back due to internal error.")
    except Exception as rollback_err:
        app.logger.error(f"❌ Error during session rollback: {rollback_err}")
    app.logger.error(f"❌ Internal Server Error: {error}", exc_info=True)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error="Internal server error"), 500
    return render_template(
        "error.html", code=500, message="Kesalahan Server Internal"
    ), 500

@app.errorhandler(403)
def forbidden_error(_error):
    app.logger.warning(f"🚫 403 Forbidden: {request.path}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error="Forbidden"), 403
    return render_template("error.html", code=403, message="Akses Ditolak"), 403

@app.errorhandler(401)
def unauthorized_error(_error):
    app.logger.warning(f"🔒 401 Unauthorized: {request.path}")
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(error="Unauthorized"), 401
    return render_template("error.html", code=401, message="Otentikasi Diperlukan"), 401

# ----------------------
# 📝 Logging Configuration
# ----------------------
def setup_logging(app_instance):
    log_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
    if not app_instance.debug:
        if not os.path.exists("logs"):
            try:
                os.mkdir("logs")
            except OSError as e:
                app_instance.logger.error(f"❌ Could not create logs directory: {e}")
        log_file = os.path.join("logs", "database.log")
        try:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=102400, backupCount=10, encoding="utf-8"
            )
            file_handler.setFormatter(log_formatter)
            file_handler.setLevel(logging.INFO)
            app_instance.logger.addHandler(file_handler)
            app_instance.logger.setLevel(logging.INFO)
            app_instance.logger.info("📝 File logging configured to INFO level.")
        except Exception as e:
            app_instance.logger.error(f"❌ Failed to setup file logging: {e}")
    else:
        app_instance.logger.setLevel(logging.DEBUG)

# ----------------------
# 🏃🏻‍♂️ Main Loop
# ----------------------
if __name__ == "__main__":
    # Only start development server if not in production mode
    if os.getenv('FLASK_ENV') != 'production':
        setup_logging(app)
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        print("Production mode detected. Use a WSGI server like Gunicorn or uWSGI.")
