# LilyOpenCMS API & Endpoint Reference

A comprehensive, grouped list of all CRUD and callable endpoints in LilyOpenCMS, including HTTP method, path, authentication, and description.

---

## News
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/news`                              | Yes  | List news articles (with filters)           |
| POST   | `/api/news`                              | Yes  | Create a new article                        |
| GET    | `/api/news/<news_id>`                    | Yes  | Get article details                         |
| PUT    | `/api/news/<news_id>`                    | Yes  | Update article                              |
| DELETE | `/api/news/<news_id>`                    | Yes  | Delete article                              |
| PATCH  | `/api/news/<news_id>/visibility`         | Yes  | Toggle article visibility                   |
| GET    | `/api/news/owned`                        | Yes  | List news owned by current user             |
| POST   | `/api/news/<news_id>/track-share`        | No   | Track a share action for a news article     |
| GET    | `/api/news/<news_id>/share-data`         | No   | Get share counts for a news article         |

## Albums
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/albums`                            | Yes  | List albums (with filters)                  |
| POST   | `/api/albums`                            | Yes  | Create a new album                          |
| GET    | `/api/albums/<album_id>`                 | Yes  | Get album details                           |
| PUT    | `/api/albums/<album_id>`                 | Yes  | Update album                                |
| DELETE | `/api/albums/<album_id>`                 | Yes  | Delete album                                |
| PATCH  | `/api/albums/<album_id>/visibility`      | Yes  | Toggle album visibility                     |
| PATCH  | `/api/albums/<album_id>/archive`         | Yes  | Archive album                               |
| PATCH  | `/api/albums/<album_id>/unarchive`       | Yes  | Unarchive album                             |
| POST   | `/api/albums/<album_id>/chapters`        | Yes  | Add chapter to album                        |
| DELETE | `/api/albums/<album_id>/chapters/<chapter_id>` | Yes | Remove chapter from album           |

## Users
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/users`                             | Yes  | List users                                  |
| POST   | `/api/users`                             | Yes  | Create a new user                           |
| GET    | `/api/users/<user_id>/performance`       | Yes  | Get user performance metrics                |
| GET    | `/api/users/performance/leaderboard`     | Yes  | Get user leaderboard                        |
| GET    | `/api/users/performance/report`          | Yes  | Get user performance report                 |
| GET    | `/api/users/<user_id>/performance/export`| Yes  | Export user performance data                |
| PATCH  | `/api/users/<user_id>/verify`            | Yes  | Verify user                                 |
| PATCH  | `/api/users/<user_id>/status`            | Yes  | Activate/deactivate user                    |
| PUT    | `/api/users/<user_id>`                   | Yes  | Update user details                         |
| DELETE | `/api/users/<user_id>`                   | Yes  | Delete user                                 |
| POST   | `/api/users/bulk/status`                 | Yes  | Bulk update user status                     |
| POST   | `/api/users/bulk/role`                   | Yes  | Bulk update user roles                      |
| POST   | `/api/users/bulk/verify`                 | Yes  | Bulk verify users                           |
| POST   | `/api/users/bulk/suspend`                | Yes  | Bulk suspend users                          |
| POST   | `/api/users/bulk/delete`                 | Yes  | Bulk delete users                           |
| POST   | `/api/users/bulk/export`                 | Yes  | Bulk export users                           |
| GET    | `/api/user/role`                         | Yes  | Get current user's role                     |
| GET    | `/api/settings/verified-users`           | Yes  | List verified users                         |
| POST   | `/api/users/<user_id>/suspend`           | Yes  | Suspend user                                |
| POST   | `/api/users/<user_id>/unsuspend`         | Yes  | Unsuspend user                              |
| GET    | `/api/users/<user_id>/activities`        | Yes  | Get user activities                         |

## Images
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/images`                            | Yes  | List images (with filters)                  |
| POST   | `/api/images`                            | Yes  | Upload a new image                          |
| GET    | `/api/images/<image_id>`                 | Yes  | Get image details                           |
| PUT    | `/api/images/<image_id>`                 | Yes  | Update image                                |
| DELETE | `/api/images/<image_id>`                 | Yes  | Delete image                                |
| PATCH  | `/api/images/<image_id>/visibility`      | Yes  | Toggle image visibility                     |
| POST   | `/api/images/bulk-delete`                | Yes  | Bulk delete images                          |
| POST   | `/api/images/bulk-visibility`            | Yes  | Bulk update image visibility                |
| GET    | `/api/images/<image_id>/usage`           | Yes  | Get image usage statistics                  |

