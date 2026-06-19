# Performance Optimizations Package

This package contains comprehensive performance optimization modules for LilyOpenCMS.

## 📁 Package Structure

```
optimizations/
├── __init__.py              # Package initialization and exports
├── cache_config.py          # Redis caching configuration and utilities
├── database_optimization.py # Database optimization and connection pooling
├── frontend_optimization.py # Frontend optimization utilities
├── performance_monitoring.py # Performance monitoring system
├── setup_redis.sh          # Redis installation script
└── README.md               # This file
```

## 🚀 Quick Start

### Installation

```python
# Import the entire package
from optimizations import *

# Or import specific modules
from optimizations import cache_with_args, optimize_news_query
```

### Basic Usage

```python
# Initialize optimizations in your Flask app
from optimizations import init_cache, create_database_optimizer, create_frontend_optimizer

init_cache(app)
db_optimizer = create_database_optimizer(app)
frontend_optimizer = create_frontend_optimizer(app)

# Use caching decorators
@cache_with_args(timeout=300, key_prefix='home')
def home():
    return render_template('home.html')

# Optimize database queries
news_query = News.query.filter_by(is_visible=True)
optimized_query = optimize_news_query(news_query)
news_list = optimized_query.all()
```

## 📦 Module Overview

### cache_config.py
Redis caching configuration and utilities.

**Key Features:**
- Redis connection management
- Cache decorators for functions and queries
- Smart cache invalidation patterns
- Configurable cache timeouts

**Usage:**
```python
from optimizations import cache_with_args, invalidate_cache_pattern

@cache_with_args(timeout=300, key_prefix='news')
def get_news():
    return News.query.all()

# Invalidate cache
invalidate_cache_pattern('news')
```

### database_optimization.py
Database optimization and connection pooling.

**Key Features:**
- Connection pooling configuration
- Automatic database indexing
- Query optimization with eager loading
- Slow query detection

**Usage:**
```python
from optimizations import optimize_news_query, create_database_optimizer

# Initialize database optimizer
db_optimizer = create_database_optimizer(app)

# Optimize queries
news_query = News.query.filter_by(is_visible=True)
optimized_query = optimize_news_query(news_query, include_author=True)
```

### frontend_optimization.py
Frontend optimization utilities.

**Key Features:**
- Asset versioning for cache busting
- Lazy loading image generation
- Progressive image loading
- Template filters and globals

**Usage:**
```python
from optimizations import create_frontend_optimizer

# Initialize frontend optimizer
frontend_optimizer = create_frontend_optimizer(app)

# Use in templates
# {{ 'css/style.css'|asset_version }}
# {{ image.url|lazy_image }}
```

### performance_monitoring.py
Performance monitoring system.

**Key Features:**
- Real-time request monitoring
- System resource tracking
- Performance metrics collection
- Slow query detection

**Usage:**
```python
from optimizations import create_performance_monitor, monitor_performance

# Initialize performance monitor
performance_monitor = create_performance_monitor(app)

# Monitor function performance
@monitor_performance(timeout=1.0)
def slow_function():
    pass
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Performance Settings
FLASK_ENV=production
```

### Redis Setup

Use the provided setup script:

```bash
chmod +x optimizations/setup_redis.sh
./optimizations/setup_redis.sh
```

## 📊 Performance Dashboard

Access the performance dashboard at `/admin/performance` to monitor:

- System metrics (CPU, Memory, Disk)
- Route performance statistics
- Slow query identification
- Cache management tools

## 🎯 Best Practices

### Caching Strategy
```python
# Cache frequently accessed, rarely changed content
@cache_with_args(timeout=1800, key_prefix='categories')  # 30 minutes
def get_categories():
    return Category.query.all()

# Cache user-specific content with shorter timeouts
@cache_with_args(timeout=300, key_prefix='user_data')    # 5 minutes
def get_user_data(user_id):
    return User.query.get(user_id)
```

### Database Optimization
```python
# Use eager loading to prevent N+1 queries
news_query = News.query.filter_by(is_visible=True)
optimized_query = optimize_news_query(news_query, include_author=True, include_category=True)

# Use pagination for large datasets
paginated_results = db_optimizer.get_paginated_results(news_query, page=1, per_page=20)
```

### Frontend Optimization
```html
<!-- Use lazy loading for images -->
<img src="/static/pic/placeholder.png" 
     data-src="{{ image.url }}" 
     alt="{{ image.description }}" 
     class="lazy" 
     loading="lazy">

<!-- Use progressive loading for responsive images -->
<img src="{{ image.url }}" 
     srcset="{{ image.url }}?w=300 300w, {{ image.url }}?w=600 600w"
     sizes="(max-width: 768px) 100vw, 50vw"
     alt="{{ image.description }}" 
     class="progressive" 
     loading="lazy">
```

## 🔍 Monitoring and Debugging

### Performance Monitoring
```python
from optimizations import get_performance_monitor

# Get performance summary
monitor = get_performance_monitor()
summary = monitor.get_performance_summary()
slow_queries = monitor.get_slow_queries(threshold=1.0)
```

### Cache Debugging
```python
from optimizations import cache

# Test cache connection
cache.set('test', 'value', timeout=60)
result = cache.get('test')
print(f"Cache test: {result}")

# Clear all cache
from optimizations import clear_all_cache
clear_all_cache()
```

## 📚 Documentation

- [Performance Optimization Guide](../docs/PERFORMANCE_OPTIMIZATION.md)
- [Quick Start Guide](../docs/PERFORMANCE_QUICK_START.md)
- [Main TODO List](../docs/TODO.md)

## 🆘 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   redis-cli ping
   # Should return PONG
   ```

2. **Cache Not Working**
   ```python
   from optimizations import cache
   cache.set('test', 'value', timeout=60)
   result = cache.get('test')
   print(f"Cache test: {result}")
   ```

3. **Slow Performance**
   - Check the performance dashboard
   - Review database indexes
   - Monitor cache hit rates

## 📈 Expected Improvements

- **Page Load Time**: 50-70% reduction
- **Database Queries**: 60-80% reduction through caching
- **Image Loading**: 40-60% improvement with lazy loading
- **Memory Usage**: 30-50% reduction with optimized queries

---

*This optimization package provides a comprehensive solution for improving LilyOpenCMS performance and scalability.* 