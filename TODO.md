# TODO — LILY OpenCMS Open Source Version

> Based on investigation of enterprise version at `/home/azzar/project/LOC/LILYOPENCMS`
> Current open-source version at `/home/azzar/project/LILYcms_based/LILYOPENCMS_BLOG`

---

## 1. Admin Nav Search Bar

**Enterprise reference:** `admin_base.html` lines 156-162 (HTML) + lines 1065-1181 (inline JS)

**What to implement:**
- [ ] Add search input HTML to sidebar in `admin_base.html` (placeholder "Cari menu...", search icon)
- [ ] Add JS event listener filtering logic:
  - Filter nav groups / subgroups / links by text match
  - Highlight matched text (`<mark>`)
  - Show/hide groups and subgroups based on match
  - Clear on Escape key and outside click
- [ ] Add `static/js/search-toggle.js` (already exists) — verify it handles sidebar search or only public navbar search
- [ ] Add `static/js/enhanced-navigation.js` from enterprise (597 lines, covers mobile menu, search, categories, dropdowns, keyboard nav) — but only port the sidebar search portion if public nav already works
- [ ] Subgroup nav structure: enterprise has nested groups → subgroups → links with role-based visibility. Current project has flat groups → links. Decide if subgroup nesting should be added

**Files to read from enterprise:**
- `templates/admin_base.html` (lines 156-162, 1065-1181)
- `static/js/enhanced-navigation.js` (lines 419-452 for search handling)
- `static/css/enhanced-navigation.css`

---

## 2. Full Email Functionality

### Current state (what already exists):
- `routes/utils/email_service.py` — `EmailService` class with all notification methods (1447 lines)
- `routes/utils/email_tasks.py` — Celery async email tasks (223 lines)
- `routes/utils/template_loader.py` — `EmailTemplateLoader` class
- 23 HTML + 20 TXT email templates in `templates/emails/`
- `EmailLog` model, `EmailType` enum, `EmailStatus` enum in `models.py`

### What's missing from open-source:

