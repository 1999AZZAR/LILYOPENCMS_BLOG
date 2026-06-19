"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import sys
import os
from datetime import datetime, timezone
import random
import json
import re
import unicodedata
import html
from urllib.parse import urlparse, urljoin

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

from models import AlbumChapter, Album, News, Category, User, Image, BrandIdentity
from sqlalchemy import text
# Import unified settings with fallback for different import contexts
try:
    from .unified_settings import get_unified_settings
except ImportError:
    from seo_injector.unified_settings import get_unified_settings

def get_seo_injection_settings():
    """Get SEO injection settings from the unified settings."""
    settings = get_unified_settings()
    return {
        'website_name': settings.get_brand_name(),
        'website_url': settings.get_website_url(),
        'website_description': settings.get_setting('website_description', ''),
        'website_language': settings.get_default_language(),
        'organization_name': settings.get_organization_name(),
        'organization_logo': settings.get_setting('organization_logo', ''),
        'organization_description': settings.get_setting('organization_description', '')
    }

def clean_markdown_content(content):
    """Clean markdown content and extract plain text for SEO with enhanced filtering."""
    if not content:
        return ""
    
    # Remove HTML tags completely
    content = re.sub(r'<[^>]+>', '', content)
    
    # Remove markdown formatting with better patterns
    # Headers (all levels)
    content = re.sub(r'^#{1,6}\s+(.*?)$', r'\1', content, flags=re.MULTILINE)
    
    # Bold and italic (handle nested cases)
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic (but not if it's part of bold)
    content = re.sub(r'__(.*?)__', r'\1', content)      # Bold underscore
    content = re.sub(r'_(.*?)_', r'\1', content)        # Italic underscore
    
    # Code blocks and inline code
    content = re.sub(r'```[\s\S]*?```', '', content)    # Code blocks
    content = re.sub(r'`([^`]+)`', r'\1', content)      # Inline code
    
    # Links (extract text only)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Markdown links
    content = re.sub(r'<([^>]+)>', r'\1', content)              # HTML links
    
    # Images (remove completely)
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)    # Markdown images
    content = re.sub(r'<img[^>]+>', '', content)                # HTML images
    
    # Strikethrough
    content = re.sub(r'~~(.*?)~~', r'\1', content)      # Strikethrough
    
    # Lists (remove markers)
    content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)  # Unordered lists
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)  # Ordered lists
    
    # Blockquotes
    content = re.sub(r'^\s*>\s+', '', content, flags=re.MULTILINE)       # Blockquotes
    
    # Horizontal rules
    content = re.sub(r'^[-*_]{3,}$', '', content, flags=re.MULTILINE)    # Horizontal rules
    
    # Tables (simplify to text)
    content = re.sub(r'\|[^|]*\|', '', content)                          # Table rows
    content = re.sub(r'^\s*[-|:]+\s*$', '', content, flags=re.MULTILINE) # Table separators
    
    # Footnotes
    content = re.sub(r'\[\^([^\]]+)\]', '', content)                     # Footnotes
    
    # Escaped characters
    content = re.sub(r'\\([\\`*_{}\[\]()#+\-!])', r'\1', content)       # Escaped markdown chars
    
    # Clean up whitespace and formatting
    content = re.sub(r'\n\s*\n', '\n', content)  # Multiple newlines to single
    content = re.sub(r'\n{3,}', '\n\n', content) # More than 2 newlines to 2
    content = re.sub(r'\s+', ' ', content)       # Multiple spaces to single
    content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)  # Trim lines
    content = content.strip()
    
    # Remove any remaining markdown artifacts
    content = re.sub(r'^\s*[#*\-+`~]\s*', '', content, flags=re.MULTILINE)
    
    return content

def extract_images_from_content(content):
    """Extract image URLs from markdown content."""
    if not content:
        return []
    
    images = []
    
    # Find markdown image syntax: ![alt](url)
    markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
    for alt, url in markdown_images:
        images.append({
            'url': url.strip(),
            'alt': alt.strip(),
            'type': 'markdown'
        })
    
    # Find HTML img tags
    html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', content)
    for url in html_images:
        images.append({
            'url': url.strip(),
            'alt': '',
            'type': 'html'
        })
    
    return images

