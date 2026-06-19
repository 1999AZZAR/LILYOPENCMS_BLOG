"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import BrandIdentity, db
from sqlalchemy import text
import json

seo_settings_bp = Blueprint('seo_settings', __name__, url_prefix='/api/seo/settings')

@seo_settings_bp.route('/load', methods=['GET'])
@login_required
def load_settings():
    """Load current SEO settings."""
    try:
        if not current_user.is_admin_tier():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Load from seo_injection_settings table
        seo_injection_settings = {}
        try:
            result = db.session.execute(text('''
                SELECT website_name, website_url, website_description, website_language, 
                       organization_name, organization_logo, organization_description,
                       default_meta_language, default_meta_robots, default_og_title, 
                       default_twitter_card, default_og_image, default_twitter_title
                FROM seo_injection_settings LIMIT 1
            '''))
            row = result.fetchone()
            if row:
                seo_injection_settings = {
                    'website_name': row[0],
                    'website_url': row[1],
                    'website_description': row[2],
                    'website_language': row[3],
                    'organization_name': row[4],
                    'organization_logo': row[5],
                    'organization_description': row[6],
                    'default_meta_language': row[7],
                    'default_meta_robots': row[8],
                    'default_og_title': row[9],
                    'default_twitter_card': row[10],
                    'default_og_image': row[11],
                    'default_twitter_title': row[12]
                }
        except Exception as e:
            current_app.logger.warning(f"Could not load SEO injection settings: {e}")
        
        # Load from BrandIdentity.seo_settings
        brand_seo_settings = {}
        try:
            brand_info = BrandIdentity.query.first()
            if brand_info and brand_info.seo_settings:
                if isinstance(brand_info.seo_settings, dict):
                    brand_seo_settings = brand_info.seo_settings
                else:
                    try:
                        brand_seo_settings = json.loads(brand_info.seo_settings) if isinstance(brand_info.seo_settings, str) else {}
                    except:
                        brand_seo_settings = {}
        except Exception as e:
            current_app.logger.warning(f"Could not load brand SEO settings: {e}")
        
        # Merge settings (seo_injection_settings takes priority)
        merged_settings = {
            # Hystory.id brand defaults
            'website_name': 'Hystory',
            'website_url': 'https://hystory.id',
            'website_description': 'Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi.',
            'website_language': 'id',
            'organization_name': 'Hystory',
            'organization_logo': 'https://hystory.id/static/pic/logo.png',
            'organization_description': 'Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi.',
            'default_language': 'id',
            'default_meta_robots': 'index, follow',
            'default_og_type': 'website',
            'default_twitter_card': 'summary_large_image',
            'default_og_image': 'https://hystory.id/static/pic/logo.png',
            'default_twitter_image': '',

            # Auto injection settings
            'auto_inject_articles': True,
            'auto_inject_albums': True,
            'auto_inject_chapters': True,
            'enable_seo_lock': False,
            'lock_after_injection': False,
            'batch_size': 20,
            'delay_between_batches': 100,
            
            # Root page templates - generic templates that can be customized
            'home_meta_title': '{brand_name} - Home',
            'home_meta_description': 'Welcome to {brand_name}. {website_description}',
            'home_meta_keywords': 'home, {brand_name}, website',
            
            'about_meta_title': 'About Us - {brand_name}',
            'about_meta_description': 'Learn about {brand_name} and our mission.',
            'about_meta_keywords': 'about, {brand_name}, company',
            
            'news_meta_title': 'News - {brand_name}',
            'news_meta_description': 'Latest news and articles from {brand_name}.',
            'news_meta_keywords': 'news, articles, {brand_name}',
            
            'albums_meta_title': 'Albums - {brand_name}',
            'albums_meta_description': 'Browse our collection of albums and stories.',
            'albums_meta_keywords': 'albums, stories, {brand_name}',
            
            # Content type templates - generic templates
            'article_meta_title': '{title} - {brand_name}',
            'article_meta_description': '{excerpt}',
            'article_meta_keywords': '{category}, {title_keywords}',
            'article_og_title': '{title} - {brand_name}',
            
            'album_meta_title': '{title} - {brand_name}',
            'album_meta_description': 'Read {title} - {chapter_count} chapters available.',
            'album_meta_keywords': '{category}, {title_keywords}',
            'album_og_title': '{title} - {brand_name}',
            
            'chapter_meta_title': '{title} - Chapter {chapter_number} - {brand_name}',
            'chapter_meta_description': 'Chapter {chapter_number}: {title}',
            'chapter_meta_keywords': '{album_category}, {title_keywords}',
            'chapter_og_title': '{title} - Chapter {chapter_number} - {brand_name}',
        }
        
        # Override with brand SEO settings (lower priority)
        for key, value in brand_seo_settings.items():
            if value is not None and value != '':
                merged_settings[key] = value
        
        # Override with SEO injection settings (higher priority)
        for key, value in seo_injection_settings.items():
            if value is not None and value != '':
                merged_settings[key] = value
        
        return jsonify({
            'status': 'success',
            'settings': merged_settings
        })
        
    except Exception as e:
        current_app.logger.error(f"Error loading SEO settings: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_settings_bp.route('/save', methods=['POST'])
@login_required
def save_settings():
    """Save SEO settings."""
    try:
        if not current_user.is_admin_tier():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Debug: Log the received data
        current_app.logger.info(f"Received SEO settings data: {data}")
        
        # Separate settings into different categories
        # Only update fields that are actually provided in the form data
        basic_settings = {}
        if 'website_name' in data:
            basic_settings['website_name'] = data.get('website_name')
        if 'website_url' in data:
            basic_settings['website_url'] = data.get('website_url')
        if 'website_description' in data:
            basic_settings['website_description'] = data.get('website_description')
        if 'website_language' in data:
            basic_settings['website_language'] = data.get('website_language')
        if 'organization_name' in data:
            basic_settings['organization_name'] = data.get('organization_name')
        if 'organization_logo' in data:
            basic_settings['organization_logo'] = data.get('organization_logo')
        if 'organization_description' in data:
            basic_settings['organization_description'] = data.get('organization_description')
        
        seo_defaults = {
            'default_meta_language': data.get('default_language'),
            'default_meta_robots': data.get('default_meta_robots'),
            'default_og_title': data.get('default_og_type'),
            'default_twitter_card': data.get('default_twitter_card'),
            'default_og_image': data.get('default_og_image'),
            'default_twitter_title': data.get('default_twitter_image')
        }
        
        # Debug: Log the extracted settings
        current_app.logger.info(f"Basic settings: {basic_settings}")
        current_app.logger.info(f"SEO defaults: {seo_defaults}")
        
        # Save to seo_injection_settings table
        try:
            # Check if record exists
            result = db.session.execute(text('SELECT COUNT(*) FROM seo_injection_settings'))
            count = result.fetchone()[0]
            
            if count > 0:
                # Update existing record - only update fields that are provided
                all_settings = {**basic_settings, **seo_defaults}
                if all_settings:
                    set_clauses = []
                    params = {}
                    for key, value in all_settings.items():
                        if value is not None:  # Only include non-None values
                            set_clauses.append(f"{key} = :{key}")
                            params[key] = value
                    
                    if set_clauses:
                        update_sql = f"UPDATE seo_injection_settings SET {', '.join(set_clauses)}"
                        db.session.execute(text(update_sql), params)
            else:
                # Insert new record - provide defaults for required fields
                all_settings = {**basic_settings, **seo_defaults}
                
                # Provide defaults for required fields if not provided
                if 'website_name' not in all_settings:
                    all_settings['website_name'] = 'Hystory'
                if 'website_url' not in all_settings:
                    all_settings['website_url'] = 'https://hystory.id'
                if 'organization_name' not in all_settings:
                    all_settings['organization_name'] = 'Hystory'
                
                # Set default values for other fields if not provided
                defaults = {
                    'website_description': 'Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi.',
                    'website_language': 'id',
                    'organization_logo': 'https://hystory.id/static/pic/logo.png',
                    'organization_description': 'Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi.',
                    'default_meta_language': 'id',
                    'default_meta_robots': 'index, follow',
                    'default_og_title': 'website',
                    'default_twitter_card': 'summary_large_image',
                    'default_og_image': 'https://hystory.id/static/pic/logo.png',
                    'default_twitter_title': ''
                }
                
                for key, default_value in defaults.items():
                    if key not in all_settings:
                        all_settings[key] = default_value
                
                insert_sql = '''
                    INSERT INTO seo_injection_settings 
                    (website_name, website_url, website_description, website_language, 
                     organization_name, organization_logo, organization_description,
                     default_meta_language, default_meta_robots, default_og_title, 
                     default_twitter_card, default_og_image, default_twitter_title)
                    VALUES 
                    (:website_name, :website_url, :website_description, :website_language, 
                     :organization_name, :organization_logo, :organization_description,
                     :default_meta_language, :default_meta_robots, :default_og_title, 
                     :default_twitter_card, :default_og_image, :default_twitter_title)
                '''
                db.session.execute(text(insert_sql), all_settings)
            
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error saving to seo_injection_settings: {e}")
            db.session.rollback()
            return jsonify({'error': f'Failed to save basic settings: {str(e)}'}), 500
        
        # Save advanced settings to BrandIdentity.seo_settings
        try:
            brand_info = BrandIdentity.query.first()
            if not brand_info:
                # Create new brand identity if it doesn't exist
                brand_info = BrandIdentity(
                    brand_name=basic_settings.get('website_name', 'Hystory'),
                    website_url=basic_settings.get('website_url', 'https://hystory.id')
                )
                current_app.db.session.add(brand_info)
            
            # Prepare advanced settings (everything except basic settings)
            advanced_settings = {k: v for k, v in data.items() if k not in basic_settings and k not in seo_defaults}
            
            # Update brand info with basic settings
            brand_info.brand_name = basic_settings.get('website_name', brand_info.brand_name)
            brand_info.website_url = basic_settings.get('website_url', brand_info.website_url)
            brand_info.tagline = basic_settings.get('website_description', brand_info.tagline)
            
            # Save advanced settings to seo_settings field
            brand_info.seo_settings = advanced_settings
            
            current_app.db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error saving to BrandIdentity: {e}")
            current_app.db.session.rollback()
            return jsonify({'error': f'Failed to save advanced settings: {str(e)}'}), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Settings saved successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error saving SEO settings: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@seo_settings_bp.route('/test', methods=['POST'])
@login_required
def test_settings():
    """Test SEO settings by running a sample injection."""
    try:
        if not current_user.is_admin_tier():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import the SEO injector
        from seo_injector.seo_injector import run_seo_injection
        
        # Run a test injection on a small sample
        result = run_seo_injection('news')
        
        return jsonify({
            'status': 'success',
            'test_result': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error testing SEO settings: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
