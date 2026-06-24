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
Script to manually add subscription fields to the database
This bypasses the migration system to fix the current issue
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

from sqlalchemy import text

def add_subscription_fields():
    """Add subscription fields to the user table and create user_subscriptions table"""
    
    with app.app_context():
        try:
            # Check if fields already exist
            result = db.session.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result.fetchall()]
            
            print("Current user table columns:", columns)
            
            # Add subscription fields to user table if they don't exist
            if 'has_premium_access' not in columns:
                print("Adding has_premium_access column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN has_premium_access BOOLEAN NOT NULL DEFAULT 0"))
            
            if 'premium_expires_at' not in columns:
                print("Adding premium_expires_at column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN premium_expires_at DATETIME"))
            
            if 'ad_preferences' not in columns:
                print("Adding ad_preferences column...")
                db.session.execute(text("ALTER TABLE user ADD COLUMN ad_preferences TEXT"))
            
            # Check if user_subscriptions table exists
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_subscriptions'"))
            if not result.fetchone():
                print("Creating user_subscriptions table...")
                db.session.execute(text("""
                    CREATE TABLE user_subscriptions (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        subscription_type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) NOT NULL DEFAULT 'active',
                        start_date DATETIME NOT NULL,
                        end_date DATETIME NOT NULL,
                        payment_provider VARCHAR(50),
                        payment_id VARCHAR(255),
                        amount NUMERIC(10,2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'IDR',
                        auto_renew BOOLEAN DEFAULT 1,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                """))
                
                # Create indexes
                db.session.execute(text("CREATE INDEX ix_user_subscriptions_user_id ON user_subscriptions (user_id)"))
                db.session.execute(text("CREATE INDEX ix_user_subscriptions_status ON user_subscriptions (status)"))
                db.session.execute(text("CREATE INDEX ix_user_subscriptions_end_date ON user_subscriptions (end_date)"))
            
            db.session.commit()
            print("✅ Subscription fields added successfully!")
            
            # Verify the changes
            result = db.session.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result.fetchall()]
            print("Updated user table columns:", columns)
            
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_subscriptions'"))
            if result.fetchone():
                print("✅ user_subscriptions table created successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_subscription_fields()