## Videos (YouTube)
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/youtube_videos`                    | Yes  | List YouTube videos                         |
| POST   | `/api/youtube_videos`                    | Yes  | Add a new YouTube video                     |
| GET    | `/api/youtube_videos/<video_id>`         | Yes  | Get YouTube video details                   |
| PUT    | `/api/youtube_videos/<video_id>`         | Yes  | Update YouTube video                        |
| DELETE | `/api/youtube_videos/<video_id>`         | Yes  | Delete YouTube video                        |
| POST   | `/api/youtube_videos/bulk-delete`        | Yes  | Bulk delete YouTube videos                  |
| POST   | `/api/youtube_videos/bulk-visibility`    | Yes  | Bulk update video visibility                |
| GET    | `/api/youtube_videos/latest`             | Yes  | Get latest YouTube videos                   |

## Categories
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/categories`                        | Yes  | List categories                             |
| POST   | `/api/categories`                        | Yes  | Create a new category                       |
| PUT    | `/api/categories/<category_id>`          | Yes  | Update category                             |
| DELETE | `/api/categories/<category_id>`          | Yes  | Delete category                             |

## Tags
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/tags`                              | Yes  | List tags                                   |

## Navigation Links
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/navigation-links`                  | Yes  | List navigation links                       |
| POST   | `/api/navigation-links`                  | Yes  | Create a new navigation link                |
| PUT    | `/api/navigation-links/<link_id>`        | Yes  | Update navigation link                      |
| DELETE | `/api/navigation-links/<link_id>`        | Yes  | Delete navigation link                      |
| POST   | `/api/navigation-links/bulk-update`      | Yes  | Bulk update navigation links                |

## Roles & Permissions
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/roles`                             | Yes  | List roles                                  |
| POST   | `/api/roles`                             | Yes  | Create a new role                           |
| PUT    | `/api/roles/<role_id>`                   | Yes  | Update role                                 |
| DELETE | `/api/roles/<role_id>`                   | Yes  | Delete role                                 |
| GET    | `/api/roles/<role_id>/permissions`       | Yes  | Get role permissions                        |
| PUT    | `/api/roles/<role_id>/permissions`       | Yes  | Update role permissions                     |
| GET    | `/api/permissions`                       | Yes  | List permissions                            |
| POST   | `/api/permissions`                       | Yes  | Create a new permission                     |
| PUT    | `/api/permissions/<permission_id>`       | Yes  | Update permission                           |
| DELETE | `/api/permissions/<permission_id>`       | Yes  | Delete permission                           |
| PUT    | `/api/users/<user_id>/role`              | Yes  | Update user's role                          |
| POST   | `/api/roles/bulk/export`                 | Yes  | Bulk export roles                           |

## Social Media
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/social-media`                      | Yes  | List social media links                     |
| POST   | `/api/social-media`                      | Yes  | Add a new social media link                 |
| GET    | `/api/social-media/<social_id>`          | Yes  | Get social media link details               |
| PUT    | `/api/social-media/<social_id>`          | Yes  | Update social media link                    |
| DELETE | `/api/social-media/<social_id>`          | Yes  | Delete social media link                    |

