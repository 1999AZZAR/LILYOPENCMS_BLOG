# TODO — LILY OpenCMS Open Source Version

> Based on investigation of enterprise version at `/home/azzar/project/LOC/LILYOPENCMS`
> Current open-source version at `/home/azzar/project/LILYcms_based/LILYOPENCMS_BLOG`

---

## PHASE 0 — Multi-Design System Engine

**Goal:** `brand_info.homepage_design` becomes the design system selector. Custom Jinja2 loader resolves templates from `templates/designs/{design}/` first. Adding a new design = drop a directory.

### Infrastructure (Done)

- [x] Create `DesignFileSystemLoader` — subclass of Jinja2 `FileSystemLoader` that checks `g.design` and tries `templates/designs/{design}/{path}` before falling back to default
- [x] Wire loader in `main.py` + `before_request` to set `g.design` from `BrandIdentity.homepage_design`
- [x] Move all current public templates into `templates/designs/news/` (current `homepage_design = "news"` becomes the Swiss-Archival design)
- [x] Update card dispatcher to resolve per-design: `designs/{design}/components/cards/_card_dispatcher.html`
- [x] Update admin brand UI: relabel "Homepage Design" → "Design System", update description/options
- [x] Verify admin/settings/email templates are excluded from design resolution (always use default path)

### Adding Future Designs

To add a new design (e.g. `"minimal"`, `"editorial"`, `"magazine"`):
- Create `templates/designs/{name}/` with only the templates that differ
- Everything else falls through to default templates
- Add its name to the admin selection dropdown

---

## HIGH PRIORITY

### 1. Fix Broken Public Site Elements

- [ ] **Social media links** — `footer.html` has empty `<div id="social-links-container">`. Needs a small inline script or new `static/js/public-footer.js` that fetches `GET /api/social-media` (public endpoint) and renders icon links in footer.
- [ ] **Brand asset paths** — `base.html` logo/favicon and `footer.html` logo use hardcoded `/static/pic/logo.png` instead of `brand_info.logo_header/logo_footer/favicon`. Update with fallback to hardcoded.
- [ ] **Footer email + policy links** — `mailto:hello@example.com` should use `brand_info.website_url` or admin-configured contact. Privacy/tos links point to `#`.
- [ ] **Homepage unnecessary queries** — `home()` route fetches `latest_videos`, `latest_images`, `latest_articles` but `index.html` never renders them. Remove or wrap in `_feature_enabled()`.

### 2. Missing Route Guards

- [ ] `/news` — add `_feature_enabled('enable_news')` guard
- [ ] `/articles` — add `_feature_enabled('enable_news')` guard
- [ ] `/utama` — add `_feature_enabled('enable_news')` guard
- [ ] `/search` — consider guard or skip (innocuous)
- [ ] `/hypes` — add guard (no matching toggle exists; skip or create `enable_hypes`)

### 3. Nav Fallback Respects Toggles

- [ ] `base.html:115-119` — fallback nav items (when no `navbar_links`) hardcodes Utama/Berita/Artikel regardless of feature toggles. Should check `enable_news`, `enable_about`, `enable_videos`, `enable_gallery` before including their links.

### 4. Implement or Remove Stale Feature Toggles

8 toggles exist in model/admin but have zero public UI:
- `enable_comments`, `enable_ratings` — no comment/rating UI exists.
- `enable_ads`, `enable_campaigns` — no ad/campaign system.
- `enable_bookmarks`, `enable_reading_history`, `enable_community`, `enable_user_stats` — no UI.
- [ ] Decide: remove from model + admin, or implement stubs.

### 5. Premium Page Integration

- [ ] Replace hardcoded pricing with `BrandIdentity` fields or a `Plan` model
- [ ] Wire subscribe buttons to actual `UserSubscription` flow
- [ ] Make feature list admin-editable

---

## MEDIUM PRIORITY

### 6. Categories Display Location Rendering

`brand_info.categories_display_location` exists in DB + admin UI but zero public templates check it. Either implement body/navbar rendering or remove the setting entirely.

### 7. Album Route Guard

- [ ] Album routes — add `_feature_enabled('enable_albums')` guard

---

## LOW PRIORITY / NICE-TO-HAVE

