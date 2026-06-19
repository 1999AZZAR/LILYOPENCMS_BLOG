"""
Advanced Query Result Caching Module
Provides intelligent caching for database queries with automatic invalidation
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from flask import current_app, request
from sqlalchemy import text
from sqlalchemy.orm import Query
import logging
from .cache_config import safe_cache_get, safe_cache_set

logger = logging.getLogger(__name__)

class QueryCache:
    """Advanced query result caching with intelligent invalidation"""
    
    def __init__(self, cache_instance):
        self.cache = cache_instance
        self.query_patterns = {}
        self.invalidation_rules = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0
        }
        
    def cache_query(self, timeout: int = 300, key_prefix: str = 'query', 
                   invalidate_on: List[str] = None, 
                   condition: Callable = None) -> Callable:
        """
        Decorator for caching query results with intelligent invalidation
        
        Args:
            timeout: Cache timeout in seconds
            key_prefix: Prefix for cache key
            invalidate_on: List of events that should invalidate this cache
            condition: Function that returns True if query should be cached
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check if caching should be skipped
                if condition and not condition(*args, **kwargs):
                    return func(*args, **kwargs)
                
                # Generate cache key
                cache_key = self._generate_query_key(func, args, kwargs, key_prefix)
                
                # Try to get from cache
                cached_result = safe_cache_get(cache_key)
                if cached_result is not None:
                    self.cache_stats['hits'] += 1
                    logger.debug(f"Cache HIT for {cache_key}")
                    return cached_result
                
                # Cache miss - execute query
                self.cache_stats['misses'] += 1
                logger.debug(f"Cache MISS for {cache_key}")
                
                result = func(*args, **kwargs)
                
                # Cache the result
                safe_cache_set(cache_key, result, timeout=timeout)
                
                # Register invalidation rules
                if invalidate_on:
                    self._register_invalidation_rules(cache_key, invalidate_on)
                
                return result
            return wrapper
        return decorator
    
    def cache_sqlalchemy_query(self, timeout: int = 300, key_prefix: str = 'sql',
                              include_user: bool = False) -> Callable:
        """
        Decorator specifically for SQLAlchemy queries
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key including user if requested
                cache_key = self._generate_sqlalchemy_key(func, args, kwargs, key_prefix, include_user)
                
                # Try to get from cache
                cached_result = safe_cache_get(cache_key)
                if cached_result is not None:
                    self.cache_stats['hits'] += 1
                    return cached_result
                
                # Cache miss - execute query
                self.cache_stats['misses'] += 1
                result = func(*args, **kwargs)
                
                # Convert SQLAlchemy objects to dict for caching
                serializable_result = self._serialize_sqlalchemy_result(result)
                
                # Cache the result
                safe_cache_set(cache_key, serializable_result, timeout=timeout)
                
                return result
            return wrapper
        return decorator
    
    def cache_aggregation(self, timeout: int = 600, key_prefix: str = 'agg') -> Callable:
        """
        Decorator for caching aggregation queries (counts, sums, etc.)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._generate_aggregation_key(func, args, kwargs, key_prefix)
                
                cached_result = safe_cache_get(cache_key)
                if cached_result is not None:
                    self.cache_stats['hits'] += 1
                    return cached_result
                
                self.cache_stats['misses'] += 1
                result = func(*args, **kwargs)
                
                # Cache aggregation results
                safe_cache_set(cache_key, result, timeout=timeout)
                
                return result
            return wrapper
        return decorator
    
    def _generate_query_key(self, func: Callable, args: tuple, kwargs: dict, 
                           prefix: str) -> str:
        """Generate cache key for function calls"""
        # Create a unique identifier for the function call
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Create a hash of the arguments
        args_hash = hashlib.md5(
            json.dumps((args, kwargs), sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        return f"{prefix}:{func_name}:{args_hash}"
    
    def _generate_sqlalchemy_key(self, func: Callable, args: tuple, kwargs: dict,
                                prefix: str, include_user: bool) -> str:
        """Generate cache key for SQLAlchemy queries"""
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Include user ID if requested
        user_id = ""
        if include_user and hasattr(request, 'user'):
            user_id = f":user_{request.user.id}" if request.user else ""
        
        # Create hash of arguments
        args_hash = hashlib.md5(
            json.dumps((args, kwargs), sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        return f"{prefix}:{func_name}{user_id}:{args_hash}"
    
    def _generate_aggregation_key(self, func: Callable, args: tuple, kwargs: dict,
                                 prefix: str) -> str:
        """Generate cache key for aggregation queries"""
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Include current date for time-based aggregations
        date_suffix = time.strftime("%Y%m%d")
        
        args_hash = hashlib.md5(
            json.dumps((args, kwargs), sort_keys=True, default=str).encode()
        ).hexdigest()[:8]
        
        return f"{prefix}:{func_name}:{date_suffix}:{args_hash}"
    
    def _serialize_sqlalchemy_result(self, result: Any) -> Any:
        """Convert SQLAlchemy objects to serializable format"""
        if isinstance(result, list):
            return [self._serialize_sqlalchemy_object(obj) for obj in result]
        elif isinstance(result, dict):
            return {k: self._serialize_sqlalchemy_object(v) for k, v in result.items()}
        else:
            return self._serialize_sqlalchemy_object(result)
    
    def _serialize_sqlalchemy_object(self, obj: Any) -> Any:
        """Convert a single SQLAlchemy object to dict"""
        if hasattr(obj, '__table__'):
            # SQLAlchemy model object
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        elif hasattr(obj, '_asdict'):
            # SQLAlchemy Row object
            return obj._asdict()
        else:
            return obj
    
    def _register_invalidation_rules(self, cache_key: str, events: List[str]):
        """Register cache invalidation rules"""
        for event in events:
            if event not in self.invalidation_rules:
                self.invalidation_rules[event] = []
            self.invalidation_rules[event].append(cache_key)
    
    def invalidate_by_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern"""
        keys_to_delete = []
        
        # This is a simplified version - in production you'd use Redis SCAN
        # For now, we'll track patterns manually
        if pattern in self.query_patterns:
            keys_to_delete.extend(self.query_patterns[pattern])
        
        for key in keys_to_delete:
            self.cache.delete(key)
            self.cache_stats['invalidations'] += 1
        
        logger.info(f"Invalidated {len(keys_to_delete)} cache entries for pattern: {pattern}")
    
    def invalidate_by_event(self, event: str):
        """Invalidate cache entries based on events"""
        if event in self.invalidation_rules:
            keys_to_delete = self.invalidation_rules[event]
            for key in keys_to_delete:
                self.cache.delete(key)
                self.cache_stats['invalidations'] += 1
            
            logger.info(f"Invalidated {len(keys_to_delete)} cache entries for event: {event}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests > 0:
            hit_rate = (self.cache_stats['hits'] / total_requests) * 100
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'invalidations': self.cache_stats['invalidations'],
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def clear_all_query_cache(self):
        """Clear all query cache entries"""
        # In a real implementation, you'd use Redis SCAN to find all keys
        # For now, we'll clear the entire cache
        self.cache.clear()
        self.cache_stats['invalidations'] += 1
        logger.info("Cleared all query cache entries")

# Convenience functions
def cache_query_result(timeout: int = 300, key_prefix: str = 'query'):
    """Simple decorator for caching query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from optimizations import cache
            
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            args_hash = hashlib.md5(
                json.dumps((args, kwargs), sort_keys=True, default=str).encode()
            ).hexdigest()[:12]
            cache_key = f"{key_prefix}:{func_name}:{args_hash}"
            
            # Try to get from cache
            cached_result = safe_cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            safe_cache_set(cache_key, result, timeout=timeout)
            
            return result
        return wrapper
    return decorator

def cache_aggregation_result(timeout: int = 600):
    """Decorator for caching aggregation results"""
    return cache_query_result(timeout=timeout, key_prefix='agg')

def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching a pattern"""
    from optimizations import cache
    # This would need to be implemented with Redis SCAN in production
    logger.info(f"Cache invalidation requested for pattern: {pattern}")

# Example usage decorators
def cache_news_queries(timeout: int = 300):
    """Decorator specifically for news-related queries"""
    return cache_query_result(timeout=timeout, key_prefix='news')

def cache_user_queries(timeout: int = 300):
    """Decorator specifically for user-related queries"""
    return cache_query_result(timeout=timeout, key_prefix='user')

def cache_analytics_queries(timeout: int = 600):
    """Decorator specifically for analytics queries"""
    return cache_query_result(timeout=timeout, key_prefix='analytics') 