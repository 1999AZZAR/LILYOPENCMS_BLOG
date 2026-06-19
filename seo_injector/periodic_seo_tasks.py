"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Periodic SEO Injection Tasks
Uses Celery for background processing to minimize system load
Runs periodically to ensure all articles eventually have proper SEO
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, TYPE_CHECKING, Union
import logging
from sqlalchemy import or_, nullsfirst

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import Celery and models (avoid circular import with main)
from celery_app.celery_app import celery_app

# Lazy imports to avoid circular dependencies
def get_app():
    from main import app
    return app

def get_db():
    from main import db
    return db

def get_news_model():
    from models import News
    return News

# Import News for type hints (only when TYPE_CHECKING to avoid circular imports)
if TYPE_CHECKING:
    from models import News
# Lazy import AutoSEOInjector to avoid circular import (import inside function where needed)
# from .auto_seo_injector import AutoSEOInjector
from .unified_settings import get_unified_settings

logger = logging.getLogger(__name__)

# Configuration for periodic SEO injection
SEO_INJECTION_CONFIG = {
    'batch_size': int(os.getenv('SEO_INJECTION_BATCH_SIZE', '10')),  # Process N articles at a time
    'max_runtime_seconds': int(os.getenv('SEO_INJECTION_MAX_RUNTIME', '300')),  # Max runtime in seconds
    'min_seo_score_threshold': int(os.getenv('SEO_INJECTION_MIN_SCORE', '70')),  # Only process articles below this score
    'max_age_days': int(os.getenv('SEO_INJECTION_MAX_AGE_DAYS', '365')),  # Only process articles newer than this
    'respect_seo_lock': os.getenv('SEO_INJECTION_RESPECT_LOCK', 'true').lower() == 'true',  # Skip locked articles
    'dry_run': os.getenv('SEO_INJECTION_DRY_RUN', 'false').lower() == 'true',  # Set to True for testing
    'enabled': os.getenv('SEO_INJECTION_ENABLED', 'true').lower() == 'true',  # Enable/disable periodic injection
}


@celery_app.task(bind=True, name='seo_injector.periodic_seo_injection')
def periodic_seo_injection_task(self, batch_size: Optional[int] = None, dry_run: Optional[bool] = None):
    """
    Periodic SEO injection task that runs in the background.

    This task finds articles with poor SEO and injects proper SEO data.
    Runs asynchronously to minimize system load.

    Args:
        batch_size: Override default batch size
        dry_run: Override dry run setting (for testing)
    """
    start_time = datetime.now(timezone.utc)
    logger.info("🚀 Starting periodic SEO injection task")

    # Check if periodic injection is enabled
    if not SEO_INJECTION_CONFIG.get('enabled', True):
        logger.info("ℹ️ Periodic SEO injection is disabled, skipping")
        return {
            'status': 'disabled',
            'message': 'Periodic SEO injection is disabled',
            'start_time': start_time.isoformat(),
            'end_time': datetime.now(timezone.utc).isoformat()
        }

    try:
        # Get configuration
        config = SEO_INJECTION_CONFIG.copy()
        if batch_size is not None:
            config['batch_size'] = batch_size
        if dry_run is not None:
            config['dry_run'] = dry_run

        with get_app().app_context():
            # Lazy import AutoSEOInjector to avoid circular import
            from .auto_seo_injector import AutoSEOInjector
            # Initialize SEO injector
            injector = AutoSEOInjector()

            # Get articles that need SEO injection
            articles_to_process = get_articles_needing_seo_injection(config)

            if not articles_to_process:
                logger.info("✅ No articles need SEO injection at this time")
                return {
                    'status': 'completed',
                    'message': 'No articles needed processing',
                    'articles_processed': 0,
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now(timezone.utc).isoformat()
                }

            logger.info(f"📊 Found {len(articles_to_process)} articles needing SEO injection")

            # Process articles in batches
            processed_count = 0
            successful_injections = 0
            errors = []

            for article in articles_to_process[:config['batch_size']]:
                try:
                    # Check if we've exceeded runtime
                    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                    if elapsed > config['max_runtime_seconds']:
                        logger.warning(f"⏰ Runtime limit exceeded ({elapsed:.1f}s), stopping processing")
                        break

                    logger.info(f"🔧 Processing article {article.id}: {article.title}")

                    # Skip if dry run
                    if config['dry_run']:
                        logger.info(f"🔍 DRY RUN: Would inject SEO for article {article.id}")
                        successful_injections += 1
                        processed_count += 1
                        continue

                    # Inject SEO
                    result = injector.inject_seo_on_publish(article)

                    if result.get('status') == 'injected':
                        successful_injections += 1
                        logger.info(f"✅ Successfully injected SEO for article {article.id} (Score: {result.get('seo_score', 'N/A')})")
                    elif result.get('status') == 'sufficient':
                        logger.info(f"ℹ️ SEO already sufficient for article {article.id}")
                    else:
                        logger.warning(f"❌ Failed to inject SEO for article {article.id}: {result}")

                    processed_count += 1

                except Exception as e:
                    error_msg = f"Error processing article {article.id}: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                    processed_count += 1

            # Calculate statistics
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            result = {
                'status': 'completed',
                'message': f'Processed {processed_count} articles, {successful_injections} SEO injections successful',
                'articles_processed': processed_count,
                'successful_injections': successful_injections,
                'errors_count': len(errors),
                'errors': errors[:5],  # Limit error details
                'dry_run': config['dry_run'],
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration
            }

            logger.info(f"✅ Periodic SEO injection completed: {result['message']}")
            return result

    except Exception as e:
        logger.error(f"❌ Critical error in periodic SEO injection: {str(e)}")
        return {
            'status': 'error',
            'message': f'Critical error: {str(e)}',
            'start_time': start_time.isoformat(),
            'end_time': datetime.now(timezone.utc).isoformat()
        }


