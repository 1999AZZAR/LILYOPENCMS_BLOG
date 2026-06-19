from routes import main_blueprint
from .common_imports import *
from models import News, Image, YouTubeVideo, UserActivity, User
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import csv
import io
from optimizations import get_performance_monitor
from optimizations import clear_all_cache, invalidate_cache_pattern
from optimizations import get_asset_optimizer, get_ssr_optimizer

# Real-time visitor tracking
active_visitors = {}

@main_blueprint.route("/api/analytics/visitors", methods=["GET"])
@login_required
def get_visitor_stats():
    """Get real-time visitor count and active users."""
    if not current_user.has_permission("analytics", "read"):
        abort(403)
    
    # Get current active visitors (simple in-memory tracking)
    current_time = datetime.now(timezone.utc)
    active_count = len([v for v in active_visitors.values() if (current_time - v).seconds < 300])  # 5 min timeout
    
    # Get total users online in last 24 hours
    yesterday = current_time - timedelta(days=1)
    recent_visitors = UserActivity.query.filter(
        UserActivity.activity_type == "login",
        UserActivity.created_at >= yesterday
    ).distinct(UserActivity.user_id).count()
    
    return jsonify({
        "active_visitors": active_count,
        "recent_visitors_24h": recent_visitors,
        "total_users": User.query.count(),
        "active_users": User.query.filter_by(is_active=True).count()
    })

@main_blueprint.route("/api/analytics/content", methods=["GET"])
@login_required
def get_content_analytics():
    """Get content analytics with view counts and engagement metrics."""
    if not current_user.has_permission("analytics", "read"):
        abort(403)
    
    # Get date range
    days = request.args.get("days", 30, type=int)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # News analytics
    news_stats = db.session.query(
        func.count(News.id).label('total_news'),
        func.sum(News.read_count).label('total_reads'),
        func.avg(News.read_count).label('avg_reads'),
        func.max(News.read_count).label('max_reads')
    ).filter(
        News.created_at >= start_date,
        News.created_at <= end_date
    ).first()
    
    # Top performing news articles
    top_news = News.query.filter(
        News.created_at >= start_date,
        News.created_at <= end_date
    ).order_by(News.read_count.desc()).limit(10).all()
    
    # Image analytics
    image_stats = db.session.query(
        func.count(Image.id).label('total_images')
    ).filter(
        Image.created_at >= start_date,
        Image.created_at <= end_date
    ).first()
    
    # Video analytics
    video_stats = db.session.query(
        func.count(YouTubeVideo.id).label('total_videos')
    ).filter(
        YouTubeVideo.created_at >= start_date,
        YouTubeVideo.created_at <= end_date
    ).first()
    
    # Content popularity rankings
    popular_content = {
        "news": [{
            "id": news.id,
            "title": news.title,
            "read_count": news.read_count,
            "created_at": news.created_at.isoformat(),
            "author": news.author.username if news.author else "Unknown"
        } for news in top_news],
        "images": db.session.query(Image).filter(
            Image.created_at >= start_date,
            Image.created_at <= end_date
        ).order_by(Image.created_at.desc()).limit(10).all(),
        "videos": db.session.query(YouTubeVideo).filter(
            YouTubeVideo.created_at >= start_date,
            YouTubeVideo.created_at <= end_date
        ).order_by(YouTubeVideo.created_at.desc()).limit(10).all()
    }
    
    return jsonify({
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "news": {
            "total": news_stats.total_news or 0,
            "total_reads": news_stats.total_reads or 0,
            "avg_reads": float(news_stats.avg_reads or 0),
            "max_reads": news_stats.max_reads or 0,
            "top_articles": popular_content["news"]
        },
        "images": {
            "total": image_stats.total_images or 0,
            "avg_downloads": 0  # No download tracking in current model
        },
        "videos": {
            "total": video_stats.total_videos or 0,
            "avg_views": 0  # No view tracking in current model
        }
    })

@main_blueprint.route("/api/analytics/activity", methods=["GET"])
@login_required
def get_activity_logs():
    """Get user activity logs (admin actions, login history)."""
    if not current_user.has_permission("analytics", "read"):
        abort(403)
    
    # Get date range
    days = request.args.get("days", 7, type=int)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get recent activities
    activities = UserActivity.query.filter(
        UserActivity.created_at >= start_date,
        UserActivity.created_at <= end_date
    ).order_by(UserActivity.created_at.desc()).limit(100).all()
    
    # Group activities by type
    activity_summary = db.session.query(
        UserActivity.activity_type,
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.created_at >= start_date,
        UserActivity.created_at <= end_date
    ).group_by(UserActivity.activity_type).all()
    
    return jsonify({
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "activities": [activity.to_dict() for activity in activities],
        "summary": [{
            "type": summary.activity_type,
            "count": summary.count
        } for summary in activity_summary]
    })

