# LILYOPENCMS_BLOG - Modern Content Management System

A comprehensive Flask-based content management system with advanced SEO features, multimedia management, and robust user permissions. Built for modern web publishing with automatic image optimization, comprehensive sitemap generation, and enterprise-grade security.

## 🚀 Features

### 🔍 Advanced SEO Engine (LOC Platform)
- **Smart Content Analysis:** Auto-readability scoring and keyword density extraction.
- **YAML-driven Quality Rules:** Custom limits for title, description, and keywords configured via `seo_injector/config/quality_rules.yaml`.
- **Lock-Protected Batch Injection:** Secure batch metadata generation and DB row injection.
- **Enhanced Diagnostics:** Full interactive dashboard (`admin/seo/analytics.html`) with health checking.

### 📝 Content Management
- **Advanced News Management**: Create, edit, delete articles with rich text editing
- **Album Management System**: Create albums containing multiple news/articles as chapters, like a novel structure
- **SEO Optimization**: Per-article SEO management (meta descriptions, keywords, Open Graph tags, Twitter Cards, Schema Markup)
- **Content Scheduling**: Schedule posts for future publication
- **Bulk Operations**: Mass edit, delete, and categorize content
- **Content Archiving**: Archive old content while preserving access
- **Content Duplication**: Clone articles for quick content creation
- **Revision History**: Track changes and restore previous versions
- **Related Articles**: Smart content suggestions

### 🎨 Media Management
- **Automatic Image Optimization**: WebP conversion, compression, and multiple thumbnail sizes
- **YouTube Integration**: Embed and manage YouTube videos
- **Gallery Management**: Organize and display image collections
- **Media Usage Tracking**: See which images are used where
- **Bulk Upload**: Multiple file upload with progress tracking
- **CDN Ready**: Optimized for content delivery networks

### 👥 User & Permission System
- **Custom Role System**: Beyond basic admin/general roles
- **Granular Permissions**: Matrix-based access control per feature
- **User Activity Tracking**: Login history, content creation, admin actions
- **Account Management**: Profile pictures, bios, social links
- **User Performance Metrics**: Track user contributions and activity
- **Account Suspension**: Temporary and permanent account restrictions
- **Registration Approval**: Admin-controlled user registration

### 🔍 SEO & Analytics
- **Comprehensive Sitemaps**: XML sitemaps for all content types
- **SEO Score Calculation**: Automated SEO scoring (0-100)
- **Meta Tag Management**: Complete meta tag control
- **Schema Markup**: JSON-LD structured data generation
- **Social Media Optimization**: Open Graph and Twitter Card support
- **Analytics Dashboard**: Content performance metrics
- **Search Engine Optimization**: URL slugs, canonical URLs, robots.txt

### 🛡️ Security & Performance
- **Advanced Security**: Rate limiting, input validation, CSRF protection
- **File Upload Security**: Virus scanning, type restrictions
- **Session Management**: Secure session handling with auto-logout
- **Database Security**: SQL injection protection with parameterized queries
- **Performance Optimization**: Redis caching, database optimization, lazy loading, progressive images
- **Performance Monitoring**: Real-time metrics, slow query detection, cache management

### 🎯 Premium & Subscription System
- **Premium Content**: Exclusive content for subscribers
- **Subscription Management**: Multiple subscription tiers
- **Ad-Free Experience**: Premium users get ad-free browsing
- **Content Gating**: Protect premium content with subscription requirements
- **Payment Integration**: Ready for payment gateway integration

## 🏗️ Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **Flask 2.x** - Web framework
- **SQLAlchemy** - ORM and database management
- **Alembic** - Database migrations
- **Flask-Login** - Authentication system
- **Flask-WTF** - Form handling and CSRF protection
- **Pillow (PIL)** - Image processing and optimization

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Modern JavaScript
- **SimpleMDE** - Markdown editor
- **Swiper.js** - Touch slider for featured content

### Database
- **SQLite** - Default database (production-ready alternatives supported)
- **PostgreSQL/MySQL** - Production database options