- [ ] Email analytics dashboard (enterprise has it)
- [ ] `enhanced-navigation.js` for admin (mobile menu, focus trap)
- [ ] Lazy-load social icons in footer with IntersectionObserver

---

## PHASE 1.5 — RBAC / ABAC Refinement

**Goal:** Fix the fragmented access control system, consolidate the permission infrastructure, seed default roles/permissions, and enforce consistent authorization across all routes with both role-based and attribute-based rules.

### Infrastructure Consolidation

- [ ] **Fix duplicate `unified_auth_required`** — Two definitions exist: `auth_helpers.py:227` and `unified_auth.py:330`. Consolidate to one, delete the other.
- [ ] **Consolidate `User.has_permission()` vs `PermissionManager.has_permission()`** — `models.py:269` hardcodes GENERAL rules; `permission_manager.py:129` delegates to custom_role permissions. Merge into a single source of truth in `PermissionManager`, make `User.has_permission()` delegate to it.
- [ ] **Create unified `@permission_required(resource, action)` decorator** — Wraps `PermissionManager.has_permission()` so routes can do `@permission_required("news", "create")` instead of inline `current_user.role` checks.
- [ ] **Create `@owner_or_permission_required(resource, action, owner_field="user_id")` decorator** — ABAC: allows access if user is the resource owner OR has the permission. E.g., a GENERAL writer can edit their own news, ADMIN can edit any.

### Seeding

- [ ] **Run `helper/init_permissions.py`** — Seeds 35 granular permissions (users CRUD+suspend, roles CRUD, permissions CRUD, news CRUD+publish, images CRUD, videos CRUD, settings read/update, categories CRUD) and 5 custom roles (Content Editor, Content Moderator, Media Manager, User Manager, System Administrator).
- [ ] **Verify seed idempotency** — Script already checks for existing records before inserting. Confirm it handles re-runs cleanly.
- [ ] **Add seed script to `main.py` CLI** — Expose `flask seed permissions` command via `click` group in `main.py` so it runs inside app context without manual `PYTHONPATH` hacks.

### Route Migration

- [ ] **Replace inline `current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]`** patterns (100+ occurrences) with `@permission_required()` decorator:
  - `routes/settings/brand.py` — All brand routes
  - `routes/settings/seo.py` — All SEO routes
  - `routes/settings/account.py` — User management routes
  - `routes/settings/contact.py` — Contact & team routes
  - `routes/settings/content.py` — Content management routes
  - `routes/settings/media.py` — Media management routes
  - `routes/settings/policies.py` — Legal/policy routes
  - `routes/settings/performance.py` — Performance routes
  - `routes/settings/dashboard.py` — Analytics dashboard
  - `routes/routes_images.py` — Image management
  - `routes/routes_public.py` — Album, navigation routes
  - `routes/routes_users.py` — User management API
  - `routes/routes_roles.py` — Permission/role API (already uses `has_permission()`)
  - `routes/routes_subscriptions.py` — Subscription management
  - `routes/routes_infos.py` — Stats & info endpoints
  - `routes/routes_analytics.py` — Performance dashboard
  - `routes/routes_auth.py` — Auth settings pages
  - `routes/routes_albums.py` — Album management
- [ ] **Add ABAC `@owner_or_permission_required` to content routes** — Writers (GENERAL) can edit/delete only their own news/albums/images; admins/superusers can edit any.

### Admin UI for Permissions

- [ ] **Create admin page for managing custom roles** — `/settings/roles` with CRUD for custom roles + permission assignment (API exists in `routes/routes_roles.py`, no UI).
- [ ] **Add permission management card** — Card on settings dashboard linking to `/settings/roles`.
- [ ] **Add user permission summary** — Show assigned custom_role + effective permissions on user management page.

### Template Enforcement

- [ ] **Audit all admin templates** for hardcoded role checks (`{% if current_user.role.value == 'su' %}`) and replace with `can_*()` template helpers from `permission_manager.py`.
- [ ] **Hide UI elements based on permissions** — E.g., hide "Delete" buttons from users without `news:delete`, hide "Users" nav from non-admin.

---

## Implementation Order

