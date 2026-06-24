"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Optimization API Routes

This module handles all optimization-related API endpoints.
"""

from routes import main_blueprint
from .common_imports import *
from flask import jsonify


# Asset Optimization API Routes
@main_blueprint.route("/api/asset-optimization/compress", methods=["POST"])
@login_required
def api_compress_assets():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.asset_optimization import compress_assets_action
        result = compress_assets_action()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error compressing assets: {str(e)}'
        }), 500


@main_blueprint.route("/api/asset-optimization/clear-cache", methods=["POST"])
@login_required
def api_clear_asset_cache():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.asset_optimization import clear_asset_cache_action
        result = clear_asset_cache_action()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing asset cache: {str(e)}'
        }), 500


@main_blueprint.route("/api/asset-optimization/regenerate-hashes", methods=["POST"])
@login_required
def api_regenerate_asset_hashes():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.asset_optimization import regenerate_hashes_action
        result = regenerate_hashes_action()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error regenerating hashes: {str(e)}'
        }), 500


# SSR Optimization API Routes
@main_blueprint.route("/api/ssr-optimization/clear-cache", methods=["POST"])
@login_required
def api_clear_ssr_cache():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.ssr_optimization import clear_ssr_cache_action
        result = clear_ssr_cache_action()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing SSR cache: {str(e)}'
        }), 500


@main_blueprint.route("/api/ssr-optimization/optimize-cache", methods=["POST"])
@login_required
def api_optimize_ssr_cache():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.ssr_optimization import optimize_ssr_cache_action
        result = optimize_ssr_cache_action()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error optimizing SSR cache: {str(e)}'
        }), 500


# Performance Optimization API Routes
@main_blueprint.route("/api/performance/clear-cache", methods=["POST"])
@login_required
def api_clear_performance_cache():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        # Clear various caches
        from optimizations.performance_monitoring import get_performance_monitor
        monitor = get_performance_monitor()
        if monitor:
            monitor.metrics.clear()
        
        return jsonify({
            'success': True,
            'message': 'Performance cache cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing performance cache: {str(e)}'
        }), 500


@main_blueprint.route("/api/performance/alerts", methods=["GET"])
@login_required
def api_get_performance_alerts():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.performance_monitoring import get_performance_monitor
        monitor = get_performance_monitor()
        if monitor:
            alerts = monitor.get_performance_alerts()
            return jsonify({
                'success': True,
                'alerts': alerts
            })
        else:
            return jsonify({
                'success': True,
                'alerts': []
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting performance alerts: {str(e)}'
        }), 500


@main_blueprint.route("/api/performance/recommendations", methods=["GET"])
@login_required
def api_get_performance_recommendations():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.performance_monitoring import get_performance_monitor
        monitor = get_performance_monitor()
        if monitor:
            recommendations = monitor.get_performance_recommendations()
            return jsonify({
                'success': True,
                'recommendations': recommendations
            })
        else:
            return jsonify({
                'success': True,
                'recommendations': []
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting performance recommendations: {str(e)}'
        }), 500


@main_blueprint.route("/api/ssr-optimization/cache-template", methods=["POST"])
@login_required
def api_cache_template():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        template_content = data.get('template_content')
        context = data.get('context', {})
        
        from optimizations.ssr_optimization import get_ssr_optimizer
        optimizer = get_ssr_optimizer()
        
        success = optimizer.cache_template(template_name, template_content, context)
        
        return jsonify({
            'success': success,
            'message': 'Template cached successfully' if success else 'Failed to cache template'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error caching template: {str(e)}'
        }), 500


@main_blueprint.route("/api/asset-optimization/minify", methods=["POST"])
@login_required
def api_minify_assets():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        from optimizations.asset_optimization import get_asset_optimizer
        optimizer = get_asset_optimizer()
        
        # This will trigger the enhanced compression with minification
        result = optimizer.compress_assets()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error minifying assets: {str(e)}'
        }), 500


# Cache Management API Routes
@main_blueprint.route("/api/cache/status", methods=["GET"])
@login_required
def api_get_cache_status():
    """Get cache status and statistics"""
    if not current_user.has_permission("settings", "read"):
        abort(403)
    
    try:
        # Try to get cache status from optimizations module
        try:
            from optimizations.cache_config import cache
            
            # Get Redis connection info
            redis_client = cache.cache._client
            info = redis_client.info()
            
            # Calculate cache statistics
            total_keys = info.get('db0', {}).get('keys', 0)
            memory_usage = info.get('used_memory_human', '0B')
            hit_rate = info.get('keyspace_hits', 0)
            miss_rate = info.get('keyspace_misses', 0)
            total_requests = hit_rate + miss_rate
            
            if total_requests > 0:
                hit_percentage = (hit_rate / total_requests) * 100
                miss_percentage = (miss_rate / total_requests) * 100
            else:
                hit_percentage = 0
                miss_percentage = 0
            
            return jsonify({
                'success': True,
                'cache_status': {
                    'total_keys': total_keys,
                    'memory_usage': memory_usage,
                    'hit_rate': round(hit_percentage, 1),
                    'miss_rate': round(miss_percentage, 1),
                    'total_requests': total_requests,
                    'hit_count': hit_rate,
                    'miss_count': miss_rate
                }
            })
        except ImportError:
            # Fallback if cache module is not available
            return jsonify({
                'success': True,
                'cache_status': {
                    'total_keys': 0,
                    'memory_usage': '0B',
                    'hit_rate': 0.0,
                    'miss_rate': 0.0,
                    'total_requests': 0,
                    'hit_count': 0,
                    'miss_count': 0,
                    'status': 'Cache module not available'
                }
            })
        except Exception as cache_error:
            # Fallback if Redis is not available
            return jsonify({
                'success': False,
                'message': f'Error getting cache status: {str(cache_error)}',
                'cache_status': {
                    'total_keys': 0,
                    'memory_usage': '0B',
                    'hit_rate': 0.0,
                    'miss_rate': 0.0,
                    'total_requests': 0,
                    'hit_count': 0,
                    'miss_count': 0,
                    'status': f'Cache not available: {str(cache_error)}'
                }
            }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting cache status: {str(e)}'
        }), 500


@main_blueprint.route("/api/cache/clear", methods=["POST"])
@login_required
def api_clear_cache():
    """Clear all cache"""
    if not current_user.has_permission("settings", "write"):
        abort(403)
    
    try:
        try:
            from optimizations.cache_config import clear_all_cache
            success = clear_all_cache()
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Cache cleared successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to clear cache (Redis unavailable or error)'
                }), 503
        except ImportError:
            return jsonify({
                'success': True,
                'message': 'Cache module not available - no cache to clear'
            })
        except Exception as cache_error:
            return jsonify({
                'success': False,
                'message': f'Error clearing cache: {str(cache_error)}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing cache: {str(e)}'
        }), 500


@main_blueprint.route("/api/cache/invalidate/<pattern>", methods=["POST"])
@login_required
def api_invalidate_cache_pattern(pattern):
    """Invalidate cache by pattern"""
    if not current_user.has_permission("settings", "write"):
        abort(403)
    
    try:
        try:
            from optimizations.cache_config import invalidate_cache_pattern
            success = invalidate_cache_pattern(pattern)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Cache pattern "{pattern}" invalidated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Failed to invalidate cache pattern "{pattern}" (Redis unavailable or error)'
                }), 503
        except ImportError:
            return jsonify({
                'success': True,
                'message': f'Cache module not available - pattern "{pattern}" not invalidated'
            })
        except Exception as cache_error:
            return jsonify({
                'success': False,
                'message': f'Error invalidating cache: {str(cache_error)}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error invalidating cache: {str(e)}'
        }), 500


@main_blueprint.route("/api/cache/keys", methods=["GET"])
@login_required
def api_get_cache_keys():
    """Get cache keys with pattern matching"""
    if not current_user.has_permission("settings", "read"):
        abort(403)
    
    try:
        try:
            from optimizations.cache_config import cache
            pattern = request.args.get('pattern', '*')
            
            # Get keys matching pattern
            keys = cache.cache._client.keys(f"lilycms_{pattern}")
            key_info = []
            
            for key in keys[:100]:  # Limit to 100 keys for performance
                key_str = key.decode('utf-8')
                ttl = cache.cache._client.ttl(key)
                key_info.append({
                    'key': key_str,
                    'ttl': ttl if ttl > 0 else 'No TTL'
                })
            
            return jsonify({
                'success': True,
                'keys': key_info,
                'total_keys': len(keys)
            })
        except ImportError:
            return jsonify({
                'success': True,
                'keys': [],
                'total_keys': 0,
                'message': 'Cache module not available'
            })
        except Exception as cache_error:
            return jsonify({
                'success': True,
                'keys': [],
                'total_keys': 0,
                'message': f'Cache not available: {str(cache_error)}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting cache keys: {str(e)}'
        }), 500


# Database Management API Routes
@main_blueprint.route("/api/database/status", methods=["GET"])
@login_required
def api_get_database_status():
    """Get database status and statistics"""
    if not current_user.has_permission("settings", "read"):
        abort(403)
    
    try:
        from sqlalchemy import text
        from models import db, User, News, Image, YouTubeVideo, UserActivity, CustomRole, Permission
        import os
        
        # Get database statistics
        stats = {}
        detailed_stats = {}
        
        # Get table counts and detailed information
        tables = {
            'users': User,
            'news': News,
            'images': Image,
            'youtube_videos': YouTubeVideo,
            'user_activities': UserActivity,
            'custom_roles': CustomRole,
            'permissions': Permission
        }
        
        total_records = 0
        for table_name, model in tables.items():
            try:
                count = db.session.query(model).count()
                stats[table_name] = count
                total_records += count
                
                # Get detailed stats for each table
                detailed_stats[table_name] = {
                    'count': count,
                    'size_estimate': f"{count * 1024} bytes" if count > 0 else "0 bytes"
                }
                
                # Get additional stats for specific tables
                if table_name == 'users':
                    active_users = db.session.query(User).filter(User.is_suspended == False).count()
                    suspended_users = db.session.query(User).filter(User.is_suspended == True).count()
                    detailed_stats[table_name].update({
                        'active_users': active_users,
                        'suspended_users': suspended_users,
                        'admin_users': db.session.query(User).filter(User.role.in_(['admin', 'superuser'])).count()
                    })
                elif table_name == 'news':
                    published_news = db.session.query(News).filter(News.is_published == True).count()
                    draft_news = db.session.query(News).filter(News.is_published == False).count()
                    detailed_stats[table_name].update({
                        'published': published_news,
                        'drafts': draft_news,
                        'featured': db.session.query(News).filter(News.is_featured == True).count()
                    })
                elif table_name == 'user_activities':
                    recent_activities = db.session.query(UserActivity).order_by(UserActivity.timestamp.desc()).limit(5).count()
                    detailed_stats[table_name].update({
                        'recent_activities': recent_activities
                    })
                    
            except Exception as e:
                stats[table_name] = 0
                detailed_stats[table_name] = {'error': str(e)}
        
        # Get database file size (for SQLite)
        db_size = "Unknown"
        try:
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if db_path and os.path.exists(db_path):
                db_size = f"{os.path.getsize(db_path)} bytes"
            else:
                # Try to get size from SQLite
                db.session.execute(text("PRAGMA page_count * PRAGMA page_size"))
                page_count = db.session.execute(text("PRAGMA page_count")).fetchone()[0]
                page_size = db.session.execute(text("PRAGMA page_size")).fetchone()[0]
                db_size = f"{page_count * page_size} bytes"
        except Exception:
            db_size = "Unknown"
        
        # Get database performance info
        performance_info = {
            'slow_queries': 0,  # SQLite doesn't have this
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Get database integrity info
        try:
            integrity_check = db.session.execute(text("PRAGMA integrity_check")).fetchone()[0]
            integrity_status = "OK" if integrity_check == "ok" else integrity_check
        except Exception:
            integrity_status = "Unknown"
        
        return jsonify({
            'success': True,
            'database_status': {
                'tables': stats,
                'detailed_stats': detailed_stats,
                'database_size': db_size,
                'total_records': total_records,
                'performance': performance_info,
                'integrity': integrity_status,
                'database_type': 'SQLite',
                'last_updated': 'Now'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting database status: {str(e)}'
        }), 500


@main_blueprint.route("/api/database/optimize", methods=["POST"])
@login_required
def api_optimize_database():
    """Optimize database tables"""
    if not current_user.has_permission("settings", "write"):
        abort(403)
    
    try:
        from sqlalchemy import text
        from models import db
        
        # Get tables to optimize
        tables = ['users', 'news', 'images', 'youtube_videos', 'user_activities', 'custom_roles', 'permissions']
        optimized_tables = []
        
        for table in tables:
            try:
                # Analyze table
                db.session.execute(text(f"ANALYZE {table}"))
                optimized_tables.append(table)
            except Exception as e:
                current_app.logger.error(f"Error optimizing table {table}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Database optimized successfully. Tables: {", ".join(optimized_tables)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error optimizing database: {str(e)}'
        }), 500


@main_blueprint.route("/api/database/cleanup", methods=["POST"])
@login_required
def api_cleanup_database():
    """Clean up old data and optimize database"""
    if not current_user.has_permission("settings", "write"):
        abort(403)
    
    try:
        from sqlalchemy import text
        from models import db
        from datetime import datetime, timedelta
        
        cleanup_stats = {}
        
        # Clean up old user activities (older than 30 days)
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            result = db.session.execute(text("""
                DELETE FROM user_activities 
                WHERE created_at < :cutoff_date
            """), {'cutoff_date': cutoff_date})
            cleanup_stats['old_activities'] = result.rowcount
        except Exception as e:
            current_app.logger.error(f"Error cleaning up old activities: {e}")
            cleanup_stats['old_activities'] = 0
        
        # Clean up orphaned images
        try:
            from models import Image, News
            orphaned_images = db.session.query(Image).filter(
                ~Image.news_id.in_(db.session.query(News.id))
            ).delete()
            cleanup_stats['orphaned_images'] = orphaned_images
        except Exception as e:
            current_app.logger.error(f"Error cleaning orphaned images: {e}")
            cleanup_stats['orphaned_images'] = 0
        
        # VACUUM database
        try:
            db.session.execute(text("VACUUM"))
            cleanup_stats['vacuum'] = True
        except Exception as e:
            current_app.logger.error(f"Error during VACUUM: {e}")
            cleanup_stats['vacuum'] = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Database cleanup completed successfully',
            'cleanup_stats': cleanup_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error cleaning up database: {str(e)}'
        }), 500


@main_blueprint.route("/api/database/backup", methods=["POST"])
@login_required
def api_backup_database():
    """Create database backup"""
    if not current_user.has_permission("settings", "write"):
        abort(403)
    
    try:
        import os
        import shutil
        from datetime import datetime
        
        # Get database path
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            return jsonify({
                'success': False,
                'message': 'Backup only supported for SQLite databases'
            }), 400
        
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'message': 'Database file not found'
            }), 404
        
        # Create backup directory
        backup_dir = os.path.join(current_app.root_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"database_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Get backup file size
        backup_size = os.path.getsize(backup_path)
        
        return jsonify({
            'success': True,
            'message': 'Database backup created successfully',
            'backup_info': {
                'filename': backup_filename,
                'path': backup_path,
                'size': f"{backup_size} bytes",
                'created_at': timestamp
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating database backup: {str(e)}'
        }), 500


@main_blueprint.route("/api/database/backups", methods=["GET"])
@login_required
def api_list_backups():
    """List available database backups"""
    if not current_user.has_permission("settings", "read"):
        abort(403)
    
    try:
        import os
        from datetime import datetime
        
        backup_dir = os.path.join(current_app.root_path, 'backups')
        backups = []
        
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.endswith('.db') and filename.startswith('database_backup_'):
                    file_path = os.path.join(backup_dir, filename)
                    file_stat = os.stat(file_path)
                    
                    backups.append({
                        'filename': filename,
                        'size': f"{file_stat.st_size} bytes",
                        'created_at': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        'path': file_path
                    })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'backups': backups,
            'total_backups': len(backups)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing backups: {str(e)}'
        }), 500


# System Management API Routes
@main_blueprint.route("/api/system/status", methods=["GET"])
@login_required
def api_get_system_status():
    """Get system status and metrics"""
    if not current_user.has_permission("settings", "read"):
        abort(403)
    
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network stats
        network = psutil.net_io_counters()
        
        # Get process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return jsonify({
            'success': True,
            'system_status': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': round(disk.percent, 1),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'network_sent_mb': round(network.bytes_sent / (1024**2), 2),
                'network_recv_mb': round(network.bytes_recv / (1024**2), 2),
                'process_memory_mb': round(process_memory.rss / (1024**2), 2)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting system status: {str(e)}'
        }), 500


@main_blueprint.route("/api/performance/summary", methods=["GET"])
@login_required
def api_get_performance_summary():
    """Get performance summary for dashboard"""
    if not current_user.has_permission("settings", "read"):
        abort(403)
    
    try:
        from optimizations.performance_monitoring import get_performance_summary
        summary = get_performance_summary()
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting performance summary: {str(e)}'
        }), 500
