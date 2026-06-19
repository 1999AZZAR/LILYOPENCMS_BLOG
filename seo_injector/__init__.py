"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
SEO Injector Package for LilyOpenCMS
Provides enhanced SEO injection capabilities for news, albums, chapters, and root pages.
"""

# Import main classes for easy access
from .seo_injector import SEOInjector
from .unified_settings import get_unified_settings

# Import enhanced classes
try:
    from .enhanced_news_injector import EnhancedNewsSEOInjector
    from .enhanced_seo_injector import EnhancedSEOInjector
except ImportError:
    # Enhanced classes may not be available in all environments
    pass

__version__ = "1.0.0"
__author__ = "LilyOpenCMS Team"
__description__ = "Enhanced SEO injection system for LilyOpenCMS"
