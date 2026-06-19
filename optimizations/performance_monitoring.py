"""
Performance Monitoring Module
Tracks application performance metrics and provides monitoring utilities
"""

import time
import logging
from functools import wraps
from flask import request, current_app, g
from datetime import datetime, timedelta
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = {}
        self.start_time = time.time()  # Add start_time for uptime calculation
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize performance monitor with app"""
        self.app = app
        
        # Register before_request and after_request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Set up periodic metrics collection
        self._setup_periodic_monitoring()
    
    def before_request(self):
        """Record request start time"""
        g.start_time = time.time()
        g.request_id = f"{int(time.time() * 1000)}_{os.getpid()}"
    
    def after_request(self, response):
        """Record request metrics"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            self._record_request_metrics(duration, response.status_code)
            
            # Log slow requests
            if duration > 1.0:
                logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
        
        return response
    
    def _record_request_metrics(self, duration, status_code):
        """Record request performance metrics"""
        path = request.path
        method = request.method
        
        if path not in self.metrics:
            self.metrics[path] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'status_codes': {},
                'last_request': None
            }
        
        metric = self.metrics[path]
        metric['count'] += 1
        metric['total_time'] += duration
        metric['avg_time'] = metric['total_time'] / metric['count']
        metric['min_time'] = min(metric['min_time'], duration)
        metric['max_time'] = max(metric['max_time'], duration)
        metric['last_request'] = datetime.now()
        
        # Record status codes
        if status_code not in metric['status_codes']:
            metric['status_codes'][status_code] = 0
        metric['status_codes'][status_code] += 1
    
    def _setup_periodic_monitoring(self):
        """Set up periodic system metrics collection"""
        def collect_system_metrics():
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_metrics = {
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available': memory.available,
                    'disk_percent': disk.percent,
                    'disk_free': disk.free
                }
                
                # Store metrics (in production, you'd send to monitoring service)
                logger.info(f"System metrics: CPU {cpu_percent}%, Memory {memory.percent}%, Disk {disk.percent}%")
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
        
        # In production, you'd use a background task scheduler
        # For now, we'll collect metrics on request
        self.collect_system_metrics = collect_system_metrics
    
    def get_performance_summary(self):
        """Get performance summary for all routes"""
        summary = {
            'total_requests': sum(m['count'] for m in self.metrics.values()),
            'routes': {},
            'system': {},
            'database': {
                'query_count': 0,
                'avg_query_time': 0,
                'slow_queries': 0
            },
            'cache': {
                'hit_rate': 0,
                'miss_rate': 0,
                'total_requests': 0
            }
        }
        
        for path, metric in self.metrics.items():
            summary['routes'][path] = {
                'count': metric['count'],
                'avg_time': metric['avg_time'],
                'min_time': metric['min_time'],
                'max_time': metric['max_time'],
                'status_codes': metric['status_codes'],
                'last_request': metric['last_request'].isoformat() if metric['last_request'] else None
            }
        
        # Add comprehensive system metrics with better error handling
        try:
            # Get CPU usage (non-blocking)
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent == 0:  # If no previous call, get a quick reading
                cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            
            # Get network stats
            network = psutil.net_io_counters()
            
            # Get load average (works on Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                # Windows doesn't have getloadavg
                load_avg = (0.0, 0.0, 0.0)
            
            # Get process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Get network connections (with error handling)
            try:
                active_connections = len(psutil.net_connections())
            except (psutil.AccessDenied, psutil.ZombieProcess):
                active_connections = 0
            
            summary['system'] = {
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
                'uptime_seconds': round(time.time() - self.start_time, 0),
                'active_connections': active_connections
            }
            
            logger.info(f"System metrics collected: CPU {cpu_percent}%, Memory {memory.percent}%, Disk {disk.percent}%")
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            # Provide fallback values
            summary['system'] = {
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
            }
        
        return summary
    
    def get_slow_queries(self, threshold=1.0):
        """Get routes with average response time above threshold"""
        slow_routes = {}
        for path, metric in self.metrics.items():
            if metric['avg_time'] > threshold:
                slow_routes[path] = {
                    'avg_time': metric['avg_time'],
                    'count': metric['count'],
                    'max_time': metric['max_time']
                }
        return slow_routes
    
    def get_performance_alerts(self):
        """Get performance alerts based on thresholds"""
        alerts = []
        
        try:
            # System alerts
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            if cpu_percent > 80:
                alerts.append({
                    'type': 'warning',
                    'message': f'High CPU usage: {cpu_percent}%',
                    'metric': 'cpu',
                    'value': cpu_percent
                })
            
            if memory.percent > 85:
                alerts.append({
                    'type': 'warning',
                    'message': f'High memory usage: {memory.percent}%',
                    'metric': 'memory',
                    'value': memory.percent
                })
            
            if disk.percent > 90:
                alerts.append({
                    'type': 'critical',
                    'message': f'Low disk space: {disk.percent}% used',
                    'metric': 'disk',
                    'value': disk.percent
                })
            
            # Route performance alerts
            for path, metric in self.metrics.items():
                if metric['avg_time'] > 2.0:
                    alerts.append({
                        'type': 'warning',
                        'message': f'Slow route: {path} (avg: {metric["avg_time"]:.2f}s)',
                        'metric': 'route_performance',
                        'value': metric['avg_time']
                    })
                
                if metric['max_time'] > 5.0:
                    alerts.append({
                        'type': 'critical',
                        'message': f'Very slow route: {path} (max: {metric["max_time"]:.2f}s)',
                        'metric': 'route_performance',
                        'value': metric['max_time']
                    })
            
            # Error rate alerts
            for path, metric in self.metrics.items():
                total_requests = sum(metric['status_codes'].values())
                error_requests = sum(count for code, count in metric['status_codes'].items() if code >= 400)
                
                if total_requests > 0 and (error_requests / total_requests) > 0.1:
                    alerts.append({
                        'type': 'critical',
                        'message': f'High error rate: {path} ({error_requests}/{total_requests} errors)',
                        'metric': 'error_rate',
                        'value': error_requests / total_requests
                    })
                    
        except Exception as e:
            logger.error(f"Error getting performance alerts: {e}")
        
        return alerts
    
    def get_performance_recommendations(self):
        """Get performance optimization recommendations"""
        recommendations = []
        
        try:
            # System recommendations
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            if cpu_percent > 70:
                recommendations.append({
                    'type': 'optimization',
                    'message': 'Consider optimizing database queries or adding caching',
                    'priority': 'high'
                })
            
            if memory.percent > 80:
                recommendations.append({
                    'type': 'optimization',
                    'message': 'Consider increasing memory or optimizing memory usage',
                    'priority': 'high'
                })
            
            # Route-specific recommendations
            for path, metric in self.metrics.items():
                if metric['avg_time'] > 1.0:
                    recommendations.append({
                        'type': 'optimization',
                        'message': f'Optimize route {path} - consider caching or database optimization',
                        'priority': 'medium'
                    })
                    
        except Exception as e:
            logger.error(f"Error getting performance recommendations: {e}")
        
        return recommendations

