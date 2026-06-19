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
import json
import re
import unicodedata
import logging
import hashlib
from urllib.parse import urljoin
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

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

from models import Album, BrandIdentity
# Import unified settings with fallback for different import contexts
try:
    from .unified_settings import get_unified_settings
except ImportError:
    from seo_injector.unified_settings import get_unified_settings

# Enhanced SEO Configuration
@dataclass
class SEOConfig:
    """Configuration for SEO injection."""
    batch_size: int = 50
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = True
    enable_ai_analysis: bool = True
    enable_quality_validation: bool = True
    enable_progress_tracking: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300

@dataclass
class SEOStats:
    """Statistics for SEO injection process."""
    total_items: int = 0
    processed_items: int = 0
    updated_items: int = 0
    skipped_items: int = 0
    error_items: int = 0
    locked_items: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0

@dataclass
class ContentFingerprint:
    """Content fingerprint for change detection."""
    content_hash: str
    last_modified: datetime
    seo_version: int = 1

class SmartContentAnalyzer:
    """AI-powered content analysis for better SEO generation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """Analyze content and extract SEO-relevant information."""
        try:
            # Basic content analysis
            word_count = len(content.split())
            char_count = len(content)
            sentence_count = content.count('.') + content.count('!') + content.count('?')
            
            # Extract keywords (simple implementation)
            keywords = self._extract_keywords(content, title)
            
            # Calculate readability score
            readability_score = self._calculate_readability(content)
            
            # Extract key phrases
            key_phrases = self._extract_key_phrases(content)
            
            # Detect content type
            content_type = self._detect_content_type(content)
            
            return {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': sentence_count,
                'keywords': keywords,
                'readability_score': readability_score,
                'key_phrases': key_phrases,
                'content_type': content_type,
                'quality_score': self._calculate_quality_score(content, word_count, readability_score)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing content: {e}")
            return {
                'word_count': len(content.split()),
                'char_count': len(content),
                'sentence_count': 0,
                'keywords': [],
                'readability_score': 50,
                'key_phrases': [],
                'content_type': 'unknown',
                'quality_score': 50
            }
    
    def _extract_keywords(self, content: str, title: str = "") -> List[str]:
        """Extract keywords from content."""
        import re
        from collections import Counter
        
        # Combine title and content
        text = f"{title} {content}".lower()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        words = [word for word in words if word not in stop_words]
        
        # Count frequency and return top keywords
        word_counts = Counter(words)
        return [word for word, count in word_counts.most_common(10)]
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (0-100)."""
        try:
            sentences = content.split('.')
            words = content.split()
            
            if len(sentences) == 0 or len(words) == 0:
                return 50.0
            
            avg_words_per_sentence = len(words) / len(sentences)
            
            # Simple readability calculation
            if avg_words_per_sentence <= 15:
                return 80.0
            elif avg_words_per_sentence <= 20:
                return 60.0
            else:
                return 40.0
        except:
            return 50.0
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content."""
        import re
        from collections import Counter
        
        # Extract 2-3 word phrases
        phrases = re.findall(r'\b\w+\s+\w+\b', content.lower())
        phrase_counts = Counter(phrases)
        
        return [phrase for phrase, count in phrase_counts.most_common(5)]
    
    def _detect_content_type(self, content: str) -> str:
        """Detect the type of content."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['story', 'novel', 'chapter', 'episode', 'part']):
            return 'story'
        elif any(word in content_lower for word in ['album', 'collection', 'series']):
            return 'album'
        elif any(word in content_lower for word in ['tutorial', 'guide', 'how to', 'step']):
            return 'tutorial'
        elif any(word in content_lower for word in ['review', 'opinion', 'analysis']):
            return 'review'
        else:
            return 'content'
    
    def _calculate_quality_score(self, content: str, word_count: int, readability_score: float) -> float:
        """Calculate overall content quality score."""
        # Base score from readability
        score = readability_score * 0.4
        
        # Word count bonus
        if word_count >= 300:
            score += 20
        elif word_count >= 150:
            score += 10
        
        # Content structure bonus
        if '#' in content:  # Has headings
            score += 10
        
        return min(100.0, max(0.0, score))

