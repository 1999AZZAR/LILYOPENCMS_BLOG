"""
Database Optimization Module
Handles database connection pooling, query optimization, and performance monitoring
"""

import time
import logging
from typing import Dict, List, Optional, Any
from flask import Flask, current_app
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError, SQLAlchemyError

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database optimization with connection pooling and query optimization"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.engine = None
        self.session_factory = None
        self.query_stats = {
            'total_queries': 0,
            'slow_queries': 0,
            'avg_query_time': 0,
            'connection_pool_size': 0,
            'active_connections': 0
        }
        self.optimization_config = {
            'enable_connection_pooling': True,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'enable_query_logging': True,
            'slow_query_threshold': 1.0  # seconds
        }
        
    def init_app(self, app: Flask):
        """Initialize database optimization with Flask app"""
        self.app = app
        
        # Configure connection pooling
        if self.optimization_config['enable_connection_pooling']:
            self._setup_connection_pooling()
        
        # Setup query monitoring
        if self.optimization_config['enable_query_logging']:
            self._setup_query_monitoring()
        
        # Register with app context
        app.extensions['database_optimizer'] = self
        
    def _setup_connection_pooling(self):
        """Setup database connection pooling"""
        try:
            # Get database URL from app config
            database_url = self.app.config.get('SQLALCHEMY_DATABASE_URI')
            
            if not database_url:
                logger.warning("No database URL found, skipping connection pooling")
                return
            
            # Create engine with connection pooling
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=self.optimization_config['pool_size'],
                max_overflow=self.optimization_config['max_overflow'],
                pool_timeout=self.optimization_config['pool_timeout'],
                pool_recycle=self.optimization_config['pool_recycle'],
                echo=False  # Set to True for SQL logging
            )
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            logger.info(f"Database connection pooling configured: "
                       f"pool_size={self.optimization_config['pool_size']}, "
                       f"max_overflow={self.optimization_config['max_overflow']}")
            
        except Exception as e:
            logger.error(f"Error setting up connection pooling: {e}")
    
    def _setup_query_monitoring(self):
        """Setup query performance monitoring"""
        try:
            if self.engine is None:
                logger.warning("No engine available, skipping query monitoring")
                return
                
            @event.listens_for(self.engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                context._query_start_time = time.time()
            
            @event.listens_for(self.engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                query_time = time.time() - context._query_start_time
                
                # Update query statistics
                self.query_stats['total_queries'] += 1
                self.query_stats['avg_query_time'] = (
                    (self.query_stats['avg_query_time'] * (self.query_stats['total_queries'] - 1) + query_time) 
                    / self.query_stats['total_queries']
                )
                
                # Track slow queries
                if query_time > self.optimization_config['slow_query_threshold']:
                    self.query_stats['slow_queries'] += 1
                    logger.warning(f"Slow query detected ({query_time:.3f}s): {statement[:100]}...")
                
                # Update connection pool stats
                if hasattr(self.engine, 'pool'):
                    pool = self.engine.pool
                    self.query_stats['connection_pool_size'] = pool.size()
                    self.query_stats['active_connections'] = pool.checkedin() + pool.checkedout()
            
            logger.info("Query monitoring setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up query monitoring: {e}")
    
    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if not self.engine:
            return {}
        
        try:
            pool = self.engine.pool
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            return {}
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return {
            'total_queries': self.query_stats['total_queries'],
            'slow_queries': self.query_stats['slow_queries'],
            'avg_query_time': round(self.query_stats['avg_query_time'], 3),
            'slow_query_threshold': self.optimization_config['slow_query_threshold'],
            'slow_query_percentage': round(
                (self.query_stats['slow_queries'] / max(self.query_stats['total_queries'], 1)) * 100, 2
            )
        }
    
    def optimize_query(self, query: str, params: Dict = None) -> str:
        """Basic query optimization (placeholder for more advanced optimization)"""
        # This is a simplified version - in production you'd use more sophisticated optimization
        optimized_query = query.strip()
        
        # Remove unnecessary whitespace
        import re
        optimized_query = re.sub(r'\s+', ' ', optimized_query)
        
        return optimized_query
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        try:
            if not self.engine:
                return {'status': 'not_configured'}
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            return {
                'status': 'connected',
                'database_url': str(self.engine.url).replace(
                    current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[0], 
                    '***:***@'
                ) if '@' in str(self.engine.url) else str(self.engine.url),
                'pool_stats': self.get_connection_pool_stats()
            }
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            if not self.engine:
                return {'status': 'not_configured', 'healthy': False}
            
            start_time = time.time()
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'healthy': True,
                'response_time': round(response_time, 3),
                'pool_stats': self.get_connection_pool_stats()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'healthy': False,
                'error': str(e)
            }
    
    def reset_stats(self):
        """Reset query statistics"""
        self.query_stats = {
            'total_queries': 0,
            'slow_queries': 0,
            'avg_query_time': 0,
            'connection_pool_size': 0,
            'active_connections': 0
        }
        logger.info("Database query statistics reset")

def create_database_optimizer(app: Flask) -> DatabaseOptimizer:
    """Create and configure database optimizer"""
    optimizer = DatabaseOptimizer(app)
    optimizer.init_app(app)
    return optimizer

# Query optimization functions
def optimize_news_query(query):
    """Optimize news-related queries"""
    # Add eager loading for related data
    if hasattr(query, 'options'):
        from sqlalchemy.orm import joinedload
        # Import models to use class-bound attributes
        from models import News, Category, User
        query = query.options(
            joinedload(News.category),
            joinedload(News.author)
        )
    return query

def optimize_user_query(query):
    """Optimize user-related queries"""
    # Add eager loading for user data
    if hasattr(query, 'options'):
        from sqlalchemy.orm import joinedload
        # Import models to use class-bound attributes
        from models import User, CustomRole
        query = query.options(
            joinedload(User.custom_role)
        )
    return query

def optimize_image_query(query):
    """Optimize image-related queries"""
    # Add eager loading for image data
    if hasattr(query, 'options'):
        from sqlalchemy.orm import joinedload
        # Import models to use class-bound attributes
        from models import Image, User
        query = query.options(
            joinedload(Image.user)
        )
    return query

# Database utilities
def get_database_optimizer() -> Optional[DatabaseOptimizer]:
    """Get the database optimizer instance"""
    return current_app.extensions.get('database_optimizer')

def get_db_stats() -> Dict[str, Any]:
    """Get database statistics"""
    optimizer = get_database_optimizer()
    if optimizer:
        return {
            'query_stats': optimizer.get_query_stats(),
            'pool_stats': optimizer.get_connection_pool_stats(),
            'health': optimizer.health_check()
        }
    return {'error': 'Database optimizer not configured'} 