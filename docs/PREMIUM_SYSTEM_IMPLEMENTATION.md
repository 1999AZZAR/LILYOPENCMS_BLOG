# Premium Content & Subscription System Implementation

## Overview

This document outlines the comprehensive implementation of the premium content and subscription system for LilyOpenCMS. The system provides:

- **Premium Content Access Control**: Restrict access to premium articles based on user subscription status
- **Ad-Free Experience**: Premium users can disable ads based on their preferences
- **Subscription Management**: Complete subscription lifecycle management with payment tracking
- **User Preferences**: Flexible ad preferences for premium users

## 🏗️ Database Schema

### New Models

#### UserSubscription Model
```python
class UserSubscription(db.Model):
    __tablename__ = "user_subscriptions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subscription_type = db.Column(db.String(50), nullable=False)  # 'monthly', 'yearly'
    status = db.Column(db.String(50), nullable=False, default='active')
    start_date = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    payment_provider = db.Column(db.String(50))  # 'stripe', 'paypal', etc.
    payment_id = db.Column(db.String(255))  # External payment ID
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='IDR')
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=default_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=default_utcnow, onupdate=default_utcnow, nullable=False)
```

#### Enhanced User Model
Added subscription-related fields to the existing User model:
```python
# Subscription-related fields
has_premium_access = db.Column(db.Boolean, default=False, nullable=False)
premium_expires_at = db.Column(db.DateTime)
ad_preferences = db.Column(db.JSON, default=lambda: {"show_ads": True, "ad_frequency": "normal"})

# Relationships
subscriptions = db.relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
```

## 🔧 API Endpoints

### Subscription Management

#### Get Available Plans
```
GET /api/subscriptions/plans
```
Returns available subscription plans with pricing and features.

#### Create Subscription
```
POST /api/subscriptions/create
```
Creates a new subscription for the current user.

**Request Body:**
```json
{
  "plan_type": "monthly",
  "payment_provider": "manual",
  "payment_id": "payment_123",
  "auto_renew": true
}
```

#### Cancel Subscription
```
POST /api/subscriptions/cancel
```
Cancels the user's active subscription.

#### Get Subscription Status
```
GET /api/subscriptions/status
```
Returns the current user's subscription status and preferences.

#### Update Ad Preferences
```
POST /api/subscriptions/update-ad-preferences
```
Updates user's ad display preferences.

**Request Body:**
```json
{
  "show_ads": false,
  "ad_frequency": "none"
}
```

#### Check Premium Access
```
GET /api/subscriptions/check-premium-access
```
Checks if the current user has premium access (for content access control).

### Admin Endpoints

#### Get All Subscriptions
```
GET /api/admin/subscriptions
```
Returns all subscriptions with pagination (admin only).

#### Update Subscription
```
PUT /api/admin/subscriptions/<subscription_id>
```
Updates a subscription (admin only).

## 🎨 Frontend Implementation

### Enhanced Ads Injection System

The `ads-injection.js` file has been enhanced to respect user preferences:

```javascript
// Check user preferences before showing ads
async function checkUserPreferences() {
    const response = await fetch('/api/subscriptions/check-premium-access');
    const data = await response.json();
    userHasPremiumAccess = data.has_premium_access;
    userShouldShowAds = data.should_show_ads;
}

// Don't inject ads if user has premium access and doesn't want ads
if (userHasPremiumAccess && !userShouldShowAds) {
    return;
}
```

### Premium Content Access Control

The reader template (`templates/public/reader.html`) now includes:

1. **Premium Content Check**: Shows a premium upgrade prompt for premium articles
2. **Dynamic Content Display**: Hides content for non-premium users
3. **Premium Badge**: Shows premium badge for users with access

```html
<!-- Premium Content Check -->
{% if news.is_premium %}
  <div id="premium-content-check" class="mb-8 p-6 bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20 rounded-lg">
    <h3 class="text-lg font-semibold text-foreground">Konten Premium</h3>
    <p class="text-muted-foreground mb-4">Artikel ini memerlukan langganan premium untuk diakses.</p>
    <div class="flex flex-wrap gap-3">
      <a href="{{ url_for('main.premium') }}" class="button button-primary">Berlangganan Premium</a>
      <a href="{{ url_for('main.login') }}" class="button button-outline">Login</a>
    </div>
  </div>
{% endif %}
```

## 🔐 Access Control

### Premium Content Decorator

A decorator is available for protecting premium content:

```python
@require_premium_access
def premium_content_route():
    # This route requires premium access
    pass
```

### User Methods

The User model includes several methods for checking premium status:

