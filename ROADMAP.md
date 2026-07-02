# LilyOpenCMS Roadmap — Multi-Use Case Architecture

## Current State (Phases 0–7 ✓)

| Layer | Status |
|---|---|
| App factory + config | ✅ Done |
| RBAC/ABAC (3 roles + custom) | ✅ Done |
| News/Category CRUD | ✅ Done |
| Media (images, videos, albums) | ✅ Done |
| Brand identity system | ✅ Done |
| SEO management | ✅ Done |
| Email system (SMTP, compose, outbox, log) | ✅ Done |
| 3 design themes (news, editorial, professional) | ✅ Done |
| Celery tasks (publish, popularity, backup, optimization) | ✅ Done |
| Go sidecars (Argus=search, Hermes=images, Cerebro=caching) | ✅ Done |
| Docker deployment (PostgreSQL, Redis, Gunicorn) | ✅ Done |

---

## Target Use Cases

| # | Use Case | Priority |
|---|---|---|
| 1 | Personal Blog | High |
| 2 | News Agency | High |
| 3 | Company Profile | Medium |
| 4 | E-commerce | Medium |

---

## Phase 8: Core CMS Foundation (gates all use cases)

> Everything below depends on this phase completing first.

### 8.1 Static Pages System
- [ ] `Page` model (title, slug, content, template, is_published, seo_id)
- [ ] CRUD routes + admin UI
- [ ] Template selection per page (default, landing, full-width, sidebar)
- [ ] Reusable blocks / components (hero, CTA, FAQ, testimonials)
- [ ] Pages: About, Services, Terms, Privacy (seed defaults)

### 8.2 Tag System (replace string field)
- [ ] `Tag` model (name, slug)
- [ ] `NewsTag` junction table
- [ ] Tag CRUD in admin
- [ ] Tag pages on frontend (`/tag/{slug}`)
- [ ] Tag cloud widget
- [ ] Auto-suggest from existing tags

### 8.3 Comment System
- [ ] `Comment` model (user_id, news_id, parent_id, content, status)
- [ ] Moderation queue (pending/approved/rejected)
- [ ] Nested replies (1 level)
- [ ] Spam detection (basic: link count, length)
- [ ] Email notification on reply
- [ ] Admin moderation UI

### 8.4 Author System
- [ ] Extend `User` model (bio, avatar, social links)
- [ ] Author profile pages (`/author/{username}`)
- [ ] Author listing page
- [ ] Author-specific RSS feed
- [ ] "Written by" card on articles

### 8.5 Content Enhancements
- [ ] Reading time estimate (auto-calc from content)
- [ ] Related articles (same category or tags)
- [ ] Table of contents (auto-generate from headings)
- [ ] Social sharing buttons (Twitter, Facebook, WhatsApp, Telegram)
- [ ] Open Graph / Twitter Card meta (extend existing SEO)
- [ ] RSS feed (per category, per author, global)

### 8.6 Sitemap
- [ ] XML sitemap generation (auto from models)
- [ ] Sitemap index for large sites
- [ ] Ping search engines on publish

### 8.7 Search Improvements
- [ ] Index all content in Cerebro/Elasticsearch
- [ ] Full-text search with ranking
- [ ] Search suggestions / autocomplete
- [ ] Search results page

---

## Phase 9: Personal Blog

> Minimal, writing-focused, beautiful reading experience.

### 9.1 Blog Design Theme
- [ ] `blog` design in `templates/designs/blog/`
- [ ] Clean, readable typography (Inter/Source Serif)
- [ ] Dark mode toggle
- [ ] Minimal navigation (Home, Tags, About)

### 9.2 Blog Features
- [ ] Reading list (bookmark articles)
- [ ] Newsletter subscription (leverage existing email system)
- [ ] Post view counter (already have `read_count`)
- [ ] "Recently read" section
- [ ] Markdown editor for posts (already have SimpleMDE)

### 9.3 Blog Admin
- [ ] Dashboard with writing stats
- [ ] Quick-publish workflow
- [ ] Draft management

---

## Phase 10: News Agency

> Multi-author, wire service, editorial workflow.

### 10.1 Editorial Workflow
- [ ] Article states: Draft → Review → Approved → Published → Archived
- [ ] `ArticleStatus` enum on News model
- [ ] Editor approval flow (Writer submits → Editor approves → Publish)
- [ ] Revision history (diff view)
- [ ] Embargo date field (publish at specific time, already have scheduled_at)

### 10.2 Multi-Author
- [ ] Byline system (multiple authors per article)
- [ ] `ArticleAuthor` junction table
- [ ] Author assignment (editor assigns to writer)
- [ ] Author workload dashboard

### 10.3 Wire Service
- [ ] `PressRelease` model (headline, body, embargo_date, source)
- [ ] Syndication feed (RSS/JSON Feed for partners)
- [ ] Embed codes for partners
- [ ] Usage analytics (who picked up what)

### 10.4 Breaking News
- [ ] Breaking news banner (JS widget)
- [ ] Push notification infrastructure
- [ ] Alert email to subscribers

### 10.5 Source Management
- [ ] `Source` model (name, url, reliability_score)
- [ ] Link sources to articles
- [ ] Source credibility tracking

### 10.6 News Agency Design
- [ ] `wire` design theme (dense, information-heavy)
- [ ] Photo essay layout
- [ ] Live blog / timeline format

---

