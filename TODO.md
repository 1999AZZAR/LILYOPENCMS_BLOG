# TODO — LILY OpenCMS Open Source Version

> Enterprise reference: `/home/ubuntu/projects/lilyopencms`
> Current open-source: `/home/ubuntu/projects/LILYOPENCMS_BLOG`

---

## Implementation Order (Summary)

```
Phase 0 — Multi-Design System Engine                          ✅ DONE
Phase 1 — Foundation (App Factory + Docker + Shared Layer)    ✅ DONE
Phase 2 — Fix Broken Public Elements                          ✅ DONE
Phase 3 — RBAC / ABAC Refinement                              ✅ DONE
Phase 4 — Module Extraction (Vertical Slice Migration)        ✅ DONE (auth module scaffolded)
Phase 5 — Sidecars (Argus, Hermes, Cerebro)                   🔲
Phase 6 — Celery Async Workers                                🔲
Phase 7 — Toggle Cleanup + Premium Integration                🔲
```

---

## PHASE 0 — Multi-Design System Engine ✅

- [x] `DesignFileSystemLoader` resolves `templates/designs/{design}/` before fallback
- [x] `before_request` sets `g.design` from `BrandIdentity.homepage_design`
- [x] Public templates moved into `templates/designs/news/`
- [x] Card dispatcher resolved per-design
- [x] Admin UI relabelled "Homepage Design" → "Design System"

---

## PHASE 1 — Foundation ✅

### 1.1 App Factory

- [x] `app/__init__.py` — `create_app()` factory with config, extensions, hooks, blueprints
- [x] `app/config.py` — `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`
- [x] `app/extensions.py` — `db`, `migrate`, `csrf`, `login_manager`, `cors` instances
- [x] `wsgi.py` — production entry point via `gunicorn wsgi:application`
- [x] `main.py` preserved for backward compatibility (legacy dev server)

### 1.2 Shared Layer

- [x] `shared/auth/decorators.py` — Consolidated `@login_required`, `@permission_required`, `@owner_or_permission_required`
- [x] `shared/auth/permission_manager.py` — Single `PermissionManager` class + all `can_*()` helpers
- [x] `shared/responses.py` — `api_success()`, `api_error()`, `api_paginated()`
- [x] `shared/schemas.py` — Marshmallow base schemas (`NewsCreateSchema`, `CategorySchema`, etc.)

### 1.3 Docker

- [x] `Dockerfile` — Multi-stage (builder + runtime), non-root user, health check
- [x] `docker-compose.yml` — PostgreSQL 16 + Redis 7 + web service
- [x] `.dockerignore` — Exclude dev artifacts from image
- [x] `env.example` — Environment variable template

### 1.4 Dependencies

- [x] `marshmallow` added to `requirements.txt`
- [x] `psycopg2-binary` uncommented for PostgreSQL support
- [x] `.venv` created and verified working

---

## PHASE 2 — Fix Broken Public Elements ✅

- [x] **Social media links** — Added `footer-social.js` to news/editorial design base templates
- [x] **Brand asset paths** — Already using `brand_info.logo_header/logo_footer/favicon` with fallbacks
- [x] **Footer email + policy links** — Removed dead `#` links, added email to editorial footer
- [x] **Homepage unnecessary queries** — Removed unused `latest_videos`/`latest_images` from `routes_public.py`
- [x] **Categories display location** — Added `categories_with_counts` to `app/__init__.py` context processor

---

## PHASE 3 — RBAC / ABAC Refinement ✅

**Goal:** Migrate 100+ inline role checks to decorators. Seed default permissions.

### Infrastructure (Done in Phase 1.2)

- [x] `@permission_required(resource, action)` decorator
- [x] `@owner_or_permission_required(resource, action, owner_field)` decorator
- [x] Consolidated `PermissionManager` (single source of truth)
- [x] Consolidated `login_required` (JWT + session)
- [x] `admin_required` + `superuser_required` decorators in `shared/auth/decorators.py`
- [x] Replaced local `login_required` in `routes/common_imports.py` (−160 lines)
- [x] Replaced Flask-Login import in `routes/settings/common_imports.py`
- [x] Replaced `@unified_auth_required` → `@login_required` in `routes_auth.py`
- [x] Updated `routes/settings/root_seo.py` to use shared decorator

