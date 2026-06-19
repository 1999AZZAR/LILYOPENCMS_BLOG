#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=== LilyOpenCMS Deployment Setup ==="
echo "Project root: $PROJECT_ROOT"
echo "This script sets up the essential structure for deployment"
echo ""

# Check for required Python packages
echo "=== Checking Dependencies ==="
python -c "
try:
    import requests, faker
    from PIL import Image
    print('✅ All required packages are available')
except ImportError as e:
    print(f'❌ Missing package: {e}')
    print('Please install with: pip install -r helper/requirements-helper.txt')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Please install missing dependencies and try again."
    exit 1
fi

# Ensure database schema is up to date
echo ""
echo "=== Setting up Database Schema ==="
python -c "
from models import db
from main import app
app.app_context().push()
db.create_all()
print('✅ Database schema created successfully')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create database schema"
    exit 1
fi

# Initialize permissions first
echo ""
echo "=== Initializing Permissions ==="
python helper/init_permissions.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize permissions"
    exit 1
fi

# Generate admin users
echo ""
echo "=== Creating Admin Users ==="
python helper/generate_user.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to create admin users"
    exit 1
fi

# Generate categories
echo ""
echo "=== Setting up Categories ==="
python helper/add_chategories.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to set up categories"
    exit 1
fi

# Initialize footer data
echo ""
echo "=== Initializing Footer Data ==="
python helper/init_footer_data.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize footer data"
    exit 1
fi

# Initialize brand identity
echo ""
echo "=== Initializing Brand Identity ==="
python -c "
from models import BrandIdentity, db
from main import app
app.app_context().push()

# Create default brand identity if it doesn't exist
brand = BrandIdentity.query.first()
if not brand:
    brand = BrandIdentity(
        brand_name='LilyOpenCMS',
        tagline='Modern content management for the digital age'
    )
    db.session.add(brand)
    db.session.commit()
    print('✅ Brand identity initialized with default values')
else:
    print('✅ Brand identity already exists')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize brand identity"
    exit 1
fi

# Initialize basic navigation links
echo ""
echo "=== Setting up Basic Navigation ==="
python -c "
from models import NavigationLink, db
from main import app
app.app_context().push()

# Check if navigation links already exist
existing_links = NavigationLink.query.count()
if existing_links == 0:
    # Create basic navigation links
    basic_links = [
        {'name': 'Beranda', 'url': '/', 'location': 'navbar', 'order': 1, 'is_active': True},
        {'name': 'Berita', 'url': '/news', 'location': 'navbar', 'order': 2, 'is_active': True},
        {'name': 'Tentang Kami', 'url': '/about', 'location': 'navbar', 'order': 3, 'is_active': True},
        {'name': 'Kebijakan Privasi', 'url': '/privacy', 'location': 'footer', 'order': 1, 'is_active': True},
        {'name': 'Tentang Kami', 'url': '/about', 'location': 'footer', 'order': 2, 'is_active': True},
    ]
    
    for link_data in basic_links:
        link = NavigationLink(**link_data)
        db.session.add(link)
    
    db.session.commit()
    print('✅ Basic navigation links created')
else:
    print('✅ Navigation links already exist')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to set up basic navigation"
    exit 1
fi

echo ""
echo "=== Deployment Setup Complete ==="
echo "✅ Database schema created"
echo "✅ Permissions initialized"
echo "✅ Admin users created"
echo "✅ Categories set up"
echo "✅ Footer data initialized"
echo "✅ Brand identity configured"
echo "✅ Basic navigation links created"
echo ""
echo "The application is now ready for deployment!"
echo "You can start the application with: python main.py"
echo ""
echo "Next steps:"
echo "1. Configure your brand identity in the admin panel"
echo "2. Add your content (news, images, videos, albums)"
echo "3. Customize navigation links as needed"
echo "4. Set up your domain and deployment configuration" 