## Subscriptions
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/subscriptions/plans`               | Yes  | Get subscription plans                      |
| POST   | `/api/subscriptions/create`              | Yes  | Create subscription                         |
| POST   | `/api/subscriptions/cancel`              | Yes  | Cancel subscription                         |
| GET    | `/api/subscriptions/status`              | Yes  | Get subscription status                     |
| POST   | `/api/subscriptions/update-ad-preferences` | Yes | Update ad preferences                   |
| GET    | `/api/subscriptions/check-premium-access` | Yes | Check premium access                    |
| GET    | `/api/admin/subscriptions`               | Yes  | List all subscriptions (admin)              |
| PUT    | `/api/admin/subscriptions/<subscription_id>` | Yes | Update subscription (admin)            |

## SEO & Branding
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/seo/articles`                      | Yes  | List articles with SEO data                 |
| GET    | `/api/seo/articles/<article_id>`         | Yes  | Get SEO data for an article                 |
| PUT    | `/api/seo/articles/<article_id>`         | Yes  | Update SEO data for an article              |
| POST   | `/api/seo/bulk-update`                   | Yes  | Bulk update SEO data                        |
| GET    | `/api/seo/metrics`                       | Yes  | Get SEO metrics                             |
| GET    | `/api/seo/global-settings`               | Yes  | Get global SEO settings                     |
| POST   | `/api/seo/global-settings`               | Yes  | Update global SEO settings                  |
| POST   | `/api/seo/global-og`                     | Yes  | Update global Open Graph settings           |
| POST   | `/api/seo/global-twitter`                | Yes  | Update global Twitter settings              |
| POST   | `/api/seo/global-structured`             | Yes  | Update global structured data settings      |
| POST   | `/api/seo/apply-global-settings`         | Yes  | Apply global SEO settings                   |
| GET    | `/api/seo/categories`                    | Yes  | List SEO categories                         |
| GET    | `/api/brand-identity`                    | Yes  | Get brand identity assets                   |
| POST   | `/api/brand-identity`                    | Yes  | Update brand identity assets                |
| POST   | `/api/brand-colors`                      | Yes  | Update brand colors                         |
| GET    | `/api/brand-colors`                      | Yes  | Get brand colors                            |

## Team Members
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/team-members`                      | Yes  | List team members                           |
| POST   | `/api/team-members`                      | Yes  | Add a new team member                       |
| PUT    | `/api/team-members/<id>`                 | Yes  | Update team member                          |
| DELETE | `/api/team-members/<id>`                 | Yes  | Delete team member                          |

## Info, Policy, Contact
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/visi-misi`                         | No   | Get visi-misi sections                      |
| GET    | `/api/penyangkalan`                      | No   | Get penyangkalan sections                   |
| POST   | `/api/penyangkalan`                      | Yes  | Create penyangkalan section                 |
| PUT    | `/api/penyangkalan/<pid>`                | Yes  | Update penyangkalan section                 |
| GET    | `/api/contact-details`                   | No   | Get contact details                         |

## Performance & Optimization
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| POST   | `/api/performance/clear-cache`           | Yes  | Clear performance cache                     |
| GET    | `/api/performance/alerts`                | Yes  | Get performance alerts                      |
| GET    | `/api/performance/recommendations`       | Yes  | Get performance recommendations             |
| GET    | `/api/performance/summary`               | Yes  | Get performance summary                     |
| POST   | `/api/asset-optimization/compress`       | Yes  | Compress static assets                      |
| POST   | `/api/asset-optimization/clear-cache`    | Yes  | Clear asset cache                           |
| POST   | `/api/asset-optimization/regenerate-hashes`| Yes  | Regenerate asset hashes                    |
| POST   | `/api/asset-optimization/minify`         | Yes  | Minify CSS/JS assets                       |
| POST   | `/api/ssr-optimization/clear-cache`      | Yes  | Clear SSR template cache                    |
| POST   | `/api/ssr-optimization/optimize-cache`   | Yes  | Optimize SSR cache                          |
| POST   | `/api/ssr-optimization/cache-template`   | Yes  | Cache specific template                     |

## Cache Management
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/cache/status`                      | Yes  | Get cache status                            |
| POST   | `/api/cache/clear`                       | Yes  | Clear all caches                            |
| POST   | `/api/cache/invalidate/<pattern>`        | Yes  | Invalidate cache by pattern                 |
| GET    | `/api/cache/keys`                        | Yes  | List cache keys                             |

## Database Management
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/database/status`                   | Yes  | Get database status                         |
| POST   | `/api/database/optimize`                 | Yes  | Optimize database                           |
| POST   | `/api/database/cleanup`                  | Yes  | Clean up database                           |
| POST   | `/api/database/backup`                   | Yes  | Create database backup                      |
| GET    | `/api/database/backups`                  | Yes  | List database backups                       |

