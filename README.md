# LilyOpenCMS

Flask-based CMS with multi-design system engine, advanced SEO management, granular role-based access, subscription gating, and full performance optimization.

```
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
Dual-licensed: GPL-3.0 for open-source / Commercial License for proprietary use.
```

## Features

- **Content Engine** — News/articles with scheduling, archiving, revision history, bulk operations, read tracking, share analytics (WhatsApp, Facebook, Twitter, Instagram, BlueSky, clipboard)
- **Album/Chapter System** — Group articles into albums (like novels) with chapter sequencing, completion tracking, hiatus status, independent SEO per album
- **Multi-Design System** — 3 built-in designs (`news`, `editorial`, `professional`). Custom Jinja2 loader resolves `templates/designs/{design}/` with fallback chain. Adding a design = drop a directory
- **Advanced SEO** — Per-article Open Graph, Twitter Cards, JSON-LD schema, canonical URLs, auto slug generation, SEO scoring (0–100), automated SEO injection, YAML quality rules, per-page Root SEO management, XML sitemaps, `robots.txt`
- **Brand Identity** — Configurable brand name, tagline, logo, favicon, placeholder, HSL color palette (primary, secondary, accent, background, foreground), feature toggles for UI sections
- **Auth & Roles** — SUPERUSER/ADMIN/GENERAL tiers + custom roles with granular permission matrix (resource + action), user activity audit trail, account suspension, registration approval
- **Subscription** — Premium content gating, tier management, monthly/yearly plans, auto-renew, ad-free experience toggle
- **Media** — Auto WebP conversion, thumbnails, YouTube embeds with metadata, gallery management, usage tracking, bulk upload
- **Email System** — SMTP delivery, template rendering, delivery status tracking (queued/sent/delivered/failed/bounced), rate limiting, retry logic, 20+ email types (verification, suspension, content approval, etc.)
- **Admin Dashboard** — Swiss-Archival warm palette, sidebar search, bulk operations, brand color presets, SEO dashboard, performance monitoring dashboard
- **Tracking/Analytics** — Google AdSense (publisher ID), Google Tag Manager, Google Analytics (GA4), Facebook Pixel — all configurable via Brand Identity
- **Performance** — Redis caching, query result caching, database query optimization, asset compression (gzip), lazy loading, SSR render time monitoring, connection pooling with WAL mode

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.8+, Flask 2.x, SQLAlchemy 2.x |
| Frontend | Tailwind CSS 4.x, ES6+, SimpleMDE, Swiper.js |
| Database | SQLite (dev with WAL), PostgreSQL/MySQL (prod) |
| Cache | Redis + memcached |
| Queue | APScheduler (periodic SEO tasks) |
| Server | Gunicorn, Passenger, Docker |

## Quick Start

```bash
git clone https://github.com/1999AZZAR/LILYOPENCMS_BLOG.git
cd LILYOPENCMS_BLOG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Open `http://127.0.0.1:5000`.

### Seed Data

```bash
cd helper
python generate_user.py
python add_categories.py
python add_fake_news.py
python add_fake_images.py
python add_videos.py
python init_footer_data.py
```

### Redis (Optional — required for caching)

```bash
# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis-server

# macOS
brew install redis && brew services start redis
```

Or use: `./optimizations/setup_redis.sh`

## Project Structure

