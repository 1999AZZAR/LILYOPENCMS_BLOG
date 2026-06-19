"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest, NotFound
from sqlalchemy import and_, or_
from datetime import datetime
import json

from models import db, RootSEO, User, UserRole
from routes.common_imports import *

# Create blueprint
root_seo_bp = Blueprint('root_seo', __name__)

@root_seo_bp.route('/settings/root-seo')
@login_required
def root_seo_management():
    """Main page for root SEO management."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'error')
        return redirect(url_for('main.settings_dashboard'))
    
    # Get all root SEO entries
    root_seo_entries = RootSEO.query.order_by(RootSEO.page_identifier).all()
    
    # Get statistics
    total_pages = len(root_seo_entries)
    active_pages = len([entry for entry in root_seo_entries if entry.is_active])
    complete_seo = len([entry for entry in root_seo_entries if entry.calculate_seo_score() >= 80])
    incomplete_seo = len([entry for entry in root_seo_entries if 40 <= entry.calculate_seo_score() < 80])
    missing_seo = len([entry for entry in root_seo_entries if entry.calculate_seo_score() < 40])
    
    # Calculate completion rate
    completion_rate = int((complete_seo / total_pages * 100) if total_pages > 0 else 0)
    
    return render_template('admin/seo/root_seo_management.html',
                         root_seo_entries=root_seo_entries,
                         total_pages=total_pages,
                         active_pages=active_pages,
                         complete_seo=complete_seo,
                         incomplete_seo=incomplete_seo,
                         missing_seo=missing_seo,
                         completion_rate=completion_rate)

@root_seo_bp.route('/settings/root-seo/create', methods=['GET', 'POST'])
@login_required
def create_root_seo():
    """Create a new root SEO entry."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        flash('Anda tidak memiliki izin untuk membuat pengaturan SEO.', 'error')
        return redirect(url_for('root_seo.root_seo_management'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('page_identifier'):
                return jsonify({'success': False, 'message': 'Page identifier is required'}), 400
            
            if not data.get('page_name'):
                return jsonify({'success': False, 'message': 'Page name is required'}), 400
            
            # Check if page identifier already exists
            existing = RootSEO.query.filter_by(page_identifier=data['page_identifier']).first()
            if existing:
                return jsonify({'success': False, 'message': 'Page identifier already exists'}), 400
            
            # Create new root SEO entry
            root_seo = RootSEO(
                page_identifier=data['page_identifier'],
                page_name=data['page_name'],
                is_active=data.get('is_active', True),
                meta_title=data.get('meta_title'),
                meta_description=data.get('meta_description'),
                meta_keywords=data.get('meta_keywords'),
                og_title=data.get('og_title'),
                og_description=data.get('og_description'),
                og_image=data.get('og_image'),
                og_type=data.get('og_type', 'website'),
                twitter_card=data.get('twitter_card', 'summary_large_image'),
                twitter_title=data.get('twitter_title'),
                twitter_description=data.get('twitter_description'),
                twitter_image=data.get('twitter_image'),
                canonical_url=data.get('canonical_url'),
                meta_author=data.get('meta_author'),
                meta_language=data.get('meta_language', 'id'),
                meta_robots=data.get('meta_robots', 'index, follow'),
                structured_data_type=data.get('structured_data_type'),
                schema_markup=data.get('schema_markup'),
                google_analytics_id=data.get('google_analytics_id'),
                facebook_pixel_id=data.get('facebook_pixel_id'),
                created_by=current_user.id,
                updated_by=current_user.id
            )
            
            # Validate and save
            root_seo.validate()
            root_seo.update_seo_fields()
            db.session.add(root_seo)
            db.session.commit()
            
            # Record activity (with safety check)
            try:
                if hasattr(current_user, 'record_activity'):
                    current_user.record_activity('create_root_seo', f'Created root SEO for page: {root_seo.page_name}')
            except Exception as e:
                current_app.logger.warning(f"Could not record user activity: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Root SEO berhasil dibuat',
                'data': root_seo.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error creating root SEO: {str(e)}'}), 500
    
    # TODO: Create root_seo_create.html template or redirect to appropriate page
    return redirect(url_for('root_seo.root_seo_management'))

@root_seo_bp.route('/settings/root-seo/<int:seo_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_root_seo(seo_id):
    """Get, update, or delete a specific root SEO entry."""
    root_seo = RootSEO.query.get_or_404(seo_id)
    
    if request.method == 'GET':
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
            flash('Anda tidak memiliki izin untuk melihat pengaturan SEO.', 'error')
            return redirect(url_for('root_seo.root_seo_management'))
        
        return jsonify({'success': True, 'data': root_seo.to_dict()})
    
    elif request.method == 'PUT':
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
            return jsonify({'success': False, 'message': 'Anda tidak memiliki izin untuk mengubah pengaturan SEO.'}), 403
        
        try:
            data = request.get_json()
            
            # Update fields
            if 'page_name' in data:
                root_seo.page_name = data['page_name']
            if 'is_active' in data:
                root_seo.is_active = data['is_active']
            if 'meta_title' in data:
                root_seo.meta_title = data['meta_title']
            if 'meta_description' in data:
                root_seo.meta_description = data['meta_description']
            if 'meta_keywords' in data:
                root_seo.meta_keywords = data['meta_keywords']
            if 'og_title' in data:
                root_seo.og_title = data['og_title']
            if 'og_description' in data:
                root_seo.og_description = data['og_description']
            if 'og_image' in data:
                root_seo.og_image = data['og_image']
            if 'og_type' in data:
                root_seo.og_type = data['og_type']
            if 'twitter_card' in data:
                root_seo.twitter_card = data['twitter_card']
            if 'twitter_title' in data:
                root_seo.twitter_title = data['twitter_title']
            if 'twitter_description' in data:
                root_seo.twitter_description = data['twitter_description']
            if 'twitter_image' in data:
                root_seo.twitter_image = data['twitter_image']
            if 'canonical_url' in data:
                root_seo.canonical_url = data['canonical_url']
            if 'meta_author' in data:
                root_seo.meta_author = data['meta_author']
            if 'meta_language' in data:
                root_seo.meta_language = data['meta_language']
            if 'meta_robots' in data:
                root_seo.meta_robots = data['meta_robots']
            if 'structured_data_type' in data:
                root_seo.structured_data_type = data['structured_data_type']
            if 'schema_markup' in data:
                root_seo.schema_markup = data['schema_markup']
            if 'google_analytics_id' in data:
                root_seo.google_analytics_id = data['google_analytics_id']
            if 'facebook_pixel_id' in data:
                root_seo.facebook_pixel_id = data['facebook_pixel_id']
            
            root_seo.updated_by = current_user.id
            root_seo.updated_at = datetime.utcnow()
            
            # Validate and update SEO fields
            root_seo.validate()
            root_seo.update_seo_fields()
            db.session.commit()
            
            # Record activity (with safety check)
            try:
                if hasattr(current_user, 'record_activity'):
                    current_user.record_activity('update_root_seo', f'Updated root SEO for page: {root_seo.page_name}')
            except Exception as e:
                current_app.logger.warning(f"Could not record user activity: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Root SEO berhasil diperbarui',
                'data': root_seo.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error updating root SEO: {str(e)}'}), 500
    
    elif request.method == 'DELETE':
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
            return jsonify({'success': False, 'message': 'Anda tidak memiliki izin untuk menghapus pengaturan SEO.'}), 403
        
        try:
            page_name = root_seo.page_name
            db.session.delete(root_seo)
            db.session.commit()
            
            # Record activity (with safety check)
            try:
                if hasattr(current_user, 'record_activity'):
                    current_user.record_activity('delete_root_seo', f'Deleted root SEO for page: {page_name}')
            except Exception as e:
                current_app.logger.warning(f"Could not record user activity: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Root SEO berhasil dihapus'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error deleting root SEO: {str(e)}'}), 500

@root_seo_bp.route('/settings/root-seo/bulk-update', methods=['POST'])
@login_required
def bulk_update_root_seo():
    """Bulk update root SEO entries."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        return jsonify({'success': False, 'message': 'Anda tidak memiliki izin untuk mengubah pengaturan SEO.'}), 403
    
    try:
        data = request.get_json()
        seo_ids = data.get('seo_ids', [])
        updates = data.get('updates', {})
        
        if not seo_ids:
            return jsonify({'success': False, 'message': 'No SEO entries selected'}), 400
        
        updated_count = 0
        for seo_id in seo_ids:
            root_seo = RootSEO.query.get(seo_id)
            if root_seo:
                # Apply updates
                for field, value in updates.items():
                    if hasattr(root_seo, field):
                        setattr(root_seo, field, value)
                
                root_seo.updated_by = current_user.id
                root_seo.updated_at = datetime.utcnow()
                root_seo.update_seo_fields()
                updated_count += 1
        
        db.session.commit()
        
        # Record activity (with safety check)
        try:
            if hasattr(current_user, 'record_activity'):
                current_user.record_activity('bulk_update_root_seo', f'Bulk updated {updated_count} root SEO entries')
        except Exception as e:
            current_app.logger.warning(f"Could not record user activity: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} root SEO entries berhasil diperbarui'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error bulk updating root SEO: {str(e)}'}), 500

@root_seo_bp.route('/settings/root-seo/analytics')
@login_required
def root_seo_analytics():
    """Get analytics data for root SEO."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        return jsonify({'success': False, 'message': 'Anda tidak memiliki izin untuk melihat analitik SEO.'}), 403
    
    try:
        # Get all root SEO entries
        root_seo_entries = RootSEO.query.all()
        
        # Calculate analytics
        total_pages = len(root_seo_entries)
        active_pages = len([entry for entry in root_seo_entries if entry.is_active])
        
        # SEO completion statistics
        complete_seo = len([entry for entry in root_seo_entries if entry.calculate_seo_score() >= 80])
        incomplete_seo = len([entry for entry in root_seo_entries if 40 <= entry.calculate_seo_score() < 80])
        missing_seo = len([entry for entry in root_seo_entries if entry.calculate_seo_score() < 40])
        
        # Average SEO score
        total_score = sum(entry.calculate_seo_score() for entry in root_seo_entries)
        avg_score = int(total_score / total_pages) if total_pages > 0 else 0
        
        # Field completion rates
        field_stats = {
            'meta_title': len([e for e in root_seo_entries if e.meta_title]),
            'meta_description': len([e for e in root_seo_entries if e.meta_description]),
            'meta_keywords': len([e for e in root_seo_entries if e.meta_keywords]),
            'og_title': len([e for e in root_seo_entries if e.og_title]),
            'og_description': len([e for e in root_seo_entries if e.og_description]),
            'og_image': len([e for e in root_seo_entries if e.og_image]),
            'canonical_url': len([e for e in root_seo_entries if e.canonical_url]),
            'schema_markup': len([e for e in root_seo_entries if e.schema_markup])
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_pages': total_pages,
                'active_pages': active_pages,
                'complete_seo': complete_seo,
                'incomplete_seo': incomplete_seo,
                'missing_seo': missing_seo,
                'avg_score': avg_score,
                'field_stats': field_stats
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting analytics: {str(e)}'}), 500

@root_seo_bp.route('/settings/root-seo/export')
@login_required
def export_root_seo():
    """Export root SEO data as JSON."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        flash('Anda tidak memiliki izin untuk mengekspor data SEO.', 'error')
        return redirect(url_for('root_seo.root_seo_management'))
    
    try:
        root_seo_entries = RootSEO.query.all()
        export_data = [entry.to_dict() for entry in root_seo_entries]
        
        from flask import Response
        response = Response(
            json.dumps(export_data, ensure_ascii=False, indent=2),
            mimetype='application/json'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=root_seo_export.json'
        
        return response
        
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('root_seo.root_seo_management')) 

@root_seo_bp.route('/api/root-seo/current')
def get_current_root_seo():
    """Get root SEO data for the current page based on request path."""
    try:
        from flask import request
        
        # Determine page identifier based on current path
        path = request.path.strip('/')
        page_identifier = 'home' if not path else path.split('/')[0]
        
        # Get root SEO data for this page
        root_seo = RootSEO.query.filter_by(
            page_identifier=page_identifier,
            is_active=True
        ).first()
        
        if root_seo:
            return jsonify({
                'success': True,
                'data': root_seo.to_dict()
            })
        else:
            # Return default SEO data
            return jsonify({
                'success': True,
                'data': {
                    'meta_title': None,
                    'meta_description': None,
                    'meta_keywords': None,
                    'og_title': None,
                    'og_description': None,
                    'og_image': None,
                    'og_type': 'website',
                    'twitter_card': 'summary_large_image',
                    'twitter_title': None,
                    'twitter_description': None,
                    'twitter_image': None,
                    'canonical_url': None,
                    'meta_author': None,
                    'meta_language': 'id',
                    'meta_robots': 'index, follow',
                    'structured_data_type': 'WebPage',
                    'schema_markup': None
                }
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500 