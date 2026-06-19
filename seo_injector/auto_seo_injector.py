"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Automatic SEO Injector for LilyOpenCMS
Triggers SEO injection when news/articles are published (is_visible = True)
"""

import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

from models import News
from seo_injector.inject_news_seo import (
    generate_meta_description,
    generate_meta_keywords,
    generate_seo_slug,
    generate_schema_markup,
    calculate_seo_score,
    generate_open_graph_data,
    get_best_image_for_seo,
    get_seo_injection_settings,
    get_website_url
)
from .unified_settings import get_unified_settings


class AutoSEOInjector:
    """Automatic SEO injector that triggers on news/article publish."""

    def __init__(self):
        self.logger = app.logger

    def check_seo_quality(self, news_item: News) -> Tuple[bool, List[str]]:
        """
        Check if SEO data is sufficient or needs injection.

        Returns:
            Tuple[bool, List[str]]: (is_sufficient, issues_list)
        """
        issues = []

        # Check for basic SEO elements
        if not news_item.meta_description or len(news_item.meta_description.strip()) < 50:
            issues.append("Meta description missing or too short")

        if not news_item.meta_keywords or len(news_item.meta_keywords.strip()) < 10:
            issues.append("Meta keywords missing or insufficient")

        if not news_item.seo_slug or len(news_item.seo_slug.strip()) == 0:
            issues.append("SEO slug missing")

        if not news_item.og_title or len(news_item.og_title.strip()) == 0:
            issues.append("Open Graph title missing")

        if not news_item.og_description or len(news_item.og_description.strip()) == 0:
            issues.append("Open Graph description missing")

        if not news_item.schema_markup or len(news_item.schema_markup.strip()) == 0:
            issues.append("Schema markup missing")

        if not news_item.canonical_url or len(news_item.canonical_url.strip()) == 0:
            issues.append("Canonical URL missing")

        # Check SEO score
        current_score = news_item.seo_score or 0
        if current_score < 70:  # Require at least 70/100 SEO score
            issues.append(f"SEO score too low ({current_score}/100)")

        return len(issues) == 0, issues

    def inject_seo_on_publish(self, news_item: News) -> Dict[str, Any]:
        """
        Automatically inject SEO data when news/article is published.

        Args:
            news_item: The news article being published

        Returns:
            Dict with injection results
        """
        try:
            with app.app_context():
                self.logger.info(f"🔍 Checking SEO for published article: {news_item.title} (ID: {news_item.id})")

                # Skip if SEO is locked
                if news_item.is_seo_lock:
                    self.logger.info(f"🔒 Skipping SEO injection - SEO is locked for article {news_item.id}")
                    return {
                        'status': 'skipped',
                        'reason': 'seo_locked',
                        'article_id': news_item.id
                    }

                # Check if SEO injection is needed
                is_sufficient, issues = self.check_seo_quality(news_item)

                if is_sufficient:
                    self.logger.info(f"✅ SEO data is sufficient for article {news_item.id}")
                    return {
                        'status': 'sufficient',
                        'article_id': news_item.id,
                        'seo_score': news_item.seo_score
                    }

                self.logger.info(f"🔧 Injecting SEO data for article {news_item.id}. Issues found: {issues}")

                # Clear existing SEO data for clean injection
                self._clear_existing_seo(news_item)

                # Inject fresh SEO data
                success = self._inject_seo_data(news_item)

                if success:
                    # Recalculate SEO score
                    news_item.seo_score = calculate_seo_score(news_item)
                    news_item.last_seo_audit = datetime.now(timezone.utc)

                    # Commit changes
                    db.session.commit()

                    self.logger.info(f"✅ SEO injection completed for article {news_item.id} (Score: {news_item.seo_score}/100)")

                    return {
                        'status': 'injected',
                        'article_id': news_item.id,
                        'seo_score': news_item.seo_score,
                        'issues_fixed': issues
                    }
                else:
                    self.logger.error(f"❌ SEO injection failed for article {news_item.id}")
                    return {
                        'status': 'error',
                        'article_id': news_item.id,
                        'error': 'Injection failed'
                    }

        except Exception as e:
            self.logger.error(f"❌ Error during auto SEO injection for article {news_item.id}: {e}")
            db.session.rollback()
            return {
                'status': 'error',
                'article_id': news_item.id,
                'error': str(e)
            }

    def _clear_existing_seo(self, news_item: News):
        """Clear existing SEO data for clean injection."""
        news_item.meta_description = None
        news_item.meta_keywords = None
        news_item.og_title = None
        news_item.og_description = None
        news_item.og_image = None
        news_item.canonical_url = None
        news_item.seo_slug = None
        news_item.schema_markup = None
        news_item.twitter_card = None
        news_item.twitter_title = None
        news_item.twitter_description = None
        news_item.meta_author = None
        news_item.meta_language = None
        news_item.meta_robots = None
        news_item.structured_data_type = None
        news_item.seo_score = None
        news_item.last_seo_audit = None

    def _inject_seo_data(self, news_item: News) -> bool:
        """Inject SEO data into the news article."""
        try:
            # Get unified settings
            unified_settings = get_unified_settings()

            # Generate SEO slug with collision handling
            base_slug = generate_seo_slug(news_item.title)
            seo_slug = self._ensure_unique_slug(base_slug, news_item.id)
            news_item.seo_slug = seo_slug

            news_item.meta_description = generate_meta_description(news_item)
            news_item.meta_keywords = generate_meta_keywords(news_item)

            # Generate Open Graph data
            og_title, og_description, og_image = generate_open_graph_data(news_item)
            news_item.og_title = og_title
            news_item.og_description = og_description
            news_item.og_image = og_image

            # Generate schema markup
            news_item.schema_markup = generate_schema_markup(news_item)

            # Set default values
            seo_settings = get_seo_injection_settings()
            website_url = seo_settings['website_url']

            news_item.canonical_url = f"{website_url}/news/{news_item.id}"
            news_item.meta_author = news_item.author.get_full_name() if news_item.author else "Unknown Author"
            news_item.meta_language = unified_settings.get_default_language()
            news_item.meta_robots = unified_settings.get_default_meta_robots()
            news_item.twitter_card = unified_settings.get_default_twitter_card()
            news_item.structured_data_type = "NewsArticle"

            return True

        except Exception as e:
            self.logger.error(f"Error injecting SEO data: {e}")
            return False

    def _ensure_unique_slug(self, base_slug: str, news_id: int) -> str:
        """Ensure the SEO slug is unique by adding suffix if needed."""
        from models import News

        # Check if the base slug is already taken by another article
        existing = News.query.filter(News.seo_slug == base_slug, News.id != news_id).first()
        if not existing:
            return base_slug

        # If taken, add article ID as suffix
        unique_slug = f"{base_slug}-{news_id}"
        return unique_slug


# Global instance for easy access
auto_seo_injector = AutoSEOInjector()


def trigger_seo_injection_on_publish(news_item: News) -> Dict[str, Any]:
    """
    Convenience function to trigger SEO injection when news is published.

    Args:
        news_item: The news article being published

    Returns:
        Dict with injection results
    """
    return auto_seo_injector.inject_seo_on_publish(news_item)


def check_seo_before_publish(news_item: News) -> Tuple[bool, List[str]]:
    """
    Check SEO quality before publishing.

    Args:
        news_item: The news article to check

    Returns:
        Tuple[bool, List[str]]: (is_ready, issues_list)
    """
    return auto_seo_injector.check_seo_quality(news_item)


if __name__ == "__main__":
    # Test the injector
    with app.app_context():
        # Get a published news article for testing
        published_news = News.query.filter_by(is_visible=True).first()
        if published_news:
            result = trigger_seo_injection_on_publish(published_news)
            print(f"SEO Injection Result: {result}")
        else:
            print("No published news articles found for testing")
