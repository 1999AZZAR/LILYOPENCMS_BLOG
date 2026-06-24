"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from routes import main_blueprint
from .common_imports import *
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    'monthly': {
        'name': 'Paket Bulanan',
        'price': Decimal('99000'),  # 99,000 IDR
        'duration_days': 30,
        'features': ['Akses artikel premium', 'Pengalaman bebas iklan', 'Konten eksklusif']
    },
    'yearly': {
        'name': 'Paket Tahunan',
        'price': Decimal('990000'),  # 990,000 IDR (16% discount)
        'duration_days': 365,
        'features': ['Akses artikel premium', 'Pengalaman bebas iklan', 'Konten eksklusif', 'Diskon 16%']
    }
}

@main_blueprint.route("/api/subscriptions/plans", methods=["GET"])
def get_subscription_plans():
    """Get available subscription plans."""
    return jsonify(SUBSCRIPTION_PLANS)

@main_blueprint.route("/api/subscriptions/create", methods=["POST"])
@login_required
def create_subscription():
    """Create a new subscription for the current user."""
    if not current_user.verified:
        return jsonify({"error": "Account must be verified to subscribe"}), 403
    
    data = request.get_json() or {}
    plan_type = data.get('plan_type')
    payment_provider = data.get('payment_provider', 'manual')  # For now, manual payment
    
    if not plan_type or plan_type not in SUBSCRIPTION_PLANS:
        return jsonify({"error": "Invalid plan type"}), 400
    
    plan = SUBSCRIPTION_PLANS[plan_type]
    
    # Check if user already has an active subscription
    active_subscription = current_user.get_active_subscription()
    if active_subscription:
        return jsonify({"error": "User already has an active subscription"}), 400
    
    try:
        # Calculate subscription dates
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=plan['duration_days'])
        
        # Create subscription record
        subscription = UserSubscription(
            user_id=current_user.id,
            subscription_type=plan_type,
            status='active',
            start_date=start_date,
            end_date=end_date,
            payment_provider=payment_provider,
            payment_id=data.get('payment_id'),
            amount=plan['price'],
            currency='IDR',
            auto_renew=data.get('auto_renew', True)
        )
        
        # Update user's premium access
        current_user.has_premium_access = True
        current_user.premium_expires_at = end_date
        
        db.session.add(subscription)
        db.session.commit()
        
        current_app.logger.info(
            f"Subscription created for user {current_user.username}: {plan_type} plan"
        )
        
        return jsonify({
            "message": "Subscription created successfully",
            "subscription": subscription.to_dict(),
            "user": current_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating subscription: {e}")
        return jsonify({"error": "Failed to create subscription"}), 500

@main_blueprint.route("/api/subscriptions/cancel", methods=["POST"])
@login_required
def cancel_subscription():
    """Cancel the user's active subscription."""
    active_subscription = current_user.get_active_subscription()
    
    if not active_subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    try:
        active_subscription.status = 'cancelled'
        active_subscription.auto_renew = False
        
        # Don't immediately revoke access - let it expire naturally
        # current_user.has_premium_access = False
        # current_user.premium_expires_at = None
        
        db.session.commit()
        
        current_app.logger.info(
            f"Subscription cancelled for user {current_user.username}"
        )
        
        return jsonify({
            "message": "Subscription cancelled successfully",
            "subscription": active_subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling subscription: {e}")
        return jsonify({"error": "Failed to cancel subscription"}), 500

@main_blueprint.route("/api/subscriptions/status", methods=["GET"])
@login_required
def get_subscription_status():
    """Get the current user's subscription status."""
    active_subscription = current_user.get_active_subscription()
    
    return jsonify({
        "has_premium_access": current_user.has_active_premium_subscription(),
        "premium_expires_at": current_user.premium_expires_at.isoformat() if current_user.premium_expires_at else None,
        "active_subscription": active_subscription.to_dict() if active_subscription else None,
        "ad_preferences": current_user.ad_preferences
    })

@main_blueprint.route("/api/subscriptions/update-ad-preferences", methods=["POST"])
@login_required
def update_ad_preferences():
    """Update user's ad preferences."""
    data = request.get_json() or {}
    
    if not current_user.ad_preferences:
        current_user.ad_preferences = {}
    
    # Update ad preferences
    for key, value in data.items():
        if key in ['show_ads', 'ad_frequency']:
            current_user.ad_preferences[key] = value
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Ad preferences updated successfully",
            "ad_preferences": current_user.ad_preferences
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ad preferences: {e}")
        return jsonify({"error": "Failed to update ad preferences"}), 500

@main_blueprint.route("/api/subscriptions/check-premium-access", methods=["GET"])
def check_premium_access():
    """Check if the current user has premium access (for content access control)."""
    if not current_user.is_authenticated:
        return jsonify({"has_premium_access": False, "reason": "not_logged_in"})
    
    has_access = current_user.has_active_premium_subscription()
    
    return jsonify({
        "has_premium_access": has_access,
        "premium_expires_at": current_user.premium_expires_at.isoformat() if current_user.premium_expires_at else None,
        "should_show_ads": current_user.should_show_ads()
    })

# Premium content access control decorator
def require_premium_access(f):
    """Decorator to require premium access for certain content."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Silakan login untuk mengakses konten premium", "warning")
            return redirect(url_for('main.login'))
        
        if not current_user.has_active_premium_subscription():
            flash("Konten ini memerlukan langganan premium", "warning")
            return redirect(url_for('main.premium'))
        
        return f(*args, **kwargs)
    return decorated_function

# Admin routes for subscription management
@main_blueprint.route("/api/admin/subscriptions", methods=["GET"])
@login_required
def admin_get_subscriptions():
    """Get all subscriptions (admin only)."""
    if not current_user.has_permission("subscriptions", "read"):
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    subscriptions_query = UserSubscription.query.order_by(UserSubscription.created_at.desc())
    subscriptions = subscriptions_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "subscriptions": [sub.to_dict() for sub in subscriptions.items],
        "pagination": {
            "page": subscriptions.page,
            "pages": subscriptions.pages,
            "per_page": subscriptions.per_page,
            "total": subscriptions.total,
            "has_next": subscriptions.has_next,
            "has_prev": subscriptions.has_prev
        }
    })

@main_blueprint.route("/api/admin/subscriptions/<int:subscription_id>", methods=["PUT"])
@login_required
def admin_update_subscription(subscription_id):
    """Update a subscription (admin only)."""
    if not current_user.has_permission("subscriptions", "update"):
        abort(403)
    
    subscription = UserSubscription.query.get_or_404(subscription_id)
    data = request.get_json() or {}
    
    try:
        # Update allowed fields
        if 'status' in data:
            subscription.status = data['status']
        
        if 'auto_renew' in data:
            subscription.auto_renew = data['auto_renew']
        
        if 'end_date' in data:
            subscription.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        db.session.commit()
        
        return jsonify({
            "message": "Subscription updated successfully",
            "subscription": subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating subscription: {e}")
        return jsonify({"error": "Failed to update subscription"}), 500
