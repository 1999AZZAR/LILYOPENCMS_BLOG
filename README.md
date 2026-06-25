# LILYOPENCMS

Flask-based CMS with SEO management, role-based access, media optimization, and multi-design system support.

## Features

- **Content** — News/articles, albums with chapters, scheduling, archiving, revision history, bulk operations
- **SEO** — Per-article meta, Open Graph, Twitter Cards, JSON-LD schema, XML sitemaps, readability scoring, YAML quality rules, `/robots.txt`
- **Media** — Auto WebP conversion, thumbnails, YouTube embeds, gallery management, usage tracking, bulk upload
- **Auth & Roles** — SUPERUSER/ADMIN/GENERAL roles, granular permission matrix, activity audit, registration approval, suspension
- **Branding** — Brand identity (logo, colors, assets), navigation links, social media, contact info, policies, team
- **Design Engine** — Multi-design system via Jinja2 loader: `templates/designs/{design}/` with fallback to default
- **Admin** — Swiss-Archival warm palette, sidebar search, bulk operations, brand color presets, SEO dashboard, tracking/script management (AdSense, GTM, GA4)
- **Performance** — Redis caching, lazy loading, asset compression, query optimization, monitoring dashboard
- **Subscription** — Premium content gating, tier management, ad-free experience

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.8+, Flask 2.x, SQLAlchemy |
| Frontend | Tailwind CSS, ES6+, SimpleMDE, Swiper.js |
| Database | SQLite (dev), PostgreSQL/MySQL (prod) |
| Cache | Redis |
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

### Seed Data (Optional)

```bash
cd helper
python generate_user.py
python add_categories.py
python add_fake_news.py
python add_fake_images.py
python add_videos.py
python init_footer_data.py
```

### Redis Setup

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

Or use the setup script: `./optimizations/setup_redis.sh`.

## Project Structure

```
├── main.py                  # Entry point
├── models.py                # DB models
├── routes/                  # Blueprints (public, admin, API, settings)
│   └── settings/            # Brand, SEO, dashboard, media, content, etc.
├── templates/
│   ├── base.html            # Public layout
│   ├── admin_base.html      # Admin layout
│   ├── public/              # Public pages
│   ├── settings/            # Admin settings
│   └── designs/             # Multi-design system directories
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── optimizations/           # Redis, caching, monitoring
├── helper/                  # Seed scripts
├── migrations/              # Alembic
└── docs/                    # Extended docs, API reference, TODO
```

## Deployment

```bash
# Gunicorn
gunicorn --bind 0.0.0.0:8000 main:app

# Passenger
passenger start

# Docker
docker build -t lilyopencms .
docker run -p 8000:8000 lilyopencms
```

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

## Contact

[azzar.mr.zs@gmail.com](mailto:azzar.mr.zs@gmail.com) — issues via GitHub.
