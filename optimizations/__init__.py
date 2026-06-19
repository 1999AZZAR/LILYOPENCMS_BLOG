"""
Performance Optimizations Package
Comprehensive performance optimization modules for LilyOpenCMS
"""

from .cache_config import (
    cache,
    init_cache,
    cache_with_args,
    cache_query_result,
    generate_cache_key,
    invalidate_cache_pattern,
    clear_all_cache,
    CACHE_TIMEOUTS,
    CACHE_PATTERNS
)

from .database_optimization import (
    DatabaseOptimizer,
    create_database_optimizer,
    optimize_news_query,
    optimize_user_query,
    optimize_image_query
)

from .frontend_optimization import (
    FrontendOptimizer,
    create_frontend_optimizer,
    get_optimized_image_url,
    generate_image_srcset,
    get_lazy_loading_script,
    get_performance_monitoring_script
)

from .performance_monitoring import (
    PerformanceMonitor,
    create_performance_monitor,
    get_performance_monitor,
    monitor_performance,
    track_database_queries
)

from .asset_optimization import (
    AssetOptimizer,
    get_asset_optimizer,
    get_asset_stats,
    compress_assets_action,
    clear_asset_cache_action,
    regenerate_hashes_action
)

from .query_caching import (
    QueryCache,
    cache_query_result,
    cache_aggregation_result,
    invalidate_cache_pattern,
    cache_news_queries,
    cache_user_queries,
    cache_analytics_queries
)

from .ssr_optimization import (
    SSROptimizer,
    get_ssr_optimizer,
    get_ssr_stats,
    clear_ssr_cache_action,
    optimize_ssr_cache_action,
    monitor_ssr_render
)

__version__ = "1.0.0"
__author__ = "LilyOpenCMS Team"

# Convenience imports for common use cases
__all__ = [
    # Cache utilities
    'cache',
    'init_cache',
    'cache_with_args',
    'cache_query_result',
    'invalidate_cache_pattern',
    'clear_all_cache',
    'CACHE_TIMEOUTS',
    
    # Database optimization
    'DatabaseOptimizer',
    'create_database_optimizer',
    'optimize_news_query',
    'optimize_user_query',
    'optimize_image_query',
    
    # Frontend optimization
    'FrontendOptimizer',
    'create_frontend_optimizer',
    'get_lazy_loading_script',
    'get_performance_monitoring_script',
    
    # Performance monitoring
    'PerformanceMonitor',
    'create_performance_monitor',
    'get_performance_monitor',
    'monitor_performance',
    'track_database_queries',
    
    # Asset optimization
    'AssetOptimizer',
    'get_asset_optimizer',
    'get_asset_stats',
    'compress_assets_action',
    'clear_asset_cache_action',
    'regenerate_hashes_action',
    
    # Query caching
    'QueryCache',
    'cache_query_result',
    'cache_aggregation_result',
    'cache_news_queries',
    'cache_user_queries',
    'cache_analytics_queries',
    
    # SSR optimization
    'SSROptimizer',
    'get_ssr_optimizer',
    'get_ssr_stats',
    'clear_ssr_cache_action',
    'optimize_ssr_cache_action',
    'monitor_ssr_render'
] 