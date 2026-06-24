"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from routes import main_blueprint
from .common_imports import *
from optimizations import cache_with_args, CACHE_TIMEOUTS
from optimizations import optimize_news_query, optimize_image_query, monitor_ssr_render
from optimizations.cache_config import safe_cache_get, safe_cache_set
from sqlalchemy import text
import time


def _feature_enabled(feature):
    """Check if a BrandIdentity feature toggle is enabled."""
    from models import BrandIdentity
    try:
        brand = BrandIdentity.query.first()
        if brand is None:
            return True
        return getattr(brand, feature, True)
    except Exception:
        return True

# Context processor to make navigation links and brand info available to all templates
@main_blueprint.context_processor
def inject_navigation_links():
    """Inject navigation links and brand info into all templates."""
    try:
        navbar_links = NavigationLink.query.filter_by(
            location='navbar', 
            is_active=True
        ).order_by(NavigationLink.order).all()
        
        footer_links = NavigationLink.query.filter_by(
            location='footer', 
            is_active=True
        ).order_by(NavigationLink.order).all()
        
        # Get brand identity info
        from models import BrandIdentity
        brand_info = BrandIdentity.query.first()
        if not brand_info:
            brand_info = BrandIdentity()
            db.session.add(brand_info)
            db.session.commit()
        
        return {
            'navbar_links': navbar_links,
            'footer_links': footer_links,
            'brand_info': brand_info
        }
    except Exception as e:
        # If there's an error (e.g., table doesn't exist yet), return empty lists
        print(f"Warning: Could not load navigation links or brand info: {e}")
        return {
            'navbar_links': [],
            'footer_links': [],
            'brand_info': None
        }

@main_blueprint.route("/")
@main_blueprint.route("/beranda")
def home():
    # Get main featured news with optimized query
    main_news_query = (
        News.query.filter_by(is_visible=True, is_main_news=True)
        .order_by(News.date.desc())
        .limit(5)
    )
    main_news = optimize_news_query(main_news_query).all()
    
    # Get latest articles (is_news=False, articles)
    latest_articles_query = (
        News.query.filter_by(is_visible=True, is_news=False)
        .order_by(News.date.desc())
        .limit(5)
    )
    latest_articles = optimize_news_query(latest_articles_query).all()
    
    # Get latest news (is_news=True, news)
    latest_news_query = (
        News.query.filter_by(is_visible=True, is_news=True)
        .order_by(News.date.desc())
        .limit(5)
    )
    latest_news = optimize_news_query(latest_news_query).all()
    
    # Get popular news
    popular_news_query = (
        News.query.filter_by(is_visible=True)
        .order_by(News.read_count.desc())
        .limit(7)
    )
    popular_news = optimize_news_query(popular_news_query).all()
    
    # Get latest YouTube videos
    latest_videos = (
        YouTubeVideo.query.filter_by(is_visible=True)
        .order_by(YouTubeVideo.created_at.desc())
        .limit(4)  # Fetching 4 videos to display in 4 columns
        .all()
    )

    # ---  QUERY for Latest Images ---
    latest_images_query = (
        Image.query.filter_by(is_visible=True)
        .order_by(Image.created_at.desc())
        .limit(5)  # Fetch the latest 5 images
    )
    latest_images = optimize_image_query(latest_images_query).all()

    # SSR monitoring
    print("DEBUG: Starting SSR monitoring for home route")
    start_time = time.time()
    try:
        result = render_template(
            "public/index.html",
            main_news=main_news,
            latest_articles=latest_articles,
            latest_news=latest_news,
            popular_news=popular_news,
            latest_videos=latest_videos,
            latest_images=latest_images,
        )
        render_time = time.time() - start_time
        print(f"DEBUG: Home route rendered in {render_time:.3f}s")
        
        # Record SSR render
        from optimizations.ssr_optimization import get_ssr_optimizer
        optimizer = get_ssr_optimizer()
        optimizer.record_render("home", render_time, cached=False)
        print("DEBUG: SSR render recorded for home route")
        
        return result
    except Exception as e:
        render_time = time.time() - start_time
        print(f"SSR render failed for home after {render_time:.3f}s: {e}")
        raise