def normalize_image_url(image_url, base_url=None):
    """Normalize image URL to handle internal vs external links."""
    if not image_url:
        return None
    
    # Get actual settings from database
    if base_url is None:
        seo_settings = get_seo_injection_settings()
        base_url = seo_settings['website_url']
    
    # If it's already a full URL
    if image_url.startswith(('http://', 'https://')):
        return image_url
    
    # If it's a relative path starting with /
    if image_url.startswith('/'):
        return urljoin(base_url, image_url)
    
    # If it's a relative path without /
    if not image_url.startswith('/'):
        return urljoin(base_url, '/' + image_url)
    
    return image_url

def get_seo_settings():
    """Get SEO settings from unified settings."""
    settings = get_unified_settings()
    return {
        'chapter_meta_title': settings.get_template('chapter_meta_title', '{title} - Chapter {chapter_number} - {album_title} - {brand_name}'),
        'chapter_meta_description': settings.get_template('chapter_meta_description', 'Read Chapter {chapter_number}: {title} from {album_title}. {excerpt} - Read online for free on {brand_name}.'),
        'chapter_meta_keywords': settings.get_template('chapter_meta_keywords', '{album_category}, {title_keywords}, chapter {chapter_number}, {album_title}, {brand_name}'),
        'chapter_og_title': settings.get_template('chapter_og_title', '{title} - Chapter {chapter_number} - {album_title} - {brand_name}')
    }

def get_website_url(brand_info=None, settings=None):
    """Get website URL from unified settings."""
    unified_settings = get_unified_settings()
    return unified_settings.get_website_url()

def get_best_image_for_seo(chapter):
    """Get the best image for SEO from chapter."""
    # First check if chapter's news has an image
    if chapter.news and chapter.news.image:
        if chapter.news.image.url:
            return normalize_image_url(chapter.news.image.url)
        elif chapter.news.image.filepath:
            return normalize_image_url(chapter.news.image.filepath)
    
    # Check if album has a cover image
    if chapter.album and chapter.album.cover_image:
        if chapter.album.cover_image.url:
            return normalize_image_url(chapter.album.cover_image.url)
        elif chapter.album.cover_image.filepath:
            return normalize_image_url(chapter.album.cover_image.filepath)
    
    # Extract images from news content
    if chapter.news and chapter.news.content:
        content_images = extract_images_from_content(chapter.news.content)
        if content_images:
            # Use the first image found
            return normalize_image_url(content_images[0]['url'])
    
    # Get actual settings from database
    seo_settings = get_seo_injection_settings()
    base_url = seo_settings['website_url']
    
    # Default image
    return f"{base_url}/static/pic/placeholder.png"

def generate_seo_slug(title):
    """Generate SEO-friendly slug from title."""
    if not title:
        return None
    
    # Normalize unicode characters
    slug = unicodedata.normalize('NFKD', title)
    
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-').lower()
    
    # Limit length
    if len(slug) > 50:
        slug = slug[:50]
    
    return slug

def generate_schema_markup(chapter):
    """Generate JSON-LD structured data for the chapter."""
    # Get actual settings from database
    seo_settings = get_seo_injection_settings()
    website_url = seo_settings['website_url']
    organization_name = seo_settings['organization_name']
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Chapter",
        "name": chapter.chapter_title,
        "description": chapter.meta_description or f"Chapter {chapter.chapter_number}: {chapter.chapter_title}",
        "author": {
            "@type": "Person",
            "name": chapter.album.creator_user.get_full_name() if chapter.album and chapter.album.creator_user else "Unknown Author"
        },
        "publisher": {
            "@type": "Organization",
            "name": organization_name,
            "url": website_url
        },
        "datePublished": chapter.created_at.isoformat() if chapter.created_at else None,
        "dateModified": chapter.updated_at.isoformat() if chapter.updated_at else None,
        "inLanguage": seo_settings['website_language'],
        "genre": chapter.album.category.name if chapter.album and chapter.album.category else None,
        "url": f"{website_url}/album/{chapter.album_id}/chapter/{chapter.chapter_number}",
        "position": chapter.chapter_number,
        "isPartOf": {
            "@type": "Book" if chapter.album and chapter.album.is_completed else "CreativeWork",
            "name": chapter.album.title if chapter.album else "Unknown Album",
            "url": f"{website_url}/album/{chapter.album_id}" if chapter.album_id else None
        }
    }
    
    # Add image if available
    image_url = get_best_image_for_seo(chapter)
    if image_url:
        schema["image"] = {
            "@type": "ImageObject",
            "url": image_url,
            "width": 800,
            "height": 600
        }
    
    # Add chapter content if available
    if chapter.news and chapter.news.content:
        clean_content = clean_markdown_content(chapter.news.content)
        if clean_content:
            schema["text"] = clean_content
    
    return json.dumps(schema, ensure_ascii=False)