```
├── main.py                  # App entry, extensions, error handlers, health check
├── models.py                # All SQLAlchemy models (~1970 lines)
├── jinja2_loader.py         # Custom design-aware Jinja2 FileSystemLoader
├── routes/                  # Blueprints
│   ├── routes_public.py     # Public-facing pages (home, news, albums, etc.)
│   ├── routes_auth.py       # Login, register, logout
│   ├── routes_news.py       # News CRUD
│   ├── routes_albums.py     # Album/chapter CRUD
│   ├── routes_images.py     # Image gallery CRUD
│   ├── routes_video.py      # YouTube video management
│   ├── routes_users.py      # User management
│   ├── routes_roles.py      # Custom role & permission management
│   ├── routes_analytics.py  # Share/click analytics
│   ├── routes_seo.py        # SEO management endpoints
│   ├── routes_infos.py      # Static pages (about, privacy, terms)
│   ├── routes_socialmedia.py# Social media link CRUD
│   ├── routes_subscriptions.py# Subscription management
│   ├── routes_chategories.py# Category CRUD
│   ├── seo_enhanced_dashboard.py # SEO performance dashboard
│   ├── seo_settings_api.py  # SEO settings API
│   ├── settings/            # Admin settings blueprints
│   │   ├── dashboard.py     # Admin dashboard
│   │   ├── brand.py         # Brand identity settings
│   │   ├── seo.py           # SEO settings
│   │   ├── root_seo.py      # Root page SEO
│   │   ├── content.py       # Content settings
│   │   ├── media.py         # Media settings
│   │   ├── contact.py       # Contact details
│   │   ├── policies.py      # Policies (privacy, terms, guidelines)
│   │   ├── account.py       # Account settings
│   │   ├── performance.py   # Performance monitor
│   │   └── api.py           # Admin API endpoints
│   └── utils/               # Shared utilities
├── templates/
│   ├── base.html            # Public layout
│   ├── admin_base.html      # Admin layout
│   ├── public/              # Public page templates
│   ├── settings/            # Admin settings templates
│   ├── admin/               # Admin pages
│   ├── emails/              # Email templates
│   ├── designs/             # Multi-design system
│   │   ├── news/            # Swiss-Archival news design (default)
│   │   ├── editorial/       # Editorial design
│   │   └── professional/    # Professional design
│   └── components/          # Reusable components (cards, etc.)
├── static/
│   ├── css/                 # Compiled Tailwind styles
│   ├── js/                  # Client-side scripts
│   ├── pic/                 # Logo, favicon, placeholders
│   └── uploads/             # User uploads
├── optimizations/           # Performance modules
│   ├── cache_config.py      # Redis/memcached caching
│   ├── database_optimization.py # Query optimization
│   ├── frontend_optimization.py # Lazy loading, compression
│   ├── asset_optimization.py    # Asset minification
│   ├── ssr_optimization.py      # Server-side render monitoring
│   └── performance_monitoring.py# Dashboards & metrics
├── seo_injector/            # Automated SEO injection
│   ├── auto_seo_injector.py  # Main injection engine
│   ├── inject_news_seo.py / inject_album_seo.py / inject_chapter_seo.py / inject_root_seo.py
│   ├── periodic_seo_tasks.py # APScheduler-based periodic SEO
│   ├── management_dashboard.py# SEO management UI
│   ├── smart_config.py       # Smart SEO configuration
│   ├── unified_settings.py   # Unified SEO settings
│   └── config/               # YAML rules (quality, keywords, templates)
├── helpers/                  # Seed data scripts
├── migrations/               # Alembic migration scripts
├── scripts/                  # Utility/maintenance scripts
└── main.py                   # WSGI entry point
```

## Design System

LilyOpenCMS uses a custom Jinja2 `DesignFileSystemLoader` that resolves templates at runtime based on `BrandIdentity.homepage_design`. The resolution chain is:

1. `templates/designs/{design}/{template}` — exact design match
2. `templates/designs/news/{template}` — fallback to `news` design
3. `templates/{template}` — default fallback

Admin, settings, email, and error templates bypass the design system. To add a new design, create `templates/designs/{name}/` with only the templates you want to override.

## API Endpoints

All `/api/*` routes are CORS-enabled and CSRF-exempt. Key public endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/news` | Paginated news list |
| `GET /api/news/<id>` | Single article |
| `GET /api/categories` | Category list |
| `GET /api/albums` | Album list with chapters |
| `GET /api/images` | Gallery images |
| `GET /api/social-media` | Social media links |
| `GET /api/search?q=` | Full-text search |
| `GET /api/share/<news_id>/<platform>` | Share count tracking |
| `GET /health` | Health check with DB status |

## Environment Variables

```
SECRET_KEY           # Flask secret key (required, auto-generated if missing)
DATABASE_URI         # SQLAlchemy DB URI (default: sqlite:///exposeur.db)
FLASK_ENV            # development / production
BASE_URL             # Canonical domain URL
WEBSITE_NAME         # Website display name
WEBSITE_DESCRIPTION  # Meta description
WEBSITE_LANGUAGE     # Content language (default: id)
ORGANIZATION_NAME    # Publisher name for schema.org
ORGANIZATION_LOGO    # Publisher logo URL
```

## Deployment

```bash
# Gunicorn
gunicorn --bind 0.0.0.0:8000 main:app

# Passenger (production WSGI)
passenger start

# Docker
docker build -t lilyopencms .
docker run -p 8000:8000 lilyopencms
```

For production: set `FLASK_ENV=production`, configure `SECRET_KEY` and `DATABASE_URI` for PostgreSQL/MySQL, set up Redis, and use Gunicorn behind a reverse proxy.

## License

Dual-licensed:
- **Open-source**: GNU General Public License v3.0 — see [LICENSE](LICENSE)
- **Commercial**: Separate Commercial License Agreement required

Contact [azzar.mr.zs@gmail.com](mailto:azzar.mr.zs@gmail.com) for commercial licensing inquiries.
