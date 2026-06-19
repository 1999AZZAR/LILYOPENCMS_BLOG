#!/usr/bin/env python3
"""
Helper script to add sample navigation links for testing
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

from models import NavigationLink, User, UserRole

def add_sample_navigation_links():
    """Add sample navigation links for testing."""
    with app.app_context():
        # Get the first admin user
        admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin_user:
            print("No admin user found. Please create an admin user first.")
            return
        
        # Sample navbar links
        navbar_links = [
            {
                'name': 'Berita',
                'url': '/news',
                'location': 'navbar',
                'order': 1,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Artikel',
                'url': '/articles',
                'location': 'navbar',
                'order': 2,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Video',
                'url': '/videos',
                'location': 'navbar',
                'order': 3,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Galeri',
                'url': '/gallery',
                'location': 'navbar',
                'order': 4,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Tentang',
                'url': '/about',
                'location': 'navbar',
                'order': 5,
                'is_active': True,
                'is_external': False
            }
        ]
        
        # Sample footer links
        footer_links = [
            {
                'name': 'Kebijakan Privasi',
                'url': '/privacy-policy',
                'location': 'footer',
                'order': 1,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Pedoman Media',
                'url': '/media-guidelines',
                'location': 'footer',
                'order': 2,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Kontak',
                'url': '/contact',
                'location': 'footer',
                'order': 3,
                'is_active': True,
                'is_external': False
            },
            {
                'name': 'Facebook',
                'url': 'https://facebook.com',
                'location': 'footer',
                'order': 4,
                'is_active': True,
                'is_external': True
            },
            {
                'name': 'Twitter',
                'url': 'https://twitter.com',
                'location': 'footer',
                'order': 5,
                'is_active': True,
                'is_external': True
            }
        ]
        
        # Add navbar links
        for link_data in navbar_links:
            link = NavigationLink(
                name=link_data['name'],
                url=link_data['url'],
                location=link_data['location'],
                order=link_data['order'],
                is_active=link_data['is_active'],
                is_external=link_data['is_external'],
                user_id=admin_user.id
            )
            db.session.add(link)
            print(f"Added navbar link: {link_data['name']}")
        
        # Add footer links
        for link_data in footer_links:
            link = NavigationLink(
                name=link_data['name'],
                url=link_data['url'],
                location=link_data['location'],
                order=link_data['order'],
                is_active=link_data['is_active'],
                is_external=link_data['is_external'],
                user_id=admin_user.id
            )
            db.session.add(link)
            print(f"Added footer link: {link_data['name']}")
        
        try:
            db.session.commit()
            print("\n✅ Sample navigation links added successfully!")
            print(f"Added {len(navbar_links)} navbar links and {len(footer_links)} footer links")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding navigation links: {e}")

if __name__ == "__main__":
    with app.app_context():
        add_sample_navigation_links() 