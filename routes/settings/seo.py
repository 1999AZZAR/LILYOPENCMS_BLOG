"""
SEO Management Routes

This module handles all SEO-related routes and API endpoints.
"""

from routes import main_blueprint
from .common_imports import *
from flask import jsonify


@main_blueprint.route("/settings/seo")
@login_required
def settings_seo():
    # Allow access only to ADMIN and SUPERUSER
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    return render_template("settings/seo_management.html")


# SEO Management API Endpoints
@main_blueprint.route("/api/seo/articles", methods=["GET"])
@login_required
def get_seo_articles():
    """Get articles with SEO information for management"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        seo_status = request.args.get('seo_status', '')
        category = request.args.get('category', '')
        
        # Build query
        query = News.query.join(Category).join(User)
        
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
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
        from datetime import datetime, timedelta, timezone
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
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
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        data = request.get_json()
        
        # For now, just return success - this could be extended to store in database
        # In a real implementation, you might want to store these in a settings table
        
        return jsonify({'message': 'Global SEO settings updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_blueprint.route("/api/seo/global-og", methods=["POST"])
@login_required
def update_global_og_settings():
    """Update global Open Graph settings"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        abort(403)
    
    try:
        data = request.get_json()
        
        # For now, just return success - this could be extended to store in database
        
        return jsonify({'message': 'Global OG settings updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_blueprint.route("/api/seo/global-twitter", methods=["POST"])
@login_required
def update_global_twitter_settings():
    """Update global Twitter Card settings"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
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