def calculate_seo_score(chapter):
    """Calculate SEO score for the chapter (0-100)."""
    score = 0
    
    # Basic SEO elements (40 points)
    if chapter.chapter_title and len(chapter.chapter_title.strip()) > 0:
        score += 10
    if chapter.meta_description and len(chapter.meta_description.strip()) > 0:
        score += 10
    if chapter.meta_keywords and len(chapter.meta_keywords.strip()) > 0:
        score += 10
    if chapter.seo_slug and len(chapter.seo_slug.strip()) > 0:
        score += 10
    
    # Social media optimization (30 points)
    if chapter.og_title and len(chapter.og_title.strip()) > 0:
        score += 10
    if chapter.og_description and len(chapter.og_description.strip()) > 0:
        score += 10
    if chapter.og_image and len(chapter.og_image.strip()) > 0:
        score += 10
    
    # Advanced SEO elements (30 points)
    if chapter.canonical_url and len(chapter.canonical_url.strip()) > 0:
        score += 10
    if chapter.schema_markup and len(chapter.schema_markup.strip()) > 0:
        score += 10
    if chapter.news and chapter.news.content and len(clean_markdown_content(chapter.news.content)) > 100:
        score += 10
    
    return min(score, 100)

def generate_meta_description(chapter):
    """Generate meta description from chapter content."""
    if chapter.meta_description:
        # Use existing meta description if available
        desc = chapter.meta_description.strip()
        if len(desc) > 160:
            desc = desc[:157] + "..."
        return desc
    
    # Generate from news content
    if chapter.news and chapter.news.content:
        clean_content = clean_markdown_content(chapter.news.content)
        if clean_content:
            # Use first 160 characters of cleaned content
            desc = clean_content[:160]
            if len(clean_content) > 160:
                desc = desc[:157] + "..."
            return desc
    
    # Fallback to chapter title and album info
    parts = [f"Chapter {chapter.chapter_number}: {chapter.chapter_title}"]
    if chapter.album:
        parts.append(f"from {chapter.album.title}")
    
    desc = " - ".join(parts)
    if len(desc) > 160:
        desc = desc[:157] + "..."
    return desc

def generate_meta_keywords(chapter):
    """Generate meta keywords from chapter content using smart configuration."""
    try:
        # Import smart config manager
        try:
            from .smart_config import SmartConfigManager
        except ImportError:
            from seo_injector.smart_config import SmartConfigManager

        # Initialize smart config manager
        config_manager = SmartConfigManager()

        # Prepare content data for smart keyword generation
        chapter_title = chapter.chapter_title or ''
        album_title = chapter.album.title if chapter.album else ''
        chapter_content = chapter.news.content if chapter.news else ''

        content_data = {
            'title': chapter_title,
            'excerpt': chapter_content[:200] if chapter_content else '',  # First 200 chars as excerpt
            'author': chapter.album.author.username if chapter.album and chapter.album.author else '',
            'album_title': album_title,
            'chapter_number': chapter.chapter_number or 1,
            'category': chapter.album.category.name.lower() if chapter.album and chapter.album.category else '',
            'date_published': chapter.created_at.isoformat() if chapter.created_at else '',
            'date_modified': chapter.updated_at.isoformat() if chapter.updated_at else '',
            'canonical_url': f"/chapter/{chapter.id}" if hasattr(chapter, 'id') else '',
            'website_name': config_manager.settings.website_name
        }

        # Add combined content for analysis
        content_text = f"{chapter_title} {album_title} {chapter_content}"
        if chapter.album:
            if chapter.album.is_completed:
                content_text += ' completed finished story'
            else:
                content_text += ' ongoing in-progress story'

            if chapter.album.is_premium:
                content_text += ' premium exclusive content'

        content_text += ' chapter episode part story content'
        content_data['content'] = content_text

        # Generate smart keywords
        seo_data = config_manager.generate_seo_data('chapter', content_data)

        return seo_data.get('meta_keywords', '')

    except Exception as e:
        print(f"Warning: Smart keyword generation failed, falling back to basic generation: {e}")

        # Fallback to basic keyword generation
        return _generate_basic_chapter_keywords(chapter)

