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
import json
from datetime import datetime, timezone

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

from models import BrandIdentity
from sqlalchemy import text

class UnifiedSEOSettings:
    """Unified SEO settings loader that checks multiple sources."""
    
    def __init__(self):
        self._settings = None
        self._brand_info = None
        self._seo_injection_settings = None
        self._brand_seo_settings = None
        
    def _load_brand_info(self):
        """Load brand identity information."""
        if self._brand_info is None:
            try:
                self._brand_info = BrandIdentity.query.first()
            except Exception as e:
                print(f"Warning: Could not load brand identity: {e}")
                self._brand_info = None
        return self._brand_info
    
    def _load_seo_injection_settings(self):
        """Load SEO injection settings from database table."""
        if self._seo_injection_settings is None:
            try:
                result = db.session.execute(text('''
                    SELECT website_name, website_url, website_description, website_language, 
                           organization_name, organization_logo, organization_description,
                           default_meta_language, default_meta_robots, default_og_title, 
                           default_twitter_card, default_og_image, default_twitter_title
                    FROM seo_injection_settings LIMIT 1
                '''))
                row = result.fetchone()
                if row:
                    self._seo_injection_settings = {
                        'website_name': row[0],
                        'website_url': row[1],
                        'website_description': row[2],
                        'website_language': row[3],
                        'organization_name': row[4],
                        'organization_logo': row[5],
                        'organization_description': row[6],
                        'default_meta_language': row[7],
                        'default_meta_robots': row[8],
                        'default_og_title': row[9],
                        'default_twitter_card': row[10],
                        'default_og_image': row[11],
                        'default_twitter_title': row[12]
                    }
                else:
                    self._seo_injection_settings = {}
            except Exception as e:
                print(f"Warning: Could not load SEO injection settings: {e}")
                self._seo_injection_settings = {}
        return self._seo_injection_settings
    
    def _load_brand_seo_settings(self):
        """Load SEO settings from BrandIdentity.seo_settings field."""
        if self._brand_seo_settings is None:
            try:
                brand_info = self._load_brand_info()
                if brand_info and brand_info.seo_settings:
                    if isinstance(brand_info.seo_settings, dict):
                        self._brand_seo_settings = brand_info.seo_settings
                    else:
                        try:
                            self._brand_seo_settings = json.loads(brand_info.seo_settings) if isinstance(brand_info.seo_settings, str) else {}
                        except:
                            self._brand_seo_settings = {}
                else:
                    self._brand_seo_settings = {}
            except Exception as e:
                print(f"Warning: Could not load brand SEO settings: {e}")
                self._brand_seo_settings = {}
        return self._brand_seo_settings
    
    def get_setting(self, key, default=None):
        """Get a setting value from the unified settings."""
        if self._settings is None:
            self._load_all_settings()
        
        return self._settings.get(key, default)
    
    def _load_all_settings(self):
        """Load all settings from all sources and merge them."""
        # Load from all sources
        seo_injection = self._load_seo_injection_settings()
        brand_seo = self._load_brand_seo_settings()
        brand_info = self._load_brand_info()
        
        # Start with Hystory.id defaults - everything else should come from settings
        self._settings = {
            # Hystory.id brand defaults
            'website_name': 'Hystory',
            'website_url': 'https://hystory.id',
            'website_description': 'Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi.',
            'website_language': 'id',
            'organization_name': 'Hystory',
            'organization_logo': 'https://hystory.id/static/pic/logo.png',
            'organization_description': 'Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi.',

            # Default SEO settings
            'default_meta_language': 'id',
            'default_meta_robots': 'index, follow',
            'default_og_title': 'website',
            'default_twitter_card': 'summary_large_image',
            'default_og_image': 'https://hystory.id/static/pic/logo.png',
            'default_twitter_title': '',

            # Auto injection settings
            'auto_inject_articles': True,
            'auto_inject_albums': True,
            'auto_inject_chapters': True,
            'enable_seo_lock': False,
            'lock_after_injection': False,
            'batch_size': 20,
            'delay_between_batches': 100,
        }
        
        # Override with SEO injection settings (highest priority)
        for key, value in seo_injection.items():
            if value is not None and value != '':
                self._settings[key] = value
        
        # Override with brand SEO settings (medium priority)
        for key, value in brand_seo.items():
            if value is not None and value != '':
                self._settings[key] = value
        
        # Override with brand info (lowest priority)
        if brand_info:
            if brand_info.brand_name:
                self._settings['website_name'] = brand_info.brand_name
                self._settings['organization_name'] = brand_info.brand_name
            if brand_info.website_url:
                self._settings['website_url'] = brand_info.website_url
            if brand_info.tagline:
                self._settings['website_description'] = brand_info.tagline
    
    def apply_template(self, template, variables):
        """Apply variables to a template string."""
        if not template:
            return ""
        
        result = template
        for key, value in variables.items():
            if value:
                result = result.replace(f"{{{key}}}", str(value))
        
        return result
    
    def get_website_url(self):
        """Get the website URL."""
        return self.get_setting('website_url', 'https://hystory.id')
    
    def get_brand_name(self):
        """Get the brand name."""
        return self.get_setting('website_name', 'LilyOpenCMS')
    
    def get_organization_name(self):
        """Get the organization name."""
        return self.get_setting('organization_name', 'LilyOpenCMS')
    
    def get_default_language(self):
        """Get the default language."""
        return self.get_setting('default_meta_language', 'id')
    
    def get_default_meta_robots(self):
        """Get the default meta robots."""
        return self.get_setting('default_meta_robots', 'index, follow')
    
    def get_default_og_type(self):
        """Get the default Open Graph type."""
        return self.get_setting('default_og_title', 'website')
    
    def get_default_twitter_card(self):
        """Get the default Twitter card type."""
        return self.get_setting('default_twitter_card', 'summary_large_image')
    
    def get_default_og_image(self):
        """Get the default Open Graph image."""
        return self.get_setting('default_og_image', '')
    
    def get_default_twitter_image(self):
        """Get the default Twitter image."""
        return self.get_setting('default_twitter_title', '')
    
    def get_template(self, template_key, default=None):
        """Get a template by key."""
        return self.get_setting(template_key, default)
    
    def is_auto_inject_enabled(self, content_type):
        """Check if auto injection is enabled for a content type."""
        return self.get_setting(f'auto_inject_{content_type}', True)
    
    def is_seo_lock_enabled(self):
        """Check if SEO lock is enabled."""
        return self.get_setting('enable_seo_lock', False)
    
    def should_lock_after_injection(self):
        """Check if content should be locked after injection."""
        return self.get_setting('lock_after_injection', False)
    
    def get_batch_size(self):
        """Get the batch size for processing."""
        return self.get_setting('batch_size', 20)
    
    def get_delay_between_batches(self):
        """Get the delay between batches in milliseconds."""
        return self.get_setting('delay_between_batches', 100)

# Global instance
unified_settings = UnifiedSEOSettings()

def get_unified_settings():
    """Get the global unified settings instance."""
    return unified_settings
