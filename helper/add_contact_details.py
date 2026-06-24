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
Add sample contact details for the about page.
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

from models import ContactDetail
from datetime import datetime

def add_contact_details():
    """Add sample contact details."""
    print("📞 Adding Contact Details")
    print("=" * 50)
    
    # Clear existing contact details
    ContactDetail.query.delete()
    
    contact_details = [
        {
            "title": "Email",
            "content": "info@kantorcerita.id",
            "section_order": 1,
            "icon_class": "envelope",
            "link": "mailto:info@kantorcerita.id",
        },
        {
            "title": "Telepon",
            "content": "+62 21 1234 5678",
            "section_order": 2,
            "icon_class": "phone",
            "link": "tel:+622112345678",
        },
        {
            "title": "Alamat",
            "content": "Jl. Sudirman No. 123, Jakarta Pusat, DKI Jakarta 12345",
            "section_order": 3,
            "icon_class": "map-marker",
            "link": None,
        },
        {
            "title": "Website",
            "content": "www.kantorcerita.id",
            "section_order": 4,
            "icon_class": "globe",
            "link": "https://www.kantorcerita.id",
        },
    ]
    
    for detail in contact_details:
        record = ContactDetail(
            title=detail["title"],
            content=detail["content"],
            section_order=detail["section_order"],
            icon_class=detail["icon_class"],
            link=detail["link"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(record)
        print(f"✅ Added: {detail['title']}")
    
    try:
        db.session.commit()
        print("-" * 50)
        print("✅ Successfully added contact details!")
    except Exception as e:
        print(f"❌ Error adding contact details: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    with app.app_context():
        add_contact_details()
