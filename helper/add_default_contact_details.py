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
Add default contact details to the database
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import ContactDetail

def add_default_contact_details():
    """Add default contact details to the database"""
    with app.app_context():
        # Check if contact details already exist
        existing_details = ContactDetail.query.count()
        if existing_details > 0:
            print(f"✅ Contact details already exist ({existing_details} records)")
            return
        
        # Default contact details
        default_details = [
            {
                "title": "Email",
                "content": "info.sindikasimedia@gmail.com",
                "section_order": 1,
                "icon_class": "envelope",
                "link": "mailto:info.sindikasimedia@gmail.com",
                "is_active": True
            },
            {
                "title": "WhatsApp",
                "content": "+62 812-3456-7890",
                "section_order": 2,
                "icon_class": "whatsapp",
                "link": "https://wa.me/6281234567890",
                "is_active": True
            },
            {
                "title": "Alamat",
                "content": "Jl. Contoh No. 123, Jakarta",
                "section_order": 3,
                "icon_class": "map-marker-alt",
                "link": "",
                "is_active": True
            },
            {
                "title": "Telepon",
                "content": "+62 21-1234-5678",
                "section_order": 4,
                "icon_class": "phone",
                "link": "tel:+622112345678",
                "is_active": True
            },
            {
                "title": "Facebook",
                "content": "Sindikasi Media",
                "section_order": 5,
                "icon_class": "facebook",
                "link": "https://facebook.com/sindikasimedia",
                "is_active": True
            },
            {
                "title": "Instagram",
                "content": "@sindikasimedia",
                "section_order": 6,
                "icon_class": "instagram",
                "link": "https://instagram.com/sindikasimedia",
                "is_active": True
            }
        ]
        
        # Add each contact detail
        for detail_data in default_details:
            detail = ContactDetail(**detail_data)
            db.session.add(detail)
        
        try:
            db.session.commit()
            print("✅ Default contact details added successfully!")
            print(f"📝 Added {len(default_details)} contact details")
            
            # Show what was added
            for detail in default_details:
                print(f"  - {detail['title']}: {detail['content']}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding contact details: {e}")
            return False
        
        return True

if __name__ == "__main__":
    print("🔧 Adding default contact details...")
    success = add_default_contact_details()
    if success:
        print("\n🎉 Contact details setup complete!")
        print("💡 You can now manage contact details from the admin panel:")
        print("   Settings > Detail Kontak")
    else:
        print("\n❌ Failed to add contact details")