def _generate_basic_chapter_keywords(chapter):
    """Fallback basic keyword generation for chapters."""
    keywords = []

    # Add chapter title words
    if chapter.chapter_title:
        title_words = [word.lower() for word in chapter.chapter_title.split() if len(word) > 2]
        keywords.extend(title_words[:5])

    # Add album and category info
    if chapter.album:
        if chapter.album.title:
            album_words = [word.lower() for word in chapter.album.title.split() if len(word) > 2]
            keywords.extend(album_words[:3])

        if chapter.album.category:
            keywords.append(chapter.album.category.name.lower())

    # Add content keywords from news
    if chapter.news and chapter.news.content:
        clean_content = clean_markdown_content(chapter.news.content)
        # Extract meaningful words (3+ characters)
        content_words = [word.lower() for word in clean_content.split() if len(word) > 3]
        # Get most common words (simple approach)
        word_freq = {}
        for word in content_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Add top 3 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords.extend([word for word, freq in sorted_words[:3]])

    # Add chapter-specific keywords
    keywords.extend(["chapter", "episode", "part", "story", "content"])

    # Add album status keywords
    if chapter.album:
        if chapter.album.is_completed:
            keywords.extend(["completed", "finished"])
        else:
            keywords.extend(["ongoing", "in-progress"])

        if chapter.album.is_premium:
            keywords.extend(["premium", "exclusive"])

    # Remove duplicates and limit
    unique_keywords = list(dict.fromkeys(keywords))[:10]
    return ", ".join(unique_keywords)

def generate_open_graph_data(chapter):
    """Generate Open Graph data for the chapter."""
    og_title = chapter.og_title or f"Chapter {chapter.chapter_number}: {chapter.chapter_title}"
    og_description = chapter.og_description or generate_meta_description(chapter)
    og_image = chapter.og_image
    
    if not og_image:
        og_image = get_best_image_for_seo(chapter)
    
    return og_title, og_description, og_image

def clear_existing_seo(chapter):
    """Clear all existing SEO data from chapter."""
    print(f"   🗑️ Clearing existing SEO data...")
    
    # Clear all SEO fields
    chapter.meta_description = None
    chapter.meta_keywords = None
    chapter.og_title = None
    chapter.og_description = None
    chapter.og_image = None
    chapter.canonical_url = None
    chapter.seo_slug = None
    chapter.schema_markup = None
    chapter.twitter_card = None
    chapter.twitter_title = None
    chapter.twitter_description = None
    chapter.twitter_image = None
    chapter.meta_author = None
    chapter.meta_language = None
    chapter.meta_robots = None
    chapter.structured_data_type = None
    chapter.seo_score = None
    chapter.last_seo_audit = None
    chapter.is_seo_lock = False  # Reset lock to false

