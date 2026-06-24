# TODO — LILY OpenCMS Open Source Version

> Based on investigation of enterprise version at `/home/azzar/project/LOC/LILYOPENCMS`
> Current open-source version at `/home/azzar/project/LILYcms_based/LILYOPENCMS_BLOG`

---

## DONE

- [x] Card design system (dispatcher + 4 variants, `index`/`utama`/`news`/`articles`/`hypes` updated)
- [x] Brand color inline `<style>` block in `base.html` reads from DB
- [x] SEO blueprints registered (`seo_enhanced_bp`, `seo_settings_bp`)
- [x] Dynamic `/robots.txt`
- [x] Navigation management (bulk actions, copy, visibility)
- [x] Brand management (4 sub-pages, 20 color presets, form handlers)
- [x] Custom email template + route
- [x] All 19 email templates redesigned with SA warm palette
- [x] Contract/wallet system removed
- [x] Admin sidebar search
- [x] Route-level guards for `enable_videos`, `enable_gallery`, `enable_about`, `enable_premium`
- [x] Categories display location: `none` option added

---

## HIGH PRIORITY — Public UI Refinement

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

8 toggles exist in model/admin but have zero public UI. Decision needed:
- `enable_comments`, `enable_ratings` — no comment/rating UI exists. Add stub or remove.
- `enable_ads`, `enable_campaigns` — no ad/campaign system in open-source. Remove.
- `enable_bookmarks`, `enable_reading_history`, `enable_community`, `enable_user_stats` — no UI. Remove.

### 5. Premium Page Integration

- [ ] Replace hardcoded pricing with `BrandIdentity` fields or a `Plan` model
- [ ] Wire subscribe buttons to actual `UserSubscription` flow
- [ ] Make feature list admin-editable

---

## MEDIUM PRIORITY

### 6. Categories Display Location Rendering

`brand_info.categories_display_location` exists in DB + admin UI but zero public templates check it:
- `body`: render categories as a section on homepage
- `navbar`: render category dropdown in navbar
- `none`: current behavior (nothing)
Either implement body/navbar rendering or remove feature entirely.

### 7. Album Route Guard

- [ ] Album routes — add `_feature_enabled('enable_albums')` guard

---

## LOW PRIORITY / NICE-TO-HAVE

- [ ] Email analytics dashboard (enterprise has it)
- [ ] `enhanced-navigation.js` for admin sidebar (mobile menu, focus trap)
- [ ] Lazy-load social icons in footer with IntersectionObserver

---

## Implementation Order

```
Phase 1 — Fix Broken Public Elements
├── Social media links in footer
├── Brand asset paths (logo, favicon, footer logo)
├── Footer email + links
├── Remove unused homepage DB queries

Phase 2 — Route Guards & Nav Fixes
├── Missing guards: /news, /articles, /utama, /hypes
├── Nav fallback respects feature toggles

Phase 3 — Toggle Cleanup
├── Remove or implement 8 stale feature toggles
├── Categories display: implement or remove

Phase 4 — Premium Integration
├── Admin-editable pricing / plans
├── Wire to subscription flow
```