**Core email features to port:**
- [ ] `custom_email.html` template (enterprise has it, current doesn't) — 1 file
- [ ] `send_custom_email()` route from enterprise `routes/routes_users.py` (lines 2010-2034) — admin ability to send custom emails to users
- [ ] SMTP config files from `/home/azzar/project/LOC/LILYOPENCMS/config/`:
  - `alternative_smtp_setup.py`, `directadmin_smtp_setup.py`, `google_workspace_setup.py`
  - `sendgrid_setup.py`, `setup_gmail.py`, `smtp_config_helper.py`, `smtp_diagnostic.py`
  - `email_templates_preview.py`
  - `update_sendgrid_key.py`
- [ ] Redis rate limiting integration for email service (enterprise uses Redis for per-hour/per-day caps)
- [ ] Email analytics/statistics UI (enterprise likely has this in admin)

**SMTP config approach (enterprise):**
- Config file at `config/smtp_config.txt` with `KEY=VALUE` format
- Auto type coercion (booleans, integers, None)
- Falls back to hardcoded defaults
- Flask-Mail under the hood

---

## 3. Email Templates Redesign (SA Theme)

### Current state:
- All email templates use **generic blue gradient** (`#1e3a5f → #2d5a87`) header
- Generic blue CTA buttons (`#3b82f6 → #2563eb`)
- Gray footer (`#f8fafc` with `#e5e7eb` borders)
- No connection to the Swiss-Archival warm palette used in admin

### Redesign scope — all 23 HTML email templates + base:
- [ ] `templates/emails/_base.html` — redesign header gradient to use SA warm colors (coffee `#2A2520`, burgundy `#9C3D3B`, or accent-based gradient)
- [ ] Update CTA buttons to use SA accent/critical/success colors
- [ ] Update status bars (verification=blue, reset=amber, success=green) to use SA palette equivalents
- [ ] Update footer to use SA surface/border colors
- [ ] Audit each child template's inline styles against SA palette

**All HTML email templates to redesign (23 files):**
```
templates/emails/
├── _base.html                    (redesign base)
├── account_deletion_confirmation.html
├── account_deletion_request.html
├── account_verified.html
├── album_edit_request_submitted.html
├── chapter_published.html
├── content_approved_notification.html
├── content_deletion_notification.html
├── content_rejected_notification.html
├── contract_accepted.html        (TO REMOVE — see section 6)
├── contract_upgrade_approved.html (TO REMOVE)
├── contract_upgrade_rejected.html (TO REMOVE)
├── contract_upgrade_request.html  (TO REMOVE)
├── edit_request_approved.html
├── edit_request_rejected.html
├── editor_edit_request_notification.html
├── custom_email.html             (TO ADD — from enterprise)
├── password_reset_email.html
├── profile_update_confirmation.html
├── scheduled_content_published.html
├── suspension_notification.html
├── verification_email.html
├── write_access_approved.html
└── write_access_rejected.html
```

**SA color palette for email templates:**
| Role | Current Color | SA Equivalent |
|------|---------------|---------------|
| Header gradient | `#1e3a5f → #2d5a87` | `#2A2520 → #3D3530` (coffee tones) |
| CTA buttons | `#3b82f6` (blue) | `#9C3D3B` (accent burgundy) |
| Success/verified | `#10b981` (green) | `#4A7C59` (sa-success) |
| Warning/reset | `#f59e0b` (amber) | `#B8860B` (sa-warning) |
| Error/critical | `#ef4444` (red) | `#9C3D3B` (sa-critical) |
| Body bg | `#f4f6f9` | `#EFE9DC` (sa-bg-linen) |
| Card bg | `#ffffff` | `#FFFFFF` (keep white) |
| Border | `#e5e7eb` | `#D6CFC3` (sa-border) |
| Body text | `#334155` | `#2A2520` (sa-fg) |
| Muted text | `#64748b` | `#5C5550` (sa-fg-tertiary) |

---

## 4. Full SEO Functionality

### Current state (already exists, but gaps):
- All route files present: `routes_seo.py`, `seo_enhanced_dashboard.py`, `seo_settings_api.py`, `settings/seo.py`, `settings/root_seo.py`
- All seo_injector files present
- `templates/admin/seo/management.html` and `settings.html` exist
- `templates/settings/seo_management.html` and `root_seo_management.html` exist
- Some JS files exist: `seo-management.js`, `seo-analytics.js`, `root-seo-management.js`, `comprehensive-seo-management.js`
- CSS: `comprehensive-seo-management.css`

### Missing:
- [ ] `static/js/seo-settings.js` — enterprise has this, needed for SEO settings form handling
- [ ] `static/js/albums-seo-management.js` — enterprise has this
- [ ] `templates/admin/seo/analytics.html` — SEO analytics dashboard template (enterprise has this)
- [ ] `static/js/seo-analytics.js` — verify if current one matches enterprise version
- [ ] Verify all enterprise SEO routes and API endpoints are registered in current project's blueprint

### Files to audit:
- Compare `routes/routes_seo.py` (both versions) for any missing endpoints
- Compare `routes/settings/seo.py` (both versions)
- Compare `routes/settings/root_seo.py` (both versions)
- Compare `routes/seo_settings_api.py` (both versions)
- Compare `routes/seo_enhanced_dashboard.py` (both versions)

---

## 5. Dynamic robots.txt Generation

### Current state:
- Static `robots.txt` at project root (14 lines, basic allow/disallow)
- Route endpoint `GET /robots.txt` already registered in `main.py` (line 531 in README)

### What to implement:
- [ ] Replace static `robots.txt` with dynamic endpoint in `routes/routes_public.py`
- [ ] Query `seo_injection_settings` table for `website_url` (fallback to `request.url_root`)
- [ ] Two profiles based on `FLASK_ENV`: non-production (restrictive) vs production (permissive with crawler-specific directives for Googlebot, Bingbot, AdsBot)
- [ ] Add `update_robots_txt()` helper function in `routes/routes_helper.py` (writes static file on-demand, used during sitemap generation)
- [ ] Register `robots.txt` non-cached handler in `main.py` (enterprise lines 676-688)
- [ ] Update `docs/api.md` to document the endpoint

**Route signature (from enterprise):**
```python
@main_blueprint.route("/robots.txt")
def robots_txt():
    # Dynamic, environment-aware, reads website_url from DB
```

---

## 6. Remove Contract Management

### What to remove:

**Email templates (8 files):**
- [ ] `templates/emails/contract_accepted.html` + `.txt`
- [ ] `templates/emails/contract_upgrade_approved.html` + `.txt`
- [ ] `templates/emails/contract_upgrade_rejected.html` + `.txt`
- [ ] `templates/emails/contract_upgrade_request.html` + `.txt`

**Model enum values in `models.py`:**
- [ ] Remove `CONTRACT_UPGRADE_REQUEST`, `CONTRACT_UPGRADE_APPROVED`, `CONTRACT_UPGRADE_REJECTED`, `CONTRACT_ACCEPTED` from `EmailType` enum (lines 1779-1782)

**Email service methods in `routes/utils/email_service.py`:**
- [ ] Remove `send_contract_upgrade_request_notification()` (~lines 1301-1335)
- [ ] Remove `send_contract_upgrade_approved_notification()` (~lines 1337-1371)
- [ ] Remove `send_contract_upgrade_rejected_notification()` (~lines 1373-1408)
- [ ] Remove `send_contract_accepted_notification()` (~lines 1410-1443)

**Content deletion helper in `routes/utils/content_deletion_helper.py`:**
- [ ] Remove `UserContractAcceptance` and `ContractUpgradeRequest` imports (lines 42-43) — these are **broken imports** (classes don't exist in models.py)
- [ ] Remove or comment out contract-related code in:
  - `delete_album_related_records()` — raw SQL + stats logging (lines 221-230)
  - `delete_user_related_records()` — model queries for contracts (lines 466-474)

### What to KEEP (not open-source relevant, but harmless):
- Database migration file already has contract enum values — historical, leave it

---

## 7. Edge Cases & Compatibility

- [ ] All email templates use `{{ brand_name }}` and `{{ brand_info }}` from context — verify these are always passed by every route that sends email
- [ ] Email `_base.html` uses `url_for('static', filename='pic/logo.png', _external=True)` — verify this file exists in current project
- [ ] Robots.txt dynamic route queries `seo_injection_settings` table — verify this table exists and has `website_url` column
- [ ] `template_loader.py` loads templates from `templates/emails/` — verify path resolution works in current project structure
- [ ] Contract email templates reference `{{ contract_category_display }}` — these will break if the route somehow reaches them after removal, so ensure the email_service methods are removed too
- [ ] After removing contract code from `content_deletion_helper.py`, verify `delete_album_related_records` and `delete_user_related_records` still function correctly
- [ ] After removing `EmailType` enum values, verify the migration file doesn't need updating (historical migration can stay)

---

## 8. Implementation Order

```
Phase 1 — Cleanup (safe, non-breaking)
├── Remove contract email templates (8 files)
├── Remove contract EmailType enum values
├── Remove contract email_service methods
├── Fix broken imports in content_deletion_helper.py

Phase 2 — SEO Completion
├── Add missing seo-settings.js, albums-seo-management.js
├── Add seo/analytics.html template
├── Audit and sync all SEO route files with enterprise

Phase 3 — Email Enhancement
├── Add custom_email.html template
├── Add send_custom_email route
├── Port SMTP config helper files
├── Add Redis rate limiting for email

Phase 4 — Redesign
├── Redesign email _base.html with SA warm palette
├── Redesign all 20+ email templates
├── Update admin header gradient to match new palette

Phase 5 — New Features
├── Add admin sidebar search bar (HTML + JS)
├── Add sidebar search filtering logic
├── Add dynamic robots.txt endpoint
├── Add update_robots_txt() helper
├── Port navigation enhancement JS/CSS as needed
```