@celery_app.task(bind=True, name='seo_injector.seo_health_check')
def seo_health_check_task(self):
    """
    SEO health check task to monitor overall SEO status.
    """
    logger.info("🔍 Running SEO health check")

    try:
        with get_app().app_context():
            # Get SEO statistics
            News = get_news_model()
            total_news = News.query.count()
            with_meta_desc = News.query.filter(News.meta_description.isnot(None)).count()
            with_meta_keywords = News.query.filter(News.meta_keywords.isnot(None)).count()
            with_seo_slug = News.query.filter(News.seo_slug.isnot(None)).count()
            with_og_title = News.query.filter(News.og_title.isnot(None)).count()
            with_schema = News.query.filter(News.schema_markup.isnot(None)).count()
            locked = News.query.filter(News.is_seo_lock == True).count()
            published = News.query.filter(News.is_visible == True).count()

            # Calculate percentages
            stats = {
                'total_articles': total_news,
                'published_articles': published,
                'seo_locked_articles': locked,
                'seo_coverage': {
                    'meta_description': (with_meta_desc / max(total_news, 1)) * 100,
                    'meta_keywords': (with_meta_keywords / max(total_news, 1)) * 100,
                    'seo_slug': (with_seo_slug / max(total_news, 1)) * 100,
                    'og_title': (with_og_title / max(total_news, 1)) * 100,
                    'schema_markup': (with_schema / max(total_news, 1)) * 100,
                },
                'published_seo_coverage': {
                    'meta_description': (with_meta_desc / max(published, 1)) * 100,
                    'meta_keywords': (with_meta_keywords / max(published, 1)) * 100,
                    'seo_slug': (with_seo_slug / max(published, 1)) * 100,
                    'og_title': (with_og_title / max(published, 1)) * 100,
                    'schema_markup': (with_schema / max(published, 1)) * 100,
                } if published > 0 else {}
            }

            logger.info(f"📊 SEO Health Check - Total: {total_news}, Published: {published}")
            logger.info(f"📈 Published SEO Coverage: {stats['published_seo_coverage']}")

            return {
                'status': 'success',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'statistics': stats
            }

    except Exception as e:
        logger.error(f"❌ Error in SEO health check: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


def get_articles_needing_seo_injection(config: Dict[str, Any]) -> List["News"]:
    """
    Get articles that need SEO injection based on configuration.

    Args:
        config: Configuration dictionary

    Returns:
        List of News articles needing SEO injection
    """
    try:
        News = get_news_model()
        # Base query: published articles that are not SEO locked
        query = News.query.filter(
            News.is_visible == True,
            News.content.isnot(None),
            News.title.isnot(None)
        )

        if config['respect_seo_lock']:
            query = query.filter(News.is_seo_lock != True)

        # Filter by age
        if config['max_age_days']:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=config['max_age_days'])
            query = query.filter(News.date >= cutoff_date)

        # Filter by SEO score (only get articles below threshold)
        if config['min_seo_score_threshold'] is not None:
            query = query.filter(
                or_(
                    News.seo_score < config['min_seo_score_threshold'],
                    News.seo_score.is_(None)
                )
            )

        # Order by priority: lowest SEO score first, then by date (newest first)
        articles = query.order_by(
            nullsfirst(News.seo_score.asc()),
            News.date.desc()
        ).all()

        return articles

    except Exception as e:
        logger.error(f"Error getting articles needing SEO injection: {str(e)}")
        return []


# Utility functions for manual triggering
def trigger_periodic_seo_injection(batch_size: Optional[int] = None, dry_run: Optional[bool] = False):
    """
    Manually trigger the periodic SEO injection task.

    Args:
        batch_size: Number of articles to process
        dry_run: Whether to do a dry run (no actual changes)
    """
    logger.info("🔧 Manually triggering periodic SEO injection")

    # Run synchronously for immediate feedback
    with get_app().app_context():
        result = periodic_seo_injection_task.apply(args=[batch_size, dry_run])
        return result.get()


def trigger_seo_health_check():
    """
    Manually trigger the SEO health check task.
    """
    logger.info("🔍 Manually triggering SEO health check")

    # Run synchronously for immediate feedback
    with get_app().app_context():
        result = seo_health_check_task.apply()
        return result.get()


if __name__ == "__main__":
    # For testing the tasks directly
    print("🧪 Testing periodic SEO injection tasks")

    # Test health check
    print("\n1. Testing SEO health check...")
    health_result = trigger_seo_health_check()
    print(f"Health check result: {health_result}")

    # Test periodic injection (dry run)
    print("\n2. Testing periodic SEO injection (dry run)...")
    injection_result = trigger_periodic_seo_injection(batch_size=5, dry_run=True)
    print(f"Injection result: {injection_result}")

    print("\n✅ Testing completed!")
