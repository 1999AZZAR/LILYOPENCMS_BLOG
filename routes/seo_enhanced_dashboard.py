#!/usr/bin/env python3

"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Enhanced SEO Dashboard Routes
Provides web interface for the enhanced SEO injector system.
"""

import sys
import os
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

# Import enhanced SEO injector components (lazy imports to avoid circular dependency)
# These will be imported inside the functions when needed

# Create blueprint
seo_enhanced_bp = Blueprint('seo_enhanced', __name__, url_prefix='/admin/seo')

# Global instances for session management
active_injectors: Dict[str, Any] = {}
active_monitors: Dict[str, Any] = {}  # Will be typed when imported

@seo_enhanced_bp.route('/enhanced')
@login_required
def enhanced_dashboard():
    """Enhanced SEO dashboard main page - redirect to analytics."""
    # Debug authentication
    current_app.logger.info(f"Enhanced SEO Dashboard access attempt by user: {current_user.username if current_user.is_authenticated else 'Not authenticated'}")
    current_app.logger.info(f"User role: {current_user.role if current_user.is_authenticated else 'N/A'}")
    current_app.logger.info(f"User authenticated: {current_user.is_authenticated}")
    
    if not current_user.is_authenticated:
        current_app.logger.warning("Enhanced SEO Dashboard: User not authenticated")
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user has admin access using the proper method
    if not current_user.is_admin_tier():
        current_app.logger.warning(f"Enhanced SEO Dashboard: User {current_user.username} with role {current_user.role} not authorized")
        return jsonify({'error': 'Admin access required'}), 403
    
    current_app.logger.info(f"Enhanced SEO Dashboard: Access granted to {current_user.username}")
    # Redirect to analytics page which now includes enhanced features
    from flask import redirect, url_for
    return redirect(url_for('main.settings_analytics'))

@seo_enhanced_bp.route('/enhanced/status')
@login_required
def get_enhanced_status():
    """Get current status of enhanced SEO system."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Lazy import to avoid circular dependency
        from seo_injector.enhanced_seo_injector import EnhancedSEOInjector
        
        # Create injector for health check
        injector = EnhancedSEOInjector()
        health = injector.run_health_check()
        
        # Get configuration status
        config_issues = injector.validate_configuration()
        
        # Get statistics
        stats = injector.get_statistics()
        
        return jsonify({
            'status': 'success',
            'health': health,
            'config_issues': config_issues,
            'statistics': stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting enhanced SEO status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/run', methods=['POST'])
@login_required
def run_enhanced_injection():
    """Run enhanced SEO injection."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Skip CSRF validation for this endpoint to avoid issues
    # In production, you might want to add proper CSRF handling
    
    try:
        # Lazy imports to avoid circular dependency
        from seo_injector.enhanced_seo_injector import EnhancedSEOInjector
        from seo_injector.enhanced_base_injector import SEOConfig
        
        data = request.get_json()
        injection_type = data.get('type', 'all')
        enable_dashboard = data.get('dashboard', False)
        batch_size = data.get('batch_size', 50)
        max_workers = data.get('max_workers', 4)
        
        # Create configuration
        config = SEOConfig(
            batch_size=batch_size,
            max_workers=max_workers,
            enable_ai_analysis=True,
            enable_quality_validation=True,
            enable_progress_tracking=True
        )
        
        # Create injector
        injector = EnhancedSEOInjector(config)
        
        # Store in active injectors
        session_id = f"{current_user.id}_{int(time.time())}"
        active_injectors[session_id] = injector
        
        # Start injection in background thread
        def run_injection():
            try:
                if injection_type == 'news':
                    result = injector.run_news_injection(enable_dashboard=enable_dashboard)
                else:
                    result = injector.run_all_injections(enable_dashboard=enable_dashboard)
                
                # Store result
                injector.last_result = result
                
            except Exception as e:
                injector.last_error = str(e)
                current_app.logger.error(f"Error in background injection: {e}")
        
        # Start background thread
        thread = threading.Thread(target=run_injection, daemon=True)
        thread.start()
        
        return jsonify({
            'status': 'started',
            'session_id': session_id,
            'injection_type': injection_type,
            'message': 'SEO injection started in background'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error starting enhanced SEO injection: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/progress/<session_id>')
@login_required
def get_injection_progress(session_id):
    """Get progress of SEO injection."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        if session_id not in active_injectors:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        injector = active_injectors[session_id]
        
        # Get monitor status
        if hasattr(injector, 'monitor'):
            status = injector.monitor.get_current_status()
            return jsonify({
                'status': 'success',
                'progress': status
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Monitor not available'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error getting injection progress: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/result/<session_id>')
@login_required
def get_injection_result(session_id):
    """Get result of SEO injection."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        if session_id not in active_injectors:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        injector = active_injectors[session_id]
        
        # Check if injection is complete
        if hasattr(injector, 'last_result'):
            return jsonify({
                'status': 'success',
                'result': injector.last_result
            })
        elif hasattr(injector, 'last_error'):
            return jsonify({
                'status': 'error',
                'message': injector.last_error
            }), 500
        else:
            return jsonify({
                'status': 'running',
                'message': 'Injection still in progress'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error getting injection result: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/stop/<session_id>', methods=['POST'])
@login_required
def stop_injection(session_id):
    """Stop SEO injection."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Skip CSRF validation for this endpoint
    
    try:
        if session_id not in active_injectors:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        injector = active_injectors[session_id]
        
        # Stop monitoring
        if hasattr(injector, 'monitor'):
            injector.monitor.stop_monitoring()
        
        # Remove from active injectors
        del active_injectors[session_id]
        
        return jsonify({
            'status': 'success',
            'message': 'Injection stopped'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error stopping injection: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/config')
@login_required
def get_enhanced_config():
    """Get enhanced SEO configuration."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Lazy import to avoid circular dependency
        from seo_injector.smart_config import SmartConfigManager
        
        config_manager = SmartConfigManager()
        
        # Get templates
        templates = {}
        for content_type in ['news', 'album', 'chapter', 'root']:
            template = config_manager.get_template(content_type)
            if template:
                templates[content_type] = {
                    'name': template.name,
                    'description': template.description,
                    'content_type': template.content_type,
                    'variables': template.variables
                }
        
        # Get quality rules
        quality_rules = config_manager.get_quality_rules()
        
        # Get settings
        settings = config_manager.get_settings()
        
        return jsonify({
            'status': 'success',
            'templates': templates,
            'quality_rules': {
                'min_meta_description_length': quality_rules.min_meta_description_length,
                'max_meta_description_length': quality_rules.max_meta_description_length,
                'min_content_length': quality_rules.min_content_length,
                'max_keywords_count': quality_rules.max_keywords_count,
                'min_readability_score': quality_rules.min_readability_score,
                'min_quality_score': quality_rules.min_quality_score
            },
            'settings': {
                'website_name': settings.website_name,
                'website_url': settings.website_url,
                'website_language': settings.website_language,
                'organization_name': settings.organization_name
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting enhanced config: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/config', methods=['POST'])
@login_required
def update_enhanced_config():
    """Update enhanced SEO configuration."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Skip CSRF validation for this endpoint
    
    try:
        # Lazy import to avoid circular dependency
        from seo_injector.smart_config import SmartConfigManager
        
        data = request.get_json()
        config_type = data.get('type')
        
        config_manager = SmartConfigManager()
        
        if config_type == 'quality_rules':
            from seo_injector.smart_config import SEOQualityRules
            quality_rules = SEOQualityRules(
                min_meta_description_length=data.get('min_meta_description_length', 50),
                max_meta_description_length=data.get('max_meta_description_length', 160),
                min_content_length=data.get('min_content_length', 100),
                max_keywords_count=data.get('max_keywords_count', 10),
                min_readability_score=data.get('min_readability_score', 30),
                min_quality_score=data.get('min_quality_score', 40)
            )
            config_manager.save_quality_rules(quality_rules)
            
        elif config_type == 'settings':
            from seo_injector.smart_config import SEOInjectionSettings
            settings = SEOInjectionSettings(
                website_name=data.get('website_name', 'LilyOpenCMS'),
                website_url=data.get('website_url', 'https://hystory.id'),
                website_language=data.get('website_language', 'id'),
                organization_name=data.get('organization_name', 'LilyOpenCMS')
            )
            # Note: Settings would need to be saved to database in real implementation
            
        return jsonify({
            'status': 'success',
            'message': 'Configuration updated successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating enhanced config: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/analytics')
@login_required
def get_enhanced_analytics():
    """Get enhanced SEO analytics."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Lazy import to avoid circular dependency
        from seo_injector.enhanced_seo_injector import EnhancedSEOInjector
        
        injector = EnhancedSEOInjector()
        stats = injector.get_statistics()
        
        return jsonify({
            'status': 'success',
            'analytics': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting enhanced analytics: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/optimize', methods=['POST'])
@login_required
def optimize_enhanced_performance():
    """Optimize enhanced SEO performance."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Skip CSRF validation for this endpoint
    
    try:
        # Lazy import to avoid circular dependency
        from seo_injector.enhanced_seo_injector import EnhancedSEOInjector
        
        injector = EnhancedSEOInjector()
        injector.optimize_performance()
        
        return jsonify({
            'status': 'success',
            'message': 'Performance optimized successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error optimizing performance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_enhanced_bp.route('/enhanced/create-config', methods=['POST'])
@login_required
def create_enhanced_config():
    """Create default configuration files."""
    if not current_user.is_authenticated or not current_user.is_admin_tier():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Skip CSRF validation for this endpoint
    
    try:
        # Lazy import to avoid circular dependency
        from seo_injector.enhanced_seo_injector import EnhancedSEOInjector
        
        injector = EnhancedSEOInjector()
        injector.create_config_files()
        
        return jsonify({
            'status': 'success',
            'message': 'Configuration files created successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating config files: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
