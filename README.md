# LilyOpenCMS

Flask-based CMS with vertical-slice architecture, multi-design system engine, advanced SEO, RBAC/ABAC, enterprise sidecars, and async workers.

```
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
Dual-licensed: GPL-3.0 for open-source / Commercial License for proprietary use.
```

## Features

- **Content Engine** — News/articles with scheduling, archiving, read tracking, share analytics
- **Static Pages** — Full CRUD with template selection (default, landing, full-width, sidebar), SEO fields, menu management
- **Tag System** — Proper many-to-many via junction table, auto-suggest, tag cloud, interactive picker in news editor
- **Comment System** — Nested replies (1 level), 4-state moderation (pending/approved/rejected/spam), spam detection, public form on articles
- **Author Profiles** — Bio, avatar, social links, `/author/<username>` pages, "Written By" card on articles
- **Album/Chapter System** — Group articles into albums with chapter sequencing, completion tracking
- **Multi-Design System** — 3 built-in designs (`news`, `editorial`, `professional`). Custom Jinja2 loader resolves `templates/designs/{design}/` with fallback chain
- **Advanced SEO** — Per-article OG/Twitter/JSON-LD, canonical URLs, auto slug, SEO scoring, XML sitemaps, `robots.txt`
- **Brand Identity** — Configurable brand name, tagline, logos, favicon, HSL color palette, feature toggles
- **Auth & Roles** — SUPERUSER/ADMIN/GENERAL + custom roles with granular permission matrix, user activity audit
- **Subscription** — Premium content gating, tier management
- **Media** — Image gallery, YouTube embeds, usage tracking
- **Email System** — SMTP delivery, HTML templates, delivery tracking, rate limiting
- **RSS Feed** — RSS 2.0 at `/rss.xml` with latest 50 articles
- **Search** — Full-text ILIKE search with dedicated results page, category/tag filtering
- **Admin Dashboard** — Swiss-Archival warm palette, SEO dashboard, performance monitor
- **Async Workers** — Celery for scheduled publishing, popularity updates, backups, DB optimization
- **Enterprise Sidecars** — Go gRPC services: Argus (logging/analytics → ES), Hermes (image processing via libvips), Cerebro (cached read + search gateway)

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12+, Flask 3.x, SQLAlchemy 2.x, Celery |
| Frontend | Tailwind CSS, SimpleMDE, Swiper.js |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Queue | Celery + Redis (broker) |
| Sidecars | Go 1.24 (gRPC: Argus, Hermes; HTTP: Cerebro) |
| Server | Gunicorn, Docker Compose |

## Quick Start

```bash
git clone https://github.com/1999AZZAR/LILYOPENCMS_BLOG.git
cd LILYOPENCMS_BLOG
cp .env.example .env
docker compose up -d
```

Open `http://localhost:5000`. First startup auto-seeds:

| Data | Amount |
|------|--------|
| Users | 3 (suadmin/suladang, admin/admin123, user/user123) |
| News articles | 8 with rich HTML content |
| Categories | 8 (Teknologi, Bisnis, Olahraga, etc.) |
| Tags | 18 with M2M associations |
| Comments | 3 with nested replies |
| Static pages | 4 (About, Privacy, Terms, Services) |
| Navigation links | 10 (navbar + footer) |
| Social media | 5 platforms |
| Team members | 5 across departments |
| Contact details | 4 (email, phone, address, hours) |

## Project Structure