class PerformanceManager:
    """Manages performance, monitoring, and batch processing."""
    
    def __init__(self, config: SEOConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stats = SEOStats()
        self.progress_callbacks: List[Callable] = []
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback function."""
        self.progress_callbacks.append(callback)
    
    def update_progress(self, processed: int, total: int, current_item: str = ""):
        """Update progress and notify callbacks."""
        self.stats.processed_items = processed
        
        for callback in self.progress_callbacks:
            try:
                callback(processed, total, current_item)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {e}")
    
    def process_batch(self, items: List[Any], processor_func: Callable) -> List[Any]:
        """Process items in batches with progress tracking."""
        results = []
        total_items = len(items)
        
        for i in range(0, total_items, self.config.batch_size):
            batch = items[i:i + self.config.batch_size]
            batch_results = []
            
            # Process batch with threading if configured
            if self.config.max_workers > 1:
                with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                    future_to_item = {
                        executor.submit(processor_func, item): item 
                        for item in batch
                    }
                    
                    for future in as_completed(future_to_item):
                        try:
                            result = future.result(timeout=self.config.timeout_seconds)
                            batch_results.append(result)
                        except Exception as e:
                            self.logger.error(f"Error processing item: {e}")
                            batch_results.append({'error': str(e)})
            else:
                # Sequential processing
                for item in batch:
                    try:
                        result = processor_func(item)
                        batch_results.append(result)
                    except Exception as e:
                        self.logger.error(f"Error processing item: {e}")
                        batch_results.append({'error': str(e)})
            
            results.extend(batch_results)
            
            # Update progress
            processed = min(i + self.config.batch_size, total_items)
            self.update_progress(processed, total_items)
        
        return results
    
    def get_stats(self) -> SEOStats:
        """Get current statistics."""
        if self.stats.start_time and self.stats.end_time:
            self.stats.duration_seconds = (self.stats.end_time - self.stats.start_time).total_seconds()
        return self.stats

class QualityValidator:
    """Validates SEO data quality and consistency."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_seo_data(self, seo_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate SEO data quality."""
        issues = []
        
        # Check meta description
        if 'meta_description' in seo_data:
            desc = seo_data['meta_description']
            if not desc or len(desc.strip()) == 0:
                issues.append("Meta description is empty")
            elif len(desc) > 160:
                issues.append(f"Meta description too long ({len(desc)} chars, max 160)")
            elif len(desc) < 50:
                issues.append(f"Meta description too short ({len(desc)} chars, min 50)")
        
        # Check meta keywords
        if 'meta_keywords' in seo_data:
            keywords = seo_data['meta_keywords']
            if not keywords or len(keywords.strip()) == 0:
                issues.append("Meta keywords is empty")
            elif len(keywords) > 255:
                issues.append(f"Meta keywords too long ({len(keywords)} chars, max 255)")
        
        # Check OG title
        if 'og_title' in seo_data:
            og_title = seo_data['og_title']
            if not og_title or len(og_title.strip()) == 0:
                issues.append("OG title is empty")
            elif len(og_title) > 200:
                issues.append(f"OG title too long ({len(og_title)} chars, max 200)")
        
        # Check OG description
        if 'og_description' in seo_data:
            og_desc = seo_data['og_description']
            if not og_desc or len(og_desc.strip()) == 0:
                issues.append("OG description is empty")
            elif len(og_desc) > 500:
                issues.append(f"OG description too long ({len(og_desc)} chars, max 500)")
        
        # Check SEO slug
        if 'seo_slug' in seo_data:
            slug = seo_data['seo_slug']
            if not slug or len(slug.strip()) == 0:
                issues.append("SEO slug is empty")
            elif not self._is_valid_slug(slug):
                issues.append(f"Invalid SEO slug format: {slug}")
        
        return len(issues) == 0, issues
    
    def _is_valid_slug(self, slug: str) -> bool:
        """Check if slug is valid."""
        import re
        # Slug should contain only lowercase letters, numbers, and hyphens
        return bool(re.match(r'^[a-z0-9-]+$', slug))
    
    def suggest_improvements(self, seo_data: Dict[str, Any]) -> List[str]:
        """Suggest improvements for SEO data."""
        suggestions = []
        
        # Meta description suggestions
        if 'meta_description' in seo_data:
            desc = seo_data['meta_description']
            if desc and len(desc) < 120:
                suggestions.append("Consider expanding meta description for better search visibility")
        
        # Keyword suggestions
        if 'meta_keywords' in seo_data:
            keywords = seo_data['meta_keywords']
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(',')]
                if len(keyword_list) < 3:
                    suggestions.append("Consider adding more relevant keywords")
                elif len(keyword_list) > 10:
                    suggestions.append("Consider reducing keywords to focus on the most important ones")
        
        return suggestions