### Deployment
- **Gunicorn** - WSGI server
- **Passenger** - Alternative WSGI server
- **Docker** - Containerization ready

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git
- Redis (for performance optimizations)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/1999AZZAR/LILYOPENCMS_BLOG.git
   cd LILYOPENCMS_BLOG
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Redis (Required for performance optimizations)**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```
   
   **macOS:**
   ```bash
   brew install redis
   brew services start redis
   ```
   
   **Windows:**
   ```bash
   # Download from https://redis.io/download
   # Or use WSL2 with Ubuntu instructions above
   ```
   
   **Using the provided setup script:**
   ```bash
   chmod +x optimizations/setup_redis.sh
   ./optimizations/setup_redis.sh
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Initialize database**
   ```bash
   flask db upgrade
   ```

7. **Seed initial data (optional)**
   ```bash
   cd helper
   python generate_user.py
   python add_categories.py
   python add_fake_news.py
   python add_fake_images.py
   python add_videos.py
   python init_footer_data.py
   ```

8. **Run the application**
   ```bash
   python main.py
   ```

   Open `http://127.0.0.1:5000` in your browser.

### Redis Configuration

The application uses Redis for caching and performance optimizations. Make sure Redis is running before starting the application.

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Test Redis connection from Python:**
```bash
python -c "import redis; r = redis.Redis(); print('Redis connection:', r.ping())"
```

**Redis Configuration Options:**
- **Default**: `redis://localhost:6379/0`
- **With Password**: `redis://:password@localhost:6379/0`
- **Custom Host/Port**: Set `REDIS_HOST` and `REDIS_PORT` in `.env`

## 🗂️ Project Structure

