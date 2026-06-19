"""
Performance Routes

This module handles performance monitoring, asset optimization, and SSR optimization routes.
"""

from routes import main_blueprint
from .common_imports import *


@main_blueprint.route("/settings/performance")
@login_required
def settings_performance():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    # Get performance data from optimizations
    try:
        from optimizations.performance_monitoring import get_performance_summary
        performance_summary = get_performance_summary()
    except Exception:
        # Provide comprehensive fallback data if optimization module fails
        import psutil
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent == 0:
                cpu_percent = psutil.cpu_percent(interval=0.1)
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                load_avg = (0.0, 0.0, 0.0)
            
            process = psutil.Process()
            process_memory = process.memory_info()
            
            try:
                active_connections = len(psutil.net_connections())
            except (psutil.AccessDenied, psutil.ZombieProcess):
                active_connections = 0
            
            performance_summary = {
                'system': {
                    'cpu_percent': round(cpu_percent, 1),
                    'memory_percent': round(memory.percent, 1),
                    'memory_used_gb': round(memory.used / (1024**3), 2),
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_percent': round(disk.percent, 1),
                    'disk_used_gb': round(disk.used / (1024**3), 2),
                    'disk_total_gb': round(disk.total / (1024**3), 2),
                    'disk_free_gb': round(disk.free / (1024**3), 2),
                    'load_avg_1min': round(load_avg[0], 2),
                    'load_avg_5min': round(load_avg[1], 2),
                    'load_avg_15min': round(load_avg[2], 2),
                    'network_bytes_sent_mb': round(network.bytes_sent / (1024**2), 2),
                    'network_bytes_recv_mb': round(network.bytes_recv / (1024**2), 2),
                    'process_memory_mb': round(process_memory.rss / (1024**2), 2),
                    'uptime_seconds': 0,
                    'active_connections': active_connections
                },
                'database': {
                    'query_count': 0,
                    'avg_query_time': 0,
                    'slow_queries': 0
                },
                'cache': {
                    'hit_rate': 0,
                    'miss_rate': 0,
                    'total_requests': 0
                },
                'total_requests': 0,
                'routes': {}
            }
        except Exception:
            # Ultimate fallback if even psutil fails
            performance_summary = {
                'system': {
                    'cpu_percent': 0,
                    'memory_percent': 0,
                    'memory_used_gb': 0,
                    'memory_total_gb': 0,
                    'memory_available_gb': 0,
                    'disk_percent': 0,
                    'disk_used_gb': 0,
                    'disk_total_gb': 0,
                    'disk_free_gb': 0,
                    'load_avg_1min': 0,
                    'load_avg_5min': 0,
                    'load_avg_15min': 0,
                    'network_bytes_sent_mb': 0,
                    'network_bytes_recv_mb': 0,
                    'process_memory_mb': 0,
                    'uptime_seconds': 0,
                    'active_connections': 0
                },
                'database': {
                    'query_count': 0,
                    'avg_query_time': 0,
                    'slow_queries': 0
                },
                'cache': {
                    'hit_rate': 0,
                    'miss_rate': 0,
                    'total_requests': 0
                },
                'total_requests': 0,
                'routes': {}
            }
    
    return render_template("settings/performance_dashboard.html", performance_summary=performance_summary)


@main_blueprint.route("/settings/asset-optimization")
@login_required
def settings_asset_optimization():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    # Get asset optimization data
    try:
        from optimizations.asset_optimization import get_asset_stats
        asset_stats = get_asset_stats()
    except Exception:
        # Provide default data if optimization module fails
        asset_stats = {
            'compressed_assets_count': 0,
            'total_size_saved': 0,
            'optimization_ratio': 0,
            'recent_optimizations': []
        }
    
    return render_template("settings/asset_optimization_dashboard.html", asset_stats=asset_stats)


@main_blueprint.route("/settings/ssr-optimization")
@login_required
def settings_ssr_optimization():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    # Get SSR optimization data
    try:
        from optimizations.ssr_optimization import get_ssr_stats
        ssr_stats = get_ssr_stats()
    except Exception:
        # Provide default data if optimization module fails
        ssr_stats = {
            'total_renders': 0,
            'cache_hit_rate': 0,
            'avg_render_time': 0,
            'active_caches': 0
        }
    
    return render_template("settings/ssr_optimization_dashboard.html", ssr_stats=ssr_stats)