### Seeding

- [ ] Run `helper/init_permissions.py` — Seeds 35 permissions + 5 custom roles
- [ ] Add `flask seed permissions` CLI command
- [ ] Verify seed idempotency on re-runs

### Route Migration

- [ ] Replace `current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]` with `@permission_required()` in:
  - `routes/settings/brand.py`, `seo.py`, `account.py`, `contact.py`, `content.py`, `media.py`, `policies.py`, `performance.py`, `dashboard.py`
  - `routes/routes_images.py`, `routes_public.py`, `routes_users.py`, `routes_roles.py`, `routes_subscriptions.py`, `routes_infos.py`, `routes_analytics.py`, `routes_auth.py`, `routes_albums.py`
- [ ] Add `@owner_or_permission_required` to content routes (writers edit own content, admins edit any)

### Admin UI

- [ ] `/settings/roles` — CRUD for custom roles + permission assignment
- [ ] Permission summary on user management page
- [ ] Template enforcement: replace `{% if current_user.role.value == 'su' %}` with `can_*()` helpers

---

## PHASE 4 — Module Extraction (Vertical Slice Migration)

**Goal:** Migrate the monolithic `routes/` + `models.py` into domain modules. Each module owns its models, routes, schemas, and services.

### Target Structure

```
app/
├── __init__.py              # App factory
├── config.py                # Configuration classes
├── extensions.py            # Shared extension instances
├── modules/
│   ├── __init__.py
│   ├── auth/                # User, CustomRole, Permission, login/register/JWT
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── models.py
│   ├── news/                # News, Category, ShareLog
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── models.py
│   ├── albums/              # Album, AlbumChapter
│   ├── media/               # Image, YouTubeVideo
│   ├── users/               # Profile management (reuses auth User)
│   ├── subscriptions/       # UserSubscription
│   ├── seo/                 # RootSEO + injector
│   ├── settings/            # BrandIdentity, NavigationLink, ContactDetail, TeamMember
│   ├── policies/            # PrivacyPolicy, MediaGuideline, VisiMisi, Penyangkalan, PedomanHak
│   └── analytics/           # EmailLog, performance stats
├── shared/                  # Cross-cutting concerns
│   ├── auth/                # Decorators, PermissionManager
│   ├── schemas.py           # Base Marshmallow schemas
│   ├── responses.py         # API response helpers
│   └── utils/               # Email, image_utils, config_reader, etc.
├── modules/sidecars/        # Go sidecar source + proto definitions
│   ├── proto/               # argus.proto, hermes.proto
│   ├── argus/               # Go source
│   ├── hermes/              # Go source
│   └── cerebro/             # Go source
└── templates/               # Jinja2 (design system intact)
```

### Extraction Order

| # | Module | Models to Extract | Route Files to Replace |
|---|--------|-------------------|----------------------|
| 1 | `auth` | User, CustomRole, Permission, UserActivity | `routes_auth.py`, `routes_users.py`, `routes_roles.py` |
| 2 | `news` | News, Category, ShareLog | `routes_news.py`, `routes_chategories.py` |
| 3 | `media` | Image, YouTubeVideo | `routes_images.py`, `routes_video.py` |
| 4 | `albums` | Album, AlbumChapter | `routes_albums.py` |
| 5 | `subscriptions` | UserSubscription | `routes_subscriptions.py` |
| 6 | `seo` | RootSEO | `routes_seo.py`, `seo_enhanced_dashboard.py`, `seo_settings_api.py` |
| 7 | `settings` | BrandIdentity, NavigationLink, ContactDetail, TeamMember | `routes/settings/*.py` |
| 8 | `policies` | PrivacyPolicy, MediaGuideline, VisiMisi, Penyangkalan, PedomanHak | `routes_infos.py` |
| 9 | `analytics` | EmailLog | `routes_analytics.py`, `routes_analytics.py` |

### Per-Module Migration Steps