## Phase 11: Company Profile

> Professional pages, services, team, contact.

### 11.1 Static Page Builder
- [ ] Block-based editor (hero, text, image, gallery, CTA, FAQ)
- [ ] `PageBlock` model (page_id, block_type, content, order)
- [ ] Drag-and-drop admin UI
- [ ] Template presets (landing, about, services, contact)

### 11.2 Services / Products Catalog
- [ ] `Service` model (name, description, icon, price_range, order)
- [ ] Service listing page
- [ ] Service detail pages

### 11.3 Team Management
- [ ] Extend existing `TeamMember` model
- [ ] Team listing page
- [ ] Individual profile pages
- [ ] Social links per member

### 11.4 Testimonials
- [ ] `Testimonial` model (name, role, company, content, rating, avatar)
- [ ] Testimonial carousel widget
- [ ] Admin CRUD

### 11.5 Contact Forms
- [ ] `ContactForm` model (name, email, subject, message, status)
- [ ] Form builder (simple: name, email, message, custom fields)
- [ ] Admin inbox with status (new/read/replied)
- [ ] Email notification on submission
- [ ] Auto-reply to submitter

### 11.6 Company Profile Design
- [ ] `corporate` design theme (professional, trust-building)
- [ ] Hero with CTA
- [ ] Client logo carousel
- [ ] Case studies layout

---

## Phase 12: E-commerce

> Products, cart, checkout, payments.

### 12.1 Product System
- [ ] `Product` model (name, slug, description, price, compare_price, sku, stock, weight, is_active)
- [ ] `ProductVariant` model (product_id, name, sku, price, stock, attributes JSON)
- [ ] `ProductImage` model (product_id, image_url, order, is_primary)
- [ ] `ProductCategory` model (name, slug, parent_id)
- [ ] `ProductTag` junction table
- [ ] Admin CRUD with variant management

### 12.2 Shopping Cart
- [ ] `Cart` model (user_id or session_id)
- [ ] `CartItem` model (cart_id, product_id, variant_id, quantity)
- [ ] Add/update/remove endpoints
- [ ] Cart persistence (session → user on login)
- [ ] Cart sidebar/widget

### 12.3 Checkout
- [ ] `Order` model (user_id, status, total, shipping_address, billing_address, notes)
- [ ] `OrderItem` model (order_id, product_id, variant_id, quantity, price)
- [ ] Checkout flow (address → shipping → payment → confirm)
- [ ] Guest checkout option

### 12.4 Payment Gateway
- [ ] `Payment` model (order_id, method, status, transaction_id, amount)
- [ ] Stripe integration (cards)
- [ ] Midtrans integration (Indonesian: VA, GoPay, OVO, etc.)
- [ ] Webhook handling for payment confirmation
- [ ] Refund management

### 12.5 Inventory
- [ ] Stock tracking (decrement on order)
- [ ] Low stock alerts
- [ ] Stock history log
- [ ] Bulk import/export (CSV)

### 12.6 Shipping
- [ ] `ShippingMethod` model (name, base_cost, per_kg_cost)
- [ ] Shipping calculation (weight-based or flat rate)
- [ ] Tracking number field
- [ ] Shipping label generation (JNE, J&T, SiCepat APIs)

### 12.7 Customer Accounts
- [ ] Order history page
- [ ] Order tracking
- [ ] Wishlist
- [ ] Product reviews & ratings

### 12.8 Promotions
- [ ] `Coupon` model (code, type, value, min_order, max_uses, expiry)
- [ ] `Discount` model (product_id, percentage/fixed, date range)
- [ ] Coupon application in checkout

### 12.9 E-commerce Design
- [ ] `shop` design theme (product-focused, conversion-optimized)
- [ ] Product grid with filters
- [ ] Product detail page
- [ ] Cart page
- [ ] Checkout page

---

## Shared Infrastructure (cross-cutting)

### Notification System
- [ ] `Notification` model (user_id, type, title, message, read, data)
- [ ] In-app notification bell
- [ ] Email notifications (extend existing)
- [ ] Push notifications (web push)

### API Layer
- [ ] REST API for mobile/headless
- [ ] API authentication (JWT tokens)
- [ ] Rate limiting
- [ ] API documentation (Swagger/OpenAPI)

### Multi-Site (optional, future)
- [ ] Tenant model (domain, settings)
- [ ] Site isolation (database or schema)
- [ ] Shared users across sites

---

## Execution Order

```
Phase 8 (Core CMS)        ← START HERE
  ├── 8.1 Static Pages
  ├── 8.2 Tags
  ├── 8.3 Comments
  ├── 8.4 Authors
  ├── 8.5 Content Enhancements
  ├── 8.6 Sitemap
  └── 8.7 Search

Phase 9 (Blog)            ← can parallel with Phase 10
Phase 10 (News Agency)    ← can parallel with Phase 9
Phase 11 (Company Profile)← after Phase 8
Phase 12 (E-commerce)     ← after Phase 8, longest phase

Shared Infrastructure     ← sprinkle across phases as needed
```

---

## Key Architectural Decisions (pending)

1. **E-commerce**: Separate module or integrated? → Module within same app
2. **Multi-site**: One DB or per-tenant? → One DB, site_id column
3. **Page builder**: Code blocks or visual? → Code blocks first, visual later
4. **Payment**: Which gateways first? → Stripe (global) + Midtrans (Indonesia)