```
belum-bernama/
├── main.py                    # Application entry point
├── models.py                  # Database models and relationships
├── passenger_wsgi.py          # Passenger WSGI entry point
├── requirements.txt           # Python dependencies
├── robots.txt                 # Search engine directives
├── generate_test_data.sh     # Test data generation script
│
├── routes/                    # Flask route blueprints
│   ├── __init__.py           # Blueprint initialization
│   ├── common_imports.py     # Shared imports and utilities
│   ├── routes_analytics.py   # Analytics and dashboard routes
│   ├── routes_auth.py        # Authentication routes
│   ├── routes_categories.py  # Category management
│   ├── routes_helper.py      # Sitemap generation and utilities
│   ├── routes_images.py      # Image management
│   ├── routes_infos.py       # Information pages and policies
│   ├── routes_news.py        # News management
│   ├── routes_public.py      # Public-facing routes and navigation
│   ├── routes_roles.py       # Role and permission management
│   ├── routes_socialmedia.py # Social media management
│   ├── routes_subscriptions.py # Premium and subscription system
│   ├── routes_users.py       # User management
│   ├── routes_video.py       # Video management
│   ├── routes_albums.py      # Album management
│   └── settings/             # Settings route modules
│       ├── __init__.py       # Settings package initialization
│       ├── account.py        # Account management routes
│       ├── api.py            # API endpoints for settings
│       ├── brand.py          # Brand identity management
│       ├── common_imports.py # Settings-specific imports
│       ├── contact.py        # Contact details management
│       ├── content.py        # Content management routes
│       ├── dashboard.py      # Dashboard routes
│       ├── media.py          # Media management routes
│       ├── performance.py    # Performance optimization routes
│       ├── policies.py       # Legal and policy pages
│       └── seo.py            # SEO management routes
│
├── optimizations/             # Performance optimization package
│   ├── __init__.py           # Package initialization and exports
│   ├── asset_optimization.py # Asset optimization and compression
│   ├── cache_config.py       # Redis caching configuration
│   ├── database_optimization.py # Database optimization
│   ├── frontend_optimization.py # Frontend optimization
│   ├── performance_monitoring.py # Performance monitoring
│   ├── query_caching.py      # Query caching strategies
│   ├── redis-performance.conf # Redis performance configuration
│   ├── setup_redis.sh        # Redis installation script
│   ├── ssr_optimization.py   # Server-side rendering optimization
│   └── README.md             # Package documentation
│
├── static/                    # Static assets
│   ├── css/                  # Stylesheets
│   │   ├── admin_base_css.css
│   │   ├── base_css.css
│   │   └── fix-simplemde-toolbar.css
│   ├── js/                   # JavaScript modules
│   │   ├── about.js          # About page functionality
│   │   ├── account-crud.js   # Account management
│   │   ├── ads-injection.js  # Advertisement system
│   │   ├── albums-management.js # Album management interface
│   │   ├── analytics-dashboard.js # Analytics dashboard
│   │   ├── asset-optimization-dashboard.js # Asset optimization
│   │   ├── brand-management.js # Brand identity management
│   │   ├── categories-management.js # Category management
│   │   ├── contact-details-management.js # Contact management
│   │   ├── extra-index.js    # Additional index functionality
│   │   ├── featured-image-modal.js # Image modal system
│   │   ├── footer-mode.js    # Footer functionality
│   │   ├── for-index.js      # Index page enhancements
│   │   ├── gallery.js        # Gallery functionality
│   │   ├── image-crud.js     # Image management
│   │   ├── images-management.js # Images management interface
│   │   ├── index.js          # Main index functionality
│   │   ├── lazy-loading.js   # Lazy loading implementation
│   │   ├── lazyload.js       # Legacy lazy loading
│   │   ├── login.js          # Login functionality
│   │   ├── login-register.js # Login/register forms
│   │   ├── mobile-toggler.js # Mobile navigation
│   │   ├── navigation-management.js # Navigation management
│   │   ├── news-create.js    # News creation interface
│   │   ├── news-management.js # News management interface
│   │   ├── pedomanhak-management.js # Legal guidelines
│   │   ├── performance-dashboard.js # Performance monitoring
│   │   ├── policy-management.js # Policy management
│   │   ├── premium.js        # Premium content system
│   │   ├── reader.js         # Article reader
│   │   ├── search-toggle.js  # Search functionality
│   │   ├── search-tool.js    # Advanced search
│   │   ├── seo-management.js # SEO management interface
│   │   ├── settings-management.js # Settings management
│   │   ├── share.js          # Social sharing
│   │   ├── sidebar-toggle.js # Sidebar navigation
│   │   ├── slick-init.js     # Slick slider initialization
│   │   ├── social-media-management.js # Social media management
│   │   ├── ssr-optimization-dashboard.js # SSR optimization
│   │   ├── tags-and-categories.js # Tag management
│   │   ├── tailwind-config.js # Tailwind configuration
│   │   ├── team-members-management.js # Team management
│   │   ├── theme-switcher.js # Theme switching
│   │   ├── toast.js          # Toast notifications
│   │   ├── users-management.js # User management interface
│   │   ├── videos.js         # Video functionality
│   │   ├── visimisi-management.js # Vision/mission management
│   │   └── youtube-management.js # YouTube management
│   ├── pic/                  # Brand assets
│   │   ├── favicon.png
│   │   ├── logo.png
│   │   ├── logo_footer.png
│   │   └── placeholder.png
│   └── uploads/              # User-uploaded content
│
├── templates/                 # Jinja2 templates
│   ├── admin_base.html       # Admin layout template
│   ├── base.html             # Base template
│   ├── error.html            # Error pages
│   ├── footer.html           # Footer template
│   ├── pagination.html       # Pagination component
│   ├── public/               # Public-facing templates
│   │   ├── about.html        # About page
│   │   ├── articles.html     # Articles listing
│   │   ├── gallery.html      # Gallery page
│   │   ├── hypes.html        # Hypes/trending content
│   │   ├── index.html        # Homepage
│   │   ├── login.html        # Login page
│   │   ├── news.html         # News listing
│   │   ├── premium.html      # Premium content page
│   │   ├── reader.html       # Article reader
│   │   ├── utama.html        # Main content page
│   │   └── videos.html       # Videos page
│   └── settings/             # Admin settings templates
│       ├── account_management.html # Account management
│       ├── albums_management.html # Album management
│       ├── analytics_dashboard.html # Analytics dashboard
│       ├── asset_optimization_dashboard.html # Asset optimization
│       ├── brand_management.html # Brand management
│       ├── categories_management.html # Category management
│       ├── contact_details_management.html # Contact management
│       ├── create_news_management.html # News creation
│       ├── images_management.html # Image management
│       ├── manage_news_management.html # News management
│       ├── navigation_management.html # Navigation management
│       ├── pedomanhak_management.html # Legal guidelines
│       ├── performance_dashboard.html # Performance monitoring
│       ├── policy_management.html # Policy management
│       ├── seo_management.html # SEO management
│       ├── settings_management.html # Settings management
│       ├── social_media_management.html # Social media
│       ├── ssr_optimization_dashboard.html # SSR optimization
│       ├── team_members_management.html # Team management
│       ├── users_management.html # User management
│       ├── visimisi_management.html # Vision/mission
│       └── youtube_management.html # YouTube management
│
├── migrations/               # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── helper/                   # Data seeding and utility scripts
│   ├── add_categories.py
│   ├── add_fake_images.py
│   ├── add_fake_news.py
│   ├── add_test_albums.py
│   ├── add_videos.py
│   ├── generate_user.py
│   ├── init_footer_data.py
│   ├── requirements-helper.txt
│   ├── set_image_visibility.py
│   └── source_images/
│
├── docs/                     # Documentation
│   ├── TODO.md               # Development roadmap
│   ├── api.md                # API documentation
│   ├── admin_ui.md           # Admin UI documentation
│   ├── ADVANCED_OPTIMIZATIONS.md # Advanced optimization guide
│   ├── FINAL_IMPLEMENTATION_SUMMARY.md # Implementation summary
│   ├── IMPLEMENTATION_SUMMARY.md # Development summary
│   ├── OPTIMIZATION_REORGANIZATION.md # Optimization structure
│   ├── PERFORMANCE_OPTIMIZATION.md # Performance guide
│   ├── PERFORMANCE_QUICK_START.md # Quick start guide
│   ├── PREMIUM_SYSTEM_IMPLEMENTATION.md # Premium system guide
│   ├── SUBSCRIPTION_SYSTEM_STATUS.md # Subscription status
│   └── SITEMAP_DOCUMENTATION.md # Sitemap documentation
│
├── instance/                 # Instance-specific files
└── .env                      # Environment variables
```