```
Phase 0 — Design System Engine (FOUNDATION) ✅
├── Custom Jinja2 loader (DesignFileSystemLoader)
├── Move templates into designs/news/
├── Wire before_request + g.design
├── Card dispatcher per-design
├── Update admin homepage_design → design_system selector

Phase 1 — Fix Broken Public Elements
├── Social media links in footer
├── Brand asset paths (logo, favicon, footer logo)
├── Footer email + links
├── Remove unused homepage DB queries

Phase 1.5 — RBAC / ABAC Refinement
├── Consolidate duplicate permission logic (User.has_permission vs PermissionManager)
├── Fix duplicate unified_auth_required
├── Create @permission_required() + @owner_or_permission_required() decorators
├── Seed default permissions + custom roles (init_permissions.py)
├── Expose flask seed permissions CLI command
├── Migrate 100+ inline role checks to decorators
├── Admin UI for custom role management + assignment
├── Template enforcement: replace raw role checks with can_*() helpers

Phase 2 — Route Guards & Nav Fixes
├── Missing guards: /news, /articles, /utama, /hypes
├── Nav fallback respects feature toggles

Phase 3 — Toggle Cleanup
├── Remove or implement 8 stale feature toggles
├── Categories display: implement or remove

Phase 4 — Premium Integration
├── Admin-editable pricing / plans
├── Wire to subscription flow

---

## DEPENDENCY VULNERABILITIES & UPGRADES

**34 Dependabot alerts + 7 bump PRs open** — all packages severely outdated. Pin versions in `requirements.txt` cause cascading CVEs. Strategy: upgrade each package to latest compatible, verify zero breaking changes.

### P0 — Framework (High/Critical CVEs)

- [ ] **Werkzeug** `2.3.7 → ~3.1.6` — 6 alerts. **HIGH**: RCE via debugger (7.5, GHSA-2g68-c3qc-8985), DoS resource exhaustion (7.5), decompression bomb bypass (7.5), DoS high-resource multipart (5.7), Windows device name (2 alerts)
- [ ] **Flask** `2.3.3 → ~3.1.3` — 1 alert (missing `Vary: Cookie` header). PR #7
- [ ] **Jinja2** `3.1.2 → latest` — 4 alerts. **HIGH**: sandbox breakout via filenames (8.8), via indirect format ref (7.8), HTML attr injection x2 (5.4)
- [ ] **Gunicorn** `21.2.0 → latest` — 2 alerts. **HIGH**: request smuggling → endpoint bypass (8.2), decompression bomb (7.5)

### P1 — HTTP & Networking

- [ ] **urllib3** `2.1.0 → ~2.7.0` — 5 alerts (header leak 5.3, redirect bypass 5.3, temp file 4.4, proxy leak 4.4, compressed data DoS). PR #2
- [ ] **requests** `2.31.0 → ~2.33.0` — 2 alerts (.netrc leak 5.3, verify=False bypass 5.6). PR #5
- [ ] **idna** `3.6 → ~3.15` — 2 alerts (DoS 6.2, unicode bypass). PR #4

### P2 — Security & Auth

- [ ] **Flask-CORS** `4.0.0 → latest` — 5 alerts (private network header 7.5, regex bypass 5.3, case sensitivity 5.3, log injection 5.3, inconsistent matching 5.3)
- [ ] **python-dotenv** `1.0.0 → ~1.2.2` — 1 alert (symlink file overwrite 6.6). PR #1

### P3 — Dev / Low Severity

- [ ] **pytest** `7.4.3 → ~9.0.3` — 1 alert (tmpdir 6.8). PR #3
- [ ] **certifi** `2023.11.17 → latest` — GLOBALTRUST removal (informational)

### P4 — Repo Housekeeping

- [ ] Enable GitHub **Code Scanning** in repo settings
- [ ] Enable GitHub **Secret Scanning** in repo settings
- [ ] Review & update remaining pinned packages to latest compatible
- [ ] Uncomment PostgreSQL (`psycopg2-binary`) and MySQL (`PyMySQL`) drivers for prod
- [ ] Migrate from `python-memcached` → `redis` as primary cache (memcached unmaintained)
- [ ] Evaluate `APScheduler` → `celery` for async task queue
```