1. Create `app/modules/{name}/models.py` — Move model classes from `models.py`
2. Create `app/modules/{name}/schemas.py` — Marshmallow schemas for validation
3. Create `app/modules/{name}/service.py` — Business logic extracted from route handlers
4. Create `app/modules/{name}/controller.py` — Thin route handlers (parse → service → respond)
5. Create `app/modules/{name}/__init__.py` — Blueprint registration
6. Wire blueprint in `app/__init__.py`
7. Verify all routes work, delete old route file
8. Run tests

---

## PHASE 5 — Sidecars (Go Microservices)

**Goal:** Port the enterprise sidecar architecture to the open-source version for observability, image processing, and high-performance read paths.

### 5.1 Infrastructure

- [ ] Copy `sidecars/` directory from enterprise (`/home/ubuntu/projects/lilyopencms/sidecars/`)
- [ ] Copy `sidecars/proto/` — `argus.proto`, `hermes.proto`
- [ ] Copy Go source for `argus/`, `hermes/`, `cerebro/` (adapt module paths)
- [ ] Update `go.mod` module path to `github.com/1999AZZAR/lilyopencms`
- [ ] Add sidecar Dockerfiles (already exist in enterprise)
- [ ] Add sidecar services to `docker-compose.yml`

### 5.2 Python gRPC Client Layer

- [ ] Create `app/shared/rpc/` — Python gRPC client package
- [ ] Generate protobuf stubs: `argus_pb2.py`, `argus_pb2_grpc.py`, `hermes_pb2.py`, `hermes_pb2_grpc.py`
- [ ] Create `app/shared/rpc/argus_client.py` — Singleton `ArgusClient` with circuit breaker
- [ ] Create `app/shared/rpc/hermes_client.py` — Singleton `HermesClient` with PIL fallback
- [ ] Create `app/shared/rpc/argus_logging.py` — `ArgusLogHandler` for Python logging

### 5.3 Circuit Breaker

- [ ] Port `celery_app/circuit_breaker.py` → `app/shared/circuit_breaker.py`
- [ ] `CircuitBreaker`, `CircuitBreakerRegistry`, `@circuit_breaker` decorator
- [ ] Pre-configured breakers: `argus_log`, `argus_analytics`, `argus_metrics`, `hermes_process`

### 5.4 Argus (Observability Sidecar)

| RPC Method | Purpose | Python Client |
|------------|---------|---------------|
| `Log` | Centralized log aggregation → Elasticsearch | `argus_client.log(level, message, service)` |
| `TrackEvent` | Analytics events (page views, purchases) | `argus_client.track_event(event_type, user_id, props)` |
| `SubmitMetrics` | System metrics (latency, throughput) | `argus_client.submit_metrics(name, value, tags)` |

- [ ] Wire `setup_unified_logging()` in `create_app()` to add `ArgusLogHandler`
- [ ] Instrument route handlers with `argus_client.track_event()` for page views
- [ ] Add metrics submission for request latency, DB query time

### 5.5 Hermes (Image Processing Sidecar)

| Feature | Enterprise | Fallback |
|---------|-----------|----------|
| Format conversion | WebP, JPEG, PNG via libvips | PIL/Pillow |
| Quality reduction loop | Auto-compress to 170-500KB | Manual |
| Emergency dimension scaling | Scale down 10% iteratively | Manual resize |

- [ ] Wire `hermes_client.process_image()` into image upload route
- [ ] Automatic WebP conversion on upload
- [ ] Thumbnail generation via Hermes
- [ ] PIL fallback when Hermes is down

### 5.6 Cerebro (Read-Path Gateway)

| Feature | Description |
|---------|-------------|
| L1 Cache | In-memory (go-cache, 5min TTL) |
| L2 Cache | Redis (10min TTL) |
| Cache Invalidation | Redis Pub/Sub channel `cache_invalidation` |
| Search | Elasticsearch multi_match with fuzziness |
| News List | Direct PostgreSQL query with caching |
| Health | `/healthz` (liveness), `/readyz` (readiness) |

- [ ] Add Cerebro service to `docker-compose.yml`
- [ ] Point public search endpoint to Cerebro `/api/public/search`
- [ ] Configure cache invalidation from Flask on news/album CRUD
- [ ] Add Elasticsearch to docker-compose (if not present)

### 5.7 Docker Compose (Full Stack)