def monitor_performance(timeout=1.0):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > timeout:
                    logger.warning(f"Slow function {func.__name__} took {duration:.2f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Function {func.__name__} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator

def track_database_queries(func):
    """Decorator to track database query performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        query_count = 0
        
        # Count queries (this is a simplified version)
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 0.5:  # Log slow database operations
                logger.warning(f"Slow database operation in {func.__name__}: {duration:.2f}s")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Database operation {func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper

# Global performance monitor instance
performance_monitor = None

def create_performance_monitor(app):
    """Create and configure performance monitor"""
    global performance_monitor
    performance_monitor = PerformanceMonitor(app)
    return performance_monitor

def get_performance_monitor():
    """Get the global performance monitor instance"""
    return performance_monitor


def get_performance_summary():
    """Get performance summary for dashboard"""
    try:
        monitor = get_performance_monitor()
        if monitor:
            return monitor.get_performance_summary()
        else:
            # Return real system data if monitor not available
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                if cpu_percent == 0:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Get network stats
                network = psutil.net_io_counters()
                
                # Get load average (works on Unix-like systems)
                try:
                    load_avg = psutil.getloadavg()
                except AttributeError:
                    load_avg = (0.0, 0.0, 0.0)
                
                # Get process-specific metrics
                process = psutil.Process()
                process_memory = process.memory_info()
                
                return {
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
                        'uptime_seconds': 0,  # No monitor, so no uptime
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
            except Exception as e:
                logger.error(f"Error getting fallback system metrics: {e}")
                return {
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
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        return {
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