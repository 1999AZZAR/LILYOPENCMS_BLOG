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

def sanitize_filename(filename):
    """Replaces spaces and invalid characters with underscores."""
    # Replace spaces with underscores first
    filename = filename.replace(" ", "_")
    # Replace any character that is not alphanumeric, underscore, or dot with an underscore
    filename = re.sub(r'[^\w.]+', '_', filename)
    # Optional: Collapse multiple underscores into one
    filename = re.sub(r'_+', '_', filename)
    return filename

def save_file(file, name=None):
    """Securely saves an uploaded file with a short unique name."""
    if name:
        filename = secure_filename(name)
    else:
        filename = secure_filename(file.filename)

    # Sanitize the filename
    sanitize_filename(filename)

    # Use shorter unique id: 6-digit microsecond timestamp
    timestamp = datetime.now().strftime('%H%M%S%f')[:9] # Use microseconds for better uniqueness
    unique_filename = f"{timestamp}_{filename}"
    file_path = os.path.join("static/uploads", unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file.save(file_path)
    return unique_filename, file_path


def update_robots_txt():
    """Update robots.txt with correct website URL from SEO settings."""
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT website_url FROM seo_injection_settings LIMIT 1'))
        row = result.fetchone()
        website_url = row[0] if row and row[0] else "https://hystory.id"

        website_url = website_url.rstrip('/')

        robots_content = f"""User-agent: *
Allow: /

# Disallow admin and private areas
Disallow: /settings/
Disallow: /api/
Disallow: /admin/
Disallow: /login
Disallow: /register
Disallow: /logout

# Allow important public content
Allow: /news/
Allow: /videos/
Allow: /gallery/
Allow: /about/
Allow: /utama/
Allow: /hypes/
Allow: /premium/

# Crawl delay (optional - be respectful to server)
Crawl-delay: 1

# Sitemap locations
Sitemap: {website_url}/sitemap.xml
Sitemap: {website_url}/sitemap-news.xml
Sitemap: {website_url}/sitemap-index.xml
"""

        with open('robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots_content)

        current_app.logger.info(f"Updated robots.txt with website URL: {website_url}")
        return True

    except Exception as e:
        current_app.logger.error(f"Failed to update robots.txt: {e}")
        return False



def download_image(image_url):
    """Downloads an image from a URL, saves it locally with a short unique name, and returns filename & path."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
            )
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download image: {e}")

    # Derive safe base name
    parsed = urlparse(image_url)
    name = os.path.basename(parsed.path) or "DownImg"
    base_filename = secure_filename(name)

    # Sanitize the base filename
    sanitized_base_filename = sanitize_filename(base_filename)

    # Ensure extension exists
    if not os.path.splitext(sanitized_base_filename)[1]:
        ext = guess_extension(response.headers.get("Content-Type", "").split(";")[0])
        sanitized_base_filename += ext or ".jpg"

    # Short timestamp
    timestamp = datetime.now().strftime('%H%M%S%f')[:9] # Use microseconds
    unique_filename = f"{timestamp}_{base_filename}"

    file_path = os.path.join("static/uploads", unique_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(response.content)

    return unique_filename, file_path



def delete_existing_file(file_path):
    """Deletes an existing file from storage if it exists."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


def parse_iso8601_duration(duration):
    """Convert ISO8601 duration (e.g. PT1H2M3S) to seconds."""
    pattern = re.compile(
        r"^PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?$"
    )
    m = pattern.match(duration)
    if not m:
        return None
    p = m.groupdict()
    return (
        int(p.get("hours") or 0) * 3600
        + int(p.get("minutes") or 0) * 60
        + int(p.get("seconds") or 0)
    )

def process_single_image(file_path):
    """Standardizes an image to WebP (fixed width 1280px, preserve aspect ratio), creates 3 types of thumbnails, deletes original."""
    try:
        img = PILImage.open(file_path).convert("RGB")
        base_dir = os.path.dirname(file_path)
        base_name, _ = os.path.splitext(os.path.basename(file_path))
        webp_path = os.path.join(base_dir, f"{base_name}.webp")

        # 📏 Standard Width
        STANDARD_WIDTH = 1280

        # Resize keeping aspect ratio
        w_percent = STANDARD_WIDTH / float(img.size[0])
        new_height = int(float(img.size[1]) * float(w_percent))
        resized_img = img.resize((STANDARD_WIDTH, new_height), PILImage.Resampling.LANCZOS)

        # Save standardized WebP
        resized_img.save(webp_path, "WEBP", quality=85, method=6)

        # 📸 Create Thumbnails
        THUMB_SIZES = {
            "portrait": (400, 600),   # 2:3
            "square": (400, 400),     # 1:1
            "landscape": (600, 400),  # 3:2
        }

        for style, size in THUMB_SIZES.items():
            thumb = img.copy()
            thumb = ImageOps.fit(img, size, PILImage.Resampling.LANCZOS, centering=(0.5, 0.5))
            thumb_path = os.path.join(base_dir, f"{base_name}_thumb_{style}.webp")
            thumb.save(thumb_path, "WEBP", quality=75, method=6)

        # ✅ Delete the original file
        if not file_path.endswith(".webp"):
            os.remove(file_path)

        return "ok"

    except Exception as e:
        return f"Processing error: {str(e)}"


# Helper function (keep as before)
def add_url_to_sitemap(urlset, loc, lastmod=None, changefreq=None, priority=None):
    """Adds a <url> element to the <urlset> ElementTree object."""
    url_element = ET.SubElement(urlset, "url")
    ET.SubElement(url_element, "loc").text = loc

    if lastmod:
        if isinstance(lastmod, datetime):
            if lastmod.tzinfo is None:
                # Assume UTC if timezone info is missing from DB datetime
                lastmod = lastmod.replace(tzinfo=timezone.utc)
            # Format to YYYY-MM-DD (widely accepted by crawlers)
            formatted_lastmod = lastmod.strftime("%Y-%m-%d")
            ET.SubElement(url_element, "lastmod").text = formatted_lastmod
        elif isinstance(lastmod, str):  # Allow pre-formatted strings
            ET.SubElement(url_element, "lastmod").text = lastmod

    if changefreq:
        ET.SubElement(url_element, "changefreq").text = changefreq
    if priority:
        ET.SubElement(url_element, "priority").text = str(
            priority
        )  # Priority must be a string


def generate_news_sitemap():
    """Generates a news-specific sitemap for better SEO."""
    try:
        urlset = ET.Element(
            "urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        )

        # Get all visible news articles with SEO data
        news_items = (
            db.session.query(
                News.id, 
                News.updated_at, 
                News.seo_slug,
                News.meta_robots,
                News.is_news,
                News.is_premium,
                News.is_main_news,
                News.read_count,
                News.date,
                News.title,
                News.category_id
            )
            .filter(News.is_visible == True)
            .order_by(News.updated_at.desc())
            .all()
        )
        
        for news_data in news_items:
            news_id, updated_at, seo_slug, meta_robots, is_news, is_premium, is_main_news, read_count, date, title, category_id = news_data
            
            # Skip if explicitly marked as noindex
            if meta_robots and "noindex" in meta_robots.lower():
                continue
                
            try:
                # Use SEO slug if available, otherwise use ID
                if seo_slug:
                    loc = url_for("main.news_detail", news_id=news_id, news_title=seo_slug, _external=True)
                else:
                    loc = url_for("main.news_detail", news_id=news_id, _external=True)
                
                # Determine priority based on content importance
                if is_main_news:
                    priority = 0.9
                elif is_premium:
                    priority = 0.8
                elif read_count and read_count > 100:
                    priority = 0.8
                else:
                    priority = 0.7
                
                # Determine change frequency
                if is_main_news:
                    changefreq = "daily"
                elif is_premium:
                    changefreq = "weekly"
                else:
                    days_old = (datetime.now(timezone.utc) - date).days if date else 365
                    if days_old < 7:
                        changefreq = "daily"
                    elif days_old < 30:
                        changefreq = "weekly"
                    elif days_old < 90:
                        changefreq = "monthly"
                    else:
                        changefreq = "yearly"
                
                add_url_to_sitemap(
                    urlset, loc, lastmod=updated_at, changefreq=changefreq, priority=priority
                )
            except Exception as e:
                current_app.logger.warning(
                    f"News sitemap: Could not generate URL for news ID {news_id}: {e}"
                )

        sitemap_xml_string = ET.tostring(urlset, encoding="unicode", method="xml")
        final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + sitemap_xml_string

        return Response(final_xml, mimetype="application/xml")

    except Exception as err:
        current_app.logger.error(
            f"News sitemap generation failed: {err}", exc_info=True
        )
        return Response("Error generating news sitemap", status=500, mimetype="text/plain")


@main_blueprint.route("/sitemap-news.xml")
def sitemap_news():
    """Generates a news-specific sitemap for better SEO."""
    return generate_news_sitemap()


@main_blueprint.route("/sitemap-index.xml")
def sitemap_index():
    """Generates a sitemap index for large sites with multiple sitemaps."""
    try:
        # Create the root <sitemapindex> element with namespace
        sitemapindex = ET.Element(
            "sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        )

        # Main sitemap
        sitemap_element = ET.SubElement(sitemapindex, "sitemap")
        ET.SubElement(sitemap_element, "loc").text = url_for("main.sitemap", _external=True)
        ET.SubElement(sitemap_element, "lastmod").text = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # News-specific sitemap
        sitemap_element = ET.SubElement(sitemapindex, "sitemap")
        ET.SubElement(sitemap_element, "loc").text = url_for("main.sitemap_news", _external=True)
        ET.SubElement(sitemap_element, "lastmod").text = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Convert to XML string
        sitemap_xml_string = ET.tostring(sitemapindex, encoding="unicode", method="xml")
        final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + sitemap_xml_string

        return Response(final_xml, mimetype="application/xml")

    except Exception as err:
        current_app.logger.error(
            f"Sitemap index generation failed: {err}", exc_info=True
        )
        return Response("Error generating sitemap index", status=500, mimetype="text/plain")


@main_blueprint.route("/sitemap.xml")
def sitemap():
    """Generates a comprehensive sitemap.xml dynamically with SEO optimization."""
    try:
        # Create the root <urlset> element with namespace
        urlset = ET.Element(
            "urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        )

        # 1. Static Pages (Publicly accessible HTML pages)
        static_endpoints = [
            ("main.home", "daily", 1.0),  # Homepage - highest priority
            ("main.news", "daily", 0.9),  # Main news listing page
            ("main.videos", "weekly", 0.8),  # Main video listing page
            ("main.gallery", "weekly", 0.7),  # Main gallery listing page
            ("main.utama", "daily", 0.8),  # Utama page
            ("main.about", "monthly", 0.5),  # About page
            ("main.hypes", "weekly", 0.6),  # Hypes page
            ("main.premium", "weekly", 0.6),  # Premium page
        ]

        for endpoint, changefreq, priority in static_endpoints:
            try:
                loc = url_for(endpoint, _external=True)
                add_url_to_sitemap(
                    urlset, loc, changefreq=changefreq, priority=priority
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Sitemap: Could not generate URL for static endpoint '{endpoint}': {e}"
                )

        # 2. News Detail Pages with SEO optimization
        news_items = (
            db.session.query(
                News.id, 
                News.updated_at, 
                News.seo_slug,
                News.meta_robots,
                News.is_news,
                News.is_premium,
                News.is_main_news,
                News.read_count,
                News.date
            )
            .filter(News.is_visible == True)
            .order_by(News.updated_at.desc())
            .all()
        )
        
        for news_data in news_items:
            news_id, updated_at, seo_slug, meta_robots, is_news, is_premium, is_main_news, read_count, date = news_data
            
            # Skip if explicitly marked as noindex
            if meta_robots and "noindex" in meta_robots.lower():
                continue
                
            try:
                # Use SEO slug if available, otherwise use ID
                if seo_slug:
                    loc = url_for("main.news_detail", news_id=news_id, news_title=seo_slug, _external=True)
                else:
                    loc = url_for("main.news_detail", news_id=news_id, _external=True)
                
                # Determine priority based on content importance
                if is_main_news:
                    priority = 0.9  # Main news gets higher priority
                elif is_premium:
                    priority = 0.8  # Premium content gets higher priority
                elif read_count and read_count > 100:
                    priority = 0.8  # Popular content gets higher priority
                else:
                    priority = 0.7  # Regular content
                
                # Determine change frequency based on content type and age
                if is_main_news:
                    changefreq = "daily"
                elif is_premium:
                    changefreq = "weekly"
                else:
                    # Determine based on how recent the content is
                    days_old = (datetime.now(timezone.utc) - date).days if date else 365
                    if days_old < 7:
                        changefreq = "daily"
                    elif days_old < 30:
                        changefreq = "weekly"
                    elif days_old < 90:
                        changefreq = "monthly"
                    else:
                        changefreq = "yearly"
                
                add_url_to_sitemap(
                    urlset, loc, lastmod=updated_at, changefreq=changefreq, priority=priority
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Sitemap: Could not generate URL for news ID {news_id}: {e}"
                )

        # 3. YouTube Videos
        videos = (
            db.session.query(YouTubeVideo.id, YouTubeVideo.updated_at, YouTubeVideo.youtube_id)
            .filter(YouTubeVideo.is_visible == True)
            .order_by(YouTubeVideo.updated_at.desc())
            .all()
        )
        
        for video_id, updated_at, youtube_id in videos:
            try:
                # Note: This assumes you have a video detail route
                # If not, you might want to link directly to YouTube or create a detail page
                loc = url_for("main.videos", _external=True) + f"#video-{youtube_id}"
                add_url_to_sitemap(
                    urlset, loc, lastmod=updated_at, changefreq="weekly", priority=0.6
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Sitemap: Could not generate URL for video ID {video_id}: {e}"
                )

        # 4. Images/Gallery Items
        images = (
            db.session.query(Image.id, Image.updated_at, Image.filename)
            .filter(Image.is_visible == True)
            .order_by(Image.updated_at.desc())
            .all()
        )
        
        for image_id, updated_at, filename in images:
            try:
                # Link to gallery page with image focus
                loc = url_for("main.gallery", _external=True) + f"#image-{image_id}"
                add_url_to_sitemap(
                    urlset, loc, lastmod=updated_at, changefreq="monthly", priority=0.5
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Sitemap: Could not generate URL for image ID {image_id}: {e}"
                )

        # 5. Category Pages with SEO optimization
        categories = Category.query.order_by(Category.name).all()
        for cat in categories:
            try:
                loc = url_for("main.news", category=cat.name, _external=True)
                # Categories get high priority as they're important for SEO
                add_url_to_sitemap(
                    urlset, loc, changefreq="daily", priority=0.8
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Sitemap: Could not generate URL for category '{cat.name}': {e}"
                )

        # 6. Tag Pages with SEO optimization
        tag_strings_tuples = (
            db.session.query(News.tagar)
            .filter(
                and_(News.is_visible == True, News.tagar.isnot(None), News.tagar != "")
            )
            .distinct()
            .all()
        )
        all_tags = set()
        for tag_string_tuple in tag_strings_tuples:
            tag_string = tag_string_tuple[0] if tag_string_tuple[0] else ""
            tags_in_string = [
                tag.strip() for tag in tag_string.split(",") if tag.strip()
            ]
            all_tags.update(tags_in_string)

        for tag_name in sorted(list(all_tags)):
            try:
                loc = url_for("main.news", tag=tag_name, _external=True)
                # Tags get good priority but slightly lower than categories
                add_url_to_sitemap(
                    urlset, loc, changefreq="daily", priority=0.7
                )
            except Exception as e:
                current_app.logger.warning(
                    f"Sitemap: Could not generate URL for tag '{tag_name}': {e}"
                )

        # 7. Pagination pages for main content types (optional, for large sites)
        # News pagination
        total_news = News.query.filter_by(is_visible=True).count()
        if total_news > 20:  # Only add pagination if there are many articles
            total_pages = (total_news + 19) // 20  # Assuming 20 per page
            for page in range(2, min(total_pages + 1, 11)):  # Limit to first 10 pages
                try:
                    loc = url_for("main.news", page=page, _external=True)
                    add_url_to_sitemap(
                        urlset, loc, changefreq="daily", priority=0.6
                    )
                except Exception as e:
                    current_app.logger.warning(
                        f"Sitemap: Could not generate URL for news page {page}: {e}"
                    )

        # Video pagination
        total_videos = YouTubeVideo.query.filter_by(is_visible=True).count()
        if total_videos > 6:  # Only add pagination if there are many videos
            total_pages = (total_videos + 5) // 6  # Assuming 6 per page
            for page in range(2, min(total_pages + 1, 6)):  # Limit to first 5 pages
                try:
                    loc = url_for("main.videos", page=page, _external=True)
                    add_url_to_sitemap(
                        urlset, loc, changefreq="weekly", priority=0.5
                    )
                except Exception as e:
                    current_app.logger.warning(
                        f"Sitemap: Could not generate URL for videos page {page}: {e}"
                    )

        # Gallery pagination
        total_images = Image.query.filter_by(is_visible=True).count()
        if total_images > 15:  # Only add pagination if there are many images
            total_pages = (total_images + 14) // 15  # Assuming 15 per page
            for page in range(2, min(total_pages + 1, 6)):  # Limit to first 5 pages
                try:
                    loc = url_for("main.gallery", page=page, _external=True)
                    add_url_to_sitemap(
                        urlset, loc, changefreq="monthly", priority=0.4
                    )
                except Exception as e:
                    current_app.logger.warning(
                        f"Sitemap: Could not generate URL for gallery page {page}: {e}"
                    )

        # Convert the ElementTree to an XML string
        sitemap_xml_string = ET.tostring(urlset, encoding="unicode", method="xml")
        # Add the XML declaration manually as ET doesn't always include it nicely
        final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + sitemap_xml_string

        return Response(final_xml, mimetype="application/xml")

    except SQLAlchemyError as db_err:
        current_app.logger.error(
            f"Sitemap generation failed due to database error: {db_err}", exc_info=True
        )
        return Response(
            "Error generating sitemap: Database unavailable",
            status=500,
            mimetype="text/plain",
        )
    except Exception as err:
        current_app.logger.error(
            f"Sitemap generation failed due to unexpected error: {err}", exc_info=True
        )
        return Response("Error generating sitemap", status=500, mimetype="text/plain")


@main_blueprint.app_errorhandler(404)
def page_not_found(error):
    return render_template(
        "error.html", code=404, message="Halaman Tidak Ditemukan"
    ), 404


@main_blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template("error.html", code=403, message="Akses Ditolak"), 403


@main_blueprint.app_errorhandler(405)
def method_not_allowed(error):
    return render_template(
        "error.html", code=405, message="Metode Tidak Diizinkan"
    ), 405


@main_blueprint.app_errorhandler(500)
def internal_server_error(error):
    return render_template(
        "error.html", code=500, message="Kesalahan Server Internal"
    ), 500


def save_brand_asset_file(file, field):
    """
    Saves a brand asset file to static/pic/ with a fixed name, replacing the existing file.
    Auto-converts any image to PNG, regardless of original type or name.
    """
    from PIL import Image as PILImage, UnidentifiedImageError
    allowed_names = {
        "logo_header": "logo.png",
        "logo_footer": "logo_footer.png",
        "favicon": "favicon.png",
        "placeholder_image": "placeholder.png",
    }
    if field not in allowed_names:
        raise ValueError("Invalid brand asset field")
    filename = allowed_names[field]
    file_path = os.path.join("static/pic", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Convert to PNG using PIL
    try:
        img = PILImage.open(file)
        img = img.convert("RGBA") if img.mode in ("RGBA", "P") else img.convert("RGB")
        img.save(file_path, format="PNG")
    except UnidentifiedImageError:
        raise ValueError("File is not a valid image")
    return filename, file_path