class EnhancedAlbumSEOInjector:
    """Enhanced album SEO injector with smart features."""
    
    def __init__(self, config: Optional[SEOConfig] = None):
        self.config = config or SEOConfig()
        self.logger = logging.getLogger(__name__)
        self.analyzer = SmartContentAnalyzer()
        self.performance_manager = PerformanceManager(self.config)
        self.validator = QualityValidator()
        self.cache: Dict[str, ContentFingerprint] = {}
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info("🎯 Enhanced Album SEO Injector initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/seo_injection.log')
            ]
        )
    
    def _generate_content_fingerprint(self, item: Album) -> ContentFingerprint:
        """Generate content fingerprint for change detection."""
        content = getattr(item, 'description', '') + getattr(item, 'title', '')
        content_hash = hashlib.md5(content.encode()).hexdigest()
        last_modified = getattr(item, 'updated_at', datetime.now(timezone.utc))
        
        return ContentFingerprint(
            content_hash=content_hash,
            last_modified=last_modified,
            seo_version=1
        )
    
    def _has_content_changed(self, item: Album) -> bool:
        """Check if content has changed since last SEO injection."""
        if not self.config.enable_caching:
            return True
        
        current_fingerprint = self._generate_content_fingerprint(item)
        item_id = getattr(item, 'id', None)
        
        if item_id in self.cache:
            cached_fingerprint = self.cache[item_id]
            return (current_fingerprint.content_hash != cached_fingerprint.content_hash or
                    current_fingerprint.last_modified > cached_fingerprint.last_modified)
        
        return True
    
    def _update_cache(self, item: Album):
        """Update cache with current fingerprint."""
        if self.config.enable_caching:
            item_id = getattr(item, 'id', None)
            if item_id:
                self.cache[item_id] = self._generate_content_fingerprint(item)
    
    def get_content_items(self) -> List[Album]:
        """Get albums to process."""
        try:
            with app.app_context():
                # Get albums that need SEO processing
                albums = Album.query.filter(
                    Album.title.isnot(None)
                ).all()
                
                self.logger.info(f"📚 Found {len(albums)} albums to process")
                return albums
                
        except Exception as e:
            self.logger.error(f"Error getting albums: {e}")
            return []
    
    def process_item(self, item: Album) -> Dict[str, Any]:
        """Process a single album."""
        try:
            self.logger.info(f"📚 Processing: {item.title}")
            
            # Analyze content
            content_analysis = self.analyzer.analyze_content(item.description or '', item.title)
            
            # Generate SEO data using existing functions
            seo_data = self._generate_seo_data(item, content_analysis)
            
            # Validate SEO data
            is_valid, issues = self.validator.validate_seo_data(seo_data)
            if not is_valid:
                self.logger.warning(f"SEO validation issues: {issues}")
                # Try to fix common issues
                seo_data = self._fix_seo_issues(seo_data, issues)
            
            # Update the item
            success = self.update_item_seo(item, seo_data)
            
            if success:
                return {
                    'status': 'success',
                    'item_id': item.id,
                    'title': item.title,
                    'seo_data': seo_data,
                    'content_analysis': content_analysis
                }
            else:
                return {
                    'status': 'error',
                    'item_id': item.id,
                    'title': item.title,
                    'error': 'Failed to update SEO data'
                }
                
        except Exception as e:
            self.logger.error(f"Error processing album {item.id}: {e}")
            return {
                'status': 'error',
                'item_id': item.id,
                'title': getattr(item, 'title', 'Unknown'),
                'error': str(e)
            }
    
    def update_item_seo(self, item: Album, seo_data: Dict[str, Any]) -> bool:
        """Update SEO data for an album."""
        try:
            with app.app_context():
                # Clear existing SEO data if not locked
                if not item.is_seo_lock:
                    self._clear_existing_seo(item)
                
                # Update SEO fields
                item.meta_title = seo_data.get('meta_title', '')
                item.meta_description = seo_data.get('meta_description', '')
                item.meta_keywords = seo_data.get('meta_keywords', '')
                item.og_title = seo_data.get('og_title', '')
                item.og_description = seo_data.get('og_description', '')
                item.og_image = seo_data.get('og_image', '')
                item.canonical_url = seo_data.get('canonical_url', '')
                item.seo_slug = seo_data.get('seo_slug', '')
                item.schema_markup = seo_data.get('schema_markup', '')
                item.twitter_card = seo_data.get('twitter_card', 'summary')
                item.twitter_title = seo_data.get('twitter_title', '')
                item.twitter_description = seo_data.get('twitter_description', '')
                item.meta_author = seo_data.get('meta_author', '')
                item.meta_language = seo_data.get('meta_language', 'id')
                item.meta_robots = seo_data.get('meta_robots', 'index, follow')
                item.structured_data_type = seo_data.get('structured_data_type', 'Book')
                item.seo_score = seo_data.get('seo_score', 0)
                item.last_seo_audit = datetime.now(timezone.utc)
                
                # Commit changes with retry logic for SQLite locking
                max_retries = 3
                retry_delay = 0.1
                for attempt in range(max_retries):
                    try:
                        db.session.commit()
                        break
                    except Exception as commit_error:
                        if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                            self.logger.warning(f"Database locked, retrying commit for album {item.id} (attempt {attempt + 1})")
                            db.session.rollback()
                            import time
                            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            # Refresh the item object
                            item = Album.query.get(item.id)
                            if not item:
                                raise ValueError(f"Album item {item.id} not found after rollback")
                        else:
                            raise commit_error
                
                self.logger.info(f"✅ Updated SEO data for: {item.title}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating SEO data for album {item.id}: {e}")
            db.session.rollback()
            return False
    
    def _generate_seo_data(self, item: Album, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO data for an album using existing functions."""
        try:
            # Get unified settings for template application
            unified_settings = get_unified_settings()
            seo_settings = get_seo_settings()
            
            # Generate meta title using template
            album_title_template = seo_settings.get('album_meta_title', '{title} - {brand_name}')
            brand_name = unified_settings.get_brand_name()
            
            # Apply template for meta title
            variables = {
                'title': item.title,
                'category': item.category.name if item.category else '',
                'brand_name': brand_name
            }
            
            meta_title = unified_settings.apply_template(album_title_template, variables)
            if not meta_title or meta_title == album_title_template:
                meta_title = f"{item.title} - {brand_name}"
            
            # Use existing functions to generate SEO data
            seo_data = {
                'meta_title': meta_title,
                'meta_description': generate_meta_description(item),
                'meta_keywords': generate_meta_keywords(item),
                'og_title': generate_open_graph_data(item)[0],
                'og_description': generate_open_graph_data(item)[1],
                'og_image': generate_open_graph_data(item)[2],
                'seo_slug': generate_seo_slug(item.title),
                'canonical_url': f"{get_website_url()}/album/{item.id}",
                'schema_markup': generate_schema_markup(item),
                'twitter_card': 'summary_large_image',
                'twitter_title': generate_open_graph_data(item)[0],
                'twitter_description': generate_open_graph_data(item)[1],
                'meta_author': item.creator_user.get_full_name() if item.creator_user else 'Unknown',
                'meta_language': 'id',
                'meta_robots': 'index, follow',
                'structured_data_type': 'Book' if item.is_completed else 'CreativeWork',
                'seo_score': calculate_seo_score(item)
            }
            
            return seo_data
            
        except Exception as e:
            self.logger.error(f"Error generating SEO data: {e}")
            return {}
    
    def _clear_existing_seo(self, item: Album):
        """Clear existing SEO data."""
        item.meta_title = None
        item.meta_description = None
        item.meta_keywords = None
        item.og_title = None
        item.og_description = None
        item.og_image = None
        item.canonical_url = None
        item.seo_slug = None
        item.schema_markup = None
        item.twitter_card = None
        item.twitter_title = None
        item.twitter_description = None
        item.meta_author = None
        item.meta_language = None
        item.meta_robots = None
        item.structured_data_type = None
        item.seo_score = None
        item.last_seo_audit = None
    
    def _fix_seo_issues(self, seo_data: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """Fix common SEO issues."""
        fixed_data = seo_data.copy()
        
        for issue in issues:
            if "Meta description too long" in issue:
                desc = fixed_data.get('meta_description', '')
                if len(desc) > 160:
                    fixed_data['meta_description'] = desc[:157] + '...'
            
            elif "Meta description too short" in issue:
                desc = fixed_data.get('meta_description', '')
                if len(desc) < 50:
                    # Try to expand with more content
                    fixed_data['meta_description'] = desc + " - " + get_unified_settings().get_brand_name()
            
            elif "OG title too long" in issue:
                title = fixed_data.get('og_title', '')
                if len(title) > 200:
                    fixed_data['og_title'] = title[:197] + '...'
            
            elif "Invalid SEO slug format" in issue:
                title = fixed_data.get('title', '')
                fixed_data['seo_slug'] = generate_seo_slug(title)
        
        return fixed_data
    
    def run_injection(self) -> Dict[str, Any]:
        """Run the complete SEO injection process."""
        self.logger.info("🚀 Starting enhanced SEO injection...")
        
        try:
            # Get content items
            items = self.get_content_items()
            self.performance_manager.stats.total_items = len(items)
            self.performance_manager.stats.start_time = datetime.now(timezone.utc)
            
            if not items:
                self.logger.info("No items found to process")
                return {'status': 'completed', 'message': 'No items to process'}
            
            self.logger.info(f"📊 Found {len(items)} items to process")
            
            # Process items
            results = self.performance_manager.process_batch(items, self._process_single_item)
            
            # Calculate final statistics
            self.performance_manager.stats.end_time = datetime.now(timezone.utc)
            stats = self.performance_manager.get_stats()
            
            # Generate summary
            summary = self._generate_summary(results, stats)
            
            self.logger.info("✅ SEO injection completed successfully")
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error during SEO injection: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'stats': self.performance_manager.get_stats()
            }
    
    def _process_single_item(self, item: Album) -> Dict[str, Any]:
        """Process a single item with enhanced features."""
        try:
            # Check if content has changed
            if not self._has_content_changed(item):
                self.performance_manager.stats.skipped_items += 1
                return {'status': 'skipped', 'reason': 'content_unchanged'}
            
            # Check if SEO is locked
            if hasattr(item, 'is_seo_lock') and item.is_seo_lock:
                self.performance_manager.stats.locked_items += 1
                return {'status': 'skipped', 'reason': 'seo_locked'}
            
            # Process the item
            result = self.process_item(item)
            
            if result.get('status') == 'success':
                self.performance_manager.stats.updated_items += 1
                self._update_cache(item)
            else:
                self.performance_manager.stats.error_items += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing item: {e}")
            self.performance_manager.stats.error_items += 1
            return {'status': 'error', 'error': str(e)}
    
    def _generate_summary(self, results: List[Dict], stats: SEOStats) -> Dict[str, Any]:
        """Generate summary of the injection process."""
        return {
            'status': 'completed',
            'message': f'SEO injection completed in {stats.duration_seconds:.2f} seconds',
            'stats': {
                'total_items': stats.total_items,
                'processed_items': stats.processed_items,
                'updated_items': stats.updated_items,
                'skipped_items': stats.skipped_items,
                'error_items': stats.error_items,
                'locked_items': stats.locked_items,
                'duration_seconds': stats.duration_seconds,
                'start_time': stats.start_time.isoformat() if stats.start_time else None,
                'end_time': stats.end_time.isoformat() if stats.end_time else None
            },
            'results': results
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        try:
            with app.app_context():
                total_albums = Album.query.count()
                with_meta_desc = Album.query.filter(Album.meta_description.isnot(None)).count()
                with_meta_keywords = Album.query.filter(Album.meta_keywords.isnot(None)).count()
                with_seo_slug = Album.query.filter(Album.seo_slug.isnot(None)).count()
                with_og_title = Album.query.filter(Album.og_title.isnot(None)).count()
                with_schema = Album.query.filter(Album.schema_markup.isnot(None)).count()
                locked = Album.query.filter(Album.is_seo_lock == True).count()
                
                return {
                    'status': 'success',
                    'stats': {
                        'total_albums': total_albums,
                        'with_meta_description': with_meta_desc,
                        'with_meta_keywords': with_meta_keywords,
                        'with_seo_slug': with_seo_slug,
                        'with_og_title': with_og_title,
                        'with_schema_markup': with_schema,
                        'seo_locked': locked,
                        'percentages': {
                            'meta_description': (with_meta_desc / total_albums * 100) if total_albums > 0 else 0,
                            'meta_keywords': (with_meta_keywords / total_albums * 100) if total_albums > 0 else 0,
                            'seo_slug': (with_seo_slug / total_albums * 100) if total_albums > 0 else 0,
                            'og_title': (with_og_title / total_albums * 100) if total_albums > 0 else 0,
                            'schema_markup': (with_schema / total_albums * 100) if total_albums > 0 else 0,
                            'seo_locked': (locked / total_albums * 100) if total_albums > 0 else 0
                        }
                    }
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

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
        'album_meta_title': settings.get_template('album_meta_title', '{title} - {brand_name}'),
        'album_meta_description': settings.get_template('album_meta_description', 'Discover {title} - a captivating story with {chapter_count} chapters. Read online for free on {brand_name}.'),
        'album_meta_keywords': settings.get_template('album_meta_keywords', '{category}, {title_keywords}, story, novel, {brand_name}'),
        'album_og_title': settings.get_template('album_og_title', '{title} - {brand_name}')
    }

def get_website_url(brand_info=None, settings=None):
    """Get website URL from unified settings."""
    unified_settings = get_unified_settings()
    return unified_settings.get_website_url()

def get_best_image_for_seo(album):
    """Get the best image for SEO from album."""
    # Check if album has a cover image
    if album.cover_image:
        if album.cover_image.url:
            return normalize_image_url(album.cover_image.url)
        elif album.cover_image.filepath:
            return normalize_image_url(album.cover_image.filepath)
    
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

def generate_schema_markup(album):
    """Generate JSON-LD structured data for the album."""
    # Get actual settings from database
    seo_settings = get_seo_injection_settings()
    website_url = seo_settings['website_url']
    organization_name = seo_settings['organization_name']
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Book" if album.is_completed else "CreativeWork",
        "name": album.title,
        "description": album.description or album.title,
        "author": {
            "@type": "Person",
            "name": album.creator_user.get_full_name() if album.creator_user else "Unknown Author"
        },
        "publisher": {
            "@type": "Organization",
            "name": organization_name,
            "url": website_url
        },
        "datePublished": album.created_at.isoformat() if album.created_at else None,
        "dateModified": album.updated_at.isoformat() if album.updated_at else None,
        "numberOfPages": album.total_chapters,
        "isAccessibleForFree": not album.is_premium,
        "inLanguage": seo_settings['website_language'],
        "genre": album.category.name if album.category else None,
        "url": f"{website_url}/album/{album.id}",
    }
    
    # Add book-specific properties if completed
    if album.is_completed:
        schema["bookFormat"] = "Digital"
        schema["isbn"] = f"ALBUM-{album.id:06d}"
    
    # Add image if available
    image_url = get_best_image_for_seo(album)
    if image_url:
        schema["image"] = {
            "@type": "ImageObject",
            "url": image_url,
            "width": 800,
            "height": 600
        }
    
    return json.dumps(schema, ensure_ascii=False)

def calculate_seo_score(album):
    """Calculate SEO score for the album (0-100)."""
    score = 0
    
    # Basic SEO elements (40 points)
    if album.title and len(album.title.strip()) > 0:
        score += 10
    if album.description and len(album.description.strip()) > 0:
        score += 10
    if album.meta_description and len(album.meta_description.strip()) > 0:
        score += 10
    if album.meta_keywords and len(album.meta_keywords.strip()) > 0:
        score += 10
    
    # Social media optimization (30 points)
    if album.og_title and len(album.og_title.strip()) > 0:
        score += 10
    if album.og_description and len(album.og_description.strip()) > 0:
        score += 10
    if album.og_image and len(album.og_image.strip()) > 0:
        score += 10
    
    # Advanced SEO elements (30 points)
    if album.seo_slug and len(album.seo_slug.strip()) > 0:
        score += 10
    if album.canonical_url and len(album.canonical_url.strip()) > 0:
        score += 10
    if album.schema_markup and len(album.schema_markup.strip()) > 0:
        score += 10
    
    return min(score, 100)

def generate_meta_description(album):
    """Generate meta description from album content."""
    if album.description:
        # Use description if available, limit to 160 characters
        desc = album.description.strip()
        if len(desc) > 160:
            desc = desc[:157] + "..."
        return desc
    else:
        # Generate from title and category
        parts = [album.title]
        if album.category:
            parts.append(f"Category: {album.category.name}")
        if album.total_chapters > 0:
            parts.append(f"{album.total_chapters} chapters")
        
        desc = " - ".join(parts)
        if len(desc) > 160:
            desc = desc[:157] + "..."
        return desc

def generate_meta_keywords(album):
    """Generate meta keywords from album content using smart configuration."""
    try:
        # Import smart config manager
        try:
            from .smart_config import SmartConfigManager
        except ImportError:
            from seo_injector.smart_config import SmartConfigManager

        # Initialize smart config manager
        config_manager = SmartConfigManager()

        # Prepare content data for smart keyword generation
        content_data = {
            'title': album.title or '',
            'description': album.description or '',
            'author': album.author or '',
            'category': album.category.name.lower() if album.category else '',
            'chapter_count': album.total_chapters or 0,
            'date_published': album.created_at.isoformat() if album.created_at else '',
            'date_modified': album.updated_at.isoformat() if album.updated_at else '',
            'language': 'id',
            'canonical_url': f"/album/{album.seo_slug}" if hasattr(album, 'seo_slug') and album.seo_slug else f"/album/{album.id}",
            'website_name': config_manager.settings.website_name,
            'organization_name': config_manager.settings.organization_name
        }

        # Add content type indicators
        content_text = f"{album.title or ''} {album.description or ''}"
        if album.is_completed:
            content_text += ' completed finished story'
        else:
            content_text += ' ongoing in-progress story'

        if album.is_premium:
            content_text += ' premium exclusive content'

        content_data['content'] = content_text

        # Generate smart keywords
        seo_data = config_manager.generate_seo_data('album', content_data)

        return seo_data.get('meta_keywords', '')

    except Exception as e:
        print(f"Warning: Smart keyword generation failed, falling back to basic generation: {e}")

        # Fallback to basic keyword generation
        return _generate_basic_album_keywords(album)

def _generate_basic_album_keywords(album):
    """Fallback basic keyword generation for albums."""
    keywords = []

    # Add title words
    if album.title:
        title_words = [word.lower() for word in album.title.split() if len(word) > 2]
        keywords.extend(title_words[:5])

    # Add category
    if album.category:
        keywords.append(album.category.name.lower())

    # Add content type
    if album.is_completed:
        keywords.extend(["completed", "finished"])
    else:
        keywords.extend(["ongoing", "in-progress"])

    # Add premium status
    if album.is_premium:
        keywords.append("premium")

    # Add genre-related keywords
    if album.category:
        category_keywords = {
            "Novel": ["novel", "fiction", "story"],
            "Comic": ["comic", "manga", "graphic"],
            "Poetry": ["poetry", "poem", "verse"],
            "Article": ["article", "blog", "content"],
            "News": ["news", "current", "update"]
        }
        keywords.extend(category_keywords.get(album.category.name, []))

    # Remove duplicates and limit
    unique_keywords = list(dict.fromkeys(keywords))[:10]
    return ", ".join(unique_keywords)

def generate_open_graph_data(album):
    """Generate Open Graph data for the album."""
    og_title = album.og_title or album.title
    og_description = album.og_description or generate_meta_description(album)
    og_image = album.og_image
    
    if not og_image:
        og_image = get_best_image_for_seo(album)
    
    return og_title, og_description, og_image

def clear_existing_seo(album):
    """Clear all existing SEO data from album."""
    print(f"   🗑️ Clearing existing SEO data...")
    
    # Clear all SEO fields
    album.meta_description = None
    album.meta_keywords = None
    album.og_title = None
    album.og_description = None
    album.og_image = None
    album.canonical_url = None
    album.seo_slug = None
    album.schema_markup = None
    album.twitter_card = None
    album.twitter_title = None
    album.twitter_description = None
    album.twitter_image = None
    album.meta_author = None
    album.meta_language = None
    album.meta_robots = None
    album.structured_data_type = None
    album.seo_score = None
    album.last_seo_audit = None
    album.is_seo_lock = False  # Reset lock to false

def inject_album_seo():
    """Inject SEO data for albums that don't have SEO fields populated."""
    print("🎯 LilyOpenCMS Album SEO Injector")
    print("=" * 50)
    
    with app.app_context():
        # Get all albums
        albums = Album.query.all()
        print(f"📚 Found {len(albums)} albums in database")
        
        if not albums:
            print("❌ No albums found in database")
            return
        
        # Track statistics
        updated_count = 0
        error_count = 0
        locked_count = 0
        
        print(f"\n🔍 Analyzing albums for SEO injection...")
        
        for i, album in enumerate(albums, 1):
            print(f"\n📖 [{i}/{len(albums)}] Processing: {album.title}")
            
            try:
                # Check if SEO is locked
                if album.is_seo_lock:
                    print(f"   🔒 Skipping - SEO is locked")
                    locked_count += 1
                    continue
                
                # Clear existing SEO data first (force clean injection)
                clear_existing_seo(album)
                
                # Generate SEO data within no_autoflush context to prevent database locks
                print(f"   🔧 Generating SEO data...")

                # Use no_autoflush context to prevent database locks during lazy loading
                from models import db
                with db.session.no_autoflush:
                    # Generate SEO slug
                    album.seo_slug = generate_seo_slug(album.title)
                    print(f"   ✅ Generated SEO slug: {album.seo_slug}")

                    # Generate meta title using template
                    seo_settings = get_seo_settings()
                    album_title_template = seo_settings.get('album_meta_title', '{title} - {brand_name}')

                    # Get brand name from unified settings
                    unified_settings = get_unified_settings()
                    brand_name = unified_settings.get_brand_name()

                    # Apply template for meta title
                    variables = {
                        'title': album.title,
                        'category': album.category.name if album.category else '',
                        'brand_name': brand_name
                    }

                    album.meta_title = unified_settings.apply_template(album_title_template, variables)
                    if not album.meta_title or album.meta_title == album_title_template:
                        album.meta_title = f"{album.title} - {brand_name}"
                    print(f"   ✅ Generated meta title: {album.meta_title}")

                    # Generate meta description
                    album.meta_description = generate_meta_description(album)
                    print(f"   ✅ Generated meta description: {album.meta_description[:50]}...")

                    # Generate meta keywords
                    album.meta_keywords = generate_meta_keywords(album)
                    print(f"   ✅ Generated meta keywords: {album.meta_keywords}")

                    # Generate Open Graph data
                    og_title, og_description, og_image = generate_open_graph_data(album)

                    album.og_title = og_title
                    print(f"   ✅ Generated OG title: {album.og_title}")

                    album.og_description = og_description
                    print(f"   ✅ Generated OG description: {album.og_description[:50]}...")

                    album.og_image = og_image
                    print(f"   ✅ Set OG image: {album.og_image}")

                    # Generate schema markup
                    album.schema_markup = generate_schema_markup(album)
                    print(f"   ✅ Generated schema markup")
                
                # Get website URL for canonical URL
                brand_info = BrandIdentity.query.first()
                seo_settings = get_seo_settings()
                website_url = get_website_url(brand_info, seo_settings)
                
                # Set default values
                album.meta_author = album.creator_user.get_full_name() if album.creator_user else "Unknown Author"
                album.meta_language = "id"
                album.meta_robots = "index, follow"
                album.twitter_card = "summary_large_image"
                album.structured_data_type = "Book" if album.is_completed else "CreativeWork"
                album.canonical_url = f"{website_url}/album/{album.id}"
                
                # Calculate SEO score
                album.seo_score = calculate_seo_score(album)
                album.last_seo_audit = datetime.now(timezone.utc)
                
                print(f"   📊 SEO Score: {album.seo_score}/100")
                
                # Save to database with retry logic for SQLite locking
                max_retries = 3
                retry_delay = 0.1
                for attempt in range(max_retries):
                    try:
                        db.session.commit()
                        break
                    except Exception as commit_error:
                        if "database is locked" in str(commit_error).lower() and attempt < max_retries - 1:
                            print(f"   🔄 Database locked, retrying commit for album {album.id} (attempt {attempt + 1})")
                            db.session.rollback()
                            import time
                            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            # Refresh the album object
                            album = Album.query.get(album.id)
                            if not album:
                                raise ValueError(f"Album {album.id} not found after rollback")
                        else:
                            raise commit_error
                print(f"   ✅ Successfully updated SEO data")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing album: {e}")
                db.session.rollback()
                error_count += 1
        
        # Final summary
        print("\n" + "=" * 50)
        print("📊 ALBUM SEO INJECTION SUMMARY")
        print("=" * 50)
        print(f"✅ Successfully updated: {updated_count} albums")
        print(f"🔒 Skipped (SEO locked): {locked_count} albums")
        print(f"❌ Errors: {error_count} albums")
        print(f"📚 Total albums processed: {len(albums)}")
        
        if updated_count > 0:
            print(f"\n🎉 Successfully injected SEO data for {updated_count} albums!")
        elif locked_count > 0:
            print(f"\nℹ️ All albums have locked SEO ({locked_count} albums)")
        else:
            print(f"\n⚠️ No albums were updated due to errors")

def show_album_seo_stats():
    """Show statistics about album SEO data."""
    print("📊 Album SEO Statistics")
    print("=" * 30)
    
    with app.app_context():
        total_albums = Album.query.count()
        
        # Count albums with different SEO fields
        with_meta_desc = Album.query.filter(Album.meta_description.isnot(None)).count()
        with_meta_keywords = Album.query.filter(Album.meta_keywords.isnot(None)).count()
        with_seo_slug = Album.query.filter(Album.seo_slug.isnot(None)).count()
        with_og_title = Album.query.filter(Album.og_title.isnot(None)).count()
        with_schema = Album.query.filter(Album.schema_markup.isnot(None)).count()
        locked_seo = Album.query.filter_by(is_seo_lock=True).count()
        
        print(f"📚 Total albums: {total_albums}")
        print(f"📝 With meta description: {with_meta_desc}")
        print(f"🏷️ With meta keywords: {with_meta_keywords}")
        print(f"🔗 With SEO slug: {with_seo_slug}")
        print(f"📱 With OG title: {with_og_title}")
        print(f"🏗️ With schema markup: {with_schema}")
        print(f"🔒 SEO locked: {locked_seo}")
        
        # Calculate percentages
        if total_albums > 0:
            print(f"\n📊 Percentages:")
            print(f"   Meta description: {(with_meta_desc/total_albums)*100:.1f}%")
            print(f"   Meta keywords: {(with_meta_keywords/total_albums)*100:.1f}%")
            print(f"   SEO slug: {(with_seo_slug/total_albums)*100:.1f}%")
            print(f"   OG title: {(with_og_title/total_albums)*100:.1f}%")
            print(f"   Schema markup: {(with_schema/total_albums)*100:.1f}%")
            print(f"   SEO locked: {(locked_seo/total_albums)*100:.1f}%")

def main():
    """Main function to run the SEO injector."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inject SEO data for albums")
    parser.add_argument("--stats", action="store_true", help="Show SEO statistics only")
    parser.add_argument("--force", action="store_true", help="Force update even if SEO data exists")
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced features (smart analysis, batch processing, etc.)")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing (enhanced mode)")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum worker threads (enhanced mode)")
    parser.add_argument("--no-cache", action="store_true", help="Disable smart caching (enhanced mode)")
    parser.add_argument("--no-validation", action="store_true", help="Disable quality validation (enhanced mode)")
    
    args = parser.parse_args()
    
    if args.stats:
        if args.enhanced:
            # Use enhanced statistics
            injector = EnhancedAlbumSEOInjector()
            result = injector.get_statistics()
            print(json.dumps(result, indent=2))
        else:
            show_album_seo_stats()
    else:
        if args.enhanced:
            # Use enhanced injection
            config = SEOConfig(
                batch_size=args.batch_size,
                max_workers=args.max_workers,
                enable_caching=not args.no_cache,
                enable_quality_validation=not args.no_validation
            )
            
            injector = EnhancedAlbumSEOInjector(config)
            
            # Add progress callback for console output
            def progress_callback(processed, total, current_item=""):
                percentage = (processed / total * 100) if total > 0 else 0
                print(f"Progress: {processed}/{total} ({percentage:.1f}%) - {current_item}")
            
            injector.performance_manager.add_progress_callback(progress_callback)
            
            result = injector.run_injection()
            print(json.dumps(result, indent=2))
        else:
            # Use legacy injection
            inject_album_seo()

if __name__ == "__main__":
    main() 