```
├── app/
│   ├── __init__.py           # App factory, hooks, blueprints
│   ├── config.py             # Dev/Prod/Test configs
│   ├── extensions.py         # db, migrate, csrf, login_manager, cors
│   ├── modules/auth/         # Auth vertical slice (blueprint, service, controller)
│   ├── shared/
│   │   ├── auth/             # Consolidated decorators + permission manager
│   │   ├── circuit_breaker.py# Production-grade circuit breaker
│   │   ├── rpc/              # Python gRPC clients (Argus, Hermes)
│   │   ├── responses.py      # API response helpers
│   │   └── schemas.py        # Marshmallow base schemas
│   └── tasks/                # Celery tasks (publish, popularity, backup, optimization)
├── models.py                 # All SQLAlchemy models
├── routes/
│   ├── __init__.py           # Blueprint + imports
│   ├── routes_public.py      # Home, news detail, search, RSS, authors, sitemap
│   ├── routes_auth.py        # Login, register, logout
│   ├── routes_news.py        # News CRUD API
│   ├── routes_pages.py       # Static pages CRUD
│   ├── routes_tags.py        # Tag CRUD + public pages
│   ├── routes_comments.py    # Comment API + moderation
│   ├── routes_albums.py      # Album/chapter CRUD
│   ├── routes_images.py      # Image gallery
│   ├── routes_video.py       # YouTube videos
│   ├── routes_users.py       # User management
│   ├── routes_roles.py       # Custom roles & permissions
│   ├── routes_analytics.py   # Share/click analytics
│   ├── routes_seo.py         # SEO management
│   ├── settings/             # Admin settings (dashboard, brand, content, etc.)
│   └── utils/                # Shared utilities
├── templates/
│   ├── base.html             # Public layout
│   ├── admin_base.html       # Admin layout (sa-* design system)
│   ├── public/               # Public templates
│   ├── settings/             # Admin settings templates
│   ├── admin/                # Admin pages
│   ├── designs/              # Multi-design system
│   │   ├── news/             # Swiss-Archival news design (default)
│   │   ├── editorial/        # Editorial design
│   │   └── professional/     # Professional design
│   └── components/           # Reusable cards, pagination
├── static/
│   ├── css/ / js/ / pic/ / uploads/
├── sidecars/
│   ├── proto/                # gRPC proto definitions
│   ├── argus/                # Go: logging/analytics → Elasticsearch
│   ├── hermes/               # Go: image processing via libvips
│   └── cerebro/              # Go: cached read + search gateway
├── migrations/               # Alembic
├── seed.py                   # Comprehensive demo data seeder
├── docker-compose.yml        # web, db, redis, elasticsearch, sidecars, celery
├── Dockerfile                # Multi-stage build
└── docker-entrypoint.sh      # Auto-create tables, stamp alembic, seed, start gunicorn
```

## Design System

Uses a custom `DesignFileSystemLoader` that resolves templates at runtime:

1. `templates/designs/{design}/{template}` — exact match
2. `templates/designs/news/{template}` — fallback
3. `templates/{template}` — default

Admin/settings/email templates bypass the design system.

## API Endpoints

### Public
| Endpoint | Description |
|----------|-------------|
| `GET /api/news` | Paginated news list |
| `GET /api/tags` | All tags with counts |
| `GET /api/tags/suggest?q=` | Tag autocomplete |
| `GET /api/categories` | Category list |
| `GET /api/albums` | Album list |
| `GET /api/albums/<id>/chapters` | Album chapters |
| `GET /api/images` | Gallery images |
| `GET /api/social-media` | Social media links |
| `GET /rss.xml` | RSS 2.0 feed |
| `GET /sitemap.xml` | XML sitemap |
| `GET /health` | Health check |

### Comments
| Endpoint | Description |
|----------|-------------|
| `POST /api/news/<id>/comments` | Post comment (guest or auth) |
| `GET /api/news/<id>/comments` | Get approved comments |

### Admin (requires auth)
| Endpoint | Description |
|----------|-------------|
| `GET/POST /api/settings/tags` | List / create tags |
| `GET/POST /api/news` | Create / list news |
| `GET /api/settings/pages` | List static pages |
| `POST /api/settings/comments/<id>/status` | Moderate comment |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | auto | Flask secret key |
| `DATABASE_URI` | `postgresql://lily:lily_secret@db:5432/lilycms` | PostgreSQL connection |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection |
| `FLASK_ENV` | `production` | Environment |
| `APP_PORT` | `5000` | Exposed port |

## Deployment

```bash
# Production
docker compose up -d

# With sidecars
docker compose up -d --profile sidecars

# Fresh start (wipe DB)
docker compose down -v && docker compose up -d

# Check logs
docker compose logs -f web
```

## License

Dual-licensed: GPL-3.0 (open-source) / Commercial License (proprietary).
Contact [azzar.mr.zs@gmail.com](mailto:azzar.mr.zs@gmail.com) for commercial inquiries.