```yaml
services:
  web:              # Flask app (gunicorn)
  celery-worker:    # Async task processing
  celery-beat:      # Periodic tasks
  db:               # PostgreSQL 16
  redis:            # Redis 7 (caching + Celery broker)
  elasticsearch:    # Elasticsearch 8 (search + Argus storage)
  argus-sidecar:    # Go gRPC — logging, analytics, metrics
  hermes-sidecar:   # Go gRPC — image processing
  cerebro-sidecar:  # Go HTTP — cached read path, search
```

---

## PHASE 6 — Celery Async Workers

**Goal:** Move long-running tasks to Celery workers. Port the enterprise celery_app structure.

### 6.1 Infrastructure

- [ ] Add `celery` + `redis` to requirements.txt
- [ ] Create `app/tasks/__init__.py` — Celery app factory
- [ ] Create `app/tasks/celery_config.py` — Broker, backend, routing
- [ ] Add `celery-worker` and `celery-beat` services to docker-compose

### 6.2 Tasks to Port

| Task | Source | Purpose |
|------|--------|---------|
| `scheduled_publish` | `celery_app/scheduled_publish.py` | Auto-publish scheduled content |
| `popularity_updater` | `celery_app/popularity_updater.py` | Batch update read counts |
| `backup_tasks` | `celery_app/backup_tasks.py` | Automated DB backups |
| `elasticsearch_sync` | `celery_app/elasticsearch_sync.py` | Sync PG → ES indices |
| `auto_accept_requests` | `celery_app/auto_accept_requests.py` | Auto-approve write access |
| `database_optimization` | `celery_app/database_optimization.py` | VACUUM, ANALYZE, index rebuild |

### 6.3 Monitoring

- [ ] Port `celery_monitoring.py` — Worker health tracking
- [ ] Port `celery_alerting.py` — Failure notifications
- [ ] Port `flower_config.py` — Flower dashboard setup

---

## PHASE 7 — Toggle Cleanup + Premium Integration

### Feature Toggle Cleanup

8 toggles exist in model/admin but have zero public UI:
- `enable_comments`, `enable_ratings` — no comment/rating UI
- `enable_ads`, `enable_campaigns` — no ad/campaign system
- `enable_bookmarks`, `enable_reading_history`, `enable_community`, `enable_user_stats` — no UI

- [ ] Decide: remove from model + admin, or implement stubs
- [ ] Remove or implement categories display location

### Premium Integration

- [ ] Replace hardcoded pricing with `BrandIdentity` fields or `Plan` model
- [ ] Wire subscribe buttons to `UserSubscription` flow
- [ ] Make feature list admin-editable

### Route Guards

- [ ] `/news`, `/articles`, `/utama` — add `_feature_enabled('enable_news')` guard
- [ ] `/hypes` — add guard or create `enable_hypes`
- [ ] Album routes — add `_feature_enabled('enable_albums')` guard
- [ ] Nav fallback respects feature toggles

---

## DEPENDENCY VULNERABILITIES & UPGRADES

**34 Dependabot alerts + 7 bump PRs open**

### P0 — Framework (High/Critical CVEs)

- [ ] **Werkzeug** `2.3.7 → ~3.1.6` — RCE via debugger, DoS, decompression bomb
- [ ] **Flask** `2.3.3 → ~3.1.3` — Missing `Vary: Cookie` header
- [ ] **Jinja2** `3.1.2 → latest` — Sandbox breakout, HTML attr injection
- [ ] **Gunicorn** `21.2.0 → latest` — Request smuggling, decompression bomb

### P1 — HTTP & Networking

- [ ] **urllib3** `2.1.0 → ~2.7.0` — Header leak, redirect bypass, temp file
- [ ] **requests** `2.31.0 → ~2.33.0` — .netrc leak, verify=False bypass
- [ ] **idna** `3.6 → ~3.15` — DoS, unicode bypass

### P2 — Security & Auth

- [ ] **Flask-CORS** `4.0.0 → latest` — Private network header, regex bypass
- [ ] **python-dotenv** `1.0.0 → ~1.2.2` — Symlink file overwrite

### P3 — Repo Housekeeping

- [ ] Enable GitHub Code Scanning + Secret Scanning
- [ ] Migrate `python-memcached` → `redis` as primary cache
- [ ] Evaluate `APScheduler` → `celery` for async task queue