## 📚 Documentation

### Core Documentation
- **[API Documentation](docs/api.md)** - Complete API reference with endpoints and examples
- **[Admin UI Guide](docs/admin_ui.md)** - Comprehensive admin interface documentation
- **[Sitemap Documentation](docs/SITEMAP_DOCUMENTATION.md)** - Complete sitemap system guide

### Performance & Optimization
- **[Performance Optimization Guide](docs/PERFORMANCE_OPTIMIZATION.md)** - Comprehensive performance optimization
- **[Performance Quick Start](docs/PERFORMANCE_QUICK_START.md)** - Quick setup for performance features
- **[Advanced Optimizations](docs/ADVANCED_OPTIMIZATIONS.md)** - Advanced optimization techniques
- **[Optimization Reorganization](docs/OPTIMIZATION_REORGANIZATION.md)** - Optimization system structure

### System Implementation
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Current system implementation status
- **[Final Implementation Summary](docs/FINAL_IMPLEMENTATION_SUMMARY.md)** - Complete implementation overview
- **[Premium System Implementation](docs/PREMIUM_SYSTEM_IMPLEMENTATION.md)** - Premium content system guide
- **[Subscription System Status](docs/SUBSCRIPTION_SYSTEM_STATUS.md)** - Subscription feature status

### Development
- **[Development Roadmap](docs/TODO.md)** - Current development status and future plans

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URI=sqlite:///lilyopencms.db

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
UPLOAD_FOLDER=static/uploads

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# YouTube API (optional)
YOUTUBE_API_KEY=your-youtube-api-key

# External Services (optional)
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX-X

# Performance Optimization (optional)
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## 🚀 Performance Optimizations