def inject_chapter_seo():
    """Inject SEO data for album chapters that don't have SEO fields populated."""
    print("🎯 LilyOpenCMS Chapter SEO Injector")
    print("=" * 50)
    
    with app.app_context():
        # Get all album chapters
        chapters = AlbumChapter.query.all()
        print(f"📖 Found {len(chapters)} chapters in database")
        
        if not chapters:
            print("❌ No chapters found in database")
            return
        
        # Track statistics
        updated_count = 0
        skipped_count = 0
        error_count = 0
        locked_count = 0
        
        print(f"\n🔍 Analyzing chapters for SEO injection...")
        
        for i, chapter in enumerate(chapters, 1):
            print(f"\n📖 [{i}/{len(chapters)}] Processing: Chapter {chapter.chapter_number} - {chapter.chapter_title}")
            
            try:
                # Check if SEO is locked
                if chapter.is_seo_lock:
                    print(f"   🔒 Skipping - SEO is locked")
                    locked_count += 1
                    continue
                
                # Clear existing SEO data first (force clean injection)
                clear_existing_seo(chapter)
                
                # Generate SEO data within no_autoflush context to prevent database locks
                print(f"   🔧 Generating SEO data...")

                # Use no_autoflush context to prevent database locks during lazy loading
                from models import db
                with db.session.no_autoflush:
                    # Generate SEO slug
                    chapter.seo_slug = generate_seo_slug(f"chapter-{chapter.chapter_number}-{chapter.chapter_title}")
                    print(f"   ✅ Generated SEO slug: {chapter.seo_slug}")

                    # Generate meta title using template
                    seo_settings = get_seo_settings()
                    chapter_title_template = seo_settings.get('chapter_meta_title', '{title} - Chapter {chapter_number} - {album_title} - {brand_name}')

                    # Get brand name from unified settings
                    unified_settings = get_unified_settings()
                    brand_name = unified_settings.get_brand_name()

                    # Apply template for meta title
                    variables = {
                        'title': chapter.chapter_title,
                        'chapter_number': chapter.chapter_number,
                        'album_title': chapter.album.title if chapter.album else '',
                        'brand_name': brand_name
                    }

                    chapter.meta_title = unified_settings.apply_template(chapter_title_template, variables)
                    if not chapter.meta_title or chapter.meta_title == chapter_title_template:
                        chapter.meta_title = f"{chapter.chapter_title} - Chapter {chapter.chapter_number} - {brand_name}"
                    print(f"   ✅ Generated meta title: {chapter.meta_title}")

                    # Generate meta description
                    chapter.meta_description = generate_meta_description(chapter)
                    print(f"   ✅ Generated meta description: {chapter.meta_description[:50]}...")

                    # Generate meta keywords
                    chapter.meta_keywords = generate_meta_keywords(chapter)
                    print(f"   ✅ Generated meta keywords: {chapter.meta_keywords}")

                    # Generate Open Graph data
                    og_title, og_description, og_image = generate_open_graph_data(chapter)

                    chapter.og_title = og_title
                    print(f"   ✅ Generated OG title: {chapter.og_title}")

                    chapter.og_description = og_description
                    print(f"   ✅ Generated OG description: {chapter.og_description[:50]}...")

                    chapter.og_image = og_image
                    print(f"   ✅ Set OG image: {chapter.og_image}")

                    # Generate schema markup
                    chapter.schema_markup = generate_schema_markup(chapter)
                    print(f"   ✅ Generated schema markup")
                
                # Get website URL for canonical URL
                brand_info = BrandIdentity.query.first()
                seo_settings = get_seo_settings()
                website_url = get_website_url(brand_info, seo_settings)
                
                # Set default values
                if chapter.album and chapter.album.creator_user:
                    chapter.meta_author = chapter.album.creator_user.get_full_name()
                else:
                    chapter.meta_author = "Unknown Author"
                
                chapter.meta_language = "id"
                chapter.meta_robots = "index, follow"
                chapter.twitter_card = "summary_large_image"
                chapter.structured_data_type = "Chapter"
                chapter.canonical_url = f"{website_url}/album/{chapter.album_id}/chapter/{chapter.chapter_number}"
                
                # Calculate SEO score
                chapter.seo_score = calculate_seo_score(chapter)
                chapter.last_seo_audit = datetime.now(timezone.utc)
                
                print(f"   📊 SEO Score: {chapter.seo_score}/100")
                
                # Save to database with retry logic for SQLite locking
                max_retries = 3
                retry_delay = 0.1
                for attempt in range(max_retries):
                    try:
                        db.session.commit()
                        break
                    except Exception as commit_error:
                        if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                            print(f"   🔄 Database locked, retrying commit for chapter {chapter.id} (attempt {attempt + 1})")
                            db.session.rollback()
                            import time
                            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            # Refresh the chapter object
                            chapter = AlbumChapter.query.get(chapter.id)
                            if not chapter:
                                raise ValueError(f"Chapter {chapter.id} not found after rollback")
                        else:
                            raise commit_error
                print(f"   ✅ Successfully updated SEO data")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing chapter: {e}")
                db.session.rollback()
                error_count += 1
        
        # Final summary
        print("\n" + "=" * 50)
        print("📊 CHAPTER SEO INJECTION SUMMARY")
        print("=" * 50)
        print(f"✅ Successfully updated: {updated_count} chapters")
        print(f"🔒 Skipped (SEO locked): {locked_count} chapters")
        print(f"❌ Errors: {error_count} chapters")
        print(f"📖 Total chapters processed: {len(chapters)}")
        
        if updated_count > 0:
            print(f"\n🎉 Successfully injected SEO data for {updated_count} chapters!")
        elif locked_count > 0:
            print(f"\nℹ️ All chapters have locked SEO ({locked_count} chapters)")
        else:
            print(f"\n⚠️ No chapters were updated due to errors")