@main_blueprint.route("/api/analytics/performance", methods=["GET"])
@login_required
def get_performance_metrics():
    """Get performance metrics (page load times, server response)."""
    if not current_user.has_permission("analytics", "read"):
        abort(403)
    
    # This would typically integrate with monitoring tools
    # For now, we'll provide basic server stats
    import psutil
    import time
    
    # System performance
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Database performance (simple query timing)
    start_time = time.time()
    User.query.count()  # Simple test query
    db_query_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return jsonify({
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "disk_percent": disk.percent,
            "disk_free": disk.free
        },
        "database": {
            "query_time_ms": round(db_query_time, 2)
        },
        "server": {
            "uptime": time.time() - psutil.boot_time(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })

@main_blueprint.route("/api/analytics/export", methods=["POST"])
@login_required
def export_analytics_report():
    """Export analytics reports (CSV/PDF for content performance, user stats)."""
    if not current_user.has_permission("analytics", "export"):
        abort(403)
    
    data = request.get_json()
    report_type = data.get("type", "content")
    days = data.get("days", 30)
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    if report_type == "content":
        return export_content_report(start_date, end_date)
    elif report_type == "users":
        return export_user_report(start_date, end_date)
    elif report_type == "activity":
        return export_activity_report(start_date, end_date)
    else:
        return jsonify({"error": "Invalid report type"}), 400

def export_content_report(start_date, end_date):
    """Export content performance report."""
    # Get content data
    news_articles = News.query.filter(
        News.created_at >= start_date,
        News.created_at <= end_date
    ).all()
    
    images = Image.query.filter(
        Image.created_at >= start_date,
        Image.created_at <= end_date
    ).all()
    
    videos = YouTubeVideo.query.filter(
        YouTubeVideo.created_at >= start_date,
        YouTubeVideo.created_at <= end_date
    ).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Content Performance Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    ])
    writer.writerow([])
    
    # News section
    writer.writerow(["News Articles"])
    writer.writerow(["Title", "Author", "Read Count", "Created Date", "Status"])
    for news in news_articles:
        writer.writerow([
            news.title,
            news.user.username if news.user else "Unknown",
            news.read_count,
            news.created_at.strftime('%Y-%m-%d'),
            "Published" if news.is_published else "Draft"
        ])
    
    writer.writerow([])
    
    # Images section
    writer.writerow(["Images"])
    writer.writerow(["Filename", "Uploader", "Download Count", "Upload Date"])
    for image in images:
        writer.writerow([
            image.filename,
            image.user.username if image.user else "Unknown",
            0,  # No download tracking in current model
            image.created_at.strftime('%Y-%m-%d')
        ])
    
    writer.writerow([])
    
    # Videos section
    writer.writerow(["Videos"])
    writer.writerow(["Title", "Uploader", "View Count", "Upload Date"])
    for video in videos:
        writer.writerow([
            video.title,
            video.uploader.username if video.uploader else "Unknown",
            0,  # No view tracking in current model
            video.created_at.strftime('%Y-%m-%d')
        ])
    
    output.seek(0)
    
    # Record export activity
    current_user.record_activity(
        "export_analytics",
        f"Exported content performance report",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=content_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

def export_user_report(start_date, end_date):
    """Export user statistics report."""
    users = User.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "User Statistics Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    ])
    writer.writerow([])
    
    # User data
    writer.writerow(["Username", "Full Name", "Role", "Status", "Last Login", "Login Count", "News Created", "Images Uploaded", "Videos Uploaded"])
    
    for user in users:
        # Get user's content counts
        news_count = News.query.filter_by(user_id=user.id).count()
        image_count = Image.query.filter_by(user_id=user.id).count()
        video_count = YouTubeVideo.query.filter_by(user_id=user.id).count()
        
        writer.writerow([
            user.username,
            user.get_full_name(),
            user.role.value,
            "Active" if user.is_active else "Inactive",
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else "Never",
            user.login_count,
            news_count,
            image_count,
            video_count
        ])
    
    output.seek(0)
    
    # Record export activity
    current_user.record_activity(
        "export_analytics",
        f"Exported user statistics report",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=user_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

def export_activity_report(start_date, end_date):
    """Export activity logs report."""
    activities = UserActivity.query.filter(
        UserActivity.created_at >= start_date,
        UserActivity.created_at <= end_date
    ).order_by(UserActivity.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Activity Log Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    ])
    writer.writerow([])
    
    # Activity data
    writer.writerow(["Timestamp", "User", "Activity Type", "Description", "IP Address"])
    
    for activity in activities:
        writer.writerow([
            activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            activity.user.username if activity.user else "Unknown",
            activity.activity_type,
            activity.description or "",
            activity.ip_address or ""
        ])
    
    output.seek(0)
    
    # Record export activity
    current_user.record_activity(
        "export_analytics",
        f"Exported activity log report",
        request.remote_addr,
        request.headers.get("User-Agent")
    )
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=activity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@main_blueprint.route("/api/analytics/dashboard", methods=["GET"])
@login_required
def get_dashboard_summary():
    """Get monthly/weekly dashboard summaries."""
    if not current_user.has_permission("analytics", "read"):
        abort(403)
    
    # Get current period
    end_date = datetime.now(timezone.utc)
    week_start = end_date - timedelta(days=7)
    month_start = end_date - timedelta(days=30)
    
    # Weekly stats
    weekly_news = News.query.filter(
        News.created_at >= week_start,
        News.created_at <= end_date
    ).count()
    
    weekly_images = Image.query.filter(
        Image.created_at >= week_start,
        Image.created_at <= end_date
    ).count()
    
    weekly_videos = YouTubeVideo.query.filter(
        YouTubeVideo.created_at >= week_start,
        YouTubeVideo.created_at <= end_date
    ).count()
    
    weekly_users = UserActivity.query.filter(
        UserActivity.activity_type == "login",
        UserActivity.created_at >= week_start,
        UserActivity.created_at <= end_date
    ).distinct(UserActivity.user_id).count()
    
    # Monthly stats
    monthly_news = News.query.filter(
        News.created_at >= month_start,
        News.created_at <= end_date
    ).count()
    
    monthly_images = Image.query.filter(
        Image.created_at >= month_start,
        Image.created_at <= end_date
    ).count()
    
    monthly_videos = YouTubeVideo.query.filter(
        YouTubeVideo.created_at >= month_start,
        YouTubeVideo.created_at <= end_date
    ).count()
    
    monthly_users = UserActivity.query.filter(
        UserActivity.activity_type == "login",
        UserActivity.created_at >= month_start,
        UserActivity.created_at <= end_date
    ).distinct(UserActivity.user_id).count()
    
    # Top content this week
    top_news_week = News.query.filter(
        News.created_at >= week_start,
        News.created_at <= end_date
    ).order_by(News.read_count.desc()).limit(5).all()
    
    return jsonify({
        "weekly": {
            "news_created": weekly_news,
            "images_uploaded": weekly_images,
            "videos_uploaded": weekly_videos,
            "active_users": weekly_users,
            "top_news": [{
                "title": news.title,
                "read_count": news.read_count,
                "author": news.author.username if news.author else "Unknown"
            } for news in top_news_week]
        },
        "monthly": {
            "news_created": monthly_news,
            "images_uploaded": monthly_images,
            "videos_uploaded": monthly_videos,
            "active_users": monthly_users
        },
        "totals": {
            "total_users": User.query.count(),
            "total_news": News.query.count(),
            "total_images": Image.query.count(),
            "total_videos": YouTubeVideo.query.count()
        }
    })

# Track visitor activity
@main_blueprint.route("/api/analytics/track", methods=["POST"])
def track_visitor():
    """Track visitor activity for real-time analytics."""
    data = request.get_json()
    visitor_id = data.get("visitor_id")
    
    if visitor_id:
        active_visitors[visitor_id] = datetime.now(timezone.utc)
    
    return jsonify({"status": "tracked"}) 

@main_blueprint.route("/admin/performance")
@login_required
def performance_dashboard():
    """Performance monitoring dashboard"""
    if not current_user.has_permission('analytics', 'read'):
        flash("You don't have permission to access performance analytics.", "error")
        return redirect(url_for("main.dashboard"))
    
    try:
        # Get performance monitor
        monitor = get_performance_monitor()
        if monitor:
            performance_summary = monitor.get_performance_summary()
            slow_queries = monitor.get_slow_queries(threshold=1.0)
        else:
            performance_summary = {'total_requests': 0, 'routes': {}, 'system': {}}
            slow_queries = {}
        
        return render_template(
            "settings/performance_dashboard.html",
            performance_summary=performance_summary,
            slow_queries=slow_queries
        )
    except Exception as e:
        flash(f"Error loading performance data: {str(e)}", "error")
        return redirect(url_for("main.dashboard"))

@main_blueprint.route("/admin/performance/clear-cache", methods=["POST"])
@login_required
def clear_cache():
    """Clear all cache"""
    if not current_user.has_permission('settings', 'update'):
        flash("You don't have permission to clear cache.", "error")
        return redirect(url_for("main.performance_dashboard"))
    
    try:
        success = clear_all_cache()
        if success:
            flash("Cache cleared successfully.", "success")
        else:
            flash("Failed to clear cache.", "error")
    except Exception as e:
        flash(f"Error clearing cache: {str(e)}", "error")
    
    return redirect(url_for("main.performance_dashboard"))

@main_blueprint.route("/admin/performance/invalidate-cache/<pattern>", methods=["POST"])
@login_required
def invalidate_cache(pattern):
    """Invalidate cache by pattern"""
    if not current_user.has_permission('admin'):
        flash("Access denied. Admin permissions required.", "error")
        return redirect(url_for("main.performance_dashboard"))
    
    try:
        invalidate_cache_pattern(pattern)
        flash(f"Cache invalidated for pattern: {pattern}", "success")
    except Exception as e:
        flash(f"Error invalidating cache: {str(e)}", "error")
    
    return redirect(url_for("main.performance_dashboard"))

@main_blueprint.route("/admin/performance/asset-optimization")
@login_required
def asset_optimization_dashboard():
    """Asset optimization dashboard"""
    if not current_user.has_permission('admin'):
        flash("Access denied. Admin permissions required.", "error")
        return redirect(url_for("main.home"))
    
    try:
        # Get asset optimization stats
        asset_optimizer = get_asset_optimizer()
        asset_stats = asset_optimizer.get_optimization_stats()
        
        return render_template(
            "settings/asset_optimization_dashboard.html",
            asset_stats=asset_stats
        )
    except Exception as e:
        flash(f"Error loading asset optimization dashboard: {str(e)}", "error")
        return redirect(url_for("main.performance_dashboard"))

@main_blueprint.route("/admin/performance/ssr-optimization")
@login_required
def ssr_optimization_dashboard():
    """SSR optimization dashboard"""
    if not current_user.has_permission('admin'):
        flash("Access denied. Admin permissions required.", "error")
        return redirect(url_for("main.home"))
    
    try:
        # Get SSR optimization stats
        ssr_optimizer = get_ssr_optimizer()
        ssr_stats = ssr_optimizer.get_render_stats()
        
        return render_template(
            "settings/ssr_optimization_dashboard.html",
            ssr_stats=ssr_stats
        )
    except Exception as e:
        flash(f"Error loading SSR optimization dashboard: {str(e)}", "error")
        return redirect(url_for("main.performance_dashboard"))

@main_blueprint.route("/admin/performance/precompile-assets", methods=["POST"])
@login_required
def precompile_assets():
    """Precompile and cache assets"""
    if not current_user.has_permission('admin'):
        flash("Access denied. Admin permissions required.", "error")
        return redirect(url_for("main.asset_optimization_dashboard"))
    
    try:
        asset_optimizer = get_asset_optimizer()
        compiled_assets = asset_optimizer.compress_assets()
        
        flash(f"Successfully precompiled {len(compiled_assets)} assets", "success")
    except Exception as e:
        flash(f"Error precompiling assets: {str(e)}", "error")
    
    return redirect(url_for("main.asset_optimization_dashboard"))

@main_blueprint.route("/admin/performance/clear-template-cache", methods=["POST"])
@login_required
def clear_template_cache():
    """Clear template cache"""
    if not current_user.has_permission('admin'):
        flash("Access denied. Admin permissions required.", "error")
        return redirect(url_for("main.ssr_optimization_dashboard"))
    
    try:
        ssr_optimizer = get_ssr_optimizer()
        ssr_optimizer.clear_template_cache()
        
        flash("Template cache cleared successfully", "success")
    except Exception as e:
        flash(f"Error clearing template cache: {str(e)}", "error")
    
    return redirect(url_for("main.ssr_optimization_dashboard")) 