LilyOpenCMS includes comprehensive performance optimizations organized in the `optimizations/` package:

### Quick Setup
```bash
# Install Redis and configure performance optimizations
chmod +x optimizations/setup_redis.sh
./optimizations/setup_redis.sh

# Access performance dashboard
# Visit: http://localhost:5000/admin/performance
```

### Key Features
- **Redis Caching**: Fast data retrieval with intelligent cache invalidation
- **Database Optimization**: Connection pooling, query optimization, automatic indexing
- **Frontend Optimization**: Lazy loading, progressive images, asset optimization
- **Performance Monitoring**: Real-time metrics, slow query detection, cache management

### Documentation
- [Performance Optimization Guide](docs/PERFORMANCE_OPTIMIZATION.md)
- [Quick Start Guide](docs/PERFORMANCE_QUICK_START.md)
- [Advanced Optimizations](docs/ADVANCED_OPTIMIZATIONS.md)
- [Optimizations Package README](optimizations/README.md)

## 🚀 API Endpoints

### Content Management
- `GET /api/news` - List news articles with filtering
- `POST /api/news` - Create new article
- `PUT /api/news/<id>` - Update article
- `DELETE /api/news/<id>` - Delete article
- `PATCH /api/news/<id>/visibility` - Toggle visibility
- `PATCH /api/news/<id>/archive` - Archive article
- `PATCH /api/news/<id>/unarchive` - Unarchive article
- `POST /api/news/<id>/duplicate` - Duplicate article
- `GET /api/albums` - List albums with filtering
- `POST /api/albums` - Create new album
- `PUT /api/albums/<id>` - Update album
- `DELETE /api/albums/<id>` - Delete album
- `PATCH /api/albums/<id>/visibility` - Toggle album visibility
- `PATCH /api/albums/<id>/archive` - Archive album
- `PATCH /api/albums/<id>/unarchive` - Unarchive album
- `POST /api/albums/<id>/chapters` - Add chapter to album
- `DELETE /api/albums/<id>/chapters/<chapter_id>` - Remove chapter from album

### Media Management
- `GET /api/images` - List images with filtering
- `POST /api/images` - Upload image
- `PUT /api/images/<id>` - Update image
- `DELETE /api/images/<id>` - Delete image
- `PATCH /api/images/<id>/visibility` - Toggle image visibility
- `GET /api/youtube_videos` - List YouTube videos
- `POST /api/youtube_videos` - Add YouTube video
- `PUT /api/youtube_videos/<id>` - Update video
- `DELETE /api/youtube_videos/<id>` - Delete video

### User Management
- `GET /api/users` - List users with filtering
- `POST /api/users` - Create user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user
- `PATCH /api/users/<id>/verify` - Toggle user verification
- `PATCH /api/users/<id>/status` - Toggle user status
- `POST /api/users/<id>/suspend` - Suspend user
- `POST /api/users/<id>/unsuspend` - Unsuspend user
- `GET /api/registrations/pending` - Get pending registrations
- `POST /api/registrations/<id>/approve` - Approve registration
- `POST /api/registrations/<id>/reject` - Reject registration

### Navigation Management
- `GET /api/navigation-links` - List navigation links
- `POST /api/navigation-links` - Create navigation link
- `PUT /api/navigation-links/<id>` - Update navigation link
- `DELETE /api/navigation-links/<id>` - Delete navigation link
- `POST /api/navigation-links/bulk-update` - Bulk update navigation links

### SEO & Analytics
- `GET /sitemap.xml` - Main sitemap
- `GET /sitemap-news.xml` - News-specific sitemap
- `GET /sitemap-index.xml` - Sitemap index
- `GET /robots.txt` - Search engine directives
- `GET /api/analytics/visitors` - Visitor statistics
- `GET /api/analytics/content` - Content analytics
- `GET /api/analytics/activity` - Activity logs
- `GET /api/analytics/performance` - Performance metrics

