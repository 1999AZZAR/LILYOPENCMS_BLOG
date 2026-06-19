#!/usr/bin/env python3
"""
Test script for the subscription system
Creates test users and subscriptions to verify functionality
"""

import sys
import os
# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

from models import User, UserSubscription, UserRole
from datetime import datetime, timezone, timedelta
import json

def create_test_data():
    """Create test users and subscriptions"""
    
    with app.app_context():
        try:
            # Clean up existing test data
            User.query.filter(User.username.like('test_%')).delete()
            db.session.commit()
            
            print("🧪 Testing Subscription System")
            print("=" * 50)
            
            # Create test users
            users = {}
            
            # Regular user
            regular_user = User(
                username='test_regular',
                password_hash='test_hash',
                role=UserRole.GENERAL,
                is_active=True,
                has_premium_access=False,
                ad_preferences={'show_ads': True, 'ad_frequency': 'normal'}
            )
            db.session.add(regular_user)
            users['regular'] = regular_user
            
            # Premium user
            premium_user = User(
                username='test_premium',
                password_hash='test_hash',
                role=UserRole.GENERAL,
                is_active=True,
                has_premium_access=True,
                premium_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                ad_preferences={'show_ads': False, 'ad_frequency': 'none'}
            )
            db.session.add(premium_user)
            users['premium'] = premium_user
            
            # Premium user with ads
            premium_with_ads_user = User(
                username='test_premium_with_ads',
                password_hash='test_hash',
                role=UserRole.GENERAL,
                is_active=True,
                has_premium_access=True,
                premium_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                ad_preferences={'show_ads': True, 'ad_frequency': 'reduced'}
            )
            db.session.add(premium_with_ads_user)
            users['premium_with_ads'] = premium_with_ads_user
            
            # Expired premium user
            expired_user = User(
                username='test_expired',
                password_hash='test_hash',
                role=UserRole.GENERAL,
                is_active=True,
                has_premium_access=False,
                premium_expires_at=datetime.now(timezone.utc) - timedelta(days=1),
                ad_preferences={'show_ads': True, 'ad_frequency': 'normal'}
            )
            db.session.add(expired_user)
            users['expired'] = expired_user
            
            db.session.commit()
            print("✅ Test users created successfully")
            
            # Create test subscriptions
            subscriptions = {}
            
            # Active monthly subscription
            monthly_sub = UserSubscription(
                user_id=users['premium'].id,
                subscription_type='monthly',
                status='active',
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=30),
                payment_provider='test',
                payment_id='test_payment_1',
                amount=99000,
                currency='IDR',
                auto_renew=True
            )
            db.session.add(monthly_sub)
            subscriptions['monthly'] = monthly_sub
            
            # Active yearly subscription
            yearly_sub = UserSubscription(
                user_id=users['premium_with_ads'].id,
                subscription_type='yearly',
                status='active',
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=365),
                payment_provider='test',
                payment_id='test_payment_2',
                amount=990000,
                currency='IDR',
                auto_renew=True
            )
            db.session.add(yearly_sub)
            subscriptions['yearly'] = yearly_sub
            
            # Expired subscription
            expired_sub = UserSubscription(
                user_id=users['expired'].id,
                subscription_type='monthly',
                status='expired',
                start_date=datetime.now(timezone.utc) - timedelta(days=31),
                end_date=datetime.now(timezone.utc) - timedelta(days=1),
                payment_provider='test',
                payment_id='test_payment_3',
                amount=99000,
                currency='IDR',
                auto_renew=False
            )
            db.session.add(expired_sub)
            subscriptions['expired'] = expired_sub
            
            db.session.commit()
            print("✅ Test subscriptions created successfully")
            
            # Test the subscription methods
            print("\n🔍 Testing Subscription Methods:")
            print("-" * 35)
            
            for user_type, user in users.items():
                print(f"\n👤 User: {user.username}")
                print(f"   Premium Access: {user.has_active_premium_subscription()}")
                print(f"   Should Show Ads: {user.should_show_ads()}")
                
                active_sub = user.get_active_subscription()
                print(f"   Active Subscription: {active_sub.subscription_type if active_sub else 'None'}")
                
                if user.ad_preferences:
                    print(f"   Ad Preferences: {user.ad_preferences}")
                else:
                    print(f"   Ad Preferences: None")
            
            print("\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()
            raise

def cleanup_test_data():
    """Clean up test data"""
    
    with app.app_context():
        try:
            User.query.filter(User.username.like('test_%')).delete()
            db.session.commit()
            print("✅ Test data cleaned up successfully")
        except Exception as e:
            print(f"❌ Error cleaning up test data: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_data()
    # Uncomment the line below to clean up test data
    # cleanup_test_data() 