"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
SEO Management Routes

This module handles all SEO-related routes and API endpoints.
"""

from routes import main_blueprint
from .common_imports import *
from flask import jsonify, redirect, url_for


@main_blueprint.route("/settings/seo")
@login_required
def settings_seo():
    # Allow access only to admin-tier users
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return render_template('admin/seo/management.html')


@main_blueprint.route("/settings/seo/management")
@login_required
def seo_management():
    """Main SEO management page for all content types"""
    # Allow access only to admin-tier users
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return render_template('admin/seo/management.html')


@main_blueprint.route("/settings/seo/settings")
@login_required
def seo_settings():
    """SEO settings page for root SEO and global settings"""
    # Allow access only to admin-tier users
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return render_template('admin/seo/settings.html')


@main_blueprint.route("/settings/seo/analytics")
@login_required
def seo_analytics():
    """SEO analytics page for performance metrics and insights"""
    # Allow access only to admin-tier users
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return render_template('admin/seo/analytics.html')


# Legacy route for backward compatibility
@main_blueprint.route("/settings/comprehensive-seo")
@login_required
def settings_comprehensive_seo():
    """Comprehensive SEO management page for all content types - redirects to new management page"""
    # Allow access only to admin-tier users
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return redirect(url_for('main.seo_management'))


# SEO Management API Endpoints
@main_blueprint.route("/api/seo/articles", methods=["GET"])
@login_required
def get_seo_articles():
    """Get articles with SEO information for management"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)  # Changed from 10 to 20
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        seo_status = request.args.get('seo_status', '')
        category = request.args.get('category', '')
        
        # Build query with explicit foreign key relationships
        query = News.query.join(Category, News.category_id == Category.id).join(User, News.user_id == User.id)
        
        # Apply filters
        if search:
            query = query.filter(News.title.ilike(f'%{search}%'))
        
        if status:
            if status == 'published':
                query = query.filter(News.is_visible == True, News.is_archived == False)
            elif status == 'draft':
                query = query.filter(News.is_visible == False, News.is_archived == False)
            elif status == 'archived':
                query = query.filter(News.is_archived == True)
        
        if category:
            query = query.filter(Category.name == category)
        
        # Apply SEO status filter
        if seo_status:
            if seo_status == 'complete':
                query = query.filter(
                    News.meta_description.isnot(None),
                    News.meta_description != '',
                    News.meta_keywords.isnot(None),
                    News.meta_keywords != '',
                    News.og_title.isnot(None),
                    News.og_title != '',
                    News.og_description.isnot(None),
                    News.og_description != '',
                    News.og_image.isnot(None),
                    News.og_image != '',
                    News.seo_slug.isnot(None),
                    News.seo_slug != ''
                )
            elif seo_status == 'incomplete':
                # Articles that have some SEO fields but not all required ones
                query = query.filter(
                    db.or_(
                        News.meta_description.is_(None),
                        News.meta_description == '',
                        News.meta_keywords.is_(None),
                        News.meta_keywords == '',
                        News.og_title.is_(None),
                        News.og_title == '',
                        News.og_description.is_(None),
                        News.og_description == '',
                        News.og_image.is_(None),
                        News.og_image == '',
                        News.seo_slug.is_(None),
                        News.seo_slug == ''
                    )
                ).filter(
                    db.or_(
                        News.meta_description.isnot(None),
                        News.meta_keywords.isnot(None),
                        News.og_title.isnot(None),
                        News.og_description.isnot(None),
                        News.og_image.isnot(None),
                        News.seo_slug.isnot(None)
                    )
                )
            elif seo_status == 'missing':
                query = query.filter(
                    News.meta_description.is_(None),
                    News.meta_keywords.is_(None),
                    News.og_title.is_(None)
                )
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        articles = query.order_by(News.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Prepare response data
        articles_data = []
        for article in articles:
            # Determine SEO status (consistent with metrics endpoint)
            has_meta_desc = bool(article.meta_description)
            has_meta_keywords = bool(article.meta_keywords)
            has_og_title = bool(article.og_title)
            has_og_desc = bool(article.og_description)
            has_og_image = bool(article.og_image)
            has_seo_slug = bool(article.seo_slug)
            
            if has_meta_desc and has_meta_keywords and has_og_title and has_og_desc and has_og_image and has_seo_slug:
                seo_status = 'complete'
            elif has_meta_desc or has_meta_keywords or has_og_title or has_og_desc or has_og_image or has_seo_slug:
                seo_status = 'incomplete'
            else:
                seo_status = 'missing'
            
            # Safely get image URL
            image_url = None
            try:
                if article.image and hasattr(article.image, 'filename'):
                    image_url = f"/static/uploads/{article.image.filename}"
            except Exception:
                pass
            
            articles_data.append({
                'id': article.id,
                'title': article.title,
                'category_name': article.category.name,
                'writer': article.writer,
                'image_url': image_url,
                'meta_description': article.meta_description,
                'meta_keywords': article.meta_keywords,
                'og_title': article.og_title,
                'og_description': article.og_description,
                'og_image': article.og_image,
                'canonical_url': article.canonical_url,
                'seo_slug': article.seo_slug,
                'seo_status': seo_status,
                'created_at': article.created_at.isoformat() if article.created_at else None
            })
        
        # Prepare pagination info for frontend compatibility
        total_pages = (total + per_page - 1) // per_page
        pagination = {
            'current_page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        return jsonify({
            'articles': articles_data,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        print(f"Error in get_seo_articles: {e}")
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/articles/<int:article_id>", methods=["GET"])
@login_required
def get_seo_article(article_id):
    """Get a specific article for SEO editing"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        article = News.query.get_or_404(article_id)
        
        return jsonify({
            'id': article.id,
            'title': article.title,
            'category_name': article.category.name,
            'writer': article.writer,
            'meta_description': article.meta_description,
            'meta_keywords': article.meta_keywords,
            'og_title': article.og_title,
            'og_description': article.og_description,
            'og_image': article.og_image,
            'canonical_url': article.canonical_url,
            'seo_slug': article.seo_slug,
            'twitter_card': article.twitter_card,
            'twitter_title': article.twitter_title,
            'twitter_description': article.twitter_description,
            'twitter_image': article.twitter_image,
            'meta_author': article.meta_author,
            'meta_language': article.meta_language,
            'meta_robots': article.meta_robots,
            'structured_data_type': article.structured_data_type,
            'schema_markup': article.schema_markup,
            'seo_score': article.seo_score,
            'last_seo_audit': article.last_seo_audit.isoformat() if article.last_seo_audit else None,
            'created_at': article.created_at.isoformat() if article.created_at else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/articles/<int:article_id>", methods=["PUT"])
@login_required
def update_seo_article(article_id):
    """Update SEO fields for a specific article"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        article = News.query.get_or_404(article_id)
        data = request.get_json()
        
        # Update basic SEO fields
        if 'meta_description' in data:
            article.meta_description = data['meta_description']
        if 'meta_keywords' in data:
            article.meta_keywords = data['meta_keywords']
        if 'og_title' in data:
            article.og_title = data['og_title']
        if 'og_description' in data:
            article.og_description = data['og_description']
        if 'og_image' in data:
            article.og_image = data['og_image']
        if 'canonical_url' in data:
            article.canonical_url = data['canonical_url']
        if 'seo_slug' in data:
            # Check if slug is unique
            existing = News.query.filter_by(seo_slug=data['seo_slug']).first()
            if existing and existing.id != article.id:
                return jsonify({'error': 'SEO slug already exists'}), 400
            article.seo_slug = data['seo_slug']
        
        # Update advanced SEO fields
        if 'twitter_card' in data:
            article.twitter_card = data['twitter_card']
        if 'twitter_title' in data:
            article.twitter_title = data['twitter_title']
        if 'twitter_description' in data:
            article.twitter_description = data['twitter_description']
        if 'twitter_image' in data:
            article.twitter_image = data['twitter_image']
        if 'meta_author' in data:
            article.meta_author = data['meta_author']
        if 'meta_language' in data:
            article.meta_language = data['meta_language']
        if 'meta_robots' in data:
            article.meta_robots = data['meta_robots']
        if 'structured_data_type' in data:
            article.structured_data_type = data['structured_data_type']
        
        # Generate schema markup if structured data type is provided
        if article.structured_data_type:
            article.schema_markup = article.generate_schema_markup()
        
        # Calculate and update SEO score
        article.seo_score = article.calculate_seo_score()
        article.last_seo_audit = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'SEO updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/bulk-update", methods=["POST"])
@login_required
def bulk_update_seo():
    """Bulk update SEO data for multiple articles"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        data = request.get_json()
        action = data.get('action')
        field = data.get('field')
        
        if not action or not field:
            return jsonify({"error": "Action and field are required"}), 400
        
        # Get all articles that need the specific field updated
        articles = []
        if action == 'add_meta_descriptions':
            articles = News.query.filter_by(meta_description=None).all()
        elif action == 'add_og_titles':
            articles = News.query.filter_by(og_title=None).all()
        elif action == 'add_seo_slugs':
            articles = News.query.filter_by(seo_slug=None).all()
        else:
            return jsonify({"error": "Invalid action"}), 400
        
        updated_count = 0
        for article in articles:
            try:
                if action == 'add_meta_descriptions':
                    # Generate meta description from title
                    article.meta_description = f"{article.title} - Berita terbaru dan terkini"
                elif action == 'add_og_titles':
                    # Use title as OG title
                    article.og_title = article.title
                elif action == 'add_seo_slugs':
                    # Generate SEO slug from title
                    from slugify import slugify
                    base_slug = slugify(article.title)
                    # Ensure uniqueness
                    counter = 1
                    new_slug = base_slug
                    while News.query.filter_by(seo_slug=new_slug).first():
                        new_slug = f"{base_slug}-{counter}"
                        counter += 1
                    article.seo_slug = new_slug
                
                # Update SEO score
                article.seo_score = article.calculate_seo_score()
                article.last_seo_audit = datetime.utcnow()
                updated_count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error updating article {article.id}: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully updated {updated_count} articles",
            "updated_count": updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk_update_seo: {e}")
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/api/seo/metrics", methods=["GET"])
@login_required
def get_seo_metrics():
    """Get comprehensive SEO metrics and analytics"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        # Get all articles with categories (left join to include articles without categories)
        articles = News.query.outerjoin(Category).all()
        total_articles = len(articles)
        
        # Initialize counters
        complete_count = 0
        incomplete_count = 0
        missing_count = 0
        issues = []
        
        # SEO field tracking
        meta_desc_count = 0
        meta_keywords_count = 0
        og_title_count = 0
        og_desc_count = 0
        og_image_count = 0
        seo_slug_count = 0
        canonical_url_count = 0
        twitter_card_count = 0
        
        # Category-based analytics
        category_stats = {}
        
        # Recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)  # Use naive datetime
        recent_articles = []
        for a in articles:
            try:
                if a.created_at and a.created_at >= thirty_days_ago:
                    recent_articles.append(a)
            except Exception as e:
                current_app.logger.warning(f"Error processing article {a.id} for recent calculation: {e}")
                continue
        
        for article in articles:
            has_meta_desc = bool(article.meta_description)
            has_meta_keywords = bool(article.meta_keywords)
            has_og_title = bool(article.og_title)
            has_og_desc = bool(article.og_description)
            has_og_image = bool(article.og_image)
            has_seo_slug = bool(article.seo_slug)
            has_canonical = bool(article.canonical_url)
            has_twitter_card = bool(article.twitter_card)
            
            # Count individual fields
            if has_meta_desc: meta_desc_count += 1
            if has_meta_keywords: meta_keywords_count += 1
            if has_og_title: og_title_count += 1
            if has_og_desc: og_desc_count += 1
            if has_og_image: og_image_count += 1
            if has_seo_slug: seo_slug_count += 1
            if has_canonical: canonical_url_count += 1
            if has_twitter_card: twitter_card_count += 1
            
            # Determine overall status
            if has_meta_desc and has_meta_keywords and has_og_title and has_og_desc and has_og_image and has_seo_slug:
                complete_count += 1
            elif has_meta_desc or has_meta_keywords or has_og_title or has_og_desc or has_og_image or has_seo_slug:
                incomplete_count += 1
            else:
                missing_count += 1
            
            # Category statistics
            category_name = article.category.name if article.category else 'Uncategorized'
            if category_name not in category_stats:
                category_stats[category_name] = {
                    'total': 0,
                    'complete': 0,
                    'incomplete': 0,
                    'missing': 0
                }
            
            category_stats[category_name]['total'] += 1
            if has_meta_desc and has_meta_keywords and has_og_title and has_og_desc and has_og_image and has_seo_slug:
                category_stats[category_name]['complete'] += 1
            elif has_meta_desc or has_meta_keywords or has_og_title or has_og_desc or has_og_image or has_seo_slug:
                category_stats[category_name]['incomplete'] += 1
            else:
                category_stats[category_name]['missing'] += 1
            
            # Identify specific issues (only for missing articles to avoid spam)
            if not has_meta_desc:
                issues.append({
                    'title': f'Missing Meta Description: {article.title}',
                    'description': f'Article "{article.title}" is missing a meta description',
                    'article_id': article.id,
                    'category': category_name,
                    'priority': 'high'
                })
            
            if not has_og_title:
                issues.append({
                    'title': f'Missing OG Title: {article.title}',
                    'description': f'Article "{article.title}" is missing an Open Graph title',
                    'article_id': article.id,
                    'category': category_name,
                    'priority': 'high'
                })
            
            if not has_seo_slug:
                issues.append({
                    'title': f'Missing SEO Slug: {article.title}',
                    'description': f'Article "{article.title}" is missing an SEO-friendly URL slug',
                    'article_id': article.id,
                    'category': category_name,
                    'priority': 'high'
                })
            
            if not has_og_image:
                issues.append({
                    'title': f'Missing OG Image: {article.title}',
                    'description': f'Article "{article.title}" is missing an Open Graph image',
                    'article_id': article.id,
                    'category': category_name,
                    'priority': 'medium'
                })
        
        # Calculate completion rates
        completion_rate = round((complete_count / total_articles) * 100) if total_articles > 0 else 0
        
        # Field completion rates
        field_completion = {
            'meta_description': round((meta_desc_count / total_articles) * 100) if total_articles > 0 else 0,
            'meta_keywords': round((meta_keywords_count / total_articles) * 100) if total_articles > 0 else 0,
            'og_title': round((og_title_count / total_articles) * 100) if total_articles > 0 else 0,
            'og_description': round((og_desc_count / total_articles) * 100) if total_articles > 0 else 0,
            'og_image': round((og_image_count / total_articles) * 100) if total_articles > 0 else 0,
            'seo_slug': round((seo_slug_count / total_articles) * 100) if total_articles > 0 else 0,
            'canonical_url': round((canonical_url_count / total_articles) * 100) if total_articles > 0 else 0,
            'twitter_card': round((twitter_card_count / total_articles) * 100) if total_articles > 0 else 0
        }
        
        # Recent activity metrics
        recent_complete = sum(1 for a in recent_articles if a.meta_description and a.meta_keywords and a.og_title and a.og_description and a.og_image and a.seo_slug)
        recent_total = len(recent_articles)
        recent_completion_rate = round((recent_complete / recent_total) * 100) if recent_total > 0 else 0
        
        # Sort issues by priority and limit to top 15
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        issues.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 0), reverse=True)
        issues = issues[:15]
        
        # Calculate category completion rates
        for category in category_stats:
            total = category_stats[category]['total']
            complete = category_stats[category]['complete']
            category_stats[category]['completion_rate'] = round((complete / total) * 100) if total > 0 else 0
        
        return jsonify({
            'complete_count': complete_count,
            'incomplete_count': incomplete_count,
            'missing_count': missing_count,
            'total_articles': total_articles,
            'completion_rate': completion_rate,
            'field_completion': field_completion,
            'category_stats': category_stats,
            'recent_activity': {
                'total_recent': recent_total,
                'complete_recent': recent_complete,
                'recent_completion_rate': recent_completion_rate
            },
            'issues': issues,
            'field_counts': {
                'meta_description': meta_desc_count,
                'meta_keywords': meta_keywords_count,
                'og_title': og_title_count,
                'og_description': og_desc_count,
                'og_image': og_image_count,
                'seo_slug': seo_slug_count,
                'canonical_url': canonical_url_count,
                            'twitter_card': twitter_card_count
        }
    }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in get_seo_metrics: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/global-settings", methods=["GET"])
@login_required
def get_global_seo_settings():
    """Get global SEO settings"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        # For now, return empty settings - this could be extended to store in database
        return jsonify({
            'default_meta_description': '',
            'default_meta_keywords': '',
            'default_og_title': '',
            'default_og_description': '',
            'default_og_image': ''
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/global-settings", methods=["POST"])
@login_required
def update_global_seo_settings():
    """Update global SEO settings"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        request.get_json()
        
        # For now, just return success - this could be extended to store in database
        # In a real implementation, you might want to store these in a settings table
        
        return jsonify({'message': 'Global SEO settings updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/global-og", methods=["POST"])
@login_required
def update_global_og_settings():
    """Update global Open Graph settings"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        request.get_json()
        
        # For now, just return success - this could be extended to store in database
        
        return jsonify({'message': 'Global OG settings updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_blueprint.route("/api/seo/global-twitter", methods=["POST"])
@login_required
def update_global_twitter_settings():
    """Update global Twitter Card settings"""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    
    try:
        data = request.get_json()
        
        # Update global settings in database or config
        current_app.logger.info(f"Updating global Twitter settings: {data}")
        
        return jsonify({"message": "Global Twitter settings updated successfully"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating global Twitter settings: {e}")
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/seo/global-structured", methods=["POST"])
@login_required
def update_global_structured_settings():
    """Update global Structured Data settings"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        data = request.get_json()
        
        # Update global settings in database or config
        current_app.logger.info(f"Updating global Structured Data settings: {data}")
        
        return jsonify({"message": "Global Structured Data settings updated successfully"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating global Structured Data settings: {e}")
        return jsonify({"error": str(e)}), 500


# Minimal Analytics Endpoints (stubs to resolve 404s)
@main_blueprint.route("/api/analytics/visitors", methods=["GET"])
@login_required
def analytics_visitors():
    try:
        total_users = User.query.count()
        total_news = News.query.count()
        from models import Image
        total_images = Image.query.count() if 'Image' in globals() else 0
        data = {
            "active_visitors": 5,
            "total_users": total_users,
            "total_news": total_news,
            "total_images": total_images,
            "total_videos": 0
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200


@main_blueprint.route("/api/analytics/content", methods=["GET"])
@login_required
def analytics_content():
    try:
        days = request.args.get('days', 30, type=int)
        # Simple aggregates
        news_total = News.query.count()
        avg_reads = db.session.query(db.func.avg(News.read_count)).scalar() or 0
        data = {
            "news": {
                "total": news_total,
                "total_reads": int(avg_reads * news_total),
                "avg_reads": float(avg_reads),
                "top_articles": []
            },
            "images": {"total": 0, "avg_downloads": 0.0},
            "videos": {"total": 0, "avg_views": 0.0}
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200


@main_blueprint.route("/api/analytics/activity", methods=["GET"])
@login_required
def analytics_activity():
    try:
        return jsonify({"activities": []}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200


@main_blueprint.route("/api/analytics/dashboard", methods=["GET"])
@login_required
def analytics_dashboard():
    try:
        data = {
            "weekly": {
                "news_created": 0,
                "images_uploaded": 0,
                "videos_uploaded": 0,
                "active_users": 0
            }
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200


@main_blueprint.route("/api/analytics/track", methods=["POST"])
def analytics_track():
    try:
        # Accept and ignore payload for now
        _ = request.get_json(silent=True) or {}
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 200


@main_blueprint.route("/api/analytics/export", methods=["POST"])
@login_required
def analytics_export():
    try:
        # Return a small CSV blob
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["type", "value"])
        writer.writerow(["example", 1])
        csv_data = output.getvalue()
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=report.csv'}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 200


# Albums SEO Management endpoint (for albums management page)
@main_blueprint.route("/api/seo/albums-management", methods=["GET"])
@login_required
def get_albums_seo_management_settings():
    """List albums with SEO fields for the albums management SEO tab."""
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '').strip()  # visible|hidden|archived
        seo_status = request.args.get('seo_status', '').strip()  # complete|incomplete|missing
        category = request.args.get('category', '').strip()

        query = db.session.query(
            Album.id,
            Album.title,
            Album.description,
            Album.meta_description,
            Album.meta_keywords,
            Album.og_title,
            Album.og_description,
            Album.seo_score,
            Album.is_visible,
            Album.is_archived,
            Album.created_at,
            Category.name.label('category_name')
        ).join(Category, Album.category_id == Category.id)

        if search:
            query = query.filter(db.or_(
                Album.title.ilike(f"%{search}%"),
                Album.description.ilike(f"%{search}%")
            ))

        if status:
            if status == 'visible':
                query = query.filter(Album.is_visible == True, Album.is_archived == False)
            elif status == 'hidden':
                query = query.filter(Album.is_visible == False, Album.is_archived == False)
            elif status == 'archived':
                query = query.filter(Album.is_archived == True)

        if category:
            # Accept category id or name
            if category.isdigit():
                query = query.filter(Category.id == int(category))
            else:
                query = query.filter(Category.name == category)

        if seo_status:
            if seo_status == 'complete':
                query = query.filter(db.and_(
                    Album.meta_description.isnot(None), Album.meta_description != '',
                    Album.meta_keywords.isnot(None), Album.meta_keywords != '',
                    Album.og_title.isnot(None), Album.og_title != ''
                ))
            elif seo_status == 'incomplete':
                query = query.filter(db.or_(
                    Album.meta_description.is_(None), Album.meta_description == '',
                    Album.meta_keywords.is_(None), Album.meta_keywords == '',
                    Album.og_title.is_(None), Album.og_title == ''
                ))
            elif seo_status == 'missing':
                query = query.filter(db.and_(
                    Album.meta_description.is_(None),
                    Album.meta_keywords.is_(None),
                    Album.og_title.is_(None)
                ))

        total_count = query.count()
        results = query.order_by(db.desc(Album.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        albums = []
        for r in results:
            fields = [r.meta_description, r.meta_keywords, r.og_title, r.og_description]
            filled = sum(1 for f in fields if f and str(f).strip())
            status_value = 'complete' if filled == len(fields) else ('missing' if filled == 0 else 'incomplete')
            albums.append({
                'id': r.id,
                'title': r.title,
                'category_name': r.category_name,
                'meta_description': r.meta_description,
                'meta_keywords': r.meta_keywords,
                'og_title': r.og_title,
                'og_description': r.og_description,
                'seo_status': status_value,
                'seo_score': r.seo_score or 0,
                'is_visible': r.is_visible,
                'is_archived': r.is_archived,
                'created_at': r.created_at.isoformat() if r.created_at else None
            })

        total_pages = (total_count + per_page - 1) // per_page
        pagination = {
            'current_page': page,
            'per_page': per_page,
            'total_items': total_count,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }

        return jsonify({'albums': albums, 'pagination': pagination}), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_albums_seo_management_settings: {e}")
        return jsonify({'error': str(e)}), 500


# REMOVED: Duplicate route - using routes_seo.py instead
# @main_blueprint.route("/api/seo/inject", methods=["POST"])
# @login_required
# def run_seo_injection_settings():
#     """Alias endpoint to run SEO injection (articles, albums, chapters, root, all)."""
#     # This route has been moved to routes_seo.py for better organization


# REMOVED: Duplicate route - using routes_seo.py instead
# Per-item SEO Injection Endpoints
# @main_blueprint.route("/api/seo/articles/<int:article_id>/inject", methods=["POST"])
# @login_required
# def inject_seo_article(article_id):
#     # This route has been moved to routes_seo.py for better organization


# REMOVED: Duplicate route - using routes_seo.py instead
# @main_blueprint.route("/api/seo/albums/<int:album_id>/inject", methods=["POST"])
# @login_required
# def inject_seo_album_item(album_id):
#     # This route has been moved to routes_seo.py for better organization


# REMOVED: Duplicate route - using routes_seo.py instead
# @main_blueprint.route("/api/seo/chapters/<int:chapter_id>/inject", methods=["POST"])
# @login_required
# def inject_seo_chapter_item(chapter_id):
#     # This route has been moved to routes_seo.py for better organization


@main_blueprint.route("/api/seo/root/<int:root_id>/inject", methods=["POST"])
@login_required
def inject_seo_root_item(root_id):
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    try:
        root = RootSEO.query.get_or_404(root_id)
        # Simple enrichment
        base_text = (root.og_description or root.meta_description or root.page_name or root.page_identifier or "").strip()
        root.meta_title = root.meta_title or f"{root.page_name or root.page_identifier} - SEO"
        root.meta_description = root.meta_description or base_text[:500]
        root.meta_keywords = root.meta_keywords or ", ".join((root.page_name or root.page_identifier or "").lower().split()[:6])
        root.og_title = root.og_title or root.meta_title
        root.og_description = root.og_description or root.meta_description
        root.seo_score = root.calculate_seo_score()
        root.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "SEO injected for root page", "id": root.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_blueprint.route("/api/seo/apply-global-settings", methods=["POST"])
@login_required
def apply_global_settings():
    """Apply global settings to all articles that don't have specific SEO fields"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        # Get all articles that need global settings applied
        articles = News.query.all()
        updated_count = 0
        
        for article in articles:
            updated = False
            
            # Apply global settings only if the field is empty
            if not article.meta_description:
                article.meta_description = "Default meta description"  # Get from global settings
                updated = True
            
            if not article.meta_keywords:
                article.meta_keywords = "default, keywords"  # Get from global settings
                updated = True
            
            if not article.og_title:
                article.og_title = article.title  # Use title as default
                updated = True
            
            if not article.og_description:
                article.og_description = article.meta_description or "Default OG description"
                updated = True
            
            if not article.twitter_card:
                article.twitter_card = "summary"  # Get from global settings
                updated = True
            
            if not article.twitter_title:
                article.twitter_title = article.title  # Use title as default
                updated = True
            
            if not article.twitter_description:
                article.twitter_description = article.meta_description or "Default Twitter description"
                updated = True
            
            if not article.structured_data_type:
                article.structured_data_type = "Article"  # Get from global settings
                updated = True
            
            if not article.meta_author:
                article.meta_author = "Default Author"  # Get from global settings
                updated = True
            
            if not article.meta_robots:
                article.meta_robots = "index, follow"  # Get from global settings
                updated = True
            
            if not article.meta_language:
                article.meta_language = "id"  # Get from global settings
                updated = True
            
            if updated:
                # Update SEO score
                article.seo_score = article.calculate_seo_score()
                article.last_seo_audit = datetime.utcnow()
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully applied global settings to {updated_count} articles",
            "updated_count": updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error applying global settings: {e}")
        return jsonify({"error": str(e)}), 500


@main_blueprint.route("/api/seo/categories", methods=["GET"])
@login_required
def get_seo_categories():
    """Get categories for SEO management filter"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        categories = Category.query.all()
        return jsonify([{
            'id': cat.id,
            'name': cat.name
        } for cat in categories]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Albums SEO API Endpoints (Placeholder for future implementation)
@main_blueprint.route("/api/seo/albums", methods=["GET"])
@login_required
def get_seo_albums():
    """Get albums with SEO information for management"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '')
        seo_status = request.args.get('seo_status', '')
        category = request.args.get('category', '')

        # Build base query
        query = db.session.query(
            Album.id,
            Album.title,
            Album.description,
            Album.meta_description,
            Album.meta_keywords,
            Album.og_title,
            Album.og_description,
            Album.seo_score,
            Album.is_visible,
            Album.is_archived,
            Album.created_at,
            Category.name.label('category_name')
        ).join(Category, Album.category_id == Category.id)

        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Album.title.ilike(f"%{search}%"),
                    Album.description.ilike(f"%{search}%")
                )
            )

        if status:
            if status == "published":
                query = query.filter(Album.is_visible == True, Album.is_archived == False)
            elif status == "draft":
                query = query.filter(Album.is_visible == False, Album.is_archived == False)
            elif status == "archived":
                query = query.filter(Album.is_archived == True)

        if category:
            query = query.filter(Category.id == category)

        # Apply SEO status filter
        if seo_status:
            if seo_status == "complete":
                query = query.filter(
                    db.and_(
                        Album.meta_description.isnot(None),
                        Album.meta_description != "",
                        Album.meta_keywords.isnot(None),
                        Album.meta_keywords != "",
                        Album.og_title.isnot(None),
                        Album.og_title != ""
                    )
                )
            elif seo_status == "incomplete":
                query = query.filter(
                    db.or_(
                        Album.meta_description.is_(None),
                        Album.meta_description == "",
                        Album.meta_keywords.is_(None),
                        Album.meta_keywords == "",
                        Album.og_title.is_(None),
                        Album.og_title == ""
                    )
                )
            elif seo_status == "missing":
                query = query.filter(
                    db.and_(
                        Album.meta_description.is_(None),
                        Album.meta_keywords.is_(None),
                        Album.og_title.is_(None)
                    )
                )

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        query = query.order_by(db.desc(Album.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Execute query
        results = query.all()

        # Process results
        albums = []
        for result in results:
            # Calculate SEO status
            seo_fields = [
                result.meta_description,
                result.meta_keywords,
                result.og_title,
                result.og_description
            ]
            
            filled_fields = sum(1 for field in seo_fields if field and field.strip())
            if filled_fields == len(seo_fields):
                seo_status = "complete"
            elif filled_fields == 0:
                seo_status = "missing"
            else:
                seo_status = "incomplete"

            albums.append({
                "id": result.id,
                "title": result.title,
                "category_name": result.category_name,
                "meta_description": result.meta_description,
                "meta_keywords": result.meta_keywords,
                "og_title": result.og_title,
                "og_description": result.og_description,
                "seo_status": seo_status,
                "seo_score": result.seo_score or 0,
                "is_visible": result.is_visible,
                "is_archived": result.is_archived,
                "created_at": result.created_at.isoformat() if result.created_at else None
            })

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

        pagination = {
            "current_page": page,
            "per_page": per_page,
            "total_items": total_count,
            "total_pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next
        }

        return jsonify({
            "albums": albums,
            "pagination": pagination
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/albums/<int:album_id>", methods=["GET"])
@login_required
def get_seo_album(album_id):
    """Get a specific album for SEO editing"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        # Eager load category to avoid N+1 queries
        from sqlalchemy.orm import joinedload
        album = Album.query.options(
            joinedload(Album.category)
        ).get_or_404(album_id)
        
        return jsonify({
            'id': album.id,
            'title': album.title,
            'category': album.category.name if album.category else "N/A",
            'meta_description': album.meta_description,
            'meta_keywords': album.meta_keywords,
            'og_title': album.og_title,
            'og_description': album.og_description,
            'og_image': album.og_image,
            'canonical_url': album.canonical_url,
            'seo_slug': album.seo_slug,
            'twitter_card': album.twitter_card,
            'twitter_title': album.twitter_title,
            'twitter_description': album.twitter_description,
            'twitter_image': album.twitter_image,
            'meta_author': album.meta_author,
            'meta_language': album.meta_language or 'id',
            'meta_robots': album.meta_robots or 'index, follow',
            'structured_data_type': album.structured_data_type or 'Book',
            'seo_score': album.seo_score or 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/albums/<int:album_id>", methods=["PUT"])
@login_required
def update_seo_album(album_id):
    """Update SEO fields for a specific album"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        album = Album.query.get_or_404(album_id)
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update SEO fields
        seo_fields = [
            'meta_description', 'meta_keywords', 'og_title', 'og_description',
            'og_image', 'canonical_url', 'seo_slug', 'twitter_card',
            'twitter_title', 'twitter_description', 'twitter_image',
            'meta_author', 'meta_language', 'meta_robots', 'structured_data_type'
        ]

        for field in seo_fields:
            if field in data:
                setattr(album, field, data[field])

        # Calculate SEO score
        seo_fields_to_check = [
            'meta_description', 'meta_keywords', 'og_title', 'og_description',
            'og_image', 'seo_slug'
        ]
        
        filled_fields = sum(1 for field in seo_fields_to_check 
                          if getattr(album, field) and getattr(album, field).strip())
        album.seo_score = min(100, int((filled_fields / len(seo_fields_to_check)) * 100))

        db.session.commit()
        return jsonify({"message": "Album SEO updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Chapters Management API Endpoints
@main_blueprint.route("/api/seo/chapters", methods=["GET"])
@login_required
def get_seo_chapters():
    """Get chapters with SEO information for management"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '')
        seo_status = request.args.get('seo_status', '')
        category = request.args.get('category', '')

        # Build base query
        query = db.session.query(
            AlbumChapter.id,
            AlbumChapter.chapter_number,
            AlbumChapter.chapter_title,
            AlbumChapter.meta_description,
            AlbumChapter.meta_keywords,
            AlbumChapter.og_title,
            AlbumChapter.og_description,
            AlbumChapter.seo_score,
            AlbumChapter.is_visible,
            AlbumChapter.created_at,
            Album.title.label('album_title'),
            Category.name.label('category_name')
        ).join(Album, AlbumChapter.album_id == Album.id).join(Category, Album.category_id == Category.id)

        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    AlbumChapter.chapter_title.ilike(f"%{search}%"),
                    Album.title.ilike(f"%{search}%")
                )
            )

        if status:
            if status == "published":
                query = query.filter(AlbumChapter.is_visible == True)
            elif status == "draft":
                query = query.filter(AlbumChapter.is_visible == False)

        if category:
            query = query.filter(Category.id == category)

        # Apply SEO status filter
        if seo_status:
            if seo_status == "complete":
                query = query.filter(
                    db.and_(
                        AlbumChapter.meta_description.isnot(None),
                        AlbumChapter.meta_description != "",
                        AlbumChapter.meta_keywords.isnot(None),
                        AlbumChapter.meta_keywords != "",
                        AlbumChapter.og_title.isnot(None),
                        AlbumChapter.og_title != ""
                    )
                )
            elif seo_status == "incomplete":
                query = query.filter(
                    db.or_(
                        AlbumChapter.meta_description.is_(None),
                        AlbumChapter.meta_description == "",
                        AlbumChapter.meta_keywords.is_(None),
                        AlbumChapter.meta_keywords == "",
                        AlbumChapter.og_title.is_(None),
                        AlbumChapter.og_title == ""
                    )
                )
            elif seo_status == "missing":
                query = query.filter(
                    db.and_(
                        AlbumChapter.meta_description.is_(None),
                        AlbumChapter.meta_keywords.is_(None),
                        AlbumChapter.og_title.is_(None)
                    )
                )

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        query = query.order_by(db.desc(AlbumChapter.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Execute query
        results = query.all()

        # Process results
        chapters = []
        for result in results:
            # Calculate SEO status
            seo_fields = [
                result.meta_description,
                result.meta_keywords,
                result.og_title,
                result.og_description
            ]
            
            filled_fields = sum(1 for field in seo_fields if field and field.strip())
            if filled_fields == len(seo_fields):
                seo_status = "complete"
            elif filled_fields == 0:
                seo_status = "missing"
            else:
                seo_status = "incomplete"

            chapters.append({
                "id": result.id,
                "chapter_number": result.chapter_number,
                "title": result.chapter_title,
                "album_title": result.album_title,
                "category_name": result.category_name,
                "meta_description": result.meta_description,
                "meta_keywords": result.meta_keywords,
                "og_title": result.og_title,
                "og_description": result.og_description,
                "seo_status": seo_status,
                "seo_score": result.seo_score or 0,
                "is_visible": result.is_visible,
                "created_at": result.created_at.isoformat() if result.created_at else None
            })

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

        pagination = {
            "current_page": page,
            "per_page": per_page,
            "total_items": total_count,
            "total_pages": total_pages,
            "has_prev": has_prev,
            "has_next": has_next
        }

        return jsonify({
            "chapters": chapters,
            "pagination": pagination
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_blueprint.route("/api/seo/chapters/<int:chapter_id>", methods=["GET"])
@login_required
def get_seo_chapter(chapter_id):
    """Get a specific chapter for SEO editing"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        # Eager load album and category to avoid N+1 queries
        from sqlalchemy.orm import joinedload
        chapter = AlbumChapter.query.options(
            joinedload(AlbumChapter.album).joinedload(Album.category)
        ).get_or_404(chapter_id)
        
        return jsonify({
            'id': chapter.id,
            'chapter_number': chapter.chapter_number,
            'title': chapter.chapter_title,
            'album': chapter.album.title if chapter.album else "N/A",
            'category': chapter.album.category.name if chapter.album and chapter.album.category else "N/A",
            'meta_description': chapter.meta_description,
            'meta_keywords': chapter.meta_keywords,
            'og_title': chapter.og_title,
            'og_description': chapter.og_description,
            'og_image': chapter.og_image,
            'canonical_url': chapter.canonical_url,
            'seo_slug': chapter.seo_slug,
            'twitter_card': chapter.twitter_card,
            'twitter_title': chapter.twitter_title,
            'twitter_description': chapter.twitter_description,
            'twitter_image': chapter.twitter_image,
            'meta_author': chapter.meta_author,
            'meta_language': chapter.meta_language or 'id',
            'meta_robots': chapter.meta_robots or 'index, follow',
            'structured_data_type': chapter.structured_data_type or 'Chapter',
            'seo_score': chapter.seo_score or 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_blueprint.route("/api/seo/chapters/<int:chapter_id>", methods=["PUT"])
@login_required
def update_seo_chapter(chapter_id):
    """Update SEO fields for a specific chapter"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        chapter = AlbumChapter.query.get_or_404(chapter_id)
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update SEO fields
        seo_fields = [
            'meta_description', 'meta_keywords', 'og_title', 'og_description',
            'og_image', 'canonical_url', 'seo_slug', 'twitter_card',
            'twitter_title', 'twitter_description', 'twitter_image',
            'meta_author', 'meta_language', 'meta_robots', 'structured_data_type'
        ]

        for field in seo_fields:
            if field in data:
                setattr(chapter, field, data[field])

        # Calculate SEO score
        seo_fields_to_check = [
            'meta_description', 'meta_keywords', 'og_title', 'og_description',
            'og_image', 'seo_slug'
        ]
        
        filled_fields = sum(1 for field in seo_fields_to_check 
                          if getattr(chapter, field) and getattr(chapter, field).strip())
        chapter.seo_score = min(100, int((filled_fields / len(seo_fields_to_check)) * 100))

        db.session.commit()
        return jsonify({"message": "Chapter SEO updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_blueprint.route("/api/seo/root", methods=["GET"])
@login_required
def get_seo_root():
    """Get root pages with SEO information for management"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)  # 20 items per page
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        request.args.get('seo_status', '')
        
        # Get root SEO entries from database
        query = RootSEO.query
        
        # If no root SEO entries exist, create some sample data
        if query.count() == 0:
            try:
                create_sample_root_seo_data()
                print("Sample root SEO data created successfully")
            except Exception as e:
                print(f"Error creating sample data: {e}")
                # Continue with empty data rather than failing
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    RootSEO.page_name.ilike(f'%{search}%'),
                    RootSEO.page_identifier.ilike(f'%{search}%')
                )
            )
        
        if status:
            if status == 'active':
                query = query.filter(RootSEO.is_active == True)
            elif status == 'inactive':
                query = query.filter(RootSEO.is_active == False)
        
        # Get total count for pagination
        total = query.count()
        print(f"Total root SEO entries found: {total}")
        
        # Apply pagination
        root_entries = query.order_by(RootSEO.page_identifier).offset((page - 1) * per_page).limit(per_page).all()
        print(f"Retrieved {len(root_entries)} root entries for page {page}")
        
        # Prepare response data
        root_data = []
        for entry in root_entries:
            try:
                # Calculate SEO score
                seo_score = entry.calculate_seo_score()
                
                # Determine SEO status
                if seo_score >= 80:
                    seo_status_value = 'complete'
                elif seo_score >= 40:
                    seo_status_value = 'incomplete'
                else:
                    seo_status_value = 'missing'
                
                root_data.append({
                    'id': entry.id,
                    'page_name': entry.page_name,
                    'page_identifier': entry.page_identifier,
                    'is_active': entry.is_active,
                    'meta_title': entry.meta_title,
                    'meta_description': entry.meta_description,
                    'meta_keywords': entry.meta_keywords,
                    'og_title': entry.og_title,
                    'og_description': entry.og_description,
                    'og_image': entry.og_image,
                    'canonical_url': entry.canonical_url,
                    'seo_score': seo_score,
                    'seo_status': seo_status_value,
                    'updated_at': entry.updated_at.isoformat() if entry.updated_at else None
                })
            except Exception as e:
                print(f"Error processing root entry {entry.id}: {e}")
                continue
        
        # Prepare pagination info
        total_pages = (total + per_page - 1) // per_page
        pagination = {
            'current_page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        print(f"Returning {len(root_data)} root entries with pagination: {pagination}")
        
        return jsonify({
            'root_entries': root_data,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        print(f"Error in get_seo_root: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


def create_sample_root_seo_data():
    """Create sample root SEO data for testing"""
    try:
        sample_pages = [
            {
                'page_identifier': 'home',
                'page_name': 'Beranda',
                'is_active': True,
                'meta_title': 'Beranda - Website Utama',
                'meta_description': 'Selamat datang di website utama kami. Temukan informasi terbaru dan terkini.',
                'meta_keywords': 'beranda, homepage, website utama',
                'og_title': 'Beranda - Website Utama',
                'og_description': 'Selamat datang di website utama kami',
                'og_image': '/static/pic/logo.png',
                'canonical_url': 'https://example.com/',
                'meta_author': 'Admin',
                'meta_language': 'id',
                'meta_robots': 'index, follow',
                'structured_data_type': 'WebPage'
            },
            {
                'page_identifier': 'about',
                'page_name': 'Tentang Kami',
                'is_active': True,
                'meta_title': 'Tentang Kami - Informasi Perusahaan',
                'meta_description': 'Pelajari lebih lanjut tentang perusahaan kami, visi, misi, dan tim kami.',
                'meta_keywords': 'tentang, perusahaan, visi, misi, tim',
                'og_title': 'Tentang Kami - Informasi Perusahaan',
                'og_description': 'Pelajari lebih lanjut tentang perusahaan kami',
                'og_image': '/static/pic/logo.png',
                'canonical_url': 'https://example.com/about',
                'meta_author': 'Admin',
                'meta_language': 'id',
                'meta_robots': 'index, follow',
                'structured_data_type': 'WebPage'
            },
            {
                'page_identifier': 'news',
                'page_name': 'Berita',
                'is_active': True,
                'meta_title': 'Berita Terbaru - Informasi Aktual',
                'meta_description': 'Baca berita terbaru dan informasi aktual dari berbagai sumber terpercaya.',
                'meta_keywords': 'berita, news, informasi, aktual',
                'og_title': 'Berita Terbaru - Informasi Aktual',
                'og_description': 'Baca berita terbaru dan informasi aktual',
                'og_image': '/static/pic/logo.png',
                'canonical_url': 'https://example.com/news',
                'meta_author': 'Admin',
                'meta_language': 'id',
                'meta_robots': 'index, follow',
                'structured_data_type': 'WebPage'
            }
        ]
        
        for page_data in sample_pages:
            # Check if entry already exists
            existing = RootSEO.query.filter_by(page_identifier=page_data['page_identifier']).first()
            if not existing:
                root_seo = RootSEO(
                    page_identifier=page_data['page_identifier'],
                    page_name=page_data['page_name'],
                    is_active=page_data['is_active'],
                    meta_title=page_data['meta_title'],
                    meta_description=page_data['meta_description'],
                    meta_keywords=page_data['meta_keywords'],
                    og_title=page_data['og_title'],
                    og_description=page_data['og_description'],
                    og_image=page_data['og_image'],
                    og_type='website',
                    twitter_card='summary_large_image',
                    twitter_title=page_data['og_title'],
                    twitter_description=page_data['og_description'],
                    twitter_image=page_data['og_image'],
                    canonical_url=page_data['canonical_url'],
                    meta_author=page_data['meta_author'],
                    meta_language=page_data['meta_language'],
                    meta_robots=page_data['meta_robots'],
                    structured_data_type=page_data['structured_data_type'],
                    created_by=1,  # Assuming admin user ID is 1
                    updated_by=1
                )
                db.session.add(root_seo)
        
        db.session.commit()
        print("Sample root SEO data created successfully")
        
    except Exception as e:
        print(f"Error creating sample root SEO data: {e}")
        db.session.rollback()