## System Status
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/api/system/status`                     | Yes  | Get system status                           |

## Registration & Auth
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/register`                              | No   | Registration page                           |
| POST   | `/register`                              | No   | Register a new user                         |
| GET    | `/login`                                 | No   | Login page                                  |
| POST   | `/login`                                 | No   | Login action                                |
| GET    | `/logout`                                | Yes  | Logout action                               |

## Settings/Admin Pages
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/settings`                              | Yes  | Settings dashboard                          |
| GET    | `/settings/account`                      | Yes  | Account settings page                       |
| GET    | `/settings/users`                        | Yes  | User management page                        |
| GET    | `/settings/analytics`                    | Yes  | Analytics dashboard                         |
| GET    | `/settings/seo`                          | Yes  | SEO management page                         |
| GET    | `/settings/create_news`                  | Yes  | Create news page                            |
| GET    | `/settings/manage_news`                  | Yes  | Manage news page                            |
| GET    | `/settings/albums`                       | Yes  | Album management page                       |
| GET/POST| `/settings/privacy-policy`              | Yes  | Privacy policy management                   |
| GET/POST| `/settings/media-guidelines`            | Yes  | Media guidelines management                 |
| GET/POST| `/settings/visi-misi`                   | Yes  | Visi-misi management                       |
| GET/POST| `/settings/pedomanhak`                  | Yes  | Pedoman hak management                      |
| GET/POST| `/settings/penyangkalan`                | Yes  | Penyangkalan management                     |
| GET/POST| `/settings/contact-details`             | Yes  | Contact details management                  |
| GET/POST| `/settings/team-members`                | Yes  | Team members management                     |
| GET    | `/settings/categories`                   | Yes  | Categories management page                  |
| GET    | `/settings/youtube`                      | Yes  | YouTube management page                     |
| GET    | `/settings/social-media`                 | Yes  | Social media management page                |
| GET    | `/settings/brand-identity`               | Yes  | Brand identity management page              |
| GET    | `/settings/performance`                  | Yes  | Performance monitoring dashboard            |
| GET    | `/settings/asset-optimization`           | Yes  | Asset optimization dashboard                |
| GET    | `/settings/ssr-optimization`             | Yes  | SSR optimization dashboard                  |

## Public/Pages
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/` or `/beranda`                        | No   | Homepage                                    |
| GET    | `/news`                                  | No   | News listing page                           |
| GET    | `/news/<news_id>`                        | No   | News detail page                            |
| GET    | `/news/<news_id>/<slug>`                 | No   | News detail page (SEO slug)                 |
| GET    | `/videos`                                | No   | Video listing page                          |
| GET    | `/gallery`                               | No   | Image gallery page                          |
| GET    | `/about`                                 | No   | About/team/contact page                     |
| GET    | `/utama`                                 | No   | Featured/premium news page                  |
| GET    | `/hypes`                                 | No   | Hypes/featured content page                 |
| GET    | `/articles`                               | No   | Articles page                               |
| GET    | `/search`                                | No   | Search page                                 |

## Sitemaps & Robots
| Method | Endpoint                                 | Auth | Description                                 |
|--------|------------------------------------------|------|---------------------------------------------|
| GET    | `/sitemap.xml`                           | No   | Main sitemap (SEO)                          |
| GET    | `/sitemap-news.xml`                      | No   | News-specific sitemap (SEO)                 |
| GET    | `/sitemap-index.xml`                     | No   | Sitemap index (SEO)                         |
| GET    | `/robots.txt`                            | No   | Robots.txt (SEO)                            |

---

> **Note:** All endpoints are listed, including those for admin/settings, public pages, and all CRUD operations. For endpoints with multiple methods (e.g., GET/POST), both are shown. Bulk and utility endpoints are included for completeness. The new Albums section includes all album and chapter management endpoints. 