```python
def has_active_premium_subscription(self):
    """Check if user has an active premium subscription."""
    
def get_active_subscription(self):
    """Get the user's active subscription if any."""
    
def should_show_ads(self):
    """Check if ads should be shown to this user based on their preferences."""
```

## 💰 Subscription Plans

### Available Plans

```python
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
```

## 🧪 Testing

### Test Script

A comprehensive test script is available at `helper/test_subscription_system.py`:

```bash
# Create test data
python helper/test_subscription_system.py

# Clean up test data
python helper/test_subscription_system.py --cleanup
```

The test script creates:
- Regular user (no premium access)
- Premium user (monthly subscription, no ads)
- Premium user with ads enabled
- Expired premium user

## 📊 Database Migration

### Migration File

The database migration is located at `migrations/versions/add_subscription_system.py` and includes:

1. **New Columns in User Table**:
   - `has_premium_access` (Boolean)
   - `premium_expires_at` (DateTime)
   - `ad_preferences` (JSON)

2. **New UserSubscription Table**:
   - Complete subscription tracking
   - Payment information
   - Subscription lifecycle management

3. **Indexes for Performance**:
   - User ID index
   - Status index
   - End date index

## 🚀 Usage Examples

### Creating a Premium Article

```python
# In the admin interface or API
news = News(
    title="Premium Article",
    content="This is premium content...",
    is_premium=True,  # Mark as premium
    is_visible=True
)
```

### Checking Premium Access in Templates

```html
{% if news.is_premium %}
  <!-- Show premium content check for non-premium users -->
  <div id="premium-content-check">
    <!-- Premium upgrade prompt -->
  </div>
{% endif %}
```

### Checking Premium Access in JavaScript

```javascript
// Check if user has premium access
const response = await fetch('/api/subscriptions/check-premium-access');
const data = await response.json();

if (data.has_premium_access) {
    // Show premium content
    showPremiumContent();
} else {
    // Show upgrade prompt
    showUpgradePrompt();
}
```

## 🔄 Workflow

### Premium Content Access Flow

1. **User visits premium article**
2. **System checks user's premium status**
3. **If premium user**: Show content with premium badge
4. **If non-premium user**: Show upgrade prompt
5. **User can subscribe or login**

### Ad Display Flow

1. **Page loads**
2. **System checks user's ad preferences**
3. **If premium user with ads disabled**: Hide all ads
4. **If regular user or premium user with ads enabled**: Show ads normally

### Subscription Management Flow

1. **User visits premium page**
2. **User selects subscription plan**
3. **System creates subscription record**
4. **User gets premium access immediately**
5. **System tracks subscription lifecycle**

## 🛡️ Security Considerations

1. **Access Control**: Premium content is protected at both frontend and backend
2. **Session Management**: Premium status is checked on each request
3. **Data Validation**: All subscription data is validated before processing
4. **Audit Trail**: Subscription changes are logged for admin review

## 📈 Performance Optimizations

1. **Caching**: User preferences are cached to reduce database queries
2. **Indexes**: Database indexes on frequently queried fields
3. **Lazy Loading**: Premium content checks are performed asynchronously
4. **Minimal Queries**: Efficient queries to check premium status

## 🔮 Future Enhancements

1. **Payment Gateway Integration**: Stripe, PayPal integration
2. **Advanced Analytics**: Revenue tracking and user behavior analysis
3. **Tiered Subscriptions**: Multiple premium tiers with different features
4. **Trial Periods**: Free trial for new subscribers
5. **Referral System**: User referral rewards
6. **Content Recommendations**: Premium content recommendations based on user preferences

## 📝 Configuration

### Environment Variables

```bash
# Payment provider configuration (future)
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Subscription settings
DEFAULT_SUBSCRIPTION_CURRENCY=IDR
SUBSCRIPTION_AUTO_RENEW=true
```

### Admin Settings

The system includes admin endpoints for:
- Viewing all subscriptions
- Managing subscription status
- Updating subscription details
- Revenue reporting

## ✅ Testing Checklist

- [x] Premium content access control
- [x] Ad-free experience for premium users
- [x] Subscription creation and management
- [x] User preference updates
- [x] Admin subscription management
- [x] Database migration
- [x] Frontend integration
- [x] API endpoint testing
- [x] Error handling
- [x] Security validation

## 🎯 Success Metrics

- **User Engagement**: Premium content read rates
- **Conversion Rate**: Free to premium user conversion
- **Revenue**: Monthly recurring revenue from subscriptions
- **User Satisfaction**: Ad-free experience satisfaction
- **Content Quality**: Premium content performance metrics

---

*This implementation provides a solid foundation for monetizing content while maintaining a good user experience for both free and premium users.* 