@main_blueprint.route("/videos")
def videos():
    if not _feature_enabled('enable_videos'):
        abort(404)
    page = request.args.get("page", 1, type=int)
    per_page = 9
    query = request.args.get("q", "")

    video_query = YouTubeVideo.query.filter_by(is_visible=True)
    if query:
        video_query = video_query.filter(YouTubeVideo.youtube_id.ilike(f"%{query}%"))

    videos_paginated = video_query.order_by(YouTubeVideo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Fetch titles using oEmbed with caching
    for video in videos_paginated.items:
        try:
            # Cache oEmbed requests
            cache_key = f"oembed_{video.youtube_id}"
            cached_title = safe_cache_get(cache_key)
            
            if cached_title:
                video.title = cached_title
            else:
                response = requests.get(
                    f"https://www.youtube.com/oembed?url={video.link}&format=json"
                )
                data = response.json()
                video.title = data.get("title", video.youtube_id)
                # Cache for 1 hour
                safe_cache_set(cache_key, video.title, timeout=3600)
        except Exception as e:
            print(f"Error fetching oEmbed for {video.youtube_id}: {e}")
            video.title = video.youtube_id  # Fallback

    return render_template("public/videos.html", videos=videos_paginated, query=query)


@main_blueprint.route("/news")
@cache_with_args(timeout=CACHE_TIMEOUTS['news_list'], key_prefix='news_list')
@monitor_ssr_render("news_list")
def news():
    page = request.args.get("page", 1, type=int)
    per_page = 9
    # Fetch all visible news articles (is_news=True)
    news_list = (
        News.query.filter_by(is_news=True, is_visible=True)
        .order_by(News.date.desc())
        .paginate(page=page, per_page=per_page)
    )

    # Fetch all categories and tags
    categories = Category.query.all()
    tags = get_tags().json  # Assuming get_tags() returns a JSON response

    return render_template(
        "public/news.html",
        news=news_list,
        categories=categories,
        tags=tags,
        query=None,
        category=None,
        tag=None,
    )


@main_blueprint.route("/hypes")
@monitor_ssr_render("hypes")
def hypes():
    page = request.args.get("page", 1, type=int)
    per_page = 9

    # Query news with share count
    hypes_query = (
        db.session.query(
            News,
            (
                ShareLog.whatsapp_count
                + ShareLog.facebook_count
                + ShareLog.twitter_count
                + ShareLog.instagram_count
                + ShareLog.bluesky_count
                + ShareLog.clipboard_count
            ).label("total_share"),
        )
        .outerjoin(ShareLog, News.id == ShareLog.news_id)
        .filter(News.is_visible == True, (News.read_count > 0))
        .order_by(db.desc("total_share"), db.desc(News.read_count))
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    # Convert tuples (News, total_share) into list with dicts
    hypes_list = []
    for news, total_share in hypes_query.items:
        news.total_share = total_share if total_share is not None else 0
        hypes_list.append(news)

    # Replace the items with our processed list
    hypes_query.items = hypes_list

    # Fetch categories and tags
    categories = Category.query.all()
    tags = get_tags().json

    return render_template(
        "public/hypes.html",
        hypes=hypes_query,
        categories=categories,
        tags=tags,
        query=None,
        category=None,
        tag=None,
    )


@main_blueprint.route("/articles")
@monitor_ssr_render("articles")
def articles():
    page = request.args.get("page", 1, type=int)
    per_page = 9
    
    # Fetch all visible articles (is_news=False)
    articles_list = (
        News.query.filter_by(is_news=False, is_visible=True)
        .order_by(News.date.desc())
        .paginate(page=page, per_page=per_page)
    )

    # Fetch all categories and tags
    categories = Category.query.all()
    tags = get_tags().json

    return render_template(
        "public/articles.html",
        articles=articles_list,
        categories=categories,
        tags=tags,
        query=None,
        category=None,
        tag=None,
    )


@main_blueprint.route("/utama")
def utama():
    page = request.args.get("page", 1, type=int)
    per_page = 9
    # Get all featured content (both articles and news)
    featured_news = (
        News.query.filter_by(is_visible=True)
        .order_by(News.date.desc())
        .paginate(page=page, per_page=per_page)
    )

    # Fetch all categories and tags
    categories = Category.query.all()
    tags = get_tags().json

    return render_template(
        "public/utama.html", news=featured_news, categories=categories, tags=tags
    )


@main_blueprint.route("/gallery")
@monitor_ssr_render("gallery")
def gallery():
    """Displays a paginated gallery of visible images."""
    if not _feature_enabled('enable_gallery'):
        abort(404)
    page = request.args.get("page", 1, type=int)
    per_page = 15

    images_query = Image.query.filter_by(is_visible=True).order_by(
        Image.created_at.desc()
    )
    images_paginated = images_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Fetch categories and tags for the sidebar/context (if your base template needs them)
    # categories = Category.query.all()
    # tags_response = get_tags() # Assuming get_tags returns a Response object
    # tags = tags_response.json if tags_response.status_code == 200 else []
    # If you use a context processor for categories/tags, you might not need them here.

    return render_template(
        "public/gallery.html",
        images=images_paginated,
        # categories=categories, # Pass if needed
        # tags=tags              # Pass if needed
    )


# ----------------------
# 📰 info Routes
# ----------------------


@main_blueprint.route("/about")
def about():
    if not _feature_enabled('enable_about'):
        abort(404)
    # Fetch active team members by group
    leadership = (
        TeamMember.query.filter_by(group="leadership", is_active=True)
        .order_by(TeamMember.member_order)
        .all()
    )
    editorial = (
        TeamMember.query.filter_by(group="editorial", is_active=True)
        .order_by(TeamMember.member_order)
        .all()
    )
    news_team = (
        TeamMember.query.filter_by(group="news", is_active=True)
        .order_by(TeamMember.member_order)
        .all()
    )
    video_team = (
        TeamMember.query.filter_by(group="video", is_active=True)
        .order_by(TeamMember.member_order)
        .all()
    )
    sales_team = (
        TeamMember.query.filter_by(group="sales", is_active=True)
        .order_by(TeamMember.member_order)
        .all()
    )
    # Fetch active contact details for Contact section
    contact_details = (
        ContactDetail.query.filter_by(is_active=True)
        .order_by(ContactDetail.section_order)
        .all()
    )
    return render_template(
        "public/about.html",
        leadership=leadership,
        editorial=editorial,
        news_team=news_team,
        video_team=video_team,
        sales_team=sales_team,
        contact_details=contact_details,
    )


@main_blueprint.route("/search", methods=["GET"])
def search():
    """Search for news articles based on query, category, or tags."""
    query = request.args.get("q", "").strip()
    selected_category_name = request.args.get("category", "").strip()
    selected_tag_name = request.args.get("tag", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 6

    # Base query
    news_query = News.query.filter_by(is_visible=True)

    # Apply filters (Keep this logic)
    if query:
        # Search in title or content (consider adding writer/author if needed)
        news_query = news_query.filter(
            News.title.ilike(f"%{query}%") | News.content.ilike(f"%{query}%")
        )

    if selected_category_name:
        # Filter by category name using relationship join
        news_query = news_query.filter(News.category.has(name=selected_category_name))

    if selected_tag_name:
        # Filter by tag name
        news_query = news_query.filter(News.tagar.ilike(f"%{selected_tag_name}%"))

    # Paginate the results
    news_list = news_query.order_by(News.date.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,  # Added error_out=False
    )

    # !! Remove API check if not needed for this specific frontend task !!
    # if request.path.startswith("/api"):
    #     return jsonify([news.to_dict() for news in news_list.items])
    # else:

    # Render the template, passing the pagination object AND
    # the specific filters applied in *this* request for pagination links.
    return render_template(
        "public/news.html",  # Or your specific search results template name
        news=news_list,  # The pagination object
        query=query,  # For pagination links
        category=selected_category_name,  # For pagination links
        tag=selected_tag_name,  # For pagination links
        # No need to pass categories/tags list here anymore (handled by context processor)
    )

# ----------------------
# 📰 News Routes
# ----------------------


@main_blueprint.route("/news/<int:news_id>/<path:news_title>")
@monitor_ssr_render("news_detail")
def news_detail(news_id, news_title):
    news_item = News.query.get_or_404(news_id)

    # Check visibility *before* doing anything else
    if not news_item.is_visible:
        current_app.logger.warning(
            f"Attempt to access non-visible news item ID: {news_id}"
        )
        abort(404)

    # --- Convert Markdown to HTML ---
    # Use 'extra' for features like footnotes, abbr, def_list, etc.
    # Also include fenced_code and tables explicitly if not covered by 'extra' in your version
    # Add 'sane_lists' for potentially better list handling.
    try:
        html_content = markdown.markdown(
            news_item.content or "",  # Handle potential None content
            extensions=["fenced_code", "tables", "extra", "sane_lists"],
        )
        # IMPORTANT: Do NOT modify news_item.content here. Pass the generated HTML
        # separately or add it as a temporary attribute if needed elsewhere in template.
        # Let's pass it separately for clarity.
    except Exception as e:
        current_app.logger.error(
            f"Markdown conversion failed for news ID {news_id}: {e}"
        )
        # Decide how to handle: show raw content, show error, or abort?
        # For now, let's pass empty string, but logging the error is crucial.
        html_content = (
            "<p><em>Error rendering content.</em></p>"
        )  # Provide fallback HTML

    # --- Increment Reads ---
    try:
        news_item.increment_reads()
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback if commit fails
        current_app.logger.error(
            f"Failed to increment read count for news ID {news_id}: {e}"
        )
        # Continue rendering the page even if read count fails

    # --- Fetch Related News ---
    # Fetch related news (same category, excluding the current news)
    related_news_query = (
        News.query.filter(
            News.category_id == news_item.category_id,  # Assuming category_id is the FK
            News.id != news_id,
            News.is_visible == True,
        )
        .order_by(News.date.desc())
        .limit(6)
    )  # Order by date makes sense
    related_news = related_news_query.all()

    # --- Fetch Popular News (if needed) ---
    needed_more = 6 - len(related_news)
    if needed_more > 0:
        # Calculate popularity score (share count + read count)
        # Ensure NULL counts are treated as 0 using coalesce or func.coalesce
        popularity_score = (
            func.coalesce(ShareLog.whatsapp_count, 0)
            + func.coalesce(ShareLog.facebook_count, 0)
            + func.coalesce(ShareLog.twitter_count, 0)
            + func.coalesce(ShareLog.instagram_count, 0)
            + func.coalesce(ShareLog.bluesky_count, 0)
            + func.coalesce(ShareLog.clipboard_count, 0)
            + func.coalesce(News.read_count, 0)  # Also coalesce read_count
        ).label("popularity_score")

        # Exclude IDs already in related_news
        exclude_ids = [news_id] + [r.id for r in related_news]

        popular_news_items = (
            db.session.query(News, popularity_score)
            .outerjoin(ShareLog, News.id == ShareLog.news_id)
            .filter(
                News.id.notin_(
                    exclude_ids
                ),  # Exclude current and already selected related
                News.is_visible == True,
            )
            .order_by(popularity_score.desc())
            .limit(needed_more)
            .all()
        )

        # Extract just the News objects
        popular_news = [item[0] for item in popular_news_items]
        related_news.extend(popular_news)

    # --- Render Template ---
    # Pass the original news object AND the generated HTML content separately
    return render_template(
        "public/reader.html",
        news=news_item,
        html_content=html_content,
        related_news=related_news,
    )

@main_blueprint.route("/news/<int:news_id>")
def news_detail_legacy(news_id):
    """
    Legacy route that redirects old URLs to new SEO-friendly URLs
    """
    # Fetch the news item to get its title
    news_item = News.query.get_or_404(news_id)
    
    # Check visibility before redirecting
    if not news_item.is_visible:
        current_app.logger.warning(
            f"Attempt to access non-visible news item ID: {news_id}"
        )
        abort(404)
    
    # Define the safe_title function directly here (same as in your context processor)
    def safe_title(title):
        import re
        filtered_title = re.sub(r'\s+', '_', title)
        filtered_title = re.sub(r'[\W]', '', filtered_title)
        max_length = 50
        if len(filtered_title) > max_length:
            filtered_title = filtered_title[:max_length]
        return filtered_title
    
    # Generate the safe title for the URL
    safe_title_result = safe_title(news_item.title)
    
    # Redirect to the new URL pattern
    return redirect(url_for('main.news_detail', 
                          news_id=news_id, 
                          news_title=safe_title_result), 
                  code=301)  # 301 is permanent redirect, good for SEO


@main_blueprint.route("/api/categories", methods=["GET"])
def get_categories():
    """Fetch all categories."""
    categories = Category.query.all()
    return jsonify(
        [{"id": category.id, "name": category.name} for category in categories]
    )


@main_blueprint.route("/api/tags", methods=["GET"])
def get_tags():
    """Fetch all unique tags from the news articles."""
    tags = db.session.query(News.tagar).distinct().all()
    # Flatten the list of tuples and split comma-separated tags
    tag_list = []
    for tag in tags:
        if tag[0]:
            tag_list.extend(tag[0].split(","))
    # Remove duplicates and empty strings
    unique_tags = list(set(tag.strip() for tag in tag_list if tag.strip()))
    return jsonify(unique_tags)


@main_blueprint.route("/premium")
def premium():
    """Premium subscription page."""
    if not _feature_enabled('enable_premium'):
        abort(404)
    return render_template("public/premium.html")


@main_blueprint.route("/test-ssr")
@monitor_ssr_render("test_ssr")
def test_ssr():
    return "SSR Test"


@main_blueprint.route("/settings/navigation")
@login_required
def navigation_management():
    """Navigation links management page."""
    # Define available internal links for the dropdown
    internal_links = [
        # Main pages
        {"name": "Beranda", "url": "/"},
        {"name": "Beranda (Alternatif)", "url": "/beranda"},
        {"name": "Berita", "url": "/news"},
        {"name": "Artikel", "url": "/articles"},
        {"name": "Hypes", "url": "/hypes"},
        {"name": "Utama", "url": "/utama"},
        {"name": "Galeri", "url": "/gallery"},
        {"name": "Videos", "url": "/videos"},
        {"name": "Tentang Kami", "url": "/about"},
        {"name": "Premium", "url": "/premium"},
        {"name": "Pencarian", "url": "/search"},
        
        # Settings pages (admin only)
        {"name": "Dashboard Settings", "url": "/settings"},
        {"name": "Analytics", "url": "/settings/analytics"},
        {"name": "Manajemen Berita", "url": "/settings/manage_news"},
        {"name": "Buat Berita", "url": "/settings/create_news"},
        {"name": "Manajemen Kategori", "url": "/settings/categories"},
        {"name": "Manajemen Video", "url": "/settings/youtube"},
        {"name": "Manajemen Gambar", "url": "/settings/image"},
        {"name": "Manajemen Album", "url": "/settings/albums"},
        {"name": "Manajemen Pengguna", "url": "/settings/users"},
        {"name": "Manajemen Akun", "url": "/settings/account"},
        {"name": "Manajemen Navigasi", "url": "/settings/navigation"},
        
        # Brand & Content Management
        {"name": "Media Sosial", "url": "/settings/social-media"},
        {"name": "Brand Identity", "url": "/settings/brand-identity"},
        {"name": "Detail Kontak", "url": "/settings/contact-details"},
        {"name": "Anggota Tim", "url": "/settings/team-members"},
        
        # Policies & Legal
        {"name": "Kebijakan Privasi", "url": "/settings/privacy-policy"},
        {"name": "Pedoman Media", "url": "/settings/media-guidelines"},
        {"name": "Visi Misi", "url": "/settings/visi-misi"},
        {"name": "Pedoman Hak", "url": "/settings/pedomanhak"},
        {"name": "Penyangkalan", "url": "/settings/penyangkalan"},
        
        # SEO & Performance
        {"name": "Manajemen SEO", "url": "/settings/seo"},
        {"name": "Dashboard Performa", "url": "/settings/performance"},
        {"name": "Optimasi Asset", "url": "/settings/asset-optimization"},
        {"name": "Optimasi SSR", "url": "/settings/ssr-optimization"},
        
        # Performance dashboards
        {"name": "Dashboard Performa", "url": "/admin/performance"},
        {"name": "Dashboard Optimasi Asset", "url": "/admin/performance/asset-optimization"},
        {"name": "Dashboard Optimasi SSR", "url": "/admin/performance/ssr-optimization"},
    ]
    
    return render_template("settings/navigation_management.html", internal_links=internal_links)

# Navigation Links API Routes
@main_blueprint.route("/api/navigation-links", methods=["GET"])
@login_required
def get_navigation_links():
    """Get all navigation links."""
    try:
        links = NavigationLink.query.order_by(NavigationLink.location, NavigationLink.order).all()
        return jsonify([link.to_dict() for link in links])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/navigation-links", methods=["POST"])
@login_required
def create_navigation_link():
    """Create a new navigation link."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["name", "url", "location"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Field '{field}' is required"}), 400
        
        # Create new navigation link
        new_link = NavigationLink(
            name=data["name"],
            url=data["url"],
            location=data["location"],
            order=data.get("order", 0),
            is_active=data.get("is_active", True),
            is_external=data.get("is_external", False),
            user_id=current_user.id
        )
        
        db.session.add(new_link)
        db.session.commit()
        
        # Invalidate navigation cache
        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass
        
        return jsonify(new_link.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/navigation-links/<int:link_id>", methods=["PUT"])
@login_required
def update_navigation_link(link_id):
    """Update a navigation link."""
    try:
        link = NavigationLink.query.get_or_404(link_id)
        data = request.get_json()
        
        # Update fields
        if "name" in data:
            link.name = data["name"]
        if "url" in data:
            link.url = data["url"]
        if "location" in data:
            link.location = data["location"]
        if "order" in data:
            link.order = data["order"]
        if "is_active" in data:
            link.is_active = data["is_active"]
        if "is_external" in data:
            link.is_external = data["is_external"]
        
        link.user_id = current_user.id
        db.session.commit()
        
        # Invalidate navigation cache
        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass
        
        return jsonify(link.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/navigation-links/<int:link_id>", methods=["DELETE"])
@login_required
def delete_navigation_link(link_id):
    """Delete a navigation link."""
    try:
        link = NavigationLink.query.get_or_404(link_id)
        db.session.delete(link)
        db.session.commit()
        
        # Invalidate navigation cache
        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass
        
        return jsonify({"message": "Navigation link deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/navigation-links/bulk-update", methods=["POST"])
@login_required
def bulk_update_navigation_links():
    """Bulk update navigation links order and visibility."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        data = request.get_json()
        if not data or 'links' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        links_data = data['links']
        
        for link_data in links_data:
            link_id = link_data.get('id')
            if not link_id:
                continue
                
            link = NavigationLink.query.get(link_id)
            if link:
                link.order = link_data.get('order', link.order)
                link.is_active = link_data.get('is_active', link.is_active)
                link.updated_at = default_utcnow()

        db.session.commit()
        
        # Invalidate navigation cache
        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass
        
        return jsonify({"message": "Navigation links updated successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error bulk updating navigation links: {e}")
        return jsonify({"error": "Failed to update navigation links"}), 500


@main_blueprint.route("/api/navigation-links/bulk-status", methods=["PUT"])
@login_required
def bulk_update_navigation_status():
    """Bulk update navigation links status (activate/deactivate)."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        data = request.get_json()
        if not data or 'link_ids' not in data or 'is_active' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        link_ids = data['link_ids']
        is_active = data['is_active']

        updated_count = 0
        for link_id in link_ids:
            link = NavigationLink.query.get(link_id)
            if link:
                link.is_active = is_active
                link.updated_at = default_utcnow()
                updated_count += 1

        db.session.commit()

        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass

        return jsonify({
            "message": f"Successfully updated {updated_count} navigation links",
            "updated_count": updated_count
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error bulk updating navigation links status: {e}")
        return jsonify({"error": f"Failed to update navigation links: {str(e)}"}), 500


@main_blueprint.route("/api/navigation-links/bulk-delete", methods=["DELETE"])
@login_required
def bulk_delete_navigation_links():
    """Bulk delete navigation links."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        data = request.get_json()
        if not data or 'link_ids' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        link_ids = data['link_ids']
        deleted_count = 0

        for link_id in link_ids:
            link = NavigationLink.query.get(link_id)
            if link:
                db.session.delete(link)
                deleted_count += 1

        db.session.commit()

        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass

        return jsonify({
            "message": f"Successfully deleted {deleted_count} navigation links",
            "deleted_count": deleted_count
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error bulk deleting navigation links: {e}")
        return jsonify({"error": "Failed to delete navigation links"}), 500


@main_blueprint.route("/api/navigation-links/copy", methods=["POST"])
@login_required
def copy_navigation_links():
    """Copy navigation links from one location to another."""
    if not current_user.verified:
        return jsonify({"error": "Account not verified"}), 403

    try:
        data = request.get_json()
        if not data or 'from_location' not in data or 'to_location' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        from_location = data['from_location']
        to_location = data['to_location']
        overwrite = data.get('overwrite', False)

        source_links = NavigationLink.query.filter_by(location=from_location).order_by(NavigationLink.order).all()

        if not source_links:
            return jsonify({"error": f"No links found in {from_location}"}), 404

        if not overwrite:
            existing_links = NavigationLink.query.filter_by(location=to_location).count()
            if existing_links > 0:
                return jsonify({"error": f"Destination {to_location} already has links. Enable overwrite to continue."}), 409

        copied_count = 0
        max_order = 0

        if not overwrite:
            max_order_result = db.session.query(db.func.max(NavigationLink.order)).filter_by(location=to_location).scalar()
            max_order = max_order_result or 0

        if overwrite:
            NavigationLink.query.filter_by(location=to_location).delete()

        for link in source_links:
            new_link = NavigationLink(
                name=link.name,
                url=link.url,
                location=to_location,
                order=max_order + link.order + 1,
                is_active=link.is_active,
                is_external=link.is_external,
                user_id=current_user.id
            )
            db.session.add(new_link)
            copied_count += 1

        db.session.commit()

        try:
            from optimizations import invalidate_cache_pattern
            invalidate_cache_pattern("navigation*")
        except ImportError:
            pass

        return jsonify({
            "message": f"Successfully copied {copied_count} links from {from_location} to {to_location}",
            "copied_count": copied_count,
            "from_location": from_location,
            "to_location": to_location
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error copying navigation links: {e}")
        return jsonify({"error": "Failed to copy navigation links"}), 500





@main_blueprint.route("/settings/albums")
@login_required
def albums_management():
    """Album management page."""
    if not current_user.verified:
        return redirect(url_for('main.login'))
    
    return render_template("settings/albums_management.html")


@main_blueprint.route("/robots.txt")
def robots_txt():
    """Serve dynamically generated robots.txt file based on request host and environment."""
    import os

    flask_env = os.getenv("FLASK_ENV", "development").lower()

    try:
        result = db.session.execute(text('SELECT website_url FROM seo_injection_settings LIMIT 1'))
        row = result.fetchone()
        website_url = row[0] if row and row[0] else None
    except Exception:
        website_url = None

    if not website_url:
        website_url = request.url_root.rstrip('/')
    else:
        website_url = website_url.rstrip('/')

    if flask_env != "production":
        robots_content = f"""# ==================================================
# robots.txt (Dynamic - Non-Production Profile)
# ==================================================

User-agent: *
Allow: /

Disallow: /settings/
Disallow: /api/
Disallow: /admin/
Disallow: /login
Disallow: /register
Disallow: /logout

Allow: /news/
Allow: /videos/
Allow: /gallery/
Allow: /about/
Allow: /utama/
Allow: /hypes/
Allow: /premium/

Crawl-delay: 1

# ==================================================
# SITEMAPS
# ==================================================
Sitemap: {website_url}/sitemap.xml
Sitemap: {website_url}/sitemap-news.xml
Sitemap: {website_url}/sitemap-index.xml
"""
    else:
        robots_content = f"""# ==================================================
# robots.txt (Dynamic - Production Profile)
# ==================================================

User-agent: *
Allow: /

Allow: /api/
Allow: /api/v1/
Allow: /news/
Allow: /videos/
Allow: /gallery/
Allow: /about/
Allow: /utama/
Allow: /hypes/
Allow: /premium/
Allow: /assets/
Allow: /images/
Allow: /static/
Allow: /public/
Allow: /feeds/
Allow: /rss/
Allow: /news/rss/
Allow: /news/json/

Allow: /*.css$
Allow: /*.js$
Allow: /*.jpg$
Allow: /*.jpeg$
Allow: /*.png$
Allow: /*.svg$
Allow: /*.webp$
Allow: /*.mp4$
Allow: /*.webm$
Allow: /*.json$

Disallow: /settings/
Disallow: /admin/
Disallow: /login
Disallow: /register
Disallow: /logout
Disallow: /cgi-bin/
Disallow: /*?*

User-agent: Googlebot
Allow: /
Disallow: /admin/

User-agent: Googlebot-News
Allow: /news/
Allow: /hypes/
Allow: /premium/

User-agent: Googlebot-Video
Allow: /videos/
Allow: /news/
Disallow: /admin/

User-agent: AdsBot-Google
Allow: /
Disallow: /admin/

User-agent: Mediapartners-Google
Allow: /
Disallow: /admin/

User-agent: Bingbot
Allow: /
Disallow: /admin/

# ==================================================
# SITEMAPS
# ==================================================
Sitemap: {website_url}/sitemap.xml
Sitemap: {website_url}/sitemap-news.xml
Sitemap: {website_url}/sitemap-index.xml
"""
    return Response(robots_content, mimetype="text/plain")