### Premium & Subscription
- `GET /api/subscriptions/plans` - Get subscription plans
- `POST /api/subscriptions/create` - Create subscription
- `POST /api/subscriptions/cancel` - Cancel subscription
- `GET /api/subscriptions/status` - Get subscription status
- `POST /api/subscriptions/update-ad-preferences` - Update ad preferences
- `GET /api/subscriptions/check-premium-access` - Check premium access

## 🔐 Authentication & Authorization

### User Roles
- **SUPERUSER**: Full system access with all permissions
- **ADMIN**: Content and user management with limited system access
- **GENERAL**: Basic content creation and personal management

### Permission System
- **Granular Permissions**: Matrix-based access control per feature
- **Role-based Access**: Automatic permission assignment based on roles
- **Activity Logging**: Comprehensive audit trails for all actions
- **Session Management**: Secure session handling with auto-logout

## 📊 SEO Features

### Sitemap Generation
- **Main Sitemap**: All content types with proper priorities
- **News Sitemap**: News-specific optimization with publication dates
- **Sitemap Index**: For large sites with multiple sitemaps
- **SEO Integration**: Uses meta_robots, seo_slug, priorities, and changefreq

### SEO Management
- **Meta Tags**: Description, keywords, author, language, robots
- **Open Graph**: Social media optimization for Facebook, LinkedIn
- **Twitter Cards**: Twitter-specific optimization
- **Schema Markup**: JSON-LD structured data for search engines
- **SEO Scoring**: Automated SEO analysis (0-100 scale)
- **Canonical URLs**: Prevent duplicate content issues
- **URL Optimization**: SEO-friendly slugs and redirects

## 🎨 UI/UX Features

### Design System
- **Tailwind CSS**: Utility-first styling with custom configuration
- **Responsive Design**: Mobile-first approach with breakpoint optimization
- **Dark Mode**: Theme switching capability with persistent preferences
- **Toast Notifications**: User feedback system with multiple types
- **Loading States**: Comprehensive loading indicators and skeleton screens

### Components
- **Dynamic Sidebar**: Role-based navigation with collapsible sections
- **Pagination**: Efficient content browsing with configurable page sizes
- **Search & Filter**: Advanced content discovery with multiple filters
- **Bulk Operations**: Efficient content management with batch processing
- **Modal System**: Reusable modal components for forms and confirmations
- **Data Tables**: Sortable, filterable tables with bulk actions

## 🗄️ Database Models

### Core Models
- **User**: Authentication, profiles, roles, permissions, activity tracking
- **News**: Articles with SEO, scheduling, archiving, related content
- **Album**: Album management with chapters, completion status, hiatus tracking
- **AlbumChapter**: Chapter relationships between albums and news articles
- **Category**: Content organization with hierarchical structure
- **Image**: Media management with optimization, usage tracking
- **YouTubeVideo**: Video content with metadata and embedding
- **TeamMember**: Team management with roles and contact information

### SEO & Brand Models
- **BrandIdentity**: Brand assets, colors, typography, guidelines
- **SocialMedia**: Social media links and platform management
- **ContactDetail**: Contact information and location data
- **NavigationLink**: Navigation menu management with internal/external links

### Legal & Policy Models
- **PrivacyPolicy**: Privacy policy content and versioning
- **MediaGuideline**: Media guidelines and usage policies
- **VisiMisi**: Vision and mission statements
- **Penyangkalan**: Disclaimer and legal disclaimers
- **PedomanHak**: Rights and guidelines documentation

### System Models
- **UserRole**: Role definitions and permissions
- **Permission**: Granular permission system
- **CustomRole**: Custom role creation and management
- **UserActivity**: Activity logging and audit trails
- **ShareLog**: Social sharing tracking and analytics

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production with Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 main:app
```

### Production with Passenger
```bash
# Configure passenger_wsgi.py
passenger start
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
python -m pytest tests/
```

### Test Coverage
```bash
python -m pytest --cov=app tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guide
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) folder for comprehensive guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

## 🏆 Acknowledgments

- Flask community for the excellent web framework
- Tailwind CSS for the utility-first CSS framework
- All contributors who have helped improve LilyOpenCMS

---

**LilyOpenCMS** - Modern content management for the digital age. 