def show_chapter_seo_stats():
    """Show statistics about chapter SEO data."""
    print("📊 Chapter SEO Statistics")
    print("=" * 30)
    
    with app.app_context():
        total_chapters = AlbumChapter.query.count()
        
        # Count chapters with different SEO fields
        with_meta_desc = AlbumChapter.query.filter(AlbumChapter.meta_description.isnot(None)).count()
        with_meta_keywords = AlbumChapter.query.filter(AlbumChapter.meta_keywords.isnot(None)).count()
        with_seo_slug = AlbumChapter.query.filter(AlbumChapter.seo_slug.isnot(None)).count()
        with_og_title = AlbumChapter.query.filter(AlbumChapter.og_title.isnot(None)).count()
        with_schema = AlbumChapter.query.filter(AlbumChapter.schema_markup.isnot(None)).count()
        locked_seo = AlbumChapter.query.filter_by(is_seo_lock=True).count()
        
        print(f"📖 Total chapters: {total_chapters}")
        print(f"📝 With meta description: {with_meta_desc}")
        print(f"🏷️ With meta keywords: {with_meta_keywords}")
        print(f"🔗 With SEO slug: {with_seo_slug}")
        print(f"📱 With OG title: {with_og_title}")
        print(f"🏗️ With schema markup: {with_schema}")
        print(f"🔒 SEO locked: {locked_seo}")
        
        # Calculate percentages
        if total_chapters > 0:
            print(f"\n📊 Percentages:")
            print(f"   Meta description: {(with_meta_desc/total_chapters)*100:.1f}%")
            print(f"   Meta keywords: {(with_meta_keywords/total_chapters)*100:.1f}%")
            print(f"   SEO slug: {(with_seo_slug/total_chapters)*100:.1f}%")
            print(f"   OG title: {(with_og_title/total_chapters)*100:.1f}%")
            print(f"   Schema markup: {(with_schema/total_chapters)*100:.1f}%")
            print(f"   SEO locked: {(locked_seo/total_chapters)*100:.1f}%")

def main():
    """Main function to run the SEO injector."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inject SEO data for album chapters")
    parser.add_argument("--stats", action="store_true", help="Show SEO statistics only")
    parser.add_argument("--force", action="store_true", help="Force update even if SEO data exists")
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced features (smart analysis, batch processing, etc.)")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing (enhanced mode)")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum worker threads (enhanced mode)")
    parser.add_argument("--no-cache", action="store_true", help="Disable smart caching (enhanced mode)")
    parser.add_argument("--no-validation", action="store_true", help="Disable quality validation (enhanced mode)")
    
    args = parser.parse_args()
    
    if args.stats:
        show_chapter_seo_stats()
    else:
        inject_chapter_seo()

if __name__ == "__main__":
    main() 