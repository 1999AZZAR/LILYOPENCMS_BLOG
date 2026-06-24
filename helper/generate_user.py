"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import sys
import os
from datetime import datetime, timedelta, timezone

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

from models import db, User, UserRole, CustomRole
from werkzeug.security import generate_password_hash

# Import app from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app

# List of users to create
users = [
    {"username": "suadmin", "role": UserRole.SUPERUSER, "is_premium": True, "custom_role": "System Administrator"},
    {"username": "admin0", "role": UserRole.ADMIN},
    {"username": "admin1", "role": UserRole.ADMIN},
    {"username": "admin2", "role": UserRole.ADMIN},
    {"username": "admin3", "role": UserRole.ADMIN},
    {"username": "admin4", "role": UserRole.ADMIN},
    {"username": "general0", "role": UserRole.GENERAL},
    {"username": "general1", "role": UserRole.GENERAL},
    {"username": "general2", "role": UserRole.GENERAL},
    {"username": "general3", "role": UserRole.GENERAL},
    {"username": "general4", "role": UserRole.GENERAL},
]

# Passwords for different roles
role_passwords = {
    UserRole.SUPERUSER: generate_password_hash("suladang"),
    UserRole.ADMIN: generate_password_hash("admin_password"),
    UserRole.GENERAL: generate_password_hash("general_password")
}

# Insert users into the database
with app.app_context():
    print("👥 LilyOpenCMS User Generator")
    print("=" * 50)
    
    # Create tables if they don't exist (ensures the 'user' table is present)
    db.create_all()
    
    added_count = 0
    skipped_count = 0
    
    for user_data in users:
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if not existing_user:
            # Set premium status for superuser
            is_premium = user_data.get("is_premium", False)
            has_premium_access = is_premium
            premium_expires_at = None
            
            if is_premium:
                # Set premium to expire in 1 year from now
                premium_expires_at = datetime.now(timezone.utc) + timedelta(days=365)
            
            new_user = User(
                username=user_data["username"],
                password_hash=role_passwords[user_data["role"]],
                role=user_data["role"],
                verified=True,
                is_active=True,
                is_premium=is_premium,
                has_premium_access=has_premium_access,
                premium_expires_at=premium_expires_at,
            )
            db.session.add(new_user)
            db.session.flush()  # Flush to get the user ID
            
            # Assign custom role if specified
            if "custom_role" in user_data:
                custom_role_name = user_data["custom_role"]
                custom_role = CustomRole.query.filter_by(name=custom_role_name).first()
                if custom_role:
                    new_user.custom_role = custom_role
                    print(f"  ✅ Created user: {user_data['username']} ({user_data['role'].value}) (Premium) - Assigned to {custom_role_name}")
                else:
                    print(f"  ⚠️ Warning: Custom role '{custom_role_name}' not found for {user_data['username']}")
                    print(f"  ✅ Created user: {user_data['username']} ({user_data['role'].value}) (Premium)")
            else:
                premium_status = " (Premium)" if is_premium else ""
                print(f"  ✅ Created user: {user_data['username']} ({user_data['role'].value}){premium_status}")
            
            added_count += 1
        else:
            # Update existing superuser to be premium and assign custom role if not already
            updated = False
            if user_data["username"] == "suadmin":
                if not existing_user.is_premium:
                    existing_user.is_premium = True
                    existing_user.has_premium_access = True
                    existing_user.premium_expires_at = datetime.now(timezone.utc) + timedelta(days=365)
                    updated = True
                
                # Assign System Administrator role if not already assigned
                if "custom_role" in user_data and not existing_user.custom_role:
                    custom_role_name = user_data["custom_role"]
                    custom_role = CustomRole.query.filter_by(name=custom_role_name).first()
                    if custom_role:
                        existing_user.custom_role = custom_role
                        updated = True
                        print(f"  🔄 Updated existing user: {user_data['username']} (now Premium + {custom_role_name})")
                    else:
                        print(f"  ⚠️ Warning: Custom role '{custom_role_name}' not found for {user_data['username']}")
                        if updated:
                            print(f"  🔄 Updated existing user: {user_data['username']} (now Premium)")
                elif updated:
                    print(f"  🔄 Updated existing user: {user_data['username']} (now Premium)")
                
                if updated:
                    added_count += 1
                else:
                    print(f"  ⏭️ Skipped existing user: {user_data['username']}")
                    skipped_count += 1
            else:
                print(f"  ⏭️ Skipped existing user: {user_data['username']}")
                skipped_count += 1
    
    db.session.commit()
    print("-" * 50)
    print(f"✅ User generation complete!")
    print(f"   Added: {added_count} users")
    if skipped_count > 0:
        print(f"   Skipped: {skipped_count} existing users")
    print("")
    print("🔐 Default Passwords:")
    print("   Superuser (suladang): suladang")
    print("   Admin: admin_password")
    print("   General: general_password")
    print("")
    print("💎 Premium Status:")
    print("   Superuser (suadmin): Premium (1 year)")
    print("")
    print("👑 Role Assignment:")
    print("   Superuser (suadmin): System Administrator (all permissions)")
